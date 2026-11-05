---
title: "Arquitectura del backend"
---

# Arquitectura del backend

## Estructura

```
backend/src/
├── config/                     # settings (base/local/test), urls, wsgi/asgi
├── core/                       # infraestructura compartida (no es app Django)
│   ├── ports/                  # ISGALegacyPort (contrato del SGA)
│   └── adapters/               # mock_sga, local_storage, pdf_validation, scope_filter
└── apps/
    ├── authentication/         # User, Role, UserRole, JWT, matriz RBAC
    ├── expedientes/            # ciclo de vida del expediente y plazos
    ├── peticiones/             # catálogo Art. 235, peticiones, documentos PDF
    ├── verificacion/           # checklist, observaciones, subsanación
    ├── resoluciones/           # informe 590, declaratoria 162, PDF ReportLab
    └── notificaciones/         # notificaciones in-app y auditoría JSONB
```

Cada app de negocio sigue el mismo patrón interno:

```
apps/<dominio>/
├── domain/       # reglas puras (sin Django)
├── services/     # casos de uso transaccionales
└── adapters/     # models, serializers, views, admin, migrations
```

## Capas y dependencias

| Capa | Responsabilidad | Puede depender de |
|---|---|---|
| `domain/` | Reglas puras (plazos, estados) | Nada |
| `services/` | Casos de uso: validación, transiciones, efectos | `domain/`, modelos de su app, `core` |
| `adapters/` | HTTP (serializers/views), ORM, admin | `services/`, `core` |
| `core` | Puertos y adaptadores compartidos | Nada de las apps |

Ejemplo verificado: `apps/expedientes/domain/plazo_calculator.py` no importa Django; `services/enviar_expediente.py` lo orquesta dentro de una transacción; `adapters/views.py` solo mapea excepciones a códigos HTTP.

## Decisiones estructurales clave

- **URLs centralizadas**: no hay `urls.py` por app; todo se registra en `config/urls.py` con `path()` explícitos (sin router DRF).
- **Permisos**: `IsAuthenticated` + `HasRolePermission` en todas las vistas de negocio; el recurso RBAC se declara por vista (`get_rbac_resource()`).
- **Aislamiento de datos**: `ScopeFilterMixin` compone `Q()` por ámbito en `get_queryset()`; los detalles usan `get_object_or_404` sobre el queryset filtrado → 404 ante objetos ajenos.
- **Serializers de salida** explícitos por caso de uso (borrador, enviado, detalle, bandeja) en lugar de un serializer genérico.
- **Notificaciones sincrónicas**: el despacho es in-process (sin cola); decisión documentada en el servicio.
- **Auditoría por signals**: `post_save` sobre las entidades críticas escribe `EventoAuditoria` (JSONB inmutable).

## Manejo de errores

| Excepción de dominio | HTTP | code DRF |
|---|---|---|
| Estado inválido del expediente | 400 | `expediente_estado_invalido` / afines |
| Requisitos incompletos al enviar | **422** | `requisitos_incompletos` |
| Objeto fuera de ámbito | 404 | — (get_object_or_404) |
| Rol sin celda en la matriz | 403 | — (HasRolePermission) |
| PDF inválido o grande | 400 | `pdf_validation_error` / `file_too_large` |
| Informe/declaratoria duplicados | 400 | `informe_ya_emitido` / `declaratoria_ya_emitida` |

## Configuración

`config/settings/` separa `base.py` (común, segura por defecto: `DEBUG=False`, `SECRET_KEY` obligatoria), `local.py` (`DEBUG=True`) y `test.py` (SQLite en memoria, hasher MD5). No existe `production.py` (ver consideraciones de seguridad).
