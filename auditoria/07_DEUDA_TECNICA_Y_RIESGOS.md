# 07 — DEUDA TÉCNICA Y RIESGOS

Formato: **ID · Prioridad · Problema · Impacto · Recomendación**. Ordenados por prioridad. Evidencias en 06 y 03.

## 1. Deuda CRÍTICA (resolver antes de continuar el desarrollo SDD)

| ID | Problema | Impacto | Recomendación |
|---|---|---|---|
| D-01 | **Ruteo de almacenamiento hardcodeado**: `PDFGeneratorAdapter.output_dir="/media/private/resoluciones"` (`pdf_generator.py:48`) y ausencia de `PRIVATE_MEDIA_ROOT` en settings → `os.makedirs` en raíz del FS | 74 tests rojos (50 FAILED+24 ERROR); flujo informes/declaratorias inservible en cualquier host distinto; riesgo de escritura fuera de media | Inyectar `PrivateMediaStorage`/`MEDIA_ROOT` al PDF generator; definir `PRIVATE_MEDIA_ROOT` en `settings/base.py`; hacer E2E verde |
| D-02 | **Memorando N° 162 no persistido** (`declarar_aptitud.py:167-181`) | Pérdida de evidencia legal del trámite: base de datos apunta a un archivo inexistente | Guardar con `guardar_archivo_privado()` + test de existencia |
| D-03 | **Endpoint checklist GET inoperable** (sin celda RBAC) | RF-006 consulta rota para todos los roles | Añadir celda GET a `RBAC_MATRIX["checklist"]` + test |
| D-04 | **Suite de pruebas en regresión** (50F/24E) y suites E2E/`core.tests` **excluidas por defecto** (`testpaths=["src/apps"]`) | Impide iteración segura; Fases siguientes construirían sobre rojo | Corregido D-01 → `pytest --cov=src` con `fail_under≥70`, incluir `src/core/tests`, `tests/e2e` y `backend/tests` en testpaths |

## 2. Deuda ALTA

| ID | Problema | Impacto | Recomendación |
|---|---|---|---|
| D-05 | Despliegue "producción" en modo dev: `CMD runserver`, `config.settings.local`, `DEBUG:-1`, sin gunicorn, sin collectstatic, nginx sin TLS/rate-limit | Stacktraces, CVE de DRF 3.16.1 en prod (security_report), rendimiento y durée | Pipeline de deploy con settings.prod: gunicorn+DEBUG=0+collectstatic+TLS+limit_req; integrar Córdoba CICD |
| D-06 | **Sin repositorio Git** en la copia de trabajo | Tractería SDD (PR template, T/RF por commit) no certificable; cero respaldo | Inicializa git; conectar remote; permitir historia de evidence |
| D-07 | Sin throttling de login ni rotación de JWT refresh | Fuerza bruta, sesiones impemorable de token comprometidos | DRF throttling + `ROTATE_REFRESH_TOKENS=True` + blacklist |
| D-08 | **README/commit_msg con métricas falsas** (95% cobertura, 468 tests) | Minedo de confianza; auditorías futuras partem de mentira | Actualizar README con datos medidos; borrar commit_msg.txt |
| D-09 | `HistorialEstado` inconsistent en emisión de informe (`estado_anterior` = ya-estado-nuevo) | Histórico corrupto en la última etapa del trámite; P-08 (trazabilidad íntegra) afectada | Guardar snapshot antes del cambio (más fácil: tomar `estado_anterior` antes de `expediente.estado = ...`) |
| D-10 | Triple validación de permisos sin fuente única (RBAC_MATRIX + `has_role` en 5 servicios + belongs_to manual con strings) | Drift inminente (ya existe: analista en `declarar_aptitud` roles vs `RBACۂ MATRIX` decano-only en `declaratorias`) | Extraer helper `has_any_role()` en authentication; conectar `RBAC_MATRIX["declaratorias"]` con roles service |
| D-11 | ADRs faltantes (0004..0008) y duplicado divergente docs/ vs backend/docs | Gobernanza arquitectónica incompleta (RNF-018) | Consolidar en `docs/adr/` (única localidad oficial); deles los archivos de backend/docs |
| D-12 | Higiene de repo: `gitleaks.exe` (16 MB), `backend/README.md` de gitleaks, `commit_msg.txt`, 6 scripts one-shot con rutas Windows y secretos de prueba (`verify_all_tasks.py:391-392`, `check_files.py:3`) | Repo lleno; secretos decay en repos públicos futuros | Mover scripts a `scripts/` de CI (arreglado paths) o eliminarlos; borrar binario; escribir README backend real |

## 3. Deuda MEDIA

| ID | Problema | Impacto | Recomendación |
|---|---|---|---|
| D-13 | `archivo_path` y rutas internas expuestas en 4+ serializers | Info leak (P-07) | Quitar campos de salida pública |
| D-14 | `print()` debug en producción + sin LOGGING settings | Observabilidad nula; leaks | logging library + settings LOGGING |
| D-15 | Notificaciones en 2 vías (notification_service vs objects.create directas) | Inconsistencia y duplicación | Servicios usan notification_service centralizado |
| D-16 | Duplication `_create_observacion_and_notify` en 2 servicios | Cambios churn fácilmente desalineados | Extraer a notification_service |
| D-17 | Código muerto / recursos RBAC muertos (`PeticionDocumentalViewSet`, `ObservacionViewSet`, `expedientes:enviar` matrix, `catalogos:requisitos` en matriz sin vista) | Confusión de mantenimiento y resultado de API false | Eliminar os conectar |
| D-18 | `Dockerfile` no copia `pyproject.toml` ni `tests/` a la imagen; imagen no reproducible para QA (verificado: ImportError "No module named 'config'") | QA en contenedor imposible sin hacks | COPY pyproject.toml + tests en Dockerfile |
| D-19 | IP de auditoría NULL (`signals.py:32-37`) | Trazabilidad forense débil (P-08) | Cuestión de middleware CRequest |
| D-20 | Dup módulo nombre `test_notifications_and_audit.py` en 2 paquetes | Riesgo de colisión de imports en pytest cuando se combine | Renombrar uno |
| D-21 | Comparaciones de UUID via strings en 4 servicios | Bug latente de tipo; refactor hard | Normalizar a `.hex`/UUID en modelos antes de compare |
| D-22 | Sin CORS ni rate limiting nginx | Bloqueo de Fase 2 frontend | Activar corsheaders en Fase 2 |
| D-23 | `pdf_generator` plantilla fija "Computación"/"FEIRNNR" (TODO en `emitir_informe.py:69-70`) | Incorrecta para otras carreras/facultades (design CAD multiplicar) | Consumir catálogos/modelos reales |
| D-24 | Bandeja y descargas: dependencias implícitas `carrera_id/facultad_id no-null` en usuarios y expedientes | Bugs silenciosos si admin crea usuarios sin carrera | Defaults o validación de modelo |
| D-25 | `.gitleaksignore` backend formato inválido (TOML) | Gitleaks no procesa lista; exclusión de tests deja de funcionar | Mover a `gitleaks.toml` correcto |

## 4. Riesgos (gestión proactiva)

| Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|
| Continuar Fase 2 (frontend) sobre backend roto (D-01..D-03) | Alta | Alto |FREEZE de nuevas tareas hasta verde+-tests incluidos en CI |
| Despliegue "producción" ofrecen sin gunicorn/TLS en entregabilidad institucional real | Alta | Alto | D-05 |
| `seed_initial_data` ejecutada en producción con password común | Media | Alto | D-12 + rotación obligatoria en producción |
| Pérdida de trámite legal (memorando) jurídicamente cuestionable (D-02) | Media | Alto | Persist + verificación de existencia |
| Cambio de año (correlativo `EXP-YYYY-NNNN` basado en string ordering de año+0001..9999) | Baja | Medio | Test de rollover año + collision guard `select_for_update` ya parcial |
| RNF-005 (p95<500 ms) nunca medido → cumplimiento no importado | Alta | Medio | Locust en Fase 2 |

## 5. Resumen de deuda por severidad
- **CRÍTICO (4):** D-01..D-04 — todos de raíz única estructural (almacenamiento + RBAC + suite roja).
- **ALTO (8):** D-05..D-12 — despliegue, metodología, contract de repo.
- **MEDIO (13):** D-13..D-25 — consistencia, observabilidad, robustez.
- **BAJO:** higiene menor (docstrings, naming, renombrar modules, sanctorios de config).
