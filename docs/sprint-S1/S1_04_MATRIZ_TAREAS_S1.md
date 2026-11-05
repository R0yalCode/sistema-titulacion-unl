# S1-04 — MATRIZ DE TAREAS SPRINT S1

**Fecha:** 02-nov-2026 · **Estado:** Propuesta. Ninguna tarea de este sprint existe aún en `tasks.md` del Spec Kit (revisado: el artefacto `sgt-siaaf/specs/001-tramite-titulacion/tasks.md` contiene solo T001-T046, todos pendientes a nivel de registro disciplinar) — **no hay duplicación ni sobrescritura**. Ninguna tarea se marcada completada.

**Nota de trazabilidad:** las tareas T001-T046 del Spec Kit NO se tocan; las tareas S1-T01…S1-T06 son un sprint de estabilización derivado de la auditoría. Se recomienda registrar esta matriz como apéndice oficial (S1.x de tasks.md o documento vinculado a la etapa Spec Kit `tasks`) tras aprobación del equipo.

---

## S1-T01 · Diagnóstico y validación técnica

- **IDENTIFICADOR:** S1-T01
- **OBJETIVO:** Consolidar la evidencia verificada de la auditoría (SEC-01/02/03, 74 resultados de test, diagnóstico Admin) como línea base aprobada para la corrección.
- **PROBLEMA QUE RESUELVE:** Las cifras alegadas ("74 errores una causa") estaban sinvalidar; hay 3 causas-raíz y un entorno de ejecución mal configurado que falseaban conclusiones.
- **ARCHIVOS/MÓDULOS:** `docs/sprint-S1/*` (los 6 documentos), `backend/src/apps/resoluciones/*` (solo lectura), `backend/src/config/settings/*` (lectura).
- **DEPENDENCIAS:** Ninguna (tarea inicial del sprint).
- **ALCANCE:** Reproducir/consolidar el diagnóstico en 2 escenarios (settings test / local), validar los 3 hallazgos, documentar pruebas base (464 tests, 398 verdes en esc. B).
- **EXCLUSIONES:** Cualquier cambio de código, configuración, admin, permisos.
- **CRITERIOS DE ACEPTACIÓN (verificables):**
  1. Los 6 documentos S1_01-S1_06 existen en `docs/sprint-S1/`.
  2. Cada hallazgo SEC-01/02/03 tiene veredicto con evidencia `archivo:línea` o salida de pytest citada.
  3. Los 3 resultados de suite (A y B) registrados con totales idénticos re-ejecutables.
  4. Contradicciones documentales C1-C4 listadas con fuentes.
- **PRUEBAS NECESARIAS:** `docker exec ... pytest -q --tb=no` en ambos escenarios; `pytest --collect-only` (464).
- **RIESGOS:** Baja (documentación). Deprecación si el equipo no aprueba la línea base → bloquea el sprint.
- **REQUISITOS RELACIONADOS:** RNF-012, C-019, C-020, C-002.
- **CONDICIÓN DE TERMINADA:** Aprobación de la matriz y hallazgos por el equipo/arquitectura.

---

## S1-T02 · Corrección de almacenamiento privado y persistencia documental

- **IDENTIFICADOR:** S1-T02
- **OBJETIVO:** Garantizar que los PDFs de resoluciones (#590 borrador y final, #162 firmado) se generen y persistan en almacenamiento privado bajo `PrivateMediaStorage` con ruta relativa, integridad (hash) y trazabilidad en BD coherente con ADR-005.
- **PROBLEMA QUE RESUELVE:** SEC-02 (ruta hardcodeada destruye ~53-56 tests y persistencia del informe) y SEC-01 (el memorando 162 nunca se escribe en disco; hash descartado).
- **ARCHIVOS/MÓDULOS:**
  - `backend/src/apps/resoluciones/adapters/pdf_generator.py:47-50` (inyectar base dinámica: `output_dir=None` → base en `PRIVATE_MEDIA_ROOT/MEDIA_ROOT/private` o delegar todo en `guardar_archivo_privado`).
  - `backend/src/apps/resoluciones/services/emitir_informe.py:178-196` (generar a storage privado, guardar ruta RELATIVA; opcional: persistir hash).
  - `backend/src/apps/resoluciones/services/declarar_aptitud.py:167-181` (usar `guardar_archivo_privado(file, expediente.id, nombre_original)` y `metadata` de `validar_pdf_completo` — persistir `archivo_path` relativa; hash si la migración se aprueba).
  - `backend/src/apps/resoluciones/tests/test_models.py` literales de fixture (solo lectura informativa).
  - Posible migración si se aprueba `hash_sha256`/`tamanio_bytes` en `InformeAptitud`/`DeclaratoriaAptitud` (sin esto NO es necesaria migración).
- **DEPENDENCIAS:** S1-T01 aprobado. Ninguna dependencia de S1-T03.
- **ALCANCE:** Proceso completo de persistencia de PDFs del módulo resoluciones. Mantener la interfaz pública de las funciones shortcuts (`generar_providencia_590`, `generar_memorando_162`).
- **EXCLUSIONES:** Cambios en peticiones/verificacion; HTTPS/servicio de ficheros; elimend de `emitir_informe.py` historial de estado antérieur (ver A1 abajo — se deja a decisión aparte por alcance exterior).
- **CRITERIOS DE ACEPTACIÓN:**
  1. Ningún path absoluto `/media/...` en módulo `resoluciones` (grep).
  2. `PDFGeneratorAdapter()` sin argumento funciona en contenedor sin `PermissionError`.
  3. `emitir_informe()` deja archivo físico bajo `MEDIA_ROOT/private/` y BD con **ruta relativa**.
  4. `declarar_aptitud()` crea el archivo físico y el apuntador a ruta relativa consintiéndose; hash y tamaño si se aprueba la壳 migración.
  5. `test_pdf_generator.py`, `test_emitir_informe.py`, `test_declarar_aptitud.py` (errors y fails de causa C1) → 0 fallos por esa causa (la causa C3/pypdf se administra en S1-T05).
  6. Re-ejecución completa: no empeora cualquier otro módulo atestiguado.
- **PRUEBAS NECESARIAS:** Suite completa en escenario B + caso nuevo de redondeo (persistencia física verificada por lectura del storage).
- **RIESGOS:** Doble escritura (generar primero en tmp y luego mover vs. generar directamente en storage); válidos camimos de ruta relativa para consultas existente; corrección sin afectar la descarga ya protegidas por API.
- **REQUISITOS RELACIONADOS:** RF-005, RF-010, RF-011, RNF-004, C-006, ADR-005, DEC-04; plan §19.
- **CONDICIÓN DE TERMINADA:** CRs y suite verde salvo causas independientes (pypdf / sqlite introspection acordadas para S1-T05), PR aprobado.

---

## S1-T03 · Corrección y validación de permisos RBAC del checklist

- **IDENTIFICADOR:** S1-T03
- **OBJETIVO:** Habilitar la consulta `GET /api/v1/expedientes/{id}/checklist/` (HU-006, FL-03 paso 1) y documentar/estabilizar las celdas GET de la matriz RBAC con pruebas para cada rol.
- **PROBLEMA QUE RESUELVE:** SEC-03 — ausencia de `GET` en `RBAC_MATRIX["checklist"]` deja el endpoint en 403 para TODOS los roles (mundo cerrado accidental), bloqueando HU-006 y el flujo completo.
- **ARCHIVOS/MÓDULOS:** `backend/src/apps/authentication/adapters/permissions.py:77-93`; `backend/src/apps/verificacion/adapters/views.py:242-267`; `backend/src/apps/authentication/tests/test_rbac_permissions.py` (matriz literal, sin GET); prueba de transporte checklist GET por rol (nueva).
- **DEPENDENCIAS:** S1-T01 (aprobación de la concesión propuesta); alcance isolation objetivo aclarado con `clarify` para el caso RESPONSOBLE_DEPENDENCIA (decisión abierta — ver riesgos).
- **ALCANCE:** La propuesta de celdas GET: `ESTUDIANTE: own`, `SECRETARIA_CARRERA: carrera`, `SECRETARIO_ABOGADO: facultad`, `ANALISTA_APOYO: facultad`, `DECANO: facultad`, `DIRECTOR_CARRERA: carrera`, `ADMINISTRADOR: allow`. Cada scope justificado por HU-006/FL-03/FL-05 y parellelismo con `expedientes:GET`. NO concedencias adicionales.
- **EXCLUSIONES:** PUT/PATCH/POST de checklist (aprobados); otros recursos; cambios al `HasRolePermission` o scope_filter.
- **CRITERIOS DE ACEPTACIÓN:**
  1. `RBAC_MATRIX["checklist"]` tiene `GET` con scopes coherentes con el isolation de consultas de expedientes.
  2. Test parametrizado: 8 roles × GET checklist → scope correcto (401 sin auth; 403 para roles denegados).
  3. Consulta GET del checklist de propio expediente responde 200 con las 5 filas.
  4. Ninguna combinación concedida sin justificación escrita en la tarea/PR.
  5. Suite RBAC existente no se debilita (matriz literal actualizada SIN eliminar tuples deny).
- **PRUEBAS NECESARIAS:** pytest RBAC (regresión + nuevo paramétrico).
- **RIESGOS:** Data-.SerializedName de over-permision: criticidad de auditoría de seguridad inspección de IDOR; `RESPONSABLE_DEPENDENCIA` sin regla resuelta en specify (decisión explícita necesaria, default deny). Antes de conceder, validar que `ScopeFilterMixin` aísla por expediente y por expediente_id en GET detail endpoint.
- **REQUISITOS RELACIONADOS:** RF-006, HU-006/FL-03, RNF-002, RNF-003, C-004, C-005.
- **CONDICIÓN DE TERMINADA:** PR con concesión explicada + test paramétrico verde + review de seguridad.

---

## S1-T04 · Implementación de Django Admin

- **IDENTIFICADOR:** S1-T04
- **OBJETIVO:** Habilitar Django Admin como consola interna de soporte con los 13 modelos administrados según reglas (read-only donde corresponde; sin carga pública de archivos).
- **PROBLEMA QUE RESUELVE:** No existe solución de administración (0 admin.py; admin deshabilitado); los equipos necesitan corregir datos de emergencia y ver catálogos sin tocar DB a mano.
- **ARCHIVOS/MÓDULOS:** `config/settings/base.py` (añadir `django.contrib.admin` + `django.contrib.messages` a INSTALLED_APPS; middleware `AuthenticationMiddleware` y `MessageMiddleware`), `config/urls.py` (admin.site.urls RESTRINGIDO — localhost/VPN o superuser only), admin.py por cada módulo, seed de usuarios admin.
- **DEPENDENCIAS:** S1-T01 (aprobación), S1-T02 (datos de resoluciones deben ser coherentes antes de admin read-only), S1-T03 (roles sanos). ─ **Nota de gobernanza:** `tasks.md` §4.2 excluye "Django Admin expuesto por HTTP" del MVP: requiere Decisión (C1) **aprobada por el equipo antes de tocar configuración** (documentar como decision en ADR/clarify).
- **ALCANCE:** Según S1_03 §3.1-3.10: read-only total para bitácora (EventoAuditoria, HistorialEstado) e inmutables (informes/declaratorias); CRUD de catálogos y users/roles; sin eliminación de expedientes/documentos; sin links públicos a archivos privados; formularios sin campos sensibles.
- **EXCLUSIONES:** Migraciones nuevas salvo decisión documentada; Django Admin como flujo de usuarios finales; APIcereza de archivos vía admin (descarga), autenticación externa, transformaciones de negocio vía actions.
- **CRITERIOS DE ACEPTACIÓN:**
  1. `manage.py check` limpia; admin accesible con staff creado por seed y aislado en local/test.
  2. Los 13 modelos registrados con la conservación demandada inversa (read-only total para 5 de ellos, según diseño aprobado).
  3. No exista acción de borrado de expedientes/documentos; `delete_selected` deshabilitado donde aplica.
  4. Dev reg chart: admin HTTP en producción expuesto solo si existe la decisión C1 aprobada; se documenta el riesgo de Nginx A-08.
  5. Pruebas: smoke test con `RequestFactory`/admin client por modelo; no hay intento de modificar estado con resultados silenciosos.
- **PRUEBAS NECESARIAS:** admin client smoke por modelo; permisos has_add/change/delete; regresión completa.
- **RIESGOS:** Apertura accidental de superfluidad de superficie HTTP; fuga de datos si `list_display`/logs mencionan campos privados; meses calidad C-019/C-020 si doc refuerzo faltante.
- **REQUISITOS RELACIONADOS:** C-008, C-012, RNF-014; plan §7/§10; tasks.md §4.2 (condición de exclusión — C1).
- **CONDICIÓN DE TERMINADA:** Decisión C1 documentada, PR aprobado por arquitectura, smoke suite verde.

---

## S1-T05 · Pruebas automatizadas y regresión (integridad del suite)

- **IDENTIFICADOR:** S1-T05
- **OBJETIVO:** Dejar la suite determinista contra cualquier motor (SQLite en test / PostgreSQL en local) y con dependencias de test declaradas.
- **PROBLEMA QUE RESUELVE:** Causa C2 (introspección `sqlite_master` en 8 tests → error en Postgres) y C3 (`pypdf` no statement ed, aserciones vacías); y el modo por defecto del contenedores usa `local`.
- **ARCHIVOS/MÓDULOS:** `backend/src/apps/notificaciones/tests/test_auditoria.py` (test_indices_creados), `test_notification_service.py`, `test_notifications_and_audit.py`, `backend/src/apps/resoluciones/tests/test_models.py` (4 introspecciones); `backend/requirements-dev.txt` (añadir `pypdf`); aserciones de texto en `test_pdf_generator.py` (fallback explícito de aviso en import missing); `backend/Dockerfile`. (Sin deletar ni skip — se hacen portá兄妹ynamicos, por ejemplo introspección via `django.db.connection.introspection` / compruebación por vendor.)
- **DEPENDENCIAS:** Ninguna para C2/C3; regresión final depende de S1-T01..T04.
- **ALCANCE:** Hacer portá CRS los 8 tests de índices; declarar pypdf; revocar el silent-fallback por skip explícito o failure descriptivo (SI lo aprobado); aseGridas CA global.
- **EXCLUSIONES:** Modificar tests funcionales para "hacer verde" con mocks artificiales; eliminar cobertura.
- **CRITERIOS DE ACEPTACIÓN:**
  1. `pytest -q` con BOTH escenarios (con y sin env var) → 464 tests; 0 errores de configuración.
  2. Cualquier test de índices corre bien en SQLite y PostgreSQL.
  3. `pypdf` presente y declarada en `requirements-dev.txt` (versión pin). Sin serum pronceño de escribir PDF de test strings.
  4. Cobertura medible (`pytest --cov`): reporte base y objetivo ≥ 70 % en lógica de negocio (RNF-012) tras converger fallas C1.
  5. Las pruebas no se debilitaron: diff-evidencia de ningún `skip` agregado sin marca explicativa.
- **PRUEBAS NECESARIAS:** doble escena-trío + `pytest-cov`.
- **RIESGOS:** Diferencias de comportamiento en índices nombrados entre motores (naming auto vs especificado); mit adaptable a introspection API.
- **REQUISITOS RELACIONADOS:** C-011, RNF-012, plan §22.
- **CONDICIÓN DE TERMINADA:** Suite completa verde en ambos escenarios + reporte cobertura + PR.

---

## S1-T06 · Validación de preparación del backend para React

- **IDENTIFICADOR:** S1-T06
- **OBJETIVO:** Confirmar que el backend expuesto en `/api/v1` está estable, documentado y defenible para consumo del frontend (Unidad 2).
- **PROBLEMA QUE RESUELVE:** No hay validación formal de contratos OpenAPI/estados/RBAC vistas completas sin rearrancarpes; también la bailia de flujo e2e (incluida declaratoria sin persistencia) impedía demo de integración FE.
- **ARCHIVOS/MÓDULOS:** `backend/contracts/openapi.yaml`, `backend/openapi.yaml`, `drf-spectacular` (`/api/v1/schema`), `tests/e2e/test_full_workflow.py`, matriz RBAC final (S1-T03), whitelist de SERVE_PERMISSIONS de swagger (`base.py:115-116` — revisar seguridad).
- **DEPENDENCIAS:** S1-T02, S1-T03, S1-T05 (todos los demás verdes).
- **ALCANCE:** E2E exitoso del flujo BORRADOR→…→DECLARADA_APTA con URLs reales vía APIClient; validación spectaculare no-cíclicas del OpenAPI; revisión de headers CORS/seguridad si aplica; verificación enumeración de qué NO se expone (media privado).
- **EXCLUSIONES:** Desarrollo del frontend; docker-compose de producción.
- **CRITERIOS DE ACEPTACIÓN:**
  1. `GET /api/v1/schema/` carga ok (404 no); Swagger UI renderiza sin errores.
  2. `tests/e2e/test_full_workflow.py` pass (hoy pendiente de verificación — determinarlo en esta tarea).
  3. Summary de endpoints × rol× szk concerted acul propuesta T03 retro anotación.
  4. Ningún endpoint muestra rutas del sistema de ficheros en respuestas (SEC-07 del audit previo, verificación incluida aquí como revisión, no cambio).
- **PRUEBAS NECESARIAS:** tests e2e, validador schema, regresión completa.
- **RIESGOS:** Insufficient feedback del frontend no disponible aún; view-inline contrato detallado excluido del MVP backend.
- **REQUISITOS RELACIONADOS:** RNF-005 (no-cumplido p95: medir en carga en futuro), RNF-007, C-010.
- **CONDICIÓN DE TERMINADA:** checklist firmado por frontend/backend leads.

---

## Orden de ejecución recomendado

```
S1-T01 (aprobación línea base)
   ├─→ S1-T02 (storage/persistencia) ─┐
   ├─→ S1-T03 (RBAC GET checklist) ───┤
   └─→ S1-T05a (config de pruebas: pypdf + portabilidad) ─┤
                                                        ├─→ S1-T05b (regresión + cobertura)
                                                        └─→ S1-T04 (Django Admin; decisión C1 antes)
                                                        └─→ S1-T06 (preparación React) — último
```

S1-T02 y S1-T03 son paralelizables; S1-T04 requiere decisión gobernanza C1 además de su dependencia técnica.
