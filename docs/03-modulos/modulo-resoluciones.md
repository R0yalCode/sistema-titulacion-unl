---
title: "Módulo: resoluciones"
---

# M-05 — resoluciones

| Campo | Valor |
|---|---|
| Objetivo | Emitir el Informe de Aptitud (Providencia N.º 590) y registrar la Declaratoria de Aptitud (Memorando N.º 162), con PDF institucional |
| Roles | Secretario Abogado (informe), Decano (declaratoria), Administrador |

## Modelos

| Modelo | Campos clave | Restricciones |
|---|---|---|
| `InformeAptitud` | `numero_providencia` único (`PROV-590-AAAA-NNNN`), `dictamen` (APTO/NO APTO), `archivo_informe_path` | OneToOne PROTECT con expediente |
| `DeclaratoriaAptitud` | `numero_memorando` único (`MEM-162-AAAA-NNNN`), `archivo_memorando_firmado_path` | OneToOne PROTECT con expediente |

## Endpoints

| Método | Ruta | Caso de uso |
|---|---|---|
| POST | `/api/v1/informes/` | Emitir informe + PDF Providencia 590 + expediente→INFORME_EMITIDO + notificar Decanos |
| POST | `/api/v1/declaratorias/` | Registrar memorando firmado (multipart) + expediente→DECLARADA_APTA + notificar actor y copias |

## Reglas de negocio

1. Informe: solo Secretario Abogado; checklist 100 % VERIFICADO (RN-003); sin informe previo; **rechaza dictamen NO APTO**; genera y persiste el PDF (ReportLab).
2. Declaratoria: solo Decano (en la matriz RBAC; el servicio admite además Analista — inconsistencia AUD-P2-07); exige INFORME_EMITIDO y informe existente; valida el PDF del memorando firmado (FirmaEC simulado, DEC-04); autogenera numeración si falta; persiste el archivo con rollback si falla el disco.
3. Numeración correlativa anual; los números son únicos y los documentos inmutables.

## Generación de PDF

`PDFGeneratorAdapter` (ReportLab): Providencia 590 y Memorando 162 con encabezado institucional; escritura en almacenamiento privado (`MEDIA_ROOT/private/resoluciones` o `PRIVATE_MEDIA_ROOT`).

## Pruebas (113)

Emitir informe (24), declarar aptitud (29), modelos (16), generador PDF (30), flujo integrado (14).

## Estado y limitaciones

- **Implementado y verificado.**
- Bug N-1: `HistorialEstado.estado_anterior` registra el estado ya mutado en la transición a INFORME_EMITIDO (AUD-P2-01).
- Hardcode de nombres "Computación"/"FEIRNNR" en el PDF con TODO (pendiente catálogo institucional).
- Serializers de entrada definidos inline en las vistas (deuda de estilo).
