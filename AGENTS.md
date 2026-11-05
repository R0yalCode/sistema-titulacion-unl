# AGENTS.md — Guía obligatoria para asistentes (Claude Code y otros agentes)

Proyecto: **SGT-SIAAF** — Sistema de Gestión del Trámite de Titulación (UNL).
Jerarquía de autoridad (rutas reales del repo): 1) Constitución (`.specify/memory/constitution.md` y `specs/001-tramite-titulacion/constitucion.md`; intocables), 2) `specs/003-frontend-titulacion/` (SDD del frontend), 3) backend vigente — código Django, `backend/openapi.yaml` y migraciones (intocables para agentes de frontend; una futura spec `specs/004-*` es **referencia reservada y aún no existe** en el repo), 4) este archivo. *(Nota MOMENTO 2: una `specs/002-*` referida en versiones anteriores tampoco existe; no se crean carpetas ni documentos.)*

## 1. Documentos obligatorios antes de cualquier tarea

Antes de proponer o ejecutar trabajo, leer (en este orden):

1. `AGENTS.md` (este archivo) y `CLAUDE.md`.
2. `sgt-siaaf/specs/003-frontend-titulacion/clarify.md` — decisiones DEC-01…DEC-14, hallazgos INC/PQ, defectos D-FE, bloqueos B-xx.
3. `sgt-siaaf/specs/003-frontend-titulacion/specify.md` — vistas V-01…V-09, rutas, requisitos RFF/RNFF, CA; §9.1 (CA globales), §9.2 (V-03), §9.3 (estados de error).
4. `sgt-siaaf/specs/003-frontend-titulacion/plan.md` — stack real, estructura, fases F0…F6 (incluida F2.5).
5. `sgt-siaaf/specs/003-frontend-titulacion/tasks.md` — lista única de tareas y sus estados (Hecha/En curso/Pendiente/Bloqueada); §2 dependencias BE-01…BE-11; §17 trazabilidad; §18 orden/lotes; §19 DoD.
6. Con tareas de UI: `diseno-ui/ui/titulacion-v2/especificaciones/01…08` (08 = estados de error) y, solo como referencia visual no normativa, los prototipos A/B.

## 2. Tareas autorizadas para agentes

- Ejecutar **una tarea por lote**, tomada de `tasks.md` en el orden de §18 (respetando el primer lote de cierre de F0 ya definido allí).
- Escribir solo en: `frontend/` (código de la tarea), y documentación si la tarea lo requiere.
- Idear la tarea en el lote y **detenerse al final del lote**, dejando `tasks.md` actualizado con el estado real de la tarea (Hecha con evidencia / En curso / bloqueada) y esperando la revisión del humano antes del siguiente lote.
- Correr siempre, en el orden dado, antes de declarar "Hecha": `npm run lint` → `npm run typecheck` → `npm run test` (y `npm run build` si se toca build/estructura). Si algo falla, no marcar "Hecha".

## 3. Prohibiciones absolutas

1. **No tocar el backend**: `backend/` (código Django), `backend/openapi.yaml`, migraciones, specs 001 (y Constitución), "Constitución". No inventar endpoints, campos, estados ni datos que el contrato no declare. (No existen specs 002 ni 004 en el repo; si aparecieran en el futuro, la prohibición aplica igual.)
2. **No instalar dependencias** sin autorización explícita del humano.
3. **No simular datos ni flujos** que el backend no provee (prohibición CA-G-01). Prohibidos: usuarios demo, login falso, contadores/porcentajes inventados, estados que no existen en el enum del backend (p. ej. "En revisión"), "Proyecto de Emprendimiento" como opción.
4. **No copiar HTML/CSS/JS de los prototipos** (A: `SGT_SIAAF_Prototipo_HTML_CSS_JS/…`; B: `SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/…`). Son referencia de tono y comportamiento; el código React se escribe desde cero siguiendo el design system (`especificaciones/01`, `03`) con tokens de `frontend/src/styles/tokens.css`.
5. No mover, renombrar ni borrar prototipos, `diseno-ui/` ni `docs/` (la copia canónica de la guía es `diseno-ui/ui/titulacion-v2/GUIA_VISTAS_TITULACION.md`).
6. No implementar los inline-alerts 409/412/428 (FE-T1213): está **Bloqueada** hasta que el backend (BE-11) declare esos códigos.
7. No usar logotipo oficial UNL sin archivo autorizado; no representar colores como "oficiales UNL" (solo "propuestos" y "observados"; PQ-13).
8. No inicializar Git, no hacer commits, no revertir archivos ajenos a la tarea.
9. No editar `clarify.md`/`specify.md`/`plan.md` salvo que la tarea explícitamente lo pida, y citando el ID de decisión afectado.
10. No crear páginas independientes para estados que se resuelven en-vista (401/403; ver DEC-13 y `especificaciones/08`).

## 4. Convenciones rápidas

- Rutas oficiales: `/login`, `/estudiante`, `/estudiante/solicitud/nueva`, `/expedientes/:id`, `/expedientes/:id/peticiones`, `/expedientes/:id/peticiones/:peticionId`, `/bandeja`, `/bandeja/:id`, `/no-habilitado`, `*` → 404.
- Idioma de UI, mensajes y comentarios: español institucional (tú/formal: "Tu solicitud…"); sin tecnicismos al usuario final.
- Accesibilidad AA y axe en cada componente (doc 05); responsive verificado de 320 px (DoD).
- Al cerrar una tarea: actualizar su **Estado** en `tasks.md` con evidencia (comandos, pruebas, capturas si aplica) y marcar dependencias desbloqueadas si corresponde.

## 5. Si encuentras algo fuera de alcance

Si una tarea necesita tocar backend, instalar paquetes, o un endpoint/campo no declarado: **detenerse** y reportar en la revisión del lote; no "arreglarlo por el lado" del frontend.
