"""Healthcheck del contenedor de producción.

Consulta `/health/` directamente en gunicorn con un `Host` admitido por
`ALLOWED_HOSTS`, sin añadir `localhost` a esa lista.
"""

import os
import sys
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/health/"


def host_permitido(allowed_hosts: str) -> str:
    """Devuelve un `Host` válido a partir del primer valor de `ALLOWED_HOSTS`."""
    primero = allowed_hosts.split(",")[0].strip()
    if not primero or primero == "*":
        return "localhost"
    return primero.lstrip(".")


def main() -> int:
    host = host_permitido(os.environ.get("ALLOWED_HOSTS", ""))
    peticion = urllib.request.Request(URL, headers={"Host": host})
    try:
        with urllib.request.urlopen(peticion, timeout=5) as respuesta:  # nosec B310
            return 0 if respuesta.status == 200 else 1
    except (urllib.error.URLError, OSError):
        return 1


if __name__ == "__main__":
    sys.exit(main())
