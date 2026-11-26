---
title: "Stack tecnológico"
---

# Stack tecnológico — Backend SGT-SIAAF

**Fuente:** `backend/requirements.txt`, `backend/requirements-dev.txt` (leídos íntegramente, no resumidos de memoria). Los rangos de versión son los **declarados en el manifiesto de dependencias**, que es lo que realmente se instala en `docker-compose up --build`; este entorno de documentación no tiene un entorno Python con las dependencias del backend instaladas, por lo que no se reporta una versión "exacta instalada" vía `pip show`, sino el rango fijado en el manifiesto (fuente autoritativa y reproducible).

## Dependencias de producción (`requirements.txt`)

| Paquete | Rango fijado | Responsabilidad |
|---|---|---|
| `Django` | `>=5.2.19,<5.3` | Framework web, ORM, migraciones, Admin |
| `djangorestframework` | `>=3.17.2,<4.0` | Serializers, ViewSets, permisos, API navegable |
| `djangorestframework-simplejwt` | `>=5.5.1,<6.0` | Autenticación JWT stateless |
| `psycopg[binary]` | `>=3.2,<4.0` | Driver PostgreSQL (psycopg3) |
| `django-environ` | `>=0.12,<1.0` | Configuración por variables de entorno (`.env`) |
| `drf-spectacular` | `>=0.27,<1.0` | Generación de esquema OpenAPI 3 / Swagger / ReDoc |
| `reportlab` | `>=4.3,<5.0` | Generación programática de PDF (informe #590, memorando #162) |
| `django-cors-headers` | `>=4.4,<5.0` | Cabeceras CORS para el cliente SPA |
| `gunicorn` | `>=23.0,<24.0` | Servidor WSGI de producción (siempre en uso — ver `DOCUMENTACION/03_ARQUITECTURA/C2_CONTENEDORES.md`) |
| `python-json-logger` | `>=2.0,<3.0` | Logging estructurado en JSON |

## Dependencias de desarrollo (`requirements-dev.txt`)

| Paquete | Rango fijado | Responsabilidad |
|---|---|---|
| `black` | `>=25.1,<26.0` | Formateo de código |
| `flake8` | `>=7.1,<8.0` | Linting |
| `isort` | `>=5.13,<7.0` | Orden de imports |
| `mypy` | `>=1.14,<2.0` | Verificación de tipos estática |
| `pytest` | `>=8.4,<9.0` | Motor de pruebas |
| `pytest-django` | `>=4.11,<5.0` | Integración pytest con Django |
| `pytest-cov` | `>=6.0,<8.0` | Cobertura de pruebas |

## Discrepancia detectada frente a `docs/adr/0002-stack-django-drf-postgresql.md`

El ADR-0002 (ver `DOCUMENTACION/03_ARQUITECTURA/ADR.md` §3) declara `djangorestframework 3.16.x`; el manifiesto real fija `>=3.17.2,<4.0`. También el ADR no menciona `django-cors-headers` ni `python-json-logger`, que sí están en el manifiesto real. Esto es una **desactualización menor del ADR respecto al código**, no un error de implementación: el stack efectivamente implementado es el que aparece en esta página, verificado por lectura directa de `requirements.txt`.

## Infraestructura (verificada en `docker-compose.yml`, `docker-compose.prod.yml`, `nginx/`)

| Componente | Versión | Rol |
|---|---|---|
| PostgreSQL | 16 | Base de datos relacional |
| Nginx | 1.24 (alpine, según `docs/adr/0002`) | Proxy inverso |
| Docker / Docker Compose | — (no se fija versión exacta en los archivos de compose) | Orquestación de contenedores |

## Resumen de verificación

**IMPLEMENTADO Y VERIFICADO**: todas las dependencias de esta página están confirmadas por lectura directa de los archivos de manifiesto del repositorio, no por inferencia ni por copia de documentación previa.
