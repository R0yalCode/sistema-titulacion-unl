"""Exports del módulo resoluciones.services."""

from apps.resoluciones.services.emitir_informe import (
    execute as emitir_informe,
    InformeYaExisteError,
    ExpedienteNoValidoParaInformeError,
    UsuarioNoAutorizadoError,
)
from apps.resoluciones.services.declarar_aptitud import (
    execute as declarar_aptitud,
    DeclaratoriaYaExisteError,
    ExpedienteNoValidoParaDeclaratoriaError,
    UsuarioNoAutorizadoError as UsuarioNoAutorizadoErrorDeclaratoria,
    PDFInvalidoError,
)

__all__ = [
    "emitir_informe",
    "InformeYaExisteError",
    "ExpedienteNoValidoParaInformeError",
    "UsuarioNoAutorizadoError",
    "declarar_aptitud",
    "DeclaratoriaYaExisteError",
    "ExpedienteNoValidoParaDeclaratoriaError",
    "UsuarioNoAutorizadoErrorDeclaratoria",
    "PDFInvalidoError",
]