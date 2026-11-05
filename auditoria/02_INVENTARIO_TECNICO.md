# 02 — INVENTARIO TÉCNICO

Inventario real del repositorio (180 archivos, excluido `.git` que no existe). Verificado por `find`.

## 1. Árbol de directorios raíz

```
Sistema_Titulacion/
├── auditoria/                    ← (nuevo: 8 informes de esta auditoría)
├── backend/                      ← TODO el código fuente (único código aplicacional)
│   ├── contracts/openapi.yaml    ← duplicado byte-a-byte de backend/openapi.yaml
│   ├── docs/adr/0001, 0002, 0003 ← ADRs backend
│   ├── openapi.yaml              ← contrato OpenAPI (17 paths / 18 operaciones)
│   ├── gitleaks.exe              ← ❌ binario Windows 16 MB (residuo)
│   ├── commit_msg.txt            ← ❌ residuo de sesión
│   ├── README.md                 ← ❌ es el README upstream de gitleaks, no del proyecto
│   ├── manage.py, requirements.txt, requirements-dev.txt, pyproject.toml
│   ├── .env.example, .bandit, .flake8, .gitleaksignore, LICENSE
│   ├── src/
│   │   ├── config/ (settings base/local/test, urls.py, wsgi/asgi)
│   │   ├── core/ (ports, adapters: mock_sga, pdf_validation, local_storage, scope_filter + tests)
│   │   └── apps/ (6 apps × adapters/domain/services/tests)
│   └── tests/e2e/test_full_workflow.py   ← NO copiado a la imagen Docker; excluido de testpaths
├── docs/
│   ├── adr/0001, 0002            ← duplicados (contenido divergente) de backend/docs/adr
│   └── security_report.md        ← informe Bandit/Gitleaks/Safety (T044)
├── nginx/nginx.conf
├── docker-compose.yml · Dockerfile · .dockerignore · .env · .gitignore
├── .gitleaksignore · .github/PULL_REQUEST_TEMPLATE.md (sin workflows CI)
├── README.md · LICENSE
├── 🛑 scripts one-shot de raíz (residuos, rutas Windows): audit_complete.py,
│   audit_tasks.py, check_files.py, check_t047.py, verify_all_tasks.py, verify_matrix.py
└── sgt-siaaf/                    ← artefactos SDD
    ├── .specify/memory/constitution.md        (Constitución v2.0, P-01..P-18)
    ├── .specify/templates/{spec,plan,tasks}-template.md   ← vacíos (0 bytes)
    └── specs/001-tramite-titulacion/
        ├── specify.md  plan.md  tasks.md  clarify.md
        └── adr/ADR-001-arquitectura.md, ADR-002-limites-modulares.md  ← vacíos (0 bytes)
```

## 2. Backend — módulos Django

| App | adapters | domain | services | tests |
|---|---|---|---|---|
| `authentication` | models (User UUID/cedula/carrera/facultad, Role, UserRole), serializers (claims JWT), views (TokenPairView), permissions.py (RBAC_MATRIX), management command `seed_initial_data` | vacío | vacío | 2 |
| `expedientes` | models (ExpedienteTitulacion 7 estados, HistorialEstado), serializers, views (ExpedienteViewSet, BandejaExpedienteViewSet) | plazo_calculator.py | crear_expediente, enviar_expediente | 6 |
| `peticiones` | models (CatalogoDocumental, PeticionDocumental 6 estados, DocumentoEntregado versionado), serializers, views (PeticionViewSet + clase muerta PeticionDocumentalViewSet) | vacío | solicitar_emision, cargar_documento | 4 |
| `verificacion` | models (ChecklistVerification, ObservacionAccionable), serializers, views (ChecklistListViewSet, ChecklistViewSet, ObservacionViewSet muerta) | vacío | evaluar_checklist, registrar_observacion, subsanar_requisito, validar_checklist_completo | 4 |
| `resoluciones` | models (InformeAptitud OneToOne, DeclaratoriaAptitud OneToOne), serializers, views (Informe/Declaratoria ViewSets), pdf_generator.py (796 líneas ReportLab) | vacío | emitir_informe, declarar_aptitud | 5 |
| `notificaciones` | models (NotificacionInterna, EventoAuditoria JSONB), serializers, views (NotificacionViewSet), signals.py (9 señales → 8 tipos de evento) | vacío | notification_service.py (despachador poco usado) | 4 |

`core`: `ports/__init__.py` (ABC `ISGALegacyPort`, dataclasses frozen `AsignaturaRecord`/`RecordAcademicoSGA`), `adapters/` (mock_sga + fixtures JSON, pdf_validation, local_storage, scope_filter) + 2 suites.

`config/settings`: `base.py` (defaults seguros, DRF/JWT/DB/estáticos), `local.py` (DEBUG=True), `test.py` (SQLite+MD5 hasher).

## 3. Endpoints reales (verificados contra `src/config/urls.py` y OpenAPI)

19 operaciones / 17 paths — todos bajo `/api/v1/`, drf-spectacular en `/schema/`, `/docs/`, `/redoc/`. Detalle completo en `03_MATRIZ_FUNCIONAL.md`. **No existe endpoint `/health/`** (RNF-006).

## 4. Dependencias (transcritas con rangos pinneados)

**requirements.txt (prod):** Django ≥5.2 <5.3 · djangorestframework ≥3.16 <4.0 · djangorestframework-simplejwt ≥5.5 <6.0 · psycopg[binary] ≥3.2 <4.0 · django-environ ≥0.12 <1.0 · drf-spectacular ≥0.27 <1.0 · reportlab ≥4.3 <5.0 (→ Pillow).
**requirements-dev.txt:** black, flake8, isort, mypy, pytest, pytest-django, pytest-cov.
**No incluidas:** gunicorn (ausente), CORS (ausente), celery/redis (por diseño), WeasyPrint (plan.md lo enumera; no está en requirements).

## 5. Infraestructura

| Artefacto | Contenido verificado |
|---|---|
| `Dockerfile` | python:3.12-slim, usuario no-root `django`, instala requirements **prod + dev**, `CMD runserver 0.0.0.0:8000` (:25). ❌ No copia `pyproject.toml`, `tests/`, ni ejecuta `collectstatic` |
| `docker-compose.yml` | db (postgres:16, healthcheck pg_isready), backend (config.settings.local, DEBUG default 1, sin healthcheck), nginx (8000→80). Volúmenes postgres_data/media_data/static_data |
| `nginx/nginx.conf` | proxy total `/` → `backend:8000`; sin rate-limit, sin servido de static/media, sin confinement a `/api/v1/` |

## 6. Documentación SDD

| Artefacto | Estado |
|---|---|
| Constitución (`constitution.md`) | OK — 18 principios P-01..P-18, 3 fases, modelo de 11 entidades |
| specify.md | OK — RF-001..RF-016, RNF-001..RNF-018, HU-001..HU-010, RN-001..RN-012, EX-001..EX-010, CA-001..CA-008, matriz §15 |
| plan.md | OK — decisiones técnicas, límites modulares, 5 paquetes semanales, lista 8 ADRs "Aceptados" |
| tasks.md | OK — T001..T046 (46 tareas, 8 paquetes). ❌ Ninguna marcada con [x]/[/] |
| clarify.md | OK — 8 asuntos (AP-01..AP-08), 5 decisiones (DEC-01..DEC-05), riesgos RSK-01..08 |
| adr/ (spec-level) | ❌ **0 bytes** (ADR-001 y ADR-002) |
| .specify/templates/* | ❌ **0 bytes** (3 plantillas) |
| ADRs `backend/docs/adr/` | Existen 0001, 0002, 0003 — **faltan 0004..0008** que plan.md declara "Aceptados" |
| ADRs `docs/adr/` | 0001, 0002 — **versiones divergentes** (no idénticas) de los de backend |

## 7. Elementos innecesarios / duplicados / desactualizados

| Elemento | Problema |
|---|---|
| `backend/gitleaks.exe` | binario PE32+ Windows x86-64, **16 MB** en un repo Django |
| `backend/README.md` | README upstream de gitleaks; no documenta el proyecto |
| `backend/commit_msg.txt` | borrador de commit (residuo) |
| `backend/contracts/openapi.yaml` | duplicado exacto (diff identico) de `backend/openapi.yaml` |
| 6 scripts de raíz | verificación one-shot de tasks.md; `check_files.py:3` y `verify_all_tasks.py:7,395,446` tienen rutas `C:\Users\DELL\OneDrive\...` no funcionales en otro equipo; `verify_all_tasks.py:391-392` embeddings de SECRET_KEY/DB_PASSWORD de prueba |
| `docs/adr` vs `backend/docs/adr` | dos copias divergentes de los ADRs 0001/0002 |
| Duplicidad `test_notifications_and_audit.py` | mismo nombre de módulo en `src/core/tests/` (12.6 KB, tests de SGA-mock) y `src/apps/notificaciones/tests/` (40.6 KB) — riesgo de colisión de nombres de módulo en pytest sin `__init__.py` |
| `.gitleaksignore` (backend) | in formato TOML `[allowlist]` con extensión `.gitleaksignore` — no es lectura válida para gitleaks (espera lista de fingerprints) |

## 8. Configuración de calidad

- `backend/pyproject.toml`: `DJANGO_SETTINGS_MODULE=config.settings.test`, `pythonpath=["src"]`, `testpaths=["src/apps"]` → **excluye `src/core/tests` y `tests/e2e` de la corrida por defecto**; **sin `fail_under` de cobertura**.
- `backend/.flake8`: max 88, ignora E203/W503, excluye migrations/.venv. `backend/.bandit`: excluye tests/migrations, skips B101.
- `.github/`: sólo `PULL_REQUEST_TEMPLATE.md` (bien orientado a trazabilidad TXXX/RF); **sin workflows CI**.

## 9. Conteo agregado

- Python aplicacional: ~6 apps × (models/serializers/views/services) + core + config ≈ **100 archivos .py de código + 24 de pruebas** (+1 E2E).
- Tests: **464 elementos en suite principal** (src/apps) + **26 en src/core/tests** (pasan) + **4 E2E** (3 pasan, 1 falla) = **494** contra los "468" del README.
- Código generado: OpenAPI 33.1 KB, ADRs 5 archivos reales (3 backend + 2 docs divergentes), security_report.md (180 líneas), scripts raíz 6 (~55 KB).
