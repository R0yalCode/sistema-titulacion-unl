---
system: SGT-SIAAF
type: traceability
area: documents
status: verified
source: knowledge-build-session
last_verified: 2026-11-11
---

# Trazabilidad documental: afirmaciones frente a realidad

Contradicciones y afirmaciones no verificables detectadas al contrastar la documentación con el código o entre documentos. **No se resolvieron**: se registran con su evidencia.

| # | Afirmación | Fuente | Realidad verificada | Evidencia |
|---|---|---|---|---|
| C-01 | Existe `ROADMAP_INCREMENTOS_IMPLEMENTACION.md` | Inventario previo (13 docs); plan maestro §14 | No existe; su contenido es la §9 del plan maestro | `find / -iname '*ROADMAP_INCREMENTOS*'` vacío |
| C-02 | "23 endpoints operativos" | Plan maestro §15.H; matriz de brechas obs. 5 | 16 rutas / 17 operaciones | `config/urls.py`, `openapi.yaml` |
| C-03 | `POST /auth/token/refresh/` "implícito" | Plan maestro §8.1 | No existe | `config/urls.py` |
| C-04 | Framer Motion, React Hook Form y Zod "ya en deps" | Plan maestro §7.3; matriz FE-10 | No instalados | `frontend/package.json` |
| C-05 | Componentes `KPICard`, `ChartWidget`… "listos" | Arquitectura de dashboards §6 | No existen | `ls frontend/src/components` |
| C-06 | Entregables DP2 en la "raíz del repo" | Plan maestro §14 | En `Documentacion-parte-2/` | `ls` |
| C-07 | F2.5 "80 %" y V-09 "✅" | Plan maestro §2.5 | F2.5 cerrada (FE-T1213 bloqueada); V-09: la página existe, pero FE-T901…904 "Pendiente" | `tasks.md`, `CLAUDE.md` |
| C-08 | 87 controles de seguridad, 73,6 % | Plan maestro §1 | La matriz de seguridad (2026-11-05) cuenta 77 | `MATRIZ_TRAZABILIDAD_SEGURIDAD.md` |
| C-09 | `INFORME_TECNICO_AUDITORIA_SEGURIDAD.md`, `MATRIZ_ESTADO_CONTROLES_SEGURIDAD.md` | DP2 | No existen | `find` |
| C-10 | Numeración SEC-T014…T016 | `TASKS_SEGURIDAD.md` frente al commit ECLIPSE | Significados distintos | Ver [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] §4 |
| C-11 | SEC-T002/T004/T008 "Pendiente" | `TASKS_SEGURIDAD.md` | Implementados | `base.py`, `views.py` |
| C-12 | 40 KPIs | `INFORME_DISENO_KPI.md` §16; DP2 | El desglose suma 47 IDs | [[KPI_CATALOG]] |
| C-13 | ADR-0003: access de 60 min | `backend/docs/adr/0003-…` | 30 min | `base.py` |
| C-14 | Dashboards por rol con backend "CV (endpoints)" | Matriz de brechas DB-02…07 | Solo bandeja y notificaciones | `urls.py` |
| C-15 | RESPONSABLE_DEPENDENCIA carga/descarga documentos | Matriz de acciones rápidas | Sin celdas RBAC | `permissions.py` |
| C-16 | RN-MOD-CAM-02 (solo el Decano autoriza) frente a la matriz §3 (el Secretario también hace POST) | Matriz de reglas de modalidades | Contradicción interna | [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]] |
| C-17 | "Sin Git (el repo no lo usa)" | `AGENTS.md` §3.8, `CLAUDE.md`, DEC-08 (spec 003) | El repo usa Git y PR | `git log`; DK-003 |
| C-18 | Copias "duplicadas" de la guía de vistas | `docs/frontend/` frente a `diseno-ui/` | Mismo tamaño, contenido distinto | `cmp` |
| C-19 | `ADR-0001/0002` en dos ubicaciones | `backend/docs/adr/` frente a `docs/adr/` | Las copias difieren | `cmp` |
| C-20 | Flujo FL-03 operativo extremo a extremo | specify 001 §8; DP2 | Sin transición `ENVIADA→EN_VERIFICACION` | Servicios; `test_expediente_state_machine.py:118` |
| C-21 | 328/328 pruebas frontend en verde | `CLAUDE.md` | 2 de 3 ejecuciones en verde; 1 con 6 fallos | [[REGRESSION_TESTS]] |
| C-22 | `CLAUDE.md` remite a `ESTADO-ACTUAL-PROYECTO.md` | Sección añadida al `CLAUDE.md` local | La nota se llama [[CURRENT_STATE]] (corregido en `CLAUDE.md`) | — |
| C-23 | `backend/contracts/openapi.yaml` es "byte a byte idéntico" a `backend/openapi.yaml` | [[API_CONTRACTS]]; EV-003 | Difieren desde `0a24109` (INC-01); PLB-E1-04 no lo introdujo. **Resuelta 2026-11-12:** copia retirada; canónico `backend/openapi.yaml` (DK-014) | EV-016 |

## Relacionado

[[SOURCE_CATALOG]] · [[GENERAL_TRACEABILITY_MATRIX]]


## Contradicciones registradas el 2026-11-11 (auditoría integral backend)

Dieciocho contradicciones entre los documentos DP2 y el código (C-01…C-18), con lo que debe confirmarse en cada una: `docs/planificacion-backend/AUDITORIA_INTEGRAL_BACKEND.md` §7. Las más relevantes:
- C-01: actor de `POST /modalidad/cambiar/` (Secretario frente a Decano, "autorización dual" sin mecanismo).
- C-11: KPI-SEC-04 y D05 usan `ChecklistVerification.peticion` (FK inexistente); el cruce correcto es por `(expediente, requisito)`.
- C-13: D01/D08 dan por existente `POST /auth/token/refresh/`; no está enrutado.
- C-14: "497 pruebas pasando"; en un entorno limpio fallan 13 (`pypdf`).
No se resolvieron inventando: quedan como DP-xx en `REGISTRO_DECISIONES_TECNICAS.md`.
