"""Resumen de solo lectura del trámite del estudiante (dashboard V-02 v2).

Alimenta `GET /api/v1/expedientes/mi-tramite/`. No cambia estados ni
reglas: reutiliza el orden del flujo de `TRANSICIONES_PERMITIDAS`, la regla
de documento en firme de `enviar_expediente` y los registros reales de
`HistorialEstado`, `DocumentoEntregado` y `ObservacionAccionable`.

Aislamiento: todas las consultas parten de `estudiante=usuario`; nunca se
recibe un identificador del cliente (sin superficie IDOR).

Datos que **no** se exponen (internos o de terceros): quién registró cada
transición u observación, nombres de usuario de funcionarios, rutas, hashes
o nombres originales de archivos, checklist interno y auditoría.
"""

from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.expedientes.services.enviar_expediente import ESTADOS_SIN_DOCUMENTO_VIGENTE
from apps.peticiones.adapters.models import DocumentoEntregado, PeticionDocumental
from apps.verificacion.adapters.models import ObservacionAccionable

E = ExpedienteTitulacion

# Etapas del flujo aprobado, en el orden de `TRANSICIONES_PERMITIDAS`
# (BORRADOR -> ENVIADA -> EN_VERIFICACION -> INFORME_EMITIDO ->
# DECLARADA_APTA). OBSERVADA no es una etapa propia: es una pausa de la
# verificación (EN_VERIFICACION <-> OBSERVADA), por eso no suma progreso.
ETAPAS_TRAMITE = (
    (E.ESTADO_BORRADOR, "Solicitud registrada"),
    (E.ESTADO_ENVIADA, "Solicitud enviada"),
    (E.ESTADO_EN_VERIFICACION, "Verificación de requisitos"),
    (E.ESTADO_INFORME_EMITIDO, "Informe emitido"),
    (E.ESTADO_DECLARADA_APTA, "Declaratoria de aptitud"),
)

# Estado del expediente -> índice de la etapa en curso.
_INDICE_ETAPA_POR_ESTADO = {
    E.ESTADO_BORRADOR: 0,
    E.ESTADO_ENVIADA: 1,
    E.ESTADO_EN_VERIFICACION: 2,
    E.ESTADO_OBSERVADA: 2,
    E.ESTADO_INFORME_EMITIDO: 3,
    E.ESTADO_DECLARADA_APTA: 4,
}

MAX_MOVIMIENTOS = 10


def _primera_entrada_por_estado(historial):
    """Fecha de la primera vez que el expediente llegó a cada estado."""
    fechas = {}
    for registro in historial:  # orden ascendente
        fechas.setdefault(registro.estado_nuevo, registro.fecha_cambio)
    return fechas


def _etapas(expediente, historial):
    fechas = _primera_entrada_por_estado(historial)
    fechas.setdefault(E.ESTADO_BORRADOR, expediente.fecha_creacion)
    indice_actual = _INDICE_ETAPA_POR_ESTADO.get(expediente.estado)
    finalizado = expediente.estado == E.ESTADO_DECLARADA_APTA

    etapas = []
    for indice, (codigo, nombre) in enumerate(ETAPAS_TRAMITE):
        if indice_actual is None:
            # CANCELADA u otro estado fuera del flujo: solo lo realmente alcanzado.
            situacion = "completada" if codigo in fechas else "pendiente"
        elif indice < indice_actual or (finalizado and indice == indice_actual):
            situacion = "completada"
        elif indice == indice_actual:
            situacion = "actual"
        else:
            situacion = "pendiente"
        etapas.append(
            {
                "codigo": codigo,
                "nombre": nombre,
                "situacion": situacion,
                "fecha": fechas.get(codigo) if situacion != "pendiente" else None,
            }
        )
    return etapas


def _progreso(expediente, etapas):
    if expediente.estado not in _INDICE_ETAPA_POR_ESTADO:
        return None
    completadas = sum(1 for etapa in etapas if etapa["situacion"] == "completada")
    return {"etapas_completadas": completadas, "etapas_totales": len(etapas)}


def _movimientos(historial, documentos, observaciones, expediente):
    movimientos = [
        {
            "tipo": "creacion",
            "fecha": expediente.fecha_creacion,
            "estado_anterior": None,
            "estado_nuevo": E.ESTADO_BORRADOR,
            "requisito_nombre": None,
            "version": None,
        }
    ]
    for registro in historial:
        movimientos.append(
            {
                "tipo": "cambio_estado",
                "fecha": registro.fecha_cambio,
                "estado_anterior": registro.estado_anterior,
                "estado_nuevo": registro.estado_nuevo,
                "requisito_nombre": None,
                "version": None,
            }
        )
    for documento in documentos:
        movimientos.append(
            {
                "tipo": "documento_cargado",
                "fecha": documento.fecha_carga,
                "estado_anterior": None,
                "estado_nuevo": None,
                "requisito_nombre": documento.peticion.requisito.nombre,
                "version": documento.version,
            }
        )
    for observacion in observaciones:
        movimientos.append(
            {
                "tipo": "observacion",
                "fecha": observacion.fecha_registro,
                "estado_anterior": None,
                "estado_nuevo": None,
                "requisito_nombre": observacion.peticion.requisito.nombre,
                "version": None,
            }
        )
    movimientos.sort(key=lambda movimiento: movimiento["fecha"], reverse=True)
    return movimientos[:MAX_MOVIMIENTOS]


def _seleccionar_expediente(estudiante):
    """El expediente activo más reciente; si no hay, el último registrado."""
    base = ExpedienteTitulacion.objects.filter(estudiante=estudiante)
    return (
        base.filter(activa=True).order_by("-fecha_creacion").first()
        or base.order_by("-fecha_creacion").first()
    )


def _resumen_expediente(expediente):
    peticiones = list(
        PeticionDocumental.objects.filter(expediente=expediente)
        .select_related("requisito")
        .order_by("requisito__codigo_requisito")
    )
    historial = list(
        HistorialEstado.objects.filter(expediente=expediente).order_by("fecha_cambio")
    )
    documentos = list(
        DocumentoEntregado.objects.filter(peticion__expediente=expediente)
        .select_related("peticion__requisito")
        .order_by("-fecha_carga")[:MAX_MOVIMIENTOS]
    )
    observaciones = list(
        ObservacionAccionable.objects.filter(expediente=expediente)
        .select_related("peticion__requisito")
        .order_by("-fecha_registro")
    )

    etapas = _etapas(expediente, historial)
    # Misma regla de completitud que `enviar_expediente` (no se duplica).
    requisitos_sin_documento = [
        str(peticion.id)
        for peticion in peticiones
        if peticion.requisito.es_obligatorio_base
        and peticion.requisito.fase == "FASE_1"
        and peticion.requisito.activo
        and peticion.estado_peticion in ESTADOS_SIN_DOCUMENTO_VIGENTE
    ]

    return {
        "id": str(expediente.id),
        "numero_expediente": expediente.numero_expediente,
        "estado": expediente.estado,
        "activa": expediente.activa,
        "fecha_creacion": expediente.fecha_creacion,
        "fecha_recepcion": expediente.fecha_recepcion,
        "fecha_actualizacion": expediente.fecha_actualizacion,
        "fecha_limite_atencion": expediente.fecha_limite_atencion,
        "numero_providencia": expediente.numero_providencia,
        "etapas": etapas,
        "progreso": _progreso(expediente, etapas),
        "peticiones": [
            {
                "id": str(peticion.id),
                "requisito_codigo": peticion.requisito.codigo_requisito,
                "requisito_nombre": peticion.requisito.nombre,
                "estado_peticion": peticion.estado_peticion,
                "dependencia_emisora": peticion.dependencia_emisora,
                "fecha_actualizacion": peticion.fecha_actualizacion,
            }
            for peticion in peticiones
        ],
        "requisitos_sin_documento": requisitos_sin_documento,
        "puede_enviarse": (
            expediente.estado == E.ESTADO_BORRADOR and not requisitos_sin_documento
        ),
        # Solo el motivo, que ya se notifica al estudiante (DEC-01); nunca
        # quién la registró.
        "observaciones_pendientes": [
            {
                "id": str(observacion.id),
                "peticion_id": str(observacion.peticion_id),
                "requisito_nombre": observacion.peticion.requisito.nombre,
                "motivo_observacion": observacion.motivo_observacion,
                "fecha_registro": observacion.fecha_registro,
            }
            for observacion in observaciones
            if not observacion.resuelta
        ],
        "movimientos": _movimientos(historial, documentos, observaciones, expediente),
    }


def execute(estudiante):
    """Datos del panel del estudiante autenticado (sin parámetros del cliente)."""
    expediente = _seleccionar_expediente(estudiante)
    nombre = estudiante.get_full_name().strip()
    return {
        "estudiante": {
            "nombre_completo": nombre or None,
            "email": estudiante.email or None,
            "cedula": estudiante.cedula,
        },
        "total_expedientes": ExpedienteTitulacion.objects.filter(
            estudiante=estudiante
        ).count(),
        "expediente": _resumen_expediente(expediente) if expediente else None,
    }
