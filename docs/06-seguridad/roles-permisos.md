---
title: "Seguridad — Roles y permisos"
---

# Matriz de roles y permisos

Fuente: `RBAC_MATRIX` (código) == literal 6.2 de `specs/001/specify.md` (verificado por prueba automatizada).

| Recurso × Método | EST | SEC.CARR | SEC.ABOG | ANALISTA | DECANO | DIR.CARR | RESP.DEP | ADMIN |
|---|---|---|---|---|---|---|---|---|
| auth/token POST | público | público | público | público | público | público | público | público |
| expedientes POST | allow | — | — | — | — | — | — | allow |
| expedientes GET | own | carrera | facultad | facultad | facultad | carrera | — | allow |
| expedientes:enviar POST | own | — | — | — | — | — | — | — |
| peticiones POST | own | — | — | — | — | — | — | allow |
| peticiones:documento POST/GET | own | asignado* | asignado | asignado | — | asignado* | — | allow |
| checklist GET | — | — | facultad | facultad | — | — | — | allow |
| checklist PUT/PATCH | — | — | allow | borrador | — | — | — | allow |
| checklist POST (subsanar) | own | carrera | — | — | — | — | — | allow |
| expedientes:observar POST | — | — | allow | — | — | — | — | — |
| informes POST | — | — | allow | borrador | — | — | — | — |
| declaratorias POST/PUT/PATCH | — | — | — | — | allow | — | — | — |
| catalogos:requisitos POST/PUT | — | — | — | — | — | — | — | allow |
| notificaciones GET/PATCH | own | carrera | facultad | facultad | facultad | carrera | — | allow |

`*` En la descarga de documentos el scope `asignado` permite a la dependencia emisora acceder a las peticiones dirigidas a su rol. `—` = celda vacía = **denegado**.

## Notas

- `peticiones:documento` GET también concede `carrera` a SECRETARIA_CARRERA y `facultad` a juristas según la implementación de `_validar_ambito_descarga` (replica la matriz con soporte adicional `asignado`).
- La celda `catalogos:requisitos` no tiene endpoint aún (preparación futura).
- El Administrador tiene `allow` en todo recurso declarado, pero **no** omite el filtro de propiedad en notificaciones (siempre `own` en la práctica).
