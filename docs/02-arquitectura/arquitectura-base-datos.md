---
title: "Arquitectura de base de datos"
---

# Arquitectura de base de datos

## Motor y configuración

- **PostgreSQL 16** en producción/desarrollo (Docker, healthcheck `pg_isready`); SQLite en memoria para pruebas.
- `CONN_HEALTH_CHECKS=True` y `CONN_MAX_AGE` configurados; zona horaria UTC.

## Modelo de datos (14 tablas)

```mermaid
erDiagram
    USER ||--o{ USER_ROLE : tiene
    ROLE ||--o{ USER_ROLE : agrupa
    USER ||--o{ EXPEDIENTE : inicia
    EXPEDIENTE ||--o{ HISTORIAL_ESTADO : registra
    EXPEDIENTE ||--o{ PETICION : contiene
    CATALOGO ||--o{ PETICION : tipifica
    PETICION ||--o{ DOCUMENTO : versiona
    USER ||--o{ DOCUMENTO : sube
    EXPEDIENTE ||--o{ CHECKLIST : verifica
    CATALOGO ||--o{ CHECKLIST : tipifica
    USER ||--o{ CHECKLIST : evalua
    EXPEDIENTE ||--o{ OBSERVACION : acumula
    PETICION ||--o{ OBSERVACION : motiva
    USER ||--o{ OBSERVACION : registra
    EXPEDIENTE ||--o| INFORME : resuelve
    EXPEDIENTE ||--o| DECLARATORIA : culmina
    USER ||--o{ INFORME : emite
    USER ||--o{ DECLARATORIA : firma
    USER ||--o{ NOTIFICACION : recibe
    EXPEDIENTE ||--o{ NOTIFICACION : contextualiza
    PETICION ||--o{ NOTIFICACION : referencia
    USER ||--o{ EVENTO_AUDITORIA : genera
    EXPEDIENTE ||--o{ EVENTO_AUDITORIA : auditA
```

## Decisiones de modelado

| Decisión | Justificación |
|---|---|
| PK UUID en todas las entidades | No enumerabilidad; seguro en URLs |
| FK PROTECT hacia User y CatalogoDocumental | Impide borrados con historial (política de no borrado) |
| UniqueConstraint `(expediente, requisito)` en peticiones y checklist | Un requisito = una petición = una verificación por expediente |
| Versionado N+1 de documentos con `(peticion, version)` único y `es_vigente` | Historial completo de entregas sin perder versiones |
| OneToOne expediente↔informe y expediente↔declaratoria | La resolución es única e inmutable |
| `EventoAuditoria.detalles` JSONB | Bitácora flexible e inmutable (C-008) |
| Índices compuestos en consultas frecuentes | Bandeja, notificaciones, auditoría temporal |

## Integridad y migraciones

13 migraciones en 6 apps; `makemigrations --check` sin pendientes (verificado 05-11-2026). Semillas: catálogo Art. 235 (migración 0002 de peticiones) y usuarios demo (management command `seed_initial_data`, idempotente, no productivo).

## Limitaciones

- Sin estrategia de backups/restauración documentada.
- Sin particionamiento previsto para `EventoAuditoria` (crecimiento temporal).
- `carrera_id`/`facultad_id` son UUID sueltos (sin FK a catálogo institucional): los reportes por carrera requieren el catálogo BE-10.
