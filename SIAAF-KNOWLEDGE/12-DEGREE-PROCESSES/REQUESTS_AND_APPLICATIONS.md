---
system: SGT-SIAAF
type: process
area: peticiones
status: verified
source: verified-code + specify-001
last_verified: 2026-11-11
---

# Peticiones documentales y solicitudes

**Código:** `backend/src/apps/peticiones/` · **Frontend:** V-05/V-06 (stubs) y `features/expediente/PeticionesSection.tsx` (V-04).

## Requisitos base (migración `peticiones/0002_catalogo_base_art235.py`)

| Código | Nombre | Rol emisor sugerido |
|---|---|---|
| `ART235-01-RECORD-ACADEMICO` | Récord académico legalizado | SECRETARIA_CARRERA |
| `ART235-02-PRACTICAS-VINCULACION` | Certificado de prácticas o vinculación | RESPONSABLE_DEPENDENCIA |
| `ART235-03-IDIOMA-B1` | Certificado de idioma nivel B1 | RESPONSABLE_DEPENDENCIA |
| `ART235-04-DIRECTOR-TRABAJO` | Certificado del director de trabajo | DIRECTOR_CARRERA |
| `ART235-05-TESORERIA` | Certificado de no adeudar (Tesorería) | RESPONSABLE_DEPENDENCIA |

## Ciclo de una petición

`PENDIENTE` → (`POST /peticiones/{id}/solicitar-emision/`, estudiante) `SOLICITADO` → (`POST /peticiones/{id}/documento/`) `CARGADO` → (evaluación de checklist) `VERIFICADO` | `OBSERVADO` → (subsanación: versión N+1) … `LEGALIZADO` existe en el enum.

Reglas: sin correo (notificación in-app, DEC-01 de la spec 001); PDF ≤ 10 MB con `%PDF-` (RN-009); versionado sin borrado (RN-011); carga limitada a 10/h (`document_upload`).

## Hallazgo verificado

**3 de los 5 requisitos tienen como emisor a `RESPONSABLE_DEPENDENCIA`, que no tiene ningún permiso en `RBAC_MATRIX`** ([[PERMISSIONS_ROLES]]). Hoy esas dependencias no pueden cargar su documento por la API; solo pueden hacerlo el estudiante (SCOPE_OWN, en línea con DEC-02 de la spec 001: "carga por Opción A, estudiante/secretaría según regla") o el ADMINISTRADOR. Encaja con VULN-006 / SEC-06.

## Pendientes

- BE-02: no existe `GET /peticiones/{id}/` ni el listado de documentos (V-06 lo necesita).
- V-05/V-06 sin implementar (FE-T501…T605).

## Relacionado

[[DEGREE_PROCESS_OVERVIEW]] · [[DOCUMENT_MANAGEMENT]] · [[API_CONTRACTS]]
