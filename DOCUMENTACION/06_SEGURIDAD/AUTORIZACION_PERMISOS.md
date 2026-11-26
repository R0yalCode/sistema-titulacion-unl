---
title: "Autorización y permisos"
---

# Autorización y permisos — SGT-SIAAF

**Fuentes:** `backend/src/apps/authentication/adapters/permissions.py` (`RBAC_MATRIX`, verificado directamente en Fases 0 y 5), `backend/src/core/adapters/scope_filter.py`, `docs/06-seguridad/{autorizacion,roles-permisos}.md`, `docs/auditoria-backend/MATRIZ_PERMISOS_ROLES.md` (fuente más extensa, no se duplica aquí su contenido íntegro).

## 1. Modelo: RBAC de mundo cerrado

Toda autorización se evalúa contra `RBAC_MATRIX`: una tabla `recurso → método HTTP → {rol: scope}`. **Principio rector, verificado en código**: una celda vacía, o un recurso no declarado, deniega — no hay "permitido por omisión". Esto se aplica mediante `HasRolePermission` (clase DRF).

## 2. Scopes de ámbito (acceso por objeto, no solo por endpoint)

| Scope | Significado |
|---|---|
| `allow` | Paso libre a nivel de permiso (el `queryset` filtra después) |
| `own` | Solo objetos propios del usuario |
| `carrera` | Objetos de la carrera del usuario |
| `facultad` | Objetos de la facultad del usuario |
| `asignado` | Objetos donde el rol del usuario es la dependencia emisora |
| `borrador` | Solo operaciones en fase de borrador (uso: `ANALISTA_APOYO`) |
| `deny` | Denegado explícito |

Orden restrictivo documentado al acumular roles: `own > asignado > borrador > carrera > facultad > allow`.

## 3. Separación de responsabilidades por rol (verificada contra `RF-009`/`RN-004`)

- La emisión del informe legal (`SECRETARIO_ABOGADO`) y la declaratoria de aptitud (`DECANO`) son competencias mutuamente exclusivas en la matriz — ningún rol tiene ambas.
- `ANALISTA_APOYO` tiene scope `borrador` en checklist/informes: puede preparar pero no tiene autoridad de emisión final — consistente con su descripción en `specify.md` §6.1 ("prepara borradores... para revisión del jurista").
- `RESPONSABLE_DEPENDENCIA` tiene la bandeja denegada (su interacción es solo por peticiones asignadas a su rol, no por vista agregada).

## 4. Aislamiento de datos / protección IDOR

`ScopeFilterMixin` (`core/adapters/scope_filter.py`) traduce el scope efectivo del rol en filtros a nivel de ORM (`estudiante_id`/`carrera_id`/`facultad_id`). Los endpoints de detalle y acción usan `get_object_or_404(self.get_queryset())`: un objeto fuera de ámbito responde **404**, no 403 — decisión deliberada para no confirmar ni negar la existencia del objeto a un usuario no autorizado (semántica anti-enumeración). Casos con lógica de ámbito ampliada: descarga de documentos (soporte adicional de `asignado` para la dependencia emisora) y marcar-notificación-leída (doble verificación de propiedad).

## 5. Inconsistencia latente ya documentada por el equipo (no nueva de esta auditoría)

`docs/06-seguridad/autorizacion.md` señala: "el servicio de declaratoria admite Analista en código, pero la matriz RBAC lo deniega antes" (catalogada como `AUD-P2-07`, prioridad P2). No se reverificó el código del servicio línea por línea en esta pasada; se cita como hallazgo heredado pendiente, consistente con la práctica de esta auditoría de no asumir sin verificar pero tampoco de reinvestigar exhaustivamente todo lo ya catalogado por el equipo con buena evidencia.

## 6. Verificación declarada (pruebas)

Según `docs/06-seguridad/autorizacion.md`: 17 pruebas de la matriz RBAC (incluida una que verifica igualdad literal con la spec `specify.md` §6.2) + 13 pruebas de aislamiento IDOR a través de los 8 roles + 4 pruebas E2E. No se re-ejecutó la suite en esta Fase 6 (se hará de forma íntegra en la Fase 7, con resultado reproducible).

## 7. Consola Django Admin (ADR-0009)

Vía de acceso adicional fuera de la API REST: `/admin/`, restringida a usuarios `staff`/`superuser` por el framework de Django (sesión, no JWT). Documentada como "consola interna de soporte" en `urls.py` (comentario del código) y en `docs/01-introduccion/alcance.md` §"Dentro del alcance" ("Django Admin como consola de soporte, modelos de solo lectura"). No se verificó en esta pasada si los modelos están efectivamente registrados como solo-lectura en el admin (pendiente, no crítico para el alcance de esta fase).
