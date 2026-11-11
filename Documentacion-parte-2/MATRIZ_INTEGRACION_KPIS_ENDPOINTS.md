# MATRIZ DE INTEGRACIÓN KPIs - ENDPOINTS — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `INFORME_DISENO_KPI.md` + `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md`  

---

## 1. ARQUITECTURA DE SERVICIOS INDICADORES

### 1.1 Nueva App: `indicadores`
```
backend/src/apps/indicadores/
├── __init__.py
├── services/
│   ├── __init__.py
│   ├── indicadores.py          # Fórmulas centralizadas (reutilizables)
│   ├── kpi_estudiante.py
│   ├── kpi_secretaria.py
│   ├── kpi_jurista.py
│   ├── kpi_decano.py
│   ├── kpi_director.py
│   ├── kpi_dependencia.py
│   ├── kpi_admin.py
│   └── kpi_modalidades.py      # KPIs específicos modalidades (KPI-MOD-01 a 08)
├── adapters/
│   ├── __init__.py
│   ├── views.py                # ViewSets endpoints
│   ├── serializers.py
│   ├── urls.py
│   ├── apps.py
│   └── migrations/
│       └── 0001_initial.py     # Si se requieren modelos auxiliares
└── tests/
    ├── __init__.py
    ├── test_indicadores.py     # Unitarias fórmulas
    ├── test_endpoints.py       # Integración endpoints
    └── test_permisos.py        # RBAC por rol
```

### 1.2 Principio: Centralización de Fórmulas
- **Una sola fuente de verdad** por KPI en `services/indicadores.py`
- ViewSets solo serializan y aplican permisos/ámbito
- Evita duplicidad entre `/dashboard/me/` y endpoints analíticos
- Tests unitarias de fórmulas independientes de HTTP

---

## 2. MAPEO KPI → ENDPOINT → SERVICIO

### 2.1 Endpoint Principal: `GET /api/v1/dashboard/me/`

| Sección Dashboard | KPIs Incluidos | Servicio Origen | Filtro Ámbito |
|-------------------|----------------|-----------------|---------------|
| `resumen.kpi_clave` | 1-3 KPIs críticos por rol | `get_kpi_clave(rol, user)` | `ScopeFilterMixin` |
| `resumen.alertas` | Conteos umbral (plazos, observados) | `get_alertas(rol, user)` | `ScopeFilterMixin` |
| `tarjetas_p0` | 4-6 tarjetas por rol (ver §3) | `get_tarjetas_p0(rol, user)` | `ScopeFilterMixin` |
| `grafico_principal` | 1 gráfico por rol | `get_grafico_principal(rol, user, params)` | `ScopeFilterMixin` |
| `tabla_trabajo` | Lista paginada trabajo diario | `get_tabla_trabajo(rol, user, page, page_size)` | `ScopeFilterMixin` |
| `actividad_reciente` | 5-10 últimos `EventoAuditoria` usuario/ámbito | `get_actividad_reciente(user, ambito)` | `ScopeFilterMixin` |
| `notificaciones_no_leidas` | `count(NotificacionInterna leida=False)` | `NotificacionService` | `SCOPE_OWN` |
| `modalidad_titulacion` | Actual + elegibilidad + historial | `get_modalidad_dashboard(user, rol)` | `ScopeFilterMixin` |

### 2.2 Endpoints Analíticos (P1/P2)

| Endpoint | KPIs | Servicio | Parámetros | Roles |
|----------|------|----------|------------|-------|
| `GET /api/v1/indicadores/modalidades/` | KPI-MOD-01 a 08 | `kpi_modalidades.get_resumen_modalidades()` | `agrupar=carrera|periodo|estado`, `desde`, `hasta` | Secretario, Decano, Director, Admin |
| `GET /api/v1/indicadores/culminacion/` | KPI-SEC-08, DEC-04, DIR-04/05, ADM-04/05 | `kpi_general.get_tasa_culminacion_tiempo()` | `cohorte_desde`, `cohorte_hasta`, `agrupar=carrera|facultad` | Decano, Director, Admin |
| `GET /api/v1/indicadores/evolucion/` | KPI-SEC-05, ADM-06, DIR-07 | `kpi_general.get_evolucion_mensual()` | `meses=12`, `agrupar=carrera|facultad` | Admin, Director, Decano |
| `GET /api/v1/indicadores/elegibilidad-ec/` | KPI-MOD-06 | `kpi_modalidades.get_elegibles_ec()` | `facultad_id`, `carrera_id` | Secretario, Decano, Admin |

---

## 3. DETALLE KPIs POR ROL Y TARJETAS P0

### 3.1 ESTUDIANTE (V-02)
| Tarjeta | KPI | Fórmula | Prioridad |
|---------|-----|---------|-----------|
| Estado actual | KPI-EST-01 | `estado` expediente `activa=True` más reciente | P0 |
| Requisitos pendientes | KPI-EST-02 | `count(PeticionDocumental estado∈{PENDIENTE,SOLICITADO})` | P0 |
| Observados | KPI-EST-03 | `count(PeticionDocumental estado=OBSERVADO ∧ ObservacionAccionable.resuelta=False)` | P0 |
| Notificaciones | KPI-EST-05 | `count(NotificacionInterna leida=False)` | P0 |
| Fecha límite | KPI-EST-06 | `fecha_limite_atencion` + `dias_restantes` | P0 |
| Progreso checklist | KPI-EST-07 | `verificados / 5 * 100` | P1 |

### 3.2 SECRETARIA_CARRERA
| Tarjeta | KPI | Fórmula | Prioridad |
|---------|-----|---------|-----------|
| En atención | KPI-SEC-01 | `count(Expediente carrera∈{ENVIADA,EN_VERIFICACION,OBSERVADA})` | P0 |
| Plazo vencido | KPI-SEC-02 | `count(Expediente carrera estado∉terminales ∧ fecha_limite<hoy)` | P0 |
| Certificados | KPI-SEC-03 | `count(Peticion dependencia=SECRETARIA_CARRERA estado∈{PENDIENTE,SOLICITADO})` | P0 |
| Validación | KPI-SEC-04 | `count(ChecklistVerification estado=PENDIENTE ∧ peticion=CARGADO)` | P0 |
| Observados | KPI-SEC-06 | `count(Expediente carrera estado=OBSERVADA)` | P1 |

### 3.3 SECRETARIO_ABOGADO / ANALISTA_APOYO
| Tarjeta | KPI | Fórmula | Prioridad |
|---------|-----|---------|-----------|
| En verificación | KPI-JUR-01 | `count(Expediente facultad estado=EN_VERIFICACION)` | P0 |
| Por evaluar | KPI-JUR-02 | `count(ChecklistVerification facultad estado=PENDIENTE)` | P0 |
| Observaciones | KPI-JUR-03 | `count(ObservacionAccionable facultad resuelta=False)` | P0 |
| Listos informe | KPI-JUR-04 | `count(Expediente facultad estado=EN_VERIFICACION ∧ ¬∃checklist≠VERIFICADO)` | P0 |
| Plazo vencido | KPI-JUR-07 | Igual KPI-SEC-02 ámbito facultad | P1 |

### 3.4 DECANO
| Tarjeta | KPI | Fórmula | Prioridad |
|---------|-----|---------|-----------|
| Pendientes declaratoria | KPI-DEC-01 | `count(Expediente facultad estado=INFORME_EMITIDO)` | P0 |
| Declaratorias período | KPI-DEC-02 | `count(DeclaratoriaAptitud facultad fecha_declaratoria∈período)` | P0 |
| Tasa culminación | KPI-DEC-04 | `(DECLARADA_APTA cohorte / ENVIADA cohorte) * 100` | P1 |

### 3.5 DIRECTOR_CARRERA
| Tarjeta | KPI | Fórmula | Prioridad |
|---------|-----|---------|-----------|
| Activos carrera | KPI-DIR-01 | `count(Expediente carrera estado∉{DECLARADA_APTA,CANCELADA,BORRADOR})` | P0 |
| Culminados período | KPI-DIR-02 | Igual KPI-SEC-07 | P0 |
| Plazo vencido | KPI-DIR-03 | Igual KPI-SEC-02 | P0 |
| Tasa culminación | KPI-DIR-04 | Igual KPI-DEC-04 ámbito carrera | P1 |
| Tiempo promedio | KPI-DIR-05 | `avg(fecha_declaratoria - fecha_recepcion)` cerrados | P1 |

### 3.6 RESPONSABLE_DEPENDENCIA
| Tarjeta | KPI | Fórmula | Prioridad |
|---------|-----|---------|-----------|
| Solicitudes mi dependencia | KPI-DEP-01 | `count(Peticion dependencia∈roles_usuario estado=SOLICITADO)` | P0 |
| Pendientes sin solicitud | KPI-DEP-02 | Igual `estado=PENDIENTE` | P1 |
| Observadas corregir | KPI-DEP-03 | Igual `estado=OBSERVADO` | P1 |

### 3.7 ADMINISTRADOR
| Tarjeta | KPI | Fórmula | Prioridad |
|---------|-----|---------|-----------|
| Usuarios | KPI-ADM-01 | `count(User)`, `count(UserRole)` por rol | P0 |
| Expedientes | KPI-ADM-02 | `count(Expediente)`, `group by estado` | P0 |
| Culminados | KPI-ADM-03 | `count(DeclaratoriaAptitud)` | P0 |
| Tasa global | KPI-ADM-04 | Igual KPI-DEC-04 sin filtro | P1 |
| Tiempo global | KPI-ADM-05 | Igual KPI-SEC-08 sin filtro | P1 |
| Evolución mensual | KPI-ADM-06 | `count(Expediente) group by month(fecha_recepcion)` | P1 |

---

## 4. KPIs MODALIDADES TITULACIÓN (KPI-MOD-01 a 08)

| ID | Nombre | Fórmula | Fuente | Endpoint | Agrupaciones | Roles |
|----|--------|---------|--------|----------|--------------|-------|
| KPI-MOD-01 | Total TIC | `count(Expediente opcion_titulacion='TIC')` | ExpedienteTitulacion | `/indicadores/modalidades/` | carrera, período, estado | Todos |
| KPI-MOD-02 | Total EC | `count(Expediente opcion_titulacion='EC')` | ExpedienteTitulacion | `/indicadores/modalidades/` | carrera, período, estado | Todos |
| KPI-MOD-03 | % TIC / % EC | `(MOD-01/total)*100`, `(MOD-02/total)*100` | ExpedienteTitulacion | `/indicadores/modalidades/` | — | Todos |
| KPI-MOD-04 | Distribución carrera | `group by carrera_id, opcion_titulacion` | ExpedienteTitulacion | `/indicadores/modalidades/?agrupar=carrera` | carrera | Director, Decano, Admin |
| KPI-MOD-05 | Distribución período | `group by year(fecha_recepcion), opcion_titulacion` | ExpedienteTitulacion | `/indicadores/modalidades/?agrupar=periodo` | período | Director, Decano, Admin |
| KPI-MOD-06 | Elegibles EC | `count(Estudiantes 2 reprobaciones + 3ra matrícula)` | Mock SGA + Expediente | `/indicadores/elegibilidad-ec/` | carrera, facultad | Secretario, Decano, Admin |
| KPI-MOD-07 | Habilitados EC | `count(Expediente opcion_titulacion='EC' estado≠BORRADOR)` | ExpedienteTitulacion | `/indicadores/modalidades/` | carrera, facultad | Secretario, Decano, Admin |
| KPI-MOD-08 | Cambios autorizados | `count(HistorialModalidad modalidad_nueva='EC')` | HistorialModalidad | `/indicadores/cambios-modalidad/` | carrera, facultad, período | Admin, Decano |

**Regla no duplicación:** Expediente contado **una sola vez** por su `opcion_titulacion` **actual**. Historial solo para KPI-MOD-08.

---

## 5. CONSULTAS POSTGRESQL OPTIMIZADAS

### 5.1 Conteos por Estado (usa índice `estado` + `carrera_id`/`facultad_id`)
```sql
SELECT estado, count(*) 
FROM expedientes_expedientetitulacion 
WHERE carrera_id = %s AND activa = true 
GROUP BY estado;
```

### 5.2 Serie Mensual (generate_series para meses sin datos)
```sql
WITH meses AS (
  SELECT generate_series(
    date_trunc('month', %s)::date,
    date_trunc('month', %s)::date,
    '1 month'
  ) AS mes
),
datos AS (
  SELECT date_trunc('month', fecha_recepcion)::date AS mes, count(*) AS total
  FROM expedientes_expedientetitulacion
  WHERE fecha_recepcion BETWEEN %s AND %s
    AND carrera_id = %s
  GROUP BY 1
)
SELECT m.mes, COALESCE(d.total, 0) AS total
FROM meses m LEFT JOIN datos d ON m.mes = d.mes
ORDER BY m.mes;
```

### 5.3 Tiempo Promedio (solo cerrados con fecha_declaratoria)
```sql
SELECT avg(d.fecha_declaratoria - e.fecha_recepcion) AS dias_promedio
FROM expedientes_expedientetitulacion e
JOIN resoluciones_declaratoriaaptitud d ON d.expediente_id = e.id
WHERE e.carrera_id = %s
  AND e.fecha_recepcion BETWEEN %s AND %s
  AND e.estado = 'DECLARADA_APTA';
```

### 5.4 Listos para Informe (checklist 100% VERIFICADO)
```sql
SELECT e.id, e.numero_expediente
FROM expedientes_expedientetitulacion e
WHERE e.facultad_id = %s
  AND e.estado = 'EN_VERIFICACION'
  AND NOT EXISTS (
    SELECT 1 FROM verificacion_checklistverification c
    WHERE c.expediente_id = e.id
      AND c.estado_verificacion != 'VERIFICADO'
  );
```

### 5.5 KPIs Modalidades (agrupados)
```sql
-- Totales
SELECT opcion_titulacion, count(*) 
FROM expedientes_expedientetitulacion 
WHERE activa = true 
GROUP BY opcion_titulacion;

-- Por carrera
SELECT carrera_id, opcion_titulacion, count(*) 
FROM expedientes_expedientetitulacion 
WHERE activa = true 
GROUP BY carrera_id, opcion_titulacion;

-- Cambios historial
SELECT modalidad_nueva, count(*) 
FROM expedientes_historialmodalidad 
WHERE modalidad_nueva = 'EC'
GROUP BY modalidad_nueva;
```

---

## 6. PERMISOS RBAC PARA ENDPOINTS INDICADORES

| Recurso | Acción | Roles | Scope | Notas |
|---------|--------|-------|-------|-------|
| `dashboard` | GET | Todos | own/carrera/facultad/all | Endpoint unificado `/dashboard/me/` |
| `indicadores:modalidades` | GET | Secretario, Decano, Director, Admin | carrera/facultad/all | Requiere BE-06 (campo modalidad) |
| `indicadores:culminacion` | GET | Decano, Director, Admin | facultad/carrera/all | — |
| `indicadores:evolucion` | GET | Admin, Director, Decano | all/facultad/carrera | — |
| `indicadores:elegibilidad-ec` | GET | Secretario, Decano, Admin | facultad/all | Requiere mock SGA |

**Implementación:** Nueva entrada en `RBAC_MATRIX` (`authentication/permissions.py`) + `ROW_TO_SCOPE` para `indicadores` recurso.

---

## 7. SERIALIZERS PROPUESTOS

### 7.1 DashboardMeSerializer
```python
class DashboardMeSerializer(serializers.Serializer):
    generado_en = serializers.DateTimeField()
    ambito = AmbitoSerializer()
    rol_principal = serializers.CharField()
    secciones = serializers.DictField(child=serializers.JSONField())
```

### 7.2 IndicadoresModalidadesSerializer
```python
class IndicadoresModalidadesSerializer(serializers.Serializer):
    total_tic = serializers.IntegerField()
    total_ec = serializers.IntegerField()
    porcentaje_tic = serializers.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_ec = serializers.DecimalField(max_digits=5, decimal_places=2)
    por_carrera = CarreraModalidadSerializer(many=True)      # opcional ?agrupar=carrera
    por_periodo = PeriodoModalidadSerializer(many=True)      # opcional ?agrupar=periodo
    por_estado = EstadoModalidadSerializer(many=True)        # opcional ?agrupar=estado
    elegibles_ec = serializers.IntegerField()                # solo roles autorizados
    habilitados_ec = serializers.IntegerField()
    cambios_autorizados = serializers.IntegerField()         # solo admin/decano
```

---

## 8. ESTRATEGIA DE PRUEBAS

### 8.1 Unitarias Fórmulas (por KPI)
- Caso 0 elementos → 0
- Caso 1 elemento → valor correcto
- Caso N elementos → agregación correcta
- Períodos vacíos → serie con ceros (generate_series)
- Cohortes mixtas (abiertos/cerrados) → solo cerrados en tiempo promedio

### 8.2 De Permisos (por endpoint)
- Cada rol consulta su dashboard → recibe solo su ámbito
- DIRECTOR no ve otra carrera (ámbito vacío o 403)
- ESTUDIANTE no accede a indicadores agregados (403 por matriz)
- ADMIN ve todo (SCOPE_ALL)

### 8.3 De Consistencia
- Doble cálculo: servicio vs ORM independiente en test
- Comparación contra conteos directos en BD de prueba

### 8.4 De Contrato
- `drf-spectacular` documenta esquemas automáticamente
- Tests de esquema: `assert_schema_equals_snapshot()`

### 8.5 Cobertura Objetivo
- App `indicadores` ≥ 90% (coherente con 93% actual backend)

---

## 9. DEPENDENCIAS Y ORDEN

```
INC-03 (Modalidades Core) 
    → INC-04-T01 (App indicadores + servicios base)
        → INC-04-T02 (Endpoint /dashboard/me/)
            → INC-04-T03 (Endpoints analíticos)
                → INC-04-T06 (KPIs modalidades - requiere MOD-01 a MOD-05 implementados)
                    → INC-08 (Frontend dashboards + modalidad)
```

**Bloqueantes:** 
- KPIs modalidades (MOD-10) requieren INC-03 completado (campo `opcion_titulacion` + `HistorialModalidad`)
- Endpoints analíticos requieren app `indicadores` creada
- Dashboard Admin requiere nombres carrera (BE-10) para KPI-ADM-07

---

## 10. ESTADO ACTUAL

| Componente | Estado | Evidencia |
|------------|--------|-----------|
| Diseño KPIs (40 indicadores) | ✅ Completado | `INFORME_DISENO_KPI.md` |
| App `indicadores` | ❌ No existe | Pendiente INC-04-T01 |
| Servicios fórmulas | ❌ No existen | Pendiente INC-04-T01 |
| Endpoint `/dashboard/me/` | ❌ No existe | Pendiente INC-04-T02 |
| Endpoints analíticos | ❌ No existen | Pendiente INC-04-T03 |
| KPIs modalidades | ❌ No existen | Pendiente INC-03 + INC-04-T06 |
| Permisos RBAC indicadores | ❌ No definidos | Pendiente INC-04-T04 |
| Tests unitarias fórmulas | ❌ No existen | Pendiente INC-04-T05 |
| Frontend consumo dashboard | ⚠️ Parcial (V-02 only) | `StudentDashboardPage.tsx` usa `useBandejaEstudiante` + `useNotificaciones` |

---

## 11. PRÓXIMOS PASOS INMEDIATOS

1. **Crear app `indicadores`** en `backend/src/apps/indicadores/`
2. **Migrar fórmulas** de `INFORME_DISENO_KPI.md` §6 a `services/indicadores.py`
3. **Implementar `DashboardMeViewSet`** con composición por rol
4. **Registrar en `RBAC_MATRIX`** recurso `dashboard` + `indicadores:*`
5. **Tests unitarias** fórmulas (casos 0, 1, N, vacíos)
6. **Integrar en frontend** `StudentDashboardPage` → consumir `/dashboard/me/` en lugar de queries separadas