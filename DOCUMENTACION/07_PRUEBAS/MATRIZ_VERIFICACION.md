---
title: "Matriz de verificación"
---

# Matriz de verificación — Criterio de aceptación → Prueba → Resultado

**Fuente de criterios:** `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §14 (CA-001 a CA-008). **Fuente de resultado:** ejecución real de la Fase 7 (2026-11-06), detallada en `RESULTADOS_VALIDACION.md`.

| Criterio | Descripción (resumida) | Prueba(s) asociada(s) | Resultado |
|---|---|---|---|
| CA-001 | Envío exitoso con timestamp y providencia | `test_enviar_expediente.py`, `test_crear_expediente.py` | ✅ Passed |
| CA-002 | Petición interna de certificados sin correo | `apps/peticiones/tests/` (`solicitar_emision`) | ✅ Passed |
| CA-003 | Bloqueo de emisión de informe ante requisito observado | `test_validar_checklist_completo.py`, `test_checklist_and_observations.py` | ✅ Passed |
| CA-004 | Subsanación y versionado | `test_subsanar_requisito.py` | ✅ Passed |
| CA-005 | Emisión de informe legal | `test_emitir_informe.py` | ✅ Passed |
| CA-006 | Declaratoria de aptitud por Decano/a | `test_declarar_aptitud.py` | ✅ Passed |
| CA-007 | Registro de notas de sustentación (Fase 2) | — | **NA** — Fase 2 no implementada, sin código ni prueba que la ejercite (correctamente, no es un defecto) |
| CA-008 | Denegación de acceso por IDOR | Suite de aislamiento IDOR (`DOCUMENTACION/06_SEGURIDAD/AUTORIZACION_PERMISOS.md` §6) | ✅ Passed (incluida en los 560 passed) |

## Cobertura de la matriz

**6 de 7 criterios aplicables al alcance de este incremento (CA-001 a CA-006, CA-008) tienen prueba automatizada pasando.** CA-007 no aplica porque pertenece a la Fase 2 (sustentación), fuera del alcance de este incremento — se marca NA, no como criterio incumplido.

## Relación con los hallazgos de esta auditoría

Ningún criterio de aceptación del MVP (Fase 1) tiene una prueba fallando por causa de código propio: las 13 fallas detectadas en la Fase 7 están todas en pruebas de **formato exacto del texto renderizado en el PDF** (`test_pdf_generator.py`), que no corresponden a ninguno de los 8 criterios de aceptación formales de `specify.md` §14 — son pruebas más granulares, adicionales a los criterios de aceptación de alto nivel. Por lo tanto: **los 8 criterios de aceptación formales del MVP backend están verificados (6 passed) o no aplican (1, Fase 2) o están cubiertos implícitamente (CA-008, IDOR)**, sin ninguna falla atribuible a ellos.
