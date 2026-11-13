---
title: "Mantenimiento"
---

# Mantenimiento

## Rutinas recomendadas

| Tarea | Frecuencia | Comando / acción |
|---|---|---|
| Migraciones pendientes | Cada despliegue | `python manage.py migrate` |
| Verificación de modelo | Pre-merge | `python manage.py makemigrations --check --dry-run` |
| Suite de pruebas | Pre-merge | `pytest -q` + suite extendida (ver calidad) |
| Lint backend | Pre-merge | `flake8 src` |
| Lint/typecheck/test/build frontend | Pre-merge | `npm run lint && npm run typecheck && npm run test && npm run build` |
| Regeneración del contrato OpenAPI | Al cambiar la API | `manage.py spectacular --validate --file openapi.yaml` + revisión del diff con `git diff backend/openapi.yaml` |
| Backup de PostgreSQL | Diario (pendiente de automatizar) | `pg_dump` — **sin procedimiento documentado aún** |
| Backup de `media_data` | Diario (pendiente) | Copia del volumen de PDFs privados |
| Rotación de logs | Pendiente | Requiere configurar `LOGGING` |

## Tareas operativas con Django Admin (ADR-0009)

- Consulta de expedientes, peticiones, verificaciones, resoluciones, notificaciones y auditoría (13 modelos, read-only, sin borrado).
- Gestión de usuarios y roles (sin eliminación).

## Deuda técnica vigilada

Lista priorizada en [`auditoria/PLAN_MEJORA_TECNICA.md`](../auditoria/PLAN_MEJORA_TECNICA.md). Ítems con vigilancia especial: bug N-1 del historial, prints de depuración, código muerto (`PeticionDocumentalViewSet`, `ObservacionViewSet`), eventos de auditoría no emitidos.
