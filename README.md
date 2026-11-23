# SGT-SIAAF — Sistema de Gestión del Trámite de Titulación

**Universidad Nacional de Loja — Facultad de la Energía, las Industrias y los Recursos Naturales No Renovables (FEIRNNR)**
**Carrera de Computación — Asignatura: Desarrollo Basado en Plataformas (5.º ciclo)**

> **Estado:** prototipo académico en desarrollo. **No está listo para producción** ([§11](#11-estado-actual-y-limitaciones)).

---

## Contenido

1. [Presentación](#1-presentación)
2. [Funcionalidades](#2-funcionalidades)
3. [Arquitectura y tecnologías](#3-arquitectura-y-tecnologías)
4. [Instalación y ejecución](#4-instalación-y-ejecución)
5. [Datos iniciales y cuentas de prueba](#5-datos-iniciales-y-cuentas-de-prueba)
6. [Ingreso al sistema](#6-ingreso-al-sistema)
7. [Google Authenticator: instrucciones para el usuario](#7-google-authenticator-instrucciones-para-el-usuario)
8. [Pruebas](#8-pruebas)
9. [Estructura del repositorio](#9-estructura-del-repositorio)
10. [Documentación complementaria](#10-documentación-complementaria)
11. [Estado actual y limitaciones](#11-estado-actual-y-limitaciones)
12. [Licencia y autores](#12-licencia-y-autores)

---

## 1. Presentación

**SGT-SIAAF** es el Sistema de Gestión del Trámite de Titulación integrado al SIAAF de la Universidad Nacional de Loja (UNL).

El trámite de titulación exige reunir certificados de varias dependencias, verificarlos, observarlos, subsanarlos, emitir un informe y registrar una declaratoria. SGT-SIAAF lo organiza en un expediente digital único, con estados, plazos, documentos versionados y una bitácora de auditoría.

**Objetivos:**

- Centralizar el expediente de titulación y su documentación.
- Coordinar a los actores del trámite con permisos acotados a su rol y su ámbito.
- Dar seguimiento al estado y a los plazos del expediente.
- Proteger el acceso con correo institucional y un segundo factor.

**Alcance actual (Fase 1):** declaratoria de aptitud legal (Art. 235 del RRA-UNL).

`BORRADOR` → `ENVIADA` → `EN_VERIFICACION` ⇄ `OBSERVADA` → `INFORME_EMITIDO` → `DECLARADA_APTA` (además de `CANCELADA`)

Las fases de sustentación y cierre (tribunal, calificaciones, acta y registro del título) **no están implementadas**.

---

## 2. Funcionalidades

| Área | Implementado |
|---|---|
| **Acceso** | Correo `@unl.edu.ec` y contraseña, validados también en el backend |
| **Doble factor (2FA)** | TOTP con Google Authenticator, códigos de recuperación y dispositivo de confianza de 5 días |
| **Recuperación** | Enlaces de un solo uso para restablecer la contraseña o el 2FA |
| **Roles y permisos** | Matriz RBAC evaluada en el servidor, con filtrado por ámbito |
| **Trámite** | Expediente, peticiones de certificados, carga de PDF versionada, verificación, observación, subsanación, informe y declaratoria |
| **Perfil académico** | Consulta mediante **MockSGA, una simulación de desarrollo** |
| **Seguimiento** | Panel del estudiante, bandeja por rol y notificaciones internas |
| **Auditoría** | Bitácora de eventos del trámite y de autenticación, sin secretos |
| **Página pública** | Presentación del sistema y acceso al ingreso |

**No implementado:** adaptador real del SGA, integración con el SAC/CAS de la UNL y fases 2 y 3 del proceso.

---

## 3. Arquitectura y tecnologías

**Monolito modular** con arquitectura hexagonal en el backend y una SPA en React.

```
navegador ──► Nginx :8000 ──┬─► /, /login, /bandeja/…      → frontend React compilado
                            ├─► /api/, /admin/, /health/   → backend Django
                            └─► /static/                   → backend Django
                                        │
                                        └─► PostgreSQL 16 (red interna de Docker)
```

Los PDF del trámite son privados y solo se entregan por la API autenticada.

| Capa | Tecnologías |
|---|---|
| Frontend | React 19, TypeScript 5, Vite 8, React Router 7, TanStack Query 5 |
| Backend | Python 3.12, Django 5.2, Django REST Framework 3, drf-spectacular |
| Autenticación | JWT (`simplejwt`), TOTP (`pyotp`), QR (`segno`), cifrado con `cryptography` |
| Datos y documentos | PostgreSQL 16, `reportlab` |
| Infraestructura | Docker, Docker Compose, Nginx, Gunicorn (imagen de producción) |
| Calidad | pytest, Vitest, Testing Library, MSW, vitest-axe, ESLint, GitHub Actions, Safety, Bandit, Gitleaks |

| | Desarrollo | Pruebas | Producción |
|---|---|---|---|
| Configuración | `config.settings.local` | `config.settings.test` | `config.settings.production` |
| Ejecución | `docker-compose.yml` | pytest y Vitest | `docker-compose.prod.yml` |
| Servidor | `runserver` | — | Gunicorn |
| Migraciones | Manuales | Automáticas | Al arrancar |
| Fuente académica | MockSGA (simulación) | MockSGA (simulación) | Sin proveedor: responde 503 |
| Correo | Log del backend | Memoria | SMTP con TLS, obligatorio |

---

## 4. Instalación y ejecución

Esta guía prepara un entorno de **desarrollo local**. El despliegue de producción se describe en [`docs/08-infraestructura/despliegue.md`](docs/08-infraestructura/despliegue.md) y aún tiene condiciones pendientes.

### 4.1 Requisitos previos

- Git.
- Docker con el plugin Docker Compose (`docker compose`).
- Puerto **8000** libre.

### 4.2 Clonar `develop`

`main` es la rama predeterminada, pero la versión de trabajo está en **`develop`**. Indique siempre la rama:

```bash
git clone -b develop https://github.com/R0yalCode/sistema-titulacion-unl.git
cd sistema-titulacion-unl
git rev-parse --short HEAD
```

Para actualizar un repositorio ya clonado:

```bash
git fetch origin
git switch develop
git pull --ff-only origin develop
```

Después de actualizar, ejecute `docker compose up --build -d`: el código se copia dentro de las imágenes. Guía completa: [`GUIA_COLABORADORES.md`](SIAAF-KNOWLEDGE/15-GIT-AND-WORKFLOWS/GUIA_COLABORADORES.md).

### 4.3 Variables de entorno

Cree el archivo **`.env`** desde la plantilla y genere sus valores. No lo versione.

```bash
cp .env.example .env
python3 - <<'PY'
import pathlib, secrets
ruta = pathlib.Path(".env")
texto = ruta.read_text()
for clave in ("POSTGRES_PASSWORD", "SECRET_KEY", "JWT_SIGNING_KEY"):
    texto = texto.replace(f"{clave}=\n", f"{clave}={secrets.token_urlsafe(48)}\n")
ruta.write_text(texto)
PY
chmod 600 .env
```

> En desarrollo, la clave que cifra los secretos del 2FA se deriva de `SECRET_KEY`. Si cambia `SECRET_KEY`, cada usuario debe registrar de nuevo su autenticador.

### 4.4 Levantar los servicios y migrar

```bash
docker compose up --build -d
docker compose ps
docker compose exec backend python manage.py migrate
```

`db` debe aparecer como `healthy`, y `backend` y `nginx` en ejecución. En desarrollo, las migraciones **no** se aplican solas.

### 4.5 Verificar

```bash
curl -s http://localhost:8000/health/                                # {"status": "ok"}
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/login # 200
```

| Recurso | URL |
|---|---|
| Aplicación | http://localhost:8000/ |
| Ingreso | http://localhost:8000/login |
| API (Swagger) | http://localhost:8000/api/v1/docs/ |
| Administración de Django | http://localhost:8000/admin/ |

> Use **`localhost`**, no `127.0.0.1`. El navegador los trata como orígenes distintos y las llamadas a la API pueden fallar.

> ⚠️ **Documentos en desarrollo:** los PDF se guardan en `backend/src/media`, fuera del volumen `media_data`. **Recrear el contenedor `backend` borra los documentos cargados** y deja sus registros sin archivo. `docker compose down -v` elimina además la base de datos.

Operaciones habituales y solución de problemas: [`TROUBLESHOOTING.md`](SIAAF-KNOWLEDGE/08-OPERATIONS/TROUBLESHOOTING.md).

---

## 5. Datos iniciales y cuentas de prueba

> ⚠️ **Solo para el entorno de desarrollo local.**
> - **No los ejecute contra producción.**
> - Los datos académicos son **simulados** y no deben usarse como información real.
> - Las cuentas demo **no son cuentas institucionales** y sus correos no son buzones reales.
> - Use una contraseña exclusiva para la demo y no la escriba en la documentación.

Las pruebas automatizadas no necesitan esta carga, porque crean su propia base temporal.

El mecanismo recomendado son tres comandos de Django, que se ejecutan **en este orden** después de migrar:

| Orden | Comando | Qué crea |
|---|---|---|
| 1 | `registrar_entorno_bd desarrollo` | Identidad de la base. Se hace una vez por base |
| 2 | `seed_initial_data` | 8 cuentas demo, una por rol, y sus roles |
| 3 | `seed_mock_sga --asignar-ambito-personal` | Catálogo académico simulado (`MOCK-…`), perfil de `estudiante_1` y ámbito del personal demo |

El catálogo de los 5 requisitos del Art. 235 no necesita carga: lo crea la migración.

### 5.1 Ejecutar la carga

El primer comando exige escribir el nombre de la base (`sgt_siaaf` por defecto, o su `POSTGRES_DB`). `docker-compose.yml` no entrega `SEED_DEMO_PASSWORD` al backend, por lo que debe pasarse en el comando. Defina una contraseña propia:

```bash
docker compose exec backend python manage.py registrar_entorno_bd desarrollo --confirmar-base sgt_siaaf

read -rsp "Contraseña para las cuentas demo: " SEED_DEMO_PASSWORD; echo
docker compose exec -e SEED_DEMO_PASSWORD="$SEED_DEMO_PASSWORD" backend python manage.py seed_initial_data
unset SEED_DEMO_PASSWORD

docker compose exec backend python manage.py seed_mock_sga --asignar-ambito-personal
```

### 5.2 Cuentas generadas

El correo de cada cuenta es `sgtdemo.<usuario>@unl.edu.ec`.

| Usuario | Rol |
|---|---|
| `estudiante_1` | `ESTUDIANTE` |
| `secretaria_carrera` | `SECRETARIA_CARRERA` |
| `secretario_abogado` | `SECRETARIO_ABOGADO` |
| `analista_apoyo` | `ANALISTA_APOYO` |
| `decano_feirnnr` | `DECANO` |
| `director_computacion` | `DIRECTOR_CARRERA` |
| `responsable_practicas` | `RESPONSABLE_DEPENDENCIA` (sin permisos todavía) |
| `admin_sys` | `ADMINISTRADOR` (sin acceso a `/admin/`) |

Cada cuenta registra Google Authenticator en su primer ingreso.

### 5.3 Verificar la carga

```bash
docker compose exec backend python manage.py shell -c "
from apps.authentication.adapters.models import User
from apps.academico.adapters.models import Carrera, Facultad, PerfilSGASimulado
print('cuentas demo:', User.objects.filter(email__startswith='sgtdemo.').count())
print('facultades:', Facultad.objects.filter(codigo__startswith='MOCK-').count())
print('carreras:', Carrera.objects.filter(codigo__startswith='MOCK-').count())
print('perfiles:', PerfilSGASimulado.objects.filter(codigo_carrera='MOCK-COMPUTACION').count())
"
```

En una base nueva, el resultado esperado es 8 cuentas, 1 facultad, 2 carreras y 1 perfil.

### 5.4 Repetición y precauciones

- Ambos comandos son **idempotentes**: al repetirlos no duplican datos.
- Repetirlos **no restablece contraseñas** ni modifica el 2FA de las cuentas existentes.
- `seed_initial_data` **vuelve a asignar** el rol demo si se retiró, y lo asigna a cualquier cuenta existente con uno de esos nombres de usuario.
- Los seeders solo escriben en una base registrada como **desarrollo**. Rechazan antes de escribir una base de producción, sin registrar o que no se pueda verificar, también desde la imagen de desarrollo.
- ⚠️ **Registre como desarrollo solo una base local.** Hacerlo sobre una base real sin marca habilitaría la carga, y un superusuario de PostgreSQL puede alterar la marca.

Para entrar a `/admin/`, cree una cuenta aparte con `createsuperuser`. Ese procedimiento, los datos exactos que crea cada comando y las operaciones que eliminan datos están en [`INITIAL_DATA.md`](SIAAF-KNOWLEDGE/08-OPERATIONS/INITIAL_DATA.md).

---

## 6. Ingreso al sistema

1. Abra http://localhost:8000/login.
2. En **«Nombre de usuario»**, escriba su **correo institucional completo** (`usuario@unl.edu.ec`).
3. Escriba su contraseña.
4. Complete el segundo factor con Google Authenticator ([§7](#7-google-authenticator-instrucciones-para-el-usuario)).
5. El sistema le dirige a su pantalla:
   - **Estudiante:** `/estudiante`.
   - **Roles operativos:** `/bandeja`.
   - **Cuenta sin rol habilitado:** `/no-habilitado`.

La sesión dura **30 minutos**. Al caducar, debe ingresar de nuevo.

Guía completa, incluida la recuperación de contraseña: [`USER_ACCESS_GUIDE.md`](SIAAF-KNOWLEDGE/08-OPERATIONS/USER_ACCESS_GUIDE.md).

---

## 7. Google Authenticator: instrucciones para el usuario

**Qué es.** Una aplicación gratuita que genera códigos temporales de 6 dígitos. Es el segundo factor de su cuenta: aunque alguien conozca su contraseña, no puede ingresar sin su teléfono.

SGT-SIAAF no se comunica con Google. La aplicación y el sistema comparten una clave secreta al escanear el QR y calculan el mismo código con el estándar TOTP.

### Instalar la aplicación

Descárguela solo desde las tiendas oficiales:

- Android: [Google Play — Google Authenticator](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2)
- iPhone: [App Store — Google Authenticator](https://apps.apple.com/us/app/google-authenticator/id388497605)

### Activar la verificación en su primer ingreso

Tras escribir su correo y contraseña, aparece **«Configurar verificación en dos pasos»** con un código QR.

1. Abra **Google Authenticator** en su teléfono.
2. Toque **«+»** y elija **«Escanear un código QR»**.
3. Escanee el QR que muestra SGT-SIAAF. Se agregará la cuenta **SGT-SIAAF UNL**.
4. Escriba en SGT-SIAAF el código de **6 dígitos** que muestra la aplicación.
5. Si es su equipo personal, puede marcar **«Confiar en este dispositivo durante 5 días»**. No lo haga en equipos compartidos.
6. Pulse **«Verificar y activar»**.
7. Aparecen **10 códigos de recuperación**. **Guárdelos en un lugar seguro**, porque no se volverán a mostrar.
8. Marque **«Guardé mis códigos de recuperación en un lugar seguro»** y pulse **«Continuar al sistema»**.

> ⚠️ **El QR es confidencial.** Contiene la clave que vincula su cuenta con su teléfono. No lo fotografíe ni lo comparta.

**Si no puede escanearlo:** abra **«¿No puede escanear el código?»**. En la aplicación elija **«Ingresar una clave de configuración»**, use el nombre y la clave que muestra SGT-SIAAF, y seleccione el tipo **basada en el tiempo**. Esa clave es igual de confidencial.

El QR vale para ese intento de ingreso y caduca a los **5 minutos**. Si caduca, inicie sesión de nuevo para obtener otro.

### Ingresar con el código

1. Escriba su correo y contraseña.
2. Abra Google Authenticator y busque **SGT-SIAAF UNL**.
3. Escriba el código actual de 6 dígitos y pulse **«Verificar»**.

Los códigos cambian cada **30 segundos** y cada uno se acepta **una sola vez**.

Si marcó «Confiar en este dispositivo», ese navegador no pedirá el código durante 5 días. **Cerrar sesión revoca esa confianza**, y también la revocan cambiar la contraseña o restablecer el 2FA.

### Si el código no es aceptado

- Use el código **actual**. Si está a punto de cambiar, espere al siguiente.
- Active la **fecha y hora automáticas** del teléfono.
- Compruebe que usa la cuenta **SGT-SIAAF UNL** correcta y borre las entradas antiguas.
- Si aparece «La verificación caducó…», vuelva a escribir su contraseña.
- Tras **5 códigos erróneos** debe escribir de nuevo la contraseña.
- Tras **10 fallos en 15 minutos**, el segundo factor se bloquea temporalmente. Espere antes de reintentar.

### Si cambia o pierde el teléfono

**Con un código de recuperación:**

1. En la pantalla del código, elija **«¿Perdió su teléfono? Use un código de recuperación»**.
2. Escriba uno de sus códigos y pulse **«Usar código de recuperación»**.
3. El autenticador anterior y **todos sus códigos de recuperación** quedan anulados.
4. Escanee el QR nuevo y borre la entrada antigua de la aplicación.
5. Al terminar recibirá **10 códigos nuevos**. Guárdelos.

**Sin códigos de recuperación:**

1. En `/login`, pulse **«Restablecer doble factor de autenticación (2FA)»**.
2. Escriba su **correo institucional**, **número de cédula** y **contraseña actual**.
3. Pulse **«Restablecer el doble factor de autenticación (2FA)»**.
4. Si los datos son correctos, recibirá en su correo registrado un **enlace de un solo uso, válido 1 hora**. El mensaje en pantalla es siempre el mismo, para no revelar si los datos coinciden.
5. Abra el enlace y pulse **«Confirmar restablecimiento»**.
6. Inicie sesión, escanee el QR nuevo y borre la entrada antigua de la aplicación.
7. Guarde los **10 códigos nuevos**.

> Si restableció su **contraseña** por correo en las últimas **72 horas**, **no recibirá el enlace**, aunque la pantalla muestre el mensaje habitual. Espere a que pase ese plazo. Es una medida para que quien controle solo su buzón no pueda anular ambos factores.

**Sin acceso a su correo:** solicite ayuda a un administrador. Puede restablecer su 2FA desde `/admin/` tras verificar su identidad por un canal institucional. El procedimiento formal aún debe definirlo la UNL.

---

## 8. Pruebas

Estos comandos usan bases de prueba y no requieren el entorno Docker.

**Backend** (Python 3.12, SQLite en memoria):

```bash
cd backend
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
export JWT_SIGNING_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')
export MFA_ENCRYPTION_KEYS=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
export DB_PASSWORD=ci
python -m pytest -ra src/apps src/core tests
```

**Frontend** (Node 24):

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm run test
npm run build
```

La integración continua (`.github/workflows/`) añade pruebas con PostgreSQL 16, validación del contrato OpenAPI, Safety, Bandit y Gitleaks. Detalle: [`REGRESSION_TESTS.md`](SIAAF-KNOWLEDGE/05-EXECUTION/REGRESSION_TESTS.md).

---

## 9. Estructura del repositorio

```
.
├── backend/
│   ├── src/
│   │   ├── config/          # settings y URLs
│   │   ├── core/            # adaptadores comunes
│   │   └── apps/            # academico, authentication, expedientes,
│   │                        # notificaciones, peticiones, resoluciones, verificacion
│   ├── tests/               # pruebas transversales
│   └── openapi.yaml         # contrato de la API
├── frontend/src/            # SPA en React
├── nginx/                   # configuración de desarrollo y producción
├── docs/                    # documentación técnica
├── SIAAF-KNOWLEDGE/         # bóveda de conocimiento del proyecto
├── sgt-siaaf/specs/         # especificaciones
├── scripts/                 # versionado COSMOS y E2E de autenticación
├── Dockerfile               # imagen del backend
├── docker-compose.yml       # desarrollo
└── docker-compose.prod.yml  # producción
```

---

## 10. Documentación complementaria

| Tema | Documento |
|---|---|
| Mapa general del conocimiento | [`MASTER_INDEX.md`](SIAAF-KNOWLEDGE/00-CORE/MASTER_INDEX.md) |
| Estado del proyecto | [`CURRENT_STATE.md`](SIAAF-KNOWLEDGE/00-CORE/CURRENT_STATE.md) |
| Arquitectura | [`GENERAL_ARCHITECTURE.md`](SIAAF-KNOWLEDGE/01-ARCHITECTURE/GENERAL_ARCHITECTURE.md) |
| API | [`API_CONTRACTS.md`](SIAAF-KNOWLEDGE/01-ARCHITECTURE/API_CONTRACTS.md) · [`openapi.yaml`](backend/openapi.yaml) |
| Roles y permisos | [`PERMISSIONS_ROLES.md`](SIAAF-KNOWLEDGE/02-BACKEND/PERMISSIONS_ROLES.md) |
| Configuración y entornos | [`ENVIRONMENTS.md`](SIAAF-KNOWLEDGE/08-OPERATIONS/ENVIRONMENTS.md) · [`backend/.env.example`](backend/.env.example) |
| Docker y CI | [`DOCKER.md`](SIAAF-KNOWLEDGE/08-OPERATIONS/DOCKER.md) |
| Clonar y ejecutar `develop` | [`GUIA_COLABORADORES.md`](SIAAF-KNOWLEDGE/15-GIT-AND-WORKFLOWS/GUIA_COLABORADORES.md) |
| Datos iniciales | [`INITIAL_DATA.md`](SIAAF-KNOWLEDGE/08-OPERATIONS/INITIAL_DATA.md) |
| Dataset sintético | [`dataset-sgt-siaaf.md`](docs/entorno-pruebas/dataset-sgt-siaaf.md) |
| Guía de acceso | [`USER_ACCESS_GUIDE.md`](SIAAF-KNOWLEDGE/08-OPERATIONS/USER_ACCESS_GUIDE.md) |
| Solución de problemas | [`TROUBLESHOOTING.md`](SIAAF-KNOWLEDGE/08-OPERATIONS/TROUBLESHOOTING.md) |
| Política del 2FA | [`politica-2fa.md`](docs/autenticacion/politica-2fa.md) · [`flujo-autenticacion.md`](docs/autenticacion/flujo-autenticacion.md) |
| Arquitectura CAS (no implementada) | [`arquitectura-cas.md`](docs/autenticacion/arquitectura-cas.md) |
| MockSGA | [`perfil-academico-mock-sga.md`](docs/academico/perfil-academico-mock-sga.md) |
| Despliegue | [`despliegue.md`](docs/08-infraestructura/despliegue.md) |

---

## 11. Estado actual y limitaciones

El sistema es un prototipo funcional de la Fase 1. **No debe desplegarse como servicio real** hasta resolver estos puntos:

**Bloquean producción:**

- **SGA:** no existe conexión ni adaptador real. MockSGA es una simulación y está prohibida en producción. Sin proveedor, el perfil académico y la creación de expedientes responden 503.
- **Infraestructura:** faltan certificados y dominio reales, y backups de base de datos y documentos.
- **Correo:** la configuración SMTP se valida al arrancar y se probó con un servidor de ensayo, pero falta configurar y probar el **SMTP institucional**.
- **Validación:** falta probar el flujo completo a través del Nginx de producción en un navegador real.

**Limitaciones conocidas:**

- **SAC/CAS:** la autenticación es local. La pantalla de ingreso se inspira en el SAC, pero **no está integrada con él**.
- **`/admin/`:** usa el inicio de sesión de Django y **no aplica el segundo factor**. Su formulario no cifra contraseñas: defínalas con `manage.py changepassword`.
- **`RESPONSABLE_DEPENDENCIA`:** el rol existe, pero no tiene permisos en la matriz RBAC.
- **Subsanación:** el estudiante no dispone de un endpoint para descubrir el identificador del requisito observado.
- **Sesión:** cerrar sesión no invalida en el servidor un JWT ya emitido; este caduca a los 30 minutos.
- **Documentos en desarrollo:** no persisten al recrear el contenedor `backend` ([§4.5](#45-verificar)).
- **Fases 2 y 3** del proceso de titulación: no implementadas.

---

## 12. Licencia y autores

Distribuido bajo la licencia **MIT** (ver [`LICENSE`](LICENSE)).

### Autores

- [Royel Jima](https://github.com/R0yalCode)
- [Steeven Pardo](https://github.com/Dan1el17)
- [Mark Gonzalez](https://github.com/7777-C)
- [Juan Calopino](https://github.com/JuanCalopinoo)
- [Jimmy Ontaneda](https://github.com/JJOC3S)
