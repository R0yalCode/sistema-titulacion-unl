---
system: SGT-SIAAF
type: session-log
date: 2026-11-26
agent: claude-code
branch: develop (merges 925a962, b1f4f10); documentación en test/ax-f-integracion-regresion
commits: [8caa4b4, 62240de, 925a962, b1f4f10]
---

# Sesión 2026-11-26: fase AX, accesibilidad global y control superior del sidebar

## Objetivo y autorizaciones (R0yalCode, 2026-11-26)

- Fase AX con reparto DK-010 en **modalidad centralizada** para AX-A…AX-F. Inicialmente se indicó «ordinaria» y el responsable lo corrigió. Plan y correspondencia: `docs/frontend/PLAN_ACCESIBILIDAD_ASISTENTE_DK010.md`.
- Integración en `develop` **rama por rama** con autorización expresa. Se autorizó AX-A y AX-B, en ese orden, con verificación del CI entre ambas.
- **Perfil sin backend nuevo:**
  - estudiante: `perfil-academico`, con `mi-tramite` como respaldo, sin partir nombres;
  - funcionarios: el rol;
  - sin fecha de último acceso ni estado de cuenta;
  - «Cambiar contraseña» lleva a `/recuperar-contrasena`.
- **Mascota de error provisional** para el asistente, registrando la decisión.
- **Preguntas frecuentes** solo sobre el uso del sistema.
- **AX-E:** solo diseño.
- **Limpieza de ramas:** se conservan solo `main` y `develop` como permanentes, además de las tareas pendientes.

## Trabajo realizado

| Paso | Resultado |
|---|---|
| AX-A (`8caa4b4`, autor JuanCalopinoo) | Panel y botón flotante de accesibilidad, proveedor global, `styles/a11y.css`, tokens de la capa flotante; 27 pruebas nuevas |
| AX-B (`62240de`, autor R0yalCode) | `BotonContraerMenu` junto al logo con tooltip en portal; 6 pruebas nuevas |
| Merge AX-A → `develop` | `925a962`: CI (frontend 627/627, backend 1263 + 26 omitidas, PostgreSQL 51, OpenAPI) y Security correctos |
| Merge AX-B → `develop` | `b1f4f10`: combinación verificada antes del push (633/633 ×3); CI (frontend 633/633, backend 1263, PostgreSQL 51) y Security correctos |
| nginx `:8000` | Imagen reconstruida desde el worktree `develop` (`docker build --target web`); solo se recreó `nginx` (`--no-deps --no-build`). El backend quedó intacto: mismo contenedor y arranque, por el riesgo de los 36 PDF. Respaldo: `sgt-siaaf-nginx:pre-accesibilidad` |
| Capturas automatizadas | 9 PNG en `~/Documentos/sgt-siaaf-capturas-ax-a-b/`: landing y login reales en `:8000`, y vistas autenticadas con el arnés de fixtures. Chrome headless sin interacción; **no es una inspección manual** |

### Limpieza de ramas (DK-013)

- **Condiciones:** 0 commits exclusivos frente a `origin/develop`, sin cambios pendientes y CI posterior a la integración correcto. Los arneses de las carpetas ignoradas se copiaron antes a `~/Respaldos/…/arnes-visual/`.
- **Worktrees quitados (sin `--force`):** `ax-a`, `ax-b`, `errores`, `liquid-glass`, `integracion-admin`, `fix-notificaciones`, `rescate`.
- **Ramas locales eliminadas (`git branch -d`):** `feat/ax-a-accesibilidad-global`, `feat/ax-b-sidebar-control-superior`, `feat/siaaf-error-pages-liquid-glass`, `feat/redesign-liquid-glass-dashboards`, `feat/integracion-rediseno-admin`, `fix/notificaciones-ambito-500`, `docs/rescate-arbol-principal` y `build/reorganizacion-estructural`.
- **Ramas remotas eliminadas:** las cinco que existían en origin, tras comprobar que eran ancestros de `origin/develop`.
- **Comprobación:** los 8 commits finales siguen siendo accesibles desde `origin/develop`.
- **Conservadas:**
  - `main` y `develop` (en remoto solo quedan estas dos);
  - `feat/dashboard-estudiante` (carpeta principal, con 255 cambios y archivos locales `.env` y `media`);
  - AX-C, AX-D y AX-F con sus worktrees;
  - el worktree `sgt-siaaf-integracion-develop`, el stash del 2026-11-23 y `refs/respaldo/rescate-fase0-2026-11-26_162654`.

## Revisión manual del responsable

- **AX-A y AX-B aceptadas**, salvo «Leer página»: no reproduce voz en su navegador.
- Registrada como **INC-23** (`clarify.md`, [[BLOCKED_TASKS]]).
- Las pruebas automatizadas de lectura usan un `speechSynthesis` simulado. La reproducción real no se ha validado con éxito.
- **AX-A no se cierra del todo.**
- No hay cambios de código hasta una tarea específica.
- **INC-24:** solapamiento del botón con el pie del login en ≤480 px, detectado en las capturas automatizadas.

## Pendientes

1. INC-23 (tarea específica de investigación y corrección).
2. INC-24 y la observación AX-01 (hueco con el sidebar contraído).
3. AX-C y AX-D: preparadas. Ramas actualizadas a `b1f4f10` por avance rápido, sin commits previos. El plan de ejecución está pendiente de aprobación.
4. AX-E (diseño) y AX-F (regresión final).
5. Fusionar en `develop` la rama de AX-F que contiene esta bitácora (requiere autorización).
