---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/ESPECIFICACION_API_MODALIDADES_TITULACION.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/ESPECIFICACION_API_MODALIDADES_TITULACION.md
source_version: "1.0"
source_date: 2026-11-09
nature: api-spec (proposal)
vigencia: propuesta; requiere-BE-06
last_verified: 2026-11-11
---

# DP2 · Especificación API de modalidades

**Original:** [[ESPECIFICACION_API_MODALIDADES_TITULACION]]

## Endpoints propuestos (ninguno existe)

| Endpoint | Método | Roles | Recurso RBAC propuesto |
|---|---|---|---|
| `/api/v1/expedientes/{id}/modalidad/` | GET | Estudiante (own), Secretario, Analista, Decano, Director, Admin | `expedientes:modalidad` GET |
| `/api/v1/expedientes/{id}/modalidad/elegibilidad/` | GET | Secretario, Decano, Admin | `expedientes:modalidad` GET |
| `/api/v1/expedientes/{id}/modalidad/cambiar/` | POST | Secretario (verifica), Decano (autoriza), Admin | `expedientes:modalidad` POST |
| `/api/v1/modalidades/` | GET | Todos los autenticados | `modalidades` GET |

Otros contenidos: esquemas `ModalidadTitulacion`, `HistorialModalidad` y `ElegibilidadEC` (§2); integración con `POST /expedientes/`, el detalle y la bandeja (§4); evento de auditoría y señal `post_save` (§5); tests de contrato por endpoint (§7); ejemplo OpenAPI con drf-spectacular (§8); checklist previo a la implementación (§9).

## Observaciones

- Usa un mismo recurso RBAC (`expedientes:modalidad` GET) para dos GET con conjuntos de roles distintos: haría falta un recurso propio para la elegibilidad.
- En §1 el GET de catálogo lo ven "todos"; en el [[DP2-PLAN_MAESTRO]] §4.4 solo "Admin".

## Relacionado

[[API_CONTRACTS]] §3 · [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]]
