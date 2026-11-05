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
| 1 | Sin throttling/rate limiting (incluido login) | P0 |
| 2 | Docker con `DEBUG=1` y `runserver`; sin `settings/production.py` ni hardening HTTPS/HSTS/cookies | P0/P1 |
| 3 | `/api/v1/schema|docs|redoc/` con `AllowAny` | P1 |
| 4 | Sin backups ni procedimiento de restauración | P1 |
| 5 | JWT sin rotación/blacklist | P2 |
| 6 | `print()` de depuración en producción; sin `LOGGING` | P2 |
| 7 | IP de auditoría siempre vacía | P2 |
| 8 | Sin escaneo antivirus de PDFs (solo validación estructural) | P2 |
| 9 | Cuentas demo con contraseña pública (riesgo si se despliega sin bloqueo) | P1 en contexto real |

## Reporte de seguridad previo

`docs/security_report.md` (T044, 22-oct-2026): Gitleaks 0 hallazgos; Bandit 0 high/17 medium/1303 low (en tests); Safety 0 críticos/49 altos en dependencias de desarrollo.
