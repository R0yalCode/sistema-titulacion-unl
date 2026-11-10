---
title: "Funcionalidad futura — Firma electrónica (FirmaEC)"
---

# Firma electrónica (FirmaEC) — Funcionalidad futura y diferida

> **Estado: PROPUESTA / DIFERIDA. No implementada.** Esta carpeta contiene
> únicamente documentación de arquitectura y planificación. No existe
> código, modelo, migración, endpoint, dependencia ni configuración
> Docker asociada a FirmaEC en este repositorio. Nada de lo aquí descrito
> debe interpretarse como funcionalidad vigente.

## Por qué existe esta carpeta

El sistema SGT-SIAAF, en su estado actual, **simula** la firma electrónica
del Memorando 162 (Decisión Arquitectónica **DEC-04**, documentada en
`docs/02-arquitectura/decisiones-arquitectonicas.md` y
`docs/02-arquitectura/c4/contexto.md`): el Decano **carga manualmente** un
PDF que ya fue firmado fuera del sistema; SGT-SIAAF no firma nada, no se
conecta a ningún servicio de firma, y no gestiona certificados ni claves.

Esta carpeta registra, para una fase futura no planificada ni autorizada,
cómo podría integrarse un servicio real de firma electrónica (FirmaEC, el
servicio institucional ecuatoriano) sin comprometer la arquitectura actual
ni los principios de seguridad ya establecidos.

## Alcance de esta documentación

- Es una **propuesta técnica para discusión**, no una especificación
  aprobada ni un compromiso de implementación.
- Depende de validaciones institucionales pendientes con la Dirección de
  Tecnologías de Información de la UNL (ver `PENDIENTES_VALIDACION_UNL.md`)
  que **no se han realizado**.
- No asume que la UNL tiene contratada o habilitada ninguna modalidad
  específica de FirmaEC, ni que la información en documentación histórica
  del proyecto (DEC-04, simulaciones, mocks) describe un servicio real
  activo — solo describe cómo el sistema se comporta **hoy**, de forma
  simulada.

## Índice de documentos

| Documento | Contenido |
|---|---|
| `PROPUESTA_INTEGRACION_FIRMAEC.md` | Qué se propone, modalidad prevista, alcance funcional y qué queda explícitamente fuera. |
| `REQUISITOS_INSTITUCIONALES.md` | Marco normativo ecuatoriano aplicable y requisitos institucionales a confirmar con la UNL. |
| `ARQUITECTURA_PROPUESTA.md` | Patrón de adaptador desacoplado, ubicación en la arquitectura hexagonal existente, entidades conceptuales. |
| `FLUJO_FIRMA_DOCUMENTOS.md` | Flujos propuestos: documentos generados por SGT-SIAAF, documentos externos cargados, firmas secuenciales. |
| `SEGURIDAD_Y_PROTECCION_CLAVES.md` | Modelo de no-custodia de claves/certificados, hash SHA-256, validación criptográfica, trazabilidad. |
| `CONTRATOS_API_PROPUESTOS.md` | Diferenciación explícita entre endpoints actuales, endpoints propuestos (no implementados) e interfaces oficiales de FirmaEC. |
| `PLAN_IMPLEMENTACION.md` | Fases conceptuales de una futura implementación, sin fechas ni compromisos, sujeta a autorización e identificadores de tarea propios. |
| `PENDIENTES_VALIDACION_UNL.md` | Lista explícita de lo que debe validarse con la Dirección de Tecnologías de Información de la UNL y autoridades correspondientes antes de avanzar. |

## Relación con el backlog de seguridad SEC-T001–SEC-T021

Ninguna. Esta propuesta es independiente del backlog de hardening de
seguridad (`docs/auditoria-backend/seguridad/plan-implementacion/`). No
se le asigna ningún identificador `SEC-T` ni `FE-T` en este documento;
cualquier identificador de tarea futuro deberá asignarse explícitamente
cuando (y si) el responsable del proyecto autorice avanzar.
