---
title: "Auditoría independiente de I-3"
subtitle: "Rama fix/i3-archivos-huerfanos (2764d12) frente a origin/main (3317231), 2026-11-12"
date: 2026-11-12
---

# Auditoría independiente de I-3

> **Dictamen vigente (tras las correcciones, §10): APROBADA CON OBSERVACIONES.**
> Dictamen inicial sobre `2764d12` (§1–§9, conservado sin cambios): NO APROBADA PARA INTEGRACIÓN.

## 1. Alcance y metodología

- **Objeto:** rama `fix/i3-archivos-huerfanos` = `2764d12` (local = `origin`), base `origin/main` = `origin/develop` = `3317231`.
- **Declaración de independencia:** el código auditado fue implementado por la misma herramienta (Claude Code) en modalidad centralizada; la auditoría **no es independiente en sentido estricto**. Para compensarlo no se reutilizaron las pruebas de la rama como evidencia principal: se revisó el código línea a línea y se escribieron **12 pruebas adversariales nuevas** (A1–A12, en el scratchpad, no versionadas) que buscan romper la implementación.
- **Entorno:** todas las ejecuciones sobre una exportación `git archive` de `2764d12` (estado commiteado, sin el árbol de trabajo); PostgreSQL 16.15 en contenedor desechable; SQLite en memoria; Django 5.2.19.
- **Solo lectura:** sin cambios de código, commits, push ni integraciones. Único archivo creado: este informe (sin commitear).

## 2. Commits revisados

| Commit | Tipo | Autor | Committer | Archivos | Coherencia con la tarea |
|---|---|---|---|---|---|
| `647c258` | Informe I-3 | R0yalCode | R0yalCode | 1 | ✔ documental autorizado |
| `070ed29` | T1 | JJOC3S | R0yalCode | 2 | ✔ |
| `082c886` | T2 | JuanCalopinoo | R0yalCode | 2 | ✔ |
| `9e004f0` | T3 | 7777-C | R0yalCode | 2 | ✔ |
| `86acce6` | T4 | Dan1el17 | R0yalCode | 2 | ✔ |
| `2764d12` | T5 | R0yalCode | R0yalCode | 9 | ✔ (código, pruebas y cierre documental) |

`origin/main..fix`: 17 archivos, +1780/−119. **Sin cambios** en `permissions.py`, `transiciones.py`, `openapi.yaml`, migraciones ni archivos locales ajenos (`entrypoint.sh`, `DISENO_FUNCIONAL…`, borrados de `docs/`).

## 3. Hallazgos por tarea

### T1 — `core/adapters/local_storage.py`

| Aspecto | Resultado | Evidencia |
|---|---|---|
| Temporal en el mismo directorio y publicación atómica | ✔ `mkstemp(dir=destino)` + `os.link` (falla si existe) o reserva `O_EXCL` + `os.replace` | Revisión; prueba de ruta sin enlaces |
| Sin sobrescritura | ✔ | A2: 16 escrituras simultáneas con el mismo nombre y segundo → 16 archivos únicos, contenidos correctos, sin temporales |
| Limpieza del temporal ante excepción | ✔ (`finally`) | A5 (subsanación) y prueba de T1 |
| Límite en bytes, extensión y `nombre_original` | ✔ 180 B, extensión ≤ 16 B, sin partir UTF-8 | Pruebas de T1/T2 |
| Subidas grandes (`TemporaryUploadedFile`, > 2,5 MB) | ✔ | A4: 3 MB → 201, bytes idénticos, SHA-256 registrado correcto, descarga 200 |
| Compensación aislada entre operaciones | ✔ | A3: A falla y B termina a la vez → solo queda el archivo de B, íntegro |
| Fallo de *commit* | ✔ | Pruebas PostgreSQL de carga y subsanación; A12 declaratoria |
| **Fallo después de publicar** | ✘ **D-05** | A1 |
| Permisos de directorio | ⚠ **D-08** | Revisión |

### T2 — carga, T3 — subsanación

✔ Toda escritura pasa por `archivos.guardar()` dentro de `compensacion_de_archivos()`, que envuelve la transacción (cubre el *commit*). Las excepciones se propagan (las vistas mantienen 400/500). Versiones anteriores intactas (SHA-256). Transiciones y notificaciones sin cambios de comportamiento (las pruebas de E1-04 y C1–C8 siguen en verde). **H-I3-05** sigue creando versiones duplicadas (prueba dedicada en verde).

### T4 — declaratoria

✔ Usa el gestor común; conserva la conversión `OSError → PDFInvalidoError(storage_error)`; el comportamiento de D-6 se mantiene (pruebas de E1-04 en verde). A12 (PostgreSQL): con *commit* fallido no queda memorando ni declaratoria.

### T5 — `reconciliar_archivos`

| Requisito | Resultado | Evidencia |
|---|---|---|
| Solo lectura por defecto | ✔ | Pruebas de T5 |
| Eliminación solo con `--eliminar --confirmar` | ✔ | Pruebas de T5 |
| No sale de `PRIVATE_MEDIA_ROOT`; no sigue enlaces | ✔ | Revisión (`os.walk(followlinks=False)`, `is_symlink`, comprobación de `parents`); A11: el destino externo queda intacto |
| Normalización de rutas | ✘ **D-01** | A7 |
| Protección de recientes | ⚠ **D-03** | A10 |
| Borradores no se borran | ✔ | Pruebas de T5 |
| Registro de eliminaciones | ✔ (`logger.warning`) | Demostración y revisión |
| Nunca borra un archivo referenciado | ✘ **D-01** | A7 |
| Una consulta o configuración errónea no provoca eliminaciones inseguras | ✘ **D-02** | A9 |
| Robustez y completitud del informe | ✘ **D-04**, ⚠ **D-06** | A6, A11 |

## 4. Defectos

| ID | Severidad | Defecto | Evidencia | Corrección (archivo) |
|---|---|---|---|---|
| **D-01** | **Importante — bloquea integrar** | `rutas_referenciadas()` solo resuelve rutas absolutas para `InformeAptitud`; en `DocumentoEntregado` y `DeclaratoriaAptitud` un valor absoluto (o con `..`) se "normaliza" quitando la `/` inicial, no coincide y el archivo **referenciado** se clasifica como huérfano | **A7:** documento con `archivo_path` absoluto → `referenciados=0, huerfanos=1`; con `--eliminar --confirmar` **se borra el archivo referenciado**. Hoy no hay datos así (el historial solo guardó rutas relativas), pero el comando debe ser seguro ante datos importados o editados | `reconciliar_archivos.py`: normalizar **todas** las referencias igual (absoluta → `resolve()` y `relative_to(raiz)`; relativa → `normpath`; lo que salga de la raíz va a `referencias_fuera_de_raiz`), con prueba de ruta absoluta y con `..` |
| **D-02** | **Importante — bloquea integrar** | Sin salvaguarda ante una base sin referencias o equivocada (configuración errónea, base vacía o restaurada): todo se clasifica como huérfano y se borra | **A9:** base sin referencias y 3 archivos antiguos → `--eliminar --confirmar` borró **3 de 3** | `reconciliar_archivos.py`: negarse a borrar si no hay ninguna referencia y existen candidatos (o si los candidatos superan un umbral) salvo opción explícita adicional; mostrar el total antes de borrar. Prueba |
| **D-03** | **Importante** | `--antiguedad-minima-horas 0` (o muy baja) permite borrar archivos de operaciones en curso cuya transacción aún no confirmó → registro sin archivo (H-I3-07 provocado) | **A10:** archivo recién escrito eliminado con `0` | `reconciliar_archivos.py`: exigir un mínimo para `--eliminar` (p. ej. ≥ 1 h) y rechazar valores menores. Prueba |
| **D-04** | Menor | Raíz privada inexistente (instalación nueva) → `KeyError: 'referencias_fuera_de_raiz'` en modo texto | **A6** (línea 196) | `reconciliar_archivos.py`: inicializar la clave antes del retorno anticipado o informar "raíz inexistente". Prueba |
| **D-05** | Menor | Si un paso **posterior a publicar** falla (`os.chmod`, o el `unlink` del temporal con un error distinto de `FileNotFoundError`), la excepción sale sin devolver la ruta: el archivo publicado no queda registrado en la compensación → huérfano | **A1:** `chmod` fallido → 1 archivo final sin registro tras la compensación | `local_storage.py` (`_escribir_atomico`): si falla algo después de publicar, borrar el destino publicado antes de relanzar. Prueba |
| **D-06** | Menor | El informe del comando omite los directorios enlazados (`os.walk` no los recorre ni los lista) y los subdirectorios ilegibles (errores de `os.walk` ignorados): el resultado puede ser incompleto sin avisarlo. No provoca borrados inseguros | **A11** | `reconciliar_archivos.py`: listar directorios enlazados y registrar errores con `onerror`. Prueba |
| **D-07** | Observación | El comando no informa de **referencias sin archivo** (H-I3-07); existió código histórico de declaratoria que construía la ruta sin guardar el archivo | Historial (`f45717e`) | Opcional: categoría `referencias_sin_archivo` (solo informe) |
| **D-08** | Menor | `_escribir_atomico` crea directorios con `os.makedirs` sin aplicar `storage.directory_permissions_mode` (Django sí lo aplicaba). Hoy no hay efecto: `FILE_UPLOAD_DIRECTORY_PERMISSIONS` no está configurado | Revisión | `local_storage.py`: respetar `directory_permissions_mode` |

No se encontraron defectos en T2, T3 ni T4.

## 5. Resultados de pruebas (exportación de `2764d12`)

| Ámbito | Resultado |
|---|---|
| `pytest` (SQLite) | 625 aprobadas, 13 fallidas: **las mismas 13 de `pypdf`** (lista idéntica a la línea base; 30/30 con lector `pdftotext`) |
| `src/core` + `tests/` (SQLite) | 127 aprobadas, 12 omitidas (`postgres`) |
| PostgreSQL 16.15, `-m postgres tests/integration` | 12/12 (C1–C8, infraestructura, *commit* fallido en carga y subsanación) |
| PostgreSQL, `tests/` | 36/36 |
| PostgreSQL, `src/apps` | 21 fallos: **los mismos conocidos** (13 `pypdf` + 8 H-30) |
| Log de PostgreSQL | Sin interbloqueos; solo los errores esperados (`IntegrityError` provocados en `test_models.py`, `sqlite_master` de H-30, `nowait` de infraestructura) |
| OpenAPI | `spectacular --validate` sin errores; `openapi.yaml` **sin diferencias** |
| flake8 (archivos nuevos) | Limpio |
| Adversariales A1–A12 | Correctas: A2, A3, A4, A5, A8, A12. Defectos: A1 (D-05), A6 (D-04), A7 (D-01), A9 (D-02), A10 (D-03), A11 (D-06) |

Ningún fallo nuevo en las suites del proyecto.

## 6. Riesgos residuales

- H-I3-07 (registro sin archivo por caída sin volcado o borrado externo): sin detección en el comando (D-07); la descarga lo detecta.
- Terminación del proceso entre escritura y *commit*: la cubre la conciliación (cuando D-01…D-03 estén corregidos).
- Servicio invocado dentro de otra transacción que revierte después: archivo sin registro, detectable por la conciliación.
- H-I3-05: fuera de alcance (decisión funcional).

## 7. Cumplimiento de DK-010

- Cinco commits de implementación, uno por tarea, con el `--author` del reparto autorizado y solo archivos de su bloque; línea de modalidad en cada cuerpo; sin menciones a IA ni coautorías; committer R0yalCode. ✔
- Constancia documental de la ejecución centralizada (informe §10 y bitácora). ✔
- **Pendiente:** no hay evidencia de que JJOC3S, JuanCalopinoo, 7777-C y Dan1el17 hayan sido informados de su atribución delegada (requisito de "conocimiento" de DK-010), igual que en E1-04.

## 8. Comparación con los criterios de aceptación (informe I-3 §8)

| # | Criterio | Estado |
|---|---|---|
| 1 | Sin huérfanos tras fallos posteriores a la escritura (incl. PostgreSQL) | ✔ (salvo el caso límite D-05) |
| 2 | Sin fragmentos parciales | ✔ |
| 3 | Compensación solo de lo propio; preexistentes y ajenos intactos | ✔ |
| 4 | Nombre multibyte largo sin 500 | ✔ |
| 5 | Comando de conciliación de solo lectura por defecto | ✔ lectura; ✘ eliminación insegura (D-01, D-02, D-03) |
| 6 | Sin regresiones | ✔ |
| 7 | Sin cambios en permisos, transiciones ni contrato | ✔ |

## 9. Dictamen

**NO APROBADA PARA INTEGRACIÓN.**

Motivo: el modo `--eliminar --confirmar` de `reconciliar_archivos` puede borrar documentos **referenciados** (D-01) y borra todo ante una base sin referencias (D-02), incumpliendo los requisitos explícitos de seguridad de la conciliación; además permite borrar archivos de operaciones en curso (D-03). El resto de la rama (T1–T4) es correcto y está verificado.

**Para aprobarla basta con:**

1. `backend/src/apps/peticiones/adapters/management/commands/reconciliar_archivos.py`: D-01, D-02, D-03 (obligatorios) y D-04, D-06 (recomendados).
2. `backend/src/core/adapters/local_storage.py`: D-05 (recomendado) y D-08 (opcional).
3. Pruebas en `backend/src/apps/peticiones/tests/test_reconciliar_archivos.py` y `backend/src/core/tests/test_local_storage.py` que reproduzcan A1, A6, A7, A9, A10 y A11 (en rojo antes de corregir).
4. Repetir la regresión completa (SQLite + PostgreSQL).

Alternativa si se quiere integrar antes: deshabilitar `--eliminar` (dejar el comando solo de lectura) hasta corregir D-01…D-03; requiere decisión del responsable.

Según DK-010, las correcciones corresponderían a los responsables de cada bloque: T5 (R0yalCode) para el comando y T1 (JJOC3S) para el almacenamiento, en commits nuevos sin reescribir los existentes.

## 10. Repetición de la auditoría tras las correcciones (2026-11-12)

**Commits correctivos** (nuevos; los seis anteriores no se modificaron):

| Commit | Corrige | Autor | Committer | Archivos |
|---|---|---|---|---|
| `cc5d8f8` | D-05, D-08 (`local_storage.py`) | JJOC3S | R0yalCode | `core/adapters/local_storage.py`, `core/tests/test_local_storage.py` |
| `7be530f` | D-01, D-02, D-03, D-04, D-06 (`reconciliar_archivos.py`) | R0yalCode | R0yalCode | el comando, `peticiones/tests/test_reconciliar_archivos.py`, `tests/integration/test_reconciliar_archivos_postgres.py` (nuevo) |

**Diseño de las correcciones del comando:**

- D-01: una única función (`relativa_a_raiz`) normaliza todas las referencias: absolutas con `resolve()` y `relative_to(raiz)`; relativas con `normpath`; lo que sale de la raíz se informa.
- D-02: antes de borrar se verifica la conciliación y, si no es fiable, se aborta sin borrar nada: base sin referencias; ningún referenciado presente en la raíz (raíz o base equivocadas); errores de lectura; candidatos por encima de `--max-eliminaciones` (50). Además solo son eliminables archivos de la carpeta de un **expediente existente**; el resto se informa como `no_verificables`.
- D-03: dos protecciones independientes: antigüedad mínima de 1 h para eliminar (rechaza valores menores) y **bloqueo del expediente con `select_for_update(nowait)`** antes de borrar; toda operación que escribe archivos mantiene ese bloqueo hasta su *commit*, por lo que un expediente en uso se omite (`en_uso_omitidos`); con el bloqueo se revalidan las referencias.

**Verificación (cada prueba nueva se ejecutó primero contra `2764d12`, en rojo):**

| Criterio solicitado | Evidencia | Resultado |
|---|---|---|
| 1. Ningún referenciado se elimina, sea cual sea el formato | Pruebas D-01 (absoluta, con `..`, con `.`; declaratoria absoluta) + A7/A8 | ✔ |
| 2. Base vacía o equivocada no provoca eliminación masiva | Pruebas D-02 (sin referencias, raíz equivocada, expediente inexistente, límite, errores de lectura) + A9 en PostgreSQL real: aborta, 3/3 archivos intactos | ✔ |
| 3. Recientes y operaciones en curso protegidos | Prueba D-03 (antigüedad 0 rechazada) + A10; **PostgreSQL:** con el expediente bloqueado por otra conexión el comando no borra (rojo con `2764d12`, que lo borraba) y lo elimina al liberarse | ✔ |
| 4. Carpeta privada inexistente sin `KeyError` | Prueba D-04 + A6 | ✔ |
| 5. Un fallo de `chmod` no deja huérfanos | Prueba D-05 + A1 (0 archivos) | ✔ |
| 6. Directorios enlazados y archivos ilegibles se reportan | Prueba D-06 + A11 | ✔ |
| 7. Solo lectura por defecto | Pruebas de T5 | ✔ |
| 8. Eliminación con `--eliminar --confirmar` | Pruebas de T5 | ✔ |
| 9. SHA-256 de preexistentes intactos | Pruebas de T1/T2/T3/T5 y D-01 | ✔ |
| 10. H-I3-05 sin cambios | `test_h_i3_05_carga_repetida_sigue_creando_version` | ✔ |

**Regresión completa (HEAD `7be530f`):**

| Ámbito | Resultado |
|---|---|
| `pytest` (SQLite) | 637 aprobadas, 13 fallidas: **las mismas 13 de `pypdf`** |
| `src/core` + `tests/` (SQLite) | 130 aprobadas, 13 omitidas (`postgres`) |
| PostgreSQL 16.15, `-m postgres tests/integration` | **13/13** (C1–C8, infraestructura, *commit* fallido, expediente en uso) |
| PostgreSQL, `tests/` | 37/37 |
| PostgreSQL, `src/apps` | 21 fallos: **los mismos conocidos** (13 `pypdf` + 8 H-30) |
| Adversariales A1–A12 | Todas conformes |
| OpenAPI | Sin errores ni diferencias |
| flake8/black | Limpios |

**Hallazgo nuevo (previo, fuera de alcance):**

- **D-09 (menor, pruebas):** `tests/integration/test_postgres_infra.py` (T3) usa `transaction=True` sin `serialized_rollback`; si se ejecuta antes que las pruebas serializadas, estas fallan al restaurar los *content types* (verificado en `2764d12`: 2 aprobadas y 10 errores con ese orden). Con el orden por defecto todo pasa. La prueba nueva de `reconciliar_archivos` se hizo independiente del orden (siembra su catálogo). Corrección sugerida: `serialized_rollback=True` en esa prueba (responsable T3).

**Observaciones que quedan:**

- D-07: el comando no informa de referencias sin archivo (H-I3-07); pendiente por decisión del responsable.
- El bloqueo de D-03 solo es efectivo en PostgreSQL (SQLite ignora `select_for_update`); el entorno de producción usa PostgreSQL.
- D-08 usa un `umask` temporal de proceso cuando `FILE_UPLOAD_DIRECTORY_PERMISSIONS` está configurado (mismo criterio que Django); hoy no está configurado.
- DK-010: sigue sin evidencia la notificación de la atribución delegada a JJOC3S, JuanCalopinoo, 7777-C y Dan1el17.

**Dictamen final: APROBADA CON OBSERVACIONES.** Los defectos bloqueantes (D-01, D-02, D-03) y los menores autorizados (D-04, D-05, D-06, D-08) están corregidos y verificados en SQLite y PostgreSQL real, sin regresiones. Las observaciones restantes no impiden integrar.
