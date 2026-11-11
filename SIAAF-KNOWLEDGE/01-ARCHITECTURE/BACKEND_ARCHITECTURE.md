---
system: SGT-SIAAF
type: architecture
area: backend
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Arquitectura backend

## Stack (verificado en `backend/requirements.txt` y `Dockerfile`)

| Componente | Versión declarada |
|---|---|
| Python (imagen) | `python:3.12-slim` (targets `development`, `production`) |
| Django | `>=5.2.19,<5.3` |
| Django REST Framework | `>=3.17.2,<4.0` |
| SimpleJWT | `>=5.5.1,<6.0` |
| drf-spectacular | `>=0.27,<1.0` |
| psycopg | `[binary]>=3.2,<4.0` (PostgreSQL 16 en Docker) |
| django-environ, django-cors-headers, gunicorn | `>=0.12`, `>=4.4`, `>=23.0` |

## Estilo arquitectónico

Monolito modular con **adaptadores hexagonales** (ADR `docs/adr/0001-arquitectura-hexagonal-monolito-modular.md`; stack en `docs/adr/0002-stack-django-drf-postgresql.md`). Cada app separa:

- `adapters/` → modelos ORM, serializers, vistas DRF, admin, migraciones.
- `services/` → casos de uso (transacciones, reglas de negocio).
- `domain/` → lógica pura (p. ej. `expedientes/domain/plazo_calculator.py`).
- `core/ports/` → puertos (p. ej. `ISGALegacyPort`) y `core/adapters/` → implementaciones (p. ej. `mock_sga.py`).

Configuración: `backend/src/config/settings/{base,local,production,test}.py`, URLs únicas en `backend/src/config/urls.py`.

## Componentes transversales (`backend/src/core/adapters/`)

| Archivo | Responsabilidad |
|---|---|
| `scope_filter.py` | `ScopeFilterMixin`: filtra querysets por OWN/CARRERA/FACULTAD (no ASIGNADO) |
| `pdf_validation.py` | Validación PDF: tamaño, magic bytes `%PDF-`, SHA-256 |
| `local_storage.py` | Almacenamiento privado de archivos |
| `mock_sga.py` | `SGAMockAdapter` (puerto `ISGALegacyPort`): récords académicos ficticios desde JSON (DEC-05; nunca conecta al SGA real) |
| `client_ip.py`, `middleware.py`, `logging_filters.py`, `security_headers.py` | IP real tras proxies confiables, cabeceras de seguridad, filtrado de logs |
| `health.py` | `GET /health/` sin autenticación |

## Seguridad relevante (verificado en `config/settings/base.py`)

- JWT: access 30 min, refresh 24 h, `ROTATE_REFRESH_TOKENS=False`, `HS256`, `SIGNING_KEY=JWT_SIGNING_KEY` (separada de `SECRET_KEY`, SEC-T004).
- Throttling configurado: `auth` (`AUTH_THROTTLE_RATE`, por defecto 5/min, `TrustedProxyScopedRateThrottle`) y `document_upload` (`DOCUMENT_UPLOAD_THROTTLE`, por defecto 10/h, `ScopedRateThrottle` en carga de documentos). **No existe** throttling para el resto de endpoints mutantes (VULN-001).
- No hay ruta de refresh ni logout (BE-03).

Detalle: [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]].

## Máquina de estados

### Expediente (`ExpedienteTitulacion.estado`)

Estados: `BORRADOR`, `ENVIADA`, `EN_VERIFICACION`, `OBSERVADA`, `INFORME_EMITIDO`, `DECLARADA_APTA`, `CANCELADA`.

| Transición | Dónde ocurre (verificado) | Precondición |
|---|---|---|
| → `BORRADOR` | `expedientes/services/crear_expediente.py:79` | Crea las 5 peticiones base (Art. 235) |
| `BORRADOR` → `ENVIADA` | `expedientes/services/enviar_expediente.py:103` | 5 peticiones con archivo vigente; fija `fecha_recepcion`, `numero_providencia`, `fecha_limite_atencion` (+8 días laborables) |
| `ENVIADA` → `EN_VERIFICACION` | **No implementada** en servicios, vistas ni señales | Los tests la fuerzan asignando el estado (`test_expediente_state_machine.py:118-129`: "En el modelo actual no hay endpoint explícito") y `tests/e2e/test_full_workflow.py:341-343` |
| `EN_VERIFICACION` → `OBSERVADA` | `verificacion/services/evaluar_checklist.py:223` (al observar un requisito) y `verificacion/services/registrar_observacion.py:149` | Estado `EN_VERIFICACION` |
| `OBSERVADA` → `EN_VERIFICACION` | `verificacion/services/subsanar_requisito.py:80` | Requisito en `OBSERVADO`; reanuda el plazo |
| `EN_VERIFICACION`/`OBSERVADA` → `INFORME_EMITIDO` | `resoluciones/services/emitir_informe.py:199` (precondición en `validar_checklist_completo.py:67`) | Checklist 100 % `VERIFICADO` |
| `INFORME_EMITIDO` → `DECLARADA_APTA` | `resoluciones/services/declarar_aptitud.py:203` | Estado `INFORME_EMITIDO`; memorando PDF |
| → `CANCELADA` | Estado definido y auditado (`EventoAuditoria.EXPEDIENTE_CANCELADO`), **sin servicio ni endpoint** que lo asigne | — |

> **GAP-STATE-01 (hallazgo de esta construcción, no listado en DP2):** por API, un expediente `ENVIADA` no puede avanzar a `EN_VERIFICACION`, y tanto `PUT /checklist/{id}/` como `POST /expedientes/{id}/observar/` exigen `EN_VERIFICACION`. El flujo extremo a extremo vía API se detiene en `ENVIADA` salvo intervención directa (admin/BD). Requiere decisión humana y autorización backend; **no** se corrigió.

### Petición documental (`PeticionDocumental.estado_peticion`)

`PENDIENTE` → `SOLICITADO` (solicitar emisión) → `CARGADO` (carga de documento) → `VERIFICADO` | `OBSERVADO` (evaluación de checklist). `LEGALIZADO` existe en el enum. Requisito de checklist (`ChecklistVerification.estado_verificacion`): `PENDIENTE`, `VERIFICADO`, `OBSERVADO`.

### Plazo

`expedientes/domain/plazo_calculator.py`: 8 días laborables desde `fecha_recepcion`, excluyendo fines de semana y feriados configurados; se pausa en `OBSERVADA` y se reanuda al subsanar (`dias_laborables_acumulados`, `fecha_ultima_pausa`). La pausa responde al supuesto S-01 de specify 001 (la norma no lo define).

## Relacionado

[[02-BACKEND/MODULES|Módulos backend]] · [[DATABASE]] · [[API_CONTRACTS]] · [[PERMISSIONS_ROLES]] · [[GENERAL_ARCHITECTURE]]
