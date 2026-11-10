"""Pruebas de SEC-T011: logging estructurado (JSON, sin secretos, con
rotación por tamaño)."""

import json
import logging
import logging.handlers
import tempfile
from pathlib import Path

import pytest
from django.conf import settings

from core.adapters.logging_filters import RequestIdFilter, SensitiveDataFilter


def _formatear(record: logging.LogRecord) -> dict:
    from pythonjsonlogger.jsonlogger import JsonFormatter

    fmt = JsonFormatter(settings.LOGGING["formatters"]["json"]["fmt"])
    SensitiveDataFilter().filter(record)
    RequestIdFilter().filter(record)
    return json.loads(fmt.format(record))


def _record(msg: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="apps.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=None,
        exc_info=None,
    )


def test_logging_structured_json_format():
    salida = _formatear(_record("mensaje de prueba SEC-T011"))
    assert salida["message"] == "mensaje de prueba SEC-T011"
    assert salida["levelname"] == "INFO"
    assert salida["name"] == "apps.test"
    assert salida["request_id"] == "-"
    assert salida["user_id"] == "-"


def test_logging_no_secrets_in_output():
    salida = _formatear(_record('login fallido password=secreto123 token=abc.def.ghi'))
    cadena = json.dumps(salida)
    assert "secreto123" not in cadena
    assert "abc.def.ghi" not in cadena
    assert "password=***" in salida["message"]
    assert "token=***" in salida["message"]


def test_logging_rotation_max_bytes():
    with tempfile.TemporaryDirectory() as tmp:
        ruta = Path(tmp) / "apps.log"
        handler = logging.handlers.RotatingFileHandler(
            ruta, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        logger = logging.getLogger("sec_t011_rotation_test")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        linea = "x" * 1024  # 1KB por línea
        for _ in range(11 * 1024):  # ~11MB > maxBytes(10MB) → debe rotar
            logger.info(linea)
        handler.close()
        logger.removeHandler(handler)

        backups = list(Path(tmp).glob("apps.log.*"))
        assert len(backups) >= 1, "Se esperaba al menos un backup tras exceder maxBytes"
        assert ruta.exists()


def test_logging_no_print_in_production_code():
    raiz = Path(__file__).resolve().parents[3]  # backend/src
    hallazgos = []
    for archivo in raiz.rglob("*.py"):
        ruta_str = str(archivo)
        if "/tests/" in ruta_str or ruta_str.endswith("manage.py"):
            continue
        if "print(" in archivo.read_text(encoding="utf-8"):
            hallazgos.append(ruta_str)
    assert hallazgos == []


@pytest.mark.django_db
def test_logging_dict_loaded_in_settings():
    assert "console" in settings.LOGGING["handlers"]
    assert settings.LOGGING["handlers"]["console"]["formatter"] == "json"
    assert "sensitive_data" in settings.LOGGING["filters"]
    assert "request_id" in settings.LOGGING["filters"]
