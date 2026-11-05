# DISEÑO DEL SISTEMA DE INDICADORES (KPI) POR ROL — SGT-SIAAF

| Campo | Valor |
|---|---|
| Documento | Propuesta técnica de indicadores y dashboards |
| Fecha | 05-11-2026 |
| Base | Código real del backend (modelos, estados, roles) verificado en `INFORME_AUDITORIA_TECNICA.md` |
| Estado | **PROPUESTA** — los endpoints de indicadores NO están implementados y requieren autorización expresa antes de codificarse |

---

## 1. INTRODUCCIÓN

Este documento define el sistema de indicadores (KPI) de SGT-SIAAF: qué debe ver cada usuario al ingresar, con qué fórmulas exactas, desde qué datos reales del modelo, y mediante qué APIs de consulta. Todo indicador se calcula **en el backend** (capa de servicios de indicadores + agregaciones PostgreSQL); el frontend solo consume y presenta.

Principios:

1. **Fidelidad al modelo real**: solo se usan entidades, estados y campos existentes (`ExpedienteTitulacion`, `PeticionDocumental`, `DocumentoEntregado`, `ChecklistVerification`, `ObservacionAccionable`, `InformeAptitud`, `DeclaratoriaAptitud`, `NotificacionInterna`, `EventoAuditoria`, `User`).
2. **Definición inequívoca**: cada KPI tiene fórmula, numerador/denominador, cohorte y tratamiento de procesos abiertos.
3. **Alcance por permisos**: cada consulta se filtra por el ámbito RBAC del usuario (own/carrera/facultad/all), reutilizando `ScopeFilterMixin`.
4. **Sin datos ficticios**: prohibido CA-G-01; los contadores provienen de agregaciones sobre la base real.

## 2. OBJETIVOS

- Que cada rol comprenda en ≤ 5 segundos: **¿cuál es la situación actual?, ¿qué requiere mi atención?, ¿qué acción debo realizar?**
- Centralizar las fórmulas en una capa de servicios de indicadores para evitar duplicidad entre endpoints.
- Dejar identificados los datos que faltan para KPI analíticos (§9), sin inventarlos.

## 3. ROLES IDENTIFICADOS (del código, no inventados)

Fuente: `backend/src/apps/authentication/adapters/models.py:7-25` y `permissions.py:24-115`.

| Rol | Ámbito RBAC | Responsabilidad en el trámite |
|---|---|---|
| `ESTUDIANTE` | own | Crea solicitud, carga documentos, subsana observaciones |
| `SECRETARIA_CARRERA` | carrera | Admite trámites, emite certificados (requisitos Art. 235) |
| `SECRETARIO_ABOGADO` | facultad | Verifica checklist, observa, emite Informe 590 |
| `ANALISTA_APOYO` | facultad (borrador) | Apoya verificación; co-firma declaratoria (servicio) |
| `DECANO` | facultad | Firma Declaratoria 162 |
| `DIRECTOR_CARRERA` | carrera | Supervisa procesos de su carrera |
| `RESPONSABLE_DEPENDENCIA` | denegado en bandeja | Dependencia emisora de requisitos (prácticas, idioma, tesorería) |
| `ADMINISTRADOR` | allow (all) | Administración del sistema |

## 4. NECESIDADES INFORMATIVAS POR ROL

| Rol | Decisiones que toma | Preguntas que el dashboard debe responder |
|---|---|---|
| SECRETARIA_CARRERA | Admisión/recepción de trámites, emisión de certificados | ¿Qué expedientes llegaron y cuánto les queda de plazo? ¿Qué documentos debo emitir? ¿Qué está observado? |
| SECRETARIO_ABOGADO | Verificación, observación, informe | ¿Qué expedientes están EN_VERIFICACION? ¿Cuántos requisitos faltan por evaluar? ¿Qué está listo para informe? |
| ANALISTA_APOYO | Apoyo de verificación | Igual que jurista, en ámbito facultad, solo borrador |
| DECANO | Firmar declaratoria | ¿Qué expedientes tienen informe emitido pendiente de declaratoria? ¿Cuántos titulé este período? |
| DIRECTOR_CARRERA | Supervisión de carrera | ¿Cómo va mi carrera? ¿Cuántos procesos activos, cuántos culminados, tiempos? |
| RESPONSABLE_DEPENDENCIA | Emitir documentos solicitados | ¿Qué peticiones hay dirigidas a mi dependencia y pendientes? |
| ESTUDIANTE | Avanzar su trámite | ¿En qué estado estoy? ¿Qué debo entregar? ¿Qué está observado y por qué? |
| ADMINISTRADOR | Administración global | ¿Cómo está el sistema completo? Distribuciones, evolución, usuarios |

## 5. PROPUESTA DE DASHBOARD POR ROL

### 5.1 Secretaría de Carrera

- **Tarjetas P0**: expedientes de su carrera en estados {ENVIADA, EN_VERIFICACION, OBSERVADA} con `fecha_limite_atencion` vigente/vencida; peticiones pendientes donde `dependencia_emisora = SECRETARIA_CARRERA` (certificados por emitir); documentos pendientes de validación (checklist PENDIENTE).
- **Alertas**: expedientes con plazo vencido (`fecha_limite_atencion < hoy` y estado no terminal).
- **Tablas**: trámites por atender (orden por `fecha_limite_atencion`).
- **Filtros**: estado, período (fecha_creacion), carrera (implícita por scope).
- **Frecuencia**: datos en vivo (staleTime ≤ 30 s).

### 5.2 Secretario Abogado / Analista de Apoyo

- **Tarjetas P0**: expedientes EN_VERIFICACION en su facultad; requisitos pendientes de evaluación (checklist PENDIENTE); observaciones sin resolver (`resuelta=False`); listos para informe (checklist 100 % VERIFICADO y estado EN_VERIFICACION).
- **P1**: expedientes OBSERVADA esperando subsanación; informes emitidos en el período.
- **Acción rápida**: abrir checklist del expediente.

### 5.3 Decano

- **Tarjetas P0**: expedientes INFORME_EMITIDO pendientes de declaratoria (su cola de firma); declaratorias firmadas en el período.
- **P1**: total de procesos de su facultad por estado; tasa de culminación de la facultad.

### 5.4 Director de Carrera

- **Tarjetas P0**: procesos activos de su carrera; culminados (DECLARADA_APTA) en el período; vencidos por plazo.
- **P1**: distribución por estado (barras); tiempo promedio de trámite; sin tutor — **no calculable** (no existe entidad de tutor/asignación en el modelo; ver §9).

### 5.5 Responsable de Dependencia

- **Tarjetas P0**: peticiones con `dependencia_emisora` ∈ roles que ejerce el usuario, en estado SOLICITADO (por emitir) y OBSERVADO (por corregir).
- Nota: hoy `RESPONSABLE_DEPENDENCIA` tiene bandeja vacía por diseño (`MAPA_INTERVENCION_POR_ROL`); este dashboard se apoya en `PeticionDocumental`, no en la bandeja.

### 5.6 Estudiante

- **Tarjeta P0**: estado actual de su expediente + fecha límite si aplica.
- **Listas P0**: requisitos pendientes (PENDIENTE/SOLICITADO), observados con motivo, documentos entregados (versión vigente), notificaciones no leídas.
- **P1**: línea de tiempo del proceso (HistorialEstado), próximo hito.

### 5.7 Administrador

- **Tarjetas P0**: usuarios registrados/activos; expedientes totales y por estado; procesos culminados.
- **P1**: distribución por carrera (UUID hasta que exista catálogo BE-10), por período académico; evolución mensual de solicitudes; tiempo promedio de trámite.
- **P2**: volumen de auditoría por acción.

## 6. CATÁLOGO DE KPI

Convención de ID: `KPI-<área>-<número>`. Unidad: `#` (conteo), `%`, `días`. Prioridad: **P0** esencial para operar, **P1** supervisión, **P2** analítico.

### 6.1 Estudiante

| ID | Nombre | Prio | Definición / Fórmula | Fuente | Unidad | Visualización |
|---|---|---|---|---|---|---|
| KPI-EST-01 | Estado actual del trámite | P0 | Valor de `estado` del expediente activo del usuario (el de `activa=True`; si hay varios, el más reciente) | `ExpedienteTitulacion` | enum | Tarjeta de estado + badge |
| KPI-EST-02 | Requisitos pendientes de entrega | P0 | `count(PeticionDocumental where expediente=mío and estado_peticion in (PENDIENTE, SOLICITADO))` | `PeticionDocumental` | # | Tarjeta + lista |
| KPI-EST-03 | Requisitos observados | P0 | `count(... estado_peticion = OBSERVADO)` con motivo de la observación pendiente (`ObservacionAccionable.resuelta=False`) | `PeticionDocumental` + `ObservacionAccionable` | # | Alerta + lista con motivo |
| KPI-EST-04 | Documentos entregados (vigentes) | P1 | `count(DocumentoEntregado where peticion∈mías and es_vigente=True)` | `DocumentoEntregado` | # | Tarjeta |
| KPI-EST-05 | Notificaciones sin leer | P0 | `count(NotificacionInterna where usuario_destino=yo and leida=False)` | `NotificacionInterna` | # | Badge/alerta |
| KPI-EST-06 | Fecha límite de atención | P0 | `fecha_limite_atencion` del expediente activo; derivado: días restantes = fecha − hoy | `ExpedienteTitulacion` | fecha/días | Tarjeta con semáforo |
| KPI-EST-07 | Progreso del checklist | P1 | `verificados / total_requisitos` del expediente (total = 5 en Fase 1) | `ChecklistVerification` | % | Barra de progreso |
| KPI-EST-08 | Hitos del proceso | P2 | Lista ordenada de `HistorialEstado` del expediente | `HistorialEstado` | — | Timeline |

### 6.2 Secretaría de Carrera (ámbito: su `carrera_id`)

| ID | Nombre | Prio | Definición / Fórmula | Fuente | Unidad | Visualización |
|---|---|---|---|---|---|---|
| KPI-SEC-01 | Expedientes en atención | P0 | `count(Expediente where carrera_id=mi_carrera and estado in (ENVIADA, EN_VERIFICACION, OBSERVADA))` | `ExpedienteTitulacion` | # | Tarjeta |
| KPI-SEC-02 | Expedientes con plazo vencido | P0 | `count(... estado not in (DECLARADA_APTA, CANCELADA, BORRADOR) and fecha_limite_atencion < hoy)` | `ExpedienteTitulacion` | # | Alerta roja |
| KPI-SEC-03 | Certificados por emitir | P0 | `count(PeticionDocumental p join Expediente e where e.carrera_id=mi_carrera and p.dependencia_emisora='SECRETARIA_CARRERA' and p.estado_peticion in (PENDIENTE, SOLICITADO))` | `PeticionDocumental` | # | Tarjeta + lista de trabajo |
| KPI-SEC-04 | Documentos pendientes de validación | P0 | `count(ChecklistVerification v join e where e.carrera_id=mi_carrera and v.estado_verificacion='PENDIENTE' and petición asociada en CARGADO)` | `ChecklistVerification` | # | Tarjeta |
| KPI-SEC-05 | Solicitudes recibidas en el período | P1 | `count(Expediente where carrera_id=mi_carrera and fecha_recepcion entre inicio y fin del filtro)` | `ExpedienteTitulacion` | # | Tarjeta + serie temporal |
| KPI-SEC-06 | Expedientes observados abiertos | P1 | `count(... estado='OBSERVADA')` | `ExpedienteTitulacion` | # | Tarjeta |
| KPI-SEC-07 | Expedientes culminados en el período | P1 | `count(... estado='DECLARADA_APTA' and fecha_declaratoria∈período)` (join con `DeclaratoriaAptitud.fecha_declaratoria`) | `DeclaratoriaAptitud` | # | Tarjeta |
| KPI-SEC-08 | Tiempo promedio de atención | P2 | `avg(fecha_declaratoria − fecha_recepcion)` sobre expedientes DECLARADA_APTA de la cohorte del filtro; los abiertos **no** se incluyen (evita sesgo) | `ExpedienteTitulacion` + `DeclaratoriaAptitud` | días | Tarjeta |

### 6.3 Secretario Abogado / Analista (ámbito: su `facultad_id`)

| ID | Nombre | Prio | Definición / Fórmula | Fuente | Unidad |
|---|---|---|---|---|---|
| KPI-JUR-01 | Expedientes en verificación | P0 | `count(Expediente where facultad_id=mi_facultad and estado='EN_VERIFICACION')` | `ExpedienteTitulacion` | # |
| KPI-JUR-02 | Requisitos por evaluar | P0 | `count(ChecklistVerification where expediente∈mi_facultad and estado_verificacion='PENDIENTE')` | `ChecklistVerification` | # |
| KPI-JUR-03 | Observaciones sin resolver | P0 | `count(ObservacionAccionable where expediente∈mi_facultad and resuelta=False)` | `ObservacionAccionable` | # |
| KPI-JUR-04 | Listos para informe | P0 | `count(Expediente e where e.facultad_id=mi_facultad and e.estado='EN_VERIFICACION' and not exists (checklist ≠ VERIFICADO))` — equivalente a `is_checklist_fully_verified` agregado | `ChecklistVerification` | # |
| KPI-JUR-05 | Informes emitidos en el período | P1 | `count(InformeAptitud where fecha_emision∈período and expediente.facultad_id=mi_facultad)` | `InformeAptitud` | # |
| KPI-JUR-06 | Expedientes observados (esperando subsanación) | P1 | `count(Expediente where facultad_id=mi_facultad and estado='OBSERVADA')` | `ExpedienteTitulacion` | # |
| KPI-JUR-07 | Plazo vencido | P1 | igual que KPI-SEC-02 con ámbito facultad | `ExpedienteTitulacion` | # |

### 6.4 Decano (ámbito: su `facultad_id`)

| ID | Nombre | Prio | Definición / Fórmula | Fuente | Unidad |
|---|---|---|---|---|---|
| KPI-DEC-01 | Pendientes de declaratoria | P0 | `count(Expediente where facultad_id=mi_facultad and estado='INFORME_EMITIDO')` | `ExpedienteTitulacion` | # |
| KPI-DEC-02 | Declaratorias firmadas en el período | P0 | `count(DeclaratoriaAptitud d join e where e.facultad_id=mi_facultad and d.fecha_declaratoria∈período)` | `DeclaratoriaAptitud` | # |
| KPI-DEC-03 | Procesos activos de la facultad | P1 | `count(Expediente where facultad_id=mi_facultad and estado not in (DECLARADA_APTA, CANCELADA))` | `ExpedienteTitulacion` | # |
| KPI-DEC-04 | Tasa de culminación (facultad) | P1 | `(expedientes DECLARADA_APTA con fecha_recepcion en la cohorte / expedientes con fecha_recepcion en la cohorte) × 100`. **Cohorte**: expedientes ENVIADOS (fecha_recepcion no nula) dentro del rango; los BORRADOR se excluyen del denominador (no iniciaron formalmente) | `ExpedienteTitulacion` | % |
| KPI-DEC-05 | Distribución por estado | P2 | `group by estado` sobre expedientes de la facultad | `ExpedienteTitulacion` | # por estado |

### 6.5 Director de Carrera (ámbito: su `carrera_id`)

| ID | Nombre | Prio | Definición / Fórmula | Fuente | Unidad |
|---|---|---|---|---|---|
| KPI-DIR-01 | Procesos activos de la carrera | P0 | `count(Expediente where carrera_id=mi_carrera and estado not in (DECLARADA_APTA, CANCELADA, BORRADOR))` | `ExpedienteTitulacion` | # |
| KPI-DIR-02 | Procesos culminados en el período | P0 | igual que KPI-SEC-07 | `DeclaratoriaAptitud` | # |
| KPI-DIR-03 | Plazo vencido | P0 | igual que KPI-SEC-02 | `ExpedienteTitulacion` | # |
| KPI-DIR-04 | Tasa de culminación (carrera) | P1 | igual que KPI-DEC-04 con ámbito carrera | `ExpedienteTitulacion` | % |
| KPI-DIR-05 | Tiempo promedio de trámite | P1 | igual que KPI-SEC-08 con ámbito carrera | `ExpedienteTitulacion`+`DeclaratoriaAptitud` | días |
| KPI-DIR-06 | Distribución por estado | P2 | `group by estado` (ámbito carrera) | `ExpedienteTitulacion` | # |
| KPI-DIR-07 | Distribución por período académico | P2 | `group by year(fecha_recepcion)` (no existe campo de período académico; ver §9) | `ExpedienteTitulacion` | # |

### 6.6 Responsable de Dependencia

| ID | Nombre | Prio | Definición / Fórmula | Fuente | Unidad |
|---|---|---|---|---|---|
| KPI-DEP-01 | Solicitudes dirigidas a mi dependencia | P0 | `count(PeticionDocumental p where p.dependencia_emisora ∈ roles_del_usuario and p.estado_peticion='SOLICITADO')` | `PeticionDocumental` | # |
| KPI-DEP-02 | Pendientes sin solicitud formal | P1 | ídem con `estado_peticion='PENDIENTE'` | `PeticionDocumental` | # |
| KPI-DEP-03 | Observadas por corregir | P1 | ídem con `estado_peticion='OBSERVADO'` | `PeticionDocumental` | # |

### 6.7 Administrador (ámbito: global)

| ID | Nombre | Prio | Definición / Fórmula | Fuente | Unidad |
|---|---|---|---|---|---|
| KPI-ADM-01 | Usuarios registrados / con rol | P0 | `count(User)`, `count(UserRole)` (y por rol) | `User`, `UserRole` | # |
| KPI-ADM-02 | Expedientes totales y por estado | P0 | `count(Expediente)`, `group by estado` | `ExpedienteTitulacion` | # |
| KPI-ADM-03 | Procesos culminados (histórico) | P0 | `count(DeclaratoriaAptitud)` | `DeclaratoriaAptitud` | # |
| KPI-ADM-04 | Tasa de culminación global | P1 | igual que KPI-DEC-04 sin filtro de ámbito | `ExpedienteTitulacion` | % |
| KPI-ADM-05 | Tiempo promedio de trámite global | P1 | igual que KPI-SEC-08 sin filtro | — | días |
| KPI-ADM-06 | Evolución mensual de solicitudes | P1 | `count(Expediente) group by month(fecha_recepcion)` de los últimos N meses (incluye meses en 0) | `ExpedienteTitulacion` | #/mes |
| KPI-ADM-07 | Distribución por carrera | P2 | `group by carrera_id` (**UUID**; requiere catálogo BE-10 para nombres) | `ExpedienteTitulacion` | # |
| KPI-ADM-08 | Actividad de auditoría por acción | P2 | `count(EventoAuditoria) group by accion` en el período | `EventoAuditoria` | # |
| KPI-ADM-09 | Usuarios activos (con sesión reciente) | P2 | **No calculable hoy**: no existe `last_login` fiable expuesto ni tabla de sesiones de API (JWT stateless). Alternativa: `User.last_login` del admin | `User` | # |

### 6.8 KPI solicitados que NO son calculables con el modelo actual

| KPI solicitado | Motivo | Dato necesario (dependencia) |
|---|---|---|
| Estudiantes sin tutor / tutores asignados / cargas de tutor | No existe entidad de director/tutor de trabajo de titulación (Fase 1 = Declaratoria de Aptitud Legal; el director de trabajo es solo un requisito documental `ART235-04`) | Modelo de asignación tutor-estudiante (fase futura del trámite) |
| Sustentaciones programadas/realizadas y sus resultados | No existe entidad de sustentación ni calificaciones | Modelo de sustentación (fase futura) |
| Distribución por modalidad de titulación | No existe campo `opcion_titulacion` (dependencia BE-06 de specs/003) | Campo/modalidad en el expediente |
| Distribución por período académico oficial | No existe entidad de período académico | Catálogo de períodos o FK a SGA |
| Nombres de carrera/facultad en KPIs | Solo hay `carrera_id`/`facultad_id` UUID | Catálogo de carreras (dependencia BE-10) |
| Procesos abandonados | No existe definición formal ni estado | Decisión institucional + regla (p. ej. sin actividad N días) |
| Usuarios activos reales | JWT stateless sin registro de sesiones | Tabla de sesiones o métrica de auditoría por usuario |

Estos KPI quedan **documentados como no implementables** hasta que exista la fuente de datos. Ningún endpoint debe fingirlos.

## 7. FÓRMULAS — precisiones clave

- **Cohorte de la tasa de culminación**: expedientes con `fecha_recepcion IS NOT NULL` dentro del rango filtrado (el envío formal marca el inicio real del trámite). Los BORRADOR se excluyen de numerador y denominador. `CANCELADA` se excluye del numerador; su tratamiento en el denominador se documentará por decisión (recomendado: excluirla y reportar su conteo aparte).
- **Tiempo promedio**: solo expedientes con `fecha_declaratoria` (proceso cerrado). Promedio en días calendario de `(fecha_declaratoria − fecha_recepcion)`; se documenta también el promedio en días **laborables** usando `dias_laborables_acumulados` + días transcurridos, si se requiere coherencia con el plazo regulatorio.
- **Deduplicación**: los KPI de expedientes cuentan **expedientes** (una fila por expediente), nunca documentos; los KPI de documentos cuentan peticiones/documentos explícitamente. Ningún expediente se cuenta dos veces.
- **Períodos sin información**: toda serie temporal devuelve meses con `0` (generados por `generate_series` en PostgreSQL), no omisiones.

## 8. FUENTES DE DATOS

| Fuente | KPIs que alimentan |
|---|---|
| `ExpedienteTitulacion` | SEC-01/02/05/06, JUR-01/06/07, DEC-01/03/04/05, DIR-01/03/04/06/07, ADM-02/04/06/07, EST-01/06 |
| `PeticionDocumental` | SEC-03, DEP-01/02/03, EST-02/03 |
| `DocumentoEntregado` | EST-04 |
| `ChecklistVerification` | SEC-04, JUR-02/04, EST-07 |
| `ObservacionAccionable` | JUR-03, EST-03 |
| `InformeAptitud` | JUR-05 |
| `DeclaratoriaAptitud` | SEC-07, DEC-02, DIR-02, ADM-03 |
| `NotificacionInterna` | EST-05 |
| `HistorialEstado` | EST-08 |
| `EventoAuditoria` | ADM-08 |
| `User`/`UserRole` | ADM-01/09 |

## 9. REQUISITOS DE INFORMACIÓN FALTANTE

Ver §6.8. Resumen de dependencias (alineadas con BE-01…BE-11 de `specs/003`): catálogo de carreras (BE-10), modalidad de titulación (BE-06), modelos de tutoría y sustentación (fases futuras del trámite), definición institucional de "abandonado". Ninguna debe resolverse simulando datos.

## 10. DISEÑO DE APIS DE INDICADORES (PROPUESTA)

> **Estado: propuesta técnica.** No existe hoy ningún endpoint de indicadores. Antes de implementar, confirmar que no duplica funcionalidad (verificado: no existe equivalente) y obtener autorización.

### 10.1 Arquitectura

- **Capa de servicios de indicadores**: nueva app `indicadores` (o módulo dentro de `core`) con `services/indicadores.py` que centraliza todas las fórmulas; los ViewSets solo serializan. Evita duplicidad entre dashboards y endpoints analíticos.
- **Patrón de respuesta único**: `{ "generado_en": ISO, "ambito": {...}, "resumen": {...}, "detalle": {...} }`.
- **Reutilización del ámbito RBAC**: los ViewSets usan `ScopeFilterMixin` con los mismos mapeos existentes; el ADMINISTRADOR recibe ámbito global, los demás su propio `carrera_id`/`facultad_id` (tomado del token/usuario, **nunca** de parámetros del cliente).

### 10.2 Endpoints propuestos (solo lectura, JWT + HasRolePermission)

| Endpoint | Rol(es) | Contenido |
|---|---|---|
| `GET /api/v1/dashboard/me/` | todos | **Recomendado como único punto de entrada**: el servidor compone el dashboard según los roles del usuario (evita 7 endpoints y filtrado en frontend) |
| `GET /api/v1/indicadores/expedientes/?estado=&desde=&hasta=` | SECRETARIA_CARRERA, DIRECTOR_CARRERA, DECANO, ADMINISTRADOR | Serie y distribución por estado |
| `GET /api/v1/indicadores/culminacion/?cohorte_desde=&cohorte_hasta=` | DIRECTOR_CARRERA, DECANO, ADMINISTRADOR | Tasa de culminación y tiempo promedio |
| `GET /api/v1/indicadores/evolucion/?meses=12` | ADMINISTRADOR, DIRECTOR_CARRERA, DECANO | Serie mensual |

Alternativa por rol (si se prefiere un endpoint explícito por dashboard): `/api/v1/dashboard/estudiante/`, `/dashboard/secretaria/`, `/dashboard/jurista/`, `/dashboard/decano/`, `/dashboard/director/`, `/dashboard/dependencia/`, `/dashboard/administrador/`. **Decisión recomendada**: `/dashboard/me/` + parámetros de sección, por menor superficie y menos duplicación.

### 10.3 Restricciones de diseño

1. Solo `GET`; sin estado.
2. Permisos del usuario autenticado; sin parámetros que amplíen el ámbito (p. ej. un DIRECTOR no puede consultar otra carrera).
3. Agregaciones en la base (`Count`, `Avg`, `TruncMonth`, `generate_series` para series completas); sin N+1; sin traer filas personales salvo las listas de trabajo explícitas del rol (limitadas y paginadas).
4. Filtros acotados a whitelist (`estado` ∈ enum real, rango de fechas con límite máximo, `meses` ≤ 24).
5. Respuestas consistentes (mismo envelope) y `Cache-Control: no-store` para datos operativos.

### 10.4 Ejemplo de respuesta (ilustrativo, campos = modelos reales)

`GET /api/v1/dashboard/me/` con rol SECRETARIA_CARRERA:

```json
{
  "generado_en": "2026-11-05T14:30:00Z",
  "ambito": { "tipo": "carrera", "carrera_id": "5f0c…" },
  "resumen": {
    "expedientes_en_atencion": 12,
    "plazo_vencido": 2,
    "certificados_por_emitir": 5,
    "documentos_por_validar": 7,
    "observados_abiertos": 3
  },
  "cola_atencion": [
    {
      "expediente_id": "…",
      "numero_expediente": "EXP-2026-0031",
      "estado": "EN_VERIFICACION",
      "fecha_limite_atencion": "2026-11-08",
      "dias_restantes": 3
    }
  ],
  "distribucion_estado": {
    "ENVIADA": 4, "EN_VERIFICACION": 6, "OBSERVADA": 2,
    "INFORME_EMITIDO": 1, "DECLARADA_APTA": 9
  }
}
```

Los valores son ilustrativos de estructura, no datos reales.

## 11. ESTRATEGIA DE CONSULTAS POSTGRESQL

- Conteos por estado: `ExpedienteTitulacion.objects.filter(ámbito).values("estado").annotate(total=Count("id"))` — usa el índice `estado` existente.
- Series mensuales: `TruncMonth("fecha_recepcion")` + `Count`, completadas con `generate_series` en SQL crudo o en Python (preferible SQL para P2).
- Tiempo promedio: `Avg(F("declaratoria__fecha_declaracion") - F("fecha_recepcion"))` con join 1:1 (OneToOne ya indexado).
- Listos para informe: `annotate(total_verif=Count("checklist_verificaciones"), verif=Count("checklist_verificaciones", filter=Q(estado_verificacion="VERIFICADO"))).filter(total_verif=F("verif"))`.
- Todas las consultas de dashboard se ejecutan en ≤ 5 agregaciones; sin `len(queryset)` ni conteos en Python.

## 12. SEGURIDAD Y PERMISOS

- Recursos RBAC nuevos en la matriz: `dashboard` (GET) con celdas: todos los roles → su ámbito; `RESPONSABLE_DEPENDENCIA` → `asignado` (solo KPI-DEP); sin celda = denegado (mundo cerrado).
- El ámbito se deriva del usuario autenticado; ningún parámetro de cliente puede sobreescribir `carrera_id`/`facultad_id`.
- Los KPI nunca exponen datos personales de terceros salvo las listas de trabajo autorizadas por la matriz existente (mismos campos que la bandeja).

## 13. ESTRATEGIA DE PRUEBAS

- **Unitarias de fórmulas**: por cada KPI, caso con 0 elementos, 1, N, y períodos vacíos (serie con ceros).
- **De permisos**: cada rol consulta su dashboard y recibe solo su ámbito; un DIRECTOR no ve otra carrera (404/ámbito vacío); ESTUDIANTE no accede a indicadores agregados de otros (403 por matriz).
- **De consistencia**: comparación contra conteos construidos con ORM independiente en el test (doble cálculo).
- **De contrato**: esquemas de respuesta estables (drf-spectacular los documenta).
- Meta: cobertura de la app de indicadores ≥ 90 %, coherente con el estándar actual (93 %).

## 14. RECOMENDACIONES PARA EL FRONTEND

- Un componente `DashboardPage` por rol con layout de tarjetas + 1 gráfico máximo por fila; sin saturación (≤ 6 tarjetas P0 visibles).
- Estados obligatorios por componente: carga (Spinner), vacío (`EmptyState` con acción), error (`ErrorState` con reintentar), sin permisos (`ForbiddenState`), ya existentes en el design system.
- Filtros de período solo donde el KPI lo define (P1/P2); el P0 siempre es "hoy".
- Acceso vía `GET /api/v1/dashboard/me/` con TanStack Query (`staleTime: 30s`); sin cálculos de negocio en el cliente: los únicos valores derivados permitidos son presentacionales (p. ej. `dias_restantes = fecha − hoy`).
- Accesibilidad AA + axe en cada tarjeta/gráfico (doc 05 de diseño UI); responsive desde 320 px.

## 15. PLAN DE IMPLEMENTACIÓN PRIORIZADO (PROPUESTA)

| Fase | Contenido | KPIs | Dependencias |
|---|---|---|---|
| I-1 (P0) | App `indicadores` + `GET /dashboard/me/` con secciones ESTUDIANTE, SECRETARIA, JURISTA, DECANO | EST-01/02/03/05/06, SEC-01/02/03/04, JUR-01/02/03/04, DEC-01/02 | Ninguna (datos existentes) |
| I-2 (P1) | Secciones DIRECTOR, DEPENDENCIA + endpoints analíticos de culminación | DIR-01/02/03, DEP-01/02/03, DEC-04, ADM-02/03/04/05/06 | Ninguna |
| I-3 (P2) | Series de evolución, distribuciones, auditoría | DIR-06/07, ADM-07/08, EST-07/08 | BE-10 (nombres de carrera) para ADM-07 |
| I-4 (bloqueado) | KPIs de tutoría, sustentación, modalidad, períodos | §6.8 | Modelos futuros del trámite |

---

## 16. RESUMEN DEL CATÁLOGO

- **KPI definidos**: 40 (EST 8, SEC 8, JUR 7, DEC 5, DIR 7, DEP 3, ADM 9 — con solapamientos de fórmula reutilizados por ámbito).
- **Implementables con datos actuales**: 33.
- **No implementables hoy**: 7 (§6.8) — requieren modelos o decisiones institucionales; quedan documentados sin fórmula fingida.
