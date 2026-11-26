---
title: "OpenAPI / Swagger"
---

# OpenAPI y Swagger — SGT-SIAAF

## 1. Ubicación del esquema

**Archivo fuente versionado:** `backend/openapi.yaml` (1224 líneas, OpenAPI 3.0.3), generado por `drf-spectacular` a partir del código real (introspección de ViewSets/serializers), no escrito a mano. **Se conserva en su ubicación original**, conforme a la instrucción del encargo; no se mueve ni se renombra.

**Duplicado detectado:** `backend/contracts/openapi.yaml` es un archivo idéntico byte a byte (mismo MD5, confirmado con `diff`/`md5sum` en la Fase 5) — ver `INVENTARIO_ENDPOINTS.md` §4.

## 2. Correspondencia con los endpoints reales (verificación cuantitativa)

Se contaron las rutas de nivel superior bajo `paths:` en `backend/openapi.yaml`: **16 rutas**. Se contaron las rutas de negocio únicas en `backend/src/config/urls.py`: **16 rutas** (17 operaciones HTTP, porque `/peticiones/{id}/documento/` agrupa GET y POST en la misma ruta). **Coincidencia exacta.** No se detectaron endpoints de negocio ausentes del esquema ni endpoints "fantasma" en el esquema sin ruta real correspondiente.

Esto es consistente con que el esquema se genera por introspección (`drf-spectacular`) y no se mantiene a mano: estructuralmente no puede desincronizarse del código salvo que alguien edite el YAML manualmente después de generarlo, lo cual no se detectó.

## 3. Cómo acceder a Swagger/ReDoc (verificado en `urls.py`)

| Interfaz | Ruta | Requiere autenticación |
|---|---|---|
| Esquema OpenAPI crudo | `GET /api/v1/schema/` | No (`AllowAny`) |
| Swagger UI | `GET /api/v1/docs/` | No |
| ReDoc | `GET /api/v1/redoc/` | No |

Con el stack levantado (`docker-compose up`, puerto 8000 vía Nginx — ver `DOCUMENTACION/08_DESPLIEGUE/` en fases posteriores), estas URLs son accesibles en `http://localhost:8000/api/v1/docs/` (Swagger) y `.../redoc/`.

## 4. Hallazgo de seguridad heredado (ya documentado por el equipo, no nuevo de esta auditoría)

`docs/RESUMEN_EJECUTIVO.md` señala como mejora menor pendiente: "endpoints de documentación OpenAPI con `AllowAny`" — es decir, el esquema y las interfaces Swagger/ReDoc son navegables sin autenticación. Esto no expone datos de negocio (el esquema solo describe la forma de la API, no devuelve datos reales), pero sí facilita el reconocimiento de la superficie de ataque a un atacante no autenticado. Se trata en profundidad en `DOCUMENTACION/06_SEGURIDAD/` (Fase 6).

## 5. Integración en el portal Quarto

Dado que `backend/openapi.yaml` es un archivo YAML extenso generado por introspección (no pensado para lectura humana directa página por página), y que Quarto no tiene un render nativo de especificaciones OpenAPI sin una extensión adicional no confirmada como instalada en este proyecto, la Fase 11 (portal Quarto) debe **enlazar** al Swagger real del backend en ejecución (`/api/v1/docs/`) en vez de intentar incrustar el YAML completo o simular que el servicio está públicamente desplegado cuando no lo está. El inventario de endpoints de esta página (`INVENTARIO_ENDPOINTS.md`) cumple la función de "representación navegable" dentro del propio portal estático.

## 6. Mejoras menores pendientes (heredadas, citadas con su fuente)

Según `docs/RESUMEN_EJECUTIVO.md` §10–12: "2 mejoras menores pendientes (securityScheme, login sin security)" en el esquema OpenAPI. No se reverificó el contenido exacto de esas dos observaciones en esta pasada (serían ediciones al `openapi.yaml`, fuera del alcance de esta auditoría documental, que no modifica `backend/`).
