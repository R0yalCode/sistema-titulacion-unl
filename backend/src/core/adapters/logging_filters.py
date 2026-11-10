"""Filtros de logging (SEC-T011).

`SensitiveDataFilter` evita que datos sensibles lleguen a los logs.
`RequestIdFilter` garantiza que `request_id` y `user_id` siempre existan
en el record (placeholders "-" mientras SEC-T005 y un futuro mecanismo de
contexto de usuario no los pueblen); sin esto, el formateador JSON con
`%(request_id)s %(user_id)s` fallaría en records que no los traigan.
"""

import logging
import re

_CAMPOS_SENSIBLES = ("password", "token", "authorization", "credit_card", "cedula")
_PATRON_SENSIBLE = re.compile(
    r"(" + "|".join(_CAMPOS_SENSIBLES) + r")=\S+", re.IGNORECASE
)


class SensitiveDataFilter(logging.Filter):
    """Elimina valores de campos sensibles de `record.msg` y de atributos
    extra del record (`record.__dict__`)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _PATRON_SENSIBLE.sub(
                lambda m: f"{m.group(1)}=***", record.msg
            )
        for campo in _CAMPOS_SENSIBLES:
            if campo in record.__dict__:
                record.__dict__[campo] = "***"
        return True


class RequestIdFilter(logging.Filter):
    """Garantiza `request_id`/`user_id` en el record. Placeholder "-" hasta
    que exista un mecanismo real de contexto (SEC-T005 aporta IP, no
    request_id; se deja preparado para cuando se añada)."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "user_id"):
            record.user_id = "-"
        return True
