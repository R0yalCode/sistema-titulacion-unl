# SGT-SIAAF · Kit de errores HTML/CSS/JS (UNL)

Prototipo visual independiente para presentación al equipo. Inspirado en los colores y la mascota compartida de la Universidad Nacional de Loja. **No es una implementación oficial, no modifica `sgt-siaaf` ni se conecta a Django o PostgreSQL.**

## Autorización de uso en SGT-SIAAF (2026-11-05)

El proyecto SGT-SIAAF autorizó expresamente el uso de las 5 ilustraciones de `assets/img/mascota-*.png` de este prototipo como recursos gráficos **complementarios e ilustrativos** de su identidad visual, en los estados 404, 403, 500 y 503 del frontend (`frontend/public/assets/mascotas/`), conservando los archivos originales y su trazabilidad de procedencia (ver inventario en `frontend/docs/assets-mascotas.md`).

Esta autorización **no cambia la naturaleza de las ilustraciones** descrita en la advertencia original más abajo: siguen siendo ilustraciones generadas a partir de referencias aportadas, no archivos de marca oficiales aprobados por la Universidad Nacional de Loja. En particular:

- No se interpretan ni se presentan como logotipo oficial de la UNL.
- El logo textual «unl» recreado conceptualmente **no** se utiliza en SGT-SIAAF.
- No se afirma la existencia de una licencia, derecho de autor o autorización institucional formal que no esté documentada.

## Cómo abrirlo

1. Descomprime el ZIP en cualquier carpeta.
2. Abre `index.html` en Chrome, Edge o Firefox (doble clic). No necesita Internet, Node.js, Python ni instalación de dependencias.
3. Navega entre las ocho vistas y prueba sus botones de demostración.
4. Para una presentación de todas las vistas, abre `galeria.html`. En el ZIP también se incluye `VISTA_GENERAL_MINIATURAS.png`.

## Contenido

- `paginas/404.html`: página no encontrada, oso desconcertado.
- `paginas/403.html`: acceso restringido, oso diciendo «alto».
- `paginas/500.html`: fallo interno, oso preocupado ante su computadora.
- `paginas/503.html`: servicio temporalmente no disponible, oso paciente.
- `paginas/401.html`: sesión vencida o autenticación requerida, oso con credencial.
- `paginas/acceso.html`: maqueta del inicio de sesión, accesible desde el 401; campos deshabilitados para no recoger contraseñas.
- `paginas/409.html`: alerta de conflicto dentro de formulario.
- `paginas/412.html`: alerta de información desactualizada dentro de formulario.
- `paginas/428.html`: alerta de versión requerida dentro de formulario.
- `assets/css/site.css`: diseño y adaptaciones móviles.
- `assets/js/site.js`: botones de demostración y avisos locales, sin enviar datos.
- `assets/img/`: 5 ilustraciones locales del oso + favicon.
- `capturas/`: imágenes de cada pantalla, listas para presentaciones.

## Integración futura con React + Django

- Estas páginas son **vistas visuales**; abrir archivos `.html` devuelve contenido local y **no crea respuestas HTTP 401/403/404/500/503**.
- El servidor Django debe mantener los códigos HTTP reales. React renderizará la vista correspondiente al status y al contexto, sin revelar rutas internas, SQL, tracebacks, JWT, secretos ni existencia de solicitudes ajenas.
- Para una URL inexistente, el router de React debe mostrar 404; un recurso ajeno puede conservar su 404 de privacidad. El servidor también debe configurar 404 para endpoints y enlaces incorrectos.
- Ante 401, presentar inicio de sesión según la arquitectura aprobada. No redirigir indiscriminadamente todo error 403.
- Los 409/412/428 deben aparecer dentro del formulario con recuperación contextual, preservando texto no guardado y evitando sobrescrituras. En 412/428 se necesita releer ETag/versiones desde el backend real; aquí la acción es ilustrativa.
- Los botones «Reintentar» muestran una notificación de demostración, **no realizan una llamada real**. Conectar a los servicios autorizados durante la implementación.
- Para que incluso fallos 500/503 del backend o de un reverse proxy presenten páginas amigables, configurar páginas de error en la capa que realmente responde cuando React no puede cargarse.
- No copiar automáticamente en tu proyecto original: revisar especificación, contratos, rutas reales, branding y permisos antes de integrar.

## Accesibilidad y seguridad

Idioma `es`, navegación con teclado, `focus-visible`, alertas ARIA, contraste legible y responsive. Los mensajes no incluyen direcciones de servidor o datos técnicos privados. Las imágenes de referencia son **ilustraciones generadas** a partir de referencias aportadas y no sustituyen archivos de marca oficiales aprobados. El logo textual «unl» es recreación conceptual; para producción usar los archivos autorizados por la universidad.

**Importante**: T063/T064 de feature 001, TR-001 y feature 002 no se ven modificadas por este ZIP; es exclusivamente una propuesta visual.
