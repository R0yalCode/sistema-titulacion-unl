# ADR-0010: Perfil académico detrás de un puerto, con simulación MockSGA

## Estado
Aceptado para el prototipo (2026-11-22). Revisar cuando exista integración
institucional con el SGA.

## Contexto
V-03 pedía al estudiante el UUID de su carrera y el backend lo aceptaba sin
validarlo: la carrera, que decide el ámbito de los roles de carrera, la
fijaba el cliente. No existe autorización, contrato ni credenciales para
consultar el SGA de la UNL, y el proyecto prohíbe acceder a sus bases de
datos (spec 001 §2).

## Decisión
1. La carrera y la facultad del expediente las determina el servidor a
   partir del perfil académico del usuario autenticado. El cliente no puede
   enviarlas (`POST /api/v1/expedientes/` con cuerpo vacío).
2. El perfil se obtiene mediante el puerto `FuenteAcademica` y se valida en
   `AcademicProfileService` contra un catálogo interno (`Facultad`,
   `Carrera`), donde la carrera determina la facultad.
3. Mientras no haya integración, la fuente es `MockSGAAdapter`, una
   simulación explícita: solo se activa si `ACADEMIC_PROFILE_MOCK_ALLOWED`
   lo permite (por defecto, solo en desarrollo), sus datos se marcan como
   simulados y la API lo comunica (`fuente.es_simulada`). En
   `config.settings.production` está prohibida: el permiso es la constante
   `False` y configurar `mock_sga` detiene el arranque.
4. Se expone `GET /api/v1/perfil-academico/`, solo para el propio estudiante.

## Alternativas descartadas
- Consulta en tiempo real o sincronización con el SGA: no hay servicio
  institucional verificado.
- Selector libre de carreras: el estudiante seguiría eligiendo su ámbito.
- Usar el `SGAMockAdapter` de `core` (récord académico): devuelve la carrera
  como texto, sin catálogo, y está pensado para notas.

## Consecuencias
- V-03 funciona de extremo a extremo y se puede demostrar sin inventar datos
  institucionales.
- Sustituir la simulación por un `SGAAdapter` no cambia el frontend, la
  creación del expediente, el RBAC ni el contrato.
- El catálogo de demostración (`MOCK-…`) debe reemplazarse por el oficial.
- Detalle: `docs/academico/perfil-academico-mock-sga.md`.
