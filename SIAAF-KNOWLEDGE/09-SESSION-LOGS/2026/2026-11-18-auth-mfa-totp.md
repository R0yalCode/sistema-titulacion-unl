---
system: SGT-SIAAF
type: session-log
date: 2026-11-18
agent: claude-code
branch: build/reorganizacion-estructural (sin push ni merge)
commits: [c6650a1, c4150e8, ebe75a9, 49153f3, 157da6d, f76fee7]
---

# Sesión 2026-11-18 — Login con TOTP (Google Authenticator), confianza de 5 días y landing

## Autorizaciones del responsable (R0yalCode, 2026-11-18)

- Excepción a «frontend only»: se autorizan backend, migración `authentication/0002` y `openapi.yaml`.
- Dependencias nuevas: `pyotp`, `segno` y `cryptography`.
- El trabajo AUTH-RC (recuperación de contraseña) sin commitear es de R0yalCode.
- **Implementación centralizada** (DK-010, enmiendas 2026-11-11/12) con este reparto aprobado:

| Tarea | Responsable (autor Git) | Commit(s) |
|---|---|---|
| AUTH-RC (previo) | R0yalCode | `c6650a1` |
| AUTH-A Arquitectura, configuración y dependencias | R0yalCode | `c4150e8`, `157da6d` |
| AUTH-B Backend MFA | Dan1el17 | `ebe75a9` |
| AUTH-C Frontend de ingreso y MFA | JuanCalopinoo | `49153f3` |
| AUTH-D Pruebas de seguridad y E2E | JJOC3S | `f76fee7` |
| AUTH-E Documentación y landing | 7777-C | commit que incluye esta nota |

La ejecución material del código fue de Claude Code. El autor Git identifica al integrante responsable de cada tarea y el committer es R0yalCode. No se afirma que los integrantes escribieran el código.

- Política de logout: todo cierre de sesión pedido por el usuario revoca la confianza del dispositivo.

## Resultados verificados

- Backend (imagen `sgt-siaaf-backend`, SQLite): 850 aprobadas y 13 omitidas. `makemigrations --check` sin cambios. `spectacular --validate` sin diferencias con `openapi.yaml`.
- Frontend: lint, typecheck y build OK; vitest 458/458.
- E2E real por HTTP (`scripts/e2e/e2e_mfa.py`): 17/17. El log del servidor no contiene secretos ni URI `otpauth`.
- Mutación: desactivar la anti-reutilización o la caducidad de la confianza hace fallar las pruebas.

## Hallazgos

- Los mensajes de los commits `c4150e8` (A) y `ebe75a9` (B) citan 850 pruebas aprobadas. Esa cifra incluía las pruebas de AUTH-D, que entonces estaban en el árbol de trabajo sin commitear.
- `.venv` del repositorio roto (sin pip ni Django).
- `local.py` heredaba `Secure` en la cookie de confianza si faltaba `DEBUG`. Lo detectó la E2E y se corrigió en `157da6d`.
- Sin ejecutar: la variante PostgreSQL (`test_postgres`) y una prueba manual con la app Google Authenticator en un teléfono real (el E2E usa `pyotp`, que implementa el mismo RFC 6238).
- `docs/autenticacion/referencias/` (capturas del SAC) queda sin commitear, a decisión del responsable.

## Documentación

[[DEGREE_PROCESS_OVERVIEW]] (etapas de la landing). Detalle en `docs/autenticacion/{flujo-autenticacion,politica-2fa,arquitectura-cas}.md`.
