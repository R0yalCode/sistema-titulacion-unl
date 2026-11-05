---
title: "Módulo: peticiones"
---

# M-03 — peticiones

| Campo | Valor |
|---|---|
| Objetivo | Gestionar el catálogo de requisitos del Art. 235, las peticiones por expediente y los documentos PDF versionados |
| Roles | Estudiante (dueño), Secretaría de Carrera, dependencias emisoras, juristas (descarga), Administrador |

## Modelos

| Modelo | Campos clave | Restricciones |
|---|---|---|
| `CatalogoDocumental` | `codigo_requisito` único, `fase` (FASE_1/2/3), `rol_emisor_sugerido` (choices de roles), `activo` | Sembrado: 5 requisitos Art. 235 (migración 0002) |
| `PeticionDocumental` | `estado_peticion` (PENDIENTE/SOLICITADO/CARGADO/LEGALIZADO/VERIFICADO/OBSERVADO/CANCELADA), `dependencia_emisora`, `fecha_solicitud` | Unique `(expediente, requisito)`; 3 índices |
| `DocumentoEntregado` | `version`, `archivo_path`, `hash_sha256`, `tamanio_bytes`, `es_vigente` | Unique `(peticion, version)`; FK PROTECT subidor |

## Endpoints

| Método | Ruta | Caso de uso |
|---|---|---|
| POST | `/api/v1/peticiones/{id}/solicitar-emision/` | PENDIENTE→SOLICITADO + notificación a la dependencia emisora |
| POST | `/api/v1/peticiones/{id}/documento/` | Cargar PDF (multipart; ≤10 MB; magic bytes; SHA-256; versión N+1) |
| GET | `/api/v1/peticiones/{id}/documento/` | Descargar versión vigente (`FileResponse`, attachment) |
| GET | `/api/v1/peticiones/{id}/documento/{version}/` | Descargar versión específica |

## Reglas de negocio

1. Solicitar emisión solo en expediente BORRADOR/OBSERVADA y petición PENDIENTE; autorizado el estudiante dueño o Secretaría de Carrera.
2. Carga permitida en estados PENDIENTE/SOLICITADO/OBSERVADO/CARGADO; el anterior vigente pasa a `es_vigente=False`.
3. Validación PDF real: tamaño ≤10 MB y magic bytes `%PDF-` (no confía en extensión ni MIME); hash SHA-256 en streaming.
4. Descarga con autorización manual de ámbito que además soporta `SCOPE_ASIGNADO` (la dependencia emisora descarga lo suyo).

## Pruebas (85)

Solicitar emisión (15), cargar (19), descargar (12), ingesta y seguridad de PDF (39).

## Estado y limitaciones

- **Implementado y verificado.**
- `LEGALIZADO` y `CANCELADA` definidos sin flujo que los produzca.
- `PeticionDocumentalViewSet` existe pero no está ruteado (código muerto, AUD-P3-01).
- Sin escaneo antivirus (solo validación estructural del PDF).
