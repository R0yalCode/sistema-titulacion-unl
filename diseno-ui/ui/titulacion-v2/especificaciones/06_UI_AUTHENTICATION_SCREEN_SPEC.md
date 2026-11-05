# 06 · Pantalla de autenticación — V-01 (SGT-SIAAF)

**Versión:** 1.1.0 · **Fecha:** 2026-11-04 · **Estado:** Referencia visual no normativa (DEC-11). Requisitos funcionales en `specs/003-frontend-titulacion/specify.md` §7 (V-01, RFF-101…RFF-107); tarea React FE-T101…FE-T104.
Especificación dedicada a la vista V-01 (`/login`, referencia prototipo A: `accessPage()`).

## 6.1. Estado real del login (importante)

- **Lo vigente (2026-11-04):** autenticación **JWT local** vía `POST /auth/token/` del backend existente. La UI construye este flujo como única vía de ingreso real: usuario+contraseña, errores genéricos (nunca revela si falló el usuario o la contraseña — CA-V01-02), sesión persistida con expiración y cierre de sesión que borra el `access` (CA de FE-T012/FE-T016). Sin renovación: la expiración del access implica volver a iniciar sesión (ver §6.4).
- **Perfiles demo:** el prototipo A muestra pestañas Estudiante/Funcionario y accesos demo. Son **solo visual** (DEC-11): en la UI real no existen usuarios sembrados ni atajos demo; los roles llegan del JWT real. Las pestañas orientatorias del prototipo pueden traducirse (si se decide) como ayuda visual, nunca como selector que fija credenciales.
- **Prohibido:** simular login sin backend, inventar usuarios demo, autocompletar credenciales; si el backend no responde, la UI muestra el 503/`ErrorState` del kit de errores (doc 08).

## 6.2. Estructura visual

- Layout de 2 columnas 50/50 en desktop (apilado 100 % en móvil — doc 04).
- **Columna izquierda:** imagen del campus UNL con degradado oscuro, logos UNL, texto "Tu futuro profesional comienza aquí".
- **Columna derecha:** fondo blanco; logo SGT-SIAAF (birrete + texto); formulario.

## 6.3. Formulario (real)

| Elemento | Comportamiento |
|---|---|
| Usuario | Correo institucional o identificador; `<label>` + validación de formato |
| Contraseña | Input con icono de ojo para ver/ocultar (`aria-label` en el botón, no `title`) |
| Botón "Ingresar" | Primario; estado `mutating` mientras `POST /auth/token/` está en vuelo (disable + spinner) |
| mensajes de error | InlineAlert bajo el formulario, genérico: "Credenciales inválidas…" o mensaje de red del backend sin datos sensibles |
| "¿Olvidó su contraseña?" / "Ayuda" | **No implementar acción**: placeholder visual solo si se aprueba decisión de producto; si no, ocultarlo (no link muerto sin comportamiento) |

Tras login exitoso: redirección al inicio por rol (`/estudiante` u `/bandeja`, tabla de redirección en `specify.md` §6).

## 6.4. Gestión de tokens y sesión (estructura oficial, coherente con `plan.md` §6 y FE-T011)

| Aspecto | Decisión documentada |
|---|---|
| **Login JWT actual** | `POST /api/v1/auth/token/` (única vía de autenticación vigente; `TokenObtainPairResponseSerializer` SimpleJWT devuelve `access` y `refresh`; el OpenAPI declara solo `200` "No response body" — INC-13) |
| **Obtención de access y refresh** | Se reciben ambos en el `200` real, aunque el contrato no los tipifique explícitamente (el cliente tipa la respuesta real) |
| **Almacenamiento** | **Solo `access`** se persiste en `sessionStorage` (clave `sgt.access`; PQ-06). El `refresh` **se descarta** — nunca se persiste (correcto con FE-T011 y `plan.md` §6.2). *(Corrección MOMENTO 2, 2026-11-04:* la redacción anterior de esta sección/`specify.md` decía "access y refresh"; se corrigió por contradicción documental)* |
| **Expiración** | El access dura lo que configure el backend (SimpleJWT; por defecto ~60 min; **no verificado en el repo**). Al recibir 401: avisar "Su sesión expiró", limpiar la sesión y redirigir a `/login` (RFF-014); sin reintento automático; el borrador local se conserva si existe (RSK-FE-03) |
| **Logout** | Sin endpoint de logout de servidor: el frontend borra el `access` de `sessionStorage` y limpia el estado del `AuthContext` (FE-T016) |
| **Renovación de tokens** | **No existe** endpoint de renovación (`POST /auth/refresh/` es una dependencia **BE-03 NO AUTORIZADA**). **No implementar refresh automático**; el usuario vuelve a iniciar sesión. Si en el futuro se aprueba, la estrategia (rotación + cookies `httpOnly`) exigirá backend y una decisión human |
| **Prohibido** | No inventar SAC, OAuth2, OIDC, TOTP ni eventos de validación: no hay nada más que el login JWT local (CL-03) |

## 6.5. Integración SAC (futuro, no implementar)

El proyecto contempla integrarse con el SAC (Servicio de Autenticación Centralizada; OAuth2/OIDC). **Hoy no existe endpoint SAC autorizado** y su inclusión queda documentada como evolución:

- Cuando el backend soporte SAC, la UI añadirá el botón secundario "Ingresar con cuenta institucional UNL" con estado de carga "Redirigiendo al SAC…".
- Mientras tanto, **no se muestra botón SAC ni texto sobre SAC** fuera de esta documentación: solo JWT real. La decisión de exposición es dependiente del backend (similar a BE-x sin par de FE).

## 6.6. Accesibilidad y estados

- V-01 es la única página visible sin sesión, junto al 404 global: mantener cumplimiento AA igual al resto.
- Estados completos de V-01 según `specify.md` §7: `idle`, `mutating`, `error` (`401` genérico / 5xx), `network` (inaccesible). Para detalles de errores del kit de errores ver doc 08 (ERR-01: 401 existe como aviso en navegación autenticada, no como página de login con credenciales).
- Redirección con sesión activa a `/login` → al inicio por rol (CA-V01-04).

## 6.7. Referencias

- Requerimientos: `specs/003-frontend-titulacion/specify.md` §7 (V-01), RFF-101…RFF-107 y CA-G-04.
- Tareas: FE-T011…FE-T017 (auth y sesión) y FE-T101…FE-T104 (página).
- Kit de errores del 401: `08_UI_ERROR_STATES_SPEC.md` ERR-01; prototipo B `acceso.html` (maqueta con campos deshabilitados: **solo referencia visual**).
