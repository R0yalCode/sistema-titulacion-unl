"""Selección explícita de la fuente académica (`ACADEMIC_PROFILE_PROVIDER`).

- `""` (por defecto fuera de DEBUG): no hay fuente; el perfil y la creación
  de expedientes responden 503 `servicio_academico_no_configurado`.
- `"mock_sga"`: simulación MockSGA. Solo se habilita si además
  `ACADEMIC_PROFILE_MOCK_ALLOWED` es verdadero (por defecto, solo en DEBUG):
  un despliegue de producción nunca la activa por accidente.
- Un nombre desconocido (p. ej. `"sga"` mientras no exista el adaptador real)
  no degrada a otra fuente: responde 503 igual que la ausencia de fuente.
"""

from django.conf import settings
from django.utils.module_loading import import_string

from apps.academico.ports.fuente_academica import (
    FuenteAcademica,
    FuenteAcademicaNoConfiguradaError,
)

_FUENTES: dict[str, str] = {
    "mock_sga": "apps.academico.adapters.mock_sga.MockSGAAdapter",
    # "sga": "apps.academico.adapters.sga.SGAAdapter",  # integración futura
}


def get_fuente_academica() -> FuenteAcademica:
    nombre = getattr(settings, "ACADEMIC_PROFILE_PROVIDER", "") or ""
    ruta = _FUENTES.get(nombre)
    if ruta is None:
        raise FuenteAcademicaNoConfiguradaError(
            "No hay una fuente académica institucional configurada."
        )
    clase = import_string(ruta)
    if clase.es_simulada and not getattr(
        settings, "ACADEMIC_PROFILE_MOCK_ALLOWED", False
    ):
        raise FuenteAcademicaNoConfiguradaError(
            "La fuente académica simulada no está permitida en este entorno."
        )
    return clase()
