---
title: "Resultados de validación (ejecución real)"
---

# Resultados de validación — Ejecución real (Fase 7)

**Esta página reporta resultados de ejecución real realizada en esta sesión de auditoría (2026-11-06), no cifras citadas de informes previos.** Se documenta el entorno exacto, los comandos exactos y los resultados textuales, siguiendo la misma disciplina de transparencia que ya practicaba `docs/auditoria-backend/INFORME_FINAL_VALIDACION.md`. Esta ejecución **resuelve el hallazgo H-02** (cifras de pruebas inconsistentes entre `docs/RESUMEN_EJECUTIVO.md` —526—, `docs/auditoria-backend/INFORME_FINAL_VALIDACION.md` —473— y `auditoria/01_AUDITORIA_GENERAL.md` —390/50/24—): ninguna de esas cifras coincide exactamente con esta ejecución, lo cual es esperable dado que cada una se hizo en un entorno distinto; lo que aporta esta fase es una medición propia, reproducible y con metodología declarada.

## 1. Entorno de ejecución (declarado explícitamente, como exige la buena práctica de reproducibilidad)

| Parámetro | Valor |
|---|---|
| Sistema operativo | Linux (contenedor de esta sesión de auditoría) |
| Python | **3.14.4** (el proyecto especifica 3.12 en `pyproject.toml`/Dockerfile; no había Python 3.12 disponible en este entorno — ver nota de fidelidad §2) |
| Base de datos de prueba | SQLite en memoria (`config.settings.test`, tal como el proyecto ya lo configura — no se usó PostgreSQL) |
| Node.js | v24.22.1 |
| npm | 11.19.1 |
| Instalación de dependencias backend | `pip install --target=<dir> -r requirements.txt -r requirements-dev.txt` (sin lockfile de versiones exactas en el repo; se resolvieron las versiones más recientes que satisfacen los rangos declarados) |
| Instalación de dependencias frontend | `node_modules/` ya presente en el repositorio (no se reinstaló) |

### Nota de fidelidad del entorno

El proyecto no incluye un lockfile de Python (`requirements.txt` usa rangos, no versiones exactas) ni documenta una versión de Python disponible distinta a 3.12 en este entorno. Esto significa que **las versiones instaladas en esta ejecución no son necesariamente idénticas** a las de un `docker-compose up --build` real (que sí fijaría Python 3.12 vía el `Dockerfile`). Por ejemplo, se instaló `djangorestframework==3.18.3` (la versión más reciente que satisface `>=3.17.2,<4.0`), no necesariamente la misma que usa el contenedor Docker real. Esta diferencia de entorno es la explicación más probable de por qué ninguna cifra de esta ejecución coincide exactamente con las de informes previos — no indica necesariamente una regresión del código.

## 2. Backend — resultado de `pytest` (dos alcances, como el propio proyecto los distingue)

`pyproject.toml` fija `testpaths = ["src/apps"]`: el comando `pytest` sin argumentos **no incluye** `src/core`. Esto ya lo documentaba `docs/RESUMEN_EJECUTIVO.md` ("53 pruebas omitidas por defecto"); se verifica aquí con ejecución real.

| Alcance | Comando | Resultado |
|---|---|---|
| Por defecto (`src/apps`) | `pytest` (desde `backend/src/`) | **484 passed, 13 failed** (497 tests) |
| Extendido (`src/core`) | `pytest src/core` | **76 passed, 0 failed** |
| **Combinado (apps + core)** | `pytest apps core` | **560 passed, 13 failed (573 tests totales)** |

### Las 13 fallas: diagnosticadas con causa raíz confirmada, no solo reportadas

Las 13 fallas son **todas** del mismo archivo, `apps/resoluciones/tests/test_pdf_generator.py`, y todas con el mismo patrón: una función auxiliar `_leer_pdf_texto()` intenta `from pypdf import PdfReader` dentro de un `try/except` con un *fallback* silencioso a cadena vacía si `pypdf` no está instalado — pero las aserciones de los tests (`assert "texto esperado" in texto`) siguen ejecutándose contra esa cadena vacía, fallando.

**Verificación de causa raíz (no solo hipótesis):** se instaló `pypdf` (que **no** es una dependencia declarada en `requirements.txt` ni `requirements-dev.txt`) únicamente en un entorno de prueba aislado y se re-ejecutó ese archivo: **las 13 fallas desaparecen (30/30 passed)**. Esto confirma de forma concluyente que es un **hueco de dependencia de entorno de pruebas**, no un defecto del producto — exactamente la caracterización que ya hizo el equipo en `specs/003-frontend-titulacion/clarify.md` (`DEC-05`: *"Se aceptan los 13 fallos de `pypdf` como deuda de entorno de pruebas del backend... no afectan al frontend ni al contrato"*). Esta auditoría **reproduce y confirma con evidencia propia** una decisión que el equipo ya había tomado, en vez de simplemente repetirla de memoria.

**Conclusión:** del total de 573 pruebas backend, el 100% de las fallas (13/13) tiene causa raíz confirmada y ya aceptada como deuda conocida. **0 fallas de causa desconocida.**

## 3. Backend — cobertura de pruebas (dos mediciones, por transparencia metodológica)

El propio `pyproject.toml` del proyecto (`[tool.coverage.run] omit`) **no excluye los archivos de prueba** de la medición de cobertura — solo excluye migraciones, settings, `apps.py` y `__init__.py`. Esto produce una cifra más alta de lo habitual porque los archivos de test se cubren casi a sí mismos al ejecutarse. Se reportan ambas mediciones:

| Medición | Alcance de `omit` | Statements | Missed | Cobertura |
|---|---|---|---|---|
| **Igual a la configuración oficial del proyecto** | migraciones, settings, `apps.py`, `__init__.py` | 8542 | 380 | **96 %** |
| **Solo código fuente (excluye `*/tests/*`)**, añadida por esta auditoría para una comparación más estándar | + `*/tests/*` | 2478 | 255 | **90 %** |

Ambas cifras **superan ampliamente** el umbral de RNF-012 (>70 %). Ninguna coincide con el 93 % de `docs/RESUMEN_EJECUTIVO.md` ni con el ~90 % "sin medir" de `docs/auditoria-backend/INFORME_FINAL_VALIDACION.md`, pero la medición "solo código fuente" (90 %) es notablemente cercana a esta última.

### Módulos con cobertura más baja (hallazgo nuevo de esta Fase 7)

| Archivo | Cobertura | Relevancia |
|---|---|---|
| `core/adapters/security_headers.py` | **0 %** (13/13 líneas sin cubrir) | **Hallazgo de seguridad**: un módulo dedicado a cabeceras de seguridad HTTP no tiene ninguna prueba automatizada — se recomienda priorizarlo, dado que `DOCUMENTACION/06_SEGURIDAD/` ya identifica hardening HTTP como brecha pendiente |
| `apps/verificacion/adapters/views.py` | 65 % | La vista con menor cobertura del conjunto de vistas reales |
| `apps/notificaciones/services/notification_service.py` | 75 % | Coherente con el hallazgo ya heredado de RF-013 parcial (`COMPONENTES_NEGOCIO.md` §11) |
| `apps/verificacion/services/registrar_observacion.py` | 76 % | — |
| `apps/authentication/adapters/management/commands/seed_initial_data.py` | 0 % | Esperable: es un comando de carga de datos, no lógica de negocio probada unitariamente |

## 4. Backend — lint y tipado (ejecutados, no citados)

| Herramienta | Comando | Resultado |
|---|---|---|
| `flake8` | `flake8 src/` (exactamente como lo documenta `docs/auditoria-backend/INFORME_FINAL_VALIDACION.md`) | **886 líneas de salida, 874 hallazgos reales** (538 `E501` línea larga, 154 `F401` import sin usar, 44 `W292` sin salto de línea final, 41 `W293` línea en blanco con espacios, 39 `F811` redefinición, 24 `F841` variable sin usar, entre otros) |
| `mypy` | `mypy src/` | **20 errores en 7 archivos** (134 archivos analizados) |

**Discrepancia detectada:** `docs/auditoria-backend/INFORME_FINAL_VALIDACION.md` (05-nov-2026) reporta *"Lint: `flake8 src/` ✅ Sin errores"*. La ejecución real de esta Fase 7, con el mismo comando documentado, produce 874 hallazgos. No se puede determinar desde esta auditoría si la discrepancia se debe a cambios en el código desde esa fecha, a una configuración de `.flake8` distinta en aquel momento, o a un error en el informe original — se reporta el hecho verificable (el comando documentado, ejecutado hoy, no da "sin errores") sin especular más allá de la evidencia. La inmensa mayoría de los hallazgos (538/874, 62 %) son de estilo (línea >88 caracteres), no de corrección funcional.

## 5. Frontend — resultado de `vitest` (ejecución repetida: resultado NO determinista)

Se ejecutó `npm run test` **cinco veces consecutivas** en esta sesión, sin cambiar ni una línea de código entre ejecuciones:

| Ejecución | Resultado |
|---|---|
| 1 | 324 passed, **4 failed** (58 archivos: 56 passed, 2 failed) |
| 2 | 324 passed, **4 failed** (mismos 2 archivos, mismas pruebas) |
| 3 | **328 passed, 0 failed** |
| 4 | **328 passed, 0 failed** |
| 5 | **328 passed, 0 failed** |

**Hallazgo nuevo de esta Fase 7: el suite de frontend no es determinista.** 2 de 5 ejecuciones (40 %) fallan; las 3 restantes pasan limpio. Las 4 pruebas que fallan intermitentemente están **todas** en `src/app/router.test.tsx` y dependen de `findByRole(...)` (que usa `waitFor` con un tiempo límite interno) esperando la resolución asíncrona de rutas con parámetro para los roles `ESTUDIANTE` y `DECANO` en `/bandeja/:id`. Al ejecutar `router.test.tsx` **de forma aislada**, sus 9 pruebas pasan siempre — lo que indica que el problema es de **aislamiento entre archivos de prueba** (posible contención de recursos o temporización bajo carga del entorno compartido, consistente con el propio aviso de Vitest en la salida: *"jsdom was created 58 times... create it once per worker... learn more: improving-performance"*), no un defecto de la lógica de enrutamiento en sí.

**Esto contradice puntualmente** la afirmación de `CLAUDE.md` (2026-11-05, cierre de V-04): *"51 pruebas nuevas; 328/328 totales, sin regresiones"*. Esa cifra es alcanzable (3 de 5 ejecuciones de esta auditoría la reproducen exactamente), pero no es garantizada en cada ejecución — "sin regresiones" es una afirmación válida sobre el código, pero no sobre la estabilidad de la ejecución del propio suite. Se recomienda, para quien dé continuidad al proyecto, investigar la configuración de aislamiento de Vitest (`pool: 'vmThreads'` o `isolate: false`, sugerido por la propia herramienta) para eliminar esta fuente de falsos negativos intermitentes — no se modifica el código del frontend en este trabajo de documentación.

## 6. Frontend — lint y tipado

| Herramienta | Comando | Resultado |
|---|---|---|
| ESLint | `npm run lint` | **0 errores** |
| TypeScript | `npm run typecheck` | **0 errores** |

Ambos limpios, sin discrepancia con lo declarado por `CLAUDE.md`.

## 7. Resumen ejecutivo de esta fase

| Suite | Resultado verificado en esta Fase 7 (2026-11-06) |
|---|---|
| Backend — pruebas | 560/573 passed (97.7 %); 13 fallas, 100 % con causa raíz confirmada como deuda de entorno ya aceptada (`DEC-05`), 0 desconocidas |
| Backend — cobertura | 90 % código fuente / 96 % incluyendo tests (ambas > umbral RNF-012 de 70 %) |
| Backend — lint/tipos | flake8: 874 hallazgos (mayormente estilo); mypy: 20 errores — **discrepancia con informe previo que reportaba "sin errores"** |
| Frontend — pruebas | No determinista: 328/328 en 3 de 5 ejecuciones, 324/328 en 2 de 5 (mismas 4 pruebas, causa de aislamiento identificada) |
| Frontend — lint/tipos | 0 errores en ambos |

**Ninguna cifra de ejecuciones previas se da por válida sin esta verificación propia; esta tabla es la fuente de verdad de esta auditoría para el estado de pruebas al 2026-11-06.**
