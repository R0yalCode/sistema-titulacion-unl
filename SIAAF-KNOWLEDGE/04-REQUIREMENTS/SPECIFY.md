---
system: SGT-SIAAF
type: requirements
status: verified
source: sgt-siaaf/specs
last_verified: 2026-11-11
aliases: [PLAN, ACCEPTANCE_CRITERIA]
---

# Especificaciones (SDD): mapa de lectura

El proyecto usa **Spec-Driven Development** (GitHub Spec Kit). Los documentos **no se copian** a la bóveda (son vivos): léelos por sección.

## Jerarquía de autoridad (`AGENTS.md`)

1. **Constitución**: `sgt-siaaf/.specify/memory/constitution.md` y `sgt-siaaf/specs/001-tramite-titulacion/constitucion.md` (intocables).
2. **Spec 003 (frontend)**: `sgt-siaaf/specs/003-frontend-titulacion/`.
3. **Backend vigente**: código, `backend/openapi.yaml` y migraciones.
4. `AGENTS.md`.

Las specs `002` y `004` **no existen**.

## Spec 001: trámite de titulación (backend MVP)

| Archivo | Tamaño | Contenido clave | Secciones útiles |
|---|---|---|---|
| `specify.md` | 69 KB | Fuentes (§1.3), alcance por fases (§2.3), actores y RBAC (§6), entidades (§7), flujos FL-01…05 (§8), HU-001…010 (§9), RF, RN-001…012 (§12), excepciones EX-001…010 (§13), CA, matriz de trazabilidad | §6, §8, §12 |
| `clarify.md` | 37 KB | DEC-01…05 y aclaraciones | — |
| `plan.md` | 46 KB | Plan técnico; declara ADR-0004…0008 (sin archivo) | — |
| `tasks.md` | 74 KB | Tareas backend T0xx | — |
| `constitucion.md` | 29 KB | Constitución | — |
| `adr/ADR-001-…`, `adr/ADR-002-…` | 0 B | Vacíos | — |

## Spec 003: frontend

| Archivo | Tamaño | Contenido clave | Secciones útiles |
|---|---|---|---|
| `clarify.md` | 42 KB | DEC-01…16, INC-xx (discrepancias contrato/código), PQ, D-FE, B-xx | INC-13, 19, 20, 21; DEC-13, 14, 15, 16 |
| `specify.md` | 60 KB | Vistas V-01…V-09, rutas (§6), RFF/RNFF, criterios globales CA-G (§9.1), V-03 (§9.2), estados de error (§9.3) | §6, §9 |
| `plan.md` | 32 KB | Stack, estructura (§4), sesión (§6), fases F0…F6 | §4, §6 |
| `tasks.md` | 124 KB | Tareas FE-T y estados; BE-01…11 (§2); trazabilidad (§17); orden (§18); DoD (§19) | §2, §18, §19 |

## Criterio de aceptación transversal más citado

**CA-G-01 (cero simulación):** nada de datos, usuarios, estados ni porcentajes que el backend no entregue.

## Otros requisitos

`DOCUMENTACION/01_ESPECIFICACION/` (RF, RNF, historias, casos de uso, matriz de trazabilidad; **sin seguimiento Git**), `auditoria/03_MATRIZ_FUNCIONAL.md`, `auditoria/05_AUDITORIA_SDD.md`.

## Relacionado

[[TASKS]] · [[REGULATORY_TRACEABILITY]] · [[GENERAL_TRACEABILITY_MATRIX]]
