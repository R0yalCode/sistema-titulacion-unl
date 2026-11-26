# Matriz inicial de cumplimiento — Evaluación Sumativa 1

**Nota metodológica:** no se localizó en el repositorio un archivo de rúbrica oficial de la Evaluación Sumativa 1 (se buscó por nombre; sin resultados). Esta matriz usa como referencia de requisitos la propia estructura de fases del encargo (Fases 1–13, excluyendo el apartado de control de versiones por instrucción explícita de la sección 2.4). Si existe una rúbrica formal fuera del repositorio, debe incorporarse antes de cerrar la Fase 13.

Leyenda de estado: **IV** = implementado y verificado · **ISV** = implementado sin verificación suficiente · **DNI** = documentado pero no implementado · **PI** = parcialmente implementado · **P** = pendiente · **NA** = no aplica.

| ID | Requisito (fase del encargo) | Evidencia encontrada | Ubicación | Estado | Acción necesaria |
|---|---|---|---|---|---|
| R-00 | Inventario y auditoría documental inicial | Este trabajo (Fase 0) | `DOCUMENTACION/00_AUDITORIA/` | **IV** | Ninguna; mantener actualizado si cambia el repo |
| R-01 | Contexto, problema, objetivos, alcance | `docs/01-introduccion/{introduccion,objetivos,alcance}.md`, `README.md`, specs 001/003 | `docs/01-introduccion/` | **ISV** | Verificar contenido contra specs y marcar vigente o corregir (Fase 1) |
| R-02 | Actores y necesidades | `docs/01-introduccion/actores.md`; roles en `authentication/adapters/permissions.py` (8 roles, confirmado) | `docs/01-introduccion/actores.md` | **ISV** | Contrastar lista de actores documentada contra `RBAC_MATRIX` real |
| R-03 | Requisitos funcionales/no funcionales consolidados | `sgt-siaaf/specs/001.../specify.md`, `specs/003.../specify.md` | `sgt-siaaf/specs/` | **IV** (como fuente SDD) | Consolidar en formato de tabla única en `DOCUMENTACION/01_ESPECIFICACION/` citando la fuente, sin reinventar |
| R-04 | Historias de usuario / casos de uso | Vistas V-01…V-09 en `specify.md`; tareas FE-T* en `tasks.md` | `sgt-siaaf/specs/003.../` | **ISV** | Consolidar, no inventar criterios nuevos |
| R-05 | Explicación del uso del GitHub Spec Kit | Artefactos reales: `constitution.md`, `specify.md`, `clarify.md`, `plan.md`, `tasks.md` (×2 specs) | `sgt-siaaf/.specify/`, `sgt-siaaf/specs/` | **IV** | Redactar narrativa de uso real sin inventar decisiones no registradas |
| R-06 | Matriz de trazabilidad requisito→prueba | `docs/auditoria/matriz-trazabilidad.md`, `tasks.md` §17 (frontend) | `docs/auditoria/`, `sgt-siaaf/specs/003.../tasks.md` | **ISV** | Verificar cobertura real y fusionar en una matriz única (Fase 1) |
| R-07 | Diagrama BPMN 2.0.2 del proceso principal | Ninguno (ni `.bpmn` ni `.svg` en el repo) | — | **P** | Crear desde cero en Fase 2, basado en el flujo real de estados del expediente (`BORRADOR→…→DECLARADA_APTA`) |
| R-08 | C1/C2/C3 en Structurizr DSL | Existen C4 como Mermaid embebido (`docs/02-arquitectura/c4/*.md`), no como `.dsl` | `docs/02-arquitectura/c4/` | **PI** | Migrar/complementar con Structurizr DSL real en Fase 3; conservar el Mermaid existente como referencia |
| R-09 | UML en PlantUML (clases/interfaces relevantes) | No se localizaron archivos `.puml` | — | **P** | Crear en Fase 3 a partir de clases reales (modelos, servicios, puertos) |
| R-10 | ADR consolidados | Dos conjuntos no idénticos: `docs/adr/0001-0002` y `sgt-siaaf/specs/001.../adr/ADR-001-002` | Ambas rutas | **PI** | Reconciliar en Fase 3 (TASK-DOC-034); no presentar como si fueran 4 decisiones independientes si en realidad son 2 |
| R-11 | Stack tecnológico documentado y verificado | `backend/requirements.txt`, `auditoria/01` (versiones verificadas) | `backend/requirements.txt` | **IV** | Confirmar versiones exactas en Fase 4 |
| R-12 | Estructura modular / arquitectura backend | `docs/02-arquitectura/arquitectura-backend.md`, `auditoria/04`, código real (`src/apps/*`, `src/core/*`) | Múltiples | **IV** | Reverificar contra H-01 (bugs ya corregidos) en Fase 4 |
| R-13 | Componentes de negocio documentados | `docs/03-modulos/modulo-*.md` (7 archivos) | `docs/03-modulos/` | **ISV** | Verificar contra servicios reales por app |
| R-14 | Persistencia (modelos, migraciones, integridad) | `docs/05-base-datos/*`, migraciones reales confirmadas (12 archivos en 6 apps) | `docs/05-base-datos/` | **ISV** | Verificar diccionario de datos contra modelos reales |
| R-15 | Inventario de endpoints | `docs/04-api/endpoints/*.md` (6 archivos), `backend/openapi.yaml` (1224 líneas) | `docs/04-api/`, `backend/openapi.yaml` | **ISV** | Confirmar cobertura 1:1 endpoints↔OpenAPI↔documentación (Fase 5) |
| R-16 | Contrato universal de respuesta API | `docs/04-api/convenciones.md` | `docs/04-api/convenciones.md` | **ISV** | Verificar contra serializers/views reales si el contrato `{success,message,data,errors,meta}` se cumple o hay excepciones |
| R-17 | OpenAPI/Swagger accesible y documentado | `backend/openapi.yaml`; posible duplicado en `backend/contracts/` (H-03) | `backend/openapi.yaml` | **PI** | Resolver duplicado; documentar acceso a Swagger/Redoc en Fase 5 |
| R-18 | Autenticación documentada | `docs/06-seguridad/autenticacion.md`, `docs/04-api/autenticacion.md` (posible duplicado temático) | `docs/06-seguridad/`, `docs/04-api/` | **PI** | Reconciliar en Fase 6; confirmar mecanismo JWT real (SimpleJWT, settings) |
| R-19 | Autorización/RBAC documentada | `docs/06-seguridad/{autorizacion,roles-permisos}.md`, `docs/auditoria-backend/MATRIZ_PERMISOS_ROLES.md`, código real (`RBAC_MATRIX`) | Múltiples | **IV** | Confirmar matriz documentada = matriz real (Fase 6) |
| R-20 | Auditoría de seguridad (OWASP) | `docs/auditoria-backend/seguridad/` (5 informes + 10 de plan), `docs/security_report.md`, `auditoria/06` (más antiguo) | `docs/auditoria-backend/seguridad/` | **IV** (como insumo) | Consolidar en un único informe narrativo citando fuentes, sin duplicar contenido íntegro |
| R-21 | Protección de datos / gestión de secretos | `.env.example`, `backend/.env.example`, settings con defaults seguros (`DEBUG=False`, sin `SECRET_KEY` por defecto, confirmado por `auditoria/01`) | `backend/src/config/settings/base.py` | **ISV** | Verificar que no se expongan secretos reales en ningún documento nuevo |
| R-22 | Estrategia y resultados de pruebas | `docs/09-calidad/*`, `docs/sprint-S1/*`, `docs/auditoria-backend/INFORME_FINAL_VALIDACION.md` | Múltiples | **PI** | Cifras inconsistentes entre documentos de la misma fecha (H-02); **requiere re-ejecución real** en Fase 7 antes de declarar cifras finales |
| R-23 | Docker / Docker Compose documentado | `docs/08-infraestructura/*`, `docker-compose.yml`, `docker-compose.prod.yml` existentes y confirmados | `docs/08-infraestructura/` | **ISV** | Verificar instrucciones contra archivos reales; resolver H-04 (modo runserver vs producción) |
| R-24 | GitHub Actions documentado | `.github/workflows/security.yml` real; `docs/09-calidad/ci-seguridad.md` | `.github/workflows/`, `docs/09-calidad/` | **ISV** | Confirmar que el documento describe exactamente el único workflow existente, sin inventar otros |
| R-25 | Observabilidad (logging, health checks) | Health check en `Dockerfile` (`/health/`); sin capítulo dedicado aún | `Dockerfile` (raíz del repositorio) | **PI** | Redactar `DOCUMENTACION/09_OBSERVABILIDAD/OBSERVABILIDAD.md` en Fase 9, diferenciando implementado de recomendado |
| R-26 | Declaratoria de uso de IA | No existe archivo de declaratoria | — | **P** | Redactar en Fase 10 según herramientas realmente usadas (NotebookLM, ChatGPT, OpenCode) |
| R-27 | Portal Quarto funcional y navegable | `docs/_quarto.yml` + 107 archivos ya scaffoldeados; Quarto CLI no instalado en este entorno, sin render verificado | `docs/` | **PI** | No declarar "publicado" sin render real; instalar/verificar Quarto en Fase 11 |
| R-28 | Workflow de publicación GitHub Pages | No existe `.github/workflows/publish-quarto.yml` | — | **P** | Crear en Fase 12 |
| R-29 | Matriz final de cumplimiento + informe final | No existe aún (se crea en Fase 13) | — | **P** | Fase 13, al cierre de todas las anteriores |
| R-30 (excluido) | Control de versiones / GitFlow / historial de commits | — | — | **NA** | Excluido explícitamente por la sección 2.4 del encargo; evidencia ya presentada por separado |

---

## Brechas priorizadas detectadas en Fase 0

1. **Diagramas fuente inexistentes** (BPMN, Structurizr DSL, PlantUML) — brecha más grande respecto al encargo; nada que consolidar, hay que crearlos (Fases 2–3).
2. **Cifras de pruebas inconsistentes entre documentos del mismo día** (H-02) — no se puede cerrar la Fase 7 sin re-ejecutar la suite real.
3. **Tres hallazgos de `auditoria/01` ya corregidos en código** (H-01) — hay que corregir la narrativa, no el código, para no reportar como vigentes bugs ya resueltos.
4. **Duplicados documentales sin reconciliar**: ADR (R-10), indicadores (`docs/indicadores/` vs `docs/07-indicadores/`), guía de vistas (`docs/frontend/` vs `diseno-ui/`), autenticación (`docs/06-seguridad/` vs `docs/04-api/`).
5. **Sin workflow de publicación ni Quarto CLI disponible localmente** — no se puede certificar que el sitio renderiza hasta instalarlo y probarlo (Fase 11/12).
6. **Sin declaratoria de IA** — brecha simple de cerrar, pendiente para Fase 10.

Estas seis brechas son las que determinan el orden de trabajo recomendado para las fases siguientes: primero cerrar las verificaciones de código (H-01 a H-04, Fases 4–8), después generar lo que falta por completo (diagramas, declaratoria IA, workflow Pages), y al final consolidar duplicados y compilar el portal.
