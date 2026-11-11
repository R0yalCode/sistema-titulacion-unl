# MATRIZ DE KPIs: MODALIDADES DE TITULACIÓN — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` §5 + `INFORME_DISENO_KPI.md` + `DISENO_FUNCIONAL_MODALIDADES_TITULACION.md`  

---

## 1. RESUMEN KPIs MODALIDADES (KPI-MOD-01 a 08)

| ID | Nombre | Prioridad | Fórmula Resumida | Fuente | Endpoint | Roles |
|----|--------|-----------|------------------|--------|----------|-------|
| **KPI-MOD-01** | Total Trabajo Integración Curricular | P0 | `count(Expediente opcion_titulacion='TIC')` | ExpedienteTitulacion | `/indicadores/modalidades/` | Todos |
| **KPI-MOD-02** | Total Examen Complexivo | P0 | `count(Expediente opcion_titulacion='EC')` | ExpedienteTitulacion | `/indicadores/modalidades/` | Todos |
| **KPI-MOD-03** | Porcentajes TIC / EC | P0 | `(MOD-01/total)*100`, `(MOD-02/total)*100` | ExpedienteTitulacion | `/indicadores/modalidades/` | Todos |
| **KPI-MOD-04** | Distribución por Carrera | P1 | `group by carrera_id, opcion_titulacion` | ExpedienteTitulacion | `?agrupar=carrera` | Director, Decano, Admin |
| **KPI-MOD-05** | Distribución por Período Académico | P1 | `group by year(fecha_recepcion), opcion_titulacion` | ExpedienteTitulacion | `?agrupar=periodo` | Director, Decano, Admin |
| **KPI-MOD-06** | Estudiantes Elegibles para EC | P1 | `count(Estudiantes 2 reprobaciones + 3ra matrícula)` | Mock SGA + Expediente | `/indicadores/elegibilidad-ec/` | Secretario, Decano, Admin |
| **KPI-MOD-07** | Estudiantes Habilitados para EC | P1 | `count(Expediente opcion_titulacion='EC' estado≠BORRADOR)` | ExpedienteTitulacion | `/indicadores/modalidades/` | Secretario, Decano, Admin |
| **KPI-MOD-08** | Cambios de Modalidad Autorizados | P1 | `count(HistorialModalidad modalidad_nueva='EC')` | HistorialModalidad | `/indicadores/cambios-modalidad/` | Admin, Decano |

---

## 2. ESPECIFICACIÓN DETALLADA POR KPI

### 2.1 KPI-MOD-01: Total Trabajo Integración Curricular (TIC)

| Atributo | Valor |
|----------|-------|
| **Definición** | Número total de expedientes activos con modalidad Trabajo de Integración Curricular |
| **Fórmula SQL** | `SELECT count(*) FROM expedientes_expedientetitulacion WHERE activa = true AND opcion_titulacion = 'TIC'` |
| **Filtros opcionales** | `carrera_id`, `facultad_id`, `estado`, `fecha_recepcion` (rango) |
| **Agrupaciones** | Ninguna (total global) / `carrera_id` / `facultad_id` / `year(fecha_recepcion)` / `estado` |
| **Unidad** | Entero (conteo expedientes) |
| **Frecuencia actualización** | Tiempo real (consulta BD) |
| **Permisos** | `SCOPE_OWN` (estudiante ve 0/1), `SCOPE_CARRERA`, `SCOPE_FACULTAD`, `SCOPE_ALL` |
| **Visualización** | Tarjeta KPI grande + gráfico pie (TIC vs EC) |
| **Endpoint** | `GET /api/v1/indicadores/modalidades/` → `total_tic` |

### 2.2 KPI-MOD-02: Total Examen Complexivo (EC)

| Atributo | Valor |
|----------|-------|
| **Definición** | Número total de expedientes activos con modalidad Examen Complexivo |
| **Fórmula SQL** | `SELECT count(*) FROM expedientes_expedientetitulacion WHERE activa = true AND opcion_titulacion = 'EC'` |
| **Filtros opcionales** | `carrera_id`, `facultad_id`, `estado`, `fecha_recepcion` (rango) |
| **Agrupaciones** | Ninguna / `carrera_id` / `facultad_id` / `year(fecha_recepcion)` / `estado` |
| **Unidad** | Entero (conteo expedientes) |
| **Frecuencia actualización** | Tiempo real |
| **Permisos** | Igual KPI-MOD-01 |
| **Visualización** | Tarjeta KPI + gráfico pie |
| **Endpoint** | `GET /api/v1/indicadores/modalidades/` → `total_ec` |

### 2.3 KPI-MOD-03: Porcentajes TIC / EC

| Atributo | Valor |
|----------|-------|
| **Definición** | Porcentaje de cada modalidad sobre total expedientes activos |
| **Fórmula** | `%TIC = (KPI-MOD-01 / (KPI-MOD-01 + KPI-MOD-02)) * 100`<br>`%EC = (KPI-MOD-02 / (KPI-MOD-01 + KPI-MOD-02)) * 100` |
| **Precisión** | 2 decimales |
| **Caso borde** | Total = 0 → 0.00% ambos |
| **Visualización** | Gráfico pie/donut + tarjetas con % |
| **Endpoint** | `GET /api/v1/indicadores/modalidades/` → `porcentaje_tic`, `porcentaje_ec` |

### 2.4 KPI-MOD-04: Distribución por Carrera

| Atributo | Valor |
|----------|-------|
| **Definición** | Conteo de expedientes por carrera y modalidad |
| **Fórmula SQL** | `SELECT carrera_id, opcion_titulacion, count(*) FROM expedientes_expedientetitulacion WHERE activa = true GROUP BY carrera_id, opcion_titulacion` |
| **Filtros** | `facultad_id`, `estado`, `fecha_recepcion` rango |
| **Formato respuesta** | `[{carrera_id: "uuid", tic: 15, ec: 3, total: 18}, ...]` |
| **Nota** | `carrera_id` es UUID; nombres requieren BE-10 (catálogo carreras) |
| **Permisos** | `SCOPE_CARRERA` (Director/Secretaria ven su carrera), `SCOPE_FACULTAD` (Decano/Jurista ven facultad), `SCOPE_ALL` (Admin) |
| **Endpoint** | `GET /api/v1/indicadores/modalidades/?agrupar=carrera` → `por_carrera` |

### 2.5 KPI-MOD-05: Distribución por Período Académico

| Atributo | Valor |
|----------|-------|
| **Definición** | Conteo de expedientes por año de recepción y modalidad |
| **Fórmula SQL** | `SELECT EXTRACT(YEAR FROM fecha_recepcion) as periodo, opcion_titulacion, count(*) FROM expedientes_expedientetitulacion WHERE activa = true AND fecha_recepcion IS NOT NULL GROUP BY periodo, opcion_titulacion ORDER BY periodo` |
| **Formato respuesta** | `[{periodo: 2025, tic: 12, ec: 2}, {periodo: 2026, tic: 8, ec: 1}, ...]` |
| **Meses sin datos** | Incluir años con 0 (generate_series equivalente) |
| **Permisos** | Igual KPI-MOD-04 |
| **Endpoint** | `GET /api/v1/indicadores/modalidades/?agrupar=periodo` → `por_periodo` |

### 2.6 KPI-MOD-06: Estudiantes Elegibles para EC

| Atributo | Valor |
|----------|-------|
| **Definición** | Estudiantes que cumplen requisitos para Examen Complexivo (2 reprobaciones + 3ra matrícula) |
| **Fuente** | **Mock SGA** (simulado) + `ExpedienteTitulacion` (para excluir ya habilitados) |
| **Fórmula** | `count(DISTINCT estudiante_id) WHERE reprobaciones_titulacion >= 2 AND tercera_matricula.activa = true AND NOT EXISTS (Expediente opcion_titulacion='EC')` |
| **Mock SGA requerido** | Servicio simulado que retorna por estudiante: `{reprobaciones, tercera_matricula, detalles}` |
| **Filtros** | `carrera_id`, `facultad_id` (desde atributos estudiante en mock) |
| **Permisos** | `SECRETARIO_ABOGADO` (facultad), `DECANO` (facultad), `ADMINISTRADOR` (all) |
| **Endpoint** | `GET /api/v1/indicadores/elegibilidad-ec/` |
| **Visualización** | Tarjeta "Elegibles EC" + lista estudiantes (nombre/cédula/carrera) |

### 2.7 KPI-MOD-07: Estudiantes Habilitados para EC

| Atributo | Valor |
|----------|-------|
| **Definición** | Expedientes que **ya tienen** modalidad EC asignada (excluye BORRADOR) |
| **Fórmula SQL** | `SELECT count(*) FROM expedientes_expedientetitulacion WHERE activa = true AND opcion_titulacion = 'EC' AND estado != 'BORRADOR'` |
| **Diferencia KPI-MOD-02** | KPI-MOD-02 = total EC (incluye BORRADOR); KPI-MOD-07 = EC en proceso |
| **Filtros** | `carrera_id`, `facultad_id`, `estado`, `fecha_recepcion` |
| **Permisos** | `SECRETARIO_ABOGADO`, `DECANO`, `ADMINISTRADOR` |
| **Endpoint** | `GET /api/v1/indicadores/modalidades/` → `habilitados_ec` |

### 2.8 KPI-MOD-08: Cambios de Modalidad Autorizados

| Atributo | Valor |
|----------|-------|
| **Definición** | Número de cambios de modalidad TIC → EC autorizados en el período |
| **Fuente** | `HistorialModalidad` (nuevo modelo INC-03) |
| **Fórmula SQL** | `SELECT count(*) FROM expedientes_historialmodalidad WHERE modalidad_nueva = 'EC' AND fecha_cambio BETWEEN :desde AND :hasta` |
| **Filtros** | `fecha_cambio` rango, `carrera_id` (via expediente), `facultad_id`, `autorizado_por` |
| **Permisos** | `DECANO` (facultad), `ADMINISTRADOR` (all) |
| **Endpoint** | `GET /api/v1/indicadores/cambios-modalidad/` (nuevo endpoint) |
| **Visualización** | Tarjeta + serie temporal mensual |

---

## 3. REGLAS DE CÁLCULO Y NO DUPLICACIÓN

### 3.1 Principio Fundamental
> **Cada expediente se cuenta UNA SOLA VEZ por su `opcion_titulacion` ACTUAL.**
> El historial (`HistorialModalidad`) **solo** se usa para KPI-MOD-08 (cambios autorizados).

### 3.2 Distinciones Críticas

| Concepto | Definición | KPI Asociado |
|----------|------------|--------------|
| **Modalidad actual** | `ExpedienteTitulacion.opcion_titulacion` valor actual | MOD-01, MOD-02, MOD-03, MOD-04, MOD-05, MOD-07 |
| **Modalidad histórica** | Registros en `HistorialModalidad` | MOD-08 únicamente |
| **Estudiante elegible** | Cumple requisitos EC (mock SGA) **pero** no ha cambiado modalidad | MOD-06 |
| **Estudiante habilitado** | Ya tiene expediente con `opcion_titulacion = 'EC'` y estado ≠ BORRADOR | MOD-07 |
| **Cambio autorizado** | Registro en `HistorialModalidad` con `modalidad_nueva = 'EC'` | MOD-08 |

### 3.3 Evitar Doble Conteo
```sql
-- INCORRECTO (duplica expedientes con historial):
SELECT count(*) FROM expedientes_expedientetitulacion e
JOIN expedientes_historialmodalidad h ON h.expediente_id = e.id
WHERE e.opcion_titulacion = 'EC' OR h.modalidad_nueva = 'EC';

-- CORRECTO (solo modalidad actual):
SELECT count(*) FROM expedientes_expedientetitulacion 
WHERE activa = true AND opcion_titulacion = 'EC';
```

---

## 4. ENDPOINTS Y PARÁMETROS

### 4.1 `GET /api/v1/indicadores/modalidades/`

| Parámetro | Tipo | Requerido | Descripción | Valores |
|-----------|------|-----------|-------------|---------|
| `agrupar` | string | No | Agrupación adicional | `carrera`, `periodo`, `estado` |
| `carrera_id` | UUID | No | Filtrar por carrera (solo Admin/Decano/Director) | UUID válido |
| `facultad_id` | UUID | No | Filtrar por facultad (solo Admin/Decano/Jurista) | UUID válido |
| `estado` | string | No | Filtrar por estado expediente | Enum `EstadoExpediente` |
| `desde` | date | No | Fecha recepción desde | YYYY-MM-DD |
| `hasta` | date | No | Fecha recepción hasta | YYYY-MM-DD |

**Respuesta base:**
```json
{
  "total_tic": 142,
  "total_ec": 18,
  "porcentaje_tic": 88.75,
  "porcentaje_ec": 11.25,
  "por_carrera": {"uuid-carrera-1": {"tic": 25, "ec": 3}, ...},
  "por_periodo": [{"periodo": 2025, "tic": 80, "ec": 10}, ...],
  "por_estado": {"ENVIADA": {"tic": 30, "ec": 5}, ...},
  "habilitados_ec": 15,
  "generado_en": "2026-11-09T14:30:00Z"
}
```

### 4.2 `GET /api/v1/indicadores/elegibilidad-ec/`

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `carrera_id` | UUID | Filtrar elegibles por carrera |
| `facultad_id` | UUID | Filtrar elegibles por facultad |

**Respuesta:**
```json
{
  "total_elegibles": 7,
  "estudiantes": [
    {"estudiante_id": "uuid", "cedula": "1234567890", "carrera_id": "uuid", "facultad_id": "uuid", "reprobaciones": 2, "tercera_matricula": true}
  ],
  "generado_en": "2026-11-09T14:30:00Z"
}
```

### 4.3 `GET /api/v1/indicadores/cambios-modalidad/` (Nuevo)

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `desde` | date | Fecha cambio desde |
| `hasta` | date | Fecha cambio hasta |
| `carrera_id` | UUID | Filtrar por carrera |
| `facultad_id` | UUID | Filtrar por facultad |

**Respuesta:**
```json
{
  "total_cambios": 12,
  "por_mes": [{"mes": "2026-01", "cambios": 3}, ...],
  "por_carrera": {"uuid": 5},
  "por_autorizador": {"uuid-decano": 8, "uuid-admin": 4},
  "generado_en": "2026-11-09T14:30:00Z"
}
```

---

## 5. PERMISOS RBAC POR KPI

| KPI | Recurso RBAC | Acción | Roles | Scope |
|-----|--------------|--------|-------|-------|
| MOD-01, MOD-02, MOD-03 | `indicadores:modalidades` | GET | Todos | own/carrera/facultad/all |
| MOD-04, MOD-05 | `indicadores:modalidades` | GET (agrupar) | Director, Decano, Admin | carrera/facultad/all |
| MOD-06 | `indicadores:elegibilidad-ec` | GET | Secretario, Decano, Admin | facultad/all |
| MOD-07 | `indicadores:modalidades` | GET | Secretario, Decano, Admin | facultad/all |
| MOD-08 | `indicadores:cambios-modalidad` | GET | Decano, Admin | facultad/all |

**Implementación:** Entradas en `RBAC_MATRIX` + `ROW_TO_SCOPE` (ver `ESPECIFICACION_SERVICIOS_DASHBOARD.md` §6).

---

## 6. VISUALIZACIÓN EN DASHBOARDS

### 6.1 Tarjetas por Rol

| Rol | Tarjetas Modalidad (P0/P1) |
|-----|----------------------------|
| **ESTUDIANTE** | Modalidad actual (badge) + "¿Eres elegible para EC?" (link) |
| **SECRETARIA_CARRERA** | Distribución TIC/EC en su carrera (gráfico pie) |
| **SECRETARIO_ABOGADO** | Elegibles EC (tarjeta + botón verificar) + Habilitados EC |
| **ANALISTA_APOYO** | Solo lectura: Distribución facultad |
| **DECANO** | Elegibles EC + Habilitados EC + Cambios autorizados (tarjetas) + Gráfico evolución cambios |
| **DIRECTOR_CARRERA** | Distribución TIC/EC por carrera + Período |
| **RESPONSABLE_DEPENDENCIA** | N/A (no aplica a peticiones) |
| **ADMINISTRADOR** | Dashboard global: Totales, %, Carrera, Período, Estado, Elegibles, Habilitados, Cambios |

### 6.2 Componente `ModalidadPanel` (Reutilizable)

```tsx
interface ModalidadPanelProps {
  datos: {
    total_tic: number;
    total_ec: number;
    porcentaje_tic: number;
    porcentaje_ec: number;
    elegibles_ec?: number;
    habilitados_ec?: number;
    cambios_autorizados?: number;
    por_carrera?: Record<string, {tic: number; ec: number}>;
    por_periodo?: Array<{periodo: number; tic: number; ec: number}>;
  };
  rol: 'estudiante' | 'secretaria' | 'jurista' | 'decano' | 'director' | 'admin';
  onVerificarElegibilidad?: () => void;
  onVerHistorial?: () => void;
}
```

---

## 7. TESTS DE VALIDACIÓN KPIs

| Test | Descripción | Datos Prueba |
|------|-------------|--------------|
| `test_kpi_mod_01_total_tic` | 15 TIC, 3 EC → total_tic = 15 | 18 expedientes (15 TIC, 3 EC) |
| `test_kpi_mod_02_total_ec` | Same → total_ec = 3 | Same |
| `test_kpi_mod_03_porcentajes` | 15/18 = 83.33%, 3/18 = 16.67% | Same |
| `test_kpi_mod_04_por_carrera` | Carrera A: 10 TIC + 2 EC; Carrera B: 5 TIC + 1 EC | Agrupación correcta |
| `test_kpi_mod_05_por_periodo` | 2025: 8 TIC + 1 EC; 2026: 7 TIC + 2 EC | Serie temporal con ceros |
| `test_kpi_mod_06_elegibles_ec` | Mock SGA: 7 elegibles, 3 ya habilitados | Total = 7 (excluye habilitados) |
| `test_kpi_mod_07_habilitados_ec` | 3 EC totales, 1 en BORRADOR → habilitados = 2 | Excluye BORRADOR |
| `test_kpi_mod_08_cambios_autorizados` | Historial: 12 cambios TIC→EC en 2026 | Conteo correcto |
| `test_no_duplicacion_historial` | Expediente con historial TIC→EC contado 1 vez en MOD-02 | Verifica principio §3.1 |

---

## 8. DEPENDENCIAS Y ORDEN

```
INC-03 (Modalidades Core: modelo + servicios + endpoints)
    ↓
INC-04-T01 a T05 (App indicadores + servicios base + /dashboard/me/)
    ↓
INC-04-T06 (Tests unitarias fórmulas)
    ↓
INC-04-T08 (KPIs modalidades - requiere MOD-01 a MOD-05 en BD)
    ↓
INC-08 (Frontend: ModalidadPanel en dashboards + V-03/V-04/V-08)
```

**Bloqueante:** KPIs modalidades (MOD-01 a 08) **requieren** INC-03 completado (campo `opcion_titulacion` + `HistorialModalidad` en BD).

---

## 9. PRÓXIMOS PASOS

1. **Validar normativa** RRA-UNL (arts. 39, 40, 212, 216, 233) → define fórmulas elegibilidad exactas
2. **Autorizar INC-03** → crea modelo + servicios + mock SGA
3. **Implementar app `indicadores`** (INC-04) con servicios `kpi_modalidades.py`
4. **Tests unitarias** fórmulas (casos 0, 1, N, vacíos, cohortes)
5. **Integrar en `/dashboard/me/`** y endpoint `/indicadores/modalidades/`
6. **Frontend** `ModalidadPanel` + tarjetas por rol (INC-08)