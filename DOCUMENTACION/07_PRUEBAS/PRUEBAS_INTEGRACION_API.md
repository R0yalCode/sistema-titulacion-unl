---
title: "Pruebas de integración y API"
---

# Pruebas de integración y API — SGT-SIAAF

**Fuente:** ejecución real Fase 7 (2026-11-06) + `DOCUMENTACION/05_API/INVENTARIO_ENDPOINTS.md`. No se ejecutaron peticiones HTTP manuales contra un servidor en ejecución en esta pasada (no se levantó `docker-compose up`); las pruebas de integración reportadas aquí son las que el propio proyecto ejecuta vía `pytest-django` con el cliente de pruebas de Django REST Framework (`APIClient`), que sí ejercita la pila completa de URL→vista→serializer→permiso→ORM dentro del proceso de prueba.

## 1. Endpoints con prueba de integración confirmada (por app, Fase 7)

Las 17 operaciones de negocio inventariadas en `DOCUMENTACION/05_API/INVENTARIO_ENDPOINTS.md` tienen, cada una, al menos un archivo de prueba en la app correspondiente (ver `PRUEBAS_UNITARIAS.md` §1 para el mapeo exacto servicio↔archivo de prueba) — los servicios de aplicación son invocados por las vistas DRF, y las pruebas existentes cubren mayoritariamente el servicio directamente (no siempre vía `APIClient` HTTP real, lo cual es una prueba de integración de capas internas, no necesariamente HTTP de punta a punta). No se auditó, endpoint por endpoint, cuáles pruebas usan `APIClient().post(...)` real contra la URL versus llamada directa a la función `execute()` del servicio — es una distinción metodológica que excede el alcance de esta Fase 7 y se señala como trabajo pendiente si se requiere ese nivel de detalle.

## 2. Casos de error probados (consistente con `CONTRATO_API.md`)

Según los nombres de clases de excepción confirmados en `COMPONENTES_NEGOCIO.md` (p. ej. `ExpedienteActivoExistenteError`, `RequisitosIncompletosError`, `InvalidVerificationStateError`, `UsuarioNoAutorizadoError`), cada servicio tiene pruebas para sus propios caminos de error, no solo el camino feliz — confirmado por la existencia de archivos de prueba con casos negativos (nombres de test visibles en la recolección de pytest, p. ej. `TestCasosEdge` en `test_pdf_generator.py`).

## 3. Pruebas de seguridad/aislamiento (RBAC e IDOR)

Ya documentadas con cifras en `DOCUMENTACION/06_SEGURIDAD/AUTORIZACION_PERMISOS.md` §6: 17 pruebas de matriz RBAC + 13 de aislamiento IDOR + 4 E2E (cifras citadas de `docs/06-seguridad/autorizacion.md`, no reejecutadas de forma aislada en esta Fase 7, pero sí incluidas dentro del total de 560 passed al estar dentro de `src/apps/authentication/tests/` y `src/core/`).

## 4. Lo que esta auditoría NO verificó en este nivel (declarado explícitamente)

- No se levantó el servidor real (`docker-compose up`) para hacer peticiones HTTP externas contra `/api/v1/` con una herramienta como `curl` o Postman.
- No se verificó el comportamiento real de CORS, ni de Nginx como proxy, en esta fase (corresponde a Fase 8).
- No se verificó empíricamente si las excepciones de dominio que responden 500 (hallazgo INC-21, `CONTRATO_API.md` §3) exponen o no un traceback en la respuesta real — requeriría una petición HTTP real contra una instancia con `DEBUG=False`, no solo una prueba unitaria contra el servicio.

## 5. Conclusión

La integración entre capas (vista → servicio → ORM → base de datos) está ejercitada por 560 pruebas pasando sobre 573 (97.7 %), con las 13 fallas restantes de causa externa confirmada (ver `RESULTADOS_VALIDACION.md`). No se realizó, en esta fase, una prueba de integración HTTP de extremo a extremo contra un servidor real en ejecución.
