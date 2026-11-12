---
system: SGT-SIAAF
type: workflow
status: active
source: user-directive 2026-11-11 (confirmada; DK-010 equipo y autoría) + repository-history
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

**Autoría:** según § "Equipo y autoría" (DK-010, que sustituye a DK-009): autor = integrante que implementó realmente el cambio; `Co-authored-by` solo para los demás integrantes que contribuyeron realmente. Nunca menciones a Claude/IA, coautoría de Claude ni firmas de herramientas.

**Merge en `develop`:** `Merge branch '<rama>' into develop` + descripción de lo integrado y cómo se validó.

**Merge en `main`:** título `release(<hito>): <resumen>` para una entrega versionada (COSMOS) o `Merge develop into main: <resumen>` en otro caso, más una descripción con: cambios integrados (agrupados), validaciones, cambios que **no** incluye y pendientes.

Tipos: `feat`, `fix`, `refactor`, `docs`, `test`, `build`, `ci`, `chore`, `perf`, `release`.

## Reglas

- Nunca `git add .`: rutas explícitas; no incluir cambios locales ajenos.
- Nada de `--force`, reescribir historial publicado, desactivar protecciones ni resolver conflictos de forma destructiva.
- Pull Request cuando haya herramienta (`gh` **no está instalada** en esta máquina; hoy los merges son locales con `--no-ff`).
- Tags y releases: solo entregas funcionales validadas ([[COSMOS_VERSIONING]]).
- La prohibición de `--force` y de reescribir historial publicado es **absoluta**: tampoco se reescribe para añadir o corregir autores de forma retroactiva.

## Equipo y autoría

> Política permanente (DK-010, 2026-11-11). Complementa el flujo anterior; no anula ni debilita ninguna de sus restricciones. Versión operativa: `CLAUDE.md` § "Equipo, autoría y distribución del trabajo".

| GitHub | Correo | Rol |
|---|---|---|
| R0yalCode | royel.jima@unl.edu.ec | Responsable del repositorio |
| JuanCalopinoo | Juan.calopino@unl.edu.ec | Integrante |
| 7777-C | markgonzalez20062@gmail.com | Integrante |
| Dan1el17 | steeven.pardo@unl.edu.ec | Integrante |
| JJOC3S | jimmy.ontaneda@unl.edu.ec | Integrante |

Identidad de referencia: no se inventan nombres personales ni se alteran los correos.

**Reglas de autoría**

1. **Individual (modalidad ordinaria):** el autor del commit es el integrante que implementó realmente el cambio. En la modalidad centralizada, ver § "Modalidad de implementación centralizada".
2. **Compartida:** si varios integrantes contribuyeron realmente a la misma tarea, el autor es el responsable principal y cada uno de los demás va en un trailer al final del mensaje: `Co-authored-by: Identificador <correo>` (exactos de la tabla).
3. No se añade por defecto a los cinco integrantes, ni se atribuyen contribuciones no realizadas o tareas no asignadas.
4. Claude Code es una herramienta de asistencia: **nunca** figura como autor, committer ni coautor.
5. La identidad de un integrante (`--author`) solo se usa con su conocimiento y la autorización del responsable; sin modificar la configuración Git global ni local.
6. **Committer:** quien ejecuta el commit. Si un integrante lo hace desde su equipo, es autor y committer; si lo prepara el responsable en su máquina, el committer es el responsable y el autor, el integrante que hizo el trabajo (o, en la modalidad centralizada, el integrante responsable de la tarea).

**Antes de cada commit**

1. `git status` y diff completo de la tarea.
2. Identificar qué archivos o partes hizo cada integrante, con evidencia verificable (sus cambios, su rama, lo que declara el equipo).
3. Comprobar que no entren cambios ajenos a la tarea.
4. Verificar la identidad: `git config user.name` / `user.email`, `git var GIT_AUTHOR_IDENT` / `GIT_COMMITTER_IDENT`.
5. Fijar autor y coautores según contribuciones verificables. **Si no se pueden verificar, se pregunta antes de hacer el commit.**
6. Mensaje Conventional Commits descriptivo (modelo de § Mensajes).

Ejemplo con coautoría:

```
feat(verificacion): exponer observaciones al estudiante (E2-02a)

…cuerpo según § Mensajes…

Co-authored-by: Dan1el17 <steeven.pardo@unl.edu.ec>
```

## Distribución de tareas

Objetivo: que los cinco integrantes tengan oportunidades reales de contribuir y generar sus propios commits.

**Procedimiento por funcionalidad**

1. Claude analiza la funcionalidad pendiente y la divide en tareas técnicas concretas (componentes, servicios, endpoints, pruebas, documentación).
2. Propone un responsable para cada tarea según su alcance técnico, sus dependencias y las responsabilidades en curso, con una carga equilibrada entre los cinco.
3. **Rotación:** no asigna siempre la misma categoría de trabajo (p. ej. pruebas o documentación) a las mismas personas; las categorías rotan entre funcionalidades.
4. Evita que dos integrantes modifiquen los mismos archivos a la vez sin coordinación; si es inevitable, lo indica y propone el orden de integración.
5. Las asignaciones son **propuestas** hasta que el equipo las confirme. Una propuesta nunca se registra como trabajo realizado.
6. Modalidad ordinaria: cada integrante desarrolla y valida su parte antes de integrarla. Modalidad centralizada: Claude Code implementa y valida cada bloque (ver § siguiente).
7. Tras verificar lo realizado (§ Antes de cada commit), y con la autorización correspondiente, Claude prepara el commit individual con la identidad del integrante que lo implementó (ordinaria; coautores si hubo contribución compartida real) o del integrante responsable de la tarea (centralizada).
8. Se registra quién hizo cada parte: tarea, bitácora de sesión y autoría del commit.

**Plantilla de planificación**

| Tarea técnica | Responsable propuesto | Archivos / componentes | Resultado esperado | Pruebas y validaciones | Commit previsto (autor real · coautores) |
|---|---|---|---|---|---|
| T1 … | Integrante | rutas | criterio verificable | comandos y casos | `tipo(ámbito): …` · autor · — |

Estado de cada fila: *propuesta* → *confirmada por el equipo* → *realizada y verificada* → *commit preparado*.

## Modalidad de implementación centralizada

> Enmienda de **DK-010** (2026-11-11), autorizada expresamente por el responsable del proyecto. Versión operativa: `CLAUDE.md` § "Equipo, autoría y distribución del trabajo".

1. **Habilitación:** solo con autorización expresa del responsable para una funcionalidad concreta y su reparto de tareas aprobado. Sin ella rige la modalidad ordinaria.
2. **Ejecución:** Claude Code implementa los bloques técnicos asignados a los integrantes; no es obligatorio que cada integrante ejecute personalmente los cambios.
3. **Commits:** uno independiente por tarea del reparto, en el orden de dependencias, con `git commit --author="<Identificador> <correo>"` y **exclusivamente** las identidades de la tabla. Cada commit contiene solo los archivos de su bloque; no se atribuyen a un integrante cambios de otro bloque. Si un cambio no es separable por bloques, se detiene la ejecución y se consulta.
4. **Significado:** el autor Git identifica al **integrante responsable de la tarea** (contribución delegada), no a quien escribió materialmente el código. Ejecución material: Claude Code. Committer: identidad Git configurada en el equipo que ejecuta (hoy R0yalCode). Claude Code no figura como autor, committer ni coautor, ni se le nombra en commits, merges, PR o releases.
5. **Constancia:** el plan de la funcionalidad y la bitácora de sesión registran la ejecución centralizada por Claude Code, la autorización del responsable (fecha) y la tabla commit ↔ tarea ↔ integrante. Nunca se afirma que el integrante escribió personalmente el código. El cuerpo de cada commit incluye:

   ```
   Modalidad: implementación centralizada (DK-010, enmienda 2026-11-11) · Tarea <ID> · responsable <Identificador>
   ```

6. **Conocimiento:** cada integrante es informado de su tarea y de que su identidad se usará como autor Git de ese bloque.
7. **Sin efectos retroactivos:** solo trabajos futuros autorizados en esta modalidad. Permanecen: prohibición absoluta de `--force` y variantes; prohibición de reescribir historial publicado; sin push, merge ni rebase de ramas publicadas sin autorización expresa; prohibido modificar o eliminar commits históricos para adaptar sus autores.

## Historial de la política

- Antes: `AGENTS.md`, `CLAUDE.md` y DEC-08 (spec 003) decían "sin Git".
- 2026-11-11: DK-003 (Git solo con autorización) → **confirmada y ampliada** con este flujo `main` → `develop` → ramas, con la pregunta obligatoria antes de tocar `main` (DK-008).
- 2026-11-11: DK-009 (autoría solo del responsable, sin coautoría). Con autorización expresa del responsable se reescribió el historial publicado de `main` y `develop` (13 commits a partir de `fee9119`, `--force-with-lease`) para eliminar las líneas de coautoría anteriores; el contenido no cambió. Ver [[BUILD_REPORT]] § Reescritura del historial.
- 2026-11-11: con autorización expresa y puntual del responsable, el commit de E2-01 `2954a21` se rehízo como `c0d75b6` (autor y committer JuanCalopinoo, mismo árbol) y el merge de `develop` `a9e79ac` como `1a1093c`, con `--force-with-lease`; después se integró en `main` (`d1fa86e`).
- 2026-11-11: **DK-010** sustituye a DK-009: autoría individual y compartida para los cinco integrantes, distribución equilibrada de tareas y prohibición absoluta de reescribir historial, también para corregir autoría.
- 2026-11-11: **enmienda de DK-010** (autorizada por el responsable): modalidad de implementación centralizada por Claude Code con commits independientes por tarea y `--author` del integrante responsable (atribución delegada, documentada). No modifica las restricciones Git ni tiene efectos retroactivos.
- Práctica histórica: ramas `release/0.2.0-andromeda`, `release/0.3.0-andromeda` y `release/0.4.0-eclipse` fusionadas en `main` (PR #14, #16); no hay tags.

## Relacionado

[[COSMOS_VERSIONING]] · [[CLAUDE_CODE_OPENCODE_GUIDE]] · [[KNOWLEDGE_MAINTENANCE]] · [[DECISIONS_LOG]]
