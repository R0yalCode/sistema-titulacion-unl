"""`AcademicProfileService`: perfil académico validado del usuario autenticado.

Consulta la fuente académica configurada (puerto `FuenteAcademica`) con la
cédula de la cuenta autenticada —nunca con un dato enviado por el cliente—,
resuelve la carrera contra el catálogo interno, deriva la facultad de la
carrera y valida la integridad del resultado.

No implementa reglas de elegibilidad académica de titulación (créditos,
promedio, prácticas, etc.): no están documentadas ni la fuente simulada
puede comprobarlas. Solo valida lo necesario para asociar el trámite a una
carrera vigente: identidad, datos completos, carrera catalogada y activa, y
coherencia entre fuente, catálogo y cuenta.
"""

from django.utils import timezone

from apps.academico.adapters.models import Carrera
from apps.academico.domain.perfil import (
    MOTIVO_ASOCIACION_LOCAL_INCONSISTENTE,
    MOTIVO_CARRERA_INACTIVA,
    MOTIVO_CARRERA_NO_CATALOGADA,
    MOTIVO_CARRERA_NO_REGISTRADA,
    MOTIVO_CORREO_NO_CORRESPONDE,
    MOTIVO_DATOS_PERSONALES_INCOMPLETOS,
    MOTIVO_FACULTAD_INACTIVA,
    MOTIVO_FACULTAD_NO_CORRESPONDE,
    MOTIVO_IDENTIFICACION_NO_REGISTRADA,
    MOTIVO_NO_ASOCIADO,
    CarreraPerfil,
    EstadoPerfil,
    EstudiantePerfil,
    FacultadPerfil,
    FuenteInfo,
    MotivoBloqueo,
    PerfilAcademico,
)
from apps.academico.ports.fuente_academica import (
    FuenteAcademica,
    FuenteAcademicaNoDisponibleError,
)
from apps.academico.services.fuentes import get_fuente_academica

MENSAJES = {
    MOTIVO_IDENTIFICACION_NO_REGISTRADA: (
        "Su cuenta no tiene una identificación registrada, por lo que no es "
        "posible consultar su información académica. Acuda a la Secretaría "
        "de su carrera."
    ),
    MOTIVO_NO_ASOCIADO: (
        "No se encontró su información académica en la fuente institucional. "
        "Acuda a la Secretaría de su carrera para verificar su registro."
    ),
    MOTIVO_DATOS_PERSONALES_INCOMPLETOS: (
        "Su información académica está incompleta (nombres, apellidos o "
        "correo institucional). Solicite su actualización en la Secretaría "
        "de su carrera."
    ),
    MOTIVO_CARRERA_NO_REGISTRADA: (
        "Su información académica no indica una carrera. Solicite su "
        "actualización en la Secretaría de su carrera."
    ),
    MOTIVO_CARRERA_NO_CATALOGADA: (
        "La carrera registrada en su información académica no está en el "
        "catálogo del sistema. Comuníquese con la Secretaría de su carrera."
    ),
    MOTIVO_FACULTAD_NO_CORRESPONDE: (
        "La facultad registrada en su información académica no corresponde "
        "a su carrera. Comuníquese con la Secretaría de su carrera."
    ),
    MOTIVO_CORREO_NO_CORRESPONDE: (
        "El correo institucional de su información académica no coincide "
        "con el de su cuenta. Comuníquese con la Secretaría de su carrera."
    ),
    MOTIVO_ASOCIACION_LOCAL_INCONSISTENTE: (
        "La carrera o facultad asignadas a su cuenta no coinciden con su "
        "información académica. Comuníquese con la Secretaría de su carrera."
    ),
    MOTIVO_CARRERA_INACTIVA: (
        "Su carrera no está vigente en el catálogo del sistema; no es "
        "posible iniciar un trámite. Comuníquese con la Secretaría de su "
        "carrera."
    ),
    MOTIVO_FACULTAD_INACTIVA: (
        "La facultad de su carrera no está vigente en el catálogo del "
        "sistema; no es posible iniciar un trámite."
    ),
}

ESTADO_POR_MOTIVO = {
    MOTIVO_IDENTIFICACION_NO_REGISTRADA: EstadoPerfil.INCOMPLETO,
    MOTIVO_NO_ASOCIADO: EstadoPerfil.NO_ASOCIADO,
    MOTIVO_DATOS_PERSONALES_INCOMPLETOS: EstadoPerfil.INCOMPLETO,
    MOTIVO_CARRERA_NO_REGISTRADA: EstadoPerfil.INCOMPLETO,
    MOTIVO_CARRERA_NO_CATALOGADA: EstadoPerfil.INCONSISTENTE,
    MOTIVO_FACULTAD_NO_CORRESPONDE: EstadoPerfil.INCONSISTENTE,
    MOTIVO_CORREO_NO_CORRESPONDE: EstadoPerfil.INCONSISTENTE,
    MOTIVO_ASOCIACION_LOCAL_INCONSISTENTE: EstadoPerfil.INCONSISTENTE,
    MOTIVO_CARRERA_INACTIVA: EstadoPerfil.CARRERA_INACTIVA,
    MOTIVO_FACULTAD_INACTIVA: EstadoPerfil.CARRERA_INACTIVA,
}


def _motivo(codigo: str) -> MotivoBloqueo:
    return MotivoBloqueo(
        codigo=codigo, mensaje=MENSAJES[codigo], estado=ESTADO_POR_MOTIVO[codigo]
    )


class AcademicProfileService:
    """Obtiene y valida el perfil académico de un usuario autenticado."""

    def __init__(self, fuente: FuenteAcademica):
        self._fuente = fuente

    @property
    def fuente(self) -> FuenteInfo:
        return FuenteInfo(
            codigo=self._fuente.codigo,
            nombre=self._fuente.nombre,
            es_simulada=bool(self._fuente.es_simulada),
        )

    def obtener_perfil(self, usuario) -> PerfilAcademico:
        fuente = self.fuente
        consultado_en = timezone.now()
        identificacion = (getattr(usuario, "cedula", None) or "").strip()
        if not identificacion:
            return PerfilAcademico(
                fuente=fuente,
                consultado_en=consultado_en,
                motivos=(_motivo(MOTIVO_IDENTIFICACION_NO_REGISTRADA),),
            )

        try:
            registro = self._fuente.consultar_por_identificacion(identificacion)
        except FuenteAcademicaNoDisponibleError:
            raise
        except Exception as error:  # cualquier fallo del adaptador es un 503
            raise FuenteAcademicaNoDisponibleError(
                "La fuente académica no respondió correctamente."
            ) from error

        if registro is None:
            return PerfilAcademico(
                fuente=fuente,
                consultado_en=consultado_en,
                motivos=(_motivo(MOTIVO_NO_ASOCIADO),),
            )
        if (registro.identificacion or "").strip() != identificacion:
            # Una fuente que devuelve a otra persona es un fallo de la fuente:
            # nunca se muestran ni se usan esos datos.
            raise FuenteAcademicaNoDisponibleError(
                "La fuente académica devolvió un registro que no corresponde."
            )

        motivos: list[str] = []
        estudiante = EstudiantePerfil(
            identificacion=identificacion,
            nombres=(registro.nombres or "").strip(),
            apellidos=(registro.apellidos or "").strip(),
            correo_institucional=(registro.correo_institucional or "").strip(),
        )
        if not (
            estudiante.nombres
            and estudiante.apellidos
            and estudiante.correo_institucional
        ):
            motivos.append(MOTIVO_DATOS_PERSONALES_INCOMPLETOS)
        correo_cuenta = (getattr(usuario, "email", "") or "").strip()
        if (
            estudiante.correo_institucional
            and correo_cuenta
            and estudiante.correo_institucional.lower() != correo_cuenta.lower()
        ):
            motivos.append(MOTIVO_CORREO_NO_CORRESPONDE)

        carrera_perfil = None
        facultad_perfil = None
        codigo_carrera = (registro.codigo_carrera or "").strip()
        if not codigo_carrera:
            motivos.append(MOTIVO_CARRERA_NO_REGISTRADA)
        else:
            carrera = (
                Carrera.objects.select_related("facultad")
                .filter(codigo=codigo_carrera)
                .first()
            )
            if carrera is None:
                motivos.append(MOTIVO_CARRERA_NO_CATALOGADA)
            else:
                facultad = carrera.facultad
                carrera_perfil = CarreraPerfil(
                    id=str(carrera.id),
                    codigo=carrera.codigo,
                    nombre=carrera.nombre,
                    activa=carrera.activa,
                )
                facultad_perfil = FacultadPerfil(
                    id=str(facultad.id),
                    codigo=facultad.codigo,
                    nombre=facultad.nombre,
                    activa=facultad.activa,
                )
                codigo_facultad = (registro.codigo_facultad or "").strip()
                if codigo_facultad and codigo_facultad != facultad.codigo:
                    motivos.append(MOTIVO_FACULTAD_NO_CORRESPONDE)
                carrera_cuenta = getattr(usuario, "carrera_id", None)
                facultad_cuenta = getattr(usuario, "facultad_id", None)
                if (carrera_cuenta and str(carrera_cuenta) != str(carrera.id)) or (
                    facultad_cuenta and str(facultad_cuenta) != str(facultad.id)
                ):
                    motivos.append(MOTIVO_ASOCIACION_LOCAL_INCONSISTENTE)
                if not carrera.activa:
                    motivos.append(MOTIVO_CARRERA_INACTIVA)
                if not facultad.activa:
                    motivos.append(MOTIVO_FACULTAD_INACTIVA)

        return PerfilAcademico(
            fuente=fuente,
            consultado_en=consultado_en,
            estudiante=estudiante,
            carrera=carrera_perfil,
            facultad=facultad_perfil,
            motivos=tuple(_motivo(codigo) for codigo in motivos),
        )


def get_academic_profile_service() -> AcademicProfileService:
    """Servicio con la fuente configurada (503 si no hay ninguna habilitada)."""
    return AcademicProfileService(get_fuente_academica())
