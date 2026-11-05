# 08 — RECOMENDACIONES DE MEJORA

Propuestas concretas, justificadas y priorizadas. **No se implementó nada** (auditoría): son acciones sugeridas al equipo.

## Prioridad 1 — Estabilizar (bloquea nuevas tareas SDD)

### R1. Unificar almacenamiento privado y arreglar el PKG PDF (solve 74 tests)
- **Justificación:** causa raiz única de la regresión (50 FAILED + 24 ERROR) — `pdf_generator.py:48` (path absoluto `/media/private/resoluciones`) + `PRIVATE_MEDIA_ROOT` ausente en settings.
- **Acción:** (1) `PDFGeneratorAdapter` recibe rutas de `PrivateMediaStorage`/`MEDIA_ROOT`; (2) definir `PRIVATE_MEDIA_ROOT` en `settings/base.py`; (3) tests parametrizados con `tmp_path` (ya existen fixtures `temp_output_dir` — conectarlas con inyección).

### R2. Persistir el memorando N° 162 (SEC-01/D-02)
- **Acción:** en `declarar_aptitud.py` reemplazar el path nominal por `guardar_archivo_privado(archivo_memorando, expediente.id, "memorando_162.pdf")`; añadir test `ArchivoExiste` tras registrar.

### R3. Habilitar `GET /expedientes/{id}/checklist/` con celda RBAC (SEC-03)
- **Acción:** añadir celda `"GET"` al recurso `checklist` en `RBAC_MATRIX` (ESTUDIANTE own; SECRETARIA/DEFAULT asignado; SECRETARIO/ANALISTA facultad; ADMIN allow) + test de integración por rol.

### R4. Volver a verde la suite y hacerla exigible
- **Acción:** pytest con `--cov=src --cov-fail-under=70`; unir en `testpaths` `src/apps`, `src/core/tests`, `backend/tests/e2e`; después de R1-R3. Meta mesurable: **494 tests** todos pasando.

## Prioridad 2 — Fiabilidad de despliegue

### R5. Configuración de "producción" real
- gunicorn en requirements + `CMD gunicorn config.wsgi`; settings.prod (o `env DEBUG=0` + settings base) en compose; collectstatic en build/run; nginx: TLS, `limit_req`, servido `/static/`, confinado a `/api/v1/`; healthcheck del backend + endpoint `/api/v1/health/` (RNF-006).

### R6. Copiar `pyproject.toml` y `tests/` al artefacto Docker (D-18)
- Habilita `docker compose run backend pytest` — QA reproducible en contenedor.

### R7. Git + CI (D-06)
- `git init` + remository remota; GitHub Actions: lint (flake8/black/isort/mypy), pytest+coverage con umbral, gitleaks/bandit/safety (formalisierung de lo ya manual en security_report.md). El PR template ya existe y exige trazabilidad.

## Prioridad 3 — Seguridad y trazabilidad

### R8. Endurecer JWT (SEC-05/SEC-08)
- Throttling en `auth/token/`; `ROTATE_REFRESH_TOKENS=True` + blacklist app; separar `JWT_SIGNING_KEY` de `SECRET_KEY`.

### R9. Registro de auditoría completo (SEC-09, D-09)
- Middleware obtiene IP (Crequest o `X-Forwarded-For` con nginx confiados); corregir snapshot `estado_anterior` en `emitir_informe` antes del cambio de estado; emitir eventos `SUBSANACION_REALIZADA`.

### R10. Evitar leak de OSD info (SEC-06/07)
- Eliminar `print()` debug (usar logger); quitar `archivo_path` de serializadores públicos.

### R11. Actualizar DRF ≥3.17.2 (security_report) y convertir el security_report en artefacto recurrente del CI (no one-shot).

## Prioridad 4 — Integridad arquitectónica y metodológica

### R12. Consolidar ADRs (D-11): `docs/adr/` como única localidad (RNF-018); redactar los 5 ADRs faltantes (0004..0008) o corregir plan.md para listar solo los existentes; unificar los duplicados divergentes 0001/0002.
### R13. Limpieza de repo (D-12): eliminar `gitleaks.exe`, `commit_msg.txt`, `backend/contracts/openapi.yaml` (duplicado); mover retrospectivos scripts a `scripts/` con rutas relativas; redactar `backend/README.md` real (el actual es el README upstream de gitleaks).
### R14. Fuente única de autorización (D-10): helper `has_any_role()` en `authentication`; `declarar_aptitud` delations alineado a matrix (`declare tableau decano+analista borrador` decide el producto deseado y reflejarlo en ambos lados).
### R15. Notificaciones vía `notification_service` única (D-15/D-16): sustituir `NotificacionInterna.objects.create` en 5 servicios y extraer el helper duplicado; así se Pacifica el patrón señales auditaría/notificación.
### R16. Gobernanza SDD (CD-01..CD-05): (a) revisar/ aprobar la Constitución y decidir si el esquema es P-XX o C-XXX (repeer su mano: normalizar plan/specify/tasks); (b) actualizar specify RN-002 con la pausa del plazo; (c) marcar tareas `[x]` real	Set de 46; (d) definir (o descartar) estados huérfanos `CANCELADA`/`LEGALIZADO` y el rol `RESPONSABLE_DEPENDENCIA` (bandeja) antes de construirlos; (e) completar las plantillas del Spec Kit.
### R17. Corregir README (D-08): métricas reales (494 tests, 88% cobertura; actualizar tras R4).

## Prioridad 5 — Preparación Fase 2 (frontend)

### R18. Habilitar CORS + global DRF pagination (bandeja y notificaciones); decidir `RESPONSABLE_DEPENDENCIA` scopes; definir schema de eventos baja latencia si se quiere realtime (polling suficiente para MVP).
### R19. Añadir pruebas de concurrencia con PostgreSQL real (P-14): hoy tests corren sobre SQLite; configurar `settings.test` con postgres via docker test-db para rollback/select_for_update reales.

## Decide-composer: resumen de impacto estimado

| Sprint | Recomendaciones | Resultado esperado |
|---|---|---|
| S1 (estabilización) | R1-R4 | Suite 494/494 green, RF completo Actividad! tutorial para/operativa |
| S2 (deli@deploy) | R5-R7 | Despliegue reproducible, CI asegurando no-regresión |
| S3 (hardening) | R8-R11 | Seguridad de nivel producción |
| S4 (acción metodológica) | R12-R17 | Gobernanza SDD coherente y trazable |
| S5+ (Fase 2) | R18-R19 | Preparación del frontend con backend instalado |
