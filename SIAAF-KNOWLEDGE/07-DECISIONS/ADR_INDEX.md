---
system: SGT-SIAAF
type: decision-index
status: verified
source: repository-docs
last_verified: 2026-11-11
---

# Índice de decisiones arquitectónicas (ADR) y de clarificación (DEC)

> Los ADR del proyecto **no se copian** aquí: se indexan con su ruta real. Las decisiones sobre la propia bóveda están en [[DECISIONS_LOG]] (prefijo `DK-`) y [[ADR-KB-001-fuentes-originales]].

## 1. ADR del sistema

| ADR | Título | Archivo(s) | Estado | Observación verificada |
|---|---|---|---|---|
| 0001 | Arquitectura hexagonal — monolito modular | `backend/docs/adr/0001-…md`, `docs/adr/0001-…md` | Aceptado; implementado | Las dos copias **difieren** desde la línea 1 (`cmp`) |
| 0002 | Stack Django 5.2 + DRF + PostgreSQL 16 | `backend/docs/adr/0002-…md`, `docs/adr/0002-…md` | Aceptado; implementado | Copias distintas desde la línea 1 |
| 0003 | Autenticación JWT stateless (SimpleJWT) | `backend/docs/adr/0003-autenticacion-jwt-stateless.md` | Aceptado | **Desactualizado**: dice access 60 min; el código usa 30 min (`base.py`, SEC-T006) |
| 0009 | Django Admin como consola interna | `backend/docs/adr/0009-django-admin-consola-interna.md` | Aceptado; implementado | Referenciado en `config/urls.py` |
| 0004–0008 | ViewSets, storage privado, notificaciones, spectacular… | Declarados en `sgt-siaaf/specs/001-tramite-titulacion/plan.md` | **Sin archivo físico** | Hallazgo AUD-P3-05 (`docs/02-arquitectura/decisiones-arquitectonicas.md`) |
| ADR-001 / ADR-002 (spec 001) | Arquitectura / límites modulares | `sgt-siaaf/specs/001-tramite-titulacion/adr/` | **Vacíos (0 bytes)** | — |
| Consolidado | ADR del paquete documental | `DOCUMENTACION/03_ARQUITECTURA/ADR.md` (sin seguimiento Git) | — | — |

Registro y resumen previos: `docs/02-arquitectura/decisiones-arquitectonicas.md`, `docs/anexos/decisiones.md`.

## 2. Decisiones de clarificación (ojo: los identificadores se repiten)

| Familia | Ubicación | Rango | Ejemplos |
|---|---|---|---|
| DEC spec 001 (backend) | `sgt-siaaf/specs/001-tramite-titulacion/clarify.md` | DEC-01…DEC-05 | DEC-04 firma FirmaEC simulada; DEC-05 promedio SGA inalterable |
| DEC spec 003 (frontend) | `sgt-siaaf/specs/003-frontend-titulacion/clarify.md` | DEC-01…DEC-16 | DEC-08 "no se usa Git por ahora"; DEC-13 409/412/428 propuestos; DEC-14 `carrera_id` ≠ `opcion_titulacion`; DEC-15 mascotas; DEC-16 BE-05 no bloquea V-02 |
| DEC de seguridad | `docs/auditoria-backend/seguridad/plan-implementacion/` | DEC-002, DEC-003, DEC-009, DEC-010… | DEC-002 throttle login; DEC-003 throttle carga; DEC-010 CSP |

**Regla de cita:** menciona siempre la familia, p. ej. "DEC-04 (spec 001)" o "DEC-14 (spec 003)", porque `DEC-04` significa cosas distintas en cada spec.

## Relacionado

[[DECISIONS_LOG]] · [[GENERAL_ARCHITECTURE]] · [[GLOSSARY]]
