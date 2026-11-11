---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/MATRIZ_BRECHAS_BACKEND_FRONTEND.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/MATRIZ_BRECHAS_BACKEND_FRONTEND.md
source_version: "1.0"
source_date: 2026-11-09
nature: gap-matrix
vigencia: vigente-con-observaciones
last_verified: 2026-11-11
---

# DP2 · Matriz de brechas backend-frontend

**Original:** [[MATRIZ_BRECHAS_BACKEND_FRONTEND]] · Consolida el [[DP2-PLAN_MAESTRO]] §10.

## Estructura

Leyenda: **CV** completado y verificado · **IP** implementado parcialmente · **PI** pendiente de implementación · **BL** bloqueado · **NA** no aplica · **NV** no verificable.

Familias de filas: SEC-01…11, MOD-01…13, KPI-01…05, DB-01…07, FE-01…10, SES-01…04, API-01…07, TEST-01…07 (P0…P3, con su incremento).

## Puntos clave que conserva

- SEC-08…11 (RS256, RFC 3161, tests de mass assignment/BOLA, historial de modelos maestros) → "Futuro".
- MOD-03 (TIC: 100 % de asignaturas **o** 85 % de horas) y MOD-04 (EC: 2 reprobaciones + 3.ª matrícula) → hipótesis normativas.
- KPI-05: 7 KPIs no implementables (tutoría, sustentación, períodos, carreras, abandonados, usuarios activos reales, modalidad). **No deben simularse** (CA-G-01).
- API-07: contrato OpenAPI contrastado con el código el 2026-11-05 (INC-13, 19, 20, 21).

## Verificación contra el código

| Fila | Afirmación | Resultado |
|---|---|---|
| SEC-02 | "validación manual solo en descarga" | ✅ Coincide ([[PERMISSIONS_ROLES]]) |
| SEC-06 | RESPONSABLE_DEPENDENCIA sin celdas | ✅ Coincide |
| DB-02…07 | Backend "CV (endpoints)" para dashboards por rol | ⚠️ Solo existen bandeja y notificaciones; no hay endpoints de dashboard ni KPI |
| FE-10 | Microinteracciones "CV (libs) Framer Motion" | ❌ Framer Motion no está instalado |
| TEST-03 | Frontend "170+ UI Kit + 81 Auth + 24" | Desactualizado: hoy hay 328 pruebas frontend |
| Observación 5 | "23 endpoints operativos" | ❌ Son 17 operaciones |
| Resumen estadístico | 97 elementos (60 backend + 37 frontend) | ⚠️ No cuadra con las filas de la matriz; los totales parecen calculados aparte |

## Relacionado

[[GENERAL_TRACEABILITY_MATRIX]] · [[DOCUMENT_TRACEABILITY]]
