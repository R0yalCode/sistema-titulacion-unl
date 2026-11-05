> **⚠ Documento duplicado (2026-11-04).** Este archivo existe en `docs/frontend/` (copia de lectura) y en `diseno-ui/ui/titulacion-v2/` (copia **canónica**, junto a las especificaciones `especificaciones/01…08`). Ambas eran idénticas byte a byte; cualquier cambio futuro debe hacerse primero en la canónica y propagarse a la otra. Fuente de verdad funcional: `specs/003-frontend-titulacion/specify.md` §6.1 y `clarify.md`.

# SGT-SIAAF — Guía de implementación de las 9 vistas de titulación

**Documento de referencia visual v2 — 21 de octubre de 2026**  
**Proyecto objetivo:** `C:\Users\Juaaaaan\sgt-siaaf` (original).  
**Proyecto de experimentos:** `C:\Users\Juaaaaan\sgt-siaaf-demo` (no fusionar automáticamente).  
**Identidad del sistema:** **SGT-SIAAF — Sistema de Gestión del Trámite de Titulación**.  
**Institución de referencia:** Universidad Nacional de Loja (UNL).  
**Estado:** propuesta académica, no diseño institucional autorizado ni aplicación funcional.

## 1. Cómo utilizar este paquete

Los PNG son **referencias de apariencia, distribución, navegación y jerarquía visual**, no código fuente ni documentación de requisitos. No debe implementarse ninguna característica basándose exclusivamente en que aparezca dibujada. Contrastar cada control y campo con `specs/`, `requirements/`, `docs/` y el contrato OpenAPI correspondiente **del proyecto original**. Los documentos de requisitos pueden ser propuestas pendientes de validación docente.

**Estado de referencia al elaborar esta guía:**
- **Original:** feature 001 (solicitudes de aptitud legal); T063 estaba pendiente de reproducción independiente.
- **Copia demo:** feature 002 con creación/consulta de peticiones documentales y bandeja de funcionario **de solo lectura**, además de frontend temporal.
- **No asumir que 002 ya se integró al original.** No copiar código, migraciones o volúmenes de la demo al original sin nueva planificación y autorización.

## 2. Lenguaje visual

- Marca textual consistente en todas las pantallas: **SGT-SIAAF** y subtítulo **Trámite de Titulación** o **Módulo de Titulación**. No alternar arbitrariamente con «SGT-TITULACIÓN».
- Referencias cromáticas para el diseño: rojo `#BF0811`, verde `#4F8E3A`, azul secundario `#004C7B`, blanco `#FFFFFF`, fondos neutros `#F6F8FA`; estos códigos son **propuesta de UI**, no certificado de exactitud cromática institucional.
- Predominio de blanco, superficies neutras, sidebar verde profundo y rojo como acento de acción. Evitar degradados fuertes, sobrecarga de tarjetas y exceso de badges.
- Tipografía legible, rejilla responsive, foco visible, contraste WCAG, formularios etiquetados, estados vacíos y manejo de errores.
- Los escudos, fotografías, personas, correos y nombres generados mediante IA **no son recursos oficiales aprobados**: reemplazar con material institucional autorizado y datos ficticios identificables. No inventar nombres de estudiantes o identificaciones reales.
- Los estados, nombres de dependencia, fechas, estadísticas y acciones de las imágenes **son ilustrativos**. Solo la respuesta del backend determina el estado real.

## 3. Vistas y correspondencia con las features

| PNG | Vista | Qué conservar | Límites y reglas |
|---|---|---|---|
| `01_inicio_sesion_conceptual.png` | Acceso | Composición dividida, identidad y formulario limpio | **Conceptual.** El original no tiene login institucional confirmado. El JWT de demostración se emitía por comando local. Implementar credenciales solo después de aprobar diseño, seguridad y endpoint real. |
| `02_estudiante_no_habilitado_conceptual.png` | Estudiante aún no habilitado | Aviso de elegibilidad y explicación de próximos pasos | **Conceptual.** No inventar un servicio que compruebe noveno ciclo, créditos, carrera o habilitación. Reglas académicas y datos institucionales pendientes de validación. |
| `03_dashboard_estudiante.png` | Inicio del estudiante | Expediente protagonista, tarjetas discretas, resumen de requisitos y próximos pasos | **Parcial.** Mostrar solo datos disponibles; no inventar créditos/ciclo/nombre. «SOLICITADO» **no equivale a CUMPLIDO**; corregir barras de progreso, porcentajes y etiquetas del mockup. |
| `04_crear_solicitud.png` | Nueva solicitud de aptitud legal | Formulario guiado, selección y confirmación antes de enviar | **Feature 001.** Las opciones son las que acepte `opcion_titulacion` en el contrato real. Las tres opciones dibujadas son ejemplos, no un catálogo aprobado. El POST inicial crea expediente `BORRADOR` y cinco requisitos. |
| `05_expediente_requisitos.png` | Mi expediente | Resumen, versión, cinco requisitos en tabla y acciones claras | **Feature 001 / 002 en demo.** Conservar tipos reales `RECORD_ACADEMICO`, `PRACTICAS_VINCULACION`, `SUFICIENCIA_B1`, `CULMINACION_OPCION`, `NO_ADEUDAR_TESORERIA`. Los rótulos bonitos no deben reemplazar el `tipo` requerido por API. Estado inicial `PENDIENTE`, y `SOLICITADO` al crear petición en demo; solicitud global sigue `BORRADOR`. |
| `06_peticion_documental_conceptual.png` | Crear petición | Modal contextual, requisito y dependencia responsable, confirmación | **Feature 002 en demo parcialmente.** POST real `{ "requisito": "TIPO" }`; no agregar descripción, carga de archivos ni notificación como operaciones efectivas sin una feature que lo soporte. La dependencia exacta proviene del catálogo provisional/contrato, no del dibujo. |
| `07_seguimiento_peticion_conceptual.png` | Ver petición | Encabezado claro, detalles, fecha de registro y contexto | **Parcial/conceptual.** La demo permite GET petición y estado inicial. «EN REVISIÓN», «EN ATENCIÓN», emisión de documentos y cronología de hitos posteriores **no están implementados**. No simularlos como respuesta real. |
| `08_bandeja_funcionario.png` | Bandeja | Filtros visuales, tabla, paginación, estados legibles | **Feature 002 en demo.** GET `/api/v1/dependencias/{codigo}/peticiones?page=N`, únicamente dependencias asignadas y **solo lectura**. Campos como nombre del estudiante, observaciones, búsqueda global o estados futuros solo si la API autorizada los devuelve. |
| `09_detalle_funcionario_conceptual.png` | Detalle de petición | Presentación por secciones y separación de información | **Parcial/conceptual.** No hay acciones de atención, adjuntos PDF, historial completo ni perfil extendido confirmado. El detalle debe limitarse a campos autorizados por el contrato real. |

**Atención a discrepancias de las maquetas:** hay distintas etiquetas para el sistema y sus requisitos, diferentes nombres de dependencia, y ejemplos de estados no desarrollados. Al programar, normalizar los nombres y usar los enums reales. No usar los textos de las imágenes como fuente normativa.

## 4. Navegación propuesta por rol

**Estudiante (feature 001 original):**
1. Inicio / mi expediente actual.
2. Crear solicitud (si el backend y las reglas lo permiten).
3. Consultar solicitud y requisitos.
4. Editar opción de titulación con `ETag`/`If-Match`, si está permitido.
5. Manejo claro de `BORRADOR`, `PENDIENTE`, `401`, `403`, `404`, `412`, `428`.

**Estudiante (cuando 002 esté formalmente aprobada e integrada):**
6. Solicitar documento por `tipo` de requisito.
7. Consultar peticiones y sus fechas.
8. Manejar `409 PETICION_DUPLICADA`, sin duplicar registro.
9. **Solicitado no significa entregado, validado o aprobado.**

**Funcionario (cuando 002 esté formalmente integrada):**
1. Acceso autenticado y rol determinado en backend.
2. Bandeja filtrada por dependencia autorizada.
3. Consulta de las peticiones propias de la unidad.
4. `403 DEPENDENCIA_NO_ASIGNADA` sin revelar datos de otras unidades.
5. **Sin aprobar/rechazar/responder/subir archivos** hasta desarrollo posterior.

**Estudiante anterior a noveno ciclo:** pantalla solo conceptual hasta definir elegibilidad y fuente de datos académicos.

## 5. Seguridad, datos y arquitectura

- Mantener arquitectura: **React + TypeScript → Caddy HTTPS → Django REST Framework → PostgreSQL**.
- JWT es autenticación, pero **la autorización se verifica en el servidor**.
- Si se usa el método temporal de demo, token exclusivamente en memoria; no `localStorage`, URL, archivos o consola.
- No construir un login con contraseña ficticio que parezca operativo si el backend no lo soporta.
- No conectar a SGA/SIAAF real ni prometer datos de ciclo/créditos sin acceso autorizado.
- El diseño es para la **Universidad Nacional de Loja**, pero la propuesta no constituye aprobación ni representación institucional.
- Datos ficticios y recursos de marca autorizados.

## 6. Orden de implementación recomendado

**Fase A — cuando Astra esté disponible:**
1. Inspeccionar **solo** el original y verificar feature 001, contratos y pendiente T063.
2. Crear un ADR/plan exclusivamente de frontend para feature 001, sin cambiar alcance del backend.
3. Implementar diseño de vistas `03`, `04`, `05` (únicamente campos reales) y una pantalla de acceso de demostración segura adecuada a la autenticación existente.
4. Pruebas visuales/manuales, build TypeScript y regresión backend.

**Fase B — cuando feature 002 del original esté aprobada y desarrollada:**
5. Adaptar vistas `06`, `07`, `08`, `09` únicamente a los contratos disponibles.
6. Comprobar permisos por dependencia, paginación y límites de datos.
7. Validar el flujo estudiante → petición → bandeja.

**Fase C — nuevos alcances previamente aprobados:**
8. Login convencional, elegibilidad por ciclo, carga/descarga de documentos, atención de peticiones, notificaciones, historial extendido y etapas de sustentación/cierre.

No borrar solicitudes antiguas para “limpiar la demo”; mostrar expediente principal e historial de forma diferenciada.

## 7. Prompt para GPT Astra cuando toque implementar

> Retomaremos el **proyecto original** `C:\Users\Juaaaaan\sgt-siaaf`. Antes de escribir código, inspecciona su arquitectura, contratos, especificaciones y tareas. Te adjunto las 9 vistas de `SGT_SIAAF_Vistas_Titulacion_v2.zip` y esta guía. Úsalas como referencias de diseño, NO como nuevas reglas de negocio. Propón un plan para implementar únicamente las vistas del estudiante compatibles con feature 001: dashboard centrado en expediente, creación de solicitud y detalle de requisitos. Conserva JWT y permisos existentes, los tipos y estados exactos del contrato, ETag/If-Match y el aislamiento del proyecto original. No copies la demo, no agregues la feature 002 al original, no hagas migraciones ni modifiques backend sin autorización, no borres datos, no hagas commits/staging. Clasifica cada elemento de las imágenes como realizable con la API actual, visual sin backend nuevo, o fuera de alcance. Detente tras presentar plan, archivos previstos y pruebas antes de implementar.

## 8. Referencia de entrega

Archivos `01` a `09`: imágenes PNG 1448×1086 creadas como maquetas y no como interfaces funcionales.  
`00_vistas_miniaturas.jpg`: mosaico de referencia.  
Esta guía Markdown: especificación de traspaso de diseño y prevención de ampliaciones no autorizadas.
