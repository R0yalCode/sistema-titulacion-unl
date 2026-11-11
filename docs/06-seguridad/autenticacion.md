---
title: "Seguridad — Autenticación"
---

# Autenticación

## Mecanismo

JWT stateless (SimpleJWT, HS256) según ADR-0003.

| Parámetro | Valor |
|---|---|
| access token | 60 minutos, claims `cedula` y `roles[]` |
| refresh token | 24 horas, sin rotación |
| firma | HS256 con `JWT_SIGNING_KEY` (independiente de `SECRET_KEY`, SEC-T004) |
| transporte | Cabecera `Authorization: Bearer` |
| almacenamiento frontend | `sessionStorage` (muere al cerrar pestaña) |

## Validaciones verificadas (pruebas)

- Credenciales inválidas → 401.
- Token expirado → 401.
- Sin token → 401 en todas las rutas de negocio.
- Firma inválida → 401.
- Anónimo → 401 (nunca 403) en rutas protegidas.

## Limitaciones conocidas

- Sin rotación de refresh ni blacklist: un refresh robado es usable durante su vigencia (AUD-P2-04).
- Resuelto (SEC-T004, 2026-11-05): `SIGNING_KEY` usa `JWT_SIGNING_KEY`, variable de entorno independiente de `SECRET_KEY`. Ver `docs/06-seguridad/SECURITY_CONFIG.md`.
- ~~Sin throttling en el endpoint de login (AUD-P0-02)~~ — resuelto: `TokenPairView` usa `TrustedProxyScopedRateThrottle` con ámbito `auth` (5/min por IP real, SEC-T002).
- No existen endpoints `POST /auth/token/refresh/` ni `POST /auth/logout/` (VULN-005, INC-02): el frontend vuelve a iniciar sesión al expirar el access token.
