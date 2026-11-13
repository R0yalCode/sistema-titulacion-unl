---
system: SGT-SIAAF
type: session-log
date: 2026-11-12
agent: claude-code
branch: develop (sin commits; cambios locales pendientes de revisión)
commits: []
---

# Sesión 2026-11-12 — Reorganización estructural del repositorio (DK-014)

## Objetivo

Reorganizar el repositorio según la auditoría estructural y las decisiones expresas del responsable (R0yalCode, 2026-11-12). Había que separar el código, el sitio Quarto publicado (`docs/`) y la bóveda (`SIAAF-KNOWLEDGE/`), y eliminar la documentación antigua y los duplicados autorizados. Todo debía quedar sin commits, push, merges ni cambios de rama, preservando los cambios locales previos.

La tarea se ejecutó en **dos partes**. Un reinicio de la máquina interrumpió la primera (fases 0 a 4) después de aplicar los cambios y antes de escribir esta bitácora y el informe. El reinicio borró el inventario inicial y las salidas de validación de la primera parte, que estaban en el directorio temporal. Por eso **todas las validaciones de esta nota se ejecutaron de nuevo en la segunda parte** sobre el estado final.

## Estado inicial

- Rama `develop`, `HEAD` = `5ef0dbd`; cambios locales previos: unas 148 entradas, de ellas **136 borrados locales de Quarto**: 133 en `docs/.quarto/`, 2 en `docs/_site/` y `docs/ENTORNO_DESARROLLO.md`.
- Trabajo ajeno protegido (no tocado): `README.md`, `SIAAF-KNOWLEDGE/.obsidian/appearance.json`, `SIAAF-KNOWLEDGE/90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/DISENO_FUNCIONAL_MODALIDADES_TITULACION.md` y `backend/entrypoint.sh` (cambio de permisos 644→755). Se tomaron sus SHA-256 al inicio de la segunda parte y se compararon al final: coinciden.

## Cambios (rutas)

**Primera parte (fases 0 a 4)**

- Eliminados (autorizados): `auditoria/` (8 MD rastreados), `docs/academico/` (1 MD sin rastrear) y `gh-pages/` (sin rastrear; copia exacta de `docs/_site` de `HEAD` más `.nojekyll`, sin consumidores).
- OpenAPI: se eliminó `backend/contracts/openapi.yaml`, un subconjunto desactualizado desde INC-01 (17 de 18 operaciones y 31 de 34 esquemas). El canónico es `backend/openapi.yaml`. Referencias corregidas en `docs/04-api/introduccion.md`, `docs/08-infraestructura/mantenimiento.md`, `docs/anexos/{decisiones,referencias}.md`, `sgt-siaaf/specs/003-frontend-titulacion/clarify.md`, [[API_CONTRACTS]], [[DOCUMENT_TRACEABILITY]] (C-23) y [[SOURCE_CATALOG]].
- Binarios y configuración de gitleaks: se eliminaron `backend/gitleaks.exe`, `backend/LICENSE` (la licencia MIT de gitleaks, «Zachary Rice», no la del proyecto) y `backend/.gitleaksignore`, cuya configuración era inválida y anulaba las reglas. Se creó `.gitleaks.toml` en la raíz.
- Workflows: `security.yml` corregido (`GITHUB_TOKEN`, permisos mínimos, también se ejecuta en `develop`); `publish-quarto.yml` con permisos por job (genera en el runner y despliega con Actions → Pages); `ci.yml` nuevo (frontend y deriva del contrato OpenAPI).
- `.gitignore`: se añadieron `docs/_site/`, `docs/.quarto/`, `gh-pages/`, `frontend/coverage/`, `*.exe`, `.DS_Store` y `*.swp`.

**Segunda parte (fases 5 y 6)**

- `backend/README.md`: el README de gitleaks (513 líneas, que llegó en `19c98fe`; hallazgo AUD-P3-06) se sustituyó por el README real del backend. Explica la estructura, el desarrollo local, las pruebas, el contrato OpenAPI y la detección de secretos con `.gitleaks.toml`. Era lo único útil del README de gitleaks para el proyecto.
- `.github/workflows/ci.yml`: las claves literales `SECRET_KEY` y `JWT_SIGNING_KEY` se sustituyeron por claves aleatorias generadas en el runner. gitleaks las marcaba como `generic-api-key` (L43-44) y habrían hecho fallar `security.yml` en cuanto se versionara `ci.yml`.
- `.gitleaks.toml`: la exclusión de `docs/(_site|.quarto)/` ahora también vale para las rutas absolutas del modo `dir`. La excepción `cafebabe:deadbeef` se **mantiene** con un comentario: sin ella, el análisis del historial encuentra el ejemplo de `sidekiq-secret` del antiguo README de gitleaks (`19c98fe`, `backend/README.md` L50).
- `docs/09-calidad/ci-seguridad.md` (gitleaks usa `.gitleaks.toml`; también se ejecuta en `develop`) y `docs/09-calidad/resultados-validacion.md` (nota sobre la copia retirada).
- Bóveda: [[DECISIONS_LOG]] (DK-014, punto 6), [[CURRENT_STATE]] (I-4 resuelta), [[ADR_INDEX]] (ADR canónicos), [[SOURCE_CATALOG]] (fila de README) y esta nota.

## Investigado y conclusiones (fase 5)

- **Scripts Python de la raíz:** se conservan (propuesta pendiente):
  - `audit_complete.py`, `audit_tasks.py`, `check_t047.py` y `verify_matrix.py` son verificaciones puntuales de `specs/001/tasks.md` (T001-T046), resueltas con rutas relativas a la raíz. Se ejecutan correctamente.
  - `check_files.py` y `verify_all_tasks.py` tienen fija una ruta de Windows (`C:\Users\DELL\...`) y no funcionan en este entorno.
  - Su único consumidor es una mención en `DOCUMENTACION/00_AUDITORIA/INVENTARIO_PROYECTO.md`, que no se rastrea. Ningún workflow, script ni prueba los usa.
- **`Documentacion-parte-2/`** (12 MD rastreados y un `index.html` sin rastrear) duplica `90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/`:
  - 11 archivos son idénticos byte a byte.
  - `DISENO_FUNCIONAL_MODALIDADES_TITULACION.md` solo difiere por el formato de una tabla, que es el cambio local ajeno y protegido de la bóveda; contra `HEAD` es idéntico.
  - El `README.md` solo está en la bóveda.
  - `index.html` es una salida de Quarto 1.11.9 suelta.
  - Unos 10 documentos lo citan.
  - No se trasladó ni se eliminó nada (instrucción expresa).
- **LICENSE:**
  - El canónico es `LICENSE` de la raíz (MIT, «Copyright (c) 2026 Royel»).
  - `backend/LICENSE` era la licencia de gitleaks y se retiró junto con el binario.
  - `frontend/coverage/readex-pro-license.txt` es la licencia de una fuente, dentro de un informe de cobertura rastreado.
- **ADR:**
  - El conjunto canónico es `backend/docs/adr/`: contiene 0001, 0002, 0003 y 0009, y es la ruta que fija `clarify.md` §2.
  - `docs/adr/0001` y `0002` son versiones anteriores con contenido distinto, no solo de formato.
  - No se consolidaron porque `specs/001` (intocable) y otras páginas consumen ambas rutas.
  - El ADR-0003 dice que el token de acceso dura 60 min, pero el código usa 30 min (ya registrado en [[ADR_INDEX]]).

## Pruebas ejecutadas (comando → resultado real, segunda parte)

| Validación | Comando | Resultado |
|---|---|---|
| Sintaxis de workflows | `rhysd/actionlint:1.7.7 -no-color` (Docker) | exit 0, sin hallazgos |
| Secretos, historial | `gitleaks:v8.24.3 git /repo --config .gitleaks.toml` | 87 commits, **no leaks found** |
| Secretos, archivos versionables | `gitleaks dir` sobre la copia de `git ls-files -co --exclude-standard` (1320 archivos) | **no leaks found** |
| Secretos, árbol completo | `gitleaks dir /repo` | 2 coincidencias en `SIAAF-KNOWLEDGE/.obsidian/plugins/vault-as-mcp/main.js` (JS minificado de un plugin local, ignorado por Git): no son credenciales |
| Contrato OpenAPI | `manage.py spectacular --validate` en `sgt-siaaf-backend:latest`, con el código montado en solo lectura y sin red | 0 errores, 2 advertencias preexistentes (`get_evaluado_por` sin anotación de tipo; colisión de `operationId` en `peticiones_documento_retrieve`); `diff` con `backend/openapi.yaml`: **idéntico** |
| Sitio Quarto | `quarto render` (`ghcr.io/quarto-dev/quarto:1.11.9`) sobre una **copia** de `docs/` en el directorio temporal | exit 0, sin advertencias; 117 HTML / 145 archivos. No se generó dentro de `docs/` para no recrear los borrados preservados |
| Frontend | `npm run lint`, `typecheck`, `test`, `build` | todo exit 0; **441/441** pruebas (70 archivos) |
| Backend | `pytest -q -p no:cacheprovider` (contenedor, solo lectura) | **637 aprobadas, 13 fallidas**, todas en `test_pdf_generator.py`. La imagen no tiene `pypdf` ni librerías equivalentes y la extracción de texto devuelve `''`. Es un fallo conocido del entorno ([[2026-11-12-i3-archivos-huerfanos]]: «13 `pypdf`»), sin relación con esta tarea |
| Referencias rotas | `grep` de las rutas eliminadas | Corregidas las de estado vigente. Las restantes están en documentos históricos (informes de auditoría con fecha, sprint S1, bitácoras, `BUILD_REPORT`, `INITIAL_DIAGNOSTIC`, `COSMOS_REGISTRO.json`), en `specs/001` (intocable) o en `DOCUMENTACION/` (sin rastrear), y no se reescriben |

## Inventario de los artefactos de Quarto rastreados (sin cambios)

| Ruta | Rastreados | Borrados localmente | En disco | Modificados |
|---|---|---|---|---|
| `docs/_site/` | 139 | 2 | 137 | 0 |
| `docs/.quarto/` | 355 (181 `xref`, 110 `idx`, 57 `quarto-session-temp…`, 6 `project-cache`, 1 `preview`) | 133 | 222 | 0 |
| **Total** | **494** | **135** | **359** | 0 |

El `docs/_site` versionado está desactualizado (último commit `8e1e1a2`, 2026-11-10). Al compararlo con el sitio recién generado, le faltan 8 páginas actuales (`auditorias/*I3*`, `planificacion-backend/*`), conserva 3 archivos obsoletos, y 110 de sus 136 archivos comunes difieren. **No se ejecutó `git rm --cached`** (pendiente de autorización).

## Decisiones (→ DECISIONS_LOG / ADR)

- [[DECISIONS_LOG]] DK-014 (puntos 1 a 6).

## Notas de la bóveda actualizadas

[[DECISIONS_LOG]], [[CURRENT_STATE]], [[API_CONTRACTS]], [[DOCUMENT_TRACEABILITY]], [[SOURCE_CATALOG]], [[ADR_INDEX]].

## Pendientes y bloqueos (requieren autorización del responsable)

1. Retirar del índice (`git rm --cached`) los 494 artefactos de `docs/_site/` y `docs/.quarto/`. En el informe de la sesión se explica qué efecto tendría.
2. Configurar GitHub: **Settings → Pages → Source = «GitHub Actions»**. Sin eso, `publish-quarto.yml` no despliega. No se pudo comprobar desde aquí.
3. Scripts de la raíz: proponer que los cuatro funcionales pasen a `scripts/spec001/` y que se retiren los dos con ruta de Windows (o se corrijan).
4. Retirar `.gitleaksignore` de la raíz (rastreado desde `19c98fe`). gitleaks lo lee automáticamente y lo marca como inválido (`Invalid .gitleaksignore entry`, 13 entradas que no son *fingerprints*). No rompe el análisis, pero es ruido y además engaña, porque no exime nada.
5. Retirar `frontend/coverage/` del índice: 126 archivos rastreados (`467ec3b`, `aae0c4c`) en una ruta que ahora está en `.gitignore`.
6. `Documentacion-parte-2/`: decidir si se elimina (la copia de la bóveda es la fuente) y qué se hace con su `index.html` suelto.
7. `docs/adr/0001-0002`: decidir si se retiran en favor de `backend/docs/adr/`. Habría que actualizar los consumidores, salvo `specs/001`.
8. CI: `ci.yml` no ejecuta `pytest` del backend. Incorporarlo exige resolver antes la dependencia de `pypdf` de `test_pdf_generator.py`.
9. Commit de la reorganización según el Flujo Git: rama `docs/` o `build/` desde `develop`, autoría y merge.

## Fuentes originales relacionadas

`backend/openapi.yaml`, `.github/workflows/`, `.gitleaks.toml`, `docs/_quarto.yml`, `backend/docs/adr/`, `docs/adr/`, `Documentacion-parte-2/`.

## Tercera parte: operaciones autorizadas tras la revisión (2026-11-12)

Autorización expresa del responsable para los puntos 1 a 7 de la lista de pendientes anterior y para evaluar las carpetas de prototipos. Sin commits, push, merges ni cambios de rama.

### Operaciones

| Operación | Resultado | Cómo queda en Git |
|---|---|---|
| Retirar del índice `docs/_site/` (139) y `docs/.quarto/` (355) | `git rm -r --cached`. Los 359 archivos que había en disco siguen en él (SHA-256 verificados). Los 135 que ya estaban borrados en local no se restauraron | 494 `D ` preparados |
| Retirar del índice `frontend/coverage/` (126) | Mismo procedimiento. Son el informe HTML de istanbul (`npm run test:coverage`); la configuración está en `vitest.config.ts`, que no se tocó. Los 135 archivos que hay en disco están intactos | 126 `D ` preparados |
| Eliminar `Documentacion-parte-2/` | 11 MD con el mismo SHA-256 que la bóveda. `DISENO_FUNCIONAL_…` es igual a `HEAD`; la versión protegida (`b448bc…`) solo existe en la bóveda y no se tocó. La diferencia era solo de espaciado de tabla. `index.html` era igual a `docs/_site/index.html` | 12 ` D` sin preparar (`index.html` no estaba rastreado) |
| Mover 4 scripts a `scripts/spec001/` | `mv` sin cambios; mismos SHA-256 y misma salida antes y después. README nuevo. `check_files.py` y `verify_all_tasks.py` siguen en la raíz | 4 ` D` + `scripts/spec001/` sin rastrear |
| Retirar `.gitleaksignore` | Tenía 13 entradas inválidas; todo lo que pretendía cubrir ya lo cubre `.gitleaks.toml`. Ningún workflow ni script lo usaba. `security.yml` declara ahora `GITLEAKS_CONFIG: .gitleaks.toml` | 1 ` D` |
| `pypdf` | Se añadió `pypdf>=7.0,<8.0` a `backend/requirements-dev.txt`, que solo se instala en el target `development`; producción no cambia. pip-audit no encuentra vulnerabilidades en 6.21.4, 7.0.0 ni 7.0.1. Imagen de comprobación `sgt-siaaf-backend:verificacion-pypdf` (pypdf 7.0.1, `pip check` correcto); `:latest` sin cambios | ` M` |
| CI del backend | `ci.yml`: job `backend` (SQLite: `src/apps`, `src/core` y `tests/`, informe JUnit) y job `backend-postgres` (servicio `postgres:16` efímero: `tests/`). Sin secretos del repositorio, claves generadas en el runner, `contents: read` | (archivo sin rastrear) |
| Prototipos | `SGT_SIAAF_Prototipo_HTML_CSS_JS/SGT_SIAAF_Prototipo_Web/` → `prototipos/prototipo-general/`; `SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/SGT_SIAAF_Errores_HTML_UNL/` → `prototipos/vistas-errores-unl/`. Solo se quitó la carpeta envoltorio del ZIP; los 40 archivos son idénticos (SHA-256). 25 referencias actualizadas en 11 documentos vigentes | 40 ` D` + `prototipos/` sin rastrear |
| ADR | Sin cambios (decisión del responsable): `backend/docs/adr/` y `docs/adr/` se mantienen hasta resolver las referencias de `specs/001` | — |

Referencias operativas a `Documentacion-parte-2/` actualizadas: README de `90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/`, [[ADR-KB-001-fuentes-originales]] (punto 3), [[KNOWLEDGE_MAINTENANCE]] (nuevo control de integridad contra `5ef0dbd`, que detecta como única diferencia el cambio local protegido), `10-REFERENCES/DOCUMENTATION.md` y [[SOURCE_CATALOG]]. `scripts/cosmos/cosmos.py` **conserva** `Documentacion-parte-2/` en sus prefijos documentales, porque sigue haciendo falta para clasificar este borrado como cambio solo documental (DK-005). Las bitácoras, los informes históricos, `INITIAL_DIAGNOSTIC`, `BUILD_REPORT` y los `source_file` de las notas `DP2-*` no se reescriben: registran la procedencia.

### Evaluación de los prototipos

| | A: `prototipo-general/` | B: `vistas-errores-unl/` |
|---|---|---|
| Contenido | 10 archivos: `index.html`, `app.js`, `styles.css`, 2 SVG, `INICIAR_WINDOWS.bat`, README y 3 documentos (`docs/`) | 30 archivos: 12 HTML (índice, galería, formularios y 9 páginas), `site.css`, `site.js`, 5 mascotas PNG, favicon SVG, 8 capturas y una miniatura general, README |
| Funcionalidad | Maqueta navegable de 9 vistas con perfiles ficticios y `sessionStorage` | Vistas 401, 403, 404, 500 y 503 y avisos 409, 412 y 428 en formulario; botones de demostración |
| Estado en React | V-01 a V-09 implementadas total o parcialmente (`router.tsx`) | 401, 403, 404, 500 y 503 implementadas. **409, 412 y 428 no** (FE-T1213 bloqueada por BE-11) |
| Duplicados | No comparte archivos con B | Las 5 mascotas son idénticas a `frontend/public/assets/mascotas/`; las de B son los **originales** cuya procedencia se exige conservar (DEC-15) |
| Referencias | `AGENTS.md` (regla 4), `clarify.md` DEC-11, `specify.md`, especificaciones UI 01, 02 y 04 | Además: especificación UI 08, `tasks.md`, `frontend/docs/assets-mascotas.md` |
| Clasificación | Referencia histórica útil, vigente como referencia visual | Prototipo vigente y reutilizable como referencia (único diseño de 409, 412 y 428) |

Validación: 155 enlaces locales de los HTML sin ninguno roto; 12 recursos servidos con HTTP 200 desde un servidor local temporal; `node --check` correcto en `app.js` y `site.js`. Ninguna de las dos carpetas está ignorada por Git.

### Pruebas (tercera parte)

- Backend, con la imagen que incluye pypdf y el código en solo lectura: `test_pdf_generator.py` **30/30**; suite configurada **650/650** (los 13 fallos desaparecen); `src/apps`, `src/core` y `tests/` juntos **780 aprobadas y 13 omitidas** (las `postgres`).
- PostgreSQL 16.15 desechable (red Docker propia, sin volumen, contraseña aleatoria): pruebas `-m postgres` **13/13** y `tests/` **37/37**.
- Ejecutar `src/apps` contra PostgreSQL da 8 fallos. Esas 8 pruebas de índices consultan `sqlite_master`, una tabla interna de SQLite, así que solo son válidas con SQLite. Por eso `backend-postgres` ejecuta únicamente `tests/`. Es un hallazgo preexistente: la bitácora I-3 contaba 21 fallos, 13 de ellos por pypdf.
- actionlint: 0 errores en 3 workflows. gitleaks: historial (87 commits) y 824 archivos versionables sin fugas. En el árbol personal ignorado hay 2 coincidencias en `.obsidian/plugins/vault-as-mcp/main.js`: son identificadores de JS minificado (`tokenizeClass=…`, `writeSetTokens=…`) de un plugin de terceros, no credenciales; no se tocaron ni se leyó su configuración.
- Quarto (copia): 0 advertencias, 117 HTML, ningún artefacto rastreado. OpenAPI: 0 errores, contrato idéntico. Frontend: lint, tipos y build en verde, 441/441.

### Pendientes

- `README.md` (protegido, ajeno) menciona `.gitleaksignore` en el árbol del proyecto (L300); conviene que lo actualice su autor.
- `check_files.py` y `verify_all_tasks.py`: decidir si se corrigen o se retiran.
- Pruebas de índices de `src/apps` dependientes de SQLite: decidir si se hacen portables.
- `docs/adr/` frente a `backend/docs/adr/`: resolver las referencias de `specs/001`.
- GitHub Pages → Source = «GitHub Actions» (manual).
- Commit de la reorganización según el Flujo Git.

## Preparación de la integración (2026-11-12)

Rama `build/reorganizacion-estructural` creada desde `develop` (`5ef0dbd`) con `git switch -c`. Índice (modos y blobs), 732 entradas y referencias de `develop`/`main`/`origin` verificados sin cambios. Sin commits ni push.

### Hallazgos de CI que preceden a DK-014 (no corregidos)

Los workflows nunca se habían versionado (no hay ninguno en `HEAD` ni en el historial), así que estos fallos aparecerán en su primera ejecución:

| Job | Hallazgo | Comprobación |
|---|---|---|
| `security.yml` → `safety` | `CVE-2025-71176` en `pytest` (rango afectado `<9.0.3`; declarado `pytest>=8.4,<9.0`) | `safety check` 3.8.1 con la política del repositorio: código de salida 64, igual con y sin `pypdf` |
| `security.yml` → `safety` | `CVE-2026-32274` en `black` (`>=24.3.0,<26.3.1`; declarado `black>=25.1,<26.0`) | Ídem |
| `security.yml` → `bandit` | `B105 LOW` en `seed_initial_data.py:60` (`PASSWORD_DEMO`, contraseña de las cuentas de demostración) | bandit 1.9.4, código de salida 1. Ya estaba documentado como conocido en `docs/09-calidad/ci-seguridad.md` |

### Propuesta técnica (sin aplicar; requiere autorización)

1. **Dependencias:** en `backend/requirements-dev.txt`, `pytest>=9.0.3,<10.0` y `black>=26.3.1,<27.0`. Se comprobó en un contenedor con requisitos temporales fuera del repositorio:
   - se instalan pytest 9.2.0, pytest-django 4.14.0, pytest-cov 7.1.0 y black 26.10.1, y `pip check` no da errores;
   - **780 aprobadas y 13 omitidas** como usuario sin privilegios;
   - `safety check` con la política del repositorio termina con **código 0**.

   Hay dos pruebas de `test_reconciliar_archivos.py` (d02 y d06) que fallan **solo como root**, también con pytest 8.4.2. Es un efecto del entorno: root puede leer los directorios que la prueba hace ilegibles. Los runners de GitHub Actions no son root. `black --check src` ya fallaba con black 25, así que el código no está formateado con black; ningún job lo exige.
2. **Bandit, sin desactivar controles:** se descartan `skips: [B105]` en `.bandit` y `--severity-level medium` en el workflow, porque reducen la cobertura en todo el código. Hay dos opciones:
   - **(a)** Un `# nosec B105` limitado a la línea 60, con justificación («contraseña de demostración académica documentada; no es una credencial de producción»). Mantiene la regla en el resto del código y bandit sigue contando la excepción en sus métricas.
   - **(b) Recomendada a medio plazo:** leer la contraseña de demostración de una variable de entorno obligatoria para `seed_initial_data`, sin valor por defecto en el código. Elimina el hallazgo de raíz, pero obliga a cambiar `docker-compose`, la documentación y el `README.md` protegido.

   Las dos modifican `backend/`, y eso requiere autorización expresa.

## Commits en `build/reorganizacion-estructural` (2026-11-13)

Autoría asignada por el responsable a sí mismo en los cinco grupos: autor y committer `R0yalCode <royel.jima@unl.edu.ec>`, la identidad Git global configurada. Commits sin push ni merge.

| Orden | Grupo | Commit | Contenido |
|---|---|---|---|
| 1 | G5 | `3cc194d` | Retirada del índice de 494 artefactos de Quarto y 126 de coverage (copias en disco conservadas) |
| 2 | G1 | `5a7b4b8` | `.gitleaks.toml`, retirada de `.gitleaksignore` (raíz y backend), `gitleaks.exe` y su LICENSE; `security.yml`, `publish-quarto.yml` y `safety-policy.yml`; `.gitignore`; scripts en `scripts/spec001/` (renombrados al 100 %) |
| 3 | G2 | `09784f9` | `pypdf` en `requirements-dev.txt`, `ci.yml`, README del backend y retirada de `backend/contracts/openapi.yaml` |
| 4 | G4 | `ccd5578` | Prototipos en `prototipos/` (40 renombrados al 100 % y README) y referencias |
| 5 | G3 | el commit que incorpora esta nota | Documentación, bóveda y retirada de `auditoria/` y `Documentacion-parte-2/` |

- **`.github/safety-policy.yml` incluido en G1** tras revisarlo: es la política SEC-T014 (`ignore-unpinned-requirements: false`), documentada en `docs/09-calidad/ci-seguridad.md` (rastreado desde `8e1e1a2`). `security.yml` la exige en `--policy-file`. No tiene datos sensibles ni del entorno, y se versionó sin cambios. `.github/dependabot.yml` sigue sin rastrear porque ningún workflow lo necesita.
- **`.gitignore`:** se actualizó el comentario que presentaba como decisión pendiente la retirada de los artefactos del índice.
- **Corrección del mensaje de `ccd5578`:** dice «25 referencias en 10 documentos». El commit contiene 23 referencias en 10 documentos; las otras 2 están en `SOURCE_CATALOG.md` (G3). No se reescribió el historial.
- **Fuera de los commits** (cambios locales que siguen pendientes):
  - los 4 archivos protegidos;
  - `docs/ENTORNO_DESARROLLO.md` (borrado preexistente);
  - `.claude/`, `DOCUMENTACION/` y `.github/dependabot.yml`.
