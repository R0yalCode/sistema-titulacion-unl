# Historias de usuario y casos de uso — SGT-SIAAF (backend)

**Fuente única:** `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §9 (HU-001 a HU-010) y §13 (matriz de excepciones EX-001 a EX-010). Se consolida en tabla para evitar reproducir íntegramente el documento fuente; los criterios de aceptación completos en formato Dado/Cuando/Entonces están en la fuente original y no se reescriben aquí.

## 1. Historias de usuario

| ID | Actor | Objetivo | Precondición | Reglas de negocio asociadas | Estado |
|---|---|---|---|---|---|
| HU-001 | ESTUDIANTE | Registrar el expediente de aptitud legal | Sin expediente activo | RN-001 | **IV** |
| HU-002 | ESTUDIANTE | Solicitar certificados internamente, sin correo | Expediente en BORRADOR/OBSERVADA | — | **IV** |
| HU-003 | Usuario autorizado | Adjuntar certificados PDF (≤10 MB) | Petición válida | RN-009 | **IV** |
| HU-004 | ESTUDIANTE | Enviar la solicitud formalmente | 5 requisitos cargados | RN-002, RN-010 | **IV** |
| HU-005 | Funcionario (Secretaría/Abogacía/Decanato) | Consultar bandeja filtrada por competencia | Rol administrativo autenticado | — | **IV** |
| HU-006 | SECRETARIO_ABOGADO | Evaluar checklist de 5 requisitos | Expediente ENVIADA/EN_VERIFICACION | — | **IV** |
| HU-007 | SECRETARIO_ABOGADO | Registrar motivo de observación | Requisito con inconsistencias | RN-003 | **IV** |
| HU-008 | ESTUDIANTE | Subsanar documento observado | Expediente OBSERVADA | RN-011 | **IV** |
| HU-009 | SECRETARIO_ABOGADO | Emitir informe legal de aptitud | 100 % requisitos VERIFICADO | RN-003, RN-004 | **IV** |
| HU-010 | DECANO | Registrar declaratoria con memorando firmado | Expediente INFORME_EMITIDO | RN-004 | **IV** |

Los 10 casos de uso del MVP (HU-001 a HU-010) corresponden uno a uno con los flujos FL-01 a FL-05 descritos en `CONTEXTO_PROYECTO.md` §1 y con los RF-001 a RF-013 de `REQUISITOS_FUNCIONALES.md`. No existen historias de usuario adicionales para Fase 1 en la fuente; HU asociadas a Fase 2/3 (sustentación, SENESCYT) no se formalizaron como HU numeradas en `specify.md` — solo como RF-014 a RF-016 de diseño preliminar.

## 2. Excepciones y escenarios alternativos (EX-001 a EX-010)

| ID | Escenario | Código HTTP esperado | Verificado contra código (Fase 0) |
|---|---|---|---|
| EX-001 | Token JWT ausente o vencido | 401 | No reverificado en esta pasada (Fase 6) |
| EX-002 | Acceso denegado por RBAC | 403 | Coherente con `RBAC_MATRIX` de mundo cerrado observada en el código |
| EX-003 | Intento IDOR a expediente ajeno | 403/404 | Coherente con `ScopeFilterMixin` observado en el código |
| EX-004 | Archivo PDF > 10 MB | 400 | Coherente con `core/adapters/pdf_validation.py` |
| EX-005 | Magic bytes inválidos | 400 | Coherente con `core/adapters/pdf_validation.py` |
| EX-006 | Transición de estado inválida | 400 | No reverificado en esta pasada (Fase 4) |
| EX-007 | Informe con requisitos observados | 422 | Coherente con RN-003 (bloqueo verificado en flujo documentado) |
| EX-008 | Falla en adaptador/mock del SGA | 503 | No reverificado en esta pasada |
| EX-009 | Error interno no mapeado | 500 | **Hallazgo relevante**: `docs/CLAUDE.md`/`INC-21` (ver frontend) documenta que varias excepciones de dominio reales (observar/evaluar/subsanar) responden **500 real**, no 400/404 como anticipaba la especificación — es una discrepancia entre lo especificado (EX-009 como "no mapeado", es decir excepcional) y la práctica real donde reglas de negocio conocidas también devuelven 500. Se documenta como hallazgo, no se corrige aquí. |
| EX-010 | Tribunal inválido (Director como miembro) | 422 | NA — pertenece a Fase 2, no implementada |

## 3. Casos de uso del frontend (referencia, no exhaustivo)

El frontend define 9 vistas (V-01 a V-09, `specs/003-frontend-titulacion/specify.md` §9) que materializan estas mismas historias de usuario del backend desde la perspectiva de interfaz. No se duplican aquí; su estado de cierre (V-01 a V-04 Hechas, V-05+ sin iniciar) se documenta en `CLAUDE.md` y se referencia en `MATRIZ_TRAZABILIDAD.md`.

## 4. Hallazgo heredado de EX-009 / INC-21

El hallazgo de EX-009 (arriba) coincide con lo que el frontend ya documentó como **INC-21**: "varias excepciones de dominio en observar/evaluar/subsanar responden HTTP 500 real (no 400/404) aunque describen reglas de negocio". Esto afecta la fidelidad del contrato de errores que `specify.md` describe (EX-007 como 422 "mapeado" vs. la realidad de algunos 500 "no mapeados" que en realidad sí son reglas de negocio conocidas). Se recomienda, para la Fase 5 (API) y Fase 6 (seguridad), verificar exactamente qué excepciones de dominio producen 500 y si corresponden a errores de programación genuinos o a reglas de negocio que deberían mapearse a 400/422.
