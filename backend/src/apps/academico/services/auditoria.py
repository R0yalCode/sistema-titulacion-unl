"""Registro de cambios del catálogo académico y de las asociaciones.

Solo se guardan códigos, identificadores técnicos y nombres de campos; nunca
cédulas, nombres ni correos (los perfiles simulados contienen datos de
identidad aunque sean ficticios).
"""

from apps.academico.adapters.models import (
    Carrera,
    EventoCatalogoAcademico,
    Facultad,
    PerfilSGASimulado,
)

#: Campos cuyo valor puede registrarse en la bitácora (sin datos personales).
CAMPOS_AUDITABLES = {
    Facultad: ("codigo", "nombre", "activa", "es_simulada"),
    Carrera: ("codigo", "nombre", "facultad_id", "activa", "es_simulada"),
    PerfilSGASimulado: ("codigo_carrera", "codigo_facultad", "activo"),
}

OBJETOS = {
    Facultad: "facultad",
    Carrera: "carrera",
    PerfilSGASimulado: "perfil_sga_simulado",
}


def instantanea(instancia) -> dict:
    """Valores auditables actuales de la instancia (como texto)."""
    campos = CAMPOS_AUDITABLES.get(type(instancia), ())
    return {campo: _texto(getattr(instancia, campo, None)) for campo in campos}


def _texto(valor):
    if valor is None or isinstance(valor, bool):
        return valor
    return str(valor)


def registrar_cambio(
    instancia,
    *,
    tipo: str,
    actor=None,
    origen: str,
    antes: dict | None = None,
    campos_modificados: list[str] | None = None,
) -> EventoCatalogoAcademico:
    despues = (
        instantanea(instancia) if tipo != EventoCatalogoAcademico.Tipo.ELIMINADO else {}
    )
    detalles: dict = {"antes": antes or {}, "despues": despues}
    if campos_modificados is not None:
        # Nombres de los campos tocados (incluidos los de identidad, sin valor).
        detalles["campos_modificados"] = sorted(campos_modificados)
    return EventoCatalogoAcademico.objects.create(
        tipo=tipo,
        objeto=OBJETOS[type(instancia)],
        objeto_id=str(instancia.pk),
        actor=actor,
        origen=origen,
        detalles=detalles,
    )


def registrar_asignacion_ambito(
    usuario, *, actor=None, origen: str, campos: dict
) -> EventoCatalogoAcademico:
    """Asignación de `carrera_id`/`facultad_id` a una cuenta de personal."""
    return EventoCatalogoAcademico.objects.create(
        tipo=EventoCatalogoAcademico.Tipo.AMBITO_ASIGNADO,
        objeto="usuario",
        objeto_id=str(usuario.pk),
        actor=actor,
        origen=origen,
        detalles={"campos": {k: _texto(v) for k, v in campos.items()}},
    )
