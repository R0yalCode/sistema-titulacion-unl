---
system: SGT-SIAAF
type: adr
id: ADR-KB-001
status: accepted
date: 2026-11-11
source: knowledge-build-session
---

# ADR-KB-001 — Copiar solo Documentacion-parte-2; referenciar el resto por ruta

## Contexto

La bóveda debe dar acceso a las fuentes originales desde Obsidian sin crear dos versiones activas y contradictorias. El repositorio tiene unos 230 documentos fuente (≈ 2,5 MB de Markdown), y algunos son **documentos vivos** que se editan en cada tarea (`specs/003/tasks.md`, `clarify.md`). Obsidian no puede abrir con `[[wikilinks]]` archivos que están fuera de la bóveda.

## Decisión

1. **Copiar íntegros**, con verificación SHA-256, los 12 Markdown de `Documentacion-parte-2/` en `90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/`. Son documentos cerrados (versión 1.0, 2026-11-09), prioritarios y explícitamente pedidos.
2. **No copiar** el resto: specs, `docs/`, `DOCUMENTACION/`, `auditoria/`, `diseno-ui/`. Se **referencian por ruta relativa al repositorio** desde [[SOURCE_CATALOG]] y desde las notas derivadas.
3. La copia **no sustituye** al original: la ruta canónica sigue siendo `Documentacion-parte-2/`. Si el original cambia, la copia se actualiza y se registra el nuevo hash.

## Consecuencias

- **+** Sin divergencia en documentos vivos; repo más liviano; fuentes DP2 navegables en Obsidian.
- **−** ~260 KB duplicados en Git; hay que vigilar la deriva entre `Documentacion-parte-2/` y su copia (comprobación con `sha256sum -c`, ver [[KNOWLEDGE_MAINTENANCE]]).
- **−** Las fuentes no copiadas se abren desde el editor o el sistema de archivos, no desde Obsidian.

## Alternativas descartadas

- **Enlaces simbólicos**: Obsidian Flatpak y Git en otras plataformas los tratan de forma inconsistente.
- **Mover la bóveda a la raíz del repositorio**: mezclaría código y notas y rompería la ubicación pedida (`SIAAF-KNOWLEDGE/`).
- **Copiar todo**: crearía copias divergentes de documentos vivos.
