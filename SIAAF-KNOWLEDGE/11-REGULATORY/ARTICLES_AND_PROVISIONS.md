---
system: SGT-SIAAF
type: regulatory
status: pending-primary-source
source: specs + Documentacion-parte-2
last_verified: 2026-11-11
aliases: [DEGREE_REGULATIONS]
---

# Artículos y disposiciones citados

Estados de validación:
- **Citado (spec):** lo cita una especificación aprobada del proyecto como fuente primaria; el texto literal no está en el repositorio.
- **Hipótesis:** la propia fuente advierte que **no** se contrastó con el texto vigente.

| Disposición | Contenido según la fuente | Fase / ámbito | Estado | Dónde se cita |
|---|---|---|---|---|
| RRA-UNL Art. 231 | Citado entre las fuentes (sin detalle en las secciones revisadas) | — | Citado (spec) | specify 001 §1.3 |
| **RRA-UNL Art. 235** | Declaratoria de aptitud legal: **5 requisitos base** (récord académico legalizado; certificado de prácticas/vinculación; certificado B1 de idioma; certificado del director de trabajo; certificado de Tesorería de no adeudar) y **plazo de 8 días laborables** | Fase 1 (MVP) | Citado (spec); **implementado** (migración `peticiones/0002_catalogo_base_art235`, `plazo_calculator.py`) | specify 001 RN-001, RN-002 |
| RRA-UNL Art. 236 | Tribunal de sustentación: 3 docentes titulares (presidente + 2 vocales); el director del trabajo no lo integra | Fase 2 | Citado (spec); no implementado | specify 001 RN-007 |
| RRA-UNL Art. 237 | Escala 0–10; nota final = promedio de récord (SGA) y sustentación; Sobresaliente 9,0–10 · Muy Buena 8,0–8,99 · Buena 7,0–7,99 · Reprobado < 7,0 | Fase 2 | Citado (spec); no implementado | specify 001 RN-008 |
| RRA-UNL Arts. 243–244 | Acta consolidada y registro SENESCYT | Fase 3 | Citado (spec); no implementado | specify 001 §2.3 |
| RRA-UNL Art. 39 | TIC como opción ordinaria: 100 % de asignaturas aprobadas **o** planificación del 85 % de horas | Modalidades | **Hipótesis** | [[DP2-DISENO_FUNCIONAL_MODALIDADES]] §1.1 |
| RRA-UNL Art. 40 | EC excepcional: 2 reprobaciones de la unidad de titulación + 3.ª matrícula efectiva | Modalidades | **Hipótesis** | Ídem |
| RRA-UNL Art. 212 (inc. b) | Procedimiento general de titulación / habilitación excepcional del EC | Modalidades | **Hipótesis** | Ídem |
| RRA-UNL Art. 216 | Requisitos de elegibilidad ordinaria (TIC) | Modalidades | **Hipótesis** | Ídem |
| RRA-UNL Art. 233 | Procedimiento de la modalidad excepcional | Modalidades | **Hipótesis** | Ídem |
| Providencia N° 590 SG-FEIRNNR-UNL | Estructura del informe legal, checklist de 5 requisitos, recepción con fecha y hora, firmas del Secretario/a-Abogado/a y del Analista | Fase 1 | Plantilla citada; el backend genera un PDF "modelo" | specify 001 §1.3 |
| Memorando N° UNL-FEIRNNR-2026-162-M | Declaratoria del Decano/a con firma electrónica externa | Fase 1 | Plantilla citada; carga de PDF firmado | specify 001 §1.3 |

## Pendientes de validación humana

1. Texto vigente de los Arts. 39, 40, 212, 216 y 233 (las 6 preguntas de [[DP2-DISENO_FUNCIONAL_MODALIDADES]] §1.2).
2. Si el plazo de 8 días se pausa o se reinicia con observaciones (supuesto S-01 de specify 001; el código **pausa**).
3. Descartar "Proyecto de Emprendimiento" como modalidad (INC-15 de la spec 003; prohibido en la UI por CA-G-01).

## Relacionado

[[INSTITUTIONAL_FRAMEWORK]] · [[REGULATORY_TRACEABILITY]]
