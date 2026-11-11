---
system: SGT-SIAAF
type: operations
status: verified
source: repository-config
last_verified: 2026-11-11
---

# Entornos

| Entorno | Settings Django | Cómo se levanta | Particularidades |
|---|---|---|---|
| Desarrollo | `config.settings.local` | `docker compose up` (backend en `:8000` vía Nginx) + `npm --prefix frontend run dev` (`:5173`) | `DEBUG=1` por defecto; CORS de desarrollo pendiente (BE-08) |
| Pruebas | `config.settings.test` | `pytest` (backend), `npm run test` (frontend, jsdom + MSW) | jsdom fija `innerWidth=1024` y no implementa `matchMedia` (D-FE-01) |
| Producción | `config.settings.production` | `docker compose -f docker-compose.prod.yml up` | HTTPS, HSTS, CSP report-only, cookies seguras; Swagger restringido; logs JSON en `LOG_DIR` |

Todos los datos son ficticios (simulación académica); el SGA solo se usa mediante `SGAMockAdapter`. **Nunca** apuntar a BD productivas del SGA/SIAAF (RN-012).

Detalle: [[DOCKER]].
