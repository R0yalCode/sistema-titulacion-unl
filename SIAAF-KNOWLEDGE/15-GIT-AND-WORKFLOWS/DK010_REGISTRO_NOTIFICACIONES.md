---
system: SGT-SIAAF
type: registro
status: active
source: verificación 2026-11-12 (repositorio, GitHub, historial Git) + enmienda de DK-010 del 2026-11-12
last_updated: 2026-11-12
---

# Registro de atribución DK-010 (antiguo registro de notificaciones)

## 0. Regla vigente: atribución por asignación (enmienda de DK-010, 2026-11-12)

Por **decisión expresa de R0yalCode del 2026-11-12**, la asignación expresa de una tarea a un integrante es **autorización suficiente** para atribuirle, como autor Git, los commits de esa tarea.

**No se requiere:**
- notificación individual;
- confirmación de recepción;
- respuesta o aceptación del integrante;
- evidencia de comunicación.

| Elemento | Responsable |
|---|---|
| Asignación de la tarea | R0yalCode |
| Ejecución material del código | Claude Code |
| Autor Git (`Author`) | Integrante asignado (identidad exacta de la tabla de integrantes) |
| Committer Git (`Committer`) | R0yalCode |
| Revisión y autorización de integración | R0yalCode |

**Condiciones que se mantienen:**
- Cada commit corresponde solo a la tarea asignada y a su responsable.
- La trazabilidad commit ↔ rama ↔ tarea ↔ responsable queda en el plan, la bitácora y la línea `Modalidad:` del commit.
- Prohibidas las atribuciones inventadas y las asignaciones ambiguas: ante la duda, se pregunta.
- La autoría Git delegada **no** significa que el integrante escribiera el código.
- Siguen prohibidos reescribir historial publicado y `--force`.

Definición: [[DECISIONS_LOG]] (DK-010) · `CLAUDE.md` § Equipo, autoría y distribución del trabajo · [[GIT_POLICY]] § Modalidad de implementación centralizada.

## 1. Verificación histórica del 2026-11-12, previa a la enmienda

Se hizo cuando la política exigía que cada integrante fuera **informado** (enmienda del 2026-11-11, «Conocimiento de los integrantes», y requisito I-1 de `docs/planificacion-backend/PLAN_E1-04_O-2.md` §7). Se conserva como registro histórico.

| Fuente revisada | Resultado |
|---|---|
| Documentación versionada (`git grep`) | Solo constaban el requisito y el texto preparado de la notificación; ningún registro de envío ni de respuesta |
| Issues de GitHub | 0 |
| PR y comentarios que mencionan a 7777-C, JuanCalopinoo, Dan1el17 o JJOC3S | 0 |
| Colaboradores del repositorio | Los cinco integrantes |
| Canales externos | No verificables desde el repositorio |

**Resultado:** no hubo constancia de notificaciones a los integrantes. **No se afirma que existieran.** Desde la enmienda del 2026-11-12 tampoco se exigen.

## 2. Commits con autoría delegada y su asignación

| Integrante | Funcionalidad | Commits | Fecha | Asignación del responsable | Notificación |
|---|---|---|---|---|---|
| 7777-C | E1-04 (T3) | `daa8b41` | 2026-11-11 | Reparto aprobado el 2026-11-11 | No constaba; no exigida |
| 7777-C | I-3 (T3) | `9e004f0` | 2026-11-12 | Reparto aprobado el 2026-11-12 | No constaba; no exigida |
| 7777-C | V-05 (FE-T501–506) | `9308ebe`, `2986e01`, `fb9bcc5`, `e8c0234` | 2026-11-12, 13:37–13:41 (-05:00) | Reparto aprobado el 2026-11-12 ([[PLAN_VISTAS_V05_V09]] §5) | No constaba; no exigida |
| JuanCalopinoo | E1-04 (T5), I-3 (T2) | `7e87483`, `082c886` | 2026-11-11, 2026-11-12 | Repartos aprobados | No constaba; no exigida |
| Dan1el17 | E1-04 (T1), I-3 (T4) | `2623685`, `86acce6` | 2026-11-11, 2026-11-12 | Repartos aprobados | No constaba; no exigida |
| JJOC3S | E1-04 (T2), I-3 (T1, D-05/D-08) | `4d02baf`, `070ed29`, `cc5d8f8` | 2026-11-11, 2026-11-12 | Repartos aprobados | No constaba; no exigida |

Ningún commit se ha modificado: autores y committers son los originales.

## 3. INC-DK010-01: resuelta mediante aclaración de política

- **Hecho histórico:** el 2026-11-12, entre las 13:37 y las 13:41 (-05:00), se crearon en `feat/v05-gestion-peticiones` los commits `9308ebe`, `2986e01`, `fb9bcc5` y `e8c0234` con autor `7777-C <markgonzalez20062@gmail.com>` y committer R0yalCode, en la modalidad centralizada. Su tarea, V-05, estaba asignada a 7777-C por el reparto que el responsable aprobó ese mismo día. No constaba ninguna notificación previa al integrante.
- **Clasificación original** (commit `2a5577c`, 2026-11-12): incumplimiento del requisito de «conocimiento de los integrantes» que figuraba entonces en DK-010.
- **Causa:** ese requisito no formaba parte del procedimiento de trabajo que el responsable quería aplicar.
- **Resolución:** R0yalCode aclaró y corrigió la política el 2026-11-12 (enmienda de DK-010): la asignación directa de la tarea es autorización suficiente para la atribución Git.
- **Reclasificación:** **incidencia documental resuelta mediante aclaración de política**. Según el procedimiento vigente, la falta de notificaciones no es un incumplimiento. La discrepancia con la política anterior queda registrada y no se oculta.
- **Sin cambios en Git:** sin reescribir historial, sin `--amend`, sin rebase, sin `--force` y sin cambios de autor o committer.
- **Estado:** **resuelta** (2026-11-12).

La misma aclaración cierra el pendiente equivalente sobre E1-04 e I-3 (requisito I-1 del plan E1-04, auditoría I-3 y `CURRENT_STATE`).

## 4. Control previo a cada commit con autoría delegada

Antes de usar `--author` de un integrante se comprueba que:
1. La tarea figura como **asignada por R0yalCode** a ese integrante en el plan de la funcionalidad aprobado.
2. Los archivos del commit pertenecen solo a esa tarea.
3. La identidad es la exacta de la tabla de integrantes.
4. El cuerpo lleva la línea `Modalidad: implementación centralizada (DK-010, …) · Tarea <ID> · responsable <Identificador>`.

Si falta alguna de estas condiciones o la asignación es ambigua, se detiene y se pregunta al responsable.

## Relacionado

[[GIT_POLICY]] · [[DECISIONS_LOG]] · [[PLAN_VISTAS_V05_V09]]
