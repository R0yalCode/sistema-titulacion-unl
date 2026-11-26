---
system: SGT-SIAAF
type: session-log
date: 2026-11-26
agent: claude-code
branch: docs/rescate-arbol-principal (base origin/develop 625c448)
commits: [9808bb0, d2ed3eb, 1ac3659, 8d1e9ee, 48f7ba6]
---

# Sesión 2026-11-26: fase 0, rescate del árbol de trabajo principal

## Objetivo y autorización

R0yalCode pidió revisar los cambios locales del árbol principal (`sgt-siaaf/`, rama `feat/dashboard-estudiante`), rescatar los útiles y consolidarlos en `develop` sin perder trabajo, antes de iniciar la siguiente fase (accesibilidad, sidebar, menú de perfil y asistente IA).

Ese mismo día decidió:

- **`DOCUMENTACION/`:** versionarlo en su ruta, marcado como histórico.
- **Prototipos:** versionar las vistas de error y los paneles Liquid Glass saneados.
- **Opcionales:** incorporar `dependabot.yml` y las dos imágenes de referencia.

**Pendiente de autorización:** publicar la rama, fusionarla en `develop` y limpiar ramas.

## Estado inicial (verificado)

- `develop` = `origin/develop` = `625c448`, sin divergencia; `main` (`d04094e`) 119 commits por detrás.
- Árbol principal en `feat/dashboard-estudiante` (`27289fa`), 72 commits por detrás de `develop`, con 255 entradas en `git status`:
  - 142 archivos modificados;
  - 38 borrados;
  - 75 sin rastrear, que son 193 archivos al expandir las carpetas.
- Ninguna rama tiene commits fuera de `origin/develop`.
- Seis worktrees.

## Respaldo (antes de cualquier operación)

- **Referencia Git local** `refs/respaldo/rescate-fase0-2026-11-26_162654` → commit `faa7ad5`. Se creó con un índice temporal, sin tocar el índice, el árbol ni la rama. Contiene el árbol completo: 335 archivos existentes y los 38 borrados.
  - Verificado blob a blob: 0 diferencias de 335.
  - `git status` quedó idéntico antes y después.
  - **No se publica:** contiene el dataset original, que no es publicable.
- **Copia en disco** `~/Respaldos/sgt-siaaf/2026-11-26_162654-rescate-fase0/`:
  - `archivos.tar` y `sha256.txt` (335 archivos; `sha256sum -c` correcto);
  - `tracked.diff` (binario), `status.txt` y `rutas.txt`.

## Clasificación de las 373 rutas

Método:

1. Comparar cada ruta con `origin/develop`.
2. Si difiere, buscar si el contenido coincide con una versión histórica de alguna rama.
3. Revisar el diff línea a línea.

| Grupo | Rutas | Resultado |
|---|---:|---|
| Modificados idénticos a `develop` | 115 | **B**: ya integrados por bloques (Design System, portal, perfil académico, panel del administrador) |
| Sin rastrear idénticos a `develop` | 100 | **B** |
| Borrados que `develop` también borró | 7 | **B** (`Header`, `Sidebar`, `AppLayout.module.css`, etc.) |
| Modificados distintos de `develop` | 27 | **C/E**: versiones **anteriores** |
| Sin rastrear distintos de `develop` | 22 | **C/E**: versiones **anteriores** |
| Borrados que `develop` conserva | 31 | **F**: no se aplican |
| Nuevos (no existen en `develop`) | 71 | **G**: 69 incorporados; 2 descartados |

Los 49 archivos que difieren de `develop`:

- **Frontend** (`AppShell`, `AppLayout`, `StudentLayout`, `router.tsx`, `KpiCard`, `BandejaPage`, `DetalleFuncionarioPage`, `ExpedientePage`, `PeticionesPage`, `SeguimientoPeticionPage`, `StudentDashboardPage`, `AdminDashboard`, `tokens.css` y sus pruebas): son anteriores al rediseño Liquid Glass y a las páginas de error.
  - Les faltan `glass`, `HeroPanel`, `QueryErrorView`, `SessionExpiredPage`, DEC-17 y `AlertaPlazos`.
  - Incorporarlos revertiría LG-A…E y ER-A…E.
  - Ninguna línea propia del árbol aporta funcionalidad ausente en `develop`.
- **Backend:** son menos seguros que `develop`.
  - `production.py` no tiene la prohibición de MockSGA ni las validaciones de correo.
  - `entrypoint.sh` no registra el entorno.
  - `seed_mock_sga.py` no exige el entorno de demostración.
- **Dataset original** (`entorno_pruebas/dataset.py`, `seed_sgt_siaaf.py`, `docs/entorno-pruebas/dataset-sgt-siaaf.md` y sus pruebas): **no publicable** (repositorio público, PR #31). `develop` ya tiene la versión sintética.
- **Documentación** (`README.md`, `DESIGN_SYSTEM.md`, `PLAN_DESIGN_SYSTEM_DK010.md`, `BLOCKED_TASKS.md`, `DOCUMENT_TRACEABILITY.md`, `clarify.md`, ADR 0010 y `perfil-academico-mock-sga.md`): son borradores previos a los de `develop`.
  - Ejemplos: «PROPUESTA pendiente» o «sin commit», y una política de MockSGA en producción ya endurecida.
- **`DISENO_FUNCIONAL_MODALIDADES_TITULACION.md`:** solo cambia el formato de una tabla en una fuente original (`90-ORIGINAL-SOURCES` no se edita).
- **`.obsidian/appearance.json`:** preferencia local de la interfaz.

**Borrados no aplicados (31):**

- El kit B antiguo de `prototipos/vistas-errores-unl/` (`paginas/`, `assets/`, `capturas/`, `galeria`, `formularios`, `index`, `README`). Lo citan la spec 08, `tasks.md`, `frontend/docs/assets-mascotas.md`, `prototipos/README.md` y DEC-15.
- `docs/ENTORNO_DESARROLLO.md`.

## Commits (rama `docs/rescate-arbol-principal`; autor y committer R0yalCode)

No es modalidad centralizada: es el rescate del trabajo del propio responsable.

| Commit | Contenido |
|---|---|
| `9808bb0` | `DOCUMENTACION/`: 53 archivos sin cambios y un `README.md` que lo marca como histórico no vigente (DK-014). Resuelve el pendiente 7 de CURRENT_STATE (parte de `DOCUMENTACION/`). |
| `d2ed3eb` | 8 vistas de error de referencia de ER-A…E, junto al kit B (no lo sustituyen), y la nota de `prototipos/README.md` sobre dependencias externas y el correo de soporte inventado. |
| `1ac3659` | 5 paneles Liquid Glass **saneados**: 29 personas, 6 correos y 14 cédulas sustituidos por marcadores sintéticos (91 líneas). Cero restos en el barrido posterior. |
| `8d1e9ee` | `.github/dependabot.yml` con `target-branch: develop` (sin esa línea, los PR irían a `main`). |
| `48f7ba6` | `referencia_login.png` (SAC, variante SGA Estudiantes; no duplica `sac-login.png`) y `color-palette-base-login.png`. |
| (este) | Bitácora y CURRENT_STATE. |

**Fuera de la integración** (solo en el árbol principal y en el respaldo):

- `.claude/launch.json` (configuración local de herramienta);
- `docs/paleta_colores_institucionales/requisito-art235-03-idioma-b1.pdf` (documento ficticio de pruebas guardado en una carpeta que no le corresponde);
- los 49 archivos anteriores descritos arriba.

## Verificaciones (ejecutadas sobre el HEAD de la rama, exportado)

- **Alcance:** el frontend y el backend son idénticos a `origin/develop` (`git diff --name-only origin/develop..HEAD -- frontend backend` = 0). Son 71 archivos solo de documentación, recursos y configuración.
- **Frontend:** `lint` 0, `typecheck` 0, `build` OK.
  - En 5 ejecuciones completas de `test` sobre esta rama, 3 dieron 600/600 y 2 tuvieron un fallo: `router.test.tsx` (/estudiante) en una y `router.errores.test.tsx` (403) en otra.
  - En la línea base limpia de `develop` también hubo un 598/600 en la primera ejecución.
  - Causa: se agota el tiempo de `findByRole` (1 s) en rutas cargadas de forma diferida con la máquina cargada. Es intermitencia preexistente, no una regresión.
- **Backend:** pytest en el contenedor `sgt-siaaf-backend:latest` sobre el repositorio exportado completo: 1263 pasadas, 26 omitidas, 0 fallos. Hubo un primer intento que montó solo `backend/`, con 4 fallos porque esas pruebas leen `nginx/`, compose y el Dockerfile.
- **Seguridad:** gitleaks v8.24.3 (la imagen del CI) sin hallazgos, tanto en los commits nuevos como en los directorios nuevos.

## Pendientes

- Autorización para publicar la rama y fusionarla en `develop` (`--no-ff`). `main` no se toca.
- Limpieza de ramas (DK-013): ver el informe de la sesión. `feat/dashboard-estudiante` y su árbol se conservan hasta que el responsable dé por válido el respaldo.
- La intermitencia de la suite frontend sigue abierta.
- Pendiente 7 de CURRENT_STATE: `.github/workflows/` ya estaba versionado; `DOCUMENTACION/` queda resuelto con esta rama.
