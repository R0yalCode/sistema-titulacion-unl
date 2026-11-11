---
system: SGT-SIAAF
type: workflow
status: active
source: user-directive 2026-11-11 + repository-history
last_updated: 2026-11-11
---

# Versionado: SemVer + COSMOS

## SemVer

`MAJOR.MINOR.PATCH`: MAJOR = cambios incompatibles; MINOR = funcionalidad nueva compatible; PATCH = correcciones compatibles. **No se incrementa por commit**, sino por **entrega real, integrada y validada**.

## COSMOS (versionado astronómico)

Formato de entrega: **`COSMOS vX.Y.Z — Descripción de la entrega`**, donde `COSMOS` es el nombre del hito.

Catálogo autorizado (no inventar nombres ni reasignarlos): ORION · POLARIS · SATURN · SIRIUS · MERCURY · PULSAR · ROSETTA · ANDROMEDA · VEGA · QUASAR · EUROPA · ORBIT · NOVA · ECLIPSE · HELIOS · TRAPPIST · SUPERNOVA.

> La **responsabilidad temática** de cada nombre no está documentada en el repositorio. Solo se observan sus usos históricos (abajo). **Pendiente:** que el equipo documente el significado asignado a cada hito antes de reutilizarlo.

## Hitos observados en el historial Git

| Hito | Versión | Evidencia | Contenido |
|---|---|---|---|
| ANDROMEDA | v0.2.0 | Rama `release/0.2.0-andromeda` (merges `b6b953a`, `f692143`) | Frontend F0–F2.5 y V-01 (`feat(frontend): integrar F0–F2.5 y V-01`) |
| ANDROMEDA | v0.3.0 | `f279090 release(andromeda): integrar V-04 — expedientes y requisitos (v0.3.0)`, PR #14 | V-04 |
| ECLIPSE | v0.4.0 | `8e1e1a2 feat(security)…`, rama `release/0.4.0-eclipse`, PR #16 | **ECLIPSE v0.4.0 — Implementación de seguridad del backend SGT-SIAAF** |
| ROSETTA | — (sin versión) | `bf74d4d docs(rosetta): incorporar documentación maestra…`, PR #20 | Documentación DP2 (ámbito de commit, no release) |

Ninguno de estos hitos tiene **tag** Git ni release en GitHub (verificado con `git tag -l` y `git ls-remote --tags`).

## Reglas

1. Tag y release **solo** para una entrega funcional integrada y validada.
2. **No** reutilizar `ECLIPSE v0.4.0` ni ningún identificador ya usado.
3. La documentación (como esta bóveda) **no** genera versión COSMOS por sí sola (DK-005). Puede usar un nombre de hito como **ámbito** de commit si el equipo lo decide, sin versión.
4. Propuesta: la siguiente entrega funcional sería **v0.5.0** (MINOR), con un hito del catálogo **elegido por el equipo**.

## Relacionado

[[GIT_POLICY]] · [[DECISIONS_LOG]]
