---
system: SGT-SIAAF
type: operations
area: soporte
status: verified
source: verified-code
last_verified: 2026-11-23
---

# Operación habitual y solución de problemas

> Comandos para el entorno de **desarrollo** (`docker-compose.yml`).

## Operaciones habituales

```bash
docker compose up --build -d nginx      # recompilar solo el frontend (no toca la base de datos)
docker compose logs -f backend          # ver el log del backend (incluye los correos en desarrollo)
docker compose restart nginx            # tras editar nginx/nginx.conf (está montado desde el equipo)
```

Para reconstruir el backend tras cambios de código:

```bash
docker compose up --build -d backend
```

> ⚠️ Este comando **recrea** el contenedor `backend`. En desarrollo los PDF se guardan en `backend/src/media`, fuera del volumen `media_data`, así que **se pierden** y sus filas quedan sin archivo. Ver [[INITIAL_DATA]] §8.

## Problemas frecuentes

| Problema | Qué hacer |
|---|---|
| `POSTGRES_PASSWORD is required` / `SECRET_KEY is required` | Defina la variable en el `.env` de la raíz |
| Errores de tablas inexistentes tras actualizar | `docker compose exec backend python manage.py migrate` |
| El frontend no refleja los cambios | `docker compose up --build -d nginx` |
| La API falla desde el navegador | Use `http://localhost:8000`, no `127.0.0.1` |
| «Ingrese un correo institucional válido» | Use su correo completo `@unl.edu.ec`, no el nombre de usuario |
| El código TOTP es rechazado | Hora automática en el teléfono, código vigente y cuenta correcta (README §7) |
| «La verificación caducó…» | El reto dura 5 minutos o se agotaron los 5 intentos: vuelva a iniciar sesión |
| No llega el correo de recuperación | En desarrollo no se envían correos: búsquelo con `docker compose logs backend` |
| Tras cambiar `SECRET_KEY` en desarrollo el código nunca es válido | La clave del 2FA se deriva de `SECRET_KEY`: restablezca el 2FA ([[USER_ACCESS_GUIDE]] §7) y registre de nuevo el autenticador |
| `seed_initial_data` indica que falta `SEED_DEMO_PASSWORD` | Pásela con `docker compose exec -e` ([[INITIAL_DATA]] §3) |
| `seed_mock_sga` indica que el entorno no permite la fuente simulada | Revise `ACADEMIC_PROFILE_MOCK_ALLOWED`. En producción es el comportamiento correcto |
| `seed_* solo puede ejecutarse en desarrollo o pruebas` | La protección rechazó el entorno. En producción es el comportamiento correcto ([[INITIAL_DATA]]) |
| Producción no arranca con `ImproperlyConfigured` sobre correo o `FRONTEND_BASE_URL` | Revise las variables de `docs/08-infraestructura/despliegue.md`, sección «Correo y enlaces de recuperación» |
| La base de datos no arranca | `docker compose logs db` |

## Relacionado

[[DOCKER]] · [[ENVIRONMENTS]] · [[INITIAL_DATA]] · [[USER_ACCESS_GUIDE]]
