# syntax=docker/dockerfile:1
#
# Multi-stage con targets `development` y `production` (SEC-T001).
# Se mantiene un único Dockerfile en la raíz, junto al resto de archivos
# de contenedores ya existentes, para no duplicar las etapas comunes
# (instalación de dependencias) entre dos archivos separados.
#
# Desarrollo: docker build --target development .  (o docker-compose.yml)
# Producción: docker build --target production .   (o docker-compose.prod.yml)

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM base AS development

RUN groupadd --system django && useradd --system --gid django django

COPY backend/requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY backend/manage.py ./
COPY backend/pyproject.toml ./
COPY backend/src ./src

RUN mkdir -p media staticfiles && chown -R django:django /app/backend

USER django

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


FROM base AS production

RUN groupadd --system appuser --gid 1000 && \
    useradd --system --uid 1000 --gid appuser appuser

COPY backend/manage.py ./
COPY backend/pyproject.toml ./
COPY backend/src ./src
COPY backend/entrypoint.sh ./entrypoint.sh

RUN chmod +x entrypoint.sh && \
    mkdir -p media/private staticfiles /var/log/sgt-siaaf && \
    chown -R appuser:appuser /app/backend /var/log/sgt-siaaf

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health/').status == 200 else 1)"

ENTRYPOINT ["./entrypoint.sh"]
