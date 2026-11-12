---
system: SGT-SIAAF
type: session-log
date: 2026-11-12
agent: claude-code
branch: fix/frontend-lib-no-versionada
---

# Sesión 2026-11-12 — `frontend/src/lib/` no versionado

## Causa

La regla `lib/` del `.gitignore` raíz (línea 17, de la plantilla de Python) ignoraba `frontend/src/lib/`. Por eso sus 15 archivos (8 módulos y 7 pruebas) nunca entraron en Git. Esto afecta a todas las versiones con frontend publicadas, de v0.2.0 a v0.5.0.

## Corrección

- `b218208`: excepción acotada `!frontend/src/lib/`. La regla `lib/` se mantiene y sigue ignorando `frontend/coverage/lib`, `backend/lib`, `lib/` en la raíz y otros `lib/` anidados.
- `79812bb`: versionado de los 15 archivos, revisados: sin secretos ni archivos generados.
- Consumidores: 23 módulos fuera de `lib/`, 22 por el alias `@/lib/` y `main.tsx` por `./lib/env`. La cifra de 24 de la auditoría anterior contaba 2 pruebas internas de `lib/` y omitía `main.tsx`.

## Evidencia

- **Árbol de trabajo:** `typecheck` y lint sin errores; 58/58 archivos, 328/328 pruebas; build correcto.
- **Clon limpio** de la rama, con `npm ci` desde `package-lock.json` (node 24.22.1, npm 11.19.1): `typecheck`, lint, 328/328 pruebas y build correctos. El bundle incluye el código de `lib/`.
- **Control negativo en `develop` `cd20875`:** 29 errores «Cannot find module», 22 archivos de prueba fallidos y build fallido.

## Pendientes

- Integración en `develop` y `main`, y evaluación de v0.5.1 (PATCH): requieren autorización.
- `frontend/coverage/` no está en `frontend/.gitignore`; hoy solo `coverage/lib` queda ignorado por la regla `lib/`.
