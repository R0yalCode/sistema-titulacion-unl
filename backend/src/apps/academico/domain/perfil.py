"""Modelo de dominio del perfil académico del estudiante.

El perfil académico es la información que SGT-SIAAF necesita de la fuente
académica institucional (hoy, la simulación MockSGA; en el futuro, el SGA de
la UNL) para iniciar un trámite: identidad del estudiante, carrera y la
facultad que esa carrera determina.

Estas estructuras no dependen de Django ni de ninguna fuente concreta: las
produce `AcademicProfileService` a partir de lo que devuelva el puerto
`FuenteAcademica`, de modo que sustituir la fuente no cambia el contrato.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EstadoPerfil(str, Enum):
    """Resultado de la validación de integridad del perfil."""

    VALIDADO = "VALIDADO"
    NO_ASOCIADO = "NO_ASOCIADO"
    INCOMPLETO = "INCOMPLETO"
    INCONSISTENTE = "INCONSISTENTE"
    CARRERA_INACTIVA = "CARRERA_INACTIVA"


#: Orden de gravedad: el estado del perfil es el del motivo más grave.
GRAVEDAD = (
    EstadoPerfil.NO_ASOCIADO,
    EstadoPerfil.INCOMPLETO,
    EstadoPerfil.INCONSISTENTE,
    EstadoPerfil.CARRERA_INACTIVA,
)


# Códigos estables de los motivos de bloqueo (los consume el cliente).
MOTIVO_NO_ASOCIADO = "perfil_academico_no_asociado"
MOTIVO_IDENTIFICACION_NO_REGISTRADA = "identificacion_no_registrada"
MOTIVO_DATOS_PERSONALES_INCOMPLETOS = "datos_personales_incompletos"
MOTIVO_CARRERA_NO_REGISTRADA = "carrera_no_registrada"
MOTIVO_CARRERA_NO_CATALOGADA = "carrera_no_catalogada"
MOTIVO_FACULTAD_NO_CORRESPONDE = "facultad_no_corresponde"
MOTIVO_CORREO_NO_CORRESPONDE = "correo_no_corresponde"
MOTIVO_ASOCIACION_LOCAL_INCONSISTENTE = "asociacion_local_inconsistente"
MOTIVO_CARRERA_INACTIVA = "carrera_inactiva"
MOTIVO_FACULTAD_INACTIVA = "facultad_inactiva"


@dataclass(frozen=True)
class RegistroAcademicoFuente:
    """Datos tal como los entrega la fuente académica (sin interpretar).

    Los códigos de carrera y facultad son los de la fuente; el servicio los
    resuelve contra el catálogo interno de SGT-SIAAF.
    """

    identificacion: str
    nombres: str
    apellidos: str
    correo_institucional: str
    codigo_carrera: str
    codigo_facultad: str


@dataclass(frozen=True)
class FuenteInfo:
    """Identifica la fuente que produjo el perfil."""

    codigo: str
    nombre: str
    es_simulada: bool


@dataclass(frozen=True)
class FacultadPerfil:
    id: str
    codigo: str
    nombre: str
    activa: bool


@dataclass(frozen=True)
class CarreraPerfil:
    id: str
    codigo: str
    nombre: str
    activa: bool


@dataclass(frozen=True)
class EstudiantePerfil:
    identificacion: str
    nombres: str
    apellidos: str
    correo_institucional: str


@dataclass(frozen=True)
class MotivoBloqueo:
    codigo: str
    mensaje: str
    estado: EstadoPerfil


@dataclass(frozen=True)
class PerfilAcademico:
    """Perfil académico validado (o los motivos por los que no lo está)."""

    fuente: FuenteInfo
    consultado_en: datetime
    estudiante: EstudiantePerfil | None = None
    carrera: CarreraPerfil | None = None
    facultad: FacultadPerfil | None = None
    motivos: tuple[MotivoBloqueo, ...] = field(default_factory=tuple)

    @property
    def estado(self) -> EstadoPerfil:
        for estado in GRAVEDAD:
            if any(m.estado == estado for m in self.motivos):
                return estado
        return EstadoPerfil.VALIDADO

    @property
    def validado(self) -> bool:
        return self.estado == EstadoPerfil.VALIDADO
