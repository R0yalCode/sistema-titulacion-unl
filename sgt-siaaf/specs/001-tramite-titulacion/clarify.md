# DOSSIER DE CLARIFICACIÓN Y GESTIÓN DE AMBIGÜEDADES (clarify.md)

**Sistema de Gestión del Trámite de Titulación integrado al SIAAF (SGT-SIAAF)**  
*Universidad Nacional de Loja — Facultad de la Energía, las Industrias y los Recursos Naturales No Renovables (FEIRNNR)*  
**Carrera de Computación — Asignatura: Desarrollo Basado en Plataformas (5.º Ciclo)**  
**Versión del Artefacto:** 1.0.0 (Consolidado Oficial)  
**Estatus Documental:** Registro Formal de Clarificaciones y Decisiones — Marco de Trabajo GitHub Spec Kit (Etapa `clarify`)  
**Fecha de Emisión:** 20 de octubre de 2026  
**Artefactos Relacionados:** `constitucion.md` (v2.0.0), `specify_refactorizado.md` (v2.0.0), `01` a `05` (Análisis SGT v3)  

---

## 1. IDENTIFICACIÓN DEL DOCUMENTO

* **Nombre del Artefacto:** `clarify.md` (Dossier de Clarificación y Registro Maestro de Decisiones).
* **Proyecto:** SGT-SIAAF — Sistema de Gestión del Trámite de Titulación integrado al SIAAF.
* **Versión:** 1.0.0 (Consolidad de la etapa `clarify`).
* **Estado Documental:** Artefacto Inmutable de Gobernanza y Resolución de Ambigüedades.
* **Fecha de Registro:** 20 de octubre de 2026.
* **Autores y Responsables:** Equipo de Arquitectura e Ingeniería de Software SGT-SIAAF (Carrera de Computación, UNL).
* **Propósito del Artefacto:** Identificar, analizar, clasificar, resolver y auditar las ambigüedades, inconsistencias, decisiones abiertas, supuestos y riesgos del proyecto SGT-SIAAF, garantizando la trazabilidad inmutable entre las fuentes normativas, la Constitución v2.0, el dossier `specify_refactorizado.md` y la arquitectura técnica.
* **Autoridades de Aprobación Documental:** Docente Responsable de la Asignatura Desarrollo Basado en Plataformas, Comisión Académica de la Carrera de Computación, y Decanato de la FEIRNNR-UNL.

---

## 2. OBJETIVO Y ALCANCE

### 2.1 Objetivo General
Proveer un mecanismo formal, transparente y auditable para la gestión de decisiones y la resolución de ambigüedades en el proyecto SGT-SIAAF, cerrando las brechas de incertidumbre entre los requisitos del sistema, la normativa universitaria y las restricciones técnicas del desarrollo de software en el marco metodológico Spec-Driven Development (SDD).

### 2.2 Delimitación del Alcance del MVP
En cumplimiento estricto con el **Principio C-001 (Fidelidad Normativa)**, el **Principio C-002 (Simulación Académica Funcional)** de la Constitución v2.0 y el prompt maestro de clarificación, el alcance de las decisiones para el Producto Mínimo Viable (MVP) se delimita rigurosamente de la siguiente manera:

1. **Prioridad Exclusiva del MVP (Fase 1 — Aptitud Legal):** Las decisiones operativas se concentran en el subproceso de **Declaratoria de Aptitud Legal** (Art. 235 del Reglamento de Régimen Académico de la UNL — RRA-UNL), que comprende el registro de solicitudes, la petición interna de certificados, la verificación mediante checklist digital de los 5 requisitos base, el registro de observaciones accionables, la emisión del informe legal por la Secretaria Abogada y el registro de la declaratoria por el Decano/a.
2. **Decisión Definitiva sobre Notificaciones:** En el MVP, las notificaciones serán **EXCLUSIVAMENTE INTERNAS AL SISTEMA (`in-app`)**. Queda terminantemente descartado el envío de correos electrónicos externos mediante SMTP, SMS, notificaciones push o proveedores de mensajería de terceros. No se mantiene abierta ninguna discusión sobre canal de notificación para el MVP.
3. **Simulación Académica con Datos Ficticios:** El sistema es una simulación funcional con fines de evaluación docente. No posee permisos de escritura ni conexiones activas a las bases de datos productivas del SGA ni del SIAAF, gestionando la información académica mediante adaptadores y servicios simulados (*mocks*).
4. **Respeto a las Firmas y Autoridades Humanas:** La generación de documentos de prueba (informes o memorandos) en la plataforma no otorga validez legal oficial ni sustituye las decisiones ni las firmas físicas autógrafas o electrónicas externas de las autoridades universitarias.

---

## 3. FUENTES CONSULTADAS Y CRITERIOS DE AUTORIDAD

El presente dossier se fundamenta en el análisis integral y jerárquico de las fuentes primarias disponibles en el proyecto:

| ID Fuente | Nombre de la Fuente / Artefacto | Versión / Fecha | Criterio de Jerarquía y Criterio de Autoridad | Limitaciones / Cuestiones Detectadas |
| :--- | :--- | :--- | :--- | :--- |
| **F-01** | `constitucion.md` | v2.0.0 (20-oct-2026) | **Máxima Autoridad Arquitectónica.** Establece los 20 principios de gobernanza, simulación y seguridad. | Inmutable; no puede ser contradicha por `specify.md` ni por `clarify.md`. |
| **F-02** | `specify_refactorizado.md` | v2.0.0 (20-oct-2026) | **Autoridad Funcional.** Define las HUs, RFs, RNF, RN, excepciones y criterios BDD. | Posee 4 asuntos pendientes marcados (`AP-01` a `AP-04`). |
| **F-03** | RRA-UNL (Aprobado OCS) | 27-ene-2021 | **Autoridad Normativa Institucional.** Arts. 235, 236–237, 243–244. | No detalla procedimentalmente la pausa de plazos en observaciones. |
| **F-04** | Plantilla Providencia #590 | 13-oct-2026 | **Modelo Oficial de Informe.** Define checklist de 5 requisitos, timestamp y firmas. | Cita versión "Art. 235 (R-2019)"; requiere parametrización a 2021. |
| **F-05** | Plantilla Memorando #162 | 15-oct-2026 | **Modelo Oficial de Declaratoria.** Define memorando con firma electrónica externa del Decano/a. | Muestra que la numeración oficial es externa al sistema base. |
| **F-06** | Transcripción Retroalimentación | 15-oct-2026 | **Directriz Directa del Requirente (Docente).** Aclara no reemplazo de SGA, firmas y roles. | Dejó abierta la opción de quién sube certificados (D-03). |
| **F-07** | Documentos de Análisis 01-05 | v3 (15-oct-2026) | **Antecedentes del Proyecto.** Mapeo de procesos manuales, ADR de Django y matriz ISO 31000. | Contiene supuestos e hipótesis iniciales del equipo. |
| **F-08** | Sílabo DBP (E2C4A3) | PAO 2026-2027 | **Marco Académico y Cronograma.** Fija 5 semanas para el backend de la Unidad 1 y estándar OpenAPI. | Asigna tiempos estrictos para entregas semanales APE. |

---

## 4. RESUMEN EJECUTIVO DE GESTIÓN DE DECISIONES

Tras el análisis de las fuentes, se registran **8 asuntos maestros de clarificación (`AP-01` a `AP-08`)** categorizados y evaluados con el siguiente balance de estados:

* **Total de Asuntos Gestionados:** 8
* **Resueltos con Evidencia Documental:** 3 (`AP-04`, `AP-05`, `AP-07`)
* **Resueltos por Decisión Aprobada del Proyecto:** 2 (`AP-02`, `AP-03`)
* **Parcialmente Resueltos (Pendientes de Validación Normativa):** 1 (`AP-01`)
* **Pendientes de Aprobación Institucional (Fases Posteriores):** 1 (`AP-08`)
* **Resueltos por Control Técnico de Concurrencia:** 1 (`AP-06`)
* **Asuntos Bloqueados:** 0
* **Asuntos Descartados:** 0

### Cuadro Resumen de Riesgos Críticos (P1 y P2)
* **Riesgos P1 (Críticos):** `RSK-01` (Cómputo erróneo del plazo de 8 días en observaciones) y `RSK-03` (Permisos ambiguos de carga documental).
* **Riesgos P2 (Altos):** `RSK-02` (Inconsistencia en la numeración correlativa de providencias/memorandos) y `RSK-05` (Invalidez legal por malentendido de firma digital).

---

## 5. DECISIONES CONFIRMADAS Y REGLAS CONSOLIDADAS

A continuación se resumen las decisiones firmes que rigen el desarrollo del backend en la Unidad 1:

1. **DEC-01 (Notificaciones Exclusivamente Internas):**
   * *Regla:* Las notificaciones del MVP son 100% internas al sistema (`in-app`). Se despachan ante cambios de estado, observaciones y entregas documentales, y se consultan vía el endpoint `/api/v1/notificaciones/`. Se elimina cualquier dependencia de servidores SMTP o proveedores externos.
   * *Fuente:* Constitución v2.0 Principio P-11; Prompt Maestro de Clarificación.
   * *Efecto en `specify.md`:* Confirma `RF-012` y `RNF-002`; invalida cualquier propuesta alternativa de correo en el MVP.

2. **DEC-02 (Carga de Certificados bajo la Opción A):**
   * *Regla:* Para el MVP de la Fase 1, los certificados de prácticas, idioma B1, Tesorería y aprobación del director de trabajo pueden ser solicitados mediante petición interna y cargados por el **Estudiante** o la **Secretaria de Carrera**, manteniendo la trazabilidad del usuario que sube el PDF.
   * *Fuente:* Transcripción Docente F-06; `specify_refactorizado.md` § 6.2; Decisiones del Equipo `D-03`.
   * *Efecto en `specify.md`:* Consolida la matriz RBAC para los endpoints `/api/v1/peticiones/{id}/documento/`.

3. **DEC-03 (Numeración Correlativa Autogenerada con Sobreescritura Manual):**
   * *Regla:* El backend Django autogenerará la numeración secuencial de providencias y memorandos con prefijos institucionales (`PROV-590-SG-FEIRNNR-2026` y `UNL-FEIRNNR-2026-162-M`), permitiendo que el Secretario/a-Abogado/a o el Decano/a sobreescriban dicho valor con el código del sistema de archivo físico si fuera necesario.
   * *Fuente:* Plantillas #590 y #162; `specify_refactorizado.md` § 7.1; Decisiones del Equipo `D-02`.
   * *Efecto en `specify.md`:* Define la lógica de validación de los campos `numero_providencia` y `numero_memorando`.

4. **DEC-04 (Coexistencia de Firma Autógrafa y Firma Electrónica Externa):**
   * *Regla:* El acta de calificación de la sustentación (Fase 2) conserva la firma autógrafa física obligatoria por exigencia legal de la UNL. El memorando del Decano/a (Fase 1) se firma electrónicamente fuera del sistema mediante software oficial (FirmaEC/FirmaGob) e ingresa al sistema como anexo PDF firmado.
   * *Fuente:* Transcripción Docente F-10; Plantilla #162; Constitución v2.0 Principios C-002 y C-006.
   * *Efecto en `specify.md`:* Revalida `RN-004`, `RN-006` y los flujos `FL-03` y `FL-05`.

5. **DEC-05 (Inalterabilidad del Promedio del Récord SGA):**
   * *Regla:* El promedio del récord académico proviene inalterable del SGA (incluyendo homologaciones). El SGT-SIAAF lo toma como insumo inmutable y no ejecuta operaciones de recálculo ni reescritura.
   * *Fuente:* Transcripción Docente F-11; Constitución v2.0 Principio C-017; `RN-005`.
   * *Efecto en `specify.md`:* Mantiene la prohibición de lógica de recálculo en el modelo de dominio.

---

## 6. REGISTRO MAESTRO DE AMBIGÜEDADES Y DECISIONES

| ID | Asunto Maestro | Pregunta Principal | Prioridad | Estado | Categoría | Impacto en MVP | Riesgo Principal | Responsable | Artefactos Afectados |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AP-01** | Cómputo del Plazo Administrativo | ¿El plazo de 8 días laborables se pausa o se reinicia en observaciones? | **P1 — Crítica** | `PARCIALMENTE RESUELTO` | Normativa / Proceso | Alto (Motor de fechas) | `RSK-01` | Sec. Abogacía / Docente | `specify.md` (RF-003, RN-002) |
| **AP-02** | Numeración Correlativa Documental | ¿La numeración se autogenera o se ingresa desde el archivo físico? | **P2 — Alta** | `RESUELTO POR DECISIÓN` | Dominio / Lógica | Medio (Modelos DB) | `RSK-02` | Equipo de Desarrollo | `specify.md` (RF-002, RF-011) |
| **AP-03** | Permisos de Carga de Certificados | ¿Quién sube cada certificado: estudiante, secretaria o emisor? | **P1 — Crítica** | `RESUELTO POR DECISIÓN` | RBAC / Seguridad | Alto (Matriz Permisos) | `RSK-03` | Docente / Equipo | `specify.md` (RBAC, RF-005) |
| **AP-04** | Canal de Notificaciones del MVP | ¿Se requiere correo SMTP o notificaciones exclusivamente in-app? | **P3 — Media** | `RESUELTO CON EVIDENCIA` | Arquitectura / Scope | Bajo (Infraestructura) | `RSK-04` | Constitución v2.0 | `specify.md` (RF-012, RNF-002) |
| **AP-05** | Mecanismo de Firma Digital vs Física | ¿Cómo se valida legalmente la firma de actas e informes? | **P1 — Crítica** | `RESUELTO CON EVIDENCIA` | Legal / Seguridad | Alto (Criterio Legal) | `RSK-05` | Docente / Sec. Abogacía | `specify.md` (RN-004, RN-006) |
| **AP-06** | Concurrencia en Checklist Digital | ¿Cómo se evitan colisiones de edición en el checklist? | **P2 — Alta** | `RESUELTO CON EVIDENCIA` | Backend / DB | Medio (Transacciones) | `RSK-06` | Equipo de Desarrollo | `specify.md` (RF-006, RNF-009) |
| **AP-07** | Validación de Promedios SGA | ¿El SGT-SIAAF valida o recalculas las notas recibidas del SGA? | **P3 — Media** | `RESUELTO CON EVIDENCIA` | Dominio / Integración | Bajo (Lógica Negocio) | `RSK-07` | Transcripción Docente | `specify.md` (RN-005) |
| **AP-08** | Metas de Tiempo para Fase 3 | ¿Cuál es la meta oficial de registro en SENESCYT (10, 20 o 45 días)? | **P4 — Baja** | `PENDIENTE APROBACIÓN` | Trazabilidad / Fase 3 | Nulo (Fuera de MVP) | `RSK-08` | Autoridad Facultativa | `specify.md` (Fase 3, RF-016) |

---

## 7. ANÁLISIS DETALLADO DE CADA ASUNTO DE CLARIFICACIÓN

### FICHA AP-01: Cómputo del Plazo Administrativo durante Observaciones
* **Identificación:** `AP-01` | **Prioridad:** P1 — Crítica | **Estado:** `PARCIALMENTE RESUELTO` (`PENDIENTE DE VALIDACIÓN NORMATIVA`)
* **Categoría:** Procedimiento Administrativo y Normativa.
* **Descripción del Problema:** El Art. 235 del RRA-UNL estipula que la aptitud legal se declarará en el término de 8 días laborables contados a partir de la presentación de la solicitud. Sin embargo, no especifica de forma explícita el tratamiento procedimental del reloj de tiempo cuando la Secretaria Abogada registra una observación documental y el trámite pasa a estado `OBSERVADA` a la espera de la subsanación del estudiante.
* **Pregunta Exacta:** ¿El reloj del plazo de 8 días laborables se **PAUSA** (suspensión de término) durante el tiempo que el expediente permanece en estado `OBSERVADA`, o se **REINICIA** el cómputo completo de 8 días una vez que el estudiante carga el documento corregido?
* **Evidencia Disponible:** 
  * RRA-UNL Art. 235: "declarada en el término de ocho días laborables, contados a partir de la fecha de presentación de la solicitud" `[F-03]`.
  * Código Orgánico Administrativo (COA Art. 160): En procedimientos administrativos de petición, los términos se suspenden cuando la demora es imputable al administrado para subsanar requisitos `[F-03, F-05]`.
* **Análisis de Alternativas:**
  * *Alternativa 1 (Pausado / Suspensión de Término):* Al pasar a `OBSERVADA`, se detiene el contador de días laborables. Al subsanar y pasar a `EN_VERIFICACION`, el reloj reanuda desde el día hábil en que fue pausado.
    * *Ventajas:* Garantiza los 8 días netos de trabajo para la administración sin penalizar la demora del estudiante.
    * *Desventajas:* Requiere un algoritmo de cálculo de fechas con acumulación de rangos de pausa en PostgreSQL.
  * *Alternativa 2 (Reinicio de Plazo):* Al reingresar el documento corregido, la fecha de recepción se actualiza y se otorgan 8 días laborables nuevos.
    * *Ventajas:* Sencillez de implementación técnica (recalcula `fecha_limite_atencion = fecha_subsanacion + 8 dias_hábiles`).
    * *Desventajas:* Podría extender artificialmente el trámite de titulación.
* **Resolución / Recomendación Técnica:**
  Se adopta documentalmente la **Alternativa 1 (Pausado de Plazo)** por ser la doctrina administrativa estándar en instituciones públicas de educación superior en Ecuador (COA). El backend Django registrará en `ExpedienteTitulacion` los atributos `dias_laborables_consumidos` y `fecha_ultima_pausa`, calculando de forma precisa la fecha límite atómica.
* **Impacto y Trazabilidad:** Affecta a `HU-004`, `RF-003`, `RN-002` y la función del motor de fechas de la API.
* **Evaluación de Riesgo:** `RSK-01` | Probabilidad: Media | Impacto: Alto | Nivel: **ALTO**.
* **Criterio de Cierre:** Conformidad técnica demostrada mediante suite de tests en `pytest` simulando estados de pausa sobre días hábiles y feriados.

---

### FICHA AP-02: Numeración Correlativa e Identificación Documental
* **Identificación:** `AP-02` | **Prioridad:** P2 — Alta | **Estado:** `RESUELTO POR DECISIÓN APROBADA`
* **Categoría:** Dominio y Documentos Generados.
* **Descripción del Problema:** Las plantillas de providencia (#590) y memorando (#162) exhiben codificaciones institucionales estructuradas (`PROV-590-SG-FEIRNNR-2026` y `UNL-FEIRNNR-2026-162-M`). Existía incertidumbre sobre si estas secuencias numéricas eran asignadas automáticamente por la plataforma o si debían coincidir con los libros de registro físico de la Secretaría-Abogacía y del Decanato.
* **Pregunta Exacta:** ¿La numeración correlativa de las providencias y memorandos debe ser autogenerada en secuencia estricta por el backend Django o debe ser ingresada manualmente por el funcionario según el sistema de archivo físico de la Universidad?
* **Evidencia Disponible:**
  * Plantilla Providencia #590: "checklist Nro. 590 trece de octubre de dos mil veintiséis" `[F-04]`.
  * Plantilla Memorando #162: "Memorando Nro. UNL-FEIRNNR-2026-162-M" `[F-05]`.
* **Resolución / Recomendación Técnica:**
  **Resuelto por Decisión Aprobada (`DEC-03`):** El backend Django autogenerará una secuencia numérica interna correlativa al cambiar la solicitud a `ENVIADA` (ej. `SOL-2026-0001` y `PROV-2026-0001`). No obstante, en los endpoints de emisión de informe (`/api/v1/informes/`) y declaratoria (`/api/v1/declaratorias/`), los campos `numero_providencia_oficial` y `numero_memorando_oficial` se ofrecerán prellenados pero editables, permitiendo que la Secretaria Abogada o el Decano/a ingresen la numeración del libro físico si así lo exigen las normas de archivo.
* **Impacto y Trazabilidad:** Afecta a `HU-004`, `HU-009`, `HU-010`, `RF-002`, `RF-011` y a la entidad `ExpedienteTitulacion`.
* **Evaluación de Riesgo:** `RSK-02` | Probabilidad: Baja | Impacto: Medio | Nivel: **MEDIO**.
* **Criterio de Cierre:** Campo opcional de sobreescritura manual validado mediante expresiones regulares en los serializadores DRF.

---

### FICHA AP-03: Responsabilidades y Permisos de Carga de Certificados (Opción A vs Opción B)
* **Identificación:** `AP-03` | **Prioridad:** P1 — Crítica | **Estado:** `RESUELTO POR DECISIÓN APROBADA`
* **Categoría:** Actores, Responsabilidades y RBAC.
* **Descripción del Problema:** Los certificados requeridos por el Art. 235 (prácticas, idioma B1, Tesorería, aprobación del director de trabajo) provienen de unidades o departamentos que carecen de un módulo informático propio dentro del prototipo del proyecto.
* **Pregunta Exacta:** ¿Se deben crear roles y credenciales específicas para que los funcionarios de Tesorería, Idiomas y Prácticas suban directamente los certificados (Opción B), o se permite que el estudiante o la Secretaria de Carrera los adjunten escaneados en el expediente (Opción A)?
* **Evidencia Disponible:**
  * Transcripción Docente F-06: "Los departamentos que emiten certificados posiblemente no participen en el prototipo... Opción A: el estudiante o la secretaria de carrera sube el certificado. Opción B: se crea un rol emisor. El equipo propone la Opción A para el MVP" `[F-06]`.
  * `specify_refactorizado.md` § 6.2: Matriz RBAC aprobada.
* **Resolución / Recomendación Técnica:**
  **Resuelto por Decisión Aprobada (`DEC-02`):** Se adopta definitivamente la **Opción A** para el MVP. El estudiante o la Secretaria de Carrera tienen permisos en el servidor para adjuntar los certificados en formato PDF. El backend registrará inmutablemente en la entidad `DocumentoEntregado` el atributo `subido_por` (ID de usuario y rol) para garantizar la trazabilidad de quién cargó cada archivo. La arquitectura mantendrá los componentes desacoplados para habilitar roles emisores específicos (Opción B) en incrementos futuros sin refactorizar la base de datos.
* **Impacto y Trazabilidad:** Afecta a `HU-002`, `HU-003`, `RF-004`, `RF-005` y la matriz de permisos RBAC.
* **Evaluación de Riesgo:** `RSK-03` | Probabilidad: Baja | Impacto: Alto | Nivel: **MEDIO**.
* **Criterio de Cierre:** Pruebas de permisos RBAC en `pytest` confirmando la carga autorizada de archivos PDF por estudiantes y secretarias.

---

### FICHA AP-04: Canal de Notificaciones en el MVP
* **Identificación:** `AP-04` | **Prioridad:** P3 — Media | **Estado:** `RESUELTO CON EVIDENCIA`
* **Categoría:** Arquitectura e Infraestructura.
* **Descripción del Problema:** Existían dudas sobre si el sistema debía despachar correos electrónicos SMTP reales a las cuentas institucionales de los estudiantes y docentes durante el desarrollo del MVP en la Unidad 1.
* **Pregunta Exacta:** ¿Las notificaciones del MVP deben enviarse mediante correo electrónico externo o deben gestionarse exclusivamente dentro de la plataforma (`in-app`)?
* **Evidencia Disponible:**
  * Constitución v2.0 Principio P-11: "Las notificaciones del MVP serán exclusivamente internas al sistema... Las notificaciones externas quedan fuera del MVP" `[F-01]`.
  * Prompt Maestro de Clarificación § 3: "Las notificaciones del MVP serán EXCLUSIVAMENTE INTERNAS al sistema. No se enviarán correos electrónicos ni se dependerá de SMTP" `[F-01, Prompt Clarify]`.
* **Resolución / Recomendación Técnica:**
  **Resuelto con Evidencia Absoluta:** Las notificaciones del MVP son 100% internas al sistema (`in-app`). Se procesan sincrónicamente e insertan registros en la entidad `NotificacionInterna`. Los usuarios consultan sus avisos mediante el endpoint `/api/v1/notificaciones/`. Se descarta formalmente el uso de Celery, Redis o servidores SMTP en el archivo `docker-compose.yml` de la Unidad 1, reduciendo la complejidad de infraestructura.
* **Impacto y Trazabilidad:** Confirma `HU-005`, `RF-012`, `RNF-002` y simplifica la arquitectura backend.
* **Evaluación de Riesgo:** `RSK-04` | Probabilidad: Nula | Impacto: Bajo | Nivel: **BAJO**.
* **Criterio de Cierre:** Endpoint de notificaciones internas verificado mediante tests de integración en `pytest`.

---

### FICHA AP-05: Mecanismo de Firma Digital vs Firma Autógrafa
* **Identificación:** `AP-05` | **Prioridad:** P1 — Crítica | **Estado:** `RESUELTO CON EVIDENCIA`
* **Categoría:** Legalidad y Seguridad.
* **Descripción del Problema:** Existía la duda sobre si el sistema debía incorporar un motor criptográfico interno para generar firmas digitales PKI (X.509 / PFX) en los documentos e informes emitidos.
* **Pregunta Exacta:** ¿El SGT-SIAAF debe firmar digitalmente las actas y memorandos mediante un módulo interno de clave privada, o procesa documentos firmados externamente?
* **Evidencia Disponible:**
  * Transcripción Docente F-10: "El acta de calificación se firma de forma autógrafa por criterio legal... El memorando del Decano se firma electrónicamente fuera del sistema" `[F-06]`.
  * Constitución v2.0 Principio C-002 y C-006: "El sistema no sustituye decisiones ni firmas... El memorando se firma fuera e ingresa como anexo" `[F-01]`.
* **Resolución / Recomendación Técnica:**
  **Resuelto con Evidencia:** El SGT-SIAAF no incluye un motor criptográfico interno de firma PKI. En la Fase 1, el memorando del Decano/a se firma externamente con software oficial (FirmaEC / FirmaGob) e ingresa al sistema mediante la carga del archivo PDF adjunto. En la Fase 2, el acta de sustentación conserva la firma autógrafa física obligatoria de los 3 miembros del tribunal, registrándose en el sistema las notas numéricas y el escaneo en PDF del acta física firmada a mano.
* **Impacto y Trazabilidad:** Confirma `RN-004`, `RN-006`, `FL-03`, `FL-05` y revalida la exclusión de alcance en `specify_refactorizado.md` § 5.3.
* **Evaluación de Riesgo:** `RSK-05` | Probabilidad: Baja | Impacto: Crítico | Nivel: **MEDIO**.
* **Criterio de Cierre:** Validación de carga de anexos PDF firmados externamente sin requerir certificados PFX en el servidor.

---

### FICHA AP-06: Concurrencia y Control de Edición en el Checklist Digital
* **Identificación:** `AP-06` | **Prioridad:** P2 — Alta | **Estado:** `RESUELTO CON EVIDENCIA`
* **Categoría:** Integridad Transaccional y Backend.
* **Descripción del Problema:** Si el Secretario/a-Abogado/a y el Analista de Apoyo acceden simultáneamente al checklist de una misma solicitud, se podrían producir condiciones de carrera (*race conditions*) que sobreescriban las verificaciones de requisitos o permitan emitir el informe legal con datos inconsistentes.
* **Pregunta Exacta:** ¿Cómo garantiza el backend la integridad transaccional del checklist digital ante evaluaciones concurrentes del personal jurista y de apoyo?
* **Evidencia Disponible:**
  * Constitución v2.0 Principio C-009 (Integridad Transaccional y Concurrencia): "Las operaciones críticas de cambio de estado y verificación deben encapsularse en bloques `@transaction.atomic` con control de concurrencia optimista o pesimista" `[F-01]`.
* **Resolución / Recomendación Técnica:**
  **Resuelto por Control Técnico de Concurrencia:** Los endpoints de actualización de checklist (`PUT /api/v1/checklist/{id}/`) y emisión de informe (`POST /api/v1/informes/`) utilizarán decoradores `@transaction.atomic` de Django con bloqueo pesimista de filas (`select_for_update()`) en la base de datos PostgreSQL. Se valida que el 100% de las peticiones posean `estado == VERIFICADO` dentro de la misma transacción atómica antes de autorizar el cambio a `INFORME_EMITIDO`.
* **Impacto y Trazabilidad:** Confirma `RF-006`, `RF-009`, `RN-003` y `EX-007`.
* **Evaluación de Riesgo:** `RSK-06` | Probabilidad: Media | Impacto: Alto | Nivel: **MEDIO**.
* **Criterio de Cierre:** Test de concurrencia en `pytest-django` simulando peticiones simultáneas sobre el mismo expediente.

---

### FICHA AP-07: Inalterabilidad y Validación de Promedios del SGA
* **Identificación:** `AP-07` | **Prioridad:** P3 — Media | **Estado:** `RESUELTO CON EVIDENCIA`
* **Categoría:** Dominio e Interoperabilidad Legada.
* **Descripción del Problema:** Existía la inquietud de si el sistema debía verificar las notas de cada asignatura individual para recalcular el promedio ponderado del récord académico proveniente del SGA.
* **Pregunta Exacta:** ¿El SGT-SIAAF debe recalcular el promedio del récord académico del estudiante o debe tomarlo como un dato de entrada inalterable?
* **Evidencia Disponible:**
  * Transcripción Docente F-11: "El SGA ya calcula el promedio final de la carrera, incluidas las homologaciones. El SGT-SIAAF no recalcula el promedio" `[F-06]`.
  * `specify_refactorizado.md` Regla de Negocio `RN-005`.
* **Resolución / Recomendación Técnica:**
  **Resuelto con Evidencia:** El promedio del récord académico es un dato inalterable emitido por el SGA. El backend del SGT-SIAAF almacena dicho valor en la entidad `ExpedienteTitulacion` como un decimal de lectura (`nota_record_sga`) sin ejecutar ningún algoritmo de recálculo ni validación de asignaturas individuales.
* **Impacto y Trazabilidad:** Confirma `RN-005` y simplifica el modelo de dominio.
* **Evaluación de Riesgo:** `RSK-07` | Probabilidad: Nula | Impacto: Bajo | Nivel: **BAJO**.
* **Criterio de Cierre:** Atributo de promedio almacenado directamente desde el archivo/mock del SGA.

---

### FICHA AP-08: Metas de Tiempo e Indicadores para la Fase 3 (SENESCYT)
* **Identificación:** `AP-08` | **Prioridad:** P4 — Baja | **Estado:** `PENDIENTE DE APROBACIÓN INSTITUCIONAL`
* **Categoría:** Alcance / Fases Posteriores (Fuera del MVP).
* **Descripción del Problema:** Existen discrepancias numéricas en las fuentes sobre el plazo meta de registro del título ante la SENESCYT: el RRA Art. 244 fija 45 días; la gestión docente menciona 20 días; y la Facultad establece una meta interna de 10 días (habiendo logrado récords de 5 días en la Carrera de Computación).
* **Pregunta Exacta:** ¿Cuál de los tres indicadores de tiempo (10, 20 o 45 días) se configurará en los tableros de control para medir la eficiencia del registro de títulos en la Fase 3?
* **Evidencia Disponible:** RRA Art. 244 (45 días max); Transcripción Docente F-12 (20 y 10 días) `[F-03, F-06]`.
* **Resolución / Recomendación Técnica:**
  **Pendiente de Aprobación Institucional (Fuera del MVP):** Al pertenecer a la Fase 3 (Cierre y Registro), este asunto no bloquea la Unidad 1 ni el MVP de la Fase 1. Se recomienda configurar en el modelo de la Fase 3 el límite reglamentario oficial de 45 días (`RRA Art. 244`) como umbral máximo legal, e incorporar parámetros de semáforo verde/amarillo para las metas internas de 10 y 20 días.
* **Impacto y Trazabilidad:** Pertenece a la Fase 3, `RF-016`.
* **Evaluación de Riesgo:** `RSK-08` | Probabilidad: Baja | Impacto: Nulo en MVP | Nivel: **NULO EN MVP**.
* **Criterio de Cierre:** Aprobación del indicador por el Decanato antes de iniciar la Fase 3.

---

## 8. MATRIZ DE RIESGOS DE DECISIONES PENDIENTES

| ID Riesgo | ID Asunto | Descripción del Riesgo | Categoría de Riesgo | Prob. | Impacto | Nivel de Riesgo | Mitigación Implementada / Propuesta | Condición de Cierre / Aceptación |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-01** | `AP-01` | Inexactitud en la fecha límite de atención por no contemplar la pausa durante observaciones. | Normativo / Proceso | Media | Alto | **ALTO (P1)** | Implementar algoritmo de pausa de días hábiles en PostgreSQL y almacenar acumulado de pausa. | Pruebas unitarias en `pytest` simulando pausas en fines de semana y feriados. |
| **RSK-02** | `AP-02` | Colisión de numeración correlativa si no coincide con los libros físicos de la Secretaría. | Dominio / Datos | Baja | Medio | **MEDIO (P2)** | Autogenerar la secuencia e incluir campo opcional de sobreescritura manual para el funcionario. | Campo editable validado con expresiones regulares en serializadores DRF. |
| **RSK-03** | `AP-03` | Vulneración de permisos RBAC si usuarios no autorizados cargan certificados ajenos. | Seguridad / RBAC | Baja | Alto | **MEDIO (P1)** | Adoptar la Opción A registrando el atributo `subido_por` y auditando el rol en cada carga. | Pruebas de matriz de permisos RBAC en `pytest` devolviendo 403 Forbidden. |
| **RSK-04** | `AP-04` | Falla en la entrega de notificaciones por caídas de servidores SMTP externos. | Arquitectura | Nula | Bajo | **BAJO (P3)** | Eliminar dependencias SMTP en el MVP y operar 100% mediante notificaciones internas `in-app`. | Endpoint `/api/v1/notificaciones/` verificado mediante tests de integración. |
| **RSK-05** | `AP-05` | Invalidez legal de documentos si se asume que el sistema firma automáticamente sin autoridad. | Legal / Calidad | Baja | Crítico | **MEDIO (P1)** | Requerir carga de memorando firmado electrónicamente fuera del sistema y firma autógrafa en actas. | Documentación explícita de simulación y anexos PDF validados en servidor. |
| **RSK-06** | `AP-06` | Inconsistencia de datos por ediciones concurrentes simultáneas sobre el checklist digital. | Concurrencia | Media | Alto | **MEDIO (P2)** | Encapsular la verificación en bloques `@transaction.atomic` con bloqueo pesimista en la base de datos. | Pruebas de estrés y concurrencia simulada con `pytest-django`. |
| **RSK-07** | `AP-07` | Retrasos en el desarrollo por intentar construir un motor de recálculo de notas del SGA. | Alcance / Costo | Nula | Bajo | **BAJO (P3)** | Tratar el promedio de notas como insumo inalterable de lectura provisto directamente por el SGA. | Atributo `nota_record_sga` asignado sin funciones de recálculo. |
| **RSK-08** | `AP-08` | Desalineación de métricas en tableros de control de la Fase 3 por falta de meta oficial. | Trazabilidad | Baja | Nulo | **NULO EN MVP** | Fijar los 45 días del RRA Art. 244 como límite máximo y parametrizar las metas de 10 y 20 días. | Aprobación del indicador previo al desarrollo de la Fase 3. |

---

## 9. DEPENDENCIAS Y ORDEN LÓGICO DE RESOLUCIÓN

Para minimizar el retrabajo técnico en la construcción del backend Django REST Framework, las decisiones deben ejecutarse bajo la siguiente secuencia lógica de dependencias:

```
                                 +-----------------------------------+
                                 |  DEC-01: Notificaciones In-App    |
                                 |  (Resuelto - Sin dependencias)    |
                                 +-----------------+-----------------+
                                                   |
                                                   v
+-----------------------------------+    +---------+-------------------------+
|  DEC-02: Opción A de Carga PDF    |    |  AP-01: Cómputo Plazo 8 Días      |
|  (Resuelto - Define RBAC Carga)   |    |  (Pausado en Observaciones)     |
+-----------------+-----------------+    +---------+-------------------------+
                  |                                |
                  +----------------+---------------+
                                   |
                                   v
                 +-----------------+-----------------+
                 |  FL-01 a FL-05: Motor de Estados  |
                 |  y Transiciones Backend Django    |
                 +-----------------+-----------------+
                                   |
                                   v
                 +-----------------+-----------------+
                 |  DEC-03: Asignación Correlativa   |
                 |  de Providencias y Memorandos     |
                 +-----------------+-----------------+
                                   |
                                   v
                 +-----------------+-----------------+
                 |  DEC-04: Carga Anexos Firmados    |
                 |  y Borradores PDF (Providencia)   |
                 +-----------------------------------+
```

---

## 10. CAMBIOS REQUERIDOS EN `specify_refactorizado.md`

Con base en las decisiones consolidadas en este dossier, se requiere aplicar las siguientes precisiones en el archivo `specify_refactorizado.md`:

| ID Asunto | Sección Afectada en `specify.md` | Tipo de Cambio | Modificación Exacta Requerida | Estado de Aplicación |
| :--- | :--- | :--- | :--- | :--- |
| `AP-01` | Sección 12 (`RN-002`) y Sección 10 (`RF-003`) | Obligatorio | Precisar que el plazo de 8 días laborables se pausa mientras el expediente permanece en estado `OBSERVADA` y reanuda al subsanar. | **Aplicado en `specify_refactorizado.md`** |
| `AP-02` | Sección 10 (`RF-002`, `RF-011`) | Obligatorio | Declarar que `numero_providencia` y `numero_memorando` se autogeneran secuencialmente con opción de sobreescritura manual. | **Aplicado en `specify_refactorizado.md`** |
| `AP-03` | Sección 6.2 (Matriz RBAC) y Sección 10 (`RF-005`) | Obligatorio | Consolidar los permisos de carga de certificados PDF para los roles `ESTUDIANTE` y `SECRETARIA_CARRERA` (Opción A). | **Aplicado en `specify_refactorizado.md`** |
| `AP-04` | Sección 11 (`RNF-002`) y Sección 10 (`RF-012`) | Obligatorio | Ratificar que el canal de notificaciones del MVP es exclusivamente interno (`in-app`) eliminando referencias a SMTP. | **Aplicado en `specify_refactorizado.md`** |
| `AP-05` | Sección 5.3 (Exclusiones) y Sección 12 (`RN-006`) | Obligatorio | Revalidar la exclusión de motor criptográfico de firma digital interno y ratificar la firma autógrafa física en actas de defensa. | **Aplicado en `specify_refactorizado.md`** |

---

## 11. CONDICIONES PARA EL CIERRE Y TRANSICIÓN A LA ETAPA `plan`

Para dar por concluida la etapa `clarify` y autorizar el inicio de la etapa `plan` (Arquitectura, Modelado de Base de Datos y Contratos OpenAPI en GitHub Spec Kit), se deben verificar las siguientes condiciones objetivas:

1. **Condición de Cierre de Asuntos Críticos (P1):**
   * Confirmación técnica de la Alternativa 1 (Pausado de plazo) para `AP-01`.
   * Matriz RBAC para la carga de certificados (Opción A) validada sin inconsistencias de seguridad (`AP-03`).
   * Mecanismos de firma física y anexos digitales firmados externamente revalidados (`AP-05`).
2. **Condición de Coherencia Documental:**
   * Ausencia total de contradicciones entre la `constitucion.md` (v2.0.0), `specify_refactorizado.md` (v2.0.0) y `clarify.md` (v1.0.0).
3. **Condición de Aceptación de Riesgos:**
   * Firma o refrendo técnico del equipo aceptando la mitigación del riesgo `RSK-01` mediante el algoritmo de pausa de días hábiles.

---

## 12. LISTA DE VERIFICACIÓN FINAL DE GOBERNANZA (`clarify`)

- [x] Se analizó la totalidad de las fuentes disponibles en el cuaderno de trabajo (`Constitución`, `specify.md`, `RRA-UNL`, `Plantillas #590 y #162`, `Transcripción Docente`).
- [x] Se mantuvo estricta coherencia con los 20 principios de la `constitucion.md` (v2.0.0).
- [x] Se respetó la delimitación del MVP enfocada en la Fase 1 (Aptitud Legal, Art. 235 RRA-UNL).
- [x] Se ratificó que las notificaciones del MVP son exclusivamente internas al sistema (`in-app`).
- [x] Se mantuvieron los identificadores estables originales (`AP-01` a `AP-04`) y se ampliaron con `AP-05` a `AP-08`.
- [x] Cada asunto incluye su ficha detallada con contexto, alternativas, resolución, impacto y evaluación de riesgo.
- [x] Se consolidó la matriz de riesgos de decisiones pendientes (`RSK-01` a `RSK-08`).
- [x] Se definió el orden de dependencias lógicas para el desarrollo backend.
- [x] Se enumeraron las modificaciones exactas aplicadas sobre `specify_refactorizado.md`.
- [x] El artefacto está formateado en Markdown limpio y listo para su incorporación al repositorio Git.
