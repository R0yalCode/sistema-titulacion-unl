# Inventario general del proyecto SGT-SIAAF

**Objetivo:** registrar, con evidencia verificable, la estructura real del repositorio antes de producir o consolidar documentación técnica para la Evaluación Sumativa 1.

**Método:** inspección directa del árbol de archivos y del código fuente (`find`, `grep`, lectura de archivos). No se asume ningún dato no observado. Fecha de corte de este inventario: 2026-11-06.

---

## 1. Estructura de directorios de primer nivel

| Carpeta | Contenido | Estado |
|---|---|---|
| `backend/` | Backend Django/DRF (fuente de verdad del dominio) | Activo, con pruebas |
| `frontend/` | SPA React (titulación, en desarrollo por fases F0–V04) | Activo, con pruebas |
| `sgt-siaaf/.specify/` y `sgt-siaaf/specs/` | Artefactos GitHub Spec Kit (constitución, specify, clarify, plan, tasks) | Activo |
| `diseno-ui/` | Especificaciones de diseño UI (`titulacion-v2/especificaciones/01…08`) | Activo, referencia normativa del frontend |
| `SGT_SIAAF_Prototipo_HTML_CSS_JS/` y `SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/` | Prototipos A/B (HTML/CSS/JS) | Solo referencia visual/tono; prohibido copiar código (AGENTS.md §3.4) |
| `auditoria/` | 8 informes de auditoría técnica (01–08) | **Desactualizado respecto a `docs/`** — ver `AUDITORIA_DOCUMENTAL.md` |
| `docs/` | Portal Quarto (sitio técnico) ya scaffoldeado con 9 capítulos + ADR + anexos + auditoría backend + indicadores + sprint S1 | Activo, parcialmente desincronizado con el estado más reciente del frontend (ver hallazgo H-02) |
| `.github/` | `workflows/security.yml`, `dependabot.yml`, `safety-policy.yml`, plantilla de PR | Activo; **no existe workflow de publicación Quarto/Pages** |
| `nginx/` | `nginx.conf`, `prod.conf` | Activo |
| `docker-compose.yml`, `docker-compose.prod.yml`, `Dockerfile` | Orquestación dev y prod | Activo |
| `.venv/` | Entorno virtual Python local | Infraestructura local, no versionable |
| Scripts raíz (`audit_complete.py`, `audit_tasks.py`, `check_files.py`, `check_t047.py`, `verify_all_tasks.py`, `verify_matrix.py`) | Scripts de verificación ad hoc | Preexistentes; no se modifican (regla 2.3) |

No existe carpeta `.git` en esta copia de trabajo (confirmado por el entorno de ejecución). Por instrucción explícita de la tarea, el apartado de control de versiones queda **excluido** de esta auditoría (sección 2.4 del prompt maestro).

---

## 2. Backend Django — aplicaciones y módulos

Arquitectura declarada: **monolito modular con arquitectura hexagonal** (`core/ports`, `core/adapters`, y por cada app `adapters/`, `domain/`, `services/`, `tests/`).

| App | Modelos ORM (`adapters/models.py`) | Serializers | ViewSets/Views | Servicios de dominio | Archivos de prueba |
|---|---|---|---|---|---|
| `authentication` | Sí (usuario/rol) | 1 clase | 1 clase | 0 (lógica en permissions) | 6 |
| `expedientes` | Sí | 6 clases | 4 clases | 2 archivos | 7 |
| `peticiones` | Sí | 7 clases | 6 clases | 2 archivos | 5 |
| `verificacion` | Sí | 8 clases | 7 clases | 4 archivos | 4 |
| `resoluciones` | Sí | 2 clases | 7 clases | 2 archivos | 5 |
| `notificaciones` | Sí | 2 clases | 1 clase | 1 archivo | 5 |
| `core` (transversal) | — | — | — | `ports/` (interfaces ABC), `adapters/` (`mock_sga.py`, `pdf_validation.py`, `local_storage.py`, `scope_filter.py`, `middleware.py`) | 2 |

Total de archivos de prueba localizados: **32** en `apps/*/tests` + **2** en `core/tests` = **34** archivos de prueba (recuento de archivos, no de casos; el recuento de casos se trata en Fase 7).

**Middleware activo** (`backend/src/config/settings/base.py`): `ThreadLocalRequestMiddleware` (propio, para auditoría) + stack estándar de Django (`SecurityMiddleware`, `SessionMiddleware`, `AuthenticationMiddleware`, `MessageMiddleware`, `CommonMiddleware`, `CsrfViewMiddleware`, `XFrameOptionsMiddleware`).

**Configuración por entorno** (`backend/src/config/settings/`): `base.py`, `local.py`, `production.py` (142 líneas — existe, a diferencia de lo que afirma `auditoria/01_AUDITORIA_GENERAL.md`), `test.py`.

**Migraciones** (`*/migrations/*.py`, sin `__init__.py`): `authentication` 1, `expedientes` 4, `notificaciones` 2, `peticiones` 3, `resoluciones` 1, `verificacion` 1.

**URLs**: enrutamiento centralizado en `backend/src/config/urls.py` (21 declaraciones `path(...)`), sin routers DRF automáticos (confirmado en `auditoria/01`).

**OpenAPI**: `backend/openapi.yaml` (1224 líneas), generado con `drf-spectacular`. Existe copia adicional en `backend/contracts/` señalada como duplicado en `auditoria/01` (pendiente de confirmar si sigue duplicada byte a byte — ver hallazgo H-03).

**Docker**: `docker-compose.yml` (servicios `db`, `backend`, `nginx`; redes/volúmenes `backend_net`, `postgres_data`, `media_data`, `static_data`) con `DJANGO_SETTINGS_MODULE=config.settings.local` y `DEBUG` por defecto `1`. `docker-compose.prod.yml` referencia `config.settings.production`. El `Dockerfile` por defecto usa `CMD ["python","manage.py","runserver",...]` con `ENTRYPOINT ["./entrypoint.sh"]` — pendiente verificar si `docker-compose.prod.yml` sobreescribe el comando con un servidor WSGI/ASGI de producción (ver hallazgo H-04, Fase 8).

---

## 3. Frontend React — estructura

`frontend/src/` organizado en `api/` (endpoints y tipos), `app/`, `auth/`, `components/{ui,layout,feedback}/`, `features/{auth,dashboard,bandeja,solicitud,expediente,peticiones,no-habilitado}/`, `lib/`, `mocks/` (MSW), `styles/` (incluye `tokens.css`), `test/`, `types/`.

Estado funcional según `CLAUDE.md` (fuente de verdad más reciente, 2026-11-05/06): F0–F2.5 cerradas, V-01 a V-04 cerradas, **328/328 pruebas** sin regresiones al cierre de V-04. V-05 y fases posteriores **sin iniciar**.

---

## 4. Documentación y especificación existentes (SDD)

| Ubicación | Contenido |
|---|---|
| `sgt-siaaf/.specify/memory/constitution.md` | Constitución del proyecto (intocable) |
| `sgt-siaaf/specs/001-tramite-titulacion/` | `constitucion.md`, `specify.md`, `clarify.md`, `plan.md`, `tasks.md`, `adr/ADR-001-arquitectura.md`, `adr/ADR-002-limites-modulares.md` (backend, Fase 1) |
| `sgt-siaaf/specs/003-frontend-titulacion/` | `specify.md`, `clarify.md`, `plan.md`, `tasks.md` (frontend, vigente) |
| `diseno-ui/ui/titulacion-v2/especificaciones/01…08` | Especificaciones visuales normativas del frontend; `08` = estados de error |
| `docs/adr/0001…0002` | ADR duplicados/paralelos a los de `specs/001` — requiere consolidación (ver auditoría documental) |

**Nota:** no existen `specs/002-*` ni `specs/004-*` en el repositorio (confirmado por `find`); `AGENTS.md` y `CLAUDE.md` ya documentan explícitamente esta ausencia.

---

## 5. Documentación técnica ya generada (fuera de `specs/`)

### 5.1 Carpeta `auditoria/` (raíz) — 8 informes, 01-nov-2026

`01_AUDITORIA_GENERAL.md`, `02_INVENTARIO_TECNICO.md`, `03_MATRIZ_FUNCIONAL.md`, `04_AUDITORIA_ARQUITECTONICA.md`, `05_AUDITORIA_SDD.md`, `06_AUDITORIA_SEGURIDAD_Y_CALIDAD.md`, `07_DEUDA_TECNICA_Y_RIESGOS.md`, `08_RECOMENDACIONES_DE_MEJORA.md` (588 líneas en total).

### 5.2 Carpeta `docs/` — portal Quarto, 107 archivos, mayormente 05-nov-2026

Estructura completa ya scaffoldeada: `01-introduccion/` a `09-calidad/` (9 capítulos numerados), `adr/`, `anexos/`, `auditoria/` (informe técnico posterior al de la raíz), `auditoria-backend/` (informe final de validación + subcarpeta `seguridad/` con 5 informes y una subcarpeta `plan-implementacion/` con 10 documentos adicionales), `frontend/` (guía de vistas e implementación), `indicadores/`, `sprint-S1/` (7 documentos de un sprint de estabilización), `_quarto.yml`, `index.qmd`, `RESUMEN_EJECUTIVO.md`, `security_report.md`.

Diagramas C4 existen como **texto Mermaid embebido en Markdown** (`docs/02-arquitectura/c4/{contexto,contenedores,componentes,codigo}.md`), no como archivos fuente Structurizr DSL independientes. **No se localizó ningún archivo `.bpmn`, `.puml`, `.dsl`, `.svg` ni `.png`** en `docs/` (verificado con `find`): los diagramas BPMN, C4 "formal" (Structurizr) y UML en PlantUML que pide el prompt maestro **no existen como artefactos fuente separados** — ver matriz de cumplimiento inicial.

### 5.3 Otros documentos de auditoría

`docs/security_report.md` (179 líneas) — informe de seguridad independiente del de `auditoria-backend/`.

---

## 6. CI/CD y automatización

Único workflow existente: `.github/workflows/security.yml` (seguridad/dependencias, junto con `dependabot.yml` y `safety-policy.yml`). **No existe** `publish-quarto.yml` ni ningún workflow de construcción/publicación del sitio Quarto. Quarto CLI **no está instalado** en este entorno (`which quarto` sin resultado) — el sitio no ha podido renderizarse ni verificarse localmente en esta sesión.

---

## 7. Hallazgos de inventario que alimentan la auditoría documental

- **H-01**: `auditoria/01_AUDITORIA_GENERAL.md` (01-nov-2026) reporta como críticos tres defectos que el código actual ya no presenta: (a) ruta de salida de PDF hardcodeada — el código actual usa `PRIVATE_MEDIA_ROOT`/`MEDIA_ROOT` configurable; (b) `declarar_aptitud` sin persistir el memorando — el código actual llama a `guardar_archivo_privado`; (c) ausencia de `checklist` en `RBAC_MATRIX` — el código actual sí declara esa clave. Verificado por `grep` directo sobre el código fuente el 2026-11-06.
- **H-02**: `docs/RESUMEN_EJECUTIVO.md` (05-nov-2026) reporta "Frontend 198 passed / 0 failed (43 archivos)", mientras que `CLAUDE.md` (mismo día, checkpoint posterior) reporta 328/328 tras el cierre de V-04. El snapshot de `docs/` quedó desactualizado dentro del mismo día por la velocidad de avance del frontend.
- **H-03**: posible duplicado de `openapi.yaml` entre `backend/openapi.yaml` y `backend/contracts/` señalado por `auditoria/01`; pendiente de reverificación en Fase 5 (API).
- **H-04** (corregido en Fase 8, tras un error propio de la Fase 3): existe `backend/src/config/settings/production.py` y `docker-compose.prod.yml`, lo que ya contradecía la afirmación de `auditoria/01` de que "no existe `production.py`" — esa parte sigue siendo correcta. Sin embargo, la Fase 3 de este trabajo concluyó erróneamente que el contenedor "siempre sirve con Gunicorn" en todos los entornos, por una lectura incompleta del `Dockerfile` (que está en la **raíz del repositorio**, no en `backend/`): es un Dockerfile multi-stage con targets `development` (sin `entrypoint.sh`, `CMD runserver`, usado por `docker-compose.yml`) y `production` (con `entrypoint.sh` → Gunicorn, usado por `docker-compose.prod.yml`). Verificado en Fase 8 (lectura completa del `Dockerfile`): **el `docker-compose.yml` por defecto SÍ ejecuta `runserver`** — la afirmación original de `auditoria/01` sobre "servidor de desarrollo en contenedor" era correcta para ese compose. Ver `DOCUMENTACION/08_DESPLIEGUE/ARQUITECTURA_DOCKER.md` §2 para el análisis definitivo.
- **H-05**: no existen archivos fuente de diagramas BPMN/C4-Structurizr/PlantUML en el repositorio; los C4 actuales son Mermaid embebido, no Structurizr DSL como pide el prompt maestro (Fase 3).

Estos hallazgos se detallan y clasifican en `AUDITORIA_DOCUMENTAL.md` y se traducen en brechas en `MATRIZ_CUMPLIMIENTO_INICIAL.md`.
