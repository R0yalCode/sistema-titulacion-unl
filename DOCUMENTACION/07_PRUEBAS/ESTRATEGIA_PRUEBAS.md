---
title: "Estrategia de pruebas"
---

# Estrategia de pruebas — SGT-SIAAF

**Fuentes:** `backend/pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.coverage.run]`), `frontend/vitest.config.ts`, RNF-012 (`specify.md`), ejecución real documentada en `RESULTADOS_VALIDACION.md`.

## 1. Niveles de prueba existentes

| Nivel | Backend | Frontend |
|---|---|---|
| Unitaria (dominio/servicios puros) | Sí — `PlazoLaboralCalculator`, validación PDF, cada servicio de aplicación con sus excepciones de dominio | Sí — componentes de UI, hooks |
| Integración (DB + ORM + vistas) | Sí — `pytest-django`, base de datos SQLite en memoria por test | Sí — MSW (Mock Service Worker) para simular la API |
| Contrato/E2E interno | Parcial — pruebas de flujo completo mencionadas en `docs/RESUMEN_EJECUTIVO.md` ("E2E automatizado que recorre FL-01→FL-05"), no verificadas línea por línea en esta auditoría | Pruebas de enrutamiento (`router.test.tsx`) que ejercitan el árbol de rutas completo con guards reales |
| Seguridad (RBAC, IDOR) | Sí — suite dedicada citada en `DOCUMENTACION/06_SEGURIDAD/AUTORIZACION_PERMISOS.md` §6 | No aplica al frontend en el mismo sentido |
| Estático (lint/tipos) | `flake8`, `mypy` | `eslint`, `tsc` |

## 2. Motor y configuración

- **Backend**: `pytest` + `pytest-django` + `pytest-cov`. Base de datos de prueba: SQLite en memoria (`config.settings.test`), no PostgreSQL — decisión que prioriza velocidad de ejecución sobre fidelidad total al motor de producción (diferencias de comportamiento SQL entre SQLite y PostgreSQL, p. ej. en JSONB, no se ejercitan en pruebas).
- **Frontend**: Vitest + Testing Library + MSW. Entorno `jsdom`.

## 3. Alcance por defecto vs. alcance completo (backend)

`testpaths = ["src/apps"]` en `pyproject.toml` significa que el comando `pytest` sin argumentos **excluye** `src/core` (76 pruebas, verificado en Fase 7). Esta es una configuración del propio proyecto, no un hallazgo de esta auditoría — pero tiene una consecuencia práctica real: cualquier verificación de CI o local que solo ejecute `pytest` a secas subestima la cobertura real de pruebas en ~13 % (76 de 573).

## 4. Meta de cobertura

RNF-012 exige >70 % de cobertura de "modelos, vistas API, permisos RBAC y motor de estados". Verificado en Fase 7: **90 %** de cobertura de código fuente (excluyendo archivos de prueba), **96 %** según la configuración exacta del proyecto (que no excluye los tests de la medición). Ambas cifras cumplen la meta con margen amplio.

## 5. Limitaciones metodológicas declaradas

- No se ejecutaron pruebas de carga/rendimiento (RNF-005, Locust) — no hay evidencia de que existan en el repositorio.
- No se ejecutaron pruebas contra PostgreSQL real ni contra el stack Docker completo en esta fase — se usó el entorno de pruebas ya configurado por el proyecto (SQLite en memoria), consistente con cómo el propio equipo ejecuta su CI local.
- El suite de frontend demostró no ser determinista (ver `RESULTADOS_VALIDACION.md` §5) — una limitación de la estrategia de aislamiento de pruebas del proyecto, no de esta auditoría.
