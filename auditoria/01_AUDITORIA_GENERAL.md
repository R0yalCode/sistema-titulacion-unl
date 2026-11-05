# 01 — AUDITORÍA GENERAL DEL PROYECTO SGT-SIAAF

**Fecha:** 01-nov-2026 · **Modo:** solo lectura (no se modificó ningún archivo existente; los 8 informes se crean en `auditoria/`)
**Alcance auditado:** repositorio `Sistema_Titulacion` completo (backend, docs SDD, Docker, nginx, scripts raíz).

---

## 1. Descripción del proyecto

**SGT-SIAAF** (Sistema de Gestión del Trámite de Titulación integrado al SIAAF) — FEIRNNR, Universidad Nacional de Loja. Automatiza el subproceso de **Declaratoria de Aptitud Legal (Art. 235 RRA-UNL)**: solicitud estudiantil → recepción con nº de providencia → plazo de 8 días laborables → checklist de 5 requisitos → observaciones/subsanación → informe legal N° 590 → declaratoria N° 162.

**Metodología declarada:** Spec-Driven Development (SDD), Fase 1/MVP = backend API. Fase 2 (sustentaciones/web) y Fase 3 (SENESCYT/móvil) documentadas y pendientes por diseño.

## 2. Estado general

| Dimensión | Veredicto |
|---|---|
| Funcionalidad MVP backend | **Sustancialmente implementada** (ﬂujo FL-01→FL-05 funciona end-to-end en servicios; 19 endpoints activos) |
| Calidad de pruebas | **REGRESIONADA**: 464 tests ejecutados → **390 OK / 50 FAILED / 24 ERROR** (≈84% de éxito). Cobertura medida: **88%**, no el 95% que declara el README |
| Despliegue | **Funciona** con Docker Compose (db healthy, migraciones y seed OK, API responde) pero con **configuración de desarrollo** (runserver, DEBUG=1, settings.local) — no apto como "producción" |
| Cumplimiento SDD | **Alto en estructura documental** (constitution/specify/plan/tasks densamente trazadas), con **vacíos materiales**: ADRs faltantes (3 de 8), plantillas y ADRs spec-level en 0 bytes, esquema de principios constitucionales inconsistente (P-01..P-18 citados como C-001..C-020), tareas sin marca de estado (0/46 marcadas) |
| Control de versiones | **La copia de trabajo NO es un repositorio Git** (no existe `.git`): la trazabilidad por commits prometida por la metodología SDD no es verificar en esta máquina |
| Integración SIAAF/SGA | **Simulada y honesta** (`SGAMockAdapter` con fixtures JSON, sin cliente HTTP), conforme a P-01/DEC-05 |

## 3. Tecnologías (verificadas en `backend/requirements.txt`)

Django 5.2.x (5.2.18 en imagen) · DRF 3.18.x · SimpleJWT 5.5.x · psycopg 3.3.x (PostgreSQL 16) · django-environ · drf-spectacular 0.30 (Swagger/ReDoc) · ReportLab 4.5 (PDF) · pytest/pytest-django/pytest-cov · Docker Compose + nginx 1.24.

**No existe frontend** (compatible con el alcance Fase 1).

## 4. Arquitectura real

Monolito modular Django con **arquitectura hexagonal declarada**:

- `src/config/` — settings por entorno (base/local/test), urls centralizado (todos los routers en un solo archivo, sin routers DRF).
- `src/core/` — `ports/` (ABC + dataclasses frozen: puerto `ISGALegacyPort`), `adapters/` (`mock_sga.py`, `pdf_validation.py`, `local_storage.py` `PrivateMediaStorage`, `scope_filter.py` anti-IDOR).
- `src/apps/<app>/{adapters,domain,services,tests}` — 6 apps (authentication con RBAC matricial en `adapters/permissions.py`; expedientes con state machine + `PlazoLaboralCalculator` puro; peticiones con ingesta PDF; verificación (checklist/observaciones); resoluciones (PDF ReportLab); notificaciones (in-app + `EventoAuditoria` JSONB vía signals)).

**Distancia a la arquitectura propuesta:** cercana, pero con violaciones observables: dominio no es 100% puro (`plazo_calculator` usa `django.utils.timezone`), import de `validar_checklist_completo` al final del módulo de vistas (`resoluciones/adapters/views.py:224`), `_checklist Arnold` (`models` importado a mitad de archivo en `peticiones/services/cargar_documento.py:52-53`), y acoplamiento por competencias lógica de negocio duplicada entre servicios.

## 5. Fortalezas (verificadas)

1. **Aislamiento IDOR robusto**: `ScopeFilterMixin` (`core/adapters/scope_filter.py:43-67`) + verificación manual reforzada en descargas (404 anti-enumeración: `peticiones/adapters/views.py:230-282`).
2. **RBAC mundo-cerrado**: matriz declarativa 8 roles × recurso × método (`authentication/adapters/permissions.py:24-110`); recurso no declarado ⇒ denegado.
3. **Validación PDF efectiva**: magic bytes `%PDF-` + SHA-256 streaming + límite 10 MB (`core/adapters/pdf_validation.py`).
4. **Media privada sin URL pública**: `base_url=None` + `url()` lanza `NotImplementedError` (`local_storage.py:25-35`).
5. **Transacciones + bloqueo pesimista**: `transaction.atomic()` + `select_for_update()` consistente en todos los servicios (expedientes, peticiones, verificación, resoluciones).
6. **Auditoría inmutable JSONB** vía signals fail-safe (`notificaciones/adapters/signals.py`) y notificaciones 100% in-app conforme DEC-01.
7. **Defaults de settings seguros**: `DEBUG` default False, `ALLOWED_HOSTS` default [], `SECRET_KEY` sin fallback (`config/settings/base.py:11-13`).
8. **Salud documental SDD** del artefacto `tasks.md` (46 tareas, 8 paquetes, matriz RF/RNF↔T) — mejor que la media en proyectos académicos.
9. **Reproducibilidad**: `docker compose up` levanta el sistema completo y con seed idempotente funcional (verificado en la sesión).

## 6. Debilidades (verificadas — detalle en 06/07)

- **CRÍTICO S1** — El `PDFGeneratorAdapter` usa `output_dir` absoluto hardcodeado `/media/private/resoluciones` (`resoluciones/adapters/pdf_generator.py:48`): intenta `os.makedirs` en la raíz del FS del contenedor. Es la causa directa de **74 fallos/errores de test** (PermissionError) y lo invalida en cualquier host.
- **CRÍTICO S2** — `declarar_aptitud` **nunca persiste el memorando N° 162 firmado**: valida el PDF, construye un path nominal y no llama a `guardar_archivo_privado` (`resoluciones/services/declarar_aptitud.py:167-181`) → **se pierde la evidencia legal del documento**.
- **CRÍTICO H1** — Endpoint `GET /api/v1/expedientes/{id}/checklist/` (recurso `checklist`, método `GET`) **no tiene celda en `RBAC_MATRIX`** (`permissions.py:77-93`) ⇒ دنیega siempre (403): endpoint inoperable.
- **BUG** — `emitir_informe` guarda `estado_anterior` = estado ya cambiado (INFORME_EMITIDO) en `HistorialEstado` (`emitir_informe.py:199-211`; correcto en `declarar_aptitud.py:189-194`).
- **Servidor de desarrollo en contenedor**: `CMD runserver` (`Dockerfile:25`) + `config.settings.local` con `DEBUG` forzado (`compose:29-30`) — contradice P-14/RNF-016.
- **`print()` con datos de usuarios/roles en producción** (`verificacion/services/evaluar_checklist.py:164,170`).
- **`archivo_path` (ruta interna de disco) expuesta** en 4+ serializadores (`peticiones/adapters/serializers.py:93,129`; `verificacion/adapters/serializers.py:173`; `resoluciones/adapters/serializers.py:26,50`).
- Hardcodes institucionales "Computación"/"FEIRNNR" (TODO real: `emitir_informe.py:69-70`).
- Código muerto: `PeticionDocumentalViewSet` (`peticiones/adapters/views.py:285-303`), `ObservacionViewSet` (`verificacion/adapters/views.py:169-239`).
- **No hay CI** (sólo plantilla PR en `.github/`), **no hay `fail_under` de cobertura**, `staticfiles` nunca se recolecta, IP de auditoría siempre NULL (todo en `signals.py:32-37`).
- **Higiene**: `backend/gitleaks.exe` (binario Windows 16 MB commiteado), `backend/README.md` es el README upstream de gitleaks (no del proyecto), `commit_msg.txt`, 6 scripts one-shot en raíz con rutas Windows (`C:\Users\DELL\OneDrive\...`), `contracts/openapi.yaml` duplicado byte-a-byte.

## 7. Riesgos (síntesis)

| Riesgo | Severidad detecada |
|---|---|
| Pérdida del memorando firmado (integridad de trámite legal) | CRÍTICO |
| Re-deploy en host sin `/media/` rompe generación de PDF / todo el flujo post-verificación | CRÍTICO |
| Uso de `runserver`/DEBUG en "despliegue" (señalesDEBUG leak, sin TLS ni TLS1.3 real, sin gunicorn) | ALTO |
| Sin rate-limiting ni throttling en login (fuerza bruta) | ALTO |
| `SECRET_KEY` reutilizada como `SIGNING_KEY` JWT (`base.py:105`) | MEDIO |
| Sin rotación de refresh tokens ni blacklist (`ROTATE_REFRESH_TOKENS=False`) | MEDIO |
| Documentación operativa que contradice a la real (README "95% cobertura", "468 tests") | MEDIO |
| Sin repositorio git activo en está copia: no history = no trazabilidad SDD demostrable | ALTO (metodológico) |

## 8. Conclusiones

SGT-SIAAF es un **backend MVP plausiblemente construido, con base arquitectónica sólida (hexagonal real y disciplina transaccional), pero en un estado de regresión de calidad medible**: ~1 de cada 6 pruebas en la suite principal falla por una única causa técnica raíz (rutas de almacenamiento hardcodeadas) y con bloqueos funcionales puntuales (endpoint de checklist, memorando no persistido). La documentación SDD es abundante y trazable en texto, aunque **inconsistente en su anclaje constitucional y con vacíos materiales (ADRs faltantes, plantillas vacías, estados de tareas sin marcar)**. El despliegue funciona, pero **no debe comercializarse como producción**: es una composición de desarrollo (runserver + DEBUG).

**Prioridad #1 antes de continuar con nuevas tareas SDD:** estabilizar la capa de almacenamiento (integrar `pdf_generator` a `PrivateMediaStorage`/`MEDIA_ROOT`), restaurar el suite a verde, habilitar el endpoint de checklist y persistir el memorando firmado. Después de eso, el proyecto está listo para retomar el flujo SDD.
