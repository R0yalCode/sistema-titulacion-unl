---
title: "Seguridad — Consideraciones"
---

# Consideraciones de seguridad

## Fortalezas verificadas

| Control | Evidencia |
|---|---|
| RBAC de mundo cerrado + tests de igualdad con la spec | `test_rbac_permissions.py` |
| Anti-IDOR a nivel ORM con semántica 404 | `test_idor_isolation_expediente.py` (13) |
| Validación real de PDF (magic bytes, no MIME/extensión) | `test_pdf_ingestion_and_security.py` (39) |
| Almacenamiento privado sin URL pública | `PrivateMediaStorage.url()` lanza excepción |
| Hash SHA-256 de cada documento | campo `hash_sha256` |
| Bloqueo pesimista en escrituras críticas | todos los servicios |
| Sin secretos en el código (gitleaks 0 hallazgos) | `docs/security_report.md` |
| `SECRET_KEY` obligatoria, `DEBUG=False` por defecto | `settings/base.py` |
| Cuentas demo marcadas como no productivas | `seed_initial_data.py:6-9` |

## Brechas abiertas (priorizadas; detalle en el plan de mejora)

| # | Brecha | Prioridad |
|---|---|---|
| 1 | ~~Sin throttling/rate limiting~~ — **Resuelto**: login 5/min por IP real (SEC-T002), carga 10/h (SEC-T008) y operaciones mutantes 30/min por usuario (VULN-001, INC-01, 2026-11-11; `core/adapters/throttling.py`) | — |
| 1b | ~~`SCOPE_ASIGNADO` no implementado en `ScopeFilterMixin`~~ — **Resuelto** (VULN-002, INC-01): `core/adapters/scope_filter.py` | — |
| 1c | ~~Sin verificación SHA-256 en la descarga~~ — **Resuelto** (VULN-003, INC-01): `peticiones/adapters/views.py` | — |
| 2 | Docker con `DEBUG=1` y `runserver` en desarrollo. `config/settings/production.py` existe (SEC-T001: HTTPS, HSTS, cookies, CORS, CSP report-only); revisar el despliegue real | P1 |
| 3 | `/api/v1/schema|docs|redoc/` restringido a administradores en producción (`test_swagger_protection.py`); abierto en desarrollo | P2 |
| 4 | Sin backups ni procedimiento de restauración | P1 |
| 5 | JWT sin rotación/blacklist | P2 |
| 6 | `print()` de depuración en producción; sin `LOGGING` | P2 |
| 7 | IP de auditoría siempre vacía | P2 |
| 8 | Sin escaneo antivirus de PDFs (solo validación estructural) | P2 |
| 9 | Cuentas demo con contraseña pública (riesgo si se despliega sin bloqueo) | P1 en contexto real |

## Reporte de seguridad previo

`docs/security_report.md` (T044, 22-oct-2026): Gitleaks 0 hallazgos; Bandit 0 high/17 medium/1303 low (en tests); Safety 0 críticos/49 altos en dependencias de desarrollo.
