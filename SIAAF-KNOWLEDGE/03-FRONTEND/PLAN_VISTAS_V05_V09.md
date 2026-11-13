---
system: SGT-SIAAF
type: plan
status: active
source: auditoría del repositorio 2026-11-12 (código real, spec 003, diseño UI, backend)
last_updated: 2026-11-12
---

# Plan de implementación de las vistas pendientes (V-05 a V-09)

> **Autoridad:** `sgt-siaaf/specs/003-frontend-titulacion/` (`specify.md`, `clarify.md`, `plan.md`, `tasks.md`) manda sobre esta nota. Aquí se registran la auditoría, el reparto y el avance. Estado por tarea: `tasks.md`.
> **Ruta real de la spec:** `sgt-siaaf/specs/003-frontend-titulacion/`. `CLAUDE.md` y `AGENTS.md` la citan sin el prefijo `sgt-siaaf/`.

## 1. Inventario de vistas (código real, `a00e452`)

| Vista | Ruta | Archivo | Rol principal | Estado real | Referencia visual |
|---|---|---|---|---|---|
| V-01 Login | `/login` | `features/auth/LoginPage.tsx` | todos | **Implementada** (FE-T101–104) | doc 06, PNG 01 (conceptual) |
| V-02 Dashboard estudiante | `/estudiante` | `features/dashboard/StudentDashboardPage.tsx` | ESTUDIANTE | **Implementada** (FE-T201–206) | PNG 03 |
| V-03 Crear solicitud | `/estudiante/solicitud/nueva` | `features/solicitud/NuevaSolicitudPage.tsx` | ESTUDIANTE | **Implementada** (FE-T301–306) | PNG 04 |
| V-04 Expediente y requisitos | `/expedientes/:id` | `features/expediente/ExpedientePage.tsx` | todos con ámbito | **Implementada** (FE-T401–411) | PNG 05 |
| V-05 Gestión de peticiones | `/expedientes/:id/peticiones` | `features/peticiones/PeticionesPage.tsx` | ESTUDIANTE, SECRETARIA_CARRERA | **Stub → en implementación** (FE-T501–506) | PNG 05 (tabla y acciones), PNG 06 (modal; parcialmente conceptual) |
| V-06 Seguimiento de petición | `/expedientes/:id/peticiones/:peticionId` | `features/peticiones/SeguimientoPeticionPage.tsx` | ESTUDIANTE y funcionarios | **Stub** (FE-T601–605) | PNG 07 (conceptual) |
| V-07 Bandeja del funcionario | `/bandeja` | `features/bandeja/BandejaPage.tsx` | roles operativos | **Stub** (FE-T701–706) | **Implementada** (FE-T701–706, 2026-11-12) |
| V-08 Detalle del funcionario | `/bandeja/:id` | `features/bandeja/DetalleFuncionarioPage.tsx` | roles operativos | **Stub** (FE-T801–810) | **Implementada** (V-08a FE-T801–803 y 806–809; V-08b FE-T804–805; 2026-11-12) |
| V-09 No habilitado | `/no-habilitado` | `features/no-habilitado/NoHabilitadoPage.tsx` | todos | **Parcial**: 403 genérico con «Volver al inicio»; faltan motivo/dependencia `BE-xx`, volver atrás y contacto (FE-T901–904) | **Implementada** (FE-T901–904, 2026-11-12) |
| Estados 401/403/404/500/503 | — | `components/ui/*State`, `NotFoundPage` | todos | **Implementados** (F2.5) | prototipo B, doc 08 |

**Referencias revisadas:**
- Prototipo A (`SGT_SIAAF_Prototipo_HTML_CSS_JS/`).
- Prototipo B de errores (`SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/`).
- `diseno-ui/ui/titulacion-v2/`: guía, especificaciones 01–08 y PNG 01–09 en `eferencias-visuales/`.
- Documentación DP2.
- Notas de la bóveda.

Los prototipos son **solo referencia visual y de tono**: no se copia su HTML/CSS/JS (máxima 3 de `CLAUDE.md`).

## 2. Prioridad de las referencias y contradicciones

**Orden aplicado:**
1. Requisitos y decisiones (`specify`, `clarify`, `tasks`).
2. Matriz 07 corregida (MOMENTO 2).
3. Guía y PNG.
4. Prototipos.
5. Código existente.

| Contradicción | Fuentes | Resolución (ya decidida en la spec) |
|---|---|---|
| «Crear petición» con `POST {requisito}` | Guía §3 (PNG 06), prototipo A | **No existe** la creación manual: las peticiones se crean con el expediente. FE-T505 / CA-V05-05: aviso, sin botón |
| Bandeja `GET /dependencias/{codigo}/peticiones` | Guía §3 (PNG 08) | **No existe**; la bandeja real es `GET /expedientes/bandeja/` (matriz 07) |
| Estados «En revisión / En atención» | PNG 07 | No están en el enum real (CA-G-01); solo se muestran estados reales |
| Carga de documentos por funcionarios | RBAC `peticiones:documento` POST (ámbito ASIGNADO para varios roles) frente a `services/cargar_documento.py` | El servicio solo acepta al estudiante propietario o a la Secretaría de Carrera en peticiones asignadas a la Secretaría. La UI aplica la regla del servicio, la más estricta. **Registrada**; corregir la matriz es tarea de backend |
| `solicitar-emision` para SECRETARIA_CARRERA | El servicio lo permite, pero RBAC `peticiones` POST no la incluye (403) | La UI no lo ofrece. **Registrada** |

## 3. Arquitectura en la que se integran

- **Base técnica:** React 18 + TypeScript, Vite, React Router con rutas `lazy`, React Query (`lib/queryClient`) y cliente `api/client.ts` (Bearer y normalización de errores en `api/errors.ts`).
- **Errores:** `presentApiError` para estados de página y `describeAccionError` para mutaciones (mensaje real del backend, INC-21).
- **UI Kit** (`components/ui`): `Table` (escritorio y móvil), `Modal`, `FileUpload` (valida PDF con `lib/files`), `Badge`, `Alert`, estados `ErrorState`/`ForbiddenState`/`NotFoundState`.
- **Descarga autenticada:** `lib/download`.
- **Reglas de lint:** no se importan módulos internos de otra *feature*; se usa su *barrel* (`@/features/<feature>`). V-05 añade el *barrel* `features/expediente/index.ts`.
- **Sin dependencias nuevas.**

## 4. Matriz vista ↔ endpoint

| Vista | Endpoint (real) | Roles (RBAC + servicio) | Dependencia backend |
|---|---|---|---|
| V-05 | `GET /expedientes/{id}/` (peticiones anidadas) | por ámbito | BE-02 (sin `GET /peticiones/{id}/`), BE-11 (409/412/428) |
| V-05 | `POST /peticiones/{id}/solicitar-emision/` | ESTUDIANTE propietario; expediente BORRADOR/OBSERVADA; petición PENDIENTE | — |
| V-05 | `POST /peticiones/{id}/documento/` (multipart `archivo`, PDF ≤ 10 MB) | ESTUDIANTE propietario; SECRETARIA_CARRERA solo en peticiones de la Secretaría; estados PENDIENTE/SOLICITADO/OBSERVADO/CARGADO | — |
| V-05/V-06 | `GET /peticiones/{id}/documento/` y `/{version}/` | ESTUDIANTE, SECRETARIA_CARRERA, SECRETARIO_ABOGADO, ANALISTA_APOYO, DIRECTOR_CARRERA, ADMINISTRADOR (sin DECANO) | — |
| V-06 | Datos de la petición desde `GET /expedientes/{id}/`; descarga vigente `GET /peticiones/{id}/documento/` | por ámbito; descarga sin DECANO | **BE-02**, verificado el 2026-11-12: `PeticionDocumentalViewSet` existe en `views.py` pero **no está registrado** en `config/urls.py`, así que `GET /peticiones/{id}/` no es accesible. No hay listado de documentos ni de versiones, la descarga no informa la versión y la petición anidada no trae fechas. BE-07 (motivo) |
| V-07 | `GET /expedientes/bandeja/` (`page`, `page_size` ≤ 50; orden por fecha límite) | roles operativos; estados por `MAPA_INTERVENCION_POR_ROL` | **BE-09**, verificado el 2026-11-12: SECRETARIA_CARRERA y DIRECTOR_CARRERA reciben siempre una lista vacía y no hay filtros ni búsqueda en el servidor. **BE-01/BE-05**: solo UUID, sin nombres. **BE-11** no afecta, porque la bandeja es solo de lectura (FE-T1213 sigue bloqueada) |
| V-08 | `GET /expedientes/{id}/`, `GET /expedientes/{id}/checklist/`, `PUT /checklist/{id}/`, `POST /expedientes/{id}/observar/`, `POST /expedientes/{id}/iniciar-verificacion/`, `POST /informes/`, `POST /declaratorias/` | por rol, verificado el 2026-11-12: iniciar y observar, SECRETARIO_ABOGADO; evaluar, SECRETARIO_ABOGADO, ANALISTA_APOYO y ADMINISTRADOR; informe, solo SECRETARIO_ABOGADO (el servicio rechaza a la analista) y solo APTO; declaratoria, DECANO | BE-07; el perfil del estudiante no se anida. **Dependencia nueva sin ID:** no hay GET de informes ni de declaratorias ni descarga de sus PDF. Discrepancias RBAC/servicio en informe (ANALISTA_APOYO) y declaratoria (ANALISTA_APOYO) |
| V-09 | — (estado de interfaz; `?motivo=` y `&dependencia=BE-xx` en lista blanca) | todos | Muestra BE-01…BE-11 cuando se le indica; sin dependencia propia |

## 5. Reparto aprobado (DK-010, modalidad centralizada)

Aprobado por el responsable (R0yalCode) el **2026-11-12**.
- **Ejecución:** Claude Code realiza el trabajo material.
- **Commits:** el autor Git es el integrante **responsable** de la tarea (responsabilidad delegada, no autoría material) y R0yalCode es el committer.
- **Rotación:** E1-04 e I-3 fueron de backend; esta fase es de frontend.

| Integrante | Bloque | Tareas | Archivos principales | Rama prevista |
|---|---|---|---|---|
| **7777-C** | V-05 Gestión de peticiones | FE-T501–506 | `api/endpoints/peticiones.ts`, `features/peticiones/{PeticionesPage,accionesPeticion,queries,…}` | `feat/v05-gestion-peticiones` |
| **JuanCalopinoo** | V-06 Seguimiento de petición | FE-T601–605 | `features/peticiones/SeguimientoPeticionPage.tsx` (+ componentes propios) | `feat/v06-seguimiento-peticion` |
| **Dan1el17** | V-07 Bandeja y cierre de V-09 | FE-T701–706, FE-T901–904 | `features/bandeja/BandejaPage.tsx`, `features/no-habilitado/` | `feat/v07-bandeja`, `feat/v09-no-habilitado` |
| **JJOC3S** | V-08a Detalle: carga, checklist, observar, descargas, solo lectura e invalidación | FE-T801–803, FE-T806–810 | `features/bandeja/DetalleFuncionarioPage.tsx` y secciones | `feat/v08-detalle-funcionario` |
| **R0yalCode** | V-08b informe y declaratoria; transversal; plan | FE-T804–805, FE-T1001, FE-T1008 | secciones de V-08 propias, `ErrorBoundary`, invalidación | tras V-08a |
| Segunda ola | Calidad | FE-T1101–1105 | repartida al cerrar las vistas | — |

**Reglas de coordinación:**
- V-05 y V-06 comparten `features/peticiones/`. V-06 reutiliza `accionesPeticion.ts` (`presentarEstadoPeticion`, `tieneDocumento`) sin modificarlo, o lo amplía en un commit propio coordinado.
- V-08a y V-08b no editan a la vez la misma sección.

**Atribución (DK-010, enmienda 2026-11-12):** la asignación de este reparto por R0yalCode es autorización suficiente para la autoría Git de cada integrante; no se requiere notificación ni respuesta. La incidencia INC-DK010-01, sobre los commits de V-05 de 7777-C sin notificación, quedó **resuelta** por aclaración de política ([[DK010_REGISTRO_NOTIFICACIONES]]).

## 6. Plan por módulo y criterios

| Orden | Módulo | Depende de | Criterios de aceptación (resumen) |
|---|---|---|---|
| 1 | **V-05** | V-04 (detalle), F2 (UI Kit) | Lista accesible con estado y dependencia. Solicitar emisión con confirmación (200 → SOLICITADO). Carga de PDF validada (inválido no se envía; 201 → invalidación). Descarga autenticada. Errores 400/403/404 con el mensaje real. Aviso sin «crear petición». Pruebas MSW + axe |
| 2 | V-06 | V-05 | Resumen de la petición desde el expediente. Estados reales sin hitos inventados. Descarga vigente y por versión. 404 |
| 3 | V-07 | F1/F2 | Bandeja paginada real. Filtros de la página actual etiquetados. Vacíos y vencimientos. Navegación a V-08 |
| 4 | V-09 | — | Motivo y `BE-xx`, volver atrás, inicio por rol y contacto. Sin bucles de redirección |
| 5 | V-08 | V-07 | Acciones por rol y estado (RBAC real). Solo lectura. Invalidación |
| 6 | Transversal y calidad | todas | Según §15 y §16 de `tasks.md` |

**Definición de hecha** (`tasks.md` §19):
- `npm run lint`, `npm run typecheck` y `npm run test` en verde, más `npm run build`.
- Accesibilidad (axe) y comportamiento responsive.
- Sin datos simulados en producción.
- Sin registrar tokens ni datos personales.

## 7. Avance y evidencia

Se actualiza al cerrar cada bloque.

| Bloque | Responsable | Commits | Validación |
|---|---|---|---|
| Plan (esta nota) | R0yalCode | commit `docs(frontend)` de esta nota | — |
| V-05 | 7777-C | ver `tasks.md` §10 | ver `tasks.md` §10 |
| V-06 | JuanCalopinoo | ver `tasks.md` §11 | ver `tasks.md` §11 (limitada por BE-02) |
| V-07 | Dan1el17 | ver `tasks.md` §12 | ver `tasks.md` §12 (limitada por BE-09) |
| V-09 | Dan1el17 | ver `tasks.md` §14 | ver `tasks.md` §14 |
| V-08a | JJOC3S | ver `tasks.md` §13 | ver `tasks.md` §13 |
| V-08b | R0yalCode | ver `tasks.md` §13 | ver `tasks.md` §13 (sin GET de resoluciones) |

## 8. Tareas transversales

| Tarea | Responsable | Estado | Evidencia |
|---|---|---|---|
| FE-T1001/FE-T1008: ningún 401 se pierde en la inicialización | R0yalCode | Integrada en `develop` (`ab2f560`) | [[REGRESSION_TESTS]] |
| Endurecer `Modal` (UI Kit) | R0yalCode | Rama `fix/modal-foco-estable` (pendiente de revisión) | `Modal.test.tsx` (+8); el código anterior falla 3 |

**`Modal`: causa raíz y alcance auditado (2026-11-12).**
- **Causa raíz:** el efecto dependía de `[open, onClose]`. Los cuatro padres pasan `onClose` en línea (`ExpedientePage`, `PeticionesPage` ×2, `DetalleFuncionarioPage`), así que cualquier re-render del padre con el diálogo abierto reiniciaba el foco. V-08b lo hizo visible y se retiró su parche provisional.
- **Corregido en el mismo cambio:** el retorno del foco a un elemento que ya no está en el documento.
- **Se mantiene, por decisión:** el foco inicial va al botón «Cerrar», el primer elemento enfocable. Es aceptable según WAI-ARIA y las pruebas existentes lo fijan.

**Tarea independiente propuesta, no implementada:** `ObservarDialog` (V-04) y `ResolucionesSection` (V-08b) conservan el texto escrito si se cierra y se vuelve a abrir el diálogo, porque el componente que guarda el estado sigue montado. `CargarDocumentoDialog` (V-05) se reinicia con `key`. Propuesta: reiniciar el estado al abrir, ya sea con `key` en el consumidor o con un reinicio explícito. Está fuera del alcance de `Modal`.

## Relacionado

[[ROUTES]] · [[MODULES]] · [[COMPONENTS]] · [[GIT_POLICY]] · [[DECISIONS_LOG]]
