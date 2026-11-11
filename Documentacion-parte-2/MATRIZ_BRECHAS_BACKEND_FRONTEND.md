# MATRIZ DE BRECHAS BACKEND-FRONTEND — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** Consolidada de `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md`  

---

## LEYENDA DE ESTADOS

| Código | Estado | Descripción |
|--------|--------|-------------|
| **CV** | COMPLETADO Y VERIFICADO | Código existe, tests pasan, evidencia verificable |
| **IP** | IMPLEMENTADO PARCIALMENTE | Código existe pero incompleto o sin tests completos |
| **PI** | PENDIENTE DE IMPLEMENTACIÓN | No existe implementación |
| **BL** | BLOQUEADO | Dependencia externa no resuelta |
| **NA** | NO APLICA | Control no relevante para este componente |
| **NV** | NO VERIFICABLE | Insuficiente evidencia para determinar estado |

---

## MATRIZ COMPLETA

| ID | Requisito | Estado Backend | Estado Frontend | Brecha | Prioridad | Incremento |
|----|-----------|----------------|-----------------|--------|-----------|------------|
| **SEGURIDAD** |
| SEC-01 | Throttling global endpoints mutantes | PI (VULN-001) | NA | Falta `MutantOperationThrottle` en 7 endpoints | P0 | INC-01 |
| SEC-02 | SCOPE_ASIGNADO en ScopeFilterMixin | IP (VULN-002) | NA | Mixin no implementa scope; validación manual solo en descarga | P0 | INC-01 |
| SEC-03 | Verificación SHA-256 al descargar | PI (VULN-003) | NA | Solo `archivo_existe()`; no compara hash BD vs disco | P1 | INC-01 |
| SEC-04 | JWT Rotación/Blocklist/Sliding | PI (VULN-005) | NA | `ROTATE_REFRESH_TOKENS=False`; sin logout server-side | P1 | INC-02 |
| SEC-05 | FirmaEC real en declaratoria | PI (VULN-010) | NA | Solo validación PDF genérica; sin verificación certificado/cadena/TSA | P0 | INC-01 (paralelo) |
| SEC-06 | RESPONSABLE_DEPENDENCIA permisos | IP (VULN-006) | NA | Rol sin celdas en matriz RBAC | P1 | INC-02 |
| SEC-07 | CSP Report endpoint | PI (VULN-004) | NA | `CSP_REPORT_ONLY_POLICY` sin `report-uri` | P1 | INC-05 |
| SEC-08 | Migración RS256 (claves asimétricas) | PI (VULN-011) | NA | HS256 simétrico; riesgo multi-servidor | P2 | Futuro |
| SEC-09 | Sellado temporal RFC 3161 | PI (VULN-012) | NA | Documentos legales sin TSA | P2 | Futuro |
| SEC-10 | Tests negativos Mass Assignment/BOLA | PI (VULN-013) | NA | Sin tests explícitos regresión | P3 | Futuro |
| SEC-11 | Historial modelos maestros (User, Role, Catalogo) | PI (VULN-014) | NA | Signals solo cubren modelos negocio | P2 | Futuro |
| **MODALIDADES TITULACIÓN** |
| MOD-01 | Campo `opcion_titulacion` en ExpedienteTitulacion | PI (BE-06) | BL (FE-T301/302) | Modelo + migración + enum `ModalidadTitulacion` | P0 | INC-03 |
| MOD-02 | Catálogo/Enum modalidades válidas (TIC, EC) | PI | BL | Dominio controlado en BD | P0 | INC-03 |
| MOD-03 | Reglas elegibilidad TIC (predeterminada) | PI | BL | Default TIC; validar 100% asignaturas o 85% horas | P0 | INC-03 |
| MOD-04 | Reglas elegibilidad EC (excepcional) | PI | BL | 2 reprobaciones + 3ra matrícula efectiva (mock SGA) | P0 | INC-03 |
| MOD-05 | Autorización cambio modalidad (Secretario+Decano) | PI | BL | Endpoint dedicado + RBAC + auditoría | P0 | INC-03 |
| MOD-06 | Historial inmutable cambios modalidad | PI | BL | Modelo `HistorialModalidad` + servicio | P0 | INC-03 |
| MOD-07 | Evidencia académica respaldo habilitación EC | PI | BL | JSON con reprobaciones, matrícula, verificación SGA | P0 | INC-03 |
| MOD-08 | Protección modificación directa API | PI | BL | Validación server-side en servicio cambio | P0 | INC-03 |
| MOD-09 | Tratamiento expedientes con actividades iniciadas | PI | BL | Reglas transición según estado actual | P0 | INC-03 |
| MOD-10 | KPIs por modalidad (8 indicadores) | PI | PI | Servicios indicadores + endpoint | P1 | INC-04 |
| MOD-11 | Selector modalidad V-03 condicionado backend | NA | BL (DEC-14) | UI solo muestra EC si backend confirma elegibilidad | P0 | INC-08 |
| MOD-12 | Modalidad actual + historial en V-04/V-08 | NA | PI | Header expediente + dialog cambio | P1 | INC-08 |
| MOD-13 | Dashboards: tarjetas/gráficos modalidad por rol | NA | PI | Integrar KPI-MOD-01 a 08 | P1 | INC-08 |
| **KPIs** |
| KPI-01 | App `indicadores` + servicios centralizados | PI | NA | Nueva app backend | P0 | INC-04 |
| KPI-02 | Endpoint `GET /api/v1/dashboard/me/` | PI | PI | Composición por rol (unificado) | P0 | INC-04 |
| KPI-03 | Endpoints analíticos (culminación, evolución) | PI | PI | `/indicadores/culminacion/`, `/evolucion/` | P1 | INC-04 |
| KPI-04 | KPIs modalidades (MOD-10) | PI | PI | Ver MOD-10 | P1 | INC-04 |
| KPI-05 | 7 KPIs no implementables (tutoría, sustentación, períodos, carreras, abandonados, usuarios activos reales, modalidad) | BL | BL | Requieren: BE-06, BE-10, modelos futuros, tabla sesiones | P2 | Futuro |
| **DASHBOARDS POR ROL** |
| DB-01 | Dashboard Estudiante (V-02) | CV | CV | Completo (bandeja BORRADOR/OBSERVADA + notificaciones) | - | - |
| DB-02 | Dashboard Secretaría Carrera | CV (endpoints) | PI (stub) | Vista completa: tarjetas, tabla, filtros, accesos rápidos | P1 | INC-07 |
| DB-03 | Dashboard Secretario Abogado / Analista | CV (endpoints) | PI (stub) | Vista completa: checklist, observaciones, informe | P1 | INC-07 |
| DB-04 | Dashboard Decano | CV (endpoints) | PI (stub) | Vista completa: declaratoria, tasa culminación facultad | P1 | INC-07 |
| DB-05 | Dashboard Director Carrera | CV (endpoints) | PI (stub) | Vista completa: distribución estados, tiempo promedio | P1 | INC-07 |
| DB-06 | Dashboard Responsable Dependencia | CV (endpoints peticiones) | PI (stub) | Vista completa: peticiones asignadas SOLICITADO/OBSERVADO | P1 | INC-07 |
| DB-07 | Dashboard Administrador | CV (endpoints) | PI (stub) | Vista completa: global, evolución, auditoría, usuarios | P1 | INC-07 |
| **FUNCIONALIDADES FRONTEND** |
| FE-01 | V-05 Gestión Peticiones Documentales | CV | PI (stub 190B) | Lista, solicitar emisión, carga PDF, validación, descarga | P1 | INC-07 |
| FE-02 | V-06 Seguimiento Petición | CV | PI (stub 188B) | Detalle, versiones, historial, descarga | P1 | INC-07 |
| FE-03 | V-07 Bandeja Funcionario | CV | PI (stub 175B) | Paginación server, filtros, columnas por rol, empty states | P1 | INC-07 |
| FE-04 | V-08 Detalle Funcionario | CV | PI (stub 186B) | Checklist, observar, informe, declaratoria, descargas, modalidad | P1 | INC-07 |
| FE-05 | Búsqueda Universal | PI | PI | Endpoint `/buscar/` + UI en header | P1 | INC-05/06 |
| FE-06 | Exportaciones PDF/Excel/CSV | PI | PI | Servicios backend + botones UI contextuales | P1 | INC-05/06 |
| FE-07 | Notificaciones Tiempo Real (WebSocket/SSE) | PI (polling) | CV (toast) | Opcional P2; polling actual funcional | P2 | INC-05 (opcional) |
| FE-08 | Acciones Rápidas Contextuales | CV (API) | PI | Componente por rol/estado en V-04/V-08 | P1 | INC-06 |
| FE-09 | Filtros Dinámicos (estado, fecha, carrera, modalidad) | CV (parámetros query) | PI | UI filtros en dashboards/bandejas | P1 | INC-07 |
| FE-10 | Microinteracciones (skeleton, transiciones, hover) | NA | CV (libs) | Framer Motion, TanStack Query, CSS tokens | - | F2.5/F3 |
| **SESESIONES Y USUARIOS ACTIVOS** |
| SES-01 | Registro sesiones verificable (tabla `SesionUsuario`) | PI | NA | Middleware actualiza último acceso; UUID sesión, user, inicio, última actividad, expiración, revocación, estado | P1 | INC-02 |
| SES-02 | Métricas: usuarios registrados/habilitados/login hoy/activos 15min/sesiones vigentes/revocadas | PI | PI | Queries sobre `SesionUsuario` + `User` + auditoría | P1 | INC-02 |
| SES-03 | Revocación tokens en logout (blocklist) | PI | NA | `token_blacklist` app + endpoint `/auth/logout/` | P1 | INC-02 |
| SES-04 | Expiración refresh por inactividad (sliding window) | PI | NA | `SLIDING_TOKEN_LIFETIME` + `SLIDING_TOKEN_REFRESH_LIFETIME` | P1 | INC-02 |
| **CONTRATOS API** |
| API-01 | Endpoints modalidades (4) | PI | BL | Ver MOD-01 a MOD-05 | P0 | INC-03 |
| API-02 | Endpoints KPIs/Dashboard (5) | PI | PI | Ver KPI-01 a KPI-04 | P0 | INC-04 |
| API-03 | Búsqueda universal (1) | PI | PI | Ver FE-05 | P1 | INC-05 |
| API-04 | Exportaciones (1 genérico) | PI | PI | Ver FE-06 | P1 | INC-05 |
| API-05 | Sesiones/Logout (3) | PI | NA | Ver SES-01 a SES-04 | P1 | INC-02 |
| API-06 | CSP Report (1) | PI | NA | Ver SEC-07 | P1 | INC-05 |
| API-07 | Validación contratos OpenAPI vs código real | CV | CV | Verificado 2026-11-05; discrepancias documentadas en `clarify.md` INC-13, INC-19, INC-20, INC-21 | - | - |
| **PRUEBAS** |
| TEST-01 | Suite backend 497 tests pasando | CV | NA | Cobertura 93%; 13 fallos `pypdf` (deuda entorno) | - | - |
| TEST-02 | Tests seguridad: IDOR (13), RBAC (30), State Machine (32), PDF (42), Concurrencia (2), Auditoría IP (4), Throttling (4) | CV | NA | Ver `INFORME_TECNICO_AUDITORIA_SEGURIDAD.md` §J | - | - |
| TEST-03 | Tests frontend 170+ UI Kit + 81 Auth + 24 F0/F1 | CV | CV | axe 0 violaciones; cobertura ≥85% auth/api | - | - |
| TEST-04 | Tests modalidades (nuevos) | PI | PI | Elegibilidad, cambio autorizado/no, historial, KPIs | P0 | INC-03/04 |
| TEST-05 | Tests integración E2E flujos completos | PI | PI | Cypress/Playwright | P0 | INC-09 |
| TEST-06 | Stress testing (Locust) | PI | NA | 50 concurrentes `enviar_expediente`, 100 `cargar_documento` | P0 | INC-09 |
| TEST-07 | Penetration testing / Fuzzing | PI | NA | OWASP ZAP / nikto en CI/CD | P3 | Futuro |

---

## RESUMEN ESTADÍSTICO

| Estado | Backend | Frontend | Total |
|--------|---------|----------|-------|
| **CV** | 18 | 8 | 26 |
| **IP** | 12 | 14 | 26 |
| **PI** | 28 | 8 | 36 |
| **BL** | 0 | 5 | 5 |
| **NA** | 2 | 2 | 4 |
| **TOTAL** | **60** | **37** | **97** |

**Brechas críticas (P0): 12** — 7 Seguridad + 5 Modalidades  
**Brechas altas (P1): 18** — 4 Seguridad + 3 KPIs + 7 Dashboards + 4 Frontend  
**Bloqueadas por dependencias: 5** — Todas en Frontend (modalidades, BE-06/BE-10)

---

## OBSERVACIONES CLAVE

1. **Modalidades de titulación son el bloqueante transversal único**: Afectan modelo, reglas, endpoints, KPIs, dashboards, frontend V-03/V-04/V-08. Sin BE-06 autorizado, todo lo relacionado está **BLOQUEADO** en frontend.

2. **Seguridad P0 (INC-01) es prerrequisito de confianza** para cualquier integración frontend-backend en producción.

3. **7 KPIs "no implementables" no son deuda técnica**: Son dependencias reales de modelos/datos que no existen (tutoría, sustentación, catálogo carreras, período académico, definición "abandonado", sesiones JWT). **No se deben simular** (CA-G-01).

4. **Frontend F0-F2.5 completado al 95%**: Solo faltan V-05/V-06/V-07/V-08 (stubs) y integración modalidades/búsqueda/exportación. Base técnica sólida (React+TS+Vite, TanStack Query, MSW, UI Kit accesible).

5. **Backend maduro para consumo**: 23 endpoints operativos, RBAC probado, validación estricta, auditoría inmutable. Único gap funcional crítico: FirmaEC en declaratoria.