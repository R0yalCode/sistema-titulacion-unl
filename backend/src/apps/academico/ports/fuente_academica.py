"""Puerto de la fuente académica institucional.

Separa *de dónde* sale la información académica del estudiante (hoy la
simulación MockSGA; en el futuro un `SGAAdapter` real) del resto del sistema:
la validación del perfil (`AcademicProfileService`), la creación del
expediente, el RBAC y el contrato `GET /api/v1/perfil-academico/` no cambian
al sustituir el adaptador.

Ver docs/academico/perfil-academico-mock-sga.md.
"""

from typing import Protocol

from apps.academico.domain.perfil import RegistroAcademicoFuente


class FuenteAcademicaNoDisponibleError(Exception):
    """La fuente no respondió o respondió con un formato inválido (503)."""


class FuenteAcademicaNoConfiguradaError(FuenteAcademicaNoDisponibleError):
    """No hay una fuente académica habilitada en esta configuración (503).

    Incluye el caso en que se configura la simulación MockSGA en un entorno
    que no la permite expresamente (p. ej. producción).
    """


class FuenteAcademica(Protocol):
    """Contrato mínimo de una fuente de perfiles académicos."""

    #: Código estable de la fuente (p. ej. "MOCK_SGA", en el futuro "SGA").
    codigo: str
    #: Nombre legible que se muestra al estudiante.
    nombre: str
    #: True si los datos NO provienen de un sistema institucional real.
    es_simulada: bool

    def consultar_por_identificacion(
        self, identificacion: str
    ) -> RegistroAcademicoFuente | None:
        """Registro académico del estudiante con esa identificación.

        Devuelve None si la fuente no tiene registro para esa persona.
        Lanza `FuenteAcademicaNoDisponibleError` ante fallos de la fuente;
        nunca inventa datos.
        """
        ...
