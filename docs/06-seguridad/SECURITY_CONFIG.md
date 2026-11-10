---
title: "Seguridad — Configuración de claves"
---

# Configuración de claves de firma

> Este documento se amplía con cada tarea SEC-T del plan de hardening
> (`docs/auditoria-backend/seguridad/plan-implementacion/`). Esta sección
> corresponde a **SEC-T004 — JWT_SIGNING_KEY separada de SECRET_KEY**.

## SEC-T004 — Separación JWT_SIGNING_KEY / SECRET_KEY

### Qué cambió

Antes: `SIMPLE_JWT["SIGNING_KEY"] = SECRET_KEY` (`backend/src/config/settings/base.py:110`,
estado previo). Un compromiso de `SECRET_KEY` comprometía simultáneamente las
sesiones/CSRF de Django **y** la firma de los JWT.

Ahora, dos variables de entorno independientes:

| Variable | Usa | Afecta |
|---|---|---|
| `SECRET_KEY` | Framework Django (`django.core.signing`) | Sesiones, cookies, CSRF |
| `JWT_SIGNING_KEY` | `SIMPLE_JWT["SIGNING_KEY"]` (SimpleJWT) | Firma y verificación de JWT access/refresh |

Ambas son **obligatorias** (`env("...")` sin valor por defecto): si falta
cualquiera de las dos, Django no arranca (`ImproperlyConfigured` al importar
`settings`). Si ambas coinciden, `base.py` registra un `logging.warning` al
arrancar — no bloquea el arranque (para no romper entornos locales
improvisados), pero deja constancia en logs de que el riesgo sigue presente.

### Generación de claves

```bash
openssl rand -base64 32
```

Generar un valor **distinto** para cada variable. Nunca reutilizar el mismo
valor entre `SECRET_KEY` y `JWT_SIGNING_KEY`, ni entre entornos (dev/staging/
producción deben tener claves propias).

### Configuración en el entorno Docker

El `docker-compose.yml` de la raíz del repo ya exigía `SECRET_KEY` como
variable obligatoria del servicio `backend`. Se añadió el mismo patrón para
`JWT_SIGNING_KEY`:

```yaml
backend:
  environment:
    SECRET_KEY: ${SECRET_KEY:?SECRET_KEY is required}
    JWT_SIGNING_KEY: ${JWT_SIGNING_KEY:?JWT_SIGNING_KEY is required}
```

Para desarrollo local con `docker-compose up`, definir ambas en el `.env` de
la raíz del repo (archivo ignorado por git, nunca commitear valores reales):

```bash
SECRET_KEY=<valor generado>
JWT_SIGNING_KEY=<otro valor generado, distinto al anterior>
```

`backend/.env.example` documenta ambas variables (con placeholders, sin
secretos reales) para quien configure un entorno nuevo.

### Impacto del cambio y procedimiento de reautenticación

Al desplegar este cambio, el servidor empieza a verificar las firmas de los
JWT contra `JWT_SIGNING_KEY` en vez de `SECRET_KEY`. Esto significa que:

- **Todos los access y refresh tokens emitidos antes del despliegue dejan de
  ser válidos de inmediato** (la firma ya no verifica contra la nueva clave).
  No hay periodo de gracia ni migración posible para tokens ya emitidos.
- Los usuarios con un token activo recibirán `401` en su siguiente petición
  autenticada y deberán volver a autenticarse en
  `POST /api/v1/auth/token/` para obtener un par de tokens válido. Esto es
  exactamente el comportamiento de "re-login al expirar" ya contemplado para
  el frontend (no se requiere ni se implementa refresh automático ni logout
  de servidor); no hay cambio de contrato ni de código en el frontend.
- **Las sesiones de Django (admin) no se ven afectadas**: siguen firmadas con
  `SECRET_KEY`, que no cambió de variable ni de valor en este despliegue.
- Recomendación operativa: desplegar en una ventana de bajo tráfico y avisar
  a los usuarios activos de que deberán iniciar sesión nuevamente.

### Procedimiento de rotación (independiente por clave) — SEC-T018

**Responsable:** Backend Lead / Responsable de Seguridad del proyecto.
**Frecuencia:** anual, o inmediata ante sospecha de compromiso de
cualquiera de las dos claves (incidente, fuga de `.env`, acceso no
autorizado al servidor).

1. Generar el nuevo valor: `openssl rand -base64 32`.

2. **Rotar `SECRET_KEY`** (afecta sesiones/cookies/CSRF de Django; no afecta JWT):
   1. Añadir el nuevo valor como `SECRET_KEY_NEW` en el entorno, **sin
      eliminar** el `SECRET_KEY` vigente todavía.
   2. Despliegue progresivo (rolling): las instancias nuevas del backend
      deben leer `SECRET_KEY_NEW`; las instancias aún no actualizadas
      siguen usando `SECRET_KEY`. Mantener ambas activas durante una
      ventana de solape (recomendado: 10 minutos, o el tiempo que tome
      completar el despliegue en todas las instancias).
   3. Verificar durante la ventana de solape: login de Django admin
      funciona en instancias viejas y nuevas; ninguna sesión activa se
      invalida antes de que termine el despliegue completo.
   4. Una vez completado el despliegue en el 100% de las instancias,
      renombrar `SECRET_KEY_NEW` → `SECRET_KEY` y eliminar el valor
      anterior de donde estuviera almacenado (gestor de secretos, `.env`
      del servidor, etc.).
   5. Efecto esperado tras completar la rotación: las sesiones/cookies
      firmadas con la clave **anterior** a toda la operación dejan de
      validar → usuarios con sesión de admin abierta desde antes de
      iniciar la rotación deben iniciar sesión de nuevo. Los JWT no se
      ven afectados (firman con `JWT_SIGNING_KEY`, sin cambios en este
      procedimiento).

3. **Rotar `JWT_SIGNING_KEY`** (afecta JWT; no afecta sesiones Django):
   1. Generar el nuevo valor y actualizar la variable de entorno.
   2. Redesplegar. A diferencia de `SECRET_KEY`, aquí **no** se recomienda
      ventana de solape con dos claves simultáneas: SimpleJWT valida con
      una única `SIGNING_KEY` a la vez, así que todos los JWT emitidos
      antes del despliegue quedan inválidos inmediatamente después de él.
   3. Comunicar a los usuarios, antes o inmediatamente después del
      despliegue: "por seguridad, vuelva a iniciar sesión".
   4. Verificar: login emite un token verificable con la clave nueva
      (200); un token firmado con la clave anterior es rechazado (401).

4. **No rotar `SECRET_KEY` y `JWT_SIGNING_KEY` al mismo tiempo sin
   ventana de solape** — dificulta diagnosticar si un fallo post-rotación
   viene de una clave o de la otra.

### Checklist de verificación post-rotación

- [ ] Login (`POST /api/v1/auth/token/`) devuelve `200` y un token válido con la clave nueva.
- [ ] Un token/cookie firmado con la clave anterior es rechazado (`401` para JWT; sesión inválida para `SECRET_KEY`).
- [ ] El login de Django admin funciona con normalidad tras la rotación.
- [ ] No quedan referencias a la clave anterior en variables de entorno activas ni en gestor de secretos.
- [ ] Se notificó a los usuarios si la rotación fue de `JWT_SIGNING_KEY` (re-login obligatorio).

### Evidencia de verificación (simulación local, 2026-11-05)

No existe todavía un entorno de staging real (depende de SEC-T001). Como
sustituto honesto de la "simulación en staging" que pide la ficha, se
rotaron ambas claves **localmente** a valores nuevos generados para la
prueba (no usados antes en ningún entorno) y se ejecutó la suite completa:
**482/482 pruebas pasando**, incluyendo toda la suite de `authentication/`
(62/62) — confirma que el sistema deriva la firma/verificación
exclusivamente de las variables de entorno, sin valores quemados en
código, por lo que el procedimiento de rotación descrito arriba es
mecánicamente seguro de ejecutar. **Esto no sustituye** una verificación
real en staging con PostgreSQL y Nginx (pendiente de SEC-T001/SEC-T020).

### Pruebas asociadas

`backend/src/apps/authentication/tests/test_security_controls.py`:

- `test_jwt_signing_key_separate_from_secret_key`
- `test_jwt_token_verification_uses_jwt_signing_key`
- `test_django_sessions_use_secret_key`

## SEC-T006 — Access Token de 30 minutos

`SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]` pasó de 60 a 30 minutos
(`backend/src/config/settings/base.py`), conforme al ACD. El refresh token
(24h, sin rotación — pendiente de SEC-T003) no cambió. Efecto: el
interceptor del frontend debe renovar el access token con mayor frecuencia
(~cada 25-30 min en vez de ~55-60 min); el mecanismo de renovación ya
existente no cambia de contrato.

**Pruebas asociadas:** `test_access_token_lifetime_30_minutes`,
`test_access_token_expired_after_31_minutes_rejected` (mismo archivo).
