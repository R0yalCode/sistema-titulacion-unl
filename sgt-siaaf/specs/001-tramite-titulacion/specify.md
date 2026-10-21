# ESPECIFICACIÓN DE REQUISITOS REFACTORIZADA Y CONSOLIDADA DEL PROYECTO SGT-SIAAF

**Sistema de Gestión del Trámite de Titulación integrado al SIAAF**  
*Universidad Nacional de Loja — Facultad de la Energía, las Industrias y los Recursos Naturales No Renovables (FEIRNNR)*  
**Carrera de Computación — Asignatura: Desarrollo Basado en Plataformas**  
**Versión de Especificación:** 2.0.0 (Refactorizada y Consolidada)  
**Estatus:** Especificación Funcional Inmutable — Marco de Trabajo GitHub Spec Kit (Etapa `specify`)  

---

## 1. CONTROL DEL DOCUMENTO Y TRAZABILIDAD NORMATIVA

### 1.1 Metadatos del Artefacto
* **Nombre del Proyecto:** SGT-SIAAF — Sistema de Gestión del Trámite de Titulación integrado al SIAAF.
* **Nombre del Artefacto:** `specify_refactorizado.md` (Dossier Completo de Especificación Funcional y Requisitos).
* **Versión:** 2.0.0 (Consolidada y refactorizada tras revisión integral de fuentes y Constitución v2.0).
* **Estado del Documento:** Especificación Funcional Inmutable para la etapa `specify`.
* **Fecha de Emisión:** 20 de octubre de 2026.
* **Autores y Responsables:** Equipo de Desarrollo de Software SGT-SIAAF (Estudiantes de 5.º Ciclo de la Carrera de Computación, UNL).
* **Público Destinatario:** Equipo de desarrollo de software, docente de la asignatura, ayudantes de cátedra, evaluadores académicos y actores institucionales de la UNL.

### 1.2 Declaración de Conformidad Constitucional
El presente documento se encuentra estrictamente subordinado a la **Constitución del Proyecto SGT-SIAAF (Versión 2.0.0 Oficial)**. En cumplimiento con el **Principio C-001 (Fidelidad Normativa y Trazabilidad de Requisitos)** y el **Principio C-019 (Calidad Documental y Gobernanza mediante SDD)**, ninguna especificación, historia de usuario, requisito funcional, requisito no funcional o criterio de aceptación contenido en este archivo contradice los principios obligatorios, restricciones arquitectónicas o reglas de gobernanza establecidas en la Constitución.

### 1.3 Inventario de Fuentes Primarias de Trazabilidad
Todas las especificaciones contenidas en este documento se fundamentan formalmente en las siguientes fuentes oficiales primarias:

1. `[Constitución v2.0]` **Constitución del Proyecto SGT-SIAAF (Versión 2.0.0 Oficial, 20-oct-2026):** Establece los 20 principios de gobernanza, restricciones arquitectónicas y reglas de simulación académica.
2. `[RRA-UNL]` **Reglamento de Régimen Académico de la Universidad Nacional de Loja (Aprobado OCS 27-01-2021):** Artículos 231, 235 (Declaratoria de Aptitud Legal), 236–237 (Sustentación y Calificación) y 243–244 (Acta Consolidada y Registro SENESCYT).
3. `[Plantilla Providencia #590]` **Providencia e Informe de Aptitud Legal N° 590 SG-FEIRNNR-UNL (13-oct-2026):** Define la estructura del informe legal, checklist de 5 requisitos, recepción con hora/fecha y firmas del Secretario/a-Abogado/a y Analista de Apoyo.
4. `[Plantilla Memorando #162]` **Memorando N° UNL-FEIRNNR-2026-162-M (15-oct-2026):** Modela la resolución formal de declaratoria de aptitud emitida por el Decano/a con firma electrónica externa y copias oficiales.
5. `[Docente]` **Transcripción Final de Retroalimentación Docente (15-oct-2026):** Directrices orales sobre complementación sin reemplazo del SGA/SIAAF, firma autógrafa física obligatoria en actas de defensa, inalterabilidad del promedio del SGA y peticiones internas sin correo.
6. `[Análisis SGT v3]` **Documentos de Análisis y Arquitectura del Proyecto (01 a 05, v3 15-oct-2026):** Mapeo de procesos manuales vs propuesta digital, delimitación del MVP, matriz RBAC de 8 roles y ADR de selección de Django + DRF.
7. `[ACD2]` **Banco de Proyectos y Requisitos Formales (ACD2_DESARROLLO.pdf):** Fichas de requisitos funcionales (RF-01 a RF-16) y no funcionales (RNF-01 a RNF-18).
8. `[Sílabo-DBP]` **Sílabo de la Asignatura Desarrollo Basado en Plataformas (E2C4A3):** Cronograma de 5 semanas para el backend, estándar RESTful, OpenAPI v3 y uso ético de Inteligencia Artificial.
9. `[Estatuto UNL]` **Estatuto Orgánico de la Universidad Nacional de Loja (06-11-2019):** Atribuciones institucionales del Rector, Decano/a y Secretaría General.

---

## 2. RESUMEN EJECUTIVO Y DECLARACIÓN DE SIMULACIÓN ACADÉMICA

### 2.1 Visión General del Sistema
El **Sistema de Gestión del Trámite de Titulación integrado al SIAAF (SGT-SIAAF)** es una plataforma informática web y móvil diseñada para centralizar, digitalizar, controlar y auditar la fase administrativa del proceso de titulación de pregrado en la Carrera de Computación de la FEIRNNR - UNL.

El sistema reemplaza los procesos presenciales atomizados y el envío informal de documentos por correo electrónico por un entorno digital unificado. A través de un punto de acceso único, el estudiante gestiona su **expediente global de titulación** y canaliza **peticiones documentales independientes** hacia las dependencias universitarias correspondientes (Secretaría de Carrera, Dirección de Carrera, Secretaría-Abogacía, Decanato, Tesorería, Instituto de Idiomas y Responsable de Prácticas), garantizando trazabilidad inmutable y visibilidad en tiempo real.

### 2.2 Declaración Obligatoria de Simulación Académica Funcional
En cumplimiento estricto con el **Principio C-002 (Separación entre Reglas Institucionales y Decisiones Técnicas)** y el **Principio C-017 (Interoperabilidad Controlada)** de la Constitución, se establece formalmente que:

1. **Datos Ficticios y Entorno Controlado:** El SGT-SIAAF es una **simulación académica funcional** desarrollada exclusivamente con fines de evaluación en la asignatura Desarrollo Basado en Plataformas. Todas las entidades, usuarios, cédulas, notas y documentos procesados en el sistema son datos ficticios de prueba.
2. **Aislamiento de Bases de Datos Productivas:** El sistema **NO posee acceso directo, credenciales ni permisos de escritura en las bases de datos productivas del SGA ni del SIAAF**. Toda interacción con estos sistemas se realiza mediante adaptadores desacoplados (*Adapters*) y servicios simulados (*Mocks*).
3. **Validez Legal de Documentos:** La generación o carga de documentos de prueba (como borradores de providencias o memorandos) dentro de la plataforma **NO otorga validez legal institucional ni sustituye el criterio, la autoridad ni las firmas físicas/electrónicas oficiales de las autoridades universitarias**.

### 2.3 Delimitación del Alcance por Fases
* **Fase 1 — MVP (Prioridad Alta): Subproceso de Declaratoria de Aptitud Legal (Art. 235 RRA-UNL).** Constituye el alcance exclusivo del MVP para la Unidad 1 del sílabo. Comprende el registro de solicitudes, la petición interna de certificados sin correo, el checklist digital de los 5 requisitos base, la gestión de observaciones, la emisión del informe legal y el registro de la declaratoria por el Decano/a.
* **Fase 2 — Incremento (Prioridad Media): Subproceso de Sustentación y Defensa (Arts. 236–237 RRA-UNL).** Diseño preliminar para la programación de defensas, designación de tribunal evaluador (3 docentes titulares), recepción de memoria digital, registro de calificaciones individuales (escala 0-10) y generación del borrador del acta de grado (conservando firma autógrafa física).
* **Fase 3 — Incremento (Prioridad Baja): Subproceso de Cierre, Acta Consolidada y Registro SENESCYT (Arts. 243–244 RRA-UNL).** Diseño preliminar para la consolidación del expediente digital por Secretaría General, la autorización del Rector y el seguimiento del envío hacia la SENESCYT.

---

## 3. CONTEXTO DEL PROBLEMA, DIAGNÓSTICO Y JUSTIFICACIÓN

### 3.1 Diagnóstico de la Situación Actual
El trámite de titulación de grado en la UNL se gestiona actualmente de forma manual, presencial e informal a través de correos electrónicos personales o institucionales `[01-problema-contexto.md]`. Esta situación genera las siguientes deficiencias operativas:

1. **Pérdida y Duplicación de Documentos:** Las solicitudes enviadas por correo se traspapelan entre las bandejas de entrada de las secretarías, obligando al estudiante a reenviar sus certificados múltiples veces.
2. **Falta de Trazabilidad y Transparencia:** El estudiante desconoce el estado real de su trámite, quién es el funcionario responsable en cada etapa o cuánto tiempo falta para recibir respuesta.
3. **Incertidumbre en los Certificados Requeridos:** Los certificados de prácticas preprofesionales, suficiencia de idioma B1 y no adeudar a Tesorería se solicitan de forma dispersa al no contar con un sistema centralizado.
4. **Incumplimiento de Plazos Reglamentarios:** La revisión manual mediante hojas de papel dificulta auditar el cumplimiento del plazo de 8 días laborables exigido por el Art. 235 del RRA-UNL.

### 3.2 Tabla Comparativa: Proceso Manual Actual vs Propuesta Digitalizada SGT-SIAAF

| N.º | Etapa del Trámite | Proceso Manual Actual | Propuesta Digitalizada SGT-SIAAF | Beneficio Directo |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Pedir Récord Académico | Correo informal a la Secretaria de Carrera. | Petición interna en la plataforma con enrutamiento automático. | Elimina correos perdidos y notifica a la Secretaria. |
| **2** | Obtener Récord Académico | Secretaria consulta en el SGA y reenvía en PDF. | Secretaria sube el récord al expediente; a futuro, servicio Mock del SGA. | Registro centralizado y reutilizable en la plataforma. |
| **3** | Legalizar Récord Académico | Traslado físico o correo al Secretario/a-Abogado/a. | Cambio de estado a `LEGALIZADO` en la bandeja del jurista. | Trazabilidad inmutable de quién y cuándo legalizó. |
| **4** | Certificado de Prácticas | Solicitud presencial al Responsable de Prácticas. | Petición interna registrada y legalizada por el Director de Carrera. | Eliminación de trámites presenciales. |
| **5** | Certificado Idioma B1 | Trámite manual en el Instituto de Idiomas. | Carga del certificado por el estudiante o rol del Instituto de Idiomas. | Validación digital centralizada en el expediente. |
| **6** | Certificado de Tesorería | Certificado físico emitido por Tesorería. | Carga del certificado por el estudiante o rol de Tesorería. | Registro digital verificado en checklist. |
| **7** | Certificado Director Trabajo | Carta física firmada por el Director de Trabajo. | Carga del documento firmado en la plataforma. | Expediente completo en formato digital. |
| **8** | Verificación de Requisitos | Revisión manual con hoja de checklist en papel. | Checklist digital en pantalla con los 5 requisitos del Art. 235. | Verificación estructurada con bloqueo de informes. |
| **9** | Notificación de Observación | Llamada telefónica o correo no oficial. | Registro de observación escrita y notificación automática al estudiante. | Comunicación oficial y accionable para subsanar. |
| **10** | Control de Plazo de 8 Días | Control manual o inexistente. | Registro inmutable de timestamp en `ENVIADA` y cálculo de fecha límite. | Cumplimiento reglamentario auditable. |
| **11** | Informe y Declaratoria | Redacción manual en Word e impresión física. | Borradores PDF autogenerados desde plantillas (#590 y #162). | Estandarización documental y reducción de tiempos. |

---

## 4. OBJETIVOS DEL PRODUCTO

### 4.1 Objetivo General
Desarrollar una plataforma informática web y móvil basada en una arquitectura monolítica modular en **Django REST Framework** y **PostgreSQL**, que digitalice, controle y audite la fase administrativa del trámite de titulación de pregrado en la Carrera de Computación de la FEIRNNR-UNL, garantizando el cumplimiento de la normativa institucional, la trazabilidad inmutable de las actuaciones y el aislamiento estricto respecto a los sistemas legados productivos.

### 4.2 Objetivos Específicos
1. **Digitalizar la Fase 1 (MVP — Aptitud Legal):** Implementar la recepción de solicitudes, la petición interna de certificados, la verificación mediante checklist digital, el registro de observaciones accionables y la emisión de resoluciones modelo (#590 y #162).
2. **Garantizar el Control de Acceso Basado en Roles (RBAC):** Implementar la autenticación basada en tokens JWT y la autorización server-side para 8 roles institucionales en cumplimiento con los Principios C-004 y C-005 de la Constitución.
3. **Asegurar la Integridad Documental:** Proveer mecanismos de validación estricta en servidor para la carga de archivos PDF (máximo 10 MB, verificación de tipo MIME y *magic bytes*) conforme al Principio C-006.
4. **Exponer una API RESTful Versionada:** Diseñar y documentar al 100% la API bajo el estándar OpenAPI v3 en la ruta `/api/v1/` para consumo transparente desde clientes Web y Móviles (Principio C-010).
5. **Asegurar la Calidad mediante Pruebas Automatizadas:** Construir una suite de pruebas automatizadas con `pytest` que alcance más del 70% de cobertura en la lógica de negocio, permisos RBAC y transiciones de estados (Principio C-011).

---

## 5. ALCANCE DEL PRODUCTO Y DELIMITACIÓN TÉCNICA

### 5.1 Alcance Funcional del MVP (Fase 1 — Aptitud Legal)
El MVP contempla exclusivamente las siguientes capacidades funcionales para la Fase 1:

1. **Gestión de Expedientes:** Creación, consulta, actualización en borrador y envío formal del expediente de aptitud legal.
2. **Petición Interna de Certificados:** Generación de solicitudes internas hacia dependencias universitarias evitando el uso de correo electrónico.
3. **Carga y Gestión Documental:** Carga, visualización, reemplazo versionado y descarga de archivos PDF por requisito.
4. **Bandejas Operativas por Rol:** Interfaces de trabajo filtradas por estado y área de competencia para los 8 roles del sistema.
5. **Checklist Digital de Verificación:** Módulo interactivo para que el Secretario/a-Abogado/a valide los 5 requisitos del Art. 235 RRA-UNL.
6. **Módulo de Observaciones Accionables:** Registro de inconsistencias por requisito con cambio automático a estado `OBSERVADA` y notificación.
7. **Emisión e Inmutabilidad de Resoluciones:** Generación de borradores PDF del informe legal (#590) y registro de la declaratoria del Decano/a (#162).
8. **Motor de Notificaciones Internas:** Sistema de alertas dentro de la plataforma para informar cambios de estado y observaciones.
9. **Bitácora Inmutable de Auditoría:** Registro automático de todos los eventos relevantes (usuario, rol, timestamp, IP, acción).

### 5.2 Alcance por Fases Tecnológicas
* **Backend:** Monolito modular desarrollado en **Python 3.12+**, **Django 5.x** y **Django REST Framework (DRF)**, respaldado por **PostgreSQL**, ejecutado en contenedores **Docker / Docker Compose**.
* **Cliente Web:** Aplicación web SPA/MPA desarrollada en HTML5/CSS3/JavaScript (o framework moderno) consumiendo la API REST.
* **Cliente Móvil:** Aplicación móvil multiplataforma para consulta de estado, recepción de notificaciones y visualización de expedientes.

### 5.3 Fuera del Alcance (Exclusiones Explícitas)
Quedan completamente excluidas del alcance del proyecto las siguientes capacidades:

1. **Gestión Académica:** No se gestionan asignaturas, contenidos, asistencias ni matrículas de las materias de titulación.
2. **Reescritura en Bases de Datos Legadas:** Prohibición absoluta de ejecutar inserciones o modificaciones en las BD del SGA o SIAAF.
3. **Firma Electrónica PKI Automática en MVP:** El sistema no integra un motor interno de firma digital con certificados X.509; los documentos firmados electrónicamente se firman fuera del sistema e ingresan como anexos PDF.
4. **Toma de Decisiones Automáticas:** El sistema no emite la aptitud legal de forma autónoma; las resoluciones dependen del registro explícito por las autoridades humanas.
5. **Notificaciones Masivas por SMS o WhatsApp:** Limitado a notificaciones internas en la plataforma y correos opcionales vía SMTP.

### 5.4 Supuestos y Restricciones Técnicas
* **Restricción R-01:** El tamaño máximo permitido por archivo adjunto es de **10 MB**, en formato estrictamente **PDF**.
* **Restricción R-02:** El backend debe desplegarse y ejecutarse de forma reproducible mediante `docker-compose up`.
* **Supuesto S-01:** La Universidad proveerá el marco reglamentario para definir si el plazo de 8 días se pausa o reinicia en observaciones.

---

## 6. ACTORES DEL SISTEMA Y MATRIZ DE PERMISOS (RBAC)

### 6.1 Descripción de los 8 Roles Institucionales Confirmados
En cumplimiento con el **Principio C-004 (Identidad y Autorización Segura RBAC)** de la Constitución, el sistema define 8 roles:

1. `ESTUDIANTE`: Aspirante a titulación. Crea solicitudes, solicita certificados internos, adjunta PDF, subsana observaciones y consulta su estado.
2. `SECRETARIA_CARRERA`: Atiende peticiones de récord académico, sube el documento emitido y gestiona la legalización ante Secretaría-Abogacía.
3. `SECRETARIO_ABOGADO`: Revisa el checklist digital, legaliza el récord, registra observaciones, emite el informe de aptitud legal (#590) y levanta actas de defensa.
4. `ANALISTA_APOYO`: Personal técnico de apoyo que prepara los borradores del informe, providencia y checklist para revisión del Secretario/a-Abogado/a.
5. `DECANO`: Máxima autoridad facultativa. Revisa el informe legal y registra la declaratoria de aptitud adjuntando el memorando firmado (#162).
6. `DIRECTOR_CARRERA`: Legaliza el certificado de prácticas preprofesionales, recibe notificaciones y designa el tribunal evaluador de la defensa (Fase 2).
7. `RESPONSABLE_DEPENDENCIA`: Roles opcionales de unidades emisoras (Tesorería, Idiomas, Prácticas) que atienden peticiones específicas.
8. `ADMINISTRADOR`: Administra usuarios, asignación de roles RBAC, parámetros globales y el catálogo configurable de requisitos.

### 6.2 Matriz Detallada de Permisos (Rol × Recurso × Acción × Endpoint HTTP)

| Recurso / Endpoint | Acción HTTP | `ESTUDIANTE` | `SECRETARIA_CARRERA` | `SECRETARIO_ABOGADO` | `ANALISTA_APOYO` | `DECANO` | `DIRECTOR_CARRERA` | `ADMIN` |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `/api/v1/expedientes/` | `POST` (Crear) | **Permitido** | Denegado | Denegado | Denegado | Denegado | Denegado | **Permitido** |
| `/api/v1/expedientes/` | `GET` (Listar) | Propio | Carrera | Facultad | Facultad | Facultad | Carrera | Todos |
| `/api/v1/expedientes/{id}/` | `GET` (Ver) | Propio | Carrera | Facultad | Facultad | Facultad | Carrera | Todos |
| `/api/v1/expedientes/{id}/enviar/` | `POST` (Enviar) | Propio | Denegado | Denegado | Denegado | Denegado | Denegado | Denegado |
| `/api/v1/peticiones/` | `POST` (Certificado) | Propio | Denegado | Denegado | Denegado | Denegado | Denegado | Denegado |
| `/api/v1/peticiones/{id}/documento/` | `POST` (Sube PDF) | Propio | Asignado | Asignado | Asignado | Denegado | Asignado | **Permitido** |
| `/api/v1/checklist/{id}/` | `PUT` / `PATCH` | Denegado | Denegado | **Permitido** | Borrador | Denegado | Denegado | **Permitido** |
| `/api/v1/expedientes/{id}/observar/` | `POST` | Denegado | Denegado | **Permitido** | Denegado | Denegado | Denegado | Denegado |
| `/api/v1/informes/` | `POST` (Emitir) | Denegado | Denegado | **Permitido** | Borrador | Denegado | Denegado | Denegado |
| `/api/v1/declaratorias/` | `POST` (Declarar) | Denegado | Denegado | Denegado | Denegado | **Permitido** | Denegado | Denegado |
| `/api/v1/catalogos/requisitos/` | `POST`/`PUT` | Denegado | Denegado | Denegado | Denegado | Denegado | Denegado | **Permitido** |

---

## 7. MODELO CONCEPTUAL DEL DOMINIO (ENTIDADES Y ATRIBUTOS)

En cumplimiento con el **Principio C-008 (Auditoría y Trazabilidad)** y el **Principio C-009 (Integridad Transaccional)**, el dominio se modela mediante las siguientes entidades relacionales en PostgreSQL:

### 7.1 Entidad `ExpedienteTitulacion`
Representa el contenedor unificado del trámite de titulación de un estudiante.
* **Atributos:** `id` (UUIDv4, PK), `numero_expediente` (VarChar, Único), `estudiante_id` (FK User), `carrera_id` (FK Carrera), `estado` (Enum: `BORRADOR`, `ENVIADA`, `EN_VERIFICACION`, `OBSERVADA`, `INFORME_EMITIDO`, `DECLARADA_APTA`, `CANCELADA`), `fecha_creacion` (DateTime), `fecha_recepcion` (DateTime, Nulable), `fecha_limite_atencion` (DateTime, Nulable), `numero_providencia` (VarChar, Nulable), `activa` (Boolean).
* **Relaciones:** 1:N con `PeticionDocumental`, 1:N con `ObservacionAccionable`, 1:N con `EventoAuditoria`.

### 7.2 Entidad `CatalogoDocumental`
Define el catálogo configurable de requisitos de titulación.
* **Atributos:** `id` (BigInt, PK), `codigo_requisito` (VarChar, Único), `nombre` (VarChar), `descripcion` (Text), `es_obligatorio_base` (Boolean), `fase` (Enum: `FASE_1`, `FASE_2`, `FASE_3`), `rol_emisor_sugerido` (Enum Rol), `activo` (Boolean).

### 7.3 Entidad `PeticionDocumental`
Representa la solicitud atómica de un certificado o requisito específico dentro del expediente.
* **Atributos:** `id` (UUIDv4, PK), `expediente_id` (FK `ExpedienteTitulacion`), `requisito_id` (FK `CatalogoDocumental`), `estado` (Enum: `PENDIENTE`, `SOLICITADO`, `CARGADO`, `LEGALIZADO`, `VERIFICADO`, `OBSERVADO`), `dependencia_emisora` (Enum Rol), `fecha_solicitud` (DateTime), `fecha_actualizacion` (DateTime).
* **Relaciones:** 1:N con `DocumentoEntregado`.

### 7.4 Entidad `DocumentoEntregado`
Almacena la metadata de los archivos PDF adjuntos a una petición.
* **Atributos:** `id` (UUIDv4, PK), `peticion_id` (FK `PeticionDocumental`), `version` (Integer), `archivo_path` (VarChar), `nombre_original` (VarChar), `tamanio_bytes` (BigInt), `hash_sha256` (VarChar), `tipo_mime` (VarChar), `subido_por` (FK User), `fecha_carga` (DateTime), `es_vigente` (Boolean).

### 7.5 Entidad `ObservacionAccionable`
Registra las deficiencias identificadas durante la verificación.
* **Atributos:** `id` (UUIDv4, PK), `expediente_id` (FK `ExpedienteTitulacion`), `peticion_id` (FK `PeticionDocumental`), `registrada_por` (FK User), `motivo_observacion` (Text), `fecha_registro` (DateTime), `resuelta` (Boolean), `fecha_resolucion` (DateTime, Nulable).

### 7.6 Entidad `NotificacionInterna`
Gestiona las alertas y avisos dentro del sistema.
* **Atributos:** `id` (UUIDv4, PK), `usuario_destino` (FK User), `expediente_id` (FK `ExpedienteTitulacion`), `titulo` (VarChar), `mensaje` (Text), `leida` (Boolean), `fecha_creacion` (DateTime).

### 7.7 Entidad `EventoAuditoria`
Bitácora inmutable de eventos de seguridad y negocio (Principio C-008).
* **Atributos:** `id` (BigInt, PK), `expediente_id` (FK `ExpedienteTitulacion`, Nulable), `usuario` (FK User), `rol_ejecutado` (Enum Rol), `accion` (VarChar), `detalles_json` (JSONB), `ip_origen` (VarChar), `timestamp` (DateTime).

---

## 8. FLUJOS PRINCIPALES DEL SISTEMA (SECUENCIAS Y TRANSICIONES)

### FL-01: Creación e Inicio del Expediente de Aptitud Legal (`BORRADOR` -> `ENVIADA`)
1. **Precondición:** Estudiante autenticado con token JWT válido.
2. **Paso 1:** Estudiante invoca `POST /api/v1/expedientes/`. El backend crea un `ExpedienteTitulacion` en estado `BORRADOR` e inicializa automáticamente las 5 peticiones documentales base del Art. 235 RRA-UNL.
3. **Paso 2:** Estudiante realiza las peticiones internas de certificados y adjunta los documentos PDF correspondientes.
4. **Paso 3:** Estudiante invoca `POST /api/v1/expedientes/{id}/enviar/`.
5. **Paso 4 (Motor de Estados):** El backend verifica que las 5 peticiones posean archivos vigentes. Si cumple, actualiza el estado a `ENVIADA`, registra inmutablemente la `fecha_recepcion` (timestamp UTC), asigna el `numero_providencia` (ej. `PROV-590-2026`) y calcula la `fecha_limite_atencion` sumando 8 días laborables (Principio C-007).
6. **Postcondición:** Expediente en estado `ENVIADA`, visible en la bandeja del Secretario/a-Abogado/a y Analista de Apoyo.

### FL-02: Petición Interna de Certificados sin Correo Electrónico
1. **Precondición:** Expediente en estado `BORRADOR` u `OBSERVADA`.
2. **Paso 1:** Estudiante invoca `POST /api/v1/peticiones/{id}/solicitar-emision/`.
3. **Paso 2:** El backend cambia el estado de la petición a `SOLICITADO` e inserta una `NotificacionInterna` dirigida a la bandeja de la dependencia emisora (ej. `SECRETARIA_CARRERA`).
4. **Paso 3:** El funcionario emisor atiende la petición subiendo el archivo PDF mediante `POST /api/v1/peticiones/{id}/documento/`.
5. **Postcondición:** Petición en estado `CARGADO`, archivo PDF validado y almacenado.

### FL-03: Verificación con Checklist Digital y Emisión del Informe Legal (`EN_VERIFICACION` -> `INFORME_EMITIDO`)
1. **Precondición:** Expediente en estado `ENVIADA` o `EN_VERIFICACION`.
2. **Paso 1:** Secretario/a-Abogado/a consulta la bandeja e invoca `GET /api/v1/expedientes/{id}/checklist/`.
3. **Paso 2:** El jurista evalúa cada requisito y marca `VERIFICADO` mediante `PUT /api/v1/checklist/{id}/`.
4. **Paso 3:** Con las 5 peticiones en `VERIFICADO`, el Secretario/a-Abogado/a invoca `POST /api/v1/informes/` para generar e inmutabilizar el informe legal modelo Providencia N° 590.
5. **Paso 4:** El motor de estados cambia el expediente a `INFORME_EMITIDO` y notifica al Decano/a.
6. **Postcondición:** Informe legal generado, expediente listo para resolución del Decano/a.

### FL-04: Registro, Notificación y Subsanación de Observaciones (`OBSERVADA` -> `EN_VERIFICACION`)
1. **Precondición:** Requisito documental con inconsistencias o ilegible.
2. **Paso 1:** Secretario/a-Abogado/a invoca `POST /api/v1/expedientes/{id}/observar/` enviando el `peticion_id` y el `motivo_observacion`.
3. **Paso 2:** El backend cambia el estado de la petición a `OBSERVADO`, el estado del expediente a `OBSERVADA` y genera una `NotificacionInterna` al estudiante.
4. **Paso 3:** El estudiante consulta la observación, subsana el documento y sube un nuevo PDF mediante `POST /api/v1/peticiones/{id}/documento/`.
5. **Paso 4:** El backend incrementa la versión del documento, marca la observación como resuelta y retorna el expediente al estado `EN_VERIFICACION`.
6. **Postcondición:** Documento subsanado con historial de versiones preservado.

### FL-05: Declaratoria de Aptitud Legal por el Decano/a (`INFORME_EMITIDO` -> `DECLARADA_APTA`)
1. **Precondición:** Expediente en estado `INFORME_EMITIDO`.
2. **Paso 1:** Decano/a (o Analista autorizado) consulta el expediente y el informe legal.
3. **Paso 2:** Decano/a sube el memorando de declaratoria firmado electrónicamente fuera del sistema (modelo #162) mediante `POST /api/v1/declaratorias/`.
4. **Paso 3:** El backend valida el archivo PDF, cambia el estado del expediente a `DECLARADA_APTA` y despacha notificaciones con copia a la Secretaria Abogada, Director de Carrera y Estudiante.
5. **Postcondición:** Aptitud legal declarada, culminación exitosa de la Fase 1.

---

## 9. HISTORIAS DE USUARIO (HU-001 a HU-010)

### HU-001: Creación del Expediente de Titulación
* **Como** Estudiante Simulado,
* **Quiero** registrar una solicitud de declaratoria de aptitud legal seleccionando mi carrera,
* **Para** iniciar formalmente mi trámite de titulación de manera digital.
* **Precondiciones:** Usuario autenticado con rol `ESTUDIANTE` y sin expediente activo en curso.
* **Criterios de Aceptación (Dado / Cuando / Entonces):**
  * **Dado** que el estudiante no posee expedientes activos,
  * **Cuando** realiza una petición `POST /api/v1/expedientes/` con su `carrera_id`,
  * **Entonces** el sistema crea un expediente en estado `BORRADOR`, inicializa los 5 requisitos base en `PENDIENTE` y retorna código HTTP `201 Created`.
* **Trazabilidad:** `RF-001`, `RN-001`, `Principio C-007`.

### HU-002: Petición Interna de Certificados
* **Como** Estudiante Simulado,
* **Quiero** solicitar la emisión interna de mi récord académico y certificados dentro del sistema,
* **Para** evitar realizar solicitudes informales por correo electrónico a la secretaría.
* **Precondiciones:** Expediente en estado `BORRADOR` u `OBSERVADA`.
* **Criterios de Aceptación:**
  * **Dado** una petición en estado `PENDIENTE`,
  * **Cuando** el estudiante envía `POST /api/v1/peticiones/{id}/solicitar-emision/`,
  * **Entonces** el estado cambia a `SOLICITADO` y se notifica a la bandeja de la dependencia correspondiente.
* **Trazabilidad:** `RF-004`, `Docente`, `Principio C-004`.

### HU-003: Carga de Archivos PDF con Validación Estricta
* **Como** Usuario Autorizado,
* **Quiero** adjuntar certificados en formato PDF de hasta 10 MB,
* **Para** respaldar documentalmente los requisitos del expediente.
* **Precondiciones:** Petición válida asociada a un expediente editable.
* **Criterios de Aceptación:**
  * **Dado** un archivo adjunto en una petición,
  * **Cuando** el usuario invoca `POST /api/v1/peticiones/{id}/documento/`,
  * **Entonces** el servidor valida que el tamaño sea <= 10 MB, la extensión sea `.pdf` y los *magic bytes* correspondan a `%PDF-`, persistiendo el archivo con hash SHA-256 y retornando HTTP `201 Created`. Si falla, retorna HTTP `400 Bad Request`.
* **Trazabilidad:** `RF-005`, `RNF-004`, `RN-009`, `Principio C-006`.

### HU-004: Envío Formal y Registro de Marca de Tiempo
* **Como** Estudiante Simulado,
* **Quiero** enviar mi solicitud de aptitud legal una vez completados mis documentos,
* **Para** iniciar el cómputo oficial del plazo reglamentario de atención.
* **Precondiciones:** Expediente en `BORRADOR` con los 5 requisitos cargados.
* **Criterios de Aceptación:**
  * **Dado** un expediente con 5 documentos vigentes,
  * **Cuando** el estudiante ejecuta `POST /api/v1/expedientes/{id}/enviar/`,
  * **Entonces** el backend cambia el estado a `ENVIADA`, registra la fecha/hora UTC inmutable, asigna el número de providencia y calcula la fecha límite a 8 días laborables, retornando HTTP `200 OK`.
* **Trazabilidad:** `RF-002`, `RF-003`, `RN-002`, `Plantilla #590`, `Principio C-007`.

### HU-005: Bandejas Operativas por Rol y Dependencia
* **Como** Funcionario Universitario (Secretaria / Abogacía / Decanato),
* **Quiero** consultar una bandeja filtrada con las solicitudes asignadas a mi área,
* **Para** gestionar oportunamente los trámites de mi competencia.
* **Precondiciones:** Usuario autenticado con rol administrativo.
* **Criterios de Aceptación:**
  * **Dado** un funcionario autenticado,
  * **Cuando** consulta `GET /api/v1/expedientes/bandeja/`,
  * **Entonces** el sistema retorna únicamente los expedientes pertenecientes a su carrera/facultad en los estados que requieren su intervención (Principio C-005).
* **Trazabilidad:** `RF-012`, `RNF-002`, `RNF-003`, `Principio C-005`.

### HU-006: Evaluación con Checklist Digital
* **Como** Secretario/a-Abogado/a,
* **Quiero** validar individualmente cada uno de los 5 requisitos mediante un checklist digital,
* **Para** verificar la conformidad legal previa a la emisión del informe.
* **Precondiciones:** Expediente en estado `ENVIADA` o `EN_VERIFICACION`.
* **Criterios de Aceptación:**
  * **Dado** el checklist digital de un expediente,
  * **Cuando** el Secretario/a-Abogado/a envía `PUT /api/v1/checklist/{id}/` marcando `VERIFICADO` o `OBSERVADO`,
  * **Entonces** el sistema actualiza el estado del requisito y registra al usuario revisor.
* **Trazabilidad:** `RF-006`, `Plantilla #590`, `Principio C-007`.

### HU-007: Registro y Notificación de Observaciones
* **Como** Secretario/a-Abogado/a,
* **Quiero** registrar el motivo de rechazo de un requisito observado,
* **Para** notificar claramente al estudiante y bloquear el trámite hasta su corrección.
* **Precondiciones:** Requisito con inconsistencias.
* **Criterios de Aceptación:**
  * **Dado** un expediente en verificación,
  * **Cuando** el Secretario/a-Abogado/a invoca `POST /api/v1/expedientes/{id}/observar/` con el motivo escrito,
  * **Entonces** el sistema marca el requisito como `OBSERVADO`, el expediente como `OBSERVADA` e impide técnicamente la emisión del informe legal.
* **Trazabilidad:** `RF-007`, `RN-003`, `EX-007`, `Principio C-007`.

### HU-008: Subsanación de Documentos Observados
* **Como** Estudiante Simulado,
* **Quiero** reemplazar el archivo de un requisito observado,
* **Para** corregir la deficiencia señalada y reanudar mi trámite.
* **Precondiciones:** Expediente en estado `OBSERVADA`.
* **Criterios de Aceptación:**
  * **Dado** una petición en estado `OBSERVADO`,
  * **Cuando** el estudiante sube un nuevo PDF válido,
  * **Entonces** el sistema asigna la versión N+1, marca la observación como resuelta, cambia el expediente a `EN_VERIFICACION` y conserva el archivo previo en el historial.
* **Trazabilidad:** `RF-008`, `RN-011`, `Principio C-006`.

### HU-009: Emisión del Informe Legal de Aptitud
* **Como** Secretario/a-Abogado/a,
* **Quiero** emitir el informe legal de aptitud cuando los 5 requisitos estén verificados,
* **Para** recomendar formalmente la declaratoria de aptitud al Decano/a.
* **Precondiciones:** Expediente en `EN_VERIFICACION` con las 5 peticiones en `VERIFICADO`.
* **Criterios de Aceptación:**
  * **Dado** un expediente con 100% de requisitos verificados,
  * **Cuando** el Secretario/a-Abogado/a envía `POST /api/v1/informes/`,
  * **Entonces** el sistema genera e inmutabiliza el informe legal modelo Providencia N° 590, cambia el estado a `INFORME_EMITIDO` y notifica al Decano/a. Si existe un requisito en `OBSERVADO`, retorna HTTP `422 Unprocessable Entity`.
* **Trazabilidad:** `RF-009`, `RF-010`, `RN-003`, `RN-004`, `Plantilla #590`.

### HU-010: Declaratoria de Aptitud Legal por el Decano/a
* **Como** Decano/a de la Facultad,
* **Quiero** registrar la declaratoria de aptitud legal adjuntando el memorando firmado electrónicamente,
* **Para** autorizar formalmente al estudiante a defender su trabajo de titulación.
* **Precondiciones:** Expediente en estado `INFORME_EMITIDO`.
* **Criterios de Aceptación:**
  * **Dado** un expediente con informe legal emitido,
  * **Cuando** el Decano/a invoca `POST /api/v1/declaratorias/` adjuntando el memorando modelo #162,
  * **Entonces** el sistema cambia el estado a `DECLARADA_APTA`, notifica con copia a las autoridades correspondientes y da por concluida la Fase 1.
* **Trazabilidad:** `RF-011`, `RN-004`, `Plantilla #162`, `Principio C-002`.

---

## 10. REQUISITOS FUNCIONALES (RF-001 a RF-016)

### RF-001: Registro e Inicialización de Solicitud
* **Descripción:** El sistema debe permitir al estudiante autenticado crear un expediente de aptitud legal en estado `BORRADOR` e inicializar las 5 peticiones documentales base del Art. 235 RRA-UNL.
* **Actor Principal:** `ESTUDIANTE`.
* **Entorno / Fase:** Backend API / Fase 1 (MVP).
* **Precondiciones:** Usuario autenticado sin expedientes activos en curso.
* **Entradas:** `carrera_id` (UUID).
* **Lógica / Comportamiento:** Validar la ausencia de expedientes activos, crear el registro `ExpedienteTitulacion` e insertar 5 registros `PeticionDocumental` asociadas a los requisitos del catálogo base.
* **Postcondiciones:** Expediente creado en `BORRADOR` con 5 peticiones en `PENDIENTE`.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-001`, `RN-001`, `Principio C-007`.

### RF-002: Recepción Inmutable y Marca de Tiempo
* **Descripción:** El sistema debe registrar inalterablemente la fecha y hora UTC de recepción, asignar el número correlativo de providencia/checklist y cambiar el estado a `ENVIADA` al recibir la confirmación del estudiante.
* **Actor Principal:** `ESTUDIANTE` / Engine Backend.
* **Precondiciones:** Expediente en `BORRADOR` con los 5 requisitos provistos de archivos vigentes.
* **Entradas:** `expediente_id` (UUID).
* **Lógica / Comportamiento:** Asignar `fecha_recepcion = ahora_utc()`, generar `numero_providencia` secuencial y cambiar estado a `ENVIADA`.
* **Postcondiciones:** Timestamp e identificador inmutables en base de datos.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-004`, `Plantilla #590`, `Principio C-007`.

### RF-003: Cómputo de Plazo Límite de 8 Días Laborables
* **Descripción:** El sistema debe calcular automáticamente la fecha límite de atención sumando 8 días laborables (excluyendo sábados, domingos y feriados configurados) a partir de la `fecha_recepcion`.
* **Actor Principal:** Engine Backend.
* **Precondiciones:** Transición del expediente a estado `ENVIADA`.
* **Lógica / Comportamiento:** Ejecutar algoritmo de suma de días hábiles sobre el calendario institucional y guardar `fecha_limite_atencion`.
* **Postcondiciones:** Fecha límite visible en las bandejas operativas.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-004`, `RN-002`, `RRA Art. 235`.

### RF-004: Petición Interna de Certificados Institucionales
* **Descripción:** El sistema debe permitir al estudiante solicitar la emisión interna de certificados (récord, prácticas, idioma, Tesorería) sin recurrir al correo electrónico, enrutando la solicitud a la bandeja del rol emisor.
* **Actor Principal:** `ESTUDIANTE`.
* **Precondiciones:** Expediente en `BORRADOR` u `OBSERVADA`.
* **Entradas:** `peticion_id` (UUID).
* **Lógica / Comportamiento:** Actualizar estado de la petición a `SOLICITADO` y generar `NotificacionInterna` al rol emisor.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-002`, `Docente`, `Principio C-004`.

### RF-005: Carga y Validación de Archivos PDF
* **Descripción:** El sistema debe permitir adjuntar archivos PDF a las peticiones documentales, ejecutando validaciones estrictas de tamaño (<= 10 MB), extensión (`.pdf`) y firma de encabezado (*magic bytes* `%PDF-`).
* **Actor Principal:** Todos los Roles autorizados.
* **Entradas:** Archivo binario multipart/form-data.
* **Lógica / Comportamiento:** Validar bytes en memoria backend, calcular hash SHA-256, almacenar el archivo en ubicaciones privadas y registrar metadata en `DocumentoEntregado`.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-003`, `RNF-004`, `RN-009`, `Principio C-006`.

### RF-006: Checklist Digital de Verificación
* **Descripción:** El sistema debe desplegar una interfaz interactiva de checklist para el Secretario/a-Abogado/a que permita evaluar individualmente los 5 requisitos base y adicionales configurados.
* **Actor Principal:** `SECRETARIO_ABOGADO`.
* **Precondiciones:** Expediente en `ENVIADA` o `EN_VERIFICACION`.
* **Lógica / Comportamiento:** Registrar la evaluación (`VERIFICADO` / `OBSERVADO`) por cada petición documental y guardar el usuario jurista revisor.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-006`, `Plantilla #590`, `Principio C-007`.

### RF-007: Registro de Observaciones Accionables y Bloqueo de Informe
* **Descripción:** El sistema debe permitir registrar el motivo escrito al marcar un requisito como `OBSERVADO`, cambiando el expediente a `OBSERVADA` e impidiendo técnicamente la emisión del informe legal.
* **Actor Principal:** `SECRETARIO_ABOGADO`.
* **Entradas:** `peticion_id`, `motivo_observacion` (Text).
* **Lógica / Comportamiento:** Insertar `ObservacionAccionable`, cambiar estado de petición a `OBSERVADO`, expediente a `OBSERVADA` y notificar al estudiante.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-007`, `RN-003`, `EX-007`, `Principio C-007`.

### RF-008: Subsanación y Reemplazo Versionado de Documentos
* **Descripción:** El sistema debe permitir al estudiante cargar un nuevo archivo PDF para reemplazar un requisito observado, asignando la versión N+1 y marcando la observación como resuelta.
* **Actor Principal:** `ESTUDIANTE`.
* **Precondiciones:** Expediente en estado `OBSERVADA`.
* **Lógica / Comportamiento:** Registrar nuevo `DocumentoEntregado` con `version = N+1`, marcar `ObservacionAccionable.resuelta = True`, retornar expediente a `EN_VERIFICACION` y conservar versión anterior.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-008`, `RN-011`, `Principio C-006`.

### RF-009: Emisión e Inmutabilidad del Informe Legal
* **Descripción:** El sistema debe permitir al Secretario/a-Abogado/a emitir e inmutabilizar el informe legal de aptitud cuando las 5 peticiones se encuentren en estado `VERIFICADO`.
* **Actor Principal:** `SECRETARIO_ABOGADO`.
* **Precondiciones:** Expediente en `EN_VERIFICACION` con 100% de requisitos en `VERIFICADO`.
* **Lógica / Comportamiento:** Generar el informe legal en PDF (modelo Providencia #590), inmutabilizar el registro, cambiar expediente a `INFORME_EMITIDO` y notificar al Decano/a.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-009`, `RN-003`, `RN-004`, `Plantilla #590`.

### RF-010: Autogeneración de Borradores PDF desde Plantillas
* **Descripción:** El sistema debe prellenar borradores de documentos en PDF (informes y providencias) combinando los datos del estudiante, fechas y checklist con las plantillas institucionales oficiales (#590).
* **Actor Principal:** Engine Backend / `ANALISTA_APOYO`.
* **Lógica / Comportamiento:** Utilizar motor de plantillas PDF en backend con datos del expediente e inyectar firma de borrador.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-009`, `Plantilla #590`, `Principio C-002`.

### RF-011: Registro de Declaratoria y Memorando (#162)
* **Descripción:** El sistema debe permitir al Decano/a registrar la resolución de declaratoria de aptitud legal adjuntando el memorando firmado electrónicamente fuera del sistema (modelo #162).
* **Actor Principal:** `DECANO`.
* **Precondiciones:** Expediente en estado `INFORME_EMITIDO`.
* **Lógica / Comportamiento:** Guardar el memorando en PDF, cambiar estado a `DECLARADA_APTA` y notificar con copia a la Secretaria Abogada, Director de Carrera y Estudiante.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-010`, `RN-004`, `Plantilla #162`.

### RF-012: Sistema de Notificaciones Internas por Rol
* **Descripción:** El sistema debe despachar alertas e insumos informativos internos dirigidos a los usuarios según su rol y ámbito ante cambios de estado, observaciones o resoluciones.
* **Actor Principal:** Engine Backend.
* **Lógica / Comportamiento:** Insertar registros en `NotificacionInterna` y exponer endpoint `GET /api/v1/notificaciones/`.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `HU-005`, `RNF-002`, `Principio C-004`.

### RF-013: Bitácora Inmutable de Auditoría
* **Descripción:** El sistema debe registrar de forma automática e inalterable cada evento relevante de negocio y seguridad en la tabla `EventoAuditoria`.
* **Actor Principal:** Engine Backend (Middleware / Signals).
* **Lógica / Comportamiento:** Guardar `usuario_id`, `rol`, `accion`, `ip`, `timestamp` y payload JSON del cambio.
* **Prioridad:** Alta (MVP).
* **Trazabilidad:** `RNF-015`, `Principio C-008`.

### RF-014: Programación de Defensa y Designación de Tribunal (Fase 2)
* **Descripción:** El sistema debe permitir al Director de Carrera designar el tribunal evaluador (3 docentes titulares: Presidente y 2 Vocales) y fijar fecha, hora y lugar de la defensa, excluyendo al Director del Trabajo.
* **Actor Principal:** `DIRECTOR_CARRERA`.
* **Entorno / Fase:** Fase 2 (Incremento).
* **Precondiciones:** Expediente en estado `DECLARADA_APTA`.
* **Lógica / Comportamiento:** Validar que el `director_trabajo_id` no conste entre los 3 juristas designados y guardar el registro `TribunalEvaluador`.
* **Prioridad:** Media (Fase 2).
* **Trazabilidad:** `RN-007`, `RRA Art. 236`.

### RF-015: Registro de Calificaciones y Acta con Firma Autógrafa (Fase 2)
* **Descripción:** El sistema debe permitir registrar las notas individuales de la sustentación (escala 0-10), promediar con el récord del SGA, determinar la mención cualitativa y generar el borrador del acta (conservando firma física autógrafa).
* **Actor Principal:** `SECRETARIO_ABOGADO` / Presidente de Tribunal.
* **Entorno / Fase:** Fase 2 (Incremento).
* **Lógica / Comportamiento:** Ponderar promedio final, asignar escala (`SOBRESALIENTE`, `MUY_BUENA`, `BUENA`, `REPROBADO`) y requerir escaneo de acta firmada a mano.
* **Prioridad:** Media (Fase 2).
* **Trazabilidad:** `RN-005`, `RN-006`, `RN-008`, `RRA Art. 237`, `Docente`.

### RF-016: Consolidación del Expediente y Registro SENESCYT (Fase 3)
* **Descripción:** El sistema debe permitir a Secretaría General estructurar el expediente digital consolidado de titulación en formato PDF-A interoperable y registrar la trazabilidad del envío a la SENESCYT.
* **Actor Principal:** `SECRETARIA_GENERAL` / Backend.
* **Entorno / Fase:** Fase 3 (Incremento).
* **Prioridad:** Baja (Fase 3).
* **Trazabilidad:** `RRA Arts. 243–244`.

---

## 11. REQUISITOS NO FUNCIONALES (RNF-001 a RNF-018)

### RNF-001: Autenticación Stateless basada en Tokens JWT
* **Categoría:** Seguridad / Autenticación.
* **Métrica / Especificación:** Toda petición protegida debe incluir el token JWT en la cabecera `Authorization: Bearer <token>`. El servidor debe validar firma, expiración y emisor sin consultar sesión en BD, devolviendo HTTP `401 Unauthorized` ante tokens inválidos.
* **Método de Verificación:** Pruebas de API automatizadas con `pytest`.
* **Trazabilidad:** `Principio C-004`, `ACD2`.

### RNF-002: Autorización Server-Side Rigurosa (RBAC)
* **Categoría:** Seguridad / Autorización.
* **Métrica / Especificación:** El middleware del backend debe verificar el rol del usuario contra la matriz RBAC para cada endpoint y verbo HTTP, retornando HTTP `403 Forbidden` ante intentos no autorizados.
* **Método de Verificación:** Suite de pruebas de seguridad con matriz de roles en `pytest`.
* **Trazabilidad:** `Principio C-004`, `ACD2`.

### RNF-003: Aislamiento de Datos por Ámbito y Protección IDOR
* **Categoría:** Seguridad / Privacidad IDOR.
* **Métrica / Especificación:** El backend debe filtrar las consultas a nivel de ORM para garantizar que un estudiante solo consulte sus expedientes y que los funcionarios solo accedan a trámites de su carrera/facultad, devolviendo HTTP `403` o `404` ante manipulaciones de ID (`Insecure Direct Object Reference`).
* **Método de Verificación:** Tests de penetración e intromisión de ID en `pytest`.
* **Trazabilidad:** `Principio C-005`, `Constitución`.

### RNF-004: Validación Estricta de Firma MIME y Magic Bytes
* **Categoría:** Seguridad / Integridad de Archivos.
* **Métrica / Especificación:** El servidor backend debe inspeccionar los primeros bytes del archivo (*magic bytes*) para confirmar el encabezado `%PDF-` antes de guardar en disco, rechazando archivos ejecutables o imágenes renombradas con HTTP `400 Bad Request`.
* **Método de Verificación:** Carga de ejecutables y scripts con extensión `.pdf` en tests.
* **Trazabilidad:** `Principio C-006`, `Constitución`.

### RNF-005: Rendimiento de la API REST Backend
* **Categoría:** Rendimiento.
* **Métrica / Especificación:** El tiempo de respuesta del servidor para endpoints de consulta GET (listado de expedientes, estados) debe ser inferior a **500 ms** en el noventa y cinco por ciento (p95) de las solicitudes bajo carga normal de 50 usuarios concurrentes.
* **Método de Verificación:** Pruebas de carga y rendimiento con `Locust`.
* **Trazabilidad:** `Principio C-010`, `ACD2`.

### RNF-006: Disponibilidad y Resiliencia de la API
* **Categoría:** Disponibilidad.
* **Métrica / Especificación:** La API backend debe mantener una disponibilidad del 99.5% durante el periodo de pruebas de evaluación, soportando reinicios controlados de contenedores Docker sin pérdida de datos persistidos.
* **Método de Verificación:** Monitoreo de salud mediante endpoint `/api/v1/health/`.
* **Trazabilidad:** `Principio C-014`, `Constitución`.

### RNF-007: Estándar RESTful, Versionado y OpenAPI v3
* **Categoría:** Interoperabilidad / Arquitectura.
* **Métrica / Especificación:** La API debe exponerse bajo el prefijo `/api/v1/`, emplear métodos HTTP con semántica correcta (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), retornar formato JSON estructurado y generar automáticamente el esquema OpenAPI v3 (Swagger UI).
* **Método de Verificación:** Validación de esquema OpenAPI y cliente Swagger.
* **Trazabilidad:** `Principio C-010`, `Sílabo-DBP`.

### RNF-008: Interoperabilidad Desacoplada mediante Adapters y Mocks
* **Categoría:** Interoperabilidad / Legados.
* **Métrica / Especificación:** Toda comunicación con sistemas externos (SGA, SIAAF, correo) debe realizarse a través de interfaces *Adapter*. Para el MVP, la información del SGA se proveerá mediante servicios *Mock* sin conexión directa a BD externas.
* **Método de Verificación:** Inspección de código en el paquete `adapters/`.
* **Trazabilidad:** `Principio C-017`, `Constitución`.

### RNF-009: Arquitectura Monolito Modular en Django 5.x / DRF
* **Categoría:** Mantenibilidad / Arquitectura.
* **Métrica / Especificación:** El backend se estructurará como un monolito modular con aplicaciones Django cohesionadas por dominio (`expedientes`, `documentos`, `usuarios`, `resoluciones`), con baja dependencia acoplada.
* **Método de Verificación:** Auditoría de arquitectura y dependencias entre apps.
* **Trazabilidad:** `Principio C-003`, `ADR Technical Decision`.

### RNF-010: Contenerización y Reproducibilidad con Docker Compose
* **Categoría:** DevOps / Reproducibilidad.
* **Métrica / Especificación:** Todo el entorno de desarrollo (Django backend, PostgreSQL, Nginx) debe compilarse y levantarse de forma 100% reproducible mediante el comando `docker-compose up --build`.
* **Método de Verificación:** Ejecución de despliegue en un entorno limpio de contenedor.
* **Trazabilidad:** `Principio C-013`, `Constitución`.

### RNF-011: Estándares de Código PEP 8 y Typing Estático
* **Categoría:** Calidad de Código.
* **Métrica / Especificación:** El código Python debe cumplir con el estándar PEP 8 comprobado mediante `flake8` / `black` e incluir anotaciones de tipo estático (*type hints*) en los servicios de negocio.
* **Método de Verificación:** Ejecución de linters en integración continua.
* **Trazabilidad:** `Principio C-016`, `Sílabo-DBP`.

### RNF-012: Pruebas Automatizadas con Cobertura >70%
* **Categoría:** Calidad / Pruebas.
* **Métrica / Especificación:** La suite de pruebas automatizadas ejecutadas con `pytest` / `pytest-django` debe cubrir más del 70% de las líneas de código del backend, incluyendo modelos, vistas API, permisos RBAC y motor de estados.
* **Método de Verificación:** Reporte de cobertura generado por `pytest-cov`.
* **Trazabilidad:** `Principio C-011`, `ACD2`.

### RNF-013: Accesibilidad UX conforme a WCAG 2.1 Nivel AA
* **Categoría:** Usabilidad / Accesibilidad.
* **Métrica / Especificación:** Los clientes Web y Móviles deben cumplir las pautas de accesibilidad WCAG 2.1 Nivel AA, garantizando contraste adecuado, navegación por teclado y etiquetas aria para lectores de pantalla.
* **Método de Verificación:** Auditoría automatizada con `Lighthouse`.
* **Trazabilidad:** `Principio C-015`, `Constitución`.

### RNF-014: Gestión Segura de Secretos por Entorno
* **Categoría:** Seguridad.
* **Métrica / Especificación:** Queda prohibido incluir claves secretas, contraseñas o tokens JWT hardcodeados en el código fuente. Toda configuración sensible debe leerse desde variables de entorno `.env`.
* **Método de Verificación:** Escaneo estático de código con `gitleaks`.
* **Trazabilidad:** `Principio C-012`, `Constitución`.

### RNF-015: Observabilidad, Logging Centralizado y Manejo de Errores
* **Categoría:** Mantenibilidad / Seguridad.
* **Métrica / Especificación:** El backend debe capturar excepciones no controladas y responder estructuradamente con códigos HTTP 4xx/5xx en JSON, omitiendo trazas internas de depuración (*stacktraces*) en producción y registrando el evento en logs rotativos.
* **Método de Verificación:** Provocación de excepciones en pruebas de integración.
* **Trazabilidad:** `Principio C-014`, `Constitución`.

### RNF-016: Protección de Datos Personales y Cifrado
* **Categoría:** Seguridad / Privacidad.
* **Métrica / Especificación:** La transmisión de datos debe realizarse sobre HTTPS con cifrado TLS 1.3. Los documentos PDF almacenados en servidor deben protegerse contra acceso directo mediante rutas privadas autenticadas.
* **Método de Verificación:** Pruebas de acceso directo a URLs de archivos.
* **Trazabilidad:** `Principio C-018`, `Constitución`.

### RNF-017: Gobernanza SDD y Auditoría de Código IA
* **Categoría:** Gobernanza / Metodología.
* **Métrica / Especificación:** Todo artefacto o módulo de código debe derivarse de la especificación aprobada. El código generado asistido por Inteligencia Artificial debe ser auditado y refrendado por los estudiantes responsables.
* **Método de Verificación:** Revisión de Pull Requests y trazabilidad en Git.
* **Trazabilidad:** `Principio C-019`, `Sílabo-DBP`.

### RNF-018: Registro de Decisiones mediante ADRs
* **Categoría:** Gobernanza / Documentación.
* **Métrica / Especificación:** Las decisiones de arquitectura relevantes (elección de frameworks, librerías PDF, esquemas de BD) deben registrarse en archivos Markdown en la carpeta `docs/adr/`.
* **Método de Verificación:** Inspección del directorio `docs/adr/`.
* **Trazabilidad:** `Principio C-020`, `Constitución`.

---

## 12. REGLAS DE NEGOCIO (RN-001 a RN-012)

* **RN-001: Cinco Requisitos Base de Aptitud Legal (Art. 235 RRA-UNL).** La declaratoria de aptitud legal exige la verificación obligatoria de: 1. Récord académico legalizado, 2. Certificado de prácticas/vinculación, 3. Certificado B1 de idioma, 4. Certificado del Director de Trabajo, y 5. Certificado de Tesorería de no adeudar.
* **RN-002: Plazo Ininterrumpido de 8 Días Laborables.** La atención de la solicitud de aptitud legal dispone de un plazo máximo de 8 días laborables contados a partir del registro inmutable de la recepción en estado `ENVIADA`.
* **RN-003: Efecto Bloqueante de Requisitos Observados o Pendientes.** Si al menos un requisito se encuentra en estado `OBSERVADO` o `PENDIENTE`, el sistema impedirá técnicamente la emisión del informe legal de aptitud.
* **RN-004: Separación de Competencias de Informe y Declaratoria.** La emisión del informe legal corresponde exclusivamente al Secretario/a-Abogado/a; la resolución de declaratoria de aptitud es atribución exclusiva del Decano/a.
* **RN-005: Inalterabilidad del Promedio Académico SGA.** El promedio del récord académico proviene del SGA e incluye homologaciones; el SGT-SIAAF lo toma como dato inmutable y no ejecuta recálculos.
* **RN-006: Firma Autógrafa Obligatoria en Actas de Sustentación (Fase 2).** El acta de calificación de la sustentación debe conservar la firma autógrafa física de los miembros del tribunal; el sistema registra las notas numéricas pero no sustituye la firma física.
* **RN-007: Conformación del Tribunal Evaluador (Fase 2, Art. 236).** El tribunal de sustentación se compone de 3 docentes titulares (Presidente y 2 Vocales). El Director del trabajo de titulación no puede integrar el tribunal evaluador.
* **RN-008: Escala Cuali-cuantitativa de Evaluación y Ponderación de Grado (Fase 2, Art. 237).** La sustentación se evalúa de 0 a 10. La nota final promedia el récord (SGA) y la sustentación: Sobresaliente (9.0-10), Muy Buena (8.0-8.99), Buena (7.0-7.99), Reprobado (< 7.0).
* **RN-009: Límite Estricto de Carga Documental.** Todo archivo adjunto debe ser de formato estrictamente PDF con un tamaño máximo de 10 MB y firma de encabezado `%PDF-`.
* **RN-010: Inmutabilidad de Marcas Temporales en Recepción.** Al pasar a estado `ENVIADA`, el sistema registra de manera inmutable la fecha, hora UTC y número correlativo de providencia/checklist.
* **RN-011: Conservación Inalterable del Historial de Versiones.** Al reemplazar un documento observado, el sistema conserva el archivo anterior asignando la versión N+1 para auditoría.
* **RN-012: Prohibición de Modificación Directa de Bases de Datos Legadas.** Queda terminantemente prohibido ejecutar operaciones de escritura o modificación directa en las bases de datos del SGA o SIAAF.

---

## 13. MATRIZ DE EXCEPCIONES Y ESCENARIOS ALTERNATIVOS (EX-001 a EX-010)

| ID | Nombre del Escenario | Desencadenante / Condición | Comportamiento Esperado del Sistema | Código HTTP / Payload |
| :--- | :--- | :--- | :--- | :--- |
| **EX-001** | Token JWT Ausente o Vencido | Petición a endpoint protegido sin cabecera `Authorization` o con token caducado. | Denegar el acceso y solicitar reautenticación limpia. | `401 Unauthorized` |
| **EX-002** | Acceso Denegado por RBAC | Estudiante u otro rol intenta invocar un endpoint fuera de sus permisos. | Rechazar la operación y registrar el intento en la bitácora de auditoría. | `403 Forbidden` |
| **EX-003** | Intento de Acceso IDOR a Expediente Ajeno | Usuario intenta consultar `/api/v1/expedientes/{id}` perteneciente a otro estudiante. | Filtrar la consulta a nivel ORM y responder con recurso no encontrado o prohibido. | `403 Forbidden` / `404 Not Found` |
| **EX-004** | Archivo Supera Límite de Tamaño | Intento de adjuntar un archivo PDF con tamaño mayor a 10 MB. | Rechazar la carga en servidor antes de guardar en disco e informar el límite. | `400 Bad Request` |
| **EX-005** | Formato de Archivo No Permitido o Magic Bytes Inválidos | Intento de adjuntar archivos con extensiones ejecutables o imágenes renombradas. | Validar *magic bytes* y rechazar el archivo solicitando un PDF válido. | `400 Bad Request` |
| **EX-006** | Transición de Estado Inválida | Intentar pasar una solicitud en `BORRADOR` directamente a `INFORME_EMITIDO`. | Rechazar la transición en el motor de estados y devolver transiciones permitidas. | `400 Bad Request` |
| **EX-007** | Intento de Informe con Requisitos Observados | Secretario/a-Abogado/a intenta emitir informe con peticiones en `OBSERVADO` o `PENDIENTE`. | Bloquear la operación por regla de negocio RN-003 e informar los requisitos pendientes. | `422 Unprocessable Entity` |
| **EX-008** | Falla en Servicio Adaptador / Mock | Indisponibilidad simulada o error en el adaptador del SGA. | Retornar respuesta de degradación controlada indicando reintento. | `503 Service Unavailable` |
| **EX-009** | Error Interno no Mapeado | Excepción no controlada en la lógica del servidor backend. | Capturar la excepción, omitir la traza interna en la respuesta y registrar en log. | `500 Internal Server Error` |
| **EX-010** | Tribunal Inválido con Director del Trabajo | Intento de asignar al Director del Trabajo como miembro del tribunal evaluador. | Rechazar la asignación por regla de negocio RN-007. | `422 Unprocessable Entity` |

---

## 14. CRITERIOS DE ACEPTACIÓN (CA-001 a CA-008)

### CA-001: Envío Exitoso y Registro de Marca de Tiempo (`HU-001`, `HU-004`, `RF-001`, `RF-002`, `RN-002`)
* **Dado** que un estudiante autenticado posee un expediente en estado `BORRADOR` con los 5 requisitos base provistos de archivos PDF válidos,
* **Cuando** invoca la acción `POST /api/v1/expedientes/{id}/enviar/`,
* **Entonces** el sistema actualiza el estado del expediente a `ENVIADA`, registra la `fecha_recepcion` en hora UTC, asigna el número correlativo de providencia (ej. `PROV-590-2026`), calcula la fecha límite a 8 días laborables y retorna código HTTP `200 OK` con la estructura JSON completa.

### CA-002: Petición Interna de Certificados sin Correo (`HU-002`, `RF-004`)
* **Dado** que un estudiante posee un expediente en estado `BORRADOR`,
* **Cuando** ejecuta `POST /api/v1/peticiones/{id}/solicitar-emision/` para el requisito de récord académico,
* **Entonces** el sistema cambia el estado de la petición a `SOLICITADO`, genera una `NotificacionInterna` en la bandeja del rol `SECRETARIA_CARRERA` y retorna HTTP `200 OK`.

### CA-003: Bloqueo de Emisión de Informe ante Requisito Observado (`HU-005`, `HU-007`, `RF-007`, `RF-009`, `RN-003`)
* **Dado** que un expediente en verificación posee 4 requisitos en estado `VERIFICADO` y 1 requisito en estado `OBSERVADO`,
* **Cuando** el Secretario/a-Abogado/a intenta ejecutar `POST /api/v1/informes/`,
* **Entonces** el sistema bloquea la transacción por regla RN-003, no genera el informe legal, mantiene el estado del expediente en `OBSERVADA` y retorna HTTP `422 Unprocessable Entity` detallando el requisito pendiente.

### CA-004: Subsanación de Requisito Observado y Versionado (`HU-008`, `RF-008`, `RN-011`)
* **Dado** que un expediente se encuentra en estado `OBSERVADA` con un motivo registrado,
* **Cuando** el estudiante adjunta un nuevo archivo PDF válido invocando `POST /api/v1/peticiones/{id}/documento/`,
* **Entonces** el sistema asigna la versión N+1 al nuevo archivo, marca la observación como resuelta, cambia el estado del expediente a `EN_VERIFICACION`, conserva la versión anterior para auditoría y retorna HTTP `201 Created`.

### CA-005: Emisión de Informe Legal por Secretaria Abogada (`HU-009`, `RF-009`, `RF-010`, `RN-004`)
* **Dado** que un expediente posee el 100% (5 de 5) de sus requisitos en estado `VERIFICADO`,
* **Cuando** el Secretario/a-Abogado/a invoca `POST /api/v1/informes/`,
* **Entonces** el sistema genera e inmutabiliza el borrador del informe legal en PDF (modelo Providencia #590), actualiza el estado del expediente a `INFORME_EMITIDO`, genera una notificación para el Decano/a y retorna HTTP `201 Created`.

### CA-006: Declaratoria de Aptitud por Decano/a con Memorando (#162) (`HU-010`, `RF-011`, `RN-004`)
* **Dado** que un expediente se encuentra en estado `INFORME_EMITIDO`,
* **Cuando** el Decano/a adjunta el memorando firmado electrónicamente fuera del sistema mediante `POST /api/v1/declaratorias/`,
* **Entonces** el sistema valida el PDF, cambia el estado a `DECLARADA_APTA`, despacha notificaciones con copia a las autoridades y retorna HTTP `200 OK`.

### CA-007: Registro de Notas de Sustentación y Acta con Firma Autógrafa (`RF-015`, `RN-006`, `RN-008`)
* **Dado** que un tribunal evaluador concluyó la sustentación individual de un estudiante,
* **Cuando** el Secretario/a-Abogado/a ingresa las calificaciones numéricas en `POST /api/v1/sustentaciones/{id}/calificaciones/`,
* **Entonces** el sistema calcula el promedio final integrando la nota del SGA, asigna la categorización cualitativa, genera el borrador del acta de grado, requiere adjuntar el escaneo del acta con firma autógrafa física y retorna HTTP `200 OK`.

### CA-008: Denegación de Acceso por Vulnerabilidad IDOR (`RNF-003`, `EX-003`)
* **Dado** que un estudiante 'A' autenticado intenta consultar el expediente `UUID-B` perteneciente a un estudiante 'B',
* **Cuando** invoca `GET /api/v1/expedientes/UUID-B/`,
* **Entonces** el servidor intercepta la consulta en el filtro ORM, niega el acceso y retorna HTTP `404 Not Found` o `403 Forbidden`, registrando el evento de violación en la bitácora de auditoría.

---

## 15. MATRIZ DE TRAZABILIDAD INTEGRAL DE REQUISITOS

| Fuente Primaria | Necesidad / Objetivo | Historia de Usuario | Requisito Funcional | Requisito No Funcional | Regla de Negocio | Escenario Excepción | Criterio Aceptación | Principio Constitución | Método Verificación |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `[RRA Art. 235]` | Digitalizar Aptitud Legal | `HU-001` | `RF-001` | `RNF-007` | `RN-001` | `EX-006` | `CA-001` | `Principio C-001` | Test `pytest` |
| `[Plantilla #590]` | Timestamp y Providencia | `HU-004` | `RF-002`, `RF-003` | `RNF-006` | `RN-002`, `RN-010` | `EX-006` | `CA-001` | `Principio C-007` | Test DB UTC |
| `[Docente]` | Eliminar correos informales | `HU-002` | `RF-004` | `RNF-002` | `RN-001` | `EX-001` | `CA-002` | `Principio C-004` | Test Permisos |
| `[Constitución]` | Integridad de archivos PDF | `HU-003` | `RF-005` | `RNF-004` | `RN-009` | `EX-004`, `EX-005`| `CA-001` | `Principio C-006` | Carga Binaria |
| `[Plantilla #590]` | Checklist 5 requisitos | `HU-006` | `RF-006` | `RNF-002` | `RN-001` | `EX-007` | `CA-003` | `Principio C-007` | Test Checklist |
| `[Docente]` | Registro de observaciones | `HU-007`, `HU-008`| `RF-007`, `RF-008` | `RNF-003` | `RN-003`, `RN-011` | `EX-007` | `CA-003`, `CA-004`| `Principio C-006` | Test Subsanar |
| `[Plantilla #590]` | Informe de Aptitud Legal | `HU-009` | `RF-009`, `RF-010` | `RNF-008` | `RN-004` | `EX-007` | `CA-005` | `Principio C-002` | Test PDF Gen |
| `[Plantilla #162]` | Declaratoria del Decano/a | `HU-010` | `RF-011` | `RNF-003` | `RN-004` | `EX-002` | `CA-006` | `Principio C-002` | Test Roles |
| `[RRA Art. 236]` | Tribunal de Sustentación | N/A | `RF-014` | `RNF-002` | `RN-007` | `EX-010` | N/A | `Principio C-001` | Test Juristas |
| `[RRA Art. 237]` | Calificación y Acta | N/A | `RF-015` | `RNF-008` | `RN-005`, `RN-006` | N/A | `CA-007` | `Principio C-002` | Test Promedio |
| `[Constitución]` | Reproducibilidad Docker | N/A | N/A | `RNF-010` | N/A | N/A | Despliegue | `Principio C-013` | Test CI/CD |

---

## 16. ASUNTOS PENDIENTES DE CLARIFICACIÓN (`clarify`)

| ID | Cuestión Pendiente de Clarificación | Impacto Técnico / Funcional | Responsable Sugerido | Riesgo Asociado |
| :--- | :--- | :--- | :--- | :--- |
| **AP-01** | **Cómputo de Plazos durante Observaciones:** ¿El plazo reglamentario de 8 días laborables se pausa o se reinicia una vez que el estudiante subsana una observación? | Modifica el algoritmo de cálculo de fechas límites y alertas en la base de datos PostgreSQL. | Secretaría-Abogacía / Docente | Medio |
| **AP-02** | **Generador de Numeración Correlativa:** ¿La numeración de providencias (#590) y memorandos (#162) se autogenera secuencialmente en el sistema o se ingresa manualmente según el sistema de archivo universitario? | Afecta la lógica de los asignadores correlativos en el backend Django DRF. | Secretaría-Abogacía | Bajo |
| **AP-03** | **Responsabilidad Final de Carga Documental:** ¿Se confirma que en el MVP el estudiante o la secretaria pueden cargar directamente los certificados escaneados? | Define la configuración definitiva de permisos en la matriz RBAC para el endpoint de carga. | Docente / Equipo | Medio |
| **AP-04** | **Despacho de Correos SMTP Institucionales:** ¿Se requiere implementar el envío real de correos vía SMTP en el MVP o se limita a notificaciones internas en la plataforma? | Determina si se incorpora la infraestructura de Celery + Redis en el archivo `docker-compose.yml`. | Docente | Bajo |

---

## 17. GLOSARIO DE TÉRMINOS TÉCNICOS Y REGLAMENTARIOS

* **Aptitud Legal:** Certificación administrativa e institucional emitida por el Decano/a previo informe favorable del Secretario/a-Abogado/a que avala que el estudiante ha cumplido los 5 requisitos reglamentarios para defender su trabajo de titulación.
* **Expediente de Titulación:** Contenedor digital unificado que agrupa todas las peticiones, documentos, observaciones e historial de un estudiante durante su proceso de graduación.
* **Petición Documental:** Solicitud atómica y dirigida a una dependencia específica para obtener o validar un certificado determinado dentro del expediente.
* **Checklist Digital:** Herramienta interactiva de control en pantalla que permite al revisor jurista evaluar individualmente cada uno de los requisitos reglamentarios.
* **Observación Accionable:** Comentario formal registrado en el sistema que especifica una deficiencia documental y habilita al estudiante a subsanarla mediante la carga de una nueva versión.
* **Spec-Driven Development (SDD):** Metodología de desarrollo guiado por especificaciones donde el código, las pruebas y la arquitectura se derivan directamente de artefactos documentales formalizados (`constitution`, `specify`, `clarify`, `plan`, `tasks`).
* **RBAC (Role-Based Access Control):** Modelo de seguridad que condiciona el acceso a recursos y acciones según el rol asignado al usuario autenticado.
* **IDOR (Insecure Direct Object Reference):** Vulnerabilidad de seguridad donde un usuario accede a objetos del sistema manipulando identificadores en la URL sin la debida autorización.
* **Magic Bytes:** Los primeros bytes del encabezado de un archivo utilizado para determinar de manera confiable su formato real (ej. `%PDF-` para archivos PDF).
* **Mock / Adapter:** Patrones de diseño orientados a simular servicios externos (como el SGA) desacoplando la lógica del sistema base respecto a dependencias de terceros.

---

## 18. CONDICIONES DE REVISIÓN, APROBACIÓN Y GOBERNANZA

- [x] El documento es 100% coherente con la *Constitución del Proyecto SGT-SIAAF (v2.0.0 Oficial)*.
- [x] Se mantiene explícita la declaración obligatoria de simulación académica funcional con datos ficticios.
- [x] Se respetan las exclusiones de alcance (no escritura en SGA/SIAAF, no firma PKI automática en MVP).
- [x] Los requisitos funcionales (RF-001 a RF-016) y no funcionales (RNF-001 a RNF-018) poseen identificadores únicos y enunciados verificables.
- [x] Se incluye la matriz RBAC de permisos por rol, recurso, acción y endpoint HTTP.
- [x] Las reglas de negocio (RN-001 a RN-012) citan sus fuentes primarias oficiales.
- [x] Las historias de usuario (HU-001 a HU-010) incluyen criterios de aceptación en formato Dado / Cuando / Entonces.
- [x] Se incluye la matriz de trazabilidad integral de requisitos.
- [x] Los asuntos pendientes de clarificación (AP-01 a AP-04) están listados para la etapa `clarify`.

---
