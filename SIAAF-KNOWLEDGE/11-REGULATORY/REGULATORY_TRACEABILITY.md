---
system: SGT-SIAAF
type: traceability
area: regulatory
status: partially-verified
source: specs + verified-code
last_verified: 2026-11-11
---

# Trazabilidad normativa → regla → implementación

| Norma | Regla | Requisito / historia | Implementación verificada | Prueba (existe) |
|---|---|---|---|---|
| Art. 235 (5 requisitos) | RN-001 | HU-001, RF-001 | `peticiones/adapters/migrations/0002_catalogo_base_art235.py`; `crear_expediente.py` crea las 5 peticiones | `test_crear_expediente.py` |
| Art. 235 (8 días laborables) | RN-002, RN-010 | HU-004, RF-002/003 | `expedientes/domain/plazo_calculator.py`; `enviar_expediente.py` fija `fecha_recepcion` y `fecha_limite_atencion` | `test_plazo_calculator.py`, `test_enviar_expediente.py` |
| Art. 235 (bloqueo de informe) | RN-003 | — | `verificacion/services/validar_checklist_completo.py` | `test_validar_checklist_completo.py` |
| Separación informe/declaratoria | RN-004 | — | RBAC `informes` (SEC_ABO/ANALISTA) y `declaratorias` (DECANO) | `test_rbac_permissions.py` |
| Promedio SGA inalterable | RN-005 | — | `core/adapters/mock_sga.py` (solo lectura) | — |
| Art. 236/237 | RN-006…008 | Fase 2 | **No implementado** | — |
| PDF ≤ 10 MB con `%PDF-` | RN-009 | — | `core/adapters/pdf_validation.py` | `test_pdf_ingestion_and_security.py` |
| Versionado N+1 | RN-011 | — | `DocumentoEntregado.version` / `es_vigente` | `test_cargar_documento.py` |
| Sin escritura en BD legadas | RN-012 | — | `SGAMockAdapter` (sin conexión) | — |
| Arts. 39/40/212/216/233 (modalidades) | RN-MOD-* (propuesta) | BE-06 | **No implementado** | — |

Matriz completa original: `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §(matriz de trazabilidad, ≈ línea 690) y `DOCUMENTACION/01_ESPECIFICACION/MATRIZ_TRAZABILIDAD.md`.

## Relacionado

[[ARTICLES_AND_PROVISIONS]] · [[GENERAL_TRACEABILITY_MATRIX]]
