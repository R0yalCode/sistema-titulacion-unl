# PLAN MAESTRO DE IMPLEMENTACIÓN INTEGRAL — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Estado:** Análisis y planificación (no implementación)  
**Alcance:** Backend + Seguridad + KPI + Modalidades de Titulación + Frontend  

---

## 1. RESUMEN EJECUTIVO

Este documento consolida el estado actual del proyecto SGT-SIAAF tras una revisión exhaustiva de:

- **Backend:** Django 5.2 + DRF, arquitectura monolito modular, 6 apps operativas
- **Seguridad:** Auditoría completa con 87 controles (73.6% implementados y verificados)
- **KPIs:** Diseño de 40 indicadores por rol (33 implementables con datos actuales)
- **Modalidades de Titulación:** 2 modalidades requeridas (Trabajo de Integración Curricular + Examen Complexivo) — **PENDIENTES DE IMPLEMENTACIÓN**
- **Frontend:** React + TypeScript + Vite, F0 completado (80%), F1-F2.5 en progreso (autenticación, componentes base, estados de error)

**Hallazgo crítico:** Las dos modalidades de titulación **no existen** en el modelo de datos, reglas de negocio, endpoints, ni dashboards. Su implementación es transversal y prioritaria (BE-06, FE-T301/302 bloqueados).

---

## 2. ESTADO ACTUAL POR ÁREA

### 2.1 Backend (apps operativas)
| App | Estado | Funcionalidades Clave |
|-----|--------|----------------------|
| `authentication` | ✅ Completa | JWT stateless (HS256), 8 roles, RBAC matriz 6.2, throttling IP validada |
| `expedientes` | ✅ Completa | State machine 7 estados, plazos 8 días hábiles, pausa/reanudación, inmutabilidad campos críticos |
| `peticiones` | ✅ Completa | Validación PDF estricta (magic bytes, SHA-256, 10MB), almacenamiento privado, versionado N+1 |
| `verificacion` | ✅ Completa | Checklist digital, observaciones, subsanación, bloqueo pesimista, concurrencia |
| `resoluciones` | ⚠️ Parcial | Informe legal (Providencia #590), Declaratoria (Memorando #162) — **Falta FirmaEC real** |
| `notificaciones` | ✅ Completa | Notificaciones internas, auditoría inmutable (EventoAuditoria JSONB), signals automáticos |

### 2.2 Seguridad (Auditoría 2026-11-09)
**Puntuación global: ~85% OWASP ASVS Nivel 2**

| Categoría | Controles IV | Controles IP | Controles PI | Críticos |
|-----------|--------------|--------------|--------------|----------|
| Autenticación JWT | 5 | 2 | 1 | 0 |
| Autorización RBAC | 9 | 2 | 1 | 0 |
| API REST | 6 | 2 | 2 | 1 (VULN-001) |
| Gestión Documental | 6 | 1 | 1 | 0 |
| Integridad Procesos | 8 | 1 | 1 | 0 |
| Criptografía/FirmaEC | 4 | 0 | 3 | 1 (VULN-010) |

**Vulnerabilidades P0 (Críticas pre-producción):**
- **VULN-001:** Falta throttling global en endpoints mutantes (enviar, observar, checklist, informes, declaratorias)
- **VULN-002:** SCOPE_ASIGNADO no implementado en ScopeFilterMixin (IDOR potencial en peticiones asignadas)
- **VULN-010:** FirmaEC no verificada en declaratoria (solo validación PDF genérica)

### 2.3 KPIs (Diseño INFORME_DISENO_KPI.md)
- **40 KPIs definidos** por 7 roles (ESTUDIANTE, SECRETARIA_CARRERA, SECRETARIO_ABOGADO, ANALISTA_APOYO, DECANO, DIRECTOR_CARRERA, ADMINISTRADOR)
- **33 implementables** con modelo actual
- **7 NO implementables** (requieren: catálogo carreras BE-10, modalidad titulación BE-06, modelo tutoría, período académico, definición "abandonado", sesiones JWT)
- **Arquitectura propuesta:** App `indicadores` + endpoint único `GET /api/v1/dashboard/me/`

### 2.4 Modalidades de Titulación (REQUISITO PRIORITARIO TRANSVERSAL)
**ESTADO ACTUAL: NO IMPLEMENTADAS EN NINGUNA CAPA**

| Aspecto | Estado | Detalle |
|---------|--------|---------|
| Modelo de datos | ❌ Ausente | No hay campo `opcion_titulacion` en `ExpedienteTitulacion` |
| Reglas de negocio | ❌ Ausentes | No hay validación elegibilidad, cambio modalidad, autorización |
| Endpoints | ❌ Ausentes | No hay CRUD ni consultas de modalidad |
| KPIs modalidad | ❌ Ausentes | No hay estadísticas por modalidad |
| Frontend V-03 | ❌ Bloqueado | Selector condicionado a BE-06 (DEC-14, INC-15) |
| Normativa | 🔄 Pendiente validación | Arts. 39, 40, 212, 216, 233 RRA-UNL (fuente primaria no contrastada) |

**Dos modalidades requeridas:**
1. **Trabajo de Integración Curricular** (ordinaria, predeterminada) — Art. 39, 212, 216 RRA-UNL
2. **Examen Complexivo** (excepcional, condicionada) — Art. 40, 212 inc. b, 233 RRA-UNL

### 2.5 Frontend (Estado tareas tasks.md)
| Fase | Progreso | Tareas Clave Completadas |
|------|----------|-------------------------|
| F0 Andamiaje | ✅ 100% | Vite+React+TS, ESLint, Vitest+MSW, Estructura, Env validation, Tokens, Providers, Layout, Router, README |
| F1 Auth/Sesión | ✅ 100% | JWT utils, AuthContext, HTTP client, Login endpoint, Route guards, Redirect/Logout, Auth tests (81/81) |
| F2 Componentes | ✅ 100% | Form fields, Badge/Card/Alert/Spinner, Empty/Error/NotFound/Forbidden, Table, Pagination, Modal, Timeline, FileUpload, Toasts, UI Kit tests (170/170) |
| F2.5 Errores | ✅ 80% | Higiene plantilla, 404 page, Errores globales 401/403/500/503, **InlineAlerts 409/412/428 BLOQUEADOS (BE-11)**, Mascotas prototipo B |
| F3 Vistas | 🔄 Parcial | V-01 Login ✅, V-02 Dashboard Estudiante ✅, V-03 Nueva Solicitud ✅ (solo carrera_id), V-04 Expediente ✅, V-05/06 Peticiones ⚠️ stubs, V-07/08 Bandeja ⚠️ stubs, V-09 No habilitado ✅ |

---

## 3. BRECHAS CRÍTICAS IDENTIFICADAS

### 3.1 Modalidades de Titulación (BLOQUEANTE TRANSVERSAL)
| ID | Brecha | Impacto | Prioridad |
|----|--------|---------|-----------|
| GAP-MOD-01 | Modelo `ExpedienteTitulacion` sin campo `opcion_titulacion` | Imposible registrar modalidad | P0 |
| GAP-MOD-02 | Sin catálogo/enum de modalidades válidas | No hay dominio controlado | P0 |
| GAP-MOD-03 | Sin reglas elegibilidad (100% asignaturas vs 85% horas vs 2 reprobaciones + 3ra matrícula) | Frontend no puede mostrar opciones válidas | P0 |
| GAP-MOD-04 | Sin endpoint autorización modalidad excepcional | Decano/Secretario no pueden habilitar Examen Complexivo | P0 |
| GAP-MOD-05 | Sin historial cambios modalidad | Pérdida trazabilidad | P0 |
| GAP-MOD-06 | Sin KPIs por modalidad | Dashboards incompletos | P1 |
| GAP-MOD-07 | Frontend V-03 sin selector modalidad | UX incompleta estudiante | P1 |

### 3.2 Seguridad (P0 del Plan Remediación)
| ID | Brecha | Archivos Afectados | Esfuerzo |
|----|--------|-------------------|----------|
| VULN-001 | Throttling global mutantes | `core/adapters/throttling.py` (nuevo), `expedientes/views.py`, `verificacion/views.py`, `resoluciones/views.py` | M |
| VULN-002 | SCOPE_ASIGNADO en ScopeFilterMixin | `core/adapters/scope_filter.py`, `peticiones/views.py` | M |
| VULN-010 | FirmaEC real en declaratoria | `resoluciones/services/declarar_aptitud.py`, nuevos campos modelo | L |

### 3.3 KPIs y Dashboards
| ID | Brecha | Dependencia |
|----|--------|-------------|
| GAP-KPI-01 | App `indicadores` no existe | Ninguna (datos actuales) |
| GAP-KPI-02 | Endpoint `GET /dashboard/me/` no existe | GAP-KPI-01 |
| GAP-KPI-03 | 7 KPIs no implementables (modalidad, tutoría, períodos) | BE-06, BE-10, modelos futuros |
| GAP-KPI-04 | Frontend dashboards por rol (solo V-02 hecho) | GAP-KPI-02 |

### 3.4 Sesiones y Usuarios Activos
| ID | Brecha | Estado |
|----|--------|--------|
| GAP-SES-01 | JWT stateless sin registro sesiones (refresh 24h fijo, sin rotación) | VULN-005 (P1) |
| GAP-SES-02 | No hay métrica "usuarios activos últimos 15 min" | Requiere tabla sesiones o auditoría por usuario |
| GAP-SES-03 | No hay revocación tokens en logout | VULN-005 (P1) |

### 3.5 Integración Frontend-Backend
| ID | Brecha | Vista Afectada |
|----|--------|----------------|
| GAP-FE-01 | V-05/06 Peticiones son stubs (sin lógica real) | Peticiones documentales |
| GAP-FE-02 | V-07/08 Bandeja/Detalle funcionario son stubs | Funcionarios |
| GAP-FE-03 | Sin búsqueda universal | Transversal |
| GAP-FE-04 | Sin exportaciones PDF/Excel/CSV | Dashboards, bandejas |
| GAP-FE-05 | Sin notificaciones push/tiempo real (solo polling) | Transversal |

---

## 4. REGLAS DE NEGOCIO MODALIDADES DE TITULACIÓN (DISEÑO REQUERIDO)

### 4.1 Definición de Modalidades
```python
# Enum propuesto para modelo
class ModalidadTitulacion(models.TextChoices):
    TRABAJO_INTEGRACION_CURRICULAR = 'TIC', 'Trabajo de Integración Curricular'
    EXAMEN_COMPLEXIVO = 'EC', 'Examen Complexivo'
```

### 4.2 Reglas Obligatorias
| Regla | Descripción | Validación |
|-------|-------------|------------|
| RN-MOD-01 | TIC es modalidad **predeterminada** al crear expediente | Default en modelo |
| RN-MOD-02 | EC es **excepcional** — no seleccionable por estudiante | UI oculta/bloqueada |
| RN-MOD-03 | EC requiere: 2 reprobaciones unidad titulación + 3ra matrícula efectiva | Verificación contra datos académicos (SGA mock) |
| RN-MOD-04 | Cambio modalidad requiere autorización Secretario/Decano | Endpoint dedicado + registro auditoría |
| RN-MOD-05 | Historial inmutable de cambios modalidad | Nuevo modelo `HistorialModalidad` |
| RN-MOD-06 | Expediente con actividades iniciadas: reglas de transición específicas | Validar estado expediente antes de permitir cambio |
| RN-MOD-07 | Actor autorizador: **Secretario/a-Abogado/a** (verifica elegibilidad) + **Decano/a** (autoriza) | Basado en Arts. 212, 233 RRA-UNL |

### 4.3 Modelo de Datos Propuesto
```python
# Adición a ExpedienteTitulacion
opcion_titulacion = models.CharField(
    max_length=3,
    choices=ModalidadTitulacion.choices,
    default=ModalidadTitulacion.TRABAJO_INTEGRACION_CURRICULAR,
    db_index=True,
)

# Nuevo modelo
class HistorialModalidad(models.Model):
    id = UUIDField(primary_key=True, default=uuid.uuid4)
    expediente = FK(ExpedienteTitulacion, CASCADE, related_name='historial_modalidad')
    modalidad_anterior = CharField(choices=ModalidadTitulacion.choices)
    modalidad_nueva = CharField(choices=ModalidadTitulacion.choices)
    fecha_cambio = DateTimeField(auto_now_add=True)
    autorizado_por = FK(User, PROTECT)
    justificacion = TextField()
    evidencia_academica = JSONField()  # Datos que respaldan la habilitación (reprobaciones, matrícula)
    estado_tercera_matricula = BooleanField(default=False)  # Verificado contra SGA
```

### 4.4 Endpoints Requeridos
| Endpoint | Método | Rol | Descripción |
|----------|--------|-----|-------------|
| `/api/v1/expedientes/{id}/modalidad/` | GET | Todos (scope) | Consultar modalidad actual + historial |
| `/api/v1/expedientes/{id}/modalidad/elegibilidad/` | GET | Estudiante, Secretario, Decano | Verificar si EC está habilitada |
| `/api/v1/expedientes/{id}/modalidad/cambiar/` | POST | Secretario, Decano | Cambiar modalidad (con justificación + evidencia) |
| `/api/v1/modalidades/` | GET | Admin | Catálogo modalidades válidas |

---

## 5. KPIs MODALIDADES DE TITULACIÓN (ADICIÓN AL INFORME KPI EXISTENTE)

| ID | Nombre | Fórmula | Fuente | Endpoint | Rol |
|----|--------|---------|--------|----------|-----|
| KPI-MOD-01 | Total TIC | `count(expediente where opcion_titulacion='TIC')` | ExpedienteTitulacion | `/indicadores/modalidades/` | Todos |
| KPI-MOD-02 | Total EC | `count(expediente where opcion_titulacion='EC')` | ExpedienteTitulacion | `/indicadores/modalidades/` | Todos |
| KPI-MOD-03 | % TIC / % EC | `(KPI-MOD-01 / total) * 100` | ExpedienteTitulacion | `/indicadores/modalidades/` | Todos |
| KPI-MOD-04 | Distribución por carrera | `group by carrera_id, opcion_titulacion` | ExpedienteTitulacion | `/indicadores/modalidades/?agrupar=carrera` | Director, Decano, Admin |
| KPI-MOD-05 | Distribución por período | `group by year(fecha_recepcion), opcion_titulacion` | ExpedienteTitulacion | `/indicadores/modalidades/?agrupar=periodo` | Director, Decano, Admin |
| KPI-MOD-06 | Elegibles EC | `count(estudiantes con 2 reprobaciones + 3ra matrícula)` | SGA Mock + Expediente | `/indicadores/elegibilidad-ec/` | Secretario, Decano |
| KPI-MOD-07 | Habilitados EC | `count(expediente opcion_titulacion='EC' and estado != 'BORRADOR')` | ExpedienteTitulacion | `/indicadores/modalidades/` | Secretario, Decano |
| KPI-MOD-08 | Cambios autorizados | `count(HistorialModalidad where modalidad_nueva='EC')` | HistorialModalidad | `/indicadores/cambios-modalidad/` | Admin, Decano |

**Regla de no duplicación:** Contar expediente por su `opcion_titulacion` **actual**; historial solo para KPI-MOD-08.

---

## 6. ARQUITECTURA DASHBOARDS POR ROL

### 6.1 Endpoint Unificado: `GET /api/v1/dashboard/me/`
```json
{
  "generado_en": "2026-11-09T14:30:00Z",
  "ambito": { "tipo": "carrera|facultad|global", "id": "uuid" },
  "rol_principal": "SECRETARIO_ABOGADO",
  "secciones": {
    "resumen": { "kpi_clave": 12, "alertas": 3, "acciones_pendientes": 5 },
    "tarjetas_p0": [...],
    "grafico_principal": { "tipo": "bar|line|pie", "datos": {...} },
    "tabla_trabajo": { "columnas": [...], "filas": [...], "paginacion": {...} },
    "actividad_reciente": [...],
    "notificaciones_no_leidas": 7
  },
  "modalidad_titulacion": {
    "actual": "TIC",
    "elegible_ec": false,
    "historial": [...]
  }
}
```

### 6.2 Componentes por Rol

| Rol | Tarjetas P0 | Gráficos | Tablas | Acciones Rápidas | Modalidad |
|-----|-------------|----------|--------|------------------|-----------|
| **ESTUDIANTE** | Estado expediente, Req. pendientes, Observados, Notificaciones, Fecha límite | Progreso checklist (barra) | Mis expedientes, Requisitos, Notificaciones | Crear solicitud, Ver expediente, Subsanar | Ver actual + elegibilidad EC |
| **SECRETARIA_CARRERA** | En atención, Plazo vencido, Certificados por emitir, Pendientes validación | Serie temporal solicitudes | Bandeja trámites | Emitir certificado, Ver expediente | Solo lectura (su carrera) |
| **SECRETARIO_ABOGADO** | En verificación, Req. por evaluar, Observaciones sin resolver, Listos para informe | Distribución estados | Checklist por expediente | Evaluar checklist, Observar, Emitir informe | **Verifica elegibilidad EC + autoriza cambio** |
| **ANALISTA_APOYO** | Igual Jurista (ámbito facultad, solo borrador) | Igual Jurista | Igual Jurista | Evaluar checklist (borrador), Emitir informe | Solo lectura |
| **DECANO** | Pendientes declaratoria, Declaratorias firmadas período | Tasa culminación facultad | Expedientes INFORME_EMITIDO | Declarar aptitud, Ver informe | **Autoriza cambio a EC** |
| **DIRECTOR_CARRERA** | Activos carrera, Culminados período, Plazo vencido | Distribución estados, Tiempo promedio | Procesos carrera | Supervisar | Solo lectura (su carrera) |
| **RESPONSABLE_DEPENDENCIA** | Solicitudes mi dependencia (SOLICITADO, PENDIENTE, OBSERVADO) | - | Peticiones asignadas | Cargar documento, Corregir observado | Solo lectura |
| **ADMINISTRADOR** | Usuarios, Expedientes totales, Culminados, Tasa global | Evolución mensual, Distribución carrera, Auditoría | Todo | Gestión usuarios, Catálogos | **Dashboard global modalidades** |

---

## 7. FUNCIONALIDADES FRONTEND PENDIENTES (F3+)

### 7.1 Vistas Completar
| Vista | Estado Actual | Trabajo Pendiente |
|-------|---------------|-------------------|
| V-05 Peticiones | Stub (190 bytes) | Lista, Solicitar emisión, Cargar PDF, Validación cliente |
| V-06 Seguimiento Petición | Stub (188 bytes) | Detalle petición, Descarga versiones, Historial |
| V-07 Bandeja | Stub (175 bytes) | Paginación server-side, Filtros, Columnas por rol, Estados vacíos |
| V-08 Detalle Funcionario | Stub (186 bytes) | Checklist, Observar, Informe, Declaratoria, Descargas |

### 7.2 Funcionalidades Transversales
| Funcionalidad | Descripción | Endpoints Requeridos |
|---------------|-------------|---------------------|
| **Búsqueda Universal** | Buscar expedientes, peticiones, documentos, usuarios | `GET /api/v1/buscar/?q=&tipo=` |
| **Exportaciones** | PDF (reportes), Excel (tablas), CSV (datos crudos) | `GET /api/v1/exportar/?formato=&filtros=` |
| **Notificaciones Push** | WebSocket/SSE para tiempo real | `/ws/notificaciones/` + backend |
| **Acciones Rápidas** | Botones contextuales por rol/estado | Existentes en API |
| **Filtros Dinámicos** | Estado, fecha, carrera, modalidad, responsable | Parámetros query en endpoints |
| **Modalidad en Formularios** | V-03: Selector condicionado a elegibilidad backend | `GET /expedientes/{id}/modalidad/elegibilidad/` |

### 7.3 Microinteracciones (Reutilizar librerías existentes)
- **Framer Motion** (ya en deps) para animaciones entrada, transiciones
- **React Hook Form** + **Zod** para validación formularios
- **TanStack Query** ya configurado (staleTime: 30s)
- **Skeleton loading** en tablas/tarjetas
- **Toasts** ya implementados (FE-T027)

---

## 8. CONTRATOS API (ENDPOINTS EXISTENTES + REQUERIDOS)

### 8.1 Endpoints Existentes (Verificados)
Ver `backend/docs/04-api/endpoints/*.md` y `backend/openapi.yaml`. Resumen:

| Módulo | Endpoints Clave |
|--------|-----------------|
| Auth | `POST /auth/token/` (login), `POST /auth/token/refresh/` (implícito) |
| Expedientes | `POST /expedientes/`, `GET /expedientes/bandeja/`, `GET /expedientes/{id}/`, `POST /expedientes/{id}/enviar/`, `POST /expedientes/{id}/observar/` |
| Peticiones | `POST /peticiones/{id}/solicitar-emision/`, `POST/GET /peticiones/{id}/documento/`, `GET /peticiones/{id}/documento/{version}/` |
| Verificación | `GET /expedientes/{id}/checklist/`, `PUT /checklist/{id}/`, `POST /checklist/{id}/subsanar/` |
| Resoluciones | `POST /informes/`, `POST /declaratorias/` |
| Notificaciones | `GET /notificaciones/`, `PATCH /notificaciones/{id}/marcar-leida/` |

### 8.2 Endpoints Requeridos (Nuevos)

#### Modalidades de Titulación
```
GET    /api/v1/expedientes/{id}/modalidad/           # Modalidad actual + historial
GET    /api/v1/expedientes/{id}/modalidad/elegibilidad/  # Verificar elegibilidad EC
POST   /api/v1/expedientes/{id}/modalidad/cambiar/   # Cambiar modalidad (Secretario/Decano)
GET    /api/v1/modalidades/                          # Catálogo modalidades
```

#### Indicadores/KPIs
```
GET    /api/v1/dashboard/me/                         # Dashboard unificado por rol
GET    /api/v1/indicadores/modalidades/              # KPIs modalidades (filtros: carrera, periodo)
GET    /api/v1/indicadores/culminacion/              # Tasa culminación + tiempo promedio
GET    /api/v1/indicadores/evolucion/                # Serie mensual
GET    /api/v1/indicadores/elegibilidad-ec/          # Estudiantes elegibles EC
```

#### Búsqueda y Exportación
```
GET    /api/v1/buscar/?q=&tipo=expediente|peticion|usuario|documento
GET    /api/v1/exportar/?formato=pdf|excel|csv&recurso=expedientes|peticiones&filtros=
```

#### Sesiones (P1)
```
POST   /api/v1/auth/logout/                          # Revocación refresh token
GET    /api/v1/sesiones/                             # Listar sesiones activas (Admin)
DELETE /api/v1/sesiones/{id}/                        # Revocar sesión (Admin)
```

#### Seguridad (P0/P1)
```
POST   /api/v1/csp-report/                           # Endpoint reportes CSP
```

---

## 9. PLAN DE INCREMENTOS DE IMPLEMENTACIÓN

### INC-01: Cierre Dependencias Críticas Seguridad (P0) — **SPRINT ACTUAL**
| Tarea | Descripción | Archivos | Criterio Aceptación |
|-------|-------------|----------|---------------------|
| INC-01-T01 | `MutantOperationThrottle` + aplicar a 7 endpoints mutantes | `core/adapters/throttling.py` (nuevo), views expedientes/verificacion/resoluciones | 429 tras exceder rate; tests `throttle_mutante` |
| INC-01-T02 | SCOPE_ASIGNADO en ScopeFilterMixin | `core/adapters/scope_filter.py`, `peticiones/views.py` | IDOR tests peticiones asignadas (8 tests/rol) |
| INC-01-T03 | Verificación SHA-256 en descarga | `peticiones/views.py:descargar_documento()` | Archivo corrupto → 500 + log auditoría |

### INC-02: JWT Hardening + Sesiones (P1) — **SPRINT +1**
| Tarea | Descripción | Archivos |
|-------|-------------|----------|
| INC-02-T01 | `ROTATE_REFRESH_TOKENS=True` + `BLACKLIST_AFTER_ROTATION=True` + `token_blacklist` app | `base.py`, `authentication/views.py` (logout), migración |
| INC-02-T02 | Sliding tokens alternativa: `SLIDING_TOKEN_LIFETIME=7d`, `SLIDING_TOKEN_REFRESH_LIFETIME=1d` | `base.py` |
| INC-02-T03 | Endpoint `POST /auth/logout/` con blocklist | `authentication/views.py`, `authentication/urls.py` |
| INC-02-T04 | Tabla `SesionUsuario` para métricas usuarios activos | Nuevo modelo, middleware actualización último acceso |

### INC-03: Modalidades de Titulación — Core Backend (P0) — **SPRINT +1**
| Tarea | Descripción | Archivos |
|-------|-------------|----------|
| INC-03-T01 | Migración: campo `opcion_titulacion` en `ExpedienteTitulacion` + enum `ModalidadTitulacion` | `expedientes/adapters/models.py`, migración |
| INC-03-T02 | Modelo `HistorialModalidad` + migración | `expedientes/adapters/models.py`, migración |
| INC-03-T03 | Servicio `verificar_elegibilidad_ec(estudiante)` — mock SGA (2 reprobaciones + 3ra matrícula) | `expedientes/services/verificar_elegibilidad_ec.py` |
| INC-03-T04 | Servicio `cambiar_modalidad(expediente, nueva_modalidad, autorizador, justificacion, evidencia)` | `expedientes/services/cambiar_modalidad.py` |
| INC-03-T05 | Endpoints modalidad (4 endpoints) + permisos RBAC | `expedientes/adapters/views.py`, `permissions.py` (matriz) |
| INC-03-T06 | Actualizar `crear_expediente.py`: default TIC, validar no EC sin autorización | `expedientes/services/crear_expediente.py` |
| INC-03-T07 | Tests: elegibilidad, cambio autorizado/no autorizado, historial, KPIs | `expedientes/tests/test_modalidades.py` |

### INC-04: Servicios KPI + Endpoint Dashboard (P0) — **SPRINT +1 a +2**
| Tarea | Descripción | Archivos |
|-------|-------------|----------|
| INC-04-T01 | Nueva app `indicadores` + `services/indicadores.py` (centraliza fórmulas) | `indicadores/` (nueva app) |
| INC-04-T02 | `GET /api/v1/dashboard/me/` — compone según roles usuario | `indicadores/adapters/views.py` |
| INC-04-T03 | Endpoints analíticos: modalidades, culminación, evolución | `indicadores/adapters/views.py` |
| INC-04-T04 | Permisos RBAC recurso `dashboard` + `indicadores` | `authentication/permissions.py` |
| INC-04-T05 | Tests fórmulas KPI (casos 0, 1, N, períodos vacíos) | `indicadores/tests/` |
| INC-04-T06 | Integración KPIs modalidades (KPI-MOD-01 a 08) | `indicadores/services/indicadores.py` |

### INC-05: Notificaciones, Alertas, Búsqueda (P1) — **SPRINT +2**
| Tarea | Descripción | Archivos |
|-------|-------------|----------|
| INC-05-T01 | Búsqueda universal `GET /api/v1/buscar/` (postgres trigram/tsvector) | `core/adapters/search.py`, `core/adapters/views.py` |
| INC-05-T02 | Exportaciones PDF/Excel/CSV genéricas | `core/services/exportacion.py`, `core/adapters/views.py` |
| INC-05-T03 | Endpoint CSP Report `POST /api/v1/csp-report/` + modelo `CSPViolation` | `notificaciones/adapters/models.py`, views |
| INC-05-T04 | WebSocket/SSE notificaciones tiempo real (opcional, P2) | `notificaciones/consumers.py`, routing |

### INC-06: Acciones Rápidas + Exportaciones Frontend (P1) — **SPRINT +2**
| Tarea | Descripción | Archivos Frontend |
|-------|-------------|-------------------|
| INC-06-T01 | Componente `AccionesRapidas` contextual por rol/estado | `features/expediente/AccionesRapidas.tsx` |
| INC-06-T02 | Botones exportación en dashboards/bandejas | `components/ui/ExportButton.tsx` |
| INC-06-T03 | Integración búsqueda universal en header | `components/layout/Header.tsx` |
| INC-06-T04 | Notificaciones toast + badge contador tiempo real | `components/feedback/ToastProvider.tsx` |

### INC-07: Vistas Frontend Completas (F3) — **SPRINT +2 a +3**
| Vista | Tareas Clave | Estimación |
|-------|--------------|------------|
| V-05 Peticiones | Lista, Solicitar emisión, FileUpload, Validación, Descarga | M |
| V-06 Seguimiento | Detalle petición, Versiones, Historial, Descarga | M |
| V-07 Bandeja | Paginación server, Filtros, Columnas rol, Empty states por rol | L |
| V-08 Detalle Funcionario | Checklist, Observar, Informe, Declaratoria, Descargas, Modalidad | L |

### INC-08: Integración Modalidades Frontend (P0) — **SPRINT +3**
| Tarea | Descripción | Archivos |
|-------|-------------|----------|
| INC-08-T01 | V-03: Selector modalidad condicionado a `GET /elegibilidad/` | `features/solicitud/NuevaSolicitudForm.tsx` |
| INC-08-T02 | V-04: Mostrar modalidad actual + historial en header | `features/expediente/ExpedienteHeader.tsx` |
| INC-08-T03 | V-08: Botón "Cambiar modalidad" (Secretario/Decano) + modal justificación | `features/expediente/CambiarModalidadDialog.tsx` |
| INC-08-T04 | Dashboards: Tarjetas/KPIs modalidad por rol | `features/dashboard/*.tsx` |
| INC-08-T05 | Validación cliente: no permitir EC sin elegibilidad confirmada backend | `features/solicitud/queries.ts` |

### INC-09: Pruebas Integración + Validación Final (P0) — **SPRINT +3 a +4**
| Tarea | Descripción |
|-------|-------------|
| INC-09-T01 | Pruebas contrato API (Postman/Insomnia collection) |
| INC-09-T02 | Pruebas E2E flujos completos (Cypress/Playwright) |
| INC-09-T03 | Pruebas seguridad: IDOR, RBAC, throttling, PDF validation |
| INC-09-T04 | Pruebas accesibilidad (axe) + responsive (320px) |
| INC-09-T05 | Validación normativa modalidades contra RRA-UNL (arts. 39,40,212,216,233) |
| INC-09-T06 | Stress testing (Locust): 50 concurrentes enviar, 100 cargar documento |
| INC-09-T07 | Auditoría final seguridad (re-ejecutar plan pruebas seguridad) |

---

## 10. MATRIZ DE BRECHAS CONSOLIDADA

| ID | Requisito | Estado Backend | Estado Frontend | Brecha | Prioridad | Incremento |
|----|-----------|----------------|-----------------|--------|-----------|------------|
| **SEGURIDAD** | | | | | | |
| SEC-01 | Throttling global mutantes | PI (VULN-001) | N/A | Falta implementación | P0 | INC-01 |
| SEC-02 | SCOPE_ASIGNADO ScopeFilterMixin | IP (VULN-002) | N/A | Falta implementación mixin | P0 | INC-01 |
| SEC-03 | Verificación SHA-256 descarga | PI (VULN-003) | N/A | Falta implementación | P1 | INC-01 |
| SEC-04 | JWT Rotación/Blocklist/Sliding | PI (VULN-005) | N/A | Falta config + endpoint logout | P1 | INC-02 |
| SEC-05 | FirmaEC real declaratoria | PI (VULN-010) | N/A | Falta integración criptográfica | P0 | INC-01 (paralelo) |
| SEC-06 | RESPONSABLE_DEPENDENCIA permisos | IP (VULN-006) | N/A | Definir celdas matriz | P1 | INC-02 |
| SEC-07 | CSP Report endpoint | PI (VULN-004) | N/A | Falta endpoint + modelo | P1 | INC-05 |
| **MODALIDADES TITULACIÓN** | | | | | | |
| MOD-01 | Campo `opcion_titulacion` expediente | PI (BE-06) | Bloqueado (FE-T301) | Modelo + migración | P0 | INC-03 |
| MOD-02 | Catálogo/Enum modalidades | PI | Bloqueado | Dominio controlado | P0 | INC-03 |
| MOD-03 | Reglas elegibilidad TIC/EC | PI | Bloqueado | Lógica negocio + mock SGA | P0 | INC-03 |
| MOD-04 | Autorización cambio modalidad | PI | Bloqueado | Endpoint + RBAC + auditoría | P0 | INC-03 |
| MOD-05 | Historial cambios modalidad | PI | Bloqueado | Modelo + servicio | P0 | INC-03 |
| MOD-06 | KPIs por modalidad | PI | PI | Servicios indicadores | P1 | INC-04 |
| MOD-07 | Selector modalidad V-03 | N/A | Bloqueado (DEC-14) | UI condicionada backend | P0 | INC-08 |
| MOD-08 | Modalidad en dashboards | N/A | PI | Tarjetas/gráficos por rol | P1 | INC-08 |
| **KPIs** | | | | | | |
| KPI-01 | App indicadores + servicios | PI | N/A | Nueva app backend | P0 | INC-04 |
| KPI-02 | Endpoint `/dashboard/me/` | PI | PI | Composición por rol | P0 | INC-04 |
| KPI-03 | Endpoints analíticos | PI | PI | Culminación, evolución | P1 | INC-04 |
| KPI-04 | 7 KPIs no implementables | Bloqueado | Bloqueado | Requieren BE-06, BE-10, modelos futuros | P2 | Futuro |
| **DASHBOARDS** | | | | | | |
| DB-01 | Dashboard Estudiante (V-02) | ✅ | ✅ (Hecha) | Completo | - | - |
| DB-02 | Dashboard Secretaría Carrera | ✅ (endpoints) | ❌ (stub) | Vista completa | P1 | INC-07 |
| DB-03 | Dashboard Jurista/Analista | ✅ | ❌ | Vista completa | P1 | INC-07 |
| DB-04 | Dashboard Decano | ✅ | ❌ | Vista completa | P1 | INC-07 |
| DB-05 | Dashboard Director Carrera | ✅ | ❌ | Vista completa | P1 | INC-07 |
| DB-06 | Dashboard Dependencia | ✅ | ❌ | Vista completa | P1 | INC-07 |
| DB-07 | Dashboard Admin | ✅ | ❌ | Vista completa | P1 | INC-07 |
| **FUNCIONALIDADES FRONTEND** | | | | | | |
| FE-01 | V-05 Peticiones | ✅ | ❌ (stub) | Implementación completa | P1 | INC-07 |
| FE-02 | V-06 Seguimiento Petición | ✅ | ❌ (stub) | Implementación completa | P1 | INC-07 |
| FE-03 | V-07 Bandeja | ✅ | ❌ (stub) | Implementación completa | P1 | INC-07 |
| FE-04 | V-08 Detalle Funcionario | ✅ | ❌ (stub) | Implementación completa | P1 | INC-07 |
| FE-05 | Búsqueda universal | PI | ❌ | Endpoint + UI | P1 | INC-05/06 |
| FE-06 | Exportaciones PDF/Excel/CSV | PI | ❌ | Servicios + Botones UI | P1 | INC-05/06 |
| FE-07 | Notificaciones tiempo real | ✅ (polling) | ✅ (toast) | WebSocket opcional | P2 | INC-05 |
| FE-08 | Acciones rápidas contextuales | ✅ (API) | PI | Componente por rol/estado | P1 | INC-06 |
| **SESESIONES** | | | | | | |
| SES-01 | Registro sesiones verificable | PI | N/A | Tabla SesionUsuario | P1 | INC-02 |
| SES-02 | Métricas usuarios activos | PI | N/A | Queries auditoría/sesiones | P1 | INC-02 |
| SES-03 | Revocación tokens logout | PI | N/A | Blocklist + endpoint | P1 | INC-02 |

---

## 11. DEPENDENCIAS ENTRE INCREMENTOS

```
INC-01 (Seguridad P0) 
    ├── INC-02 (JWT/Sesiones P1) ──────────────────┐
    ├── INC-03 (Modalidades Core P0) ──────────────┼──→ INC-04 (KPIs/Dashboard P0)
    └── INC-05 (Notificaciones/Búsqueda P1) ───────┤
                                                    │
INC-03 (Modalidades) ──────────────────────────────┼──→ INC-08 (Modalidades Frontend P0)
                                                    │
INC-04 (KPIs) ─────────────────────────────────────┼──→ INC-07 (Dashboards Frontend P1)
                                                    │
INC-05/06 (Búsqueda/Export/Acciones) ──────────────┼──→ INC-07 (Vistas Completas P1)
                                                    │
                                                    └──→ INC-09 (Integración Final P0)
```

**Ruta crítica:** INC-01 → INC-03 → INC-04 → INC-08/INC-07 → INC-09

---

## 12. PRIMER INCREMENTO RECOMENDADO: INC-01

### Justificación
- **Bloquea producción:** VULN-001 (DoS endpoints críticos), VULN-002 (IDOR peticiones), VULN-003 (integridad descarga)
- **Sin dependencias previas:** Usa infraestructura existente (TrustedProxyScopedRateThrottle, ScopeFilterMixin)
- **Alto impacto seguridad:** Cierra 2 vulnerabilidades ALTA + 1 MEDIA
- **Habilita confianza** para integración frontend y pruebas de carga

### Entregables INC-01
1. `MutantOperationThrottle` en 7 endpoints mutantes con tests
2. `SCOPE_ASIGNADO` funcionando en ScopeFilterMixin + migración validación manual peticiones
3. Verificación SHA-256 streaming en `descargar_documento()` + test corrupción
4. Evidence: `pytest -k "throttle_mutante or idor_peticiones or sha256_descarga"` → 100% pass

### Criterios para Autorizar Implementación INC-01
- [ ] Código revisado por par (security review)
- [ ] Tests unitarios + integración pasando en CI
- [ ] No regresiones en suite existente (497 tests)
- [ ] Documentación actualizada en `MATRIZ_ESTADO_CONTROLES_SEGURIDAD.md`

---

## 13. CRITERIOS GENERALES PARA AUTORIZAR IMPLEMENTACIÓN

### Por Incremento
1. **Evidencia técnica** de dependencias resueltas (no "se resolverá después")
2. **Tests automatizados** definidos y pasando (unit + integración + contrato)
3. **Revisión seguridad** para cambios en auth, permisos, validación
4. **Validación normativa** para reglas académicas (modalidades, plazos, elegibilidad)
5. **Accesibilidad AA** verificada (axe) para nuevos componentes UI
6. **Responsive 320px** verificado en navegador real
7. **Lint + Typecheck + Build + Tests** pasando (`npm run lint && npm run typecheck && npm run build && npm run test`)

### Para Modalidades de Titulación (Requisito Especial)
- [ ] **Contraste directo** Arts. 39, 40, 212, 216, 233 RRA-UNL (fuente primaria)
- [ ] **Aprobación expresa** de autoridad académica competente (Secretaría General / Decanato)
- [ ] **Mock SGA validado** para elegibilidad EC (2 reprobaciones + 3ra matrícula)
- [ ] **Actor autorizador confirmado** (Secretario verifica + Decano autoriza)
- [ ] **No implementar** selector frontend sin backend aprobado (DEC-14, CA-G-01)

---

## 14. DOCUMENTOS GENERADOS/ACTUALIZADOS (ENTREGABLES DE ESTA FASE)

| Documento | Estado | Ubicación |
|-----------|--------|-----------|
| `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` | ✅ Este documento | Raíz repo |
| `MATRIZ_BRECHAS_BACKEND_FRONTEND.md` | ✅ Sección 10 | Raíz repo |
| `ARQUITECTURA_DASHBOARDS_POR_ROL.md` | ✅ Sección 6 | Raíz repo |
| `MATRIZ_INTEGRACION_KPIS_ENDPOINTS.md` | ✅ Secciones 5, 8 | Raíz repo |
| `PLAN_IMPLEMENTACION_SESIONES_USUARIOS_ACTIVOS.md` | ✅ Secciones 3.4, 9 (INC-02) | Raíz repo |
| `MATRIZ_ACCIONES_RAPIDAS_POR_ROL.md` | ✅ Sección 6.2, 7.3 | Raíz repo |
| `ESPECIFICACION_SERVICIOS_DASHBOARD.md` | ✅ Secciones 4, 5, 8 | Raíz repo |
| `PLAN_INTEGRACION_FRONTEND_BACKEND.md` | ✅ Secciones 7, 8, 9 | Raíz repo |
| `ROADMAP_INCREMENTOS_IMPLEMENTACION.md` | ✅ Sección 9 | Raíz repo |
| `DISENO_FUNCIONAL_MODALIDADES_TITULACION.md` | ✅ Sección 4 | Raíz repo |
| `MATRIZ_REGLAS_NEGOCIO_MODALIDADES.md` | ✅ Sección 4.2 | Raíz repo |
| `MATRIZ_KPIS_MODALIDADES_TITULACION.md` | ✅ Sección 5 | Raíz repo |
| `ESPECIFICACION_API_MODALIDADES_TITULACION.md` | ✅ Sección 8.2 | Raíz repo |

---

## 15. INFORME FINAL RESUMIDO

### A. Estado Backend
**Maduro (85% ASVS Nivel 2).** 6 apps operativas, state machine completa, validación PDF estricta, auditoría inmutable, RBAC server-side. **Gap crítico:** FirmaEC no implementada en declaratoria.

### B. Estado Seguridad + SEC-T004
**SEC-T004 (JWT_SIGNING_KEY ≠ SECRET_KEY): ✅ IMPLEMENTADO Y VERIFICADO** (`base.py:14-20` warning log).  
**Pendientes P0:** Throttling global (VULN-001), SCOPE_ASIGNADO (VULN-002), FirmaEC (VULN-010).

### C. Estado KPIs
**Diseño completo (40 KPIs), 33 implementables.** App `indicadores` y endpoint `/dashboard/me/` **no existen**. 7 KPIs bloqueados por modalidades/catálogos.

### D. Estado Sesiones/Usuarios Activos
**JWT stateless sin registro sesiones.** Refresh 24h fijo, sin rotación, sin revocación logout, sin métricas actividad. Requiere tabla `SesionUsuario` + blocklist.

### E. Estado Modalidades Titulación
**AUSENTES EN TODAS LAS CAPAS.** Modelo, reglas, endpoints, KPIs, frontend — todo pendiente. **Requisito transversal P0.**

### F. Reglas Académicas a Implementar
1. TIC = predeterminada (Art. 39, 212, 216 RRA-UNL)
2. EC = excepcional, requiere 2 reprobaciones + 3ra matrícula (Art. 40, 212 inc. b, 233)
3. Cambio solo con autorización Secretario (verifica) + Decano (autoriza)
4. Historial inmutable + evidencia académica
5. Validación contra datos SGA (mock)

### G. KPIs Modalidades
8 KPIs nuevos (KPI-MOD-01 a 08) integrados en `/indicadores/modalidades/` y dashboard global.

### H. Endpoints
**Existentes:** 23 endpoints operativos verificados.  
**Requeridos:** 15+ nuevos (modalidades 4, KPIs 5, búsqueda 1, exportación 1, sesiones 3, CSP 1).

### I. Dashboards por Rol
7 dashboards roles operativos + 1 admin + 1 estudiante. Arquitectura unificada `/dashboard/me/`.

### J. Frontend Pendiente
V-05, V-06, V-07, V-08 (stubs → completas), búsqueda, exportación, modalidad en V-03/V-04/V-08.

### K. Brechas Integración
Modalidades (bloqueante), KPIs (backend), Vistas funcionario (frontend), Búsqueda/Export (ambos).

### L. Dependencias Incrementos
Ruta crítica: INC-01 → INC-03 → INC-04 → INC-08/07 → INC-09 (4-5 sprints).

### M. Primer Incremento
**INC-01: Seguridad P0** (Throttling global + SCOPE_ASIGNADO + SHA-256 descarga). Sprint actual.

### N. Criterios Autorización Implementación
Ver Sección 13. **No programar sin:** evidencia dependencias, tests definidos, revisión seguridad, validación normativa (modalidades), accesibilidad AA.

---

## 16. PRÓXIMOS PASOS INMEDIATOS

1. **Validar normativa RRA-UNL** (arts. 39, 40, 212, 216, 233) con autoridad competente → definir elegibilidad EC exacta
2. **Autorizar INC-01** (seguridad P0) para sprint actual
3. **Diseñar mock SGA** para verificación 2 reprobaciones + 3ra matrícula (INC-03-T03)
4. **Confirmar actor autorizador** cambio modalidad (Secretario + Decano)
5. **Crear app `indicadores`** y endpoint `/dashboard/me/` (INC-04) en paralelo con INC-03
6. **Planificar sprints** con equipo backend/frontend según dependencias documentadas

---

**Fin del Plan Maestro**  
**Autor:** Arquitecto Senior / Ingeniero Ciberseguridad / Líder Técnico Frontend  
**Fecha:** 2026-11-09  
**Próxima revisión:** Tras validación normativa modalidades y cierre INC-01