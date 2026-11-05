---
title: "Módulo: verificacion"
---

# M-04 — verificacion

| Campo | Valor |
|---|---|
| Objetivo | Verificación documental por el jurista: checklist digital, observaciones accionables y subsanación |
| Roles | Secretario Abogado (evalúa/observa), Analista de Apoyo (evalúa borrador), Estudiante/Secretaría (subsanа), Administrador |

## Modelos

| Modelo | Campos clave | Restricciones |
|---|---|---|
| `ChecklistVerification` | `estado_verificacion` (PENDIENTE/VERIFICADO/OBSERVADO), `evaluado_por`, `fecha_evaluacion` | Unique `(expediente, requisito)` |
| `ObservacionAccionable` | `motivo_observacion`, `resuelta`, `fecha_registro`, `fecha_resolucion` | FK expediente + petición; índices compuestos |

## Endpoints

| Método | Ruta | Caso de uso |
|---|---|---|
| GET | `/api/v1/expedientes/{expediente_id}/checklist/` | Listado del checklist del expediente |
| PUT | `/api/v1/checklist/{id}/` | Evaluar requisito (VERIFICADO/OBSERVADO + motivo) |
| POST | `/api/v1/checklist/{id}/subsanar/` | Subsanar con PDF (versión N+1, cierra observación, reanuda plazo) |

## Reglas de negocio

1. Evaluación con `select_for_update` (sin condiciones de carrera); solo roles juristas; expediente en EN_VERIFICACION; verificación PENDIENTE.
2. Motivo obligatorio si OBSERVADO; al observar: petición→OBSERVADO, expediente→OBSERVADA, **pausa del plazo**, notificación al estudiante (DEC-01).
3. Subsanación (DEC-02): estudiante dueño o Secretaría de la misma carrera; expediente OBSERVADA; crea versión N+1; verificación→PENDIENTE; petición→CARGADO; expediente→EN_VERIFICACION **reanudando el plazo**.
4. RN-003: `validar_checklist_completo` exige 100 % VERIFICADO antes del informe; expone la lista de pendientes.

## Pruebas (72)

Evaluar (22), checklist+observaciones ciclo completo (28), subsanar (15), completitud (7).

## Estado y limitaciones

- **Implementado y verificado.**
- `ObservacionViewSet` no ruteado y con recurso RBAC inexistente (AUD-P3-01).
- `print()` de depuración en `evaluar_checklist.py:164,170` (AUD-P2-02).
- Cobertura de `views.py` 65 % (ramas de error), mejorable (AUD-P2-10).
