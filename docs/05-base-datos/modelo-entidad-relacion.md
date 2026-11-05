---
title: "Modelo entidad-relación"
---

# Modelo entidad-relación

14 tablas en 6 apps (PostgreSQL). Diagrama completo en [Arquitectura de base de datos](../02-arquitectura/arquitectura-base-datos.md).

## Entidades por dominio

### Identidad (authentication)

| Entidad | Descripción |
|---|---|
| `User` | Usuario institucional: UUID, username, cédula única, `carrera_id`/`facultad_id` (UUID sueltos, indexados) |
| `Role` | Catálogo cerrado de 8 roles |
| `UserRole` | Asignación única (usuario, rol) con fecha |

### Trámite (expedientes)

| Entidad | Descripción |
|---|---|
| `ExpedienteTitulacion` | Unidad del trámite: numeración única, estado (7), fechas de recepción/límite, días acumulados, `activa` |
| `HistorialEstado` | Bitácora de transiciones (estado anterior/nuevo, registrador) |

### Requisitos (peticiones)

| Entidad | Descripción |
|---|---|
| `CatalogoDocumental` | Requisito del reglamento: código único, fase, rol emisor sugerido, activo |
| `PeticionDocumental` | Requisito instanciado en un expediente (único por par) con estado propio |
| `DocumentoEntregado` | Versión N de un PDF entregado (hash, tamaño, vigencia) |

### Verificación (verificacion)

| Entidad | Descripción |
|---|---|
| `ChecklistVerification` | Evaluación del jurista por requisito (única por par expediente-requisito) |
| `ObservacionAccionable` | Motivo que bloquea una petición; se cierra al subsanar |

### Resolución (resoluciones)

| Entidad | Descripción |
|---|---|
| `InformeAptitud` | Providencia 590 (1:1 con expediente) |
| `DeclaratoriaAptitud` | Memorando 162 (1:1 con expediente) |

### Comunicación (notificaciones)

| Entidad | Descripción |
|---|---|
| `NotificacionInterna` | Mensaje in-app a un usuario, contextualizado en expediente/petición |
| `EventoAuditoria` | Registro inmutable de acciones con detalles JSONB |

## Cardinalidades clave

- User 1—N Expediente (PROTECT), 1 expediente activo por estudiante (regla de servicio).
- Expediente 1—N PeticionDocumental (exactamente 5 al crear, Fase 1).
- PeticionDocumental 1—N DocumentoEntregado (versionado N+1, 1 vigente).
- Expediente 1—0..1 InformeAptitud / DeclaratoriaAptitud (OneToOne PROTECT).
