# 06 — AUDITORÍA DE SEGURIDAD Y CALIDAD

Hallazgos con formato: **ID · Severidad · Descripción · Evidencia (path:línea) · Módulo · Impacto · Recomendación breve**.

## A. Seguridad

### SEC-01 · CRÍTICO · Archivo del memorando N° 162 nunca persistido
- **Evidencia:** `resoluciones/services/declarar_aptitud.py:167-181` — valida el PDF (`validar_pdf_completo`), pero construye el string `archivo_memorando_firmado_path=f"expedientes/…/memorando_162_…pdf"` sin llamar a `guardar_archivo_privado`.
- **Módulo:** resoluciones (RF-011).
- **Impacto:** el documento firmado (via FirmaEC según DEC-04) **se pierde al terminar la request**; la base de datos registra un path que apunta a un archivo inexistente → integridad del trámite comprometida y `FileResponse` a futuro dará 404.
- **Recomendación:** persistir con `guardar_archivo_privado()` y registrar la ruta devuelta (mismo patrón de `cargar_documento.py`).

### SEC-02 · CRÍTICO · Rutas de almacenamiento hardcodeadas fuera de MEDIA_ROOT (disponibilidad + integridad)
- **Evidencia:** `resoluciones/adapters/pdf_generator.py:48` (`output_dir="/media/private/resoluciones"`, `os.makedirs` desde raíz FS — verificado: `PermissionError: [Errno 13] Permission denied: '/media/private'` en 74 tests); `tests/e2e` falla con `/app/backend/src/media` por ausencia de `PRIVATE_MEDIA_ROOT` (settings no lo definen, `config/settings/base.py:87`).
- **Módulo:** core/alomacenamiento + resoluciones.
- **Impacto:** generación de PDF inservible fuera del entorno original; riesgo de escritura a otras ubicaciones del host.
- **Recomendación:** unificar TODO el almacenamiento en `PrivateMediaStorage`/`MEDIA_ROOT`; definir `PRIVATE_MEDIA_ROOT` en settings.

### SEC-03 · ALTO · Endpoint `GET /expedientes/{id}/checklist/` inoperable (mundo-cerrado accidental)
- **Evidencia:** recurso `checklist` sin celda `"GET"` en `RBAC_MATRIX` (`authentication/adapters/permissions.py:77-93`); `HasRolePermission` deniega por defecto. El endpoint está registrado (`config/urls.py:63-67`) y documentado en openapi.yaml.
- **Impacto:** RF-006 roto en su consulta; alumnos/roles legítimos reciben 403 siempre.
- **Recomendación:** añadir celda GET por rol (estudiante own / secretaría asig / analista borrador / admin allow).

### SEC-04 · ALTO · Servidor de desarrollo y DEBUG=1 en el despliegue contenedorizado
- **Evidencia:** `Dockerfile:25` `CMD ["python","manage.py","runserver","0.0.0.0:8000"]`; `docker-compose.yml:29-30` (`config.settings.local`, `DEBUG: ${DEBUG:-1}`) y `settings/local.py:3` fuerza `DEBUG=True`.
- **Impacto:** stacktraces al cliente, sin gunicorn pneumático, penaliza seguridad y rendimiento; contradice RNF-016 y plan (gunicorn).
- **Recomendación:** settings de despliegue con `DEBUG=0` + gunicorn + collectstatic + TLS en nginx.

### SEC-05 · ALTO · Sin throttling ni rate limiting en autenticación
- **Evidencia:** `REST_FRAMEWORK` sin `DEFAULT_THROTTLE_CLASSES` (`config/settings/base.py:93-98`); `urls.py:25` TokenPairView sin throttle_scope; nginx sin limit_req.
- **Impacto:** brute-force/credential-stuffing en `POST /auth/token/`.
- **Recomendación:** throttling ScopedRateThrottle + nginx limit_req.

### SEC-06 · MEDIO · `print()` de datos de usuario/roles en flujo de producción
- **Evidencia:** `verificacion/services/evaluar_checklist.py:164` y `:170` (imprime usernames, roles, comparaciones de facultad).
- **Impacto:** fuga de información a stdout/logs del contenedor; RNF-015 incumplido (no logging).
- **Recomendación:** eliminar o mover a `logging.debug`; añadir `LOGGING` en settings.

### SEC-07 · MEDIO · Rutas internas de disco expuestas en respuestas API
- **Evidencia:** `archivo_path` (o equivalente) en `peticiones/adapters/serializers.py:93,129`, `verificacion/adapters/serializers.py:173`, `resoluciones/adapters/serializers.py:26,50`.
- **Impacto:** discovery de estructura de filesystem; INFO en seguridad mínima-privilegio (P-07).
- **Recomendación:** remover del output público o renombrar como identificador opaco.

### SEC-08 · MEDIO · `SECRET_KEY` compartida como clave de firma JWT
- **Evidencia:** `config/settings/base.py:105` (`SIGNING_KEY = env("SECRET_KEY")`).
- **Impacto:** rotación acoplada; comprometer Django secretas compromete todos los JWT.
- **Recomendación:** claves separadas + calcular con rotación/blacklist. Además `ROTATE_REFRESH_TOKENS=False` (`:101-106`).

### SEC-09 · MEDIO · IP de auditoría siempre NULL
- **Evidencia:** `notificaciones/adapters/signals.py:32-37` — `_get_current_request()` devuelve `None` siempre; campo `ip` del `EventoAuditoria` no se llena con `X-Forwarded-For`.
- **Impacto:** trazabilidad forense incompleta (RN/constitución P-08 ini plenitud exigida).
- **Recomendación:** Crequest (django-request-id) o middleware de IP.

### SEC-10 · MEDIO · Sin configuración CORS y sin CI de seguridad
- **Evidencia:** grep de corsheaders = 0 en src;.github sin workflows (solo PR template). security_report.md (T044) corrió Bandit/Gitleaks/Safety manualmente: DRF 3.16.1 usado en prod con 2 CVEs (plan de upgrade a ≥3.17.2 documentado pero no ejecutado).

### SEC-11 · BAJO · Elementos de higiene de seguridad
- `seed_initial_data.py:60` — contraseña demo hardcodeada `"SgtDemo2026!"` (documentada como demo; riesgo si se ejecuta en producción: 8 cuentas con clave común).
- `verify_all_tasks.py:391-392` — SECRET_KEY/DB_PASSWORD de prueba hardcodeadas en el repo.
- `backend/.gitleaksignore` — en formato TOML inválido para gitleaks (espera fingerprints).
- `gitleaks.exe` (binario de 16 MB commiteado).
- ROOT `.gitleaksignore` correcto en formato fingerprints, en cambio.

### Fortalezas de seguridad verificadas
- Defaults seguros provienen del `DEBUG` (default False), `ALLOWED_HOSTS` (default vacío), `SECRET_KEY` (sin fallback) en `settings/base.py:11-13`.
- Almacenamiento privado sin URL pública (`local_storage.py:25-35`); descarga JWT→404 anti-enumeración (`peticiones/adapters/views.py:230-282`).
- MD5 hasher usado **solo** en settings de test (`test.py:12-14`).
- Validación PDF correcta: magic bytes + SHA-256 streaming + límite 10MB; dependencia con tests que rechazan ejecutables renombrados/imágenes.
- R针织 todos los services con autorización en try/catch de failure y mundo cerrado.

## B. Calidad de código / pruebas (medido)

### B.1 Resultados reales de ejecución (evidencia: corrida pytest 01-nov-2026)
- **suite principal (`testpaths=src/apps`): 464 coleccionados → `50 failed, 390 passed, 24 errors`** (~5 min de ejecución, SQLite in-memory).
- **Cobertura medida: TOTAL 88%** (7267 stmts / 855 miss). Cobertura **productiva** por módulo relevante:
  - ✅ sólido: core pdf_validation (100%), crear/enviar expediente (100%), peticiones services (90-100%), authentication (97-100%), models (88-100%).
  - ⚠️ bajo: `resoluciones/services/declarar_aptitud.py` **35%**, `verificacion/adapters/views.py` **65%**, `resoluciones/adapters/views.py` **74%**, `resoluciones/services/emitir_informe.py` **62%**.
- **suites excluidas por defecto** (pyproject `testpaths=["src/apps"]`):
  - `src/core/tests`: **26/26 pasan** (server execution).
  - `tests/e2e`: **3/4**; el flujo completo (test_flujo_completo…) **FALLA** con `PermissionError: /app/backend/src/media` en la subsanación.
- Fallos agrupados (causa raiz): PermissionError de rutas de PDF/storage — 74 de 74 fallos/errores.
  - ⚠️ 5 FAILED en notificaciones y 1 FAILED en notification_service **por el PermissionError de PDF** (notify… informe emitido genera PDF). Los test de auditoría no pasan.

### B.2 Configuración de pruebas
- `pyproject.toml`: pytest settings correctos (settings.test, pythonpath src) pero **sin `--cov` addopts ni `fail_under`** — cobertura no exigible.
- Tests unitarios usan SQLite; constitución P-14 exigía "pruebas de integridad/rollback/concurrencia con **PostgreSQL real**" — **incumplido en la configuración actual** (sin configuración de test para_postgres).
- Duplication modules: `test_notifications_and_audit.py` en 2 paquetes distintos.

### B.3 Problemas de estilo verificados
- Código de clase muerta sin URLs: `PeticionDocumentalViewSet`, `ObservacionViewSet`.
- Import widgets: `models` import a mitad de archivo (`peticiones/services/cargar_documento.py:52-53`), `validar_checklist_completo` al final (`resoluciones/adapters/views.py:224`).
- Serializadores de request duplicados inline en views de resolución (dos veces cada uno).
- TODO REAL: `emitir_informe.py:69-70` ("Computación", "FEIRNNR" hardcodeados).
- Responsabilidad RBAC quebrada en distintas capas (matriz + service + compare objetos) — correcto riesgo de drift alto.
- Docstrings correctos y en español CONSISTENTES; nombre de funciones en español — bien.

## C. Mantenibilidad
- +Flake8/mypy/black configurados (no ejecutados por CI; la auditoría no correó flake8).
- Sin dependabots ni renovate; safety identifica CVEs transitorios en dev deps (informe ya existía).
- README intenta disipar medias verdades → no coincide con realidad; commit_msg.txt generado manual undermines contracto de repo.

## D. Resumen del estado de cumplimiento de seguridad
| Área | Status |
|---|---|
| Autenticación JWT | OK (con mejoras: rotación, throttling) |
| Autorización RBAC | ALTA (mundo cerrado consistent), 1 defecto (SEC-03) |
| Validación entrada | ALTA (PDF, tamaño, serializers) |
| Integridad de datos transaccional | ALTA (atomic+select_for_update) |
| Integridad de evidencia documental | BAJA (SEC-01, SEC-02, A-01) |
| Operación de despliegue | BAJA (SEC-04, A-04, sin TLS/healthcheck) |
| Observabilidad | BAJA (SEC-06, SEC-09, sin LOGGING) |
| Cadena de suministro | MEDIA (informe T044, DRF CVE pendiente) |
