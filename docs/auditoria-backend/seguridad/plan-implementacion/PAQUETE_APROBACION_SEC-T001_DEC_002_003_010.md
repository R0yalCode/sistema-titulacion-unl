---
title: "Paquete de aprobación — DEC-002, DEC-003, DEC-010 (desbloqueo SEC-T001)"
---

# Paquete de aprobación para desbloquear SEC-T001

**Fecha:** 2026-11-05
**Estado:** Análisis técnico para decisión del responsable. **Ninguna decisión aquí descrita está aprobada.** Ninguna fue marcada como tal en `DECISIONES_TECNICAS_PENDIENTES.md`, que permanece sin modificar.
**Relación con otros documentos:** complementa, no sustituye, a `DECISIONES_TECNICAS_PENDIENTES.md` (que define el problema y las alternativas originales) y a `FICHAS_TECNICAS_SEC_T001_SEC_T021.md` (ficha de SEC-T001). Este documento profundiza DEC-002, DEC-003 y DEC-010 con evidencia verificada directamente en el código y arquitectura actuales, y añade el análisis de ubicación de archivos de producción y de la inconsistencia DEC-004.

No se implementó SEC-T001 ni ninguna otra tarea. No se modificó código, Docker, Nginx, frontend ni dependencias. No se modificó ninguna ficha técnica existente — las correcciones propuestas se presentan como texto, no como ediciones aplicadas.

---

## 1. DEC-002 — Tasa de throttling para login

### 1.1 Problema técnico que resuelve

`POST /api/v1/auth/token/` (`TokenPairView`, `backend/src/apps/authentication/adapters/views.py`) no tiene `throttle_classes` configurado. Verificado contra el código actual: el endpoint acepta intentos de autenticación sin límite de frecuencia, lo que permite fuerza bruta de contraseñas y *credential stuffing* contra cualquier cuenta conocida (username basado en cédula/matrícula, predecible).

### 1.2 Alternativas disponibles (ya documentadas en `DECISIONES_TECNICAS_PENDIENTES.md`, no nuevas)

| Valor | Ventaja | Desventaja |
|---|---|---|
| 5/min/IP | Conservador, estándar de referencia (OWASP) | Mayor riesgo de bloquear usuarios legítimos tras una IP compartida |
| 10/min/IP | Menos falsos positivos | Ventana de ataque más amplia |
| 20/min/IP | Casi sin falsos positivos | Protección débil |
| Configurable por variable de entorno | Flexible por entorno | Requiere igualmente fijar un valor por defecto |

### 1.3 Ventajas, desventajas y riesgos

- **Riesgo arquitectónico verificado:** el throttling por IP (`AnonRateThrottle`) solo es confiable si la IP capturada es la real del cliente. Hoy `_get_client_ip()` (SEC-T005, no cerrada) no valida `X-Forwarded-For` contra proxies confiables. **DEC-002 depende técnicamente de SEC-T005**, tal como ya documenta la ficha de SEC-T002 ("Condición de bloqueo: Si SEC-T005 no cerrada → IP no confiable → throttling por IP de proxy → bloqueo masivo").
- **Riesgo institucional no verificable desde el código:** una universidad típicamente concentra el tráfico de red de campus (WiFi, laboratorios) detrás de un número reducido de IPs públicas por NAT. Si varios estudiantes inician sesión desde la misma red de campus en la misma ventana de un minuto (p. ej. al abrir un plazo de titulación), un límite estricto por IP podría bloquear usuarios legítimos simultáneamente. Esto **no está confirmado para la red real de la UNL** — es un riesgo genérico de cualquier red institucional, no un dato verificado de este proyecto.
- **Mitigación posible, no implementada:** un throttle complementario (p. ej. límite también por intento de usuario, no solo por IP) reduciría el riesgo de bloqueo masivo, pero la ficha de SEC-T002 prohíbe explícitamente `UserRateThrottle` en este endpoint ("requiere usuario autenticado; login es anónimo"). Esto es correcto para `UserRateThrottle` de DRF (que requiere `request.user` ya autenticado), pero no excluye un throttle *scoped* por nombre de usuario intentado (vía `ScopedRateThrottle` con una clave derivada del campo `username` del payload). Señalo esto como una opción técnica adicional no contemplada en la ficha original — **no la propongo como cambio de alcance, solo como información para la decisión.**

### 1.4 Revisión de la arquitectura actual

- `TokenPairView` no tiene `throttle_classes` (confirmado, `views.py`).
- `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` no existe en `base.py` (confirmado).
- El `nginx/nginx.conf` de desarrollo ya reenvía `X-Forwarded-For` y `X-Forwarded-Proto` al backend — es decir, cuando exista `production.py` + `TRUSTED_PROXIES` (SEC-T005), la cabecera necesaria para la IP real **ya llega** desde la capa Nginx existente; falta la validación en Django, no la cabecera en el proxy.

### 1.5 Recomendación técnica (propuesta, no aprobada)

Mantener la recomendación ya documentada: **5/minuto/IP**, configurable vía `AUTH_THROTTLE_RATE`, **condicionado a que SEC-T005 esté cerrada primero** (orden ya establecido en la matriz de dependencias, sin cambios). No propongo un valor distinto porque no tengo evidencia del tráfico real de la UNL para justificar otro número — 5/min/IP es la referencia OWASP estándar, no un valor inventado para este proyecto.

### 1.6 Impactos

| Área | Impacto |
|---|---|
| Backend | Bajo esfuerzo (clase de throttle + config), ya diseñado en la ficha de SEC-T002 |
| Frontend | Bajo: debe mostrar mensaje ante `429` (ya contemplado en `MATRIZ_COMPATIBILIDAD_BACKEND_FRONTEND_SEGURIDAD.md`) |
| Infraestructura | Ninguno adicional más allá de SEC-T005 (ya contemplado) |
| Compatibilidad | Ninguna ruptura de contrato; solo un código HTTP nuevo (`429`) en un escenario antes inexistente |

### 1.7 Información adicional necesaria para decidir

- Si existe algún dato (aunque sea estimado) de cuántos usuarios concurrentes podrían autenticarse desde una misma IP de campus en la práctica — no disponible en este repositorio.
- Confirmación del responsable de que 5/min/IP es aceptable como riesgo de falso-positivo institucional, o si prefiere 10/min/IP u otro valor.

---

## 2. DEC-003 — Tasa de throttling para carga de documentos

### 2.1 Problema técnico que resuelve

`POST /api/v1/peticiones/{id}/documento/` (acción `cargar_documento`, `PeticionViewSet`) no tiene límite de frecuencia. Un usuario autenticado podría cargar archivos de hasta 10MB repetidamente sin límite, agotando almacenamiento (`MEDIA_ROOT`) o degradando el servicio.

### 2.2 Alternativas disponibles (ya documentadas, no nuevas)

| Valor | Justificación |
|---|---|
| 10/hora/usuario | Referencia de la auditoría original |
| 20/hora/usuario | Más permisivo para flujos con varias subsanaciones |
| 5/hora/usuario | Restrictivo |
| Configurable por variable de entorno | Flexible |

### 2.3 Ventajas, desventajas y riesgos — análisis basado en datos reales del catálogo documental

A diferencia de DEC-002, aquí sí pude fundamentar un valor con un dato **verificado en el código**, no estimado:

- El catálogo base de requisitos (`backend/src/apps/peticiones/adapters/migrations/0002_catalogo_base_art235.py`) define exactamente **5 requisitos documentales obligatorios** por expediente (Art. 235 RRA-UNL: récord académico, prácticas/vinculación, idioma B1, director de trabajo, certificado de tesorería).
- En el flujo normal (sin observaciones), un estudiante carga como máximo 5 documentos en total durante **todo** el trámite, no por hora.
- El flujo de subsanación (`ESTADO_OBSERVADO` → nueva carga) permite que un mismo requisito se recargue más de una vez. Incluso en un escenario pesimista de 2-3 recargas por requisito en una sola sesión de corrección, el total realista en una hora de trabajo activo del estudiante ronda las 10-15 cargas — lo que hace que **10/hora/usuario** sea un límite holgado para el uso legítimo y, a la vez, efectivo contra abuso sostenido (cargas automatizadas/repetidas fuera de este patrón).
- El catálogo es "configurable" (`CatalogoDocumental.activo`, administrable), por lo que el número de requisitos podría crecer en el futuro — el valor de throttle debería revisarse si el catálogo institucional se amplía significativamente más allá de los 5 actuales.

### 2.4 Revisión de la arquitectura actual

- `cargar_documento` no tiene `throttle_classes` ni `throttle_scope` (confirmado).
- No hay actualmente ningún límite de tamaño agregado por usuario/tiempo, solo el límite de 10MB por archivo individual (`pdf_validation.py`, ya verificado en auditorías previas).

### 2.5 Recomendación técnica (propuesta, no aprobada)

**10/hora/usuario** (`UserRateThrottle`, no `AnonRateThrottle` — el endpoint ya requiere autenticación), configurable vía `DOCUMENT_UPLOAD_THROTTLE`. A diferencia de DEC-002, esta recomendación no depende de SEC-T005 (el throttle es por usuario autenticado, no por IP), por lo que **técnicamente podría implementarse de forma independiente de SEC-T001**, tal como ya indica su propia ficha ("Dependencias: Ninguna (independiente, Fase 0)") — lo menciono aquí solo como verificación, sin proponer adelantar su implementación sin autorización.

### 2.6 Impactos

| Área | Impacto |
|---|---|
| Backend | Bajo esfuerzo, ya diseñado en la ficha de SEC-T008 |
| Frontend | Bajo: mensaje ante `429` |
| Infraestructura | Ninguno |
| Compatibilidad | Ninguna ruptura; nuevo código `429` en escenario antes inexistente |

### 2.7 Información adicional necesaria para decidir

- Confirmación de si el catálogo documental institucional se mantendrá cercano a los 5 requisitos actuales o si hay planes de ampliarlo sustancialmente (afectaría el valor recomendado).
- Confirmación del responsable de que 10/hora/usuario es aceptable, o si prefiere un valor distinto.

---

## 3. DEC-010 — Estrategia de Content Security Policy (CSP)

### 3.1 Problema técnico que resuelve

`production.py` no existe; no hay ninguna cabecera `Content-Security-Policy` configurada. Sin CSP, el sitio no tiene mitigación de XSS a nivel de cabecera ni protección contra *clickjacking* vía `frame-ancestors`, ni contra inyección de `<base>` vía `base-uri`.

### 3.2 Alternativas disponibles (ya documentadas, no nuevas)

- **A)** CSP estricta desde el inicio.
- **B)** Solo `frame-ancestors 'none'` + `base-uri 'self'`.
- **C)** Sin CSP en el MVP.
- **D)** CSP en modo `Report-Only` + `frame-ancestors`/`base-uri` bloqueantes desde el inicio — **recomendación ya registrada** en `DECISIONES_TECNICAS_PENDIENTES.md`.

### 3.3 Verificación directa de la alternativa D contra el código real del frontend

Esta es la parte de la decisión que sí pude fundamentar con evidencia directa, en vez de repetir la recomendación genérica:

| Verificación | Resultado | Relevancia para CSP |
|---|---|---|
| `frontend/index.html` | Un único `<script type="module" src="/src/main.tsx">`; **sin scripts inline**, sin CDN, sin Google Fonts, sin analytics | Favorece `script-src 'self'` sin `'unsafe-inline'` para la app principal |
| `frontend/vite.config.ts` | Configuración mínima (plugin React, alias); sin integraciones externas | Sin origenes externos que añadir a `connect-src`/`script-src` por configuración de build |
| Estilos (`src/styles/*.css`, `*.module.css`) | CSS Modules + CSS plano; **sin CSS-in-JS** (no hay `styled-components` ni `emotion` en `package.json`) | Favorece `style-src 'self'` sin `'unsafe-inline'`; Vite extrae CSS Modules a archivos `.css` estáticos, no a `<style>` inline, en el build de producción |
| `package.json` (dependencias) | React 19, react-dom, react-router-dom únicamente como runtime; sin librerías de gráficos/mapas que suelan requerir CDN | Sin orígenes externos adicionales conocidos |
| `VITE_API_BASE_URL` | Variable configurable, consumida por el cliente HTTP del frontend | **Debe incluirse explícitamente en `connect-src`** la URL real de la API en cada entorno — no se puede fijar un valor único válido para todos los entornos sin conocer el dominio real de despliegue |
| `drf-spectacular-sidecar` | **No está instalado** (`requirements.txt` no lo incluye); Swagger/ReDoc (`SpectacularSwaggerView`, `SpectacularRedocView` en `config/urls.py`) usan por defecto los assets servidos desde CDN (`unpkg.com`) de `drf-spectacular` | Una CSP estricta (`script-src 'self'`) rompería `/api/v1/docs/` y `/api/v1/redoc/` salvo que se permita ese CDN explícitamente o se instale `drf-spectacular-sidecar` (dependencia nueva, requiere autorización aparte) |

**Conclusión de la verificación:** la app principal del frontend (lo que usan estudiantes y funcionarios) está, por diseño actual, en una posición favorable para una CSP relativamente estricta — **no encontré evidencia de scripts inline, CDN, fuentes externas o CSS-in-JS que la bloqueen**. El punto de riesgo real identificado es Swagger/ReDoc (uso administrativo, ya restringido a `IsAdminUser` por SEC-T013), no la aplicación de negocio.

**Importante — límite de esta verificación:** esto se basó en inspección estática del código fuente y configuración (`index.html`, `vite.config.ts`, `package.json`, estilos), **no en ejecutar `npm run build` y auditar el bundle real producido**, ni en pruebas de navegador con la cabecera activa. Antes de activar cualquier modo bloqueante (más allá de `frame-ancestors`/`base-uri`), se debería validar contra el build real, no solo contra el código fuente.

### 3.4 Requisitos reales para activar la alternativa D

1. Modo `Report-Only` requiere, para ser útil, un **endpoint de recepción de reportes** (`report-uri`/`report-to`). **Ese endpoint no existe hoy** y no está descrito en la ficha de SEC-T001 más allá de mencionar el modo Report-Only — sin él, las violaciones solo serían visibles manualmente en las herramientas de desarrollador del navegador durante QA manual, no de forma monitoreada. Esto es una limitación operativa real a decidir: aceptar monitoreo manual, o ampliar el alcance para incluir un endpoint de reportes (cambio de alcance, requeriría autorización propia).
2. `frame-ancestors 'none'` y `base-uri 'self'` como directivas bloqueantes desde el inicio son de bajo riesgo verificado: la aplicación no usa `<iframe>` para embeberse a sí misma en otros sitios (no encontré uso de `<frame>`/`<iframe>` en el frontend) ni manipula `<base>` dinámicamente.
3. Si en el futuro se decide endurecer `script-src`/`style-src` más allá de Report-Only, debe hacerse **después** de validar contra el build de producción real y, si se mantiene Swagger/ReDoc con CDN, excluir esas rutas del endurecimiento o resolver primero `drf-spectacular-sidecar`.

### 3.5 Riesgos de la alternativa D

- Riesgo bajo de romper la app principal (evidencia favorable, aunque no validada contra build real).
- Riesgo medio de romper Swagger/ReDoc si en algún momento se pasa de Report-Only a bloqueante sin resolver el CDN de `drf-spectacular` — mitigado porque Swagger ya está planeado para quedar restringido a administradores (SEC-T013).
- Riesgo operativo de que el modo Report-Only, sin endpoint de reportes, no aporte valor de monitoreo real más allá de pruebas manuales puntuales.

### 3.6 Recomendación técnica (propuesta, no aprobada)

Confirmar la alternativa **D** ya documentada, con dos matices que añado tras la verificación:
- Aclarar explícitamente, al aprobarla, si se acepta monitoreo manual del modo Report-Only (sin endpoint de reportes) como suficiente para esta fase, o si se amplía el alcance para construir ese endpoint.
- Validar la política contra un build de producción real (`npm run build`) antes de desplegar a staging, no solo contra el código fuente.

### 3.7 Impactos

| Área | Impacto |
|---|---|
| Backend | Cabecera añadida en `production.py`; sin cambios de lógica |
| Frontend | Ninguno si se mantiene Report-Only; posible ajuste futuro si se endurece `connect-src` con el dominio real de la API |
| Infraestructura | Ninguno adicional (la cabecera la pone Django, no Nginx, salvo que se decida lo contrario) |
| Compatibilidad | Ninguna ruptura en modo Report-Only; riesgo solo si se pasa a bloqueante sin validar |

### 3.8 Información adicional necesaria para decidir

- Dominio(s) real(es) de despliegue (frontend y API) para completar `connect-src`/`CORS_ALLOWED_ORIGINS` — no inventados aquí.
- Decisión sobre si se requiere un endpoint de reportes CSP en esta fase o se posterga.
- Decisión sobre si Swagger/ReDoc deben excluirse de cualquier endurecimiento futuro de `script-src`, o si se autoriza instalar `drf-spectacular-sidecar`.

---

## 4. Matriz resumen DEC-002, DEC-003, DEC-010

| Decisión | Problema | Recomendación (NO aprobada) | Depende de | Riesgo principal | Bloquea |
|---|---|---|---|---|---|
| DEC-002 | Login sin límite de intentos | 5/min/IP, vía `AUTH_THROTTLE_RATE` | SEC-T005 (IP confiable) | Bloqueo de usuarios tras NAT compartida (no verificable desde el código) | SEC-T002, parte de contenido de SEC-T001 |
| DEC-003 | Carga de documentos sin límite | 10/hora/usuario, vía `DOCUMENT_UPLOAD_THROTTLE` | Ninguna (independiente) | Bajo — holgado frente a los 5 requisitos reales del catálogo | SEC-T008, parte de contenido de SEC-T001 |
| DEC-010 | Sin cabecera CSP | Alternativa D (Report-Only + `frame-ancestors`/`base-uri` bloqueantes) | Dominio real de despliegue; decisión sobre endpoint de reportes | Swagger/ReDoc vía CDN si se endurece sin resolver sidecar | SEC-T001 completo (precondición explícita de su ficha) |

---

## 5. Recomendación de ubicación de archivos de producción (backend/ vs raíz)

**No se creó, movió ni modificó ningún archivo para este análisis.**

### 5.1 Estado verificado de la convención actual (desarrollo)

| Archivo | Ubicación real hoy | Detalle verificado |
|---|---|---|
| `Dockerfile` (dev) | Raíz del repo | Build de una sola etapa; `WORKDIR /app/backend`; contexto de build `.` (raíz); `COPY backend/requirements.txt .`, `COPY backend/src ./src`; usuario `django`; `CMD runserver` |
| `docker-compose.yml` (dev) | Raíz del repo | Servicios `db`, `backend`, `nginx`; variables de entorno inline (no `env_file`), alimentadas por `.env` en la raíz; volúmenes `media_data`→`/app/backend/media`, `static_data`→`/app/backend/staticfiles` |
| `nginx/nginx.conf` (dev) | `nginx/` en la raíz | Proxy HTTP simple; **ya reenvía** `X-Forwarded-For`/`X-Forwarded-Proto` hacia el backend |
| `.env` (dev, real) | Raíz del repo | `POSTGRES_*`, `SECRET_KEY`, `JWT_SIGNING_KEY`, `DEBUG` |

La ficha original de SEC-T001 propone, en cambio: `backend/Dockerfile` (multi-stage, `WORKDIR /app`, usuario `appuser`, gunicorn), `backend/docker-compose.prod.yml` (con `env_file: .env.prod`), `backend/nginx/prod.conf` — es decir, un árbol **completamente separado y anidado dentro de `backend/`**, distinto de la convención real ya existente.

### 5.2 Comparación

| Criterio | Opción A — todo en `backend/` (como propone la ficha original) | Opción B — junto a los archivos de desarrollo, en la raíz |
|---|---|---|
| Convenciones existentes | Introduce una convención nueva y distinta a la ya usada en desarrollo | Coincide exactamente con la convención ya usada en desarrollo |
| Contexto de build Docker | Ficha asume contexto `backend/` (`COPY requirements.txt .` sin prefijo) → distinto del contexto actual `.` (raíz) | Puede reutilizar el mismo contexto `.` (raíz) y las mismas rutas `COPY backend/...` ya usadas |
| Variables de entorno | Introduce un segundo archivo de entorno (`backend/.env.prod`), paralelo al `.env` de raíz ya usado por Docker Compose | Puede extender el mismo mecanismo de `.env` de raíz (o un `.env.prod` también en la raíz), sin introducir una segunda convención |
| Nginx | Crea un segundo directorio `nginx/` (dentro de `backend/`), separado del `nginx/` ya existente en la raíz | Puede añadir `nginx/prod.conf` al `nginx/` que ya existe, un solo lugar para toda la configuración de proxy |
| Volúmenes | Nombres de volumen nuevos (`media_private`) sin relación declarada con `media_data`/`static_data` ya existentes | Misma oportunidad de definir volúmenes nuevos, pero con visibilidad junto a los ya existentes en el mismo `docker-compose.prod.yml` de raíz |
| Mantenimiento/despliegue | Quien despliegue debe saber que dev vive en raíz y prod vive en `backend/` — dos lugares distintos para el mismo concepto | Un único lugar (`raíz`) para encontrar cualquier archivo relacionado con contenedores, independientemente del entorno |

### 5.3 Recomendación (propuesta, no aplicada)

**Opción B — mantener los archivos de producción en la raíz del repositorio, junto a los de desarrollo**, reutilizando el `nginx/` ya existente (añadiendo `nginx/prod.conf` junto a `nginx/nginx.conf`) y el mismo patrón de `.env` de raíz. Esto es más coherente con la convención real verificada del proyecto y evita mantener dos ubicaciones distintas para el mismo concepto (contenedor del backend).

**Decisión menor pendiente, no bloqueante:** si la imagen de producción se implementa como un **archivo separado** (`Dockerfile.prod`) o como un **target multi-stage** dentro del `Dockerfile` único ya existente (`docker build --target=production`). Ambas son prácticas comunes; no tomo esta decisión aquí, solo la señalo para que el responsable la resuelva junto con la autorización de SEC-T001.

---

## 6. Análisis de la inconsistencia DEC-004

### 6.1 Verificación

Releí la ficha de SEC-T001 completa (`FICHAS_TECNICAS_SEC_T001_SEC_T021.md`). Su sección **"Precondiciones"** dice textualmente:

> - DEC-010 (CSP strategy) aprobada.
> - Repositorio limpio (sin cambios locales pendientes).
> - Decisiones DEC-002, DEC-003, DEC-004 valores confirmados para config.

Revisé exhaustivamente la sección **"Cambios autorizables"** de esa misma ficha (producción.py, Dockerfile, entrypoint.sh, docker-compose.prod.yml, nginx/prod.conf, .env.example): no contiene ninguna referencia a cobertura de pruebas, `pytest`, `testpaths` ni `--cov-fail-under`. Esos elementos corresponden exclusivamente a la ficha de **SEC-T016** ("Cobertura Tests + testpaths"), que es la que lista a DEC-004 como su propia precondición ("DEC-004 aprobada (umbral 80% u otro)") y es la única con contenido real relacionado (`pyproject.toml`, `[tool.pytest.ini_options]`, `[tool.coverage.run]`).

### 6.2 Conclusión

**Confirmado: es un error documental.** DEC-004 no tiene ninguna relación de contenido con SEC-T001; pertenece exclusivamente a SEC-T016. La tabla "Matriz de Decisiones vs Tareas Bloqueadas" de `DECISIONES_TECNICAS_PENDIENTES.md` ya lo refleja correctamente (DEC-004 → solo SEC-T016), lo que refuerza que la lista de precondiciones de la ficha de SEC-T001 es la que está equivocada, no al revés.

### 6.3 Corrección exacta propuesta (NO aplicada)

En `FICHAS_TECNICAS_SEC_T001_SEC_T021.md`, sección SEC-T001 → "Precondiciones":

```diff
- - Decisiones DEC-002, DEC-003, DEC-004 valores confirmados para config.
+ - Decisiones DEC-002, DEC-003 valores confirmados para config.
```

Esta es la única corrección propuesta. No afecta ninguna otra precondición, dependencia ni contenido de la ficha.

---

## 7. Decisiones que requieren aprobación del responsable del proyecto

- DEC-002 (valor final de throttling login: 5/min/IP recomendado, u otro).
- DEC-003 (valor final de throttling carga: 10/hora/usuario recomendado, u otro).
- DEC-010 (confirmación de la alternativa D, más las dos precisiones del §3.6: aceptación de monitoreo manual sin endpoint de reportes, y validación contra build real antes de staging).
- Ubicación de archivos de producción (recomendación: raíz, junto a los de desarrollo — Opción B del §5).
- Formato del Dockerfile de producción: archivo separado vs. target multi-stage (§5.3, decisión menor).
- Corrección documental de DEC-004 en la ficha de SEC-T001 (§6.3) — presentada, no aplicada.

## 8. Decisiones que requieren validación institucional externa

**Ninguna.** A diferencia de la línea de trabajo de FirmaEC, DEC-002, DEC-003, DEC-010, la ubicación de archivos de producción y la corrección de DEC-004 son decisiones técnicas internas del proyecto (backend/infraestructura), sin necesidad de validación de la Dirección de Tecnologías de Información de la UNL ni de otras autoridades institucionales.

---

**No se implementó SEC-T001 ni ninguna otra tarea. No se modificó código, frontend, Docker, Nginx, dependencias, ni el estado de ninguna decisión DEC-001 a DEC-010. No se alteró SEC-T004 ni su acta de cierre.**
