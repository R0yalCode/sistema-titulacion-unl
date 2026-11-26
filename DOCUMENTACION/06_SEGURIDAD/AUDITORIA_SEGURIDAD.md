---
title: "Auditoría de seguridad"
---

# Auditoría de seguridad — SGT-SIAAF

**Objetivo de esta página:** consolidar, sin duplicar íntegramente, los hallazgos de seguridad ya producidos por el equipo (`docs/security_report.md`, `docs/06-seguridad/consideraciones-seguridad.md`, `docs/auditoria-backend/seguridad/`), actualizados con verificación directa de código donde esta auditoría encontró que el estado real difiere de lo documentado. Fuente de herramientas automatizadas: `docs/security_report.md` (Gitleaks, Bandit, Safety — 22-oct-2026); no se reejecutaron esas herramientas en esta pasada (no son parte del alcance de una auditoría documental; si se requiere, corresponde a Fase 7 con el entorno real).

## 1. Resultados de herramientas automatizadas (citados, no reejecutados)

| Herramienta | Resultado (22-oct-2026) | Estado |
|---|---|---|
| Gitleaks 8.25.1 | 0 secretos reales (tras excluir constantes de prueba) | ✅ Passed |
| Bandit 1.9.4 | 0 High/Critical en `src/`; 17 Medium + 1303 Low, todos `B101 assert_used` en archivos de prueba (falso positivo conocido) | ✅ Passed |
| Safety 3.8.1 | 0 críticos; 49 vulnerabilidades en 15 paquetes, mayormente dependencias de desarrollo/transitivas; **2 en `djangorestframework` 3.16.1 (producción, prioridad Alta)** | ⚠️ Condicional en su momento |

## 2. Verificación de remediación: la vulnerabilidad de DRF señalada por Safety ya fue corregida

El informe de Safety (22-oct-2026) recomendaba explícitamente: *"Actualizar djangorestframework a ≥ 3.17.2 — Vulnerabilidades CVE-2026-73228, CVE-2026-73229"*, como acción **inmediata antes de release a producción**. Se verificó en la Fase 4 de esta auditoría (lectura directa de `backend/requirements.txt`, 2026-11-06) que el manifiesto actual fija `djangorestframework>=3.17.2,<4.0` — **la recomendación fue aplicada**. Esto también explica la discrepancia de versión ya señalada entre `docs/adr/0002-stack-django-drf-postgresql.md` (que aún cita `3.16.x`, sin actualizar tras el parche) y el código real.

**Conclusión:** de las vulnerabilidades de prioridad "Alta" señaladas por Safety, la única de dependencia directa de producción (DRF) está **remediada y verificada**. Las demás (urllib3, sqlparse, python-dotenv, pillow) son transitivas de prioridad Media y no se reverificaron en esta pasada.

## 3. Corrección de otro hallazgo: el throttling de login ya está implementado

Ver el detalle completo en `AUTENTICACION.md` §5. **`docs/06-seguridad/consideraciones-seguridad.md` y `docs/RESUMEN_EJECUTIVO.md` listan "sin throttling/rate limiting (incluido login)" como brecha P0.** Verificado directamente en `base.py` y en la vista de login (Fase 6, 2026-11-06): existe `DEFAULT_THROTTLE_RATES` con límite de 5/minuto en login y 10/hora en carga de documentos, con una clase de throttling (`TrustedProxyScopedRateThrottle`) diseñada para ser efectiva detrás de un proxy (`TRUSTED_PROXIES` configurado en `production.py`, SEC-T005 ya implementado). **Este P0 está cerrado**, no abierto como indica la documentación previa — probablemente implementado después de la fecha de esos informes (los códigos de tarea `SEC-T002`/`SEC-T005` con fecha de aprobación "2026-11-05" en `.env.example` son consistentes con esa hipótesis, sin confirmarla formalmente).

## 4. Brechas que SÍ siguen abiertas (reverificadas, no solo citadas)

| # | Brecha | Prioridad original | Estado verificado en esta Fase 6 |
|---|---|---|---|
| 1 | Sin rotación/blacklist de refresh tokens | P2 | **Confirmado vigente** (`ROTATE_REFRESH_TOKENS=False` en código) |
| 2 | `/api/v1/schema\|docs\|redoc/` con `AllowAny` | P1 | **Confirmado vigente** (verificado en Fase 5, `urls.py`) |
| 3 | ~~IP de auditoría siempre vacía~~ | P2 | **CORREGIDO en Fase 9**: `resolver_ip_cliente()` (`core/adapters/client_ip.py`) captura la IP real, consciente de `TRUSTED_PROXIES`, y `notificaciones/adapters/signals.py` la persiste en cada `EventoAuditoria`. El hallazgo heredado ya no es cierto — ver `DOCUMENTACION/09_OBSERVABILIDAD/OBSERVABILIDAD.md` §3-4. |
| 4 | `print()` de depuración en producción | P2 | No reverificado en esta pasada |
| 5 | Sin backups ni procedimiento de restauración documentado | P1 | No reverificado en esta pasada (es un tema de Fase 8, despliegue) |
| 6 | Sin escaneo antivirus de PDFs (solo validación estructural: magic bytes + tamaño + hash) | P2 | Confirmado por diseño — es una limitación conocida, no un defecto |
| 7 | Excepciones de dominio que responden 500 en vez de 400/422 (INC-21, ver `CONTRATO_API.md` §3) | Sin priorizar previamente | **Nuevo en esta auditoría**: puede implicar fuga de información si el 500 expone traceback — pendiente de confirmar en Fase 7 si `DEBUG=False` en producción efectivamente lo evita (es la configuración por defecto, verificada en Fase 0) |

## 5. Mapeo a categorías OWASP (orientativo, sobre controles ya verificados en esta auditoría — no es un pentest)

| Categoría OWASP Top 10 (2021) | Control relevante en SGT-SIAAF | Evidencia |
|---|---|---|
| A01 Broken Access Control | RBAC de mundo cerrado + anti-IDOR (404) | `AUTORIZACION_PERMISOS.md` |
| A02 Cryptographic Failures | Claves de firma separadas (JWT vs Django), sin `SECRET_KEY` por defecto | `AUTENTICACION.md` §4 |
| A03 Injection | ORM de Django (parametrizado por diseño); sin SQL crudo detectado en los servicios revisados | No se auditó exhaustivamente cada archivo en esta pasada |
| A04 Insecure Design | Validación estricta de PDF (magic bytes, no extensión/MIME declarado) | `PROTECCION_DATOS.md` |
| A05 Security Misconfiguration | `DEBUG=False` por defecto, `ALLOWED_HOSTS=[]` por defecto | Verificado Fase 0 |
| A07 Identification and Authentication Failures | JWT con expiración corta (30 min) + throttling de login | `AUTENTICACION.md` |
| A09 Security Logging and Monitoring Failures | Bitácora de auditoría JSONB con IP real (corregido en Fase 9) + logging estructurado JSON con enmascarado de datos sensibles; posiblemente aún con eventos sin emitir (no reverificado) | `DOCUMENTACION/09_OBSERVABILIDAD/OBSERVABILIDAD.md` |

Este mapeo es orientativo y no sustituye un pentest o un análisis OWASP ASVS formal, que no se realizó en este trabajo (fuera de alcance: esta es una auditoría documental, no una prueba de penetración).

## 6. Conclusión de esta fase

Dos de los hallazgos de seguridad más críticos reportados previamente como abiertos (vulnerabilidad de DRF y ausencia de throttling de login) están **verificablemente corregidos**, lo cual mejora sustancialmente el panorama de seguridad descrito en los informes de octubre/principios de noviembre de 2026. Las brechas restantes (rotación de refresh, IP de auditoría, backups) siguen sin evidencia de corrección y se mantienen como pendientes documentadas, no inventadas.
