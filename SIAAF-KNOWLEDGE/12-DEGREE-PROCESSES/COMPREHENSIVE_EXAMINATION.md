---
system: SGT-SIAAF
type: process
area: modalidades
modality: EC
status: proposal
source: Documentacion-parte-2 (hypothesis)
last_verified: 2026-11-11
---

# Modalidad: Examen Complexivo (EC)

> **No implementada.** Propuesta e hipótesis normativa ([[DP2-DISENO_FUNCIONAL_MODALIDADES]], [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]]).

| Dimensión | Según la propuesta | Estado |
|---|---|---|
| Clasificación | **Excepcional**, condicionada a la situación académica y a la habilitación institucional | Hipótesis (Arts. 40, 212 inc. b, 233) |
| Condiciones académicas (elegibilidad) | ≥ 2 reprobaciones de la unidad de titulación **y** 3.ª matrícula efectiva, con evidencia documental | Hipótesis; sin definir qué es "unidad" ni cómo se verifica la matrícula |
| Verificación | El Secretario/a-Abogado/a verifica (mock SGA + revisión) | Propuesta |
| Habilitación / autorización | El Decano/a autoriza | Propuesta (RN-MOD-07, RN-MOD-CAM-02) |
| Registro | Cambio TIC→EC por un endpoint dedicado; `HistorialModalidad` inmutable con justificación (≥ 50 caracteres) y evidencia JSON | Propuesta |
| Selección por el estudiante | **No** seleccionable | Propuesta (RN-MOD-02) |
| Estados del expediente en que se permite el cambio | BORRADOR, ENVIADA, EN_VERIFICACION | Propuesta |
| Reversibilidad | Irreversible; un solo cambio por expediente | Propuesta, **sin artículo citado** |
| Proceso académico | Examen integral ante tribunal (Fase 2); acta propia | Propuesta |

## Requisitos previos a cualquier implementación (plan maestro §13)

1. Contraste directo con los Arts. 39, 40, 212, 216 y 233 del RRA-UNL (fuente primaria).
2. Aprobación expresa de la autoridad académica competente.
3. Mock del SGA validado (reprobaciones y matrícula). Hoy `core/adapters/mock_sga.py` devuelve récords ficticios; su estructura no se revisó para estos campos.
4. Confirmar el actor autorizador.
5. No implementar el selector en el frontend sin backend aprobado (DEC-14, CA-G-01).

## Relacionado

[[CURRICULAR_INTEGRATION_WORK]] · [[KPI_CATALOG]] (KPI-MOD-06/07/08)
