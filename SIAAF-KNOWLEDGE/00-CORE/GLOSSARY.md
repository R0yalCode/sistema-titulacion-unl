---
system: SGT-SIAAF
type: glossary
status: active
last_updated: 2026-11-11
---

# Glosario

## Dominio

| Término | Significado |
|---|---|
| **Expediente de titulación** | `ExpedienteTitulacion`: el trámite global del estudiante → [[STUDENT_RECORDS]] |
| **Petición documental** | Solicitud interna de un certificado a una dependencia (`PeticionDocumental`) → [[REQUESTS_AND_APPLICATIONS]] |
| **Checklist** | Verificación de los 5 requisitos del Art. 235 (`ChecklistVerification`) |
| **Observación accionable** | Motivo por el que un requisito queda `OBSERVADO` y debe subsanarse |
| **Subsanación** | Corrección de un requisito observado (nueva versión del documento) |
| **Informe de aptitud (Providencia #590)** | Informe legal del Secretario/a-Abogado/a |
| **Declaratoria de aptitud (Memorando #162)** | Resolución del Decano/a, firmada externamente |
| **TIC** | Trabajo de Integración Curricular (modalidad ordinaria; propuesta) |
| **EC** | Examen Complexivo (modalidad excepcional; propuesta) |
| **Elegibilidad / autorización / registro** | Condición académica / acto de autoridad / dato guardado: conceptos distintos ([[CURRICULAR_INTEGRATION_WORK]]) |
| **RRA-UNL** | Reglamento de Régimen Académico de la UNL |
| **FEIRNNR** | Facultad de la Energía, las Industrias y los Recursos Naturales No Renovables |
| **SGA / SIAAF** | Sistemas académicos institucionales (sin acceso; solo mock) |
| **FirmaEC** | Firma electrónica oficial de Ecuador (no integrada) |
| **SENESCYT** | Organismo de registro de títulos (Fase 3) |

## Técnico

| Término | Significado |
|---|---|
| **Scope** | Ámbito RBAC: OWN, CARRERA, FACULTAD, ASIGNADO, BORRADOR, ALLOW → [[PERMISSIONS_ROLES]] |
| **Bandeja** | Lista de expedientes donde interviene el rol (`/expedientes/bandeja/`) |
| **Stub** | Página o componente placeholder sin lógica (V-05…V-08) |
| **MSW** | Mock Service Worker: simula la API **solo en pruebas** |
| **SDD** | Spec-Driven Development (GitHub Spec Kit) |
| **COSMOS** | Versionado astronómico de entregas → [[COSMOS_VERSIONING]] |
| **DP2** | `Documentacion-parte-2` (12 documentos de planificación) |

## Familias de identificadores

| Prefijo | Significado | Dónde |
|---|---|---|
| RN-001…012 | Reglas de negocio (Fase 1–2) | specify 001 §12 |
| RN-MOD-* | Reglas de modalidades (propuesta) | [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]] |
| HU / RF / RNF / CA / EX / FL | Historias, requisitos funcionales y no funcionales, criterios de aceptación, excepciones, flujos | specify 001 |
| RFF / RNFF / CA-G | Requisitos y criterios del frontend | specify 003 |
| V-01…V-09 | Vistas del frontend | [[ROUTES]] |
| FE-Txxx | Tareas del frontend | [[TASKS]] |
| BE-01…11 | Dependencias backend no autorizadas | [[BLOCKED_TASKS]] |
| DEC-xx | Decisiones de clarificación: **¡se repiten entre spec 001, spec 003 y seguridad!** | [[ADR_INDEX]] §2 |
| INC-xx | **Ambiguo**: en `clarify.md` 003 = hallazgo/discrepancia (INC-13, 19, 21); en DP2 = **incremento** (INC-01…09) | — |
| SEC-Txxx | Tareas de seguridad (numeración inconsistente entre fuentes) | [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] |
| VULN-0xx | Vulnerabilidades (catálogo solo en DP2 y en el commit ECLIPSE) | Ídem |
| KPI-ROL-nn | Indicadores (EST, SEC, JUR, DEC, DIR, DEP, ADM, MOD) | [[KPI_CATALOG]] |
| GAP-* | Brechas (DP2 y esta bóveda) | [[BLOCKED_TASKS]] |
| DK-xxx | Decisiones sobre la bóveda | [[DECISIONS_LOG]] |
| C-xx / EV-xxx | Contradicciones / evidencias de la bóveda | [[DOCUMENT_TRACEABILITY]], [[EVIDENCE_INDEX]] |
