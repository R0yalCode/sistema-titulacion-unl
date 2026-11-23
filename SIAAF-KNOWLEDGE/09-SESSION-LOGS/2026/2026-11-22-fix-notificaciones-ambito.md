---
system: SGT-SIAAF
type: session-log
date: 2026-11-22
agent: claude-code
branch: fix/notificaciones-ambito-500 (base origin/develop 704d696; sin merge ni push)
commits: []
---

# Sesión 2026-11-22: error 500 en GET /notificaciones/

## Objetivo

Corregir, por autorización expresa del responsable (2026-11-22), el HTTP 500 de `GET /api/v1/notificaciones/` para Secretaría de carrera, Dirección de carrera, Secretaría abogada, Analista de apoyo y Decanato. La autorización no incluye merge, push, cambios en `main` o `develop`, ni reconstruir el servicio del puerto 8000.

## Causa raíz

`NotificacionViewSet` declaraba `scope_owner_field`, pero heredaba de `ScopeFilterMixin` los valores por defecto `carrera_id` y `facultad_id`. `NotificacionInterna` no tiene esos campos. Con un rol de alcance de carrera o facultad y un usuario con ese ámbito, el ORM lanzaba `FieldError` y la respuesta era 500. Los usuarios sin ámbito no llegaban a esa consulta, por lo que el defecto no aparecía en todas las cuentas.

## Cambios (rutas)

- `backend/src/apps/notificaciones/adapters/views.py`: el ámbito de carrera y facultad se resuelve con `expediente__carrera_id` y `expediente__facultad_id`, la convención de peticiones y verificación. Se mantienen `scope_owner_field` y el filtro `usuario_destino`.
- `backend/src/apps/notificaciones/tests/test_ambito_notificaciones.py`: 63 casos nuevos.

No cambian RBAC, MFA, JWT, modelos, migraciones, serializadores, OpenAPI ni `production.py`.

## Regla resultante

Una notificación es visible solo si está dirigida al usuario y alguno de sus roles le concede el ámbito de su expediente:

- Carrera: Secretaría y Dirección de carrera.
- Facultad: Secretaría abogada, Analista y Decanato.
- Propio: Estudiante, por destinatario (contrato existente).
- Administrador: todas las dirigidas a su cuenta.

Sin ámbito o fuera de él, el listado no las incluye y `marcar-leida` responde 404.

## Pruebas ejecutadas (resultados reales)

- Pruebas nuevas con la corrección: 63 pasaron. Sin la corrección: 48 fallan.
- `pytest src/apps src/core tests` (SQLite), base sin corrección: 889 pasaron, 13 omitidas.
- La misma suite con la corrección: 952 pasaron, 13 omitidas.
- PostgreSQL 16 desechable, `tests/` más las pruebas nuevas: 100 pasaron.
- Suites con RBAC o IDOR (12 archivos): 270 pasaron.
- `manage.py spectacular --validate`: el esquema generado coincide con `openapi.yaml`.
- Copia temporal de la integración `8e3935f` más esta corrección: 1040 pasaron, 14 omitidas.

## Riesgos residuales y decisiones pendientes

- **Copias DEC-04:** `declarar_aptitud` envía copia a los directores de toda la facultad, pero el RBAC de Dirección es de carrera. Esas copias de otra carrera quedan guardadas y no se muestran (5 en los datos locales). Falta decidir si se limita el envío a la carrera o se cambia la regla de visibilidad.
- **Solicitud de emisión:** `obtener_usuario_emisor` puede recurrir al primer usuario del rol, aunque sea de otro ámbito. Ese aviso no sería visible y la solicitud podría quedar sin atender.
- **Usuarios sin ámbito:** reciben 200 con lista vacía, aunque tengan avisos guardados. Es el comportamiento de mundo cerrado del filtro y requiere completar sus datos.

## Relación con otras entregas

Es independiente de BE-PA y de los bloques del dashboard. `views.py` es idéntico en `704d696` y `8e3935f`. El nuevo shell consulta notificaciones en cada página, por lo que esta corrección debe integrarse antes o junto con DS-C. La integración definitiva sigue pendiente de aprobación.

## Fuentes originales relacionadas

- `backend/src/core/adapters/scope_filter.py`
- `backend/src/apps/authentication/adapters/permissions.py` (`RBAC_MATRIX`, recurso `notificaciones`)
- `backend/src/apps/resoluciones/services/declarar_aptitud.py`
- `backend/src/apps/peticiones/services/solicitar_emision.py`
