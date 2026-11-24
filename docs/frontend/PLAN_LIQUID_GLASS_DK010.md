# Reparto DK-010: rediseño Liquid Glass de los paneles por rol

> **Estado: aprobado por R0yalCode el 2026-11-24 e implementado por bloques en `feat/redesign-liquid-glass-dashboards`.**
> Modalidad centralizada (DK-010, enmiendas 2026-11-11 y 2026-11-12), autorizada expresamente por el responsable para esta funcionalidad el 2026-11-24. La ejecución material fue centralizada mediante Claude Code. El autor Git identifica al integrante responsable de la tarea asignada, no a quien escribió el código. Nunca se afirma que un integrante lo desarrolló personalmente.
> Committer de todos los bloques: R0yalCode.
> Línea de cada commit: `Modalidad: implementación centralizada (DK-010, enmienda 2026-11-11) · Tarea <ID> · responsable <Identificador>`.

Bitácora: [[2026-11-24-rediseno-liquid-glass]]. Guía de uso: `docs/frontend/DESIGN_SYSTEM.md` §12.

## Criterio del reparto

Se rotaron las categorías respecto del reparto anterior (DS/ADM, 2026-11-22). Así nadie repite el mismo tipo de trabajo: 7777-C pasa de layout y panel a tokens; JJOC3S, de tokens y búsqueda a componentes; Dan1el17, del kit y la paleta al shell; JuanCalopinoo, de autenticación al panel del estudiante; R0yalCode integra los paneles de funcionarios y la documentación. Cada bloque toca archivos propios y lleva sus pruebas.

## Correspondencia tarea ↔ responsable ↔ commit ↔ archivos

| Orden | Tarea | Responsable | Commit | Archivos | Alcance |
|---:|---|---|---|---:|---|
| 1 | LG-A | 7777-C | `d147940` | 3 | Tokens de la capa glass (`tokens.css`), utilidades `styles/glass.css` e importación en `main.tsx` |
| 2 | LG-B | JJOC3S | `7ae5896` | 9 | `UrgencyIndicator`, `HeroPanel`, `ActionCard`, variante glass de `KpiCard` y `LiquidGlass.test.tsx` |
| 3 | LG-C | Dan1el17 | `f510294` | 6 | `AppShell` (`glass`), CSS del shell, `AppLayout`, `StudentLayout` y sus pruebas |
| 4 | LG-B (corrección) | JJOC3S | `8971d82` | 2 | El indicador de `ActionCard` pasa a la fila de la categoría (hallazgo de la verificación visual) |
| 5 | LG-D | JuanCalopinoo | `ea4eb83` | 5 | Panel del estudiante: hero, `AccionPrioritaria`, KPI de progreso glass y pruebas |
| 6 | LG-E | R0yalCode | commit que contiene este documento | 11 | `AlertaPlazos`, hero de la bandeja y del administrador, pruebas, guía, este plan, bitácora y trazabilidad |

## Dependencias y orden

`LG-A → LG-B → LG-C → LG-D → LG-E`. Cada commit pasa por separado lint, typecheck, pruebas y build (ver su mensaje).

## Correspondencia prototipo ↔ rol real

| Prototipo | Contenido del prototipo | Rol real en SGT-SIAAF | Resultado |
|---|---|---|---|
| `Dasboard_estudiante.html` | Hero, acción prioritaria, KPI, hoja de ruta | `ESTUDIANTE` | Implementado con `GET /expedientes/mi-tramite/` |
| `Dasboard_secretaria.html` | Bandeja de validación documental | `SECRETARIO_ABOGADO`, `ANALISTA_APOYO`, `DECANO` (bandeja); `SECRETARIA_CARRERA` (sin bandeja, BE-09) | Hero y alerta de plazos sobre `GET /expedientes/bandeja/`; la Secretaría de carrera conserva su panel de avisos |
| `Dasboard_admin.html` | Usuarios, RBAC, auditoría, sesiones | `ADMINISTRADOR` | Hero y alerta de plazos; los indicadores de usuarios, sesiones e integridad **no** se implementaron (sin endpoints) |
| `Dasboard_tutor.html` | Coordinación de cohorte, balance de tutorías | Ninguno (`DIRECTOR_CARRERA` no tiene bandeja ni esos datos) | No implementado |
| `Dasboard_docente.html` | Tesistas asignados, dictámenes, Turnitin | Ninguno: no existen los roles DOCENTE ni TUTOR | No implementado |

## Fuera de esta integración

- Paneles de docente y tutor: requieren roles, relaciones y endpoints que el backend no tiene. No se inventaron.
- Skill `frontend-design` (`npx skills add anthropics/skills -s frontend-design`): no se instaló. Ejecutaría un paquete npm no verificado y añadiría archivos fuera del alcance. Sus principios (jerarquía, tipografía, movimiento contenido) se aplicaron directamente.
- `prototipos/vistas_liquid_glass/` sigue sin versionar en la carpeta principal: es referencia visual, no código del producto.
