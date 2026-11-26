---
title: "Pruebas en Docker"
---

# Pruebas dentro de contenedores — SGT-SIAAF

**Fuente:** `README.md`, inferencia razonable a partir de `docker-compose.yml` (no se ejecutó `docker compose exec` en esta auditoría — ver nota de alcance abajo).

## 1. Comando documentado

`README.md` no documenta explícitamente un comando `pytest` dentro de Docker (solo lo hace para el entorno local sin contenedores, §"Desarrollo Local"). Por la estructura del `docker-compose.yml` (el contenedor `backend` monta el código y tiene `pytest`/`pytest-django`/`pytest-cov` instalados vía `requirements-dev.txt` en el target `development`), el comando esperable sería:

```bash
docker compose exec backend pytest
docker compose exec backend pytest src/apps src/core --cov=src
```

## 2. Diferencia relevante frente a la ejecución de esta auditoría (Fase 7)

La Fase 7 de este trabajo **no** ejecutó las pruebas dentro de Docker: se instalaron las dependencias directamente en el entorno de la sesión de auditoría (Python 3.14, sin PostgreSQL, usando `config.settings.test` con SQLite en memoria). Ejecutar `pytest` dentro del contenedor `backend` usaría **Python 3.12** (la versión real del `Dockerfile`) y, si se apuntara a `config.settings.local` en vez de `config.settings.test`, requeriría PostgreSQL real. Esto es relevante porque explica, en parte, por qué los resultados de la Fase 7 (entorno Python 3.14, dependencias resueltas por rango) no coinciden exactamente con ninguna cifra de informes anteriores: ninguno de los dos entornos (el de esta auditoría ni necesariamente el de los informes previos) es idéntico al de Docker con Python 3.12 fijo.

## 3. Nota de alcance

No se verificó en esta auditoría si `pytest` ejecutado dentro del contenedor `backend` (Python 3.12 real, target `development`) produce resultados distintos a los de la Fase 7. Sería la validación más fiel al entorno de producción real del proyecto, pero requiere levantar el stack de Docker — se solicitaría autorización explícita antes de hacerlo, por ser una acción con mayor huella que ejecutar pruebas localmente (consistente con el criterio ya aplicado en Fase 7).
