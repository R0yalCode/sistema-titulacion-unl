---
title: "Resultados de validación"
---

# Resultados de validación (05-11-2026)

Resultados **reproducibles** obtenidos durante la auditoría. Comandos exactos en el [informe de auditoría §3](../auditoria/INFORME_AUDITORIA_TECNICA.md).

| Verificación | Resultado |
|---|---|
| Backend: suite configurada (`pytest -q`) | **473 passed**, 0 failed, 0 errors, 15 warnings (10,8 s) |
| Backend: suite extendida (`src/core`, `core/adapters/tests`, `tests/e2e`) | **53 passed** (1,0 s) |
| Backend: cobertura | **93 %** |
| Backend: migraciones (`makemigrations --check`) | Sin cambios pendientes |
| Backend: OpenAPI regenerado vs `openapi.yaml` | **Idéntico** (0 errores, 2 advertencias de spectacular) |
| Backend: `openapi.yaml` vs `contracts/openapi.yaml` | Idénticas (byte a byte) en la fecha de esta validación. *La copia `contracts/` divergió desde INC-01 y se retiró el 2026-11-12 (DK-014).* |
| Backend: flake8 | 854 hallazgos (estilo: E501 530, W292 44, W293 41, F811 ~39) |
| Frontend: `npm run lint` | Sin errores |
| Frontend: `npm run typecheck` | Sin errores |
| Frontend: `npm run test` | **198 passed** (43 archivos, 16,5 s) |
| Frontend: `npm run build` | Exitoso (~296 ms) |

## Advertencias observadas

- 15 warnings de pytest: `InsecureKeyLengthWarning` de PyJWT por la clave de prueba corta (28 bytes < 32 recomendados) — artefacto del entorno de auditoría, no del código.
- 2 warnings de drf-spectacular al regenerar el esquema (menores, sin impacto en el contrato).

## Condiciones de ejecución

- Backend: `DJANGO_SETTINGS_MODULE=config.settings.test` (SQLite en memoria), dependencias instaladas en entorno temporal fuera del repositorio.
- No se dispuso de un servicio PostgreSQL durante la auditoría; la validación contra PostgreSQL real queda como acción recomendada (CI con servicio de BD).
