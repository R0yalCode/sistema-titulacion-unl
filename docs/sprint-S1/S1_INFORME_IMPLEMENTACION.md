# S1 · Informe de Implementación

**Proyecto:** SGT-SIAAF (Sistema de Gestión de Titulación)
**Sprint:** S1 — Estabilización y consola interna
**Fecha:** 2026-11-02
**Base normativa:** Constitución v2.1 (con ADR-0009), plan.md, S1_01–S1_06

---

## 1. Alcance ejecutado

| Tarea | Estado | Resumen |
|---|---|---|
| S1-T01 Diagnóstico y validación | ✅ | Ver los informes S1_01–S1_06 |
| S1-T02 SEC-01/SEC-02 almacenamiento y persistencia | ✅ | Corregidos y validados con el suite |
| S1-T03 SEC-03 permisos RBAC del checklist | ✅ | GET añadido a la matriz con privilegio mínimo |
| S1-T04 Django Admin (Bloques A, B, C) | ✅ | Configurado, registrado y con smoke tests |
| S1-T05 Suite de regresión (escenarios A y B) | ✅ | Sin regresiones nuevas; fallas restantes documentadas |
| S1-T06 Preparación para React | ℹ️ | No requiere cambios de código; ver §8 |

---

## 2. Correcciones de seguridad y persistencia

### SEC-02 — Ruta privada fuera del sandbox (`pdf_generator.py`)

- **Hallazgo:** `adapters/pdf_generator.py:48` fijaba `/media/private/resoluciones` (raíz del filesystem) → `PermissionError: [Errno 13]` y ~53 fallas en el suite.
- **Corrección:** el adaptador resuelve su raíz con el helper `_raiz_almacenamiento_privado()`, que usa `settings.PRIVATE_MEDIA_ROOT` y, en su defecto, `MEDIA_ROOT/private`. El directorio por defecto pasa a ser `<raíz privada>/resoluciones`.
- **Resultado:** todos los tests de generación (emisión de informe, providencia 590, memorando 162) vuelven a ejecutarse contra almacenamiento privado válido.

### SEC-01 — `DeclaratoriaAptitud` sin archivo persistido (`declarar_aptitud.py`)

- **Hallazgo:** el servicio registraba `archivo_memorando_firmado_path` sin guardar el archivo del memorando firmado.
- **Corrección:** antes de crear la `DeclaratoriaAptitud`, el servicio persiste el archivo con `guardar_archivo_privado(archivo_memorando, str(expediente.id), nombre_original=...)` (adapters/local_storage.py:51), con nombre `memorando_162_{numero}.pdf` normalizado. Un fallo de E/S eleva `PDFInvalidoError(code="storage_error")` y no queda registro huérfano.
- **Resultado:** la ruta almacenada apunta a un archivo real en el almacenamiento privado; el test de persistencia (`assert .endswith(".pdf")`) pasa.

### Nota de integridad (opcional, pendiente de aprobación)

`validar_pdf_completo()` calcula `hash_sha256/tamanio_bytes/tipo_mime` de los archivos cargados, pero el modelo no tiene columnas para persistirlos. Añadirlas exige una migración a `InformeAptitud`/`DeclaratoriaAptitud`, que queda fuera del alcance aprobado de S1 (C-11). Queda como decisión pendiente P2.

---

## 3. SEC-03 — Permisos RBAC del checklist

- **Hallazgo:** `RBAC_MATRIX["checklist"]` no tenía clave `GET`; el `ChecklistListViewSet` quedaba denegado para todos los roles (mundo cerrado).
- **Corrección (privilegio mínimo, literal 6.2):**

| Rol | GET | POST | PATCH | PUT | DELETE |
|---|---|---|---|---|---|
| SECRETARIO_ABOGADO | `SCOPE_FACULTAD` | ALLOW | DENY | DENY | DENY |
| ANALISTA_APOYO | `SCOPE_FACULTAD` | ALLOW | DENY | DENY | DENY |
| ADMINISTRADOR | ALLOW | ALLOW | DENY | DENY | DENY |
| ESTUDIANTE / DECANO / RESPONSABLE_DEPENDENCIA | DENY | — | — | — | — |

- **Verificación:** la matriz codificada se ejecuta contra el literal `MATRIZ_62_LITERALS` actualizado; el test de mundo cerrado (`get_scope` RESP_EXTERNO == DENY) se extiende al checklist GET. `test_rbac_permissions.py` pasa 100 %.

---

## 4. Django Admin — Bloques A, B, C (S1-T04)

**Aprobación:** ADR-0009; Constitución v2.1 reescribe P-18 como *aprobada con controles* (consola interna de administración y soporte).

### Bloque A — Configuración base

- `INSTALLED_APPS`: añadidos `django.contrib.admin` y `django.contrib.messages`.
- `MIDDLEWARE`: añadidos `AuthenticationMiddleware` y `MessageMiddleware` (`settings/base.py`).
- `urls.py`: montado `admin/` al inicio del árbol de URLs.

### Bloque B — Registros por app

| App | Modelos | Política |
|---|---|---|
| authentication | User (admin personalizado con inline de roles), Role, UserRole | Role/UserRole solo lectura; Username bloqueado en edición |
| expedientes | ExpedienteTitulacion (+ inline HistorialEstado), HistorialEstado | Estado, numeración y fechas solo lectura; sin agregar ni eliminar |
| peticiones | CatalogoDocumental (editable, sin eliminar), PeticionDocumental / DocumentoEntregado (solo consulta; hash, path y tamaño bloqueados) | — |
| verificacion | ChecklistVerification, ObservacionAccionable | Solo consulta total; estados solo via servicios |
| resoluciones | InformeAptitud, DeclaratoriaAptitud | Inmutables de fábrica: solo changelist y detalle |
| notificaciones | NotificacionInterna (solo consulta), EventoAuditoria | Bitácora P-08: estricto read-only sin delete |

Acciones masivas (`actions = None`) deshabilitadas en todos los registros para evitar modificaciones en lote sobre el dominio.

### Bloque C — Smoke tests

`src/apps/authentication/tests/test_django_admin.py`: 4 pruebas (index, 13 changelists, bloqueo de "add" en modelos inmutables, pantalla de usuarios personalizada) — **4/4 pasan**.

---

## 5. Resultados del suite completo (473 pruebas)

| Escenario | Comando | Passed | Failed |
|---|---|---|---|
| **A** — env por defecto (PostgreSQL) | `python -m pytest -q` | 452 | 21 |
| **B** — `config.settings.test` (sqlite) | `python -m pytest -q` con `DJANGO_SETTINGS_MODULE=config.settings.test` | 460 | 13 |
| Objetivo de correcciones | `test_rbac_permissions.py`, `test_declarar_aptitud.py`, `test_emitir_informe.py`, `test_resoluciones_and_pdf_generation.py`, `test_django_admin.py` | 117/117 | 0 |

### Clasificación de las fallas restantes (preexistentes, fuera de alcance)

1. **`pypdf` ausente en requirements (13 por escenario):** el helper `_leer_pdf_texto` (test_pdf_generator.py:22) silencia el ImportError y devuelve "" — los asserts de texto fallan. Los PDFs se generan correctamente (tamaño > 0). **Acción propuesta:** añadir `pypdf` a requirements-dev.txt. Pendiente de aprobación.
2. **Introspección `sqlite_master` sobre PostgreSQL (8, solo escenario A):** `test_auditoria.py`, `test_notification_service.py`, `test_notifications_and_audit.py`, `resoluciones/test_models.py` consultan `sqlite_master` directamente. No es regreso de S1. **Acción propuesta (P2):** reescribir los índices/constraints usando `Meta`/in `_meta` o SQL portátil.

### Incremento del total de pruebas

El total pasó de 464 a 473 pruebas colectadas: +4 son los smoke tests nuevos del Admin; el resto corresponde a `core/tests/test_notifications_and_audit.py`, que ahora se colecta al haberse añadido `core/tests/__init__.py` (antes colisionaba con `apps/notificaciones/tests/test_notifications_and_audit.py` por basename sin marcador de paquete y provocaba error de import mismatch durante la colección). No se añadieron ni debilitaron tests de negocio.

---

## 6. Cambios aplicados (inventario)

| Archivo | Tipo | Contenido |
|---|---|---|
| `backend/src/apps/resoluciones/adapters/pdf_generator.py` | EDICIÓN | helper `_raiz_almacenamiento_privado()` + exportación por defecto de ruta privada |
| `backend/src/apps/resoluciones/services/declarar_aptitud.py` | EDICIÓN | persistencia real del memorando con `guardar_archivo_privado()` |
| `backend/src/apps/authentication/adapters/permissions.py` | EDICIÓN | añadir GET al checklist en RBAC_MATRIX |
| `backend/src/apps/authentication/tests/test_rbac_permissions.py` | EDICIÓN | literal 6.2 GET, PARAMETROS_CELDAS y mundo cerrado |
| `backend/src/apps/authentication/adapters/admin.py` | NUEVO | registros de Admin para autenticación |
| `backend/src/apps/expedientes/adapters/admin.py` | NUEVO | Expediente + Historial (inline read-only) |
| `backend/src/apps/peticiones/adapters/admin.py` | NUEVO | catálogo editable + peticiones/documentos solo lectura |
| `backend/src/apps/verificacion/adapters/admin.py` | NUEVO | checklist y observaciones solo consulta |
| `backend/src/apps/resoluciones/adapters/admin.py` | NUEVO | resoluciones inmutables |
| `backend/src/apps/notificaciones/adapters/admin.py` | NUEVO | notificaciones + auditoría read-only |
| `backend/src/apps/authentication/tests/test_django_admin.py` | NUEVO | 4 smoke tests del admin |
| `backend/src/core/tests/__init__.py` | NUEVO | marcador de paquete para resolver colisión de basename en la colección |
| `backend/src/config/settings/base.py` | EDICIÓN | apps admin/messages + middlewares auth/message |
| `backend/src/config/urls.py` | EDICIÓN | ruta `/admin/` |
| `Dockerfile` | EDICIÓN | `COPY backend/pyproject.toml ./` para que pytest en el contenedor resuelva la configuración del suite |
| `sgt-siaaf/specs/.../constitucion.md` | NUEVO | Constitución v2.1 (P-18 aprobada con controles) |
| `backend/docs/adr/0009-django-admin-consola-interna.md` | NUEVO | ADR-0009 formal |

**No se debilitó ni eliminó ningún test.** No hay migraciones sin aprobar; no hay secretos en el repo.

---

## 7. Riesgos y limitaciones remanentes

1. **Variable de entorno del contenedor:** compose fija `DJANGO_SETTINGS_MODULE=config.settings.local`, que eclipsa la configuración de pytest al correr el escenario A; allí se cargan settings "local" y aparecen 8 fallas adicionales de introspección (`sqlite_master` sobre PostgreSQL). No es un bug del código de dominio — el escenario B demuestra que todo el negocio pasa con settings de test. Recomendación: inyectar la variable al ejecutar pytest (`docker exec -e DJANGO_SETTINGS_MODULE=config.settings.test ...`) o ajustar compose para CI.

2. **`pypdf` faltante** (requiere añadir a `requirements-dev.txt`).
3. **Contradicción C-03:** `declarar_aptitud` permite `ANALISTA_APOYO` a nivel de servicio, mientras la matriz oficial restringe a `DECANO` — se abordará en futura tarea (no es un defecto de administración).
4. **Bug N-1:** `emitir_informe.py:206-211` calcula `estado_anterior` a partir del estado correcto tras emitir el informe — revisar en fase de auditoría de flujo (no corregido en S1 para no alterar lógica de dominio aprobada).

---

## 8. Conclusión S1-T05/T06

- El backend queda estabilizado y preparado para el desarrollo del frontend React sobre una API saneada: las resoluciones escriben dentro del sandbox de almacenamiento privado, y los permisos del checklist se aplican por RBAC con privilegio mínimo según el literal 6.2.
- La consola interna (Django Admin) está operativa y alineada con la Constitución v2.1: solo lectura para estados, resoluciones, auditoría y hash; edición reservada al catálogo documental y gestión de usuarios.
- Pendientes para próximas tandas (P2): añadir `pypdf` a requirements-dev, migración de `hash_sha256` para trazabilidad documental, reescritura portable de tests de introspección, bug N-1 y la contradicción C-03.

---

*Informe de cierre del Sprint S1 bajo el flujo Spec-Driven Development (SDD).*
