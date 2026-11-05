---
title: "Módulo: core"
---

# M-07 — core (infraestructura compartida)

| Campo | Valor |
|---|---|
| Objetivo | Infraestructura transversal: aislamiento por ámbito, validación de PDF, almacenamiento privado y adaptador del SGA |
| Naturaleza | No es una app Django; es un paquete de puertos y adaptadores |

## Componentes

| Componente | Responsabilidad | Detalles |
|---|---|---|
| `adapters/scope_filter.py` | Anti-IDOR a nivel ORM | `ScopeFilterMixin.scope_queryset`: rol→ámbito (`own/carrera/facultad/all`; RESPONSABLE_DEPENDENCIA→denegado); compone `Q()` sobre `estudiante_id/carrera_id/facultad_id`; anónimo o sin predicates → `queryset.none()` |
| `adapters/pdf_validation.py` | Validación de PDFs | ≤10 MB (`file_too_large`), magic bytes `%PDF-` reales (`invalid_magic_bytes`), hash SHA-256 en streaming; devuelve `{tamanio_bytes, hash_sha256, tipo_mime}` |
| `adapters/local_storage.py` | Almacenamiento privado | `PrivateMediaStorage` sobre `MEDIA_ROOT/private` (o `PRIVATE_MEDIA_ROOT`); `url()` prohibido (NotImplementedError); rutas `expedientes/{año}/{id}/{timestamp}_{nombre}`; guardar/obtener/eliminar |
| `adapters/mock_sga.py` + `ports/` | Puerto del SGA | `ISGALegacyPort`; dataclasses frozen (promedio inmutable, RN-005); `MockSGAAdapter` con fixture JSON de 5 récords, búsqueda por cédula, caché perezosa, sin conexiones reales |

## Reglas de uso

- Las apps de negocio consumen `core` pero `core` nunca importa de las apps (dependencia unidireccional).
- Toda vista que exponga objetos por dueño/carrera/facultad debe usar `ScopeFilterMixin` + `get_object_or_404(self.get_queryset())`.

## Pruebas (71)

Validación PDF (24), mock SGA (25), contrato del puerto e inmutabilidad (22). **Nota**: `core/tests` y `core/adapters/tests` están fuera de `testpaths` de pytest (AUD-P1-04) y deben ejecutarse explícitamente.

## Estado

**Implementado y verificado.** Limitación: `PRIVATE_MEDIA_ROOT` no declarado en settings (fallback implícito, AUD-P2-05).
