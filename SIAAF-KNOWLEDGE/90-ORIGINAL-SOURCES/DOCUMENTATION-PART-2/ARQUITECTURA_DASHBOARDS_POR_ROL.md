# ARQUITECTURA DE DASHBOARDS POR ROL — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `INFORME_DISENO_KPI.md` + `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md`  

---

## 1. PRINCIPIOS DE DISEÑO

### 1.1 Endpoint Unificado
```
GET /api/v1/dashboard/me/
```
- **Único punto de entrada** para todos los roles
- El servidor compone el dashboard según `roles` del JWT (evita 7 endpoints duplicados)
- Reutiliza `ScopeFilterMixin` + matriz RBAC para ámbito de datos
- Parámetros opcionales: `seccion=resumen|grafico|tabla|actividad|notificaciones|modalidad`

### 1.2 Estructura de Respuesta Estándar
```json
{
  "generado_en": "2026-11-09T14:30:00Z",
  "ambito": { "tipo": "carrera|facultad|global|own", "id": "uuid|null" },
  "rol_principal": "SECRETARIO_ABOGADO",
  "secciones": {
    "resumen": { "kpi_clave": 12, "alertas": 3, "acciones_pendientes": 5 },
    "tarjetas_p0": [...],
    "grafico_principal": { "tipo": "bar|line|pie|progress", "datos": {...}, "titulo": "..." },
    "tabla_trabajo": { "columnas": [...], "filas": [...], "paginacion": {...}, "acciones": [...] },
    "actividad_reciente": [...],
    "notificaciones_no_leidas": 7,
    "modalidad_titulacion": { "actual": "TIC", "elegible_ec": false, "historial": [...] }
  }
}
```

### 1.3 Principios UX
- **≤ 5 segundos** para comprender: situación actual, qué requiere atención, acción a realizar
- **Tarjetas P0 siempre visibles** (máx 6), gráficos máx 1 por fila
- **Estados obligatorios**: loading (skeleton), empty (con CTA), error (reintento), forbidden, read-only
- **Accesibilidad AA + axe** en cada componente
- **Responsive 320px** verificado (tabla → tarjetas en móvil)
- **Sin cálculos negocio en cliente**: solo presentacionales (ej. `dias_restantes = fecha - hoy`)

---

## 2. DASHBOARDS POR ROL

### 2.1 ESTUDIANTE (`/estudiante`)

| Componente | Contenido | KPIs | Fuente | Acción |
|------------|-----------|------|--------|--------|
| **Header** | Saludo + cédula (del JWT) | — | `User` | — |
| **Tarjeta Estado** | Badge estado expediente activo + fecha límite (semáforo) | KPI-EST-01, 06 | `ExpedienteTitulacion` | Ver expediente (V-04) |
| **Tarjeta Requisitos** | Contador pendientes (PENDIENTE/SOLICITADO) | KPI-EST-02 | `PeticionDocumental` | Ver peticiones (V-05) |
| **Tarjeta Observados** | Contador + motivos observaciones no resueltas | KPI-EST-03 | `PeticionDocumental` + `ObservacionAccionable` | Subsanar (V-04) |
| **Tarjeta Notificaciones** | Badge no leídas + lista 5 recientes | KPI-EST-05 | `NotificacionInterna` | Marcar leída / Ver todas |
| **Tarjeta Progreso** | Barra % checklist verificado (5 req. base) | KPI-EST-07 | `ChecklistVerification` | Ver checklist (V-04) |
| **Tabla Expedientes** | Mis expedientes BORRADOR/OBSERVADA (paginada) | — | `ExpedienteTitulacion` (bandeja) | Ver detalle |
| **Accesos Rápidos** | Historial local navegación (sessionStorage) | — | `localStorage` | Volver a expediente visitado |
| **Modalidad** | **Solo lectura**: Actual (TIC/EC) + "¿Eres elegible para Examen Complexivo?" (link a elegibilidad) | KPI-MOD-01/02 | `ExpedienteTitulacion.opcion_titulacion` + `GET /elegibilidad/` | — |

**Permisos:** `SCOPE_OWN` — solo sus expedientes, notificaciones, peticiones.

---

### 2.2 SECRETARIA_CARRERA (`/bandeja`)

| Componente | Contenido | KPIs | Fuente | Acción |
|------------|-----------|------|--------|--------|
| **Tarjeta En Atención** | Expedientes carrera en {ENVIADA, EN_VERIFICACION, OBSERVADA} con plazo vigente/vencido | KPI-SEC-01 | `ExpedienteTitulacion` | Ver detalle (V-08) |
| **Tarjeta Plazo Vencido** | Alerta roja: count `fecha_limite_atencion < hoy` estado no terminal | KPI-SEC-02 | `ExpedienteTitulacion` | Priorizar atención |
| **Tarjeta Certificados** | Peticiones `dependencia_emisora=SECRETARIA_CARRERA` en PENDIENTE/SOLICITADO | KPI-SEC-03 | `PeticionDocumental` | Cargar documento (V-08) |
| **Tarjeta Validación** | Checklist `PENDIENTE` con petición `CARGADO` en su carrera | KPI-SEC-04 | `ChecklistVerification` | Ver expediente |
| **Tarjeta Observados** | Expedientes carrera en OBSERVADA | KPI-SEC-06 | `ExpedienteTitulacion` | Ver detalle |
| **Gráfico** | Serie temporal solicitudes recibidas (últimos 6 meses) | KPI-SEC-05 | `ExpedienteTitulacion` | Filtrar período |
| **Tabla Trabajo** | Bandeja paginada: N° expediente, estudiante, estado, fecha límite, acciones | — | `ExpedienteTitulacion` (bandeja) | Ver detalle, Emitir certificado |
| **Modalidad** | **Solo lectura**: Distribución TIC/EC en su carrera (gráfico pie) | KPI-MOD-04 | `ExpedienteTitulacion` | — |

**Permisos:** `SCOPE_CARRERA` — expedientes/peticiones de su `carrera_id`. Sin bandeja de expedientes (lista vacía por diseño actual).

---

### 2.3 SECRETARIO_ABOGADO / ANALISTA_APOYO (`/bandeja`)

| Componente | Contenido | KPIs | Fuente | Acción |
|------------|-----------|------|--------|--------|
| **Tarjeta En Verificación** | Expedientes facultad en `EN_VERIFICACION` | KPI-JUR-01 | `ExpedienteTitulacion` | Ver checklist (V-08) |
| **Tarjeta Por Evaluar** | Requisitos checklist `PENDIENTE` en su facultad | KPI-JUR-02 | `ChecklistVerification` | Evaluar (V-08) |
| **Tarjeta Observaciones** | Observaciones `resuelta=False` en su facultad | KPI-JUR-03 | `ObservacionAccionable` | Ver expediente |
| **Tarjeta Listos Informe** | Expedientes `EN_VERIFICACION` con checklist 100% `VERIFICADO` | KPI-JUR-04 | `ExpedienteTitulacion` + `ChecklistVerification` | Emitir informe (V-08) |
| **Tarjeta Plazo Vencido** | Igual KPI-SEC-02 ámbito facultad | KPI-JUR-07 | `ExpedienteTitulacion` | Priorizar |
| **Gráfico** | Distribución estados expedientes facultad (barras) | KPI-JUR-05/06 | `ExpedienteTitulacion` | — |
| **Tabla Trabajo** | Bandeja: expedientes ENVIADA/EN_VERIFICACION/OBSERVADA (paginada) | — | `ExpedienteTitulacion` (bandeja) | Ver detalle, Evaluar, Observar, Informe |
| **Acciones Rápidas** | "Evaluar checklist", "Observar expediente", "Emitir informe" (según estado) | — | API mutaciones | Mutaciones directas |
| **Modalidad** | **Verifica elegibilidad EC**: Botón "Verificar elegibilidad Examen Complexivo" → llama `GET /elegibilidad/` | KPI-MOD-06 | `ExpedienteTitulacion` + Mock SGA | Si elegible → "Autorizar cambio a EC" (Secretario) |

**Permisos:** `SCOPE_FACULTAD` — expedientes de su `facultad_id`.  
**Diferencia Analista:** Solo evaluar checklist en **borrador** (`SCOPE_BORRADOR`); no observar ni emitir informe final.

---

### 2.4 DECANO (`/bandeja`)

| Componente | Contenido | KPIs | Fuente | Acción |
|------------|-----------|------|--------|--------|
| **Tarjeta Pendientes Declaratoria** | Expedientes facultad en `INFORME_EMITIDO` (su cola de firma) | KPI-DEC-01 | `ExpedienteTitulacion` | Declarar aptitud (V-08) |
| **Tarjeta Declaratorias Período** | Count `DeclaratoriaAptitud` firmadas en período | KPI-DEC-02 | `DeclaratoriaAptitud` | Ver histórico |
| **Tarjeta Procesos Activos** | Expedientes facultad no terminales | KPI-DEC-03 | `ExpedienteTitulacion` | Supervisar |
| **Tarjeta Tasa Culminación** | % facultad (cohorte `fecha_recepcion` en rango) | KPI-DEC-04 | `ExpedienteTitulacion` | Filtrar cohorte |
| **Gráfico** | Distribución por estado (pie) + evolución mensual (línea) | KPI-DEC-05 | `ExpedienteTitulacion` | — |
| **Tabla Trabajo** | Expedientes `INFORME_EMITIDO` (paginada) | — | `ExpedienteTitulacion` (bandeja) | Ver informe, Declarar aptitud |
| **Acciones Rápidas** | "Ver informe", "Declarar aptitud" (carga memorando firmado) | — | API | Mutación declaratoria |
| **Modalidad** | **Autoriza cambio a EC**: Botón "Cambiar modalidad a Examen Complexivo" → modal justificación + evidencia → `POST /cambiar/` | KPI-MOD-07/08 | `HistorialModalidad` | Decisión final |

**Permisos:** `SCOPE_FACULTAD` — expedientes de su `facultad_id`. Bandeja solo `INFORME_EMITIDO`.

---

### 2.5 DIRECTOR_CARRERA (`/bandeja`)

| Componente | Contenido | KPIs | Fuente | Acción |
|------------|-----------|------|--------|--------|
| **Tarjeta Activos Carrera** | Expedientes carrera no terminales (excluye BORRADOR) | KPI-DIR-01 | `ExpedienteTitulacion` | Supervisar |
| **Tarjeta Culminados Período** | Declaratorias período en su carrera | KPI-DIR-02 | `DeclaratoriaAptitud` | Ver histórico |
| **Tarjeta Plazo Vencido** | Igual KPI-SEC-02 ámbito carrera | KPI-DIR-03 | `ExpedienteTitulacion` | Alertar |
| **Tarjeta Tasa Culminación** | % carrera (cohorte `fecha_recepcion`) | KPI-DIR-04 | `ExpedienteTitulacion` | Filtrar cohorte |
| **Tarjeta Tiempo Promedio** | Días promedio `fecha_declaratoria - fecha_recepcion` (cerrados) | KPI-DIR-05 | `ExpedienteTitulacion` + `DeclaratoriaAptitud` | — |
| **Gráfico 1** | Distribución por estado (barras) | KPI-DIR-06 | `ExpedienteTitulacion` | — |
| **Gráfico 2** | Distribución por período académico (línea) | KPI-DIR-07 | `ExpedienteTitulacion` | Requiere BE-10 (nombres carrera) |
| **Tabla Trabajo** | Expedientes carrera (paginada, todos estados en curso) | — | `ExpedienteTitulacion` (bandeja) | Ver detalle |
| **Modalidad** | **Solo lectura**: Distribución TIC/EC en su carrera | KPI-MOD-04 | `ExpedienteTitulacion` | — |

**Permisos:** `SCOPE_CARRERA` — expedientes de su `carrera_id`. Sin bandeja por diseño actual (lista vacía).

---

### 2.6 RESPONSABLE_DEPENDENCIA (`/bandeja`)

| Componente | Contenido | KPIs | Fuente | Acción |
|------------|-----------|------|--------|--------|
| **Tarjeta Solicitudes Mi Dependencia** | Peticiones `dependencia_emisora` ∈ roles usuario en `SOLICITADO` | KPI-DEP-01 | `PeticionDocumental` | Cargar documento |
| **Tarjeta Pendientes Sin Solicitud** | Igual en `PENDIENTE` | KPI-DEP-02 | `PeticionDocumental` | Solicitar emisión (estudiante) / Esperar |
| **Tarjeta Observadas Corregir** | Igual en `OBSERVADO` | KPI-DEP-03 | `PeticionDocumental` | Corregir documento |
| **Tabla Trabajo** | Peticiones asignadas (paginada) | — | `PeticionDocumental` | Cargar/Descargar/Corregir |
| **Modalidad** | **Solo lectura**: N/A (no aplica a peticiones) | — | — | — |

**Permisos:** `SCOPE_ASIGNADO` — peticiones donde `dependencia_emisora` coincide con roles del usuario.  
**Nota:** Hoy `RESPONSABLE_DEPENDENCIA` tiene `ROW_TO_SCOPE = DENEGADO` y sin celdas matriz (VULN-006). Requiere TASK-P1-004.

---

### 2.7 ADMINISTRADOR (`/bandeja`)

| Componente | Contenido | KPIs | Fuente | Acción |
|------------|-----------|------|--------|--------|
| **Tarjeta Usuarios** | Registrados / Con rol / Por rol | KPI-ADM-01 | `User` + `UserRole` | Gestionar usuarios/roles |
| **Tarjeta Expedientes** | Totales + por estado | KPI-ADM-02 | `ExpedienteTitulacion` | Ver distribución |
| **Tarjeta Culminados** | Total histórico `DeclaratoriaAptitud` | KPI-ADM-03 | `DeclaratoriaAptitud` | — |
| **Tarjeta Tasa Global** | % global (cohorte `fecha_recepcion`) | KPI-ADM-04 | `ExpedienteTitulacion` | Filtrar cohorte |
| **Tarjeta Tiempo Promedio** | Días promedio global | KPI-ADM-05 | `ExpedienteTitulacion` + `DeclaratoriaAptitud` | — |
| **Gráfico 1** | Evolución mensual solicitudes (12 meses, ceros incluidos) | KPI-ADM-06 | `ExpedienteTitulacion` | — |
| **Gráfico 2** | Distribución por carrera (UUID → nombre requiere BE-10) | KPI-ADM-07 | `ExpedienteTitulacion` | — |
| **Gráfico 3** | Auditoría por acción (barras) | KPI-ADM-08 | `EventoAuditoria` | Filtrar período |
| **Tabla Usuarios** | Lista paginada: cédula, roles, último login, estado | — | `User` + `UserRole` | Editar roles, Ver auditoría |
| **Modalidad** | **Dashboard global**: KPI-MOD-01 a 08 (totales, %, carrera, período, estado, elegibles, habilitados, cambios) | KPI-MOD-01 a 08 | `ExpedienteTitulacion` + `HistorialModalidad` | Ver detalle cambios |

**Permisos:** `SCOPE_ALL` — sin filtro ORM. Acceso completo a todos los recursos.

---

## 3. COMPONENTES REUTILIZABLES FRONTEND

### 3.1 Tarjeta KPI (`KPICard`)
```tsx
interface KPICardProps {
  titulo: string;
  valor: number | string;
  variante?: 'neutro' | 'info' | 'success' | 'warning' | 'danger';
  tendencia?: { valor: number; direccion: 'up' | 'down' | 'stable' };
  accion?: { label: string; onClick: () => void; };
  loading?: boolean;
}
```

### 3.2 Gráfico Estadístico (`ChartWidget`)
```tsx
interface ChartWidgetProps {
  tipo: 'bar' | 'line' | 'pie' | 'progress';
  datos: ChartData;
  titulo: string;
  altura?: number;
  responsive?: boolean;
  loading?: boolean;
}
```
- **Librería:** `recharts` (ya en deps) o `chart.js` + `react-chartjs-2`
- **Accesibilidad:** `aria-label` descriptivo, tabla de datos alternativa (screen readers)

### 3.3 Tabla de Trabajo (`WorkTable`)
```tsx
interface WorkTableProps<T> {
  columnas: ColumnDef<T>[];
  filas: T[];
  paginacion: { page: number; pageSize: number; total: number; onPageChange: (p: number) => void; };
  filaKey: (fila: T) => string;
  accionPorFila?: (fila: T) => ReactNode; // Botones contextuales
  loading?: boolean;
  emptyState?: { titulo: string; descripcion: string; cta?: ReactNode; };
}
```
- **Responsive:** `< 768px` → tarjetas con mismos datos
- **Accesibilidad:** `<caption>`, `<th scope="col">`, contenedor scroll `tabIndex=0`

### 3.4 Panel Modalidad (`ModalidadPanel`)
```tsx
interface ModalidadPanelProps {
  modalidadActual: 'TIC' | 'EC';
  elegibleEC: boolean;
  historial: HistorialModalidad[];
  rol: 'estudiante' | 'secretario' | 'decano' | 'admin' | 'readonly';
  onVerificarElegibilidad?: () => void;
  onCambiarModalidad?: (justificacion: string, evidencia: any) => void;
}
```
- **Estudiante:** Solo lectura + link "Verificar elegibilidad"
- **Secretario:** Botón "Verificar elegibilidad" + si elegible "Autorizar cambio"
- **Decano:** Botón "Cambiar modalidad" (decisión final)
- **Admin:** Vista completa con historial y KPIs

---

## 4. FLUJO DE DATOS

```mermaid
graph TD
    A[Usuario autenticado] --> B[JWT con roles + carrera_id/facultad_id]
    B --> C[GET /api/v1/dashboard/me/]
    C --> D[AuthContext → roles]
    D --> E[ScopeFilterMixin → ámbito consulta]
    E --> F[Servicios Indicadores → fórmulas KPI]
    F --> G[Agregaciones PostgreSQL]
    G --> H[Respuesta JSON unificada]
    H --> I[TanStack Query (staleTime: 30s)]
    I --> J[Componentes Dashboard por rol]
    J --> K[Tarjetas P0 + Gráfico + Tabla + Acciones]
```

---

## 5. PERMISOS Y SEGURIDAD

| Recurso RBAC | Acción | Roles | Scope |
|--------------|--------|-------|-------|
| `dashboard` | GET | Todos (según rol) | own/carrera/facultad/all |
| `indicadores:modalidades` | GET | Secretario, Decano, Director, Admin | carrera/facultad/all |
| `indicadores:culminacion` | GET | Decano, Director, Admin | facultad/carrera/all |
| `indicadores:evolucion` | GET | Admin, Director, Decano | all/facultad/carrera |
| `indicadores:elegibilidad-ec` | GET | Secretario, Decano, Admin | facultad/all |

**Regla:** El ámbito **nunca** viene de parámetros cliente; se deriva del `User` autenticado (JWT → `carrera_id`/`facultad_id`).

---

## 6. ESTADO ACTUAL IMPLEMENTACIÓN FRONTEND

| Vista | Componente Principal | Estado | Faltante |
|-------|---------------------|--------|----------|
| V-02 Estudiante | `StudentDashboardPage.tsx` | ✅ Hecha | Modalidad (solo lectura) |
| V-07 Bandeja | `BandejaPage.tsx` | ❌ Stub | Implementación completa por rol |
| V-08 Detalle | `DetalleFuncionarioPage.tsx` | ❌ Stub | Implementación completa por rol |
| Dashboard Admin | — | ❌ No existe | Nueva vista |
| Dashboard Dependencia | — | ❌ No existe | Nueva vista (requiere VULN-006) |

**Componentes base listos:** `KPICard`, `ChartWidget`, `WorkTable`, `ModalidadPanel` — por crear en F3.

---

## 7. PRÓXIMOS PASOS

1. **INC-04:** Backend app `indicadores` + endpoint `/dashboard/me/`
2. **INC-07:** Frontend dashboards por rol (V-07, V-08, Admin, Dependencia)
3. **INC-08:** Integración modalidad en dashboards (tarjetas KPI-MOD, panel V-04/V-08)
4. **Validar** con stakeholders: ¿métricas correctas? ¿acciones rápidas completas? ¿filtros necesarios?