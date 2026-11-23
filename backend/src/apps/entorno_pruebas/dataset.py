"""Definición determinista del dataset sintético (lote `sgt-siaaf-v1`).

Identidades claramente FICTICIAS, derivadas del rol y de un índice:
`Estudiante Ficticio 01`, `ds.estudiante.01@sgt-siaaf.example`. El dominio
`.example` está reservado por la RFC 2606 y no admite buzones reales. Las cédulas
empiezan por `99`, código que no corresponde a ninguna provincia.

El catálogo académico es SIMULADO: los códigos son `MOCK-…` y los registros
llevan `es_simulada=True`. No es el catálogo oficial de la UNL.
"""

from dataclasses import dataclass

LOTE = "sgt-siaaf-v1"
CUENTAS_POR_ROL = 10
DOMINIO_CORREO = "sgt-siaaf.example"
#: Prefijo de los correos locales creados con `--correo-institucional`.
PREFIJO_CORREO_LOCAL = "sgtdemo"

#: Roles verificados en el código (RBAC_MATRIX y tabla Role). No se crean
#: roles nuevos.
ROLES = (
    "ESTUDIANTE",
    "SECRETARIA_CARRERA",
    "DIRECTOR_CARRERA",
    "SECRETARIO_ABOGADO",
    "ANALISTA_APOYO",
    "DECANO",
    "RESPONSABLE_DEPENDENCIA",
    "ADMINISTRADOR",
)

#: Etiqueta visible de cada rol. Los nombres se derivan del rol y del índice,
#: de modo que no pueden confundirse con los de una persona.
ETIQUETA_ROL = {
    "ESTUDIANTE": "Estudiante",
    "SECRETARIA_CARRERA": "Secretaría",
    "DIRECTOR_CARRERA": "Dirección",
    "SECRETARIO_ABOGADO": "Abogacía",
    "ANALISTA_APOYO": "Analista",
    "DECANO": "Decanato",
    "RESPONSABLE_DEPENDENCIA": "Dependencia",
    "ADMINISTRADOR": "Administración",
}


@dataclass(frozen=True)
class FacultadDataset:
    codigo: str
    nombre: str


@dataclass(frozen=True)
class CarreraDataset:
    codigo: str
    nombre: str
    facultad: str


FACULTADES = (
    # Ya la crea `seed_mock_sga`; se reutiliza con el mismo código.
    FacultadDataset(
        "MOCK-FEIRNNR",
        "Facultad de la Energía, las Industrias y los Recursos Naturales "
        "No Renovables",
    ),
    FacultadDataset("MOCK-FCEA", "Facultad de Ciencias Económicas y Administrativas"),
)
CARRERAS = (
    CarreraDataset("MOCK-COMPUTACION", "Computación", "MOCK-FEIRNNR"),
    CarreraDataset("MOCK-TELECOMUNICACIONES", "Telecomunicaciones", "MOCK-FEIRNNR"),
    CarreraDataset("MOCK-ELECTRICIDAD", "Electricidad", "MOCK-FEIRNNR"),
    CarreraDataset("MOCK-ADMINISTRACION", "Administración de Empresas", "MOCK-FCEA"),
    CarreraDataset("MOCK-CONTABILIDAD", "Contabilidad y Auditoría", "MOCK-FCEA"),
)
CODIGOS_CARRERA = tuple(c.codigo for c in CARRERAS)
FACULTAD_DE = {c.codigo: c.facultad for c in CARRERAS}

# Escenarios de los 10 estudiantes: (carrera, escenario). Los escenarios usan
# solo estados y servicios que existen en el código.
SIN_EXPEDIENTE = "sin_expediente"
BORRADOR = "borrador"
BORRADOR_CON_DOCUMENTOS = "borrador_con_documentos"
ENVIADA = "enviada"
EN_VERIFICACION = "en_verificacion"
OBSERVADA = "observada"
SUBSANADA = "subsanada"
INFORME_EMITIDO = "informe_emitido"
DECLARADA_APTA = "declarada_apta"

ESTUDIANTES = (
    ("MOCK-COMPUTACION", SIN_EXPEDIENTE),
    ("MOCK-CONTABILIDAD", SIN_EXPEDIENTE),
    ("MOCK-TELECOMUNICACIONES", BORRADOR),
    ("MOCK-ADMINISTRACION", BORRADOR_CON_DOCUMENTOS),
    ("MOCK-ELECTRICIDAD", ENVIADA),
    ("MOCK-COMPUTACION", EN_VERIFICACION),
    ("MOCK-TELECOMUNICACIONES", OBSERVADA),
    ("MOCK-ADMINISTRACION", SUBSANADA),
    ("MOCK-COMPUTACION", INFORME_EMITIDO),
    ("MOCK-ELECTRICIDAD", DECLARADA_APTA),
)

#: Ámbito que cada rol usa realmente (core/adapters/scope_filter.py y
#: servicios de verificación y resoluciones).
AMBITO_CARRERA = ("SECRETARIA_CARRERA", "DIRECTOR_CARRERA")
AMBITO_FACULTAD = (
    "SECRETARIO_ABOGADO",
    "ANALISTA_APOYO",
    "DECANO",
    # Sin ámbito RBAC (SCOPE_DENEGADO); la facultad solo orienta a quién se
    # notifica una solicitud de emisión. No concede ningún permiso.
    "RESPONSABLE_DEPENDENCIA",
)


@dataclass(frozen=True)
class Persona:
    rol: str
    indice: int  # 1..10
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    cedula: str
    carrera: str | None
    facultad: str | None
    escenario: str | None

    @property
    def clave(self) -> str:
        return f"usuario:{self.rol}:{self.indice:02d}"

    @property
    def apellidos(self) -> str:
        return f"{self.apellido_paterno} {self.apellido_materno}"

    def candidatos_usuario(self) -> list[str]:
        """Nombres de usuario posibles, derivados del rol y del índice."""
        base = f"ds.{self.rol.lower().replace('_', '-')}.{self.indice:02d}"
        return [base, f"{base}.b", f"{base}.c"]


def _cedula(numero_global: int) -> str:
    return f"99{numero_global:08d}"


def personas() -> list[Persona]:
    resultado = []
    for r, rol in enumerate(ROLES):
        for i in range(CUENTAS_POR_ROL):
            n = r * CUENTAS_POR_ROL + i  # 0..79
            carrera = facultad = escenario = None
            if rol == "ESTUDIANTE":
                carrera, escenario = ESTUDIANTES[i]
                facultad = FACULTAD_DE[carrera]
            elif rol in AMBITO_CARRERA:
                carrera = CODIGOS_CARRERA[i % len(CODIGOS_CARRERA)]
                facultad = FACULTAD_DE[carrera]
            elif rol in AMBITO_FACULTAD:
                facultad = FACULTADES[i % len(FACULTADES)].codigo
            resultado.append(
                Persona(
                    rol=rol,
                    indice=i + 1,
                    nombres=ETIQUETA_ROL[rol],
                    apellido_paterno="Ficticio",
                    apellido_materno=f"{i + 1:02d}",
                    cedula=_cedula(n + 1),
                    carrera=carrera,
                    facultad=facultad,
                    escenario=escenario,
                )
            )
    return resultado
