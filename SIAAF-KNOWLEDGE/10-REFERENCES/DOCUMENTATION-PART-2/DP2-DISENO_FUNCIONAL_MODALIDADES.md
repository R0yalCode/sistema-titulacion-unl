---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/DISENO_FUNCIONAL_MODALIDADES_TITULACION.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/DISENO_FUNCIONAL_MODALIDADES_TITULACION.md
source_version: "1.0"
source_date: 2026-11-09
nature: functional-design (proposal)
vigencia: propuesta; pendiente-validacion-normativa; requiere-BE-06
last_verified: 2026-11-11
---

# DP2 · Diseño funcional de modalidades de titulación

**Original:** [[DISENO_FUNCIONAL_MODALIDADES_TITULACION]]
**Estado declarado por la fuente:** "Diseño pendiente de validación normativa y autorización BE-06".

## Contenido

1. **Contexto normativo (§1)**: Arts. 39, 40, 212, 216, 233 RRA-UNL, con la advertencia expresa de que **no se contrastaron con el texto vigente** y de que el análisis secundario (NotebookLM) "no constituye fuente normativa". Seis decisiones requieren aprobación humana (texto exacto, definición de 100 % / 85 %, de "2 reprobaciones", de "3.ª matrícula efectiva", actor autorizador y descarte de "Proyecto de Emprendimiento").
2. **Enum (§2.1):** `ModalidadTitulacion`: `TIC` = Trabajo de Integración Curricular; `EC` = Examen Complexivo.
3. **Características (§2.2):** TIC ordinaria y predeterminada (automática al crear el expediente); EC excepcional, no seleccionable por el estudiante, la verifica el Secretario y la autoriza el Decano; proceso académico de Fase 2.
4. **Modelo de datos (§4):** campo `opcion_titulacion` (max 3, default TIC, index) y modelo `HistorialModalidad` (anterior, nueva, fecha, `autorizado_por`, justificación, `evidencia_academica` JSON, `estado_tercera_matricula`).
5. **Servicios (§5):** `verificar_elegibilidad_ec.py` y `cambiar_modalidad.py` (código de ejemplo propuesto).
6. **API y RBAC (§6–7):** ver [[DP2-ESPECIFICACION_API_MODALIDADES]].
7. **Frontend (§8):** V-03 `NuevaSolicitudForm`, V-04 `ExpedienteHeader`, V-08 acciones, `ModalidadPanel`.
8. **Validación normativa requerida (§11)** antes de implementar.

## Verificación contra el código

Nada de lo anterior existe: no hay `opcion_titulacion`, `HistorialModalidad`, servicios ni endpoints (grep en `backend/src`, 2026-11-11). La spec 003 (DEC-14) mantiene `carrera_id` ≠ `opcion_titulacion` y prohíbe simular el selector (CA-G-01).

## Relacionado

[[CURRICULAR_INTEGRATION_WORK]] · [[COMPREHENSIVE_EXAMINATION]] · [[ARTICLES_AND_PROVISIONS]] · [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]]
