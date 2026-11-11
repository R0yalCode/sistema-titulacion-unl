---
system: SGT-SIAAF
type: process
area: tribunales
status: not-implemented
source: specify-001 + INFORME_DISENO_KPI
last_verified: 2026-11-11
---

# Tutores y tribunales

**Estado: no implementado.** No existe ningún modelo de tutor, director de trabajo ni tribunal (verificado en `backend/src/apps/*/adapters/models.py`).

| Elemento | Fuente | Estado |
|---|---|---|
| Director de trabajo de titulación | Solo es un **requisito documental** (`ART235-04-DIRECTOR-TRABAJO`, emisor DIRECTOR_CARRERA) | Implementado como petición |
| Tribunal evaluador: 3 docentes titulares (presidente + 2 vocales); el director no lo integra | RN-007, Art. 236 (Fase 2) | Diseño preliminar |
| Designación del tribunal | Atribución del DIRECTOR_CARRERA (specify 001 §6.1) | Fase 2 |
| KPIs de tutoría (sin tutor, cargas) | INFORME_DISENO_KPI §6.8 | No implementables |
| Entidad `TribunalEvaluador` | [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]] §1.5 | Propuesta |

## Relacionado

[[DEFENSES_AND_GRADES]] · [[DEGREE_PROCESS_OVERVIEW]]
