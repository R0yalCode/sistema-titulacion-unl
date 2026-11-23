"""Configuración de gunicorn del target `production`.

El paquete `config` vive en `backend/src`. `manage.py` añade esa ruta por su
cuenta, pero gunicorn no pasa por él: se declara aquí, relativa a este archivo,
para no depender del directorio de trabajo ni de variables de entorno.
"""

from pathlib import Path

pythonpath = str(Path(__file__).resolve().parent / "src")
bind = "0.0.0.0:8000"
workers = 4
timeout = 60
accesslog = "-"
errorlog = "-"
