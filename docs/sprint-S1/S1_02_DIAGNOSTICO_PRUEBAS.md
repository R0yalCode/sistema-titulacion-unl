# S1-02 — DIAGNÓSTICO DE PRUEBAS AUTOMATIZADAS

**Fecha:** 02-nov-2026 · Estado: NO se alteró ninguna prueba, línea de código, dependencia ni configuración.

## 1. Marco de ejecución observado

| Elemento | Valor observado | Evidencia |
| :--- | :--- | :--- |
| Framework | `pytest` 8.4.2 + `pytest-django` 4.14.0 + `pytest-cov` 7.1.0 | `requirements-dev.txt`, contenedor |
| Settings declarados en ini | `DJANGO_SETTINGS_MODULE = config.settings.test` | `backend/pyproject.toml [tool.pytest.ini_options]` |
| Settings de `test.py` | SQLite `:memory:`, hasher MD5, `DEBUG=False` | `config/settings/test.py` |
| Settings **efectivos por defecto** | `config.settings.local` → **PostgreSQL** | variable de entorno del contenedor `DJANGO_SETTINGS_MODULE=config.settings.local`; pytest-django no sobreescribe una variable ya existente |
| Cobertura de dependentcias | `pytest` y todos los prod deps instalados en el contenedor | `pip list` (verificado) |
| Dependencia de testing faltante | **`pypdf`** (usada solo por tests para extraer texto de PDF) NO está en `requirements-dev.txt` | `src/apps/resoluciones/tests/test_pdf_generator.py:27-38` |
| Total de tests | **464** | `--collect-only` |

## 2. Resultados

### Escenario A — por defecto del entorno actual (settings `local` → PostgreSQL)
```
50 failed, 390 passed, 24 errors  (228 s)
```
- 84 % de las pruebas en verde **aun con el entorno incorrecto**.

### Escenario B — `DJANGO_SETTINGS_MODULE=config.settings.test` (settings correctos, sin tocar código)
```
42 failed, 398 passed, 24 errors  (7 s)
```
- Desaparecen los 8 fallos de introspección `sqlite_master` (categoría 2 abajo), porque con SQLite sí aplican.
- Persisten **todas las demás** fallas: son independientes del motor de BD.

## 3. Clasificación por causa raíz (únicas 3 causas reales)

### Causa 1 — `PermissionError: [Errno 13] Permission denied: '/media/private'` (≈ 53-56 tests)
- **Errores (24):** setup de `TestDeclararAptitud*` completo (`test_declarar_aptitud.py:221` en fixture `expediente_con_informe` → `emitir_informe()`) — no llega al assert.
- **Fallos (~29):** todo test que llama `emitir_informe()` o instancia `PDFGeneratorAdapter()`: `test_emitir_informe.py` (11), `test_resoluciones_and_pdf_generation.py` (≈10), `test_auditoria.py`, `test_notifications_and_audit.py`, `test_declarar_aptitud.py` (1).
- **Origen:** `pdf_generator.py:48-49` — ruta absoluta en raíz FS = **consecuencia directa de SEC-02**.
- **Tipo:** fallo de código productivo (bloqueante del flujo #590 completo).

### Causa 2 — Tests con introspección SQLite hardcodeada (`sqlite_master`) (8 tests en escenario A)
- `test_auditoria.py` `test_indices_creados`, `test_notification_service.py` `test_indices_creados`, `test_notifications_and_audit.py` ×2 (índices), `test_models.py` ×4 (`TestIndicesYConstraints`).
- Se ejecutan con `cursor.execute("SELECT name FROM sqlite_master ...")` → sobre PostgreSQL produce `psycopg.errors.UndefinedTable`.
- **Tipo:** **error de entorno/prueba** (antipatrón: introspección acoplada a un motor). En escenario B pasan. Los índices reales de los modelos existen en las migraciones; la aserción es frágil.
- Nota organizacional: la auditoría previa dijo "74 errores con causa raiz común PermissionError (74 de 74)". Esta validación lo desmiente: **74 = 50F+24E y al menos 8 no provienen de PermissionError**.

### Causa 3 — `pypdf` no instalada → aserciones de contenido vacías (13 tests en escenario B)
- `test_pdf_generator.py`: 13 fallos con `assert 'APTO' in ''` (todas las comprobaciones de texto interior del PDF).
- El helper `_leer_pdf_texto()` retorna `""` al capturar `ImportError`; el fallback silencioso convierte "dependencia faltante" en "contenido incorrecto", ocultando la causa.
- **Tipo:** deficiencia de configuración de pruebas (dependencia de test no declarada). El PDF en sí se genera (los tests de existencia/tamaño pasan).

## 4. Desglose por módulo (escenario B)

| Módulo de test | F | E | Causas |
| :--- | ---: | ---: | :--- |
| `notificaciones/tests/test_auditoria.py` | 3 | 0 | C1 (2), C2 escondida por B (1: índices) |
| `notificaciones/tests/test_notification_service.py` | 0 | 0 | (1 fallo índices solo en esc. A) |
| `notificaciones/tests/test_notifications_and_audit.py` | 3 | 0 | C1 (3) |
| `resoluciones/tests/test_declarar_aptitud.py` | 1 | 24 | C1 (todos) |
| `resoluciones/tests/test_emitir_informe.py` | 11 | 0 | C1 (todos) |
| `resoluciones/tests/test_models.py` | 0 | 0 | C2 solo en esc. A |
| `resoluciones/tests/test_pdf_generator.py` | 13 | 0 | C3 (todos) |
| `resoluciones/tests/test_resoluciones_and_pdf_generation.py` | 11 | 0 | C1 (≈8), C3/pypdf (implicit) |

## 5. Módulos productivos afectados directamente

1. `apps/resoluciones/adapters/pdf_generator.py` — **bloqueante** (SEC-02).
2. `apps/resoluciones/services/emitir_informe.py` — usa el generador roto; guarda rutas absolutas.
3. `apps/resoluciones/services/declarar_aptitud.py` — archivo no persistido (SEC-01), sin bloqueo por test (por eso los setups rompen antes).
4. `apps/resoluciones/adapters/views.py` (endpoint `informes/` logueó `Internal Server Error` 3 veces capturadas en la corrida A).

## 6. Conclusión de estado

| Afirmación | Verificación |
| :--- | :--- |
| "74 errores" reportados por auditoría | Falso como dato único real: son 74 combinandoescenarios A (50F+24E = 74). Ningún escenario da 74 "errores" puros; en B son 66 (42F+24E). |
| ¿Todos misma causa? | NO: 3 causas (rutas hardcodeadas ~53-56; introspección sqlite ~8 en A; pypdf 13; superposición menor). |
| ¿Fallos previos a cambios S1? | Sí — todo lo observado existe **antes** de cualquier modificación de S1. Este sprint parte de 398/464 (85,8 %) verdes con settings correctos. |
| ¿Alguna prueba fue deshabilitada o weakenada? | NO. Se ejecutó sin `-k`, sin `--deselect`, sin `skip`. |
| Cobertura | Medible en S1-T05 con `pytest --cov`; foco declarado en `auditoria/06`: `declarar_aptitud.py` 35 %, `verificacion/adapters/views.py` 65 %, `resoluciones/adapters/views.py` 74 %, `emitir_informe.py` 62 % (fuente: doc de auditoria previa, no re-medido aquí). |
