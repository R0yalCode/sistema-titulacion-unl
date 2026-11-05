---
title: "Anexos — Decisiones"
---

# Anexos — Decisiones documentales

Decisiones tomadas durante la elaboración de esta documentación (no modifican el producto).

| ID | Decisión | Justificación |
|---|---|---|
| DOC-01 | El contrato OpenAPI canónico sigue siendo `backend/openapi.yaml` (y su copia en `contracts/`); esta documentación lo **referencia** en lugar de duplicarlo | Evita desincronización; el archivo ya es válido y está verificado |
| DOC-02 | La documentación de endpoints se organiza por grupos de módulo en `04-api/endpoints/` | Navegabilidad; cada página documenta parámetros, cuerpos y respuestas reales |
| DOC-03 | Los KPI quedan como **propuesta** sin implementación | Restricción de la auditoría: no se autorizó código nuevo |
| DOC-04 | Se recomienda un único endpoint `GET /dashboard/me/` en lugar de 7 dashboards separados | Menor superficie, menos duplicación de fórmulas; decisión final pendiente |
| DOC-05 | Los diagramas C4 usan Mermaid (nativo de Quarto) | Sin dependencias adicionales |
| DOC-06 | Los procesos de propuesta/tutoría/sustentación/titulados se marcan explícitamente como fuera de Fase 1 | Honestidad documental: no existen en el modelo |
| DOC-07 | Las cifras de esta documentación (526 pruebas, 93 %, 17 endpoints) prevalecen sobre READMEs anteriores | Medición reproducible del 05-11-2026 |
| DOC-08 | No se corrigieron READMEs ni código durante la auditoría | Alcance de solo lectura; correcciones en el plan de mejora |
