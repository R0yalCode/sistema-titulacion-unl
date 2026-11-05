# S1-05 — CRITERIOS DE ACEPTACIÓN DEL SPRINT S1

**Fecha:** 02-nov-2026 · Aplicables a cada tarea de `S1_04_MATRIZ_TAREAS_S1.md`; verificables por comando, test o artifact.

## 1. Criterios globales del sprint (Definition of Done)

| # | Criterio | Verificación |
| :--- | :--- | :--- |
| DO-1 | Suite completa verde: `464` tests, 0 failed, 0 errors, en `config.settings.test` | `python -m pytest -q` en contenedor, con y sin `DJANGO_SETTINGS_MODULE` pre-set |
| DO-2 | Ningún test eliminado, deshabilitado ni debilitado respecto a `main` (baseline 464) | `git diff --stat` sobre `**/tests/**` sin borrados ni `skip` nuevos sin justificación |
| DO-3 | Cobertura de lógica de negocio ≥ 70 % (RNF-012) | `pytest --cov=src/apps --cov=src/core --cov-report=term` |
| DO-4 | Sin rutas absolutas `/media/...` en `src/apps/resoluciones` ni rutas construidas a mano fuera del storage porte | `grep -rn "/media/" src/apps/resoluciones` → 0; revisión de PR |
| DO-5 | El memorando #162 y la providencia #590 finales se guardan físicamente con hash si migración aprobada | Test de persistencia (`archivo_existe()` + `hashlib` al reexaminar) |
| DO-6 | `GET checklist` responde por rol según matriz aprobada y con aislamiento por expediente | tests paramétricos RBAC + IDOR |
| DO-7 | Decisión sobre C1 (Django Admin) documentada (ADR/clarify) ANTES de tocar settings | commit del documento de decisión |
| DO-8 | Sin registro de contraseñas/tokens en logs, admin ni auditoría | revisión + `pytest` sobre serializers/logging |
| DO-9 | `docker-compose up --build` sigue funcionando con almacenamiento en volumen privado | despliegue limpio + test de persistencia después de recrear contenedor |
| DO-10 | Documentación SDD actualizada (entregables S1 + nota de decisión) | existencia y aprobación |

## 2. Criterios por tarea (resumen operativo)

| Tarea | C.A. clave (ver detalle en S1_04) |
| :--- | :--- |
| S1-T01 | 6 documentos, hallazgos con veredicto y evidencia, baseline re-ejecutable |
| S1-T02 | 0 PermissionError; rutas relativas; archivo físico existe; no regresiones |
| S1-T03 |_matriz GET checklist con tests 8 roles; default deny para `RESPONSABLE_DEPENDENCIA` mejorhall clarification |
| S1-T04 | check limpio; 13 modelos registrados conforme a diseño; 5 read-only; sin delete de expedientes; smoke tests |
| S1-T05 | portabilidad SQLite/PostgreSQL de tests de índices; pypdf en dev-reqs; sin skips silenciosos |
| S1-T06 | OpenAPI válido; e2e; matriz endpoint×rol presentada |

## 3. Criterios de NO-ACPTACIÓN (reinicio de tarea)

- Cualquier cambio que modifique la matriz RBAC aprobada sin justificación en PR y sin mapeo a specify/planner.
- Deshabilitar u omitir pruebas para resolver la causa silenciosamente.
- Persistencia de archivos fuera del almacenamiento privado.
- Internacionalización de la ruta hardcodeada en vez de eliminar la causa raíz.
- Admin que muestre o permita edición de: `hash_sha256`, `archivo_path`, `detalles_json` modificable, estados de expediente, o contraseñas.

## 4. Acercamiento en disputa
Ante conflicto entre los criterios y una restricción de la Constitución/ESpecs SDD: precedia el documento SDD (jerarquía plan.md §1), y el conflicto debe documentarse como propósito de nueva decisión (como se hizo con C1).
