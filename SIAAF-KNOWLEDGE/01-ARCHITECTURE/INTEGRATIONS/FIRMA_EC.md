---
system: SGT-SIAAF
type: integration
area: firma-electronica
status: proposed
source: repository-docs + verified-code
last_verified: 2026-11-11
---

# Integración FirmaEC (firma electrónica)

## Estado real

**No implementada.** El sistema **simula** la firma del Memorando 162 (DEC-04, `docs/02-arquitectura/decisiones-arquitectonicas.md`): el Decano/a carga un PDF **firmado fuera del sistema**, y `backend/src/apps/resoluciones/services/declarar_aptitud.py` solo lo valida como PDF genérico (tamaño, magic bytes, hash) y lo guarda en almacenamiento privado. No hay verificación de certificado, cadena de confianza ni sellado de tiempo (VULN-010, VULN-012).

## Documentación de la propuesta (diferida)

Carpeta `docs/02-arquitectura/funcionalidades-futuras/firma-electronica/` (9 documentos, marcados "PROPUESTA / DIFERIDA. No implementada"):

| Documento | Tema |
|---|---|
| `README.md` | Por qué existe la carpeta, alcance, relación con SEC-T001…T021 |
| `ARQUITECTURA_PROPUESTA.md` | Arquitectura objetivo |
| `PROPUESTA_INTEGRACION_FIRMAEC.md` | Integración con FirmaEC |
| `FLUJO_FIRMA_DOCUMENTOS.md` | Flujo de firma |
| `CONTRATOS_API_PROPUESTOS.md` | Endpoints propuestos (inexistentes) |
| `SEGURIDAD_Y_PROTECCION_CLAVES.md` | Gestión de claves |
| `REQUISITOS_INSTITUCIONALES.md` | Requisitos UNL |
| `PENDIENTES_VALIDACION_UNL.md` | Pendientes de validación institucional |
| `PLAN_IMPLEMENTACION.md` | Plan |

## Reglas institucionales relacionadas

- Los documentos generados en el sistema **no tienen validez legal** (specify 001 §2.2.3).
- Las actas de sustentación (Fase 2) conservan **firma autógrafa física** (RN-006).

## Relacionado

[[ELECTRONIC_SIGNATURES]] · [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] · [[02-BACKEND/MODULES|Módulos backend]] (resoluciones)
