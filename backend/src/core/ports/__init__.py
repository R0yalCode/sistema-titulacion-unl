"""Puertos de salida (Output Ports) para arquitectura hexagonal.

Define las interfaces abstractas que el dominio utiliza para interactuar
con sistemas externos (adaptadores). Los adaptadores concretos implementan
estos puertos (ej. SGAMockAdapter, futuros SGA_REST_Adapter, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AsignaturaRecord:
    """Representa una asignatura en el récord académico del SGA.

    Inmutable: el SGT-SIAAF no recalcula ni modifica estos datos (DEC-05, RN-005).
    """

    codigo: str
    nombre: str
    creditos: int
    calificacion: float  # Escala 0-10 o 0-20 según normativa
    estado: str  # APROBADA, REPROBADA, HOMOLOGADA, CONVALIDADA
    fecha_aprobacion: Optional[str] = None  # ISO 8601


@dataclass(frozen=True)
class RecordAcademicoSGA:
    """Récord académico completo provisto por el SGA (inmutable).

    El promedio ya viene calculado por el SGA incluyendo homologaciones.
    El SGT-SIAAF lo consume como insumo de lectura inalterable (DEC-05, AP-07).
    """

    cedula: str
    estudiante_nombre: str
    carrera: str
    facultad: str
    asignaturas: tuple[AsignaturaRecord, ...]
    promedio_final: float  # Promedio ponderado calculado por el SGA
    total_creditos: int
    creditos_aprobados: int
    fecha_emision: str  # ISO 8601


class ISGALegacyPort(ABC):
    """Puerto abstracto para consulta de récords académicos del SGA.

    Implementaciones:
    - SGAMockAdapter (MVP actual): datos ficticios en JSON/archivo
    - SGA_REST_Adapter (Fase futura): llamada HTTP real al SGA institucional
    """

    @abstractmethod
    def obtener_record_por_cedula(self, cedula: str) -> Optional[RecordAcademicoSGA]:
        """Obtiene el récord académico completo por cédula del estudiante.

        Args:
            cedula: Número de cédula/identificación del estudiante.

        Returns:
            RecordAcademicoSGA si existe, None si no se encuentra.
            Nunca lanza excepción por "no encontrado"; usa None.

        Raises:
            SGAConnectionError: Si hay fallo de comunicación (solo adaptadores reales).
            SGAValidationError: Si la respuesta del SGA es inválida.
        """
        ...

    @abstractmethod
    def obtener_promedio_por_cedula(self, cedula: str) -> Optional[float]:
        """Obtiene solo el promedio final del récord académico.

        Versión optimizada para casos donde solo se requiere el promedio
        (ej. cálculo de nota final de titulación en Fase 2).

        Args:
            cedula: Número de cédula/identificación del estudiante.

        Returns:
            Promedio final (float) si existe, None si no se encuentra.
        """
        ...


class SGAConnectionError(Exception):
    """Excepción para errores de conexión con el SGA (adaptadores reales)."""

    pass


class SGAValidationError(Exception):
    """Excepción para respuestas inválidas del SGA."""

    pass
