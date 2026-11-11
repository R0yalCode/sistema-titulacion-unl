---
system: SGT-SIAAF
type: execution
area: blocked
status: verified
source: sgt-siaaf/specs/003-frontend-titulacion/tasks.md §2 + verified-code
last_verified: 2026-11-11
---

# Tareas bloqueadas y dependencias no autorizadas

## Dependencias backend (tasks 003 §2): todas **NO AUTORIZADAS**

| ID | Dependencia | Vistas | ¿Confirmado ausente en el código? |
|---|---|---|---|
| BE-01 | Perfil `/me` o claims `carrera`/`facultad` en el JWT | V-02…V-06 | ✅ Ausente |
| BE-02 | `GET /peticiones/{id}/` y listado de documentos | V-04, V-06, V-08 | ✅ Ausente |
| BE-03 | Refresh y logout de servidor | V-01, layout | ✅ Ausente |
| BE-04 | `GET .../checklist/` para ESTUDIANTE (propios) | V-04 | ✅ 403 para ESTUDIANTE |
| BE-05 | Perfil e historial completo del estudiante | V-02…V-04 | ✅ Ausente (no bloquea V-02, DEC-16) |
| BE-06 | `opcion_titulacion` (modalidad) | V-03, V-04 | ✅ Ausente |
| BE-07 | Exponer `motivo_observacion` | V-04, V-08 | No reverificado |
| BE-08 | CORS para el origen del frontend | Todas | `django-cors-headers` instalado y `CORS_ALLOWED_ORIGINS` en `.env.example` para producción; configuración de desarrollo no reverificada |
| BE-09 | Bandeja para roles sin expedientes + filtros | V-07 | ✅ `MAPA_INTERVENCION_POR_ROL` vacío para SEC_CAR, DIR_CAR y RESP_DEP |
| BE-10 | Catálogo de carreras `GET /carreras/` | V-03 | ✅ Ausente |
| BE-11 | 409/412/428 con ETag/If-Match | Formularios | ✅ Ausente |

## Tareas bloqueadas

| Tarea | Motivo |
|---|---|
| **FE-T1213** (InlineAlerts 409/412/428) | BE-11. **No tocar** (`CLAUDE.md` máxima 5) |
| V-03 selector de modalidad / INC-08 | BE-06 + validación normativa |
| Dashboards por rol / INC-07 | INC-04 (app `indicadores`) + BE-09 |

## Brechas detectadas en esta construcción (sin ID previo)

| ID provisional | Brecha | Impacto |
|---|---|---|
| ~~GAP-STATE-01~~ | ~~No hay operación que pase `ENVIADA→EN_VERIFICACION`~~ | **Resuelta 2026-11-11** por E2-01 (`POST /expedientes/{id}/iniciar-verificacion/`, AUT-02) |
| GAP-STATE-02 | `CANCELADA` sin servicio ni endpoint | Ningún expediente puede cancelarse |
| GAP-RBAC-01 | `RESPONSABLE_DEPENDENCIA` sin permisos, aunque emite 3 de los 5 requisitos | Las dependencias no pueden cargar sus certificados |

Requieren **decisión humana** ([[DECISIONS_LOG]] DK-007).

## Relacionado

[[TASKS]] · [[API_CONTRACTS]] · [[CURRENT_STATE]]
