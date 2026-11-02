# ADR-0002: Stack Backend — Django 5.x + Django REST Framework + PostgreSQL 16

- **Estado:** Aceptado
- **Fecha:** 20 de octubre de 2026
- **Tarea de origen:** `T006` en `tasks.md` v1.0.0
- **Sistema:** SGT-SIAAF — Backend de la Fase de entrega 1 (Unidad 1)

## Contexto

El backend debía seleccionar el lenguajaje/framework de servidor, el marco
API y el motor de base de datos para la simulación del trámite de titulación,
teniendo en cuenta: (a) los principios de la Constitución (sección 6
"Aquitectura y Tecnologías"), (b) los requisitos no funcionales de
`specify.md` (`RNF-001` a `RNF-018`), (c) el plazo del sílabo (5 semanas) y
(d) las capacidades de datos requeridas (JSONB para auditoría, bloqueo
pesimista para el checklist, fechas y transacciones).

## Decisión

1. **Lenguaje y framework:** Python 3.12+ con **Django 5.x**.
2. **Capa de API:** **Django REST Framework (DRF)** que expone la API REST
   versionada bajo `/api/v1/`, con contratos `OpenAPI`.
3. **Base de datos:** **PostgreSQL 16**, vía driver **psycopg 3**.
4. **Entornos reproducibles:** Docker / Docker Compose (Dockerfile +
   `docker-compose.yml` verificados en `T002`), con verificación de calidad de
   código protegidas con lint (`T005`).
5. Autenticación JWT: se decide por la separación ADR-003
   (`djangorestframework-simplejwt`), no por este ADR.

## Justificación (plan.md § 6.2)

- *Django + DRF:* paradigma baterías incluidas, ORM declarativo,
  serializadores con validaciones integradas, ecosistema maduro de seguridad
  y de pruebas.
- *PostgreSQL 16:* transacciones ACID, tipos `JSONB` para la bitácora inmutable
  de auditoría (`RF-013`), cálculo de fechas y bloqueo pesimista
  `SELECT FOR UPDATE` para el checklist digital (`ADR-007`) y soporte nativo a
  requisitos de integridad y concurrencia.

## Consecuencias

- Positivas: la estructura aprobada ya se verifica en los entornos
  contenerizados (T002-T004), reduciendo riesgo de (re)configuración durante
  las semanas restantes; DRF y PostgreSQL proveen los mecanismos exigidos por
  los requisitos transaccionales y de auditoría del MVP.
- Negativas: acoplamiento tecnológico a Python/Django; las versiones exactas
  se mantienen en `requirements.txt`; los cambios de versión mayor requieren
  nuevo ADR.
- La conexión productiva a sistemas institucionales (`SGA/SIAAF`) queda
  fuera de decisión y queda bajo ADR-004 (mock `SGAMockAdapter`), sin
  supervisión funcional del dominio ni credenciales reales.

## Referencias

- `constitucion.md` — sección 6 ("Arquitectura y tecnologías"), P-12, P-13.
- `plan.md` — § 2, § 6.2, § 11 (fronteras), § 13 (árbol), § 23 (Docker/
  reproducibilidad).
- `specify.md` — `RF-006` (checklist digital), `RF-013` (bitácora inmutable
  JSONB), `RNF-001` (JWT), `RNF-006` (OpenAPI), `RNF-009` (Monolito modular),
  `RNF-010` (Docker Compose reproducible).
- `tasks.md` — Tareas `T002`, `T003`, `T004` y `T005` (implementación ya
  verificada del stack aprobado).
