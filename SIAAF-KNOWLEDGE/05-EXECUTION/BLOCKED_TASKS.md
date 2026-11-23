---
system: SGT-SIAAF
type: execution
area: blocked
status: verified
source: sgt-siaaf/specs/003-frontend-titulacion/tasks.md §2 + verified-code
last_verified: 2026-11-22
---

# Tareas bloqueadas y dependencias no autorizadas

## Dependencias backend (tasks 003 §2): todas **NO AUTORIZADAS**

| ID | Dependencia | Vistas | ¿Confirmado ausente en el código? |
|---|---|---|---|
| BE-01 | Perfil `/me` o claims `carrera`/`facultad` en el JWT | V-02…V-06 | Parcial (2026-11-22): `GET /api/v1/perfil-academico/` da carrera y facultad del ESTUDIANTE (fuente simulada MockSGA); sin `/me` general ni claims en el JWT |
| BE-02 | `GET /peticiones/{id}/` y listado de documentos | V-04, V-06, V-08 | ✅ Ausente |
| BE-03 | Refresh y logout de servidor | V-01, layout | ✅ Ausente |
| BE-04 | `GET .../checklist/` para ESTUDIANTE (propios) | V-04 | ✅ 403 para ESTUDIANTE |
| BE-05 | Perfil e historial completo del estudiante | V-02…V-04 | ✅ Ausente (no bloquea V-02, DEC-16) |
| BE-06 | `opcion_titulacion` (modalidad) | V-03, V-04 | ✅ Ausente |
| BE-07 | Exponer `motivo_observacion` | V-04, V-08 | No reverificado |
| BE-08 | CORS para el origen del frontend | Todas | `django-cors-headers` instalado y `CORS_ALLOWED_ORIGINS` en `.env.example` para producción; configuración de desarrollo no reverificada |
| BE-09 | Bandeja para roles sin expedientes + filtros | V-07 | ✅ `MAPA_INTERVENCION_POR_ROL` vacío para SEC_CAR, DIR_CAR y RESP_DEP |
| BE-10 | Catálogo de carreras `GET /carreras/` | V-03 | Catálogo interno `Carrera`/`Facultad` creado el 2026-11-22 (datos de demostración `MOCK-…`); sin endpoint público de listado: V-03 ya no lo necesita (la carrera sale de `GET /api/v1/perfil-academico/`) |
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

## Incidencias funcionales de notificaciones (registradas el 2026-11-22)

Quedan abiertas y **sin cambio de comportamiento** hasta una decisión específica del responsable.

| ID | Descripción | Impacto | Riesgo | Propuesta de tratamiento |
|---|---|---|---|---|
| INC-NOTIF-01 | `declarar_aptitud` envía copia a los directores de toda la facultad, pero el RBAC de Dirección tiene alcance de carrera | Las copias de otra carrera quedan guardadas y no se muestran (5 en los datos locales) | Medio: una autoridad puede creer que no recibió la copia; mostrarla sin decidir ampliaría la visibilidad de expedientes | Decidir la regla normativa. Recomendado: limitar el envío a la carrera del expediente y conservar el Decanato como copia de facultad |
| INC-NOTIF-02 | `obtener_usuario_emisor` recurre al primer usuario del rol cuando no hay responsable en el ámbito | El aviso puede llegar a alguien de otro ámbito, que no lo verá, y la solicitud puede quedar sin atender | Alto para el flujo documental: pérdida silenciosa de una solicitud; además, el mensaje incluye datos del estudiante | Quitar el respaldo global y registrar un error o una cola de solicitudes sin responsable, previa decisión funcional |
| INC-NOTIF-03 | Usuarios con roles de carrera o facultad sin ámbito institucional completo | Reciben 200 con lista vacía, aunque tengan avisos guardados | Medio: la ausencia de avisos parece normal y puede ocultar trabajo pendiente | Auditar las cuentas, completar su ámbito y definir un aviso de «ámbito incompleto» en la interfaz |

## Tareas obligatorias antes de `main`

| ID | Tarea | Motivo |
|---|---|---|
| PROD-ACAD-01 | Incorporar `settings/production.py` en un cambio independiente, con una prueba que use `DEBUG=1` | Sin ese cambio, `DEBUG=1` en el entorno de producción activa la fuente simulada MockSGA |

## Relacionado

[[TASKS]] · [[API_CONTRACTS]] · [[CURRENT_STATE]]
