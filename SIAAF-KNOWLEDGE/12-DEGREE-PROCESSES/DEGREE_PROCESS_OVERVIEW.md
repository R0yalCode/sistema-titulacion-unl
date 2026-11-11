---
system: SGT-SIAAF
type: process
status: verified
source: specify-001 + verified-code
last_verified: 2026-11-11
---

# Proceso de titulación — visión general

## Fases (specify 001 §2.3)

| Fase | Subproceso | Norma | Estado en el sistema |
|---|---|---|---|
| **1 — MVP** | Declaratoria de aptitud legal | Art. 235 | **Implementado** (con brechas, ver abajo) |
| 2 | Sustentación y defensa: tribunal de 3 docentes, memoria digital, calificaciones 0–10, borrador del acta con firma autógrafa | Arts. 236–237 | Diseño preliminar; no implementado |
| 3 | Cierre: acta consolidada, autorización del Rector, registro SENESCYT | Arts. 243–244 | Diseño preliminar; no implementado |
| Transversal | Modalidades (TIC / EC) | Arts. 39, 40, 212, 216, 233 (hipótesis) | Propuesta (BE-06) |

## Flujo Fase 1 (FL-01…FL-05, specify 001 §8)

1. **FL-01 Creación** — el estudiante crea el expediente (`BORRADOR`) y se generan las 5 peticiones base → [[STUDENT_RECORDS]].
2. **FL-02 Petición interna** — solicita a cada dependencia la emisión del certificado, sin correo → [[REQUESTS_AND_APPLICATIONS]].
3. Envío — con los 5 documentos vigentes, `ENVIADA` (fecha y hora UTC inmutables, providencia, plazo de 8 días laborables).
4. **FL-03 Verificación** — el Secretario/a-Abogado/a evalúa el checklist (`EN_VERIFICACION`) y emite el informe #590 (`INFORME_EMITIDO`). ⚠️ No hay endpoint para `ENVIADA→EN_VERIFICACION` (GAP-STATE-01).
5. **FL-04 Observación y subsanación** — `OBSERVADA` ↔ `EN_VERIFICACION`, con versionado N+1 y pausa del plazo.
6. **FL-05 Declaratoria** — el Decano/a carga el memorando #162 firmado externamente (`DECLARADA_APTA`) → [[DOCUMENT_MANAGEMENT]], [[ELECTRONIC_SIGNATURES]].

Detalle técnico: [[BACKEND_ARCHITECTURE#Máquina de estados]]. Diagrama BPMN: `DOCUMENTACION/02_PROCESOS/diagramas/proceso_principal.bpmn` (= `docs/10-auditoria-2026-11/assets/proceso_principal.bpmn`).

## Notas por subproceso

[[STUDENT_RECORDS]] · [[REQUESTS_AND_APPLICATIONS]] · [[DOCUMENT_MANAGEMENT]] · [[ELECTRONIC_SIGNATURES]] · [[TUTORS_AND_COMMITTEES]] · [[DEFENSES_AND_GRADES]] · [[CURRICULAR_INTEGRATION_WORK]] · [[COMPREHENSIVE_EXAMINATION]] · Notificaciones: [[02-BACKEND/MODULES|módulo notificaciones]]
