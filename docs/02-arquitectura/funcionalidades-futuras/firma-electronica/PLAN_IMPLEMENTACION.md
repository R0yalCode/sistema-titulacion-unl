---
title: "FirmaEC — Plan de implementación (conceptual)"
---

# Plan de implementación (conceptual, no autorizado)

**Estado: PROPUESTA / DIFERIDA. No implementada. No autorizada.** Este
plan es deliberadamente conceptual: no incluye fechas, estimaciones de
esfuerzo en días/semanas, ni asignación de responsables, porque cualquiera
de esos compromisos sería prematuro mientras existan bloqueos
institucionales sin resolver (`PENDIENTES_VALIDACION_UNL.md`). Tampoco se
le asigna un identificador de tarea (`SEC-T`/`FE-T`): eso corresponde al
responsable del proyecto cuando decida activar esta línea de trabajo.

## Fase 0 — Validación institucional (precondición de todo lo demás)

Nada de lo descrito en las fases siguientes puede iniciar sin resolver
`PENDIENTES_VALIDACION_UNL.md`. Esta fase no es técnica: es de gestión
institucional con la Dirección de Tecnologías de Información de la UNL y
las autoridades correspondientes.

## Fase 1 — Diseño detallado (una vez resuelta la Fase 0)

- Confirmar el puerto (`core/ports/firma_electronica.py`) con el contrato
  mínimo real que necesita el dominio, ajustado a la modalidad de
  FirmaEC que la UNL haya confirmado.
- Diseñar las entidades conceptuales de `ARQUITECTURA_PROPUESTA.md` como
  modelos Django reales, con sus migraciones, **en una rama/trabajo
  separado y autorizado explícitamente** — no como parte de este
  documento.
- Definir el contrato API definitivo (sustituyendo los endpoints
  "propuestos" de `CONTRATOS_API_PROPUESTOS.md` por una especificación
  OpenAPI real, versionada junto a `backend/openapi.yaml`).

## Fase 2 — Adaptador simulado (`firma_ec_mock.py`)

- Implementar primero el adaptador simulado, para poder construir y
  probar todo el flujo de negocio (secuencia de firmantes, estados,
  auditoría) sin depender del proveedor real — mismo enfoque que
  `mock_sga.py` tuvo para el SGA/SIAAF.
- Esto permite validar el diseño de dominio antes de necesitar acceso a
  un ambiente real o de pruebas del proveedor.

## Fase 3 — Adaptador real (`firma_ec_real.py`)

- Solo si la Fase 0 confirma una modalidad real disponible y accesible
  (sandbox o producción) para el equipo de desarrollo.
- Requiere credenciales/ambiente del proveedor que **SGT-SIAAF no
  gestiona ni almacena como secretos propios del sistema** (ver
  `SEGURIDAD_Y_PROTECCION_CLAVES.md`) — la gestión de esas credenciales
  de integración (distintas de los certificados personales de cada
  funcionario) es responsabilidad institucional, documentada aparte si
  corresponde.

## Fase 4 — Piloto acotado

- Un solo tipo de documento (sugerido: Memorando 162, por ser el que ya
  tiene un flujo de firma simulado al que comparar) y un número reducido
  de firmantes reales antes de extender a todos los documentos.

## Fase 5 — Generalización

- Extensión a otros documentos (Providencia 590 u otros) solo si el
  piloto de la Fase 4 es validado institucional y técnicamente.

## Qué se necesita antes de poder convertir esto en tareas con
identificador y estimación real

1. Resolución de `PENDIENTES_VALIDACION_UNL.md` (todas las filas).
2. Aprobación de `REQUISITOS_INSTITUCIONALES.md` por las instancias
   correspondientes de la UNL.
3. Autorización explícita del responsable del proyecto para abrir esta
   línea de trabajo, con alcance y fase inicial definidos — siguiendo el
   mismo modelo de autorización tarea-por-tarea ya usado para el backlog
   SEC-T001–SEC-T021.
