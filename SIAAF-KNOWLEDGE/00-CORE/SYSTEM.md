---
system: SGT-SIAAF
type: bootstrap
status: active
last_updated: 2026-11-11
---

# SYSTEM: contexto mínimo para agentes

> Nota de arranque diseñada para caber en contextos pequeños (p. ej., OpenCode con 8K). Si solo puedes leer una nota, lee esta.

- **Qué es:** SGT-SIAAF, sistema web del trámite de titulación (fase administrativa) de la Carrera de Computación, FEIRNNR, Universidad Nacional de Loja. **Simulación académica**: datos ficticios, sin acceso real al SGA/SIAAF.
- **Stack:** backend Django 5.2 + DRF + PostgreSQL 16 (monolito modular hexagonal); frontend React 19 + TS + Vite + TanStack Query.
- **Hecho:** Fase 1 (aptitud legal, Art. 235) en el backend: 17 operaciones API; frontend V-01…V-04 y UI Kit.
- **No existe:** modalidades TIC/EC, app `indicadores`/dashboards, refresh/logout, búsqueda/exportación, FirmaEC real, Fase 2/3.
- **Brechas críticas:** sin transición `ENVIADA→EN_VERIFICACION` (GAP-STATE-01); `RESPONSABLE_DEPENDENCIA` sin RBAC; throttling de mutantes ausente.
- **Prohibido:** inventar endpoints, campos o estados; simular datos (CA-G-01); tocar el backend desde tareas frontend; agregar dependencias sin autorización; Git sin autorización expresa.
- **Verdad:** el código manda sobre la documentación para el estado de implementación.
- **Siguiente lectura:** [[MASTER_INDEX]] → [[CURRENT_STATE]] → nota del módulo.
