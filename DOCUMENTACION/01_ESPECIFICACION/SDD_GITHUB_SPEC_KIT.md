# Uso del GitHub Spec Kit (Spec-Driven Development) en SGT-SIAAF

**Objetivo:** describir cómo se usaron realmente los artefactos `constitution` → `specify` → `clarify` → `plan` → `tasks`, citando únicamente lo que existe en el repositorio. No se narran decisiones ni reuniones que no estén registradas en los propios artefactos.

## 1. Artefactos reales inspeccionados

| Etapa SDD | Backend (`specs/001-tramite-titulacion/`) | Frontend (`specs/003-frontend-titulacion/`) |
|---|---|---|
| `constitution` | `sgt-siaaf/.specify/memory/constitution.md` (573 líneas) + copia en `constitucion.md` (606 líneas) | Hereda la misma Constitución (jerarquía declarada en `AGENTS.md`) |
| `specify` | `specify.md` (746 líneas; v2.0.0, 20-oct-2026) | `specify.md` (996 líneas) |
| `clarify` | `clarify.md` (352 líneas; v1.0.0, 20-oct-2026) | `clarify.md` (269 líneas; con actualizaciones registradas hasta 2026-11-05) |
| `plan` | `plan.md` (809 líneas, 28 secciones) | `plan.md` (704 líneas) |
| `tasks` | `tasks.md` (937 líneas, 12 secciones) | `tasks.md` (1831 líneas) |

No existen `specs/002-*` ni `specs/004-*` en el repositorio; `AGENTS.md` ya documenta explícitamente esta ausencia y advierte que si aparecieran en el futuro la prohibición de uso seguiría aplicando igual.

## 2. Cómo se usó cada etapa (evidencia directa de los artefactos)

### 2.1 `constitution` — gobernanza no negociable

Define **18 principios** (P-01 a P-18, no 20 — ver hallazgo en §4) organizados en: propósito y alcance por fases de entrega (§§1–2), principios no negociables (§3), modelo conceptual obligatorio (§4), actores y autorización (§5), arquitectura y tecnologías (§6), requisitos no funcionales mínimos (§7), desarrollo guiado por especificaciones (§8), pruebas y criterios de terminado (§9), gestión de cambios (§10) y decisiones confirmadas/pendientes (§11). Es la autoridad máxima: tanto `specify.md` como `clarify.md` declaran explícitamente estar subordinados a ella.

### 2.2 `specify` — especificación funcional inmutable

El documento del backend se autodenomina "Especificación Funcional Inmutable" y declara 9 fuentes primarias de trazabilidad (Constitución, RRA-UNL, plantillas de Providencia #590 y Memorando #162, transcripción de retroalimentación docente, análisis previos, banco de requisitos ACD2, sílabo de la asignatura y Estatuto UNL). A partir de esas fuentes deriva: diagnóstico del problema, objetivos, alcance, actores y matriz RBAC, modelo conceptual de entidades, 5 flujos principales (FL-01…FL-05), 10 historias de usuario, 16 requisitos funcionales, 18 no funcionales, 12 reglas de negocio, 10 escenarios de excepción, 8 criterios de aceptación y una matriz de trazabilidad integral. Esta especificación es la fuente única usada para consolidar `REQUISITOS_FUNCIONALES.md`, `REQUISITOS_NO_FUNCIONALES.md` y `HISTORIAS_Y_CASOS_DE_USO.md` de este expediente.

### 2.3 `clarify` — gestión formal de ambigüedades

Se usó para resolver explícitamente 8 asuntos de clarificación (`AP-01` a `AP-08`) antes de permitir el avance a `plan`. El propio documento registra su resultado: 3 resueltos con evidencia documental, 2 resueltos por decisión aprobada del equipo, 1 parcialmente resuelto (pendiente de validación normativa externa), 1 resuelto por control técnico (concurrencia) y 1 pendiente de aprobación institucional (fuera del MVP). Cada ficha de asunto documenta pregunta exacta, alternativas evaluadas, decisión tomada y riesgo residual (`RSK-01` a `RSK-08`). Las decisiones DEC-01 a DEC-05 derivadas de este proceso se verificaron contra el código en Fase 0/1 de este trabajo (ver `MATRIZ_TRAZABILIDAD.md`) y están implementadas.

El `clarify.md` del frontend usa el mismo mecanismo de forma más granular y con fecha de actualización continua (DEC-01 a DEC-16, INC-14 a INC-21, D-FE-01 a D-FE-04): es el artefacto que efectivamente gobernó decisiones operativas recientes como la autorización de mascotas del prototipo B (DEC-15) o la verificación de BE-05 contra el código real (DEC-16).

### 2.4 `plan` — arquitectura y diseño técnico

El plan del backend traduce la especificación en arquitectura: selección de Django+DRF con justificación (§7), diagramas de contexto y contenedores (§§8–9) descritos en texto, arquitectura hexagonal con dirección de dependencias (§10), diseño del monolito modular (§11), modelo de dominio (§12), estructura de directorios (§13) y estrategia de persistencia/transacciones (§14) — todo ello coincide con la estructura real observada en `backend/src/` durante la Fase 0 de este trabajo, lo cual confirma que el plan efectivamente guio la implementación y no quedó solo en el papel.

### 2.5 `tasks` — ejecución trazable

`tasks.md` (backend) organiza el trabajo en paquetes (§7, hasta la línea 850) con una matriz de trazabilidad integral requisito-tarea-prueba-estado (§8) y un registro explícito de tareas bloqueadas (§9). El `tasks.md` del frontend sigue el mismo patrón y es, según `AGENTS.md` y `CLAUDE.md`, el artefacto que efectivamente se actualiza al cierre de cada lote de trabajo del frontend (estado Hecha/En curso/Bloqueada con evidencia).

## 3. Evidencia de que el ciclo se siguió en la práctica, no solo en el papel

- Las decisiones de `clarify.md` (backend) se reflejan en el código real verificado en Fase 0 (p. ej. `guardar_archivo_privado` llamado en `declarar_aptitud.py`, acorde a DEC-04).
- El `clarify.md` del frontend se actualiza con fechas y verificaciones directas contra código (DEC-16: "Verificado 2026-11-05 contra el código real..."), lo cual es un patrón de gobernanza SDD activo, no solo documental.
- `AGENTS.md` y `CLAUDE.md` (las guías operativas para agentes) citan explícitamente el orden de lectura `constitution → specify → clarify → plan → tasks` como prerrequisito antes de cualquier tarea, confirmando que el ciclo se usa como control de proceso real, no solo como artefacto de entrega.

## 4. Hallazgo: inconsistencia de numeración de principios

Como ya se señaló en `CONTEXTO_PROYECTO.md` §9, `specify.md` cita sistemáticamente "Principio C-001" a "C-020" (hasta 20 principios), mientras que la Constitución real numera sus principios como P-01 a P-18 (18 principios). Esta inconsistencia estaba ya señalada por `auditoria/05_AUDITORIA_SDD.md` (01-nov-2026) y permanece sin corregir al 2026-11-06. No se resuelve en este trabajo de documentación (no está autorizado editar `specify.md` sin citar el ID de decisión afectado); se deja registrada como pendiente para quien tenga autoridad sobre esos artefactos.

## 5. Conclusión

El proyecto usó el GitHub Spec Kit de forma sustantiva, no decorativa: cada etapa aporta artefactos extensos y específicos, con trazabilidad cruzada verificable, y las decisiones documentadas en `clarify.md` tienen correlato comprobable en el código. La principal debilidad metodológica detectada no es la ausencia de uso del Spec Kit, sino una inconsistencia de numeración interna entre `constitution` y `specify` que no se ha corregido.
