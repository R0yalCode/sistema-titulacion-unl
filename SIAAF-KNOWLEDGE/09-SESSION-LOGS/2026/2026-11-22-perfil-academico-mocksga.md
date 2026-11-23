---
system: SGT-SIAAF
type: session-log
date: 2026-11-22
agent: claude-code
branch: feat/dashboard-estudiante (sin commit, sin push ni merge)
commits: []
---

# Sesión 2026-11-22: V-03 sin UUID de carrera, perfil académico y MockSGA

## Alcance autorizado

Lo pidió expresamente el responsable: implementar una integración académica **simulada** (MockSGA), el endpoint `GET /api/v1/perfil-academico/`, la creación segura del expediente y una V-03 sin UUID. Incluye backend, migración y `openapi.yaml`. Quedan excluidos los commits, el push, el merge y los cambios de rama. No se añadieron dependencias.

## Qué se hizo

- Nueva app `apps/academico`:
  - Dominio, puerto `FuenteAcademica`, `AcademicProfileService` y `MockSGAAdapter`.
  - Modelos `Facultad`, `Carrera`, `PerfilSGASimulado` y `EventoCatalogoAcademico` (migración `academico/0001`).
  - Admin auditado y comando `seed_mock_sga`.
- `POST /api/v1/expedientes/`:
  - Cuerpo vacío. La carrera sale del perfil validado y la facultad, de la carrera.
  - Responde 400 `campo_no_permitido`, 422 si el perfil no está validado y 503 si no hay fuente.
  - Bloquea la fila del estudiante para evitar duplicados concurrentes.
- La señal `EXPEDIENTE_CREADO` existente ahora incluye carrera, facultad y fuente.
- V-03 se reescribió:
  - Perfil de solo lectura, aviso de datos simulados y estados de carga, bloqueo, expediente activo y error 503 con reintento.
  - Sin campo UUID ni borrador.
- Documentación:
  - `docs/academico/perfil-academico-mock-sga.md` y `docs/adr/0010-…`.
  - DEC-17 e INC-22 en `sgt-siaaf/specs/003-frontend-titulacion/clarify.md`.
  - C-V03-01…04 en `13-TRACEABILITY/DOCUMENT_TRACEABILITY.md` y BE-01/BE-10 en `05-EXECUTION/BLOCKED_TASKS.md`.

## Pruebas (resultados reales)

- **Backend con SQLite** (`pytest`, contenedor desechable): 846 pasaron.
  - La línea base antes del cambio era 777 pasadas y 1 fallo de entorno (`MFA_ENCRYPTION_KEYS` sin definir), que no es una regresión.
- **Backend con PostgreSQL 16.15 desechable** (`pytest tests`): 39 pasaron, incluida la nueva `test_crear_expediente_concurrencia_postgres.py`.
- **Frontend**:
  - `lint`, `typecheck` y `build` en verde.
  - `vitest`: 539/539 en la segunda ejecución completa. En la primera, `MfaFlow.test.tsx` falló una vez; pasa aislado y en la repetición. Es la intermitencia ya conocida y no la causó este cambio.
- `manage.py spectacular --validate`: 0 errores. Las 2 advertencias ya existían.

## Entorno de desarrollo

- Se guardaron como respaldo las imágenes `sgt-siaaf-backend:pre-perfil-academico` y `sgt-siaaf-nginx:pre-perfil-academico`.
- Se reconstruyeron solo `backend` y `nginx`. El servicio `db` y los volúmenes no se tocaron.
- Se aplicó `migrate academico`, que solo crea tablas nuevas.
- `seed_mock_sga --asignar-ambito-personal`:
  - Creó el catálogo MOCK (1 facultad y 2 carreras) y el perfil de `estudiante_1`.
  - Asignó ámbito a 5 cuentas demo del personal que no tenían ninguno.
  - La segunda ejecución confirmó que es idempotente.
- Evidencia de solo lectura con `estudiante_1`:
  - `GET /api/v1/perfil-academico/` devuelve 200 `VALIDADO`.
  - Un `POST` con `carrera_id` devuelve 400 `campo_no_permitido`.
  - La secretaría recibe 403.
- No se creó ningún expediente.

## Pendientes y decisiones del responsable

- Restricción única en la base de datos (un expediente activo por estudiante): haría fallar unas 85 pruebas de otros módulos.
- Actualizar HU-001 en la spec 001 (C-V03-01).
- Catálogo oficial de la UNL e integración real con el SGA.
- La página `/estudiante/perfil` sigue sin mostrar la carrera (su comentario cita BE-10).
- Las pruebas de otros módulos solo cambiaron `crear_expediente.execute(est, CARRERA)` por `registrar_expediente(...)`. También `test_mi_tramite.py` (sin commit, del dashboard) y `test_audit_ip.py`.
