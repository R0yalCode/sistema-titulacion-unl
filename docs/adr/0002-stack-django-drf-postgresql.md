# ADR-002: Stack Tecnologico Django 5.x + DRF + PostgreSQL 16

## Estado
Aceptado

## Contexto
El SGT-SIAAF requiere un stack tecnologico que garantice:
- Desarrollo rapido y mantenible (academico)
- Ecosistema maduro y documentado
- Soporte para arquitectura hexagonal
- Despliegue reproducible con Docker
- Cumplimiento normativo (RRA-UNL, Art. 235)

## Decision
Se adopta el siguiente stack tecnologico para el MVP (Fase 1):

| Capa | Tecnologia | Version | Justificacion |
|------|------------|---------|---------------|
| **Lenguaje** | Python | 3.12 | Soporte LTS, tipado estatico, ecosistema |
| **Framework Web** | Django | 5.2.x | ORM robusto, Admin, Migrations, Security |
| **API Framework** | Django REST Framework | 3.16.x | Serializers, ViewSets, Permissions, Browsable API |
| **Base de Datos** | PostgreSQL | 16 | JSONB, UUID, Indices parciales, Fiabilidad |
| **Autenticacion** | djangorestframework-simplejwt | 5.5.x | JWT Stateless, Rotacion refresh, RFC 7519 |
| **Configuracion** | django-environ | 0.12.x | 12-factor app, .env, Tipado |
| **Documentacion API** | drf-spectacular | 0.27.x | OpenAPI 3.0, Swagger UI, ReDoc, Schema-first |
| **Testing** | pytest + pytest-django + pytest-cov | 8.4.x / 4.11.x / 7.1.x | Fixtures, Parametrize, Coverage >70% |
| **Calidad Codigo** | Black + Flake8 + Isort + MyPy | 25.x / 7.x / 6.x / 1.x | Formato, Lint, Types |
| **Generacion PDF** | ReportLab | 5.0.x | PDF programatico, Plantillas institucionales |
| **Contenedores** | Docker + Docker Compose | 24.x / 2.20.x | Reproducibilidad, Aislamiento |
| **Proxy Reverso** | Nginx | 1.24-alpine | Terminacion SSL, Static files, Rate limiting |

## Versiones fijadas (requirements.txt)
```
Django>=5.2,<5.3
djangorestframework>=3.16,<4.0
djangorestframework-simplejwt>=5.5,<6.0
psycopg[binary]>=3.2,<4.0
django-environ>=0.12,<1.0
drf-spectacular>=0.27,<1.0
```

## Versiones desarrollo (requirements-dev.txt)
```
black>=25.1,<26.0
flake8>=7.1,<8.0
isort>=5.13,<7.0
mypy>=1.14,<2.0
pytest>=8.4,<9.0
pytest-django>=4.11,<5.0
pytest-cov>=6.0,<8.0
```

## Alternativas consideradas
| Opcion | Rechazada porque |
|--------|------------------|
| FastAPI + Pydantic | Menos maduro para admin/ORM complejo, menos talento disponible |
| Flask + SQLAlchemy | Falta admin, migrations, structure opinada |
| Node.js/Express | Equipo con expertise Python, requisitos academicos |
| MySQL/MariaDB | Sin JSONB nativo robusto, sin UUID nativo |
| MongoDB | No relacional, ACID limitado, no apto para tramites legales |
| JWT manual (PyJWT) | Reimplementar rotacion, blacklist, refresh tokens |

## Consecuencias
- Productividad: Django Admin, ORM, Migrations, Auth out-of-the-box
- Ecosistema: Paquetes maduros para JWT, PDF, OpenAPI, Testing
- Despliegue: Docker Compose reproducible, PostgreSQL oficial
- Seguridad: JWT stateless, RBAC server-side, Validacion PDF estricta
- Overhead: Django anade abstracciones (mitigado con arquitectura hexagonal)
- Migraciones: Cuidado con makemigrations/migrate en equipo

## Referencias
- Django 5.2 Release Notes
- DRF 3.16 Release Notes
- PostgreSQL 16 Release Notes
- drf-spectacular Documentation
- constitucion.md Principios C-002, C-010, C-012, C-013
- plan.md 13, 15, 22, 23