---
system: SGT-SIAAF
type: architecture
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Arquitectura general

```
Navegador ──► SPA React (frontend/, Vite)
                 │  JWT Bearer, /api/v1
                 ▼
            Nginx (nginx/nginx.conf; :8000 dev, :80/:443 prod)
                 │
                 ▼
            Django + DRF (backend/, gunicorn)  ── monolito modular hexagonal
              apps: authentication · expedientes · peticiones · verificacion · resoluciones · notificaciones
              core: scope_filter · pdf_validation · local_storage · mock_sga · security_headers · health
                 │                                   │
                 ▼                                   ▼
            PostgreSQL 16                   Almacenamiento privado (media/private)
                                             SGA/SIAAF: solo vía SGAMockAdapter (sin conexión real, RN-012)
```

## Decisiones estructurales vigentes

| Decisión | Fuente |
|---|---|
| Monolito modular + arquitectura hexagonal | `docs/adr/0001-arquitectura-hexagonal-monolito-modular.md` |
| Django + DRF + PostgreSQL | `docs/adr/0002-stack-django-drf-postgresql.md` |
| Consola admin interna solo staff (ADR-0009) | Citada en `backend/src/config/urls.py` |
| SGA/SIAAF solo mediante adaptadores simulados; prohibido escribir en BD legadas | DEC-05, RN-012, Constitución C-002/C-017 |
| Firma electrónica simulada (carga de PDF firmado externamente) | DEC-04 |
| Frontend separado, sin dependencias nuevas sin autorización | `AGENTS.md`, specs 003 |

Índice completo de ADR: [[ADR_INDEX]].

## Naturaleza del sistema

Según specify 001 §2.2, SGT-SIAAF es una **simulación académica funcional** (asignatura Desarrollo Basado en Plataformas): datos ficticios, sin acceso a BD productivas y sin validez legal de los documentos generados.

## Vistas detalladas

[[BACKEND_ARCHITECTURE]] · [[FRONTEND_ARCHITECTURE]] · [[DATABASE]] · [[API_CONTRACTS]] · [[FIRMA_EC]] · [[DOCKER]]

Documentación C4 previa: `docs/02-arquitectura/c4/{contexto,contenedores,componentes,codigo}.md`, `DOCUMENTACION/03_ARQUITECTURA/C1…C4`, `workspace.dsl`.
