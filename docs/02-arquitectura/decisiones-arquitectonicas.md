---
title: "Decisiones arquitectónicas"
---

# Decisiones arquitectónicas (ADRs)

## Registro real de ADRs

| ADR | Título | Ubicación | Estado verificado |
|---|---|---|---|
| 0001 | Arquitectura hexagonal — monolito modular | `backend/docs/adr/0001-…md` y `docs/adr/0001-…md` | Aceptado; implementado |
| 0002 | Stack Django 5.2 + DRF 3.16 + PostgreSQL 16 | `backend/docs/adr/0002-…md` y `docs/adr/0002-…md` | Aceptado; implementado |
| 0003 | Autenticación JWT stateless (SimpleJWT) | `backend/docs/adr/0003-…md` | Aceptado; implementado |
| 0009 | Django Admin como consola interna | `backend/docs/adr/0009-…md` | Aceptado; implementado (13 modelos, sin borrado) |
| 0010 | Perfil académico detrás de un puerto, con simulación MockSGA | `docs/adr/0010-perfil-academico-puerto-y-mocksga.md` | Aceptado para el prototipo (2026-11-22); implementado sin commit; **sin integración institucional** |
| 0004–0008 | (ViewSets, storage privado, notificaciones, spectacular, etc.) | Declarados en `specs/001/plan.md` | **Sin archivo físico** (ver hallazgo AUD-P3-05) |
| ADR-001/002 spec | Arquitectura / límites modulares | `specs/001/adr/` | **Archivos vacíos (0 bytes)** |

## Resumen de las decisiones vigentes

- **ADR-0001 — Hexagonal + monolito modular**: dominio puro, servicios transaccionales, adaptadores delgados; módulos con límites explícitos y `core` compartido. *Consecuencia*: testeable sin HTTP (dominio puro probado), costo de estructura por app.
- **ADR-0002 — Stack**: Python 3.12 (contenedor), Django 5.2.x, DRF 3.16.x, PostgreSQL 16, SimpleJWT 5.5.x, drf-spectacular, ReportLab. *Consecuencia*: ecosistema maduro, sin dependencias exóticas.
- **ADR-0003 — JWT stateless**: access 60 min, refresh 24 h, HS256, claims `cedula` y `roles`. *Consecuencia*: sin estado de sesión en servidor; contrapartida: sin rotación/blacklist (ver AUD-P2-04).
- **ADR-0010 — Perfil académico y MockSGA**: la carrera y la facultad del expediente las determina el servidor desde el perfil académico del usuario autenticado (puerto `FuenteAcademica`, catálogo interno `Carrera → Facultad`). La fuente actual es una simulación explícita (MockSGA), bloqueada fuera de desarrollo salvo permiso expreso. *Consecuencia*: sustituirla por un `SGAAdapter` no cambia el frontend, la creación ni el RBAC. Detalle: `docs/academico/perfil-academico-mock-sga.md`.
- **ADR-0009 — Admin interno**: consola de soporte, no interfaz operativa; modelos inmutables, eliminación deshabilitada, sin enlaces a archivos privados. Asociado a la Constitución v2.1 (P-18).

## Decisiones de clarificación relevantes (specs/001, DEC-01…DEC-05)

| Decisión | Contenido |
|---|---|
| DEC-01 | Notificaciones 100 % internas in-app (sin correo) |
| DEC-02 | Carga de certificados por Opción A (estudiante/secretaría según regla) |
| DEC-03 | Numeración correlativa autogenerada con posible sobreescritura manual |
| DEC-04 | Coexistencia de firma autógrafa y electrónica externa (FirmaEC simulado) |
| DEC-05 | El promedio del récord SGA es inalterable por el sistema (RN-005) |
