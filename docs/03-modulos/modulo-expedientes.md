---
title: "Módulo: expedientes"
---

# M-02 — expedientes

| Campo | Valor |
|---|---|
| Objetivo | Gestionar el ciclo de vida del expediente de titulación y sus plazos regulatorios |
| Procesos | Crear solicitud, enviar formalmente, bandeja operativa, observación, plazos |
| Roles | Estudiante (dueño), juristas/secretaría (bandeja), Decano, Administrador |

## Modelos

| Modelo | Campos clave | Restricciones |
|---|---|---|
| `ExpedienteTitulacion` | `numero_expediente` único (`EXP-AAAA-NNNN`), `numero_providencia` único (`PROV-AAAA-NNNN`), `estado` (7 choices, indexado), `fecha_recepcion`, `fecha_limite_atencion`, `dias_laborables_acumulados`, `activa` | FK PROTECT a estudiante; índice `carrera_id` |
| `HistorialEstado` | `estado_anterior`, `estado_nuevo`, `fecha_cambio` | FK CASCADE al expediente; FK registrador. Se crea **solo** desde `registrar_transicion()` (DT-12), una fila por transición, con el estado anterior leído de la BD antes del cambio |

## Endpoints

| Método | Ruta | Caso de uso |
|---|---|---|
| POST | `/api/v1/expedientes/` | Crear BORRADOR + 5 peticiones Art. 235 (atómico) |
| GET | `/api/v1/expedientes/bandeja/` | Bandeja paginada filtrada por rol (10/página, máx 50) |
| GET | `/api/v1/expedientes/{id}/` | Detalle con aislamiento (404 si es ajeno) |
| POST | `/api/v1/expedientes/{id}/enviar/` | BORRADOR→ENVIADA; providencia + plazo 8 días hábiles |
| POST | `/api/v1/expedientes/{id}/observar/` | Delega en verificacion (observación accionable) |

## Reglas de negocio

1. Un expediente activo por estudiante (`select_for_update`).
2. Requieren exactamente 5 requisitos base Art. 235 FASE_1 activos.
3. Envío solo con todos los requisitos en firme (estados bloqueados: PENDIENTE, SOLICITADO, OBSERVADO, CANCELADA) — si no, **422** `requisitos_incompletos`.
4. Plazo: 8 días hábiles desde el día hábil siguiente al envío (AP-01/COA Art. 160); se pausa al observar y reanuda al subsanar, extendiendo la fecha límite.
5. Bandeja por rol (`MAPA_INTERVENCION_POR_ROL`): Estudiante ve BORRADOR/OBSERVADA; juristas ENVIADA/EN_VERIFICACION/OBSERVADA; Decano INFORME_EMITIDO; Admin todas; Secretaría/Director/Responsable: vacía.

## Pruebas (73)

Crear (8), enviar (7), máquina de estados (25), IDOR (13), bandeja (9), plazos (11).

## Estado y limitaciones

- **Implementado y verificado.**
- Estado `CANCELADA` sin flujo que lo produzca; bug de `estado_anterior` en la transición a INFORME_EMITIDO se registra en resoluciones (AUD-P2-01).
- `fecha_limite_atencion` se actualiza solo vía pausa/reanudación; no hay job de vencimientos (la detección de vencidos es en consulta).
