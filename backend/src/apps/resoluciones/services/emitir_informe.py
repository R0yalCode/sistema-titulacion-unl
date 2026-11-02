"""Caso de uso para emisión e inmutabilización del informe legal (T034; HU-009, RF-009, RN-004, CA-005).

Emite el informe legal de aptitud (Providencia N° 590) cuando el checklist está 100% verificado.
Inmutabiliza el registro, cambia el expediente a INFORME_EMITIDO y notifica al Decano/a.
"""

from django.db import transaction
from django.utils import timezone

from apps.resoluciones.adapters.models import InformeAptitud
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.verificacion.services import validar_checklist_completo
from apps.resoluciones.adapters.pdf_generator import PDFGeneratorAdapter
from apps.notificaciones.adapters.models import NotificacionInterna


class InformeYaExisteError(Exception):
    """El expediente ya tiene un informe de aptitud emitido."""


class ExpedienteNoValidoParaInformeError(Exception):
    """El expediente no cumple los requisitos para emitir informe."""


class UsuarioNoAutorizadoError(Exception):
    """El usuario no tiene permisos para emitir informes."""


def _generar_numero_providencia(expediente: ExpedienteTitulacion) -> str:
    """Genera número de providencia único: PROV-590-YYYY-NNNN."""
    from django.db.models import Max
    anio = timezone.now().year
    # Buscar el último número de providencia de este año
    ultimo = InformeAptitud.objects.filter(
        numero_providencia__startswith=f"PROV-590-{anio}-"
    ).aggregate(Max("numero_providencia"))
    if ultimo["numero_providencia__max"]:
        try:
            ultimo_num = int(ultimo["numero_providencia__max"].split("-")[-1])
            nuevo_num = ultimo_num + 1
        except (ValueError, IndexError):
            nuevo_num = 1
    else:
        nuevo_num = 1
    return f"PROV-590-{anio}-{nuevo_num:04d}"


def _obtener_datos_expediente_para_pdf(expediente: ExpedienteTitulacion) -> dict:
    """Obtiene los datos del expediente formateados para el generador de PDF."""
    from apps.peticiones.adapters.models import PeticionDocumental

    peticiones = PeticionDocumental.objects.filter(
        expediente=expediente
    ).select_related("requisito").order_by("requisito__codigo_requisito")

    checklist = []
    for p in peticiones:
        checklist.append({
            "codigo": p.requisito.codigo_requisito,
            "nombre": p.requisito.nombre,
            "estado": p.estado_peticion,
            "observacion": "",
        })

    return {
        "numero_expediente": expediente.numero_expediente,
        "estudiante_nombre": expediente.estudiante.get_full_name() or expediente.estudiante.username,
        "estudiante_cedula": expediente.estudiante.cedula or "N/A",
        "carrera_nombre": "Computación",  # TODO: obtener de catálogo si está disponible
        "facultad_nombre": "FEIRNNR",
        "fecha_recepcion": expediente.fecha_recepcion.strftime("%d/%m/%Y") if expediente.fecha_recepcion else "N/A",
        "fecha_limite_atencion": expediente.fecha_limite_atencion.strftime("%d/%m/%Y") if expediente.fecha_limite_atencion else "N/A",
    }, checklist


def _obtener_decanos_facultad(facultad_id: str):
    """Obtiene los usuarios con rol DECANO de la facultad dada."""
    from apps.authentication.adapters.models import User, Role, UserRole

    try:
        rol_decano = Role.objects.get(name="DECANO")
        return User.objects.filter(
            role_assignments__role=rol_decano,
            facultad_id=facultad_id,
        ).distinct()
    except Role.DoesNotExist:
        return User.objects.none()


def _crear_notificacion_decano(expediente: ExpedienteTitulacion, numero_providencia: str, decanos):
    """Crea notificaciones internas para el/los decano(s) de la facultad."""
    for decano in decanos:
        NotificacionInterna.objects.create(
            usuario_destino=decano,
            expediente=expediente,
            titulo=f"Informe Legal Emitido - {expediente.numero_expediente}",
            mensaje=(
                f"Se ha emitido el Informe Legal de Aptitud (Providencia N° {numero_providencia}) "
                f"para el expediente {expediente.numero_expediente}. "
                f"El expediente ha cambiado al estado INFORME_EMITIDO y está listo para la "
                f"Declaratoria de Aptitud por parte del Decanato."
            ),
        )


def execute(usuario, expediente_id, dictamen: str = "APTO", fundamentacion: str = ""):
    """
    Emite el informe legal de aptitud (Providencia N° 590).

    Args:
        usuario: Usuario autenticado (SECRETARIO_ABOGADO)
        expediente_id: UUID del expediente
        dictamen: "APTO" o "NO APTO"
        fundamentacion: Fundamentación jurídica adicional (opcional)

    Returns:
        InformeAptitud creado

    Raises:
        ExpedienteNoValidoParaInformeError: Si el expediente no cumple requisitos
        InformeYaExisteError: Si ya existe informe para este expediente
        UsuarioNoAutorizadoError: Si el usuario no tiene permisos
        ChecklistIncompletoError: Si el checklist no está 100% verificado
    """
    # Validar rol del usuario
    if not usuario.has_role("SECRETARIO_ABOGADO"):
        raise UsuarioNoAutorizadoError(
            "Solo SECRETARIO_ABOGADO puede emitir informes legales de aptitud."
        )

    # Validar dictamen
    if dictamen not in ("APTO", "NO APTO"):
        raise ValueError("El dictamen debe ser 'APTO' o 'NO APTO'.")

    with transaction.atomic():
        # Obtener expediente con bloqueo
        try:
            expediente = ExpedienteTitulacion.objects.select_for_update().get(pk=expediente_id)
        except ExpedienteTitulacion.DoesNotExist:
            raise ValueError("El expediente no existe.")

        # Verificar que no tenga informe ya emitido
        if hasattr(expediente, "informe_aptitud"):
            raise InformeYaExisteError(
                f"El expediente {expediente.numero_expediente} ya tiene un informe emitido."
            )

        # Validar que el usuario pertenezca a la facultad del expediente
        user_facultad = str(usuario.facultad_id) if usuario.facultad_id else None
        expediente_facultad = str(expediente.facultad_id) if expediente.facultad_id else None
        if user_facultad != expediente_facultad:
            raise UsuarioNoAutorizadoError(
                "El usuario no pertenece a la facultad del expediente."
            )

        # Validar checklist completo (T029 / RN-003)
        validar_checklist_completo.execute(expediente_id)

        # Verificar que el dictamen sea APTO (si es NO APTO, no se debe emitir informe)
        if dictamen == "NO APTO":
            raise ExpedienteNoValidoParaInformeError(
                "No se puede emitir informe con dictamen NO APTO. "
                "El expediente debe ser observado o subsanado."
            )

        # Generar número de providencia
        numero_providencia = _generar_numero_providencia(expediente)

        # Preparar datos para PDF
        datos_expediente, checklist = _obtener_datos_expediente_para_pdf(expediente)
        datos_secretario = {
            "nombre_completo": usuario.get_full_name() or usuario.username,
            "cargo": "SECRETARIO/A-ABOGADO/A - FEIRNNR",
            "ci": usuario.cedula or "N/A",
        }

        # Generar PDF de la Providencia N° 590
        pdf_generator = PDFGeneratorAdapter()
        archivo_pdf = pdf_generator.generar_providencia_590(
            expediente=datos_expediente,
            secretario=datos_secretario,
            checklist=checklist,
            dictamen=dictamen,
            numero_providencia=numero_providencia,
            archivo_salida=None,  # Auto-generar
            es_borrador=False,  # Informe final
        )

        # Crear registro InformeAptitud (inmutable)
        informe = InformeAptitud.objects.create(
            expediente=expediente,
            numero_providencia=numero_providencia,
            emisor=usuario,
            dictamen=dictamen,
            archivo_informe_path=archivo_pdf,
        )

        # Actualizar expediente
        expediente.estado = ExpedienteTitulacion.ESTADO_INFORME_EMITIDO
        expediente.numero_providencia = numero_providencia
        expediente.fecha_actualizacion = timezone.now()
        expediente.save(update_fields=["estado", "numero_providencia", "fecha_actualizacion"])

        # Registrar en historial de estados
        from apps.expedientes.adapters.models import HistorialEstado
        HistorialEstado.objects.create(
            expediente=expediente,
            estado_anterior=expediente.estado,  # Se guardará el anterior
            estado_nuevo=ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
            registrado_por=usuario,
        )

        # Notificar al Decano/a
        decanos = _obtener_decanos_facultad(expediente.facultad_id)
        if decanos.exists():
            _crear_notificacion_decano(expediente, numero_providencia, decanos)

        return informe