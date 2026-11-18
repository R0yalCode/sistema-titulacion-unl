---
system: SGT-SIAAF
type: session-log
date: 2026-11-18
agent: claude-code
branch: build/reorganizacion-estructural → develop
commits: [5701b4c, 1d02ad6, fe1a4c6]
---

# Sesión 2026-11-18 (2) — Acceso por correo institucional, login con identidad SAC, restablecimiento del 2FA y nueva landing

## Autorización y reparto (R0yalCode, 2026-11-18)

El responsable autorizó la integración en `develop` y asignó expresamente las tareas en **modalidad centralizada** (DK-010, enmiendas 2026-11-11/12). La ejecución material fue de Claude Code; el autor Git identifica al integrante responsable y el committer es R0yalCode.

| Tarea | Responsable | Commit | Contenido |
|---|---|---|---|
| AUTH-F | Dan1el17 | `5701b4c` | Backend: acceso por correo @unl.edu.ec, migración 0003, restablecimiento del 2FA por enlace |
| AUTH-G | JuanCalopinoo | `1d02ad6` | Frontend: login con identidad del SAC, mensajes de validación, páginas de restablecimiento del 2FA |
| AUTH-H | 7777-C | `fe1a4c6` | Landing institucional según la referencia UNL |
| AUTH-I | JJOC3S | commit que incluye esta nota | Documentación de `docs/autenticacion/` y referencias visuales |

## Resultados verificados

- Backend: 889 aprobadas y 13 omitidas. Sin migraciones pendientes. `openapi.yaml` sincronizado.
- Frontend: lint, typecheck y build OK; vitest 475/475. El commit AUTH-G se verificó aislado (472/472 sobre el árbol del índice).
- Stack Docker (PostgreSQL): migraciones 0002 y 0003 aplicadas; correos demo `sgtdemo.<usuario>@unl.edu.ec`; verificación HTTP real 87/87 sobre 7 cuentas.
- Landing: verificación CDP en 5 resoluciones, estados del botón y navegación a `/login`.

## Incidencia

Un script de verificación ejecutó `restablecer_mfa` sobre todas las cuentas y **borró el Google Authenticator que el responsable había registrado a mano en `estudiante_1`**. Su contraseña se conservó. Se corrigió el script para preservar las cuentas con datos propios. El responsable debe volver a registrar el autenticador.

## Pendientes de la UNL

- Canal del enlace de restablecimiento del 2FA (correo personal o institucional).
- Aceptación del procedimiento y de la espera de 72 h.
- Alternativa presencial.
- SMTP real.
- Autorización para usar la identidad visual del SAC en un servicio aún no integrado.

Detalle en `docs/autenticacion/{flujo-autenticacion,politica-2fa,arquitectura-cas}.md`.
