# Análisis del proceso principal — SGT-SIAAF

## 1. Selección del proceso (TASK-DOC-020)

**Proceso seleccionado:** *Declaratoria de Aptitud Legal* (Art. 235 del Reglamento de Régimen Académico de la UNL), correspondiente a los flujos **FL-01 a FL-05** de `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §8.

**Justificación:**

1. Es el **único proceso con implementación backend completa y verificada**: los requisitos RF-001 a RF-012 que lo componen están todos en estado **IV** (implementado y verificado), según `DOCUMENTACION/01_ESPECIFICACION/REQUISITOS_FUNCIONALES.md`. Los procesos de Fase 2 (sustentación, RF-014/RF-015) y Fase 3 (SENESCYT, RF-016) son solo diseño preliminar, sin código — modelarlos en BPMN presentaría como "proceso" algo que no existe en ejecución, violando la regla de no presentar lo documentado-sin-implementar como terminado.
2. Es el proceso que define el **incremento funcional objeto de la Evaluación Sumativa 1** (backend Fase 1).
3. Involucra a **6 de los 8 roles** del sistema en una secuencia con actividades, decisiones y bucles reales (observación/subsanación), lo que lo hace representativo para un diagrama BPMN con múltiples lanes, en vez de un proceso trivial de una sola tarea.
4. Tiene **trazabilidad completa y verificable** a nivel de requisito, modelo, endpoint y prueba (`MATRIZ_TRAZABILIDAD.md`), lo que permite construir el diagrama citando una fuente concreta para cada actividad, sin inventar pasos.

## 2. Análisis previo al diagrama (TASK-DOC-021)

### 2.1 Participantes

| Lane | Rol(es) reales | Fuente |
|---|---|---|
| Estudiante | `ESTUDIANTE` | `specify.md` §6.1 |
| Dependencia emisora | `SECRETARIA_CARRERA` / `DIRECTOR_CARRERA` / `RESPONSABLE_DEPENDENCIA`, según el requisito solicitado (récord académico, prácticas, idioma B1, Tesorería) | `specify.md` §6.1; `docs/01-introduccion/actores.md` |
| Secretario/a-Abogado/a y Analista de Apoyo | `SECRETARIO_ABOGADO` (decisión final), `ANALISTA_APOYO` (apoyo en borrador, sin autoridad de emisión — RBAC se lo restringe) | `specify.md` §6.1 |
| Decano/a | `DECANO` | `specify.md` §6.1 |
| Sistema SGT-SIAAF | Motor de estados y notificaciones del backend (tareas automáticas: inicialización de peticiones, cálculo de plazo, numeración, notificaciones in-app) | Código real (`core`, `expedientes`, `notificaciones`) |

**Decisión de modelado (abstracción documentada):** el certificado del Director de Trabajo puede ser cargado directamente por el estudiante o por la Secretaría de Carrera (Opción A, `DEC-02` en `clarify.md`). Para mantener el diagrama legible, la actividad "Atender petición y cargar certificado" se modela una sola vez en la lane "Dependencia emisora"; la variante en que el propio estudiante carga el documento se documenta aquí en texto, no como una rama adicional en el diagrama, para no multiplicar nodos sin aportar información de proceso distinta (la actividad de negocio es la misma: cargar un PDF validado).

`DIRECTOR_CARRERA` y `ADMINISTRADOR` no participan en lanes propias de este diagrama: el primero actúa como una de las posibles "dependencias emisoras" (ya cubierto en esa lane); el segundo no tiene intervención en la ejecución de este proceso de negocio (es transversal/administrativo, fuera del flujo operativo FL-01→FL-05).

### 2.2 Eventos

- **Evento de inicio:** "Iniciar trámite de aptitud legal" (disparado por la decisión del estudiante de solicitar su declaratoria; precondición: sin expediente activo, `RF-001`).
- **Evento de fin:** "Aptitud legal declarada" (postcondición de `FL-05`/`RF-011`; cierre exitoso de la Fase 1 para ese expediente).

No se modelan eventos de fin alternativos (p. ej. abandono del trámite) porque `specify.md` no define ese camino para el MVP; el estado `CANCELADA` existe en el enum pero sin flujo que lo produzca (confirmado en `docs/auditoria/matriz-trazabilidad.md`, sección "Requisitos sin implementación declarada") — no se modela un camino que no tiene soporte real.

### 2.3 Actividades (verbo infinitivo + complemento)

Dieciséis tareas, listadas en el orden del flujo, cada una trazada a su RF/HU de origen (ver tabla completa en `DIAGRAMA_BPMN.md`): crear expediente, inicializar peticiones, solicitar emisión, notificar petición, atender petición y cargar certificado, enviar solicitud, registrar recepción y plazo, notificar inicio de verificación, evaluar checklist, registrar observación, notificar observación, subsanar documento, emitir informe legal, notificar informe, registrar declaratoria, notificar declaratoria final.

### 2.4 Decisiones (gateways)

1. **"¿Los cinco documentos están vigentes?"** (exclusiva) — corresponde a la validación interna de `RF-002`/`FL-01` paso 4 antes de permitir el envío formal. Si falta algún documento, el flujo regresa a la solicitud de emisión.
2. **"¿Todos los requisitos están verificados?"** (exclusiva) — corresponde a `RN-003`/`EX-007`: si hay al menos un requisito `OBSERVADO` o `PENDIENTE`, se bloquea la emisión del informe y se activa `FL-04` (observación/subsanación); si los 5 están `VERIFICADO`, continúa a `FL-03` paso 3 (emisión del informe).

### 2.5 Flujos y bucles

El proceso tiene **dos bucles reales**, ambos verificados en el código (máquina de estados del expediente):

- **Bucle de completitud documental**: mientras falten documentos vigentes, se repite "solicitar emisión → atender petición y cargar certificado" (estado `BORRADOR` persiste).
- **Bucle de observación/subsanación**: el expediente alterna `EN_VERIFICACION ⇄ OBSERVADA` hasta que el jurista verifica los 5 requisitos (`docs/01-introduccion/introduccion.md` ya documenta esta alternancia en el diagrama de estados textual).

### 2.6 Datos

Entidades que fluyen por el proceso (del modelo conceptual, `specify.md` §7): `ExpedienteTitulacion`, `PeticionDocumental`, `DocumentoEntregado`, `ObservacionAccionable`, `NotificacionInterna`, `InformeAptitud`/`DeclaratoriaAptitud` (nombradas como `InformeAptitud`/`DeclaratoriaAptitud` en el código real; `specify.md` las describe conceptualmente sin nombre de clase final). No se modelan como objetos de datos BPMN explícitos para no sobrecargar el diagrama; se referencian en el glosario de `DIAGRAMA_BPMN.md`.

### 2.7 Excepciones no modeladas en este diagrama (y por qué)

`EX-001` (token vencido), `EX-003` (IDOR) y `EX-009` (error 500 no mapeado, incluido el hallazgo INC-21 ya documentado en `HISTORIAS_Y_CASOS_DE_USO.md`) son excepciones **técnicas/de seguridad**, no pasos del proceso de negocio: no se modelan como actividades BPMN porque no son parte del camino de negocio que un analista de procesos representaría; se documentan en `DOCUMENTACION/01_ESPECIFICACION/HISTORIAS_Y_CASOS_DE_USO.md` §2, que es su lugar correcto.

### 2.8 Resultado del proceso

Expediente en estado `DECLARADA_APTA`, con informe legal (Providencia 590) y memorando de declaratoria (Memorando 162) persistidos, y notificaciones despachadas a Secretaría-Abogacía, Director de Carrera y estudiante (`FL-05`, postcondición).

## 3. Artefactos generados

- `diagramas/proceso_principal.bpmn` — fuente BPMN 2.0.2 editable (XML, abrible en herramientas como bpmn.io o Camunda Modeler).
- `diagramas/proceso_principal.svg` — representación visual derivada de las mismas coordenadas del archivo `.bpmn`.
- `DIAGRAMA_BPMN.md` — explicación del diagrama, leyenda y tabla de trazabilidad actividad↔requisito.
