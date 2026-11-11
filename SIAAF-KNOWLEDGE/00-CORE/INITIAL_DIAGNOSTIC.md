---
system: SGT-SIAAF
type: diagnostic
status: verified
source: repository-inspection
last_verified: 2026-11-11
---

# Diagnóstico inicial — construcción de SIAAF-KNOWLEDGE

> Instantánea del 2026-11-11 tomada **antes** de crear contenido en la bóveda. Todo lo que figura aquí se comprobó con comandos sobre el repositorio, el sistema de archivos y la configuración de Claude Code. Para el estado vivo, consulta [[CURRENT_STATE]].

## 1. Repositorio

| Elemento | Valor verificado |
|---|---|
| Ruta absoluta | `/home/royeljima/Documentos/sgt-siaaf` |
| Remoto | `origin` → `git@github.com:R0yalCode/sistema-titulacion-unl.git` (SSH) |
| Rama al iniciar | `main` (con cambios locales sin confirmar) |
| Último commit en `main` | `fe75d39 Merge pull request #21 from R0yalCode/develop` |
| `origin/develop` | `fee9119 Merge pull request #20 …/docs/rosetta-documentacion-maestra` |
| Divergencia `origin/main…origin/develop` | `main` +1 (commit de merge) / `develop` +0; **árboles idénticos** (`git diff main origin/develop` vacío) |
| `develop` local | No existía; se creó desde `origin/develop` |
| Tags | Ninguno (ni locales ni remotos: `git ls-remote --tags` vacío) |
| CLI `gh` | **No instalada** (no se pueden crear PR ni releases desde terminal) |

### Árbol de trabajo al iniciar (cambios ajenos, NO tocados)

148 entradas en `git status --short`:

- **136 borrados** (`D`) bajo `docs/`: `docs/ENTORNO_DESARROLLO.md` y artefactos generados (`docs/.quarto/**`, `docs/_site/**`).
- **2 modificados** (`M`): `CLAUDE.md` (+25 líneas: sección "Política de consulta del conocimiento SIAAF-KNOWLEDGE") y `backend/entrypoint.sh` (solo cambio de modo/permisos, 0 líneas).
- **10 sin seguimiento** (`??`): `.claude/`, `.github/dependabot.yml`, `.github/safety-policy.yml`, `.github/workflows/`, `DOCUMENTACION/`, `Documentacion-parte-2/index.html`, `SIAAF-KNOWLEDGE/`, `docs/academico/`, `gh-pages.zip`, `gh-pages/`.

Estos cambios se conservaron intactos durante el cambio de rama (los árboles de `main` y `develop` son idénticos). Solo se confirmaron los archivos de esta tarea (ver [[BUILD_REPORT]]).

### Estructura general

| Carpeta | Contenido | Seguimiento Git |
|---|---|---|
| `backend/` | Django 5.2 + DRF; `src/apps/{authentication,expedientes,peticiones,verificacion,resoluciones,notificaciones}`, `src/core`, `src/config` | Sí |
| `frontend/` | React 19 + TS + Vite; `src/{api,app,auth,components,features,lib,mocks,styles,test,types}` | Sí |
| `sgt-siaaf/` | SDD: `.specify/memory/constitution.md`, `specs/001-tramite-titulacion/`, `specs/003-frontend-titulacion/` | Sí |
| `docs/` | Documentación Quarto (01…11), ADR, auditorías backend/seguridad, KPI, sprint S1 | Sí (salvo `docs/academico/`) |
| `DOCUMENTACION/` | Paquete documental 00…11 (45 MD + diagramas) | **No** (sin seguimiento) |
| `Documentacion-parte-2/` | 12 MD de planificación maestra (commit `bf74d4d`) + `index.html` | MD sí; `index.html` no |
| `auditoria/` | 8 informes de auditoría (01…08) | Sí |
| `diseno-ui/` | Especificaciones UI 01…08 + guía de vistas | Sí |
| `SGT_SIAAF_Prototipo_HTML_CSS_JS/`, `SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/` | Prototipos A/B (referencia visual) | Sí |
| `gh-pages/`, `gh-pages.zip` | Sitio publicado generado | No |
| `nginx/`, `Dockerfile`, `docker-compose*.yml` | Operación | Sí |
| `*.py` en raíz (`audit_*.py`, `verify_*.py`, `check_*.py`) | Scripts auxiliares de verificación de tareas | Sí |

## 2. Bóveda Obsidian

| Ubicación | Estado encontrado |
|---|---|
| `<repo>/SIAAF-KNOWLEDGE/` | Existía, **vacía**: solo `.obsidian/` (app, appearance, core-plugins, community-plugins, workspace, `plugins/vault-as-mcp`). Es la bóveda **abierta** en Obsidian (Flatpak, `obsidian.json` → `open: true`). |
| `/home/royeljima/Documentos/SIAAF-KNOWLEDGE` (externa) | Registrada en Obsidian pero **ya movida a la papelera** por el usuario (`DeletionDate=2026-11-11T01:02:02`). Contenido: solo `.obsidian/`, **0 notas**. |
| `<repo>/documentacion-original/SIAAF-KNOWLEDGE` | Registrada en Obsidian, **en la papelera** (`DeletionDate=2026-11-11T01:01:53`). Contenido: solo `.obsidian/`, **0 notas**. |

**Conclusión:** no había notas que migrar. La bóveda interna se reutiliza como bóveda oficial; no se creó una segunda. No se tocó la papelera ni el registro de bóvedas de Obsidian.

## 3. Documentación encontrada

### 3.1 `Documentacion-parte-2`

Variantes buscadas: `Documentacion-parte-2`, `documentacion parte 2`, `Documentacion parte 2`, `documentacion-parte-2` (búsqueda insensible a mayúsculas en `/home/royeljima`, profundidad 4).

| Copia | Archivos | Diferencias |
|---|---|---|
| `<repo>/Documentacion-parte-2/` (**canónica**) | 12 MD + `index.html` | — |
| `~/Documentos/sgt-siaaf-backup-antes-de-git/Documentacion-parte-2/` | 12 MD + `index.html` | Idéntica (`diff -rq` vacío) |
| `~/Documentos/GitKraken/sistema-titulacion-unl/Documentacion-parte-2/` | 12 MD | Solo falta `index.html` |

**Cantidad exacta: 12 documentos Markdown.** El 13.º documento esperado, `ROADMAP_INCREMENTOS_IMPLEMENTACION.md`, **no existe en ningún lugar del disco** (`find / -iname '*ROADMAP_INCREMENTOS*'` vacío). El propio plan maestro (§14) lo lista como "✅ Sección 9": su contenido está **incrustado en la §9 de `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md`** y nunca se creó como archivo. Esto explica la discrepancia 12/13. `index.html` es un render Quarto (`generator quarto-1.11.9`), no un documento fuente → excluido.

### 3.2 Recuento por formato (sin generados ni dependencias)

| Carpeta | Archivos | Formatos principales |
|---|---|---|
| `DOCUMENTACION/` | 53 | 45 md, 5 svg, 1 puml, 1 dsl, 1 bpmn |
| `docs/` (sin `_site`/`.quarto`) | 121 | 105 md, 6 qmd, 5 svg, 1 yml, 1 puml, 1 dsl |
| `auditoria/` | 8 | 8 md |
| `diseno-ui/` | 20 | 10 md, 9 png, 1 jpg |
| `sgt-siaaf/` | 15 | 15 md (6 vacíos: plantillas y ADR-001/002 de spec 001) |
| `Documentacion-parte-2/` | 13 | 12 md, 1 html |
| Prototipos A/B | 40 | html/css/js/png/svg/md |
| `gh-pages/` | 120 | 109 html (sitio generado) |

Especificaciones OpenAPI: `backend/openapi.yaml` y `backend/contracts/openapi.yaml`.
PDF/DOCX/XLSX: **no hay documentos normativos oficiales** en el repositorio. Los únicos PDF están en `backend/src/media/private/**` (documentos de expedientes y resoluciones generados por el sistema; carpeta ignorada por Git) → **excluidos por seguridad**.

Inventario completo y decisiones de incorporación: [[SOURCE_CATALOG]].

## 4. Módulos y arquitectura identificados

- **Backend** (monolito modular, adaptadores hexagonales): 6 apps + `core`. Detalle: [[02-BACKEND/MODULES|Módulos backend]].
- **Frontend** (SPA React): features `auth`, `dashboard`, `solicitud`, `expediente`, `peticiones` (stub), `bandeja` (stub), `no-habilitado`. Detalle: [[03-FRONTEND/MODULES|Módulos frontend]].
- **No existen** en el código: app `indicadores`, endpoint `/dashboard/me/`, modalidades de titulación (`opcion_titulacion`), modelo de sesiones, refresh/logout, búsqueda y exportación.

## 5. MCP de Obsidian

Servidor `obsidian` (alcance usuario), HTTP `http://localhost:8765/mcp`, **conectado**; lo sirve el plugin comunitario `vault-as-mcp` 1.2.1 sobre la bóveda abierta (interna). Al iniciar, `list_notes("")` devolvía la bóveda vacía. Detalle: [[OBSIDIAN_MCP]].

## 6. Riesgos documentales

1. **Estado frontend desactualizado en DP2**: el plan maestro declara F2.5 "80 %" y V-03/V-04 en estados que difieren de `tasks.md`/`CLAUDE.md` (V-01…V-04 cerradas).
2. **Afirmaciones no verificadas en DP2** (ver [[DOCUMENT_TRACEABILITY]]): "23 endpoints operativos" (el código expone 17 operaciones API), "Framer Motion ya en deps" (no está en `package.json`), `POST /auth/token/refresh/` "implícito" (no existe ruta).
3. **Normativa de modalidades sin fuente primaria**: Arts. 39, 40, 212, 216, 233 RRA-UNL marcados por la propia fuente como hipótesis.
4. **Documentación sin seguimiento Git**: `DOCUMENTACION/` (53 archivos) y `docs/academico/` no están versionados; podrían perderse.
5. **Duplicados**: `docs/frontend/GUIA_VISTAS_TITULACION.md` y `diseno-ui/.../GUIA_VISTAS_TITULACION.md` tienen el mismo tamaño (11 155 B) pero **difieren** desde la línea 1 (`cmp`); la copia canónica es la de `diseno-ui/` (`AGENTS.md` §3.5). `FRONTEND_IMPLEMENTATION_PLAN.md` está vacío en ambas ubicaciones. Los diagramas `clases_dominio.puml`, `workspace.dsl` y `proceso_principal.bpmn` son **byte a byte idénticos** en `DOCUMENTACION/` y `docs/10-auditoria-2026-11/assets/` (más una tercera copia generada en `docs/_site/`). `backend/openapi.yaml` y `backend/contracts/openapi.yaml` son idénticos (16 rutas).
6. **Política Git contradictoria**: `AGENTS.md` §3.8 y `CLAUDE.md` máxima 4 dicen "sin Git (el repo no lo usa)", pero el repo usa Git, ramas `release/*` y PR. Ver [[DECISIONS_LOG]] DK-003.
7. **Pruebas intermitentes**: 1 de 3 ejecuciones de la suite frontend falló (6/328). Ver [[REGRESSION_TESTS]].

## 7. Propuesta de organización (aplicada)

- Estructura `00-CORE … 15-GIT-AND-WORKFLOWS`, `90-ORIGINAL-SOURCES`, sin carpetas vacías.
- **Copia íntegra** (verificada por SHA-256) solo de los 12 MD de `Documentacion-parte-2` en `90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/`; el resto de fuentes se **referencia por ruta** desde [[SOURCE_CATALOG]] para no crear copias divergentes de documentos vivos (specs, tasks). Justificación: [[ADR-KB-001-fuentes-originales]].
- Una nota derivada por documento DP2 en `10-REFERENCES/DOCUMENTATION-PART-2/`, con verificación contra código.
