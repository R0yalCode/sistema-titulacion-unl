---
system: SGT-SIAAF
type: build-report
status: final
date: 2026-11-11
branch: docs/siaaf-knowledge
---

# Informe de construcción: SIAAF-KNOWLEDGE

> Solo resultados **ejecutados y comprobados**. Lo que no se hizo o no se pudo hacer se indica explícitamente.

## 1. Diagnóstico inicial
Ver [[INITIAL_DIAGNOSTIC]]. En síntesis: repo en `main` con 148 cambios locales ajenos; `main` y `origin/develop` con árboles idénticos; bóveda interna vacía y ya abierta en Obsidian; 12 documentos DP2; MCP `obsidian` conectado; sin tags; sin `gh`.

## 2. Ubicación original de la bóveda
Dos bóvedas registradas en Obsidian (`~/Documentos/SIAAF-KNOWLEDGE` y `<repo>/documentacion-original/SIAAF-KNOWLEDGE`), ambas **vacías** (solo `.obsidian/`) y **ya en la papelera** por acción previa del usuario (2026-11-11 01:01–01:02). No había notas que migrar; no se tocó la papelera (el respaldo se conserva allí).

## 3. Ubicación definitiva
`/home/royeljima/Documentos/sgt-siaaf/SIAAF-KNOWLEDGE/`: bóveda abierta en Obsidian (`obsidian.json` → `open: true`) y servida por el MCP.

## 4. Estructura final (81 archivos Markdown: 69 notas propias + 12 copias de fuentes; + 4 JSON de configuración)
| Carpeta | Notas | | Carpeta | Notas |
|---|---|---|---|---|
| 00-CORE | 8 (incluido este informe) | | 09-SESSION-LOGS | 2 |
| 01-ARCHITECTURE | 6 | | 10-REFERENCES | 14 (12 DP2-*) |
| 02-BACKEND | 2 | | 11-REGULATORY | 3 |
| 03-FRONTEND | 3 | | 12-DEGREE-PROCESSES | 9 |
| 04-REQUIREMENTS | 2 | | 13-TRACEABILITY | 3 |
| 05-EXECUTION | 2 | | 14-METRICS-AND-DASHBOARDS | 2 |
| 06-AUDITS | 2 | | 15-GIT-AND-WORKFLOWS | 5 |
| 07-DECISIONS | 2 | | 90-ORIGINAL-SOURCES | 14 (12 copias + README + catálogo) |
| 08-OPERATIONS | 2 | | 99-ARCHIVE | **No creada** (no hay elementos históricos que archivar) |

**Notas de la estructura propuesta que no se crearon, y por qué** (no crear contenido ficticio): `02-BACKEND/TECHNICAL_REPORT`, `REFACTORING_PLAN` y `SECURITY_AUDIT` → integradas en [[06-AUDITS/BACKEND/BACKEND_AUDITS|BACKEND_AUDITS]] y [[06-AUDITS/SECURITY/SECURITY_AUDIT|SECURITY_AUDIT]] (alias), para no duplicar; `04-REQUIREMENTS/PLAN` y `ACCEPTANCE_CRITERIA` → dentro de [[SPECIFY]]; `05-EXECUTION/EXECUTION_CHECKLIST`, `CURRENT_SPRINT` y `COMPLETED_TASKS` → no hay datos de sprint verificables; las tareas completadas están en [[TASKS]]; `06-AUDITS/FRONTEND` y `FINAL_VALIDATION` → no existe una auditoría frontend propia, y la validación final está indexada en BACKEND_AUDITS; `07-DECISIONS/ADR-001…003` → los ADR del proyecto se indexan en [[ADR_INDEX]] (no se copian) y la decisión propia es [[ADR-KB-001-fuentes-originales]]; `08-OPERATIONS/INSTALLATION` y `DEPLOYMENT` → dentro de [[DOCKER]]; `11-REGULATORY/DEGREE_REGULATIONS` → dentro de [[ARTICLES_AND_PROVISIONS]]; `13-TRACEABILITY/REQUIREMENTS_IMPLEMENTATION` y `REQUIREMENTS_TESTS` → dentro de [[GENERAL_TRACEABILITY_MATRIX]]; `14-…/ROLE_DASHBOARDS` y `KPI_ENDPOINT_MATRIX` → dentro de [[DASHBOARD_ARCHITECTURE]] y [[KPI_CATALOG]].

## 5. Inventario documental
[[SOURCE_CATALOG]]: unas 230 fuentes en 9 grupos, cada una con su decisión (incorporada, referenciada o excluida) y motivo.

## 6. Archivos incorporados
12 MD de `Documentacion-parte-2` (4 829 líneas añadidas en el commit `9f8e416`, incluidos el README y el catálogo).

## 7. Estado de todos los archivos de Documentacion-parte-2
12/12 **incorporados**, con copia íntegra verificada por SHA-256 y una nota derivada verificada contra el código. `index.html` **excluido** (render Quarto). Tabla completa: [[SOURCE_CATALOG]] §1.

## 8. Estado de los 13 documentos previamente identificados
12 existen y están incorporados. **`ROADMAP_INCREMENTOS_IMPLEMENTACION.md` no existe** en ninguna parte del disco; el plan maestro §14 lo declara como "Sección 9", y su contenido (INC-01…INC-09) está en [[DP2-PLAN_MAESTRO]]. No se creó un archivo ficticio.

## 9. Módulos documentados
Backend: authentication, expedientes, peticiones, verificacion, resoluciones, notificaciones, core. Frontend: api, auth, app, components (ui, feedback, layout), features (auth, dashboard, solicitud, expediente, peticiones, bandeja, no-habilitado), lib, mocks, styles.

## 10. Arquitectura identificada
Monolito modular hexagonal Django 5.2/DRF/PostgreSQL 16 + SPA React 19/Vite + Nginx; SGA solo por mock → [[GENERAL_ARCHITECTURE]].

## 11. Notas creadas
69 notas propias y derivadas (incluidos este informe, el README de fuentes y el catálogo) + 12 copias íntegras de fuentes = 81 archivos `.md`. Índice: [[MASTER_INDEX]].

## 12. Matrices creadas
[[GENERAL_TRACEABILITY_MATRIX]], [[REGULATORY_TRACEABILITY]], [[DOCUMENT_TRACEABILITY]], [[EVIDENCE_INDEX]], [[PERMISSIONS_ROLES]] (RBAC real), [[API_CONTRACTS]], [[KPI_CATALOG]].

## 13. Enlaces internos
Verificación con script (resuelve `[[nombre]]` y `[[ruta/nombre]]`, ignora bloques de código): **499 wikilinks en 81 notas, 0 rotos y 0 ambiguos tras crear este informe** (antes de crearlo, los únicos rotos eran 8 enlaces a `BUILD_REPORT`). Nombre de archivo repetido: `MODULES` (02-BACKEND y 03-FRONTEND), siempre enlazado con ruta. Ninguna nota sin enlaces entrantes.

## 14. Duplicados encontrados
- Diagramas `clases_dominio.puml`, `workspace.dsl` y `proceso_principal.bpmn`: idénticos en `DOCUMENTACION/` y `docs/10-auditoria-2026-11/assets/`.
- `backend/openapi.yaml` = `backend/contracts/openapi.yaml`.
- Copias de DP2 fuera del repo (backup y GitKraken), idénticas.
- **Falsos duplicados** (mismo nombre, contenido distinto): `GUIA_VISTAS_TITULACION.md` (docs/frontend frente a diseno-ui) y ADR-0001/0002 (backend/docs frente a docs).

## 15. Contradicciones encontradas
22 registradas en [[DOCUMENT_TRACEABILITY]] (C-01…C-22). Las más relevantes: 23 endpoints declarados frente a 17 reales; refresh "implícito" inexistente; Framer Motion no instalado; 87 frente a 77 controles de seguridad; 40 frente a 47 KPIs; documentos de seguridad citados que no existen; numeración SEC-T inconsistente; política "sin Git" frente a uso real de Git.

## 16. Pendientes de verificación
1. Texto vigente de los Arts. 39, 40, 212, 216 y 233 RRA-UNL (no hay fuente primaria en el repo).
2. Qué 6 pruebas frontend fallaron de forma intermitente.
3. Suite backend (497) en esta versión del código.
4. BE-07 (exposición de `motivo_observacion`) y configuración de CORS en desarrollo (BE-08).
5. `User.last_login` en el login por API ([[DP2-PLAN_SESIONES]]).
6. Fuente de los "87 controles" y del catálogo VULN-001…014.
7. Significado temático de cada nombre COSMOS.

## 17. Configuración de Claude Code
`CLAUDE.md`: nueva política de consulta (recuperación progresiva, MCP con alternativa directa, verificación contra código, mantenimiento), hallazgos vigentes y máxima 4 de Git actualizada (DK-003). Se conservó el resto del contenido. **Nota:** el `CLAUDE.md` local tenía 25 líneas sin confirmar (la sección de política de consulta); se reescribieron y quedaron incluidas en el commit `5b96cde`.

## 18. Configuración de OpenCode
`AGENTS.md` §6 nueva (misma bóveda y reglas) y §3.8 (Git). `~/.config/opencode/opencode.json` inspeccionado (Ollama local, contextos de 8K, sin MCP de Obsidian): **no modificado**. [[SYSTEM]] está pensado para contextos de 8K.

## 19. Estado del MCP
Servidor `obsidian`, alcance usuario, HTTP `http://localhost:8765/mcp`, **Connected**; plugin `vault-as-mcp` 1.2.1 en `127.0.0.1`, sin TLS, sin autenticación y sin `pathACL`. Operaciones verificadas: `list_notes` (vacía antes), `search_notes` por carpeta y frontmatter (2 resultados correctos), `read_note` por encabezado (solo la sección), `patch_note` (cambio comprobado en disco con `grep`). Configuración **no modificada**. Detalle: [[OBSIDIAN_MCP]].

## 20. Exclusiones por seguridad
`.env` y `frontend/.env.local` (no se leyeron), PDF de `backend/src/media/private/**`, plugins de terceros y estado local de `.obsidian` (vía `.gitignore`), binario `gitleaks.exe`. Los valores de `docker-compose.yml` se redactaron al inspeccionarlos.

## 21. Validaciones ejecutadas
| Validación | Resultado |
|---|---|
| Integridad de las copias DP2 (`sha256sum -c`) | 12/12 OK |
| Originales intactos | Copias solo de lectura; `git status` sin cambios en `Documentacion-parte-2/*.md` |
| Wikilinks (script Python, `-I`) | 0 rotos, 0 ambiguos |
| Búsqueda de secretos (patrones de claves, tokens, JWT, claves privadas) en `SIAAF-KNOWLEDGE/**/*.md` | Sin coincidencias. Única cadena de 10 dígitos: `1234567890`, cédula de ejemplo ficticia en una fuente DP2 |
| `.gitignore` (`git check-ignore`) | `workspace.json` y `plugins/` ignorados; los 4 JSON compartibles, versionables |
| Endpoints frente a OpenAPI | Coinciden (16/17) |
| Suite frontend | 322/328 → (2.ª sin FAIL) → 328/328 |
| Suite backend | **No ejecutada** |
| Apertura en Obsidian | El MCP (que corre dentro de Obsidian) lista y lee las notas nuevas; no se abrió la interfaz gráfica |

## 22. Rama utilizada
`docs/siaaf-knowledge`, creada desde `develop` local (recién creada para seguir a `origin/develop` = `fee9119`, `git pull --ff-only`: "Ya está actualizado").

## 23. Commits realizados
| Hash | Mensaje |
|---|---|
| `9f8e416` | docs(obsidian): incorporar fuentes originales de Documentacion-parte-2 |
| `af62f3e` | docs(architecture): documentar arquitectura, módulos y contratos verificados |
| `02b31f0` | docs(knowledge): documentar normativa, procesos, trazabilidad y KPIs |
| `8893145` | docs(obsidian): núcleo, flujos de trabajo y configuración de la bóveda |
| `5b96cde` | docs(agents): apuntar CLAUDE.md y AGENTS.md a SIAAF-KNOWLEDGE |
| (este informe) | docs(obsidian): agregar informe de construcción BUILD_REPORT |

Todos con `git add` de rutas explícitas; los cambios locales ajenos (borrados en `docs/`, `backend/entrypoint.sh`, archivos sin seguimiento) **no se incluyeron** y siguen en el árbol de trabajo.

## 24. Push realizado
`git push -u origin docs/siaaf-knowledge` → `* [new branch] docs/siaaf-knowledge -> docs/siaaf-knowledge` (OK).

## 25. Pull Request o integración
Sin PR (no hay `gh`); merge `--no-ff` local en `develop` (`6ddcc87`) y push aceptado. Detalle: [[#Resultado de la integración]].

## 26. Estado de `develop`
Ver [[#Resultado de la integración]].

## 27. Estado de `main`
**Sin cambios**: no se hicieron commits, merges ni pushes sobre `main`. `origin/main` sigue en `fe75d39`.

## 28. Tags y releases
**Ninguno** (DK-005): la bóveda es documentación, no una entrega funcional; no se reutilizó ECLIPSE v0.4.0.

## 29. Abrir la bóveda en Obsidian
Ya está registrada y abierta. En otra máquina: Obsidian → "Open folder as vault" → `<repo>/SIAAF-KNOWLEDGE`. Para el MCP: instalar y activar el plugin comunitario `vault-as-mcp` (su código no se versiona) y registrar `claude mcp add --transport http obsidian http://localhost:8765/mcp` (alcance usuario).

## 30. Trabajo en sesiones futuras
`CLAUDE.md` → [[MASTER_INDEX]] → [[CURRENT_STATE]] → nota del módulo → fuente → código. Cierre de tarea: [[KNOWLEDGE_MAINTENANCE]]. Guía: [[CLAUDE_CODE_OPENCODE_GUIDE]].

## 31. Limitaciones encontradas
- No hay normativa oficial en el repo: las reglas institucionales dependen de citas.
- No se pudo ejecutar la suite backend (requiere PostgreSQL/Docker).
- CLI `gh` no instalada: no se pueden crear PR ni releases desde la terminal.
- Las fuentes no copiadas no se abren desde Obsidian (están fuera de la bóveda).
- `DOCUMENTACION/` y `.github/workflows/` no están versionados (cambios locales ajenos; no se incorporaron).

## 32. Operaciones pendientes y motivos
| Operación | Motivo |
|---|---|
| Decidir sobre GAP-STATE-01, el RBAC de RESPONSABLE_DEPENDENCIA y `CANCELADA` | Cambios de backend: requieren autorización |
| Confirmar DK-003 (nueva redacción de la política Git) | Cambia instrucciones permanentes de los agentes |
| Validar normativa de modalidades | Requiere autoridad académica |
| Versionar `DOCUMENTACION/`, `docs/academico/` y `.github/workflows/` | Son cambios locales ajenos a esta tarea |
| Diagnosticar las pruebas frontend intermitentes | Tarea de código, fuera de alcance |
| Eliminar la rama documental | Ver [[#Resultado de la integración]] |

## Resultado de la integración

| Paso | Comando | Resultado comprobado |
|---|---|---|
| Pull Request | — | **No creado**: la CLI `gh` no está instalada y no se buscaron credenciales alternativas. GitHub ofreció la URL `https://github.com/R0yalCode/sistema-titulacion-unl/pull/new/docs/siaaf-knowledge` |
| Actualizar `develop` | `git switch develop && git pull --ff-only origin develop` | Ya al día (`fee9119`) |
| Merge | `git merge --no-ff docs/siaaf-knowledge` | Commit de merge `6ddcc87` (sin conflictos) |
| Publicar `develop` | `git push origin develop` | `fee9119..6ddcc87 develop -> develop`: aceptado (la rama **no** rechazó el push directo, por lo que no parece tener protección que exija PR) |
| Verificación | `git fetch` + `git diff origin/develop docs/siaaf-knowledge -- SIAAF-KNOWLEDGE` | Sin diferencias; `origin/develop = 6ddcc87` |
| `main` | `git rev-parse origin/main` | `fe75d39`, **sin cambios** |
| Árbol de trabajo | `git status --short` | Cambios ajenos intactos: 136 `D` (docs/), 1 `M` (`backend/entrypoint.sh`), 9 `??` |
| Este apartado | Commit de seguimiento en la rama, integrado en `develop` por fast-forward | Ver `git log origin/develop` |
| Eliminación de la rama `docs/siaaf-knowledge` (local y remota) | `git branch -d` / `git push origin --delete` | Se ejecuta **después** de este commit, una vez verificado que `develop` la contiene; comprobable con `git ls-remote --heads origin docs/siaaf-knowledge` |

**Estado de `develop`:** contiene toda la bóveda SIAAF-KNOWLEDGE, `CLAUDE.md`/`AGENTS.md` actualizados y la regla de `.gitignore`. **Estado de `main`:** intacto.
