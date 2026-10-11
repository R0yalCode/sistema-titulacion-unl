# 03. Alcance del MVP, flujo inicial y etapas SDD

**Proyecto:** SGT-SIAAF — Sistema de Gestión del Trámite de Titulación integrado al SIAAF  
**Asignatura:** Desarrollo Basado en Plataformas  
**Carrera:** Computación  
**Institución:** Universidad Nacional de Loja  
**Responsable:** Integrante 3 — Alcance del MVP  
**Estado:** Propuesta inicial pendiente de aprobación del equipo y validación del docente.

## 1. Delimitación del proceso

### 1.1. Contexto

El trámite de titulación comprende distintas actividades académicas y administrativas, desde la preparación del trabajo de integración curricular hasta la sustentación y emisión del título. Abordar todas estas actividades en una primera versión incrementaría la complejidad del proyecto y dificultaría la definición de requisitos verificables.

Por este motivo, se propone delimitar el producto mínimo viable (MVP) a un subproceso específico: la solicitud y el seguimiento de la declaratoria de aptitud legal previa a la sustentación, tomando como referencia el artículo 235 del Reglamento de Régimen Académico de la Universidad Nacional de Loja.

Esta selección constituye una propuesta inicial y deberá confirmarse con el equipo y el docente.

### 1.2. Inicio y finalización

**Inicio:** el estudiante registra una solicitud de declaratoria de aptitud legal cuando considera que cumple los requisitos correspondientes y dispone de la documentación necesaria.

**Finalización:** la solicitud alcanza un resultado final registrado en el sistema, de acuerdo con el procedimiento y las autorizaciones que se validen. Se propone contemplar la declaratoria de aptitud o el cierre de la solicitud sin declaratoria, cuando corresponda.

**Límites del MVP:** no se pretende gestionar integralmente la elaboración del trabajo de titulación, la asignación del director, la designación del tribunal, la sustentación ni la emisión del título.

### 1.3. Justificación de la delimitación

La selección de este subproceso permite concentrar el desarrollo en la gestión de solicitudes, la documentación, las observaciones, los permisos, las transiciones de estado y la trazabilidad. Además, permite preparar una posible interoperabilidad futura con el SIAAF sin asumir que ya existe una API disponible o que se cuenta con autorización para utilizarla.

## 2. Flujo inicial propuesto

El flujo describe el comportamiento funcional que se pretende implementar. Sus estados, responsables y condiciones de transición deberán validarse antes de considerarlos requisitos definitivos.

1. **Registro de la solicitud.** El estudiante registra la información inicial y adjunta la documentación requerida, según los requisitos que se confirmen.
2. **Envío de la solicitud.** El estudiante verifica la información y envía la solicitud para su revisión.
3. **Revisión administrativa.** El usuario autorizado verifica los documentos y los requisitos correspondientes.
4. **Registro de observaciones.** Si existen datos incompletos, documentos incorrectos u obligaciones pendientes, el revisor registra las observaciones para que puedan ser atendidas.
5. **Corrección y reenvío.** El estudiante consulta las observaciones, corrige la información y vuelve a enviar la solicitud.
6. **Registro del resultado.** Una vez completada la revisión, se registra el resultado de la etapa y la decisión de la autoridad que corresponda.

El sistema deberá impedir transiciones no autorizadas y conservar un historial de los cambios relevantes.

## 3. Estados iniciales de la solicitud

Los siguientes estados son una propuesta de diseño, no una lista definitiva de estados institucionales.

| Estado | Descripción |
|---|---|
| `BORRADOR` | Solicitud creada que todavía no se ha enviado. |
| `ENVIADA` | Solicitud remitida para su revisión. |
| `EN_REVISION` | Solicitud que está siendo revisada por un usuario autorizado. |
| `OBSERVADA` | Solicitud con observaciones pendientes de atención. |
| `INFORME_EMITIDO` | Se ha registrado la emisión del informe correspondiente, si se requiere como estado independiente. |
| `DECLARADA_APTA` | Se ha registrado la declaratoria de aptitud por la autoridad competente. |
| `CANCELADA` | Solicitud cerrada sin llegar a la declaratoria, cuando exista una causa y autorización válidas. |

La transición entre estados deberá estar sujeta al rol del usuario, las condiciones del proceso y las reglas que se confirmen. En particular, se debe determinar si `INFORME_EMITIDO` y `DECLARADA_APTA` representan etapas separadas y bajo qué condiciones puede cancelarse una solicitud.

## 4. Alcance funcional del MVP

### 4.1. Funcionalidades incluidas inicialmente

| Funcionalidad | Propósito |
|---|---|
| Registro y consulta de solicitudes | Permitir crear solicitudes y consultar su información. |
| Autenticación y autorización por roles | Restringir las operaciones según las responsabilidades asignadas. |
| Gestión de documentos | Adjuntar, consultar y, cuando corresponda, reemplazar documentos. |
| Registro de observaciones | Documentar las correcciones solicitadas durante la revisión. |
| Corrección y reenvío | Permitir que el estudiante atienda las observaciones. |
| Gestión de estados | Registrar el avance de la solicitud mediante transiciones controladas. |
| Historial de cambios | Identificar quién realizó un cambio, cuándo y qué acción ejecutó. |
| Validaciones y pruebas | Comprobar las reglas funcionales y los permisos. |
| Documentación técnica | Describir la API y las instrucciones para ejecutar el sistema. |

### 4.2. Funcionalidades fuera del MVP

| Funcionalidad excluida | Justificación |
|---|---|
| Digitalización de todo el proceso de titulación | Ampliaría excesivamente el alcance inicial. |
| Gestión de la designación del tribunal y la sustentación | Corresponde a etapas posteriores al subproceso seleccionado. |
| Firma electrónica institucional | Requiere definir mecanismos y autorizaciones adicionales. |
| Decisiones académicas o legales automáticas | Las decisiones deben respetar las competencias y procedimientos institucionales. |
| Integración real con el SIAAF | Depende de documentación técnica, acceso y autorización institucional. |
| Verificación automática de información institucional | Depende de servicios y fuentes de datos que todavía deben confirmarse. |
| Migración masiva de expedientes históricos | No es necesaria para validar el funcionamiento básico del MVP. |
| Notificaciones por correo o aplicaciones móviles | Se pueden considerar como mejoras posteriores si no son imprescindibles para el alcance aprobado. |
| Reportes estadísticos institucionales | No constituyen la prioridad de la primera versión. |

Las exclusiones pueden modificarse si el docente o el equipo justifican un cambio de alcance.

## 5. Documentación requerida

Tomando como referencia el artículo 235 del Reglamento de Régimen Académico de la UNL, el ejemplo de trabajo identifica los siguientes documentos para la solicitud:

| Documento | Aspecto que debe confirmarse |
|---|---|
| Récord académico legalizado | Quién lo obtiene o adjunta y bajo qué procedimiento. |
| Certificado de cumplimiento de horas de prácticas preprofesionales y vinculación | Entidad emisora y formato admitido. |
| Certificado de suficiencia de idioma, nivel B1 | Requisitos de presentación y entidad emisora. |
| Certificado del director del trabajo de culminación y aprobación | Formato y procedimiento de emisión. |
| Certificado de Tesorería de no adeudar a la institución | Forma de obtención y responsable de incorporarlo al expediente. |

La lista debe contrastarse con la versión oficial vigente de la normativa y con las instrucciones institucionales aplicables. También debe confirmarse cuáles documentos aporta el estudiante y cuáles incorpora el personal autorizado.

No se establecerán límites definitivos de tamaño, formato ni tipos de archivo hasta que el equipo los acuerde y documente como decisiones técnicas.

## 6. Relación con las etapas de SDD

El desarrollo guiado por especificaciones (Spec-Driven Development, SDD) organiza el trabajo desde los principios del proyecto hasta las tareas verificables.

| Etapa | Aplicación al proyecto | Evidencia esperada |
|---|---|---|
| `constitution` | Establecer principios de calidad, seguridad, transparencia, trazabilidad, protección de datos y colaboración. | Constitución del proyecto. |
| `specify` | Definir el subproceso, los actores, las necesidades, los requisitos funcionales y no funcionales y sus criterios de aceptación. | Especificación funcional. |
| `clarify` | Resolver ambigüedades relacionadas con documentos, roles, estados, autorizaciones y futura integración con el SIAAF. | Registro de preguntas y aclaraciones. |
| `plan` | Definir la arquitectura, las tecnologías, la persistencia, la seguridad y la estrategia de pruebas. | Plan técnico y decisiones justificadas. |
| `tasks` | Descomponer los requisitos en actividades pequeñas, asignables y verificables. | Lista de tareas o incidencias vinculadas a requisitos. |

### 6.1. Relación entre las etapas

La constitución establece los principios que deben respetarse en todo el desarrollo. A partir de ellos, la especificación determina qué necesita el sistema y cómo se comprobará su cumplimiento. Las aclaraciones permiten resolver las ambigüedades antes de tomar decisiones definitivas. El plan establece cómo implementar los requisitos y las tareas organizan ese trabajo en actividades verificables.

Por tanto, las etapas deben mantenerse relacionadas: cada tarea debe responder a un requisito o necesidad, y su cumplimiento debe poder comprobarse mediante criterios de aceptación y pruebas.

## 7. Decisiones pendientes de validación

Antes de cerrar el alcance, el equipo deberá resolver las siguientes cuestiones:

1. ¿Se aprueba la solicitud de declaratoria de aptitud legal como subproceso del MVP?
2. ¿Qué roles institucionales intervienen realmente en la revisión y la declaratoria?
3. ¿Qué documentos aporta el estudiante y cuáles incorpora el personal autorizado?
4. ¿Qué estados y transiciones corresponden al procedimiento oficial?
5. ¿La emisión del informe y la declaratoria de aptitud deben registrarse como etapas separadas?
6. ¿Qué condiciones permiten cerrar o cancelar una solicitud?
7. ¿Qué requisitos de seguridad y conservación de documentos deben respetarse?
8. ¿Existe documentación y autorización para una futura integración con el SIAAF?

Las respuestas deberán documentarse y utilizarse para actualizar la especificación funcional y el alcance.

## 8. Conclusión

La delimitación propuesta concentra el MVP en un subproceso concreto del trámite de titulación, lo que permite definir un flujo verificable y priorizar la gestión de solicitudes, documentos, observaciones, estados, permisos e historial de cambios. La relación con las etapas SDD permite organizar las decisiones funcionales y técnicas de forma progresiva, manteniendo identificadas las cuestiones que necesitan confirmación institucional antes de iniciar una implementación definitiva.

## 9. Referencias

[1] Universidad Nacional de Loja, *Reglamento de Régimen Académico de la Universidad Nacional de Loja*, versión oficial aplicable. Consultar especialmente el artículo 235 y los artículos relacionados con las etapas previas y posteriores del proceso de titulación.

[2] Universidad Nacional de Loja, *Sílabo de Desarrollo Basado en Plataformas*, Carrera de Computación, 2026.

[3] Universidad Nacional de Loja, *Banco de proyectos para ACD1*, proyecto “Trámite de titulación integrado al SIAAF”, 2026.

Las referencias deberán completarse con los enlaces, datos de publicación y versiones verificadas de los documentos efectivamente consultados.
