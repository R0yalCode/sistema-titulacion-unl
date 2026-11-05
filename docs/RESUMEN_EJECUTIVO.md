---
title: "Resumen ejecutivo"
---

# RESUMEN EJECUTIVO — Auditoría y documentación SGT-SIAAF

| Campo | Valor |
|---|---|
| Fecha | 05-11-2026 |
| Informes derivados | `auditoria/INFORME_AUDITORIA_TECNICA.md`, `indicadores/INFORME_DISENO_KPI.md`, `auditoria/PLAN_MEJORA_TECNICA.md`, `auditoria/matriz-trazabilidad.md` |

## 1. Estado real del backend

**MVP funcional y verificado.** El flujo completo del trámite (crear → enviar → verificar/observar → subsanar → informe → declaratoria) está implementado en una arquitectura hexagonal real (no solo documentada), con RBAC de mundo cerrado, protección IDOR verificada, almacenamiento privado de PDFs con validación criptográfica y bitácora de auditoría JSONB.

## 2. Porcentaje de funcionalidades verificadas

**56 % (18 de 32) implementadas y verificadas con ejecución real; 9 % parcial; 28 % no implementado; 6 % por diseño.**

*Método de cálculo*: matriz de 32 funcionalidades (§10 del informe de auditoría); una funcionalidad es "verificada" solo si existe evidencia de ejecución (pruebas corridas en esta auditoría o regeneración/verificación directa del artefacto). El 100 % de las funcionalidades **del alcance de Fase 1 backend** está verificado; los NI corresponden a frontend (vistas) y a fases futuras del trámite.

## 3. Resultados de las pruebas (reproducibles)

| Suite | Resultado |
|---|---|
| Backend configurada | 473 passed / 0 failed |
| Backend extendida (core + e2e) | 53 passed |
| **Total backend** | **526 passed / 0 failed** |
| Cobertura backend | **93 %** |
| Frontend | 198 passed / 0 failed (43 archivos) |
| Lint/typecheck/build (frontend) | Sin errores / exitoso |
| Migraciones | Sin pendientes |
| OpenAPI regenerado | Idéntico al contrato versionado |

## 4. Hallazgos críticos

1. **P0**: despliegue Docker en modo desarrollo (`DEBUG=1`, `runserver`, sin `production.py`).
2. **P0**: sin throttling/rate limiting (login expuesto a fuerza bruta).
3. **P1**: endpoints de documentación OpenAPI con `AllowAny`; sin backups; suite por defecto omite 53 pruebas (core/e2e).
4. **P2 confirmado**: bug de trazabilidad N-1 (`estado_anterior` incorrecto en el informe), prints de depuración en producción, IP de auditoría siempre vacía.
5. Revalidación del sprint S1: SEC-01 y SEC-03 **corregidos**; SEC-02 parcialmente; R5 (producción) abierta.

## 5–9. Cifras de la entrega

| Métrica | Valor |
|---|---|
| Módulos documentados | 7 (6 apps + core) |
| Endpoints inventariados y documentados | 17 operaciones (+ 3 de documentación); 100 % cubiertos por el contrato OpenAPI |
| KPI propuestos | 40 |
| KPI implementables con datos existentes | 33 |
| KPI que requieren información adicional | 7 (tutoría, sustentaciones, modalidad, períodos, abandono, usuarios activos, nombres de carrera) |

## 10–12. Estado de los entregables técnicos

| Entregable | Estado |
|---|---|
| **OpenAPI** | Válido, sincronizado con el código (regeneración idéntica), servido en Swagger/Redoc; 2 mejoras menores pendientes (securityScheme, login sin security) |
| **Quarto** | Sitio configurado (`docs/_quarto.yml`) con navegación completa, tema cosmo, buscador, numeración y Mermaid; se construye con `quarto render` |
| **Diagramas C4** | 4 niveles (contexto, contenedores, componentes, código) en Mermaid, fieles al código (integraciones simuladas marcadas como tales) |

## 13. Recomendación de demostración

**El sistema SÍ está preparado para una demostración funcional vía API**: flujo completo de extremo a extremo con datos de prueba (`seed_initial_data`), Swagger UI incluido y E2E automatizado que lo recorre.

**No está preparado para una demostración de producto con interfaz de usuario**: las 9 vistas del frontend son stubs (aunque el andamiaje —router, auth, design system, 198 pruebas— está completo y probado).

**Recomendación**: para una demo inmediata, usar `/api/v1/docs/` recorriendo FL-01→FL-05 con los usuarios demo. Para una demo de producto, completar primero V-01, V-07 y V-02 del plan FE (tareas ya especificadas en `specs/003`). Antes de cualquier exposición pública del despliegue, resolver los P0 (MEJ-P0-01, MEJ-P0-02).
