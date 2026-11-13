---
system: SGT-SIAAF
type: source-catalog
status: verified
source: repository-inspection
last_verified: 2026-11-12
---

# Catálogo de fuentes originales

Política: [[ADR-KB-001-fuentes-originales]]. **Incorporación**: *Incorporado* = copiado íntegro en la bóveda · *Referenciado* = se cita por ruta y se resume en notas · *Excluido* = no se usa (con motivo). Las rutas son relativas a la raíz del repositorio. Los originales **no se modificaron**.

## 1. Documentacion-parte-2 (12 MD): incorporados

Origen: `Documentacion-parte-2/` (**eliminada de la raíz el 2026-11-12**, DK-014; la copia de la bóveda es ahora la canónica y el original sigue en el historial, `5ef0dbd`) · Commit `bf74d4d` (ROSETTA, 2026-11-11) · Versión 1.0, fecha 2026-11-09 en todos · Copia: `90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/` · Integridad: SHA-256 idéntico (EV-001).

| Archivo | Líneas | Tamaño | SHA-256 (16) | Tema / módulo | Nota derivada | Importancia | Estado |
|---|---|---|---|---|---|---|---|
| `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` | 606 | 37269 B | `a8ecdffa089ca574` | Planificación integral; INC-01…09 (incluye el "roadmap", §9) | [[DP2-PLAN_MAESTRO]] | Crítica | Vigente como plan; estado del frontend desactualizado |
| `MATRIZ_BRECHAS_BACKEND_FRONTEND.md` | 127 | 10838 B | `12bfb1ec24bcbfc0` | Brechas | [[DP2-MATRIZ_BRECHAS]] | Alta | Vigente con observaciones |
| `ARQUITECTURA_DASHBOARDS_POR_ROL.md` | 284 | 16072 B | `8d4105d9df395687` | Dashboards | [[DP2-ARQUITECTURA_DASHBOARDS]] | Media | Propuesta |
| `MATRIZ_INTEGRACION_KPIS_ENDPOINTS.md` | 344 | 15928 B | `57c95345ecc1a904` | KPI → endpoint | [[DP2-MATRIZ_INTEGRACION_KPIS]] | Media | Propuesta |
| `ESPECIFICACION_SERVICIOS_DASHBOARD.md` | 713 | 28831 B | `85575a5811d88f39` | Servicios `indicadores` | [[DP2-ESPECIFICACION_SERVICIOS_DASHBOARD]] | Media | Propuesta |
| `PLAN_IMPLEMENTACION_SESIONES_USUARIOS_ACTIVOS.md` | 457 | 20358 B | `8c2ee62728f71ad7` | Sesiones JWT (INC-02) | [[DP2-PLAN_SESIONES]] | Media | Propuesta |
| `MATRIZ_ACCIONES_RAPIDAS_POR_ROL.md` | 313 | 16278 B | `a314e1f057335aa2` | UX por rol | [[DP2-MATRIZ_ACCIONES_RAPIDAS]] | Media | Contradice el RBAC real |
| `PLAN_INTEGRACION_FRONTEND_BACKEND.md` | 330 | 16094 B | `883121932d852888` | Integración | [[DP2-PLAN_INTEGRACION]] | Alta | Vigente como plan |
| `DISENO_FUNCIONAL_MODALIDADES_TITULACION.md` | 508 | 23079 B | `1cc8e1ee52dc4b71` | Modalidades | [[DP2-DISENO_FUNCIONAL_MODALIDADES]] | Alta | Propuesta; normativa sin validar |
| `MATRIZ_REGLAS_NEGOCIO_MODALIDADES.md` | 193 | 14017 B | `a3e55a16c7b72e2e` | Reglas de modalidades | [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]] | Alta | Propuesta |
| `MATRIZ_KPIS_MODALIDADES_TITULACION.md` | 316 | 15473 B | `3d651cd97ae9d357` | KPIs de modalidades | [[DP2-MATRIZ_KPIS_MODALIDADES]] | Media | Propuesta |
| `ESPECIFICACION_API_MODALIDADES_TITULACION.md` | 492 | 17236 B | `9ac4eeac40056f4a` | API de modalidades | [[DP2-ESPECIFICACION_API_MODALIDADES]] | Media | Propuesta |

Relaciones: los 11 documentos citan el plan maestro como fuente; la cadena de modalidades es DISEÑO → REGLAS → API → KPIs.
**Esperado y no encontrado:** `ROADMAP_INCREMENTOS_IMPLEMENTACION.md` (es la §9 del plan maestro). **Excluido:** `Documentacion-parte-2/index.html` (render Quarto generado, sin seguimiento Git).
Otras copias idénticas fuera del repo: `~/Documentos/sgt-siaaf-backup-antes-de-git/Documentacion-parte-2/`, `~/Documentos/GitKraken/sistema-titulacion-unl/Documentacion-parte-2/`.

## 2. Fuentes referenciadas (no copiadas)

| Fuente | Ruta | Formato / n.º | Tema | Seguimiento Git | Notas que la usan |
|---|---|---|---|---|---|
| Constitución | `sgt-siaaf/.specify/memory/constitution.md`, `sgt-siaaf/specs/001-tramite-titulacion/constitucion.md` | MD | Gobierno del proyecto | Sí | [[SPECIFY]] |
| Spec 001 (backend) | `sgt-siaaf/specs/001-tramite-titulacion/` | 5 MD + 2 ADR vacíos | Requisitos, RN, flujos | Sí | [[SPECIFY]], [[ARTICLES_AND_PROVISIONS]] |
| Spec 003 (frontend) | `sgt-siaaf/specs/003-frontend-titulacion/` | 4 MD | Vistas, tareas, decisiones | Sí | [[TASKS]], [[BLOCKED_TASKS]] |
| OpenAPI | `backend/openapi.yaml` (único; `backend/contracts/openapi.yaml` retirado el 2026-11-12, DK-014) | YAML | Contrato | Sí | [[API_CONTRACTS]] |
| ADR | `backend/docs/adr/`, `docs/adr/` | 4 + 2 MD | Decisiones | Sí | [[ADR_INDEX]] |
| Docs Quarto | `docs/01-introduccion` … `docs/11-inteligencia-artificial`, `docs/index.qmd`, `docs/_quarto.yml` | ≈ 70 MD/QMD | Documentación técnica publicada | Sí | Varias |
| Auditoría backend y seguridad | `docs/auditoria-backend/**` | 21 MD | Seguridad, refactorización | Sí | [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]], [[06-AUDITS/BACKEND/BACKEND_AUDITS|Auditorías backend]] |
| Auditoría técnica | `docs/auditoria/` | 3 MD | — | Sí | [[06-AUDITS/BACKEND/BACKEND_AUDITS|Auditorías backend]] |
| KPI | `docs/indicadores/INFORME_DISENO_KPI.md` | MD | 40/47 KPIs | Sí | [[KPI_CATALOG]] |
| Firma electrónica | `docs/02-arquitectura/funcionalidades-futuras/firma-electronica/` | 9 MD | Propuesta diferida | Sí | [[FIRMA_EC]] |
| Sprint S1 | `docs/sprint-S1/` | 7 MD | Validación de hallazgos | Sí | [[06-AUDITS/BACKEND/BACKEND_AUDITS|Auditorías backend]] |
| Auditoría general | `auditoria/01…08` | 8 MD | — | **Eliminada** el 2026-11-12 por decisión del responsable (DK-014); recuperable desde el historial Git (`5ef0dbd`) | Ídem |
| Diseño UI | `diseno-ui/ui/titulacion-v2/especificaciones/01…08`, `GUIA_VISTAS_TITULACION.md` | 9 MD + 10 imágenes | Diseño | Sí | [[COMPONENTS]] |
| Prototipos A/B | `prototipos/prototipo-general/`, `prototipos/vistas-errores-unl/` | HTML/CSS/JS/PNG | Referencia visual (no copiar código) | Sí | [[COMPONENTS]] |
| Paquete DOCUMENTACION | `DOCUMENTACION/00_AUDITORIA` … `11_PUBLICACION_GITHUB_PAGES.md`, `CONTROL_MAESTRO_DOCUMENTACION.md` | 45 MD + diagramas | Documentación consolidada | **No** (local) | Varias |
| Académico | `docs/academico/ACD_3_CLINICA_ARQUITECTURA_Y_CONTRATO_API.md` | MD 112 KB | Actividad académica | **Eliminado** el 2026-11-12 por decisión del responsable (DK-014); nunca estuvo en Git | — |
| Diagramas | `DOCUMENTACION/03_ARQUITECTURA/diagramas/{clases_dominio.puml,workspace.dsl}`, `DOCUMENTACION/02_PROCESOS/diagramas/proceso_principal.bpmn` | PUML/DSL/BPMN | Idénticos a `docs/10-auditoria-2026-11/assets/` | Mixto | [[GENERAL_ARCHITECTURE]] |
| Instrucciones de agentes | `AGENTS.md`, `CLAUDE.md`, `.github/PULL_REQUEST_TEMPLATE.md` | MD | Flujo de trabajo | Sí | [[CLAUDE_CODE_OPENCODE_GUIDE]] |
| README | `README.md`, `backend/README.md`, `frontend/README.md` (`backend/README.md` contenía el README de gitleaks hasta el 2026-11-12; sustituido por el README real del backend) | MD | Instalación | Sí | [[DOCKER]] |

## 3. Exclusiones

| Elemento | Motivo |
|---|---|
| `.env`, `frontend/.env.local` | Secretos / configuración local: **no se leyeron** |
| `backend/src/media/private/**` (PDF de expedientes y resoluciones) | Datos de expedientes (posibles datos personales); ignorado por Git |
| `gh-pages/`, `gh-pages.zip`, `docs/_site/`, `docs/.quarto/`, `Documentacion-parte-2/index.html` | Artefactos generados. `gh-pages/` eliminada el 2026-11-12 (copia exacta de `docs/_site` de `HEAD`); `docs/_site/`, `docs/.quarto/` y `gh-pages/` en `.gitignore` (DK-014) |
| `node_modules/`, `.venv/`, `__pycache__/`, `coverage/`, `dist/` | Dependencias y cachés |
| `backend/gitleaks.exe` | Binario de herramienta; retirado del árbol el 2026-11-12 junto con su `LICENSE` (DK-014) |
| `scripts/spec001/{audit_complete,audit_tasks,check_t047,verify_matrix}.py` (trasladados desde la raíz el 2026-11-12, DK-014); `check_files.py` y `verify_all_tasks.py` (raíz, ruta de Windows fija, no funcionan) | Scripts; no son documentación |
| Papelera (`~/.local/share/Trash/files/SIAAF-KNOWLEDGE`, `…/documentacion-original*`) | Bóvedas vacías ya descartadas por el usuario |
| Plantillas vacías (`.specify/templates/*`, `FRONTEND_IMPLEMENTATION_PLAN.md`, ADR-001/002 de la spec 001) | 0 bytes |

## 4. Documentos normativos oficiales

**Ninguno en el repositorio** (ni PDF, DOCX ni XLSX institucionales). Ver [[INSTITUTIONAL_FRAMEWORK]].
