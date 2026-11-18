# SGT-SIAAF — Sistema de Gestión del Trámite de Titulación

**Universidad Nacional de Loja — Facultad de la Energía, las Industrias y los Recursos Naturales No Renovables (FEIRNNR)**
**Carrera de Computación — Asignatura: Desarrollo Basado en Plataformas (5.º ciclo)**

---

## Contenido

1. [Presentación](#1-presentación)
2. [Funcionalidades](#2-funcionalidades)
3. [Tecnologías](#3-tecnologías)
4. [Arquitectura](#4-arquitectura)
5. [Instalación y ejecución local](#5-instalación-y-ejecución-local)
6. [Guía de ingreso al sistema](#6-guía-de-ingreso-al-sistema)
7. [Google Authenticator: instrucciones para el usuario](#7-google-authenticator-instrucciones-para-el-usuario)
8. [Recuperación de contraseña y del segundo factor](#8-recuperación-de-contraseña-y-del-segundo-factor)
9. [Roles y permisos](#9-roles-y-permisos)
10. [Configuración y seguridad](#10-configuración-y-seguridad)
11. [Pruebas y calidad](#11-pruebas-y-calidad)
12. [API](#12-api)
13. [Estado del proyecto y limitaciones](#13-estado-del-proyecto-y-limitaciones)
14. [Solución de problemas](#14-solución-de-problemas)
15. [Licencia y autores](#15-licencia-y-autores)

---

## 1. Presentación

**SGT-SIAAF** es el Sistema de Gestión del Trámite de Titulación integrado al SIAAF de la Universidad Nacional de Loja (UNL).

**Problema que resuelve.** El trámite de titulación exige reunir certificados de varias dependencias, verificarlos, observarlos y subsanarlos, emitir un informe y registrar una declaratoria. Hecho a mano, con papel y correo, el trámite es lento, difícil de seguir y no deja trazabilidad. SGT-SIAAF lo digitaliza en un expediente único con estados, plazos, documentos versionados y una bitácora de auditoría.

**Objetivos principales.**

- Centralizar el expediente de titulación del estudiante y su documentación.
- Coordinar a los actores del trámite con permisos acotados a su rol y su ámbito (carrera o facultad).
- Dar seguimiento al estado y a los plazos del expediente.
- Proteger el acceso con correo institucional y un segundo factor de autenticación.

**Alcance funcional actual (Fase 1).** Declaratoria de aptitud legal (Art. 235 del RRA-UNL). Estados del expediente:

`BORRADOR` → `ENVIADA` → `EN_VERIFICACION` ⇄ `OBSERVADA` → `INFORME_EMITIDO` → `DECLARADA_APTA` (además de `CANCELADA`)

Las fases de sustentación y de cierre del trámite (tribunal, calificaciones, acta y registro del título) **no están implementadas**. La página pública las presenta solo como referencia.

---

## 2. Funcionalidades

### Implementadas

| Área | Qué hace hoy |
|---|---|
| **Acceso con correo institucional** | Se ingresa con el correo `@unl.edu.ec` y la contraseña. El dominio se valida en el navegador **y en el backend**. |
| **Doble factor (2FA) con TOTP** | Google Authenticator (u otra app TOTP compatible) se registra mediante un código QR. Después se solicita el código temporal en cada ingreso, salvo que el dispositivo sea de confianza. |
| **Dispositivo de confianza** | Opcional, de 5 días. El cierre de sesión revoca la confianza de ese dispositivo. |
| **Códigos de recuperación** | 10 códigos de un solo uso que se entregan al activar el 2FA. |
| **Recuperación de contraseña** | Se envía un enlace de un solo uso al correo registrado. |
| **Restablecimiento del 2FA** | Correo + cédula + contraseña actual permiten solicitar un enlace de un solo uso; el autenticador se retira al confirmar ese enlace. |
| **Control de acceso por roles (RBAC)** | Matriz rol × recurso × acción evaluada en el servidor, con filtrado por ámbito (propio, carrera, facultad, asignado). |
| **Gestión del trámite** | Creación del expediente, peticiones de certificados a las dependencias, carga de PDF versionada, envío, verificación por checklist, observación y subsanación, informe de aptitud y declaratoria. |
| **Seguimiento** | Panel del estudiante, bandeja operativa por rol, detalle del expediente y de cada petición, notificaciones internas. |
| **Auditoría y seguridad** | Bitácora de eventos del trámite y de autenticación (sin secretos), límites de intentos, documentos privados, cabeceras de seguridad. |
| **Página pública** | Presentación del sistema y del proceso general de titulación, con acceso al ingreso. |

### Futuras o pendientes

- **Integración con el Servicio de Autenticación Centralizada (SAC/Apereo CAS) de la UNL:** solo está **documentada y preparada** (puerto de proveedor de identidad), **no implementada**. Ver [`docs/autenticacion/arquitectura-cas.md`](docs/autenticacion/arquitectura-cas.md).
- Fases 2 y 3 del proceso de titulación.
- Envío real de correos (requiere configurar SMTP).

---

## 3. Tecnologías

| Capa | Tecnologías (según `package.json`, `requirements*.txt` y Dockerfiles) |
|---|---|
| Frontend | React 19, TypeScript 5, Vite 8, React Router 7, TanStack Query 5 |
| Backend | Python 3.12, Django 5.2, Django REST Framework 3, drf-spectacular (OpenAPI 3) |
| Autenticación | JWT con `djangorestframework-simplejwt`; TOTP (RFC 6238) con `pyotp`; QR con `segno`; cifrado de secretos con `cryptography` (MultiFernet) |
| Base de datos | PostgreSQL 16 |
| Documentos | `reportlab` (generación de PDF) |
| Infraestructura | Docker, Docker Compose, Nginx, Gunicorn (imagen de producción) |
| Pruebas | pytest + pytest-django; Vitest + Testing Library + MSW + vitest-axe |
| Calidad y seguridad | ESLint, Prettier, flake8, black, isort, mypy; GitHub Actions con gitleaks (`.github/workflows/`) |

---

## 4. Arquitectura

**Monolito modular** con arquitectura hexagonal en el backend (`domain`, `ports`, `services`, `adapters` por módulo) y una SPA en React.

```
navegador ──► nginx :8000 ──┬─► /, /login, /bandeja/…    → frontend React compilado
                            ├─► /api/, /admin/, /health/  → backend Django
                            └─► /static/, /media/          → backend Django
                                         │
                                         └─► PostgreSQL 16 (red interna de Docker)
```

- **Frontend.** SPA servida por Nginx. Cualquier ruta que no sea del backend devuelve `index.html`, para que React Router resuelva las rutas.
- **Backend.** API REST bajo `/api/v1/`. Los PDF del trámite son privados: solo se entregan por la API autenticada.
- **Comunicación.** Mismo origen (`http://localhost:8000`). El frontend envía el JWT en `Authorization: Bearer`. La cookie de dispositivo de confianza es `HttpOnly` y solo viaja a `/api/v1/auth/`.
- **Autenticación.** Ocurre en dos pasos y en ningún caso se emite un JWT sin el segundo factor; ver [§6](#6-guía-de-ingreso-al-sistema) y [`docs/autenticacion/flujo-autenticacion.md`](docs/autenticacion/flujo-autenticacion.md).
- **Autorización.** Los roles se leen de la base de datos local (`UserRole`) y se evalúan en el servidor en cada operación. La interfaz solo decide a qué pantalla redirigir.
- **Contenedores** (`docker-compose.yml`): `db` (PostgreSQL 16), `backend` (Django, `runserver` en desarrollo) y `nginx` (frontend compilado + proxy, puerto **8000**).

### Estructura del repositorio (resumen)

```
.
├── backend/
│   ├── src/
│   │   ├── config/            # settings (base, local, production, test), urls
│   │   ├── core/              # adaptadores comunes: PDF, almacenamiento, IP, logging, errores
│   │   └── apps/
│   │       ├── authentication/   # usuarios, roles, RBAC, login, 2FA, recuperación
│   │       ├── expedientes/      # expediente, estados, plazos, bandeja
│   │       ├── peticiones/       # peticiones a dependencias y documentos PDF
│   │       ├── verificacion/     # checklist, observaciones, subsanación
│   │       ├── resoluciones/     # informe de aptitud y declaratoria
│   │       └── notificaciones/   # notificaciones internas y auditoría
│   ├── tests/                 # pruebas transversales
│   ├── openapi.yaml           # contrato de la API (se valida en CI)
│   └── .env.example           # variables del backend documentadas
├── frontend/
│   └── src/
│       ├── app/               # router y proveedores
│       ├── auth/              # contexto de sesión, guardas, redirección por rol
│       ├── api/               # cliente HTTP y endpoints
│       ├── components/        # UI kit y layout
│       └── features/          # landing, auth, dashboard, solicitud, expediente, peticiones, bandeja…
├── nginx/nginx.conf           # proxy y fallback de la SPA (desarrollo)
├── docs/                      # documentación técnica (incluye docs/autenticacion/)
├── SIAAF-KNOWLEDGE/           # bóveda de conocimiento del proyecto
├── sgt-siaaf/specs/           # especificaciones
├── scripts/                   # utilidades (versionado COSMOS, E2E de autenticación)
├── Dockerfile                 # imagen del backend (development / production)
├── docker-compose.yml         # entorno de desarrollo
└── docker-compose.prod.yml    # entorno de producción
```

---

## 5. Instalación y ejecución local

### 5.1 Requisitos previos

- Docker y el plugin Docker Compose (`docker compose`).
- Git.
- Puerto **8000** libre en el equipo.

### 5.2 Clonar el repositorio

```bash
git clone git@github.com:R0yalCode/sistema-titulacion-unl.git
cd sistema-titulacion-unl
```

### 5.3 Variables de entorno

Docker Compose lee un archivo **`.env` en la raíz** del repositorio (no versionado). Créelo con estas variables, que son las que usa `docker-compose.yml`:

```dotenv
# Obligatorias: docker compose no arranca sin ellas
POSTGRES_PASSWORD=<contraseña de la base de datos de desarrollo>
SECRET_KEY=<cadena aleatoria larga>
JWT_SIGNING_KEY=<otra cadena aleatoria, distinta de SECRET_KEY>

# Opcionales (valor por defecto entre paréntesis)
POSTGRES_DB=sgt_siaaf          # (sgt_siaaf)
POSTGRES_USER=sgt_user         # (sgt_user)
DEBUG=1                        # (1)
# VITE_API_BASE_URL=http://localhost:8000   # URL de la API compilada en el frontend
```

Para generar valores aleatorios:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

> En desarrollo (`config.settings.local`), si no se define `MFA_ENCRYPTION_KEYS`, la clave de cifrado de los secretos TOTP se **deriva de `SECRET_KEY`**. Si cambia `SECRET_KEY`, los autenticadores ya registrados dejan de poder validarse y deben registrarse de nuevo. En producción esa clave es obligatoria e independiente ([§10](#10-configuración-y-seguridad)).

### 5.4 Construir y levantar los servicios

```bash
docker compose up --build -d
docker compose ps        # db (healthy), backend y nginx en ejecución
```

`--build` recompila también el frontend dentro de la imagen de `nginx`: no se usa `frontend/dist` del equipo.

### 5.5 Aplicar las migraciones

En desarrollo el contenedor `backend` arranca con `runserver` y **no** aplica migraciones automáticamente. Ejecútelas tras el primer arranque y después de cada actualización que incluya migraciones:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py showmigrations authentication   # todas marcadas con [X]
```

> La imagen de producción (`docker-compose.prod.yml`, `target: production`) sí ejecuta `migrate` al arrancar mediante `backend/entrypoint.sh`.

### 5.6 Crear una cuenta para ingresar

El acceso requiere una **cuenta habilitada con correo institucional y un rol asignado**. En un entorno nuevo:

1. Cree un administrador de Django (le pedirá usuario, correo y contraseña):
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```
2. Entre en `http://localhost:8000/admin/` con ese usuario.
3. Si la tabla de roles está vacía, cree los roles necesarios en **Roles**. Los nombres válidos son los de [§9](#9-roles-y-permisos).
4. Cree o edite las cuentas en **Users**:
   - correo **`@unl.edu.ec`** (es el dato de ingreso);
   - rol en la sección de roles del usuario.
   - Para el rol de estudiante o de carrera, registre también la carrera o facultad que corresponda.
5. Defina **siempre** la contraseña desde la terminal, porque el formulario de usuarios del admin no la cifra:
   ```bash
   docker compose exec backend python manage.py changepassword <usuario>
   ```

> El correo de cada cuenta debe ser único. Una cuenta sin rol reconocido llega a la pantalla «No habilitado». El superusuario creado en el paso 1 también necesita un rol (por ejemplo `ADMINISTRADOR`) para usar la aplicación.

### 5.7 Verificar que funciona

| Recurso | URL |
|---|---|
| Página pública | http://localhost:8000/ |
| Ingreso | http://localhost:8000/login |
| Estado del backend | http://localhost:8000/health/ → `{"status": "ok"}` |
| Documentación de la API (Swagger) | http://localhost:8000/api/v1/docs/ |
| Administración de Django | http://localhost:8000/admin/ |

```bash
curl -s http://localhost:8000/health/                                    # {"status": "ok"}
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/login      # 200 (React)
```

> Abra la aplicación en **http://localhost:8000**, no en `http://127.0.0.1:8000`: el navegador los trata como orígenes distintos y las llamadas a la API pueden fallar.

### 5.8 Operaciones habituales

```bash
docker compose up --build -d nginx      # recompilar solo el frontend (no toca la base de datos)
docker compose up --build -d backend    # reconstruir el backend tras cambios de código
docker compose logs -f backend          # ver el log del backend (incluye los correos en desarrollo)
docker compose restart nginx            # tras editar nginx/nginx.conf (está montado desde el equipo)
```

---

## 6. Guía de ingreso al sistema

### Paso 1 — Correo institucional

En `http://localhost:8000/login`, el campo se llama **«Nombre de usuario»**, igual que en el SAC de la UNL. Lo que debe escribir en él es su **correo institucional completo**:

```
usuario@unl.edu.ec
```

- Solo se admite el dominio `@unl.edu.ec`. Se rechazan Gmail, Hotmail, `unl.edu`, subdominios u otros dominios, y se muestra «Ingrese un correo institucional válido (@unl.edu.ec).».
- No importan las mayúsculas ni los espacios al inicio o al final.
- Si deja el campo vacío, verá «El nombre de usuario es un campo requerido.».

### Paso 2 — Contraseña

Escriba la contraseña de su cuenta. Si el campo está vacío verá «La contraseña es un campo requerido.».

Si el correo o la contraseña no son correctos, el sistema responde **«Usuario o contraseña incorrectos.»** sin indicar cuál de los dos falló. Tras **5 intentos por minuto** desde la misma red se muestra «Demasiados intentos…»; espere un momento.

### Paso 3 — Primer ingreso: configurar el segundo factor

Si su cuenta aún no tiene segundo factor, aparece **«Configurar verificación en dos pasos»** con un **código QR**:

1. Abra **Google Authenticator** en su teléfono (instalación en [§7](#7-google-authenticator-instrucciones-para-el-usuario)).
2. Toque **«+»** y elija **«Escanear un código QR»**.
3. Escanee el QR que muestra SGT-SIAAF.
4. La aplicación registra la cuenta **SGT-SIAAF UNL** con su usuario.
5. Google Authenticator empieza a generar códigos de **6 dígitos**.
6. Escriba en SGT-SIAAF el código que muestra la aplicación y pulse **«Verificar y activar»**.
7. Si lo desea, marque **«Confiar en este dispositivo durante 5 días»** (no lo haga en equipos compartidos).
8. Aparecen **10 códigos de recuperación**. **Guárdelos ahora**: no se volverán a mostrar. Marque «Guardé mis códigos…» y pulse **«Continuar al sistema»**.

> ⚠️ **El código QR debe escanearse con Google Authenticator; no debe copiarse como si fuera una contraseña.** Contiene la clave secreta que vincula su cuenta con su teléfono: trátelo como información **confidencial**, no lo fotografíe ni lo comparta. Si no puede escanearlo, la opción «¿No puede escanear el código?» muestra una clave para introducirla a mano en la aplicación («Ingresar una clave de configuración», tipo *basada en el tiempo*). Esa clave es igual de confidencial.

El QR solo vale para ese intento de ingreso: la verificación caduca a los **5 minutos**. Si caduca, vuelva a iniciar sesión y se mostrará un QR nuevo.

### Paso 4 — Ingresos siguientes: código TOTP

En cada ingreso posterior, tras la contraseña, aparece **«Verificación de seguridad (2FA)»**:

1. Abra Google Authenticator.
2. Busque la cuenta **SGT-SIAAF UNL**.
3. Lea el código vigente de 6 dígitos.
4. Escríbalo en SGT-SIAAF y pulse **«Verificar»**.

Los códigos cambian cada **30 segundos** (`TOTP_INTERVAL = 30`). El servidor tolera un periodo de diferencia de reloj hacia cada lado (`MFA_TOTP_VALID_WINDOW = 1`). Cada código se acepta **una sola vez**.

**Límites de intentos:**

- Tras **5 códigos erróneos** en el mismo intento, debe volver a escribir la contraseña.
- Tras **10 fallos en 15 minutos**, la cuenta queda bloqueada temporalmente para el segundo factor.

Si marcó «Confiar en este dispositivo», durante **5 días** ese navegador no pedirá el código. **Cerrar sesión revoca esa confianza**; la caducidad de la sesión no la revoca.

### Paso 5 — Acceso al panel

Con los dos factores verificados:

1. El backend emite la sesión (JWT, vigencia de **30 minutos**; luego debe volver a ingresar).
2. Los permisos se obtienen de los **roles asignados en SGT-SIAAF**: base de datos local y matriz RBAC. **No** se consultan al SAC.
3. El sistema le dirige a su pantalla:
   - **Estudiante** → `/estudiante` (panel del estudiante).
   - **Roles operativos** → `/bandeja` (bandeja de expedientes).
   - **Cuenta sin rol habilitado** → `/no-habilitado`.

---

## 7. Google Authenticator: instrucciones para el usuario

**Qué es.** Una aplicación gratuita de Google que genera códigos temporales de 6 dígitos. Es **externa** a SGT-SIAAF: el sistema no se comunica con Google. Ambos comparten un secreto al escanear el QR y calculan el mismo código con el estándar **TOTP (RFC 6238)**; el servidor de SGT-SIAAF valida el código.

**Para qué se usa.** Es el segundo factor: aunque alguien conozca su contraseña, no puede ingresar sin su teléfono.

**Instalación** (solo desde las tiendas oficiales):

- Android: [Google Play — Google Authenticator](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2)
- iPhone: [App Store — Google Authenticator](https://apps.apple.com/us/app/google-authenticator/id388497605)

**Agregar la cuenta.** Abra la app, toque **«+»**, elija **«Escanear un código QR»** y apunte al QR de SGT-SIAAF ([§6, paso 3](#paso-3--primer-ingreso-configurar-el-segundo-factor)).

**Consultar el código.** Abra la app y busque **SGT-SIAAF UNL**. El círculo junto al código indica el tiempo que le queda.

**Si el código no es aceptado:**

- Use el código **actual**. Si está a punto de cambiar, espere al siguiente.
- Active la **fecha y hora automáticas** del teléfono. Un reloj desfasado produce códigos inválidos.
- Compruebe que usa la cuenta **SGT-SIAAF UNL** correcta. Si registró el sistema más de una vez, borre las entradas antiguas.
- Si vuelve a la pantalla de ingreso con «La verificación caducó…», escriba de nuevo su contraseña.

**Si cambia o pierde el teléfono:**

- **Con un código de recuperación:** en la pantalla del código, elija «¿Perdió su teléfono? Use un código de recuperación». El autenticador anterior queda anulado y se le pide registrar uno nuevo.
- **Sin códigos:** use el restablecimiento del doble factor ([§8](#82-restablecimiento-del-segundo-factor-2fa)).
- **Al cambiar de teléfono teniendo el antiguo:** use un código de recuperación o el restablecimiento para registrar el nuevo.

---

## 8. Recuperación de contraseña y del segundo factor

### 8.1 Recuperación de contraseña

1. En `/login`, pulse **«Restablecer contraseña»** (ruta `/recuperar-contrasena`).
2. Escriba el **correo registrado** en su cuenta.
3. El sistema responde siempre con el mismo mensaje, exista o no la cuenta.
4. Si la cuenta existe y está activa, se envía un enlace a `/restablecer-contrasena?uid=…&token=…`:
   - es válido **1 hora** (`PASSWORD_RESET_TIMEOUT`);
   - sirve **una sola vez**.
5. Defina la nueva contraseña, que debe cumplir la política de Django.
6. Al cambiar la contraseña se **revoca la confianza de todos sus dispositivos**: el siguiente ingreso pedirá el código TOTP.

Límite: 10 solicitudes por hora desde la misma red.

### 8.2 Restablecimiento del segundo factor (2FA)

Para cuando no tiene el teléfono **ni** sus códigos de recuperación:

1. En `/login`, pulse **«RESTABLECER DOBLE FACTOR DE AUTENTICACIÓN (2FA)»** (ruta `/restablecer-2fa`).
2. Complete:
   - **correo institucional** (solo `@unl.edu.ec`);
   - **número de cédula** (10 dígitos);
   - **contraseña actual**.
3. Pulse «Restablecer el doble factor de autenticación (2FA)». La respuesta es **siempre la misma**, para no revelar si los datos coinciden.
4. **Estos datos no retiran el 2FA por sí solos.** Si coinciden con una cuenta con 2FA activo, se envía al correo registrado un **enlace de un solo uso**. Es válido 1 hora y deja de valer si cambia la contraseña.
5. Abra el enlace (`/restablecer-2fa/confirmar`) y pulse **«Confirmar restablecimiento»**. Se retiran:
   - el autenticador anterior;
   - los códigos de recuperación;
   - la confianza de todos sus dispositivos.
6. Inicie sesión de nuevo: el sistema mostrará un **QR nuevo** para registrar Google Authenticator. En la app, borre la entrada antigua de SGT-SIAAF.

**Restricciones:**

- **Espera de 72 horas tras restablecer la contraseña** (`MFA_RESET_COOLDOWN_HOURS`). Si restableció la contraseña por correo, durante 72 h no se acepta el restablecimiento del 2FA por el mismo canal. Así, quien solo controle el buzón no puede anular ambos factores.
- Límite: 10 solicitudes por hora desde la misma red.
- Todas las operaciones quedan auditadas, sin guardar correo, cédula, contraseña ni enlace.
- Si tampoco tiene acceso a su correo, un administrador puede usar la acción **«Restablecer doble factor (2FA)»** en `/admin/` tras verificar su identidad por un canal institucional. El procedimiento formal está pendiente de definición por la UNL.

### 8.3 Correos: desarrollo frente a producción

- **Desarrollo (configuración actual de `docker-compose.yml`):** no se envían correos. El backend usa `django.core.mail.backends.console.EmailBackend`, así que **el mensaje, con su enlace, se escribe en el log del backend**:
  ```bash
  docker compose logs backend | grep -A20 "Subject:"
  ```
- **Producción:** configure un proveedor SMTP institucional con `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` y `DEFAULT_FROM_EMAIL`. Configure también `FRONTEND_BASE_URL` (origen público con el que se construyen los enlaces). **Sin SMTP configurado no se envía ningún correo.**
- **Pendiente de la UNL:** la referencia del SAC envía el enlace del 2FA al «correo personal»; SGT-SIAAF solo almacena el correo institucional, que es a donde lo envía hoy.

---

## 9. Roles y permisos

Roles definidos en `backend/src/apps/authentication/adapters/models.py`. Permisos según `RBAC_MATRIX` (`adapters/permissions.py`), con denegación por defecto:

| Rol | Pantalla | Puede (API) |
|---|---|---|
| `ESTUDIANTE` | `/estudiante` | Crear su expediente, verlo y enviarlo; crear peticiones y solicitar certificados; cargar y descargar sus documentos; subsanar requisitos observados; sus notificaciones |
| `SECRETARIA_CARRERA` | `/bandeja` | Ver expedientes de su carrera; cargar y descargar documentos de peticiones asignadas; subsanar requisitos de su carrera; notificaciones de su carrera |
| `SECRETARIO_ABOGADO` | `/bandeja` | Ver expedientes de su facultad; iniciar la verificación; ver y evaluar el checklist; observar expedientes; emitir el informe de aptitud; documentos asignados; notificaciones |
| `ANALISTA_APOYO` | `/bandeja` | Ver expedientes de su facultad; ver el checklist y evaluarlo en borrador; preparar el informe en borrador; documentos asignados; notificaciones |
| `DECANO` | `/bandeja` | Ver expedientes de su facultad; registrar la declaratoria de aptitud; notificaciones |
| `DIRECTOR_CARRERA` | `/bandeja` | Ver expedientes de su carrera; documentos asignados; notificaciones |
| `ADMINISTRADOR` | `/bandeja` | Acceso completo de lectura; crear expedientes y peticiones; checklist; catálogo de requisitos; notificaciones |
| `RESPONSABLE_DEPENDENCIA` | `/no-habilitado` | **Aún sin acceso funcional:** el rol existe, pero la matriz RBAC no le concede ninguna operación (brecha conocida) |

El backend comprueba el rol **en cada petición**. Ocultar un botón en la interfaz no concede ni retira permisos.

---

## 10. Configuración y seguridad

Todas las variables están documentadas, sin valores secretos, en [`backend/.env.example`](backend/.env.example). Nunca versione archivos `.env` ni copie en ellos valores reales de otros entornos.

| Variable | Uso |
|---|---|
| `SECRET_KEY` | Firma de Django (sesiones, CSRF, enlaces de recuperación). Obligatoria. |
| `JWT_SIGNING_KEY` | Firma de los JWT. Obligatoria y **distinta** de `SECRET_KEY`. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Base de datos en Compose (el backend las recibe como `DB_NAME`, `DB_USER` y `DB_PASSWORD`). |
| `ALLOWED_HOSTS` | Hosts admitidos por Django (obligatoria en producción). |
| `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | Orígenes permitidos. Solo se configuran en producción; en desarrollo todo es mismo origen. |
| `TRUSTED_PROXIES` | Proxies de confianza para obtener la IP real (límites de intentos y auditoría). |
| `MFA_ENCRYPTION_KEYS` | Claves Fernet para cifrar los secretos TOTP en reposo. Admite varias separadas por comas: la primera cifra y todas descifran. |
| `MFA_TRUSTED_DEVICE_DAYS`, `MFA_CHALLENGE_*`, `MFA_USER_*`, `MFA_THROTTLE_RATE`, `MFA_RESET_COOLDOWN_HOURS` | Política del 2FA (valores por defecto en `.env.example` y `config/settings/base.py`). |
| `AUTH_THROTTLE_RATE`, `PASSWORD_RESET_THROTTLE_RATE`, `PASSWORD_RESET_TIMEOUT` | Límites de intentos y vigencia de los enlaces. |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `FRONTEND_BASE_URL` | Envío de correos ([§8.3](#83-correos-desarrollo-frente-a-producción)). |

**Sesión.** JWT `access` de 30 minutos. No existe renovación automática: al expirar, se vuelve a ingresar. El cierre de sesión no invalida en el servidor un JWT ya emitido, que caduca por tiempo.

**Clave de cifrado del 2FA en producción.** `docker-compose.prod.yml` exige `MFA_ENCRYPTION_KEYS`. Genere una clave **independiente** de `SECRET_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Para rotarla:

1. Anteponga la clave nueva: `MFA_ENCRYPTION_KEYS=<nueva>,<anterior>`.
2. Reinicie el servicio.
3. Ejecute `python manage.py rotate_mfa_keys`.
4. Retire la clave anterior.

Si se pierde una clave en uso, los autenticadores que cifraba deben registrarse de nuevo. Detalle en [`docs/autenticacion/politica-2fa.md`](docs/autenticacion/politica-2fa.md).

**Desarrollo frente a producción:**

| | Desarrollo (`docker-compose.yml`) | Producción (`docker-compose.prod.yml`) |
|---|---|---|
| Settings | `config.settings.local` (`DEBUG`) | `config.settings.production` |
| Servidor | `runserver`, migraciones manuales | Gunicorn, `migrate` automático en el arranque |
| HTTPS y cookies | HTTP local; cookie de confianza sin `Secure` | HTTPS obligatorio, HSTS, cookies `Secure` |
| Clave del 2FA | Derivada de `SECRET_KEY` si falta | `MFA_ENCRYPTION_KEYS` obligatoria |
| Correo | Consola (log del backend) | SMTP a configurar |

**Controles implementados:**

- Contraseñas con los hashers de Django.
- Límites de intentos por IP y bloqueo del 2FA por cuenta.
- Secretos TOTP cifrados.
- Retos, tokens de confianza y códigos de recuperación guardados solo como hash.
- Filtro que enmascara datos sensibles en los logs.
- RBAC con filtrado por ámbito (evita accesos a expedientes ajenos).
- PDF validados (cabecera `%PDF-`, SHA-256, ≤ 10 MB) y almacenados de forma privada.
- Auditoría de eventos del trámite y de autenticación.
- Escaneo de secretos con gitleaks en CI.

---

## 11. Pruebas y calidad

### Backend

CI (`.github/workflows/ci.yml`) ejecuta las pruebas desde `backend/` con Python 3.12, SQLite en memoria (`config.settings.test`) y claves desechables:

```bash
cd backend
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
export JWT_SIGNING_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
export DB_PASSWORD=ci
python -m pytest -ra src/apps src/core tests
```

Cubren:

- el dominio y los servicios de cada módulo;
- el RBAC y el aislamiento por ámbito;
- la máquina de estados y los plazos;
- los documentos PDF;
- la autenticación: correo institucional, TOTP, ventana temporal, reutilización de códigos, límites, cifrado, dispositivo de confianza, recuperación y restablecimiento del 2FA;
- el flujo completo del trámite.

> No ejecute `pytest` dentro del contenedor `backend` de desarrollo: la imagen no incluye `backend/conftest.py` ni `backend/tests/`, y su `DJANGO_SETTINGS_MODULE` apunta a PostgreSQL.

### Frontend

Con Node 24 (versión usada en `frontend/Dockerfile` y en CI):

```bash
cd frontend
npm ci
npm run lint        # ESLint (incluye reglas de accesibilidad jsx-a11y)
npm run typecheck   # TypeScript
npm run test        # Vitest + Testing Library + MSW + vitest-axe
npm run build
```

Cubren:

- formularios y mensajes de validación;
- flujo de ingreso con 2FA y restablecimiento;
- guardas de ruta y redirección por rol;
- vistas del trámite;
- accesibilidad automática con axe.

### E2E de autenticación

`scripts/e2e/e2e_mfa.py` recorre por HTTP el flujo completo contra un backend en ejecución. Calcula los códigos TOTP igual que Google Authenticator. Las instrucciones están en la cabecera del script.

> **Referencia de una ejecución concreta (2026-11-18):** backend 889 aprobadas y 13 omitidas; frontend 475/475. Las cifras cambian con el proyecto: ejecute las pruebas para conocer el estado actual.

---

## 12. API

Documentación interactiva: http://localhost:8000/api/v1/docs/ (Swagger), http://localhost:8000/api/v1/redoc/ (ReDoc), esquema en http://localhost:8000/api/v1/schema/. El contrato versionado es [`backend/openapi.yaml`](backend/openapi.yaml).

| Grupo | Endpoints (prefijo `/api/v1/`) |
|---|---|
| Autenticación | `auth/login/`, `auth/mfa/setup/`, `auth/mfa/setup/confirm/`, `auth/mfa/verify/`, `auth/mfa/recovery/`, `auth/mfa/reset/`, `auth/mfa/reset/confirm/`, `auth/logout/`, `auth/password-reset/`, `auth/password-reset/validate/`, `auth/password-reset/confirm/` |
| Expedientes | `expedientes/`, `expedientes/bandeja/`, `expedientes/{id}/`, `expedientes/{id}/enviar/`, `expedientes/{id}/iniciar-verificacion/`, `expedientes/{id}/observar/` |
| Peticiones | `peticiones/{id}/solicitar-emision/`, `peticiones/{id}/documento/`, `peticiones/{id}/documento/{version}/` |
| Verificación | `expedientes/{id}/checklist/`, `checklist/{id}/`, `checklist/{id}/subsanar/` |
| Resoluciones | `informes/`, `declaratorias/` |
| Notificaciones | `notificaciones/`, `notificaciones/{id}/marcar-leida/` |

Fuera de la API: `/health/` (estado) y `/admin/` (administración de Django).

---

## 13. Estado del proyecto y limitaciones

- **Autenticación local.** SGT-SIAAF valida correo y contraseña contra su propia base de datos. La pantalla de ingreso reproduce la apariencia del SAC de la UNL, pero **no es el SAC ni está integrada con él**.
- **Correo institucional validado en el backend**, no solo en la interfaz.
- **Segundo factor TOTP** propio de SGT-SIAAF (Google Authenticator), con secretos cifrados.
- **Autorización mediante RBAC local.** Los roles se asignan en SGT-SIAAF; no se obtienen del SAC.
- **Integración con SAC/CAS: pendiente.** Requiere el registro de SGT-SIAAF como servicio y la autorización institucional. La arquitectura está preparada y documentada en [`docs/autenticacion/arquitectura-cas.md`](docs/autenticacion/arquitectura-cas.md).
- **SMTP:** debe configurarse para que los correos se envíen en producción.
- **`MFA_ENCRYPTION_KEYS`:** debe configurarse antes de cualquier despliegue productivo.
- **Administración de Django (`/admin/`):** usa el inicio de sesión propio de Django (usuario y contraseña) y **no aplica el segundo factor**. Restrinja las cuentas `is_staff` y el acceso a esa ruta.
- **Contraseñas en el admin:** el formulario de usuarios de `/admin/` no cifra la contraseña. Defínala con `manage.py changepassword`.
- **Rol `RESPONSABLE_DEPENDENCIA`:** sin permisos en la matriz RBAC.
- **Fases 2 y 3 del proceso de titulación:** no implementadas.
- **Decisiones pendientes de la UNL:** canal del enlace de restablecimiento del 2FA, aceptación formal del procedimiento, alternativa presencial y uso de la identidad visual del SAC en un servicio aún no integrado.

---

## 14. Solución de problemas

| Problema | Qué hacer |
|---|---|
| `POSTGRES_PASSWORD is required` / `SECRET_KEY is required` | Defina la variable en el `.env` de la raíz ([§5.3](#53-variables-de-entorno)). |
| Errores de tablas inexistentes tras actualizar | `docker compose exec backend python manage.py migrate` |
| El frontend no refleja los cambios | `docker compose up --build -d nginx` |
| La API falla desde el navegador | Use `http://localhost:8000`, no `127.0.0.1`. |
| «Ingrese un correo institucional válido» | Use su correo completo `@unl.edu.ec`, no el nombre de usuario. |
| El código TOTP es rechazado | Hora automática en el teléfono, código vigente y cuenta correcta ([§7](#7-google-authenticator-instrucciones-para-el-usuario)). |
| «La verificación caducó…» | El reto dura 5 minutos o se agotaron los 5 intentos: vuelva a iniciar sesión. |
| No llega el correo de recuperación | En desarrollo no se envían correos: búsquelo con `docker compose logs backend`. |
| Tras cambiar `SECRET_KEY` en desarrollo el código nunca es válido | La clave del 2FA se deriva de `SECRET_KEY`: restablezca el 2FA ([§8.2](#82-restablecimiento-del-segundo-factor-2fa)) y registre de nuevo el autenticador. |
| La base de datos no arranca | `docker compose logs db` |

---

## 15. Licencia y autores

Distribuido bajo la licencia **MIT** (ver [`LICENSE`](LICENSE)).

### Autores

- [Royel Jima](https://github.com/R0yalCode)
- [Steeven Pardo](https://github.com/Dan1el17)
- [Mark Gonzalez](https://github.com/7777-C)
- [Juan Calopino](https://github.com/JuaaanCalopino)
- [Jimmy Ontaneda](https://github.com/JJOC3S)
