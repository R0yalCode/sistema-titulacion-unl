---
title: "Observabilidad"
---

# Observabilidad — SGT-SIAAF

**Fuente:** lectura directa de `backend/src/core/adapters/{health,logging_filters,middleware,client_ip}.py`, `backend/src/apps/notificaciones/adapters/signals.py` y `backend/src/config/settings/base.py` (sección `LOGGING`), todo verificado en esta Fase 9 (2026-11-06). Esta página **corrige dos hallazgos heredados** que esta misma auditoría venía repitiendo sin reverificar desde la Fase 0 — ver §4.

## 1. Health check — IMPLEMENTADO Y VERIFICADO

`GET /health/` (`core/adapters/health.py`): responde `{"status": "ok"}` sin autenticación, confirmando únicamente que el proceso Django responde — no expone información del sistema (versión, configuración, estado de la base de datos), por diseño declarado en el propio docstring del archivo. Usado como `HEALTHCHECK` del contenedor Docker en el target `production` (`DOCUMENTACION/08_DESPLIEGUE/ARQUITECTURA_DOCKER.md` §3), cada 30s. Cobertura de pruebas: 67% (Fase 7) — el archivo tiene solo 3 líneas de código, por lo que esa cifra corresponde a una única rama sin ejercitar, no a un vacío significativo.

**Limitación declarada por diseño, no un defecto**: el healthcheck no verifica conectividad real a PostgreSQL ni al almacenamiento de archivos — solo que el proceso Python responde. Un fallo de base de datos no se reflejaría en `/health/` como "unhealthy".

## 2. Logging estructurado — IMPLEMENTADO Y VERIFICADO (corrige un hallazgo heredado)

`base.py` define un `LOGGING` dict completo (Django `dictConfig`): formateador JSON vía `python-json-logger` (dependencia confirmada en `STACK_TECNOLOGICO.md`), dos filtros propios (`SensitiveDataFilter`, `RequestIdFilter`) y una jerarquía de loggers (`apps`/`core` a `INFO`, `django`/`django.request` a `WARNING`, `django.security` a `INFO`).

- **`SensitiveDataFilter`** (`core/adapters/logging_filters.py`): usa una expresión regular para enmascarar campos sensibles (`password`, `token`, `authorization`, `credit_card`, `cedula`) tanto en el mensaje de log como en atributos extra del record — es decir, está diseñado específicamente para que un log accidental de un payload no filtre credenciales o cédulas.
- **`RequestIdFilter`**: garantiza que `request_id`/`user_id` existan en cada record (con placeholder `"-"` hasta que exista un mecanismo de contexto de request más completo), evitando que el formateador JSON falle por campos faltantes.

## 3. Bitácora de auditoría de negocio (`EventoAuditoria`) — IP REAL, NO VACÍA (corrige un hallazgo heredado)

`apps/notificaciones/adapters/signals.py` (`_crear_evento_auditoria`) obtiene la IP del cliente llamando a `resolver_ip_cliente(request)` (`core/adapters/client_ip.py`), donde `request` se recupera del middleware thread-local (`ThreadLocalRequestMiddleware`, primero en `MIDDLEWARE`, confirmado en Fase 0). `resolver_ip_cliente` solo confía en la cabecera `X-Forwarded-For` si la IP que habló directamente con Django está dentro de `TRUSTED_PROXIES` — de lo contrario usa `REMOTE_ADDR` directamente, y sin `TRUSTED_PROXIES` configurado (dev/test) nunca confía en la cabecera. Es la misma función que usa el throttling de login (SEC-T002), evitando que ambos mecanismos tuvieran lógicas de confianza en IP divergentes.

Cada evento de auditoría se crea con `usuario`, `rol_usuario`, `expediente`, `ip`, `timestamp` y `detalles` (JSONB), dentro de un `try/except` que registra el error vía `logger.error(..., exc_info=True)` **sin romper la operación de negocio principal** si la auditoría falla — un patrón de resiliencia deliberado (fail-safe), consistente con lo que ya documentaba `auditoria/01_AUDITORIA_GENERAL.md` ("auditoría inmutable vía signals fail-safe").

## 4. Corrección de hallazgos heredados (verificado en esta fase, no antes)

Esta auditoría venía repitiendo, desde la Fase 0, dos afirmaciones de `docs/06-seguridad/consideraciones-seguridad.md` y `docs/auditoria/matriz-trazabilidad.md` sin haberlas verificado directamente contra el código actual:

| Afirmación heredada | Estado real verificado en Fase 9 |
|---|---|
| "`print()` de depuración en producción" (`evaluar_checklist.py:164,170` según `auditoria/01`) | **No existe ningún `print()` en `backend/src`** (excluyendo tests/migraciones), verificado con búsqueda exhaustiva. El archivo citado ya no los tiene. |
| "sin `LOGGING`" | **Existe un `LOGGING` completo** en `base.py` (ver §2) — posiblemente añadido después de los informes que señalaban su ausencia. |
| "IP de auditoría siempre vacía" (RF-013 marcado IP en `docs/auditoria/matriz-trazabilidad.md`) | **La IP se captura y persiste realmente** vía `resolver_ip_cliente` (ver §3), con lógica consciente de proxies de confianza. |

Esto significa que el estado de RF-013 (bitácora de auditoría), documentado como **IP** (parcial) en `DOCUMENTACION/01_ESPECIFICACION/REQUISITOS_FUNCIONALES.md` y en `MATRIZ_TRAZABILIDAD.md`, debe revisarse: de los dos defectos que lo mantenían en "parcial" (eventos sin emitir, IP vacía), **el de la IP vacía ya no es cierto**. No se verificó en esta fase si los "3 eventos de auditoría sin emitir" siguen pendientes — esa parte de la calificación "parcial" puede seguir siendo válida.

## 5. Manejo de excepciones y exposición de información (RNF-015)

Ya cubierto en `DOCUMENTACION/06_SEGURIDAD/PROTECCION_DATOS.md` §4: con `DEBUG=False` (configuración por defecto de `base.py`), Django no debería incluir tracebacks completos en la respuesta HTTP. Las excepciones de dominio no controladas se registran vía `logger.error(..., exc_info=True)` en el caso de auditoría (§3); no se verificó si existe un patrón equivalente centralizado (p. ej. un `EXCEPTION_HANDLER` de DRF) para todas las vistas — ya se confirmó en `CONTRATO_API.md` que **no existe** un `EXCEPTION_HANDLER` personalizado, lo cual es coherente con el hallazgo INC-21 (algunas excepciones de dominio producen 500 genéricos en vez de códigos semánticos): el logging de esas excepciones depende de los handlers por defecto de Django/DRF, no de un mecanismo de observabilidad centralizado y deliberado para errores de API.

## 6. Diagnóstico — lo que NO está implementado (declarado, no inventado)

- Sin integración con una herramienta de monitoreo externa (APM, Sentry, Prometheus) detectada en `requirements.txt` — el logging estructurado en JSON está preparado para ser consumido por un agregador externo (formato compatible), pero no hay evidencia de que exista uno configurado en este repositorio.
- Sin métricas de aplicación (contadores, latencias) expuestas — no hay endpoint `/metrics/` ni dependencia tipo `django-prometheus` en `requirements.txt`.
- El `healthcheck` no verifica dependencias externas (ver §1).

## 7. Conclusión

La observabilidad real del backend es más sólida de lo que las fuentes heredadas indicaban: logging estructurado con enmascarado de datos sensibles, auditoría de negocio con IP real capturada de forma segura (consciente de proxies), y manejo de errores fail-safe en la auditoría. La brecha real que permanece es la ausencia de una herramienta de monitoreo/métricas externa — algo nunca reclamado como implementado por ninguna fuente, por lo que no es una regresión, es simplemente una capacidad no construida.
