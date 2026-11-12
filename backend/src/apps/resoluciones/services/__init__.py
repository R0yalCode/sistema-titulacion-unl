"""Exports del módulo resoluciones.services."""

from apps.resoluciones.services.emitir_informe import (
    execute as emitir_informe,
    InformeYaExisteError,
    ExpedienteNoValidoParaInformeError,
    UsuarioNoAutorizadoError,
    ExpedienteNoEncontradoError,
    ReglaPendienteO1Error,
)
from apps.resoluciones.services.declarar_aptitud import (
    execute as declarar_aptitud,
    DeclaratoriaYaExisteError,
    ExpedienteNoValidoParaDeclaratoriaError,
    UsuarioNoAutorizadoError as UsuarioNoAutorizadoErrorDeclaratoria,
    PDFInvalidoError,
    ExpedienteNoEncontradoError as ExpedienteNoEncontradoErrorDeclaratoria,
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
    "ExpedienteNoEncontradoError",
    "ExpedienteNoEncontradoErrorDeclaratoria",
    "ReglaPendienteO1Error",
]