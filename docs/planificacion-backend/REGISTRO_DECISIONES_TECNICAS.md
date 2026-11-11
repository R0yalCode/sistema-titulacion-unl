---
title: "Registro de decisiones técnicas"
subtitle: "Decisiones tomadas (DT) y decisiones pendientes de aprobación (DP) — backend"
date: 2026-11-11
---

# Registro de decisiones técnicas

Las **DT** son decisiones técnicas tomadas por el equipo de desarrollo dentro de su competencia (reversibles y justificadas). Las **DP** requieren aprobación del responsable del repositorio o de una autoridad institucional; mientras no se aprueben, las tareas que dependen de ellas quedan **bloqueadas** y no se implementan con supuestos.

## 1. Decisiones técnicas tomadas

### DT-01 — Orden de ejecución: seguridad → flujo → indicadores → modalidades
- **Contexto:** D01 ordena INC-01 → INC-03 (modalidades) → INC-04 (KPI). La auditoría encontró que el flujo de verificación es inalcanzable (H-01) y que modalidades está bloqueada normativamente (D09 §11).
- **Decisión:** E1 (INC-01) → E2 (flujo) → E4 (KPI no ambiguos) ∥ E3 (sesiones) → E5 (modalidades) cuando se desbloquee.
- **Alternativas:** seguir D01 al pie de la letra (descartada: E5 no puede empezar sin validación, y E4 depende de que E2 produzca datos reales).
- **Riesgo:** ninguno nuevo; el contenido de los INC se conserva.

### DT-02 — `SCOPE_ASIGNADO`: queryset en la lectura, servicio en la escritura
- **Contexto:** filtrar también el POST de carga con el ámbito asignado convertía el 403 documentado (rol no autorizado) en 404 y rompía dos pruebas de contrato.
- **Decisión:** las concesiones RBAC "asignado" se aplican al queryset solo en `GET peticiones:documento` (la descarga ya respondía 404 para lo ajeno). En la carga, el servicio exige `dependencia_emisora == SECRETARIA_CARRERA` para la Secretaría y responde **403**.
- **Semántica de "asignado":** `dependencia_emisora ∈ roles(usuario)` ∧ el expediente está en la carrera del usuario (o en su facultad si no tiene carrera); sin carrera ni facultad, no se concede nada.
- **Alternativas:** 404 también en la carga (descartada: cambio de contrato sin necesidad).
- **Riesgo:** dos puntos de control (mixin + servicio); ambos tienen pruebas.

### DT-03 — Tasa del throttle `mutante`: 30/minuto por usuario, contador compartido (provisional)
- **Contexto:** D01 pide un "429 tras exceder la tasa", pero no fija el valor.
- **Decisión:** 30/min por usuario, compartido entre todas las mutaciones, configurable con `MUTANT_THROTTLE_RATE`. Margen amplio para el trabajo humano (un funcionario no evalúa 30 ítems por minuto) que corta los bucles automáticos.
- **Pendiente:** ratificación del responsable (DP-16).

### DT-04 — Caché de throttling
- **Contexto:** no hay `CACHES` configurado, así que DRF usa `LocMemCache` por proceso.
- **Decisión:** no se cambia en este incremento (afectaría a todos los throttles y requiere infraestructura). Se documenta el riesgo R-05: con N workers de gunicorn, el límite efectivo es N veces la tasa.
- **Recomendación:** configurar `DatabaseCache` (sin dependencias) o Redis en `production.py`.

### DT-05 — Sesiones sin Redis/Celery
- **Contexto:** D06 propone Redis y Celery Beat, ausentes del stack.
- **Decisión:** usar la "alternativa simple" de D06 §11 (escritura de actividad como máximo cada 5 min por sesión) y el `jti` nativo de simplejwt (C-12).

### DT-06 — Series temporales portables
- **Decisión:** `TruncMonth` + relleno de meses vacíos en Python, en lugar de `generate_series` (exclusivo de PostgreSQL), para que las pruebas sigan corriendo en SQLite en memoria. Coste despreciable (≤ 24 elementos).

### DT-07 — Contrato tipado de `/dashboard/me/` y usuarios multirrol
- **Decisión:** listas `tarjetas[]`/`graficos[]`/`alertas[]` identificadas por id de KPI y `no_disponibles[]` con su motivo, en lugar del diccionario libre `secciones` de D05 (que impide tipar en OpenAPI). Para usuarios multirrol, el ámbito es la **unión** de los ámbitos de sus roles (igual que `ScopeFilterMixin`) y las tarjetas son la unión de las de cada rol, sin el "rol principal" de D05 (C-18).

### DT-08 — Búsqueda y exportación sin dependencias nuevas
- **Decisión:** búsqueda por `istartswith` sobre los números y la cédula (índices B-tree existentes); exportación **CSV** (librería estándar) y **PDF** con `reportlab` (ya es dependencia). Excel (`openpyxl`) y `pg_trgm` requieren autorización (DP-17).

### DT-09 — Gestión de usuarios por `/admin/`
- **Decisión:** no se crea una API de usuarios/roles mientras el Django admin cubra la operación (RQ-API-08). Se reevalúa si el frontend necesita gestionar usuarios.

### DT-10 — Fallo de integridad SHA-256 → HTTP 500
- **Decisión:** seguir D01 ("archivo corrupto → 500 + log"). Código semántico `documento_integridad_comprometida`; `logger.error` con ids (sin datos personales). El evento de auditoría queda para PLB-E1-05 (requiere migración de `choices`).
- **Alternativas:** 409 o 503 (descartadas: no es un conflicto del cliente ni una indisponibilidad transitoria).

### DT-11 — `SGTAutoSchema` para respuestas transversales
- **Decisión:** subclase mínima de `AutoSchema` (`core/adapters/openapi.py`) que añade 429 a las operaciones mutantes con `MutantOperationThrottle` y respuestas extra declaradas por vista (`openapi_respuestas_extra`). Evita reescribir `@extend_schema` en cada vista y mantiene `openapi.yaml` como salida generada.

### DT-12 — Fuente única de transiciones: `registrar_transicion()` (resuelve DP-22; **no autorizada para implementación**)
- **Contexto:** H-24 (la señal del expediente atribuye todo `ESTADO_CAMBIADO` al estudiante y duplica el evento del historial) y H-25 (el informe registra en el historial un estado anterior erróneo). Evidencia empírica: la e2e produce 8 eventos `ESTADO_CAMBIADO` para 6 transiciones.
- **Decisión (adoptada por el responsable como decisión técnica, 2026-11-11):** una única función de dominio `registrar_transicion(expediente, nuevo_estado, actor, origen)` en `expedientes`, invocada por todos los servicios que cambian el estado, dentro de su transacción:
  1. valida la transición contra una tabla de transiciones permitidas;
  2. captura el estado anterior **antes** de modificarlo;
  3. actualiza el expediente (`select_for_update` en el servicio llamador);
  4. crea `HistorialEstado` con `registrado_por = actor`;
  5. crea **un** `EventoAuditoria` `ESTADO_CAMBIADO` con `usuario = actor` y el rol con el que actuó.
- **Actor:** se pasa explícitamente desde la vista (el usuario autenticado de la petición); no se infiere del expediente ni del contexto global de la petición.
- **Señales:** la señal `post_save` del expediente deja de auditar transiciones (conserva `EXPEDIENTE_CREADO`); la señal de `HistorialEstado` deja de crear `ESTADO_CAMBIADO` para no duplicarlo. Los eventos de negocio (`CHECKLIST_EVALUADO`, `OBSERVACION_REGISTRADA`, `INFORME_EMITIDO`, `DECLARATORIA_REGISTRADA`…) se mantienen: describen actos distintos de la transición.
- **Garantías verificables:** prueba de arquitectura (ningún servicio asigna `expediente.estado` fuera de la función); prueba "1 transición = 1 `HistorialEstado` + 1 `ESTADO_CAMBIADO`, actor correcto"; los eventos existentes no se reescriben (son inmutables) y se documenta la fecha de corte.
- **Estado:** **implementada el 2026-11-11** con autorización expresa del responsable (PLB-E2-06); pendiente de su aprobación de fase.

## 2. Requerimientos ambiguos detectados

Ver `AUDITORIA_INTEGRAL_BACKEND.md` §7 (C-01…C-18). Los que afectan a la implementación inmediata se convierten en las DP siguientes.

## 3. Decisiones pendientes de aprobación

| ID | Decisión requerida | Quién decide | Opciones | Bloquea |
|---|---|---|---|---|
| **DP-01** | Cómo y quién inicia la verificación (`ENVIADA→EN_VERIFICACION`) | Responsable funcional / Secretaría-Abogacía | **Definida técnicamente — implementación no autorizada.** Criterio del responsable (2026-11-11, fuente secundaria, ver §4): acción explícita `POST /expedientes/{id}/iniciar-verificacion/` del SECRETARIO_ABOGADO. Pendiente: participación del ANALISTA_APOYO (DP-01b) | PLB-E2-01 (**P0**) |
| **DP-02** | Validación firmada de los arts. 39, 40, 212, 216 y 233 RRA-UNL (modalidades) | Secretaría General / Decanato / Jurídico | Checklist D09 §11 | Toda la etapa E5 |
| **DP-03** | Fuente de reprobaciones y tercera matrícula (¿mock SGA ampliado o integración real?) | Responsable + SGA | Ampliar `ISGALegacyPort` | RQ-MOD-03, KPI-MOD-06 |
| **DP-04** | Consulta y subsanación de observaciones por el estudiante | Responsable | **Parcialmente definida — implementación no autorizada.** Criterio del responsable (2026-11-11, fuente secundaria, ver §4): el estudiante consulta los requisitos observados, el motivo, la fecha y el estado de subsanación, y puede presentar una nueva versión. La subsanación **no** resuelve la observación: queda en revisión hasta que el SECRETARIO_ABOGADO verifique. Pendientes: DP-19 (plazo) y DP-20 (subsanación parcial) | PLB-E2-02a, E2-02b1/b2/b3 |
| **DP-05** | Acceso documental y competencias del jurista y del analista | Responsable / Secretaría-Abogacía | **Definida técnicamente para el jurista — implementación no autorizada; requiere AUT-01 (pendiente).** Criterio del responsable (2026-11-11, fuente secundaria, ver §4): SECRETARIO_ABOGADO con lectura y descarga de los 5 requisitos en su facultad. ANALISTA_APOYO **sin ampliación** hasta que se definan sus atribuciones (DP-05b) | PLB-E2-03, PLB-E2-05 |
| **DP-06** | Renovación de sesión: rotación+blacklist o sliding; y si el frontend la adopta (hoy `plan.md` §6 impone re-login) | Responsable | A / B | E3 |
| **DP-07** | Modelado de "dependencia" para RESPONSABLE_DEPENDENCIA (hoy el dominio de `dependencia_emisora` son los roles) | Responsable institucional | Catálogo de dependencias + asignación usuario↔dependencia | PLB-E7-01, KPI-DEP |
| **DP-08** | Cancelación de expediente: actor, estados de origen y efectos | Responsable funcional | — | PLB-E2-04 |
| **DP-09** | FirmaEC: verificación de firma, cadena y sellado | Responsable + TI UNL | Librería/servicio a autorizar | PLB-E7-02 |
| **DP-10** | ¿CANCELADA cuenta en el denominador de la tasa de culminación? | Responsable funcional | IK §7 recomienda excluirla e informarla aparte | KPI DEC-04/DIR-04/ADM-04 |
| **DP-11** | Catálogo de carreras/facultades (BE-10) | Responsable | Tabla propia o SGA | Nombres en KPI y filtros |
| **DP-12** | Lista de trabajo de SECRETARIA_CARRERA y DIRECTOR_CARRERA (hoy, bandeja vacía) | Responsable funcional | Estados por rol | PLB-E4-05 (parte) |
| **DP-13** | ¿Existen roles "Coordinador" o "Docente/Tutor" en el alcance? | Responsable institucional | — | Dashboards para esos roles |
| **DP-14** | ¿Un expediente OBSERVADO (plazo en pausa) cuenta como "plazo vencido"? | Responsable funcional | Excluir / incluir | KPI SEC-02/JUR-07/DIR-03 |
| **DP-15** | ¿Un expediente sin filas de checklist es "listo para informe"? | Responsable funcional | Exigir checklist completo | KPI JUR-04 |
| **DP-16** | Ratificar la tasa `mutante` (DT-03) | Responsable | 30/min u otra | — (ya configurable) |
| **DP-17** | Autorizar dependencias: `pypdf` (dev), `openpyxl`, `pg_trgm` | Responsable (CLAUDE.md, máxima 4) | — | PLB-E0-01, Excel, búsqueda difusa |
| **DP-01b** | ¿Puede el ANALISTA_APOYO iniciar la verificación? ("soporte operativo" no define el acto) | Secretaría-Abogacía | Sí / No | Celda RBAC de E2-01 (por defecto, **no**) |
| **DP-05b** | Atribuciones del ANALISTA_APOYO: hoy evalúa el checklist de forma **definitiva** y puede observar vía `PUT OBSERVADO`; D03 §2.3 y D07 dicen "solo borrador"; `SCOPE_BORRADOR` no se aplica en ningún sitio | Secretaría-Abogacía | (a) solo lectura; (b) evaluación en borrador que confirma el jurista; (c) mantener | PLB-E2-05 |
| **DP-18** | ¿El envío exige los 5 requisitos con documento? Hoy sí (422, T016; D07 §3.2). El criterio del responsable pide **no asumirlo** y contrastarlo con el procedimiento de observaciones | Responsable funcional + Art. 235 (texto primario) | (a) mantener la exigencia; (b) permitir el envío incompleto y que la falta se gestione como observación | Validación de `enviar_expediente` (sin cambio hasta decidir) |
| **DP-19** | Efecto de una observación sobre el plazo de 8 días: pausa (código actual en `POST /observar/`), reinicio o continuidad. Además, hoy `PUT /checklist/ OBSERVADO` **no** pausa: dos caminos con efectos distintos | Responsable funcional (ya pendiente en `ARTICLES_AND_PROVISIONS` #2) | Pausa / reinicio / continúa | PLB-E2-02c |
| **DP-21** | (N-07) La SECRETARIA_CARRERA puede subsanar (DEC-02, `subsanar_requisito.py`), pero el criterio de DP-04 solo contempla al estudiante y E2-02a no le concede la consulta de observaciones: o tiene la consulta, o pierde la subsanación | Responsable funcional | (a) concederle la consulta en `SCOPE_CARRERA`; (b) retirarle la subsanación; (c) mantener la situación actual, documentada | Celda de E2-02a para ese rol (excluida por defecto) |
| **DP-22** | (H-24, H-25) Fuente única del evento de transición y atribución del actor | Responsable | **Resuelta (DT-12, decisión técnica del responsable) e implementada el 2026-11-11 con autorización expresa** | PLB-E2-06 (definida, no autorizada); E2-01 y E2-02b3.1 deben usar `registrar_transicion()` |
| **AUT-01** | Autorizar el cambio de la celda **implementada** `peticiones:documento` GET para SECRETARIO_ABOGADO: `SCOPE_ASIGNADO` → `SCOPE_FACULTAD`. Valor vigente desde el commit `795d6a7` (2026-10-20). La matriz 6.2 de `sgt-siaaf/specs/001-tramite-titulacion/specify.md` (especificación funcional inmutable) **no define el GET de descarga**: solo el POST ("Asignado"). El valor actual es una derivación de implementación, no una celda aprobada | Responsable del repositorio | Conceder / denegar. **Pendiente: sin autorización expresa** | PLB-E2-03 |
| **AUT-02** | Autorizar la **nueva** celda `expedientes:iniciar_verificacion` POST = `{SECRETARIO_ABOGADO: SCOPE_FACULTAD}`, que amplía la matriz implementada (sin equivalente en la matriz 6.2 de la especificación) | Responsable del repositorio | **Concedida el 2026-11-11 por el responsable**, exclusivamente para la operación de inicio de verificación de PLB-E2-01. Se aplicará en la Fase 2, que espera la aprobación de la Fase 1 (E2-06) | PLB-E2-01 |
| **AUT-03** | Autorizar la **nueva** celda `expedientes:observaciones` GET = `{ESTUDIANTE: SCOPE_OWN, SECRETARIO_ABOGADO: SCOPE_FACULTAD, ADMINISTRADOR: ALLOW}` (ANALISTA según DP-05b; SECRETARIA_CARRERA según DP-21) | Responsable del repositorio | Conceder / denegar. **Pendiente** | PLB-E2-02a |
| **DP-20** | Subsanación parcial: con varias observaciones, ¿el expediente vuelve a EN_VERIFICACION tras subsanar cada ítem, o solo cuando todos los ítems observados estén subsanados? Hoy, tras la primera subsanación, el resto de ítems observados queda bloqueado (H-19) | Responsable funcional | (a) retorno cuando todos los ítems observados estén en revisión; (b) retorno por ítem, con mecanismo para subsanar los restantes; (c) otra. Sin opción preferida aprobada | **PLB-E2-02b3.2** (bloqueada); además, por R-07, el **despliegue** de PLB-E2-02b1 no puede preceder a E2-02b3.2 |

## 4. Revisión de DP-01, DP-04 y DP-05 (2026-11-11)

### 4.1 Naturaleza del fundamento

Las conclusiones aportadas por el responsable provienen de una **consulta en NotebookLM** sobre la normativa. Según `DISENO_FUNCIONAL_MODALIDADES_TITULACION.md` §1.1 y `SIAAF-KNOWLEDGE/11-REGULATORY/INSTITUTIONAL_FRAMEWORK.md`, ese análisis secundario **no constituye fuente normativa**, y el texto del RRA-UNL no está en el repositorio. Se registran, por tanto, como **criterio funcional del responsable** con fundamento secundario. Cada fila indica qué parte se apoya en una fuente citada del proyecto: Art. 235 (5 requisitos y 8 días laborables) y la plantilla de la Providencia N° 590 (recepción con fecha y hora; firmas del Secretario/a-Abogado/a y del Analista), ambas en estado "Citado (spec)" en `ARTICLES_AND_PROVISIONS.md`.

### 4.2 Matriz de decisión

**Estados de aprobación.** *Definida técnicamente*: especificada con suficiente detalle para implementarse; **no** equivale a *autorizada para implementar*, que solo se da con una indicación expresa del responsable. *Parcialmente definida*: una parte depende de decisiones pendientes. *Bloqueada*: no se implementa ni se simula. A 2026-11-11, **ninguna** parte de DP-01, DP-04 ni DP-05 está autorizada para implementarse.

| Decisión | Fundamento | Estado actual del backend | Cambios necesarios | Bloqueos | Estado de aprobación |
|---|---|---|---|---|---|
| **DP-01** Inicio de la verificación | Criterio del responsable (NotebookLM): competencia del SECRETARIO_ABOGADO con soporte del ANALISTA; acción explícita, nunca como efecto de un GET. Providencia 590 (citada): recepción con fecha y hora. D07 §3.5: evaluar/observar/informe exigen EN_VERIFICACION | Recepción ✔: `enviar_expediente` fija `fecha_recepcion` (fecha y hora), `numero_providencia` y el plazo. **No existe** `ENVIADA→EN_VERIFICACION` (H-01). **Ningún servicio crea las filas de `ChecklistVerification`** (H-17: el helper `_get_or_create_checklist_verification` no se usa; e2e y pruebas las crean a mano). `HistorialEstado` no se registra al enviar (H-23) | Servicio nuevo `expedientes/services/iniciar_verificacion.py` (transacción + `select_for_update`): valida ENVIADA y la facultad, crea de forma idempotente las 5 filas PENDIENTE (reutilizando el helper existente), ENVIADA→EN_VERIFICACION y notificación al estudiante, en una única transacción. La transición se registra con `registrar_transicion()` (DT-12): un `HistorialEstado` y un `ESTADO_CAMBIADO` con el actor autenticado, por lo que E2-01 requiere E2-06. Acción `iniciar_verificacion` en `ExpedienteViewSet` (hereda `MutantOperationThrottle`) + ruta + celda RBAC `expedientes:iniciar_verificacion` POST `{SECRETARIO_ABOGADO}`. Plazo: **sin cambios** (corre desde la recepción según RN-002 de specify 001, que cita el Art. 235; **el cómputo exacto requiere verificación directa de la fuente normativa primaria**, no disponible en el repositorio). No duplica nada: no hay otro endpoint con esta función | DP-01b (analista); DP-18 (completitud en el envío; no bloquea E2-01) | **Definida técnicamente** (SECRETARIO_ABOGADO como único actor, mundo cerrado). **Implementación no autorizada; requiere AUT-02 (celda nueva) y E2-06.** Analista: pendiente (DP-01b) |
| **DP-04** Consulta y subsanación de observaciones | Criterio del responsable (NotebookLM): el estudiante consulta los requisitos observados, el motivo, la fecha y el estado de subsanación, y presenta una nueva versión; la observación **no** se resuelve al cargar, queda pendiente hasta la verificación del jurista; acceso solo a lo propio | Consulta: el detalle muestra `estado_peticion=OBSERVADO`, pero **no** el motivo, la fecha ni el `checklist_verification_id`; `GET .../checklist/` → 403 para ESTUDIANTE (H-04). Subsanación: `subsanar_requisito` **marca `resuelta=True` al cargar** (contradice el criterio), devuelve el ítem a PENDIENTE (correcto) y el expediente a EN_VERIFICACION **tras la primera subsanación**, lo que bloquea el resto de ítems observados (H-19). La notificación de "subsanación recibida" va al **estudiante** con un texto dirigido al verificador (H-18). `POST /peticiones/{id}/documento/` acepta peticiones OBSERVADO y las pasa a CARGADO **sin** tocar la observación, el checklist ni el plazo: un camino paralelo que esquiva la subsanación (H-21). Plazo: `POST /observar/` pausa; `PUT /checklist/ OBSERVADO` **no** pausa (H-20) | (a) Endpoint de lectura `GET /expedientes/{id}/observaciones/` con `SCOPE_OWN` (+ juristas de la facultad): requisito, motivo, fecha, estado de subsanación, `checklist_verification_id` y `puede_subsanar`, **sin** datos internos (evaluador). Preferible a abrir el checklist completo al estudiante. (b) Modelo: campo `estado_subsanacion` en `ObservacionAccionable` (`PENDIENTE`, `EN_REVISION`, `ACEPTADA`, `REITERADA`) + `fecha_subsanacion` (migración aditiva; `resuelta` se mantiene por compatibilidad). (c) `subsanar_requisito`: pasar a EN_REVISION, sin `resuelta=True`. (d) `evaluar_checklist`: VERIFICADO → ACEPTADA + `resuelta=True`; OBSERVADO sobre un ítem EN_REVISION → REITERADA + nueva observación; ajustar la guarda `ObservacionYaExisteError` de `registrar_observacion`. (e) Notificación de subsanación al SECRETARIO_ABOGADO de la facultad. (f) `cargar_documento`: rechazar OBSERVADO (409/400) y remitir a la subsanación. (g) Unificar el efecto sobre el plazo de ambos caminos de observación | DP-19 (plazo), DP-20 (parcial). La migración (b) es una decisión técnica, no normativa | **Parcialmente definida**: (a) → E2-02a (requiere AUT-03), (b–d) → E2-02b3.1, (e) → E2-02b2 y (f) → E2-02b1 definidos técnicamente; (g) → E2-02c bloqueado (DP-19); subsanación parcial → E2-02b3.2 bloqueada (DP-20); Secretaría de Carrera → DP-21. **Implementación no autorizada** |
| **DP-05** Competencias del jurista y del analista | Criterio del responsable (NotebookLM): el SECRETARIO_ABOGADO lee y descarga los 5 requisitos de su facultad, verifica, observa con motivo y emite el informe legal; se distinguen verificación jurídica, legalización y declaratoria; el ANALISTA, solo con atribuciones justificadas. Providencia 590 (citada): informe con firma del Secretario/a-Abogado/a y del Analista | Checklist GET `facultad` ✔; evaluar y observar con control de facultad ✔; informe solo SECRETARIO_ABOGADO ✔ (`emitir_informe.py:67`); declaratoria solo DECANO ✔. **Descarga**: `peticiones:documento` GET = `SCOPE_ASIGNADO` → el jurista solo ve lo asignado a su rol (H-07). Analista: evalúa de forma **definitiva** y puede observar vía `PUT`; `SCOPE_BORRADOR` no se aplica en ningún sitio; RBAC `informes` le concede POST pero el servicio lo rechaza (H-22). Legalización: el estado `LEGALIZADO` existe pero **ningún servicio lo asigna** | (a) `RBAC_MATRIX["peticiones:documento"]["GET"]["SECRETARIO_ABOGADO"] = SCOPE_FACULTAD` (una celda; `get_scope_grants` ya traduce `facultad`) + pruebas IDOR (otra facultad → 404). (b) Sin cambios para el ANALISTA hasta DP-05b. (c) Documentar que la verificación jurídica (checklist + informe) no es la legalización (acto de la dependencia emisora sobre el documento, p. ej. el récord académico legalizado del Art. 235) ni la declaratoria (DECANO). No se implementa la legalización sin definición | DP-05b (analista); legalización sin definición institucional | **Definida técnicamente para el SECRETARIO_ABOGADO. Implementación no autorizada; requiere además AUT-01** (cambio de la celda implementada `peticiones:documento` GET, no definida en la matriz 6.2 de la especificación). Analista (DP-05b) y legalización: pendientes |

### 4.3 Contradicciones detectadas al contrastar

| ID | Contradicción | Fuentes |
|---|---|---|
| N-01 | El criterio de DP-05 amplía el ámbito de descarga del jurista. La celda afectada (`peticiones:documento` GET = `SCOPE_ASIGNADO`) es una **derivación de implementación**: la matriz 6.2 de la especificación aprobada solo define el POST ("Asignado") y no el GET de descarga | NotebookLM vs `permissions.py`; `specs/001` §6.2 |
| N-02 | D03 §2.3 y D07 restringen al ANALISTA a "borrador" (sin observar ni informe final); el código le permite evaluar en definitiva y observar vía `PUT` | D03, D07 vs `evaluar_checklist.py:149` |
| N-03 | El criterio pide no asumir que el envío exige los 5 requisitos; el código (T016), D07 §3.2 y la regla RN-001 lo exigen | NotebookLM vs `enviar_expediente.py`, D07 |
| N-04 | El criterio dice que la subsanación no resuelve la observación; el código la resuelve al cargar | NotebookLM vs `subsanar_requisito.py` |
| N-05 | D07 §3.3 permite subsanar desde la ruta de carga; el código tiene dos caminos (carga y subsanación) con efectos distintos | D07 vs `cargar_documento.py:91`, `subsanar_requisito.py` |
| N-06 | Dos caminos de observación (`POST /observar/` y `PUT /checklist/ OBSERVADO`) con efectos distintos sobre el plazo y el historial | `registrar_observacion.py:141` vs `evaluar_checklist.py` |
| N-07 | El criterio guarda silencio sobre la SECRETARIA_CARRERA, a la que el código (DEC-02) permite subsanar; se mantiene hasta nueva decisión → **DP-21** | NotebookLM vs `subsanar_requisito.py` |

### 4.4 Correspondencia decisión → tareas

| Decisión | Tareas que habilita | Tareas que bloquea mientras siga pendiente |
|---|---|---|
| DP-01 (definida) + AUT-02 + DP-22 | E2-01 | E2-01 sin AUT-02 |
| DP-01b | — | Inclusión del analista en E2-01 |
| DP-04 (parcial) (+ AUT-03 para E2-02a) | E2-02a, E2-02b1, E2-02b2, E2-02b3.1 | E2-02a sin AUT-03 |
| DP-05 (definida para el jurista) + AUT-01 | E2-03 | E2-03 sin AUT-01 |
| DP-05b | — | E2-05; inclusión del analista en E2-02a y E2-02b2 |
| DP-18 | — | Cambios en la precondición de envío (ninguno planificado) |
| DP-19 | — | E2-02c; efecto sobre el plazo de E2-02b3.2 |
| DP-20 | — | E2-02b3.2 y, por R-07, el despliegue de E2-02b1 |
| DP-21 | — | Celda de E2-02a para la SECRETARIA_CARRERA |
| DP-22 (DT-12, implementada) | E2-06 (hecha) | — |
