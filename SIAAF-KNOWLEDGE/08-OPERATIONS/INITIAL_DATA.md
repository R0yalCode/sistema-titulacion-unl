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
> **Verificación (2026-11-23):** la secuencia y los rechazos se ejecutaron con PostgreSQL 16 e imágenes desechables. No se ejecutó contra ninguna base real.

## Uso por entorno

| Entorno | Settings | `seed_initial_data` | `seed_mock_sga` | Indicación |
|---|---|---|---|---|
| **Desarrollo** | `config.settings.local` | Disponible en una base registrada como `desarrollo`; requiere `SEED_DEMO_PASSWORD` | Disponible en una base registrada como `desarrollo` | Único entorno para esta carga |
| **Pruebas** | `config.settings.test`, `test_postgres` | Solo dentro de pytest, en su base temporal | Solo dentro de pytest, en su base temporal | No requiere carga manual ni registro |
| **Producción** | `config.settings.production` | **Rechazado antes de acceder a la base** | **Rechazado antes de acceder a la base** | Las cuentas reales no se crean con estos comandos |

## Protección de la base

Los comandos llaman a `exigir_entorno_de_demostracion` (`backend/src/core/adapters/entorno_demo.py`) antes de escribir. Deben cumplirse todas las condiciones:

1. `DJANGO_SETTINGS_MODULE` es `config.settings.local`, `test` o `test_postgres`.
2. No existe `/app/backend/.entorno-produccion`, la marca de solo lectura de la imagen `production`.
3. **El destino lo admite:** la base está registrada como `desarrollo`, o es la base temporal de pytest (ejecutor de pruebas activo, base en memoria o con prefijo `test_`).

`DEBUG`, `ACADEMIC_PROFILE_MOCK_ALLOWED` y `test_postgres` no autorizan la carga por sí solos.

### Identidad de la base

La tabla `sgt_identidad_entorno` (migración `authentication/0004`) admite **una sola fila**, con valor `desarrollo` o `produccion`. En PostgreSQL, unos triggers impiden `UPDATE`, `DELETE` y `TRUNCATE` sobre ella. Los seeders solo la leen.

| Situación | Resultado |
|---|---|
| Arranque de la imagen `production` sobre una base sin marca | Tras `migrate`, la registra como `produccion` |
| Arranque de la imagen `production` sobre una base de `desarrollo` | **El arranque se detiene** |
| Imagen de desarrollo + base `produccion` | Seeders rechazados, y no se puede reclasificar |
| Imagen de desarrollo + base `desarrollo` | Carga permitida e idempotente |
| Base sin marca | Rechazada, salvo la temporal de pytest |
| Marca inconsistente o que no se puede consultar | Rechazada |
| `test_postgres` fuera de pytest, aunque la base empiece por `test_` | Rechazada |
| Backup restaurado o base clonada | Conserva la identidad y sus triggers |
| Base creada desde cero | Sin marca hasta registrarla |
| Base sin migrar | Rechazada: no tiene la tabla |

### Preparar una base nueva de desarrollo

Se hace **una vez** por base, después de `migrate`. Hay que escribir el nombre exacto de la base:

```bash
docker compose exec backend python manage.py registrar_entorno_bd desarrollo --confirmar-base sgt_siaaf
```

Use el valor de `POSTGRES_DB` si no es `sgt_siaaf`. Si la base ya tiene otra identidad, el comando falla y no cambia nada.

### Límites

- Quien registre manualmente como `desarrollo` una base **sin marca** habilita la carga. Por eso debe confirmar su nombre, y nunca debe hacerlo sobre una base real.
- Un **superusuario de PostgreSQL** puede desactivar los triggers y alterar la marca. `docker-compose.prod.yml` conecta la aplicación con el usuario creado por `POSTGRES_USER`, que es superusuario. Separar un rol de aplicación sin esos privilegios sigue pendiente.
- La protección no impide escribir con SQL directo o con código propio en una base con credenciales válidas.
- No se probó contra un PostgreSQL gestionado ni con el esquema de roles de un despliegue real.

## 1. Mecanismos existentes

| Mecanismo | Ruta | Uso |
|---|---|---|
| `seed_initial_data` | `backend/src/apps/authentication/adapters/management/commands/seed_initial_data.py` | **Recomendado.** 8 cuentas demo y sus roles |
| `seed_mock_sga` | `backend/src/apps/academico/adapters/management/commands/seed_mock_sga.py` | **Recomendado.** Catálogo y perfiles simulados |
| `registrar_entorno_bd` | `backend/src/apps/authentication/adapters/management/commands/registrar_entorno_bd.py` | Registra la identidad de la base |
| `seed_sgt_siaaf` | `backend/src/apps/entorno_pruebas/adapters/management/commands/seed_sgt_siaaf.py` | **Opcional.** Dataset sintético de 80 cuentas ([guía](../../docs/entorno-pruebas/dataset-sgt-siaaf.md)) |
| Migración del catálogo | `backend/src/apps/peticiones/adapters/migrations/0002_catalogo_base_art235.py` | Automática con `migrate`: 5 requisitos del Art. 235 |
| `createsuperuser` | Comando estándar de Django | Cuenta para `/admin/` |
| `sga_mock_records.json` | `backend/src/core/adapters/fixtures/` | Fixture del adaptador simulado de `core`. No se carga con `loaddata` |

No existe un script único de inicialización ni un `Makefile`.

## 2. Requisitos previos

1. Servicios levantados: `docker compose up --build -d`.
2. PostgreSQL `healthy` en `docker compose ps`.
3. Migraciones aplicadas: `docker compose exec backend python manage.py migrate`.
4. `DJANGO_SETTINGS_MODULE=config.settings.local`, que Compose ya define y permite MockSGA.
5. Base registrada como desarrollo: `docker compose exec backend python manage.py registrar_entorno_bd desarrollo --confirmar-base sgt_siaaf`.

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
| `registrar_entorno_bd desarrollo` sobre una base real sin marca | **Habilitaría la carga.** Confirme siempre que la base es local |
| Repetir `seed_initial_data` tras retirar un rol | Restaura ese rol en la cuenta |
| Recrear el contenedor `backend` de desarrollo | Borra los PDF, que están en `backend/src/media`, fuera del volumen. Sus filas quedan sin archivo |
| `docker compose down -v` | Elimina la base de datos y los volúmenes |
| `reconciliar_archivos --eliminar --confirmar` | Borra archivos huérfanos. Sin esas opciones es de solo lectura |
| Cambiar `SECRET_KEY` en desarrollo | Invalida los autenticadores registrados |

## 9. Pendientes

- Valorar un comando único de preparación del entorno de desarrollo (propuesta, no implementada).

## Relacionado

[[ENVIRONMENTS]] · [[DOCKER]] · [[PERMISSIONS_ROLES]] · [[USER_ACCESS_GUIDE]] · [[TROUBLESHOOTING]]
