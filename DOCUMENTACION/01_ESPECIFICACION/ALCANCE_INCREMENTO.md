# Alcance del incremento funcional — Backend Fase 1 (Evaluación Sumativa 1)

**Fuentes:** `docs/01-introduccion/alcance.md`, `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §5, `DOCUMENTACION/00_AUDITORIA/INVENTARIO_PROYECTO.md`.

## 1. Qué cubre el incremento evaluado

El incremento funcional corresponde al **backend de la Fase 1 (MVP de Aptitud Legal)**, implementado como monolito modular Django/DRF con arquitectura hexagonal real (verificado en código, no solo documentado — ver `DOCUMENTACION/00_AUDITORIA/INVENTARIO_PROYECTO.md` §2).

| Área funcional | Contenido | Evidencia de implementación |
|---|---|---|
| Gestión de expedientes | Creación, envío, bandeja por rol | App `expedientes` (6 serializers, 4 vistas, 2 servicios, 7 archivos de prueba) |
| Petición documental | Solicitud interna de certificados, carga/descarga de PDF versionado | App `peticiones` (7 serializers, 6 vistas, 2 servicios, 5 archivos de prueba) |
| Verificación | Checklist digital, observaciones accionables, subsanación | App `verificacion` (8 serializers, 7 vistas, 4 servicios, 4 archivos de prueba) |
| Resoluciones | Informe de aptitud (Providencia 590), declaratoria (Memorando 162) | App `resoluciones` (2 serializers, 7 vistas, 2 servicios, 5 archivos de prueba) |
| Notificaciones | Notificaciones internas, bitácora de auditoría JSONB | App `notificaciones` (2 serializers, 1 vista, 1 servicio, 5 archivos de prueba) |
| Autenticación/RBAC | JWT, matriz de 8 roles × recurso × método | App `authentication` (1 serializer, 1 vista, 6 archivos de prueba) |
| Transversal | Puertos/adaptadores (mock SGA, validación PDF, almacenamiento privado, filtro de ámbito) | `core/ports`, `core/adapters` |

## 2. Qué NO cubre (fuera de alcance de este incremento)

- Integración real con el SGA/SIAAF institucional y con FirmaEC (ambas simuladas por decisión de diseño — `DEC-04`/`DEC-05` en `clarify.md`).
- Fase 2 (sustentación/defensa, Arts. 236–237) y Fase 3 (cierre/SENESCYT, Arts. 243–244): solo diseño preliminar (`RF-014`…`RF-016`), sin implementación.
- Frontend de negocio completo: a la fecha de este informe (2026-11-06), según `CLAUDE.md` (fuente más reciente), están cerradas las fases F0–F2.5 y las vistas V-01 (login), V-02 (dashboard/bandeja), V-03 (nueva solicitud) y V-04 (expediente/requisitos). **V-05 en adelante no han iniciado** y requieren autorización explícita independiente.
- Estados `CANCELADA` (expediente) y `LEGALIZADO` (petición): definidos en el enum del modelo pero sin flujo que los produzca (confirmado por `docs/01-introduccion/introduccion.md` y por `docs/auditoria/matriz-trazabilidad.md`, sección "Requisitos sin implementación declarada").
- CRUD de catálogo de requisitos y modalidades de titulación: sin endpoint (NI, no implementado).

## 3. Restricciones de modificación vigentes durante esta auditoría documental

Por instrucción del encargo y por las prohibiciones ya vigentes en `AGENTS.md`/`CLAUDE.md`, este trabajo de documentación **no modifica** `backend/`, `openapi.yaml`, las migraciones, ni las specs 001/Constitución. Cualquier corrección de código identificada en la auditoría (Fase 0) se reporta como hallazgo, no se aplica.

## 4. Relación con el frontend (fuera del incremento backend, pero parte del sistema documentado)

El frontend (`frontend/`) tiene su propio ciclo SDD (`specs/003-frontend-titulacion/`) y su propio `CLAUDE.md` con reglas de "frontend only". Este expediente de documentación lo describe como parte del sistema completo (para contexto, arquitectura y API), pero el incremento evaluado en la Evaluación Sumativa 1, según el título del encargo ("incremento funcional del backend"), es el backend de Fase 1.
