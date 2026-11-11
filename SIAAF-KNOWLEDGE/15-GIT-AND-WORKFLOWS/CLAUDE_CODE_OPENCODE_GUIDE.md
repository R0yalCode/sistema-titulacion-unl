---
system: SGT-SIAAF
type: workflow
status: active
source: knowledge-build-session
last_updated: 2026-11-11
---

# Guía para Claude Code y OpenCode

Ambos agentes usan **la misma bóveda** (`SIAAF-KNOWLEDGE/`) y las mismas reglas. Punto de entrada: `CLAUDE.md` (Claude Code) y `AGENTS.md` (OpenCode y otros agentes), en la raíz.

## Orden de consulta (recuperación progresiva)

1. `CLAUDE.md` / `AGENTS.md` (siempre en contexto).
2. [[MASTER_INDEX]]: localizar el área.
3. [[CURRENT_STATE]]: solo el contexto general (fase, bloqueos).
4. La nota específica del módulo o proceso (p. ej. [[02-BACKEND/MODULES|Módulos backend]], [[STUDENT_RECORDS]]).
5. Solo si hace falta: requisitos ([[SPECIFY]]), decisiones ([[ADR_INDEX]]), auditorías y trazabilidad.
6. Solo si hace falta: la **sección** concreta del documento original (ruta en [[SOURCE_CATALOG]]).
7. **Siempre** verificar el código real antes de implementar o de afirmar que algo existe.

No vuelvas a leer lo que ya está en contexto y no ha cambiado.

## Reglas de eficiencia

- No leer la bóveda ni el repo enteros; no cargar módulos ajenos a la tarea.
- Con MCP: `search_notes` → `read_note(metadataOnly)` → `read_note(heading)`.
- Sin MCP: `grep -rn "<término>" SIAAF-KNOWLEDGE/` y leer por rango de líneas.
- Specs grandes (`tasks.md` 124 KB, `specify.md` 60–69 KB): leer **por sección o ID** (`grep -n "FE-T501"`).

## Reglas de verdad

- Estado de implementación = **código + pruebas ejecutadas** (DK-004).
- Requisitos = normativa y specs; si chocan con el código, **registrar** la contradicción.
- Distinguir: implementado y verificado · parcial · documentado sin implementar · propuesta · pendiente · no verificado.

## OpenCode

Configuración global en `~/.config/opencode/opencode.json` (proveedor Ollama local, modelos de 8K de contexto). **Con 8K de contexto**, la recuperación selectiva es obligatoria: leer solo [[SYSTEM]] y la nota del módulo. OpenCode no tiene configurado el MCP de Obsidian (la configuración no lo declara): usa la lectura directa de Markdown. No se modificó su configuración.

## Cierre de tarea

Procedimiento en [[KNOWLEDGE_MAINTENANCE]].
