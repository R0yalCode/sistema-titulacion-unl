---
title: "Paquete de aprobación — DEC-001, DEC-004 a DEC-009"
---

# Paquete de aprobación de decisiones pendientes

**Fecha:** 2026-11-06
**Estado:** Análisis técnico para decisión del responsable. **Ninguna decisión aquí descrita está aprobada.** No se modificó ninguna ficha técnica, ningún código, ninguna configuración, ni el frontend. No se implementó ninguna de las tareas SEC-T003, SEC-T007, SEC-T009, SEC-T010, SEC-T016, SEC-T017, SEC-T019, SEC-T021.

**Verificación de partida (antes de analizar nada):** Confirmé los 21 estados reportados contra el repositorio real. Coinciden, con una corrección aplicada: **SEC-T006, SEC-T008 y SEC-T012 estaban correctamente implementadas y probadas desde la sesión anterior, pero su sección en `CHECKLIST_EJECUCION_Y_CIERRE.md` nunca se había actualizado** (quedaron con todas las casillas sin marcar). Corregido con evidencia re-verificada (código real + 497/497 tests), no con una simple re-afirmación.

**Hallazgo adicional de esta verificación, relevante para DEC-004 (ver abajo):** `pytest` sin argumentos (lo que esta sesión y la anterior llamaron repetidamente "suite completa") respeta `testpaths = ["src/apps"]` de `pyproject.toml` y por lo tanto **nunca ejecuta `src/core/adapters/tests/` ni `src/core/tests/`**. Son **497** pruebas bajo esa configuración (igual que siempre se reportó — no es un error de ejecuciones anteriores) y **573** si se incluye `src/core` explícitamente. La diferencia (76 pruebas reales, ya existentes y pasando, incluidas 5 de `core/adapters/tests/test_logging.py` de SEC-T011) es exactamente la brecha que SEC-T016 debe cerrar.

---

## DEC-001 — Validación MIME real (SEC-T007)

### Problema que resuelve

`core/adapters/pdf_validation.py` solo valida tamaño (≤10MB), los primeros 5 bytes (`%PDF-`) y calcula un hash SHA-256 — pero **no valida la estructura interna del PDF ni su tipo MIME real**. `validar_pdf_completo()` incluso **fija `"tipo_mime": "application/pdf"` como literal fijo**, sin detectarlo. Un archivo cuyos primeros 5 bytes sean `%PDF-` pasa, sin importar qué contenga después.

### Situación actual verificada (no asumida de la ficha)

Instalé `pikepdf` y `python-magic` (con `libmagic` ya presente en este sistema) y los probé contra: (a) un PDF real generado por el propio sistema (ReportLab, Providencia 590), (b) un políglota construido apendizando bytes de un ZIP falso al final de ese mismo PDF real, (c) ese mismo PDF truncado a la mitad, (d) un PNG con cabecera `%PDF-` falsa, (e) un archivo con cabecera ZIP seguida de contenido PDF válido.

| Caso | `pikepdf.open()` | `python-magic` (primeros 2048 bytes) |
|---|---|---|
| PDF real institucional | ✅ Acepta (correcto) | ✅ `application/pdf` (correcto) |
| **Políglota (PDF + ZIP apendizado)** | ❌ **Acepta igual** (no detecta el apéndice) | ❌ **`application/pdf`** (solo mira el inicio, no detecta el apéndice) |
| PDF truncado a la mitad | ❌ **Acepta igual** (parser tolerante por diseño) | ❌ `application/pdf` (los primeros bytes siguen siendo válidos) |
| Cabecera no-PDF (PNG) | — (no se probó, ya lo rechaza el check de magic bytes actual) | ✅ Rechaza correctamente |
| Cabecera ZIP + PDF después | — | ✅ Rechaza correctamente (pero el check de magic bytes **actual** ya rechaza esto, porque no empieza con `%PDF-`) |

**Conclusión verificada, no asumida:** contrario a lo que decía la ficha original ("pikepdf... rechaza políglotas/corruptos"), **ni `pikepdf` ni `python-magic` detectan, por sí solos, el caso de políglota más simple y realista** (contenido extra apendizado después de un PDF válido) — exactamente el escenario que motivó esta decisión. Ambos solo agregan valor marginal sobre el chequeo de magic bytes que **ya existe** hoy, para el caso donde la cabecera NO es `%PDF-` (que el código actual ya rechaza).

Sí encontré un chequeo adicional, simple y efectivo, que ninguna de las dos librerías hace por defecto: **un PDF legítimo no tiene datos después de su último `%%EOF`** (verificado en el PDF real: 1 byte sobrante, un salto de línea). Un políglota por apéndice sí los tiene.

### Alternativas

| Opción | Cierra el políglota por apéndice | Dependencia de sistema | Riesgo de falso positivo (verificado) |
|---|---|---|---|
| A) Solo `python-magic` | No (verificado arriba) | `libmagic` (ya está en este host; no verificado si está en la imagen `python:3.12-slim` del Dockerfile — probablemente no, requeriría `apt-get install libmagic1`) | Bajo, pero no cierra el problema real |
| B) Solo `pikepdf` | No (verificado arriba) | Ninguna (pure Python) | Bajo, pero no cierra el problema real |
| C) `pikepdf` o `python-magic` **+ verificación de bytes sobrantes tras el último `%%EOF`** | **Sí** | Según cuál de las dos se elija | Riesgo real: algunos generadores de PDF (no solo ReportLab) podrían dejar más de un byte de margen tras `%%EOF` — necesitaría probarse contra una muestra real más amplia antes de ser estricto, no solo contra 1 PDF |
| D) Mantener solo lo actual | No | Ninguna | No cierra nada, es el estado de hoy |

### Riesgos y ventajas

- **Ventaja de C:** es la única opción que realmente cierra la brecha original, con esfuerzo bajo (una comparación de offsets, sin librería adicional para ese chequeo específico).
- **Riesgo de C:** falso positivo si algún flujo legítimo (p. ej. un estudiante que sube un PDF exportado por un escáner o editor que añade metadatos/bytes tras el `%%EOF`, algo que ocurre en la práctica con algunos lectores) queda rechazado. Esto **no se puede descartar sin probar contra una muestra más amplia de PDFs reales** de la UNL, que no tengo disponible en este entorno.
- **Riesgo de A/B solas:** dan una falsa sensación de que el problema está resuelto cuando, verificado empíricamente, no lo está para el caso de apéndice.

### Recomendación técnica (propuesta, no aprobada)

**Opción C, con `pikepdf`** (pure Python, sin dependencia de sistema, más simple de añadir al Dockerfile ya existente) **más** la verificación de bytes sobrantes tras `%%EOF`. Antes de activar el rechazo por bytes-sobrantes de forma estricta, probar contra una muestra real más amplia de PDFs generados por los flujos reales (ReportLab del propio sistema, y PDFs subidos por estudiantes reales si se dispone de un conjunto de prueba) — no inventar ese corpus aquí.

### Compatibilidad backend/frontend

Backend-only. Mismo contrato (`400` si inválido, sin cambio de forma de respuesta). Sin impacto frontend.

### Criterios de aceptación propuestos

- `pikepdf.open()` + verificación de bytes tras `%%EOF` integrados en `validar_pdf_completo()`, antes de guardar.
- Pruebas con los 5 casos verificados arriba (incluido que el políglota por apéndice ahora SÍ se rechace).
- Prueba contra al menos los PDFs reales ya generados por el sistema (Providencia 590, Memorando 162) sin falsos positivos.
- `tipo_mime` deja de ser un literal fijo.

---

## DEC-004 — Umbral de cobertura (SEC-T016)

### Problema que resuelve

`pyproject.toml` no tiene `--cov-fail-under` ni incluye `src/core` en `testpaths`. No hay enforcement de cobertura en CI.

### Situación actual verificada

Ejecuté `pytest --cov=src --cov-report=term-missing` de verdad (no asumido): **93% de cobertura global** (8023 líneas, 549 sin cubrir), **573 pruebas pasando** cuando se incluye `src/core` (497 si solo se cuenta lo que corre por defecto hoy).

Por área:
- Apps de negocio (`authentication`, `peticiones`, `expedientes`, `resoluciones`, `verificacion`, `notificaciones`): mayoría de archivos entre 90-100%; los puntos más bajos reales son `verificacion/adapters/views.py` (65%) y `verificacion/services/registrar_observacion.py` (76%).
- `core/adapters/`: alto en lo que ya tiene test (`pdf_validation.py` 100%, `middleware.py` 100%, `mock_sga.py` 84%), pero **`production.py` y `security_headers.py` están en 0%** — código real, pero solo se ejecuta bajo `DJANGO_SETTINGS_MODULE=config.settings.production`, que `pytest` nunca carga (se verificó manualmente fuera de pytest en sesiones anteriores, no vía test automatizado).
- **Un archivo de pruebas reales, `src/core/tests/test_notifications_and_audit.py` (330 líneas, prueba el contrato de `ISGALegacyPort`/`SGAMockAdapter`), existe, pasa, y nunca se ejecuta** por el mismo motivo de `testpaths`.

### Alternativas

| Umbral global | Contexto verificado |
|---|---|
| 70% | Muy por debajo de la realidad actual (93%); no exige nada |
| **80%** (recomendación original de la ficha) | Ya superado hoy con margen amplio; fácil de cumplir, pero no refleja el nivel real ya alcanzado |
| 90% | Más cercano a la realidad verificada (93%), pero **`production.py`/`security_headers.py` en 0% bajarían el promedio** si se incluyen sin excepción |
| Progresivo (ej. 80% ahora, subir 2-3 puntos por trimestre) | Evita que el umbral bloquee CI por los módulos de producción no ejecutables bajo `settings.test` |

### Riesgos y ventajas

- Fijar el umbral **sin antes resolver la inclusión de `src/core`** en `testpaths` sería engañoso: CI seguiría sin correr 76 pruebas reales.
- Incluir `production.py`/`security_headers.py` en el cálculo de cobertura sin poder ejecutarlos bajo `pytest` (requieren variables de entorno que `settings.test` no define) bajaría artificialmente el número, o forzaría a excluirlos vía `omit` — una decisión legítima pero que debe quedar explícita, no implícita.

### Recomendación técnica (propuesta, no aprobada)

1. **Primero** corregir `testpaths = ["src/apps", "src/core"]` (o `["src"]`), e investigar por qué `src/core/tests/test_notifications_and_audit.py` quedó fuera (parece simplemente un descuido de configuración, no una decisión deliberada).
2. **Umbral global: 85%** — por debajo del 93% ya verificado (deja margen para que `production.py`/`security_headers.py` entren al cálculo sin romper CI de inmediato), pero exigiendo más que el 80% original.
3. **Módulos críticos (`authentication`, `peticiones`, `verificacion.services`, `core.adapters`) sin excepción: 90%** — ya se cumple hoy en casi todos, exceptuando `verificacion/adapters/views.py` y `registrar_observacion.py`, que necesitarían una o dos pruebas adicionales.
4. **Excluir explícitamente de cobertura** (`omit`, con justificación documentada, no silenciosa): `*/settings/production.py` si no se decide ejecutar pruebas contra él vía un proceso separado (como se hizo manualmente en SEC-T001/T011), y los archivos ya excluidos (`migrations`, `settings/*` en general, `apps.py`, `__init__.py`).
5. Progresividad: no es necesaria dado que el nivel real (93%) ya supera la propuesta (85%) — **no se requiere una rampa**, se puede exigir desde ya.

### Compatibilidad backend/frontend

Backend-only, configuración de CI/tooling. Sin impacto frontend.

### Criterios de aceptación propuestos

- `testpaths` corregido; las 573 pruebas (no 497) corren con `pytest` sin argumentos.
- `--cov-fail-under=85` global, verificación manual de que módulos críticos ≥90%.
- Documentado en `docs/09-calidad/cobertura.md` (ya existe, actualizar en vez de duplicar).

---

## DEC-005 — Retención de archivos huérfanos (SEC-T019)

### Problema que resuelve

No hay ningún mecanismo que libere espacio de versiones de documentos ya no vigentes (`DocumentoEntregado.es_vigente=False`) ni de archivos huérfanos (sin registro en BD). Riesgo de agotamiento de disco a largo plazo (relevante tras el incidente real de espacio en disco de esta misma sesión, aunque no relacionado con este mecanismo).

### Situación actual verificada

`DocumentoEntregado` tiene `es_vigente` (booleano, indexado) y `fecha_carga` (auto, no se actualiza tras creación) — no tiene un campo "fecha en que dejó de ser vigente", por lo que un cálculo de "N días desde que dejó de ser vigente" requeriría o bien añadir ese campo (cambio de esquema) o usar `fecha_carga` de la **siguiente** versión vigente como proxy (ya disponible sin migración, algo menos preciso pero suficiente).

### Alternativas

| Política | Riesgo |
|---|---|
| Eliminación inmediata al dejar de ser vigente | **Irreversible y sin ventana de recuperación** — si una subsanación resulta errónea o se necesita auditar una versión anterior poco después, no habría forma de recuperarla. No recomendado sin revisión legal. |
| Periodo de gracia configurable (90 días sugerido originalmente) | Razonable; requiere definir desde cuándo se cuenta (ver arriba) |
| Conservar indefinidamente, solo limpiar huérfanos reales (sin registro en BD) | Más conservador; no resuelve el crecimiento de versiones no vigentes, pero evita cualquier riesgo de borrar algo con registro |
| Mover a cuarentena (no borrar) tras el periodo de gracia, borrado manual posterior | Más seguro operativamente; doble paso antes de la pérdida irreversible |

### Riesgos y ventajas

- Cualquier automatización de borrado es, por definición, una operación potencialmente irreversible sobre datos de usuarios — exactamente lo que esta sesión tiene prohibido ejecutar sin una política aprobada.
- Un `--dry-run` por defecto (sin flag no borra nada) y un paso de "cuarentena" antes del borrado real reduce el riesgo de un error de implementación con consecuencias irreversibles.

### Recomendación técnica (propuesta, no aprobada)

- **Periodo de gracia: 90 días**, contado desde que la versión dejó de ser la vigente (aproximado con la `fecha_carga` de la versión que la reemplazó, sin requerir migración).
- **Identificación segura de huérfanos:** (a) archivos en disco sin ningún `DocumentoEntregado.archivo_path` coincidente — candidatos a huérfanos reales; (b) versiones con registro pero `es_vigente=False` y más de 90 días — candidatas a limpieza por política, **no por "huérfanas"** (tienen registro, son una categoría distinta y deben tratarse con más cuidado).
- **Exclusiones explícitas:** nunca tocar `es_vigente=True`; nunca tocar nada con menos de 90 días; nunca tocar archivos de `resoluciones/` (Providencia 590, Memorando 162) en esta primera versión del comando — son actos administrativos, su política de retención documental es un tema distinto y más sensible que el de documentos de requisitos.
- **Mecanismo:** mover a una carpeta de cuarentena (no borrar) en la primera ejecución real; un paso separado, posterior y explícito, borra la cuarentena tras otro periodo (ej. 30 días adicionales). `--dry-run` por defecto.
- **Auditoría:** cada archivo movido/borrado genera un registro en `EventoAuditoria` (reutilizando el mecanismo ya existente, sin crear uno paralelo) con el `hash_sha256` del archivo antes de tocarlo, por si se necesita verificar después qué se eliminó.

### Compatibilidad backend/frontend

Backend-only (management command + cron). Sin impacto frontend.

### Criterios de aceptación propuestos

- `--dry-run` por defecto; requiere flag explícito para actuar.
- Nunca toca `es_vigente=True` ni archivos con menos de 90 días.
- Cuarentena antes de borrado real; registro en `EventoAuditoria`.
- Pruebas que demuestren que NO borra nada fuera de la política exacta.

---

## DEC-006 — Descarga de declaratorias (SEC-T009)

### Problema que resuelve

`DeclaratoriaAptitudSerializer` expone `archivo_memorando_firmado_path` (ruta interna real del filesystem) en las respuestas de la API — confirmado, sigue expuesto hoy. No existe ningún endpoint `GET` de descarga para declaratorias (confirmado: `DeclaratoriaViewSet` solo tiene `create`).

### Situación actual verificada

El patrón de descarga segura **ya existe y funciona** para peticiones (`PeticionViewSet.descargar_documento`): valida ámbito/IDOR manualmente, verifica existencia física, sirve con `FileResponse` streaming. No hay ninguna razón técnica para no replicar exactamente ese mismo patrón para declaratorias — es el mismo tipo de almacenamiento privado (`PrivateMediaStorage`), la misma necesidad de autorización RBAC.

### Alternativas (de `DECISIONES_TECNICAS_PENDIENTES.md`, re-evaluadas)

| Opción | Evaluación tras verificar el código real |
|---|---|
| A) Nuevo action `GET /api/v1/declaratorias/{id}/documento/` en `DeclaratoriaViewSet`, replicando `descargar_documento` de peticiones | **Confirmado como la opción correcta** — mismo patrón, mismo almacenamiento, ya probado en producción (código) para peticiones |
| B) Reutilizar un endpoint existente | No existe ninguno adecuado, confirmado |
| C) Endpoint genérico de archivos | Sobre-ingeniería para una necesidad acotada, descartado como en el análisis original |
| D) Mantener la ruta expuesta temporalmente | Deuda técnica activa y ya identificada por la auditoría original; no resuelve nada |

### Riesgos y ventajas

- Riesgo bajo: el patrón a replicar ya está probado (tests de `descargar_documento` de peticiones pasan).
- Compatibilidad: es un endpoint **nuevo** (no modifica ninguno existente), por lo que no rompe ningún contrato ya consumido.

### Recomendación técnica (propuesta, no aprobada)

Opción A. `GET /api/v1/declaratorias/{id}/documento/`, con autorización equivalente a la ya definida en `RBAC_MATRIX` para `declaratorias` (mismo ámbito que ya aplica a `create`: Decano de la facultad). Luego, en SEC-T009 (tarea separada, no esta decisión), remover `archivo_memorando_firmado_path` del serializer y añadir `download_url` apuntando a este nuevo endpoint — exactamente como ya se hizo conceptualmente para peticiones.

### Compatibilidad backend/frontend

**Backend: nuevo endpoint, sin romper nada existente.** **Frontend: SEC-T009 (no esta decisión) requerirá que la vista que hoy lea `declaratoria.archivo_memorando_firmado_path` cambie a `declaratoria.download_url`** — impacto real pero acotado a un campo en una vista. No se modifica el frontend en esta fase; se documenta el impacto para cuando SEC-T009 se autorice.

### Criterios de aceptación propuestos

- Nuevo endpoint funcional, con los mismos controles de ámbito/RBAC que `create` de declaratorias.
- Pruebas de autorización (quién puede descargar, 403/404 para quien no debería).
- SEC-T009 puede entonces remover la ruta interna del serializer sin dejar la función de descarga sin reemplazo.

---

## DEC-007 — Evidencias ACD4 (SEC-T021)

### Problema que resuelve

`MATRIZ_TRAZABILIDAD_SEGURIDAD.md` lista identificadores `a1b2c3d`, `e4f5g6h`, `i7j8k9l`, `m0n1o2p`, `q3r4s5t` como evidencia de PRs (#42-#46) de 5 integrantes, todos marcados **ya en el documento original** como "NO ENCONTRADO"/"NO VERIFICADO".

### Situación actual verificada

Confirmé el patrón: son 5 hashes de 7 caracteres, con progresión alfabética simple (`a1b2c3d`, `e4f5g6h`, `i7j8k9l`...) — un patrón típico de datos de ejemplo/plantilla, no de hashes Git reales (un hash corto real de Git es una subcadena de un SHA-1 real, sin un patrón secuencial tan regular). **No existe repositorio Git en este proyecto** (confirmado en sesiones anteriores) y no hay ninguna plataforma externa (GitHub/GitLab) accesible desde aquí para verificar PRs #42-46.

### Alternativas

Las mismas tres ya identificadas en `DECISIONES_TECNICAS_PENDIENTES.md`: (1) son placeholders → cancelar: (2) son reales en otra plataforma → pedir mapeo real; (3) faltan por registrar → registrar ahora.

### Riesgos y ventajas

**No se puede, ni se debe, generar evidencia para completar esta decisión.** Cualquier intento de "rellenar" estos identificadores con datos inventados sería exactamente lo que la restricción de esta fase prohíbe explícitamente y, más allá de eso, sería falsificar un registro de auditoría — inaceptable independientemente de cualquier autorización, por tratarse de evidencia académica/institucional.

### Recomendación técnica (propuesta, no aprobada)

Dado el patrón observado y la ausencia total de medios de verificación en este entorno, **la evidencia disponible apunta a que son placeholders**, pero esta sesión no tiene autoridad ni información para confirmarlo con certeza — es una pregunta que solo el Coordinador Académico/Responsable del Proyecto puede responder (puede que esos PRs existan en una plataforma real que yo no tengo forma de consultar). Recomiendo preguntar directamente: *"¿Los identificadores a1b2c3d/e4f5g6h/i7j8k9l/m0n1o2p/q3r4s5t corresponden a Pull Requests reales en una plataforma Git (GitHub/GitLab) de este proyecto, o son datos de ejemplo del documento?"*

### Compatibilidad backend/frontend

No aplica — es documentación/trazabilidad, no código.

### Criterios de aceptación propuestos

- Si el responsable confirma que son placeholders: actualizar `MATRIZ_TRAZABILIDAD_SEGURIDAD.md` marcando SEC-T021 "NO APLICA", con esa justificación citada.
- Si confirma que son reales: proveer el mapeo real (SHA/PR/autor verificables), y solo entonces actualizar la matriz con esos datos reales — nunca con datos generados por mí.

---

## DEC-008 — Almacenamiento de refresh tokens en frontend (SEC-T003)

### Problema que resuelve

SEC-T003 (rotación + blacklist de refresh tokens) necesita saber dónde y cómo el frontend guarda el refresh token, para no romper el flujo de renovación de sesión al rotar.

### Situación actual verificada (hallazgo importante, cambia el análisis original)

Revisé `frontend/src/auth/AuthContext.tsx` y `frontend/src/auth/storage.ts` directamente:

```ts
// storage.ts — únicamente existe esto:
const ACCESS_TOKEN_KEY = 'sgt.access'
export function saveAccessToken(token: string) { sessionStorage.setItem(ACCESS_TOKEN_KEY, token) }
export function getAccessToken() { return sessionStorage.getItem(ACCESS_TOKEN_KEY) }
export function clearAccessToken() { sessionStorage.removeItem(ACCESS_TOKEN_KEY) }
```

`AuthContext.login(tokens: TokenPair)` recibe `{ access, refresh }` del backend, pero **solo llama a `saveAccessToken(tokens.access)` — el `refresh` recibido se descarta, nunca se guarda en ningún lado** (ni `localStorage`, ni `sessionStorage`, ni cookie). Confirmado con `grep -rln "refresh"` en todo `src/`: solo aparece en el tipo `TokenPair`, en el endpoint de login, y en fixtures de mocks — en ningún archivo de lógica real de renovación de sesión.

Esto coincide exactamente con lo que ya documenta `CLAUDE.md`/`plan.md` §6: *"El backend no ofrece renovación de sesión: no implementes refresh automático ni logout de servidor inventados (re-login al expirar)"*. **El frontend, hoy, no tiene ningún flujo de refresh activo** — la sesión muere cuando el access token expira o se cierra la pestaña (`sessionStorage`), y el usuario vuelve a iniciar sesión.

### Alternativas (re-evaluadas con este hallazgo)

| Opción | Relevancia dado el hallazgo |
|---|---|
| A) httpOnly cookie (recomendación original) | Resolvería el problema para una *futura* funcionalidad de refresh, pero no hay ninguna urgencia de migración porque no hay nada que migrar hoy |
| B) localStorage/sessionStorage | Mismo caso — sería implementar algo nuevo, no migrar algo existente |
| C) No implementar renovación en el frontend por ahora | **Es, de hecho, el estado actual real**, y coincide con la política ya documentada del proyecto |

### Riesgos y ventajas

- **El riesgo que motivó originalmente esta decisión (cómo migrar el almacenamiento existente del refresh token) no existe hoy**, porque no hay nada que migrar.
- Implementar SEC-T003 (rotación/blacklist + endpoint de logout) en el backend **no tiene ningún impacto en el frontend actual**, porque el frontend nunca usa el refresh token después del login.
- El único riesgo real es si alguien asume, al leer la ficha original, que hay trabajo de coordinación de frontend pendiente — no lo hay, para el estado actual del código.

### Recomendación técnica (propuesta, no aprobada)

**No bloquear SEC-T003 por DEC-008.** El backend puede implementar rotación + blacklist + logout sin ningún requisito de cambio de frontend, porque el frontend no persiste el refresh token. Si en el futuro se decide implementar renovación de sesión en el frontend (fuera del alcance actual, y requeriría autorización explícita de cambio de frontend), **en ese momento** se recomienda httpOnly cookie (opción A), por ser la más segura ante XSS — pero esa es una decisión a tomar cuando esa funcionalidad se autorice, no ahora.

### Compatibilidad backend/frontend

**Sin impacto frontend verificado.** No se requiere ni se propone ningún cambio de frontend para desbloquear SEC-T003.

### Criterios de aceptación propuestos

- Confirmar (ya verificado aquí) que el frontend no persiste el refresh token antes de cerrar esta decisión.
- SEC-T003 puede proceder con el backend solo, documentando el logout endpoint como disponible para un futuro consumo del frontend, sin exigir su adopción inmediata.

---

## DEC-009 — Mensaje de error 500 (SEC-T010)

### Problema que resuelve

SEC-T010 (handler global de excepciones) necesita un mensaje final para el usuario en errores 500, sin exponer detalles técnicos, manteniendo la información técnica completa solo en logs internos.

### Situación actual verificada

Ya existe infraestructura reutilizable: `core/adapters/logging_filters.py` (SEC-T011) ya filtra datos sensibles de los logs, y el `LOGGING` dict ya tiene un logger `django.request`. Las excepciones de dominio actuales (`EstadoPeticionInvalidoAPI`, `UsuarioNoAutorizadoAPI`, etc., en `peticiones/adapters/views.py`) ya son `APIException` con `status_code`/`default_code` propios (400/403) — **ninguna de ellas es un 500**; los 500 reales de este sistema son excepciones no controladas (bugs), no reglas de negocio con código propio.

### Alternativas (de `DECISIONES_TECNICAS_PENDIENTES.md`, sin cambios sustanciales tras verificar)

Las tres ya planteadas: mensaje institucional genérico, mensaje "inesperado" genérico, o mensaje con `request_id` para soporte.

### Riesgos y ventajas

- Incluir un `request_id` en la respuesta al usuario (no solo en logs) es útil para soporte, pero requiere que exista un mecanismo de `request_id` — hoy `RequestIdFilter` (SEC-T011) ya pone un placeholder `"-"` porque no hay un generador de `request_id` real todavía (quedó explícitamente pendiente para un futuro mecanismo). Prometer un `request_id` útil en el mensaje de error sin tener aún ese mecanismo sería una promesa vacía.
- Un mensaje puramente genérico sin ningún identificador dificulta el soporte real a usuarios que reporten un error.

### Recomendación técnica (propuesta, no aprobada)

**"Error interno del servidor. El equipo técnico ha sido notificado."** (la opción ya recomendada originalmente), **sin `request_id` por ahora** — hasta que exista un generador real de `request_id` (no inventar uno solo para este mensaje). El detalle completo (excepción, traza, request) va únicamente al logger `django.request`/`security_file` ya configurado en SEC-T011, que ya tiene filtro de datos sensibles.

### Compatibilidad backend/frontend

El **formato de respuesta cambia** para todos los códigos de error (ver estructura `{"error": {"code", "message", "details"}}` ya definida en la ficha), no solo el 500 — esto es un cambio de contrato que **sí requiere coordinación con el frontend** cuando SEC-T010 se autorice (actualizar su manejo de errores global). Esta decisión (DEC-009) en sí misma solo fija el *texto* del mensaje 500; el cambio de forma de la respuesta es responsabilidad de la implementación de SEC-T010, no de esta decisión.

### Criterios de aceptación propuestos

- Ningún 500 expone traza, SQL, ni rutas de archivo al cliente.
- El mensaje institucional aprobado aparece de forma consistente.
- El detalle completo queda en el logger ya existente, con los filtros de datos sensibles de SEC-T011 ya aplicados.

---

## Orden de ejecución propuesto (evaluado contra las dependencias reales de las fichas, no solo el orden sugerido)

El orden que planteó la instrucción es, en general, coherente. Ajustes verificados:

1. **SEC-T007** (DEC-001) — independiente, puede ir primero tal cual.
2. **SEC-T009** (DEC-006) — independiente de las anteriores.
3. **SEC-T010** (DEC-009) — independiente de las anteriores.
4. **SEC-T016** (DEC-004) — independiente; **recomiendo adelantarla antes de T019/T003/T017** porque corrige `testpaths` y afecta cómo se mide la regresión de todas las tareas siguientes (si se implementa T019/T003 antes de T016, sus pruebas nuevas en `core/` o `apps/` podrían quedar con el mismo problema de visibilidad que ya encontramos).
5. **SEC-T019** (DEC-005) — depende de SEC-T001 (ya cerrada); sin cambio de orden.
6. **SEC-T003** (DEC-008) — con el hallazgo de esta sesión, **ya no depende de ningún trabajo de frontend**; puede proceder apenas se apruebe DEC-008 tal como está, sin esperar nada adicional.
7. **SEC-T017** — correcto mantenerla al final de este bloque: depende de SEC-T002/T003/T005/T013; las primeras tres ya están cerradas, solo falta T003.
8. **SEC-T021** (DEC-007) — depende exclusivamente de una respuesta humana (DEC-007), no de ningún trabajo técnico; puede resolverse en cualquier momento, en paralelo a todo lo anterior.

**Orden final recomendado:** T007 → T009 → T010 → **T016** → T019 → T003 → T017, con **T021 en paralelo** (no bloquea ni es bloqueada por las demás).

## Tareas que requieren autorización adicional para tocar frontend o infraestructura

- **SEC-T009**: requiere que el frontend migre de `archivo_memorando_firmado_path` a `download_url` en la vista de declaratorias — **cambio de frontend real, pequeño y acotado, identificado aquí, no autorizado ni ejecutado**.
- **SEC-T010**: requiere que el frontend actualice su manejo de errores global al nuevo formato `{"error": {...}}` — **cambio de frontend real, de mayor alcance (afecta todos los endpoints), identificado aquí, no autorizado ni ejecutado**.
- **SEC-T003**: **no requiere cambio de frontend**, contrario a lo asumido originalmente (ver DEC-008).
- **SEC-T019**: requiere decidir si se provisiona almacenamiento/cuarentena adicional (infraestructura menor, dentro del volumen ya existente, no un recurso nuevo).
- El resto (T007, T016, T021) no tocan frontend ni infraestructura.

---

## SEC-T015 — Revisión de lo ya configurado y checklist para cuando el repo esté en GitHub

Revisé `.github/workflows/security.yml`, `.github/safety-policy.yml` y `.github/dependabot.yml` (ya creados y verificados localmente en la sesión anterior). Siguen correctos: `dependabot.yml` apunta a `/backend` (donde realmente está `requirements.txt`), sin claves inválidas (`automerge`/`reviewers` inventados correctamente omitidos); `security.yml` referencia `.bandit` (ya corregido a YAML válido) y la política de `safety` (ya fuerza la evaluación de rangos no fijados).

**Checklist para cuando el repositorio esté disponible en GitHub** (ninguno de estos puntos se puede verificar desde este entorno):

- [ ] Confirmar que Dependabot aparece como activo en la pestaña "Insights → Dependency graph → Dependabot" del repositorio.
- [ ] Confirmar que el workflow `security.yml` se dispara en el primer PR/push real.
- [ ] Revisar el resultado real del job `safety` (¿sigue en 2 vulnerabilidades de `pytest`/`black`, o cambió por actualizaciones de paquetes desde esta sesión?).
- [ ] Revisar el resultado real del job `bandit` (¿sigue siendo solo el hallazgo LOW de `seed_initial_data.py`?).
- [ ] Revisar el resultado real del job `gitleaks` — **esta sesión nunca pudo ejecutarlo**, es la primera vez que correrá de verdad.
- [ ] Guardar como evidencia real los logs/capturas de esa primera ejecución en `docs/09-calidad/ci-seguridad.md`, reemplazando las notas de "no verificable en este entorno" por resultados reales.

No se hizo push ni se publicó nada en esta sesión.
