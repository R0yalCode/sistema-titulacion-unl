---
title: "APIs de indicadores"
---

# APIs de indicadores (propuesta)

> **No implementadas.** Diseño completo con requisitos, restricciones, ejemplos JSON y estrategia de pruebas: [`docs/indicadores/INFORME_DISENO_KPI.md` §10-13](../indicadores/INFORME_DISENO_KPI.md).

## Propuesta resumida

| Endpoint | Método | Roles | Contenido |
|---|---|---|---|
| `/api/v1/dashboard/me/` | GET | todos | Dashboard compuesto según roles del usuario (recomendado) |
| `/api/v1/indicadores/expedientes/` | GET | SEC.CARR, DIR.CARR, DECANO, ADMIN | Distribución y serie por estado |
| `/api/v1/indicadores/culminacion/` | GET | DIR.CARR, DECANO, ADMIN | Tasa de culminación y tiempo promedio |
| `/api/v1/indicadores/evolucion/` | GET | DIR.CARR, DECANO, ADMIN | Serie mensual (meses vacíos = 0) |

## Requisitos de diseño

1. Solo lectura; JWT + recurso RBAC `dashboard`.
2. Ámbito derivado del usuario autenticado (nunca de parámetros del cliente).
3. Agregaciones en PostgreSQL (`Count`, `Avg`, `TruncMonth`, `generate_series`); sin N+1.
4. Filtros con whitelist (estados del enum real, rangos acotados, `meses` ≤ 24).
5. Fórmulas centralizadas en una capa de servicios (sin duplicación entre endpoints).
6. Pruebas automatizadas por KPI (0, 1, N, períodos vacíos) y por permisos.

## Ejemplo de respuesta (estructura, no datos reales)

```json
{
  "generado_en": "2026-11-05T14:30:00Z",
  "ambito": { "tipo": "carrera", "carrera_id": "5f0c…" },
  "resumen": {
    "expedientes_en_atencion": 12,
    "plazo_vencido": 2,
    "certificados_por_emitir": 5
  },
  "distribucion_estado": { "ENVIADA": 4, "EN_VERIFICACION": 6, "OBSERVADA": 2 }
}
```
