---
title: "Decisiones de arquitectura (ADR)"
---

# Architecture Decision Records — SGT-SIAAF

**Objetivo de esta página:** consolidar las decisiones de arquitectura documentadas, citando su fuente real, y declarar explícitamente cuáles tienen evidencia documental formal y cuáles no, sin presentar como "decisión histórica confirmada" algo sin respaldo (regla del encargo, Fase 3).

## 1. Inventario real de ADR en el repositorio

| Ubicación | Archivo | Contenido |
|---|---|---|
| `docs/adr/0001-arquitectura-hexagonal-monolito-modular.md` | ADR-0001 | **Con contenido sustantivo** (56 líneas): decisión, alternativas, consecuencias |
| `docs/adr/0002-stack-django-drf-postgresql.md` | ADR-0002 | **Con contenido sustantivo** (77 líneas): stack completo con versiones y alternativas rechazadas |
| `sgt-siaaf/specs/001-tramite-titulacion/adr/ADR-001-arquitectura.md` | — | **Vacío (0 bytes)** — verificado por lectura directa en esta Fase 3 |
| `sgt-siaaf/specs/001-tramite-titulacion/adr/ADR-002-limites-modulares.md` | — | **Vacío (0 bytes)** — verificado por lectura directa en esta Fase 3 |

**Corrección respecto a la Fase 0 de este mismo trabajo**: inicialmente se catalogó esto como "dos conjuntos de ADR a reconciliar". Al leer el contenido completo se confirmó que no hay duplicación real — los archivos de `specs/001-tramite-titulacion/adr/` son plantillas nunca completadas. El único contenido ADR sustantivo de todo el repositorio está en `docs/adr/`. Este hallazgo ya lo había señalado `auditoria/01_AUDITORIA_GENERAL.md` ("plantillas y ADRs spec-level en 0 bytes"), y sigue vigente al 2026-11-06.

## 2. ADR-0001: Arquitectura Hexagonal con Monolito Modular

- **Identificador:** ADR-0001 (`docs/adr/0001-arquitectura-hexagonal-monolito-modular.md`)
- **Estado:** Aceptado (según el documento fuente)
- **Contexto:** necesidad de separar dominio de negocio y detalles técnicos, testabilidad aislada, evolución independiente de módulos.
- **Decisión:** Arquitectura Hexagonal (Ports & Adapters) combinada con Monolito Modular para el MVP.
- **Alternativas consideradas (según el documento):** arquitectura en capas tradicional (rechazada por acoplamiento a Django/BD), microservicios (rechazada por complejidad operacional excesiva para un proyecto académico), Clean Architecture pura (considerada similar, se prefirió Hexagonal por definición más clara de puertos).
- **Consecuencias declaradas:** testabilidad del dominio sin BD ni Django; mantenibilidad; preparación para Fases 2/3; curva de aprendizaje y boilerplate inicial como costos.
- **Verificación contra el código (Fase 0/3 de este trabajo):** la estructura de paquetes declarada (`core/{domain,ports,adapters}`, `apps/{authentication,expedientes,peticiones,verificacion,resoluciones,notificaciones}`) **coincide exactamente** con el código real. **Matiz importante** (no contradice la decisión, pero sí templa su alcance): el documento afirma "el dominio define qué necesita (ej. `ISGALegacyPort`)" en plural implícito, pero en la práctica **solo existe ese único puerto real** — no hay puertos de repositorio para persistencia ni para almacenamiento de PDF como interfaces abstractas separadas (ver `C3_COMPONENTES.md`, nota de fidelidad). La decisión arquitectónica en sí es correcta y está implementada; el detalle de "cuántos puertos" es menos exhaustivo en la práctica que lo que el ADR sugiere.
- **Estado de esta verificación:** IMPLEMENTADO Y VERIFICADO (la decisión central), con la salvedad anterior.

## 3. ADR-0002: Stack Tecnológico Django 5.x + DRF + PostgreSQL 16

- **Identificador:** ADR-0002 (`docs/adr/0002-stack-django-drf-postgresql.md`)
- **Estado:** Aceptado (según el documento fuente)
- **Decisión:** stack completo detallado (Python 3.12, Django 5.2.x, DRF 3.16.x, PostgreSQL 16, djangorestframework-simplejwt 5.5.x, django-environ 0.12.x, drf-spectacular 0.27.x, pytest/pytest-django/pytest-cov, Black/Flake8/Isort/MyPy, ReportLab, Docker + Docker Compose, Nginx).
- **Alternativas consideradas (según el documento):** FastAPI+Pydantic, Flask+SQLAlchemy, Node.js/Express, MySQL/MariaDB, MongoDB, JWT manual — todas rechazadas con justificación explícita.
- **Verificación contra `backend/requirements.txt` (Fase 0):** coincide en las dependencias principales (Django, DRF, SimpleJWT, psycopg, django-environ, drf-spectacular, ReportLab, Gunicorn). Las versiones exactas no se verificaron línea por línea en esta pasada (pendiente para la Fase 4, `STACK_TECNOLOGICO.md`).
- **Estado de esta verificación:** IMPLEMENTADO Y VERIFICADO (a nivel de presencia de dependencias); verificación exacta de versiones pendiente de Fase 4.

## 4. Decisiones sin ADR formal (documentadas en `clarify.md`, no en `docs/adr/`)

El proyecto tiene un mecanismo de decisión adicional, más granular, que **no** usa el formato ADR pero sí deja registro formal: el dossier `clarify.md` (ver `DOCUMENTACION/01_ESPECIFICACION/SDD_GITHUB_SPEC_KIT.md`). Decisiones como DEC-01 (notificaciones in-app), DEC-02 (carga de certificados Opción A), DEC-03 (numeración correlativa), DEC-04 (firma externa) y DEC-05 (inalterabilidad del promedio SGA) están documentadas allí con contexto, alternativas y justificación — cumplen el espíritu de un ADR, pero no están en `docs/adr/`. No se duplican aquí; se referencian.

## 5. Decisiones técnicas pendientes de formalización

Conforme a la instrucción de no presentar como "decisión histórica confirmada" algo sin evidencia documental:

| Decisión técnica observada en el código | Evidencia | Estado de formalización |
|---|---|---|
| Separación de servidor de aplicaciones por entorno: `runserver` en `development` (sin hardening) y Gunicorn en `production` (vía `entrypoint.sh`), mediante un `Dockerfile` multi-stage con dos targets | `Dockerfile` (raíz), `backend/entrypoint.sh` (verificado y corregido en Fase 8; la Fase 3 de este trabajo había concluido erróneamente que Gunicorn se usaba siempre — ver `DOCUMENTACION/08_DESPLIEGUE/ARQUITECTURA_DOCKER.md`) | **PENDIENTE DE FORMALIZACIÓN** — no existe ADR ni mención en `clarify.md`/`plan.md` que documente explícitamente la decisión de usar un Dockerfile multi-stage con dos targets, aunque la implementación es coherente y deliberada (comentario propio en el `Dockerfile` cita "SEC-T001") |
| Simplificación del patrón de puertos a un único `ISGALegacyPort` (sin repositorios abstractos para persistencia/almacenamiento) | Código real (`core/ports/__init__.py`) vs. `plan.md` §10 (más exhaustivo) | **PENDIENTE DE FORMALIZACIÓN** — es una decisión de implementación razonable (evitar sobre-ingeniería en un MVP académico) pero no está registrada como decisión consciente en ningún artefacto SDD |
| Plantillas `ADR-001`/`ADR-002` de `specs/001-tramite-titulacion/adr/` nunca completadas | Archivos vacíos, verificado | **PENDIENTE** — brecha de proceso SDD, no de arquitectura en sí |

## 6. Conclusión

El repositorio tiene **2 ADR sustantivos y verificados** (arquitectura hexagonal/monolito modular, y stack tecnológico), ambos con buena correspondencia con el código real salvo matices menores ya señalados. No hay ADR duplicados. Las plantillas vacías en `specs/001-tramite-titulacion/adr/` son una brecha de formalización del proceso SDD (ya señalada por una auditoría previa y aún vigente), no una pérdida de contenido real.
