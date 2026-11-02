"""Señales Django para bitácora inmutable de auditoría (T039; Principio C-008).

Captura automáticamente eventos de negocio y los registra en EventoAuditoria
con formato JSONB inmutable.
"""

import logging

from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from apps.notificaciones.adapters.models import EventoAuditoria
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.peticiones.adapters.models import PeticionDocumental, DocumentoEntregado
from apps.resoluciones.adapters.models import InformeAptitud, DeclaratoriaAptitud
from apps.verificacion.adapters.models import ChecklistVerification, ObservacionAccionable

logger = logging.getLogger(__name__)


def _get_client_ip(request):
    """Extrae la IP del cliente desde el request."""
    if request is None:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _get_current_request():
    """Obtiene el request actual (si está disponible en thread local)."""
    # En producción se usaría middleware para guardar request en thread local
    # Por ahora retornamos None y se llenará desde la vista
    return None


def _crear_evento_auditoria(
    accion,
    usuario,
    expediente,
    detalles,
    ip=None,
):
    """Crea un registro inmutable en EventoAuditoria."""
    try:
        # Obtener rol del usuario
        roles = list(usuario.get_roles()) if hasattr(usuario, "get_roles") else []
        rol_usuario = roles[0] if roles else "DESCONOCIDO"

        # Obtener IP si no se proporciona
        if ip is None:
            request = _get_current_request()
            ip = _get_client_ip(request)

        EventoAuditoria.objects.create(
            accion=accion,
            usuario=usuario,
            rol_usuario=rol_usuario,
            expediente=expediente,
            ip=ip,
            timestamp=timezone.now(),
            detalles=detalles,
        )
        logger.info(
            f"EventoAuditoria creado: {accion} by {usuario} on expediente {expediente.id}"
        )
    except Exception as e:
        # Log pero no romper la operación principal
        logger.error(f"Error creando EventoAuditoria: {e}", exc_info=True)


# ============================================================
# Señales para ExpedienteTitulacion
# ============================================================

@receiver(pre_save, sender=ExpedienteTitulacion)
def expediente_pre_save(sender, instance, **kwargs):
    """Captura estado anterior antes de guardar."""
    if instance.pk:
        try:
            anterior = ExpedienteTitulacion.objects.get(pk=instance.pk)
            instance._estado_anterior = anterior.estado
        except ExpedienteTitulacion.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None


@receiver(post_save, sender=ExpedienteTitulacion)
def expediente_post_save(sender, instance, created, **kwargs):
    """Registra creación de expediente o cambio de estado."""
    if created:
        _crear_evento_auditoria(
            accion=EventoAuditoria.Accion.EXPEDIENTE_CREADO,
            usuario=instance.estudiante,
            expediente=instance,
            detalles={
                "numero_expediente": instance.numero_expediente,
                "estado_inicial": instance.estado,
                "fecha_creacion": instance.fecha_creacion.isoformat() if instance.fecha_creacion else None,
            },
        )
    else:
        # Verificar cambio de estado
        if hasattr(instance, "_estado_anterior") and instance._estado_anterior != instance.estado:
            _crear_evento_auditoria(
                accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
                # El usuario que causó el cambio se determina por contexto
                # En la práctica se pasaría desde la vista; aquí usamos estudiante como fallback
                usuario=instance.estudiante,
                expediente=instance,
                detalles={
                    "estado_anterior": instance._estado_anterior,
                    "estado_nuevo": instance.estado,
                    "fecha_cambio": timezone.now().isoformat(),
                },
            )


# ============================================================
# Señales para HistorialEstado (cambio de estado explícito)
# ============================================================

@receiver(post_save, sender="expedientes.HistorialEstado")
def historial_estado_post_save(sender, instance, created, **kwargs):
    """Registra cambios de estado explícitos."""
    if created:
        _crear_evento_auditoria(
            accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
            usuario=instance.registrado_por,
            expediente=instance.expediente,
            detalles={
                "estado_anterior": instance.estado_anterior,
                "estado_nuevo": instance.estado_nuevo,
                "fecha_cambio": instance.fecha_cambio.isoformat() if instance.fecha_cambio else None,
                "registrado_por_id": str(instance.registrado_por_id) if instance.registrado_por_id else None,
            },
        )


# ============================================================
# Señales para ChecklistVerification
# ============================================================

@receiver(post_save, sender=ChecklistVerification)
def checklist_verification_post_save(sender, instance, created, **kwargs):
    """Registra evaluación de checklist."""
    if created or instance.estado_verificacion in ["VERIFICADO", "OBSERVADO"]:
        # Solo crear auditoría si hay un usuario evaluador
        if instance.evaluado_por:
            detalles = {
                "requisito_id": str(instance.requisito_id),
                "requisito_codigo": instance.requisito.codigo_requisito if instance.requisito else None,
                "estado_verificacion": instance.estado_verificacion,
                "evaluado_por_id": str(instance.evaluado_por_id) if instance.evaluado_por_id else None,
                "fecha_evaluacion": instance.fecha_evaluacion.isoformat() if instance.fecha_evaluacion else None,
            }
            # Solo agregar motivo_observacion si es OBSERVADO
            if instance.estado_verificacion == "OBSERVADO":
                # Buscar la observación asociada
                from apps.verificacion.adapters.models import ObservacionAccionable
                observacion = ObservacionAccionable.objects.filter(
                    expediente=instance.expediente,
                    peticion__requisito=instance.requisito,
                    resuelta=False,
                ).first()
                if observacion:
                    detalles["motivo_observacion"] = observacion.motivo_observacion

            _crear_evento_auditoria(
                accion=EventoAuditoria.Accion.CHECKLIST_EVALUADO,
                usuario=instance.evaluado_por,
                expediente=instance.expediente,
                detalles=detalles,
            )


# ============================================================
# Señales para ObservacionAccionable
# ============================================================

@receiver(post_save, sender=ObservacionAccionable)
def observacion_post_save(sender, instance, created, **kwargs):
    """Registra registro de observación."""
    if created:
        _crear_evento_auditoria(
            accion=EventoAuditoria.Accion.OBSERVACION_REGISTRADA,
            usuario=instance.registrada_por,
            expediente=instance.expediente,
            detalles={
                "peticion_id": str(instance.peticion_id),
                "requisito_codigo": instance.peticion.requisito.codigo_requisito if instance.peticion and instance.peticion.requisito else None,
                "motivo_observacion": instance.motivo_observacion,
                "registrada_por_id": str(instance.registrada_por_id) if instance.registrada_por_id else None,
            },
        )


# ============================================================
# Señales para DocumentoEntregado (carga de documentos)
# ============================================================

@receiver(post_save, sender="peticiones.DocumentoEntregado")
def documento_entregado_post_save(sender, instance, created, **kwargs):
    """Registra carga de documento."""
    if created:
        _crear_evento_auditoria(
            accion=EventoAuditoria.Accion.DOCUMENTO_CARGADO,
            usuario=instance.subido_por,
            expediente=instance.peticion.expediente,
            detalles={
                "peticion_id": str(instance.peticion_id),
                "requisito_codigo": instance.peticion.requisito.codigo_requisito if instance.peticion and instance.peticion.requisito else None,
                "version": instance.version,
                "nombre_original": instance.nombre_original,
                "tamanio_bytes": instance.tamanio_bytes,
                "hash_sha256": instance.hash_sha256,
                "tipo_mime": instance.tipo_mime,
                "subido_por_id": str(instance.subido_por_id),
            },
        )


# ============================================================
# Señales para InformeAptitud (Providencia N° 590)
# ============================================================

@receiver(post_save, sender=InformeAptitud)
def informe_aptitud_post_save(sender, instance, created, **kwargs):
    """Registra emisión de informe legal."""
    if created:
        _crear_evento_auditoria(
            accion=EventoAuditoria.Accion.INFORME_EMITIDO,
            usuario=instance.emisor,
            expediente=instance.expediente,
            detalles={
                "numero_providencia": instance.numero_providencia,
                "dictamen": instance.dictamen,
                "archivo_informe_path": instance.archivo_informe_path,
                "emisor_id": str(instance.emisor_id),
            },
        )


# ============================================================
# Señales para DeclaratoriaAptitud (Memorando N° 162)
# ============================================================

@receiver(post_save, sender=DeclaratoriaAptitud)
def declaratoria_aptitud_post_save(sender, instance, created, **kwargs):
    """Registra registro de declaratoria."""
    if created:
        _crear_evento_auditoria(
            accion=EventoAuditoria.Accion.DECLARATORIA_REGISTRADA,
            usuario=instance.decano,
            expediente=instance.expediente,
            detalles={
                "numero_memorando": instance.numero_memorando,
                "archivo_memorando_firmado_path": instance.archivo_memorando_firmado_path,
                "decano_id": str(instance.decano_id),
            },
        )