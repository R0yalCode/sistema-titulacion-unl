"""Caso de uso de creacion e inicializacion de expediente (T015; RF-001).

La carrera y la facultad del expediente ya no las envía el cliente: se toman
del perfil académico validado del estudiante autenticado
(`AcademicProfileService`), y la facultad se deriva siempre de la carrera
del catálogo interno.

Valida el perfil académico, la ausencia de expedientes activos del
estudiante (HU-001, RN-001) y el catálogo base del Art. 235; crea el
`ExpedienteTitulacion` en estado `BORRADOR` e inicializa las 5 peticiones
documentales base en `PENDIENTE`, todo dentro de una transacción atómica. El
evento `EXPEDIENTE_CREADO` lo registra la señal de notificaciones, con la
carrera, la facultad y la fuente del perfil que fija este caso de uso.

Duplicados concurrentes: la transacción bloquea la fila del estudiante
(`select_for_update`), lo que serializa sus creaciones en PostgreSQL; la
comprobación de RN-001 se hace con ese bloqueo tomado. Una restricción única
parcial en la base de datos queda pendiente de decisión: numerosas pruebas
de otros módulos crean varios expedientes activos por estudiante (ver
docs/academico/perfil-academico-mock-sga.md, "Limitaciones").
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.academico.adapters.models import Carrera
from apps.academico.domain.perfil import PerfilAcademico
from apps.academico.services.perfil_academico import (
    AcademicProfileService,
    get_academic_profile_service,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_PENDIENTE,
    FASE_1,
    CatalogoDocumental,
    PeticionDocumental,
)

REQUISITOS_BASE_ESPERADOS = 5


class ExpedienteActivoExistenteError(Exception):
    """El estudiante ya posee un expediente activo (HU-001 precondicion)."""


class CatalogoIncompletoError(Exception):
    """El catalogo base del Art. 235 no contiene los 5 requisitos vigentes."""


class PerfilAcademicoNoValidoError(Exception):
    """El perfil académico del estudiante no permite iniciar el trámite."""

    def __init__(self, perfil: PerfilAcademico):
        self.perfil = perfil
        mensaje = (
            perfil.motivos[0].mensaje
            if perfil.motivos
            else "Su perfil académico no está validado."
        )
        super().__init__(mensaje)


class CarreraNoVigenteError(Exception):
    """La carrera del perfil dejó de estar vigente durante la creación."""


def tiene_expediente_activo(estudiante) -> bool:
    return ExpedienteTitulacion.objects.filter(
        estudiante=estudiante, activa=True
    ).exists()


def generar_numero_expediente():
    """Numero correlativo anual, p. ej. `EXP-2026-0001` (plan.md 12)."""
    anio = timezone.localtime(timezone.now()).year
    prefijo = f"EXP-{anio}-"
    ultimo = (
        ExpedienteTitulacion.objects.filter(
            numero_expediente__startswith=prefijo,
        )
        .order_by("-numero_expediente")
        .values_list("numero_expediente", flat=True)
        .first()
    )
    correlativo = int(ultimo[len(prefijo) :]) + 1 if ultimo else 1
    return f"{prefijo}{correlativo:04d}"


def _error_activo():
    return ExpedienteActivoExistenteError(
        "El estudiante ya posee un expediente de titulacion activo; "
        "no se permite iniciar otro tramite en curso (HU-001)."
    )


def execute(estudiante, servicio_perfil: AcademicProfileService | None = None):
    """Entrada del caso de uso (V-03, `POST /api/v1/expedientes/`).

    Obtiene el perfil académico validado del estudiante autenticado y crea el
    expediente con su carrera y la facultad que esa carrera determina.

    Lanza `FuenteAcademicaNoDisponibleError` (503) si no hay fuente
    académica, `PerfilAcademicoNoValidoError` (422) si el perfil no está
    validado, `CarreraNoVigenteError` (422) si la carrera dejó de estar
    vigente y `ExpedienteActivoExistenteError` (400) por RN-001.
    """
    servicio = servicio_perfil or get_academic_profile_service()
    # La consulta a la fuente va fuera de la transacción: con un adaptador
    # real puede tardar y no debe retener bloqueos.
    perfil = servicio.obtener_perfil(estudiante)
    if not perfil.validado:
        raise PerfilAcademicoNoValidoError(perfil)

    with transaction.atomic():
        _bloquear_estudiante(estudiante)
        carrera = (
            Carrera.objects.select_related("facultad")
            .filter(pk=perfil.carrera.id, activa=True, facultad__activa=True)
            .first()
        )
        if carrera is None:
            raise CarreraNoVigenteError(
                "Su carrera no está vigente en el catálogo del sistema; no es "
                "posible iniciar un trámite."
            )
        return registrar_expediente(
            estudiante,
            carrera.id,
            facultad_id=carrera.facultad_id,
            detalles_auditoria={
                "carrera_codigo": carrera.codigo,
                "fuente_perfil": perfil.fuente.codigo,
                "fuente_simulada": perfil.fuente.es_simulada,
                "perfil_consultado_en": perfil.consultado_en.isoformat(),
            },
        )


def _bloquear_estudiante(estudiante):
    # Serializa las creaciones del mismo estudiante (PostgreSQL): un
    # `select_for_update` sobre un conjunto vacío de expedientes no bloquea
    # nada; la fila del usuario sí.
    get_user_model().objects.select_for_update().filter(pk=estudiante.pk).first()


def registrar_expediente(
    estudiante,
    carrera_id,
    *,
    facultad_id=None,
    detalles_auditoria: dict | None = None,
):
    """Primitiva transaccional: RN-001, catálogo base, expediente y peticiones.

    No consulta el perfil académico: la usa `execute` con la carrera y la
    facultad ya validadas. Ninguna vista la invoca con datos del cliente; las
    pruebas de otros módulos la usan para preparar expedientes. Si no se
    indica `facultad_id`, se toma la de la cuenta (comportamiento anterior).
    """
    with transaction.atomic():
        _bloquear_estudiante(estudiante)
        if tiene_expediente_activo(estudiante):
            raise _error_activo()

        catalogo = list(
            CatalogoDocumental.objects.filter(
                es_obligatorio_base=True,
                fase=FASE_1,
                activo=True,
            ).order_by("codigo_requisito")
        )
        if len(catalogo) != REQUISITOS_BASE_ESPERADOS:
            raise CatalogoIncompletoError(
                f"El catalogo base del Art. 235 requiere "
                f"{REQUISITOS_BASE_ESPERADOS} requisitos vigentes; se "
                f"encontraron {len(catalogo)}."
            )
        expediente = ExpedienteTitulacion(
            numero_expediente=generar_numero_expediente(),
            estudiante=estudiante,
            carrera_id=carrera_id,
            facultad_id=(
                facultad_id if facultad_id is not None else estudiante.facultad_id
            ),
            estado=ExpedienteTitulacion.ESTADO_BORRADOR,
            activa=True,
        )
        # La señal `expediente_post_save` (notificaciones) registra el único
        # evento EXPEDIENTE_CREADO; estos datos lo completan.
        expediente._detalles_auditoria_creacion = {
            "carrera_id": str(expediente.carrera_id) if expediente.carrera_id else None,
            "facultad_id": (
                str(expediente.facultad_id) if expediente.facultad_id else None
            ),
            **(detalles_auditoria or {"fuente_perfil": None}),
        }
        expediente.save()

        PeticionDocumental.objects.bulk_create(
            PeticionDocumental(
                expediente=expediente,
                requisito=requisito,
                estado_peticion=ESTADO_PENDIENTE,
                dependencia_emisora=requisito.rol_emisor_sugerido,
            )
            for requisito in catalogo
        )
        expediente.refresh_from_db()
        return expediente
