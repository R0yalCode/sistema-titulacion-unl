---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md
source_version: "1.0"
source_date: 2026-11-09
nature: planning
vigencia: vigente-como-plan; estado-frontend-desactualizado
last_verified: 2026-11-11
---

# DP2 · Plan maestro de implementación integral

**Original:** [[PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF]] · Commit de incorporación: `bf74d4d` (ROSETTA)
**Naturaleza:** análisis y planificación; el propio documento dice "no implementación".

## Objetivo y alcance

Consolida el estado de backend, seguridad, KPIs, modalidades y frontend, y define **9 incrementos (INC-01…INC-09)** con sus dependencias. Es el documento central de DP2: los otros 11 desarrollan sus secciones (§14), y el "ROADMAP_INCREMENTOS_IMPLEMENTACION.md" esperado **es su §9** (nunca se creó como archivo).

## Contenido clave (identificadores)

- **Brechas:** GAP-MOD-01…07, GAP-KPI-01…04, GAP-SES-01…03, GAP-FE-01…05; matriz consolidada §10 (SEC-01…07, MOD-01…08, KPI-01…04, DB-01…07, FE-01…08, SES-01…03).
- **Reglas de modalidades:** RN-MOD-01…07 (detalladas en [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]]).
- **KPIs de modalidades:** KPI-MOD-01…08 ([[DP2-MATRIZ_KPIS_MODALIDADES]]).
- **Endpoints propuestos:** §8.2 (modalidades 4, indicadores 5, búsqueda 1, exportación 1, sesiones 3, CSP 1).

### Incrementos y ruta crítica

| Inc. | Contenido | Prioridad | Tipo |
|---|---|---|---|
| INC-01 | Throttling mutantes, SCOPE_ASIGNADO, SHA-256 al descargar | P0 | Backend |
| INC-02 | Rotación/blacklist JWT, logout, `SesionUsuario` | P1 | Backend |
| INC-03 | Modalidades core (campo, historial, elegibilidad, cambio, 4 endpoints) | P0 | Backend |
| INC-04 | App `indicadores`, `/dashboard/me/`, endpoints analíticos | P0 | Backend |
| INC-05 | Búsqueda, exportación, CSP report, WebSocket opcional | P1 | Backend |
| INC-06 | `AccionesRapidas`, exportación, búsqueda en header | P1 | Frontend |
| INC-07 | V-05…V-08 completas | P1 | Frontend |
| INC-08 | Modalidades en V-03/V-04/V-08 y dashboards | P0 | Frontend |
| INC-09 | Contrato, E2E, seguridad, a11y, validación normativa, stress | P0 | Ambos |

Ruta crítica: **INC-01 → INC-03 → INC-04 → INC-08/INC-07 → INC-09** (4-5 sprints). Primer incremento recomendado: INC-01. Criterios de autorización: §13 (para modalidades exige contraste con la fuente primaria RRA-UNL y aprobación expresa de la autoridad).

## Verificación contra el código (2026-11-11)

| Afirmación | Resultado |
|---|---|
| 6 apps operativas; `resoluciones` parcial por FirmaEC | ✅ Correcto |
| Modalidades ausentes en todas las capas | ✅ Correcto (sin `opcion_titulacion`) |
| App `indicadores` y `/dashboard/me/` no existen | ✅ Correcto |
| "23 endpoints operativos verificados" (§15.H) | ❌ El código tiene **17 operaciones en 16 rutas** ([[API_CONTRACTS]]) |
| `POST /auth/token/refresh/` "(implícito)" (§8.1) | ❌ No existe la ruta |
| "Framer Motion (ya en deps)", React Hook Form + Zod (§7.3) | ❌ No están en `frontend/package.json` |
| Frontend F2.5 "80 %", V-03 "solo carrera_id" (§2.5) | ⚠️ Desactualizado: F2.5 está cerrada (FE-T1213 bloqueada por diseño) |
| Ubicación de los entregables "Raíz repo" (§14) | ❌ Están en `Documentacion-parte-2/` |
| "Suite existente 497 tests" | No reverificado (necesita entorno backend) |
| SEC-T004 implementado (`base.py:14-20`) | ✅ `JWT_SIGNING_KEY` separada |

## Contradicciones y pendientes

- No menciona GAP-STATE-01 (falta la transición `ENVIADA→EN_VERIFICACION`), detectada en esta construcción.
- La normativa de modalidades (Arts. 39, 40, 212, 216, 233) se presenta como hipótesis pendiente de validación: ver [[ARTICLES_AND_PROVISIONS]].
- Cita `MATRIZ_ESTADO_CONTROLES_SEGURIDAD.md`, que no existe.

## Relacionado

[[DP2-MATRIZ_BRECHAS]] · [[DOCUMENT_TRACEABILITY]] · [[CURRENT_STATE]] · [[BLOCKED_TASKS]]
