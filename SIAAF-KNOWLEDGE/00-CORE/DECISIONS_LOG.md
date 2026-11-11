---
system: SGT-SIAAF
type: decision-log
status: active
source: knowledge-build-session
last_updated: 2026-11-11
---

# Registro de decisiones

Decisiones de **gestión del conocimiento y del flujo de trabajo** (prefijo `DK-`). Las decisiones de arquitectura del sistema están en [[ADR_INDEX]]. Añade las nuevas al final, con fecha, fuente y si requieren validación humana.

| ID | Fecha | Decisión | Motivo | Validación humana |
|---|---|---|---|---|
| DK-001 | 2026-11-11 | Reutilizar `<repo>/SIAAF-KNOWLEDGE/` como única bóveda oficial; no crear otra ni tocar las bóvedas externas en la papelera | Las externas estaban vacías (solo `.obsidian/`) y el usuario ya las había movido a la papelera; Obsidian ya tiene abierta la interna | No requerida |
| DK-002 | 2026-11-11 | Copia íntegra solo de `Documentacion-parte-2/`; resto referenciado por ruta | [[ADR-KB-001-fuentes-originales]] | No requerida |
| DK-003 | 2026-11-11 | La política "sin Git" de `AGENTS.md` §3.8 / `CLAUDE.md` máxima 4 / DEC-08 (spec 003) queda **matizada**: los agentes solo hacen commit, push o merge con **autorización humana explícita para esa tarea** y siguiendo [[GIT_POLICY]] | El repo sí usa Git (ramas `release/*`, PR #9…#21); en esta sesión el usuario autorizó expresamente el ciclo Git completo | **Confirmada** por el responsable el 2026-11-11 (ampliada en DK-008) |
| DK-004 | 2026-11-11 | El **código** es la fuente de verdad del estado de implementación; la normativa y las specs, de los requisitos. Cuando chocan, se registra la contradicción, sin resolverla | Mandato de la construcción; evita declarar implementado lo planificado | No requerida |
| DK-005 | 2026-11-11 | No se crea versión COSMOS, tag ni release por la construcción de la bóveda | Es documentación, no una entrega funcional ([[COSMOS_VERSIONING]]) | No requerida |
| DK-006 | 2026-11-11 | `.obsidian/`: se versionan `app.json`, `appearance.json`, `core-plugins.json` y `community-plugins.json`; se ignoran `workspace*.json`, `plugins/` y la caché | Los primeros son configuración compartible; los segundos son estado local y código de terceros | No requerida |
| DK-007 | 2026-11-11 | Se registran como brechas, **sin corregirlas**: GAP-STATE-01 (no hay transición `ENVIADA→EN_VERIFICACION`), falta de `CANCELADA` operativa y RBAC vacío de `RESPONSABLE_DEPENDENCIA` | Tarea solo documental; cambiar el backend requiere autorización | **Sí**: decidir si se abren tareas backend |
| DK-008 | 2026-11-11 | Flujo Git oficial: `main` (principal) → `develop` (derivada de `main`) → ramas de trabajo desde `develop`; merge `--no-ff` en `develop`; **merge `develop`→`main` solo tras preguntar al responsable y recibir confirmación explícita**, con título y descripción profesionales; después se alinea `develop` con `main` | Instrucción directa del responsable; consolidada en `CLAUDE.md` § Flujo Git y [[GIT_POLICY]] | Confirmada |
