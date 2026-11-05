# Clarificaciones — Frontend de Titulación (SGT-SIAAF)

**Feature ID:** `003-frontend-titulacion`
**Documento:** `clarify.md`
**Versión:** 1.2.0
**Fecha:** 2026-11-05
**Estado:** Aprobado en ETAPA B / refactorizado tras auditoría de prototipos y del frontend (2026-11-04, DEC-11…DEC-14, INC-14…INC-18, D-FE-01…D-FE-04, B-11/BE-11); **revisado en MOMENTO 2 (misma fecha): DEC-14 e INC-15 reformulados con trazabilidad de corrección** (opciones de titulación pendientes de validación del RRA-UNL; selector no descartado pero sin implementar); **actualizado 2026-11-05 con DEC-15** (autorización de uso de mascotas del prototipo B en F2.5/FE-T1214), sin cambios de otra naturaleza.
**Ámbito:** Documentación SDD. **No implementa código, no modifica backend, no modifica OpenAPI, no modifica la constitución ni los artefactos de `001-tramite-titulacion`.**

---

## 1. Propósito

Este documento registra las decisiones, supuestos, contradicciones y preguntas abiertas que condicionan la especificación, el plan y las tareas del frontend de titulación. Su función es evitar que el implementador (o un agente) resuelva silenciosamente ambigüedades, invente contratos o altere el backend para "hacer funcionar" la interfaz.

Regla de oro: **toda funcionalidad no confirmada por el código real, los contratos o la documentación institucional se documenta como limitación, no se simula como si existiera.**

---

## 2. Jerarquía de autoridad aplicada

En caso de conflicto, prevalece el orden siguiente (de mayor a menor):

1. Constitución del proyecto (`.specify/memory/constitution.md`).
2. Requisitos institucionales (memorandos, providencias, normativa citada).
3. Especificaciones funcionales aprobadas (`specs/001-tramite-titulacion/specify.md`).
4. ADRs (`backend/docs/adr/`).
5. Contrato OpenAPI (`backend/openapi.yaml` y `backend/contracts/openapi.yaml`).
6. Código real del backend (modelos, serializers, views, permisos).
7. Pruebas del backend.
8. Documentación técnica.
9. Especificaciones UI/UX (`diseno-ui/ui/titulacion-v2/especificaciones/`). **No normativas.**
10. Referencias visuales (imágenes). **No normativas.**

Cuando el código real contradice el OpenAPI, se documenta la discrepancia y se implementa contra el comportamiento real, sin modificar el contrato. Cuando la UI propone algo que el backend no soporta, se implementa un estado vacío/no habilitado con explicación, no una simulación de datos.

---

## 3. Decisiones aprobadas (ETAPA B)

| ID | Decisión | Justificación | Impacto |
|----|----------|---------------|---------|
| **DEC-01** | SDD ID = `003-frontend-titulacion` | Evita colisión con `001-tramite-titulacion` y con la "feature 002 demo" referenciada en la guía, que no existe en el repositorio. | Carpeta `specs/003-frontend-titulacion/`. |
| **DEC-02** | Los 7 documentos de `especificaciones/` se usan como referencia **visual y técnica no normativa**. | Están poblados (1.005–4.364 B) y describen el diseño esperado; no son contrato funcional. | La especificación funcional manda sobre la UI cuando hay conflicto. |
| **DEC-03** | Stack del frontend = **React + TypeScript + Vite**. | Decisión explícita del usuario. | `plan.md` fija stack, estructura y herramientas compatibles. |
| **DEC-04** | Se documentan las **9 vistas**, incluidas las que tienen limitaciones funcionales. | El usuario pidió las 9 vistas, no solo las 5 viables. | Cada vista declara clasificación y bloqueos. |
| **DEC-05** | Se aceptan los **13 fallos de `pypdf`** como deuda de entorno de pruebas del backend. | No afectan al frontend ni al contrato; son fallos de `resoluciones/tests/test_pdf_generator.py` por dependencia ausente. | Se registran como riesgo heredado, no como tarea de frontend. |
| **DEC-06** | Las dependencias de backend se registran como **B-01…B-10 / BE-01…BE-10**, tareas separadas y **NO autorizadas**. | El usuario prohibió modificar backend, migraciones y OpenAPI. | `tasks.md` las lista como bloqueos externos, no como tareas ejecutables del frontend. |
| **DEC-07** | Ubicación de la documentación: `sgt-siaaf/specs/003-frontend-titulacion/`. | Decisión explícita del usuario. | Cuatro archivos: `clarify.md`, `specify.md`, `plan.md`, `tasks.md`. |
| **DEC-08** | No se usa Git por ahora. | Instrucción explícita del usuario. | No hay ramas, commits ni PR en este trabajo. |
| **DEC-09** | No se instalan dependencias. | Instrucción explícita del usuario. | El plan propone dependencias; la instalación queda para la fase de implementación autorizada. |
| **DEC-10** | No se fusiona ni se usa la "feature 002 demo". | No existe en el repositorio; la guía advierte que no está mergeada. | No se citan endpoints ni pantallas de esa demo. |
| **DEC-11** | Se aprueban los nuevos prototipos **A** (`SGT_SIAAF_Prototipo_HTML_CSS_JS/SGT_SIAAF_Prototipo_Web/`) y **B** (`SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/SGT_SIAAF_Errores_HTML_UNL/`) como **referencia visual y de comportamiento, no normativa**. Se conservan en su ubicación original; no se copia su HTML/CSS/JS a la implementación React. | Decisión del usuario (auditoría 2026-11-04). | lay-and-etiqueta di la UI en `specify.md` §3 y en la matriz de correspondencia; la SDD y el OpenAPI mandan. |
| **DEC-12** | La numeración oficial de vistas es la de la SDD (V-01…V-09, `specify.md` §9). La numeración UI-01…UI-09 de prototipos y documentos visuales se documenta mediante **matriz de correspondencia** (`specify.md` §6.1), sin renumerar. | Conserva trazabilidad de IDs y evita reescribir tareas y requisitos. | La documentación visual referencia la numeración UI con su equivalencia SDD. |
| **DEC-13** | Los estados HTTP **409, 412 y 428** NO se implementan como funcionalidad confirmada. Se documentan como **escenarios propuestos**, condicionados a la definición y autorización del backend (B-11/BE-11: ETag/`If-Match` y códigos de conflicto). El OpenAPI vigente no los declara. | El contrato OpenAPI declara solo `200`; sin respaldo de backend un 409/412/428 es un estado no respaldado. | El kit de errores (prototipo B) se documenta como referencia visual; su resignación al código es tarea bloqueada (FE-T1213, estado Bloqueada). |
| **DEC-14** | En V-03 se mantiene `carrera_id` como dato obligatorio conforme al contrato vigente (`POST /expedientes/`). `carrera_id` (carrera) y `opcion_titulacion` (modalidad de titulación) son **conceptos distintos** y no deben confundirse. Las opciones identificadas por el análisis secundario (NotebookLM, **referencia no normativa**) son: **Trabajo de Integración Curricular** (ordinaria) y **Examen Complexivo** (excepcional), con condiciones de elegibilidad registradas como **hipótesis pendientes de contraste directo con el Reglamento de Régimen Académico (RRA-UNL)** — arts. 39, 40, 212, 216 y 233 señalados (fuente primaria no presente en el repo; **no verificada**). **Proyecto de Emprendimiento: no confirmado** por la normativa consultada; no se incorpora como opción válida mientras exista esa situación. **No se implementa** selector, reglas de elegibilidad, campos ni endpoints: la implementación queda **pendiente de decisión humana, validación del RRA-UNL y disponibilidad de contrato backend aprobado** (campo `opcion_titulacion`/BE-06 solo como dependencia de backend a solicitar, **no autoriza a modificar el backend**). | Decisión del usuario (corregida en MOMENTO 2, 2026-11-04); jerarquía normativa: fuente primaria institucional > referencias secundarias > prototipo. | V-03 continua exigiendo `carrera_id` UUID (BE-10). El detalle completo (conocido/pendiente/necesarios del frontend/ausentes del backend/decisión requerida) queda en `specify.md` §9.2; tareas que lo citan: FE-T301, FE-T302. |
| **DEC-15** | Se **autoriza** el uso de las 5 mascotas PNG originales del prototipo B (`assets/img/mascota-{401,403,404,500,503}.png`) en `frontend/public/assets/mascotas/`, exclusivamente como **recursos gráficos complementarios e ilustrativos**, **no** como logotipo oficial de la UNL ni sustituto de su identidad corporativa. Condiciones vigentes: (1) no usar el logo «unl» recreado conceptualmente como oficial; (2) no afirmar licencias o autorizaciones institucionales no documentadas; (3) conservar trazabilidad de procedencia (ver `frontend/docs/assets-mascotas.md`); (4) mantener los criterios de accesibilidad/optimización/contraste de FE-T1214. El `README.md` del prototipo B fue **actualizado** (no reescrito) para reflejar esta autorización, conservando íntegra la advertencia original de que son "ilustraciones generadas" que no sustituyen marca oficial aprobada. | Autorización explícita del usuario (2026-11-05), posterior al hallazgo del bloqueo documentado en el propio README del prototipo B durante la revisión previa de F2.5. | FE-T1214 (Hecha): mascotas 403/404 integradas visualmente (`NoHabilitadoPage`, `NotFoundPage`); 401/500/503 copiadas y documentadas, sin integración visual aún (no existen páginas independientes para esos códigos, por diseño — DEC-13 y `08_UI_ERROR_STATES_SPEC.md`). |

---

## 4. Clarificaciones cerradas

| ID | Pregunta | Resolución | Evidencia |
|----|----------|------------|-----------|
| **CL-01** | ¿Qué vistas entran? | Las 9 vistas de `GUIA_VISTAS_TITULACION.md`: 01 Login, 02 Dashboard estudiante, 03 Crear solicitud, 04 Expediente/requisitos, 05 Crear petición, 06 Seguimiento petición, 07 Bandeja funcionario, 08 Detalle funcionario, 09 Estado no habilitado. | Guía de vistas; referencias `00…09`. |
| **CL-02** | ¿Qué clasificación tiene cada vista? | V-01 IF, V-02 CD, V-03 IP, V-04 IP, V-05 IP, V-06 IP, V-07 PB, V-08 IP, V-09 IP. (IF=funcional, IP=parcial, PB=pendiente de backend, CD=conceptual). | Auditoría ETAPA A/B; código real. |
| **CL-03** | ¿Autenticación? | JWT local únicamente (`POST /api/v1/auth/token/`). Sin SAC, OAuth2, OIDC, TOTP ni QR. Sin endpoint de refresh ni logout. | `authentication/adapters/serializers.py`; OpenAPI. |
| **CL-04** | ¿Claims del token? | Solo `cedula` y `roles`. **No** hay `carrera`, `facultad` ni `nombre`. | Serializer JWT real. |
| **CL-05** | ¿Estados de expediente confirmados? | `BORRADOR`, `ENVIADA`, `EN_VERIFICACION`, `OBSERVADA`, `INFORME_EMITIDO`, `DECLARADA_APTA`. `CANCELADA` aparece en el enum del contrato pero **no se usa** en el flujo implementado. | `expedientes/adapters/models.py`; OpenAPI `EstadoEnum`. |
| **CL-06** | ¿Estados de petición confirmados? | `PENDIENTE`, `SOLICITADO`, `CARGADO`, `VERIFICADO`, `OBSERVADO`. `LEGALIZADO` aparece en el enum pero **no se usa** en el flujo implementado. | `peticiones/adapters/models.py`; OpenAPI `EstadoPeticionEnum`. |
| **CL-07** | ¿Roles confirmados? | `ESTUDIANTE`, `SECRETARIA_CARRERA`, `SECRETARIO_ABOGADO`, `ANALISTA_APOYO`, `DECANO`, `DIRECTOR_CARRERA`, `ADMINISTRADOR`. `RESPONSABLE_DEPENDENCIA` aparece en el enum pero **no tiene celdas RBAC**. | `RBAC_MATRIX` en `permissions.py`. |
| **CL-08** | ¿Permisos del checklist para estudiante? | El `GET /api/v1/expedientes/{id}/checklist/` solo está permitido a `SECRETARIO_ABOGADO`, `ANALISTA_APOYO` y `ADMINISTRADOR`. El estudiante recibe 403. | `ChecklistListViewSet` + matriz RBAC. |
| **CL-09** | ¿Existe `GET /api/v1/peticiones/{id}/`? | **No.** Solo existen `POST /peticiones/{id}/solicitar-emision/`, `POST /peticiones/{id}/documento/` y `GET /peticiones/{id}/documento/` (y `.../documento/{version}/`). El detalle de petición solo llega anidado en `GET /api/v1/expedientes/{id}/`. | `config/urls.py`; views de peticiones. |
| **CL-10** | ¿Existe `GET /api/v1/expedientes/` (lista)? | **No.** Solo `POST /api/v1/expedientes/` (crear) y `GET /api/v1/expedientes/{id}/` (detalle). La bandeja es `GET /api/v1/expedientes/bandeja/`. | `config/urls.py`; views. |
| **CL-11** | ¿La bandeja muestra todos los estados? | No para todos los roles. La bandeja filtra por rol: `ESTUDIANTE` ve `BORRADOR`/`OBSERVADA`; `SECRETARIO_ABOGADO` y `ANALISTA_APOYO` ven `ENVIADA`/`EN_VERIFICACION`/`OBSERVADA`; `DECANO` ve `INFORME_EMITIDO`; `ADMINISTRADOR` ve todos los estados en curso; `SECRETARIA_CARRERA` y `DIRECTOR_CARRERA` no tienen expedientes asignados. | `expedientes/adapters/views.py` `MAPA_INTERVENCION_POR_ROL`. |
| **CL-12** | ¿Hay endpoint de catálogo de carreras? | **No.** `POST /expedientes/` recibe `carrera_id` (UUID); no hay catálogo público. | OpenAPI; views. |
| **CL-13** | ¿Hay endpoint de perfil `/me`? | **No.** No hay perfil de estudiante ni datos de carrera/facultad en el token. | `config/urls.py`; serializer JWT. |
| **CL-14** | ¿Hay CORS configurado? | **No** de forma explícita para el frontend. Es dependencia de backend (BE-08). | Configuración Django; auditoría. |
| **CL-15** | ¿La UI puede "simular" datos? | No. Las vistas sin backend se muestran como no habilitadas, con estado vacío explicativo y sin datos falsos que parezcan reales. | P-01 (simulación) y jerarquía de autoridad. |
| **CL-16** | ¿Se puede modificar el OpenAPI? | No. Las discrepancias se documentan; el frontend se adapta al comportamiento real. | Instrucción del usuario. |
| **CL-17** | ¿Se pueden añadir endpoints? | No. Cualquier necesidad se registra como BE-01…BE-10. | Instrucción del usuario. |
| **CL-18** | ¿La numeración de principios? | Se usa `P-XX` para la constitución. Las referencias `C-XXX` detectadas se registran como **pendientes de normalización**, sin renumerar. | Constitución; auditoría. |
| **CL-19** | ¿Evidencia de pruebas del backend? | 473 descubiertas / 460 pasadas / 13 fallidas / 0 errores / 0 omitidas / 93% cobertura. Los 13 fallos son por `pypdf` ausente en `test_pdf_generator.py`. | Ejecución ETAPA B. |
| **CL-20** | ¿Se cita el contenedor `sgt-siaaf-test` con 612 pruebas? | **No.** Corresponde a otro proyecto (`001-registro-solicitud-aptitud`, settings development, gunicorn). | Verificación ETAPA B. |
| **CL-21** | ¿Cuál es el estado real del frontend al 2026-11-04? | Snapshot inicial (auditoría): F0 ≈ 80% completado: lint ✅, typecheck ✅, build ✅ (12 chunks lazy), pruebas 23/24 (1 falla en `AppLayout.test.tsx`). FE-T001…T007 y FE-T009 cumplen sus criterios con evidencia; FE-T008 en curso (test fallido + logout TODO/F1); FE-T010 pendiente (README = plantilla Vite). **Actualizado tras cierre de F0 (mismo día):** FE-T001…T010 y FE-T1210 Hechas; D-FE-01…D-FE-04 resueltos; lint/typecheck/build ✅, pruebas 24/24. Las 9 vistas siguen siendo stubs; `src/api/` y handlers MSW siguen vacíos; sin guards — correctamente fuera del alcance de F0 (ver FE-T011…T017, F1). | Ejecución `npm run lint/typecheck/build/test` (2026-11-04); inventario de `frontend/src/**`. |
| **CL-22** | ¿El OpenAPI declara 409/412/428/503? | **No.** Todas las operaciones declaran solo `'200'`. 400/401/403/404/500 ocurren por semántica DRF de facto; 409/412/428 carecen de respaldo (requieren BE-11). 503 es responsabilidad de infraestructura. | `backend/openapi.yaml` (verificado 2026-11-04); `grep` de códigos. |
| **CL-23** | ¿Cubren los prototipos las 9 vistas? | Prototipo A: cubre las 9 (más extras: Historial, Mis tareas, Consultas, modales Ayuda/Elegibilidad). Prototipo B: 8 estados de error (401/403/404/409/412/428/500/503) + `acceso.html` (maqueta visual de V-01 con campos deshabilitados). | Inventario recursivo 2026-11-04. |

### 4.1 Evidencia de pruebas del backend

| Ejecución | Pruebas | Contexto |
|-----------|---------|----------|
| Original | 464 | `testpaths=["src/apps"]`. |
| Ampliada | 494 | +26 de `src/core/tests` +4 de `tests/e2e` (excluidas por defecto). |
| Actual (post Sprint S1) | 473 descubiertas / 460 pasadas / 13 fallidas / 0 errores / 0 omitidas / 93% cobertura | Incluye +4 smoke de admin y adiciones RBAC/pruebas. |
| Contenedor `sgt-siaaf-test` | 612 | **Otro proyecto** (`001-registro-solicitud-aptitud`, `config.settings.development`, gunicorn). **No se cita.** |

Los 13 fallos corresponden a `resoluciones/tests/test_pdf_generator.py` por ausencia de `pypdf` en el entorno de pruebas. Se aceptan como deuda de entorno (DEC-05); no afectan al frontend ni al contrato.

---

## 5. Supuestos

| ID | Supuesto | Consecuencia si es falso |
|----|----------|--------------------------|
| **AS-01** | El backend se desplegará en un origen distinto al frontend y se habilitará CORS (BE-08). | Sin CORS, el frontend no puede consumir la API en navegador; se requiere proxy de desarrollo o cambio de backend. |
| **AS-02** | El frontend se sirve como SPA estática con `VITE_API_BASE_URL` configurable. | Si se sirve bajo subruta, debe ajustarse `base` de Vite y el `basename` del router. |
| **AS-03** | El access token dura lo que configure SimpleJWT (por defecto 60 min) y no hay refresh. | Al expirar, el usuario debe volver a iniciar sesión; la UI lo informa. |
| **AS-04** | Los roles del token son la única fuente de autorización de UI. | Si cambian roles en backend, la UI debe revalidar en cada petición (el servidor sigue siendo la autoridad). |
| **AS-05** | Las referencias visuales son orientativas; no hay assets finales (logos, tipografías licenciadas). | Se usan placeholders y tokens; la sustitución es tarea de diseño. |
| **AS-06** | El navegador objetivo es Chromium/Firefox/Safari modernos (ES2020+). | Navegadores antiguos no están soportados. |
| **AS-07** | El backend no expone documentación interactiva autenticada para el frontend. | El cliente se tipa manualmente desde el OpenAPI y el código. |
| **AS-08** | No hay requisito de SSR ni SEO. | Se usa Vite SPA, sin Next.js. |
| **AS-09** | No hay i18n multi-idioma; la interfaz es en español. | Textos centralizados para facilitar traducción futura, pero sin framework i18n. |
| **AS-10** | No hay notificaciones en tiempo real (WebSocket/SSE). | Las notificaciones internas se consultan por polling o al cargar la vista. |

---

## 6. Preguntas abiertas

Estas preguntas **no bloquean** la redacción de la especificación, pero deben resolverse antes de implementar la vista afectada. Se registran con propietario sugerido y valor por defecto.

| ID | Pregunta | Vista afectada | Valor por defecto si no se responde | Propietario |
|----|----------|----------------|--------------------------------------|-------------|
| **PQ-01** | ¿URL/base del backend por entorno (`dev`, `test`, `prod`)? | Todas | `VITE_API_BASE_URL` obligatoria; sin valor por defecto en producción. | DevOps / Backend |
| **PQ-02** | ¿Se dispondrá de catálogo de carreras antes de implementar V-03? | V-03 | La vista pide `carrera_id` manual (UUID) o queda bloqueada hasta BE-10. | Backend / Producto |
| **PQ-03** | ¿El estudiante debe ver el checklist? | V-04 | Se muestra solo la lista de peticiones anidadas; el checklist queda como "no disponible para su rol" (403 esperado). | Producto / Backend (BE-04) |
| **PQ-04** | ¿Se habilitará `GET /peticiones/{id}/`? | V-06, V-08 | La vista usa los datos anidados del expediente y refresca el detalle completo. | Backend (BE-02) |
| **PQ-05** | ¿Se habilitará refresh/logout? | V-01, layout | Sin refresh: re-login al expirar. Sin logout de servidor: el cliente borra el token. | Backend (BE-03) |
| **PQ-06** | ¿Dónde se almacena el token? | V-01 | `sessionStorage` (se borra al cerrar pestaña), con advertencia de riesgo XSS. | Seguridad / Frontend |
| **PQ-07** | ¿Se requiere modo demo visible? | Todas | Sí: banner "Entorno de demostración" cuando `VITE_DEMO_MODE=true`, conforme P-01. | Producto |
| **PQ-08** | ¿Se requiere descarga de PDF con nombre original? | V-04, V-06, V-08 | Sí; usar `Content-Disposition` si está disponible; si no, nombre genérico. | Backend |
| **PQ-09** | ¿Se requiere firma electrónica en frontend? | V-09 | No. La firma es externa (FirmaEC) y el frontend solo carga el PDF firmado. | Producto |
| **PQ-10** | ¿Se requiere auditoría visual de acciones? | V-07, V-08 | No en el MVP; el backend ya registra trazabilidad. | Producto |
| **PQ-11** | ¿Se debe mostrar `CANCELADA` / `LEGALIZADO`? | V-04, V-06, V-08 | No, porque no se producen en el flujo real; se documentan como estados no soportados. | Backend |
| **PQ-12** | ¿Se implementará V-09 (estado no habilitado) como página independiente o como estado dentro de cada vista? | V-09 | Página independiente en `/no-habilitado`, reutilizable por guardas. | Frontend |
| **PQ-13** | ¿Cómo se valida la elegibilidad por opción de titulación (Trabajo de Integración Curricular ordinaria; Examen Complexivo excepcional)? | V-03 | La UI **no** implementa lógica de elegibilidad. Condiciones preliminares registradas en `specify.md` §9 (V-03) deben contrastarse contra el texto vigente del **RRA-UNL** antes de cualquier regla de UI. Mientras el backend no exponga opciones/elegibilidad (BE-06), V-03 no muestra selector de opciones. | Producto / Normativa UNL |
| **PQ-14** | ¿El backend declarará el paquete de conflictos 409/412/428 (`ETag`/`If-Match`) que el prototipo B representa? | Transversal (formularios) | No se implementan como confirmados; los inline-alerts quedan en la especificación 08 como escenarios propuestos (BE-11). | Backend / Producto |

---

## 7. Contradicciones e inconsistencias detectadas

No se resuelven silenciosamente. Se documentan y se aplica la jerarquía de autoridad.

| ID | Inconsistencia | Fuente A | Fuente B | Tratamiento |
|----|----------------|----------|----------|-------------|
| **INC-01** | `CANCELADA` en el enum de estado de expediente, pero sin transición implementada. | `openapi.yaml` `EstadoEnum` | Código de `expedientes` | Se tipa el enum completo, pero la UI no ofrece acciones que produzcan `CANCELADA`; se muestra solo si el backend lo devolviera. |
| **INC-02** | `LEGALIZADO` en el enum de petición, pero sin transición implementada. | `openapi.yaml` `EstadoPeticionEnum` | Código de `peticiones` | Igual que INC-01: badge soportado, sin acción de UI. |
| **INC-03** | `RESPONSABLE_DEPENDENCIA` en el enum de dependencia/rol, sin celdas RBAC. | `openapi.yaml` | `RBAC_MATRIX` | No se usa para guardas ni para asignación de vistas. |
| **INC-04** | El contrato declara `GET /api/v1/expedientes/{id}/checklist/`, pero no hay prueba de integración de ese endpoint (solo celda RBAC unitaria). | OpenAPI | Pruebas backend | El frontend lo consume; se marca como endpoint con cobertura de prueba insuficiente. |
| **INC-05** | El schema `ChecklistVerification` tipa `requisito` como `integer`, pero el serializer real puede devolver el id del requisito como UUID/entero según modelo. | OpenAPI | Serializer real | El cliente tipa como `string \| number` y normaliza; no se modifica OpenAPI. |
| **INC-06** | `Subsanacion` y `CargarDocumento` declaran respuesta con `archivo` tipo `uri`, cuando la operación real devuelve metadata del documento. | OpenAPI | Serializers de peticiones/checklist | El cliente tipa la respuesta real (`DocumentoEntregado`) y documenta la discrepancia. |
| **INC-07** | La guía de vistas menciona una "feature 002 demo" no presente. | `GUIA_VISTAS_TITULACION.md` | Repositorio | No se usa; se documenta como referencia externa no disponible. |
| **INC-08** | `FRONTEND_IMPLEMENTATION_PLAN.md` está vacío (0 B). | Archivo | Resto de especificaciones | No se usa como fuente; se ignora. |
| **INC-09** | Las referencias visuales están en carpeta `eferencias-visuales` (typo). | Sistema de archivos | Guía | Se usa la ruta real; se documenta el typo. |
| **INC-10** | La constitución usa `P-XX`, pero hay referencias `C-XXX` en documentos derivados. | Constitución | Documentos | Se mantiene `P-XX`; `C-XXX` queda pendiente de normalización. |
| **INC-11** | El informe de implementación S1 reporta D-01/D-02 resueltos y D-03 parcial; D-04 sigue abierto. | `S1_INFORME_IMPLEMENTACION.md` | Código actual | Se refleja en riesgos; D-04 no afecta al frontend directamente, pero puede mostrar estados inconsistentes. |
| **INC-12** | El contenedor `sgt-siaaf-test` reporta 612 pruebas, pero pertenece a otro proyecto. | Evidencia de contenedor | Repositorio actual | No se cita como evidencia de este proyecto. |
| **INC-13** | El OpenAPI declara `200` con "No response body" para `POST /auth/token/`, pero SimpleJWT devuelve `access` y `refresh`. | `openapi.yaml` | Serializer/real de SimpleJWT | El cliente tipa la respuesta real (`TokenPair`); no se modifica OpenAPI. |
| **INC-14** | Los prototipos A y B usan paletas propias (A: verde `#073b2d` + rojo `#c9081e`; B: rojo `#bb0920` + azul `#155bb7`) distintas de la paleta del design system (01_UI_DESIGN_SYSTEM: `#BF0811`/#4F8E3A/#004C7B/#0B3B24). El prototipo A declara su paleta como "inspiración en colores UNL", no como identidad oficial. | Prototipos A/B | `01_UI_DESIGN_SYSTEM.md` | Los valores del prototipo se registran como **colores observados**; los del design system como **valores propuestos**; ningún color institucional está todavía confirmado (`08…` tokens pending). No se cambian tokens vigentes por decisión visual. |
| **INC-15** | El wizard del prototipo A (V-03 por UI-04) selecciona `opcion_titulacion`; la SDD funcional exige `carrera_id` (UUID) porque el backend no tiene catálogo ni campo de opción. Además, "Proyecto de Emprendimiento" carece de respaldo normativo. | Prototipo A | SDD + normativa UNL | **MOMENTO 2 (corrección):** no se "descarta" el selector; queda **condicionado y pendiente** de DEC-14/B-06/RRA-UNL. Registra: la SDD manda para la implementación vigente; el wizard conserva su condición de referencia y la decisión sobre su implementación está sin aprobar. || **INC-16** | El prototipo A usa numeración UI-01…UI-09 distinta de la numeración V-01…V-09 de la SDD (mismo contenido, ids diferentes). | Prototipos | `specify.md` §9 | DEC-12: numeración SDD oficial; matriz de correspondencia en `specify.md` §6.1. |
| **INC-17** | `GUIA_VISTAS_TITULACION.md` describe la bandeja con `GET /api/v1/dependencias/{codigo}/peticiones` (endpoint de la feature 002 demo), mientras la matriz UI y la SDD usan `GET /api/v1/expedientes/bandeja/` (real). | GUIA | OpenAPI/urls.py | Regla DEC-10: no se usa el endpoint de la demo; la fuente funcional es la SDD. Pendiente de corrección al consolidar la GUIA. |
| **INC-18** | `07_UI_IMPLEMENTATION_MATRIX.md` señala `GET .../checklist/` "inoperable (P0)". Revalidado 2026-11-04: el endpoint existe en `config/urls.py` y deniega el rol `ESTUDIANTE` **por diseño** (CL-08); los hallazgos P0 heredados (D-01…D-04) están en §7.1. | Matriz UI | Código actual | La matriz se corrige: "operable para SECRETARIO_ABOGADO/ANALISTA_APOYO/ADMINISTRADOR; 403 para ESTUDIANTE (por diseño, BE-04)". |

### 7.1 Estado de defectos P0 (verificado en ETAPA B)

| Defecto | Estado | Evidencia | Impacto en el frontend |
|---------|--------|-----------|------------------------|
| **D-01** | **Resuelto** | S1-T02 `_raiz_almacenamiento_privado()` | Ninguno; las descargas usan almacenamiento privado. |
| **D-02** | **Resuelto** | S1 `guardar_archivo_privado` | Ninguno. |
| **D-03** | **Parcial** | `GET checklist` solo para `SECRETARIO_ABOGADO`, `ANALISTA_APOYO` y `ADMINISTRADOR`; `ESTUDIANTE` recibe 403. | V-04 muestra panel de limitación (BE-04). |
| **D-04** | **Abierto** | `resoluciones/services/emitir_informe.py:199-211` registra el estado nuevo como `estado_anterior`. | No mostrar historial de estados; solo el estado actual. |

### 7.2 Defectos del frontend detectados (auditoría 2026-11-04; cierre verificado 2026-11-04)

| Defecto | Estado | Evidencia | Impacto / tareas |
|---------|--------|-----------|------------------|
| **D-FE-01** | **Resuelto** | Causa raíz confirmada: el botón `aria-label="Abrir navegación"` solo es visible vía `@media (max-width:768px)`; jsdom fija `window.innerWidth=1024` y no implementa `window.matchMedia`, por lo que el elemento queda fuera del árbol de accesibilidad en la suite y su nombre accesible computado es `""` conforme a la especificación WAI-ARIA AccName para elementos ocultos (no es un bug de `dom-accessibility-api`/jsdom). Corregido únicamente en `AppLayout.test.tsx` (consulta por atributo en vez de rol/nombre para esa aserción de estado), sin desactivar validaciones. 4/4 tests de `AppLayout.test.tsx` + axe pasan. | FE-T008 cerrada como Hecha. |
| **D-FE-02** | **Resuelto** | `frontend/src/index.css` eliminado; import retirado de `main.tsx`. CSS compilado 7.02 KB → 5.23 KB; sin `--accent`/`#root{...}` de la plantilla en `dist/assets/*.css`. | Tarea FE-T1210 cerrada como Hecha. |
| **D-FE-03** | **Resuelto** | `frontend/README.md` reemplazado por documentación real (requisitos, instalación, scripts, variables de entorno, tabla BE-01…BE-11, enlaces a `specs/003-frontend-titulacion/`). | FE-T010 cerrada como Hecha. |
| **D-FE-04** | **Resuelto** | `frontend/index.html`: `lang="es"`, `<title>SGT-SIAAF</title>`. | Tarea FE-T1210 cerrada como Hecha. |

---

## 8. Dependencias de backend (no autorizadas)

Se registran como bloqueos. **No se implementan en esta feature.** La numeración `B-01…B-10` se conserva y se mapea a `BE-01…BE-10` en `tasks.md`.

| ID | Dependencia | Vistas afectadas | Estado | Evidencia |
|----|-------------|------------------|--------|-----------|
| **B-01 / BE-01** | Endpoint de perfil `/me` o claims de carrera/facultad en el JWT. | V-02, V-03, V-04, V-05, V-06 | Ausente | Serializer JWT solo `cedula` + `roles`. |
| **B-02 / BE-02** | `GET /api/v1/peticiones/{id}/` (detalle) y/o `GET /api/v1/peticiones/` (lista). | V-06, V-08 | Ausente | `config/urls.py`. |
| **B-03 / BE-03** | Refresh token y logout de servidor. | V-01, layout | Ausente | OpenAPI/auth. |
| **B-04 / BE-04** | Permitir `GET checklist` al rol `ESTUDIANTE`. | V-04 | Denegado (403) | `RBAC_MATRIX`. |
| **B-05 / BE-05** | Perfil de estudiante (nombre, carrera, facultad). | V-02, V-03, V-04 | Ausente | Sin endpoint. |
| **B-06 / BE-06** | Campo `opcion_titulacion` en expediente/petición. | V-03, V-04 | Ausente | Modelos/serializers. |
| **B-07 / BE-07** | Campo `motivo` / `motivo_observacion` en respuestas de expediente. | V-04, V-08 | Parcial | Solo en request de observación/checklist. |
| **B-08 / BE-08** | CORS para el origen del frontend. | Todas | Ausente | Configuración Django. |
| **B-09 / BE-09** | Ampliar la bandeja para roles sin expedientes asignados (`SECRETARIA_CARRERA`, `DIRECTOR_CARRERA`) o para estados no cubiertos, si el producto lo requiere. | V-07 | Parcial (filtrado por rol) | `MAPA_INTERVENCION_POR_ROL` en `expedientes/adapters/views.py`. |
| **B-10 / BE-10** | Catálogo de carreras (`GET /carreras/`). | V-03 | Ausente | Sin endpoint. |
| **B-11 / BE-11** | Paquete de control de versiones/conflicto para formularios: declarar `409` (petición duplicada), `412` (versión desactualizada) y `428` (versión requerida) con `ETag`/`If-Match`, incluido mensaje diferenciado con `error.code`. | Formularios V-03/V-04/V-05/V-06 | Ausente del contrato | OpenAPI declara solo `200` (CL-22). Representado visualmente en el prototipo B (`409.html`, `412.html`, `428.html`). Mientras no exista, el frontend no implementa los inline-alerts correspondientes (FE-T1213 Bloqueada). |

---

## 9. Riesgos del frontend

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|----|--------|--------------|---------|------------|
| **RSK-FE-01** | Sin CORS (BE-08), la API no responde desde el navegador. | Alta | Alto | Proxy en Vite (`server.proxy`) para desarrollo; documentar BE-08 como bloqueo de producción. |
| **RSK-FE-02** | Token en `sessionStorage` expuesto a XSS. | Media | Alto | CSP, sanitización, no `dangerouslySetInnerHTML`, dependencias auditadas; documentar que la solución definitiva requiere cookies httpOnly (BE-03). |
| **RSK-FE-03** | Sin refresh (BE-03), sesión expira y se pierde el formulario. | Alta | Medio | Guardar borradores localmente en `sessionStorage`; aviso de expiración; re-login. |
| **RSK-FE-04** | Sin catálogo de carreras (BE-10), V-03 no puede completarse con UX real. | Alta | Alto | Campo UUID manual en modo técnico o vista bloqueada; no inventar catálogo. |
| **RSK-FE-05** | Sin `GET /peticiones/{id}/` (BE-02), V-06 depende del detalle del expediente. | Alta | Medio | Refrescar expediente completo; no simular detalle inexistente. |
| **RSK-FE-06** | El estudiante no puede ver checklist (BE-04), V-04 queda parcial. | Alta | Medio | Mostrar peticiones anidadas y mensaje de limitación. |
| **RSK-FE-07** | OpenAPI y código divergen (INC-05, INC-06). | Media | Medio | Tipos manuales basados en serializers reales; pruebas de contrato con MSW. |
| **RSK-FE-08** | D-04 (estado anterior mal registrado en informe) puede mostrar historial confuso. | Media | Bajo | No mostrar historial no soportado; solo estado actual. |
| **RSK-FE-09** | Assets visuales no finales. | Alta | Bajo | Tokens y placeholders; sustitución posterior. |
| **RSK-FE-10** | Deuda de pruebas backend (13 fallos `pypdf`). | Alta | Bajo | No afecta al frontend; se registra como contexto. |

---

## 10. Fuera de alcance (confirmado)

- Implementar código React, componentes, estilos o pruebas en esta etapa.
- Modificar backend, migraciones, modelos, serializers, views, permisos, settings, OpenAPI o contratos.
- Modificar la constitución, `specs/001-tramite-titulacion/` o cualquier documento existente.
- Instalar dependencias, crear `package.json` o ejecutar `npm install`.
- Implementar autenticación SAC, OAuth2, OIDC, TOTP, QR o firma electrónica en frontend.
- Implementar endpoints nuevos o "maquetas" que simulen datos del backend.
- Implementar funcionalidades de `CANCELADA`, `LEGALIZADO` o `RESPONSABLE_DEPENDENCIA` como si estuvieran soportadas.
- Desplegar, configurar CI/CD o crear contenedores.
- Fusionar la "feature 002 demo".

---

## 11. Condiciones de cierre de esta fase

1. Los cuatro documentos existen en `specs/003-frontend-titulacion/`.
2. Cada vista tiene especificación, dependencias, criterios de aceptación y tareas atómicas.
3. Cada requisito de frontend tiene trazabilidad a una vista y, cuando aplica, a un endpoint y a una tarea.
4. Las dependencias de backend están registradas y marcadas como no autorizadas.
5. No se modificó ningún archivo preexistente.
6. Las preguntas abiertas tienen valor por defecto o propietario; ninguna bloquea la redacción.

---

## 12. Referencias

- `.specify/memory/constitution.md` — principios `P-01…P-18`.
- `specs/001-tramite-titulacion/specify.md` — RF, RNF, RN, CA, RBAC.
- `backend/openapi.yaml` — contrato (no modificar).
- `backend/src/config/urls.py` — rutas reales.
- `backend/src/apps/authentication/adapters/permissions.py` — `RBAC_MATRIX`.
- `backend/src/apps/expedientes/adapters/` — estados, creación, bandeja, detalle.
- `backend/src/apps/peticiones/adapters/` — peticiones, documentos.
- `backend/src/apps/verificacion/adapters/views.py` — checklist.
- `diseno-ui/ui/titulacion-v2/GUIA_VISTAS_TITULACION.md` — guía de vistas.
- `diseno-ui/ui/titulacion-v2/especificaciones/01…08_*.md` — referencia visual no normativa (08 = estados de error).
- `SGT_SIAAF_Prototipo_HTML_CSS_JS/SGT_SIAAF_Prototipo_Web/` — prototipo A (9 vistas), referencia visual y de comportamiento no normativa (DEC-11).
- `SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/SGT_SIAAF_Errores_HTML_UNL/` — prototipo B (kit de errores), referencia visual no normativa (DEC-11, DEC-13).
- `docs/sprint-S1/` — evidencia S1 (D-01…D-04).
- Reglamento de Régimen Académico UNL (RRA-UNL, arts. 39, 40, 212, 216, 233) — fuente normativa de elegibilidad por opción de titulación; **contrastación pendiente** (PQ-13). Las síntesis de análisis (p. ej. NotebookLM) son referencias secundarias.
