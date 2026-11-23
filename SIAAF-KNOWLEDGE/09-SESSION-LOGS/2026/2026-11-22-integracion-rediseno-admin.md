---
system: SGT-SIAAF
type: session-log
date: 2026-11-22
agent: claude-code
branch: feat/integracion-rediseno-admin (base origin/develop 704d696)
commits: [31ad3b2, c436b29, 8e3935f, 1310e00, 8fa133a, d1cd9d2, 7307c69, 6a37b96, 83cdaef, 610bb4b, 227975c, 121f44f, dfab27c, 4f78caf, 97fb720]
---

# Sesión 2026-11-22: integración del rediseño del administrador

## Objetivo y autorización

R0yalCode autorizó el 2026-11-22 la integración controlada de la corrección de notificaciones y de los 14 bloques, en modalidad centralizada DK-010. La ejecución material corresponde a Claude Code. La autorización excluye desplegar en el puerto 8000, producción, releases, tags y `production.py`.

La correspondencia tarea ↔ responsable ↔ commit ↔ archivos está en `docs/frontend/PLAN_DESIGN_SYSTEM_DK010.md`. ADM-5 es el commit que contiene esta bitácora.

## Método

- Worktree propio desde `origin/develop` (`704d696`); el árbol principal no se modificó.
- Cada bloque se copió por rutas explícitas. Los archivos con dos capas se separaron antes de ADM-3 y ADM-4.
- Cada commit se creó solo si typecheck y Vitest coincidían con el ensayo.
- `1310e00` se incorporó con `git merge --no-ff` (`8fa133a`), sin modificarlo.

## Pruebas ejecutadas (resultados reales)

| Validación | Resultado |
|---|---|
| Lint, typecheck y build | Correctos |
| Vitest en serie | 544 pasaron, 0 fallan |
| Backend SQLite (`src/apps src/core tests`) | 1040 pasaron, 14 omitidas |
| PostgreSQL 16 desechable (`tests/` y ámbito de notificaciones) | 102 pasaron |
| Notificaciones | 139 pasaron |
| Suites RBAC/IDOR (14 archivos) | 321 pasaron |
| Contrato de errores OpenAPI | 21 pasaron |
| `spectacular --validate` | 0 errores; esquema idéntico a `openapi.yaml` |
| `makemigrations --check` | Sin cambios |
| Imagen Docker y Nginx aislados | Bundle con el rediseño; `nginx -t` correcto; rutas 200 |
| Login, MFA y JWT con cuentas desechables | Sin token antes del TOTP; TOTP erróneo rechazado; tokens sin firma, alterados o inválidos, 401 |
| Notificaciones de los cinco roles | 200, solo avisos en su ámbito; acceso a avisos ajenos, 404 |
| Permisos por rol | Estudiante accede a `mi-tramite` y `perfil-academico`; funcionarios y administrador, 403; `RESPONSABLE_DEPENDENCIA`, 403 |
| Interfaz del administrador | Login real, 1440, 820 y 390 px, sin overflow ni errores de consola |
| Entorno real | Contenedores, volúmenes, imagen y conteos sin cambios |

Por bloque: DS-A 475, DS-B 489, DS-E 482 y 7 fallos, EST-2 501 y 6 fallos, DS-C 524, DS-D 539, ADM-1 a ADM-4 539 y final 544.

## Desviaciones y observaciones

- Hay un merge interno adicional (`8fa133a`) para incorporar la corrección sin reescribir commits.
- ADM-3 falló 2 pruebas de `LoginPage` en su primer intento y pasó en el segundo. Las suites de layout, login y MFA pasaron después 5 de 5 rondas. Se trata como la intermitencia conocida de esas pruebas por tiempos de espera.
- La primera petición a `/` de la pila aislada devolvió `000` porque Nginx acababa de arrancar. Repetida con espera, respondió 200.
- `siaaf-modern.css` cita `docs/paleta_colores_institucionales`, carpeta no versionada aquí; `DESIGN_SYSTEM.md` §11 lo aclara.
- La imagen validada apunta al API desechable (`127.0.0.1:18080`) y no sirve para el puerto 8000.

## Pendientes y bloqueos

- Incidencias INC-NOTIF-01 a 03 y tarea PROD-ACAD-01 en [[BLOCKED_TASKS]].
- El despliegue en el puerto 8000 requiere una autorización independiente y una decisión sobre la landing local.
- El árbol principal conserva sus cambios locales, incluidos los ya integrados, hasta que se reconcilie.

## Notas de la bóveda actualizadas

[[BLOCKED_TASKS]] · [[CURRENT_STATE]]
