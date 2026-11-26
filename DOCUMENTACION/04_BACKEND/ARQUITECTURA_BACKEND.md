---
title: "Arquitectura del backend"
---

# Arquitectura del backend — SGT-SIAAF

**Fuente:** estructura real de `backend/src/` (verificada con `find`/`ls` en las Fases 0 y 3), complementada por `DOCUMENTACION/03_ARQUITECTURA/{C3_COMPONENTES.md,ADR.md}` (no se repite el contenido de esas páginas, se referencia).

## 1. Organización de directorios

```
backend/src/
├── config/
│   ├── settings/{base,local,production,test}.py
│   ├── urls.py            # enrutamiento centralizado, 21 declaraciones path()
│   └── wsgi.py / asgi.py
├── core/                  # módulo transversal, no es una "app" de negocio
│   ├── ports/              # ISGALegacyPort (único puerto abstracto real)
│   ├── adapters/           # mock_sga, pdf_validation, local_storage, scope_filter,
│   │                       # middleware, client_ip, security_headers, health, logging_filters
│   └── tests/
└── apps/
    ├── authentication/     # adapters/, domain/, ports/ (vacío), services/ (vacío), tests/
    ├── expedientes/        # adapters/, domain/, services/, tests/
    ├── peticiones/         # adapters/, domain/, services/, tests/
    ├── verificacion/       # adapters/, domain/, services/, tests/
    ├── resoluciones/       # adapters/, domain/, services/, tests/
    └── notificaciones/     # adapters/, domain/, services/, tests/
```

Cada app de negocio sigue la misma convención interna (arquitectura hexagonal por app, no solo a nivel de proyecto):

| Subcarpeta | Contenido típico |
|---|---|
| `adapters/` | `models.py` (ORM Django), `views.py` (DRF ViewSets), `serializers.py`, `permissions.py` (solo en `authentication`) |
| `domain/` | Lógica de dominio; en la práctica, solo `expedientes/domain/plazo_calculator.py` contiene una clase de dominio verdaderamente pura (sin imports de Django) |
| `services/` | Casos de uso (capa de aplicación): funciones `execute(...)` con excepciones de dominio propias por archivo |
| `tests/` | Pruebas unitarias/integración de la app |

## 2. Separación de responsabilidades (verificada, no solo declarada)

- **Capa de presentación/entrada**: `adapters/views.py` (DRF ViewSets) y `adapters/serializers.py`. Reciben la petición HTTP, delegan al servicio correspondiente.
- **Capa de aplicación**: `services/*.py`. Cada archivo de servicio expone una función `execute(...)` y declara sus propias excepciones de dominio (p. ej. `ExpedienteActivoExistenteError`, `RequisitosIncompletosError`, `VerificationAlreadyCompletedError`) — esto es consistente con un patrón de "casos de uso" explícito, verificado en 13 archivos de servicio reales (`crear_expediente.py`, `enviar_expediente.py`, `solicitar_emision.py`, `cargar_documento.py`, `evaluar_checklist.py`, `registrar_observacion.py`, `subsanar_requisito.py`, `validar_checklist_completo.py`, `emitir_informe.py`, `declarar_aptitud.py`, `notification_service.py`).
- **Capa de dominio puro**: limitada en la práctica a `PlazoLaboralCalculator` (cálculo de días laborables, sin dependencias de framework). La mayoría de la "lógica de negocio" vive en los servicios de aplicación, que sí importan Django (acceso directo al ORM) — ver la nota de fidelidad en `C3_COMPONENTES.md` sobre por qué esto difiere del diseño idealizado de `plan.md`.
- **Capa de infraestructura/adaptadores de salida**: `core/adapters/` (mock SGA, validación PDF, almacenamiento privado, filtro de ámbito anti-IDOR, middleware de IP de auditoría).

`authentication` es la única app sin `services/` con contenido: su lógica de autorización vive enteramente en `adapters/permissions.py` (`RBAC_MATRIX` + `HasRolePermission`), no en casos de uso — es coherente con su naturaleza transversal (no hay un "caso de uso de negocio" para autenticar, solo para autorizar en cada petición).

## 3. Dependencias entre módulos (verificadas por `grep` de imports/llamadas reales)

Ver la tabla completa y el diagrama en `DOCUMENTACION/03_ARQUITECTURA/C3_COMPONENTES.md`. Resumen de la cadena principal: `authentication` (base) ← `expedientes` ← `peticiones` ← `verificacion` ← `resoluciones`; `notificaciones` observa a todos vía Django signals (acoplamiento débil, no importa directamente los servicios de las otras apps).

## 4. Enrutamiento

`config/urls.py` centraliza las 21 rutas de `/api/v1/` **sin** usar `DefaultRouter` de DRF (confirmado por `auditoria/01_AUDITORIA_GENERAL.md` y no contradicho en esta verificación): cada `path()` se declara explícitamente, a diferencia del patrón más común de registrar un router por ViewSet.

## 5. Configuración por entorno

Cuatro módulos de settings (`base.py`, `local.py`, `production.py`, `test.py`), siguiendo el patrón 12-factor con `django-environ`. `base.py` define `DEBUG=False` por defecto y no fija un `SECRET_KEY` de reserva (verificado en Fase 0) — ambos son buenas prácticas de seguridad por defecto.
