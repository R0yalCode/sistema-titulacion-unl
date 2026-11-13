---
system: SGT-SIAAF
type: reference
status: verified
last_verified: 2026-11-11
---

# Mapa de la documentación del repositorio

Para el inventario completo y las decisiones de incorporación, ver [[SOURCE_CATALOG]]. Esta nota es una guía rápida de "dónde buscar qué".

| Necesito… | Busca en |
|---|---|
| Reglas que gobiernan el proyecto | `sgt-siaaf/.specify/memory/constitution.md` |
| Requisitos del backend / reglas RN | `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §12 |
| Vistas, rutas y criterios del frontend | `sgt-siaaf/specs/003-frontend-titulacion/specify.md` §6, §9 |
| Estado de una tarea FE-T | `sgt-siaaf/specs/003-frontend-titulacion/tasks.md` (`grep -n "FE-Txxx"`) |
| Discrepancias contrato ↔ código | `sgt-siaaf/specs/003-frontend-titulacion/clarify.md` (INC-xx) |
| Contrato API | `backend/openapi.yaml` |
| Diseño visual y estados de error | `diseno-ui/ui/titulacion-v2/especificaciones/01…08` |
| Seguridad | `docs/auditoria-backend/seguridad/` |
| Plan de incrementos | `SIAAF-KNOWLEDGE/90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` §9 (el original de `Documentacion-parte-2/` se retiró el 2026-11-12, DK-014) |
| KPIs | `docs/indicadores/INFORME_DISENO_KPI.md` |
| Sitio publicado | GitHub Pages desde `docs/` (Quarto) |

Notas derivadas de DP2: `10-REFERENCES/DOCUMENTATION-PART-2/` (12 notas `DP2-*`). Recursos externos: [[EXTERNAL_RESOURCES]].
