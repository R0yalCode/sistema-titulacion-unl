---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/MATRIZ_ACCIONES_RAPIDAS_POR_ROL.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/MATRIZ_ACCIONES_RAPIDAS_POR_ROL.md
source_version: "1.0"
source_date: 2026-11-09
nature: ux-matrix (proposal)
vigencia: parcialmente-contradice-RBAC-real
last_verified: 2026-11-11
---

# DP2 · Matriz de acciones rápidas por rol

**Original:** [[MATRIZ_ACCIONES_RAPIDAS_POR_ROL]]

## Contenido

Definición: botones contextuales que ejecutan la operación más frecuente del rol; **el RBAC lo aplica el servidor** y el frontend solo muestra u oculta. Matriz acción × rol × contexto (§2), acciones por vista V-02, V-04, V-05, V-07 y V-08 (§3), componente `AccionesRapidas` con props, lógica e integración (§4), helpers de permisos (§5) y dependencias backend (§8).

## Contraste con `RBAC_MATRIX` real

| Celda de la matriz DP2 | RBAC real | Resultado |
|---|---|---|
| RESPONSABLE_DEPENDENCIA: cargar/descargar documento (asignado) | Sin celdas | ❌ Hoy recibiría 403 |
| SECRETARIA_CARRERA: subsanar (asignado) | `checklist` POST = SCOPE_CARRERA | ⚠️ Scope distinto |
| ADMINISTRADOR: evaluar checklist, subsanar, cargar | ALLOW | ✅ |
| ADMINISTRADOR: observar, emitir informe, declarar | Sin celda | ✅ (❌ en ambos) |
| "Ver auditoría" `GET /api/v1/auditoria/` | Endpoint inexistente | ❌ |
| Verificar elegibilidad / autorizar EC | Endpoints inexistentes | Propuesta (BE-06) |

## Estado de implementación (§6, verificado)

`features/dashboard/AccesosRapidos.tsx` existe (accesos locales del estudiante); `features/expediente/accionesPorRolEstado.ts` existe (la DP2 lo describe como "parcial, solo lectura"). No existe un `AccionesRapidas` genérico ni para funcionarios.

## Relacionado

[[PERMISSIONS_ROLES]] · [[COMPONENTS]] · [[DASHBOARD_ARCHITECTURE]]
