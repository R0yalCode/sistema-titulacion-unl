# PLAN DE INTEGRACIÓN FRONTEND-BACKEND — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` + `specs/003-frontend-titulacion/` + auditoría backend  

---

## 1. ESTADO ACTUAL DE LA INTEGRACIÓN

### 1.1 Frontend (Completado F0-F2.5)
| Capa | Estado | Evidencia |
|------|--------|-----------|
| Andamiaje (Vite+React+TS, ESLint, Vitest, MSW) | ✅ 100% | `npm run lint/typecheck/build/test` ✅ |
| Autenticación (JWT, AuthContext, HTTP client, Guards, Login) | ✅ 100% | 81/81 tests auth/api |
| UI Kit (Form fields, Badge/Card/Alert/Spinner, Empty/Error/NotFound/Forbidden, Table, Pagination, Modal, Timeline, FileUpload, Toasts) | ✅ 100% | 170/170 tests + axe 0 violations |
| Estados error (404 page, 401/403/500/503 globales, InlineAlerts 409/412/428 bloqueados BE-11) | ✅ 80% | FE-T1210 a FE-T1214 |
| Vistas implementadas | V-01, V-02, V-03, V-04, V-09 | Ver `tasks.md` F3 |
| Vistas **stubs** (sin lógica) | V-05, V-06, V-07, V-08 | 175-190 bytes c/u |

### 1.2 Backend (Operativo)
| Módulo | Endpoints | Tests | Estado |
|--------|-----------|-------|--------|
| Auth | `POST /auth/token/`, `POST /auth/token/refresh/` | 4 | ✅ |
| Expedientes | 6 endpoints (CRUD + bandeja + enviar + observar) | 75 | ✅ |
| Peticiones | 4 endpoints (solicitar, cargar/descargar doc) | 98 | ✅ |
| Verificación | 4 endpoints (checklist, evaluar, subsanar) | 87 | ✅ |
| Resoluciones | 2 endpoints (informe, declaratoria) | 73 | ⚠️ Falta FirmaEC |
| Notificaciones | 2 endpoints (listar, marcar leída) | 92 | ✅ |

### 1.3 Brechas de Integración Identificadas
| Brecha | Frontend | Backend | Impacto |
|--------|----------|---------|---------|
| **Modalidades titulación** | V-03 bloqueado (DEC-14), V-04/V-08 sin modalidad | BE-06 ausente (campo `opcion_titulacion`) | **BLOQUEANTE TRANSVERSAL** |
| **KPIs/Dashboard unificado** | V-02 usa queries separadas | App `indicadores` + `/dashboard/me/` no existen | Duplicidad, sin métricas modalidad |
| **Vistas funcionario** | V-07/V-08 stubs | Endpoints existen | Funcionarios sin UI operativa |
| **Búsqueda universal** | No existe | No existe | Transversal |
| **Exportaciones** | No existe | No existe | Dashboards, bandejas |
| **Notificaciones tiempo real** | Solo polling (TanStack Query) | Solo polling | Opcional P2 |
| **CORS** | Requerido para desarrollo | BE-08 ausente | Bloquea consumo API en navegador |

---

## 2. ESTRATEGIA DE INTEGRACIÓN

### 2.1 Principios
1. **Backend = Autoridad única**: Reglas negocio, permisos, validaciones, modalidades, KPIs
2. **Frontend = Consumo + UX**: Nunca duplica lógica negocio; solo presentacional (`dias_restantes = fecha - hoy`)
3. **Contrato estable**: Tipos derivados de OpenAPI/código real; discrepancias documentadas en `clarify.md`
4. **Degradación elegante**: Vistas sin backend → estado "no habilitado" explicativo (V-09), nunca datos ficticios (CA-G-01)
5. **Autenticación JWT stateless**: Access en `sessionStorage` (clave `sgt.access`); Refresh **no persistido** (sin endpoint refresh BE-03)

### 2.2 Flujo de Datos Típico
```
Usuario → Login (V-01) → JWT access + roles + cedula
    → AuthContext → Guards (rol/ruta) → Dashboard (V-02/V-07)
    → TanStack Query (staleTime: 30s) → GET /api/v1/dashboard/me/
    → Servicios Indicadores (BD) → JSON unificado
    → Componentes Dashboard (Tarjetas, Gráficos, Tabla, Acciones)
    → Mutaciones (POST/PUT) → Invalidación queries → UI actualizada
```

### 2.3 Manejo de Errores (Unificado)
- `src/api/client.ts` → `ApiRequestError` normalizado (status, fieldErrors, message, code)
- `src/lib/apiErrorPresentation.ts` → `presentApiError()` mapea a componente UI (`ErrorState`, `ForbiddenState`, `NotFoundState`, `InlineAlert`)
- **401** → Limpia sesión + redirige `/login` + toast "Sesión expirada"
- **403** → `ForbiddenState` en vista + V-09 por guardas
- **404** → `NotFoundState` (página global) o en recurso
- **5xx/red** → `ErrorState` con "Reintentar" real (refetch)
- **409/412/428** → `InlineAlert` en formulario (solo si BE-11 declara códigos)

---

## 3. PLAN DE INTEGRACIÓN POR INCREMENTOS

### INC-01: Seguridad P0 (Backend) — **Sprint Actual**
- Throttling global mutantes, SCOPE_ASIGNADO, SHA-256 descarga
- **Frontend:** Sin cambios (solo beneficia estabilidad)

### INC-02: JWT/Sesiones (Backend) — **Sprint +1**
- Rotación refresh, blocklist logout, métricas usuarios activos
- **Frontend:** Conectar `AuthContext.logout()` → `POST /auth/logout/` (ya implementado en `AppLayout.tsx`)

### INC-03: Modalidades Core (Backend) — **Sprint +1** 🔑 **CRÍTICO**
- Campo `opcion_titulacion`, `HistorialModalidad`, elegibilidad EC, endpoints modalidad
- **Frontend:** Preparar tipos + hooks (sin UI aún)

### INC-04: KPIs/Dashboard (Backend) — **Sprint +1 a +2** 🔑 **CRÍTICO**
- App `indicadores`, `/dashboard/me/`, endpoints analíticos, KPIs modalidad
- **Frontend:** `StudentDashboardPage` → `useDashboardMe()` (reemplaza queries separadas)

### INC-05: Búsqueda/Exportación/CSP (Backend) — **Sprint +2**
- `/buscar/`, `/exportar/`, `/csp-report/`
- **Frontend:** `SearchBar` en Header, `ExportButton` en AccionesRapidas

### INC-06: Acciones Rápidas/Exportación (Frontend) — **Sprint +2**
- Componente `AccionesRapidas` genérico + helpers permisos completos
- `ExportButton` modal con formato/filtros

### INC-07: Vistas Funcionario Completas (Frontend) — **Sprint +2 a +3**
| Vista | Trabajo | Endpoints Backend |
|-------|---------|-------------------|
| V-05 Peticiones | Lista, Solicitar emisión, FileUpload, Validación, Descarga, Versiones | `GET /expedientes/{id}/`, `POST /peticiones/{id}/solicitar-emision/`, `POST/GET /peticiones/{id}/documento/` |
| V-06 Seguimiento | Detalle petición, Historial versiones, Descarga | `GET /expedientes/{id}/` (peticiones anidadas), `GET /peticiones/{id}/documento/{version}/` |
| V-07 Bandeja | Paginación server, Filtros, Columnas por rol, Empty states | `GET /expedientes/bandeja/?page=&page_size=` + filtros query |
| V-08 Detalle Funcionario | Checklist, Observar, Informe, Declaratoria, Descargas, **Modalidad** | Todos endpoints verificacion/resoluciones + modalidad |

### INC-08: Modalidad en Frontend — **Sprint +3** 🔑 **CRÍTICO**
| Componente | Cambio | Endpoint |
|------------|--------|----------|
| `NuevaSolicitudForm` (V-03) | Selector modalidad condicionado a `GET /elegibilidad/` | `GET /expedientes/{id}/modalidad/elegibilidad/` |
| `ExpedienteHeader` (V-04) | Badge modalidad actual + historial | `GET /expedientes/{id}/modalidad/` |
| `AccionesRapidas` (V-04/V-08) | "Verificar elegibilidad EC" (Secretario), "Cambiar modalidad" (Decano) | `GET/POST /expedientes/{id}/modalidad/` |
| Dashboards | Tarjetas KPI-MOD-01 a 08 + `ModalidadPanel` | `/indicadores/modalidades/` |

### INC-09: Integración Final + Pruebas — **Sprint +3 a +4**
- Pruebas contrato (Postman/Insomnia collection)
- Pruebas E2E (Cypress/Playwright): flujos completos por rol
- Stress testing (Locust): 50 concurrentes enviar, 100 cargar documento
- Accesibilidad (axe) + Responsive (320px) todas las vistas
- Validación normativa modalidades (RRA-UNL arts. 39,40,212,216,233)

---

## 4. CONTRATOS DE TIPOS COMPARTIDOS

### 4.1 Tipos Frontend (Derivados de OpenAPI + Código Real)
```typescript
// frontend/src/api/types/expediente.ts
export type EstadoExpediente = 
  | 'BORRADOR' | 'ENVIADA' | 'EN_VERIFICACION' 
  | 'OBSERVADA' | 'INFORME_EMITIDO' | 'DECLARADA_APTA' | 'CANCELADA';

export type ModalidadTitulacion = 'TIC' | 'EC';  // Trabajo Integración Curricular | Examen Complexivo

export interface ExpedienteDetalle {
  id: string;
  numero_expediente: string;
  estudiante_id: string;
  carrera_id: string;
  facultad_id: string;
  estado: EstadoExpediente;
  opcion_titulacion: ModalidadTitulacion;  // NUEVO INC-03
  activa: boolean;
  fecha_creacion: string;
  fecha_recepcion: string | null;
  numero_providencia: string | null;
  fecha_limite_atencion: string | null;
  dias_laborables_acumulados: number;
  peticiones: PeticionInicializada[];
}

export interface HistorialModalidad {
  id: string;
  expediente: string;
  modalidad_anterior: ModalidadTitulacion;
  modalidad_nueva: ModalidadTitulacion;
  fecha_cambio: string;
  autorizado_por: string;
  justificacion: string;
  evidencia_academica: any;
  estado_tercera_matricula: boolean;
}
```

### 4.2 Tipos Dashboard
```typescript
// frontend/src/api/types/dashboard.ts
export interface DashboardMeResponse {
  generado_en: string;
  ambito: { tipo: 'own' | 'carrera' | 'facultad' | 'all' | 'asignado'; id: string | null };
  rol_principal: string;
  secciones: {
    resumen: { kpi_clave: number; alertas: number; acciones_pendientes: number };
    tarjetas_p0: Array<{ titulo: string; valor: string; variante: string; accion?: { label: string; endpoint: string } }>;
    grafico_principal: { tipo: 'bar' | 'line' | 'pie' | 'progress'; datos: any; titulo: string };
    tabla_trabajo: { columnas: any[]; filas: any[]; paginacion: any; acciones?: any[] };
    actividad_reciente: any[];
    notificaciones_no_leidas: number;
    modalidad_titulacion: { 
      actual: ModalidadTitulacion; 
      elegible_ec: boolean; 
      historial: HistorialModalidad[] 
    };
  };
}
```

---

## 5. CONFIGURACIÓN DESARROLLO (CORS + PROXY)

### 5.1 Vite Proxy (`frontend/vite.config.ts`)
```typescript
// temporal hasta BE-08 (CORS backend)
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // backend dev
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
```

### 5.2 Variables Entorno Frontend (`.env.example`)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_DEMO_MODE=false
VITE_USE_MOCKS=false
VITE_APP_NAME=SGT-SIAAF
```

---

## 6. MANEJO DE DISCREPANCIAS BACKEND-FRONTEND

| Discrepancia | Documentada en | Tratamiento Frontend |
|--------------|----------------|---------------------|
| `POST /auth/token/` retorna `access`+`refresh` (OpenAPI dice "No response body") | `clarify.md` INC-13 | Tipar `TokenPair {access, refresh}`; no modificar OpenAPI |
| `GET /notificaciones/` retorna `{results: []}` sin paginación (OpenAPI dice array plano) | `clarify.md` INC-19 | Implementar contra código real: `ListNotificacionesResponse {results: NotificacionInterna[]}` |
| `POST /expedientes/{id}/observar/` retorna 201 (specify.md decía 200) | `clarify.md` INC-21 | Tipar respuesta real `ObservacionAccionable` |
| Excepciones dominio → 500 genérico (observar, evaluar, subsanar) | `clarify.md` INC-21 | `describeAccionError()` muestra `detail` real sin importar status |
| Subsanación requiere `checklist_verification_id` (no `peticion_id`) y estudiante no tiene acceso a checklist | `clarify.md` FE-T407 hallazgo crítico | UI informa limitación; no inventar flujo |

**Regla:** Frontend se adapta a comportamiento real; discrepancias documentadas, no corregidas en backend.

---

## 7. PRUEBAS DE INTEGRACIÓN

### 7.1 Colección Postman/Insomnia (Backend)
- Carpeta por módulo: Auth, Expedientes, Peticiones, Verificación, Resoluciones, Notificaciones, Indicadores, Modalidades
- Casos: 200, 400, 401, 403, 404, 422, 500
- Variables entorno: `base_url`, `access_token`, `refresh_token`
- Scripts: Auto-guardar tokens, refrescar en 401

### 7.2 Tests MSW Frontend (`frontend/src/mocks/handlers.ts`)
```typescript
// Handlers por vista para tests integración
export const handlers = [
  // Auth
  http.post('/api/v1/auth/token/', () => HttpResponse.json({ access: '...', refresh: '...' })),
  http.post('/api/v1/auth/token/refresh/', () => HttpResponse.json({ access: '...' })),
  // Dashboard
  http.get('/api/v1/dashboard/me/', () => HttpResponse.json(dashboardMeFixture)),
  http.get('/api/v1/indicadores/modalidades/', () => HttpResponse.json(modalidadesFixture)),
  // Expedientes
  http.get('/api/v1/expedientes/bandeja/', () => HttpResponse.json(bandejaFixture)),
  http.get('/api/v1/expedientes/:id/', () => HttpResponse.json(expedienteDetalleFixture)),
  http.post('/api/v1/expedientes/:id/enviar/', () => HttpResponse.json(expedienteEnviadoFixture)),
  // ... etc
];
```

### 7.3 Tests E2E (Cypress/Playwright) — INC-09
| Flujo | Roles | Validaciones |
|-------|-------|--------------|
| Login → Dashboard → Crear solicitud → Enviar → Verificar → Informe → Declaratoria | Estudiante, Secretario, Decano | Estados, notificaciones, plazos, modalidad |
| Funcionario: Bandeja → Detalle → Evaluar checklist → Observar → Subsanar → Informe | Secretario, Analista | RBAC, ScopeFilterMixin, plazos |
| Admin: Usuarios → Roles → Catálogos → Auditoría | Admin | SCOPE_ALL, gestión usuarios |

---

## 8. CHECKLIST PRE-INTEGRACIÓN POR SPRINT

### Sprint Actual (INC-01)
- [ ] Backend: Throttling global + SCOPE_ASIGNADO + SHA-256 descarga passing tests
- [ ] Frontend: Sin cambios requeridos

### Sprint +1 (INC-02 + INC-03 + INC-04 inicio)
- [ ] Backend: JWT rotación + logout + métricas usuarios activos
- [ ] Backend: Modalidades core (modelo, servicios, endpoints, tests)
- [ ] Backend: App `indicadores` + `/dashboard/me/` (básico)
- [ ] Frontend: Actualizar tipos TypeScript (modalidad, dashboard)
- [ ] Frontend: Conectar logout real → `POST /auth/logout/`

### Sprint +2 (INC-04 completo + INC-05 + INC-06)
- [ ] Backend: Endpoints analíticos + búsqueda + exportación + CSP
- [ ] Frontend: `StudentDashboardPage` → `useDashboardMe()`
- [ ] Frontend: `AccionesRapidas` genérico + `ExportButton`
- [ ] Frontend: `SearchBar` en Header

### Sprint +3 (INC-07 + INC-08)
- [ ] Frontend: V-05, V-06, V-07, V-08 completas
- [ ] Frontend: Modalidad en V-03, V-04, V-08, Dashboards
- [ ] Backend: Validación integración modalidad + KPIs modalidad

### Sprint +4 (INC-09)
- [ ] Pruebas contrato (Postman)
- [ ] Pruebas E2E (Cypress) flujos completos
- [ ] Stress testing (Locust)
- [ ] Accesibilidad + Responsive audit
- [ ] Validación normativa modalidades (RRA-UNL)

---

## 9. RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| BE-08 (CORS) no resuelto a tiempo | Alta | Bloquea consumo API en navegador | Vite proxy temporal; documentar como bloqueo producción |
| Modalidades (BE-06) requiere validación normativa extensa | Media | Bloquea INC-03/08 | Iniciar validación RRA-UNL **ya** (arts. 39,40,212,216,233) |
| FirmaEC (VULN-010) compleja integración PKI | Media | Declaratoria sin validez legal | Paralelizar: mock FirmaEC para dev; producción con PKI real |
| SCOPE_ASIGNADO (VULN-002) requiere refactor ScopeFilterMixin | Media | IDOR peticiones | Prioridad P0 en INC-01; tests IDOR exhaustivos |
| Frontend V-07/V-08 complejas (lógica por rol/estado) | Media | Retraso INC-07 | Componentes base listos; `accionesPorRolEstado.ts` base existente |

---

## 10. COMUNICACIÓN Y GOBERNANZA

- **Reunión semanal** integración: Backend lead + Frontend lead + Product Owner
- **Definición de Hecha (DoD) compartida**: Lint + Typecheck + Tests + Build + Accesibilidad + Code Review
- **Branch strategy**: `main` (protegida), `feature/*` por incremento, PR obligatorio
- **Documentación viva**: `clarify.md` actualizado con cada discrepancia; `tasks.md` estado real por tarea
- **No simular**: Si backend no expone dato → frontend muestra limitación (V-09 o estado vacío)

---

## 11. PRÓXIMOS PASOS INMEDIATOS

1. **Validar normativa RRA-UNL** (arts. 39, 40, 212, 216, 233) con autoridad competente → definir elegibilidad EC exacta
2. **Autorizar INC-01** (Seguridad P0) para sprint actual
3. **Iniciar INC-03** (Modalidades Core) en paralelo: crear migración `opcion_titulacion` + `HistorialModalidad`
4. **Crear app `indicadores`** (INC-04) estructura base
5. **Configurar Vite proxy** + variables entorno frontend para desarrollo integrado
6. **Generar colección Postman** base con endpoints actuales
7. **Actualizar `tasks.md`** con estado real post-auditoría (ya hecho en F0-F2.5)