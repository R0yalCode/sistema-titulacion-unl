---
system: SGT-SIAAF
type: session-log
date: 2026-11-22
agent: claude-code
branch: feat/dashboard-estudiante (sin commit, sin push ni merge)
commits: []
---

# Sesión 2026-11-22: dataset de 80 cuentas y pruebas MFA

## Alcance

Lo pidió expresamente el responsable:
- 10 cuentas por cada uno de los 8 roles reales, con identidades ficticias de apariencia institucional.
- Perfiles MockSGA, expedientes en distintos estados construidos con los servicios de negocio, y pruebas de MFA y RBAC.

Quedan excluidos los commits, el push, el merge, los cambios de rama, crear roles y cambiar el RBAC o la arquitectura MFA.

## Qué se hizo

- Nueva app `apps/entorno_pruebas`:
  - Marcador interno `RegistroDatasetSintetico` (migración `0001`) y admin de solo lectura.
  - `dataset.py` con la definición determinista del dataset.
  - Comando `seed_sgt_siaaf`: idempotente; se niega a ejecutarse en producción, sin mock permitido o con SMTP; nunca toca `MfaDevice`.
- Catálogo simulado ampliado con 2 facultades y 5 carreras.
- Documentación: `docs/entorno-pruebas/dataset-sgt-siaaf.md`.

## Pruebas (resultados reales)

- Backend con SQLite: 879 pasaron, 33 de ellas nuevas en `entorno_pruebas`.
- `tests/` más `entorno_pruebas` contra PostgreSQL 16 desechable: 72 pasaron.
- Frontend sin cambios: lint, typecheck y build en verde; vitest 539/539.
- OpenAPI regenerado: sin cambios.
- Entorno de desarrollo:
  - Se guardó la imagen de respaldo `sgt-siaaf-backend:pre-dataset-sgt-siaaf` y se aplicó la migración.
  - El seed creó 80 cuentas, 10 perfiles y 8 escenarios (33 documentos y 62 notificaciones).
  - La segunda ejecución no creó nada.
  - Las 80 cuentas llegan a `mfa_setup_required` y 8 logins HTTP a través de nginx (1 por rol) también.
- **No se realizó** el escaneo con Google Authenticator en un teléfono.
- Las 9 cuentas previas y el MFA del responsable siguen intactos (1 dispositivo confirmado, que no es del dataset).

## Pendientes

- Prueba manual con Google Authenticator (guion en el §10 de la documentación).
- RBAC de RESPONSABLE_DEPENDENCIA.
