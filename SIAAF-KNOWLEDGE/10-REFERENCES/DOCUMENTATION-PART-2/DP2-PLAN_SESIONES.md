---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/PLAN_IMPLEMENTACION_SESIONES_USUARIOS_ACTIVOS.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/PLAN_IMPLEMENTACION_SESIONES_USUARIOS_ACTIVOS.md
source_version: "1.0"
source_date: 2026-11-09
nature: implementation-plan (proposal)
vigencia: propuesta; INC-02; requiere-dependencias-nuevas
last_verified: 2026-11-11
---

# DP2 · Plan de sesiones y usuarios activos (INC-02)

**Original:** [[PLAN_IMPLEMENTACION_SESIONES_USUARIOS_ACTIVOS]]

## Problema (§1), verificado

Access de 30 min ✅, refresh de 24 h sin rotación ✅ (`ROTATE_REFRESH_TOKENS=False`), sin sliding window, sin blacklist, sin tabla de sesiones ✅ (no existe). "`User.last_login` solo se actualiza en el admin": **no verificado**.

## Propuesta

- Modelo `SesionUsuario` (ID, usuario, inicio, última actividad, expiración, revocación, estado VIGENTE/REVOCADA/CERRADA/EXPIRADA, JTI de access y refresh).
- Claim `jti`, `ROTATE_REFRESH_TOKENS` + `BLACKLIST_AFTER_ROTATION` (app `token_blacklist`), `CustomTokenRefreshView`, `POST /auth/logout/`.
- Actividad sin escribir en cada petición: caché + `bulk_update` periódico (**Redis + Celery**), con una alternativa simple sin Redis/Celery (§11).
- Métricas KPI-ADM-09 (§4, §7): usuario registrado, habilitado, con login hoy, activo en los últimos 15 min, sesión vigente, sesión revocada.
- Tareas INC-02-T01…T10 (§5) y criterios de aceptación (§10).

## Observaciones

- Redis y Celery **no están** en `backend/requirements.txt`: serían dependencias nuevas (requieren autorización).
- La §10 lista criterios de aceptación con ✅: son **objetivos**, no evidencia de implementación.
- INC-02-T10 dice "logout ya en `AppLayout.tsx`": existe un logout **local** (FE-T016), no de servidor.
- Choca con la regla actual del frontend: sin refresh ni logout de servidor inventados (plan 003 §6, BE-03).

## Relacionado

[[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] (VULN-005) · [[BLOCKED_TASKS]] (BE-03)
