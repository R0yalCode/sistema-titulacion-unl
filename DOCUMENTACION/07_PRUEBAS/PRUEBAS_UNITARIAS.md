---
title: "Pruebas unitarias"
---

# Pruebas unitarias — SGT-SIAAF (backend)

**Fuente:** ejecución real (Fase 7, 2026-11-06), detalle completo en `RESULTADOS_VALIDACION.md`. Esta página organiza el mismo resultado por componente probado, para trazabilidad con `COMPONENTES_NEGOCIO.md`.

## 1. Archivos y componentes probados (los 11 servicios + dominio puro)

| Componente probado | Archivo de prueba | Resultado (Fase 7) |
|---|---|---|
| `crear_expediente` | `apps/expedientes/tests/test_crear_expediente.py` | ✅ incluido en los 560 passed |
| `enviar_expediente` | `apps/expedientes/tests/test_enviar_expediente.py` | ✅ |
| `PlazoLaboralCalculator` (dominio puro) | `apps/expedientes/tests/test_plazo_calculator.py` | ✅ |
| `solicitar_emision` | `apps/peticiones/tests/` | ✅ |
| `cargar_documento` | `apps/peticiones/tests/` | ✅ |
| `evaluar_checklist` | `apps/verificacion/tests/test_evaluar_checklist.py` | ✅ |
| `registrar_observacion` | `apps/verificacion/tests/test_checklist_and_observations.py` | ✅ |
| `subsanar_requisito` | `apps/verificacion/tests/test_subsanar_requisito.py` | ✅ |
| `validar_checklist_completo` | `apps/verificacion/tests/test_validar_checklist_completo.py` | ✅ |
| `emitir_informe` | `apps/resoluciones/tests/test_emitir_informe.py` | ✅ |
| `declarar_aptitud` | `apps/resoluciones/tests/test_declarar_aptitud.py` | ✅ |
| Generación de PDF (ReportLab) | `apps/resoluciones/tests/test_pdf_generator.py` | ⚠️ **17/30 passed, 13 failed** — causa raíz confirmada: dependencia opcional de lectura (`pypdf`) ausente del entorno, no un defecto del generador (ver `RESULTADOS_VALIDACION.md` §2) |
| `notification_service` | `apps/notificaciones/tests/` | ✅ |
| RBAC / `HasRolePermission` | `apps/authentication/tests/` | ✅ |
| `ISGALegacyPort` / `SGAMockAdapter` | `core/adapters/tests/test_mock_sga.py`, `core/tests/test_notifications_and_audit.py` | ✅ (parte del alcance extendido `src/core`) |
| Validación de PDF (magic bytes, SHA-256) | `core/adapters/tests/test_pdf_validation.py` | ✅ |

## 2. Cobertura por componente (extracto de los puntos más bajos, Fase 7)

Ver tabla completa en `RESULTADOS_VALIDACION.md` §3. Los tres componentes con menor cobertura de código fuente:

1. `core/adapters/security_headers.py` — **0 %** (sin ninguna prueba).
2. `apps/verificacion/adapters/views.py` — 65 %.
3. `apps/notificaciones/services/notification_service.py` — 75 %.

## 3. Conclusión

De los 11 servicios de negocio documentados en `DOCUMENTACION/04_BACKEND/COMPONENTES_NEGOCIO.md`, **10 tienen su suite de pruebas unitarias pasando al 100 %** en esta ejecución; el componente de generación de PDF tiene fallas, pero con causa raíz externa al propio generador, confirmada por experimento controlado (instalar la dependencia faltante hace pasar las 30 pruebas del archivo). No se detectó ningún fallo de causa desconocida en el nivel unitario.
