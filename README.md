# SGT-SIAAF — Sistema de Gestión del Trámite de Titulación

**Universidad Nacional de Loja — Facultad de la Energía, las Industrias y los Recursos Naturales No Renovables (FEIRNNR)**  
**Carrera de Computación — Asignatura: Desarrollo Basado en Plataformas (5.º Ciclo)**

---

## 📋 Descripción General

**SGT-SIAAF** es el Sistema de Gestión del Trámite de Titulación integrado al SIAAF, diseñado para automatizar y gestionar el proceso de titulación de la FEIRNNR-UNL conforme al Art. 235 del RRA-UNL (Aptitud Legal).

**Arquitectura:** Monolito modular con arquitectura hexagonal (Django 5.2 + DRF + PostgreSQL 16)  
**MVP (Fase 1):** Aptitud Legal (Art. 235 RRA-UNL) — Estados: `BORRADOR` → `ENVIADA` → `EN_VERIFICACION` → `OBSERVADA` → `EN_VERIFICACION` → `INFORME_EMITIDO` → `DECLARADA_APTA`

---

## 🐳 Despliegue con Docker Compose (Recomendado)

### Prerrequisitos
- **Docker** ≥ 24.0
- **Docker Compose** ≥ 2.20 (plugin `docker compose` o `docker-compose` standalone)
- **Git** (para clonar el repositorio)
- Puertos libres: **8000** (nginx proxy), **5432** (PostgreSQL interno)

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd sistema-titulacion-unl
```

### 2. Configurar variables de entorno
Crear archivo `.env` en la raíz del proyecto:

```bash
# .env (raíz del proyecto)
POSTGRES_DB=sgt_siaaf
POSTGRES_USER=sgt_user
POSTGRES_PASSWORD=una_clave_segura_para_produccion
SECRET_KEY=django-insecure-clave-secreta-muy-larga-y-aleatoria
DEBUG=0
```

> **Nota:** En desarrollo local puede usar valores por defecto; en producción **cambie obligatoriamente** `SECRET_KEY` y `POSTGRES_PASSWORD`.

### 3. Levantar el entorno
```bash
# Construir imágenes y levantar servicios (primera vez)
docker compose up --build -d

# Verificar que los contenedores están saludables
docker compose ps
```

Servicios esperados:
| Servicio | Puerto | Healthcheck |
|----------|--------|-------------|
| `db` (PostgreSQL 16) | 5432 (interno) | `pg_isready` |
| `backend` (Django) | 8000 (interno) | - |
| `nginx` | **8000** (expuesto) | - |

### 4. Ejecutar migraciones y cargar datos iniciales
```bash
# Ejecutar migraciones de Django
docker compose exec backend python manage.py migrate

# Cargar 8 cuentas demo (idempotente)
docker compose exec backend python manage.py seed_initial_data
```

### 5. Verificar despliegue
- **Swagger UI:** http://localhost:8000/api/v1/docs/
- **ReDoc:** http://localhost:8000/api/v1/redoc/
- **OpenAPI Schema (YAML):** http://localhost:8000/api/v1/schema/

---

## 🔧 Desarrollo Local (sin Docker)

### Prerrequisitos
- **Python** 3.12
- **PostgreSQL** 16
- **pip** / **venv**

### Configuración
```bash
cd backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar .env (backend/.env)
cp .env.example .env
# Editar .env con credenciales de PostgreSQL local
```

### Comandos útiles
```bash
# Migraciones
python manage.py migrate

# Datos de prueba
python manage.py seed_initial_data

# Servidor de desarrollo
python manage.py runserver 0.0.0.0:8000

# Tests
pytest                    # Todos los tests
pytest -v                 # Verboso
pytest --cov=src          # Con cobertura
pytest src/apps/          # Solo tests de apps
```

---

## 📚 Documentación API (OpenAPI v3)

| Interfaz | URL |
|----------|-----|
| **Swagger UI** | http://localhost:8000/api/v1/docs/ |
| **ReDoc** | http://localhost:8000/api/v1/redoc/ |
| **Schema YAML** | http://localhost:8000/api/v1/schema/ |

Generar schema manualmente:
```bash
docker compose exec backend python manage.py spectacular --file openapi.yaml
```

---

## 🔐 Cuentas Demo (seed_initial_data)

El comando `seed_initial_data` crea 8 cuentas idempotentes:

| Usuario | Cédula | Rol | Contraseña |
|---------|--------|-----|------------|
| `estudiante_1` | 1100000002 | ESTUDIANTE | `SgtDemo2026!` |
| `secretaria_carrera` | 1100000003 | SECRETARIA_CARRERA | `SgtDemo2026!` |
| `secretario_abogado` | 1100000004 | SECRETARIO_ABOGADO | `SgtDemo2026!` |
| `analista_apoyo` | 1100000005 | ANALISTA_APOYO | `SgtDemo2026!` |
| `decano_feirnnr` | 1100000006 | DECANO | `SgtDemo2026!` |
| `director_computacion` | 1100000007 | DIRECTOR_CARRERA | `SgtDemo2026!` |
| `responsable_practicas` | 1100000008 | RESPONSABLE_DEPENDENCIA | `SgtDemo2026!` |
| `admin_sys` | 1100000009 | ADMINISTRADOR | `SgtDemo2026!` |

> ⚠️ **Solo para demostración académica.** En producción, cambie contraseñas y use gestión de secretos segura.

---

## 🔗 Endpoints Principales (v1)

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/token/` | Obtener JWT (access + refresh) |

### Expedientes
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/expedientes/` | Crear expediente (BORRADOR) |
| GET | `/api/v1/expedientes/bandeja/` | Bandeja operativa filtrada por rol |
| GET | `/api/v1/expedientes/{id}/` | Detalle de expediente |
| POST | `/api/v1/expedientes/{id}/enviar/` | Enviar expediente (ENVIADA) |
| POST | `/api/v1/expedientes/{id}/observar/` | Observar expediente |

### Peticiones Documentales
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/peticiones/{id}/solicitar-emision/` | Solicitar certificado interno |
| POST | `/api/v1/peticiones/{id}/documento/` | Cargar PDF (validación magic bytes + SHA-256) |
| GET | `/api/v1/peticiones/{id}/documento/` | Descargar versión vigente |
| GET | `/api/v1/peticiones/{id}/documento/{v}/` | Descargar versión específica |

### Verificación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/expedientes/{id}/checklist/` | Listar checklist |
| PUT | `/api/v1/checklist/{id}/` | Evaluar requisito (VERIFICADO/OBSERVADO) |
| POST | `/api/v1/checklist/{id}/subsanar/` | Subsanar requisito observado |

### Resoluciones
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/informes/` | Emitir informe legal (Secretario Abogado) |
| POST | `/api/v1/declaratorias/` | Registrar declaratoria (Decano) |

### Notificaciones
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/notificaciones/` | Listar notificaciones (filtro `?leida=true/false`) |
| PATCH | `/api/v1/notificaciones/{id}/marcar-leida/` | Marcar como leída |

---

## 🧪 Tests y Cobertura

```bash
# Todos los tests (464+)
pytest

# Con reporte de cobertura HTML
pytest --cov=src --cov-report=html
# Abrir htmlcov/index.html
```

**Cobertura objetivo:** ≥ 70% (actual: **95%**)

### Suites principales
| Módulo | Tests | Cobertura |
|--------|-------|-----------|
| `authentication` | 48 | 97% |
| `expedientes` | 75 | 95% |
| `notificaciones` | 71 | 95% |
| `peticiones` | 95 | 95% |
| `resoluciones` | 122 | 95% |
| `verificacion` | 72 | 92% |
| `e2e` | 4 | - |
| **TOTAL** | **468** | **95%** |

---

## 🛡️ Seguridad

- **Autenticación:** JWT stateless (access 60min, refresh 24h)
- **Autorización:** RBAC server-side (8 roles × recursos × acciones)
- **Aislamiento:** `ScopeFilterMixin` previene IDOR por carrera/facultad
- **Validación PDF:** Magic bytes `%PDF-` + SHA-256 + tamaño ≤ 10MB
- **Almacenamiento:** Archivos en volumen privado (no web-accessible)
- **Auditoría:** `EventoAuditoria` inmutable en JSONB (Django signals)
- **Mock SGA:** `SGAMockAdapter` sin conexiones externas (DEC-05)

---

## 📦 Estructura del Proyecto

```
sistema-titulacion-unl/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── manage.py
│   ├── .env.example
│   ├── .env                    # No commitear
│   ├── src/
│   │   ├── config/             # Settings, URLs, WSGI
│   │   ├── core/               # Puertos, adaptadores core (Mock SGA, PDF, Storage)
│   │   └── apps/
│   │       ├── authentication/ # JWT, RBAC, Usuarios
│   │       ├── expedientes/    # Expedientes, plazos, bandeja
│   │       ├── peticiones/     # Peticiones, documentos, PDF
│   │       ├── verificacion/   # Checklist, observaciones, subsanación
│   │       ├── resoluciones/   # Informe, declaratoria, PDF generator
│   │       └── notificaciones/ # In-app notifications, auditoría
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.override.yml  # Para desarrollo local
├── .gitleaksignore
├── .bandit
├── .dockerignore
├── .gitignore
├── LICENSE
├── docs/
│   └── security_report.md      # T044 - Auditoría de seguridad
├── tests/
│   └── e2e/
│       └── test_full_workflow.py
└── README.md
```

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| `POSTGRES_PASSWORD is required` | Definir `POSTGRES_PASSWORD` en `.env` |
| `SECRET_KEY is required` | Definir `SECRET_KEY` en `.env` |
| DB no inicia (healthcheck falla) | `docker compose logs db` → verificar puerto 5432 libre |
| Migraciones fallan | `docker compose exec backend python manage.py migrate --fake-initial` |
| Puerto 8000 ocupado | Cambiar `ports:` en `docker-compose.yml` (ej. `"8080:80"`) |
| Permisos en volúmenes | `docker compose exec backend chown -R django:django /app/backend/media` |

---

## 📄 Licencia

**Proprietary** — Universidad Nacional de Loja. Uso académico autorizado.

---

## 👥 Equipo

**Arquitectura e Ingeniería SGT-SIAAF** — Carrera de Computación, UNL  
**Versión:** 1.0.0 (MVP — Aptitud Legal, Art. 235 RRA-UNL)  
**Fecha:** Octubre 2026