# 04. Alternativas Tecnológicas, Decisión Preliminar y Riesgos 
> **Proyecto:** Sistema de Gestión de Titulación UNL   
> **Entorno:** Docker / Docker Compose (Web + App Móvil)
---

## 1. Comparación de Alternativas Tecnológicas de Backend

Se evaluaron tres arquitecturas de backend (*Django + DRF*, *Spring Boot* y *FastAPI*) bajo criterios técnicos homogéneos para responder a las necesidades del Sistema de Titulación de la UNL.

### Tabla Comparativa de Criterios

| Criterio | Django + DRF | Spring Boot | FastAPI | Ref. Académica |
| :--- | :--- | :--- | :--- | :--- |
| **Desarrollo** | **Alta.** ORM y Admin nativos. Minimiza tiempo de desarrollo. | **Media/Baja.** Alta verbosidad y *boilerplate code*. | **Alta/Media.** Conciso, pero requiere integrar ORM y Admin. | Pressman (2019) [1] |
| **Validación** | **Excelente.** Serializadores acoplados a modelos con validación declarativa. | **Excelente.** Estándar Bean Validation (JSR-380). | **Excelente.** Validación en tiempo de ejecución con Pydantic. | Bass et al. (2012) [4] |
| **Autenticación** | **Excelente.** Sistema RBAC y grupos integrado en el núcleo. | **Alta/Compleja.** Muy robusto (Spring Security), curva alta. | **Media.** Depende de librerías de terceros para RBAC. | Ferraiolo et al. (2001) [3] |
| **Exposición API** | **Excelente.** ViewSets y Routers listos para Web y Móvil. | **Alta.** Controladores REST (`@RestController`) empresariales. | **Excelente.** Basado en el estándar OpenAPI (Swagger UI). | Fielding (2000) [2] |
| **Pruebas** | **Alta.** Módulo de pruebas con cliente API y aislamiento de BD. | **Excelente.** Soporte avanzado para pruebas (JUnit, Mockito). | **Alta.** Integración directa con `pytest` y cliente asíncrono. | Pressman (2019) [1] |
| **Documentación** | **Excelente.** Madurez documental oficial y esquemas OpenAPI. | **Excelente.** Documentación corporativa extensa y consolidada. | **Excelente.** Documentación interactiva autogenerada por defecto. | Pressman (2019) [1] |
| **Mantenimiento** | **Alta.** Estructura modular en apps con alta cohesión. | **Alta.** Arquitectura en capas para grandes equipos. | **Media/Alta.** Requiere definir patrones de arquitectura limpia. | Bass et al. (2012) [4] |
| **Interoperabilidad** | **Alta.** Cliente HTTP para consumo de servicios externos (SIAAF). | **Excelente.** Integración con patrones empresariales avanzados. | **Alta.** E/S no bloqueante para alta concurrencia externa. | Bass et al. (2012) [4] |

---

### Análisis de Ventajas, Limitaciones y Justificación Científica

#### 1. Django + Django REST Framework (DRF)
* **Ventajas:** Su paradigma *batteries-included* reduce la cantidad de código para tareas administrativas e infraestructura de seguridad [1]. El panel de administración auditable *out-of-the-box* acelera la gestión de trámites.
* **Limitaciones:** Su modelo de ejecución síncrono estándar (WSGI) presenta mayor latencia en concurrencia masiva, aunque se mitiga mediante servidores ASGI/Gunicorn [4].

#### 2. Spring Boot
* **Ventajas:** Rendimiento óptimo en procesamiento concurrente y tipado estático estricto, ideal para sistemas empresariales [4].
* **Limitaciones:** La sobrecarga de configuración inicial e incremento de verbosidad elevan el tiempo de desarrollo para un plazo acotado de 5 meses [1].

#### 3. FastAPI
* **Ventajas:** Gran rendimiento asíncrono y contratos de API (OpenAPI) autogenerados de forma nativa [2].
* **Limitaciones:** Carece de un ORM y panel de administración nativos; ensamblar librerías externas aumenta el riesgo de incompatibilidad en el mantenimiento [4].

---

## 2. Decisión Técnica Preliminar

### Alternativa Recomendada
Se selecciona **Django + Django REST Framework (DRF)** como el backend oficial para el Sistema de Titulación UNL.

### Justificación Técnica Argumentada
1. **Reducción del Time-to-Market (5 meses):** La literatura en ingeniería de software demuestra que reutilizar componentes probados de autenticación, ORM y administración acelera la entrega del MVP [1].
2. **Soporte Multi-cliente (Web + App Móvil):** La arquitectura RESTful desacoplada propuesta por Fielding [2] permite consumir la misma API desde la plataforma web y la app móvil mediante tokens JWT.
3. **Control de Acceso Basado en Roles (RBAC):** La gestión de trámites exige privilegios estrictos para Estudiantes, Tutores, Lectores y Administradores, cumpliendo con el modelo estándar RBAC [3].
4. **Despliegue Contenerizado:** Integración nativa con **Docker** y **PostgreSQL** para garantizar entornos reproducibles en desarrollo y producción.

### Alternativas Descartadas
* **Spring Boot:** La complejidad accidental de su configuración inicial compromete el cumplimiento del cronograma de 5 meses [1].
* **FastAPI:** Requeriría construir manualmente la interfaz administrativa y el sistema de permisos RBAC, consumiendo tiempo crítico del desarrollo [3].

### Supuestos Técnicos
* El sistema funcionará sobre contenedores **Docker Compose** utilizando **PostgreSQL**.
* La comunicación entre clientes y servidor se protegerá mediante tokens **JWT Stateless** sobre HTTPS [2].

### Riesgos Pendientes y Condiciones de Cambio
* La decisión cambiaría a *Spring Boot* si la normativa de TI de la universidad exige el uso exclusivo de la Máquina Virtual de Java (JVM).
* Se incorporarán colas de tareas asíncronas (Celery/Redis) si se identifican procesos de procesamiento de archivos de alta carga.

---

## 3. Matriz Preliminar de Evaluación de Riesgos Técnicos

La evaluación de riesgos se estructura según los lineamientos del estándar internacional ISO/IEC 31000 de Gestión de Riesgos [5].

| Riesgo Técnico | Prob. | Impacto | Acción Preventiva / Plan de Mitigación | Ref. |
| :--- | :---: | :---: | :--- | :---: |
| **1. Falta de documentación del proceso** | Media | Alto | Diseñar un patrón de Máquina de Estados Finitos para adaptar estados sin alterar la estructura base. | ISO 31000 [5] |
| **2. Incertidumbre en integración SIAAF** | Alta | Medio | Implementar una capa de abstracción con servicios simulados (*Mock Services*) para no detener el MVP. | Bass [4] |
| **3. Permisos mal definidos entre roles** | Media | Alto | Aplicar matriz formal de RBAC y automatizar pruebas sobre permisos en cada endpoint. | Ferraiolo [3] |
| **4. Exposición de datos personales** | Media | Crítico | Restringir acceso mediante JWT y servir expedientes únicamente por rutas privadas protegidas. | Fielding [2] |
| **5. Cambios de requisitos en desarrollo** | Alta | Medio | Aplicar metodología ágil con congelamiento de alcance (*Scope Freeze*) para v1.0 al tercer mes. | Pressman [1] |
| **6. Ausencia de pruebas o documentación** | Media | Alto | Automatizar pruebas con `pytest` en el flujo de trabajo y generar documentación OpenAPI v3. | Pressman [1] |

---

## 4. Resultado Esperado

La adopción de **Django + Django REST Framework** proporciona un marco técnico sólido, auditable y respaldado por la literatura científica. Ofreciendo soporte desacoplado para la aplicación móvil y la interfaz web en un entorno contenerizado con Docker.

---

## 5. Referencias Bibliográficas

1. Pressman, R. S., & Maxim, B. R. (2019). *Software Engineering: A Practitioner's Approach* (9th ed.). McGraw-Hill Education.
2. Fielding, R. T. (2000). *Architectural Styles and the Design of Network-based Software Architectures* (Doctoral dissertation). University of California, Irvine.
3. Ferraiolo, D. F., Sandhu, R., Gavrila, S., Kuhn, D. R., & Chandramouli, R. (2001). Proposed NIST standard for role-based access control. *ACM TISSEC*, 4(3), 224-274.
4. Bass, L., Clements, P., & Kazman, R. (2012). *Software Architecture in Practice* (3rd ed.). Addison-Wesley Professional.
5. International Organization for Standardization. (2018). *Risk management — Guidelines* (ISO Standard No. 31000:2018).
