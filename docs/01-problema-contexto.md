# 01. Contexto Institucional y Análisis del Problema

## 1. Nombre provisional del proyecto
**SGT-SIAAF — Sistema de Gestión del Trámite de Titulación integrado al SIAAF**.

---

## 2. Contexto institucional documentado
El proyecto proviene del portafolio remitido por la Dirección de Tecnologías de la Información (DTI) para la asignatura *Desarrollo Basado en Plataformas* de la Carrera de Computación de la Universidad Nacional de Loja (UNL).

El banco de proyectos plantea textualmente la necesidad de:
> *"apoyar la gestión del trámite de titulación mediante un flujo digital que permita registrar solicitudes, documentos, observaciones, estados y responsables, considerando su futura relación con sistemas institucionales."*

El proceso de titulación en la UNL se rige normativamente por el **Reglamento de Régimen Académico**, el cual norma aspectos cruciales como:
* Las opciones de titulación (Trabajo de Integración Curricular y Examen Complexivo).
* La comprobación de prerrequisitos para la **Declaratoria de Aptitud Legal**.
* La designación del tribunal de sustentación y emisión de actas de grado.

Adicionalmente, el **Anexo de la Resolución 09-2020-UNL** regula directrices metodológicas específicas, tales como los flujos para el **cambio de opción de titulación**, el plazo de tres meses para rendir el examen tras el acompañamiento y la validez de **sustentaciones virtuales**.

El banco de proyectos advierte explícitamente que el proceso completo de titulación es amplio, por lo que el equipo debe delimitar un subproceso concreto para desarrollar un **Producto Mínimo Viable (MVP)** sin intentar reproducir todo el sistema académico institucional ni asumir capacidades no documentadas del SIAAF.

---

## 3. Descripción del problema
El trámite de titulación involucra a diversos actores institucionales  y requiere la validación de múltiples expedientes y certificaciones. Cuando este flujo se gestiona mediante canales manuales, informales o desarticulados, se genera una problemática central:

> **Problema central:** La ausencia de un flujo digital acotado que permita registrar, dar seguimiento y mantener la trazabilidad del trámite de titulación, considerando su futura relación con sistemas institucionales.

Esta situación se manifiesta en las siguientes falencias operativas:
* **Falta de registro unificado:** No existe una plataforma centralizada para el ingreso de solicitudes de titulación y solicitudes de cambio de modalidad.
* **Dispersión documental:** La entrega y revisión de documentos y certificados (prácticas, idiomas, tesorería) se realiza por vías heterogéneas.
* **Opacidad en observaciones y correcciones:** Las revisiones del tutor o tribunales carecen de un historial digital centralizado y auditable.
* **Ambigüedad de roles y estados:** Incerteza respecto a la fase exacta en la que se encuentra el trámite y sobre quién es el responsable de dar el siguiente paso administrativo o académico.

---

## 4. Consecuencias o dificultades que se pretenden reducir
A través de la implementación del flujo digital acotado, se busca mitigar las siguientes dificultades potenciales:

| Dificultad potencial | Descripción y consecuencia institucional |
| :--- | :--- |
| **Dificultad para conocer el estado de una solicitud** | Incertidumbre del estudiante sobre la etapa de su trámite. |
| **Entrega y revisión de documentos por canales dispersos** | Duplicidad de revisiones y riesgo de pérdida o traspapelo de evidencias académicas. |
| **Falta de registro de observaciones y correcciones** | Ausencia de una bitácora que permita verificar si el estudiante subsanó las observaciones de la guía o tutoría. |
| **Falta de claridad sobre responsables** | Retrasos en la atención por falta de asignación explícita de tareas al Director de Carrera, Secretario/a Abogado/a o Decano/a. |
| **Ausencia de trazabilidad en el expediente legal** | Dificultad para auditorías y reconstrucción del historial de la Declaratoria de Aptitud Legal. |

---

## 5. Justificación de la propuesta
El desarrollo de esta solución digital se justifica por los siguientes factores:
1. **Atención a una necesidad institucional documentada:** El DTI identifica formalmente la conveniencia de informatizar este procedimiento.
2. **Soporte al cumplimiento normativo:** El Reglamento de Régimen Académico exige la verificación rigurosa de requisitos previos a la sustentación o examen complexivo. Un sistema digital garantiza que ningún estudiante avance a la fase de tribunal sin la Declaratoria de Aptitud Legal debidamente respaldada.
3. **Garantía de trazabilidad y transparencia:** Permite auditar cada interacción, dictamen o resolución administrativa emitida por los actores del proceso.
4. **Viabilidad técnica mediante un MVP:** Centrar el proyecto en un subproceso delimitado asegura entregables funcionales en el tiempo académico disponible sin sobrecargar el alcance.
5. **Arquitectura desacoplada:** Preparar el sistema para una futura interoperabilidad con el SIAAF permite estructurar los datos sin depender del estado actual de desarrollo de dicho sistema institucional.

---

## 6. Información confirmada, supuestos y aspectos pendientes de validar

### 6.1 Información confirmada
* El proyecto proviene del portafolio del DTI para la asignatura *Desarrollo Basado en Plataformas*.
* El objetivo es apoyar el trámite de titulación mediante un flujo digital de solicitudes, documentos, observaciones, estados y responsables.
* Se contempla la integración futura con el sistema institucional SIAAF.
* El marco normativo exige requisitos específicos para la Aptitud Legal y reglamenta el cambio de opción a Examen Complexivo.

### 6.2 Supuestos de trabajo
* El trámite actual presenta ineficiencias de trazabilidad e información dispersa.
* Los actores institucionales (estudiantes, docentes, secretarios-abogados y autoridades) están dispuestos a adoptar un flujo digital unificado.
* Es posible aislar un subproceso crítico que funcione como un MVP autónomo.
* La estructura documental de la titulación es lo suficientemente estable como para modelar reglas de negocio fijas.

### 6.3 Aspectos pendientes de validar con el requirente
* ¿Cuál es el delimitador exacto (inicio y fin) del subproceso elegido para el MVP?
* ¿Qué catálogo de documentos será estrictamente obligatorio dentro del MVP? 
* ¿Cuáles son las reglas de transición de estados y los permisos exactos por rol? 
* ¿Qué mecanismos o API expone el SIAAF para la sincronización futura de datos estudiantiles?

> **Advertencia explícita:** No se afirma que el SIAAF disponga actualmente de servicios de integración específicos expuestos, ya que no se cuenta con documentación técnica que lo respalde. La relación con el SIAAF se trata como una dependencia futura a clarificar.

---

## 7. Fuentes consultadas

| Fuente | Tipo de documento | Aporte al análisis |
| :--- | :--- | :--- |
| **Banco de Proyectos para ACD1 — Proyecto N.º 6** | Documento académico (UNL) | Definición del reto, necesidad institucional y delimitación del MVP. |
| **Reglamento de Régimen Académico de la UNL** | Normativa institucional (Res. SE-No.01-ROCS-No-04-27-01-2021) | Requisitos de Aptitud Legal, flujos de titulación, roles y tribunal. |
| **Anexo Resolución 09-R-UNL-2020** | Normativa institucional | Reglas para cambio de opción de titulación y sustentaciones virtuales. |
| **Documentación Inicial SGT-SIAAF** | Documento de trabajo | Estructura conceptual previa y alineación con SDD. |
| **GitHub Spec Kit** | Marco metodológico | Estructura de desarrollo guiado por especificaciones (`constitution`, `specify`, `clarify`, `plan`, `tasks`). |
