# 02 · Especificaciones visuales de las 9 vistas (SGT-SIAAF)

**Versión:** 1.1.0 · **Fecha:** 2026-11-04 · **Estado:** Referencia visual no normativa (DEC-11).
**Correspondencia oficial de IDs:** la matriz UI-01…UI-09 ↔ V-0x vive en `specs/003-frontend-titulacion/specify.md` §6.1. Este documento describe la intención de diseño de cada vista y fija su archivo de referencia en el prototipo A.

## 0. Convenciones

- **Composición general:** sidebar verde profundo (260 px) + header blanco (64 px) + contenido. V-01 (login) y el 404 global no usan este shell.
- Los datos mostrados en los prototipos (nombres, fechas, contadores como "2 de 5", "7mo ciclo", "168/220 créditos", IDs como `TI-2026-0045`) son **conceptuales** y no deben implementarse como lógica: la UI solo muestra lo que el backend provee (reglas en la matriz del doc 07 y CA-G-01 en `specify.md` §9.1).
- Las cámaras de prototipos con funcionalidad demo (login con perfiles demo, botones demo) son **solo visual**: nunca se simulan flujos reales sin endpoint autorizado.

## Vista 01 · Inicio de sesión — V-01 · `/login` · referencia: `accessPage()`

- **Composición:** split screen 50/50 (apilado en móvil). Izquierda: imagen del campus UNL, escudo, texto "Tu futuro profesional comienza aquí". Derecha: fondo blanco, logo SGT-SIAAF (birrete), tabs Estudiante/Funcionario, inputs Usuario/Contraseña, botón rojo "Ingresar".
- **Notas:** el login real usa `POST /auth/token/` (JWT local del backend vigente); el SAC (OAuth2/OIDC) es **futuro** y se documenta en el doc 06. Sin backend, la UI muestra 503/inaccesible, nunca un login falso.

## Vista 02 · Estudiante no habilitado — V-09 · `/no-habilitado` · referencia: `undergradPage()`

- **Composición:** layout estándar con contenido centrado.
- **Elementos:** tarjeta de bienvenida con imagen de facultad; banner de advertencia (fondo ámbar suave, borde ámbar, icono de alerta, botón "Ver requisitos"); fila de 4 tarjetas conceptuales (Carrera, Ciclo, Créditos, Estado).
- **Notas:** las 4 tarjetas son conceptuales (no hay API de récord académico/SGA); el contenido normativo real (requisitos, matrícula vigente) debe venir del backend. V-09 también es el destino de las guardas 403 (con `ForbiddenState` dentro del layout, doc 08).

## Vista 03 · Dashboard del estudiante — V-02 · `/estudiante` · referencia: `dashboard()`

- **Composición:** sidebar + header; grid principal.
- **Elementos:** saludo con nombre; tarjeta de expediente principal (icono documento, título, badge de estado, botón "Ver solicitud"); barra de progreso "Avance del proceso" verde con subtítulo "N de M requisitos"; fila de 5 hitos con badges; dos tarjetas inferiores ("Mis solicitudes", "Peticiones documentales") con contadores.
- **Notas:** el porcentaje progreso y contadores se calculan con los datos devueltos (frontend-only si la API no suma); si todos los estados de la bandeja están cerrados (RFF-201), la vista muestra el estado vacío oficial (FE-T201) en vez de "0 de 5".

## Vista 04 · Crear solicitud de aptitud — V-03 · `/estudiante/solicitud/nueva` · referencia: `createApplication()`

- **Composición:** breadcrumb (Titulación > Nueva solicitud); contenedor blanco centrado; stepper de 3 pasos (Opción, Confirmación, Creada); tarjetas de selección tipo radio grandes.
- **Restricción clave (DEC-14, corregida MOMENTO 2):** la implementación vigente usa `carrera_id` (obligatorio, UUID, sin catálogo —BE-10). Las opciones del prototipo ("Trabajo de Integración Curricular" y "Examen Complexivo") están **identificadas por análisis secundario, pendientes de validación con el RRA-UNL** (arts. 39, 40, 212, 216, 233; fuente primaria no verificada — ver `specify.md` §9.2, a–f); "Proyecto de Emprendimiento" **no está confirmado** y no se muestra. El selector de modalidades **no está descartado, pero no se implementa**: pendiente de decisión humana + BE-06 + contrato backend aprobado.
- La creación real es `POST /expedientes/` con una sola confirmación de `carrera_id`; el wizard del prototipo no es vinculante en la versión vigente.

## Vista 05 · Expediente y requisitos — V-04 · `/expedientes/:id` · referencia: `recordPage()` (+ `historyPage()` extra no oficial)

- **Composición:** header con título, badge "EN TRÁMITE", botón "Acciones"; tarjeta de resumen en 3 columnas (Proceso, Fecha, Versión); tabs "Requisitos de titulación" / "Información general"; tabla (`#`, Requisito, Estado, Fecha, Acciones) con botones "Solicitar" (rojo) y "Ver detalle" (outline).
- **Notas:** la consulta del checklist solo está disponible para roles autorizados (RBAC de backend, por diseño; RFF-404); la vista degradada del estudiante usa solo `GET expedientes/{id}/` + creación/derivación de peticiones. `historyPage()` del prototipo es un extra no oficial (historial no existe en endpoints).

## Vista 06 · Crear petición documental (modal) — asociado a V-05 · `/expedientes/:id/peticiones` · referencia: `modalHtml()`

- **Composición:** overlay oscurecido; modal centrado (max-width 600 px) con header (icono birrete, título, botón X), texto "Documento requerido: [Nombre]", alerta informativa azul, textarea "Motivo de la solicitud (opcional)", dropzone "Arrastra y suelta archivos aquí", footer con "Cancelar" y "Enviar solicitud" (rojo).
- **Notas:** subida real es `POST /peticiones/{id}/documento/` con validación de extensión/PDF y 10 MB (RFF-005); el "motivo" conceptual no es campo del backend — si se usa, es texto de contexto del estudiante, no campo puesto en cielo: controlar contra datos reales de DB (matriz doc 07).

## Vista 07 · Seguimiento de petición — V-06 · `/expedientes/:id/peticiones/:peticionId` · referencia: `petitionDetail()`

- **Composición:** breadcrumb; header con ID (TI-2026-0045 es formato conceptual), badge "EN ATENCIÓN", botón "Volver"; grid 70/30: izquierda "Información general" (Requisito, Dependencia, Fecha, Descripción); derecha "Estado del trámite" con timeline vertical (check verde = hecho, círculo con check en borde rojo = activo, gris = futuro).
- **Notas:** el backend no expone historial por petición; el timeline se infiere del estado actual (`specify.md` RFF-604). Los estados "En revisión" del prototipo no existen en el enum del backend ("PENDIENTE, SOLICITADO, CARGADO..."); solo se muestran estados reales devueltos. No existe `GET /peticiones/{id}/`: la fuente de datos debe declararse antes que la UI (RFF-605/CAP-605).

## Vista 08 · Bandeja del funcionario — V-07 · `/bandeja` · referencia: `staffPage()`

- **Composición:** layout estándar; título "Bandeja de peticiones documentales".
- **Elementos:** barra de filtros (Selects Dependencia/Estado, input de búsqueda, botón filtro); tabla (ID, Estudiante, Dependencia, Fecha, Estado, Observaciones, Acciones con botón "ojo" outline); paginación inferior "Mostrando 1–5 de 28 resultados" con botones de página.
- **Notas:** si la API no soporta filtros/paginación, se hacen en frontend solo con los datos reales recibidos (no se inventan páginas).

## Vista 09 · Detalle de petición (funcionario) — V-08 · `/bandeja/:id` · referencia: `staffDetail()`

- **Composición:** breadcrumb, header con ID, badge, botón "Acciones"; grid 2x2: "Información del estudiante" (avatar con iniciales, nombre, email, carrera, ciclo), "Información de la petición" (tipo, fecha, descripción), "Archivos adjuntos", "Historial de acciones" (timeline vertical).
- **Notas:** la API de expediente no anida el perfil completo del estudiante (email/ciclo) — mostrar solo los campos que llegan reales (o `BE-*` si el backend se amplía); la dropzone del funcionario es **solo lectura** (estado vacío, no subida); no existe endpoint de historial de acciones: el panel "Historial" se puebla únicamente con datos reales o se oculta con estado vacío.

## Kit de errores (transversal)

Las 9 vistas comparten estados de error y operativos (401/403/404/409/412/428/500/503, loading, empty, success, read-only). Su especificación completa está en `08_UI_ERROR_STATES_SPEC.md`; el prototipo de referencia es el kit B: `prototipos/vistas-errores-unl/paginas/{401,403,404,409,412,428,500,503}.html` y `acceso.html`.

## Referencias

- Prototipo A: `prototipos/prototipo-general/index.html` (páginas generadas por `app.js`: funciones listadas arriba).
- Prototipo B: `prototipos/vistas-errores-unl/`.
- SDD de vistas: `specs/003-frontend-titulacion/specify.md` §6 (IDs y rutas), §9.1 (CA-G-01), §9.2 (V-03/DEC-14), §9.3 (estados de error).
- Tareas React: `specs/003-frontend-titulacion/tasks.md` (FE-T1xx…FE-T9xx).
