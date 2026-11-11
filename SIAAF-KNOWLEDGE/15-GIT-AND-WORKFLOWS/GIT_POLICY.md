---
system: SGT-SIAAF
type: workflow
status: active
source: user-directive 2026-11-11 (confirmada) + repository-history
last_updated: 2026-11-11
---

# Política Git

> **Confirmada por el responsable el 2026-11-11.** La versión operativa está en `CLAUDE.md` § "Flujo Git"; esta nota la detalla.

## Ramas

```
main  (principal)
 └── develop  (se deriva de main; integración)
      ├── feat/<funcionalidad>
      ├── fix/<corrección>
      └── docs/<tema> …   (una rama por tarea, siempre desde develop)
```

| Rama | Rol | Reglas |
|---|---|---|
| `main` | Principal | No se trabaja ni se hacen commits directos. Solo recibe merges `--no-ff` desde `develop`, **y solo tras preguntar al responsable y recibir su confirmación explícita** |
| `develop` | Integración | Se deriva de `main`. Recibe las ramas de trabajo con `--no-ff`. Tras cada fusión en `main`, se alinea con `git merge --ff-only main` |
| Ramas de trabajo | Una por tarea o funcionalidad | Parten de `develop` actualizada: `feat/`, `fix/`, `docs/`, `refactor/`, `security/`, `test/`, `build/`, `ci/` |

Remoto: `origin` → `git@github.com:R0yalCode/sistema-titulacion-unl.git`.

## Ciclo completo

1. `git switch develop && git pull --ff-only origin develop && git switch -c <tipo>/<descripcion>`
2. Commits en la rama (formato abajo) → `git push -u origin <rama>`
3. `git switch develop && git merge --no-ff <rama> -F <mensaje>` → `git push origin develop` → borrar la rama (local y remota) una vez integrada.
4. **Preguntar:** "¿Quieres fusionar `develop` con `main`?"
5. Solo con un "sí" explícito: `main` ← `git merge --no-ff develop -F <mensaje>` → `git push origin main` → en `develop`: `git merge --ff-only main` → `git push origin develop`.

Si el árbol de trabajo tiene cambios locales ajenos, se puede fusionar en `main` desde un `git worktree` temporal para no tocarlos.

## Mensajes (mismo modelo que el historial)

**Commit de rama de trabajo:**

```
tipo(ámbito): descripción breve en imperativo

Párrafo de contexto: qué problema resuelve.

Cambios realizados:
- módulo/archivo: qué cambió y por qué.

Validación:
- comando ejecutado → resultado real.

Pendientes / limitaciones (si los hay).
```

**Autoría:** los commits y merges figuran **solo a nombre del responsable** (usuario Git configurado). No se añaden líneas `Co-Authored-By`, menciones a Claude/IA ni firmas de herramientas (DK-009, 2026-11-11). Los commits anteriores a esa fecha conservan su línea `Co-Authored-By` en el historial publicado.

**Merge en `develop`:** `Merge branch '<rama>' into develop` + descripción de lo integrado y cómo se validó.

**Merge en `main`:** título `release(<hito>): <resumen>` para una entrega versionada (COSMOS) o `Merge develop into main: <resumen>` en otro caso, más una descripción con: cambios integrados (agrupados), validaciones, cambios que **no** incluye y pendientes.

Tipos: `feat`, `fix`, `refactor`, `docs`, `test`, `build`, `ci`, `chore`, `perf`, `release`.

## Reglas

- Nunca `git add .`: rutas explícitas; no incluir cambios locales ajenos.
- Nada de `--force`, reescribir historial publicado, desactivar protecciones ni resolver conflictos de forma destructiva.
- Pull Request cuando haya herramienta (`gh` **no está instalada** en esta máquina; hoy los merges son locales con `--no-ff`).
- Tags y releases: solo entregas funcionales validadas ([[COSMOS_VERSIONING]]).

## Historial de la política

- Antes: `AGENTS.md`, `CLAUDE.md` y DEC-08 (spec 003) decían "sin Git".
- 2026-11-11: DK-003 (Git solo con autorización) → **confirmada y ampliada** con este flujo `main` → `develop` → ramas, con la pregunta obligatoria antes de tocar `main` (DK-008).
- Práctica histórica: ramas `release/0.2.0-andromeda`, `release/0.3.0-andromeda` y `release/0.4.0-eclipse` fusionadas en `main` (PR #14, #16); no hay tags.

## Relacionado

[[COSMOS_VERSIONING]] · [[CLAUDE_CODE_OPENCODE_GUIDE]] · [[KNOWLEDGE_MAINTENANCE]] · [[DECISIONS_LOG]]
