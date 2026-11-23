---
system: SGT-SIAAF
type: workflow
status: active
source: repository-config
last_verified: 2026-11-23
---

# Guía para colaboradores: obtener y ejecutar `develop`

> `main` es la rama predeterminada de GitHub y **no contiene la versión de trabajo**. Un `git clone` sin `-b develop` entrega una versión anterior. La referencia para desarrollar es **`develop`**.

## 1. Clonar `develop`

```bash
git clone -b develop https://github.com/R0yalCode/sistema-titulacion-unl.git
cd sistema-titulacion-unl
git branch --show-current     # develop
git rev-parse --short HEAD
git ls-remote origin refs/heads/develop
```

El commit local debe coincidir con el inicio del hash que muestra `git ls-remote`.

## 2. Actualizar un repositorio ya clonado

```bash
git fetch origin
git switch develop
git pull --ff-only origin develop
git rev-parse --short HEAD
```

Si Git rechaza el `pull`, hay cambios locales o commits propios. No use `reset --hard`: guarde su trabajo en una rama antes de continuar.

## 3. Crear `.env`

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

No comparta ni versione este archivo.

## 4. Levantar el entorno

Requiere Docker con Docker Compose y el puerto **8000** libre.

```bash
docker compose up --build -d
docker compose ps
docker compose exec backend python manage.py migrate
```

`db` debe aparecer como `healthy`, y `backend` y `nginx` en ejecución.

## 5. Cargar datos de desarrollo

Registre la identidad de la base **una vez**. Use el valor de `POSTGRES_DB` si no es `sgt_siaaf`.

```bash
docker compose exec backend python manage.py registrar_entorno_bd desarrollo --confirmar-base sgt_siaaf

read -rsp "Contraseña para las cuentas demo: " SEED_DEMO_PASSWORD; echo
docker compose exec -e SEED_DEMO_PASSWORD="$SEED_DEMO_PASSWORD" backend python manage.py seed_initial_data
unset SEED_DEMO_PASSWORD

docker compose exec backend python manage.py seed_mock_sga --asignar-ambito-personal
```

Las cuentas demo usan el correo `sgtdemo.<usuario>@unl.edu.ec`, por ejemplo `sgtdemo.estudiante_1@unl.edu.ec`. No son buzones reales. El dataset opcional de 80 cuentas está en [`dataset-sgt-siaaf.md`](../../docs/entorno-pruebas/dataset-sgt-siaaf.md).

> **Nunca** registre como desarrollo una base real ni use estos comandos con credenciales de producción.

## 6. Verificar

```bash
curl -s http://localhost:8000/health/                                # {"status": "ok"}
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/login # 200
```

Abra **http://localhost:8000** (no `127.0.0.1`), ingrese con una cuenta demo y configure Google Authenticator. Compruebe:

- `estudiante_1` llega a `/estudiante`.
- `secretario_abogado` llega a `/bandeja`.

## 7. Cuándo reconstruir con Docker

El código del backend y el frontend compilado se **copian dentro de las imágenes**. Actualizar Git no cambia lo que ejecuta un contenedor hasta reconstruir su imagen.

| Situación | Comando |
|---|---|
| Después de `git pull` o de cambiar código, dependencias o Dockerfile | `docker compose up --build -d` |
| Encender de nuevo sin cambios de código | `docker compose up -d` |
| Solo cambió el frontend | `docker compose up --build -d nginx` |
| Solo se editó `nginx/nginx.conf` | `docker compose restart nginx` |
| Hay migraciones nuevas | `docker compose exec backend python manage.py migrate` |

Si ve una versión antigua, compruebe la rama y el commit y reconstruya.

## 8. Qué puede perder datos

| Operación | Efecto |
|---|---|
| Reconstruir o recrear `backend` | **Borra los PDF cargados.** En desarrollo se guardan en `backend/src/media`, fuera del volumen, y sus registros quedan sin archivo |
| `docker compose down` | Elimina los contenedores y, con ellos, esos PDF. Conserva la base |
| `docker compose down -v` | **Elimina también la base de datos y los volúmenes** |

Si necesita conservar los PDF de desarrollo, cópielos antes de reconstruir:

```bash
docker compose cp backend:/app/backend/src/media ./respaldo-media
```

No versione esa carpeta. Tras borrar una base, repita las secciones 4 y 5.

## Relacionado

[[INITIAL_DATA]] · [[DOCKER]] · [[TROUBLESHOOTING]] · [[GIT_POLICY]]
