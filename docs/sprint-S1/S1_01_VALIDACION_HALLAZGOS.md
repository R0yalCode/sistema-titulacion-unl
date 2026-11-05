# S1-01 — VALIDACIÓN DE HALLAZGOS DE AUDITORÍA (NotebookLM)

**Proyecto:** SGT-SIAAF — backend (`backend/`)
**Sprint:** S1 (Estabilización del Backend y Django Admin)
**Fecha:** 02-nov-2026
**Alcance de este documento:** exclusively validación — NO se modificó código, configuración, migraciones, permisos ni pruebas.
**Fuente de hallazgos:** auditoría previa ("NotebookLM" / `auditoria/06_AUDITORIA_SEGURIDAD_Y_CALIDAD.md`, hallazgos SEC-01, SEC-02, SEC-03).
**Veredicto por cada ítem:** CONFIRMADO / PARCIALMENTE CONFIRMADO / NO VERIFICABLE, con evidencia puntual (archivo:línea) o salida de prueba.

---

## 0. Contexto metodológico

Toda afirmación de la auditoría previa fue verificada selectivamente sobre el repositorio, sin asumir la cifra "74 errores" ni su interpretación. Las pruebas se ejecutaron en dos escenarios:

- **Escenario A (container por defecto):** `DJANGO_SETTINGS_MODULE=config.settings.local` exportado en el contenedor Docker (`sistema_titulacion-backend-1`). Resultado: **50 failed, 390 passed, 24 errors** (464 tests).
- **Escenario B (settings de prueba correctos, sin modificar código):** `DJANGO_SETTINGS_MODULE=config.settings.test`. Resultado: **42 failed, 398 passed, 24 errors** (464 tests).

⚠️ El escenario evidencia que la suite *no corría* con `config.settings.test` como declara `pyproject.toml`: la variable de entorno del contenedor anula la opción `DJANGO_SETTINGS_MODULE` del ini (pytest-django no sobreescribe una variable ya presente). Ver `S1_02_DIAGNOSTICO_PRUEBAS.md`.

---

## 1. SEC-02 — Almacenamiento privado de resoluciones (`pdf_generator.py`)

### Veredicto: ✔ CONFIRMADO (y agravado por evidencia empírica)

| Comprobación | Resultado | Evidencia |
| :--- | :--- | :--- |
| ¿Existe la ruta hardcodeada? | Sí | `backend/src/apps/resoluciones/adapters/pdf_generator.py:48` — `self.output_dir = output_dir or "/media/private/resoluciones"` |
| ¿La ruta es absoluta en raíz del filesystem? | Sí | `/media` en la raíz `/` del contenedor, **no** bajo `MEDIA_ROOT` (`backend/src/media`, definido en `config/settings/base.py:87`) ni bajo `PRIVATE_MEDIA_ROOT` (variable que sí consume `PrivateMediaStorage` vía `getattr`, pero que ningún settings define) |
| ¿Se asegura en constructor? | Sí | `pdf_generator.py:49` — `os.makedirs(self.output_dir, exist_ok=True)` → en el contenedor lanza `PermissionError: [Errno 13] Permission denied: '/media/private'` (verificado en ejecución) |
| ¿Existe `PrivateMediaStorage`? | Sí, correcto y aislado | `backend/src/core/adapters/local_storage.py:16-35` (base `MEDIA_ROOT/private` o `PRIVATE_MEDIA_ROOT`, `base_url=None`, `url()` lanza `NotImplementedError`) |
| ¿Cómo se genera el PDF del informe #590? | Se escribe al directorio hardcodeado (fuera del storage privado) | `backend/src/apps/resoluciones/services/emitir_informe.py:178-187` — `PDFGeneratorAdapter()` sin `output_dir`, luego `archivo_informe_path=archivo_pdf` guarda la ruta absoluta del filesystem en BD (línea 195) |
| ¿Rutas privadas protegidas en descargas? | Sí para DocumentoEntregado | Descarga autorizada vía endpoint `PeticionViewSet.descargar_documento` (`urls.py:92-101`); `PrivateMediaStorage.base_url=None` y no existe ruta pública que sirva `/media/private/` |
| ¿Otras rutas hardcodeadas? | Sí — SOLO Una en código productivo; `tests` usan literales en fixtures | `pdf_generator.py:48` (única en producción). Literales en archivos de test: `test_models.py:98,207` (`"/media/private/expedientes/..."`, solo strings de fixture, inofensivas). **Adicional:** `declarar_aptitud.py:180` construye la ruta con f-string en lugar de `generar_ruta_archivo()` |

### Consecuencia probada
El defecto de SEC-02 rompe ~53-56 pruebas: `PDFGeneratorAdapter()` (invocado desde `emitir_informe.py:178`) y el *setup* de fixtures de `test_declarar_aptitud.py` fallan con `PermissionError` antes de llegar al objetivo del test. Es la **causa única** del bloque masivo de errores (detalle en `S1_02`).

### Riesgo adicional (nuevo, no estaba en el hallazgo)
Si en un entorno con permisos `root` la ruta se creara, resueluciones PDF quedarían en `/media/...` de la raíz del contenedor — por fuera del volumen `private_media` mapeado en `docker-compose.yml` → **pérdida de archivos al recrear contenedor**. ADR-005 / plan.md §19 exige `/workspace/backend/media/private/...` (en el repo: `MEDIA_ROOT/private`).

---

## 2. SEC-01 — Persistencia del PDF del memorando N.º 162 (`declarar_aptitud.py`)

### Veredicto: ✔ CONFIRMADO

| Comprobación | Resultado | Evidencia |
| :--- | :--- | :--- |
| ¿Existe `guardar_archivo_privado()`? | Sí | `backend/src/core/adapters/local_storage.py:51-79`. Firma: `guardar_archivo_privado(file: BinaryIO, expediente_id: str, nombre_original: str) -> str`. Guarda vía `PrivateMediaStorage.save()` y retorna ruta relativa a `MEDIA_ROOT/private`. Robusta: hace `seek(0)` antes y restaura posición después |
| ¿Ya es usada por otros casos de uso equivalentes? | Sí (regularidad del patrón) | `apps/peticiones/services/cargar_documento.py:17,122` y `apps/verificacion/services/subsanar_requisito.py:27,190` |
| ¿La declaración usa la función? | **NO** | `declarar_aptitud.py:176-181` crea el registro `DeclaratoriaAptitud` con `archivo_memorando_firmado_path=f"expedientes/{anio}/{id}/memorando_162_...pdf"` — **el archivo físico nunca se escribe en disco** |
| ¿Persistencia física? | **NO** | Ninguna llamada a storage en el caso de uso; todas las pruebas que llegan al `create` (que hoy solo pasan de setups fallidos) no pueden verificar durabilidad del archivo |
| ¿Registro en BD? | Parcial defectuoso | Se graba el registro con una ruta que **no existe en disco** → apuntador huérfano (punto crítico de integridad, C-006/RNF-004) |
| ¿Trazabilidad documental? | Parcial | Progresión de estados e `HistorialEstado` y notificaciones (DEC-04) sí se registran (líneas 183-197); pero no hay `hash_sha256` ni `tamanio_bytes` del memorando |
| ¿Controles de integridad? | Parcial no aprovechado | `validar_pdf_completo()` (`core/adapters/pdf_validation.py:111-118`) **sí** calcula y retorna `hash_sha256`, `tamanio_bytes`, `tipo_mime` — pero en `declarar_aptitud.py:167-169` el resultado se asigna a `metadata` y **se descarta, nunca se usa ni persiste** |
| ¿Se invoca la función sin validar contrato? | NO se invocó | Este documento solo audita el contrato y el flujo; la corrección se planifica en S1-T02 |

### Consecuencia probada
1. La declaratoria queda en BD con `archivo_memorando_firmado_path` inexistente: documento oficial se pierde al finalizar el flujo (fase DECLARADA_APTA).
2. Sin hash: no hay verificación de integridad subsecuente del memorando oficial firmado (contraste con `DocumentoEntregado.hash_sha256`, que sí existe para certificados).

### Nota de modelo
`InformeAptitud` y `DeclaratoriaAptitud` no tienen campos `hash_sha256`/`tamanio_bytes` (`apps/resoluciones/adapters/models.py`). El modelo conceptual ER de `plan.md` §12 tampoco los define para estos dos modelos (solo para `DocumentoEntregado`). **La corrección de minimos (persistir el archivo) no requiere migración; agregar hash sí** → derivar la decisión en S1-T02 con aprobación.

---

## 3. SEC-03 — Matriz RBAC del checklist (`permissions.py`)

### Veredicto: ✔ CONFIRMADO (clarificado: el alcance es mayor que solo Jurista/Apoyo)

| Comprobación | Resultado | Evidencia |
| :--- | :--- | :--- |
| Estructura real de `RBAC_MATRIX` | Dict `recurso → método → rol → scope/allow/deny` (mundo cerrado; ausencia = deny) | `backend/src/apps/authentication/adapters/permissions.py:24-110` |
| Roles soportados | 8 roles de specify.md §6.1 ( worldview completo en matriz de referencia de tests) | `tests/test_rbac_permissions.py:39-`, `specify.md §6.2` |
| `RBAC_MATRIX["checklist"]` | Define **PUT, PATCH, POST** — **NO tiene clave GET** | `permissions.py:77-93` |
| ¿Quién leería el checklist? | Todos los roles del flujo (HU-006/FL-03): jurista consulta `GET /api/v1/expedientes/{id}/checklist/` antes de evaluar; analista prepara borradores; decano revisa en su fase | `specify.md FL-03 paso 1, HU-006; urls.py:47-51` |
| ¿EFECTO en runtime? | `ChecklistListViewSet` (view GET de listado de checklist) usa `rbac_resource="checklist"` → `get_granted_scopes()` devuelve set vacío → `403` **para TODOS los roles, incluida JWT válida** | `verificacion/adapters/views.py:242-267`; `permissions.py:113-124,153-160` |
| ¿El hallazgo estaba acotado a Jurista y Apoyo? | PARCIAL: es correcto que a ellos se les deba conceder GET; pero el endpoint está **inoperante para cualquier rol** (mundo-cerrado accidental) | Contraste: los scopes GET para ESTUDIANTE/SECRETARIA/DECANO/DIRECTOR/ADMIN deben justificarse por ámbito paralel al recurso `expedientes:GET`, no por conveniencia |
| ¿La matriz literal de specify §6.2 define GET del checklist? | NO | La tabla §6.2 solo cubre `PUT/PATCH` para `/api/v1/checklist/{id}/`. **El GET de consulta no está en la matriz funcional**; su necesidad proviene de HU-006/FL-03 (pasos 1-2) |
| ¿Existen pruebas para cada combinación rol × método? | Parcial | `test_rbac_permissions.py` cubre exhaustivamente celdas PUT y su matriz literal propia (línea 90-101) también **sin GET** → la brecha está replicada en las pruebas; no hay test de consulta GET de checklist para ningún rol |

### Justificación de la concesión si se aprueba (propuesta, NO implementada)
La lectura del checklist es requisito previo de la evaluación (HU-006) y de la revisión de la declaratoria (FL-05 paso 1). Coherencia con aislamiento: scopes paralelos a `expedientes:GET` — `ESTUDIANTE: own`, `SECRETARIA_CARRERA: carrera`, `SECRETARIO_ABOGADO: facultad`, `ANALISTA_APOYO: facultad (borrador)`, `DECANO: facultad`, `DIRECTOR_CARRERA: carrera`, `ADMINISTRADOR: allow`, `RESPONSABLE_DEPENDENCIA: deny (no investigado aún; decidir en la tarea S1-T03)`.

> ⚠️ **No se concedió ningún permiso en esta fase.** La concesión y su prueba deben pasar por S1-T03 y aprobación previa (ver `S1_04`, exclusión E3).

---

## 4. Síntesis

| Hallazgo | Veredicto | Causa raíz única en código | Prioridad propuesta |
| :--- | :--- | :--- | :--- |
| SEC-02 ruta hardcodeada `/media/private/resoluciones` | CONFIRMADO | `pdf_generator.py:47-50` | **Crítica** |
| SEC-01 PDF memorando 162 no persistido (sin `guardar_archivo_privado`) | CONFIRMADO | `declarar_aptitud.py:167-181` | **Crítica** |
| SEC-03 sin `GET` en `RBAC_MATRIX["checklist"]` | CONFIRMADO (alcance mayor: endpoint GET inoperante para todos los roles) | `permissions.py:77-93` + `views.py:250` | **Alta** |

**Ningún hallazgo fue desmentido.** SEC-03 se confirma con alcance ampliado. Se añaden 6 problemas nuevos documentados en `S1_02` y `S1_06`.

---

## 5. Contradicciones documentales detectadas (a resolver antes de codificar)

| # | Contradicción | Referencias |
| :--- | :--- | :--- |
| C1 | El paquete S1 pide **implementar Django Admin**; `tasks.md` §4.2 excluye explícitamente *"Habilitación de Django Admin como interfaz operativa expuesta por HTTP"*; y no existe `constitution.md` contra la cual cotejar | `sgt-siaaf/specs/001-tramite-titulacion/tasks.md` §4.2; `plan.md` §10 (incluye `Admin_Views` como adaptador de entrada: ambiguo) |
| C2 | `constitution.md` v2.0.0 es **norma suprema** en la jerarquía declarada por plan.md/tasks.md §1, pero **el archivo no existe en el repositorio** (`specify.md`, `clarify.md`, `plan.md` y `tasks.md` tienen referencias constantes) | Búsqueda `**/constitution*.md` → 0 resultados |
| C3 | `specify.md` §6.2 y matriz RBAC restringen `/declaratorias/` POST a `DECANO`; pero el servicio permite también `ANALISTA_APOYO` (comportamiento + test que lo asume: `test_analista_apoyo_puede_registrar`) | `declarar_aptitud.py:123-127`; `permissions.py:101-105`; `specify.md §6.2` |
| C4 | Notificaciones del MVP: `clarify`/`plan` dicen 100% in-app; `specify.md` §5.3.5 menciona "correos opcionales vía SMTP" (ambigüedad menor; in-app es lo implementado y correcto) | `specify.md:130` |
