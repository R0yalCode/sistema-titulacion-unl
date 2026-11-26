# Auditoría documental — SGT-SIAAF

**Objetivo:** determinar, documento por documento, qué existe, dónde, qué contiene y si está vigente, para evitar duplicar trabajo y para decidir qué se consolida, qué se conserva como fuente y qué se declara obsoleto en el expediente de la Evaluación Sumativa 1.

**Criterio de vigencia:** un documento se considera **VIGENTE** si sus afirmaciones verificables coinciden con el código/estructura actual del repositorio (verificado por lectura directa o `grep`); **DESACTUALIZADO** si describe un estado del código que ya cambió; **SIN VERIFICAR** si no se contrastó en esta pasada.

---

## 1. Conjunto `auditoria/` (raíz del repo) — 01-nov-2026

| Archivo | Líneas | Contenido | Vigencia |
|---|---|---|---|
| `01_AUDITORIA_GENERAL.md` | 84 | Descripción del proyecto, estado general, tecnologías, arquitectura, fortalezas, debilidades, riesgos | **DESACTUALIZADO en 3 puntos críticos** (ver H-01 en `INVENTARIO_PROYECTO.md`): el bug de ruta hardcodeada de PDF, la falta de persistencia del memorando y la ausencia de `checklist` en `RBAC_MATRIX` ya no existen en el código actual. El resto (arquitectura hexagonal, 8 apps, stack tecnológico, ausencia de Git) sigue siendo correcto. |
| `02_INVENTARIO_TECNICO.md` | 111 | Inventario técnico detallado | SIN VERIFICAR en esta pasada (no leído línea a línea); su fecha (01-nov) es anterior a varias correcciones registradas en `docs/auditoria-backend/`, por lo que debe tratarse como **posiblemente desactualizado** hasta reverificación en Fase 4. |
| `03_MATRIZ_FUNCIONAL.md` | 90 | Matriz de funcionalidades | SIN VERIFICAR; su cifra de cobertura/funcionalidades puede estar superada por `docs/RESUMEN_EJECUTIVO.md` (56 % / 18 de 32, fecha posterior). |
| `04_AUDITORIA_ARQUITECTONICA.md` | 73 | Arquitectura | SIN VERIFICAR en esta pasada; en principio la arquitectura hexagonal declarada no ha cambiado. |
| `05_AUDITORIA_SDD.md` | 82 | Cumplimiento SDD | SIN VERIFICAR; `01_AUDITORIA_GENERAL.md` ya señala vacíos (ADR faltantes, tareas sin marcar) que pueden haberse resuelto después. |
| `06_AUDITORIA_SEGURIDAD_Y_CALIDAD.md` | 112 | Seguridad y calidad | SIN VERIFICAR; existe un conjunto más reciente y más extenso en `docs/auditoria-backend/seguridad/` (5 informes + 10 documentos de plan de implementación) que debe tratarse como la fuente más autorizada por fecha y profundidad. |
| `07_DEUDA_TECNICA_Y_RIESGOS.md` | 60 | Deuda técnica | SIN VERIFICAR; parcialmente superado por los mismos hallazgos de H-01. |
| `08_RECOMENDACIONES_DE_MEJORA.md` | 66 | Recomendaciones | SIN VERIFICAR; puede solaparse con `docs/auditoria/PLAN_MEJORA_TECNICA.md` (posterior). |

**Conclusión sobre `auditoria/`:** es una auditoría **anterior y parcialmente superada** por el trabajo posterior en `docs/auditoria-backend/` y `docs/auditoria/`. No se elimina (regla 2.3 prohíbe borrar archivos existentes) ni se duplica su contenido. Se referencia como antecedente histórico y se marca explícitamente como **superada en los puntos donde choca con evidencia de código más reciente**. Las fases siguientes de este trabajo deben citar `docs/auditoria-backend/` y `docs/auditoria/` como fuente primaria para seguridad y validación, no `auditoria/06…08`.

---

## 2. Conjunto `docs/` (portal Quarto) — mayormente 05-nov-2026

### 2.1 Capítulos numerados (`01-introduccion` … `09-calidad`)

Cubren, en estructura, la práctica totalidad de lo que el prompt maestro pide para las Fases 1 (contexto/requisitos), 3 (arquitectura), 4 (backend), 5 (API), 6 (seguridad), 8 (despliegue) y 9 (calidad/pruebas). **No se leyó el contenido completo de los 47 archivos en esta pasada** (alcance de Fase 0: inventariar, no auditar contenido línea por línea); se deja como tarea de las fases 1–9 de este plan verificar cada capítulo contra el código antes de darlo por bueno, siguiendo el mismo método usado para detectar H-01/H-02.

**Riesgo identificado:** el `_quarto.yml` referencia explícitamente los 4 niveles C4 (`02-arquitectura/c4/*.md`) y 6 páginas de endpoints (`04-api/endpoints/*.md`); todas existen como archivos (verificado), por lo que la navegación del sitio no debería romperse por archivos faltantes. Pendiente: verificar que Quarto efectivamente renderice sin errores (requiere instalar Quarto CLI, no disponible en este entorno — ver Fase 11/12).

### 2.2 `docs/RESUMEN_EJECUTIVO.md`

Fechado 05-nov-2026. Reporta backend "526 passed / 0 failed", cobertura 93 %, frontend "198 passed / 0 failed (43 archivos)". **Parcialmente desactualizado**: la cifra de frontend es anterior al cierre de V-01→V-04 documentado en `CLAUDE.md` (328/328, mismo día, checkpoint posterior). La cifra de backend no se contrastó en esta pasada (se hará en Fase 7, ejecutando la suite real).

### 2.3 `docs/auditoria-backend/`

Conjunto más extenso y más reciente (`INFORME_FINAL_VALIDACION.md` fechado 2026-11-05, entorno y variables de ejecución documentados explícitamente — buena práctica de trazabilidad). Incluye matrices de permisos, compatibilidad backend-frontend, plan de refactorización y una subcarpeta `seguridad/` con 5 informes más una subcarpeta `plan-implementacion/` con 10 documentos (fichas técnicas SEC-T001…T021, decisiones pendientes, actas de cierre). **Es, por fecha y nivel de detalle, la fuente primaria recomendada para las Fases 4, 6 y 7** de este trabajo, por delante de `auditoria/06…07`.

### 2.4 `docs/auditoria/`

Tres documentos (`INFORME_AUDITORIA_TECNICA.md`, `matriz-trazabilidad.md`, `PLAN_MEJORA_TECNICA.md`), referenciados directamente desde `docs/RESUMEN_EJECUTIVO.md` como "informes derivados". Tratados como vigentes salvo verificación puntual en fases posteriores.

### 2.5 `docs/adr/` vs `sgt-siaaf/specs/001-tramite-titulacion/adr/` — CORREGIDO EN FASE 3

**Corrección respecto a la Fase 0**: en la auditoría inicial se planteó esto como "dos conjuntos de ADR a reconciliar". Al leer el contenido completo en la Fase 3 se confirmó que `sgt-siaaf/specs/001-tramite-titulacion/adr/ADR-001-arquitectura.md` y `ADR-002-limites-modulares.md` están **vacíos (0 bytes)** — no son una versión alternativa, son plantillas nunca completadas. No hay, por tanto, ninguna duplicación real que reconciliar: el único contenido sustantivo de ADR en todo el repositorio es `docs/adr/0001-arquitectura-hexagonal-monolito-modular.md` y `docs/adr/0002-stack-django-drf-postgresql.md`. Esto confirma y reverifica directamente (con lectura de archivo, no solo referencia cruzada) el hallazgo que ya había señalado `auditoria/01_AUDITORIA_GENERAL.md` ("plantillas y ADRs spec-level en 0 bytes"), vigente al 2026-11-06. Se documenta como brecha de formalización SDD en `DOCUMENTACION/03_ARQUITECTURA/ADR.md`, no como duplicado.

### 2.6 `docs/02-arquitectura/funcionalidades-futuras/firma-electronica/`

8 documentos sobre una propuesta de integración con FirmaEC. Es una **propuesta, no una implementación**: debe marcarse en el portal final como "DOCUMENTADO, PERO NO IMPLEMENTADO" y nunca presentarse como funcionalidad terminada (regla 2.2).

### 2.7 `docs/frontend/`

`FRONTEND_IMPLEMENTATION_PLAN.md` y `GUIA_VISTAS_TITULACION.md`. El segundo se declara en `AGENTS.md` como "copia canónica" — existe también una copia en `diseno-ui/ui/titulacion-v2/GUIA_VISTAS_TITULACION.md` según `AGENTS.md` §3.5. **Pendiente**: confirmar en Fase 1 cuál de las dos ubicaciones es la fuente única real y evitar citar ambas como si fueran independientes.

### 2.8 `docs/sprint-S1/`

7 documentos de un sprint de estabilización (validación de hallazgos, diagnóstico de pruebas, diagnóstico de Django Admin, matriz de tareas, criterios de aceptación, riesgos/dependencias, informe de implementación). Es evidencia de iteración real (fechas y resultados concretos) y debe citarse en la Fase 7 (pruebas) y Fase 12 (informe final) como evidencia de aseguramiento de calidad.

### 2.9 `docs/indicadores/` y `docs/07-indicadores/`

Existen dos ubicaciones para KPI: `docs/indicadores/INFORME_DISENO_KPI.md` y el capítulo `docs/07-indicadores/{informe-kpi,catalogo-indicadores,dashboards-por-rol,apis-indicadores}.md`. Mismo patrón que el ADR: verificar en fases posteriores si uno es la versión "borrador" y el otro la versión "capítulo del portal", para no presentarlos como fuentes independientes.

### 2.10 `docs/security_report.md`

179 líneas, independiente de `docs/auditoria-backend/AUDITORIA_SEGURIDAD.md` y de `docs/auditoria-backend/seguridad/`. Pendiente de reconciliar en Fase 6 (seguridad): puede ser un informe de una herramienta automatizada (bandit/gitleaks, dado que `backend/.bandit` y `backend/gitleaks.exe` existen) en lugar de un informe narrativo — se confirmará leyendo su contenido en Fase 6.

---

## 3. Conjunto `sgt-siaaf/specs/` y `.specify/`

Artefactos SDD reales (constitución, specify, clarify, plan, tasks) para `001-tramite-titulacion` (backend) y `003-frontend-titulacion` (frontend). Son la **autoridad normativa** del proyecto según la jerarquía declarada en `AGENTS.md` línea 4. No se duplican ni se reescriben; la Fase 1 de este trabajo (TASK-DOC-014) debe **describir cómo se usaron**, citándolos, sin reinterpretar su contenido.

---

## 4. Documentos sin contraparte de auditoría (requieren verificación directa contra código)

- `backend/openapi.yaml` / posible duplicado en `backend/contracts/` (H-03).
- `backend/README.md` — señalado por `auditoria/01` como "el README upstream de gitleaks, no del proyecto" (es decir, el README real del backend podría no describir el backend). Pendiente de verificación directa en Fase 4/8.
- `README.md` (raíz, 302 líneas) — describe instalación con Docker Compose; es la fuente a usar para `TASK-DOC-081` (instalación), contrastándolo con el `docker-compose.yml` real.

---

## 5. Conclusión de la auditoría documental

El proyecto **no carece de documentación**: existen 8 informes en `auditoria/` y 107 archivos en `docs/`, además de los artefactos SDD normativos. El trabajo de las fases siguientes **no es crear desde cero**, sino:

1. Verificar contenido de cada capítulo de `docs/` contra el código (no se hizo exhaustivamente en esta Fase 0).
2. Reconciliar los duplicados identificados (ADR, indicadores, guía de vistas).
3. Marcar `auditoria/` como antecedente parcialmente superado, sin borrarlo.
4. Rellenar los vacíos reales: diagramas fuente BPMN/Structurizr/PlantUML (no existen como archivos), workflow de publicación GitHub Pages (no existe), declaratoria de IA (no existe), carpeta `DOCUMENTACION/` con el control maestro (se crea en esta fase).
5. Re-ejecutar las pruebas reales antes de dar por buena cualquier cifra de cobertura/resultados (Fase 7), dado que ya se detectaron dos snapshots distintos del mismo día (H-02).
