---
system: SGT-SIAAF
type: session-log
date: 2026-11-12
agent: claude-code
branch: fix/i3-archivos-huerfanos
commits: [647c258, 070ed29, 082c886, 9e004f0, 86acce6]
---

# Sesión 2026-11-12 — I-3: archivos huérfanos en carga, subsanación y declaratoria

## Modalidad (DK-010, enmienda 2026-11-11)

Implementación **centralizada**: el código lo ejecutó materialmente Claude Code, con autorización expresa del responsable (R0yalCode, 2026-11-12). El autor Git de cada commit identifica al integrante responsable de la tarea (responsabilidad delegada), **no** a quien escribió el código. Committer: R0yalCode.

| Tarea | Responsable | Commit |
|---|---|---|
| Informe I-3 (documental) | R0yalCode | `647c258` |
| T1 almacenamiento atómico y compensación | JJOC3S | `070ed29` |
| T2 carga | JuanCalopinoo | `082c886` |
| T3 subsanación | 7777-C | `9e004f0` |
| T4 declaratoria | Dan1el17 | `86acce6` |
| T5 conciliación, PostgreSQL y cierre | R0yalCode | el commit que incorpora esta bitácora |

## Preparación Git

`main` local y `develop` avanzados por avance rápido a `3317231`; `develop` publicado (`728f725..3317231`); rama `fix/i3-archivos-huerfanos` creada desde `develop` en el árbol principal (cambio de rama verificado sin efecto sobre los cambios locales del usuario). `integracion/develop-en-main` conservada.

## Evidencia

- Cada prueba nueva se ejecutó primero contra la línea base (en rojo) y después contra la corrección (en verde); detalle en `docs/auditorias/INFORME_I3_ARCHIVOS_HUERFANOS.md` §10.
- Fallo real de *commit* en PostgreSQL 16.15 (contenedor desechable): huérfanos en `3317231`, ninguno en la rama.
- `reconciliar_archivos` demostrado de extremo a extremo en PostgreSQL real con un `MEDIA_ROOT` temporal.
- Regresión: SQLite 625 aprobadas + 13 `pypdf`; `src/core` 103/103; `tests/` 24 + 12 omitidas; PostgreSQL integración 12/12, `tests/` 36/36, `src/apps` con los 21 fallos conocidos; OpenAPI sin errores ni diferencias.

## Pendientes

- Revisión y autorización de la integración de la rama en `develop` y `main`.
- H-I3-05 (cargas repetidas) y H-I3-07 (registro sin archivo): fuera de alcance / riesgo residual.
- Notificación a los integrantes de su atribución delegada en E1-04 y en I-3 (DK-010): sin evidencia registrada.
