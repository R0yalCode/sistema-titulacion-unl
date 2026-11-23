"""Adaptador MockSGA: simulación de la fuente académica institucional.

PROTOTIPO. No existe conexión con el SGA de la UNL: los datos salen de la
tabla `PerfilSGASimulado`, cargada por `seed_mock_sga` o por el admin. Se
marca `es_simulada = True` y la API lo comunica al cliente en `fuente`.

Solo se instancia si la configuración lo permite expresamente
(`ACADEMIC_PROFILE_MOCK_ALLOWED`; ver `services/fuentes.py`).
"""

from apps.academico.adapters.models import PerfilSGASimulado
from apps.academico.domain.perfil import RegistroAcademicoFuente


class MockSGAAdapter:
    codigo = "MOCK_SGA"
    nombre = "MockSGA (simulación del SGA, prototipo sin conexión institucional)"
    es_simulada = True

    def consultar_por_identificacion(
        self, identificacion: str
    ) -> RegistroAcademicoFuente | None:
        registro = PerfilSGASimulado.objects.filter(
            identificacion=identificacion, activo=True
        ).first()
        if registro is None:
            return None
        return RegistroAcademicoFuente(
            identificacion=registro.identificacion,
            nombres=registro.nombres,
            apellidos=registro.apellidos,
            correo_institucional=registro.correo_institucional,
            codigo_carrera=registro.codigo_carrera,
            codigo_facultad=registro.codigo_facultad,
        )
