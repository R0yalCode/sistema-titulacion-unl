# Guía de preparación del entorno de desarrollo — SGT-SIAAF

**Proyecto:** SGT-SIAAF — Sistema de Gestión del Trámite de Titulación (UNL / FEIRNNR)
**Público:** desarrolladores que se incorporan al proyecto
**Verificada:** noviembre de 2026, sobre un entorno Ubuntu 26.04 LTS (x86_64)

Esta guía describe, de principio a fin, cómo preparar un entorno de desarrollo funcional
desde cero: base de datos, backend Django, Django Admin, Swagger UI y documentación
técnica con Quarto. Todos los comandos han sido validados en la puesta en marcha documentada.

---

## 1. Requisitos previos

| Requisito | Versión mínima | Verificación |
|---|---|---|
| Docker Engine | ≥ 24.0 (probado: 29.1.3) | `docker --version` |
| Docker Compose (plugin) | ≥ 2.20 (probado: 2.40.3) | `docker compose version` |
| Git | any (probado: 2.53.0) | `git --version` |
| Python 3 | ≥ 3.10 (solo para utilidades locales) | `python3 --version` |
| Quarto | ≥ 1.11 (probado: 1.11.9) | `quarto --version` |
| Puertos libres | **8000** (nginx→Django) | `ss -tlnp \| grep 8000` |

No es necesario instalar Python 3.12, PostgreSQL ni las dependencias de `requirements.txt`
en el equipo: todo se ejecuta dentro de contenedores construidos desde el `Dockerfile`
del repositorio (python:3.12-slim + Django 5.2 + dependencias).

## 2. Sistemas operativos compatibles

- **Ubuntu / Debian (Linux):** entorno de referencia de esta guía. Comandos `apt`.
- **Windows:** vía WSL2 con Docker Desktop (o Docker Engine dentro de WSL2).
- **macOS:** Docker Desktop.

Los comandos de Docker Compose son idénticos en los tres sistemas; solo cambia la forma
de instalar Docker y Quarto (véanse §3 y §12).

## 3. Instalación de Docker

### Ubuntu / Debian

Referencia oficial: <https://docs.docker.com/engine/install/ubuntu/>. Alternativa suficiente
para desarrollo: el paquete de la propia distribución (`docker.io` + plugin `docker-compose-v2`).
Verificación posterior:

```bash
docker --version && docker compose version && docker info
```

### Windows y macOS

Instalar **Docker Desktop** desde <https://www.docker.com/products/docker-desktop/> y
activar la integración con WSL2 (Windows). Verificar con los mismos comandos anteriores.

### Permisos de usuario

Si `docker info` falla con `permission denied`, añada su usuario al grupo `docker`:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

> ⚠️ **Aviso de seguridad:** pertenecer al grupo `docker` equivale en la práctica a tener
> privilegios de root en el equipo (es posible montar el sistema de archivos anfitrión
> desde un contenedor). Habilite el acceso únicamente a usuarios de desarrollo de confianza.

## 4. Preparación de variables de entorno

En la **raíz** del proyecto debe existir un archivo `.env` con estas cinco variables
(obligatorias para `docker compose`):

| Variable | Uso |
|---|---|
| `POSTGRES_DB` | Nombre de la base de datos (por defecto: `sgt_siaaf`) |
| `POSTGRES_USER` | Usuario de PostgreSQL (por defecto: `sgt_user`) |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL — **obligatoria**, sin valor por defecto |
| `SECRET_KEY` | Clave de Django — **obligatoria**, sin valor por defecto |
| `DEBUG` | `1` en desarrollo local |

Reglas:

1. **No** exponga las credenciales: nunca suba el `.env` al repositorio (ya está en `.gitignore`).
2. Si el archivo no existe, créelo localmente con valores generados por usted (no copie credenciales de otros integrantes).
3. Los valores de producción deben ser distintos de los de desarrollo y gestionarse con un gestor de secretos.

## 5. Levantamiento del sistema con Docker Compose

Desde la raíz del proyecto:

```bash
# validar la configuración (no ejecuta nada)
docker compose config

# construir imágenes y levantar los servicios en segundo plano
docker compose up -d --build

# comprobar estado
docker compose ps
```

Servicios definidos en `docker-compose.yml`:

| Servicio | Imagen | Función | Puertos |
|---|---|---|---|
| `db` | postgres:16 | Base de datos PostgreSQL 16 | 5432 solo interno (sin publicación) |
| `backend` | imagen local (`Dockerfile`) | Django 5.2 + DRF (`runserver`) | 8000 interno |
| `nginx` | nginx:1.24-alpine | Proxy inverso hacia `backend:8000` | **8000 publicado** en el anfitrión |

Detalles relevantes de la topología:

- `db` declara un `healthcheck` con `pg_isready`; `backend` no arranca hasta que `db` esté *healthy* (`condition: service_healthy`).
- El `Dockerfile` ejecuta el proceso como usuario no-root (`django`) y monta volúmenes `media_data` y `static_data`.
- Redes: `backend_net` (bridge, interna). PostgreSQL no está expuesto al anfitrión: úsese con `docker compose exec db psql …`, nunca desde fuera.
- Volúmenes con estado: `postgres_data`, `media_data`, `static_data`.

## 6. Verificación de PostgreSQL

```bash
# estado + healthcheck
docker compose ps db          # debe mostrar "Up ... (healthy)"

# servidor aceptando conexiones y versión
docker compose exec db pg_isready
```

Conectividad desde Django (comando de diagnóstico dentro del contenedor backend):

```bash
docker compose exec backend python manage.py shell -c \
  "from django.db import connection; cursor=connection.cursor(); cursor.execute('SELECT current_database()'); print(cursor.fetchone())"
```

Salida esperada: `('sgt_siaaf',)` (o el nombre que configurara). La base de datos se crea
automáticamente al primer arranque del contenedor `db` con las credenciales del `.env`.
**No** cree una segunda base de datos manually ni edite los volúmenes.

## 7. Ejecución de migraciones

```bash
# ¿quedan migraciones pendientes? (exit 0 = todo aplicado)
docker compose exec backend python manage.py migrate --check

# aplicar (solo si el paso anterior indica pendientes y la base es local)
docker compose exec backend python manage.py migrate

# catálogo completo de migraciones por app
docker compose exec backend python manage.py showmigrations
```

Estado esperado tras la primera puesta en marcha: ~30 migraciones
(`auth`, `admin`, `sessions`, `authentication`, `expedientes`, `peticiones`,
`verificacion`, `resoluciones`, `notificaciones`) que crean las 23 tablas del esquema.

> Nunca genere migraciones nuevas (`makemigrations`) desde un entorno de puesta en marcha:
> las migraciones ya están versionadas en `backend/src/apps/*/adapters/migrations/`.

## 8. Creación del superusuario

El proyecto usa un modelo propio `authentication.User` (extiende `AbstractUser`, añade
`cedula`, `carrera_id`, `facultad_id` y roles vía `UserRole`). El comando estándar de Django
funciona porque el manager del proyecto soporta `create_superuser` con los campos básicos.

```bash
docker compose exec backend python manage.py createsuperuser
```

El comando es **interactivo**: introduzca personalmente usuario, correo y contraseña (los
caracteres de la contraseña no se muestran al escribir). El campo `cedula` es opcional;
puede dejarse en blanco y asignarse después desde el Admin.

Otra vía, equivalente, para roles y catálogos operativos: el comando del proyecto
`seed_initial_data` (documentado en el `README.md`, raíz del proyecto) crea idempotentemente
las cuentas funcionales de demostración y el catálogo de roles. Úselo solo en entornos
académicos/desarrollo.

## 9. Acceso al Django Admin

| URL | Descripción |
|---|---|
| <http://localhost:8000/admin/> | Consola de administración (ADR-0009) |

Verificación funcional:

1. `/admin/` redirige a `/admin/login/` y muestra el formulario con `csrfmiddlewaretoken`.
2. Un envío con credenciales incorrectas responde HTTP 200 con el mensaje de error de Django (pipeline de autenticación activo).
3. El superusuario creado en §8 debe aparecer con `is_staff=True`, `is_superuser=True` en el Admin (`authentication → users`).

Modelos registrados en el Admin: `User`, `Role`, `UserRole` (con inlines de asignación de
roles y controles de solo lectura por perfil administrativo). La consola es de soporte:
el trámite se opera por la API, no desde el Admin.

## 10. Acceso a Swagger UI

| URL | Descripción |
|---|---|
| <http://localhost:8000/api/v1/docs/> | **Swagger UI** (interactiva) |
| <http://localhost:8000/api/v1/redoc/> | ReDoc (lectura) |
| <http://localhost:8000/api/v1/schema/> | Esquema OpenAPI 3.0.3 (YAML) |

Comprobaciones de Swagger UI: agrupación de endpoints, métodos HTTP, descripciones,
parámetros, esquemas de entrada/salida, códigos de error y esquema de seguridad JWT
(candado *Authorize* en cada operación). Para ejecutar solicitudes de prueba autenticadas,
obtenga el token en `POST /api/v1/auth/token/` y pulse *Authorize* con
`Bearer <access_token>`.

## 11. Identificación del esquema OpenAPI

- Herramienta: **drf-spectacular** (configurado en `backend/src/config/settings/base.py` y rutas en `backend/src/config/urls.py`).
- Endpoint dinámico: `GET /api/v1/schema/` — generado desde los ViewSets y serializers reales.
- Copia canónica versionada: `backend/openapi.yaml` (33113 bytes, OpenAPI 3.0.3, 16 rutas).

Reglas del proyecto:

1. **El contrato no se edita durante la puesta en marcha.** El esquema sirve desde la implementación.
2. Regenerar la copia versionada solo cuando exista un cambio aprobado en los endpoints:
   `docker compose exec backend python manage.py spectacular --file openapi.yaml`
3. Validación rápida sin entorno gráfico:
   `curl -s http://localhost:8000/api/v1/schema/ \| grep -c "openapi"` → debe devolver `1` (o alguna salida positiva).

## 12. Instalación de Quarto

Referencia oficial: <https://quarto.org/docs/download/>. Descargue siempre instaladores
publicados por `quarto.org` o el repositorio oficial `github.com/quarto-dev/quarto-cli`.

### Ubuntu / Debian (amd64)

```bash
# descarga de la versión estable vigente (sustituya la versión por la última publicada)
curl -L -o /tmp/quarto.deb \
  https://github.com/quarto-dev/quarto-cli/releases/download/v1.11.9/quarto-1.11.9-linux-amd64.deb

# instalación (requiere sudo)
sudo apt install /tmp/quarto.deb

# verificación
quarto --version && quarto check
```

### Windows

Instalador `.msi` oficial desde la página de descargas.

### macOS

Instalador `.pkg` oficial (o `brew install --cask quarto`).

`quarto check` puede informar *no detectados* LaTeX, R, Julia o Jupyter: son avisos
informativos. El sitio documental de SGT-SIAAF no usa celdas computacionales ni LaTeX,
así que no es necesario instalarlos para `render`/`preview`.

## 13. Renderizado de la documentación

El proyecto de documentación vive en `docs/` (`docs/_quarto.yml`, tipo: website).

```bash
# desde la raíz del proyecto
quarto render docs
```

Salida esperada: `Output created: docs/_site/index.html` con ~70 páginas HTML
(identificación, arquitectura, módulos, C4, API, base de datos, seguridad, indicadores,
infraestructura, calidad, auditoría y anexos). Los diagramas Mermaid se renderizan en el
navegador vía mermaid.js (configuración del sitio), por lo que aparecen al abrir las páginas.

Para validar el sitio generado sin abrirlo en el navegador:

```bash
cd docs/_site && python3 -m http.server 8491
# abrir http://localhost:8491/  y luego detener con Ctrl+C
```

## 14. Visualización de la documentación

```bash
# desde la raíz del proyecto; Ctrl+C para salir
quarto preview docs
```

Quarto publica el sitio (por defecto en `http://localhost:4200`) con recarga automática
al editar los fuentes en `docs/`.

## 15. Comandos frecuentes

```bash
# ── Ciclo de vida ──────────────────────────────────────────────
docker compose up -d --build          # construir y levantar
docker compose ps                     # estado de los servicios
docker compose logs -f backend        # logs en vivo del backend
docker compose logs --tail=100        # últimos 100 renglones de todos
docker compose stop                   # detener (conserva datos)
docker compose start                  # reanudar
docker compose restart backend        # reiniciar un servicio
docker compose down                   # detener y borrar redes/contenedores (MANTÉN volúmenes)

# ── Django (dentro del contenedor backend) ─────────────────────
docker compose exec backend python manage.py migrate                   # migraciones
docker compose exec backend python manage.py check                     # diagnóstico
docker compose exec backend python manage.py createsuperuser           # superusuario
docker compose exec backend python manage.py shell                     # consola interactiva
docker compose exec backend python manage.py spectacular --file openapi.yaml

# ── PostgreSQL (sin exponer puertos) ───────────────────────────
docker compose exec db psql -U sgt_user -d sgt_siaaf

# ── Documentación ─────────────────────────────────────────────
quarto check docs                     # diagnóstico del proyecto Quarto
quarto render docs                    # generar docs/_site
quarto preview docs                   # servir con recarga en vivo
```

## 16. Problemas comunes y soluciones

| Síntoma | Causa | Solución |
|---|---|---|
| `Bind for 0.0.0.0:8000 failed: port is already allocated` | Otro servicio (u otra pila de este proyecto) ya publica el 8000 | Identificar con `ss -tlnp \| grep 8000` y `docker ps --format '{{.Names}}\t{{.Ports}}'`; detener el proceso o contenedor ajeno (con autorización del propietario) y reintentar |
| Contenedor nginx sin puerto publicado tras un arranque fallido | El contenedor quedó en estado intermedio al fallar el *bind* | `docker compose up -d --force-recreate nginx` |
| `POSTGRES_PASSWORD is required` / `SECRET_KEY is required` | Falta el `.env` o sus claves obligatorias | Completar el `.env` de la raíz (§4) |
| `db` no pasa el healthcheck | PostgreSQL aún arrancando o el puerto 5432 interno ocupado por otro contenedor | `docker compose logs db`; esperar el reintento de `pg_isready` |
| Django: `AbstractUser...` o error de conexión a DB | `backend` arrancó antes que `db` o credenciales inconsistentes | Confirmar el `.env` y `docker compose restart backend` |
| 30 migraciones no aplicadas en el log del backend | Primera puesta en marcha | Aplicar `python manage.py migrate` (§7) |
| `connection refused` en `localhost:8000` | nginx detenido o sin publicación de puerto | `docker compose ps nginx`; recrear si no lista puertos |
| Swagger en blanco | Caché del navegador o schema sin respuesta | `curl -I http://localhost:8000/api/v1/schema/` |
| Mermaid no renderiza | Navegador sin JavaScript | Habilitar JS; los diagramas son client-side |

Nunca utilice `docker compose down -v` ni `docker system prune` en este proyecto sin
autorización explícita: borrarían volúmenes con datos de la base de documentos y media.

## 17. Detención planificada del proyecto

```bash
docker compose stop          # hábito recomendado: conserva contenedores, volúmenes y datos
```

La contraseña de PostgreSQL y el `SECRET_KEY` del `.env` persisten; al reanudar no hace
falta reconstruir nada. Si está seguro de querer retirar además contenedores y redes
(sin volúmenes):

```bash
docker compose down          # los volúmenes postgres_data/media_data/static_data permanecen
```

## 18. Volver a iniciar el proyecto

```bash
cd /home/.../sgt-siaaf
docker compose start         # si se detuvo con `stop`
# o, si se detuvo con `down`:
docker compose up -d
# comprobar:
docker compose ps
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/admin/login/   # 200 esperado
```

## 19. Consideraciones de seguridad

1. **Credenciales:** use solo valores personales en desarrollo; nunca reutilice credenciaales de otros integrantes ni las publique en chat/issue/documento.
2. **`.env` nunca se versiona** (ya excluido por `.gitignore`); comparta la estructura, no los valores.
3. **Django Admin (ADR-0009):** es consola interna de soporte; el trámite se opera por la API con RBAC server-side. No se eliminan controles de seguridad para facilitar el acceso.
4. **PostgreSQL no está publicado** al anfitrión: no añada mapeos de puertos de la base de datos a redes públicas.
5. **JWT:** los tokens se obtienen vía `POST /api/v1/auth/token/` (access 60 min, refresh 24 h); no los almacene en repositorios ni archivos de configuración.
6. **Grupo `docker`:** concede privilegios equivalentes a root (§3); conceda la membresía con criterio.
7. **Passwords generadas dinámicamente:** al crear superusuarios, hágalo en su terminal interactiva (§8) — nunca en scripts ni parámetros de línea de comandos.
8. **Producción:** cambie obligatoriamente `SECRET_KEY` y `POSTGRES_PASSWORD`, use HTTPS y gestion de secretos; `DEBUG=0`.

---

*Documento generado durante la puesta en marcha verificada del proyecto (noviembre de 2026).
Sin credenciales ni secretos. Las URL de referencia son locales y accesibles solo en desarrollo.*
