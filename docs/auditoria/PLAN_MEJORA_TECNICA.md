---
title: "Plan de mejora técnica"
---

# PLAN DE MEJORA TÉCNICA — SGT-SIAAF

| Campo | Valor |
|---|---|
| Fecha | 05-11-2026 |
| Origen | Hallazgos de `INFORME_AUDITORIA_TECNICA.md` |
| Alcance | Propuesta — **ninguna mejora se ejecutó durante la auditoría** |

## Resumen por prioridad

| Prioridad | Tareas | Tema central |
|---|---|---|
| P0 | 2 | Producción segura (settings + throttling) |
| P1 | 5 | Endurecimiento, suite completa, backups, frontend |
| P2 | 8 | Correcciones de trazabilidad, observabilidad, consistencias |
| P3 | 7 | Limpieza, documentación, automatización del contrato |

---

## P0 — Impiden demostrar funcionamiento con seguridad o comprometen integridad

### MEJ-P0-01 — Configuración de producción real

- **Descripción**: crear `config/settings/production.py` (DEBUG=False, ALLOWED_HOSTS, SECURE_SSL_REDIRECT, HSTS, cookies seguras, CORS explícito, LOGGING), cambiar el CMD del Dockerfile a gunicorn y eliminar `DEBUG=1`/settings `local` del compose por defecto.
- **Justificación**: hoy el despliegue por defecto es inseguro (AUD-P0-01); recomendación R5 del sprint S1 sigue abierta.
- **Dependencias**: ninguna.
- **Módulo/archivos**: `backend/src/config/settings/`, `Dockerfile`, `docker-compose.yml`, `nginx/nginx.conf`.
- **Criterios de aceptación**: `manage.py check --deploy` sin errores de nivel crítico; contenedor sirve con gunicorn; DEBUG=False por defecto.
- **Pruebas**: suite completa en verde tras el cambio; smoke de despliegue.
- **Riesgo**: medio (toca despliegue). **Esfuerzo**: M.

### MEJ-P0-02 — Throttling / rate limiting

- **Descripción**: habilitar throttling DRF: `AnonRateThrottle` estricto en `auth/token/` y `ScopedRateThrottle`/UserRateThrottle global razonable.
- **Justificación**: login sin límite permite fuerza bruta (AUD-P0-02).
- **Dependencias**: ninguna.
- **Archivos**: `settings/base.py`, `authentication/adapters/views.py`.
- **Criterios de aceptación**: exceder el límite devuelve 429 (documentar el código en OpenAPI); pruebas del comportamiento.
- **Riesgo**: bajo. **Esfuerzo**: S.

## P1 — Importantes para completar procesos y operación

### MEJ-P1-03 — Endurecimiento de seguridad complementario

Restringir `/api/v1/schema|docs|redoc/` en producción (AUD-P1-02); bloquear `seed_initial_data` fuera de DEBUG (riesgo cuentas demo); declarar `PRIVATE_MEDIA_ROOT` (AUD-P2-05). Esfuerzo S.

### MEJ-P1-04 — Suite completa por defecto

Incluir `src/core`, `src/core/adapters/tests` y `tests/e2e` en `testpaths` de `pyproject.toml` (AUD-P1-04). Criterio: `pytest -q` ejecuta 526 pruebas. Esfuerzo XS.

### MEJ-P1-05 — Backups y restauración

Backup programado de PostgreSQL y del volumen `media_data`, con procedimiento de restauración documentado y probado (AUD-P1-05). Esfuerzo M.

### MEJ-P1-06 — Healthcheck de la aplicación

Endpoint o comando de salud + healthcheck en compose. Esfuerzo S.

### MEJ-P1-07 — Continuar el plan FE (vistas V-01…V-09)

Prioridad sugerida: V-01 (login real), V-07 (bandeja), V-02 (dashboard estudiante) — máximo valor de demostración con las APIs existentes. Esfuerzo L (proyecto aparte según specs/003).

## P2 — Correcciones y mejora operativa

| ID | Tarea | Hallazgo | Esfuerzo |
|---|---|---|---|
| MEJ-P2-08 | Corregir `estado_anterior` en `emitir_informe.py` (capturar el estado antes de mutar) | AUD-P2-01 | S |
| MEJ-P2-09 | Eliminar prints de depuración y configurar `LOGGING` | AUD-P2-02/03 | S |
| MEJ-P2-10 | Rotación de refresh tokens + blacklist (o decisión documentada de no rotar) | AUD-P2-04 | M |
| MEJ-P2-11 | Emitir eventos de auditoría faltantes; resolver IP real del request | AUD-P3-02, AUD-P2-06 | M |
| MEJ-P2-12 | Alinear roles del servicio de declaratoria con la matriz RBAC | AUD-P2-07 | S |
| MEJ-P2-13 | Ajustar securityScheme del OpenAPI (BearerAuth/jwtAuth) y quitar security del login | AUD-P2-08 | S |
| MEJ-P2-14 | Corregir READMEs (17 endpoints, 93 %, 526 pruebas; reescribir README del backend; actualizar README frontend) | AUD-P2-09, AUD-P3-06/08 | S |
| MEJ-P2-15 | Subir cobertura de ramas de error (verificacion/views 65 %, registrar_observacion 76 %) | AUD-P2-10 | M |

## P3 — Optimizaciones futuras

| ID | Tarea | Hallazgo |
|---|---|---|
| MEJ-P3-16 | Eliminar o rutear código muerto (`PeticionDocumentalViewSet`, `ObservacionViewSet`) | AUD-P3-01 |
| MEJ-P3-17 | Limpieza flake8 + black/isort en CI | AUD-P3-03 |
| MEJ-P3-18 | Generar `contracts/openapi.yaml` desde CI (evitar copia manual) | AUD-P3-04 |
| MEJ-P3-19 | Consolidar constituciones (v2.0 vs v2.1) y ADRs fantasma/vacíos | AUD-P3-05 |
| MEJ-P3-20 | Usar o eliminar guard/barrels vacíos del frontend | AUD-P3-07 |
| MEJ-P3-21 | `Content-Length` real en descargas | AUD-P3-09 |
| MEJ-P3-22 | CI/CD con PostgreSQL real + cobertura mínima (`--cov-fail-under=70`) | R4/S1 |

## Orden sugerido

1. MEJ-P0-02 (rápido, alto valor) → 2. MEJ-P1-04 (XS) → 3. MEJ-P0-01 → 4. MEJ-P2-08/09 → 5. MEJ-P1-05 → 6. resto por prioridad.
