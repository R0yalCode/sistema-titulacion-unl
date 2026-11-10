# INFORME DE PRUEBAS DE SEGURIDAD — SGT-SIAAF Backend

**Fecha de ejecución:** 2026-11-05  
**Entorno:** Local (Windows 11, Python 3.12, pytest 8.4, Django 5.2, SQLite :memory:)  
**Variables de entorno:** `SECRET_KEY="test-secret-key-for-audit"`, `DB_PASSWORD="test"`, `DEBUG=False` (settings.test)  
**Comando:** `python -m pytest -x -q`  
**Resultado global:** **473 passed, 15 warnings** (0 failed, 0 errors, 0 skipped)

---

## 1. Resumen de Suites Ejecutadas

| Suite | Tests | Estado | Tiempo |
|-------|-------|--------|--------|
| `src/apps/authentication/tests/` | 40 | ✅ Passed | ~2.1s |
| `src/apps/expedientes/tests/` | 67 | ✅ Passed | ~3.8s |
| `src/apps/notificaciones/tests/` | 62 | ✅ Passed | ~2.5s |
| `src/apps/peticiones/tests/` | 118 | ✅ Passed | ~5.2s |
| `src/apps/resoluciones/tests/` | 73 | ✅ Passed | ~3.1s |
| `src/apps/verificacion/tests/` | 87 | ✅ Passed | ~2.8s |
| `src/core/adapters/tests/` | 26 | ✅ Passed | ~0.7s |
| **TOTAL** | **473** | ✅ **All Passed** | **20.24s** |

---

## 2. Pruebas por Categoría de Seguridad

### 2.1 Autenticación JWT (`test_jwt.py` - 6 tests)

| Test | Descripción | Resultado |
|------|-------------|-----------|
| `test_obtener_token_credenciales_validas` | Login exitoso retorna access+refresh con claims cedula+roles | ✅ |
| `test_obtener_token_credenciales_invalidas` | Password incorrecta → 401 | ✅ |
| `test_refresh_tokens_no_renovacion_por_defecto` | Refresh no rota token (ROTATE_REFRESH_TOKENS=False) | ✅ |
| `test_access_token_expirado_rechazado_401` | Token expirado → 401 en vista protegida | ✅ |
| `test_peticion_sin_token_devuelve_401` | Sin Authorization header → 401 | ✅ |
| `test_token_firma_invalida_rechazado` | Token malformado → 401 | ✅ |
| `test_authentication_failed_rechaza_token_expirado` | JWTAuthentication.authenticate lanza AuthenticationFailed | ✅ |

**Observaciones:**
- Tests validan flujo básico JWT pero **no verifican lifetime del access token** (60 min actual vs 30 min ACD).
- **No hay tests de throttling** en login (SEC-AUTH-01).
- **No hay tests de rotación/blacklist** (SEC-AUTH-02) — funcionalidad deshabilitada.
- Warning `InsecureKeyLengthWarning`: SECRET_KEY de test (25 bytes) < 32 bytes recomendados para HS256.

### 2.2 Autorización RBAC e IDOR (`test_rbac_permissions.py` - 34 tests + `test_idor_isolation_expediente.py` - 12 tests)

| Test | Descripción | Resultado |
|------|-------------|-----------|
| `test_matriz_codificada_coincide_literal_62` | Matriz RBAC código == literal specify.md §6.2 | ✅ |
| 28 tests `test_celda_matriz_por_rol` | Cada celda (recurso, método, rol) = alcance esperado | ✅ |
| `test_rol_fuera_de_matriz_denegado_mundo_cerrado` | RESPONSABLE_DEPENDENCIA → DENY en todos recursos | ✅ |
| `test_anonimo_sin_token_denegado` | Usuario None → DENY | ✅ |
| `test_estudiante_acceso_recurso_decano_403` | Estudiante → declaratorias POST = 403 | ✅ |
| `test_decano_acceso_recurso_decano_200` | Decano → declaratorias POST = 200 | ✅ |
| `test_rol_responsable_recurso_declaratorias_403` | Responsable → declaratorias = 403 | ✅ |
| `test_idor_del_ajeno_por_uuid_404_del_propio_200` | Estudiante ve propio (200) / ajeno (404) | ✅ |
| 12 tests `test_idor_isolation_expediente.py` | Aislamiento por rol (own/carrera/facultad/admin) + 404 IDOR | ✅ |

**Observaciones:**
- **Cobertura completa** de matriz 6.2 y 14 casos IDOR históricos.
- IDOR retorna **404** (no 403) para no filtrar existencia — correcto (DEC-13).
- `ScopeFilterMixin` validado para todos los ámbitos (own, carrera, facultad, asignado, borrador, admin).

### 2.3 Validación PDF (`test_pdf_validation.py` - 25 tests + `test_pdf_ingestion_and_security.py` - 67 tests)

| Categoría | Tests | Resultado |
|-----------|-------|-----------|
| Tamaño archivo (≤10MB, >10MB, vacío) | 7 | ✅ |
| Magic bytes (%PDF-, PE, PNG, JPEG, texto, espacios, vacío) | 11 | ✅ |
| Hash SHA-256 (cálculo, consistencia, streaming, posición) | 7 | ✅ |
| Validación completa (integración) | 7 | ✅ |
| Casos borde (versiones PDF, streaming, posición) | 7 | ✅ |
| Carga documento service (éxito, versionado, permisos, rechazo) | 28 | ✅ |
| Carga documento endpoint (201, 401, 403, 400, 404, versionado) | 14 | ✅ |
| Descarga segura (200, 401, 403, 404, versionado, almacenamiento) | 19 | ✅ |
| Flujo completo integración (solicitud→carga→descarga, subsanación) | 3 | ✅ |
| Seguridad endpoint (400 magic, 400 size, 401, 403, 404) | 5 | ✅ |
| Registro subido_por (service + endpoint) | 3 | ✅ |

**Observaciones:**
- **Validación magic bytes robusta**: rechaza PE (MZ), PNG, JPEG, texto, vacío, espacios antes de header.
- **Hash SHA-256** verificado: consistente, streaming, posición restaurada.
- **Versionado N+1** probado: múltiples cargas incrementan versión, marcan anterior `es_vigente=False`.
- **Almacenamiento privado** verificado: ruta `private/`, sin `base_url`, `url()` → NotImplementedError.
- **Descarga autorizada**: 401 sin token, 403/404 rol/estudiante ajeno, 200 autorizado.
- **Gap**: No hay test de validación MIME real con `python-magic` (no implementado).

### 2.4 Verificación Checklist (`test_evaluar_checklist.py` - 17 tests + `test_checklist_and_observations.py` - 23 tests + `test_subsanar_requisito.py` - 13 tests + `test_validar_checklist_completo.py` - 6 tests)

| Test | Descripción | Resultado |
|------|-------------|-----------|
| `test_evaluar_verificado_exitoso` | SECRETARIO_ABOGADO/ANALISTA_APOYO evalúan VERIFICADO | ✅ |
| `test_evaluar_observado_crea_observacion_y_notifica` | OBSERVADO crea ObservacionAccionable + notificación | ✅ |
| `test_falla_si_estado_invalido` | Estado ≠ VERIFICADO/OBSERVADO → error | ✅ |
| `test_falla_si_observado_sin_motivo` | OBSERVADO sin motivo → error | ✅ |
| `test_falla_si_ya_evaluado` | Re-evaluar → VerificationAlreadyCompletedError | ✅ |
| `test_falla_si_expediente_no_en_verificacion` | Estado expediente ≠ EN_VERIFICACION → error | ✅ |
| `test_falla_si_usuario_no_autorizado` | Estudiante/Secretaria → UserNotAuthorizedError | ✅ |
| `test_analista_apoyo_puede_evaluar` | ANALISTA_APOYO con facultad match → OK (borrador) | ✅ |
| `test_falla_si_usuario_distinta_facultad` | Facultad distinta → 403/404 | ✅ |
| `test_concurrencia_dos_usuarios_mismo_requisito` | `select_for_update` bloquea 2ª evaluación concurrente | ✅ |
| `test_bloquea_emision_si_requisitos_pendientes` | RN-003: checklist incompleto → no emite informe | ✅ |
| `test_ciclo_completo_observar_subsanar_verificar` | Flujo completo: observar → subsanar → verificar | ✅ |
| `test_versionado_n_mas_1_subsanacion` | Subsanación incrementa versión documento | ✅ |
| `test_estudiante_no_puede_evaluar_checklist` | RBAC: ESTUDIANTE → DENY en checklist PUT | ✅ |
| `test_idor_prevencion_acceso_expediente_ajeno` | IDOR protección en endpoints verificación | ✅ |

**Observaciones:**
- **Bloqueo pesimista** (`select_for_update`) verificado para concurrencia.
- **RN-003** (bloqueo emisión si checklist incompleto) probado en service y endpoint.
- **Ciclo completo** observación → subsanación → verificación validado con versionado.
- **Print statements** en `evaluar_checklist.py:164,170` ejecutados durante tests (aparecen en stdout) — fuga info sensible.

### 2.5 Resoluciones (Informe/Declaratoria) - 34 tests

| Test | Descripción | Resultado |
|------|-------------|-----------|
| `test_emitir_informe_exitoso_apto` | SECRETARIO_ABOGADO emite informe APTO + PDF providencia | ✅ |
| `test_emitir_informe_genera_pdf_providencia` | PDF generado con magic bytes, estructura, firma | ✅ |
| `test_falla_si_checklist_no_completo` | RN-003: checklist incompleto → error | ✅ |
| `test_falla_si_usuario_no_secretario_abogado` | RBAC: solo SECRETARIO_ABOGADO → allow | ✅ |
| `test_registrar_declaratoria_exitoso` | DECANO registra declaratoria + PDF memorando | ✅ |
| `test_falla_si_usuario_no_decano` | RBAC: solo DECANO → allow | ✅ |
| `test_falla_si_archivo_invalido` | Validación PDF en memorando (magic bytes, size) | ✅ |
| `test_informe_aptitud_inmutable` | Informe creado → no modificable (inmutabilidad) | ✅ |
| `test_declaratoria_aptitud_inmutable` | Declaratoria creada → no modificable | ✅ |

**Observaciones:**
- **Inmutabilidad** registros verificada (no UPDATE tras CREATE).
- **PDF generation** validado: magic bytes, tamaño ≤10MB, estructura, firmas.
- **RBAC estricto**: solo roles autorizados (Secretario Abogado / Decano / Analista Apoyo para registrar).

### 2.6 Notificaciones y Auditoría - 44 tests

| Test | Descripción | Resultado |
|------|-------------|-----------|
| `test_crear_evento_auditoria_basico` | EventoAuditoria creado con JSONB detalles | ✅ |
| `test_evento_auditoria_jsonb_detalles` | Estructura JSONB preservada | ✅ |
| `test_crear_expediente_genera_auditoria` | Signal post_save → EXPEDIENTE_CREADO | ✅ |
| `test_cambio_estado_genera_auditoria` | Signal → ESTADO_CAMBIADO con delta | ✅ |
| `test_evaluar_checklist_genera_auditoria` | Signal → CHECKLIST_EVALUADO | ✅ |
| `test_cargar_documento_genera_auditoria` | Signal → DOCUMENTO_CARGADO con hash | ✅ |
| `test_emitir_informe_genera_auditoria` | Signal → INFORME_EMITIDO | ✅ |
| `test_registrar_declaratoria_genera_auditoria` | Signal → DECLARATORIA_REGISTRADA | ✅ |
| `test_evento_auditoria_no_modificable` | Inmutabilidad: save() tras create → error | ✅ |
| `test_flujo_completo_con_auditoria` | E2E: expediente → checklist → docs → informe → declaratoria | ✅ |
| `test_notificacion_creada_inmediatamente_en_transaccion` | Despacho sincrónico en transacción | ✅ |
| `test_notificacion_rollback_no_persiste` | Rollback transacción → notificación no persiste | ✅ |
| `test_marcar_leida_exitosa` | Endpoint PATCH /marcar-leida/ → leida=True | ✅ |

**Observaciones:**
- **Auditoría inmutable** verificada (JSONB, sin UPDATE).
- **Señales Django** cubren todos los eventos de negocio (expediente, checklist, docs, resoluciones).
- **IP auditoría**: campo existe en modelo y `_crear_evento_auditoria` lo guarda, pero `_get_current_request()` retorna `None` → IP = `None` en tests (no verificada en entorno real con proxy).

### 2.7 Expedientes (Crear, Enviar, Bandeja, Máquina de Estados) - 67 tests

| Test | Descripción | Resultado |
|------|-------------|-----------|
| `test_crear_expediente_201_con_5_peticiones_pendiente` | POST /expedientes/ → 201 + 5 peticiones base | ✅ |
| `test_envio_completo_200_con_timestamp_y_plazo` | POST /enviar/ → estado ENVIADA + fecha_limite 8 días hábiles | ✅ |
| `test_estudiante_no_ve_expediente_ajeno_404` | IDOR: estudiante → expediente ajeno = 404 | ✅ |
| `test_secretaria_carrera_ve_expediente_su_carrera_200` | Ámbito carrera funcionando | ✅ |
| `test_secretario_abogado_ve_expediente_su_facultad_200` | Ámbito facultad funcionando | ✅ |
| `test_administrador_ve_todos_los_expedientes_200` | ADMINISTRADOR → ALLOW | ✅ |
| `test_responsable_dependencia_sin_acceso_403` | RESPONSABLE_DEPENDENCIA → DENY | ✅ |
| Máquina de estados (14 tests) | Transiciones válidas/inválidas, plazo laboral, pausa/reanudación, inmutabilidad campos | ✅ |

**Observaciones:**
- **Máquina de estados** completa: BORRADOR → ENVIADA → EN_VERIFICACIÓN → OBSERVADA/INFORME_EMITIDO → DECLARADA_APTA/CANCELADA.
- **Plazo laboral** 8 días hábiles calculado correctamente (omite feriados, fines de semana).
- **Pausa/reanudación reloj** verificada (observación pausa, subsanación reanuda).
- **Inmutabilidad** campos críticos (`fecha_recepcion`, `numero_providencia`, `fecha_limite_original`) verificada.

---

## 3. Pruebas Faltantes / No Ejecutadas (Gaps de Seguridad)

| Control | Tests Requeridos | Estado |
|---------|------------------|--------|
| **SEC-AUTH-01 Throttling login** | `test_login_throttle_5_per_minute`, `test_login_throttle_returns_429`, `test_login_throttle_per_ip` | **AUSENTES** (funcionalidad no implementada) |
| **SEC-AUTH-02 Rotación/Blacklist** | `test_refresh_rotates_token`, `test_old_refresh_rejected_after_rotate`, `test_blacklisted_refresh_rejected`, `test_logout_blacklists_refresh` | **AUSENTES** (funcionalidad deshabilitada) |
| **SEC-AUTH-03 Access token 30 min** | `test_access_token_lifetime_30_minutes` (validar claim `exp`) | **AUSENTE** |
| **SEC-VAL-01 MIME real** | `test_pdf_validation_with_python_magic`, `test_polyglot_pdf_rejected` | **AUSENTES** (python-magic no instalado) |
| **SEC-VAL-02 Throttling carga** | `test_document_upload_throttle_10_per_hour`, `test_upload_throttle_returns_429` | **AUSENTES** (no implementado) |
| **SEC-SEC-02 Rutas internas** | `test_serializer_excludes_archivo_path`, `test_serializer_excludes_memorando_path` | **AUSENTES** (serializers exponen rutas) |
| **SEC-LOG-01 Handler global** | `test_500_no_stacktrace_leak`, `test_409_format_uniform`, `test_429_format_uniform`, `test_500_format_uniform` | **AUSENTES** (handler no existe) |
| **SEC-LOG-02 Logging** | `test_no_print_in_production_code`, `test_logging_structured_json`, `test_logging_no_secrets`, `test_logging_rotation` | **PARCIAL** (print() existe en evaluar_checklist.py) |
| **SEC-LOG-03 IP auditoría** | `test_audit_ip_captured_with_proxy`, `test_audit_ip_spoofing_blocked`, `test_audit_ip_persisted_in_evento` | **AUSENTES** (middleware thread-local + TRUSTED_PROXIES no implementados) |
| **Swagger/ReDoc protección** | `test_swagger_anonymous_denied_in_prod`, `test_swagger_admin_allowed_in_prod`, `test_schema_anonymous_denied_in_prod` | **AUSENTES** (config AllowAny) |
| **E2E** | Suite `tests/e2e/` con flujos completos usuario real | **AUSENTE** (directorio no existe) |

---

## 4. Cobertura de Código (Estimada)

> **Nota:** No se ejecutó `--cov` en esta auditoría. La siguiente es una estimación basada en módulos cubiertos por tests.

| Módulo | Estimación Cobertura | Tests Relevantes |
|--------|---------------------|------------------|
| `authentication/` | ~95% | test_jwt.py, test_rbac_permissions.py, test_django_admin.py |
| `expedientes/` | ~90% | test_crear, test_enviar, test_bandeja, test_state_machine, test_idor, test_plazo |
| `peticiones/` | ~95% | test_cargar, test_descargar, test_solicitar, test_pdf_security |
| `verificacion/` | ~90% | test_evaluar, test_checklist_obs, test_subsanar, test_validar_completo |
| `resoluciones/` | ~85% | test_emitir, test_declarar, test_models, test_pdf_generator |
| `notificaciones/` | ~95% | test_notification_service, test_endpoints, test_auditoria, test_notifications_and_audit |
| `core/adapters/` | ~80% | test_pdf_validation, test_mock_sga |
| **Promedio ponderado** | **~90%** | - |

**Recomendación:** Ejecutar `pytest --cov=src --cov-report=term-missing --cov-fail-under=80` en CI para medir y enforzar cobertura.

---

## 5. Advertencias y Problemas Detectados Durante Ejecución

### 5.1 Warnings de PyJWT (InsecureKeyLengthWarning)
```
InsecureKeyLengthWarning: The HMAC key is 25 bytes long, which is below the minimum recommended length of 32 bytes for SHA256.
```
- **Causa:** `SECRET_KEY="test-secret-key-for-audit"` (25 chars) en entorno de test.
- **Impacto:** Solo en tests; en producción `SECRET_KEY` debe ser ≥32 bytes (generada con `secrets.token_urlsafe(32)`).
- **Acción:** Documentar requisito longitud mínima en `.env.example` y validar en `production.py`.

### 5.2 Print Statements en Código Producción
```
DEBUG: user=..., roles=['SECRETARIO_ABOGADO'], has_secretario=True, has_analista=False
DEBUG FACULTY CHECK: user_facultad=..., expediente_facultad=..., match=True
```
- **Archivo:** `src/apps/verificacion/services/evaluar_checklist.py:164,170`
- **Impacto:** Fuga de información sensible (usuario, roles, facultad) en stdout contenedor.
- **Acción:** Reemplazar con `logger.debug()` y eliminar antes de producción.

### 5.3 Tests `src/core/tests` No En `testpaths`
- **Configuración:** `testpaths = ["src/apps"]` en `pyproject.toml:20`
- **Comportamiento:** pytest descubre `src/core/adapters/tests/` por convención (`test_*.py`) pero no por config explícita.
- **Riesgo:** Si se añade `--ignore-glob` o se restringe descubrimiento, estos tests no correrían.
- **Acción:** Cambiar a `testpaths = ["src"]`.

---

## 6. Reproducibilidad

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Entorno aislado | ✅ | SQLite :memory: en `settings.test` |
| Variables entorno controladas | ✅ | `SECRET_KEY`, `DB_PASSWORD` seteadas en comando |
| Dependencias fijadas | ⚠️ | Rangos `>=x.y,<z.0` en requirements.txt (no `==x.y.z`) |
| Orden tests determinístico | ✅ | pytest default (basado en path/name) |
| Datos de prueba aislados | ✅ | Fixtures pytest-django con `db` transaction rollback |
| Ejecución repetible | ✅ | 3 ejecuciones consecutivas → mismos 473 passed |

---

## 7. Conclusiones de Pruebas

### Fortalezas
- **Suite robusta:** 473 tests cubren auth, RBAC, IDOR, PDF validation, checklist, resoluciones, notificaciones, auditoría, expedientes.
- **Regresión IDOR completa:** 14 casos históricos automatizados y passing.
- **Validación PDF exhaustiva:** Magic bytes, tamaño, hash, versionado, almacenamiento, descarga — todos con tests positivos y negativos.
- **Concurrencia verificada:** `select_for_update` en evaluación checklist probado.
- **Inmutabilidad auditada:** EventoAuditoria, InformeAptitud, DeclaratoriaAptitud inmutables tras creación.
- **Ejecución limpia:** 0 failed, 0 errors, 0 skipped en 20.24s.

### Brechas Críticas en Pruebas
1. **Sin tests de throttling** (login, carga docs) — funcionalidad no implementada.
2. **Sin tests de rotación/blacklist JWT** — funcionalidad deshabilitada.
3. **Sin tests de protección Swagger/ReDoc en producción** — configuración `AllowAny`.
4. **Sin tests de IP auditoría real** — middleware thread-local + TRUSTED_PROXIES no implementados.
5. **Sin suite E2E** — no existe `tests/e2e/`.
6. **Sin umbral de cobertura** — no `--cov-fail-under`.
7. **Print statements en código** ejecutados durante tests (fuga info en stdout).

### Veredicto de Pruebas
> **La suite de pruebas es funcional y completa para lógica de negocio y autorización, pero INCOMPLETA para controles de seguridad de infraestructura (throttling, rotación tokens, logging, IP auditoría, hardening producción).**  
> Los 473 tests passing validan el comportamiento funcional correcto, pero **no validan la postura de seguridad operativa** (rate limiting, token revocation, log security, production config).  
> **Requerido:** Implementar controles faltantes + agregar tests correspondientes antes de considerar backend listo para producción.

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Comando ejecutado:** `SECRET_KEY="test-secret-key-for-audit" DB_PASSWORD="test" python -m pytest -x -q`  
**Duración:** 20.24s  
**Resultado:** 473 passed, 15 warnings