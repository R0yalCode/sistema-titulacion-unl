"""Correo institucional como identificador de acceso.

Dominio puro: sin ORM ni Django. El dominio admitido se recibe como
parámetro para que la configuración (`INSTITUTIONAL_EMAIL_DOMAIN`) viva en
settings.
"""

import re

MENSAJE_CORREO_INVALIDO = "Ingrese un correo institucional válido (@unl.edu.ec)."

# Parte local conservadora: letras, dígitos y . _ % + - (sin espacios ni @).
_PARTE_LOCAL = re.compile(r"^[a-z0-9._%+-]+$")


def normalizar_correo(valor: str) -> str:
    """Quita espacios exteriores y pasa a minúsculas (dominio y parte local:
    las cuentas institucionales no distinguen mayúsculas)."""
    return (valor or "").strip().lower()


def es_correo_institucional(valor: str, dominio: str) -> bool:
    """True si `valor` ya normalizado es `<parte_local>@<dominio>` exacto.

    Rechaza otros dominios, subdominios parecidos (`unl.edu`, `unl.edu.ec.x`,
    `mail.unl.edu.ec`) y direcciones sin dominio.
    """
    if valor.count("@") != 1:
        return False
    local, _, dominio_valor = valor.partition("@")
    return (
        bool(local)
        and len(valor) <= 254
        and bool(_PARTE_LOCAL.match(local))
        and not local.startswith(".")
        and not local.endswith(".")
        and ".." not in local
        and dominio_valor == dominio.lower()
    )
