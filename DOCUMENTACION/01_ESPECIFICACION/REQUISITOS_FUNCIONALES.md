# Requisitos funcionales — SGT-SIAAF (backend)

**Fuente única de los requisitos:** `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §10 (RF-001 a RF-016). **Fuente del estado de implementación:** `docs/auditoria/matriz-trazabilidad.md` (verificado contra código real) y, para discrepancias detectadas en Fase 0, `DOCUMENTACION/00_AUDITORIA/`. No se redactan requisitos nuevos ni se cambia la numeración original.

Leyenda: **IV** implementado y verificado · **IP** parcial · **NI** no implementado · **BLQ** bloqueado.

| ID | Descripción (resumida) | Actor principal | Prioridad/Fase | Criterio de aceptación asociado | Estado |
|---|---|---|---|---|---|
| RF-001 | Registro e inicialización del expediente con 5 peticiones base | ESTUDIANTE | Alta / Fase 1 | CA-001 | **IV** |
| RF-002 | Recepción inmutable con timestamp y numeración de providencia | ESTUDIANTE / Backend | Alta / Fase 1 | CA-001 | **IV** |
| RF-003 | Cómputo del plazo límite de 8 días laborables | Backend | Alta / Fase 1 | CA-001 | **IV** |
| RF-004 | Petición interna de certificados sin correo | ESTUDIANTE | Alta / Fase 1 | CA-002 | **IV** |
| RF-005 | Carga y validación estricta de archivos PDF | Todos los roles autorizados | Alta / Fase 1 | CA-001, CA-004 | **IV** |
| RF-006 | Checklist digital de verificación (5 requisitos) | SECRETARIO_ABOGADO | Alta / Fase 1 | CA-003 | **IV** |
| RF-007 | Registro de observaciones accionables y bloqueo del informe | SECRETARIO_ABOGADO | Alta / Fase 1 | CA-003 | **IV** |
| RF-008 | Subsanación y reemplazo versionado de documentos | ESTUDIANTE | Alta / Fase 1 | CA-004 | **IV** |
| RF-009 | Emisión e inmutabilidad del informe legal (#590) | SECRETARIO_ABOGADO | Alta / Fase 1 | CA-005 | **IV** |
| RF-010 | Autogeneración de borradores PDF desde plantillas | Backend / ANALISTA_APOYO | Alta / Fase 1 | CA-005 | **IV** |
| RF-011 | Registro de declaratoria y memorando (#162) | DECANO | Alta / Fase 1 | CA-006 | **IV** |
| RF-012 | Notificaciones internas por rol | Backend | Alta / Fase 1 | CA-002 | **IV** |
| RF-013 | Bitácora inmutable de auditoría | Backend (signals) | Alta / Fase 1 | — | **IP** — funcional; posiblemente con 3 eventos sin emitir (no reverificado); **la IP de origen YA NO está vacía** — corregido y verificado en Fase 9 (`DOCUMENTACION/09_OBSERVABILIDAD/OBSERVABILIDAD.md` §3-4) |
| RF-014 | Programación de defensa y designación de tribunal | DIRECTOR_CARRERA | Media / Fase 2 | — | **NI** — diseño preliminar, fuera del alcance de este incremento |
| RF-015 | Registro de calificaciones y acta con firma autógrafa | SECRETARIO_ABOGADO / Tribunal | Media / Fase 2 | CA-007 | **NI** — diseño preliminar, fuera del alcance de este incremento |
| RF-016 | Consolidación del expediente y registro SENESCYT | SECRETARIA_GENERAL / Backend | Baja / Fase 3 | — | **NI** — diseño preliminar, fuera del alcance de este incremento |

## Notas de verificación

- RF-001 a RF-012 corresponden íntegramente al MVP de Fase 1 y están respaldados por módulo, modelo, endpoint y prueba específicos en `docs/auditoria/matriz-trazabilidad.md` (backend). Ese documento data de antes del cierre de las últimas vistas de frontend, pero el estado de los RF del **backend** no se ve afectado por ese desfase (H-02 en `00_AUDITORIA/`).
- RF-013 se marca **IP**, no IV, porque la fuente de trazabilidad explícitamente documenta 3 eventos de auditoría sin emitir y el campo de IP de origen siempre vacío; esto no se reverificó contra el código en esta Fase 1 (queda pendiente para la Fase 4/6).
- Los requisitos sin implementación declarada que el backend define en su enum pero sin flujo operativo (estado `LEGALIZADO` de petición, estado `CANCELADA` de expediente, CRUD de catálogo de requisitos) se listan aparte en `docs/auditoria/matriz-trazabilidad.md` y se citan aquí por referencia, sin asignárseles un ID RF propio porque no lo tienen en `specify.md`.

## Requisitos funcionales del frontend (RFF)

Los requisitos funcionales del frontend están en `sgt-siaaf/specs/003-frontend-titulacion/specify.md` §7 (globales) y §9 (por vista, RFF-101…RFF-9xx). No se consolidan en detalle en este documento porque el incremento evaluado es el backend; se referencian en `MATRIZ_TRAZABILIDAD.md` con su estado según `CLAUDE.md` (fuente más reciente: V-01 a V-04 cerradas, V-05+ sin iniciar).
