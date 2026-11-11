# MATRIZ DE ACCIONES RÁPIDAS POR ROL — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` + `ARQUITECTURA_DASHBOARDS_POR_ROL.md` + `specs/003-frontend-titulacion/specify.md`  

---

## 1. DEFINICIÓN

**Acciones Rápidas:** Botones/atajos contextuales en dashboards y vistas de detalle que ejecutan la operación más frecuente del rol sin navegación intermedia. Respetan RBAC server-side; frontend solo muestra si el rol tiene permiso en la matriz.

**Ubicaciones:**
- Dashboard (`/estudiante`, `/bandeja`): Tarjetas P0 + barra superior
- Detalle expediente (`/expedientes/:id`, `/bandeja/:id`): Header + barra acciones
- Tablas de trabajo: Columna "Acciones" por fila

---

## 2. MATRIZ ACCIONES RÁPIDAS × ROL × CONTEXTO

| Acción | Endpoint | Método | ESTUDIANTE | SECRETARIA_CARRERA | SECRETARIO_ABOGADO | ANALISTA_APOYO | DECANO | DIRECTOR_CARRERA | RESPONSABLE_DEPENDENCIA | ADMINISTRADOR |
|--------|----------|--------|------------|-------------------|-------------------|----------------|--------|------------------|------------------------|---------------|
| **Crear solicitud** | `/expedientes/` | POST | ✅ (V-02, V-03) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Ver mi expediente** | `/expedientes/{id}/` | GET | ✅ (own) | ❌ | ✅ (facultad) | ✅ (facultad) | ✅ (facultad) | ✅ (carrera) | ❌ | ✅ (all) |
| **Enviar expediente** | `/expedientes/{id}/enviar/` | POST | ✅ (BORRADOR) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Solicitar emisión** | `/peticiones/{id}/solicitar-emision/` | POST | ✅ (PENDIENTE) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Cargar documento** | `/peticiones/{id}/documento/` | POST | ✅ (SOLICITADO) | ✅ (asignado) | ✅ (asignado) | ✅ (asignado) | ❌ | ✅ (asignado) | ✅ (asignado) | ✅ |
| **Descargar documento** | `/peticiones/{id}/documento/` | GET | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Evaluar checklist** | `/checklist/{id}/` | PUT | ❌ | ❌ | ✅ (PENDIENTE) | ✅ (borrador) | ❌ | ❌ | ❌ | ✅ |
| **Observar expediente** | `/expedientes/{id}/observar/` | POST | ❌ | ❌ | ✅ (EN_VERIFICACION) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Subsanar requisito** | `/checklist/{id}/subsanar/` | POST | ✅ (own, OBSERVADO) | ✅ (asignado) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Emitir informe** | `/informes/` | POST | ❌ | ❌ | ✅ (100% VERIFICADO) | ✅ (borrador) | ❌ | ❌ | ❌ | ❌ |
| **Declarar aptitud** | `/declaratorias/` | POST | ❌ | ❌ | ❌ | ❌ | ✅ (INFORME_EMITIDO) | ❌ | ❌ | ❌ |
| **Verificar elegibilidad EC** | `/expedientes/{id}/modalidad/elegibilidad/` | GET | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Autorizar cambio EC** | `/expedientes/{id}/modalidad/cambiar/` | POST | ❌ | ❌ | ✅ (verifica) | ❌ | ✅ (autoriza) | ❌ | ❌ | ✅ |
| **Gestionar usuarios/roles** | `/admin/` + API usuarios | Varios | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Ver auditoría** | `/api/v1/auditoria/` | GET | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**Leyenda:** ✅ = Permitido (matriz RBAC + estado válido) | ❌ = Denegado | (estado) = Condición de estado expediente/petición | (own/asignado/facultad/carrera/all) = Scope RBAC

---

## 3. ACCIONES RÁPIDAS POR VISTA

### 3.1 V-02 Dashboard Estudiante (`/estudiante`)

| Tarjeta/Sección | Acción Rápida | Endpoint | Condición |
|-----------------|---------------|----------|-----------|
| **Estado expediente** | "Ver expediente" | `GET /expedientes/{id}/` | Tiene expediente activo |
| **Estado expediente** | "Crear solicitud" | `POST /expedientes/` → V-03 | Sin expediente activo |
| **Requisitos pendientes** | "Ver peticiones" | Navega `/expedientes/{id}/peticiones` (V-05) | Tiene peticiones PENDIENTE/SOLICITADO |
| **Observados** | "Subsanar" | `POST /checklist/{id}/subsanar/` (desde V-04) | Tiene observaciones no resueltas |
| **Notificaciones** | "Marcar leída" | `PATCH /notificaciones/{id}/marcar-leida/` | Tiene no leídas |
| **Notificaciones** | "Ver todas" | Navega lista notificaciones | — |
| **Accesos rápidos** | "Volver a EXP-2026-0031" | `GET /expedientes/{id}/` | Historial local (sessionStorage) |
| **Modalidad** | "Verificar elegibilidad EC" | `GET /expedientes/{id}/modalidad/elegibilidad/` | Modalidad actual = TIC |

### 3.2 V-04 Detalle Expediente (`/expedientes/:id`) — Estudiante

| Barra Acciones | Acción | Endpoint | Condición |
|----------------|--------|----------|-----------|
| **Principal** | Enviar expediente | `POST /expedientes/{id}/enviar/` | Estado = BORRADOR + 5 docs vigentes |
| **Secundaria** | Ver peticiones | Navega V-05 | Siempre |
| **Secundaria** | Descargar documento | `GET /peticiones/{id}/documento/` | Tiene documentos |
| **Modalidad** | Ver modalidad actual | Solo lectura (badge) | Siempre |
| **Modalidad** | Verificar elegibilidad EC | `GET /expedientes/{id}/modalidad/elegibilidad/` | Modalidad = TIC |

### 3.3 V-05 Peticiones (`/expedientes/:id/peticiones`) — Estudiante

| Fila Petición | Acción | Endpoint | Condición |
|---------------|--------|----------|-----------|
| **PENDIENTE** | Solicitar emisión | `POST /peticiones/{id}/solicitar-emision/` | Rol = ESTUDIANTE |
| **SOLICITADO** | Cargar documento | `POST /peticiones/{id}/documento/` (FileUpload) | Rol autorizado |
| **OBSERVADO** | Subsanar | `POST /checklist/{id}/subsanar/` (desde checklist V-04) | Rol = ESTUDIANTE + own |
| **Cualquiera** | Descargar vigente | `GET /peticiones/{id}/documento/` | Rol autorizado |
| **Cualquiera** | Descargar versión N | `GET /peticiones/{id}/documento/{version}/` | Rol autorizado |

### 3.4 V-07 Bandeja Funcionario (`/bandeja`) — Secretaría Carrera

| Fila Expediente | Acción Rápida | Endpoint | Condición |
|-----------------|---------------|----------|-----------|
| **Cualquiera** | Ver detalle | `GET /expedientes/{id}/` → V-08 | Siempre |
| **ENVIADA/EN_VERIFICACION/OBSERVADA** | Emitir certificado | `POST /peticiones/{id}/documento/` (desde V-08) | `dependencia_emisora=SECRETARIA_CARRERA` |
| **Plazo vencido** | ⚠️ Badge rojo | Solo visual | `fecha_limite_atencion < hoy` |

### 3.5 V-08 Detalle Funcionario (`/bandeja/:id`) — Secretario Abogado

| Sección | Acción Rápida | Endpoint | Condición |
|---------|---------------|----------|-----------|
| **Header** | Observar expediente | `POST /expedientes/{id}/observar/` | Estado = EN_VERIFICACION |
| **Header** | Emitir informe | `POST /informes/` | Estado = EN_VERIFICACION + checklist 100% VERIFICADO |
| **Checklist fila** | Verificar | `PUT /checklist/{id}/` {estado: VERIFICADO} | Estado item = PENDIENTE |
| **Checklist fila** | Observar item | `PUT /checklist/{id}/` {estado: OBSERVADO, motivo} | Estado item = PENDIENTE |
| **Checklist fila** | Subsanar (estudiante) | `POST /checklist/{id}/subsanar/` | Estado item = OBSERVADO + own/asignado |
| **Modalidad** | Verificar elegibilidad EC | `GET /expedientes/{id}/modalidad/elegibilidad/` | Modalidad actual = TIC |
| **Modalidad** | Autorizar cambio a EC | `POST /expedientes/{id}/modalidad/cambiar/` | Elegible EC confirmada + justificación |

### 3.6 V-08 Detalle Funcionario — Decano

| Sección | Acción Rápida | Endpoint | Condición |
|---------|---------------|----------|-----------|
| **Header** | Declarar aptitud | `POST /declaratorias/` (multipart: memorando) | Estado = INFORME_EMITIDO |
| **Header** | Ver informe | `GET /expedientes/{id}/` (incluye informe) | Estado = INFORME_EMITIDO |
| **Modalidad** | Cambiar modalidad a EC | `POST /expedientes/{id}/modalidad/cambiar/` | Autorización final (tras verificación Secretario) |

### 3.7 V-08 Detalle Funcionario — Responsable Dependencia

| Fila Petición | Acción Rápida | Endpoint | Condición |
|---------------|---------------|----------|-----------|
| **SOLICITADO** | Cargar documento | `POST /peticiones/{id}/documento/` | `dependencia_emisora` = mi rol |
| **OBSERVADO** | Corregir documento | `POST /peticiones/{id}/documento/` (nueva versión) | `dependencia_emisora` = mi rol |
| **Cualquiera** | Descargar | `GET /peticiones/{id}/documento/` | `dependencia_emisora` = mi rol |

---

## 4. COMPONENTE FRONTEND: `AccionesRapidas`

### 4.1 Props
```tsx
interface AccionesRapidasProps {
  rol: string;                    // Rol principal del usuario
  contexto: 'dashboard' | 'expediente-detalle' | 'peticiones' | 'bandeja' | 'funcionario-detalle';
  entidad: ExpedienteDetalle | PeticionDocumental | ChecklistItem | null; // Entidad contextual
  permisos: string[];             // Acciones permitidas por RBAC (calculadas en frontend)
  onAccion: (accion: string, payload?: any) => Promise<void>; // Handler mutaciones
}
```

### 4.2 Lógica de Visualización
```typescript
function getAccionesRapidas(props: AccionesRapidasProps): AccionRapida[] {
  const { rol, contexto, entidad, permisos } = props;
  const acciones: AccionRapida[] = [];
  
  // Reglas por rol + contexto + estado entidad
  if (contexto === 'dashboard' && rol === 'ESTUDIANTE') {
    if (entidad?.estado === 'BORRADOR') {
      acciones.push({ key: 'enviar', label: 'Enviar expediente', variant: 'primary', endpoint: 'enviarExpediente' });
    }
    if (!entidad) {
      acciones.push({ key: 'crear', label: 'Crear solicitud', variant: 'primary', endpoint: 'crearExpediente' });
    }
  }
  
  if (contexto === 'expediente-detalle') {
    if (rol === 'ESTUDIANTE' && entidad?.estado === 'BORRADOR') {
      acciones.push({ key: 'enviar', label: 'Enviar', variant: 'primary' });
    }
    if (rol === 'SECRETARIO_ABOGADO' && entidad?.estado === 'EN_VERIFICACION') {
      acciones.push({ key: 'observar', label: 'Observar', variant: 'warning' });
      if (esChecklistCompleto(entidad)) {
        acciones.push({ key: 'informe', label: 'Emitir informe', variant: 'primary' });
      }
    }
    if (rol === 'DECANO' && entidad?.estado === 'INFORME_EMITIDO') {
      acciones.push({ key: 'declarar', label: 'Declarar aptitud', variant: 'primary' });
    }
    // Modalidad (transversal)
    if (entidad?.opcion_titulacion === 'TIC' && ['SECRETARIO_ABOGADO', 'DECANO', 'ADMINISTRADOR'].includes(rol)) {
      acciones.push({ key: 'elegibilidad-ec', label: 'Verificar elegibilidad EC', variant: 'secondary' });
    }
  }
  
  // Filtrar por permisos reales (frontend helper, server es autoridad)
  return acciones.filter(a => permisos.includes(a.key));
}
```

### 4.3 Integración en Vistas
```tsx
// StudentDashboardPage.tsx
<AccionesRapidas 
  rol={auth.user.roles[0]} 
  contexto="dashboard" 
  entidad={expedienteActivo} 
  permisos={calcularPermisosEstudiante(expedienteActivo)}
  onAccion={handleAccionRapida}
/>

// ExpedientePage.tsx (header)
<AccionesRapidas 
  rol={auth.user.roles[0]} 
  contexto="expediente-detalle" 
  entidad={expediente} 
  permisos={calcularPermisosExpediente(expediente, auth.user.roles)}
  onAccion={handleAccionRapida}
/>
```

---

## 5. PERMISOS FRONTEND (HELPERS)

```typescript
// frontend/src/features/expediente/permisos.ts

export function calcularPermisosEstudiante(expediente?: ExpedienteDetalle): string[] {
  const permisos = ['ver-expediente', 'crear-solicitud'];
  if (expediente) {
    if (expediente.estado === 'BORRADOR') permisos.push('enviar-expediente');
    if (expediente.peticiones.some(p => ['PENDIENTE', 'SOLICITADO'].includes(p.estado_peticion))) {
      permisos.push('solicitar-emision', 'cargar-documento');
    }
    if (expediente.peticiones.some(p => p.estado_peticion === 'OBSERVADO')) {
      permisos.push('subsanar');
    }
  }
  return permisos;
}

export function calcularPermisosExpediente(expediente: ExpedienteDetalle, roles: string[]): string[] {
  const permisos: string[] = [];
  const esSecretario = roles.includes('SECRETARIO_ABOGADO');
  const esAnalista = roles.includes('ANALISTA_APOYO');
  const esDecano = roles.includes('DECANO');
  const esSecretaria = roles.includes('SECRETARIA_CARRERA');
  const esDirector = roles.includes('DIRECTOR_CARRERA');
  const esAdmin = roles.includes('ADMINISTRADOR');
  const esResponsable = roles.includes('RESPONSABLE_DEPENDENCIA');
  const esEstudiante = roles.includes('ESTUDIANTE');
  
  // Comunes
  permisos.push('ver-expediente', 'descargar-documento');
  
  if (esEstudiante) {
    if (expediente.estado === 'BORRADOR') permisos.push('enviar-expediente');
    if (expediente.peticiones.some(p => ['PENDIENTE', 'SOLICITADO'].includes(p.estado_peticion))) {
      permisos.push('solicitar-emision', 'cargar-documento');
    }
  }
  
  if (esSecretario) {
    if (expediente.estado === 'EN_VERIFICACION') {
      permisos.push('observar-expediente', 'evaluar-checklist');
      if (esChecklistCompleto(expediente)) permisos.push('emitir-informe');
    }
  }
  
  if (esAnalista) {
    if (expediente.estado === 'EN_VERIFICACION') {
      permisos.push('evaluar-checklist-borrador', 'emitir-informe-borrador');
    }
  }
  
  if (esDecano) {
    if (expediente.estado === 'INFORME_EMITIDO') permisos.push('declarar-aptitud');
  }
  
  if (esSecretaria || esDirector || esResponsable) {
    permisos.push('cargar-documento'); // En peticiones asignadas
  }
  
  if (esAdmin) {
    permisos.push('*'); // Todos (server valida)
  }
  
  // Modalidad (transversal)
  if (expediente.opcion_titulacion === 'TIC' && (esSecretario || esDecano || esAdmin)) {
    permisos.push('verificar-elegibilidad-ec', 'cambiar-modalidad');
  }
  
  return permisos;
}

function esChecklistCompleto(expediente: ExpedienteDetalle): boolean {
  // Requiere checklist cargado (query separada) — simplificado aquí
  return expediente.peticiones.every(p => ['CARGADO', 'LEGALIZADO', 'VERIFICADO'].includes(p.estado_peticion));
}
```

---

## 6. ESTADO ACTUAL IMPLEMENTACIÓN

| Componente | Estado | Archivo |
|------------|--------|---------|
| `AccionesRapidas` (dashboard estudiante) | ✅ Hecha | `features/dashboard/AccesosRapidos.tsx` (básico, solo historial local) |
| `AccionesRapidas` (expediente detalle) | ❌ No existe | Pendiente INC-06-T01 / INC-07 |
| `AccionesRapidas` (funcionario detalle) | ❌ No existe | Pendiente INC-07 |
| Helpers permisos por rol/estado | ⚠️ Parcial | `features/expediente/accionesPorRolEstado.ts` (solo lectura, sin modalidad) |
| Integración modalidad en acciones | ❌ No existe | Pendiente INC-08 |
| Botones exportación en acciones | ❌ No existe | Pendiente INC-06-T02 |

---

## 7. PRÓXIMOS PASOS (INC-06 / INC-07 / INC-08)

1. **INC-06-T01:** Crear `AccionesRapidas.tsx` genérico + helpers permisos completos (con modalidad)
2. **INC-06-T02:** Añadir `ExportButton` en `AccionesRapidas` (contexto dashboards/tablas)
3. **INC-07:** Integrar en V-04, V-05, V-07, V-08 (reemplazar botones hardcodeados)
4. **INC-08:** Añadir acciones modalidad: "Verificar elegibilidad EC" (Secretario), "Cambiar modalidad" (Decano)
5. **Tests:** RTL + axe para cada variante rol/contexto/estado

---

## 8. DEPENDENCIAS BACKEND

| Acción | Endpoint | Estado Backend | Notas |
|--------|----------|----------------|-------|
| Verificar elegibilidad EC | `GET /expedientes/{id}/modalidad/elegibilidad/` | PI (INC-03) | Requiere mock SGA |
| Cambiar modalidad | `POST /expedientes/{id}/modalidad/cambiar/` | PI (INC-03) | Requiere justificación + evidencia |
| Exportar PDF/Excel/CSV | `GET /api/v1/exportar/` | PI (INC-05) | Genérico con filtros |
| Búsqueda universal | `GET /api/v1/buscar/` | PI (INC-05) | Requiere índice trigram/tsvector |

---

## 9. OBSERVACIONES

1. **Frontend nunca decide permisos**: `AccionesRapidas` usa helpers para **UX only**; server (RBAC + ScopeFilterMixin) es autoridad final.
2. **Modalidad transversal**: Acciones "Verificar elegibilidad" y "Cambiar modalidad" aparecen en **todos los contextos** donde el rol tiene permiso (Secretario, Decano, Admin).
3. **Estudiante nunca ve "Cambiar modalidad"**: EC solo habilitada por backend tras verificación elegibilidad.
4. **Acciones rápidas ≠ Acciones completas**: En V-08 (detalle funcionario) hay formularios completos (observar, evaluar, informe, declaratoria) que no son "rápidas" sino flujos guiados.
5. **Exportación**: Botón "Exportar" en `AccionesRapidas` de dashboards/tablas → abre modal con opciones formato + filtros → llama `/api/v1/exportar/`.