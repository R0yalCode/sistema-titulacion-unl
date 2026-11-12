---
system: SGT-SIAAF
type: registro
status: active
source: verificación 2026-11-12 (repositorio, GitHub e historial Git)
last_updated: 2026-11-12
---

# Registro de notificaciones DK-010 (autoría delegada)

**Requisito (DK-010, enmienda 2026-11-11, "Conocimiento de los integrantes"):** cada integrante es informado de la tarea que se le asigna y de que su identidad se usará como autor Git de ese bloque. Formato de cierre: requisito I-1 de `docs/planificacion-backend/PLAN_E1-04_O-2.md` §7. Por cada integrante se registran la fecha, el medio con constancia escrita y la respuesta.

## 1. Verificación del 2026-11-12

| Fuente revisada | Resultado |
|---|---|
| Documentación versionada (`git grep`) | Solo constan el requisito (`CLAUDE.md`, `GIT_POLICY.md`), el texto preparado de la notificación (`PLAN_E1-04_O-2.md` §7) y el pendiente de la auditoría I-3. **No hay ningún registro de envío ni de respuesta** |
| Issues de GitHub del repositorio | 0 issues en total |
| PR y comentarios que mencionan a 7777-C, JuanCalopinoo, Dan1el17 o JJOC3S (`gh search`) | 0 |
| Colaboradores del repositorio | Los cinco integrantes tienen acceso (JJOC3S, Dan1el17, R0yalCode, JuanCalopinoo, 7777-C) |
| Canales externos (chat del equipo, correo, reuniones) | **No verificables** desde el repositorio |

**Conclusión:** no hay evidencia de que se informara a ningún integrante antes de los commits con autoría delegada. No se presume que la notificación existió ni que faltó: solo se constata que no hay constancia.

## 2. Commits con autoría delegada y estado de notificación

| Integrante | Funcionalidad | Commits (autor = responsable delegado) | Notificación previa |
|---|---|---|---|
| 7777-C | E1-04 (T3) | `daa8b41` | Sin evidencia |
| 7777-C | I-3 (T3) | `9e004f0` | Sin evidencia |
| 7777-C | **V-05** (FE-T501–506) | `9308ebe`, `2986e01`, `fb9bcc5`, `e8c0234` | **Sin evidencia: INC-DK010-01** |
| JuanCalopinoo | E1-04 (T5), I-3 (T2) | `7e87483`, `082c886` | Sin evidencia |
| Dan1el17 | E1-04 (T1), I-3 (T4) | `2623685`, `86acce6` | Sin evidencia |
| JJOC3S | E1-04 (T2), I-3 (T1 y D-05/D-08) | `4d02baf`, `070ed29`, `cc5d8f8` | Sin evidencia |
| R0yalCode | todas | — | **Conocido** (responsable que autoriza) |

E1-04 e I-3 ya estaban integrados en `develop` y `main` con este pendiente abierto (auditoría I-3 y bitácoras).

## 3. Incidencia INC-DK010-01: V-05 sin notificación previa registrada

- **Hecho:** el 2026-11-12, entre las 13:37 y las 13:41 (-05:00), se crearon cuatro commits con autor `7777-C <markgonzalez20062@gmail.com>` en la rama `feat/v05-gestion-peticiones`, en la modalidad centralizada.
- **Autorización del responsable:** el reparto se aprobó ese mismo día. La opción elegida advertía de que «ese integrante debe estar informado de su asignación (DK-010)».
- **Incumplimiento:** no consta la notificación a 7777-C antes de los commits.
- **Impacto:** no afecta al código ni a las pruebas. Afecta al requisito de conocimiento de DK-010: la identidad de 7777-C figura como autor sin constancia de que lo sepa.
- **Lo que no se hace:** no se reescribe historial, no se modifican los commits, no se usa `--force` y no se cambian autores. DK-010 lo prohíbe y la regla 5 del flujo Git es absoluta.
- **Corrección:**
  1. El responsable notifica a 7777-C con constancia escrita, preferiblemente con un issue o un comentario en GitHub.
  2. Se registran en §4 la fecha, el medio y la respuesta.
  3. **Recomendación:** no integrar V-05 en `develop` hasta registrar la notificación, o integrarla dejando la incidencia abierta y documentada si el responsable lo decide.
- **Prevención:** antes de cada commit con `--author` de un integrante, comprobar en §4 que su notificación para esa funcionalidad está registrada. Si no lo está, detenerse y pedir la decisión al responsable.
- **Estado:** **abierta**.

## 4. Registro de notificaciones (lo completa el responsable)

| Integrante | Funcionalidades | Fecha | Medio y enlace | Respuesta | Registrado por |
|---|---|---|---|---|---|
| 7777-C | E1-04, I-3, V-05 | — | — | — | — |
| JuanCalopinoo | E1-04, I-3, V-06 (asignada) | — | — | — | — |
| Dan1el17 | E1-04, I-3, V-07/V-09 (asignadas) | — | — | — | — |
| JJOC3S | E1-04, I-3, V-08a (asignada) | — | — | — | — |

**Texto mínimo sugerido** (adaptado de I-1):

> En SGT-SIAAF figuras como autor Git de los commits de las tareas <IDs> (`<hashes>`) y tienes asignada <vista/bloque>. La implementación la ejecutó de forma centralizada Claude Code, con autorización del responsable (DK-010, enmienda 2026-11-11). El autor Git representa tu responsabilidad delegada sobre la tarea, no que escribieras el código. Detalle: `SIAAF-KNOWLEDGE/03-FRONTEND/PLAN_VISTAS_V05_V09.md` y este registro.

## Relacionado

[[GIT_POLICY]] · [[DECISIONS_LOG]] · [[PLAN_VISTAS_V05_V09]]
