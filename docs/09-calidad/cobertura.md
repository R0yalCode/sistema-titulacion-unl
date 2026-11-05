---
title: "Cobertura"
---

# Cobertura de código

## Backend — medición del 05-11-2026

Comando: `pytest --cov=src --cov-report=term` (suite configurada, 473 pruebas).

| Métrica | Valor |
|---|---|
| Declaraciones | 7.693 |
| Omitidas | 534 |
| **Cobertura total** | **93 %** |

### Módulos destacados

| Módulo | Cobertura |
|---|---|
| `core/adapters/pdf_validation.py` | 100 % |
| `core/adapters/scope_filter.py` | 97 % |
| `resoluciones/services/emitir_informe.py` | 95 % |
| `resoluciones/services/declarar_aptitud.py` | 88 % |
| `verificacion/services/evaluar_checklist.py` | 92 % |
| `verificacion/services/registrar_observacion.py` | 76 % |
| `verificacion/adapters/views.py` | **65 %** (mínimo) |
| `core/adapters/mock_sga.py` | 84 % |
| `config/urls.py` | 100 % |

### Notas metodológicas

- La medición cubre `src/apps` (testpaths por defecto). `core/tests` aparece en 0 % en este reporte porque su suite no se ejecutó en la misma corrida (está fuera de `testpaths`, hallazgo AUD-P1-04); sus 47 pruebas sí pasan al ejecutarlas explícitamente.
- El README raíz declara "95 %": la medición reproducible actual es **93 %** (hallazgo AUD-P2-09).

## Frontend

`npm run test:coverage` disponible (vitest + v8). No se registró una cifra de cobertura en esta auditoría; la suite completa (198 pruebas) pasa sin fallos.
