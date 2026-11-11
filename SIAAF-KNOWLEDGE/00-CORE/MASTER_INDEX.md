---
system: SGT-SIAAF
type: index
status: active
last_updated: 2026-11-11
---

# Mapa maestro: SIAAF-KNOWLEDGE

> **Cómo usar esta bóveda:** busca aquí el área de tu tarea, abre **solo** esa nota y sigue sus enlaces. No leas la bóveda entera. Arranque mínimo: [[SYSTEM]]. Estado vivo: [[CURRENT_STATE]].
> Leyenda: ✅ verificado contra código · 📐 propuesta/plan · ⚖️ normativa · 🔎 índice de fuentes.

## 00 · Núcleo
[[SYSTEM]] · [[PROJECT_OVERVIEW]] · [[CURRENT_STATE]] · [[GLOSSARY]] · [[DECISIONS_LOG]] · [[INITIAL_DIAGNOSTIC]] · [[BUILD_REPORT]]

## 01 · Arquitectura ✅
[[GENERAL_ARCHITECTURE]] · [[BACKEND_ARCHITECTURE]] (incluye la máquina de estados) · [[FRONTEND_ARCHITECTURE]] · [[DATABASE]] · [[API_CONTRACTS]] · Integraciones: [[FIRMA_EC]] 📐

## 02 · Backend ✅
[[02-BACKEND/MODULES|Módulos backend]] · [[PERMISSIONS_ROLES]]

## 03 · Frontend ✅
[[03-FRONTEND/MODULES|Módulos frontend]] · [[ROUTES]] · [[COMPONENTS]]

## 04 · Requisitos 🔎
[[SPECIFY]] (mapa de las specs 001/003, Constitución, CA-G-01) · [[TASKS]]

## 05 · Ejecución
[[BLOCKED_TASKS]] · [[REGRESSION_TESTS]]

## 06 · Auditorías
[[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] · [[06-AUDITS/BACKEND/BACKEND_AUDITS|Índice de auditorías técnicas]]

## 07 · Decisiones
[[ADR_INDEX]] · [[ADR-KB-001-fuentes-originales]]

## 08 · Operación
[[DOCKER]] (incluye despliegue y CI) · [[ENVIRONMENTS]]

## 09 · Bitácoras
[[SESSION_TEMPLATE]] · [[2026-11-11-construccion-siaaf-knowledge]]

## 10 · Referencias 🔎
[[DOCUMENTATION]] · [[EXTERNAL_RESOURCES]]
**Notas derivadas de Documentacion-parte-2** 📐: [[DP2-PLAN_MAESTRO]] · [[DP2-MATRIZ_BRECHAS]] · [[DP2-PLAN_INTEGRACION]] · [[DP2-ARQUITECTURA_DASHBOARDS]] · [[DP2-MATRIZ_INTEGRACION_KPIS]] · [[DP2-ESPECIFICACION_SERVICIOS_DASHBOARD]] · [[DP2-MATRIZ_ACCIONES_RAPIDAS]] · [[DP2-PLAN_SESIONES]] · [[DP2-DISENO_FUNCIONAL_MODALIDADES]] · [[DP2-MATRIZ_REGLAS_NEGOCIO_MODALIDADES]] · [[DP2-ESPECIFICACION_API_MODALIDADES]] · [[DP2-MATRIZ_KPIS_MODALIDADES]]

## 11 · Normativa ⚖️
[[INSTITUTIONAL_FRAMEWORK]] · [[ARTICLES_AND_PROVISIONS]] · [[REGULATORY_TRACEABILITY]]

## 12 · Procesos de titulación
[[DEGREE_PROCESS_OVERVIEW]] · [[STUDENT_RECORDS]] · [[REQUESTS_AND_APPLICATIONS]] · [[DOCUMENT_MANAGEMENT]] · [[ELECTRONIC_SIGNATURES]] · [[TUTORS_AND_COMMITTEES]] · [[DEFENSES_AND_GRADES]] · Modalidades 📐: [[CURRICULAR_INTEGRATION_WORK]] · [[COMPREHENSIVE_EXAMINATION]]

## 13 · Trazabilidad
[[GENERAL_TRACEABILITY_MATRIX]] · [[DOCUMENT_TRACEABILITY]] (22 contradicciones) · [[EVIDENCE_INDEX]]

## 14 · Métricas y dashboards 📐
[[KPI_CATALOG]] · [[DASHBOARD_ARCHITECTURE]]

## 15 · Git y flujos de trabajo
[[GIT_POLICY]] · [[COSMOS_VERSIONING]] · [[CLAUDE_CODE_OPENCODE_GUIDE]] · [[OBSIDIAN_MCP]] · [[KNOWLEDGE_MAINTENANCE]]

## 90 · Fuentes originales 🔎
[[SOURCE_CATALOG]] · Copias íntegras de DP2: [[90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/README|DOCUMENTATION-PART-2]]

---

### Por pregunta frecuente

| Pregunta | Nota |
|---|---|
| ¿Qué endpoint existe y quién puede usarlo? | [[API_CONTRACTS]], [[PERMISSIONS_ROLES]] |
| ¿En qué estado puede estar un expediente y quién lo cambia? | [[BACKEND_ARCHITECTURE]] |
| ¿Qué tarea toca ahora y qué está bloqueado? | [[TASKS]], [[BLOCKED_TASKS]] |
| ¿Qué dice la norma? | [[ARTICLES_AND_PROVISIONS]] |
| ¿Están implementadas las modalidades o los KPIs? | No: [[COMPREHENSIVE_EXAMINATION]], [[KPI_CATALOG]] |
| ¿Qué documento contradice a cuál? | [[DOCUMENT_TRACEABILITY]] |
