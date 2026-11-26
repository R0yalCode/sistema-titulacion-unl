---
title: "Persistencia"
---

# Persistencia — Backend SGT-SIAAF

**Fuente:** lectura directa de `backend/src/apps/*/adapters/models.py` (nombres de clase, claves, restricciones e índices verificados por `grep`/lectura de código, no transcritos de `plan.md`). El modelo entidad-relación completo (atributos, tipos) ya se documentó en `DOCUMENTACION/03_ARQUITECTURA/C4_UML.md`; esta página se centra en integridad, restricciones y migraciones — no repite la lista de atributos.

## 1. Motor y convenciones

PostgreSQL 16 (confirmado, `docker-compose.yml`). Claves primarias `UUID` en la mayoría de entidades de negocio (`ExpedienteTitulacion`, `PeticionDocumental`, `DocumentoEntregado`, `ObservacionAccionable`, `InformeAptitud`, `DeclaratoriaAptitud`, `NotificacionInterna`), `BigInt` autoincremental en catálogos y tablas de alto volumen (`CatalogoDocumental`, `EventoAuditoria`). Todas las tablas de negocio declaran `db_table` explícito (p. ej. `peticiones_peticiondocumental`) en vez de dejar el nombre autogenerado por Django.

## 2. Restricciones de integridad verificadas (no inferidas)

| Entidad | Restricción | Nombre real en el código | Regla de negocio que protege |
|---|---|---|---|
| `UserRole` | `UniqueConstraint(fields=["user","role"])` | `unique_user_role` | Un usuario no puede tener el mismo rol duplicado |
| `PeticionDocumental` | `UniqueConstraint(fields=["expediente","requisito"])` | `unique_peticion_por_requisito` | Un expediente no puede tener dos peticiones para el mismo requisito (RN-001) |
| `DocumentoEntregado` | `UniqueConstraint(fields=["peticion","version"])` | `unique_version_por_peticion` | El versionado de documentos no puede colisionar (RN-011) |
| `ChecklistVerification` | `UniqueConstraint(fields=["expediente","requisito"])` | `unique_verificacion_por_requisito` | Un requisito no puede tener más de una verificación activa por expediente |

## 3. Índices declarados (rendimiento de consulta, no solo integridad)

`PeticionDocumental`: índices sobre `expediente`, `estado_peticion`, `requisito` (`idx_peticion_expediente`, `idx_peticion_estado`, `idx_peticion_requisito`) — coherente con RNF-005 (rendimiento de bandejas filtradas por estado). `DocumentoEntregado.es_vigente`, `NotificacionInterna.leida`/`fecha_creacion`, `EventoAuditoria.timestamp`, `ObservacionAccionable.resuelta`/`fecha_registro`: todos con `db_index=True`, coherente con los patrones de consulta reales (bandejas, notificaciones no leídas, auditoría por fecha).

## 4. Integridad transaccional (verificada en servicios, no solo declarada en ADR)

Los servicios críticos (`crear_expediente`, `enviar_expediente`, `evaluar_checklist`) usan `transaction.atomic()` combinado con `select_for_update()` (bloqueo pesimista a nivel de fila), confirmado por lectura directa del código en la Fase 0 y reconfirmado en Fase 4. Esto respalda la Ficha `AP-06`/`DEC` de `clarify.md` (control de concurrencia en el checklist digital) como **implementada**, no solo decidida.

## 5. Migraciones

| App | Migraciones | Qué agregó cada una (por nombre de archivo, evidencia indirecta) |
|---|---|---|
| `authentication` | 1 (`0001_initial`) | Esquema inicial de `User`/`Role`/`UserRole` |
| `expedientes` | 4 | Inicial + `numero_providencia` + `facultad_id` + `fecha_actualizacion` (evolución incremental documentada por los propios nombres de migración) |
| `peticiones` | 3 | Inicial + `catalogo_base_art235` (carga del catálogo de los 5 requisitos del Art. 235) + `documentoentregado_and_more` |
| `verificacion` | 1 (`0001_initial`) | Esquema inicial de `ChecklistVerification`/`ObservacionAccionable` |
| `resoluciones` | 1 (`0001_initial`) | Esquema inicial de `InformeAptitud`/`DeclaratoriaAptitud` |
| `notificaciones` | 2 | Inicial + `eventoauditoria` (la bitácora de auditoría se agregó en una migración posterior, no en el esquema inicial) |

**Total: 12 archivos de migración** (excluyendo `__init__.py`), confirmado por `find`. No se ejecutó `makemigrations --check` en esta pasada para confirmar ausencia de migraciones pendientes (`docs/RESUMEN_EJECUTIVO.md` lo reporta como "sin pendientes", pero esa cifra está sujeta a la misma reserva de re-verificación que el resto de resultados de ejecución — ver Fase 7).

## 6. Operaciones relevantes sobre el modelo (más allá de CRUD simple)

- **Numeración correlativa anual** (`generar_numero_expediente`, `generar_numero_providencia`): consulta el máximo existente del año en curso y genera el siguiente, dentro de la misma transacción con bloqueo — evita colisiones bajo concurrencia (DEC-03).
- **Versionado de documentos**: `DocumentoEntregado` nunca se sobreescribe; cada subsanación inserta una fila nueva con `version` incrementado y marca `es_vigente` en la fila anterior (RN-011), preservando el historial completo para auditoría.
- **Auditoría inmutable vía signals**: `EventoAuditoria` se escribe por señales de Django disparadas por cambios en otras apps, no por llamada directa desde los servicios de negocio — un patrón de "fire and forget" que desacopla la auditoría del flujo principal, pero que (según el hallazgo heredado en `COMPONENTES_NEGOCIO.md` §11) no está capturando el 100% de los eventos previstos.
