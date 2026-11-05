---
title: "API — Introducción"
---

# API REST de SGT-SIAAF

## Contrato canónico

- **Fuente de verdad**: `backend/openapi.yaml` (generado con drf-spectacular desde el código) — copia versionada en `backend/contracts/openapi.yaml` (idénticas, verificado por `diff`).
- **Servido en vivo**: `GET /api/v1/schema/` (OpenAPI), `GET /api/v1/docs/` (Swagger UI), `GET /api/v1/redoc/` (Redoc).
- **17 operaciones** de negocio + 3 de documentación. Sin rutas documentadas que no existan en `config/urls.py` (verificado).

## Base URL y versionado

```
http://localhost:8000/api/v1/
```

Versionado por prefijo de ruta (`/api/v1/`). No hay negociación de versión por cabecera.

## Referencia por grupos

| Grupo | Página | Operaciones |
|---|---|---|
| Autenticación | [auth.md](endpoints/auth.md) | 1 |
| Expedientes | [expedientes.md](endpoints/expedientes.md) | 5 (+1 checklist de expediente) |
| Peticiones y documentos | [peticiones.md](endpoints/peticiones.md) | 4 |
| Checklist | [checklist.md](endpoints/checklist.md) | 2 |
| Resoluciones | [resoluciones.md](endpoints/resoluciones.md) | 2 |
| Notificaciones | [notificaciones.md](endpoints/notificaciones.md) | 2 |

## Principios del contrato

1. Solo JSON (excepto carga de PDF: `multipart/form-data` y descargas: `application/pdf`).
2. Errores con cuerpo DRF estándar (`detail` y/o `fieldErrors`) y `code` semántico cuando aplica.
3. IDs UUID v4 en rutas; sin IDs secuenciales expuestos.
4. Sin operaciones DELETE (política de no borrado).
