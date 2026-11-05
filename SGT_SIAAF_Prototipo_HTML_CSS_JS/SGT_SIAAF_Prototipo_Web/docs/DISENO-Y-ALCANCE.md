# Diseño y alcance — SGT-SIAAF

## Alcance

Prototipo interactivo de **nueve vistas funcionales en navegador**, inspirado en el diseño conceptual de SGT-SIAAF y las referencias visuales compartidas. Su propósito es recoger opiniones del grupo. **No es el frontend conectado al backend original y no guarda información en PostgreSQL.**

## Identidad

- Nombre uniforme: **SGT-SIAAF — Sistema de Gestión del Trámite de Titulación**.
- Inspiración en colores de la Universidad Nacional de Loja: rojo de acento, verde oscuro institucional referencial, azules secundarios, fondo blanco/neutro.
- El icono SVG es **conceptual**, no es el escudo oficial UNL ni un reemplazo autorizado.
- Tipografía del sistema para evitar dependencias externas. Accesibilidad: encabezados semánticos, foco visible, mensajes con rol alert/status, responsive.

## Pantallas

1. Acceso demostrativo por perfil, sin credenciales reales.
2. Estudiante no habilitado (7.º ciclo **ilustrativo**, sin integración académica).
3. Estudiante próximo a egresar: panel de trámite.
4. Nueva solicitud de aptitud legal con selector y confirmación.
5. Mi expediente con los cinco requisitos y su estado.
6. Nueva petición documental (modal sobre el expediente).
7. Seguimiento de una petición documental.
8. Bandeja del funcionario con filtro, búsqueda y paginación local.
9. Detalle de una petición para el funcionario, de **solo lectura**.

## Lo que sí simula de forma interactiva

- Selección de estudiante próximo a egresar, estudiante no habilitado o funcionario.
- Crear expedientes ilustrativos y generar los cinco requisitos.
- Marcar un requisito como `SOLICITADO` al registrar una petición.
- Impedir duplicados para el mismo requisito en un expediente (solo lógica de la demo).
- La petición creada para Secretaría de Carrera o Prácticas se verá en bandeja de funcionario tras cambiar de perfil.
- Filtros, búsqueda local, detalles, paginación, navegación y reset.
- Datos ficticios persistidos solo en `sessionStorage` dentro de la pestaña del navegador, nunca enviados a un servidor.

## NO implementado en este paquete

- Autenticación real, JWT, consulta del noveno ciclo, APIs, PostgreSQL, permisos de Django, notificaciones, carga de PDFs, aprobación de peticiones, resolución legal, sustentación, cierre de titulación.
- La cuenta que seleccionas al entrar al prototipo no representa una identidad de servidor.
- Los textos y catálogos del mockup **no son normativa universitaria aprobada**.

## Relación con el proyecto original

- El original `C:\Users\Juaaaaan\sgt-siaaf` continuaba en la feature 001 al prepararse la maqueta.
- La feature 002 y su bandeja existían en la copia demo, pero NO deben tratarse como integradas al original.
- Para conectar a API real: reescribir adaptadores de datos manteniendo las pantallas, añadir autenticación autorizada y manejar errores 401/403/409/412/428 y ETag/If-Match; hacerlo en una fase futura planificada.
