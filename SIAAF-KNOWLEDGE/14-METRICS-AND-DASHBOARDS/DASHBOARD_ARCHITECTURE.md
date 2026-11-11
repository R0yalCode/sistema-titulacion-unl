---
system: SGT-SIAAF
type: architecture
area: dashboards
status: mixed
source: verified-code + Documentacion-parte-2
last_verified: 2026-11-11
aliases: [ROLE_DASHBOARDS]
---

# Arquitectura de dashboards (real frente a propuesta)

## Implementado (verificado)

| Dashboard | Ruta | Fuente de datos real | Estado |
|---|---|---|---|
| Estudiante (V-02) | `/estudiante` | `GET /expedientes/bandeja/` (BORRADOR/OBSERVADA) + `GET /notificaciones/` + `PATCH marcar-leida`; accesos rápidos locales (`localStorage`) | Hecho |
| Funcionarios (V-07) | `/bandeja` | — | Stub |

## Propuesto (no implementado)

Endpoint unificado `GET /api/v1/dashboard/me/` compuesto en el servidor según los roles del usuario, con tarjetas P0 (máx. 6), un gráfico principal, una tabla de trabajo, actividad reciente, notificaciones no leídas y un bloque de modalidad. Detalle: [[DP2-ARQUITECTURA_DASHBOARDS]], [[DP2-ESPECIFICACION_SERVICIOS_DASHBOARD]].

### Dashboards por rol propuestos

| Rol | Tarjetas P0 | Acciones rápidas | Modalidad |
|---|---|---|---|
| ESTUDIANTE | Estado, requisitos pendientes, observados, notificaciones, fecha límite | Crear solicitud, ver expediente, subsanar | Ver la actual + elegibilidad EC |
| SECRETARIA_CARRERA | En atención, plazo vencido, certificados por emitir, por validar | Emitir certificado, ver expediente | Solo lectura |
| SECRETARIO_ABOGADO | En verificación, por evaluar, observaciones abiertas, listos para informe | Evaluar, observar, emitir informe | Verifica elegibilidad EC |
| ANALISTA_APOYO | Igual que el jurista (facultad, borrador) | Evaluar (borrador), informe | Solo lectura |
| DECANO | Pendientes de declaratoria, declaratorias del período | Declarar aptitud | Autoriza el cambio a EC |
| DIRECTOR_CARRERA | Activos, culminados, plazo vencido | Supervisar | Solo lectura |
| RESPONSABLE_DEPENDENCIA | Solicitudes de su dependencia | Cargar o corregir documento | Solo lectura |
| ADMINISTRADOR | Usuarios, expedientes, culminados, tasa global | Usuarios, catálogos | Dashboard global |

Fuente: [[DP2-PLAN_MAESTRO]] §6.2.

## Bloqueos para implementarlo

1. App `indicadores` + `/dashboard/me/` (INC-04, backend no autorizado).
2. Bandeja vacía para SECRETARIA_CARRERA, DIRECTOR_CARRERA y RESPONSABLE_DEPENDENCIA (`MAPA_INTERVENCION_POR_ROL`, BE-09).
3. RESPONSABLE_DEPENDENCIA sin RBAC (VULN-006) y fuera de `OPERATIONAL_ROLES` en el frontend.
4. Modalidad: BE-06.
5. GAP-STATE-01: sin la transición a `EN_VERIFICACION`, los indicadores del jurista no reflejarían el flujo real.

## Relacionado

[[KPI_CATALOG]] · [[ROUTES]] · [[DP2-MATRIZ_ACCIONES_RAPIDAS]]
