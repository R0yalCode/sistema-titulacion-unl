# Reparto DK-010: sistema de páginas de error (Liquid Glass)

> **Estado: aprobado por R0yalCode el 2026-11-24 e implementado por bloques en `feat/siaaf-error-pages-liquid-glass`.**
> Modalidad centralizada (DK-010, enmiendas 2026-11-11 y 2026-11-12), autorizada expresamente por el responsable para esta funcionalidad el 2026-11-24.
> La ejecución material fue centralizada mediante Claude Code. El autor Git identifica al integrante responsable de la tarea asignada, no a quien escribió el código. Nunca se afirma que un integrante lo desarrolló personalmente.
> Committer de todos los bloques: R0yalCode.
> Línea de cada commit: `Modalidad: implementación centralizada (DK-010, enmienda 2026-11-11) · Tarea <ID> · responsable <Identificador>`.

Bitácora: [[2026-11-24-paginas-error]]. Documentación técnica: `docs/frontend/ERROR_PAGES.md`.

## Criterio del reparto

Se rotaron las categorías respecto del rediseño Liquid Glass (LG). Así nadie repite el mismo tipo de trabajo:

| Integrante | En LG | En este reparto |
|---|---|---|
| Dan1el17 | Shell | Arquitectura base |
| 7777-C | Tokens | Diseño visual |
| JJOC3S | Componentes | Router, autenticación y ErrorBoundary |
| JuanCalopinoo | Panel del estudiante | Recuperación e integración en las vistas |
| R0yalCode | Paneles y documentación | Integración, pruebas y documentación |

## Correspondencia tarea ↔ responsable ↔ commit ↔ archivos

| Orden | Tarea | Responsable | Commit | Archivos | Alcance |
|---:|---|---|---|---:|---|
| 1 | ER-A | Dan1el17 | `9ae8491` | 5 | `errorCatalog`, `classifyError`, `ErrorView` (estructura) y pruebas |
| 2 | ER-B | 7777-C | `fa432f4` | 5 | `ErrorPage`, estilo Liquid Glass, mascota, animaciones, responsive y contraste |
| 3 | ER-C | JJOC3S | `44c07d4` | 14 | 404 real, `/sesion-expirada`, marca de expiración en `RequireAuth`, `ErrorBoundary` y pruebas del router |
| 4 | ER-D | JuanCalopinoo | `bd20e33` | 14 | `QueryErrorView`, `useControlledRetry`, `useOnlineStatus` y cinco vistas conectadas |
| 5 | ER-C (corrección) | JJOC3S | `759aeb2` | 2 | La vista 401 limpia la marca también al salir (hallazgo de integración) |
| 6 | ER-E | R0yalCode | commit que contiene este documento | 9 | `router.errores.test.tsx`, limpieza de CSS sin uso, `ERROR_PAGES.md`, guía §13, este plan, DEC-17, `CLAUDE.md`, bitácora y trazabilidad |

## Dependencias y orden

`ER-A → ER-B → ER-C → ER-D → ER-E`. Cada commit pasó por separado lint, typecheck, pruebas y build; las ejecuciones intermitentes se documentan en su mensaje.

## Correspondencia prototipo ↔ implementación

| Prototipo | Variante | Dónde se usa |
|---|---|---|
| `404.html` | `not-found` | Ruta `*` (página) y 404 de recursos (en la vista) |
| `401.html` | `unauthorized` | `/sesion-expirada` (página) |
| `403.html` | `forbidden` | En la vista; la ruta sin rol sigue en V-09 |
| `500.html` | `server` | En la vista y ErrorBoundary (página) |
| `503.html` | `unavailable` | En la vista, con espera creciente |
| `sin_conexion.html` | `offline` | En la vista |
| `timeout.html` | `timeout` | En la vista |
| `data_error.html` | `data` | En la vista |

**Descartado de los prototipos, por no tener fuente real:**
- IDs de incidencia, nodos, latencias, «15 minutos», «TLS 1.3» y horario de soporte.
- «Borrador en caché», «Conexión restablecida» y cifras de registros.
- Roles inexistentes y enlaces a módulos que no existen.
