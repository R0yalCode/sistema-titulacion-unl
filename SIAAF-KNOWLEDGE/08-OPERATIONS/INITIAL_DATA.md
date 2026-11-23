---
system: SGT-SIAAF
type: operations
area: datos-iniciales
status: verified
source: verified-code
last_verified: 2026-11-23
---

# Datos iniciales y cuentas de prueba

> ⚠️ **Advertencias**
> - **No ejecutar contra producción.** Ninguna cuenta demo debe existir allí (C-012).
> - **No usar los datos simulados como información académica real.** SGT-SIAAF no tiene conexión con el SGA.
> - **No introducir contraseñas reales** en esta documentación, en archivos versionados ni como contraseña demo.
> - **No confundir las cuentas demo con cuentas institucionales.** Sus correos `sgtdemo.*@unl.edu.ec` no son buzones reales.
>
> **Verificación (2026-11-23):** la secuencia se ejecutó dos veces con PostgreSQL 16 desechable y la imagen de desarrollo, con el resultado de la sección 5. El rechazo se comprobó con la imagen de producción. No se ejecutó contra ninguna base real.

## Uso por entorno

| Entorno | Settings | `seed_initial_data` | `seed_mock_sga` | Indicación |
|---|---|---|---|---|
| **Desarrollo** | `config.settings.local` | Disponible; requiere `SEED_DEMO_PASSWORD` | Disponible | Único entorno para esta carga |
| **Pruebas** | `config.settings.test`, `test_postgres` | Lo ejecutan sus pruebas | Lo ejecutan sus pruebas | No requiere carga manual: pytest crea una base temporal |
| **Producción** | `config.settings.production` | **Rechazado antes de acceder a la base** | **Rechazado antes de acceder a la base** | Las cuentas reales no se crean con estos comandos |

## Protección en producción

Ambos comandos llaman a `exigir_entorno_de_demostracion` (`backend/src/core/adapters/entorno_demo.py`) antes de leer la contraseña o abrir la base. Solo continúan si se cumplen las dos condiciones:

1. `DJANGO_SETTINGS_MODULE` es `config.settings.local`, `config.settings.test` o `config.settings.test_postgres`. Cualquier otro módulo se rechaza.
2. No existe `/app/backend/.entorno-produccion`, la marca de solo lectura que crea la imagen `production`. Así, usar `--settings=config.settings.local` o cambiar la variable dentro de esa imagen tampoco habilita la carga.

Ninguna opción ni variable, incluidas `DEBUG` y `ACADEMIC_PROFILE_MOCK_ALLOWED`, desactiva esta protección.

**Límite:** la marca solo existe en la imagen `production`. Ejecutar la imagen de **desarrollo** con las credenciales de una base de producción no se detecta, por lo que nunca deben entregarse esas credenciales a un entorno de desarrollo.

## 1. Mecanismos existentes

| Mecanismo | Ruta | Uso |
|---|---|---|
| `seed_initial_data` | `backend/src/apps/authentication/adapters/management/commands/seed_initial_data.py` | **Recomendado.** 8 cuentas demo y sus roles |
| `seed_mock_sga` | `backend/src/apps/academico/adapters/management/commands/seed_mock_sga.py` | **Recomendado.** Catálogo y perfiles simulados |
| Migración del catálogo | `backend/src/apps/peticiones/adapters/migrations/0002_catalogo_base_art235.py` | Automática con `migrate`: 5 requisitos del Art. 235 |
| `createsuperuser` | Comando estándar de Django | Cuenta para `/admin/` |
| `sga_mock_records.json` | `backend/src/core/adapters/fixtures/` | Fixture del adaptador simulado de `core`. No se carga con `loaddata` |

No existe un script único de inicialización ni un `Makefile`.

## 2. Requisitos previos

1. Servicios levantados: `docker compose up --build -d`.
2. PostgreSQL `healthy` en `docker compose ps`.
3. Migraciones aplicadas: `docker compose exec backend python manage.py migrate`.
4. `DJANGO_SETTINGS_MODULE=config.settings.local`, que Compose ya define y permite MockSGA.

| Variable | Requerida por | Notas |
|---|---|---|
| `SEED_DEMO_PASSWORD` | `seed_initial_data` | Obligatoria y sin valor por defecto. Si falta, no crea nada. `docker-compose.yml` no la entrega: use `exec -e` |
| `ACADEMIC_PROFILE_MOCK_ALLOWED` | `seed_mock_sga` | Verdadera por defecto en `local.py`. Si es falsa, el comando no carga nada |

## 3. Orden de ejecución

```bash
read -rsp "Contraseña para las cuentas demo: " SEED_DEMO_PASSWORD; echo
docker compose exec -e SEED_DEMO_PASSWORD="$SEED_DEMO_PASSWORD" backend python manage.py seed_initial_data
unset SEED_DEMO_PASSWORD

docker compose exec backend python manage.py seed_mock_sga --asignar-ambito-personal
```

`seed_mock_sga` debe ir después: toma la cédula y el correo de las cuentas que ya existen. Si `estudiante_1` no existe, lo avisa y lo omite.

## 4. Qué crea cada comando

### `seed_initial_data`

- 8 cuentas, con correo `sgtdemo.<usuario>@unl.edu.ec` y cédula ficticia definida en el código.
- Los roles que falten y la relación usuario-rol.
- No marca ninguna cuenta como `is_staff`, así que `admin_sys` **no** entra a `/admin/`.
- No configura 2FA: cada cuenta lo registra en su primer ingreso.
- Se ejecuta en una transacción: si una cédula o un correo ya pertenece a otra cuenta, falla y no guarda ningún cambio.
- Identifica las cuentas por `username`. **Si ya existe una cuenta con uno de esos nombres, le asigna el rol demo**, aunque no sea una cuenta demo.

| Usuario | Rol |
|---|---|
| `estudiante_1` | `ESTUDIANTE` |
| `secretaria_carrera` | `SECRETARIA_CARRERA` |
| `secretario_abogado` | `SECRETARIO_ABOGADO` |
| `analista_apoyo` | `ANALISTA_APOYO` |
| `decano_feirnnr` | `DECANO` |
| `director_computacion` | `DIRECTOR_CARRERA` |
| `responsable_practicas` | `RESPONSABLE_DEPENDENCIA` |
| `admin_sys` | `ADMINISTRADOR` |

### `seed_mock_sga`

- Facultad `MOCK-FEIRNNR`.
- Carreras `MOCK-COMPUTACION` (activa) y `MOCK-CARRERA-INACTIVA`.
- Un `PerfilSGASimulado` por cada estudiante indicado. Por defecto, `estudiante_1`.
- Un evento en `EventoCatalogoAcademico` por cada alta.

| Opción | Efecto |
|---|---|
| `--estudiantes <usuario> [...]` | Crea perfiles simulados para esos usuarios con rol `ESTUDIANTE` y cédula. **Admite cuentas que no son demo:** úselo solo con cuentas de prueba |
| `--asignar-ambito-personal` | Asigna la facultad simulada, y también la carrera a los roles de carrera, a las 5 cuentas de personal por `username`. Omite las que ya tienen carrera o facultad |

No crea ni elimina cuentas, ni cambia contraseñas, roles o 2FA. Se ejecuta en una transacción y omite con un aviso las cuentas inexistentes, sin rol `ESTUDIANTE` o sin cédula.

## 5. Verificación

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

Resultado esperado en una base nueva: `8`, `1`, `2` y `1`.

## 6. Repetición

Ambos comandos son idempotentes:

- `seed_initial_data` usa `get_or_create` y aplica la contraseña solo a cuentas nuevas. En cuentas existentes completa un correo vacío y **vuelve a asignar el rol demo si se había retirado**.
- `seed_mock_sga` no sobrescribe el catálogo, los perfiles ni los ámbitos existentes.

Para cambiar la contraseña de una cuenta demo: `docker compose exec backend python manage.py changepassword <usuario>`.

## 7. Crear una cuenta manualmente

1. Ejecute `docker compose exec backend python manage.py createsuperuser`. Pide usuario, correo y contraseña.
2. Entre a `http://localhost:8000/admin/`.
3. Si no se ejecutó `seed_initial_data`, cree los roles en **Roles**: la tabla empieza vacía.
4. En **Users**, cree o edite la cuenta:
   - correo **`@unl.edu.ec`**, único, que es el dato de ingreso;
   - rol en la sección de roles del usuario;
   - carrera o facultad, según el rol.
5. Defina **siempre** la contraseña desde la terminal, porque el formulario del admin no la cifra:

   ```bash
   docker compose exec backend python manage.py changepassword <usuario>
   ```

El superusuario también necesita un rol, por ejemplo `ADMINISTRADOR`, para usar la aplicación. Sin rol reconocido llega a «No habilitado».

## 8. Operaciones que requieren precaución

| Operación | Efecto |
|---|---|
| Imagen de desarrollo con credenciales de producción | **No se detecta.** Crearía cuentas demo, incluida una `ADMINISTRADOR` |
| Repetir `seed_initial_data` tras retirar un rol | Restaura ese rol en la cuenta |
| Recrear el contenedor `backend` de desarrollo | Borra los PDF, que están en `backend/src/media`, fuera del volumen. Sus filas quedan sin archivo |
| `docker compose down -v` | Elimina la base de datos y los volúmenes |
| `reconciliar_archivos --eliminar --confirmar` | Borra archivos huérfanos. Sin esas opciones es de solo lectura |
| Cambiar `SECRET_KEY` en desarrollo | Invalida los autenticadores registrados |

## 9. Pendientes

- Valorar un comando único de preparación del entorno de desarrollo (propuesta, no implementada).
- El dataset ampliado `seed_sgt_siaaf` existe solo como trabajo local sin integrar en `develop`. No documentarlo como disponible hasta su integración.

## Relacionado

[[ENVIRONMENTS]] · [[DOCKER]] · [[PERMISSIONS_ROLES]] · [[USER_ACCESS_GUIDE]] · [[TROUBLESHOOTING]]
