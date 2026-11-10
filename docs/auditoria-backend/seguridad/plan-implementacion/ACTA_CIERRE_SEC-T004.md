# Acta de Cierre — SEC-T004

**Tarea:** SEC-T004 — JWT_SIGNING_KEY Separada de SECRET_KEY
**Proyecto:** SGT-SIAAF — Sistema de Gestión del Proceso de Titulación Integrado al SIAAF, Universidad Nacional de Loja
**Fecha de cierre técnico-documental:** 2026-11-05
**Estado:** CERRADA (técnica y documentalmente) — formalización mediante firma electrónica **FirmaEc: PENDIENTE**

> Este documento resume, para su revisión y posterior suscripción mediante
> FirmaEc por el responsable del proyecto, el trabajo realizado, verificado
> y auditado de forma independiente sobre la tarea SEC-T004. No sustituye
> la firma electrónica; es el documento que debe suscribirse con ella.

---

## 1. Identificación

| Campo | Valor |
|---|---|
| Identificador | SEC-T004 |
| Nombre | JWT_SIGNING_KEY Separada de SECRET_KEY |
| Origen | `docs/auditoria-backend/seguridad/plan-implementacion/FICHAS_TECNICAS_SEC_T001_SEC_T021.md` |
| Prioridad / Riesgo (según plan) | ALTA / ALTO |
| Dependencias | Ninguna (independiente) |
| Tareas desbloqueadas | SEC-T003, SEC-T006, SEC-T018 |

## 2. Problema resuelto

`SIMPLE_JWT["SIGNING_KEY"]` reutilizaba `SECRET_KEY` (`backend/src/config/settings/base.py`, línea 110 antes del cambio). Un compromiso de `SECRET_KEY` permitía simultáneamente falsificar JWT y firmar sesiones/cookies/CSRF de Django. Se separaron en dos variables de entorno independientes y obligatorias.

## 3. Alcance autorizado y archivos modificados

Autorización original de implementación: sesión del 2026-11-05. Archivos modificados en el alcance de SEC-T004:

1. `backend/src/config/settings/base.py` — nueva variable `JWT_SIGNING_KEY`, `SIMPLE_JWT["SIGNING_KEY"]` apunta exclusivamente a ella, warning si coincide con `SECRET_KEY`.
2. `backend/.env.example` — documentación de ambas variables con instrucción de generación (`openssl rand -base64 32`), sin secretos reales.
3. `.env` (raíz, gitignored) — valor dev-only no productivo añadido para continuidad del entorno Docker local.
4. `docker-compose.yml` — `JWT_SIGNING_KEY` propagada como variable obligatoria del servicio `backend`, mismo patrón que `SECRET_KEY`.
5. `backend/src/apps/authentication/tests/test_security_controls.py` (nuevo) — 3 pruebas de seguridad.
6. `docs/06-seguridad/SECURITY_CONFIG.md` (nuevo) — procedimiento de rotación, configuración Docker, impacto y reautenticación.
7. `docs/06-seguridad/autenticacion.md` — corrección de 2 líneas desactualizadas.

Corrección documental adicional (autorizada en sesión posterior de validación, tras auditoría independiente):

8. `backend/docs/adr/0003-autenticacion-jwt-stateless.md` — corregida la descripción de la clave de firma JWT; añadida sección de actualización.
9. `docs/08-infraestructura/configuracion.md` — añadida fila `JWT_SIGNING_KEY`, corregida fila `SECRET_KEY`.
10. `docs/08-infraestructura/entorno-desarrollo.md` — instrucción de preparación de entorno actualizada.

No se modificó ningún archivo de `frontend/`, ningún endpoint, contrato (`openapi.yaml`), regla de negocio, ni ninguna otra tarea SEC-TXXX.

## 4. Pruebas ejecutadas y resultados (verificados en dos sesiones independientes de esta conversación)

| Verificación | Resultado |
|---|---|
| `test_security_controls.py` (3 pruebas nuevas) | 3 passed |
| Suite `authentication/` completa | 60 passed |
| Suite completa del backend | **476 passed, 0 failed** (473 previos + 3 nuevos) |
| `flake8` sobre archivos tocados | 0 hallazgos |
| Fallo seguro sin `JWT_SIGNING_KEY` | `ImproperlyConfigured: Set the JWT_SIGNING_KEY environment variable` |
| Fallo seguro sin `SECRET_KEY` (regresión) | Mismo comportamiento preexistente, sin cambios |
| Ambas claves iguales | Arranca con `logging.warning(...)`, sin exponer el valor real de ninguna clave |

Estos resultados fueron reproducidos de forma independiente (con valores de clave distintos a los de la implementación original) durante la auditoría de validación posterior, sin alterar ni reejecutar la suite en esta sesión de redacción del acta.

## 5. Validación independiente (auditoría)

Se realizó una auditoría de validación independiente, posterior a la implementación, que incluyó: relectura directa de los 8 archivos originales, verificación de huella temporal (`mtime`) en todo el repositorio para confirmar que ningún archivo fuera del alcance declarado fue modificado, re-ejecución de las pruebas con credenciales distintas, verificación de ausencia de secretos reales, y comprobación de que el contrato API (`openapi.yaml`) y el frontend permanecen intactos.

**Hallazgos de esa auditoría:**
- H1, H2, H3 (documentación descriptiva desactualizada) — **corregidos** (ver §3, puntos 8-10).
- H4 (ausencia de control que impida usar claves de desarrollo en producción) — riesgo residual reconocido, diferido a SEC-T001 (no es criterio de aceptación de SEC-T004).
- H5 (cobertura de prueba de sesión Django a nivel de framework de firma, no end-to-end HTTP real) — limitación menor reconocida, no bloqueante.

## 6. Criterios de aceptación de la ficha SEC-T004

| Criterio | Estado |
|---|---|
| Variables en `.env.example` | ✅ Cumplido |
| Tests pasando | ✅ Cumplido (476/476) |
| Procedimiento de rotación documentado en `SECURITY_CONFIG.md` | ✅ Cumplido |
| Documentación descriptiva coherente con la implementación real | ✅ Cumplido (H1-H3 corregidos) |

## 7. Riesgos pendientes (no bloqueantes para el cierre de esta tarea)

- Validación de igualdad de claves ubicada en `base.py` en vez de `production.py` (este último no existe; depende de SEC-T001).
- Sin generación de claves de staging/producción (esos entornos no existen todavía).
- Sin validación en un despliegue real con PostgreSQL (solo verificado con SQLite en memoria, settings de test).
- H4: sin control que impida el uso accidental de claves de desarrollo en un entorno de producción.

## 8. Impacto backend-frontend

Ninguno a nivel de contrato API. Único efecto: los JWT emitidos antes de este cambio quedan inválidos tras el despliegue; comportamiento ya cubierto por el frontend actual (re-login al expirar, sin refresh automático ni logout de servidor inventado). No se requirió ni se realizó ningún cambio en `frontend/`.

## 9. Conclusión técnica

Todos los criterios de aceptación de la ficha SEC-T004 están demostrados mediante evidencia verificada de forma independiente. No se identificaron defectos funcionales, de seguridad ni regresiones. La tarea se considera **CERRADA desde el punto de vista técnico y documental**.

---

## 10. Espacio reservado para formalización (FirmaEc)

**Esta sección se deja intencionalmente sin firma.** No se ha insertado ninguna imagen de firma, sello ni certificado. La formalización de esta acta corresponde exclusivamente al responsable del proyecto mediante el sistema de firma electrónica FirmaEc, fuera de esta conversación.

| Campo | Valor |
|---|---|
| Nombre del responsable | _______________________________ |
| Cargo / rol en el proyecto | _______________________________ |
| Fecha de autorización conversacional (ya ocurrida) | 2026-11-05 |
| Fecha de firma electrónica FirmaEc | **PENDIENTE** |
| Estado de la firma electrónica | **PENDIENTE DE SUSCRIPCIÓN** |

*Firma electrónica (FirmaEc): PENDIENTE. Este documento no está firmado electrónicamente. Debe exportarse/suscribirse por el responsable a través de FirmaEc para completar la formalización del cierre de SEC-T004.*
