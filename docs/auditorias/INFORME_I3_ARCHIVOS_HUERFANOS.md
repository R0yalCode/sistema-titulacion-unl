---
title: "Informe I-3: archivos huérfanos en subsanación y carga de documentos"
subtitle: "Auditoría técnica sobre origin/main (3317231), 2026-11-12"
date: 2026-11-12
---

# Informe I-3: archivos huérfanos en subsanación y carga de documentos

> **Estado:** auditoría terminada; **sin cambios de código**. Las correcciones de §6 son propuestas pendientes de revisión y autorización. Origen: riesgo residual I-3 de PLB-E1-04 + O-2 ([PLAN_E1-04_O-2.md](../planificacion-backend/PLAN_E1-04_O-2.md) §10).

## 1. Alcance y archivos examinados

**Referencia:** `origin/main` = `3317231` (leído con `git show`; las reproducciones se ejecutaron sobre una exportación `git archive` de ese commit, sin modificar el repositorio).

| Capa | Archivo (en `backend/src/`) | Elementos |
|---|---|---|
| Vista | `apps/peticiones/adapters/views.py` | `PeticionViewSet.cargar_documento` (`POST /api/v1/peticiones/{id}/documento/`) |
| Vista | `apps/verificacion/adapters/views.py` | `ChecklistViewSet.subsanar` (`POST /api/v1/checklist/{id}/subsanar/`) |
| Servicio | `apps/peticiones/services/cargar_documento.py` | `execute()`, `_obtener_siguiente_version()` |
| Servicio | `apps/verificacion/services/subsanar_requisito.py` | `execute()`, `_get_siguiente_version()`, `_marcar_anterior_no_vigente()`, `_reanudar_plazo_y_cambiar_estados()` |
| Almacenamiento | `core/adapters/local_storage.py` | `PrivateMediaStorage`, `generar_ruta_archivo()`, `guardar_archivo_privado()`, `eliminar_archivo()` |
| Validación | `core/adapters/pdf_validation.py` | `validar_pdf_completo()` |
| Modelo | `apps/peticiones/adapters/models.py` | `DocumentoEntregado` (`UniqueConstraint(peticion, version)`) |
| Transiciones | `apps/expedientes/services/transiciones.py` | `registrar_transicion()` |
| Plazo | `apps/expedientes/domain/plazo_calculator.py` | `reanudar_reloj()` (idempotente sin pausa: no falla) |
| Django 5.2.19 | `django/core/files/storage/filesystem.py` | `FileSystemStorage._save()` |
| Configuración | `config/settings/base.py` | Sin `ATOMIC_REQUESTS` (la transacción del servicio es la externa) |

Fuera de alcance, ya cubiertos por D-6 (PLB-E1-04): informe y declaratoria (`emitir_informe`, `declarar_aptitud`), salvo lo indicado en H-I3-03.

## 2. Descripción de los flujos

### 2.1 Carga de documento (`cargar_documento.execute`)

Todo dentro de una `transaction.atomic()`:

1. Resuelve `expediente_id`; **bloquea expediente → petición** (`select_for_update`).
2. Valida estado de la petición y permisos.
3. `validar_pdf_completo()` (tamaño, *magic bytes*, SHA-256).
4. **`guardar_archivo_privado()` → escribe el archivo en disco** (`storage.save`).
5. Calcula la versión N+1; marca la anterior `es_vigente=False` (`UPDATE`).
6. `DocumentoEntregado.objects.create(...)`.
7. `peticion.save()` (estado `CARGADO`).
8. *Commit* al salir del bloque.

### 2.2 Subsanación (`subsanar_requisito.execute`)

Todo dentro de una `transaction.atomic()`:

1. Bloquea **expediente → petición → checklist**.
2. Valida estado del expediente (OBSERVADA), del ítem (OBSERVADO), permisos, petición OBSERVADO y observación pendiente.
3. `validar_pdf_completo()`.
4. Marca la observación como resuelta; calcula la versión; marca la anterior no vigente.
5. **`guardar_archivo_privado()` → escribe el archivo en disco.**
6. `DocumentoEntregado.objects.create(...)`; actualiza petición y checklist.
7. `_reanudar_plazo_y_cambiar_estados()` → **`registrar_transicion()`** (OBSERVADA → EN_VERIFICACION).
8. `NotificacionInterna.objects.create(...)`.
9. *Commit*.

### 2.3 Propiedad común

En ambos flujos el archivo se escribe **dentro** de la transacción pero **antes** de los pasos de base de datos que pueden fallar, y **no existe ninguna compensación**: si algo falla después del paso de escritura, la base de datos revierte y el archivo permanece. `eliminar_archivo()` existe en `local_storage.py` pero **no la usa ningún flujo** (verificado: ni `eliminar_archivo`, ni `.delete(`, ni `os.remove` aparecen en ambos servicios).

**Lo que sí está bien:**

- No hay **sobrescritura**: `FileSystemStorage._save` abre con `O_EXCL` y, si el nombre existe, usa `get_available_name()`; además el nombre lleva marca de tiempo.
- No hay **eliminaciones** de archivos en estos flujos: las versiones anteriores se conservan a propósito (`es_vigente=False`), referenciadas por su `DocumentoEntregado`.
- Las validaciones de negocio y del PDF ocurren **antes** de escribir: un rechazo normal no deja archivo (verificado).
- La concurrencia está serializada por el bloqueo del expediente (PLB-E1-04 + O-2, C6/C8): una segunda solicitud espera y, si debe fallar, falla en sus validaciones, antes de escribir.

## 3. Hallazgos y evidencia

Leyenda: **R** = reproducido con prueba; **T** = teórico (razonado, no reproducido).

| ID | Tipo | Hallazgo | Evidencia |
|---|---|---|---|
| **H-I3-01** | R | **Carga:** si cualquier paso de BD posterior a la escritura falla (`create`, `peticion.save`, *commit*), la transacción revierte y el archivo queda **huérfano**; la API responde 500 genérico | Fallo inyectado en `DocumentoEntregado.objects.create` y en `peticion.save`: `status=500`, `docs=0`, petición `PENDIENTE`, **1 archivo sin registro** en `expedientes/2026/<expediente>/…_doc.pdf` |
| **H-I3-02** | R | **Subsanación:** si falla un paso posterior a la escritura (`registrar_transicion`, notificación, *commit*), revierten el estado, la observación y el documento, pero el archivo queda **huérfano**. Con `TransicionNoPermitidaError` la API responde **400 `transicion_invalida`** (el cliente ve un rechazo limpio mientras el archivo permanece) | Inyección en `registrar_transicion`: `status=400`, expediente OBSERVADA, observación pendiente 1, **1 archivo nuevo sin registro**. Inyección en la notificación: `status=500`, mismo resultado |
| **H-I3-03** | R | **Escritura parcial:** si la escritura falla a mitad (disco lleno, E/S), Django no borra el fragmento (`_save` cierra el descriptor en `finally` sin eliminar). Queda un **archivo truncado** sin registro. Afecta a toda llamada a `guardar_archivo_privado()`, incluida `declarar_aptitud` (D-6 solo borra la ruta *devuelta*, que no existe si `save` falla) | `chunks()` que falla tras 20 bytes: `OSError` propagada, `docs=0`, **fragmento de 20 bytes** (archivo completo: 142) |
| **H-I3-04** | R (relacionado) | **Nombre multibyte largo:** `generar_ruta_archivo()` conserva caracteres Unicode (`isalnum()`); el upload se trunca a 255 *caracteres* pero el sistema de archivos limita a 255 *bytes*. Resultado: `OSError [Errno 36] File name too long` en `local_storage.py:75`, **500 genérico** sin mapear (no deja huérfano ni registro) | Nombre `"é"*200 + ".pdf"` → 420 bytes en disco → `status=500`, `archivos=[]`, `docs=0` |
| **H-I3-05** | R (relacionado) | **Reintento de carga:** repetir la misma carga (p. ej. tras un *timeout* del cliente) crea una **versión duplicada** con el mismo SHA-256 y otro archivo. No es huérfano (ambos referenciados), pero acumula copias | Dos POST iguales: `201, 201`; versiones `(1, h, no vigente)` y `(2, h, vigente)`, mismo hash; 2 archivos. En subsanación el reintento responde 400 **sin escribir** |
| **H-I3-06** | T | **Terminación del proceso** (SIGKILL, *timeout* del worker, caída) entre la escritura y el *commit*: archivo huérfano. Ninguna compensación en proceso puede cubrirlo | Razonamiento sobre el orden de pasos; no reproducido |
| **H-I3-07** | T | **Inverso (registro sin archivo):** el registro solo se confirma después de escribir, por lo que no se produce por los flujos. Podría ocurrir sin `fsync` (caída del sistema tras el *commit* con datos no volcados) o por borrado externo; la descarga lo detecta (404 si falta; 500 `documento_integridad_comprometida` si el contenido no coincide) | Razonamiento; la detección existe (INC-01) |
| **H-I3-08** | T | **Sin detección:** no hay herramienta para listar archivos del almacenamiento privado sin `DocumentoEntregado`/`InformeAptitud`/`DeclaratoriaAptitud`; los huérfanos (documentos con datos personales) quedan sin trazabilidad | `git ls-tree`: solo existe el comando `seed_initial_data` |

**Escenarios descartados (comprobados):** rechazo por PDF inválido o por estado → 400 sin archivo; subsanación repetida → 400 sin archivo; carga correcta → 0 huérfanos.

## 4. Escenarios reproducibles y pruebas propuestas

Reproducción ejecutada (scratchpad, no versionada): `test_i3_reproduccion.py`, 11 pruebas, **11 aprobadas** confirmando los hallazgos R contra `3317231`. Se propone convertirla en pruebas permanentes que **fallen hoy y pasen tras la corrección**:

| Prueba propuesta | Ubicación | Comprueba |
|---|---|---|
| `test_carga_fallo_tras_guardar_no_deja_huerfano[create, peticion_save, commit]` | `peticiones/tests/test_archivos_huerfanos.py` | BD revertida **y** 0 archivos no referenciados |
| `test_subsanar_fallo_tras_guardar_no_deja_huerfano[transicion, notificacion, commit]` | `verificacion/tests/test_archivos_huerfanos.py` | Ídem; observación sigue pendiente |
| `test_escritura_parcial_no_deja_fragmento` | `core/tests/test_local_storage.py` | Ningún archivo (ni parcial) tras `OSError` |
| `test_no_borra_archivos_preexistentes_ni_ajenos` | ídem | Centinelas (incluido uno con el mismo nombre base) intactos por SHA-256 |
| `test_nombre_multibyte_largo` | `peticiones/tests/` | Se almacena con nombre acotado en bytes (o error 4xx explícito, según decisión) |
| `test_conciliacion_lista_huerfanos_sin_borrar` | `core/tests/` | El comando informa huérfanos en modo lectura y solo borra con confirmación explícita |
| Fallo en *commit* real | `tests/integration/` (PostgreSQL) | Restricción diferida o `on_commit` que falla: sin huérfanos |

El *commit* fallido no es reproducible con SQLite (no hay restricciones diferidas); requiere PostgreSQL con la infraestructura de T3.

## 5. Riesgo e impacto

| ID | Probabilidad | Impacto | Nivel |
|---|---|---|---|
| H-I3-01 / H-I3-02 | Baja: requiere un fallo de BD o un error futuro posterior a la escritura | Documentos con **datos personales** retenidos sin registro ni trazabilidad; espacio; en H-I3-02 el usuario ve un 400 limpio mientras el archivo persiste | **Medio** |
| H-I3-03 | Baja (disco lleno, E/S) | Fragmentos corruptos sin registro | **Medio-bajo** |
| H-I3-04 | Media: nombres con tildes/ñ son habituales, pero hacen falta ~85+ caracteres multibyte | 500 genérico; el usuario no puede cargar | **Medio-bajo** (fuera del objetivo de I-3 pero en el mismo flujo) |
| H-I3-05 | Media (reintentos de red) | Duplicados, no huérfanos | **Bajo** |
| H-I3-06 | Baja | Huérfano no compensable en proceso | **Bajo**, requiere conciliación |
| H-I3-07 | Muy baja | Detectado en descarga | **Bajo** |
| H-I3-08 | — | Agrava H-I3-01…06: sin forma de encontrarlos | **Medio** |

## 6. Recomendación técnica por hallazgo

| ID | Recomendación |
|---|---|
| H-I3-01, H-I3-02 | **Compensación local, como D-6:** registrar la ruta devuelta por `guardar_archivo_privado()` y, si cualquier excepción sale del bloque atómico (incluido el *commit*), borrar **solo esa ruta** con `storage.delete()` y relanzar. Encapsularlo en un gestor de contexto reutilizable en `core/adapters/local_storage.py` (p. ej. `archivo_con_compensacion()`), usado por carga, subsanación y declaratoria. Mantener la invariante sin `ATOMIC_REQUESTS` (prueba ya existente en T4). Alternativa con menos ventana: mover la escritura al último paso posible, aunque la ruta se necesita para `create` |
| H-I3-03 | **Escritura atómica** en `guardar_archivo_privado()`: escribir en un temporal del mismo directorio y publicarlo con un enlace exclusivo (`os.link`, que falla si existe, y después `os.unlink` del temporal) o equivalente; ante error, borrar el temporal. Así nunca existe un archivo final parcial y se conserva la garantía de no sobrescritura |
| H-I3-04 | Acotar el nombre almacenado **en bytes** en `generar_ruta_archivo()` (truncado UTF-8 seguro, conservando la extensión), sin cambiar `nombre_original`. No cambia el contrato. Si se prefiere rechazar, requiere decisión: sería un 400 nuevo |
| H-I3-05 | Fuera de I-3: decidir si se quiere idempotencia (p. ej. rechazar o no versionar una carga con el mismo SHA-256 que la vigente). Requiere decisión funcional |
| H-I3-06, H-I3-08 | **Comando de conciliación** `reconciliar_archivos` (solo lectura por defecto): lista archivos del almacenamiento privado sin referencia en `DocumentoEntregado`, `InformeAptitud` y `DeclaratoriaAptitud`, con antigüedad mínima configurable para no tocar operaciones en curso; borrar solo con `--eliminar` explícito y registro de auditoría |
| H-I3-07 | Opcional: `fsync` del archivo y del directorio antes del *commit*. La detección (INC-01) ya existe |

## 7. Archivos que sería necesario modificar

| Archivo | Cambio | Hallazgos |
|---|---|---|
| `backend/src/core/adapters/local_storage.py` | Escritura atómica, nombre acotado en bytes, gestor de compensación | 01, 02, 03, 04 |
| `backend/src/apps/peticiones/services/cargar_documento.py` | Usar la compensación | 01 |
| `backend/src/apps/verificacion/services/subsanar_requisito.py` | Usar la compensación | 02 |
| `backend/src/apps/resoluciones/services/declarar_aptitud.py` | Opcional: migrar su compensación de D-6 al gestor común (sin cambiar comportamiento) | 03 |
| `backend/src/apps/<app>/adapters/management/commands/reconciliar_archivos.py` (nuevo; la app concreta se decide al implementar) | Conciliación | 06, 08 |
| Pruebas nuevas | §4 | Todos |

**No** requiere cambios en `permissions.py`, `TRANSICIONES_PERMITIDAS`, OpenAPI (salvo que H-I3-04 se resuelva con un 400 nuevo) ni migraciones.

## 8. Criterios de aceptación de I-3

1. Ninguna excepción posterior a la escritura (BD, transición, notificación, *commit*) deja archivos no referenciados en carga ni subsanación; pruebas de §4 en verde, incluida una con PostgreSQL.
2. Ningún fallo de escritura deja un fragmento parcial.
3. La compensación borra **solo** el archivo creado por la operación: archivos preexistentes (incluido el mismo nombre base) y ajenos intactos (SHA-256).
4. Un nombre de archivo multibyte largo no produce 500 genérico.
5. Existe un comando de conciliación de solo lectura por defecto que detecta huérfanos.
6. Sin regresiones: suite completa (las 13 de `pypdf` siguen siendo las únicas fallidas en SQLite), C1–C8 en PostgreSQL, contrato OpenAPI sin cambios no autorizados, SHA-256 de INC-01 intacta.
7. Sin cambios en permisos, transiciones ni contrato público, salvo decisión expresa.

## 9. Riesgos residuales

- **H-I3-06:** la terminación abrupta del proceso no se puede compensar en proceso; depende de la conciliación periódica.
- **Ventana entre *commit* y compensación:** si el *commit* tiene éxito y después falla algo fuera del bloque (p. ej. la serialización de la respuesta), el archivo es válido y queda referenciado: no es huérfano.
- **Conciliación y operaciones en curso:** borrar un archivo recién escrito cuya transacción aún no confirmó crearía el problema inverso; de ahí la antigüedad mínima y el modo lectura por defecto.
- **H-I3-05 y H-I3-04** dependen de decisiones funcionales si se opta por rechazar en lugar de normalizar.
- La reproducción usa inyección de fallos; los disparadores reales (caída de BD, disco lleno) no se provocaron.
