# Especificación Funcional — Frontend de Titulación (SGT-SIAAF)

**Feature ID:** `003-frontend-titulacion`
**Documento:** `specify.md`
**Versión:** 1.1.0
**Fecha:** 2026-11-04
**Estado:** Especificación aprobada para planificación; refactorizada tras auditoría de prototipos (2026-11-04): correspondencia numeración UI↔SDD (§6.1), clarificación V-03 (§9.2), estados de error (§9.3). F0 del frontend está parcialmente implementado (ver `clarify.md` CL-21); la especificación funcional no cambia por eso.
**Autoridad:** Subordinada a la constitución, a la normativa institucional y al Reglamento de Régimen Académico UNL (RRA-UNL), a `specs/001-tramite-titulacion/specify.md`, a los ADRs y al contrato OpenAPI.
**Naturaleza:** Documento de especificación. **No contiene código de implementación.**

---

## 1. Resumen ejecutivo

Se especifica el frontend del Sistema de Gestión del Trámite de Titulación (SGT-SIAAF) para la Facultad de Ingeniería en Ciencias de la Tierra (FEIRNNR) de la Universidad Nacional de Loja. El frontend es una SPA en **React + TypeScript + Vite** que consume la API REST existente en `/api/v1/` mediante autenticación **JWT local**.

El alcance cubre **9 vistas**: login, dashboard del estudiante, creación de solicitud, expediente y requisitos, gestión de peticiones documentales, seguimiento de peticiones, bandeja del funcionario, detalle del funcionario y estado no habilitado.

La especificación es **honesta sobre las limitaciones del backend actual**: varias vistas no pueden completarse porque faltan endpoints, campos, catálogos o permisos. Esas limitaciones se documentan como estados de "no habilitado" y se registran como dependencias de backend (`B-01…B-10` / `BE-01…BE-10`), **no se simulan con datos falsos**.

---

## 2. Alcance

### 2.1 Dentro del alcance

- Autenticación local JWT y cierre de sesión local.
- Navegación y guardas por rol.
- Las 9 vistas, con sus estados de carga, vacío, error, éxito y no habilitado.
- dentro de cada vista deve de haber un boton para regresar a la vista anterior, esto aplica para todas las vista
- Consumo de los endpoints existentes, sin modificarlos.
- Carga y descarga de PDF.
- Notificaciones internas (listado y marcar leída).
- Accesibilidad WCAG 2.1 AA, responsive y manejo de errores.
- Pruebas unitarias, de integración y de contrato con MSW.
- Trazabilidad a requisitos, endpoints y tareas.

### 2.2 Fuera del alcance

- Backend, migraciones, modelos, serializers, views, permisos, settings, OpenAPI o contratos.
- Constitución, `specs/001-tramite-titulacion/` y cualquier documento preexistente.
- SAC, OAuth2, OIDC, TOTP, QR, firma electrónica en frontend.
- Endpoints nuevos o datos simulados que aparenten ser reales.
- Despliegue, CI/CD, contenedores.
- La "feature 002 demo" (no existe en el repositorio).
- Funcionalidades de `CANCELADA`, `LEGALIZADO` o `RESPONSABLE_DEPENDENCIA` como si estuvieran operativas.

---

## 3. Fuentes y trazabilidad

| Fuente | Uso | ¿Normativa? |
|--------|-----|-------------|
| `.specify/memory/constitution.md` | Principios `P-01…P-18` | Sí |
| `specs/001-tramite-titulacion/specify.md` | RF, RNF, RN, EX, CA, RBAC | Sí |
| `backend/docs/adr/` | Decisiones de arquitectura | Sí |
| `backend/openapi.yaml` | Contrato de endpoints y esquemas | Sí (sujeto a código real) |
| `backend/src/apps/**` | Comportamiento real | Sí (prevalece sobre OpenAPI si difiere) |
| `diseno-ui/ui/titulacion-v2/especificaciones/01…07_*.md` | Referencia visual/UX | No |
| `diseno-ui/ui/titulacion-v2/eferencias-visuales/00…09*` | Referencia visual | No |
| `diseno-ui/ui/titulacion-v2/GUIA_VISTAS_TITULACION.md` | Guía de vistas | No |
| `prototipos/prototipo-general/` (prototipo A) | Referencia visual y de comportamiento, no normativa (DEC-11). Sus datos, flujos y paleta son demostrativos; **no** modera requisitos ni contratos. | No |
| `prototipos/vistas-errores-unl/` (prototipo B) | Referencia visual de estados de error; los HTTP 409/412/428 son **escenarios propuestos** condicionados a BE-11 (DEC-13). | No |
| Reglamento de Régimen Académico UNL (RRA-UNL) | Fuente normativa de modalidades/elegibilidad de titulación (arts. 39, 40, 212, 216, 233 según referencias preliminares). Las síntesis de análisis externas (p. ej. NotebookLM) son referencias secundarias que deben contrastarse con el texto vigente. | Sí (pendiente de contrastación directa: PQ-13) |

---

## 4. Actores y permisos confirmados

### 4.1 Roles

| Rol | Código | Vistas principales | Observación |
|-----|--------|--------------------|-------------|
| Estudiante | `ESTUDIANTE` | V-01, V-02, V-03, V-04, V-05, V-06, V-09 | Único rol que crea expedientes y solicita emisión. |
| Secretaria de Carrera | `SECRETARIA_CARRERA` | V-01, V-07, V-08, V-09 | Sin expedientes en bandeja; actúa sobre peticiones/documentos. |
| Secretario/a-Abogado/a | `SECRETARIO_ABOGADO` | V-01, V-07, V-08, V-09 | Evalúa checklist, observa, emite informe. |
| Analista de Apoyo | `ANALISTA_APOYO` | V-01, V-07, V-08, V-09 | Evalúa checklist en borrador, emite informe. |
| Decano/a | `DECANO` | V-01, V-07, V-08, V-09 | Declara aptitud; bandeja en `INFORME_EMITIDO`. |
| Director de Carrera | `DIRECTOR_CARRERA` | V-01, V-07, V-08, V-09 | Sin expedientes en bandeja; alcance de carrera. |
| Administrador | `ADMINISTRADOR` | V-01, V-07, V-08, V-09 | Acceso amplio; no es un rol operativo del trámite. |
| Responsable de Dependencia | `RESPONSABLE_DEPENDENCIA` | — | **No soportado**: aparece en el enum, sin celdas RBAC. |

### 4.2 Matriz resumida de operaciones del frontend

| Operación | Endpoint | Roles confirmados |
|-----------|----------|-------------------|
| Login | `POST /api/v1/auth/token/` | Público (credenciales válidas) |
| Crear expediente | `POST /api/v1/expedientes/` | `ESTUDIANTE`, `ADMINISTRADOR` |
| Ver expediente | `GET /api/v1/expedientes/{id}/` | Todos con alcance (own/carrera/facultad/asignado/allow) |
| Enviar expediente | `POST /api/v1/expedientes/{id}/enviar/` | `ESTUDIANTE` (own) |
| Observar expediente | `POST /api/v1/expedientes/{id}/observar/` | `SECRETARIO_ABOGADO` |
| Bandeja | `GET /api/v1/expedientes/bandeja/` | Todos los roles con estados asignados |
| Ver checklist | `GET /api/v1/expedientes/{id}/checklist/` | `SECRETARIO_ABOGADO`, `ANALISTA_APOYO`, `ADMINISTRADOR` |
| Evaluar checklist | `PUT /api/v1/checklist/{id}/` | `SECRETARIO_ABOGADO`, `ANALISTA_APOYO` (borrador), `ADMINISTRADOR` |
| Subsanar requisito | `POST /api/v1/checklist/{id}/subsanar/` | `ESTUDIANTE` (own), `SECRETARIA_CARRERA`, `ADMINISTRADOR` |
| Solicitar emisión | `POST /api/v1/peticiones/{id}/solicitar-emision/` | `ESTUDIANTE` (own), `ADMINISTRADOR` |
| Cargar documento | `POST /api/v1/peticiones/{id}/documento/` | `ESTUDIANTE`, `SECRETARIA_CARRERA`, `SECRETARIO_ABOGADO`, `ANALISTA_APOYO`, `DIRECTOR_CARRERA`, `ADMINISTRADOR` |
| Descargar documento | `GET /api/v1/peticiones/{id}/documento/` y `/{version}/` | Mismos que carga (excepto `DECANO`) |
| Emitir informe | `POST /api/v1/informes/` | `SECRETARIO_ABOGADO`, `ANALISTA_APOYO` |
| Declarar aptitud | `POST /api/v1/declaratorias/` | `DECANO` |
| Notificaciones | `GET /api/v1/notificaciones/` | Todos con alcance |
| Marcar leída | `PATCH /api/v1/notificaciones/{id}/marcar-leida/` | Todos con alcance |

> La autorización real es **server-side**. Las guardas del frontend son UX, no seguridad.

---

## 5. Estados y enums

### 5.1 Estado del expediente

| Estado | ¿Se produce en el flujo real? | Uso en UI |
|--------|-------------------------------|-----------|
| `BORRADOR` | Sí | Badge neutro; acciones de edición/envío. |
| `ENVIADA` | Sí | Badge informativo; espera de verificación. |
| `EN_VERIFICACION` | Sí | Badge en proceso; checklist. |
| `OBSERVADA` | Sí | Badge de advertencia; subsanación. |
| `INFORME_EMITIDO` | Sí | Badge informativo; declaratoria (Decano). |
| `DECLARADA_APTA` | Sí | Badge de éxito; solo lectura. |
| `CANCELADA` | **No** | Badge soportado si el backend lo devuelve; sin acción de UI. |

### 5.2 Estado de la petición

| Estado | ¿Se produce en el flujo real? | Uso en UI |
|--------|-------------------------------|-----------|
| `PENDIENTE` | Sí | Badge neutro; solicitar emisión. |
| `SOLICITADO` | Sí | Badge informativo; espera de carga. |
| `CARGADO` | Sí | Badge en proceso; verificar. |
| `VERIFICADO` | Sí | Badge de éxito. |
| `OBSERVADO` | Sí | Badge de advertencia; corregir. |
| `LEGALIZADO` | **No** | Badge soportado si el backend lo devuelve; sin acción de UI. |

### 5.3 Estado de verificación del checklist

`PENDIENTE`, `VERIFICADO`, `OBSERVADO`.

### 5.4 Dependencia emisora

`ESTUDIANTE`, `SECRETARIA_CARRERA`, `SECRETARIO_ABOGADO`, `ANALISTA_APOYO`, `DECANO`, `DIRECTOR_CARRERA`, `RESPONSABLE_DEPENDENCIA`, `ADMINISTRADOR`.

> `RESPONSABLE_DEPENDENCIA` se tipa pero no se usa en guardas ni se ofrece como acción.

---

## 6. Rutas y navegación

| Ruta | Vista | Guarda | Redirección si no autorizado |
|------|-------|--------|------------------------------|
| `/login` | V-01 | Pública (si hay sesión, redirige al inicio por rol) | — |
| `/` | Redirección | Autenticada | `/login` |
| `/estudiante` | V-02 | `ESTUDIANTE` | `/bandeja` o `/no-habilitado` |
| `/estudiante/solicitud/nueva` | V-03 | `ESTUDIANTE` | `/no-habilitado` |
| `/expedientes/:id` | V-04 | Autenticada + alcance | `/no-habilitado` (403) / `/404` |
| `/expedientes/:id/peticiones` | V-05 | Autenticada + alcance | `/no-habilitado` |
| `/expedientes/:id/peticiones/:peticionId` | V-06 | Autenticada + alcance | `/no-habilitado` |
| `/bandeja` | V-07 | Roles operativos | `/no-habilitado` |
| `/bandeja/:id` | V-08 | Roles operativos | `/no-habilitado` |
| `/no-habilitado` | V-09 | Autenticada | `/login` |
| `*` | 404 | — | — |

**Redirección post-login por rol** (si hay varios roles, se aplica el primero de la lista):
`ADMINISTRADOR` → `/bandeja`; `SECRETARIO_ABOGADO` → `/bandeja`; `ANALISTA_APOYO` → `/bandeja`; `DECANO` → `/bandeja`; `SECRETARIA_CARRERA` → `/bandeja`; `DIRECTOR_CARRERA` → `/bandeja`; `ESTUDIANTE` → `/estudiante`.

### 6.1 Correspondencia numeración UI ↔ numeración oficial (DEC-12)

Los prototipos (A y B) y la documentación visual usan UI-01…UI-09. La numeración oficial es la de esta especificación. Tabla de correspondencia (mismo contenido, etiquetas distintas):

| UI (prototipos/documentos visuales) | Nombre en documentos visuales | ID oficial SDD | Ruta oficial | Archivo de referencia prototipo A |
|---|---|---|---|---|
| **UI-01** | Acceso / Inicio de sesión | **V-01** | `/login` | `prototipos/prototipo-general/index.html` → `accessPage()` (app.js) |
| **UI-02** | Estudiante no habilitado | **V-09** | `/no-habilitado` | `index.html` → `undergradPage()` |
| **UI-03** | Dashboard del estudiante | **V-02** | `/estudiante` | `index.html` → `dashboard()` |
| **UI-04** | Crear solicitud | **V-03** | `/estudiante/solicitud/nueva` | `index.html` → `createApplication()` (wizard 3 pasos) |
| **UI-05** | Expediente y requisitos | **V-04** | `/expedientes/:id` | `index.html` → `recordPage()` (+ `historyPage()`, extra no oficial) |
| **UI-06** | Crear petición documental (modal) | **V-05** (lista; sin creación manual) + modal asociado a V-04 | `/expedientes/:id/peticiones` | `index.html` → `modalHtml()` (`dialog='request'`, `choose-request`) |
| **UI-07** | Seguimiento de petición | **V-06** | `/expedientes/:id/peticiones/:peticionId` | `index.html` → `petitionDetail()` (+ página global "Mis peticiones", extra no oficial) |
| **UI-08** | Bandeja del funcionario | **V-07** | `/bandeja` | `index.html` → `staffPage()` |
| **UI-09** | Detalle del funcionario | **V-08** | `/bandeja/:id` | `index.html` → `staffDetail()` |

Kit de errores (prototipo B, común a varias vistas): `paginas/401.html`, `403.html`, `404.html`, `409.html`, `412.html`, `428.html`, `500.html`, `503.html` y `acceso.html` (maqueta visual de V-01 con campos deshabilitados). Ver §9.3.

---

## 7. Requisitos funcionales globales

| ID | Requisito | Prioridad | Criterio de aceptación |
|----|-----------|-----------|------------------------|
| **RFF-001** | Autenticación local JWT contra `POST /api/v1/auth/token/`. | Must | Credenciales válidas → 200 con `access` y `refresh`; inválidas → 401 y mensaje. |
| **RFF-002** | Guardas de ruta por autenticación y rol. | Must | Sin token → `/login`; rol no autorizado → `/no-habilitado`; nunca se muestra contenido protegido. |
| **RFF-003** | Layout con encabezado, navegación por rol, identificador de usuario y cierre de sesión. | Must | Visible en todas las vistas autenticadas; responsive. |
| **RFF-004** | Estados de interfaz homogéneos: `loading`, `empty`, `error`, `success`, `forbidden`, `not-found`. | Must | Cada vista declara y renderiza sus estados; no hay pantallas en blanco. |
| **RFF-005** | Formularios con validación cliente y mensajes en español. | Must | Errores junto al campo; foco en el primer error; sin envío inválido. |
| **RFF-006** | Carga de archivos PDF con validación cliente (MIME/extensión, tamaño ≤ 10 MB, magic bytes `%PDF-`). | Must | Archivo inválido → error local sin llamar a la API; válido → `multipart/form-data`. |
| **RFF-007** | Descarga de documentos con `Authorization` y manejo de `Content-Disposition`. | Must | Archivo se descarga; 404/403 muestran mensaje. |
| **RFF-008** | Notificaciones internas: listar y marcar leída. | Should | Lista paginada; contador de no leídas; `PATCH` actualiza el estado. |
| **RFF-009** | Paginación de bandeja y notificaciones. | Must | Controles anterior/siguiente; `page_size` ≤ 50; no se inventan páginas. |
| **RFF-010** | Modo demostración visible cuando `VITE_DEMO_MODE=true` (P-01). | Should | Banner persistente "Entorno de demostración"; no altera datos. |
| **RFF-011** | Accesibilidad WCAG 2.1 AA. | Must | Navegación por teclado, foco visible, etiquetas, contraste, `aria-live` para errores. |
| **RFF-012** | Diseño responsive (móvil, tablet, escritorio). | Must | Sin scroll horizontal; tablas con vista alternativa en móvil. |
| **RFF-013** | Errores de red con reintento manual y mensaje claro. | Must | Timeout/offline → estado de error con botón "Reintentar". |
| **RFF-014** | Sesión expirada (401) → limpiar sesión y redirigir a login con aviso. | Must | No se reintenta en bucle; no se pierde el borrador local si existe. |
| **RFF-015** | Formato de fechas y estados legible (zona horaria local, badges). | Must | Fechas ISO → `dd/mm/aaaa hh:mm`; estados con etiqueta en español. |
| **RFF-016** | Confirmación explícita en acciones irreversibles o sensibles. | Must | Enviar, observar, evaluar, declarar y cargar documento piden confirmación. |
| **RFF-017** | Manejo diferenciado de 403 y 404. | Must | 403 → "sin permisos"; 404 → "no encontrado"; no se filtran detalles internos. |
| **RFF-018** | Persistencia local de borradores de formulario (no de datos sensibles). | Should | Recargar la página conserva el borrador; se limpia al enviar o cerrar sesión. |
| **RFF-019** | Prohibido simular datos del backend. | Must | Vistas sin soporte muestran V-09 o estado vacío explicativo; nunca datos ficticios. |
| **RFF-020** | Logging seguro sin tokens, contraseñas ni PII. | Must | Consola y reportes de error no contienen `access`, `refresh`, `password` ni cédula completa. |

---

## 8. Requisitos no funcionales

| ID | Requisito | Métrica / verificación |
|----|-----------|------------------------|
| **RNFF-001** | Accesibilidad WCAG 2.1 AA. | Auditoría axe sin errores críticos; navegación completa por teclado. |
| **RNFF-002** | Tokens no se registran ni se exponen en URLs. | Revisión de código; sin `console.log` de tokens; sin query params. |
| **RNFF-003** | Sin secretos en el bundle. | `grep` de claves; solo variables `VITE_*` públicas. |
| **RNFF-004** | Rendimiento aceptable. | LCP < 2.5 s en 3G rápida; bundle inicial < 300 KB gzip (objetivo). |
| **RNFF-005** | Responsive. | 320 px, 768 px, 1024 px, 1440 px sin overflow. |
| **RNFF-006** | Compatibilidad. | Últimas 2 versiones de Chrome, Firefox, Safari y Edge. |
| **RNFF-007** | Testabilidad. | Cobertura ≥ 80% en lógica y componentes críticos; pruebas de integración por vista. |
| **RNFF-008** | Tipado estricto. | `strict: true`; sin `any` implícito; `tsc --noEmit` sin errores. |
| **RNFF-009** | Manejo de errores uniforme. | Un normalizador de errores; mensajes consistentes. |
| **RNFF-010** | Idioma español. | Textos centralizados; sin literales dispersos. |
| **RNFF-011** | Observabilidad sin PII. | Errores con código y contexto técnico, sin datos personales. |
| **RNFF-012** | Mantenibilidad. | Estructura por features; componentes reutilizables; lint sin errores. |
| **RNFF-013** | Contratos estables. | Tipos derivados del OpenAPI/código; cambios documentados. |
| **RNFF-014** | Dependencias justificadas. | Cada dependencia con propósito y alternativa evaluada. |
| **RNFF-015** | Documentación. | README de frontend con variables, scripts y limitaciones. |

---

## 9. Especificaciones de vistas

### 9.1 Catálogo de requisitos específicos por vista

| ID | Requisito | Vista |
|----|-----------|-------|
| **RFF-101** | Formulario de login con `username` y `password`. | V-01 |
| **RFF-102** | Consumir `POST /auth/token/` y validar la respuesta. | V-01 |
| **RFF-103** | Persistir la sesión y decodificar `cedula`/`roles`. | V-01 |
| **RFF-104** | Redirigir por rol tras el login. | V-01 |
| **RFF-105** | Mostrar errores 400/401/403/5xx/red. | V-01 |
| **RFF-106** | Cerrar sesión local. | V-01 |
| **RFF-107** | Avisar de la expiración sin refresh. | V-01 |
| **RFF-201** | Mostrar saludo con la cédula del token. | V-02 |
| **RFF-202** | Listar expedientes del estudiante (`BORRADOR`/`OBSERVADA`). | V-02 |
| **RFF-203** | Mostrar notificaciones no leídas y marcarlas leídas. | V-02 |
| **RFF-204** | Acciones a V-03 y V-04. | V-02 |
| **RFF-205** | Aviso de limitación por falta de perfil/historial. | V-02 |
| **RFF-301** | Formulario de creación con `carrera_id`. | V-03 |
| **RFF-302** | Validar UUID y campos del formulario. | V-03 |
| **RFF-303** | Consumir `POST /expedientes/`. | V-03 |
| **RFF-304** | Manejar 400 (expediente activo/catálogo incompleto). | V-03 |
| **RFF-305** | Redirigir a V-04 tras el éxito. | V-03 |
| **RFF-306** | Bloquear/explicar si no hay catálogo o perfil. | V-03 |
| **RFF-401** | Cargar el detalle del expediente. | V-04 |
| **RFF-402** | Mostrar peticiones anidadas. | V-04 |
| **RFF-403** | Cargar checklist si el rol está autorizado. | V-04 |
| **RFF-404** | Manejar el 403 del checklist como limitación. | V-04 |
| **RFF-405** | Enviar el expediente. | V-04 |
| **RFF-406** | Observar el expediente. | V-04 |
| **RFF-407** | Evaluar checklist. | V-04 |
| **RFF-408** | Subsanar checklist. | V-04 |
| **RFF-409** | Descargar documentos. | V-04 |
| **RFF-410** | Mostrar timeline solo con estados reales. | V-04 |
| **RFF-411** | Refrescar tras mutaciones. | V-04 |
| **RFF-501** | Listar peticiones del expediente. | V-05 |
| **RFF-502** | Solicitar emisión. | V-05 |
| **RFF-503** | Cargar documento PDF. | V-05 |
| **RFF-504** | Validar PDF en cliente. | V-05 |
| **RFF-505** | Manejar 400/403/404. | V-05 |
| **RFF-506** | Explicar que no hay creación manual de peticiones. | V-05 |
| **RFF-601** | Resolver la petición desde el detalle del expediente. | V-06 |
| **RFF-602** | Mostrar estado, dependencia y requisito. | V-06 |
| **RFF-603** | Descargar documento vigente o por versión. | V-06 |
| **RFF-604** | Refrescar y manejar no encontrado. | V-06 |
| **RFF-605** | Explicar la limitación por falta de `GET /peticiones/{id}/`. | V-06 |
| **RFF-701** | Listar bandeja paginada por rol. | V-07 |
| **RFF-702** | Mostrar las columnas requeridas. | V-07 |
| **RFF-703** | Filtros limitados a la página actual. | V-07 |
| **RFF-704** | Navegar a V-08. | V-07 |
| **RFF-705** | Estado vacío por rol sin expedientes. | V-07 |
| **RFF-706** | Manejar 401/403/red. | V-07 |
| **RFF-801** | Cargar detalle y checklist. | V-08 |
| **RFF-802** | Evaluar checklist. | V-08 |
| **RFF-803** | Observar expediente. | V-08 |
| **RFF-804** | Emitir informe. | V-08 |
| **RFF-805** | Declarar aptitud. | V-08 |
| **RFF-806** | Descargar documentos. | V-08 |
| **RFF-807** | Mostrar acciones por rol/estado. | V-08 |
| **RFF-808** | Estado solo lectura tras `DECLARADA_APTA`. | V-08 |
| **RFF-809** | Refrescar tras mutaciones. | V-08 |
| **RFF-901** | Página de estado no habilitado. | V-09 |
| **RFF-902** | Explicar la dependencia `BE-xx`. | V-09 |
| **RFF-903** | Navegación de retorno. | V-09 |
| **RFF-904** | Reutilizable por guardas y vistas parciales. | V-09 |

### V-01 — Login

| Campo | Valor |
|-------|-------|
| **ID** | V-01 |
| **Nombre** | Inicio de sesión |
| **Ruta** | `/login` |
| **Clasificación** | **IF** (funcional) |
| **Actor** | Público |
| **Referencia visual** | `00_login.png` (referencia no normativa) |

**Objetivo.** Permitir que un usuario se autentique con sus credenciales institucionales y obtenga un token JWT local.

**Alcance funcional.**
- Formulario con `username` y `password`.
- Mostrar/ocultar contraseña.
- Estado de carga durante la petición.
- Manejo de credenciales inválidas (401), validación (400) y error de red.
- Persistencia de la sesión y redirección por rol.
- Banner de modo demostración si aplica.
- No hay recuperación de contraseña, registro, SSO ni refresh.

**Endpoint.**
- `POST /api/v1/auth/token/`
  - Request JSON: `{ "username": string, "password": string }`
  - Response 200 (real, SimpleJWT): `{ "access": string, "refresh": string }`
  - Response 401: `{ "detail": "No active account found with the given credentials" }` (mensaje se traduce en UI).
  - El OpenAPI declara "No response body"; **discrepancia documentada (INC-13)**. El cliente tipa la respuesta real.

**Datos y claims.**
- Decodificar el `access` (sin verificar firma en cliente) para leer `cedula` y `roles`.
- Si el token no contiene `roles`, tratar como sesión inválida y mostrar error.
- No hay `nombre`, `carrera` ni `facultad`.

**Reglas de UI.**
- Campos obligatorios; `username` sin espacios al inicio/fin.
- Enter envía el formulario.
- Bloquear doble envío.
- No mostrar si la contraseña es correcta/incorrecta de forma que filtre información.
- Tras login, guardar **solo `access`** en `sessionStorage` (clave `sgt.access`; decisión PQ-06). El `refresh` **se recibe y se descarta**, sin persistirlo, porque no existe endpoint de renovación (BE-03 ausente; `plan.md` §6.2 y FE-T011). Ante la **expiración del access**, la UI avisa y el usuario debe **volver a iniciar sesión**; no hay renovación automática. *(Corrección MOMENTO 2, 2026-11-04: este punto decía "guardar access y refresh" y ha sido corregido por contradecir `plan.md` §6.2, FE-T011 y CL-03/AS-03.)*

**Estados.**
- `idle`, `submitting`, `error` (credenciales, red, servidor), `success`.

**Errores.**
- 400 → mensaje de validación.
- 401 → "Usuario o contraseña incorrectos".
- 403 → "Usuario sin acceso al sistema".
- 5xx → "No se pudo iniciar sesión. Intente nuevamente."
- Red/timeout → "No hay conexión con el servidor".

**Dependencias.** BE-03 (refresh/logout) para sesión prolongada; no bloquea el login.

**Criterios de aceptación.**
- **CA-V01-01** Dado credenciales válidas, cuando envío el formulario, entonces recibo 200, se guarda la sesión y soy redirigido según mi rol.
- **CA-V01-02** Dado credenciales inválidas, cuando envío, entonces veo un mensaje genérico y permanezco en `/login`.
- **CA-V01-03** Dado un error de red, cuando envío, entonces veo el estado de error y puedo reintentar.
- **CA-V01-04** Dado que ya tengo sesión, cuando visito `/login`, entonces soy redirigido a mi inicio.
- **CA-V01-05** Dado que cierro sesión, cuando lo confirmo, entonces se borran los tokens y vuelvo a `/login`.

**Pruebas.** Unitarias del formulario; integración con MSW para 200/401/500; prueba de redirección por rol; prueba de accesibilidad del formulario.

**Limitaciones.** Sin refresh ni logout de servidor; sin recuperación de contraseña; sin SSO.

---

### V-02 — Dashboard del estudiante

| Campo | Valor |
|-------|-------|
| **ID** | V-02 |
| **Nombre** | Panel del estudiante |
| **Ruta** | `/estudiante` |
| **Clasificación** | **CD** (conceptual) |
| **Actor** | `ESTUDIANTE` |
| **Referencia visual** | `01_dashboard_estudiante.png` |

**Objetivo.** Ofrecer un punto de entrada al estudiante con sus solicitudes en curso, observadas y notificaciones.

**Alcance funcional.**
- Saludo con la cédula del token (no hay nombre).
- Tarjetas: solicitudes en borrador, observadas, notificaciones no leídas.
- Lista de expedientes del estudiante en `BORRADOR`/`OBSERVADA` (bandeja del rol).
- Acceso a crear solicitud (V-03), ver expediente (V-04) y notificaciones.
- Aviso de limitación: no hay perfil ni historial completo.

**Endpoints.**
- `GET /api/v1/expedientes/bandeja/?page=&page_size=`
  - El rol `ESTUDIANTE` ve solo `BORRADOR` y `OBSERVADA`.
  - Respuesta paginada: `{ count, next, previous, results: BandejaExpediente[] }`.
- `GET /api/v1/notificaciones/` (paginado; estructura estándar DRF).
- `PATCH /api/v1/notificaciones/{id}/marcar-leida/`.

**Datos mostrados.**
- `numero_expediente`, `estado`, `fecha_creacion`, `fecha_recepcion`, `fecha_limite_atencion`.
- `carrera_id` y `facultad_id` como UUID (sin nombres; no hay catálogo).
- Notificaciones: `titulo`, `mensaje`, `leida`, `fecha_creacion`, `expediente_numero`.

**Reglas de UI.**
- Los contadores se calculan sobre la página cargada; si hay más páginas, se indica "ver todas".
- No mostrar tarjetas con datos inventados si la API falla; mostrar estado de error.
- Si no hay expedientes, estado vacío con CTA "Crear solicitud".
- Si el estudiante tiene un expediente `ENVIADA` o posterior, no aparecerá en la bandeja; se muestra un aviso y se ofrece el acceso por enlace/ID guardado localmente.

**Estados.** `loading`, `empty`, `error`, `success`, `partial` (notificaciones fallan pero expedientes cargan).

**Errores.** 401 → sesión expirada; 403 → V-09; 5xx/red → error con reintento.

**Dependencias.** BE-01/BE-05 (perfil e historial completo), BE-09 (bandeja para estados posteriores).

**Criterios de aceptación.**
- **CA-V02-01** Dado un estudiante autenticado, cuando entra a `/estudiante`, entonces ve su cédula y sus expedientes en `BORRADOR`/`OBSERVADA`.
- **CA-V02-02** Dado que no tiene expedientes, entonces ve un estado vacío con CTA para crear uno.
- **CA-V02-03** Dado que tiene notificaciones no leídas, entonces ve el contador y puede marcarlas como leídas.
- **CA-V02-04** Dado que la API falla, entonces ve un error con reintento y no datos ficticios.
- **CA-V02-05** Dado un expediente en `ENVIADA`, entonces la UI informa que no se lista por limitación del backend.

**Pruebas.** Integración con MSW (bandeja, notificaciones), estados vacío/error, accesibilidad de tarjetas, cálculo de contadores.

**Limitaciones.** Sin nombre/carrera/facultad; sin historial completo; sin agregados del backend.

---

### V-03 — Crear solicitud

| Campo | Valor |
|-------|-------|
| **ID** | V-03 |
| **Nombre** | Nueva solicitud de titulación |
| **Ruta** | `/estudiante/solicitud/nueva` |
| **Clasificación** | **IP** (parcial) |
| **Actor** | `ESTUDIANTE` |
| **Referencia visual** | `02_crear_solicitud.png` |

**Objetivo.** Registrar un expediente de titulación en estado `BORRADOR` y generar sus peticiones documentales iniciales.

**Alcance funcional.**
- Formulario con `carrera_id` (UUID).
- Sin catálogo de carreras: en el MVP se permite entrada manual de UUID en modo técnico o se muestra V-09 si el producto exige selección.
- Sin `opcion_titulacion` (no existe en backend).
- Sin datos de perfil (el backend deriva `estudiante_id` del token).
- Confirmación y creación; redirección a V-04.
- Persistencia local del borrador del formulario.

**Endpoint.**
- `POST /api/v1/expedientes/`
  - Request: `{ "carrera_id": "uuid" }`
  - Response 201: `CrearExpediente` con `id`, `numero_expediente`, `estudiante_id`, `carrera_id`, `facultad_id`, `estado`, `activa`, `fecha_creacion`, `fecha_recepcion`, `numero_providencia`, `fecha_limite_atencion`, `dias_laborables_acumulados`, `peticiones[]`.
  - 400: expediente activo existente o catálogo incompleto.
  - 403: rol no autorizado.

**Validaciones.**
- `carrera_id` obligatorio y UUID válido (regex/parse).
- No se permiten campos extra.
- Evitar doble envío.
- Si ya existe un expediente activo, mostrar el mensaje del backend y ofrecer ir al expediente.

**Estados.** `idle`, `validating`, `submitting`, `success`, `error`, `blocked` (sin catálogo).

**Errores.**
- 400 → mensaje del backend (expediente activo / catálogo incompleto).
- 403 → V-09.
- 422/500 → mensaje genérico con reintento.

**Dependencias.** BE-10 (catálogo de carreras), BE-06 (`opcion_titulacion`), BE-05 (perfil).

**Criterios de aceptación.**
- **CA-V03-01** Dado un UUID de carrera válido, cuando envío, entonces se crea el expediente y soy redirigido a V-04.
- **CA-V03-02** Dado un UUID inválido, entonces veo el error antes de llamar a la API.
- **CA-V03-03** Dado que ya tengo un expediente activo, entonces veo el mensaje y un enlace al expediente.
- **CA-V03-04** Dado que no hay catálogo, entonces la vista muestra la limitación y no inventa carreras.
- **CA-V03-05** Dado que recargo la página, entonces el borrador del formulario se conserva.

**Pruebas.** Validación de UUID, integración 201/400/403, persistencia de borrador, accesibilidad.

**Limitaciones.** Sin catálogo, sin perfil, sin opción de titulación; la UX real requiere BE-05/BE-06/BE-10.

#### 9.2 V-03 — Clarificación sobre carrera y opciones de titulación (DEC-14; corrección MOMENTO 2, 2026-11-04)

> **Trazabilidad de la corrección.** La versión anterior clasificaba la selección de opciones como "solo visual" y daba por descartado el selector de modalidades. La corrección (aprobada por el humano) conserva esa decisión —**V-03 vigente no implementa el selector**— pero la reformula: el selector **no queda descartado definitivamente**, queda **condicionado y pendiente de decisión**. El texto estático anterior no se elimina de la historia: DEC-14 (v. inciso de corrección) e INC-15 registran el cambio. `carrera_id` y `opcion_titulacion` son conceptos distintos y no deben confundirse.

**a) Qué se conoce (confirmado por el contrato vigente).**

- **`carrera_id`** (obligatorio): identifica la **carrera** del estudiante ante el backend. Es el único dato de identidad académica que consume `POST /api/v1/expedientes/`. Se envía como UUID; no existe catálogo (BE-10).
- **`opcion_titulacion`** (concepto distinto): identificaría la **modalidad** con la que el estudiante culmina su titulación. **El backend no declara este campo** —ni modelo, endpoint ni catálogo— (B-06/BE-06, NO AUTORIZADA; no se interpreta como autorización para modificar el backend).

**b) Opciones identificadas por el análisis secundario (NotebookLM — referencia NO normativa), pendientes de validación con la fuente primaria.**

| Opción | Condición preliminar (hipótesis) | Base legal señalada (por contrastar con el RRA-UNL vigente) | Estado |
|---|---|---|---|
| **Trabajo de Integración Curricular** | Opción ordinaria: registro al aprobar el 100% de asignaturas (o planificado desde el 85% de horas, según la referencia) | Arts. 39, 212 y 216 | **Hipótesis pendiente** de fuente primaria |
| **Examen Complexivo** | Excepcional: habilitado solo tras reprobar dos veces la unidad e ingresar a tercera matrícula (según la referencia) | Arts. 40, 212 inciso b) y 233 | **Hipótesis pendiente** de fuente primaria |
| **Proyecto de Emprendimiento** | No aparece identificado como modalidad independiente en la normativa consultada | No señalado | **No confirmado**; no se incorpora |

**c) Qué está pendiente de validación normativa (no verificable en el repo).**

- La fuente primaria del **RRA-UNL** no existe en el repositorio: los artículos 39, 40, 212, 216 y 233 señalados **no han sido contrastados** con el texto vigente del reglamento. El análisis secundario (NotebookLM) **no constituye fuente normativa** y no habilita por sí solo ninguna regla de elegibilidad.
- No se inventan reglas adicionales, no se infieren **diferencias** de elegibilidad por licenciaturas vs ingenierías, y no se asume que todo estudiante pueda escoger libremente entre modalidades.

**d) Qué necesita el frontend — para mostrar opciones y elegibilidad (hoy disponible: nada).**

- Definición aprobada por el humano de las modalidades habilitadas y sus condiciones (validadas contra el RRA-UNL).
- Contrato backend aprobado que incluya (a lo menos): catálogo de modalidades válidas por carrera (evolución de BE-10), campo `opcion_titulacion` en la creación/lectura del expediente (BE-06), y datos de habilitación del estudiante (malla/avance/matrícula hoy ausentes: BE-01/BE-05 y fuentes externas).
- Reglas de elegibilidad computables o, en su defecto, el cálculo del lado del backend.

**e) Qué NO provee el backend actualmente.**

- El campo `opcion_titulacion` no existe en ningún modelo, serializer ni endpoint vigente; no hay catálogo de modalidades ni datos de habilitación académica. Cualquier UI de opciones sería hoy un estado inventado (prohibición CA-G-01).

**f) Decisión que deberá aprobarse antes de implementar V-03 con opciones.**

1. Validar la fuente primaria del RRA-UNL (modalidades y condiciones de elegibilidad arti­culadas).
2. Aprobar/otorgar la ampliación de contratos del backend (BE-06 + BE-10 evolucionados) según la jerarquía normativa.
3. Autorizar la implementación del selector en el SDD (edición explícita de `specify.md` §V-03 y `tasks.md` FE-T301/FE-T302) cuando 1 y 2 estén cerrados.
4. Mientras no ocurra 1–3, V-03 se implementa **solo con `carrera_id`**, sin wizard de modalidades, y el prototipo A (`createApplication()`) permanece como referencia visual no vinculante para ese componente.

---

### V-04 — Expediente y requisitos

| Campo | Valor |
|-------|-------|
| **ID** | V-04 |
| **Nombre** | Detalle del expediente |
| **Ruta** | `/expedientes/:id` |
| **Clasificación** | **IP** (parcial) |
| **Actor** | Todos con alcance |
| **Referencia visual** | `03_expediente_requisitos.png` |

**Objetivo.** Mostrar el estado del expediente, sus peticiones documentales y, según el rol, el checklist y las acciones disponibles.

**Alcance funcional.**
- Cargar detalle del expediente.
- Mostrar timeline de estados y datos generales.
- Mostrar peticiones anidadas.
- Cargar checklist si el rol está autorizado.
- Acciones por rol/estado:
  - Estudiante: enviar (`BORRADOR`), subsanar checklist (`OBSERVADO`), cargar documento, descargar.
  - Secretario/Abogado: observar, evaluar checklist, emitir informe, descargar.
  - Analista: evaluar checklist en borrador, emitir informe, descargar.
  - Decano: declarar aptitud cuando `INFORME_EMITIDO` (sin descarga de petición por RBAC).
  - Secretaria/Director: cargar/descargar documentos.
- Refrescar tras cada mutación.

**Endpoints.**
- `GET /api/v1/expedientes/{id}/` → `ExpedienteDetalle` (incluye `peticiones[]`).
- `GET /api/v1/expedientes/{id}/checklist/` → `ChecklistVerification[]` (solo roles autorizados).
- `POST /api/v1/expedientes/{id}/enviar/` → 200 `ExpedienteEnviado`; 400 estado inválido; 422 requisitos incompletos.
- `POST /api/v1/expedientes/{id}/observar/` → 201; body `{ motivo_observacion, peticion_id? }`; 400/403/404.
- `PUT /api/v1/checklist/{id}/` → 200; body `{ estado_verificacion: VERIFICADO|OBSERVADO, motivo_observacion? }`; `motivo_observacion` obligatorio si `OBSERVADO`.
- `POST /api/v1/checklist/{id}/subsanar/` → 200; `multipart/form-data` con `archivo` PDF.
- `GET /api/v1/peticiones/{id}/documento/` y `/{version}/` → archivo.
- `POST /api/v1/informes/` → 201; body `{ expediente_id, dictamen: APTO|NO APTO, fundamentacion? }`.
- `POST /api/v1/declaratorias/` → 201; `multipart/form-data` con `expediente_id`, `archivo_memorando`, `numero_memorando?`.

**Datos mostrados.**
- `numero_expediente`, `estado`, `activa`, `fecha_creacion`, `fecha_recepcion`, `numero_providencia`, `fecha_limite_atencion`, `dias_laborables_acumulados`.
- `estudiante_id`, `carrera_id`, `facultad_id` (UUID; sin nombres).
- Peticiones: `id`, `requisito_codigo`, `requisito_nombre`, `estado_peticion`, `dependencia_emisora`.
- Checklist: `id`, `requisito_codigo`, `requisito_nombre`, `estado_verificacion`, `evaluado_por_username`, `fecha_evaluacion`, `fecha_actualizacion`.

**Reglas de UI.**
- No mostrar acciones no permitidas por rol/estado.
- El checklist para `ESTUDIANTE` devuelve 403: mostrar un panel informativo "No disponible para su rol" y no reintentar en bucle.
- Las acciones de escritura piden confirmación.
- Tras `enviar`, actualizar estado y deshabilitar acciones de borrador.
- Tras `observar`, mostrar el motivo y el nuevo estado.
- Tras evaluar/subsanar, refrescar checklist y expediente.
- Los documentos se descargan con el token; no se enlazan sin auth.

**Estados.** `loading`, `not-found` (404), `forbidden` (403), `partial` (checklist 403), `error`, `success`, `mutating`.

**Errores.**
- 401 → login.
- 403 → V-09 o panel de limitación según contexto.
- 404 → "Expediente no encontrado".
- 422 → "Faltan requisitos en firme para enviar".
- 400 → mensaje del backend.
- 5xx/red → error con reintento.

**Dependencias.** BE-04 (checklist estudiante), BE-02 (detalle de petición), BE-07 (motivo en respuestas), BE-08 (CORS).

**Criterios de aceptación.**
- **CA-V04-01** Dado un expediente existente, cuando cargo la vista, entonces veo sus datos y peticiones.
- **CA-V04-02** Dado un estudiante en `BORRADOR`, cuando envío, entonces el estado cambia a `ENVIADA` y se refresca.
- **CA-V04-03** Dado un envío con requisitos incompletos, entonces veo el mensaje 422 y no se envía.
- **CA-V04-04** Dado un secretario en `EN_VERIFICACION`, cuando observo con motivo, entonces el expediente pasa a `OBSERVADA` y veo el motivo.
- **CA-V04-05** Dado un secretario/analista, cuando evalúo un checklist como `OBSERVADO` sin motivo, entonces la UI bloquea el envío.
- **CA-V04-06** Dado un estudiante, cuando abro el checklist, entonces veo el panel de limitación (403) sin errores de consola no controlados.
- **CA-V04-07** Dado un PDF inválido en subsanación, entonces veo el error local y no se llama a la API.

**Pruebas.** Integración por rol/estado; MSW para 200/400/403/404/422; pruebas de acciones; accesibilidad de timeline y formularios.

**Limitaciones.** Sin nombres de estudiante/carrera/facultad; sin historial de estados; sin checklist para estudiante; sin detalle de petición independiente.

---

### V-05 — Gestión de peticiones documentales

| Campo | Valor |
|-------|-------|
| **ID** | V-05 |
| **Nombre** | Peticiones del expediente |
| **Ruta** | `/expedientes/:id/peticiones` |
| **Clasificación** | **IP** (parcial) |
| **Actor** | Estudiante y roles con alcance |
| **Referencia visual** | `04_crear_peticion.png` |

**Objetivo.** Gestionar las peticiones documentales generadas por el expediente: solicitar emisión y cargar el documento correspondiente.

**Alcance funcional.**
- Listar peticiones del expediente (desde el detalle).
- Solicitar emisión de una petición `PENDIENTE`.
- Cargar un PDF para una petición `SOLICITADO` (o según regla del backend).
- Mostrar estado y dependencia emisora.
- **No** existe creación manual de peticiones: se generan al crear el expediente. La vista lo explica.

**Endpoints.**
- `GET /api/v1/expedientes/{id}/` (para obtener peticiones).
- `POST /api/v1/peticiones/{id}/solicitar-emision/` (sin body) → 200 `{ id, requisito_codigo, requisito_nombre, estado_peticion, dependencia_emisora, fecha_solicitud }`.
- `POST /api/v1/peticiones/{id}/documento/` (`multipart/form-data`, `archivo`) → 201 `DocumentoEntregado`.
- `GET /api/v1/peticiones/{id}/documento/` y `/{version}/` → archivo.

**Datos mostrados.**
- `requisito_codigo`, `requisito_nombre`, `requisito_descripcion` (si está disponible), `estado_peticion`, `dependencia_emisora`, `fecha_solicitud`, `fecha_actualizacion`.
- Documento: `nombre_original`, `version`, `tamanio_bytes`, `tipo_mime`, `fecha_carga`, `es_vigente`.

**Reglas de UI.**
- "Solicitar emisión" solo si `PENDIENTE` y el rol lo permite.
- "Cargar documento" solo si el estado lo permite y el rol lo permite.
- Validar PDF (MIME/extensión, ≤ 10 MB, magic bytes) antes de enviar.
- Mostrar progreso de carga.
- Tras éxito, refrescar el expediente.
- No mostrar un botón "Crear petición" que no tenga endpoint.

**Estados.** `loading`, `empty`, `error`, `success`, `uploading`, `mutating`.

**Errores.**
- 400 → estado inválido o PDF inválido.
- 403 → sin permisos.
- 404 → petición/expediente no encontrado.
- 5xx/red → reintento.

**Dependencias.** BE-02 (detalle de petición), BE-06 (opción de titulación si aplica), BE-08 (CORS).

**Criterios de aceptación.**
- **CA-V05-01** Dado un expediente con peticiones, entonces veo la lista con su estado.
- **CA-V05-02** Dado una petición `PENDIENTE` y rol autorizado, cuando solicito emisión, entonces pasa a `SOLICITADO` y se refresca.
- **CA-V05-03** Dado una petición `SOLICITADO`, cuando cargo un PDF válido, entonces se registra el documento y cambia a `CARGADO`.
- **CA-V05-04** Dado un archivo > 10 MB o no PDF, entonces veo el error local y no se envía.
- **CA-V05-05** Dado que no existe endpoint de creación, entonces la UI no ofrece "crear petición" y explica la limitación.

**Pruebas.** Integración de solicitar/cargar; validación de archivo; MSW 200/201/400/403/404; accesibilidad del formulario de carga.

**Limitaciones.** No hay creación manual de peticiones; no hay detalle independiente; la carga depende del estado real.

---

### V-06 — Seguimiento de petición

| Campo | Valor |
|-------|-------|
| **ID** | V-06 |
| **Nombre** | Seguimiento de petición documental |
| **Ruta** | `/expedientes/:id/peticiones/:peticionId` |
| **Clasificación** | **IP** (parcial) |
| **Actor** | Estudiante y roles con alcance |
| **Referencia visual** | `05_seguimiento_peticion.png` |

**Objetivo.** Mostrar el estado y los documentos de una petición documental.

**Alcance funcional.**
- Obtener la petición desde el detalle del expediente (no hay `GET /peticiones/{id}/`).
- Mostrar estado, dependencia, requisito, fechas.
- Descargar el documento vigente o una versión.
- Refrescar manualmente.
- Explicar la limitación si no se encuentra la petición en el detalle.

**Endpoints.**
- `GET /api/v1/expedientes/{id}/` → buscar `peticiones[]` por `peticionId`.
- `GET /api/v1/peticiones/{id}/documento/` → descarga vigente.
- `GET /api/v1/peticiones/{id}/documento/{version}/` → descarga versión.

**Datos mostrados.**
- `requisito_codigo`, `requisito_nombre`, `estado_peticion`, `dependencia_emisora`, `fecha_solicitud`, `fecha_actualizacion`.
- Documento: `nombre_original`, `version`, `tamanio_bytes`, `hash_sha256`, `tipo_mime`, `fecha_carga`, `es_vigente`, `subido_por_username`.

**Reglas de UI.**
- Si la petición no está en el detalle (p. ej., por paginación o cambio), mostrar "No encontrada" con enlace al expediente.
- No inventar un historial de versiones: solo se puede descargar la vigente o una versión conocida.
- Mostrar el estado con badge y descripción.
- El botón de descarga usa `fetch` con `Authorization` y `blob`.

**Estados.** `loading`, `not-found`, `error`, `success`, `downloading`.

**Errores.**
- 404 → "Petición o documento no encontrado".
- 403 → V-09.
- 401 → login.
- 5xx/red → reintento.

**Dependencias.** BE-02 (`GET /peticiones/{id}/` y listado de documentos).

**Criterios de aceptación.**
- **CA-V06-01** Dado un expediente con la petición, entonces veo su estado y datos.
- **CA-V06-02** Dado un documento vigente, cuando descargo, entonces se descarga el PDF.
- **CA-V06-03** Dado que la petición no está en el detalle, entonces veo "No encontrada" y un enlace al expediente.
- **CA-V06-04** Dado un error de red, entonces veo reintento y no un estado vacío engañoso.

**Pruebas.** Integración con MSW; descarga con blob; estados de error; accesibilidad.

**Limitaciones.** Sin endpoint de detalle; sin historial de documentos; sin notificaciones en tiempo real.

---

### V-07 — Bandeja del funcionario

| Campo | Valor |
|-------|-------|
| **ID** | V-07 |
| **Nombre** | Bandeja operativa |
| **Ruta** | `/bandeja` |
| **Clasificación** | **PB** (pendiente de backend para la experiencia completa) |
| **Actor** | Roles operativos |
| **Referencia visual** | `06_bandeja_funcionario.png` |

**Objetivo.** Mostrar los expedientes que requieren intervención del rol, ordenados por fecha límite.

**Alcance funcional.**
- Listar expedientes paginados según el rol.
- Mostrar columnas: número, estudiante, carrera, facultad, estado, fecha de creación, fecha de recepción, providencia, fecha límite.
- Navegar al detalle (V-08).
- Búsqueda/filtros solo sobre la página cargada (no hay filtros server-side).
- Estado vacío cuando el rol no tiene expedientes asignados.

**Endpoint.**
- `GET /api/v1/expedientes/bandeja/?page=&page_size=`
  - `page_size` por defecto 10, máximo 50.
  - Respuesta: `{ count, next, previous, results: BandejaExpediente[] }`.
  - Filtrado por rol:
    - `ESTUDIANTE`: `BORRADOR`, `OBSERVADA`.
    - `SECRETARIO_ABOGADO` / `ANALISTA_APOYO`: `ENVIADA`, `EN_VERIFICACION`, `OBSERVADA`.
    - `DECANO`: `INFORME_EMITIDO`.
    - `ADMINISTRADOR`: todos los estados en curso.
    - `SECRETARIA_CARRERA` / `DIRECTOR_CARRERA`: sin expedientes (lista vacía).
  - Orden: `fecha_limite_atencion`, `fecha_creacion`.

**Datos mostrados.**
- `numero_expediente`, `estudiante_id`, `carrera_id`, `facultad_id`, `estado`, `fecha_creacion`, `fecha_recepcion`, `numero_providencia`, `fecha_limite_atencion`.

**Reglas de UI.**
- No mostrar filtros que el backend no soporta como si fueran globales; si se ofrecen, etiquetar "filtra la página actual".
- Indicar el total (`count`) y la paginación.
- En móvil, tarjetas en lugar de tabla.
- Resaltar vencimientos próximos (cálculo local sobre `fecha_limite_atencion`).
- No mostrar acciones de escritura en la bandeja; solo navegación.

**Estados.** `loading`, `empty`, `error`, `success`.

**Errores.**
- 401 → login.
- 403 → V-09.
- 5xx/red → reintento.

**Dependencias.** BE-09 (bandeja para roles sin expedientes y filtros si se requieren), BE-08 (CORS).

**Criterios de aceptación.**
- **CA-V07-01** Dado un secretario, entonces veo expedientes en `ENVIADA`/`EN_VERIFICACION`/`OBSERVADA`.
- **CA-V07-02** Dado un decano, entonces veo expedientes en `INFORME_EMITIDO`.
- **CA-V07-03** Dado un rol sin expedientes, entonces veo un estado vacío explicativo.
- **CA-V07-04** Dado más de una página, entonces puedo navegar y el tamaño máximo es 50.
- **CA-V07-05** Dado un expediente, cuando hago clic, entonces navego a V-08.

**Pruebas.** Integración por rol; paginación; estado vacío; responsive de tabla; accesibilidad.

**Limitaciones.** Sin filtros/búsqueda server-side; sin asignación; roles sin bandeja; sin acciones masivas.

---

### V-08 — Detalle del funcionario

| Campo | Valor |
|-------|-------|
| **ID** | V-08 |
| **Nombre** | Detalle operativo del expediente |
| **Ruta** | `/bandeja/:id` |
| **Clasificación** | **IP** (parcial) |
| **Actor** | Roles operativos |
| **Referencia visual** | `07_detalle_funcionario.png` |

**Objetivo.** Permitir al funcionario revisar el expediente, evaluar requisitos, observar, emitir informe y, para el Decano, declarar aptitud.

**Alcance funcional.**
- Cargar detalle del expediente y checklist.
- Evaluar requisitos (`VERIFICADO`/`OBSERVADO`).
- Observar el expediente con motivo.
- Emitir informe (`APTO`/`NO APTO`).
- Declarar aptitud con memorando firmado.
- Descargar documentos.
- Refrescar tras mutaciones.
- Mostrar acciones según rol/estado.

**Endpoints.**
- `GET /api/v1/expedientes/{id}/`
- `GET /api/v1/expedientes/{id}/checklist/`
- `PUT /api/v1/checklist/{id}/`
- `POST /api/v1/expedientes/{id}/observar/`
- `POST /api/v1/informes/`
- `POST /api/v1/declaratorias/`
- `GET /api/v1/peticiones/{id}/documento/` y `/{version}/`

**Datos mostrados.**
- Los de V-04, más checklist y acciones.
- Informe: `dictamen`, `fundamentacion` (si se devuelve).
- Declaratoria: `numero_memorando`, `archivo_memorando`.

**Reglas de UI.**
- `SECRETARIO_ABOGADO`: observar, evaluar checklist, emitir informe.
- `ANALISTA_APOYO`: evaluar checklist (borrador), emitir informe.
- `DECANO`: declarar aptitud cuando `INFORME_EMITIDO` (sin descarga de petición por RBAC).
- `SECRETARIA_CARRERA` / `DIRECTOR_CARRERA`: cargar/descargar documentos; sin acciones de estado.
- `ADMINISTRADOR`: acciones permitidas por RBAC; la UI no asume más de lo que el backend permite.
- Confirmaciones con resumen de la acción.
- Tras declarar, el expediente pasa a `DECLARADA_APTA` y queda solo lectura.
- No mostrar un historial de informes/declaratorias si no hay endpoint de consulta.

**Estados.** `loading`, `not-found`, `forbidden`, `error`, `success`, `mutating`, `read-only`.

**Errores.**
- 400 → estado inválido o datos inválidos.
- 403 → V-09.
- 404 → no encontrado.
- 422 → requisitos incompletos (si aplica).
- 5xx/red → reintento.

**Dependencias.** BE-02 (detalle de petición), BE-07 (motivo), BE-08 (CORS).

**Criterios de aceptación.**
- **CA-V08-01** Dado un secretario en `EN_VERIFICACION`, entonces ve checklist y acciones de evaluar/observar.
- **CA-V08-02** Dado un checklist `OBSERVADO` sin motivo, entonces la UI bloquea y muestra el error.
- **CA-V08-03** Dado un analista, entonces puede emitir informe si el estado lo permite.
- **CA-V08-04** Dado un decano con `INFORME_EMITIDO`, entonces puede declarar aptitud con PDF firmado.
- **CA-V08-05** Dado un expediente `DECLARADA_APTA`, entonces no se muestran acciones de escritura.
- **CA-V08-06** Dado un rol sin permiso, entonces no ve la acción y, si fuerza la petición, recibe 403 manejado.

**Pruebas.** Integración por rol/estado; formularios de checklist/observación/informe/declaratoria; carga de PDF; MSW; accesibilidad.

**Limitaciones.** Sin consulta de informes/declaratorias; sin historial de estados; sin asignación; sin firma electrónica en frontend.

---

### V-09 — Estado no habilitado

| Campo | Valor |
|-------|-------|
| **ID** | V-09 |
| **Nombre** | Funcionalidad no habilitada |
| **Ruta** | `/no-habilitado` |
| **Clasificación** | **IP** (parcial) |
| **Actor** | Autenticado |
| **Referencia visual** | `08_estado_no_habilitado.png` / `09_estado_no_habilitado.png` |

**Objetivo.** Comunicar de forma clara que una funcionalidad no está disponible por una limitación del backend o del alcance, sin simular datos.

**Alcance funcional.**
- Página reutilizable con:
  - Título y descripción de la funcionalidad.
  - Motivo: "No disponible en esta versión".
  - Dependencia asociada (`BE-xx`) cuando aplique.
  - Alternativas: volver, ir al expediente, contactar soporte.
  - Código de referencia para soporte.
- Usada por guardas y por vistas parciales.

**Reglas de UI.**
- No mostrar datos ficticios.
- No ofrecer botones que no funcionen.
- Mantener el layout y la navegación.
- Ser accesible y responsive.
- Si se llega por 403, no revelar la existencia de recursos no autorizados.

**Estados.** `info` (por defecto), `forbidden`, `not-found`.

**Criterios de aceptación.**
- **CA-V09-01** Dado un rol no autorizado, cuando accede a una ruta protegida, entonces ve V-09 con el motivo y una alternativa.
- **CA-V09-02** Dado un enlace a una funcionalidad no soportada, entonces V-09 muestra la dependencia `BE-xx`.
- **CA-V09-03** Dado que el usuario vuelve, entonces regresa a una ruta válida.
- **CA-V09-04** Dado un lector de pantalla, entonces el mensaje se anuncia correctamente.

**Pruebas.** Unitarias de contenido; integración de guardas; accesibilidad.

**Limitaciones.** Es una vista de comunicación, no una funcionalidad de negocio.

---

### 9.3 Estados de error (clasificación oficial)

La clasificación operativa de los estados de error —**errores globales, errores de formularios y estados operativos reutilizables**— está detallada en `diseno-ui/ui/titulacion-v2/especificaciones/08_UI_ERROR_STATES_SPEC.md` (referencia visual, no normativa para la funcionalidad). Principios vinculantes de esta especificación:

| Clase | Estados | Comportamiento normativo (RFF) | Respaldo de backend |
|-------|---------|-------------------------------|---------------------|
| **Globales (app/ruta)** | 401 sesión requerida · 403 acceso restringido · 404 no encontrado · 500 error interno · 503 servicio no disponible | RFF-014 (401→login), RFF-002 (403→V-09), RFF-017 (403/404 diferenciados), RFF-013 (reintento) | 401/403/404/500 de facto (DRF); 503 de infraestructura. **Ninguno declarado en OpenAPI** (CL-22). |
| **Procesos (formularios)** | 400 validación · 422 requisitos incompletos · 409 petición duplicada · 412 información desactualizada · 428 versión requerida | RFF-005 (validación), RFF-016 (confirmación); **409/412/428 = escenarios propuestos (DEC-13), condicionados a BE-11** | 400/422 de facto; 409/412/428 **no respaldados** (BE-11 pendiente). |
| **Operativos (reutilizables)** | loading · empty (sin expedientes / sin resultados / sin asignación) · forbidden state (checklist 403 BE-04) · success · read-only | RFF-004 (estados homogéneos), RFF-009 (paginación), RFF-705 (vacío por rol) | Estados derivables de respuestas reales. |

Reglas:
- No se crean páginas independientes para estados que un componente reutilizable resuelve: `401` (redirección a `/login` con aviso) usa el propio login; `404` es página (navegación directa puede ocurir); `403` usa `ForbiddenState` dentro del layout y la guarda reutiliza V-09; `500/503` usan `ErrorState` con reintento (páginas solo si el ErrorBoundary global necesite pintar un shell).
- Los inline-alerts 409/412/428 del prototipo B no se implementan hasta que BE-11 esté autorizado (tarea FE-T1213 **Bloqueada**).
- Ningún estado no representado en prototipos ni respaldado por requisitos se inventa; los enumerados en la clase 08 como "pendientes" (p. ej. 429 rate limiting, usuario inactivo) quedan **no definidos**.

---

## 10. Matriz de trazabilidad

### 10.1 Vista ↔ requisitos ↔ endpoints ↔ tareas

| Vista | Clasificación | Requisitos FE | Endpoints principales | Tareas (ver `tasks.md`) |
|-------|---------------|---------------|-----------------------|--------------------------|
| V-01 | IF | RFF-001, RFF-002, RFF-014, RFF-101…107 | `POST /auth/token/` | FE-T1xx |
| V-02 | CD | RFF-003, RFF-008, RFF-201…205 | `GET /expedientes/bandeja/`, `GET /notificaciones/`, `PATCH /notificaciones/{id}/marcar-leida/` | FE-T2xx |
| V-03 | IP | RFF-005, RFF-018, RFF-301…306 | `POST /expedientes/` | FE-T3xx |
| V-04 | IP | RFF-004, RFF-006, RFF-007, RFF-016, RFF-401…411 | `GET /expedientes/{id}/`, `GET /expedientes/{id}/checklist/`, `POST /expedientes/{id}/enviar/`, `POST /expedientes/{id}/observar/`, `PUT /checklist/{id}/`, `POST /checklist/{id}/subsanar/`, `GET /peticiones/{id}/documento/` | FE-T4xx |
| V-05 | IP | RFF-006, RFF-501…506 | `POST /peticiones/{id}/solicitar-emision/`, `POST /peticiones/{id}/documento/` | FE-T5xx |
| V-06 | IP | RFF-007, RFF-601…605 | `GET /expedientes/{id}/`, `GET /peticiones/{id}/documento/` | FE-T6xx |
| V-07 | PB | RFF-009, RFF-701…706 | `GET /expedientes/bandeja/` | FE-T7xx |
| V-08 | IP | RFF-016, RFF-801…809 | `GET /expedientes/{id}/`, `GET /expedientes/{id}/checklist/`, `PUT /checklist/{id}/`, `POST /expedientes/{id}/observar/`, `POST /informes/`, `POST /declaratorias/` | FE-T8xx |
| V-09 | IP | RFF-017, RFF-901…904 | — | FE-T9xx |

### 10.2 Requisitos FE ↔ requisitos backend

| Requisito FE | Requisito backend relacionado | Evidencia |
|--------------|-------------------------------|-----------|
| RFF-001 | RF-001/HU-001 (autenticación), RNF-002 | `authentication` |
| RFF-002 | RBAC §6.2, RNF-002 | `permissions.py` |
| RFF-003 | RF-012/HU-005 (bandeja) | `expedientes` |
| RFF-004 | RNF-009 (errores), CA globales | `specify.md` |
| RFF-005 | RN/EX de validación | `specify.md` |
| RFF-006 | RNF-004 (PDF ≤ 10 MB) | `CargarDocumentoSerializer` |
| RFF-007 | RNF-016 (IDOR/descarga segura) | `descargar_documento` |
| RFF-008 | DEC-01 (notificaciones) | `notificaciones` |
| RFF-009 | RF-012 (bandeja paginada) | `BandejaPagination` |
| RFF-010 | P-01 (simulación) | Constitución |
| RFF-011 | P-16 (accesibilidad) | Constitución |
| RFF-012 | P-17 (incremental) / UX | Constitución |
| RFF-013 | RNF-009 | `specify.md` |
| RFF-014 | RNF-002 (sesión) | `authentication` |
| RFF-015 | RNF-010 (formatos) | `specify.md` |
| RFF-016 | P-02 (autoridad humana) | Constitución |
| RFF-017 | RNF-002/RNF-016 | `specify.md` |
| RFF-018 | P-17 (incremental) | Constitución |
| RFF-019 | P-01 | Constitución |
| RFF-020 | P-08 (trazabilidad), RNF-016 | Constitución |

---

## 11. Criterios de aceptación globales

1. **CA-G-01** Ninguna vista muestra datos ficticios cuando el backend no los provee.
2. **CA-G-02** Toda petición a la API incluye `Authorization: Bearer <access>` salvo el login.
3. **CA-G-03** Un 401 limpia la sesión y redirige a `/login` con aviso.
4. **CA-G-04** Un 403 muestra V-09 o un panel de limitación, sin filtrar detalles internos.
5. **CA-G-05** Un 404 muestra un estado "no encontrado" con navegación de retorno.
6. **CA-G-06** Todos los formularios validan en cliente y muestran errores accesibles.
7. **CA-G-07** Todas las vistas son navegables por teclado y tienen foco visible.
8. **CA-G-08** Todas las vistas son responsive a 320 px sin scroll horizontal.
9. **CA-G-09** No se registran tokens, contraseñas ni PII en consola.
10. **CA-G-10** La cobertura de pruebas es ≥ 80% en lógica y componentes críticos.
11. **CA-G-11** `tsc --noEmit`, ESLint y las pruebas pasan sin errores.
12. **CA-G-12** La documentación de frontend describe variables de entorno, scripts y limitaciones.

---

## 12. Glosario

| Término | Definición |
|---------|------------|
| **Expediente** | Unidad de trámite de titulación de un estudiante. |
| **Petición documental** | Requisito documental asociado a un expediente, con estado y dependencia emisora. |
| **Checklist** | Lista de verificación de requisitos de un expediente. |
| **Bandeja** | Lista de expedientes que requieren intervención de un rol. |
| **RBAC** | Control de acceso basado en roles. |
| **JWT** | JSON Web Token usado para autenticación local. |
| **SPA** | Single Page Application. |
| **MSW** | Mock Service Worker, para pruebas de integración. |
| **IF / IP / PB / CD** | Funcional / Parcial / Pendiente de backend / Conceptual. |
| **BE-xx** | Dependencia de backend no autorizada en esta feature. |

---

## 13. Referencias

- `clarify.md` — decisiones, supuestos y preguntas abiertas.
- `plan.md` — arquitectura, stack y estrategia.
- `tasks.md` — tareas atómicas y dependencias.
- `../001-tramite-titulacion/specify.md` — requisitos funcionales del backend.
- `../../backend/openapi.yaml` — contrato.
- `../../diseno-ui/ui/titulacion-v2/especificaciones/08_UI_ERROR_STATES_SPEC.md` — clasificación de estados de error (referencia visual).
- `../../prototipos/prototipo-general/` — prototipo A (referencia visual y de comportamiento, DEC-11).
- `../../prototipos/vistas-errores-unl/` — prototipo B, kit de errores (referencia visual, DEC-11/DEC-13).
