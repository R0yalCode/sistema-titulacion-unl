# Reparto DK-010: Design System, portal del estudiante y panel del administrador

> **Estado: aprobado por R0yalCode e integrado por bloques el 2026-11-22.**
> La ejecución material fue centralizada mediante Claude Code. El autor Git identifica al integrante responsable de la tarea asignada, no a quien escribió el código. Nunca se afirma que un integrante lo desarrolló personalmente.
> Committer de todos los bloques: R0yalCode.
> Línea de cada commit: `Modalidad: implementación centralizada (DK-010, enmienda 2026-11-11) · Tarea <ID> · responsable <Identificador>`.

Detalle de validación y desviaciones: [[2026-11-22-integracion-rediseno-admin]].

## Correspondencia tarea ↔ responsable ↔ commit ↔ archivos

| Orden | Tarea | Responsable | Commit | Archivos | Alcance |
|---:|---|---|---|---:|---|
| 1 | BE-PA | R0yalCode | `31ad3b2` | 56 | App `academico`, `GET /perfil-academico/`, creación segura del expediente, errores 422/503, OpenAPI y pruebas |
| 2 | EST-1 | R0yalCode | `c436b29` | 6 | `GET /expedientes/mi-tramite/`, celda RBAC propia del estudiante y pruebas |
| 3 | BE-PA docs | R0yalCode | `8e3935f` | 7 | Guía, ADR-0010, decisiones, trazabilidad y bitácora |
| 4 | FIX-NOTIF | R0yalCode | `1310e00` | 3 | Ámbito de notificaciones por expediente, pruebas y bitácora |
| 5 | DS-A | JJOC3S | `d1cd9d2` | 16 | Tokens, estilos globales, Inter y `DESIGN_SYSTEM.md` |
| 6 | DS-B | Dan1el17 | `7307c69` | 48 | `components/ui`, `feedback`, `lib/estados.ts`, `test/confirmar.ts` |
| 7 | DS-E | JuanCalopinoo | `6a37b96` | 13 | `features/auth/**` |
| 8 | EST-2 | R0yalCode | `83cdaef` | 23 | `features/dashboard/*`, `miTramite.ts`, `lib/dates.ts`, `mocks/*`, `peticiones/index.ts` |
| 9 | DS-C | 7777-C | `610bb4b` | 19 | `components/layout/*`, rutas, roles y `features/cuenta/*` |
| 10 | DS-D | R0yalCode | `227975c` | 48 | Bandeja, expediente, peticiones, solicitud, no habilitado, `expedientes.ts`, `perfilAcademico.ts`, `lib/storage.ts` |
| 11 | ADM-1 | Dan1el17 | `121f44f` | 1 | `styles/siaaf-modern.css` |
| 12 | ADM-2 | JJOC3S | `dfab27c` | 5 | Búsqueda Ctrl/Cmd + K, enlaces de consola y barrel de bandeja |
| 13 | ADM-3 | JuanCalopinoo | `4f78caf` | 3 | Capa de administrador en `AppShell` y `AppLayout` |
| 14 | ADM-4 | 7777-C | `97fb720` | 5 | `AdminDashboard`, `KpiCard`, `BandejaPage`, `PanelesInicio` |
| 15 | ADM-5 | R0yalCode | commit que contiene este documento | 6 | Prueba del panel, documentación, incidencias y registro |

`1310e00` se incorporó con el merge `8fa133a`, sin alterar su contenido ni su autoría.

## Dependencias y orden

`BE-PA → EST-1 → FIX-NOTIF → DS-A → DS-B → DS-E → EST-2 → DS-C → DS-D → ADM-1 → ADM-2 → ADM-3 → ADM-4 → ADM-5`.

DS-E y EST-2 conservan fallos intermedios documentados en sus mensajes de commit:

- DS-E: 7 pruebas de login y MFA esperan el dashboard de EST-2.
- EST-2: 5 pruebas del router y 1 de cierre de sesión esperan DS-C.

Esos commits siguen en el historial después de `merge --no-ff` y `git bisect` puede detenerse en ellos. El conjunto integrado pasa todas las pruebas.

## Ajustes respecto del reparto inicial

- `peticiones/index.ts` pasó de DS-D a EST-2, porque el portal del estudiante lo importa.
- `expedientes.ts`, `perfilAcademico.ts` y `lib/storage.ts` se asignaron a DS-D, junto con V-03.
- `LandingPage.module.css` salió de DS-E: la landing local tiene cambios en su `.tsx` y en su prueba que no pertenecen a un bloque aprobado.
- Este documento se versiona en ADM-5 para no publicar un estado de propuesta ya superado.
- `KpiCard`, `AppShell`, `AppLayout`, `BandejaPage` y `PanelesInicio` tienen dos capas: la base en DS-B, DS-C o DS-D y la capa del administrador en ADM-3 o ADM-4.

## Fuera de esta integración

`settings/production.py`, `apps/entorno_pruebas`, la landing local, `backend/entrypoint.sh`, `README.md`, `.obsidian`, `DOCUMENTACION/`, `.github/dependabot.yml`, `.claude/launch.json`, `docs/paleta_colores_institucionales/`, la referencia visual del login, `DISENO_FUNCIONAL_MODALIDADES_TITULACION.md` y el borrado local de `docs/ENTORNO_DESARROLLO.md`.
