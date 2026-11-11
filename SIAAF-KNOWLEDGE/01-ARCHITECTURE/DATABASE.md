---
system: SGT-SIAAF
type: architecture
area: database
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Base de datos y modelo de datos

Motor: PostgreSQL 16 (`docker-compose.yml`, `TZ: UTC`). Modelos en `backend/src/apps/*/adapters/models.py`. Todos los PK son `UUIDField`.

## 1. Entidades reales

| App | Modelo | Campos clave | Relaciones (on_delete) |
|---|---|---|---|
| authentication | `User` (AbstractUser) | `cedula` (solo dígitos), `carrera_id`, `facultad_id` (UUID sin FK) | — |
| authentication | `Role` | `name` (único, `ROLE_CHOICES`), `description` | — |
| authentication | `UserRole` | `fecha_asignacion` | `user`→User (CASCADE), `role`→Role (CASCADE) |
| expedientes | `ExpedienteTitulacion` | `numero_expediente` (único), `numero_providencia`, `carrera_id`, `facultad_id` (index), `estado`, `fecha_creacion`, `fecha_recepcion`, `fecha_limite_atencion`, `dias_laborables_acumulados`, `fecha_ultima_pausa`, `fecha_actualizacion`, `activa` | `estudiante`→User (PROTECT) |
| expedientes | `HistorialEstado` | `estado_anterior`, `estado_nuevo`, `fecha_cambio` | `expediente` (CASCADE), `registrado_por`→User (PROTECT) |
| peticiones | `CatalogoDocumental` | `codigo_requisito` (único), `nombre`, `es_obligatorio_base`, `fase` (FASE_1/2/3), `rol_emisor_sugerido`, `activo` | — |
| peticiones | `PeticionDocumental` | `estado_peticion`, `dependencia_emisora` (rol), `fecha_solicitud` | `expediente` (CASCADE), `requisito`→CatalogoDocumental (PROTECT) |
| peticiones | `DocumentoEntregado` | `version`, `archivo_path`, `nombre_original`, `tamanio_bytes`, hash SHA-256, `tipo_mime`, `fecha_carga`, `es_vigente` | `peticion` (CASCADE), `subido_por`→User (PROTECT) |
| verificacion | `ChecklistVerification` | `estado_verificacion`, `fecha_evaluacion` | `expediente` (CASCADE), `requisito`→CatalogoDocumental (PROTECT), `evaluado_por`→User (PROTECT) |
| verificacion | `ObservacionAccionable` | `motivo_observacion`, `resuelta`, `fecha_resolucion` | `expediente` (CASCADE), `peticion` (CASCADE), `registrada_por`→User (PROTECT) |
| resoluciones | `InformeAptitud` | `numero_providencia`, `dictamen`, `archivo_informe_path`, `fecha_emision` | `expediente` **OneToOne** (PROTECT), `emisor`→User (PROTECT) |
| resoluciones | `DeclaratoriaAptitud` | `numero_memorando`, `archivo_memorando_firmado_path`, `fecha_declaratoria` | `expediente` **OneToOne** (PROTECT), `decano`→User (PROTECT) |
| notificaciones | `NotificacionInterna` | `titulo`, `mensaje`, `leida` (index), `fecha_creacion` (index) | `usuario_destino` (CASCADE), `expediente` (CASCADE), `peticion` (CASCADE) |
| notificaciones | `EventoAuditoria` | `accion` (10 valores), `rol_usuario`, `ip`, `timestamp` (index), `detalles` (JSON) | `usuario` (PROTECT), `expediente` (PROTECT) |

Acciones de auditoría (`EventoAuditoria.Accion`): `EXPEDIENTE_CREADO`, `EXPEDIENTE_ENVIADO`, `ESTADO_CAMBIADO`, `CHECKLIST_EVALUADO`, `OBSERVACION_REGISTRADA`, `SUBSANACION_REALIZADA`, `DOCUMENTO_CARGADO`, `INFORME_EMITIDO`, `DECLARATORIA_REGISTRADA`, `EXPEDIENTE_CANCELADO`.

## 2. Migraciones existentes (12)

| App | Migraciones |
|---|---|
| authentication | `0001_initial` |
| expedientes | `0001_initial`, `0002_expedientetitulacion_numero_providencia`, `0003_expedientetitulacion_facultad_id`, `0004_expedientetitulacion_fecha_actualizacion` |
| peticiones | `0001_initial`, `0002_catalogo_base_art235` (datos: requisitos base Art. 235), `0003_documentoentregado_and_more` |
| verificacion | `0001_initial` |
| resoluciones | `0001_initial` |
| notificaciones | `0001_initial`, `0002_eventoauditoria` |

Ruta: `backend/src/apps/<app>/adapters/migrations/`. **Los agentes de frontend no deben tocarlas** (`AGENTS.md` §3.1).

## 3. Lo que NO existe (propuestas documentadas)

| Elemento propuesto | Fuente | Estado |
|---|---|---|
| `ExpedienteTitulacion.opcion_titulacion`, enum `ModalidadTitulacion`, modelo `HistorialModalidad` | [[DP2-DISENO_FUNCIONAL_MODALIDADES]] | Propuesta (BE-06, INC-03) |
| `SesionUsuario`, `token_blacklist` | [[DP2-PLAN_SESIONES]] | Propuesta (INC-02) |
| `CSPViolation` | [[DP2-PLAN_MAESTRO]] INC-05-T03 | Propuesta |
| Catálogo de carreras/facultades (`carrera_id`/`facultad_id` son UUID sueltos) | BE-10 | No existe |
| `TrabajoTitulacion`, `TribunalEvaluador`, `ExamenComplexivo`, `ActaGrado` | [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]] §1.5 | Fase 2/3 futura |

## Relacionado

[[BACKEND_ARCHITECTURE]] · [[02-BACKEND/MODULES|Módulos backend]] · Documentación previa: `docs/05-base-datos/` (diccionario, ER, relaciones), `DOCUMENTACION/04_BACKEND/PERSISTENCIA.md`
