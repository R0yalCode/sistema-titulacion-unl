---
title: "Plan de APIs, dashboards y KPI"
subtitle: "Qué necesita el frontend y cómo lo provee el backend (2026-11-11)"
date: 2026-11-11
---

# Plan de APIs, dashboards y KPI

> **Reglas.** (1) Ningún KPI se calcula con datos ficticios ni se rellena cuando falta su fuente: la clave se omite y el endpoint informa `no_disponible` con el motivo. (2) Las fórmulas provienen de `docs/indicadores/INFORME_DISENO_KPI.md` (IK) y de D11; las correcciones propias se marcan **[corrección]** y quedan registradas en `REGISTRO_DECISIONES_TECNICAS.md`. (3) El ámbito sale del usuario autenticado (BD), nunca de parámetros del cliente.

## 1. Roles reales del sistema

Ocho roles en `authentication/adapters/models.py`: ESTUDIANTE, SECRETARIA_CARRERA, SECRETARIO_ABOGADO, ANALISTA_APOYO, DECANO, DIRECTOR_CARRERA, RESPONSABLE_DEPENDENCIA y ADMINISTRADOR. **No existen roles "Coordinador" ni "Docente"** en el código ni en los 12 documentos; la tutoría tampoco está modelada (IK §6.8). Cualquier dashboard para ellos requiere una decisión institucional (DP-13).

## 2. Necesidades del frontend por vista

| Vista | Necesita | Disponible hoy | Falta (tarea) |
|---|---|---|---|
| V-02 Estudiante | Estado, plazo, requisitos pendientes/observados, notificaciones | Bandeja + detalle + notificaciones | Agregado único (E4-02); observaciones del estudiante vía `GET /expedientes/{id}/observaciones/` (E2-02a) |
| V-04 Expediente | Cabecera, peticiones, timeline, acciones | Detalle + checklist (solo juristas) | Historial de estados (E4-08, depende de E2-06/DT-12); observaciones e id para subsanar (E2-02a), sin abrir el checklist al dueño |
| V-05/V-06 Peticiones | Lista, versiones, descarga | Detalle con peticiones anidadas; descarga | Listado de versiones (E4-09) |
| V-07 Bandeja | Paginación, filtros, columnas por rol | Paginación | Filtros (E4-05); lista para SECRETARIA/DIRECTOR (DP-12) |
| V-08 Detalle funcionario | Checklist, observar, informe, declaratoria, documentos | Mutaciones | Iniciar verificación (E2-01), lectura de informe/declaratoria (E4-07), documentos de otras dependencias (E2-03) |
| Dashboards de funcionario/Admin | Tarjetas, gráficos, tabla | Nada | `/dashboard/me/` + analíticos (E4) |

## 3. APIs pendientes

### 3.1 `GET /api/v1/dashboard/me/` (PLB-E4-02)
- **Objetivo:** dashboard compuesto según los roles del usuario (D03 §1.1).
- **Parámetros:** `desde`, `hasta` (fechas ISO; por defecto, los últimos 6 meses; rango ≤ 24 meses).
- **Respuesta 200:**
```json
{
  "generado_en": "2026-11-11T15:00:00Z",
  "roles": ["SECRETARIO_ABOGADO"],
  "ambito": {"tipo": "facultad", "carrera_id": null, "facultad_id": "uuid"},
  "periodo": {"desde": "2026-05-01", "hasta": "2026-11-11"},
  "tarjetas": [
    {"id": "KPI-JUR-01", "titulo": "Expedientes en verificación", "valor": 4, "unidad": "#", "variante": "info"}
  ],
  "graficos": [
    {"id": "KPI-DEC-05", "tipo": "bar", "titulo": "Distribución por estado", "series": [{"clave": "ENVIADA", "valor": 3}]}
  ],
  "alertas": [{"id": "KPI-JUR-07", "nivel": "danger", "valor": 1}],
  "no_disponibles": [{"id": "KPI-MOD-01", "motivo": "Modalidad de titulación no implementada (BE-06)"}],
  "notificaciones_no_leidas": 7
}
```
- **Permisos:** recurso `dashboard` GET para los 7 roles operativos (RESPONSABLE_DEPENDENCIA bloqueado, DP-07). Estudiante: `SCOPE_OWN`.
- **Validaciones:** fechas válidas, `desde ≤ hasta`, rango máximo; 400 en caso contrario.
- **Modelos/servicios:** `indicadores/services/kpi_*.py` sobre `ExpedienteTitulacion`, `PeticionDocumental`, `ChecklistVerification`, `ObservacionAccionable`, `InformeAptitud`, `DeclaratoriaAptitud`, `NotificacionInterna`, `EventoAuditoria`.
- **Requerimientos:** RQ-KPI-02, RQ-KPI-06 (D03, D04 §2.1, D05 §4).
- **Diferencia con D03/D05 (justificada en DT-07):** se usan listas `tarjetas`/`graficos` con `id` de KPI en lugar de `secciones` libres (`DictField` de `JSONField`), para tener un contrato tipado en OpenAPI. La `tabla_trabajo` no se duplica: la tabla es la bandeja (`/expedientes/bandeja/`).

### 3.2 `GET /api/v1/indicadores/culminacion/` (PLB-E4-03)
- **Parámetros:** `cohorte_desde`, `cohorte_hasta` (sobre `fecha_recepcion`), `agrupar ∈ {carrera, facultad}` (solo dentro del ámbito).
- **Respuesta:** `{"cohorte": {...}, "enviados": 40, "culminados": 12, "cancelados": 1, "tasa_culminacion": 30.0, "tiempo_promedio_dias": 21.5, "por_grupo": [{"clave": "uuid", "enviados": 10, "culminados": 4, "tasa_culminacion": 40.0}]}`
- **Permisos:** DECANO (facultad), DIRECTOR_CARRERA (carrera), ADMINISTRADOR. **KPI:** DEC-04, DIR-04/05, ADM-04/05, SEC-08.

### 3.3 `GET /api/v1/indicadores/evolucion/` (PLB-E4-03)
- **Parámetros:** `meses` (1–24, por defecto 12).
- **Respuesta:** `{"serie": [{"mes": "2026-01", "solicitudes": 0}, ...]}` con los meses vacíos en 0.
- **Permisos:** SECRETARIA_CARRERA, DECANO, DIRECTOR_CARRERA, ADMINISTRADOR (según ámbito). **KPI:** SEC-05, ADM-06.

### 3.4 Otras pendientes

| Método y ruta | Objetivo | Permisos | Tarea | Estado |
|---|---|---|---|---|
| `POST /api/v1/expedientes/{id}/iniciar-verificacion/` | ENVIADA→EN_VERIFICACION + crear el checklist; respuesta: detalle del expediente | SECRETARIO_ABOGADO (facultad), celda nueva sujeta a **AUT-02**; ANALISTA según DP-01b | E2-01 | Definida, **no autorizada** |
| `GET /api/v1/expedientes/{id}/observaciones/` | Observaciones para el estudiante: `[{id, requisito_codigo, requisito_nombre, motivo, fecha_observacion, estado_subsanacion, checklist_verification_id, puede_subsanar}]` | ESTUDIANTE (own), SECRETARIO_ABOGADO (facultad), ADMIN, celda nueva sujeta a **AUT-03**; ANALISTA según DP-05b; SECRETARIA_CARRERA según DP-21 | E2-02a | Definida, **no autorizada** |
| `POST /api/v1/auth/token/refresh/` | Renovar el par (rotación) | Pública + throttle `auth` | E3-01 | Lista |
| `POST /api/v1/auth/logout/` | Revocar el refresh | Autenticado | E3-02 | Lista |
| `GET /api/v1/indicadores/usuarios-activos/` | KPI-ADM-09 | ADMINISTRADOR | E3-03 | Tras E3-03 |
| `GET /api/v1/expedientes/{id}/informe/`, `/declaratoria/` | Lectura de resoluciones | Juristas/Decano (facultad), dueño, Admin | E4-07 | Lista |
| `GET /api/v1/expedientes/{id}/historial/` | Timeline real (`HistorialEstado`) | Mismo ámbito que el detalle | E4-08 | Lista |
| `GET /api/v1/peticiones/{id}/documentos/` | Lista de versiones (metadatos) | Mismo ámbito que la descarga | E4-09 | Lista |
| `GET /api/v1/auditoria/` | Consulta de `EventoAuditoria` | ADMINISTRADOR | E7-04 | Lista |
| `GET /api/v1/buscar/` | Búsqueda por número/cédula | Según ámbito | E6-01 | Lista |
| `GET /api/v1/exportar/` | CSV/PDF de la bandeja | Según ámbito | E6-02 | Lista (CSV/PDF) |
| `POST /api/v1/csp-report/` | Reportes CSP | Anónimo + throttle | E6-03 | Lista |
| `GET /api/v1/expedientes/{id}/modalidad/` (+ elegibilidad, cambiar), `GET /modalidades/` | Modalidades | D12 | E5 | **Bloqueada** |

## 4. Endpoints existentes que deben ampliarse

| Endpoint | Ampliación | Compatibilidad |
|---|---|---|
| `GET /expedientes/bandeja/` | Filtros en lista blanca (E4-05) | Parámetros opcionales; sin cambio por defecto |
| `GET /notificaciones/` | Paginación opt-in con `?page=` (E4-06) | Sin `page` responde igual que hoy |
| `GET /expedientes/{id}/checklist/` | **Sin cambios**: el estudiante usa `/observaciones/` (DP-04), que expone menos datos | — |
| `POST /checklist/{id}/subsanar/` | Deja la observación EN_REVISION, sin resolverla (E2-02b3.1), y notifica al jurista (E2-02b2); retorno del expediente según DP-20 (E2-02b3.2, bloqueada) | Misma ruta y cuerpo |
| `POST /peticiones/{id}/documento/` | Rechaza peticiones OBSERVADO (E2-02b1, H-21; desplegar con E2-02b3.2, R-07) | Cambio justificado |
| `GET /peticiones/{id}/documento/` | SECRETARIO_ABOGADO: ámbito de facultad (E2-03, requiere AUT-01) | Solo amplía el acceso del jurista |
| `POST` de mutación | 429 (hecho) y errores de dominio 4xx (E1-04) | 500→4xx justificado |

## 5. Dashboards por rol

| Rol | Tarjetas (P0) | Gráficos | Filtros | Ámbito | Fuente |
|---|---|---|---|---|---|
| ESTUDIANTE | EST-01 estado, EST-06 plazo, EST-02 pendientes, EST-03 observados, EST-05 notificaciones | EST-07 progreso | — | own | `/dashboard/me/` |
| SECRETARIA_CARRERA | SEC-01, SEC-02, SEC-03, SEC-04 [corrección C-11] | SEC-05 (serie) | período | carrera | `/dashboard/me/`, `/indicadores/evolucion/` |
| SECRETARIO_ABOGADO / ANALISTA_APOYO | JUR-01, JUR-02, JUR-03, JUR-04 | DEC-05 (estado, ámbito facultad) | período | facultad | `/dashboard/me/` |
| DECANO | DEC-01, DEC-02, DEC-03 | DEC-05; DEC-04 | período / cohorte | facultad | `/dashboard/me/`, `/indicadores/culminacion/` |
| DIRECTOR_CARRERA | DIR-01, DIR-02, DIR-03 | DIR-06; DIR-04/05 | período / cohorte | carrera | ídem |
| RESPONSABLE_DEPENDENCIA | DEP-01…03 | — | — | **bloqueado (DP-07)** | — |
| ADMINISTRADOR | ADM-01, ADM-02, ADM-03 | ADM-06, ADM-08; ADM-04/05 | período / cohorte | global | ídem |

Modalidad (KPI-MOD-*) en todos: **no disponible** hasta E5.

## 6. Catálogo de KPI (estado de implementación backend)

Columnas: fórmula expresada en ORM sobre el queryset **ya acotado al ámbito**; "Período" = filtro `desde/hasta`; periodicidad = en tiempo real (consulta en cada petición, `no-store`).

| ID | Nombre / objetivo | Fórmula (ORM) | Variables y fuente | Filtros | Rol | Endpoint | Estado |
|---|---|---|---|---|---|---|---|
| EST-01 | Estado actual del trámite | `estado` del expediente `activa=True` más reciente | `ExpedienteTitulacion` | — | ESTUDIANTE | dashboard | Implementable |
| EST-02 | Requisitos pendientes | `PeticionDocumental.filter(expediente=activo, estado_peticion__in=[PENDIENTE, SOLICITADO]).count()` | `PeticionDocumental` | — | ESTUDIANTE | dashboard | Implementable |
| EST-03 | Requisitos observados | `ObservacionAccionable.filter(expediente=activo, resuelta=False)` (requisito + motivo) | `ObservacionAccionable` | — | ESTUDIANTE | dashboard | Implementable |
| EST-04 | Documentos vigentes | `DocumentoEntregado.filter(peticion__expediente=activo, es_vigente=True).count()` | `DocumentoEntregado` | — | ESTUDIANTE | dashboard | Implementable |
| EST-05 | Notificaciones sin leer | `NotificacionInterna.filter(usuario_destino=u, leida=False).count()` | `NotificacionInterna` | — | Todos | dashboard | Implementable |
| EST-06 | Fecha límite y días restantes | `fecha_limite_atencion`; `vencido = fecha < hoy` | `ExpedienteTitulacion` | — | ESTUDIANTE | dashboard | Implementable |
| EST-07 | Progreso del checklist | `VERIFICADO / requisitos base activos × 100` **[corrección C-10: denominador = `CatalogoDocumental(es_obligatorio_base, activo).count()`, no 5 fijo]** | `ChecklistVerification`, `CatalogoDocumental` | — | ESTUDIANTE | dashboard | Implementable (inicialmente 0 hasta E2-01) |
| EST-08 | Hitos del proceso | Fechas de `HistorialEstado` | `HistorialEstado` | — | ESTUDIANTE | historial (E4-08) | Implementable |
| SEC-01 | Expedientes en atención | `estado__in=[ENVIADA, EN_VERIFICACION, OBSERVADA]` | `ExpedienteTitulacion` | — | SECRETARIA | dashboard | Implementable |
| SEC-02 / JUR-07 / DIR-03 | Plazo vencido | `exclude(estado__in=[DECLARADA_APTA, CANCELADA, BORRADOR]).filter(fecha_limite_atencion__lt=now)` | `ExpedienteTitulacion` | — | SEC, JUR, DIR | dashboard (alerta) | Implementable; **PV**: ¿se excluye OBSERVADA, cuyo plazo está en pausa? (DP-14) |
| SEC-03 | Certificados por emitir | `PeticionDocumental(dependencia_emisora=SECRETARIA_CARRERA, estado_peticion__in=[PENDIENTE, SOLICITADO])` | `PeticionDocumental` | — | SECRETARIA | dashboard | Implementable |
| SEC-04 | Documentos pendientes de validación | `ChecklistVerification(estado=PENDIENTE)` con `Exists(PeticionDocumental(expediente=OuterRef(expediente), requisito=OuterRef(requisito), estado_peticion=CARGADO))` **[corrección C-11]** | `ChecklistVerification`, `PeticionDocumental` | — | SECRETARIA | dashboard | Implementable |
| SEC-05 | Solicitudes recibidas | `filter(fecha_recepcion__range=período).count()`; serie con `TruncMonth` | `ExpedienteTitulacion` | período | SEC, ADM (06) | dashboard / evolucion | Implementable |
| SEC-06 / JUR-06 | Observados abiertos | `estado=OBSERVADA` | `ExpedienteTitulacion` | — | SEC, JUR | dashboard | Implementable |
| SEC-07 / DIR-02 / DEC-02 | Culminados en el período | `DeclaratoriaAptitud.filter(fecha_declaratoria__range=período)` (ámbito vía `expediente__`) | `DeclaratoriaAptitud` | período | SEC, DIR, DEC | dashboard | Implementable |
| SEC-08 / DIR-05 / ADM-05 | Tiempo promedio (días) | `Avg(declaratoria_aptitud__fecha_declaratoria − fecha_recepcion)` sobre DECLARADA_APTA de la cohorte | Expediente + Declaratoria | cohorte | SEC, DIR, ADM | culminacion | Implementable; días calendario (IK §7) |
| JUR-01 | En verificación | `estado=EN_VERIFICACION` | `ExpedienteTitulacion` | — | JUR | dashboard | Implementable (0 hasta E2-01) |
| JUR-02 | Requisitos por evaluar | `ChecklistVerification(estado=PENDIENTE)` | `ChecklistVerification` | — | JUR | dashboard | Implementable |
| JUR-03 | Observaciones sin resolver | `ObservacionAccionable(resuelta=False)` | `ObservacionAccionable` | — | JUR | dashboard | Implementable |
| JUR-04 | Listos para informe | `estado=EN_VERIFICACION` ∧ `~Exists(checklist ≠ VERIFICADO)` ∧ checklist completo **[PV: un expediente sin filas de checklist no debe contar como "listo" (DP-15)]** | Expediente + Checklist | — | JUR | dashboard | Implementable tras DP-15 |
| JUR-05 | Informes emitidos | `InformeAptitud.filter(fecha_emision__range=período)` | `InformeAptitud` | período | JUR | dashboard | Implementable |
| DEC-01 | Pendientes de declaratoria | `estado=INFORME_EMITIDO` | `ExpedienteTitulacion` | — | DECANO | dashboard | Implementable |
| DEC-03 / DIR-01 | Procesos activos | `exclude(estado__in=[DECLARADA_APTA, CANCELADA])` (DIR además excluye BORRADOR) | `ExpedienteTitulacion` | — | DEC, DIR | dashboard | Implementable; **PV**: criterio distinto de BORRADOR entre DEC y DIR (IK) |
| DEC-04 / DIR-04 / ADM-04 | Tasa de culminación | `culminados(cohorte) / enviados(cohorte) × 100`; cohorte = `fecha_recepcion` no nula en el rango | `ExpedienteTitulacion` | cohorte | DEC, DIR, ADM | culminacion | Implementable; tratamiento de CANCELADA: DP-10 |
| DEC-05 / DIR-06 | Distribución por estado | `values('estado').annotate(Count('id'))` | `ExpedienteTitulacion` | — | DEC, DIR, JUR | dashboard | Implementable |
| DIR-07 | Distribución por "período" | `ExtractYear(fecha_recepcion)` | `ExpedienteTitulacion` | — | DIR | evolucion | **PV**: es un año, no un período académico (C-08) |
| DEP-01…03 | Peticiones de mi dependencia | `dependencia_emisora ∈ roles` por estado | `PeticionDocumental` | — | RESP. DEP. | dashboard | **BL** (DP-07) |
| ADM-01 | Usuarios / con rol | `User.count()`; `UserRole.values('role__name').annotate(Count)` | `User`, `UserRole` | — | ADMIN | dashboard | Implementable |
| ADM-02 | Expedientes por estado | ídem DEC-05, global | `ExpedienteTitulacion` | — | ADMIN | dashboard | Implementable |
| ADM-03 | Culminados (histórico) | `DeclaratoriaAptitud.count()` | `DeclaratoriaAptitud` | — | ADMIN | dashboard | Implementable |
| ADM-06 | Evolución mensual | `TruncMonth(fecha_recepcion)` + ceros | `ExpedienteTitulacion` | meses | ADMIN | evolucion | Implementable |
| ADM-07 | Distribución por carrera | `values('carrera_id').annotate(Count)` | `ExpedienteTitulacion` | — | ADMIN | dashboard | Implementable con UUID; nombres **BL** (BE-10) |
| ADM-08 | Auditoría por acción | `EventoAuditoria.filter(período).values('accion').annotate(Count)` | `EventoAuditoria` | período | ADMIN | dashboard | Implementable |
| ADM-09 | Usuarios activos | ver D06 §4 | `SesionUsuario` | — | ADMIN | usuarios-activos | **BL** (E3-03) |
| MOD-01…08 | Modalidades | D11 | `opcion_titulacion`, `HistorialModalidad` | — | varios | indicadores/modalidades | **BL** (E5) |

## 7. Consideraciones de seguridad

- **Agregados sin fuga:** los KPI usan el mismo predicado de ámbito que la API de detalle; las pruebas comparan el conteo del dashboard con el queryset de la bandeja del mismo usuario.
- **Sin parámetros de ámbito:** `carrera_id`/`facultad_id` en la query solo pueden **restringir** dentro del ámbito propio; nunca ampliarlo (lista blanca; 403 si están fuera del ámbito).
- **Sin datos personales en agregados** (salvo las listas operativas, que ya existen en la bandeja). KPI-MOD-06 (lista de cédulas elegibles) requiere revisión de privacidad cuando se desbloquee.
- `Cache-Control: no-store` en dashboard e indicadores; throttling de lectura no necesario hoy (se revisará tras medir).

## 8. Consideraciones de rendimiento

- Una consulta agregada por KPI (`aggregate`/`annotate`) o, mejor, **varias métricas en un único `aggregate` con `Count(filter=Q(...))`** para los conteos por estado del mismo queryset.
- Índices existentes que cubren los filtros: `estado`, `carrera_id`, `facultad_id` (expediente), `estado_peticion` (petición), `(expediente, estado_verificacion)` (checklist), `(expediente, resuelta)` (observación), `fecha_declaratoria` y `fecha_emision`. **Falta** un índice en `fecha_recepcion` para las series y cohortes: añadirlo en E4-03 (migración sin pérdida de datos).
- Series temporales: `TruncMonth` + relleno de ceros en Python (12–24 elementos): portable y barato (DT-06). `generate_series` queda como optimización exclusiva de PostgreSQL.
- Objetivo verificable: `/dashboard/me/` con un número **constante** de consultas por rol (≤ 12), comprobado con `django_assert_num_queries`.
