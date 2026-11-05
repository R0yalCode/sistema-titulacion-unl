---
title: "Diccionario de datos"
---

# Diccionario de datos

Campos principales por tabla (tipos PostgreSQL via Django). Fuente: `apps/*/adapters/models.py` y migraciones.

## authentication_user

| Campo | Tipo | Restricción |
|---|---|---|
| id | UUID | PK |
| username / email / password | varchar | heredado AbstractUser |
| cedula | varchar(20) | UNIQUE, validador de dígitos |
| carrera_id / facultad_id | UUID | NULL, indexados |
| is_active / is_staff / is_superuser | boolean | — |

## authentication_role / authentication_userrole

| Campo | Tipo | Restricción |
|---|---|---|
| role.name | varchar(64) | UNIQUE, choices de 8 roles |
| userrole.(user, role) | — | UNIQUE compuesto |

## expedientes (2 tablas)

| Campo | Tipo | Restricción |
|---|---|---|
| numero_expediente | varchar(64) | UNIQUE — formato `EXP-AAAA-NNNN` |
| numero_providencia | varchar(64) | UNIQUE, NULL, indexado — `PROV-AAAA-NNNN` |
| estudiante_id | UUID | FK PROTECT → user |
| estado | varchar(32) | choices 7 estados, indexado, default BORRADOR |
| fecha_recepcion / fecha_limite_atencion / fecha_ultima_pausa | datetime | NULL |
| dias_laborables_acumulados | integer | default 0 |
| activa | boolean | default true |
| historial: estado_anterior/estado_nuevo | varchar(32) | choices; fecha_cambio auto |

## peticiones (3 tablas)

| Campo | Tipo | Restricción |
|---|---|---|
| catalogo.codigo_requisito | varchar(64) | UNIQUE — p. ej. `ART235-01-RECORD-ACADEMICO` |
| catalogo.fase | varchar(8) | choices FASE_1/2/3, default FASE_1 |
| catalogo.rol_emisor_sugerido | varchar(64) | choices de roles |
| peticion.estado_peticion | varchar(16) | choices 7 estados, indexado, default PENDIENTE |
| peticion.(expediente, requisito) | — | UNIQUE compuesto |
| documento.version | integer | UNIQUE con peticion |
| documento.archivo_path | varchar(512) | ruta privada |
| documento.hash_sha256 | varchar(64) | SHA-256 en hex |
| documento.es_vigente | boolean | indexado, default true |

## verificacion (2 tablas)

| Campo | Tipo | Restricción |
|---|---|---|
| checklist.estado_verificacion | varchar(16) | PENDIENTE/VERIFICADO/OBSERVADO, indexado |
| checklist.(expediente, requisito) | — | UNIQUE compuesto |
| checklist.evaluado_por | UUID | FK PROTECT, NULL |
| observacion.motivo_observacion | text | obligatorio |
| observacion.resuelta | boolean | indexado, default false |

## resoluciones (2 tablas)

| Campo | Tipo | Restricción |
|---|---|---|
| informe.numero_providencia | varchar(64) | UNIQUE — `PROV-590-AAAA-NNNN` |
| informe.dictamen | text | APTO / NO APTO |
| informe.expediente_id | UUID | OneToOne PROTECT |
| declaratoria.numero_memorando | varchar(64) | UNIQUE — `MEM-162-AAAA-NNNN` |
| declaratoria.archivo_memorando_firmado_path | varchar(512) | PDF firmado persistido |

## notificaciones (2 tablas)

| Campo | Tipo | Restricción |
|---|---|---|
| notificacion.leida | boolean | indexado, default false |
| evento.accion | varchar(32) | choices de 10 acciones, indexado |
| evento.detalles | JSONB | inmutable |
| evento.ip | inet (GenericIPAddress) | NULL (actualmente siempre vacío) |
