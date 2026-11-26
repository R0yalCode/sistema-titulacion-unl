---
title: "Control maestro de documentación — SGT-SIAAF"
---

# CONTROL MAESTRO DE DOCUMENTACIÓN — SGT-SIAAF

**Última actualización:** 2026-11-06 · **Responsable de la pasada actual:** Claude Code (asistente), bajo supervisión del usuario.

---

## 1. Objetivo general

Producir una auditoría integral y un expediente técnico-académico verificable del proyecto SGT-SIAAF para la Evaluación Sumativa 1 (incremento funcional del backend), consolidando la documentación ya existente, llenando únicamente las brechas reales, y publicando el resultado como un portal Quarto navegable, sin modificar código, reglas de negocio ni configuración de producción.

## 2. Alcance

- **Dentro de alcance:** documentación técnica y académica (contexto, requisitos, SDD, BPMN, C4/UML, backend, API, seguridad, pruebas, Docker/despliegue, observabilidad, declaratoria de IA, portal Quarto, publicación GitHub Pages, matrices de cumplimiento).
- **Fuera de alcance:** cualquier cambio a `backend/` (código, modelos, permisos, migraciones, configuración de producción), a `openapi.yaml`, a las specs 001 ni a la Constitución; control de versiones/GitFlow/historial de commits (excluido explícitamente, ya evidenciado por separado); invención de funcionalidades, endpoints, cifras o decisiones no respaldadas.

## 3. Inventario de documentos (ver detalle en `00_AUDITORIA/`)

| Conjunto | Ubicación | Nº de archivos | Vigencia |
|---|---|---|---|
| Auditoría previa (raíz) | `auditoria/` | 8 | Parcialmente superada (ver H-01) |
| Portal Quarto existente | `docs/` | 107 | Mayormente vigente, con snapshots desactualizados puntuales (H-02) y duplicados por reconciliar |
| SDD backend | `sgt-siaaf/specs/001-tramite-titulacion/` | 7 (+2 ADR) | Vigente, normativo |
| SDD frontend | `sgt-siaaf/specs/003-frontend-titulacion/` | 4 | Vigente, normativo |
| Especificaciones de UI | `diseno-ui/ui/titulacion-v2/especificaciones/` | 8 | Vigente, normativo (solo frontend) |
| Este expediente (nuevo) | `DOCUMENTACION/` | 12 (hasta ahora) | En construcción |

## 4. Inventario de evidencias técnicas verificables

- Código fuente real: `backend/src/apps/{authentication,expedientes,peticiones,verificacion,resoluciones,notificaciones}`, `backend/src/core/{ports,adapters}`.
- `backend/openapi.yaml` (1224 líneas), posible duplicado en `backend/contracts/` (pendiente de confirmar, H-03).
- 34 archivos de prueba backend (32 en apps + 2 en core); conteo de casos pendiente de ejecución real (Fase 7).
- `docker-compose.yml`, `docker-compose.prod.yml`, `Dockerfile`, `nginx/`.
- `.github/workflows/security.yml`, `dependabot.yml`, `safety-policy.yml`.
- `CLAUDE.md` (raíz) como fuente de verdad más reciente del estado del frontend (actualizado 2026-11-05/06).

## 5. Matriz de cumplimiento

Ver `00_AUDITORIA/MATRIZ_CUMPLIMIENTO_INICIAL.md` (30 filas, incluida la exclusión explícita de Git). Se actualizará a matriz final en la Fase 13 (`DOCUMENTACION/12_CIERRE/`).

## 6. Lista de tareas y estado

| Fase | Tareas | Estado | Notas |
|---|---|---|---|
| 0 | TASK-DOC-000/001/002 + control maestro | **COMPLETADA** | Ver sección 11 |
| 1 | TASK-DOC-010…015 (contexto, actores, RF/RNF, historias, SDD, trazabilidad) | **COMPLETADA** | 8 archivos en `01_ESPECIFICACION/`; corrige H-02 en la matriz de trazabilidad; detecta nuevo hallazgo H-06 (numeración P-01…P-18 vs "C-001…C-020" citada en `specify.md`) |
| 2 | TASK-DOC-020…022 (BPMN) | **COMPLETADA** | Diagrama creado desde cero (sin artefacto previo); 20 elementos de flujo, 5 carriles, 2 compuertas, 2 bucles verificados contra el código; validado visualmente por render headless |
| 3 | TASK-DOC-030…034 (C4/UML/ADR) | **COMPLETADA** | C1/C2/C3 en Structurizr DSL (un workspace, 3 vistas) + UML en PlantUML, todo creado desde cero (H-05) y corregido contra el código real donde `plan.md` era idealizado (SGA/SIAAF unificado, Gunicorn no runserver, un solo puerto real ISGALegacyPort). ADR: no había duplicado real — `specs/001/adr/` está vacío (corrección de la Fase 0) |
| 4 | TASK-DOC-040…043 (backend) | **COMPLETADA** | Stack con versiones exactas del manifiesto (discrepancia detectada vs ADR-0002), estructura modular, 11 componentes de negocio (servicios reales) y persistencia (constraints/índices/migraciones) verificados por lectura directa de código |
| 5 | TASK-DOC-050…052 (API) | **COMPLETADA** | H-03 confirmado (MD5 idéntico, duplicado real); 17 operaciones de negocio inventariadas desde `urls.py`; **hallazgo nuevo**: el contrato universal `{success,data,errors,meta}` que pide el encargo NO existe en este proyecto (verificado, NA); OpenAPI↔urls.py coincide 16/16 rutas |
| 6 | TASK-DOC-060…063 (seguridad) | **COMPLETADA** | Consolidado sin duplicar; **2 hallazgos P0 previamente reportados como abiertos se verificaron CERRADOS** (vulnerabilidad DRF y throttling de login); 1 inconsistencia documental corregida (vida del access token: 30 min, no 60) |
| 7 | TASK-DOC-070…074 (pruebas) | **COMPLETADA** | **H-02 resuelto con ejecución real**: backend 560/573 passed (90% cobertura fuente), 13 fallas con causa raíz confirmada (dependencia `pypdf` ausente, deuda ya aceptada en DEC-05); frontend **no determinista** (328/328 en 3/5 corridas, 324/328 en 2/5 — hallazgo nuevo); flake8 contradice informe previo ("sin errores" vs 874 hallazgos reales) |
| 8 | TASK-DOC-080…084 (Docker/despliegue) | **COMPLETADA** | **Autocorrección importante**: la conclusión de H-04 en Fase 3 ("siempre Gunicorn") era errónea — el `Dockerfile` (raíz, no `backend/`) es multi-stage; `docker-compose.yml` (dev, por defecto) SÍ usa `runserver`, solo `docker-compose.prod.yml` usa Gunicorn. Corregido en 4 documentos. Hallazgo nuevo: `.env` de ejemplo del README omite `JWT_SIGNING_KEY` (rompe `docker compose up` tal como está documentado); CI solo cubre seguridad, sin pruebas/lint |
| 9 | TASK-DOC-090 (observabilidad) | **COMPLETADA** | Health check, logging JSON estructurado con enmascarado de datos sensibles, y bitácora de auditoría — **2 hallazgos heredados corregidos**: ya no hay `print()` de depuración, y la IP de auditoría ya NO está vacía (se propagó la corrección a 4 documentos previos de este mismo expediente) |
| 10 | TASK-DOC-100 (declaratoria IA) | **COMPLETADA** | NotebookLM y Claude Code confirmados con evidencia directa citada del repositorio (`clarify.md`, `docs/auditoria-backend/seguridad/plan-implementacion/`); ChatGPT documentado como categoría del encargo **sin** evidencia directa en el repo — declarado explícitamente, no inventado; corrección de nomenclatura: el encargo pedía documentar "OpenCode", pero la evidencia real del repositorio es "Claude Code" |
| 11 | TASK-DOC-110…116 (portal Quarto) | **COMPLETADA** | Quarto CLI 1.11.9 instalado (portable, checksum verificado) con autorización del usuario. El portal preexistente (107 archivos) renderizó limpio en el baseline (0 errores/warnings) — se adaptó, no se reconstruyó: nuevo capítulo "Auditoría 2026-11" (5 páginas nuevas) + "Inteligencia Artificial", diagramas BPMN/C4/UML embebidos y verificados visualmente, `index.qmd` actualizado con cifras reverificadas. Render final: 109 archivos, 0 errores, 0 warnings |
| 12 | TASK-DOC-120…124 (GitHub Pages) | **COMPLETADA** | `publish-quarto.yml` creado (build+deploy vía Actions, permisos mínimos); carpeta `/gh-pages` (raíz) generada como sitio estático listo para publicar — verificada sirviéndola de forma aislada (200 OK en index, página BPMN, asset SVG); **hallazgo propio detectado y corregido**: faltaba `.nojekyll`, sin el cual GitHub Pages (modo branch) excluiría `_quarto/` por Jekyll, rompiendo el CSS |
| 13 | TASK-DOC-130…132 (matriz final + informe) | PENDIENTE | Cierre, depende de todas las anteriores |

Seguimiento operativo adicional de esta sesión en la lista de tareas del asistente (`TaskList`), tareas #1–#14, una por fase.

## 7. Archivos generados hasta ahora

- `DOCUMENTACION/00_AUDITORIA/INVENTARIO_PROYECTO.md`
- `DOCUMENTACION/00_AUDITORIA/AUDITORIA_DOCUMENTAL.md`
- `DOCUMENTACION/00_AUDITORIA/MATRIZ_CUMPLIMIENTO_INICIAL.md`
- `DOCUMENTACION/CONTROL_MAESTRO_DOCUMENTACION.md` (este archivo)
- `DOCUMENTACION/01_ESPECIFICACION/CONTEXTO_PROYECTO.md`
- `DOCUMENTACION/01_ESPECIFICACION/ALCANCE_INCREMENTO.md`
- `DOCUMENTACION/01_ESPECIFICACION/ACTORES_Y_NECESIDADES.md`
- `DOCUMENTACION/01_ESPECIFICACION/REQUISITOS_FUNCIONALES.md`
- `DOCUMENTACION/01_ESPECIFICACION/REQUISITOS_NO_FUNCIONALES.md`
- `DOCUMENTACION/01_ESPECIFICACION/HISTORIAS_Y_CASOS_DE_USO.md`
- `DOCUMENTACION/01_ESPECIFICACION/SDD_GITHUB_SPEC_KIT.md`
- `DOCUMENTACION/01_ESPECIFICACION/MATRIZ_TRAZABILIDAD.md`
- `DOCUMENTACION/02_PROCESOS/ANALISIS_PROCESO.md`
- `DOCUMENTACION/02_PROCESOS/diagramas/proceso_principal.bpmn`
- `DOCUMENTACION/02_PROCESOS/diagramas/proceso_principal.svg`
- `DOCUMENTACION/02_PROCESOS/DIAGRAMA_BPMN.md`
- `DOCUMENTACION/03_ARQUITECTURA/C1_CONTEXTO.md`
- `DOCUMENTACION/03_ARQUITECTURA/C2_CONTENEDORES.md`
- `DOCUMENTACION/03_ARQUITECTURA/C3_COMPONENTES.md`
- `DOCUMENTACION/03_ARQUITECTURA/C4_UML.md`
- `DOCUMENTACION/03_ARQUITECTURA/ADR.md`
- `DOCUMENTACION/03_ARQUITECTURA/diagramas/workspace.dsl`
- `DOCUMENTACION/03_ARQUITECTURA/diagramas/c1_contexto.svg`
- `DOCUMENTACION/03_ARQUITECTURA/diagramas/c2_contenedores.svg`
- `DOCUMENTACION/03_ARQUITECTURA/diagramas/c3_componentes.svg`
- `DOCUMENTACION/03_ARQUITECTURA/diagramas/clases_dominio.puml`
- `DOCUMENTACION/03_ARQUITECTURA/diagramas/clases_dominio.svg`
- `DOCUMENTACION/04_BACKEND/STACK_TECNOLOGICO.md`
- `DOCUMENTACION/04_BACKEND/ARQUITECTURA_BACKEND.md`
- `DOCUMENTACION/04_BACKEND/COMPONENTES_NEGOCIO.md`
- `DOCUMENTACION/04_BACKEND/PERSISTENCIA.md`
- `DOCUMENTACION/05_API/INVENTARIO_ENDPOINTS.md`
- `DOCUMENTACION/05_API/CONTRATO_API.md`
- `DOCUMENTACION/05_API/OPENAPI.md`
- `DOCUMENTACION/06_SEGURIDAD/AUTENTICACION.md`
- `DOCUMENTACION/06_SEGURIDAD/AUTORIZACION_PERMISOS.md`
- `DOCUMENTACION/06_SEGURIDAD/AUDITORIA_SEGURIDAD.md`
- `DOCUMENTACION/06_SEGURIDAD/PROTECCION_DATOS.md`
- `DOCUMENTACION/07_PRUEBAS/ESTRATEGIA_PRUEBAS.md`
- `DOCUMENTACION/07_PRUEBAS/PRUEBAS_UNITARIAS.md`
- `DOCUMENTACION/07_PRUEBAS/PRUEBAS_INTEGRACION_API.md`
- `DOCUMENTACION/07_PRUEBAS/RESULTADOS_VALIDACION.md`
- `DOCUMENTACION/07_PRUEBAS/MATRIZ_VERIFICACION.md`
- `DOCUMENTACION/08_DESPLIEGUE/ARQUITECTURA_DOCKER.md`
- `DOCUMENTACION/08_DESPLIEGUE/INSTALACION.md`
- `DOCUMENTACION/08_DESPLIEGUE/CONFIGURACION.md`
- `DOCUMENTACION/08_DESPLIEGUE/EJECUCION.md`
- `DOCUMENTACION/08_DESPLIEGUE/PRUEBAS_DOCKER.md`
- `DOCUMENTACION/08_DESPLIEGUE/GITHUB_ACTIONS.md`
- `DOCUMENTACION/08_DESPLIEGUE/PROBLEMAS_FRECUENTES.md`
- `DOCUMENTACION/09_OBSERVABILIDAD/OBSERVABILIDAD.md`
- `DOCUMENTACION/10_INTELIGENCIA_ARTIFICIAL/DECLARATORIA_IA.md`
- `docs/10-auditoria-2026-11/{index,bpmn,arquitectura,pruebas-reales}.qmd` + `assets/` (7 diagramas copiados: SVG, BPMN, DSL, PUML)
- `docs/11-inteligencia-artificial/declaratoria-ia.qmd`
- `docs/_quarto.yml` (navbar actualizado: 2 entradas nuevas) y `docs/index.qmd` (cifras reverificadas, enlaces nuevos) — modificados, no recreados
- `.github/workflows/publish-quarto.yml`
- `/gh-pages` (raíz del repositorio) — sitio estático completo, 109 páginas, listo para publicar
- `DOCUMENTACION/11_PUBLICACION_GITHUB_PAGES.md`

## 8. Hallazgos (acumulados, ver detalle en `00_AUDITORIA/`)

- **H-01**: tres defectos críticos reportados por `auditoria/01_AUDITORIA_GENERAL.md` (01-nov-2026) ya no existen en el código actual (ruta de PDF hardcodeada, memorando no persistido, `checklist` ausente de `RBAC_MATRIX`). Verificado por `grep` directo el 2026-11-06.
- **H-02** (RESUELTO en Fase 7 con ejecución real): backend 560/573 passed (97.7%), 13 fallas con causa raíz 100% confirmada (dependencia opcional `pypdf` ausente del entorno de pruebas — ya aceptada como deuda en `clarify.md` DEC-05, confirmado experimentalmente instalándola). Cobertura: 90% (código fuente) / 96% (incl. tests, igual a la config del proyecto) — ambas superan RNF-012. Frontend: **no determinista** — 328/328 en 3 de 5 ejecuciones, 324/328 en 2 de 5 (mismas 4 pruebas de `router.test.tsx`, relacionadas con temporización `findByRole`; pasan siempre en aislamiento, indicando un problema de aislamiento entre archivos de Vitest, no un defecto de enrutamiento). Ninguna cifra previa (526, 473, 482, 198, 328) se reproduce exactamente — esperable por diferencias de entorno (Python 3.14 vs 3.12 del proyecto, sin lockfile) — pero la nueva medición es reproducible y con metodología declarada.
- **H-10** (Fase 7): `docs/auditoria-backend/INFORME_FINAL_VALIDACION.md` reporta `flake8 src/` con "✅ Sin errores"; la ejecución real del mismo comando en esta Fase 7 produce 874 hallazgos (538 de ellos solo de longitud de línea). No se puede determinar la causa de la discrepancia sin más contexto histórico.
- **H-11** (Fase 7): `core/adapters/security_headers.py` tiene **0% de cobertura de pruebas** — módulo de seguridad sin ninguna prueba automatizada.
- **H-03** (RESUELTO en Fase 5): `backend/contracts/openapi.yaml` y `backend/openapi.yaml` son **idénticos byte a byte** (mismo MD5, `diff` sin salida) — duplicado real confirmado, no solo señalado por referencia. No se elimina ningún archivo (regla 2.3); se reporta como hallazgo de higiene de repositorio.
- **H-07** (Fase 5): el "contrato universal de respuesta" `{success, message, data, errors, meta}` que el encargo pide verificar **no existe en este proyecto**: no aparece en `specify.md`/`plan.md`/`clarify.md` del backend ni en el código (`openapi.yaml`, `views.py`, sin `EXCEPTION_HANDLER` personalizado). Se declara NA, documentando en su lugar el contrato real (DRF estándar + códigos semánticos ya descritos en `docs/04-api/convenciones.md`).
- **H-08** (Fase 6, positivo): dos brechas P0 reportadas como abiertas en `docs/RESUMEN_EJECUTIVO.md`/`docs/06-seguridad/consideraciones-seguridad.md` están en realidad **cerradas**, verificado en código: (1) la vulnerabilidad de `djangorestframework` 3.16.1 señalada por Safety ya está remediada (`requirements.txt` fija `>=3.17.2`); (2) el throttling de login (`5/minute`) y de carga de documentos (`10/hour`) ya está implementado, con una clase consciente de `TRUSTED_PROXIES` (SEC-T005 ya configurado en `production.py`). Los informes previos probablemente predatan estas correcciones.
- **H-09** (Fase 6): inconsistencia entre `docs/06-seguridad/autenticacion.md` ("60 minutos" de vida del access token) y el código real (`ACCESS_TOKEN_LIFETIME = 30 minutos`, confirmado por `base.py` y por `docs/06-seguridad/SECURITY_CONFIG.md`, que documenta el cambio como SEC-T006). El primer documento no se actualizó tras aplicar ese cambio.
- **H-04** (reabierto y corregido definitivamente en Fase 8 — **la Fase 3 de este mismo trabajo había llegado a una conclusión incorrecta**): el `Dockerfile` real está en la **raíz del repositorio** (no en `backend/`, cita de ruta errónea arrastrada desde la Fase 0) y es **multi-stage** con targets `development` (sin `entrypoint.sh`, `CMD runserver`, usado por `docker-compose.yml`) y `production` (con `entrypoint.sh` → Gunicorn, usado por `docker-compose.prod.yml`). La Fase 3 leyó `CMD` y `ENTRYPOINT` sin notar que pertenecían a stages distintos y concluyó erróneamente que Gunicorn se usaba siempre. **Conclusión correcta**: el compose de desarrollo por defecto SÍ ejecuta `runserver` con `DEBUG=1`; la afirmación original de `auditoria/01` era correcta para ese caso. Solo el despliegue explícito de producción usa Gunicorn — y ese despliegue de producción ya existe y está razonablemente completo (`docker-compose.prod.yml`, `production.py`, TLS en `nginx/prod.conf`). Corregido en `C2_CONTENEDORES.md`, `INVENTARIO_PROYECTO.md`, `ADR.md` y documentado en detalle en `DOCUMENTACION/08_DESPLIEGUE/ARQUITECTURA_DOCKER.md`.
- **H-12** (Fase 8): el `.env` de ejemplo en `README.md` no incluye `JWT_SIGNING_KEY`, que `docker-compose.yml` exige sin valor por defecto — siguiendo el README al pie de la letra, `docker compose up` falla.
- **H-13** (Fase 8): el único workflow de GitHub Actions (`security.yml`) cubre exclusivamente seguridad (Safety/Bandit/Gitleaks); no existe ningún job de CI que ejecute pruebas, lint o build. Ya lo señalaba `auditoria/01`; reconfirmado leyendo el workflow completo.
- **H-14** (Fase 9, positivo): dos hallazgos heredados más resultaron estar corregidos: (1) no existe ningún `print()` de depuración en `backend/src` (búsqueda exhaustiva, cero resultados); (2) la configuración `LOGGING` sí existe en `base.py` (JSON estructurado, enmascarado de datos sensibles). Ambos contradicen `docs/06-seguridad/consideraciones-seguridad.md` brecha #6.
- **H-15** (Fase 9, positivo): el campo `EventoAuditoria.ip_origen`, que tres documentos previos de este propio expediente (`REQUISITOS_FUNCIONALES.md`, `MATRIZ_TRAZABILIDAD.md`, `COMPONENTES_NEGOCIO.md`, heredado de `docs/auditoria/matriz-trazabilidad.md`) venían citando como "siempre vacío" sin reverificar, **sí se captura correctamente** vía `resolver_ip_cliente()` con lógica consciente de `TRUSTED_PROXIES`. Se corrigió retroactivamente en los 3 documentos que lo repetían.
- **H-16** (Fase 10): el encargo de esta auditoría pide documentar el uso de una herramienta llamada "OpenCode"; no se encontró ninguna mención a ese nombre en el repositorio. En cambio, hay evidencia directa y repetida de **Claude Code** (citado por nombre en `docs/auditoria-backend/seguridad/plan-implementacion/`, y en `AGENTS.md`/`CLAUDE.md`, que son guías operativas escritas específicamente para esa herramienta). Se documentó la herramienta real en vez de forzar el nombre del encargo sobre evidencia que no lo respalda.
- **H-17** (Fase 12): el `quarto render` de este proyecto **no genera `.nojekyll`** en `docs/_site`. Sin ese archivo, GitHub Pages en modo "Deploy from a branch" aplicaría procesamiento Jekyll por defecto, que excluye cualquier carpeta cuyo nombre empiece con `_` — rompiendo `_quarto/styles.css` (el CSS del sitio) si se publicara así. Detectado y corregido antes de que causara un problema real: se añadió `.nojekyll` a `/gh-pages`, y se documentó como paso obligatorio en cada regeneración (`DOCUMENTACION/11_PUBLICACION_GITHUB_PAGES.md` §4).
- **H-05**: no existen archivos fuente `.bpmn`, `.dsl` (Structurizr) ni `.puml` en el repositorio; los C4 actuales son Mermaid embebido en Markdown, no Structurizr DSL.
- **Duplicados por reconciliar** (no son errores, pero no deben tratarse como documentos independientes): ADR (`docs/adr/` vs `specs/001/adr/`), indicadores (`docs/indicadores/` vs `docs/07-indicadores/`), guía de vistas (`docs/frontend/` vs `diseno-ui/`), autenticación (`docs/06-seguridad/` vs `docs/04-api/`).
- **H-06** (Fase 1): `sgt-siaaf/specs/001-tramite-titulacion/specify.md` cita sistemáticamente "Principio C-001" a "C-020" (20 principios), mientras que la Constitución real (`.specify/memory/constitution.md` y su copia en `specs/001/constitucion.md`) numera sus principios como P-01 a P-18 (18 principios). Ya señalado por `auditoria/05_AUDITORIA_SDD.md` (01-nov-2026); sigue sin corregir al 2026-11-06. No se corrige en este trabajo (no autorizado editar `specify.md` sin citar el ID de decisión afectado).

## 9. Problemas pendientes

- No se localizó un archivo de rúbrica oficial de la Evaluación Sumativa 1 en el repositorio; la matriz de cumplimiento usa como referencia la propia estructura de fases del encargo. Si el usuario dispone de la rúbrica real, debe aportarla antes de la Fase 13.
- Quarto CLI no está instalado en este entorno; no se puede verificar render del sitio hasta la Fase 11.
- No existe `.git` en esta copia de trabajo; la publicación en GitHub Pages (Fase 12) requerirá que el usuario indique cómo y cuándo se sincronizará este trabajo con el repositorio remoto real (fuera del alcance de esta auditoría, según sección 2.4).

## 10. Última tarea completada

**FASE 12 completa**: publicación en GitHub Pages. A petición explícita del usuario, se generó además una **carpeta lista para publicar en la raíz del repositorio** (`/gh-pages`, 109 páginas, 9.5 MB), no solo un workflow. Entregables: `.github/workflows/publish-quarto.yml` (build+deploy vía `actions/upload-pages-artifact` + `actions/deploy-pages`, permisos mínimos, dispara en push a `docs/**` o manualmente), `/gh-pages` (copia autocontenida del sitio renderizado, verificada sirviéndola de forma **aislada** en un puerto distinto sin `docs/` al lado — 200 OK en `index.html`, la página BPMN y un asset SVG) y `DOCUMENTACION/11_PUBLICACION_GITHUB_PAGES.md` (instrucciones exactas para ambas rutas de publicación). **Hallazgo propio (H-17)**: `quarto render` no genera `.nojekyll`; sin él, GitHub Pages en modo "branch" excluiría `_quarto/` (Jekyll ignora carpetas con `_`) y rompería el CSS del sitio — se detectó y corrigió antes de entregar la carpeta, no después de un fallo. No se publicó nada en un GitHub real: esta sesión no tiene `.git` ni acceso de red a un remoto; eso queda explícitamente para el usuario, con instrucciones exactas.

## 11. Próxima tarea autorizada

**FASE 13** (TASK-DOC-130 a 132): matriz final de cumplimiento, análisis de los 5 criterios de rúbrica (sin garantizar calificación) e informe final de documentación (`DOCUMENTACION/12_CIERRE/INFORME_FINAL_DOCUMENTACION.md`). Es la fase de cierre: consolida los 17 hallazgos (H-01 a H-17) de todo el expediente, confronta cada requisito académico contra su evidencia final, y deja instrucciones de entrega. No requiere autorización adicional del humano para iniciar; es la última fase, tras la cual se presenta un resumen general a el usuario.
