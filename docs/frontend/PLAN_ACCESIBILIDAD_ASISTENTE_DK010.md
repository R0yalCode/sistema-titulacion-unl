# Reparto DK-010: accesibilidad global, navegación, perfil y asistente institucional (fase AX)

> **Estado (2026-11-26):** AX-A y AX-B integradas en `develop` y aceptadas en la revisión funcional del responsable, con la incidencia **INC-23** abierta (la lectura en voz alta no se reproduce). AX-C y AX-D están en preparación. AX-E es solo diseño. AX-F incluye este documento.
>
> **Modalidad:** centralizada (DK-010, enmiendas 2026-11-11 y 2026-11-12), autorizada expresamente por R0yalCode para esta fase el 2026-11-26, para todas las tareas AX-A…AX-F.
> La ejecución material es de Claude Code. El autor Git identifica al integrante responsable de la tarea, no a quien escribió el código; nunca se afirma que el integrante lo desarrolló personalmente.
> Committer de todos los bloques: R0yalCode.
> Línea de cada commit: `Modalidad: implementación centralizada (DK-010, enmienda 2026-11-11) · Tarea <ID> · responsable <Identificador>`.
>
> **Integración:** rama por rama, cada una con autorización expresa del responsable. No hay autorización global. `main` no se toca.

Origen de los criterios: DK-010 es la política de autoría y reparto, no una especificación funcional. Los requisitos de esta fase son los que el responsable describió el 2026-11-26 (accesibilidad, sidebar, menú de perfil, asistente con RAG local), además de RFF-011 y RNFF-001 de `specify.md` (WCAG 2.1 AA, axe sin errores críticos).

## Reparto (rotación respecto de LG y ER)

| Tarea | Responsable | En LG / ER | Rama |
|---|---|---|---|
| AX-A Accesibilidad global | JuanCalopinoo | Panel del estudiante / recuperación en vistas | `feat/ax-a-accesibilidad-global` (integrada y eliminada) |
| AX-B Control superior del sidebar | R0yalCode | Paneles y documentación / integración | `feat/ax-b-sidebar-control-superior` (integrada y eliminada) |
| AX-C Menú desplegable de perfil | Dan1el17 | Shell / arquitectura base | `feat/ax-c-menu-perfil` |
| AX-D Interfaz del asistente | JJOC3S | Componentes / router y autenticación | `feat/ax-d-asistente-ui` |
| AX-E Diseño técnico RAG (sin implementación) | R0yalCode | — | se crea al iniciarla |
| AX-F Integración, regresión y documentación | 7777-C | Tokens / diseño visual | `test/ax-f-integracion-regresion` |

## Correspondencia tarea ↔ responsable ↔ commit

| Tarea | Responsable | Commit | Merge en `develop` | CI y Security del merge |
|---|---|---|---|---|
| AX-A | JuanCalopinoo | `8caa4b4` | `925a962` | correctos (frontend 627/627, backend 1263 + 26 omitidas, PostgreSQL 51, OpenAPI; safety, bandit y gitleaks) |
| AX-B | R0yalCode | `62240de` | `b1f4f10` | correctos (frontend 633/633, backend 1263 + 26 omitidas, PostgreSQL 51, OpenAPI; safety, bandit y gitleaks) |
| AX-F (documentación de la revisión) | 7777-C | commit que contiene este documento | pendiente de autorización | — |

## Revisión funcional del responsable (2026-11-26)

R0yalCode revisó AX-A y AX-B en su entorno local (`http://localhost:8000`; imagen nginx reconstruida desde `develop` `b1f4f10`; respaldo de la anterior `sgt-siaaf-nginx:pre-accesibilidad`).

- **Aceptado:** todas las herramientas de AX-A (tamaño de texto, modos de color, enlaces subrayados, fuente legible, velocidad de lectura, detener y restablecer; panel, teclado, cierre y persistencia) y todo AX-B (control junto al logo, tooltip, estados expandido y contraído, persistencia y navegación).
- **No aceptado:** «Leer página» no reproduce el contenido en su navegador → **INC-23, abierta**. La lectura en voz alta **no se considera funcional** y AX-A **no está cerrada del todo**.

## Incidencias y observaciones abiertas

| ID | Tarea | Descripción | Estado |
|---|---|---|---|
| **INC-23** | AX-A | «Leer página» no produce voz en el navegador del responsable. Las 27 pruebas de AX-A validan la lectura con un `speechSynthesis` **simulado**, porque jsdom no lo implementa, y las capturas automatizadas no pueden reproducir audio: la reproducción real **nunca se validó con éxito**. | Abierta. Sin cambios de código hasta una tarea específica. |
| **INC-24** | AX-A | En ≤480 px el botón de accesibilidad tapa el inicio del pie del login. La reserva de espacio (`#main-content::after`) no se aplica a las vistas públicas, que no usan ese contenedor. Detectado en las capturas automatizadas. | Abierta, para AX-F o una corrección de AX-A. |
| Obs. AX-01 | AX-A/AX-B | Con el sidebar contraído en escritorio, el botón y el panel de accesibilidad se colocan según el ancho expandido (unos 190 px de hueco). No tapan nada. | Observación menor para AX-F. |

**Hipótesis de INC-23, sin verificar** (las debe comprobar la tarea específica):

1. El navegador o el sistema no tienen voces instaladas (`speechSynthesis.getVoices()` vacío). En Chrome para Linux, la síntesis depende de `speech-dispatcher`.
2. `getVoices()` se carga de forma asíncrona (`voiceschanged`) y la primera llamada devuelve una lista vacía.
3. Llamar a `speak()` justo después de `cancel()` descarta la cola en algunas versiones de Chrome.
4. Fragmentación o idioma (`lang`) que el motor no admite.

## Dependencias e integración

`AX-A ∥ AX-B → AX-C → AX-D → AX-F`. AX-E es independiente.

- **AX-C** modifica `AppShell.tsx` (zona del perfil y pie del sidebar). Empieza después de que AX-B esté en `develop` (cumplido: base `b1f4f10`).
- **AX-D** se monta en `app/App.tsx`. Empieza después de AX-A (cumplido).
- Antes de cada tarea, la rama integra `develop` (avance rápido, sin pérdida de commits).

## Verificación usada en cada bloque

`npm run lint`, `npm run typecheck`, `npm run build` y `npm run test` (×3, por la intermitencia conocida de las pruebas de rutas). Capturas automatizadas con Chrome headless y el arnés de fixtures no versionado (respaldo en `~/Respaldos/sgt-siaaf/2026-11-26_162654-rescate-fase0/arnes-visual/`). Las capturas **no** equivalen a una inspección manual.
