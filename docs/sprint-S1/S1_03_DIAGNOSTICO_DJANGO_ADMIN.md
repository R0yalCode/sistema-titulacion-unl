# S1-03 — DIAGNÓSTICO DE DJANGO ADMIN

**Fecha:** 02-nov-2026 · Inspección sin modificar ninguna configuración ni registro.

## 1. Estado actual (verificado)

| Punto de control | Estado | Evidencia |
| :--- | :--- | :--- |
| ¿Admin habilitado? | **NO** | `apps/` no incluye `django.contrib.admin` (ni `django.contrib.messages`) en `config/settings/base.py:15-28` |
| ¿`path('admin/', admin.site.urls)`? | **NO** | `config/urls.py` no contiene ruta admin |
| ¿Modelo de usuario personalizado? | **SÍ** | `class User(AbstractUser)` en `apps/authentication/adapters/models.py:86`; `AUTH_USER_MODEL = "authentication.User"` (`base.py:91`) con `cedula`, `carrera_id`, `facultad_id` y roles vía `UserRole` |
| ¿Existen `admin.py`? | **NO** | `glob backend/**/admin.py` → 0 archivos |
| ¿Modelos registrados? | **NO** | Ninguno |
| Contexto del contenedor | No es un cambio confirmable aún | auditoria previa `04_AUDITORIA_ARQUITECTONICA.md` A-08 menciona "Nginx… expone Django Admin (migración accidental)" — wording preventivo, noShipping evidencia de endpoint activo hoy |
| Posturas antagónicas en repositorio | Sí | `specify/tasks.md` §4.2 EXCLUYE "Django Admin como interfaz operativa expuesta por HTTP" del MVP; `plan.md` §10 incluye `Admin_Views` como adaptador de entrada |

**Conclusión:** Django Admin está *no-activo*. Activarlo requiere: añadir `django.contrib.admin` (+`messages`) a `INSTALLED_APPS`, middleware `Auth`/`MessageMiddleware` que hoy **no están en `MIDDLEWARE`** (`base.py:30-35`, solo Security/Sessions/Common/CSRF), y montar `admin.site.urls`. Son 3 cambios de configuración → **riesgo documentado** (ver `S1_06`).

## 2. Inventario real de modelos del dominio (nombres verificables)

| App (adapters) | Modelos |
| :--- | :--- |
| `authentication` | `User` (custom), `Role`, `UserRole` (+ `UserManager`) |
| `expedientes` | `ExpedienteTitulacion`, `HistorialEstado` |
| `peticiones` | `CatalogoDocumental`, `PeticionDocumental`, `DocumentoEntregado` |
| `verificacion` | `ChecklistVerification`, `ObservacionAccionable` |
| `resoluciones` | `InformeAptitud`, `DeclaratoriaAptitud` |
| `notificaciones` | `NotificacionInterna`, `EventoAuditoria` |

Total: **13 modelos**, todos con `db_table` explícito y consistencia/spec (7.1-7.7 de specify + User/Role/Role). No se inventan entidades.

## 3. Diseño administrativo propuesto (por modelo — propuesta, requiere aprobación)

> Todo esto pertenece a **S1-T04**. Django Admin es soporte interno; NO reemplaza API REST ni a React (`plan.md` §7, condición del paquete S1).

### 3.1 `User` (authentication)
- `list_display`: `username`, `get_full_name`, `cedula`, `carrera`, `facultad`, `is_active`.
- `search_fields`: `username`, `cedula`, `first_name`, `last_name`.
- `readonly_fields`: `last_login`, `date_joined`; `fieldsets` con redundancia de grupos default **oculta** (roles gestionados por `UserRole`, evitar doble canal de autorización).
- **Prohibido** listar/edición de nada sensible al password (no excluir `password` de admin base nativo, ni verbose adicional). Deshabilitar add/delete masivo si `Role`-seed es mandatorio (usar seed management command `seed_initial_data`).
- `inlines`: `UserRoleInline`, histórico de expedientes como solo lectura plegable (opcional).

### 3.2 `Role` / `UserRole`
- Tabla catálogo pequeña; solo lectura para no-supersuarios. `list_display` sin campos sensibles.

### 3.3 `ExpedienteTitulacion`
- `list_display`: `numero_expediente`, `estado`, `estudiante`, `carrera_id`, `fecha_recepcion`, `fecha_limite_atencion`, `activo`.
- `list_filter`: `estado`, `activo`, `carrera_id`; `search_fields`: `numero_expediente`, `estudiante__username`, `estudiante__cedula`.
- `readonly_fields`: `numero_expediente` (UK), `fecha_creacion`, `fecha_recepcion` (inmutable por RF-002), `fecha_limite_atencion` (calculada RF-003), `dias_laborables_acumulados`, `fecha_ultima_pausa`.
- `ordering`: `-fecha_creacion`; `date_hierarchy`: `fecha_creacion`.
- **No permitir** edición de `estado` desde el form (motor de estados controlado; las transiciones solo por servicios). Si corre, solo lectura + acciones administrativas a través de servicios de dominio si se justifica.
- `inlines`: `HistorialEstado` (solo lectura), `PeticionDocumental` (lectura), `ChecklistVerification` (lectura), `ObservacionAccionable` (lectura).
- `actions` restringidas; **desactivar eliminación** (`has_delete_permission=False` o límite superuser).

### 3.4 `HistorialEstado`
- Solo lectura (`readonly`, sin add/delete) — es bitácora inmutable (C-008).
- `list_display`: `expediente`, `estado_anterior`, `estado_nuevo`, `registrado_por`, fecha; `date_hierarchy`.

### 3.5 `CatalogoDocumental`
- Administrable por ADMINISTRADOR (permissions matrix): `list_display`, `search_fields codigo/nombre`, `list_filter fase/activo/es_obligatorio_base`.
- Permitir edición: catálogo es configurable por diseño (RNF/`ADMINISTRADOR` en matriz).

### 3.6 `PeticionDocumental` / `DocumentoEntregado`
- Peticiones: `list_display` expediente/requisito/estado/dependencia; filtro por estado; readonly `fecha_solicitud`, `fecha_actualizacion`. Estado solo por servicios, no form.
- Documentos: `hash_sha256`, `archivo_path`, `tamanio_bytes` **readonly** (integridad C-006, regla nº 1 del paquete). Sin acciones de reemplazo manual de `archivo_path`. `es_vigente` con queryset filter; **no exponer descarga directa del archivo** (no `admin link to file`): si se requiere verificación, se hace vía endpoint autorizado en la API.
- Eliminación prohibida (historial versionado N+1).

### 3.7 `ChecklistVerification` / `ObservacionAccionable`
- Read-only en estado normal; edición solo se permite vía servicios (controles de `evaluado_por`, firma de fecha). La auditoría admin SOLO lectura. `ObservacionAccionable.resuelta` NO editable a mano (la marca de resolución es consecuencia del subsanar, no un toggle).

### 3.8 `InformeAptitud` / `DeclaratoriaAptitud`
- **Solo lectura total** (inmutabilidad RN-004): no add, no change, no delete desde admin; `readonly_fields` = todos; método `has_add/change/delete_permission → False`.
- `list_display`: numero_providencia/memorando, expediente, dictamen, fecha; `search_fields` por número; `date_hierarchy`: fecha_emision/fecha_declaratoria. **NO hacer link directo al archivo** (paths parciales).
- Sin inlines que permitan mutaciones.

### 3.9 `NotificacionInterna`
- Read-only; `list_filter leida`, búsqueda por título/usuario; sin edición de mensajes (traceability).

### 3.10 `EventoAuditoria`
- **Bitácora inmutable, read-only y no-deletable** (RF-013, C-008): `has_add_permission=False` (se escribe por signals), `has_change/delete=False`.
- `list_display`: usuario, rol, acción, expediente, timestamp, IP; `list_filter` acción/rol; `search_fields` usuario/acción; `date_hierarchy`: timestamp. `detalles_json` readonly, **cuidado con datos sensibles** (passwords/tokens nunca logueados — validación de esta política en S1-T05).

## 4. Requisitos transversales para S1-T04 (derivados de reglas del paquete)

1. `hash_sha256` y métricas de archivos: solo lectura SIEMPRE.
2. Historial/bitácora (EventoAuditoria, HistorialEstado): inmutables, sin delete.
3. Estado de expedientes/verificaciones/documentos: nunca editable por form admin (transiciones controladas) - read-only o acciones que llamen servicios de dominio si se aprueban.
4. Ningún link público a archivos privados; solo paths parciales o sin link.
5. Permisos por perfil administrativo: Django staff+superuser controlado; no crear cuentas staff por defecto; seed command define quién.
6. Sin contraseñas ni tokens en listados (`list_diselect`: incluye exclusiones de campos sensibles).
7. Eliminación de expedientes: prohibida en admin (modificación con `get_actions` → escoja `"delete_selected"` removal en changuelist + `has_delete_permission=False`).
8. Trazabilidad de operaciones admin: hooks en `log_audit_event()`/signals donde el modelopor lo tenga; documentado como tarea de verificación, no introducir registro nuevo sin aprobación.

## 5. Entidades a admin-istrar — decisión y justificación

Recomendación por naturaleza del modelo:

| Modelo | ¿Admin? | Nivel | Justificación |
| :--- | :--- | :--- | :--- |
| User, UserRole | Sí (gestión de cuentas/roles; matriz §6.2 da a ADMIN "permitted" en creación/edición) | CRUD limitado | Función adm-otorgada |
| Role | Sí solo lectura | R | Catálogo seedeado |
| ExpedienteTitulacion | Sí (otorga soporte) | Read + corrección por servicio | Regla 3 |
| HistorialEstado | Solo lectura | R | Bitácora |
| CatalogoDocumental | Sí CRUD | CRUD | ADMIN tiene permiso en matriz |
| PeticionDocumental | Sí read | R+transición por servicio |
| DocumentoEntregado | Read-only o creación restringida | R | C-006 |
| ChecklistVerification | Read-only | R | Servicios control |
| ObservacionAccionable | Read-only | R | Subsanación es del circuito |
| InformeAptitud | Read-only total | R | RN-004 |
| DeclaratoriaAptitud | Read-only total | R | RN-004/DEC-04 |
| NotificacionInterna | Read-only | R |
| EventoAuditoria | Read-only estricto | R | C-008 |

**Todo lo anterior es propuesta:** nada registrado todavía, ningún cambio de settings/middleware.
