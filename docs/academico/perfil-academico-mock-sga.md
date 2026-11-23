# Perfil académico del estudiante y simulación MockSGA

> **Aviso.** MockSGA es una **simulación de prototipo**. SGT-SIAAF **no tiene
> conexión** con el SGA ni con ningún sistema académico de la UNL: no hay
> autorización, contrato técnico ni credenciales. Los datos que devuelve
> MockSGA son de demostración, se marcan como tales en la base de datos
> (`es_simulada`, códigos `MOCK-…`) y la API lo comunica al cliente
> (`fuente.es_simulada = true`). Nunca deben presentarse como información
> institucional real.

Implementado el 2026-11-22 (V-03, rama `feat/dashboard-estudiante`, sin commit).

## 1. Problema que resuelve

Antes, V-03 (Crear solicitud) obligaba al estudiante a escribir el UUID de su
carrera, y `POST /api/v1/expedientes/` aceptaba cualquier UUID con formato
válido: el estudiante decidía en qué bandeja de carrera aparecía su
expediente y la facultad salía de otra fuente (`User.facultad_id`). Ahora el
backend determina la carrera a partir del perfil académico del usuario
autenticado y deriva la facultad de esa carrera.

## 2. Arquitectura

```
V-03 (frontend) ──GET /api/v1/perfil-academico/──▶ PerfilAcademicoView
        │                                              │
        └──POST /api/v1/expedientes/ {}──▶ ExpedienteViewSet.create
                                                       │
                                     crear_expediente.execute(estudiante)
                                                       │
                                     AcademicProfileService.obtener_perfil(user)
                                       │  (identidad: request.user.cedula)
                                       ▼
                         Puerto FuenteAcademica  ◀── configurado en settings
                           ├─ MockSGAAdapter  (hoy; tabla PerfilSGASimulado)
                           └─ SGAAdapter      (futuro; no implementado)
                                       │
                         Catálogo interno: Carrera ─▶ Facultad
```

| Pieza | Ubicación | Responsabilidad |
|---|---|---|
| Dominio | `apps/academico/domain/perfil.py` | `PerfilAcademico`, `EstadoPerfil`, motivos de bloqueo (sin Django) |
| Puerto | `apps/academico/ports/fuente_academica.py` | Contrato `FuenteAcademica` y errores de disponibilidad |
| Servicio | `apps/academico/services/perfil_academico.py` | `AcademicProfileService`: consulta, resuelve el catálogo, valida |
| Selección de fuente | `apps/academico/services/fuentes.py` | Lee `ACADEMIC_PROFILE_PROVIDER`; bloquea el mock si no está permitido |
| Adaptador simulado | `apps/academico/adapters/mock_sga.py` | `MockSGAAdapter` (lee `PerfilSGASimulado`) |
| Catálogo y bitácora | `apps/academico/adapters/models.py` | `Facultad`, `Carrera`, `PerfilSGASimulado`, `EventoCatalogoAcademico` |
| API | `apps/academico/adapters/views.py` | `GET /api/v1/perfil-academico/` |
| Creación | `apps/expedientes/services/crear_expediente.py` | `execute()` exige perfil validado |

El frontend no conoce el proveedor: solo consume el contrato y muestra
`fuente`. La creación del expediente depende del servicio, no del mock.

## 3. Catálogo académico

- `Facultad(codigo único, nombre, activa, es_simulada)`.
- `Carrera(codigo único, nombre, facultad → Facultad, activa, es_simulada)`.
  **La carrera determina la facultad**: el expediente toma
  `facultad_id = carrera.facultad_id`.
- No se eliminan desde el admin (se desactivan), para no dejar expedientes
  con referencias rotas.

Catálogo de demostración que carga `seed_mock_sga` (todo `es_simulada=True`):

| Código | Nombre | Activa | Observación |
|---|---|---|---|
| `MOCK-FEIRNNR` | Facultad de la Energía, las Industrias y los Recursos Naturales No Renovables | Sí | Nombre tomado de la spec 001 §1; **código no oficial** |
| `MOCK-COMPUTACION` | Computación | Sí | Carrera de la spec 001; **código no oficial** |
| `MOCK-CARRERA-INACTIVA` | Carrera ficticia inactiva (solo demostración) | No | Ficticia; sirve para demostrar el bloqueo |

Los UUID se derivan del código con `uuid5` (espacio de nombres fijo en
`seed_mock_sga.py`): son iguales en todos los entornos, pero **no** son
identificadores institucionales.

**Incorporar el catálogo oficial:** cuando la UNL entregue el catálogo
validado (códigos y nombres), cargarlo con `es_simulada=False` mediante una
migración de datos o el admin, desactivar los registros `MOCK-…` y reasignar
el ámbito del personal. Los códigos deben coincidir con los que use la
fuente académica real.

## 4. MockSGA

`PerfilSGASimulado` representa lo que devolvería el SGA para una cédula:
`identificacion`, `nombres`, `apellidos`, `correo_institucional`,
`codigo_carrera`, `codigo_facultad`, `activo`. Los códigos se guardan como
texto, como los entregaría la fuente, y el servicio los resuelve contra el
catálogo. Así se pueden demostrar perfiles incompletos o inconsistentes sin
tocar el catálogo.

No se simula estado académico, créditos, promedio ni ninguna otra regla de
elegibilidad: no están documentadas para este flujo (ver §9).

## 5. Validación del perfil

El servicio busca en la fuente la cédula de la **cuenta autenticada** (nunca
un dato del cliente) y devuelve un estado (el del motivo más grave):

| Estado | Motivos (`codigo`) | Cuándo |
|---|---|---|
| `NO_ASOCIADO` | `perfil_academico_no_asociado` | La fuente no tiene registro activo para esa cédula |
| `INCOMPLETO` | `identificacion_no_registrada`, `datos_personales_incompletos`, `carrera_no_registrada` | Cuenta sin cédula; faltan nombres, apellidos o correo; sin carrera |
| `INCONSISTENTE` | `carrera_no_catalogada`, `facultad_no_corresponde`, `correo_no_corresponde`, `asociacion_local_inconsistente` | La carrera no está en el catálogo; la facultad de la fuente no es la de la carrera; el correo no es el de la cuenta; `User.carrera_id`/`facultad_id` contradicen el perfil |
| `CARRERA_INACTIVA` | `carrera_inactiva`, `facultad_inactiva` | Carrera o facultad desactivadas en el catálogo |
| `VALIDADO` | — | Ninguno de los anteriores |

Si la fuente falla o devuelve el registro de otra persona, el servicio lanza
`FuenteAcademicaNoDisponibleError` (503) y no usa esos datos.

## 6. Contrato API

### `GET /api/v1/perfil-academico/`

Solo `ESTUDIANTE` (celda RBAC `perfil_academico`, alcance `own`). Sin
parámetros: se ignora cualquier `cedula`, `usuario` o `carrera_id` de la
consulta. Respuesta 200 (también con perfil no validado):

```json
{
  "estudiante": {"identificacion": "…", "nombres": "…", "apellidos": "…", "correo_institucional": "…"},
  "carrera": {"id": "uuid", "codigo": "MOCK-COMPUTACION", "nombre": "Computación", "activa": true},
  "facultad": {"id": "uuid", "codigo": "MOCK-FEIRNNR", "nombre": "…", "activa": true},
  "fuente": {"codigo": "MOCK_SGA", "nombre": "MockSGA (simulación…)", "es_simulada": true},
  "consultado_en": "2026-11-22T18:20:26Z",
  "estado_perfil": "VALIDADO",
  "perfil_validado": true,
  "puede_iniciar_tramite": true,
  "motivos_bloqueo": []
}
```

`estudiante`, `carrera` y `facultad` son `null` si la fuente no los tiene.
`puede_iniciar_tramite = perfil_validado && sin expediente activo`; con un
expediente activo se añade el motivo `expediente_activo_existente`.

Errores: 401 sin sesión; 403 otros roles; 503
`servicio_academico_no_configurado` (sin fuente o mock no permitido) o
`servicio_academico_no_disponible` (la fuente falló).

### `POST /api/v1/expedientes/` (cambio de contrato)

Cuerpo vacío `{}`. El backend obtiene el perfil, lo exige validado, revalida
dentro de la transacción que la carrera siga vigente y crea el expediente con
`carrera_id` del perfil y `facultad_id` de la carrera.

| Código | `code` | Caso |
|---|---|---|
| 201 | — | Expediente `BORRADOR` con sus 5 peticiones |
| 400 | `campo_no_permitido` | El cuerpo trae `carrera_id`, `facultad_id` o `estudiante_id` |
| 400 | `expediente_activo_existente` | RN-001 (sin cambios; no 409, BE-11) |
| 422 | `perfil_academico_no_asociado` / `perfil_academico_incompleto` / `perfil_academico_inconsistente` / `carrera_inactiva` | Perfil no validado |
| 500 | `configuracion_catalogo_incompleta` | Catálogo documental base incompleto (sin cambios) |
| 503 | `servicio_academico_no_configurado` / `servicio_academico_no_disponible` | Sin fuente académica |

Ambos están en `backend/openapi.yaml` (regenerado con drf-spectacular).

## 7. Creación segura del expediente

- La consulta a la fuente se hace **fuera** de la transacción (un adaptador
  real puede tardar y no debe retener bloqueos).
- Dentro de la transacción se bloquea la fila del estudiante
  (`select_for_update`), se comprueba RN-001, se revalida la carrera y se
  crea el expediente. Dos creaciones simultáneas del mismo estudiante quedan
  serializadas: verificado con PostgreSQL real
  (`tests/integration/test_crear_expediente_concurrencia_postgres.py`).
- La señal existente de notificaciones registra el único `EXPEDIENTE_CREADO`
  en `EventoAuditoria`, ahora con `carrera_id`, `carrera_codigo`,
  `facultad_id`, `fuente_perfil`, `fuente_simulada` y `perfil_consultado_en`
  (sin cédula ni nombres).
- `registrar_expediente()` es la primitiva transaccional que usa `execute()`.
  Ninguna vista la invoca con datos del cliente; las pruebas de otros
  módulos la usan para preparar expedientes.

## 8. Configuración

| Variable | Desarrollo (`local.py`) | Pruebas (`test.py`) | Producción (`production.py`) |
|---|---|---|---|
| `ACADEMIC_PROFILE_PROVIDER` | `mock_sga` | `mock_sga` | vacío (sin fuente → 503) |
| `ACADEMIC_PROFILE_MOCK_ALLOWED` | `true` | `true` | `false` (constante, no se lee del entorno) |

En producción, `mock_sga` detiene el arranque con `ImproperlyConfigured`,
sea cual sea el valor de `DEBUG` o de `ACADEMIC_PROFILE_MOCK_ALLOWED`.

Fuera de producción, el mock solo funciona si **ambas** variables lo permiten. Un nombre de
proveedor desconocido (p. ej. `sga` mientras no exista el adaptador) no
degrada a otra fuente: responde 503. `seed_mock_sga` se niega a ejecutarse
si `ACADEMIC_PROFILE_MOCK_ALLOWED` es falso.

No existe ningún endpoint para crear o modificar perfiles simulados: solo el
admin de Django (personal autorizado) y el comando de gestión.

## 9. Preparación de la demostración

En el entorno de desarrollo (`docker compose`), una sola vez:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_mock_sga --asignar-ambito-personal
```

- Crea el catálogo `MOCK-…` y el perfil MockSGA de `estudiante_1` (con la
  cédula y el correo de su propia cuenta). Es idempotente y nunca sobrescribe
  un perfil existente.
- `--asignar-ambito-personal` asigna la carrera o facultad de demostración a
  las cuentas demo del personal que **no tienen ninguna** (secretaría y
  dirección de carrera → carrera; secretaría abogada, analista y decanato →
  facultad), para que vean en su ámbito los expedientes creados en la demo.
  No cambia contraseñas, roles ni 2FA.
- Cada alta queda en `EventoCatalogoAcademico` (origen `seed_mock_sga`).

Guion sugerido: iniciar sesión como `estudiante_1` → Nueva solicitud →
revisar los datos académicos (aviso "Información académica simulada") →
Iniciar trámite → confirmar. Para mostrar un bloqueo, en el admin
(`/admin/academico/perfilsgasimulado/`) cambiar `codigo_carrera` a
`MOCK-CARRERA-INACTIVA` o desmarcar `activo`, y volver a consultar en V-03.
El cambio queda auditado; revertirlo después.

La demostración no puede ejecutarse con `config.settings.production`. Si se
necesitara fuera del entorno de desarrollo, debe plantearse un módulo de
settings independiente, sin añadir excepciones a producción.

## 10. Seguridad

| Riesgo | Control | Prueba |
|---|---|---|
| UUID de carrera manipulado / carrera ajena | El cliente no puede enviar `carrera_id`/`facultad_id`/`estudiante_id` (400) | `test_cliente_no_puede_fijar_carrera_facultad_ni_estudiante_400` |
| IDOR del perfil | Sin parámetros; siempre `request.user` | `test_idor_parametros_ignorados_siempre_perfil_propio` |
| Fuente que devuelve a otra persona | Se descarta (503) | `test_fuente_que_devuelve_otra_persona_no_se_usa` |
| Otros roles | RBAC `perfil_academico` solo ESTUDIANTE | `test_solo_estudiante_403_para_otros_roles` |
| Sin perfil / incompleto / inconsistente / carrera inactiva | 422 en la creación, bloqueo en V-03 | `test_crear_expediente.py`, `test_perfil_academico_service.py` |
| Carrera desactivada durante la creación | Revalidación en la transacción | `test_carrera_desactivada_entre_consulta_y_creacion_422` |
| Duplicado concurrente | Bloqueo de la fila del estudiante | `test_creaciones_simultaneas_del_mismo_estudiante` (PostgreSQL) |
| Mock expuesto en producción | Requiere permiso explícito; producción sin valor por defecto | `test_mock_en_produccion_no_disponible_503`, `test_settings_de_produccion_no_habilitan_el_mock_por_defecto` |
| Administración del catálogo | Solo admin de Django; sin borrado de catálogo; bitácora de solo lectura | `test_admin_y_seed.py` |
| Datos personales en bitácoras | Solo códigos e ids; nombres de campos sin valor | `test_cambio_de_perfil_desde_el_admin_queda_auditado` |

## 11. Limitaciones

- **No hay integración institucional.** Ni SGA ni SAC/CAS. El perfil no
  demuestra que la persona esté matriculada ni que cumpla requisitos.
- **Elegibilidad:** no se validan créditos, promedio, prácticas ni modalidad
  (RRA-UNL no contrastado; PQ-13, BE-06). Solo identidad, carrera catalogada y
  vigente, coherencia de datos y RN-001.
- **Restricción única en base de datos pendiente:** una restricción única
  parcial "un expediente activo por estudiante" haría fallar unas 85 pruebas
  de otros módulos (verificación, resoluciones, peticiones, notificaciones),
  cuyos fixtures crean varios expedientes activos por estudiante. Se dejó
  fuera por afectar funcionalidades ajenas a esta tarea; la protección vigente
  es el bloqueo transaccional. Requiere decisión del responsable.
- **Ámbito del personal:** `User.carrera_id`/`facultad_id` del personal siguen
  siendo UUID sueltos (sin clave foránea al catálogo). El comando los asigna
  de forma coherente para la demo; la validación general queda pendiente.
- `ADMINISTRADOR` conserva el permiso RBAC de `POST /expedientes/`, pero sin
  perfil académico propio recibe 422.
- El puerto `ISGALegacyPort` / `SGAMockAdapter` de `core` (récord académico
  con notas, solo usado en pruebas) es distinto de este y no se modificó.

## 12. Migración futura al SGA real

1. Obtener de la UNL: autorización, contrato del servicio (identificador de
   consulta, campos, códigos de carrera y facultad), credenciales y
   entorno de pruebas.
2. Implementar `apps/academico/adapters/sga.py` con `SGAAdapter` (atributos
   `codigo="SGA"`, `nombre`, `es_simulada=False`, método
   `consultar_por_identificacion`), con timeouts y conversión de fallos a
   `FuenteAcademicaNoDisponibleError`.
3. Registrarlo en `_FUENTES` (`services/fuentes.py`) y configurar
   `ACADEMIC_PROFILE_PROVIDER=sga`.
4. Cargar el catálogo oficial con los códigos de la fuente.
5. Añadir pruebas de contrato del adaptador.

No cambian V-03, `crear_expediente`, el RBAC ni el contrato de
`GET /api/v1/perfil-academico/`.
