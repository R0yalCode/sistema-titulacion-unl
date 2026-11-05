---
title: "Relaciones e integridad"
---

# Relaciones e integridad referencial

## Mapa de relaciones

| Relación | Cardinalidad | ON DELETE | Motivo |
|---|---|---|---|
| User → UserRole → Role | N:M vía UserRole | CASCADE | Asignación de roles |
| User → ExpedienteTitulacion (estudiante) | 1:N | **PROTECT** | No se borra un usuario con expedientes |
| Expediente → HistorialEstado | 1:N | CASCADE | El historial vive con el expediente |
| Expediente → PeticionDocumental | 1:N (5 en Fase 1) | CASCADE | Ídem |
| CatalogoDocumental → PeticionDocumental | 1:N | **PROTECT** | El catálogo no se borra si hay peticiones |
| PeticionDocumental → DocumentoEntregado | 1:N versionado | CASCADE | Versiones N+1 |
| User → DocumentoEntregado (subido_por) | 1:N | **PROTECT** | Trazabilidad de quién subió |
| Expediente → ChecklistVerification | 1:N | CASCADE | — |
| CatalogoDocumental → ChecklistVerification | 1:N | **PROTECT** | — |
| Expediente/Peticion → ObservacionAccionable | 1:N / 1:N | CASCADE | — |
| Expediente → InformeAptitud / DeclaratoriaAptitud | 1:0..1 | **PROTECT** | Resolución única e inmutable |
| User → NotificacionInterna | 1:N | CASCADE | Notificaciones personales |
| Expediente/Peticion → NotificacionInterna | 1:N / 0..1:N | CASCADE | Contexto |
| User/Expediente → EventoAuditoria | 1:N | **PROTECT** | La auditoría nunca se pierde por borrado |

## Restricciones de unicidad (negocio en la BD)

| Restricción | Regla de negocio que protege |
|---|---|
| `(user, role)` único | Sin roles duplicados |
| `numero_expediente`, `numero_providencia`, `numero_providencia` (informe), `numero_memorando` | Numeración correlativa única |
| `(expediente, requisito)` en peticiones y checklist | Un requisito = una petición = una verificación |
| `(peticion, version)` en documentos | Versionado sin colisiones |
| `cedula` | Identidad institucional |

## Índices de consulta frecuente

| Índice | Consulta que atiende |
|---|---|
| `idx_exped_carrera` | Bandejas y KPIs por carrera |
| `idx_peticion_estado`, `idx_doc_peticion_vigente` | Listas de trabajo por dependencia |
| `idx_verif_expediente_estado` | Checklist y RN-003 |
| `idx_obs_expediente_resuelta` | Observaciones pendientes |
| `idx_notif_usuario_leida`, `idx_notif_usuario_fecha` | Bandeja de notificaciones |
| `idx_audit_expediente_fecha`, `idx_audit_accion_fecha` | Auditoría temporal |

## Integridad transaccional (aplicación)

Más allá de la BD, los casos de uso usan `transaction.atomic` + `select_for_update` sobre las filas críticas (expediente, petición, verificación) para evitar condiciones de carrera en transiciones de estado. Verificado por pruebas de concurrencia lógica (`test_evaluar_checklist.py`).
