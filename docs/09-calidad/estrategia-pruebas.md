---
title: "Estrategia de pruebas"
---

# Estrategia de pruebas

## Principios

1. **Pruebas por capa**: dominio puro (sin Django), servicios transaccionales, endpoints HTTP, permisos/IDOR, integración E2E.
2. **La matriz RBAC se prueba contra la spec**: existe una prueba que compara la matriz codificada con el literal 6.2 del documento de especificación.
3. **Aislamiento con semántica 404**: cada rol tiene pruebas que exigen 404 ante objetos ajenos.
4. **Accesibilidad en frontend**: cada componente del design system incluye aserciones axe (`toHaveNoViolations`).

## Inventario backend (526 pruebas)

| Área | Pruebas | Qué verifica |
|---|---|---|
| authentication | 28 | JWT (7), RBAC (17), Admin (4) |
| expedientes | 73 | Crear (8), enviar (7), máquina de estados (25), IDOR (13), bandeja (9), plazos (11) |
| peticiones | 85 | Solicitar emisión (15), cargar (19), descargar (12), seguridad PDF (39) |
| verificacion | 72 | Evaluar (22), ciclo observar-subsanar (28), subsanar (15), completitud (7) |
| resoluciones | 113 | Informe (24), declaratoria (29), modelos (16), PDF (30), flujo (14) |
| notificaciones | 71 | Servicio (17), endpoints (12), auditoría (14), integración (28) |
| core | 71 | Validación PDF (24), mock SGA (25), puerto (22) |
| E2E | 4 | Flujo completo FL-01→FL-05, mock SGA, IDOR, matriz |

## Inventario frontend (198 pruebas, 43 archivos)

| Área | Contenido |
|---|---|
| Infra | cliente HTTP (status codes, 401 global, timeout, red), errores, env, validación PDF |
| Auth | JWT, storage, AuthContext, guards, redirect, expiración de sesión |
| Router | rutas oficiales, guards por rol, 404 |
| UI | ~24 componentes con axe |
| Layout | AppLayout, Sidebar, ToastProvider, ErrorBoundary, DemoBanner |

## Vacíos identificados

- Sin pruebas sobre PostgreSQL real en esta auditoría (SQLite).
- Sin E2E de navegador en frontend (no hay Playwright/Cypress).
- Ramas de error con menor cobertura (`verificacion/views.py` 65 %).
- Sin pruebas de carga/concurrencia paralela real.
- `core` y `e2e` fuera de `testpaths` (AUD-P1-04).
