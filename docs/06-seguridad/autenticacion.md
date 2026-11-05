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
| firma | HS256 con `SECRET_KEY` de Django |
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
- `SIGNING_KEY = SECRET_KEY`: la clave de firma es la misma del framework (aceptable en MVP; separable a futuro).
- Sin throttling en el endpoint de login (AUD-P0-02).
