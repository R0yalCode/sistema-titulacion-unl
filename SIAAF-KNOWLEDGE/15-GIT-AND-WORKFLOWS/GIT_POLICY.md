---
system: SGT-SIAAF
type: workflow
status: active
source: user-directive 2026-11-11 + repository-history
last_updated: 2026-11-11
---

# Política Git

## Ramas

| Rama | Rol | Reglas |
|---|---|---|
| `main` | Protegida | **Nunca** trabajar, hacer commit ni fusionar hacia `main` desde un agente; nunca usarla como origen de ramas de trabajo |
| `develop` | Integración | Todas las ramas de trabajo parten de `develop` actualizada (`git pull --ff-only origin develop`) y se integran en ella |
| Ramas de trabajo | — | `docs/…`, `feat/…`, `fix/…`, `refactor/…`, `security/…`, `test/…`, `build/…`, `ci/…` |

Remoto: `origin` → `git@github.com:R0yalCode/sistema-titulacion-unl.git`.

## Commits (Conventional Commits)

Formato `tipo(ámbito): descripción breve`. Tipos: `feat`, `fix`, `refactor`, `docs`, `test`, `build`, `ci`, `chore`, `perf`. Cuerpo técnico con cambios, validaciones **realmente ejecutadas** y limitaciones.
- Nunca `git add .`: agrega rutas explícitas.
- No incluyas cambios locales ajenos a la tarea (el árbol suele tener trabajo sin confirmar del equipo).
- Nada de `--force`, ni desactivar protecciones, ni resolver conflictos con operaciones destructivas.

## Integración

Por **Pull Request hacia `develop`** cuando la herramienta lo permita (la CLI `gh` **no está instalada** en esta máquina: el PR se crea desde la web de GitHub). Si `develop` no está protegida, se admite un merge local `--no-ff` y push, solo con autorización expresa.

## Autorización de agentes (DK-003)

`AGENTS.md` §3.8, `CLAUDE.md` y DEC-08 (spec 003) decían "sin Git". Política vigente: **los agentes solo hacen commit, push o merge con autorización humana explícita para esa tarea**. Sin autorización, dejan los cambios en el árbol de trabajo y los describen.

## Práctica histórica observada

- Ramas `release/0.2.0-andromeda`, `release/0.3.0-andromeda` y `release/0.4.0-eclipse` se fusionaron **directamente en `main`** (y PR #16). Tras la nueva política, eso no debe repetirse desde agentes.
- Mensajes `release(andromeda): …`, `feat(security): …`, `docs(rosetta): …`.
- **No existen tags** en el repositorio (ni locales ni remotos).

## Relacionado

[[COSMOS_VERSIONING]] · [[CLAUDE_CODE_OPENCODE_GUIDE]] · [[KNOWLEDGE_MAINTENANCE]]
