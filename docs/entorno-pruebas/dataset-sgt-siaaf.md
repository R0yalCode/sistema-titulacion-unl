# Dataset sintético del entorno de desarrollo (`seed_sgt_siaaf`)

> **Solo para bases locales de desarrollo y pruebas.** Las 80 identidades son **ficticias** y se derivan del rol y de un índice. El perfil académico proviene de **MockSGA**, una simulación sin conexión con el SGA. Ver [`perfil-academico-mock-sga.md`](../academico/perfil-academico-mock-sga.md).

## 1. Contenido

| Elemento | Cantidad |
|---|---|
| Cuentas (10 × 8 roles) | 80 |
| Facultades simuladas | 2 (`MOCK-FEIRNNR`, `MOCK-FCEA`) |
| Carreras simuladas activas | 5 |
| Perfiles MockSGA | 10, uno por estudiante |
| Expedientes | 8; 2 estudiantes quedan sin expediente |

Los expedientes cubren `BORRADOR`, `ENVIADA`, `EN_VERIFICACION`, `OBSERVADA`, subsanación, `INFORME_EMITIDO` y `DECLARADA_APTA`. Se construyen con los servicios de negocio y usan PDF ficticios.

## 2. Identidades

| Campo | Formato |
|---|---|
| Nombre | `Estudiante Ficticio 01` |
| Usuario | `ds.estudiante.01` |
| Correo por defecto | `ds.estudiante.01@sgt-siaaf.example` |
| Correo con `--correo-institucional` | `sgtdemo.ds.estudiante.01@unl.edu.ec` |
| Cédula | Empieza por `99`, código que no corresponde a ninguna provincia |

El dominio `.example` está reservado por la RFC 2606. La interfaz solo admite el dominio institucional, así que **para ingresar por el navegador** debe crear las cuentas con `--correo-institucional`. Ese formato usa el prefijo `sgtdemo.` de las cuentas demo, y esos correos no son buzones reales.

Ninguna cuenta es `is_staff` ni `is_superuser`. Cada una registra su propio 2FA en el primer ingreso.

## 3. Uso

Requiere `migrate`, una base registrada como desarrollo y `seed_initial_data`, que crea los roles ([`INITIAL_DATA.md`](../../SIAAF-KNOWLEDGE/08-OPERATIONS/INITIAL_DATA.md)).

```bash
read -rsp "Contraseña del dataset: " SEED_DATASET_PASSWORD; echo
docker compose exec -e SEED_DATASET_PASSWORD="$SEED_DATASET_PASSWORD" backend \
  python manage.py seed_sgt_siaaf --correo-institucional
unset SEED_DATASET_PASSWORD

docker compose exec backend python manage.py seed_sgt_siaaf --listar
```

| Opción | Efecto |
|---|---|
| `--correo-institucional` | Crea las cuentas nuevas con correo `sgtdemo.*` para ingresar por la interfaz |
| `--sin-escenarios` | Crea cuentas y perfiles, sin expedientes |
| `--listar` | Lista las cuentas, sin contraseñas ni cédulas |

La contraseña debe cumplir la política de Django y no se escribe en la salida.

## 4. Protección e idempotencia

- Solo escribe en una base registrada como `desarrollo` o en la base temporal de pytest.
- Se niega a ejecutarse con los settings de producción, si MockSGA no está permitido o si `EMAIL_BACKEND` no es local.
- La segunda ejecución no crea cuentas ni escenarios. No cambia contraseñas, roles, ámbitos ni MFA.
- `--correo-institucional` no modifica cuentas ya creadas.
- No borra datos y no usa ningún dato externo.
- `RegistroDatasetSintetico` identifica cada registro del lote. No lo elimine.

## 5. Limitaciones

- No se probó el escaneo real del QR con un teléfono.
- `RESPONSABLE_DEPENDENCIA` autentica, pero la matriz RBAC no le concede lectura.
- Las cuentas comparten la contraseña inicial que defina quien ejecuta el comando.
- Si un escenario falla, la base se revierte, pero los PDF ya escritos pueden quedar huérfanos. `reconciliar_archivos` los detecta.
