---
title: "Autenticación"
---

# Autenticación — SGT-SIAAF

**Fuentes:** `backend/src/config/settings/base.py` (leído directamente), `docs/06-seguridad/autenticacion.md`, `docs/06-seguridad/SECURITY_CONFIG.md`, `backend/.env.example`. Esta página **corrige una inconsistencia detectada entre esos dos documentos del propio proyecto** (ver §3).

## 1. Mecanismo

JWT stateless vía `djangorestframework-simplejwt`. Transporte: cabecera `Authorization: Bearer <token>`. Endpoint de emisión: `POST /api/v1/auth/token/` (sin autenticación previa, es el login).

## 2. Configuración verificada directamente en `base.py`

| Parámetro | Valor verificado | Línea de referencia |
|---|---|---|
| `ACCESS_TOKEN_LIFETIME` | **30 minutos** | `base.py:122` |
| `REFRESH_TOKEN_LIFETIME` | 24 horas | `base.py:123` |
| `ROTATE_REFRESH_TOKENS` | `False` (sin rotación) | `base.py:124` |
| `SIGNING_KEY` | `JWT_SIGNING_KEY` (variable de entorno independiente de `SECRET_KEY`) | `base.py:126` |

## 3. Corrección de una inconsistencia documental interna

`docs/06-seguridad/autenticacion.md` afirma "access token 60 minutos". `docs/06-seguridad/SECURITY_CONFIG.md` (más detallado y con pruebas asociadas citadas: `test_access_token_lifetime_30_minutes`) documenta que **SEC-T006 cambió el valor de 60 a 30 minutos**. La lectura directa del código (`base.py:122`, arriba) confirma **30 minutos** como el valor vigente. `docs/06-seguridad/autenticacion.md` quedó desactualizado tras aplicar SEC-T006 y no se modifica en este trabajo (no se edita `docs/`); se deja esta página como la referencia corregida para el portal.

## 4. Separación de claves de firma (SEC-T004) — verificado

`SECRET_KEY` (Django: sesiones/CSRF/cookies) y `JWT_SIGNING_KEY` (SimpleJWT: firma de JWT) son **dos variables de entorno independientes, ambas obligatorias** (`env("...")` sin valor por defecto — Django no arranca si falta alguna). Si ambas coinciden, se registra un `logging.warning` (no bloquea el arranque, pero deja constancia). Verificado en código: `base.py:11-18`.

## 5. Throttling en el login — hallazgo de corrección importante (P0 cerrado)

**`docs/RESUMEN_EJECUTIVO.md` y `docs/06-seguridad/consideraciones-seguridad.md` listan como brecha P0 abierta: "Sin throttling/rate limiting (incluido login)".** Se verificó directamente en el código (Fase 6 de esta auditoría, 2026-11-06) que **esto ya no es así**:

- `base.py` declara `DEFAULT_THROTTLE_RATES` con `"auth": env("AUTH_THROTTLE_RATE", default="5/minute")`.
- La vista de login (`TokenPairView`) usa una clase de throttling propia, `TrustedProxyScopedRateThrottle` (no el genérico `AnonRateThrottle`), diseñada explícitamente para ser consciente de `TRUSTED_PROXIES` y evitar que un atacante burle el límite falsificando la cabecera de IP de origen.
- `TRUSTED_PROXIES` está configurado en `production.py` (coherente con el comentario de `.env.example`: "Solo es efectivo contra suplantación de IP una vez TRUSTED_PROXIES esté configurado correctamente (SEC-T005)" — SEC-T005 ya está implementado).
- También existe throttling para carga de documentos: `"document_upload": "10/hour"`.

**Conclusión:** el hallazgo P0 "sin throttling" de `docs/RESUMEN_EJECUTIVO.md` (05-nov-2026) está **desactualizado**: el throttling de login y de carga de documentos ya está implementado y es efectivo en producción (depende de `TRUSTED_PROXIES`, que también está configurado). Esto se corrige en `AUDITORIA_SEGURIDAD.md` de esta misma fase.

## 6. Limitaciones conocidas que siguen vigentes (no corregidas por lo anterior)

- Sin rotación de refresh tokens ni blacklist (`ROTATE_REFRESH_TOKENS=False`, verificado): un refresh robado sigue siendo usable durante sus 24 horas de vigencia.
- Almacenamiento del token en el frontend: `sessionStorage` (según `docs/06-seguridad/autenticacion.md`; no se reverificó contra el código del frontend en esta pasada, fuera del alcance del incremento backend).
