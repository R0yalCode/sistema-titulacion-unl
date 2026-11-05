# ADR-0009: Incorporación de Django Admin como consola interna de administración (Sprint S1)

**Estado:** Aceptado (02-nov-2026)
**Decisionado por:** Equipo SGT-SIAAF (autorización del product owner, 02-nov-2026)
**Enmienda asociada:** Constitución v2.1 (P-18, §2, §11) — `sgt-siaaf/specs/001-tramite-titulacion/constitucion.md`
**Tarea asociada:** S1-T04 (`docs/sprint-S1/S1_04_MATRIZ_TAREAS_S1.md`)

## Contexto

La versión 2.0 de la Constitución y `tasks.md` §4.2 excluían la "Habilitación de Django Admin como interfaz operativa expuesta por HTTP" del MVP. El diagnóstico S1 (`S1_03_DIAGNOSTICO_DJANGO_ADMIN.md`) constató que no existe ningún `admin.py`, `django.contrib.admin` no está en `INSTALLED_APPS` y no hay ruta `/admin/`.

La auditoría S1 identificó la necesidad de una consola de administración de soporte (gestión de cuentas/roles, catálogos, correcciones controladas, visualización de bitácoras). El equipo **aprobó expresamente (02-nov-2026) la incorporación de Django Admin** en el Sprint S1, condicionada a los controles de seguridad de la auditoría.

## Decisión

Se incorpora Django Admin como **consola interna de administración y soporte técnico**, NO como interfaz operativa del trámite:

1. Los actores del trámite (estudiante, secretaría, jurista, decano, director) continúan operando exclusivamente por la API REST (`/api/v1/`) y el futuro frontend React.
2. El acceso Admin se restringe a perfiles `staff`/`superuser` controlados, creados por semilla (`seed_initial_data`) o alta explícita. El usuario de migraciones/BD no se usa como credencial HTTP (P-18).
3. Modelos inmutables (`InformeAptitud`, `DeclaratoriaAptitud`, `EventoAuditoria`, `HistorialEstado`) quedan en solo lectura, sin agregar ni eliminar.
4. Campos sensibles en solo lectura: `hash_sha256`, rutas de archivo, tamaños, y estados con transición controlada (`estado` de expedientes/peticiones/checklist y `resuelta` de observaciones no son editables desde formularios admin).
5. Eliminación deshabilitada para expedientes, documentos, declaratorias, informes, bitácoras (P-08, reglas S1 §5.2/5.8).
6. No se exponen enlaces a archivos privados desde Admin (descarga solo por endpoint API autorizado).
7. Configuración mínima: `django.contrib.admin` + `django.contrib.messages` en `INSTALLED_APPS`; `AuthenticationMiddleware` y `MessageMiddleware` en `MIDDLEWARE`; `path("admin/", admin.site.urls)`.

## Consecuencias

**Positivas:** consola de soporte operativa; gestión de catálogos/usuarios conforme a la matriz 6.2 (ADMINISTRADOR ya tenía permisos de catálogo); trazabilidad visual de bitácoras.

**Negativas / riesgos gestionados:**
- Se añaden sesiones y CSRF a la superficie del backend (mitigación: ruta admin sin exposición pública por Nginx; auditoría A-08 como control).
- Acciones de negocio vía Admin prohibidas (transiciones solo por servicios de dominio); cualquier acción futura requiere nuevo incremento (P-18).

## Alternativas descartadas

- Mantener la exclusión (v2.0): el equipo la desautorizó explícitamente al aprobar el Bloque C del Sprint S1.
- Herramientas externas (django-su, schleuder, fabric): innecesarias para la escala; Django Admin ya está en el stack aprobado (ADR-002) y plan.md §10 lo contemplaba como adaptador de entrada.
