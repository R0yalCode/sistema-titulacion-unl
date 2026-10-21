# DOSSIER MAESTRO DE TAREAS TÉCNICAS, TRAZABLES Y VERIFICABLE (tasks.md)

**Sistema de Gestión del Trámite de Titulación integrado al SIAAF (SGT-SIAAF)**  
*Universidad Nacional de Loja — Facultad de la Energía, las Industrias y los Recursos Naturales No Renovables (FEIRNNR)*  
**Carrera de Computación — Asignatura: Desarrollo Basado en Plataformas (5.º Ciclo)**  
**Versión del Artefacto:** 1.0.0 (Oficial)  
**Estatus Documental:** Plan de Tareas Técnicas y Descomposición de Trabajo — GitHub Spec Kit (Etapa `tasks`)  
**Fecha de Emisión:** 20 de octubre de 2026  
**Artefactos de Referencia:** `constitucion.md` (v2.0.0), `specify_refactorizado.md` (v2.0.0), `clarify.md` (v1.0.0), `plan.md` (v1.0.0)  

---

## 1. IDENTIFICACIÓN DEL DOCUMENTO Y VERSIÓN DE REFERENCIA

* **Nombre del Artefacto:** `tasks.md` (Plan Maestro de Tareas de Implementación Técnica).
* **Proyecto:** SGT-SIAAF — Sistema de Gestión del Trámite de Titulación integrado al SIAAF.
* **Versión:** 1.0.0 (Aprobado para ejecución en la Unidad 1 del sílabo).
* **Estatus:** Inmutable y vinculante para las etapas de codificación, pruebas y auditoría.
* **Fecha de Registro:** 20 de octubre de 2026.
* **Autores y Responsables:** Equipo de Arquitectura e Ingeniería de Software SGT-SIAAF (Carrera de Computación, UNL).
* **Jerarquía de Autoridad y Trazabilidad:**
  1. `constitucion.md` (v2.0.0): Norma suprema de gobernanza, simulación y seguridad.
  2. `specify_refactorizado.md` (v2.0.0): Especificación funcional, requisitos, HUs y criterios BDD.
  3. `clarify.md` (v1.0.0): Registro maestro de clarificaciones, decisiones cerradas (`DEC-01` a `DEC-05`) y gestión de ambigüedades.
  4. `plan.md` (v1.0.0): Arquitectura hexagonal, monolito modular, modelo de dominio, contratos REST y estrategia de persistencia.
  5. `tasks.md` (v1.0.0 - Este documento): Descomposición atómica, trazable y verificable en tareas de implementación.

---

## 2. OBJETIVO Y REGLAS DE EJECUCIÓN

### 2.1 Objetivo General
Transformar la planificación técnica y arquitectónica definida en `plan.md` en un conjunto estructurado de tareas atómicas de ingeniería de software, ordenadas cronológicamente por dependencias, trazables hasta los requisitos y verificables mediante criterios objetivos y pruebas automatizadas.

### 2.2 Reglas Fundamentales de Ejecución
1. **Atomicidad y Verificabilidad:** Cada tarea debe producir un resultado concreto comprobable (código, migración, contrato, test, configuración o documento).
2. **Prioridad Absoluta del MVP (Fase 1 — Aptitud Legal):** Las tareas están enfocadas exclusivamente en la construcción del backend de la Fase 1 (Art. 235 RRA-UNL). Las Fases 2 y 3 constan únicamente como preparación arquitectónica no bloqueante.
3. **Restricción Expresa de Notificaciones:** Notificaciones **100% INTERNAS (In-App)**. Se prohíbe crear tareas para SMTP, correo electrónico, SMS, WhatsApp o notificaciones push de terceros (`DEC-01`).
4. **Restricción Expresa de Integración SGA/SIAAF:** Se prohíbe implementar conexiones directas o escrituras en bases de datos del SGA/SIAAF. La interacción se realiza vía `SGAMockAdapter` en memoria o archivo JSON (`DEC-05`).
5. **Aislamiento Hexagonal:** La lógica de negocio reside en el núcleo de dominio (`apps/<modulo>/domain/` y `services/`), desacoplada de vistas y serializadores DRF.

---

## 3. REFERENCIAS Y ARTEFACTOS FUENTE

| ID Fuente | Nombre de la Fuente / Artefacto | Versión / Fecha | Criterio de Jerarquía y Contenido Aportado |
| :--- | :--- | :--- | :--- |
| **F-01** | `constitucion.md` | v2.0.0 (20-oct-2026) | **Gobernanza Supremas.** 20 principios de arquitectura, seguridad RBAC, auditoría y Docker. |
| **F-02** | `specify_refactorizado.md` | v2.0.0 (20-oct-2026) | **Especificación Funcional.** Requisitos `RF-001` a `RF-016`, `RNF-001` a `RNF-018`, `HU-001` a `HU-010`. |
| **F-03** | `clarify.md` | v1.0.0 (20-oct-2026) | **Registro de Decisiones.** Decisiones cerradas `DEC-01` a `DEC-05` y resolución de ambigüedades `AP-01` a `AP-08`. |
| **F-04** | `plan.md` | v1.0.0 (20-oct-2026) | **Arquitectura y Diseño.** Monolito modular, arquitectura hexagonal, diagrama ER, contratos OpenAPI y ADRs. |
| **F-05** | `RRA-UNL` | 27-ene-2021 | **Normativa Legal.** Artículos 235 (Aptitud Legal), 236-237 (Sustentación) y 243-244 (SENESCYT). |
| **F-06** | Plantillas `#590` y `#162` | 13-oct / 15-oct-2026 | **Modelos Oficiales.** Providencia e Informe N° 590 y Memorando de Declaratoria N° 162. |

---

## 4. ALCANCE DEL MVP Y EXCLUSIONES EXPLÍCITAS

### 4.1 Incluido en el MVP (Fase 1 — Aptitud Legal)
* Autenticación JWT stateless y autorización RBAC para 8 roles institucionales (`DEC-02`).
* Gestión de expedientes de titulación en estados `BORRADOR`, `ENVIADA`, `EN_VERIFICACION`, `OBSERVADA`, `INFORME_EMITIDO` y `DECLARADA_APTA`.
* Motor de plazo laboral de 8 días hábiles con soporte de pausa automática durante el estado `OBSERVADA` (`AP-01`).
* Petición interna de certificados institucionales sin uso de correo electrónico (`DEC-01`).
* Ingestión y validación criptográfica de archivos PDF (máximo 10 MB, *magic bytes* `%PDF-` y SHA-256) (`ADR-005`).
* Evaluador de checklist digital con bloqueo pesimista `SELECT FOR UPDATE` (`ADR-007`).
* Módulo de observaciones accionables con efecto bloqueante sobre el informe legal (`RN-003`).
* Subsanación y reemplazo versionado N+1 de requisitos documentales observados.
* Autogeneración de borradores PDF para Providencia N° 590 e ingreso de Declaratoria N° 162 con anexo PDF firmado externamente (`DEC-04`).
* Despachador de notificaciones internas in-app e inserción de auditoría inmutable en `JSONB` (`DEC-01`).
* Esquema OpenAPI v3 interactivo (Swagger UI / Redoc) y suite de pruebas en `pytest` (>70% cobertura).

### 4.2 Exclusiones Explícitas del MVP
* Sending de correos electrónicos externos mediante SMTP, SendGrid, Mailgun o SMS (`DEC-01`).
* Conexión o escritura directa en las bases de datos de producción del SGA o SIAAF (`DEC-05`).
* Motor interno de firma digital criptográfica PKI (X.509 / PFX).
* Reemplazo de firmas físicas autógrafas en las actas de sustentación de la Fase 2 (`RN-006`).
* Habilitación de Django Admin como interfaz operativa expuesta por HTTP.

---

## 5. CONVENCIONES DE SINTAXIS, ESTADOS Y VERIFICACIÓN

* **Formato de ID de Tarea:** `T001`, `T002`, `T003` ... `T046`.
* **Tipos de Tarea:** `Infraestructura`, `Dominio`, `Backend/API`, `Seguridad`, `Pruebas`, `Documentación`.
* **Prioridades:**
  * `Bloqueante`: Requisito indispensable previo para que otros componentes puedan compilar o ejecutarse.
  * `Alta`: Funcionalidad del núcleo del MVP (Fase 1).
  * `Media`: Funcionalidades secundarias o preparación de fases futuras.
  * `Baja`: Mejoras estéticas o documentación complementaria.
* **Estados de Tarea:** `[ ] Pendiente`, `[/] En Progreso`, `[x] Completado`.
* **Métodos de Verificación:** Comandos de terminal, suite de tests en `pytest`, inspección de esquemas OpenAPI o scripts de validación.

---

## 6. MAPA DE DEPENDENCIAS Y SECUENCIA DE EJECUCIÓN

El siguiente grafo ASCII representa la secuencia crítica de implementación entre paquetes de trabajo:

```
[Paquete 1: Infraestructura & Repositorio (T001-T006)]
                     |
                     v
[Paquete 2: Autenticación, JWT & Matriz RBAC (T007-T012)]
                     |
                     v
[Paquete 3: Expedientes & Motor de Plazos 8 Días (T013-T019)]
                     |
                     v
[Paquete 4: Peticiones Documentales & Ingestión PDF (T020-T025)]
                     |
                     v
[Paquete 5: Verificación, Checklist & Observaciones (T026-T031)]
                     |
                     v
[Paquete 6: Resoluciones #590/#162 & Generación PDF (T032-T036)]
                     |
                     v
[Paquete 7: Notificaciones In-App, Auditoría & Mock SGA (T037-T041)]
                     |
                     v
[Paquete 8: Contrato OpenAPI, Pruebas E2E & Docker (T042-T046)]
```

---

## 7. PAQUETES DE TRABAJO Y LISTADO DETALLADO DE TAREAS

### PAQUETE 1: INICIALIZACIÓN DEL PROYECTO, INFRAESTRUCTURA BASE Y ENTORNO DOCKER

#### T001: Estructuración del Repositorio Git y Configuración de Ramas
* **ID:** `T001` | **Tipo:** `Infraestructura` | **Fase:** `Paquete 1` | **Prioridad:** `Bloqueante`
* **Título:** Inicializar el repositorio Git y configurar la estructura de ramas conforme a GitFlow y Spec Kit.
* **Alcance:** Creación del repositorio, configuración de ramas `main` y `develop`, archivo `.gitignore` para Python/Django/Docker, y plantilla de Pull Requests. Excluye código de la aplicación.
* **Fundamento:** `plan.md` § 23, `constitucion.md` Principio C-013, C-019.
* **Componente Afectado:** Raíz del Repositorio Git.
* **Dependencias:** Ninguna (Tarea Inicial).
* **Precondiciones:** Git instalado localmente.
* **Resultado Esperado:** Repositorio estructurado con ramas protegidas y `.gitignore` configurado.
* **Criterios de Finalización:** Ejecución limpia de `git status` sin rastreo de archivos temporales `.pyc`, `.env` o `__pycache__`.
* **Verificación:** `git branch -a` muestra `main` y `develop`.
* **Evidencia:** Repositorio en GitHub / Git local.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T002: Configuración del Entorno Contenerizado con Docker Compose
* **ID:** `T002` | **Tipo:** `Infraestructura` | **Fase:** `Paquete 1` | **Prioridad:** `Bloqueante`
* **Título:** Crear el `Dockerfile` y `docker-compose.yml` para los servicios de Django, PostgreSQL 16 y Nginx.
* **Alcance:** Definición del contenedor Python 3.12, servicio de base de datos PostgreSQL 16 con volumen persistente, proxy Nginx y red aislada. Excluye lógica Django.
* **Fundamento:** `plan.md` § 23.1, `specify_refactorizado.md` `RNF-010`, `constitucion.md` Principio C-013.
* **Componente Afectado:** `docker-compose.yml`, `Dockerfile`, `nginx/nginx.conf`.
* **Dependencias:** `T001`.
* **Precondiciones:** Docker y Docker Compose instalados.
* **Resultado Esperado:** Entorno multicontenedor orquestado listo para levantar con un solo comando.
* **Criterios de Finalización:** `docker-compose up --build` inicia los servicios de Django y PostgreSQL sin errores de conexión.
* **Verificación:** `docker-compose ps` confirma estado `Up` en todos los contenedores.
* **Evidencia:** Archivos `Dockerfile` y `docker-compose.yml` en la raíz.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T003: Inicialización del Proyecto Django 5.x y Configuración Modular de Settings
* **ID:** `T003` | **Tipo:** `Infraestructura` | **Fase:** `Paquete 1` | **Prioridad:** `Bloqueante`
* **Título:** Inicializar el proyecto Django 5.x y dividir la configuración en entornos `base.py`, `local.py` y `test.py`.
* **Alcance:** Creación del paquete `config/settings/`, lectura de variables de entorno mediante `python-decouple` o `django-environ`, y configuración de conexión a PostgreSQL.
* **Fundamento:** `plan.md` § 13, `specify_refactorizado.md` `RNF-014`, `constitucion.md` Principio C-012.
* **Componente Afectado:** `/workspace/backend/src/config/settings/`.
* **Dependencias:** `T002`.
* **Precondiciones:** Contenedor Docker Django en ejecución.
* **Resultado Esperado:** Estructura de settings Django dividida y limpia sin claves hardcodeadas.
* **Criterios de Finalización:** `python manage.py check --settings=config.settings.local` retorna `System check identified no issues (0 silenced)`.
* **Verificación:** Ejecución de `python manage.py check`.
* **Evidencia:** Módulo `src/config/settings/` e historia de variables en `.env.example`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T004: Estructuración del Árbol de Directorios para Arquitectura Hexagonal y Monolito Modular
* **ID:** `T004` | **Tipo:** `Infraestructura` | **Fase:** `Paquete 1` | **Prioridad:** `Bloqueante`
* **Título:** Crear la estructura física de directorios para las 6 aplicaciones Django y los paquetes `core/`.
* **Alcance:** Creación de carpetas `apps/authentication`, `apps/expedientes`, `apps/peticiones`, `apps/verificacion`, `apps/resoluciones`, `apps/notificaciones`, y `core/domain`, `core/ports`, `core/adapters`.
* **Fundamento:** `plan.md` § 11 y § 13, `specify_refactorizado.md` `RNF-009`, `constitucion.md` Principio C-003.
* **Componente Afectado:** Estrutura completa de `/workspace/backend/src/`.
* **Dependencias:** `T003`.
* **Precondiciones:** Proyecto Django inicializado.
* **Resultado Esperado:** Estructura de directorios que refleja fielmente el monolito modular hexagonal.
* **Criterios de Finalización:** Todos los módulos contienen archivos `__init__.py` y son reconocidos por Django en `INSTALLED_APPS`.
* **Verificación:** `python manage.py showmigrations` reconoce las 6 aplicaciones sin errores de importación.
* **Evidencia:** Árbol de directorios en `src/apps/`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T005: Configuración de Herramientas de Calidad de Código y Linters (PEP 8, MyPy, Flake8)
* **ID:** `T005` | **Tipo:** `Infraestructura` | **Fase:** `Paquete 1` | **Prioridad:** `Alta`
* **Título:** Configurar linters y formateadores de código Python (Flake8, Black, MyPy, Isort).
* **Alcance:** Archivos `.flake8`, `pyproject.toml` con reglas Black e Isort, y configuración de chequeo de tipos MyPy.
* **Fundamento:** `plan.md` § 22, `specify_refactorizado.md` `RNF-011`, `constitucion.md` Principio C-016.
* **Componente Afectado:** Raíz del proyecto backend (`.flake8`, `pyproject.toml`).
* **Dependencias:** `T004`.
* **Precondiciones:** Dependencias instaladas en `requirements.txt`.
* **Resultado Esperado:** Herramientas de linter listas para validar el código en integración continua.
* **Criterios de Finalización:** `flake8 src/` y `black --check src/` ejecutan sin advertencias de formato.
* **Verificación:** Ejecución de comandos `flake8` y `black`.
* **Evidencia:** Archivos de configuración `.flake8` y `pyproject.toml`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T006: Registro de Architecture Decision Records (ADR-001 y ADR-002)
* **ID:** `T006` | **Tipo:** `Documentación` | **Fase:** `Paquete 1` | **Prioridad:** `Alta`
* **Título:** Redactar y publicar en el repositorio los archivos `ADR-001` y `ADR-002`.
* **Alcance:** Documentar la selección de la Arquitectura Hexagonal con Monolito Modular (`ADR-001`) y el stack Django 5.x + DRF + PostgreSQL 16 (`ADR-002`).
* **Fundamento:** `plan.md` § 21, `specify_refactorizado.md` `RNF-018`, `constitucion.md` Principio C-020.
* **Componente Afectado:** `/workspace/backend/docs/adr/`.
* **Dependencias:** `T004`.
* **Precondiciones:** Decisión técnica tomada.
* **Resultado Esperado:** Documentos ADR formalizados en formato Markdown.
* **Criterios de Finalización:** Archivos `0001-arquitectura-hexagonal-monolito-modular.md` y `0002-stack-django-drf-postgresql.md` creados con estatus `Aceptado`.
* **Verificación:** Inspección visual de archivos en `docs/adr/`.
* **Evidencia:** Documentos ADR en repositorio.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

---

### PAQUETE 2: MÓDULO DE AUTENTICACIÓN, USUARIOS Y MATRIZ RBAC (apps.authentication)

#### T007: Modelado de Entidades Relacionales de Usuario, Rol y Permisos RBAC
* **ID:** `T007` | **Tipo:** `Dominio` | **Fase:** `Paquete 2` | **Prioridad:** `Bloqueante`
* **Título:** Implementar el modelo de usuario personalizado (`User`) y la asignación de roles RBAC en PostgreSQL.
* **Alcance:** Atributos `id` (UUID), `cedula` (Único), `email`, `carrera_id`, `facultad_id`, e integración con la tabla de roles (`ESTUDIANTE`, `SECRETARIA_CARRERA`, `SECRETARIO_ABOGADO`, `ANALISTA_APOYO`, `DECANO`, `DIRECTOR_CARRERA`, `RESPONSABLE_DEPENDENCIA`, `ADMINISTRADOR`).
* **Fundamento:** `plan.md` § 12, `specify_refactorizado.md` § 6.1, `constitucion.md` Principio C-004.
* **Componente Afectado:** `apps/authentication/adapters/models.py`.
* **Dependencias:** `T004`.
* **Precondiciones:** Módulo `authentication` registrado.
* **Resultado Esperado:** Modelo ORM de usuarios y roles migrado exitosamente en PostgreSQL.
* **Criterios de Finalización:** `python manage.py makemigrations` y `migrate` ejecutan sin conflictos en la base de datos.
* **Verificación:** Inspección de tablas creadas en PostgreSQL con `psql` o pgAdmin.
* **Evidencia:** Archivo de migración en `apps/authentication/adapters/migrations/`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T008: Configuración del Adaptador de Autenticación JWT Stateless (SimpleJWT / ADR-003)
* **ID:** `T008` | **Tipo:** `Backend/API` | **Fase:** `Paquete 2` | **Prioridad:** `Bloqueante`
* **Título:** Configurar `djangorestframework-simplejwt` para la emisión y verificación de tokens JWT.
* **Alcance:** Endpoint POST `/api/v1/auth/token/` para obtención de par `access` (60 min) y `refresh` (24 h), y personalización del payload JWT incluyendo `user_id`, `cedula` y `roles`.
* **Fundamento:** `plan.md` § 15 y § 18, `specify_refactorizado.md` `RNF-001`, `clarify.md` § 5.
* **Componente Afectado:** `apps/authentication/adapters/views.py`, `config/urls.py`.
* **Dependencias:** `T007`.
* **Precondiciones:** Modelo de usuario activo.
* **Resultado Esperado:** Endpoint de autenticación operativo devolviendo JWT stateless sobre HTTPS.
* **Criterios de Finalización:** Petición POST válida a `/api/v1/auth/token/` retorna tokens JWT con código HTTP 200 OK.
* **Verificación:** Test con `pytest` enviando credenciales válidas e inválidas.
* **Evidencia:** Vistas de autenticación y archivo `ADR-003-autenticacion-jwt-stateless.md`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T009: Implementación del Evaluador Servidor de Permisos RBAC (`RBACPermissionEvaluator`)
* **ID:** `T009` | **Tipo:** `Seguridad` | **Fase:** `Paquete 2` | **Prioridad:** `Bloqueante`
* **Título:** Desarrollar la clase de permisos personalizada DRF (`HasRolePermission`) que evalúa la matriz RBAC.
* **Alcance:** Evaluación server-side de la combinación `(Rol × Recurso × Acción × Endpoint)` según la matriz de la sección 6.2 de `specify_refactorizado.md`.
* **Fundamento:** `plan.md` § 18, `specify_refactorizado.md` § 6.2, `constitucion.md` Principio C-004.
* **Componente Afectado:** `apps/authentication/adapters/permissions.py`.
* **Dependencias:** `T008`.
* **Precondiciones:** Payload JWT con roles integrado.
* **Resultado Esperado:** Clase de permiso DRF reutilizable que deniega accesos no autorizados devolviendo HTTP 403 Forbidden.
* **Criterios de Finalización:** Intento de acceso de un `ESTUDIANTE` a un endpoint reservado para `DECANO` es rechazado con 403.
* **Verificación:** Suite de pruebas de matriz de permisos en `pytest`.
* **Evidencia:** Archivo `apps/authentication/adapters/permissions.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T010: Desarrollo de Filtro ORM para Aislamiento de Datos por Ámbito (Prevención IDOR)
* **ID:** `T010` | **Tipo:** `Seguridad` | **Fase:** `Paquete 2` | **Prioridad:** `Alta`
* **Título:** Implementar el mixin o servicio de filtrado de QuerySets por ámbito institucional (`ScopeFilterMixin`).
* **Alcance:** Filtrar las consultas a nivel ORM para garantizar que un estudiante solo acceda a sus expedientes y que los funcionarios solo consulten trámites de su carrera o facultad (`RNF-003`).
* **Fundamento:** `plan.md` § 18, `specify_refactorizado.md` `RNF-003`, `constitucion.md` Principio C-005.
* **Componente Afectado:** `core/adapters/scope_filter.py`.
* **Dependencias:** `T009`.
* **Precondiciones:** Modelo de usuario con atributos `carrera_id` y `facultad_id`.
* **Resultado Esperado:** Mecanismo centralizado que evita vulnerabilidades IDOR filtrando registros en la base de datos.
* **Criterios de Finalización:** Intento de consulta de un expediente ajeno por ID directo retorna HTTP 403 Forbidden o 404 Not Found.
* **Verificación:** Test en `pytest` forzando manipulación de UUID de expedientes entre usuarios.
* **Evidencia:** Mixin de filtrado y tests de intromisión.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T011: Creación de Fixtures y Seeders de Datos Ficticios de Prueba para 8 Roles
* **ID:** `T011` | **Tipo:** `Infraestructura` | **Fase:** `Paquete 2` | **Prioridad:** `Alta`
* **Título:** Crear comando Django de carga de datos iniciales ficticios (`seed_initial_data`).
* **Alcance:** Generación de usuarios ficticios de prueba para cada uno de los 8 roles institucionales (`estudiante_1`, `secretaria_carrera`, `secretario_abogado`, `analista_apoyo`, `decano_feirnnr`, `director_computacion`, `responsable_practicas`, `admin_sys`).
* **Fundamento:** `plan.md` § 23, `specify_refactorizado.md` § 2.2, `constitucion.md` Principio C-002, P-01.
* **Componente Afectado:** `apps/authentication/management/commands/seed_initial_data.py`.
* **Dependencias:** `T007`.
* **Precondiciones:** Tablas de usuario creadas.
* **Resultado Esperado:** Comando ejecutable que puebla la base de datos con cuentas de prueba listas para la demostración.
* **Criterios de Finalización:** `python manage.py seed_initial_data` ejecuta sin errores y crea las 8 cuentas ficticias.
* **Verificación:** Consulta de la tabla de usuarios con `manage.py shell`.
* **Evidencia:** Archivo de comando Seeder en el repositorio.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T012: Pruebas Automatizadas del Módulo de Autenticación y Matriz RBAC con `pytest`
* **ID:** `T012` | **Tipo:** `Pruebas` | **Fase:** `Paquete 2` | **Prioridad:** `Alta`
* **Título:** Desarrollar la suite de pruebas unitarias e integración para autenticación JWT y matriz RBAC.
* **Alcance:** Pruebas de obtención de token, expiración, renovación, denegación 401/403 y aislamiento de datos por ámbito.
* **Fundamento:** `plan.md` § 22, `specify_refactorizado.md` `RNF-012`, `constitucion.md` Principio C-011.
* **Componente Afectado:** `apps/authentication/tests/`.
* **Dependencias:** `T008`, `T009`, `T010`.
* **Precondiciones:** Pytest y pytest-django configurados.
* **Resultado Esperado:** Suite de pruebas en verde verificando la seguridad del módulo de autenticación.
* **Criterios de Finalización:** `pytest apps/authentication/` ejecuta al 100% de éxito con cobertura >80%.
* **Verificación:** Reporte de ejecución de `pytest`.
* **Evidencia:** Archivos `test_jwt.py` y `test_rbac_permissions.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

---

### PAQUETE 3: MÓDULO DE EXPEDIENTES Y MOTOR DE CÓMPUTO DE PLAZOS (apps.expedientes)

#### T013: Modelado e Implementación de la Entidad Relacional `ExpedienteTitulacion`
* **ID:** `T013` | **Tipo:** `Dominio` | **Fase:** `Paquete 3` | **Prioridad:** `Bloqueante`
* **Título:** Implementar el modelo ORM de `ExpedienteTitulacion` e historial de estados en PostgreSQL.
* **Alcance:** Atributos `id` (UUID), `numero_expediente` (Único), `estudiante_id` (FK User), `carrera_id`, `estado` (Enum de 7 estados), `fecha_creacion`, `fecha_recepcion`, `fecha_limite_atencion`, `dias_laborables_acumulados`, `fecha_ultima_pausa`, `activa`.
* **Fundamento:** `plan.md` § 12, `specify_refactorizado.md` § 7.1, `constitucion.md` Principio C-007.
* **Componente Afectado:** `apps/expedientes/adapters/models.py`.
* **Dependencias:** `T007`.
* **Precondiciones:** Módulo `authentication` migrado.
* **Resultado Esperado:** Modelo de expediente relacional listo en PostgreSQL con índices por estado y carrera.
* **Criterios de Finalización:** Migración creada y ejecutada exitosamente.
* **Verificación:** Inspección de tabla `expedientes_expedientetitulacion` en la base de datos.
* **Evidencia:** Archivo de migración en `apps/expedientes/adapters/migrations/`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T014: Implementación del Servicio de Dominio `PlazoLaboralCalculator` con Soporte de Pausa (AP-01)
* **ID:** `T014` | **Tipo:** `Dominio` | **Fase:** `Paquete 3` | **Prioridad:** `Bloqueante`
* **Título:** Desarrollar el calculador de fechas límites sumando 8 días laborables y gestionando pausas en observaciones (`COA Art. 160`).
* **Alcance:** Algoritmo puro de dominio en Python que excluye fines de semana y feriados institucionales configurados, con métodos `calcular_fecha_limite(fecha_inicio, dias=8)` y `pausar_reloj(expediente)` / `reanudar_reloj(expediente)`.
* **Fundamento:** `plan.md` § 5, `specify_refactorizado.md` `RF-003`, `RN-002`, `clarify.md` § 7 (Ficha AP-01).
* **Componente Afectado:** `apps/expedientes/domain/plazo_calculator.py`.
* **Dependencias:** `T013`.
* **Precondiciones:** Ninguna (Dominio puro sin dependencias externas).
* **Resultado Esperado:** Servicio de dominio robusto para el cálculo de plazos de atención y acumulación de pausas.
* **Criterios de Finalización:** Pruebas unitarias de dominio confirman el cálculo exacto de días hábiles omitiendo sábados y domingos.
* **Verificación:** Test unitario en `pytest` con fechas fijas de prueba.
* **Evidencia:** Archivo `plazo_calculator.py` y suite de pruebas unitarias.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T015: Caso de Uso y Endpoint para Creación e Inicialización de Expediente (`BORRADOR`)
* **ID:** `T015` | **Tipo:** `Backend/API` | **Fase:** `Paquete 3` | **Prioridad:** `Alta`
* **Título:** Implementar el caso de uso `CrearExpedienteUseCase` y el endpoint POST `/api/v1/expedientes/`.
* **Alcance:** Validar la ausencia de expedientes activos previa creación, insertar el expediente en estado `BORRADOR` e inicializar automáticamente las 5 peticiones documentales base del Art. 235 del RRA-UNL.
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-001`, `RF-001`, `CA-001`.
* **Componente Afectado:** `apps/expedientes/services/crear_expediente.py`, `views.py`.
* **Dependencias:** `T013`, `T014`.
* **Precondiciones:** Autenticación JWT activa.
* **Resultado Esperado:** Endpoint POST que inicializa la solicitud de titulación y sus 5 requisitos asociados.
* **Criterios de Finalización:** Petición exitosa retorna HTTP 201 Created con el objeto expediente y las 5 peticiones inicializadas.
* **Verificación:** Test de integración con `pytest` consumiendo el endpoint.
* **Evidencia:** Controlador ViewSet y serializadores DRF.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T016: Caso de Uso y Endpoint para Envío Formal, Marca de Tiempo UTC y Asignación de Providencia (`ENVIADA`)
* **ID:** `T016` | **Tipo:** `Backend/API` | **Fase:** `Paquete 3` | **Prioridad:** `Alta`
* **Título:** Implementar el caso de uso `EnviarExpedienteUseCase` y el endpoint POST `/api/v1/expedientes/{id}/enviar/`.
* **Alcance:** Validar que los 5 requisitos contengan archivos PDF vigentes, cambiar estado a `ENVIADA`, registrar inmutablemente `fecha_recepcion` en UTC, autogenerar `numero_providencia` (ej. `PROV-590-2026`) y calcular `fecha_limite_atencion` (`DEC-03`).
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-004`, `RF-002`, `RN-010`, `CA-001`.
* **Componente Afectado:** `apps/expedientes/services/enviar_expediente.py`, `views.py`.
* **Dependencias:** `T015`.
* **Precondiciones:** Requisitos documentales provistos de archivos.
* **Resultado Esperado:** Registro inmutable del inicio formal del trámite administrativo de 8 días laborables.
* **Criterios de Finalización:** Envío con 5 requisitos válidos retorna HTTP 200 OK con fecha límite calculada; envío incompleto retorna 422 Unprocessable Entity.
* **Verificación:** Test BDD en `pytest` simula envío completo e incompleto.
* **Evidencia:** Caso de uso y test `test_enviar_expediente.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T017: Implementación de la Vista de Bandeja Operativa Filtrada por Rol y Dependencia
* **ID:** `T017` | **Tipo:** `Backend/API` | **Fase:** `Paquete 3` | **Prioridad:** `Alta`
* **Título:** Desarrollar el endpoint GET `/api/v1/expedientes/bandeja/` para consulta de trámites asignados.
* **Alcance:** Retornar el listado paginado de expedientes que requieren la intervención del rol del usuario autenticado (ej. solicitudes `ENVIADA` para Secretaría-Abogacía, `INFORME_EMITIDO` para Decanato).
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-005`, `RF-012`.
* **Componente Afectado:** `apps/expedientes/adapters/views.py`.
* **Dependencias:** `T016`, `T010`.
* **Precondiciones:** Autenticación y permisos RBAC activos.
* **Resultado Esperado:** Endpoint de bandeja operativa eficiente que facilita la atención de trámites.
* **Criterios de Finalización:** Consulta por rol `SECRETARIO_ABOGADO` retorna únicamente expedientes en estado `ENVIADA`, `EN_VERIFICACION` y `OBSERVADA` pertenecientes a su facultad.
* **Verificación:** Test en `pytest` autenticando con diferentes roles y comprobando el filtrado.
* **Evidencia:** Vista DRF `BandejaExpedienteViewSet`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T018: Implementación de Filtro ORM de Aislamiento por Ámbito (Prevención IDOR en Expedientes)
* **ID:** `T018` | **Tipo:** `Seguridad` | **Fase:** `Paquete 3` | **Prioridad:** `Alta`
* **Título:** Aplicar la restricción de ámbito en el QuerySet base de expedientes (`get_queryset`).
* **Alcance:** Garantizar que las operaciones GET, PUT o POST sobre un expediente específico verifiquen que el estudiante sea el propietario o que el funcionario pertenezca a la misma carrera/facultad.
* **Fundamento:** `plan.md` § 18, `specify_refactorizado.md` `RNF-003`, `EX-003`, `CA-008`.
* **Componente Afectado:** `apps/expedientes/adapters/views.py`.
* **Dependencias:** `T017`, `T010`.
* **Precondiciones:** `ScopeFilterMixin` disponible.
* **Resultado Esperado:** Prevención absoluta de vulnerabilidades de acceso directo a objetos (IDOR).
* **Criterios de Finalización:** Intento de consultar expediente ajeno mediante UUID directo retorna HTTP 403 Forbidden o 404 Not Found.
* **Verificación:** Test de seguridad en `pytest` (`CA-008`).
* **Evidencia:** Test `test_idor_isolation_expediente.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T019: Pruebas Automatizadas del Motor de Estados y Cómputo de Plazos Laborables con `pytest`
* **ID:** `T019` | **Tipo:** `Pruebas` | **Fase:** `Paquete 3` | **Prioridad:** `Alta`
* **Título:** Crear la suite de pruebas automatizadas para la máquina de estados de expedientes y cálculo de días hábiles.
* **Alcance:** Pruebas de transiciones válidas e inválidas, cálculo de 8 días hábiles, registro inmutable de timestamp y comportamiento ante pausa de plazo.
* **Fundamento:** `plan.md` § 22, `specify_refactorizado.md` `CA-001`, `constitucion.md` Principio C-011.
* **Componente Afectado:** `apps/expedientes/tests/`.
* **Dependencias:** `T016`, `T018`.
* **Precondiciones:** Pytest-django operativo.
* **Resultado Esperado:** Suite completa de pruebas en verde para la lógica del expediente.
* **Criterios de Finalización:** `pytest apps/expedientes/` ejecuta con 100% de éxito y cobertura >80%.
* **Verificación:** Ejecución de `pytest`.
* **Evidencia:** Archivo `test_expediente_state_machine.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

---

### PAQUETE 4: MÓDULO DE PETICIONES DOCUMENTALES E INGESTIÓN PDF (apps.peticiones)

#### T020: Modelado Relacional de `CatalogoDocumental`, `PeticionDocumental` y `DocumentoEntregado`
* **ID:** `T020` | **Tipo:** `Dominio` | **Fase:** `Paquete 4` | **Prioridad:** `Bloqueante`
* **Título:** Implementar los modelos ORM del catálogo de requisitos, peticiones y archivos adjuntos en PostgreSQL.
* **Alcance:** Tablas `CatalogoDocumental` (código, nombre, emisor_sugerido), `PeticionDocumental` (expediente_id, requisito_id, estado_peticion), y `DocumentoEntregado` (version, archivo_path, hash_sha256, tamanio_bytes, subido_por, es_vigente).
* **Fundamento:** `plan.md` § 12, `specify_refactorizado.md` § 7.2-7.4, `constitucion.md` Principio C-006.
* **Componente Afectado:** `apps/peticiones/adapters/models.py`.
* **Dependencias:** `T013`.
* **Precondiciones:** Modelo de expedientes migrado.
* **Resultado Esperado:** Tablas de peticiones y documentos con llaves foráneas e índices por versión vigentes.
* **Criterios de Finalización:** Migraciones de Django aplicadas limpiamente en PostgreSQL.
* **Verificación:** Inspección de base de datos con `psql`.
* **Evidencia:** Archivo de migración en `apps/peticiones/adapters/migrations/`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T021: Caso de Uso y Endpoint para Petición Interna de Certificados Institucionales Sin Correo
* **ID:** `T021` | **Tipo:** `Backend/API` | **Fase:** `Paquete 4` | **Prioridad:** `Alta`
* **Título:** Implementar el endpoint POST `/api/v1/peticiones/{id}/solicitar-emision/` para solicitar certificados dentro del sistema.
* **Alcance:** Cambiar el estado de la petición documental de `PENDIENTE` a `SOLICITADO` y despachar sincrónicamente una `NotificacionInterna` a la bandeja de la dependencia emisora (`DEC-01`).
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-002`, `RF-004`, `Docente`.
* **Componente Afectado:** `apps/peticiones/services/solicitar_emision.py`, `views.py`.
* **Dependencias:** `T020`.
* **Precondiciones:** Expediente en `BORRADOR` u `OBSERVADA`.
* **Resultado Esperado:** Petición interna tramitada que notifica automáticamente a la dependencia sin usar correos informales.
* **Criterios de Finalización:** Ejecución del endpoint cambia el estado a `SOLICITADO` y genera un registro en `notificaciones_notificacioninterna`.
* **Verificación:** Test en `pytest` verificando el cambio de estado y la creación de notificación.
* **Evidencia:** Caso de uso y test de integración.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T022: Implementación del Adaptador de Validación Criptográfica e Ingestión PDF (Magic Bytes & SHA-256 / ADR-005)
* **ID:** `T022` | **Tipo:** `Backend/API` | **Fase:** `Paquete 4` | **Prioridad:** `Bloqueante`
* **Título:** Desarrollar el validador de archivos PDF `PDFValidationAdapter` (validación de tamaño <=10 MB, *magic bytes* `%PDF-` y hash SHA-256).
* **Alcance:** Inspección de bytes en memoria del archivo subido antes de guardar en disco, rechazando ejecutables, imágenes renombradas o archivos mayores a 10 MB con HTTP 400 Bad Request.
* **Fundamento:** `plan.md` § 19, `specify_refactorizado.md` `RNF-004`, `RN-009`, `EX-004`, `EX-005`, `ADR-005`.
* **Componente Afectado:** `core/adapters/pdf_validation.py`.
* **Dependencias:** `T020`.
* **Precondiciones:** Ninguna (Componente de utilidad puro).
* **Resultado Esperado:** Componente reutilizable de validación estricta de archivos PDF.
* **Criterios de Finalización:** Intento de cargar un archivo `.exe` renombrado como `.pdf` genera una excepción `ValidationError` identificando la firma invalida.
* **Verificación:** Test unitario en `pytest` enviando archivos binarios de prueba válidos e inválidos.
* **Evidencia:** Archivo `core/adapters/pdf_validation.py` y tests.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T023: Caso de Uso y Endpoint para Carga de Certificados PDF con Registro `subido_por` (Opción A / DEC-02)
* **ID:** `T023` | **Tipo:** `Backend/API` | **Fase:** `Paquete 4` | **Prioridad:** `Alta`
* **Título:** Desarrollar el endpoint POST `/api/v1/peticiones/{id}/documento/` para adjuntar requisitos en PDF.
* **Alcance:** Recibir archivo multipart/form-data, ejecutar `PDFValidationAdapter`, guardar el PDF en el volumen privado, registrar el metadato `subido_por` (ID usuario y rol) y actualizar el estado de la petición a `CARGADO` (`DEC-02`).
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-003`, `RF-005`, `CA-001`, `DEC-02`.
* **Componente Afectado:** `apps/peticiones/services/cargar_documento.py`, `views.py`.
* **Dependencias:** `T022`.
* **Precondiciones:** Usuario autenticado con rol `ESTUDIANTE` o `SECRETARIA_CARRERA`.
* **Resultado Esperado:** Ingestión segura del certificado PDF en el expediente digital con auditoría del usuario emisor.
* **Criterios de Finalización:** Carga exitosa de PDF válido de 2 MB retorna HTTP 201 Created con los metadatos del documento.
* **Verificación:** Test de carga multipart con `pytest-django`.
* **Evidencia:** Servicio y controlador ViewSet de carga.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T024: Implementación de Almacenamiento Privado Protegido y Endpoint de Descarga Autorizada
* **ID:** `T024` | **Tipo:** `Seguridad` | **Fase:** `Paquete 4` | **Prioridad:** `Alta`
* **Título:** Configurar la descarga protegida de archivos PDF desde el almacenamiento privado (`/media/private/`).
* **Alcance:** Almacenar archivos fuera de la carpeta pública web y servir descargas únicamente previo paso por el middleware de autenticación y verificación de permisos RBAC/IDOR (`RNF-016`).
* **Fundamento:** `plan.md` § 19, `specify_refactorizado.md` `RNF-016`, `constitucion.md` Principio C-018, P-07.
* **Componente Afectado:** `core/adapters/local_storage.py`, `apps/peticiones/views.py`.
* **Dependencias:** `T023`.
* **Precondiciones:** Almacenamiento privado montado en Docker.
* **Resultado Esperado:** Sistema de descarga de archivos 100% seguro contra lecturas no autorizadas.
* **Criterios de Finalización:** Solicitud GET directa a la URL física del archivo sin token JWT retorna 401/403.
* **Verificación:** Test de descarga autenticada y denegación anónima en `pytest`.
* **Evidencia:** Adaptador de almacenamiento privado e historial de descargas.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T025: Pruebas Automatizadas de Ingestión, Validación PDF y Descarga Segura con `pytest`
* **ID:** `T025` | **Tipo:** `Pruebas` | **Fase:** `Paquete 4` | **Prioridad:** `Alta`
* **Título:** Crear la suite de pruebas de integración para la gestión documental e ingestión PDF.
* **Alcance:** Tests de validación de *magic bytes*, rechazo de archivos >10 MB, versionado de documentos y descargas protegidas.
* **Fundamento:** `plan.md` § 22, `specify_refactorizado.md` `CA-001`, `constitucion.md` Principio C-006.
* **Componente Afectado:** `apps/peticiones/tests/`.
* **Dependencias:** `T023`, `T024`.
* **Precondiciones:** Archivos de prueba PDF binarios en carpeta de fixtures.
* **Resultado Esperado:** Suite de pruebas en verde para la gestión de documentos en PDF.
* **Criterios de Finalización:** `pytest apps/peticiones/` ejecuta con 100% de éxito.
* **Verificación:** Reporte de ejecución de `pytest`.
* **Evidencia:** Archivo `test_pdf_ingestion_and_security.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

---

### PAQUETE 5: MÓDULO DE VERIFICACIÓN, CHECKLIST Y OBSERVACIONES ACCIONABLES (apps.verificacion)

#### T026: Modelado e Implementación de Entidades `ChecklistVerification` y `ObservacionAccionable`
* **ID:** `T026` | **Tipo:** `Dominio` | **Fase:** `Paquete 5` | **Prioridad:** `Bloqueante`
* **Título:** Implementar los modelos ORM de evaluación de checklist y observaciones escritas en PostgreSQL.
* **Alcance:** Tablas `ChecklistVerification` (expediente_id, requisito_id, estado_verificacion, evaluado_por) y `ObservacionAccionable` (expediente_id, peticion_id, motivo_observacion, registrada_por, resuelta, fecha_resolucion).
* **Fundamento:** `plan.md` § 12, `specify_refactorizado.md` § 7.5, `constitucion.md` Principio C-007.
* **Componente Afectado:** `apps/verificacion/adapters/models.py`.
* **Dependencias:** `T020`.
* **Precondiciones:** Módulo `peticiones` migrado.
* **Resultado Esperado:** Entidades del checklist y observaciones asociadas a expedientes y peticiones.
* **Criterios de Finalización:** Migraciones de Django ejecutadas correctamente.
* **Verificación:** Inspección de tablas en PostgreSQL.
* **Evidencia:** Archivos de migración en `apps/verificacion/adapters/migrations/`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T027: Endpoint de Evaluación del Checklist Digital con Bloqueo Pesimista `select_for_update()` (ADR-007 / AP-06)
* **ID:** `T027` | **Tipo:** `Backend/API` | **Fase:** `Paquete 5` | **Prioridad:** `Alta`
* **Título:** Desarrollar el endpoint PUT `/api/v1/checklist/{id}/` con transacciones atómicas y bloqueo pesimista en PostgreSQL.
* **Alcance:** Evaluar cada requisito (`VERIFICADO` / `OBSERVADO`) encapsulado en `@transaction.atomic` utilizando `select_for_update()` para evitar condiciones de carrera entre juristas y analistas de apoyo (`AP-06`).
* **Fundamento:** `plan.md` § 14.2, `specify_refactorizado.md` `HU-006`, `RF-006`, `ADR-007`.
* **Componente Afectado:** `apps/verificacion/services/evaluar_checklist.py`, `views.py`.
* **Dependencias:** `T026`.
* **Precondiciones:** Usuario autenticado con rol `SECRETARIO_ABOGADO` o `ANALISTA_APOYO`.
* **Resultado Esperado:** Endpoint de verificación concurrente seguro que garantiza la consistencia del checklist.
* **Criterios de Finalización:** Petición PUT actualiza el estado del requisito e inaltera evaluaciones concurrentes simultáneas.
* **Verificación:** Test de concurrencia simulada con `pytest-django`.
* **Evidencia:** Servicio y controlador ViewSet del checklist.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T028: Caso de Uso y Endpoint para Registro de Observaciones Accionables y Cambio a Estado `OBSERVADA`
* **ID:** `T028` | **Tipo:** `Backend/API` | **Fase:** `Paquete 5` | **Prioridad:** `Alta`
* **Título:** Desarrollar el endpoint POST `/api/v1/expedientes/{id}/observar/` para registrar motivos de rechazo documental.
* **Alcance:** Insertar registro en `ObservacionAccionable`, cambiar el estado de la petición a `OBSERVADO`, cambiar el expediente a `OBSERVADA`, pausar el plazo de 8 días hábiles (`AP-01`) y despachar `NotificacionInterna` al estudiante (`DEC-01`).
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-007`, `RF-007`, `CA-003`, `clarify.md` § 7.
* **Componente Afectado:** `apps/verificacion/services/registrar_observacion.py`, `views.py`.
* **Dependencias:** `T027`, `T014`.
* **Precondiciones:** Requisito con deficiencias documentales.
* **Resultado Esperado:** Registro formal de observaciones escritas con pausa automática del plazo de atención.
* **Criterios de Finalización:** Ejecución del endpoint cambia el expediente a `OBSERVADA`, registra la observación y detiene el contador de días hábiles.
* **Verificación:** Test en `pytest` comprobando el cambio de estado y la pausa del reloj.
* **Evidencia:** Servicio de observacion y tests de integracion.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T029: Implementación del Efecto Bloqueante de Requisitos Observados sobre la Emisión del Informe Legal
* **ID:** `T029` | **Tipo:** `Backend/API` | **Fase:** `Paquete 5` | **Prioridad:** `Bloqueante`
* **Título:** Implementar la validación de negocio que impide técnicamente emitir el informe legal si existe al menos un requisito en `OBSERVADO` o `PENDIENTE` (`RN-003`).
* **Alcance:** Verificar a nivel de servicio que el 100% de los requisitos del Art. 235 posean estado == `VERIFICADO` previa autorización de cambio a `INFORME_EMITIDO`, retornando HTTP 422 Unprocessable Entity en caso contrario.
* **Fundamento:** `plan.md` § 5, `specify_refactorizado.md` `RN-003`, `EX-007`, `CA-003`.
* **Componente Afectado:** `apps/verificacion/services/validar_checklist_completo.py`.
* **Dependencias:** `T028`.
* **Precondiciones:** Intento de emisión de informe legal.
* **Resultado Esperado:** Regla de negocio inquebrantable que previene la aprobación de expedientes deficientes.
* **Criterios de Finalización:** Intento de emitir informe con un requisito en `OBSERVADO` falla devolviendo HTTP 422 e indicando el requisito pendiente.
* **Verificación:** Test BDD en `pytest` (`CA-003`).
* **Evidencia:** Test `test_bloqueo_emision_informe_observado.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T030: Caso de Uso y Endpoint para Subsanación y Versionado N+1 de Documentos Observados
* **ID:** `T030` | **Tipo:** `Backend/API` | **Fase:** `Paquete 5` | **Prioridad:** `Alta`
* **Título:** Implementar el flujo de subsanación de documentos observados por el estudiante.
* **Alcance:** Permitir la carga de un nuevo PDF para un requisito `OBSERVADO`, incrementar la versión del archivo a N+1, marcar `ObservacionAccionable.resuelta = True`, reanudar el reloj de plazo laborable y retornar el expediente al estado `EN_VERIFICACION`.
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-008`, `RF-008`, `RN-011`, `CA-004`.
* **Componente Afectado:** `apps/verificacion/services/subsanar_requisito.py`, `views.py`.
* **Dependencias:** `T028`, `T023`.
* **Precondiciones:** Expediente en estado `OBSERVADA`.
* **Resultado Esperado:** Subsanación limpia de observaciones con historial de versiones anterior conservado en la base de datos.
* **Criterios de Finalización:** Carga de archivo corregido pasa la petición a `CARGADO`, el expediente a `EN_VERIFICACION` y conserva el archivo previo en el historial.
* **Verificación:** Test BDD en `pytest` (`CA-004`).
* **Evidencia:** Servicio de subsanación y test `test_subsanacion_versionado.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T031: Pruebas Automatizadas de Concurrencia, Bloqueo de Informes y Subsanación con `pytest`
* **ID:** `T031` | **Tipo:** `Pruebas` | **Fase:** `Paquete 5` | **Prioridad:** `Alta`
* **Título:** Desarrollar la suite de pruebas automatizadas para el módulo de verificación y checklist.
* **Alcance:** Tests de bloqueo pesimista `SELECT FOR UPDATE`, validación de efecto bloqueante `RN-003`, resolución de observaciones y versionado documental.
* **Fundamento:** `plan.md` § 22, `specify_refactorizado.md` `CA-003`, `CA-004`, `constitucion.md` Principio C-011.
* **Componente Afectado:** `apps/verificacion/tests/`.
* **Dependencias:** `T027`, `T029`, `T030`.
* **Precondiciones:** Entorno de base de datos PostgreSQL de pruebas activo.
* **Resultado Esperado:** Suite de pruebas en verde para el checklist y observaciones.
* **Criterios de Finalización:** `pytest apps/verificacion/` ejecuta con 100% de éxito.
* **Verificación:** Reporte de ejecución de `pytest`.
* **Evidencia:** Archivo `test_checklist_and_observations.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

---

### PAQUETE 6: MÓDULO DE RESOLUCIONES Y GENERACIÓN PDF (apps.resoluciones)

#### T032: Modelado Relacional e Implementación de Entidades `InformeAptitud` y `DeclaratoriaAptitud`
* **ID:** `T032` | **Tipo:** `Dominio` | **Fase:** `Paquete 6` | **Prioridad:** `Bloqueante`
* **Título:** Implementar los modelos ORM de resoluciones oficiales en PostgreSQL.
* **Alcance:** Tablas `InformeAptitud` (expediente_id, numero_providencia, emisor_id, dictamen, archivo_informe_path) y `DeclaratoriaAptitud` (expediente_id, numero_memorando, decano_id, archivo_memorando_firmado_path).
* **Fundamento:** `plan.md` § 12, `specify_refactorizado.md` § 7.6, `constitucion.md` Principio C-002, C-007.
* **Componente Afectado:** `apps/resoluciones/adapters/models.py`.
* **Dependencias:** `T026`.
* **Precondiciones:** Módulo `verificacion` migrado.
* **Resultado Esperado:** Tablas de resoluciones relacionales con restricciones de unicidad en número de providencia y memorando.
* **Criterios de Finalización:** Migraciones de Django ejecutadas sin errores.
* **Verificación:** Inspección de tablas en PostgreSQL con `psql`.
* **Evidencia:** Archivos de migración en `apps/resoluciones/adapters/migrations/`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T033: Implementación del Adaptador Generador de Borradores PDF desde Plantillas Institucionales (`#590` / `#162`)
* **ID:** `T033` | **Tipo:** `Backend/API` | **Fase:** `Paquete 6` | **Prioridad:** `Alta`
* **Título:** Desarrollar el servicio de renderizado de borradores PDF `PDFGeneratorAdapter` (ReportLab / WeasyPrint).
* **Alcance:** Prellenar dinámicamente las plantillas oficiales de la FEIRNNR-UNL (Providencia N° 590 y Memorando N° 162) inyectando datos del estudiante, fechas, checklist y pie de firma de borrador (`RF-010`).
* **Fundamento:** `plan.md` § 19, `specify_refactorizado.md` `RF-010`, `Plantilla #590`, `Plantilla #162`.
* **Componente Afectado:** `apps/resoluciones/adapters/pdf_generator.py`.
* **Dependencias:** `T032`.
* **Precondiciones:** Librería ReportLab/WeasyPrint instalada.
* **Resultado Esperado:** Servicio capaz de generar archivos PDF maquetados profesionalmente a partir de datos del expediente.
* **Criterios de Finalización:** Invocación del generador produce un archivo PDF válido en el sistema de archivos con los textos e insignias institucionales.
* **Verificación:** Test unitario en `pytest` generando y validando un PDF borrador.
* **Evidencia:** Adaptador `pdf_generator.py` y plantilla base HTML/ReportLab.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T034: Caso de Uso y Endpoint para Emisión e Inmutabilización del Informe Legal por Secretaria Abogada
* **ID:** `T034` | **Tipo:** `Backend/API` | **Fase:** `Paquete 6` | **Prioridad:** `Alta`
* **Título:** Desarrollar el endpoint POST `/api/v1/informes/` para la emisión formal del informe legal de aptitud.
* **Alcance:** Validar que las 5 peticiones posean estado == `VERIFICADO`, generar el PDF borrador de la Providencia N° 590, inmutabilizar el registro `InformeAptitud`, cambiar el expediente a `INFORME_EMITIDO` y notificar al Decano/a.
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-009`, `RF-009`, `RN-004`, `CA-005`.
* **Componente Afectado:** `apps/resoluciones/services/emitir_informe.py`, `views.py`.
* **Dependencias:** `T033`, `T029`.
* **Precondiciones:** Usuario autenticado con rol `SECRETARIO_ABOGADO` y checklist 100% verificado.
* **Resultado Esperado:** Emisión e inmutabilización del informe legal de aptitud previo a la declaratoria del Decano/a.
* **Criterios de Finalización:** Petición exitosa retorna HTTP 201 Created con la URL del informe PDF generado y actualiza el expediente a `INFORME_EMITIDO`.
* **Verificación:** Test BDD en `pytest` (`CA-005`).
* **Evidencia:** Servicio y controlador ViewSet de informes.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T035: Caso de Uso y Endpoint para Registro de Declaratoria de Aptitud por Decano/a con Anexo PDF (`DEC-04`)
* **ID:** `T035` | **Tipo:** `Backend/API` | **Fase:** `Paquete 6` | **Prioridad:** `Alta`
* **Título:** Desarrollar el endpoint POST `/api/v1/declaratorias/` para el registro de la declaratoria de aptitud legal.
* **Alcance:** Recibir el memorando modelo N° 162 firmado electrónicamente fuera del sistema (FirmaEC), validar el PDF, asociarlo al expediente, cambiar el estado a `DECLARADA_APTA` y despachar notificaciones con copia a autoridades y estudiante (`DEC-04`).
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-010`, `RF-011`, `RN-004`, `CA-006`, `DEC-04`.
* **Componente Afectado:** `apps/resoluciones/services/declarar_aptitud.py`, `views.py`.
* **Dependencias:** `T034`, `T022`.
* **Precondiciones:** Usuario autenticado con rol `DECANO` (o Analista autorizado) y expediente en `INFORME_EMITIDO`.
* **Resultado Esperado:** Culminación exitosa del flujo administrativo de la Fase 1 (MVP) con el registro de la declaratoria de aptitud.
* **Criterios de Finalización:** Registro exitoso cambia el expediente a `DECLARADA_APTA`, retorna HTTP 201 Created y despacha los avisos con copia.
* **Verificación:** Test BDD en `pytest` (`CA-006`).
* **Evidencia:** Servicio y controlador ViewSet de declaratorias.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T036: Pruebas Automatizadas de Generación y Registro de Resoluciones con `pytest`
* **ID:** `T036` | **Tipo:** `Pruebas` | **Fase:** `Paquete 6` | **Prioridad:** `Alta`
* **Título:** Crear la suite de pruebas automatizadas para el módulo de resoluciones oficiales.
* **Alcance:** Tests de emisión de informe legal, autogeneración PDF, registro de declaratoria por el Decano/a y despacho de copias.
* **Fundamento:** `plan.md` § 22, `specify_refactorizado.md` `CA-005`, `CA-006`, `constitucion.md` Principio C-011.
* **Componente Afectado:** `apps/resoluciones/tests/`.
* **Dependencias:** `T034`, `T035`.
* **Precondiciones:** Fixtures de expedientes en estado `EN_VERIFICACION` e `INFORME_EMITIDO`.
* **Resultado Esperado:** Suite de pruebas en verde para la emisión de resoluciones.
* **Criterios de Finalización:** `pytest apps/resoluciones/` ejecuta al 100% de éxito.
* **Verificación:** Reporte de ejecución de `pytest`.
* **Evidencia:** Archivo `test_resoluciones_and_pdf_generation.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

---

### PAQUETE 7: NOTIFICACIONES INTERNAS, BITÁCORA DE AUDITORÍA Y MOCK SGA (apps.notificaciones & core.adapters)

#### T037: Modelado e Implementación de Entidad `NotificacionInterna` y Despachador Sincrónico In-App (`DEC-01`)
* **ID:** `T037` | **Tipo:** `Dominio` | **Fase:** `Paquete 7` | **Prioridad:** `Bloqueante`
* **Título:** Implementar el modelo relacional `NotificacionInterna` y el servicio despachador sincrónico in-app.
* **Alcance:** Atributos `id` (UUID), `usuario_destino` (FK User), `expediente_id` (FK), `titulo`, `mensaje`, `leida` (Boolean), `fecha_creacion`. Despacho sincrónico in-process descartando infraestructura SMTP (`DEC-01`).
* **Fundamento:** `plan.md` § 20, `specify_refactorizado.md` `RF-012`, `RNF-002`, `clarify.md` § 5 (DEC-01).
* **Componente Afectado:** `apps/notificaciones/adapters/models.py`, `services/notification_service.py`.
* **Dependencias:** `T007`.
* **Precondiciones:** Ninguna.
* **Resultado Esperado:** Servicio de alertas in-app ligero y confiable sin dependencias de correo externo.
* **Criterios de Finalización:** Invocación del servicio inserta el registro en la base de datos de forma sincrónica sin bloquear la transacción principal.
* **Verificación:** Test unitario en `pytest` despachando notificaciones de prueba.
* **Evidencia:** Servicio `notification_service.py` y modelo de notificaciones.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T038: Endpoint GET `/api/v1/notificaciones/` y Pruebas de Despacho de Avisos In-App
* **ID:** `T038` | **Tipo:** `Backend/API` | **Fase:** `Paquete 7` | **Prioridad:** `Alta`
* **Título:** Desarrollar la vista API para consulta y marcado de lectura de notificaciones internas.
* **Alcance:** Endpoint GET `/api/v1/notificaciones/` filtrado por usuario autenticado y PATCH `/api/v1/notificaciones/{id}/marcar-leida/`.
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `HU-005`, `RF-012`.
* **Componente Afectado:** `apps/notificaciones/adapters/views.py`.
* **Dependencias:** `T037`.
* **Precondiciones:** Usuario autenticado.
* **Resultado Esperado:** Endpoint operativo para la consulta de alertas in-app por los usuarios.
* **Criterios de Finalización:** Petición GET retorna el listado de avisos del usuario con estado `leida = False`.
* **Verificación:** Test en `pytest` autenticando y consultando notificaciones.
* **Evidencia:** Controlador ViewSet de notificaciones.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T039: Implementación de la Bitácora Inmutable `EventoAuditoria` en `JSONB` mediante Django Signals
* **ID:** `T039` | **Tipo:** `Seguridad` | **Fase:** `Paquete 7` | **Prioridad:** `Alta`
* **Título:** Implementar el escuchador de eventos de auditoría inmutables en PostgreSQL usando `JSONB`.
* **Alcance:** Capturar automáticamente cambios de estado, evaluaciones de checklist, cargas documentales y emisiones de resoluciones e insertar registros en `EventoAuditoria` (usuario_id, rol, accion, ip, timestamp, detalles_json) (`Principio C-008`).
* **Fundamento:** `plan.md` § 18, `specify_refactorizado.md` `RF-013`, `RNF-015`, `constitucion.md` Principio C-008.
* **Componente Afectado:** `apps/notificaciones/adapters/signals.py`, `models.py`.
* **Dependencias:** `T013`, `T020`.
* **Precondiciones:** Eventos de dominio definidos.
* **Resultado Esperado:** Registro inalterable de auditoría técnica y de negocio para todos los trámites.
* **Criterios de Finalización:** Un cambio de estado de expediente genera automáticamente una fila en `EventoAuditoria` conteniendo el delta del cambio en formato JSONB.
* **Verificación:** Test en `pytest` ejecutando acciones y consultando la tabla de auditoría.
* **Evidencia:** Archivo de señales Django `signals.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T040: Implementación del Adaptador Hexagonal Mock SGA (`SGAMockAdapter`) para Récords Académicos (`DEC-05`)
* **ID:** `T040` | **Tipo:** `Backend/API` | **Fase:** `Paquete 7` | **Prioridad:** `Alta`
* **Título:** Desarrollar el adaptador de integración simulada `SGAMockAdapter` para consulta inmutable de récords.
* **Alcance:** Implementar el puerto `ISGALegatePort` retornando estructuras JSON ficticias de asignaturas, calificaciones y promedio final inalterable del SGA, sin ejecutar conexiones reales (`DEC-05`).
* **Fundamento:** `plan.md` § 17, `specify_refactorizado.md` `RN-005`, `RNF-008`, `constitucion.md` Principio C-017, `DEC-05`.
* **Componente Afectado:** `core/adapters/mock_sga.py`.
* **Dependencias:** `T004`.
* **Precondiciones:** Puerto abstracto `ISGALegatePort` definido.
* **Resultado Esperado:** Adaptador desacoplado que simula las respuestas del SGA institucional de manera transparente.
* **Criterios de Finalización:** Invocación del adaptador con una cédula ficticia retorna el payload JSON de notas con el promedio calculado previamente por el SGA.
* **Verificación:** Test unitario en `pytest` consumiendo el servicio Mock SGA.
* **Evidencia:** Archivo `core/adapters/mock_sga.py` y archivo de fixture JSON.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T041: Pruebas Automatizadas de Auditoría, Despacho de Avisos y Adaptadores Mock con `pytest`
* **ID:** `T041` | **Tipo:** `Pruebas` | **Fase:** `Paquete 7` | **Prioridad:** `Alta`
* **Título:** Crear la suite de pruebas automatizadas para auditoría, notificaciones in-app y adaptadores Mock.
* **Alcance:** Tests de despacho sincrónico de notificaciones, inmutabilidad de registros de auditoría JSONB e integración con `SGAMockAdapter`.
* **Fundamento:** `plan.md` § 22, `specify_refactorizado.md` `RF-012`, `RF-013`, `constitucion.md` Principio C-011.
* **Componente Afectado:** `apps/notificaciones/tests/`, `core/tests/`.
* **Dependencias:** `T038`, `T039`, `T040`.
* **Precondiciones:** Pytest operativo.
* **Resultado Esperado:** Suite de pruebas en verde para notificaciones, auditoría y mocks.
* **Criterios de Finalización:** `pytest apps/notificaciones/` ejecuta con 100% de éxito.
* **Verificación:** Reporte de ejecución de `pytest`.
* **Evidencia:** Archivo `test_notifications_and_audit.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

---

### PAQUETE 8: CONTRATO OPENAPI, PRUEBAS INTEGRADAS, SEGURIDAD Y DOCUMENTACIÓN FINAL

#### T042: Generación, Publicación y Validación de Esquema OpenAPI v3 (`/api/v1/docs/` / Swagger UI)
* **ID:** `T042` | **Tipo:** `Documentación` | **Fase:** `Paquete 8` | **Prioridad:** `Alta`
* **Título:** Configurar `drf-spectacular` para la generación automática del esquema OpenAPI v3 e interfaz Swagger UI.
* **Alcance:** Exponer endpoints `/api/v1/schema/`, `/api/v1/docs/` (Swagger UI) y `/api/v1/redoc/`, documentando esquemas de petición, respuesta, errores HTTP y seguridad JWT.
* **Fundamento:** `plan.md` § 15, `specify_refactorizado.md` `RNF-006`, `constitucion.md` Principio C-010, `Sílabo-DBP`.
* **Componente Afectado:** `config/urls.py`, `config/settings/base.py`.
* **Dependencias:** `T016`, `T023`, `T027`, `T034`, `T035`.
* **Precondiciones:** Todos los ViewSets y endpoints REST registrados.
* **Resultado Esperado:** Documentación viva e interactiva del contrato API RESTful pública en el navegador.
* **Criterios de Finalización:** Navegación hacia `/api/v1/docs/` renderiza la interfaz Swagger UI con el 100% de los endpoints documentados sin errores de esquema.
* **Verificación:** Comando `python manage.py espectacular --file openapi.yaml` valida el esquema sin advertencias.
* **Evidencia:** Archivo `contracts/openapi.yaml` e interfaz Swagger UI operativa.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T043: Ejecución de Suite de Pruebas de Integración Extremo a Extremo (E2E) comprobando Cobertura >70%
* **ID:** `T043` | **Tipo:** `Pruebas` | **Fase:** `Paquete 8` | **Prioridad:** `Bloqueante`
* **Título:** Ejecutar la suite completa de pruebas E2E validando los flujos `FL-01` a `FL-05` y la cobertura total del código.
* **Alcance:** Simulación de punta a punta: Creación (`BORRADOR`) -> Envío (`ENVIADA`) -> Observación (`OBSERVADA`) -> Subsanación (`EN_VERIFICACION`) -> Informe (`INFORME_EMITIDO`) -> Declaratoria (`DECLARADA_APTA`), verificando cobertura >70% con `pytest-cov`.
* **Fundamento:** `plan.md` § 22, `specify_refactorizado.md` `RNF-012`, `constitucion.md` Principio C-011.
* **Componente Afectado:** `tests/e2e/`.
* **Dependencias:** Todos los paquetes previos (`T001` a `T041`).
* **Precondiciones:** Base de datos PostgreSQL de pruebas lista.
* **Resultado Esperado:** Verificación integral de la estabilidad, seguridad y funcionalidad del backend SGT-SIAAF.
* **Criterios de Finalización:** `pytest --cov=src/` ejecuta el 100% de los tests en verde alcanzando una cobertura >= 70%.
* **Verificación:** Reporte HTML de cobertura generado en `htmlcov/index.html`.
* **Evidencia:** Reporte de cobertura y suite E2E en `tests/e2e/test_full_workflow.py`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T044: Escaneo de Seguridad Estático (Gitleaks, Bandit) y Verificación de Ausencia de Secretos
* **ID:** `T044` | **Tipo:** `Seguridad` | **Fase:** `Paquete 8` | **Prioridad:** `Alta`
* **Título:** Ejecutar herramientas de escaneo estático de seguridad y auditoría de código sensible (Bandit, Gitleaks, Safety).
* **Alcance:** Inspeccionar el repositorio para descartar la presencia de claves secretas, tokens, contraseñas hardcodeadas o vulnerabilidades comunes en dependencias Python.
* **Fundamento:** `plan.md` § 18, `specify_refactorizado.md` `RNF-014`, `constitucion.md` Principio C-012, P-07.
* **Componente Afectado:** Todo el código fuente del proyecto.
* **Dependencias:** `T043`.
* **Precondiciones:** Herramientas `bandit` y `gitleaks` instaladas.
* **Resultado Esperado:** Repositorio verificado y libre de vulnerabilidades o filtración de secretos.
* **Criterios de Finalización:** `bandit -r src/` y `gitleaks detect` finalizan con 0 hallazgos de severidad alta o crítica.
* **Verificación:** Reporte de salida de Bandit y Gitleaks.
* **Evidencia:** Informe de auditoría de seguridad en `docs/security_report.md`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T045: Verificación de Despliegue Reproducible `docker-compose up` y Documentación del `README.md`
* **ID:** `T045` | **Tipo:** `Documentación` | **Fase:** `Paquete 8` | **Prioridad:** `Alta`
* **Título:** Validar la reproducibilidad del entorno en un contenedor limpio y redactar la guía del `README.md`.
* **Alcance:** Instrucciones de instalación, requerimientos previos, comandos para levantar el entorno (`docker-compose up --build`), ejecución de migraciones, carga de datos iniciales (`seed_initial_data`) y ejecución de pruebas.
* **Fundamento:** `plan.md` § 23, `specify_refactorizado.md` `RNF-010`, `constitucion.md` Principio C-013, P-15.
* **Componente Afectado:** `README.md`.
* **Dependencias:** `T043`, `T044`.
* **Precondiciones:** Entorno Docker aislado de prueba.
* **Resultado Esperado:** Documentación clara que permite a cualquier miembro del equipo levantar y probar el sistema sin conocimiento previo.
* **Criterios de Finalización:** Un evaluador ejecuta los pasos del `README.md` en una máquina limpia y logra acceder a Swagger UI y ejecutar las pruebas exitosamente.
* **Verificación:** Inspección y prueba del procedimiento del `README.md`.
* **Evidencia:** Archivo `README.md` en la raíz del repositorio.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

#### T046: Auditoría de Consistencia Técnica y Cierre del Dossier de Tareas `tasks.md`
* **ID:** `T046` | **Tipo:** `Documentación` | **Fase:** `Paquete 8` | **Prioridad:** `Alta`
* **Título:** Realizar la auditoría de consistencia final del artefacto `tasks.md` comprobando la cobertura del 100% de requisitos.
* **Alcance:** Verificar que no existan tareas huérfanas, IDs duplicados o dependencias circulares, y confirmar la trazabilidad bidireccional con `specify_refactorizado.md` y `plan.md`.
* **Fundamento:** `plan.md` § 27, `specify_refactorizado.md` § 18, `constitucion.md` Principio C-019.
* **Componente Afectado:** `tasks.md`.
* **Dependencias:** `T042` a `T045`.
* **Precondiciones:** Todas las tareas redactadas e integradas en la matriz de trazabilidad.
* **Resultado Esperado:** Artefacto `tasks.md` auditado, consistente y oficialmente cerrado para la fase de construcción.
* **Criterios de Finalización:** Cumplimiento del 100% del checklist de gobernanza de la etapa `tasks`.
* **Verificación:** Revisión estática de consistencia en el archivo `tasks.md`.
* **Evidencia:** Cierre formal del documento `tasks.md`.
* **Bloqueos:** Ninguno.
* **Entrega:** MVP.

---

## 8. MATRIZ DE TRAZABILIDAD INTEGRAL (REQUISITO - TAREA - PRUEBA - ESTADO)

| ID Requisito | Descripción del Requisito | Tareas Relacionadas | Prueba de Verificación | Estado Planificación | Bloqueo / Observación |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-001** | Registro de Solicitud en BORRADOR | `T013`, `T015` | `test_crear_expediente` | **Ejecutable** | Ninguno (MVP) |
| **RF-002** | Timestamp UTC y Providencia | `T013`, `T016` | `test_enviar_timestamp` | **Ejecutable** | Ninguno (MVP) |
| **RF-003** | Plazo 8 Días Hábiles con Pausa | `T014`, `T016`, `T028` | `test_calculo_dias_habiles` | **Ejecutable** | Resolvió AP-01 (`COA Art. 160`) |
| **RF-004** | Petición Interna de Certificados | `T020`, `T021` | `test_solicitar_emision` | **Ejecutable** | Sin correos informales (`DEC-01`) |
| **RF-005** | Carga de Archivos PDF <=10 MB | `T022`, `T023` | `test_carga_pdf_magic_bytes` | **Ejecutable** | Opción A de Carga (`DEC-02`) |
| **RF-006** | Checklist Digital de Requisitos | `T026`, `T027` | `test_checklist_verification` | **Ejecutable** | Bloqueo Pesimista (`ADR-007`) |
| **RF-007** | Registro de Observaciones | `T026`, `T028` | `test_pausa_plazo_observada` | **Ejecutable** | Ninguno (MVP) |
| **RF-008** | Subsanación y Versionado N+1 | `T023`, `T030` | `test_subsanacion_versionado` | **Ejecutable** | Historial preservado |
| **RF-009** | Emisión e Inmutabilidad Informe | `T032`, `T034` | `test_bloqueo_informe_observado`| **Ejecutable** | Providencia N° 590 |
| **RF-010** | Autogeneración Borradores PDF | `T033`, `T034` | `test_pdf_generation_draft` | **Ejecutable** | Plantilla `#590` / `#162` |
| **RF-011** | Declaratoria Decano/a | `T032`, `T035` | `test_declaratoria_decano` | **Ejecutable** | Anexo PDF firmado (`DEC-04`) |
| **RF-012** | Notificaciones Internas In-App | `T037`, `T038` | `test_notificaciones_in_app` | **Ejecutable** | 100% In-App (`DEC-01`) |
| **RF-013** | Bitácora Inmutable Auditoría | `T039` | `test_audit_event_jsonb` | **Ejecutable** | Formato `JSONB` |
| **RF-014** | Tribunal de Sustentación (F2) | `T013` (Estructura) | N/A en MVP | **Futura** | Fase 2 (Incremento) |
| **RF-015** | Acta Sustentación Firma Física | `T013` (Estructura) | N/A en MVP | **Futura** | Firma física autógrafa (`RN-006`) |
| **RF-016** | Expediente Consolidado SENESCYT| `T013` (Estructura) | N/A en MVP | **Futura** | Fase 3 (`AP-08`) |
| **RNF-001**| Autenticación JWT Stateless | `T008`, `T012` | `test_jwt_auth_pass_and_fail`| **Ejecutable** | SimpleJWT (`ADR-003`) |
| **RNF-002**| Permisos RBAC 8 Roles | `T007`, `T009`, `T012` | `test_rbac_matrix_8_roles` | **Ejecutable** | Matriz server-side |
| **RNF-003**| Protección IDOR por Ámbito | `T010`, `T018` | `test_idor_isolation` | **Ejecutable** | Filtrado ORM por Carrera/Fac. |
| **RNF-004**| Validación Magic Bytes PDF | `T022` | `test_magic_bytes_rejection` | **Ejecutable** | Encabezado `%PDF-` |
| **RNF-006**| API RESTful OpenAPI v3 | `T042` | `test_openapi_schema_valid` | **Ejecutable** | `/api/v1/docs/` |
| **RNF-008**| Interoperabilidad Mock SGA | `T040` | `test_sga_mock_adapter` | **Ejecutable** | Sin conexión BD externa (`DEC-05`) |
| **RNF-010**| Docker Compose Reproducible | `T002`, `T045` | `test_docker_build` | **Ejecutable** | `docker-compose up` |
| **RNF-012**| Cobertura Pruebas >70% | `T043` | `pytest --cov` | **Ejecutable** | `pytest-cov` |

---

## 9. REGISTRO DE TAREAS BLOQUEADAS Y DECISIONES PENDIENTES

Actualmente, **NO EXISTEN TAREAS BLOQUEADAS** para la ejecución del MVP de la Fase 1. Todos los asuntos de clarificación de la etapa `clarify` fueron cerrados mediante decisiones de proyecto o evidencias normativas:

* **AP-01 (Cómputo de Plazos en Observaciones):** RESUELTO mediante la incorporación de la lógica de pausa de días hábiles (`COA Art. 160`) en la tarea `T014`.
* **AP-02 (Numeración Correlativa Documental):** RESUELTO mediante autogeneración con opción de sobreescritura manual (`DEC-03`) en las tareas `T016` y `T034`.
* **AP-03 (Permisos de Carga de Certificados):** RESUELTO mediante la adopción de la Opción A (`DEC-02`) con auditoría `subido_por` en la tarea `T023`.
* **AP-04 (Canal de Notificaciones del MVP):** RESUELTO mediante notificaciones 100% in-app (`DEC-01`) en las tareas `T037` y `T038`.
* **AP-05 (Firma Digital vs Autógrafa):** RESUELTO revalidando la firma autógrafa física en actas y anexos PDF firmados externamente (`DEC-04`) en la tarea `T035`.
* **AP-06 (Concurrencia en Checklist):** RESUELTO mediante bloqueo pesimista `SELECT FOR UPDATE` (`ADR-007`) en la tarea `T027`.
* **AP-07 (Promedios SGA):** RESUELTO tomando el promedio del SGA como insumo inalterable de lectura (`DEC-05`) en la tarea `T040`.
* **AP-08 (Metas de Tiempo Fase 3):** Clasificado como **Futura** al pertenecer a la Fase 3, no afectando el MVP.

---

## 10. COBERTURA DE SEGURIDAD, RBAC Y REQUISITOS NO FUNCIONALES

| Dominio de Seguridad / RNF | Requisito Asociado | Tareas de Implementación | Tareas de Verificación |
| :--- | :--- | :--- | :--- |
| **Autenticación Stateless** | `RNF-001`, `C-004` | `T008` (SimpleJWT) | `T012` (Tests JWT) |
| **Autorización RBAC 8 Roles** | `RNF-002`, `C-004` | `T007`, `T009` (`RBACPermission`) | `T012` (Tests Matriz RBAC) |
| **Aislamiento IDOR por Ámbito**| `RNF-003`, `C-005` | `T010`, `T018` (`ScopeFilterMixin`) | `T018` (Tests Intromisión IDOR) |
| **Integridad de Archivos PDF** | `RNF-004`, `C-006` | `T022` (`PDFValidationAdapter`) | `T025` (Tests Magic Bytes) |
| **Descarga Privada Protegida** | `RNF-016`, `C-018` | `T024` (Private Storage Endpoint) | `T025` (Tests Descarga 403) |
| **Concurrencia Transaccional** | `RNF-009`, `C-009` | `T027` (`select_for_update`) | `T031` (Tests Concurrencia DB) |
| **Auditoria Inmutable JSONB** | `RF-013`, `C-008` | `T039` (`Django Signals Audit`) | `T041` (Tests Audit Logs) |
| **Gestión Segura de Secretos** | `RNF-014`, `C-012` | `T003` (`python-decouple` / `.env`) | `T044` (Escaneo Gitleaks/Bandit) |
| **Reproducibilidad Docker** | `RNF-010`, `C-013` | `T002` (`docker-compose.yml`) | `T045` (Prueba Despliegue Limpio) |

---

## 11. CRITERIOS GLOBAL DE FINALIZACIÓN DEL MVP (FASE 1)

El desarrollo del MVP del **SGT-SIAAF** se considerará 100% completado y listo para demostración académica cuando se cumplan las siguientes condiciones objetivas:

1. **Flujo Funcional de Extremo a Extremo Operativo:** Un estudiante de prueba puede crear su expediente (`BORRADOR`), pedir certificados internamente, adjuntar archivos PDF válidos, enviar la solicitud (`ENVIADA`), recibir marca de tiempo UTC y número de providencia, sufrir una observación (`OBSERVADA`), subsanar el documento (`EN_VERIFICACION`), recibir el informe legal emitido por la Secretaria Abogada (`INFORME_EMITIDO`) y obtener la declaratoria de aptitud registrada por el Decano/a (`DECLARADA_APTA`).
2. **Notificaciones Internas Despachadas:** Los eventos de cambio de estado y observaciones generan registros consultables vía `/api/v1/notificaciones/` para los roles destinatarios.
3. **Contrato OpenAPI Validado:** La especificación OpenAPI v3 en `/api/v1/docs/` renderiza la interfaz Swagger UI sin errores de esquema.
4. **Cobertura de Pruebas >70%:** La suite de pruebas en `pytest` ejecuta con 100% de tests en verde y alcanza una cobertura superior al 70% comprobada con `pytest-cov`.
5. **Cero Secretos Hardcodeados:** El repositorio pasa la auditoría estática de `gitleaks` y `bandit` sin hallazgos de severidad alta.
6. **Despliegue Reproducible:** El sistema levanta de forma limpia mediante `docker-compose up --build` siguiendo exclusivamente las instrucciones del `README.md`.

---

## 12. CHECKLIST DE VALIDACIÓN DEL ARCHIVO `tasks.md`

- [x] Todos los IDs de tareas (`T001` a `T046`) son únicos y estables.
- [x] Todas las dependencias referencian IDs de tareas existentes sin ciclos.
- [x] Cada tarea incluye título con verbo de acción, tipo, paquete, prioridad, fundamento, precondiciones, resultado esperado y criterio de finalización.
- [x] Se respeta la prioridad del MVP (Fase 1 — Aptitud Legal, Art. 235 RRA-UNL).
- [x] Se acata la restricción de notificaciones 100% internas in-app (`DEC-01`).
- [x] Se acata la prohibición de escrituras directas en las BD del SGA/SIAAF (`DEC-05`).
- [x] La matriz de trazabilidad cubre los requisitos funcionales, no funcionales y reglas de negocio.
- [x] Las tareas de seguridad (JWT, RBAC, IDOR, PDF magic bytes) están integradas en la planificación.
- [x] El artefacto está redactado en Markdown técnico limpio y listo para su incorporación al repositorio Git.

---
