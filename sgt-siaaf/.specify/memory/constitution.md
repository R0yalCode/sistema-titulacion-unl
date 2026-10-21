# Constitución del Proyecto SGT-SIAAF

**Sistema de Gestión de Trámites de Titulación e Integración Académica**

-   **Versión:** 2.0 --- propuesta consolidada
-   **Fecha:** 20 de octubre de 2026
-   **Estado:** Propuesta para revisión y aprobación del equipo
-   **Tipo de proyecto:** Simulación académica funcional, preparada
    conceptualmente para una posible integración institucional futura

> Este documento establece los principios obligatorios de arquitectura,
> seguridad, calidad, alcance y trabajo para SGT-SIAAF. No reemplaza las
> especificaciones funcionales, los contratos API, los ADR ni la
> normativa institucional. Las reglas académicas o administrativas no
> confirmadas deben permanecer explícitamente pendientes y no pueden
> presentarse como reglas oficiales.

------------------------------------------------------------------------

## 1. Propósito y visión

SGT-SIAAF busca simplificar y dar trazabilidad al proceso de titulación
mediante un sistema centralizado en el que el estudiante pueda gestionar
peticiones documentales dirigidas a diferentes dependencias
universitarias, consultar el progreso de su expediente y acceder a los
documentos que los responsables hayan cargado.

En el proceso que se pretende simular, el estudiante no debería tener
que coordinar cada petición por separado mediante visitas presenciales o
correos electrónicos. Desde el sistema podrá iniciar varias peticiones
en paralelo ---por ejemplo, a Secretaría de Carrera y a Dirección de
Carrera--- y consultar el estado, responsable, fechas, observaciones e
historial de cada una desde una vista consolidada.

El proyecto es una **simulación académica con datos ficticios**. No
tiene acceso autorizado al SGA o al SIAAF productivos y no debe afirmar
que se encuentra integrado con ellos. La arquitectura podrá preparar
interfaces y adaptadores sustituibles para una posible integración
futura, pero esa integración requerirá autorización, contratos técnicos
y validación institucional independientes.

El sistema apoya la gestión y la trazabilidad; no sustituye las
decisiones ni las atribuciones de las autoridades universitarias.

## 2. Alcance del producto y fases de entrega

El desarrollo del proyecto se organiza en **tres fases de entrega
tecnológica**, que no deben confundirse con las etapas académicas del
proceso de titulación.

### Fase de entrega 1 --- Backend

Construir y verificar la API, las reglas de negocio, persistencia,
seguridad, auditoría, documentación y servicios necesarios para
representar las etapas del proceso de titulación. El backend deberá
contemplar, mediante incrementos especificados y verificables, los
flujos simulados de:

1.  Gestión de solicitudes y requisitos documentales para la aptitud
    legal.
2.  Sustentación y defensa.
3.  Cierre del proceso, actas y registro posterior representado en la
    simulación.

La inclusión de estas tres etapas en el backend **no implica que todas
estén implementadas desde el inicio**. Cada incremento debe tener
especificación, plan, tareas, pruebas y evidencia propias. La normativa,
los plazos, los formularios y las competencias institucionales que no se
hayan validado se representarán como configuraciones o reglas
provisionales claramente etiquetadas.

### Fase de entrega 2 --- Frontend web

Construir una interfaz web que consuma la API documentada y permita, de
acuerdo con los permisos del usuario:

-   al estudiante crear y consultar su expediente y sus peticiones;
-   presentar una línea de tiempo consolidada y el historial individual
    de cada petición;
-   a los responsables consultar la bandeja de su dependencia simulada,
    atender peticiones, registrar observaciones y entregar documentos de
    prueba;
-   consultar notificaciones internas, estados y documentos autorizados;
-   mostrar avisos claros cuando un dato, documento, plazo o resultado
    sea simulado.

El frontend no debe contener reglas de autorización que sustituyan la
comprobación del backend. Ocultar un botón no constituye un control de
acceso.

### Fase de entrega 3 --- Aplicación móvil

Construir una aplicación móvil acotada que consuma los mismos contratos
de la API. Su alcance inicial recomendado es consultar el expediente, la
línea de tiempo, los estados, las observaciones y las notificaciones
internas; la carga o reenvío de documentos podrá incluirse si se aprueba
en su especificación y el calendario lo permite.

La aplicación móvil no debe duplicar las reglas de negocio ni conectarse
directamente a la base de datos. Toda operación protegida se valida en
el backend.

### Fuera del alcance actual

-   Conexión real a sistemas institucionales productivos o modificación
    de sus bases de datos.
-   Uso de credenciales, datos personales o documentos oficiales reales
    en la demostración.
-   Generación de firmas digitales oficiales, certificación de firmas o
    declaración legal de aptitud automática.
-   Envío de correos, SMS o notificaciones push como requisito del MVP;
    las notificaciones serán internas.
-   Habilitación de Django Admin como interfaz operativa institucional
    en el incremento actual. Se evaluará posteriormente mediante una
    decisión arquitectónica explícita.
-   Afirmar que un documento de prueba tiene validez legal por su
    formato, apariencia o carga en el sistema.

## 3. Principios no negociables

### P-01. Simulación explícita y honesta

Todos los usuarios, dependencias, expedientes, datos académicos,
documentos, entregas, actuaciones y resultados usados en la demostración
serán ficticios. La interfaz y los documentos de ejemplo deberán indicar
de forma visible que son de simulación y no tienen validez oficial.
Ninguna operación podrá enviar datos de prueba a sistemas externos
reales.

### P-02. No reemplazar a la autoridad humana

El sistema registra actuaciones y facilita el seguimiento, pero no
determina automáticamente la elegibilidad legal, no sustituye una firma
oficial ni concede aptitud por el mero hecho de completar un checklist o
cargar archivos. Las decisiones institucionales deben ser registradas
por el actor autorizado según las reglas aprobadas.

### P-03. Expediente global y peticiones independientes

El expediente de titulación agrupa el proceso de un estudiante. Cada
petición documental es una unidad de trabajo independiente, vinculada al
expediente, al tipo de documento y a la dependencia competente. El
estudiante puede mantener varias peticiones abiertas en paralelo. El
avance, rechazo, observación o entrega de una petición no debe bloquear
ni cancelar automáticamente las demás.

### P-04. Separación entre estado global y estado por petición

El estado del expediente resume el proceso; el estado de cada petición
refleja su ciclo de vida particular. No se debe almacenar toda la
actividad en un único estado global. Las transiciones permitidas, los
actores autorizados y sus consecuencias deben definirse en la
especificación de cada incremento.

### P-05. Responsabilidad configurable, no nombres codificados

Las peticiones se enrutan a una dependencia o módulo responsable
configurado. El sistema registra el funcionario ficticio que ejecutó
cada actuación, su rol y la dependencia en cuyo ámbito actuó. Los
nombres personales y las asignaciones cambiantes no deben codificarse
como reglas permanentes. Las sustituciones de responsables deben
conservar la trazabilidad.

### P-06. Seguridad por defecto y mínimo privilegio

Toda operación protegida requiere autenticación y autorización en el
servidor. Los permisos deben comprobar rol, estado de la cuenta,
propiedad del expediente o petición y ámbito de la dependencia, según
corresponda. Se deniega por defecto cualquier acción no autorizada. Los
procesos de mantenimiento y migración deben usar credenciales separadas
del usuario de ejecución HTTP.

### P-07. Privacidad y minimización de datos

Se recopilará únicamente la información ficticia o estrictamente
necesaria para la función implementada. Los documentos no serán públicos
ni accesibles mediante rutas sin autorización. No se incluirán secretos,
tokens, contraseñas, datos personales reales o contenido sensible en el
repositorio, imágenes, logs, fixtures o evidencia de pruebas.

### P-08. Trazabilidad e historial íntegro

Las acciones relevantes deberán registrar actor, fecha y hora UTC,
objeto afectado, acción y resultado; cuando proceda, se registrarán
cambios de estado, observaciones, entrega o sustitución de documentos y
motivo. El historial no podrá alterarse o borrarse mediante operaciones
HTTP ordinarias. La auditoría debe ser consistente con la operación
principal: si la transacción debe fallar, no puede quedar un registro
parcial de éxito.

### P-09. Documentos y versiones

Los PDF cargados serán documentos de prueba. El tamaño máximo permitido
será **10 MB por archivo PDF**, aplicado de manera consistente en
backend y frontend y comprobado por pruebas. La validación no se
limitará a la extensión: deberá verificar tipo real, estructura básica,
tamaño y condiciones de seguridad definidas en la especificación.

Cada entrega deberá asociarse a una petición, al responsable que la
cargó, a la fecha y a sus metadatos. Si se reemplaza un documento, la
versión anterior se conservará conforme a la política aprobada y se
registrará quién realizó la sustitución. La descarga requiere
autorización por expediente, petición y documento.

### P-10. Observaciones accionables

Una observación debe ser visible para los actores autorizados e incluir
autor, fecha, motivo y, cuando corresponda, acción esperada. Una
petición observada podrá corregirse, responderse o reanudarse según su
tipo y sus permisos. Una observación de una petición no cancelará el
expediente completo ni las demás peticiones por defecto.

### P-11. Notificaciones internas en el MVP

Los eventos relevantes generarán notificaciones internas para
destinatarios autorizados: nueva petición en la bandeja de la
dependencia, observación, cambio de estado, entrega de documento y otros
eventos definidos por la especificación. Las notificaciones externas
quedan fuera del MVP. La entrega y deduplicación de notificaciones deben
ser verificables; los fallos no deben corromper la operación principal.

### P-12. Interoperabilidad desacoplada

El backend ofrecerá una API REST versionada y contratos OpenAPI. La
simulación de datos que en el futuro podrían proceder del SGA/SIAAF se
implementará detrás de interfaces o adaptadores reemplazables. Ningún
componente podrá escribir directamente en sistemas institucionales
reales. Una integración futura requiere aprobación formal, definición de
contratos, autorización y pruebas independientes.

### P-13. Contratos estables entre clientes

El frontend web y la aplicación móvil consumirán la misma API pública
documentada. Los cambios incompatibles deben versionarse o migrarse
mediante un plan explícito. Los clientes no deben acceder directamente a
tablas, modelos internos ni credenciales de base de datos.

### P-14. Calidad demostrable

Las funciones críticas deben verificarse mediante pruebas automatizadas
y evidencia reproducible. Una declaración de "completado" requiere
pruebas pertinentes, revisión de seguridad, documentación actualizada y
registro de los resultados. Las pruebas de concurrencia y privilegios
deben ejecutarse contra PostgreSQL con conexiones y roles adecuados, no
únicamente mediante mocks o memoria.

### P-15. Reproducibilidad

El entorno de desarrollo y demostración debe poder prepararse con
instrucciones versionadas, Docker Compose, variables documentadas y
datos ficticios reproducibles. Las pruebas no deben depender de datos
personales ni de servicios institucionales externos. Las imágenes deben
excluir secretos, archivos locales innecesarios y artefactos privados.

### P-16. Accesibilidad y claridad

Las interfaces deben presentar estados, fechas, responsables,
observaciones y acciones pendientes con lenguaje claro. No se debe
comunicar como oficial una fecha, requisito, plazo, firma o resultado
que sea únicamente ilustrativo. Los errores deben orientar al usuario
sin revelar detalles internos, secretos ni trazas.

### P-17. Evolución incremental y compatibilidad

Las decisiones aprobadas se registran en especificaciones y ADR. Una
nueva funcionalidad no debe alterar silenciosamente el comportamiento ya
aprobado. Cuando un incremento afecte un contrato o requisito existente,
se debe documentar el impacto, definir una migración y agregar pruebas
de regresión.

### P-18. Herramientas administrativas bajo control

Django Admin no forma parte del alcance operativo actual. Su
incorporación posterior requerirá un incremento aprobado que defina
autenticación, sesiones y CSRF, permisos por objeto y dependencia,
auditoría, acciones permitidas y un rol SQL apropiado. No se permitirá
usar el usuario de migraciones como credencial de una interfaz
administrativa expuesta por HTTP.

## 4. Modelo conceptual obligatorio

El modelo debe representar, como mínimo, los conceptos siguientes. Los
nombres concretos de tablas y clases se establecen en el plan técnico y
no son impuestos por esta constitución.

-   **Estudiante simulado:** identidad de prueba que inicia y consulta
    su propio proceso.
-   **Expediente de titulación:** contenedor global del proceso de una
    persona para el ciclo de titulación representado.
-   **Petición documental:** solicitud independiente dirigida a una
    dependencia, vinculada al expediente y a un tipo documental.
-   **Catálogo documental:** tipos de documentos, dependencia
    responsable y reglas de aplicabilidad configurables.
-   **Dependencia o módulo simulado:** unidad que recibe y atiende
    peticiones.
-   **Responsable simulado:** usuario, rol y dependencia que puede
    ejecutar acciones autorizadas.
-   **Documento entregado:** archivo de prueba con versión, metadatos,
    procedencia y relación con la petición.
-   **Observación:** explicación registrada por un actor autorizado y
    visible a los destinatarios permitidos.
-   **Notificación interna:** aviso asociado a un evento y a sus
    destinatarios autorizados.
-   **Evento de auditoría / historial:** registro de las actuaciones y
    transiciones relevantes.
-   **Actuación académica posterior:** entidad o registro para
    representar, mediante incrementos futuros, verificación de aptitud,
    sustentación, defensa, cierre y registro final simulado.

El expediente debe poder mostrar una vista consolidada, pero cada
petición mantiene sus fechas, estado, responsable, documentos y
observaciones. El catálogo y las reglas de aplicabilidad deben permitir
que un requisito sea no aplicable cuando así lo determine la
configuración aprobada; no se debe asumir que todos los requisitos son
obligatorios para todas las personas.

## 5. Actores y autorización

Los roles exactos y sus competencias institucionales deberán validarse
antes de convertirse en reglas definitivas. Para la simulación se podrán
representar, como mínimo:

-   **Estudiante:** crea y consulta su expediente, crea peticiones
    permitidas, consulta observaciones y descarga documentos propios
    autorizados.
-   **Responsable de dependencia:** ve la bandeja de su dependencia,
    atiende las peticiones que le corresponden, registra observaciones y
    carga o sustituye documentos conforme a permisos.
-   **Autoridad académica o administrativa simulada:** ejecuta
    únicamente las decisiones del proceso para las que se le haya
    concedido permiso explícito.
-   **Analista de apoyo simulado:** prepara información o borradores si
    el flujo aprobado lo contempla, sin adquirir por ello atribuciones
    de aprobación.
-   **Administrador técnico de simulación:** prepara catálogos,
    dependencias y usuarios ficticios mediante herramientas controladas;
    no equivale a una autoridad universitaria.

La autorización se define mediante una matriz rol × acción × recurso ×
dependencia. Las operaciones de listar, leer, editar, observar,
entregar, reemplazar, descargar, cancelar y decidir deben evaluarse por
separado. No se deben deducir permisos administrativos a partir de que
un usuario sea funcionario.

## 6. Arquitectura y tecnologías

La arquitectura aprobada para el backend inicial es un monolito modular
con:

-   Python y Django;
-   Django REST Framework para la API;
-   PostgreSQL para persistencia;
-   Docker y Docker Compose para entornos reproducibles;
-   autenticación basada en tokens verificados y autorización en el
    servidor, conforme a los ADR aprobados;
-   contratos OpenAPI y endpoints versionados bajo `/api/v1/`;
-   cliente web y aplicación móvil como consumidores independientes de
    la API;
-   HTTPS en los entornos donde se exponga el servicio.

Las versiones exactas, paquetes, topología de contenedores, políticas de
claves, permisos SQL y decisiones de despliegue se mantienen en el plan
técnico y los ADR. Esta constitución no autoriza un despliegue
productivo ni presupone que exista un proveedor institucional de
identidad o una API real del SGA/SIAAF.

## 7. Requisitos no funcionales mínimos

### Seguridad

-   Validar autenticación, cuenta activa, rol, propiedad y ámbito en
    cada operación.
-   Mantener secretos fuera del código, de imágenes, logs y archivos
    versionados.
-   Aplicar mínimo privilegio a usuarios de base de datos y procesos.
-   Usar HTTPS y no deshabilitar la validación de certificados para
    superar errores de pruebas.
-   Proteger documentos en almacenamiento y durante la descarga.
-   Responder de forma segura ante recursos ajenos, inexistentes o
    identificadores malformados.

### Integridad y concurrencia

-   Usar transacciones para cambios que deban ser atómicos.
-   Conservar consistencia entre petición, documento, notificación e
    historial.
-   Proteger las modificaciones concurrentes mediante bloqueo, versión o
    precondición según el contrato.
-   Probar rollbacks, duplicados, carreras y restricciones con
    PostgreSQL real cuando aplique.

### Rendimiento y escalabilidad razonable

-   Evitar consultas N+1 y paginar listados.
-   Establecer objetivos cuantitativos de rendimiento cuando se disponga
    de escenarios y datos representativos; no afirmar metas que no hayan
    sido medidas.
-   Mantener un diseño modular suficiente para la escala académica, sin
    introducir servicios distribuidos innecesarios.

### Observabilidad y errores

-   Utilizar errores de API consistentes y documentados.
-   No devolver trazas, credenciales, SQL, rutas privadas ni información
    sensible.
-   Registrar eventos técnicos útiles sin volcar contenido confidencial
    de documentos.

### Mantenibilidad

-   Mantener responsabilidades separadas entre modelos, servicios,
    vistas, permisos, adaptadores y tareas de infraestructura.
-   Documentar decisiones arquitectónicas y cambios incompatibles.
-   Mantener pruebas de regresión para funcionalidades ya verificadas.

### Documentación

-   Actualizar OpenAPI, guía de instalación, variables de entorno,
    comandos de ejecución y procedimientos de demostración.
-   Mantener matriz de trazabilidad entre requisito, criterio de
    aceptación, endpoint, prueba y evidencia.
-   Etiquetar claramente las decisiones institucionales pendientes.

## 8. Desarrollo guiado por especificaciones

El equipo seguirá el flujo de trabajo Spec-Driven Development:

1.  **Constitution:** comprobar que la propuesta respeta los principios
    de este documento.
2.  **Specify:** definir problema, actores, historias, requisitos
    funcionales y no funcionales, excepciones y criterios de aceptación.
3.  **Clarify:** resolver ambigüedades o registrarlas como pendientes
    con responsable y riesgo.
4.  **Plan:** investigar, definir arquitectura y contratos, y registrar
    decisiones en ADR cuando corresponda.
5.  **Tasks:** descomponer el plan en tareas pequeñas, trazables y
    verificables.
6.  **Implement:** ejecutar únicamente las tareas autorizadas, con
    pruebas y revisión de regresiones.
7.  **Validate:** verificar criterios de aceptación, seguridad,
    documentación y evidencia antes de marcar una tarea como completa.

No se debe implementar una regla institucional basándose únicamente en
una suposición, ejemplo o nombre de estado. Si una decisión no está
confirmada, se documenta como provisional, se limita su impacto y se
solicita aprobación antes de convertirla en regla normativa.

## 9. Pruebas y criterios de terminado

Una tarea o incremento no se considera terminado por el solo hecho de
que el código compile. Debe cumplir, según corresponda, con:

-   criterios de aceptación aprobados;
-   pruebas unitarias, de integración y de regresión;
-   pruebas de autorización por rol, propietario y dependencia;
-   pruebas de integridad, rollback y concurrencia;
-   pruebas de documentos de hasta 10 MB y rechazo de archivos no
    válidos;
-   pruebas de notificaciones internas y prevención de duplicados;
-   verificación de contratos OpenAPI;
-   comprobación de migraciones y permisos SQL;
-   comprobación de HTTPS cuando aplique;
-   documentación y matriz de trazabilidad actualizadas;
-   evidencia reproducible de los comandos y resultados;
-   ausencia de secretos, datos reales y cambios no autorizados.

Las limitaciones del entorno deben registrarse; no se debe afirmar que
una comprobación pasó si no se ejecutó.

## 10. Gestión de cambios y compatibilidad con lo existente

La constitución orienta el trabajo futuro, pero no reescribe
retroactivamente el historial de decisiones ni autoriza cambios
silenciosos a funcionalidades ya implementadas.

Antes de modificar una especificación, contrato o modelo existente, el
equipo deberá:

1.  identificar los artefactos y funcionalidades afectados;
2.  explicar el motivo y el beneficio esperado;
3.  evaluar compatibilidad, migración y regresiones;
4.  registrar la decisión en la especificación o ADR correspondiente;
5.  obtener aprobación cuando el cambio altere alcance, comportamiento o
    una decisión previamente acordada;
6.  implementar las pruebas y documentación necesarias.

La Feature 001 conserva su comportamiento aprobado mientras no se
apruebe un cambio explícito. Las nuevas peticiones documentales,
bandejas por dependencia, notificaciones internas y entregas de PDF
deberán incorporarse como incrementos definidos y trazables, no como
modificaciones improvisadas.

## 11. Decisiones confirmadas y asuntos pendientes

### Decisiones confirmadas por el equipo

-   El proyecto es una simulación académica para demostrar una propuesta
    de futura implementación.
-   La integración con SGA/SIAAF será simulada; no se dispone de acceso
    a los sistemas productivos.
-   El backend debe contemplar las tres etapas del proceso de titulación
    mediante incrementos verificables.
-   Las peticiones a diferentes módulos podrán tramitarse en paralelo y
    estarán vinculadas a un expediente global.
-   La asignación se realizará a una dependencia configurada; se
    registrará el responsable ficticio que actúe.
-   Las notificaciones del MVP serán internas.
-   Los PDF de prueba tendrán un tamaño máximo de **10 MB por archivo**
    y no tendrán validez oficial.
-   Django Admin se evaluará en un incremento posterior.
-   La entrega del documento no equivale por sí sola a una aprobación
    legal ni a una declaración de aptitud.

### Asuntos que deben validarse antes de codificar reglas definitivas

-   Catálogo exacto de documentos y condiciones de aplicabilidad por
    tipo de titulación.
-   Matriz definitiva de roles, competencias, sustituciones y permisos.
-   Estados y transiciones autorizados para cada tipo de petición y para
    el expediente global.
-   Procedimiento para observaciones, respuestas, rechazo, cancelación y
    reapertura.
-   Qué actos o resultados se simularán en las etapas de aptitud,
    sustentación, defensa, cierre y registro final.
-   Plantillas, campos y contenido que podrán aparecer en documentos de
    prueba.
-   Política de conservación, eliminación y reemplazo de archivos.
-   Objetivos cuantitativos de rendimiento y disponibilidad, si se
    exigen en la evaluación.
-   Alcance exacto de la app móvil, condicionado al calendario y a la
    aprobación de su especificación.
-   Cualquier regla normativa, plazo, feriado, firma o requisito
    institucional que no tenga fuente confirmada.

Las decisiones pendientes no deben bloquear el diseño general si pueden
aislarse; sí deben impedir que una hipótesis se presente como requisito
oficial o que se implemente una decisión de alto impacto sin aprobación.

## 12. Criterio de éxito del proyecto

SGT-SIAAF será una demostración satisfactoria cuando pueda mostrar, de
extremo a extremo y con datos ficticios:

1.  un estudiante que consulta su expediente;
2.  varias peticiones documentales creadas y tramitadas en paralelo;
3.  la llegada de cada petición a la bandeja de su dependencia simulada;
4.  responsables ficticios que registran atención u observaciones;
5.  la carga, versionado y descarga autorizada de documentos PDF de
    prueba;
6.  notificaciones internas e historial de actuaciones;
7.  una línea de tiempo consolidada y el estado independiente de cada
    petición;
8.  la representación controlada de las etapas de titulación cubiertas
    por los incrementos aprobados;
9.  controles de seguridad, pruebas y documentación que permitan
    reproducir la demostración;
10. una separación clara entre resultados simulados y cualquier proceso
    institucional real.

El éxito no se medirá por aparentar una integración institucional que no
existe, sino por demostrar un flujo coherente, seguro, trazable,
verificable y extensible para una posible implementación futura.

------------------------------------------------------------------------

## Regla final

Cuando exista conflicto entre una decisión de implementación y esta
constitución, se deberá detener el cambio afectado, documentar la
discrepancia y resolverla mediante especificación y ADR. Ninguna
urgencia de desarrollo justifica omitir controles de seguridad,
presentar datos simulados como oficiales o atribuir al sistema
competencias que corresponden a personas o autoridades institucionales.
