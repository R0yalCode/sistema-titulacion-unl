"""Fuente única de transiciones de estado del expediente (DT-12; PLB-E2-06).

`registrar_transicion()` es el **único** punto autorizado para cambiar
`ExpedienteTitulacion.estado` después de la creación. En una sola
transacción:

1. lee y bloquea el estado vigente en la base de datos (estado anterior real);
2. valida la transición contra `TRANSICIONES_PERMITIDAS`;
3. actualiza el expediente (estado + campos adicionales del servicio llamador);
4. crea un `HistorialEstado` con `registrado_por = actor`;
5. crea **un** `EventoAuditoria` `ESTADO_CAMBIADO` con `usuario = actor`.

Corrige H-24 (actor atribuido siempre al estudiante y eventos duplicados por
señales) y H-25 (estado anterior erróneo en el historial del informe). Las
señales ya no auditan transiciones: se conserva solo `EXPEDIENTE_CREADO`.
Los eventos históricos existentes no se modifican.

Los roles de `TRANSICIONES_PERMITIDAS` sirven **solo para atribuir** el rol
con el que actuó el usuario (reflejan las guardas ya existentes en cada
servicio); la autorización sigue en RBAC y en los servicios.
"""

from django.db import transaction

from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.notificaciones.adapters.models import EventoAuditoria
from core.adapters.client_ip import resolver_ip_cliente
from core.adapters.middleware import get_current_request

E = ExpedienteTitulacion

# (estado_anterior, estado_nuevo) -> roles que ejecutan esa transición en
# los servicios actuales (solo para atribución del rol en la auditoría).
TRANSICIONES_PERMITIDAS: dict[tuple[str, str], tuple[str, ...]] = {
    # enviar_expediente: solo el estudiante dueño (vista filtra por dueño).
    (E.ESTADO_BORRADOR, E.ESTADO_ENVIADA): ("ESTUDIANTE",),
    # iniciar_verificacion (PLB-E2-01, AUT-02): solo SECRETARIO_ABOGADO.
    (E.ESTADO_ENVIADA, E.ESTADO_EN_VERIFICACION): ("SECRETARIO_ABOGADO",),
    # registrar_observacion / evaluar_checklist (OBSERVADO).
    (E.ESTADO_EN_VERIFICACION, E.ESTADO_OBSERVADA): (
        "SECRETARIO_ABOGADO",
        "ANALISTA_APOYO",
    ),
    # subsanar_requisito (DEC-02: estudiante o Secretaría de Carrera).
    (E.ESTADO_OBSERVADA, E.ESTADO_EN_VERIFICACION): (
        "ESTUDIANTE",
        "SECRETARIA_CARRERA",
    ),
    # emitir_informe.
    (E.ESTADO_EN_VERIFICACION, E.ESTADO_INFORME_EMITIDO): ("SECRETARIO_ABOGADO",),
    # declarar_aptitud (el servicio admite DECANO y ANALISTA_APOYO).
    (E.ESTADO_INFORME_EMITIDO, E.ESTADO_DECLARADA_APTA): (
        "DECANO",
        "ANALISTA_APOYO",
    ),
}

ROL_MAX_LEN = 32


class TransicionNoPermitidaError(Exception):
    """La transición solicitada no está en `TRANSICIONES_PERMITIDAS`.

    Expone `estado_anterior` (leído con bloqueo) y `estado_nuevo` para que
    las vistas distingan su causa sin interpretar el mensaje (E1-04).
    """

    def __init__(self, mensaje, *, estado_anterior=None, estado_nuevo=None):
        super().__init__(mensaje)
        self.estado_anterior = estado_anterior
        self.estado_nuevo = estado_nuevo


class ActorRequeridoError(Exception):
    """La transición exige un usuario autenticado explícito."""


def transicion_permitida(estado_actual: str, nuevo_estado: str) -> bool:
    """Indica si la transición está en `TRANSICIONES_PERMITIDAS` (solo lectura).

    Permite a un servicio prevalidar la transición **antes** de producir
    efectos que la transacción no revierte (p. ej. archivos), sin modificar
    la tabla. La validación definitiva sigue en `registrar_transicion()`.
    """
    return (estado_actual, nuevo_estado) in TRANSICIONES_PERMITIDAS


def _rol_actuante(actor, roles_transicion: tuple[str, ...]) -> str:
    roles_actor = list(actor.get_roles())
    for rol in roles_transicion:
        if rol in roles_actor:
            return rol
    # Sin coincidencia (p. ej. administrador en pruebas): se registran los
    # roles reales del actor, nunca un rol ajeno.
    return ",".join(sorted(roles_actor))[:ROL_MAX_LEN] or "SIN_ROL"


def registrar_transicion(
    expediente: ExpedienteTitulacion,
    nuevo_estado: str,
    actor,
    *,
    origen: str,
    campos_adicionales: tuple[str, ...] | list[str] = (),
) -> HistorialEstado:
    """Cambia el estado del expediente y lo registra una sola vez.

    Args:
        expediente: instancia a modificar. Los campos de `campos_adicionales`
            deben estar ya asignados en la instancia por el servicio llamador.
        nuevo_estado: estado destino.
        actor: usuario autenticado que ejecuta la acción (obligatorio).
        origen: identificador de la operación (p. ej. "enviar_expediente").
        campos_adicionales: otros campos del expediente a persistir en la
            misma escritura (plazos, número de providencia...).

    Returns:
        El `HistorialEstado` creado.

    Raises:
        ActorRequeridoError: sin actor autenticado.
        TransicionNoPermitidaError: transición fuera de la tabla.
    """
    if actor is None or not getattr(actor, "is_authenticated", False):
        raise ActorRequeridoError(
            "Toda transición de estado requiere un usuario autenticado explícito."
        )

    with transaction.atomic():
        estado_anterior = (
            ExpedienteTitulacion.objects.select_for_update()
            .values_list("estado", flat=True)
            .get(pk=expediente.pk)
        )
        clave = (estado_anterior, nuevo_estado)
        if clave not in TRANSICIONES_PERMITIDAS:
            raise TransicionNoPermitidaError(
                f"Transición de estado no permitida: {estado_anterior} -> "
                f"{nuevo_estado}.",
                estado_anterior=estado_anterior,
                estado_nuevo=nuevo_estado,
            )

        expediente.estado = nuevo_estado
        campos = ["estado", "fecha_actualizacion", *campos_adicionales]
        expediente.save(update_fields=list(dict.fromkeys(campos)))

        historial = HistorialEstado.objects.create(
            expediente=expediente,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            registrado_por=actor,
        )

        request = get_current_request()
        EventoAuditoria.objects.create(
            accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
            usuario=actor,
            rol_usuario=_rol_actuante(actor, TRANSICIONES_PERMITIDAS[clave]),
            expediente=expediente,
            ip=resolver_ip_cliente(request) if request is not None else None,
            detalles={
                "estado_anterior": estado_anterior,
                "estado_nuevo": nuevo_estado,
                "origen": origen,
                "historial_id": str(historial.id),
            },
        )
    return historial
