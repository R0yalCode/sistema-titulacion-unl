# Ruta de integración futura con SGT-SIAAF original

**No ejecutar automáticamente esta guía.** Se necesita revisión del equipo, especificaciones y autorización antes de modificar el proyecto `C:\Users\Juaaaaan\sgt-siaaf`.

## 1. Objetivo

Convertir gradualmente estas nueve vistas HTML/CSS/JS en componentes de React + TypeScript que consuman la API REST existente en Django REST Framework. **El prototipo actual NO consume esa API.**

## 2. Alcance real al momento de elaborar estas pantallas

### Feature 001, original

- `POST /api/v1/solicitudes` — crear solicitud de aptitud legal.
- `GET /api/v1/solicitudes` — listar solicitudes propias.
- `GET /api/v1/solicitudes/{id}` — obtener detalle, cinco requisitos y versión.
- `PATCH /api/v1/solicitudes/{id}` — modificación permitida con `ETag` / `If-Match`.
- Estado global `BORRADOR`; requisitos inicialmente `PENDIENTE`.

### Feature 002, SOLO EN LA COPIA DEMO (no asumir original)

- `POST /api/v1/solicitudes/{id}/peticiones` — crear petición con cuerpo `{ "requisito": "TIPO" }`.
- `GET /api/v1/solicitudes/{id}/peticiones` y su endpoint de detalle.
- `GET /api/v1/dependencias/{codigo}/peticiones?page=N` — bandeja autorizada, de solo lectura.
- El requisito pasa `PENDIENTE` → `SOLICITADO`; global sigue `BORRADOR`.
- Control de duplicados, permisos y error 403 para dependencias no asignadas.

**No copiar migraciones o código de la demo al original sin una fase de integración explícita.**

## 3. Correspondencia de UI

| Vista prototipo | Datos necesarios | Riesgos a resolver |
|---|---|---|
| Acceso | Flujo de autenticación real aprobado | No existe un login convencional confirmado en el original; no reemplazarlo por una autenticación falsa |
| Estudiante no habilitado | Carrera, ciclo, créditos, condición de elegibilidad | Fuente SGA y reglas de noveno ciclo pendientes de validación; no inventar datos |
| Dashboard | `GET /solicitudes` + detalle | No equiparar «SOLICITADO» con «CUMPLIDO» |
| Crear solicitud | `POST /solicitudes` | Usar SOLO el enum `opcion_titulacion` aceptado por el backend; el prototipo tiene opciones ilustrativas |
| Expediente | `GET /solicitudes/{id}` | Tipos reales, versiones, propietarios y fechas UTC → America/Guayaquil |
| Solicitar documento | Endpoint POST de la feature 002 cuando exista en el original | Body real solo `{requisito: TIPO}`; descripción/PDF todavía no disponibles |
| Seguimiento | GET de petición | Estados de atención/entrega de documentación todavía no disponibles |
| Bandeja | GET de dependencia asignada | Autorización por servidor, paginación, no exponer información no entregada por API |
| Detalle funcionario | Campos reales de petición | No generar respuesta, aprobación, adjuntos, observaciones o datos personales adicionales ficticios |

## 4. Pasos seguros a futuro

1. Leer `spec.md`, `tasks.md`, los contratos y ADRs del proyecto **original** y verificar el estado real de la feature 001/T063.
2. Definir un ADR de implementación frontend y autenticar contra backend de forma autorizada.
3. Configurar build estático de React/TypeScript con HTTPS en el origen autorizado, sin modificar permisos SQL ni el sistema original en producción.
4. Implementar primero las vistas de feature 001 y probar `GET`/`POST`/`PATCH`, errores y concurrencia `If-Match`.
5. Planificar formalmente feature 002 y solo después integrar creación de peticiones y bandeja.
6. Incorporar el registro de estudiante próximo a egresar únicamente cuando la elegibilidad esté definida por requisitos oficiales.
7. Mantener las pruebas del backend y añadir pruebas E2E de frontend, seguridad y accesibilidad.

## 5. Ideas visuales trasladables sin nuevo backend

- Mejor jerarquía de pantallas, menú lateral, tablas, búsqueda **local sobre datos realmente cargados**.
- Etiquetas amigables para los cinco códigos de requisito, preservando sus valores de API.
- Estados vacíos, validaciones visibles, diseño responsive y accesible.
- Distinción explícita entre solicitud, requisito y petición documental.

## 6. Estado documental

Estas vistas son una referencia visual para discusión del equipo. Las reglas institucionales (ciclo, documentos exigidos, roles finales, plazos y flujo de aprobación) deben contrastarse con `docs/`, `requirements/`, y validarse con la autoridad académica pertinente. No presentar este prototipo como sistema oficial ni como feature 003.
