---
title: "Anexos — Referencias"
---

# Anexos — Referencias

## Documentos normativos del proyecto

| Documento | Ubicación |
|---|---|
| Constitución (v2.1, canónica en specs) | `sgt-siaaf/specs/001-tramite-titulacion/constitucion.md` |
| Constitución (copia de memoria, v2.0 — desactualizada) | `sgt-siaaf/.specify/memory/constitution.md` |
| Especificación backend | `sgt-siaaf/specs/001-tramite-titulacion/specify.md` |
| Plan backend | `sgt-siaaf/specs/001-tramite-titulacion/plan.md` |
| Tareas backend (T001…T046) | `sgt-siaaf/specs/001-tramite-titulacion/tasks.md` |
| Clarificación backend (AP/DEC/RSK) | `sgt-siaaf/specs/001-tramite-titulacion/clarify.md` |
| Especificación frontend (V-01…V-09) | `sgt-siaaf/specs/003-frontend-titulacion/specify.md` |
| Plan frontend | `sgt-siaaf/specs/003-frontend-titulacion/plan.md` |
| Tareas frontend (FE-T) | `sgt-siaaf/specs/003-frontend-titulacion/tasks.md` |
| Clarificación frontend (DEC-11…14) | `sgt-siaaf/specs/003-frontend-titulacion/clarify.md` |

## ADRs

- `backend/docs/adr/0001-arquitectura-hexagonal-monolito-modular.md`
- `backend/docs/adr/0002-stack-django-drf-postgresql.md`
- `backend/docs/adr/0003-autenticacion-jwt-stateless.md`
- `backend/docs/adr/0009-django-admin-consola-interna.md`

## Auditorías y sprints previos

- `auditoria/01…08` (auditoría general del 01-nov-2026)
- `docs/sprint-S1/` (estabilización del backend, 02-nov-2026)
- `docs/security_report.md` (gitleaks/bandit/safety, 22-oct-2026)

## Contrato de API

- `backend/openapi.yaml` (canónico y único, generado con drf-spectacular; la copia `backend/contracts/openapi.yaml` se retiró el 2026-11-12, DK-014)
- Servido en vivo: `/api/v1/schema/`, `/api/v1/docs/`, `/api/v1/redoc/`

## Documentación de diseño UI

- `diseno-ui/ui/titulacion-v2/especificaciones/01…08` (08 = estados de error)
- `diseno-ui/ui/titulacion-v2/GUIA_VISTAS_TITULACION.md` (copia canónica)
- Prototipos A y B (referencia visual no normativa)

## Estándares externos

- [C4 Model](https://c4model.com/) — modelo de arquitectura usado en los diagramas
- [OpenAPI 3.x](https://spec.openapis.org/) — formato del contrato
- [Quarto](https://quarto.org/) — generador de esta documentación
- [Mermaid](https://mermaid.js.org/) — diagramas embebidos
- WCAG 2.1 AA — objetivo de accesibilidad del frontend
