---
title: "FirmaEC — Contratos API propuestos"
---

# Contratos API propuestos

**Estado: PROPUESTA / DIFERIDA. No implementada.** Ninguno de los
endpoints de esta sección existe en `backend/openapi.yaml` ni en el
código. Se diferencian explícitamente tres capas para evitar cualquier
confusión entre lo que ya existe, lo que se propone, y lo que pertenece a
un tercero.

## 1. Endpoints EXISTENTES de SGT-SIAAF (sin cambios, solo referencia)

Estos endpoints ya existen hoy, implementan el flujo simulado de DEC-04,
y **esta propuesta no los modifica**:

| Método | Ruta | Comportamiento actual |
|---|---|---|
| POST | `/api/v1/informes/` | Emite Providencia 590 (PDF generado, sin firma) |
| POST | `/api/v1/declaratorias/` | Registra Memorando 162 con PDF **ya firmado externamente**, cargado manualmente (multipart) |

## 2. Endpoints PROPUESTOS de SGT-SIAAF (NO implementados, solo diseño conceptual)

Estos endpoints **no existen**. Se proponen únicamente como forma de
ilustrar qué necesitaría el flujo descrito en `FLUJO_FIRMA_DOCUMENTOS.md`.
Cualquier similitud en nombres con convenciones REST existentes es
intencional (consistencia), no una implementación real.

| Método | Ruta propuesta | Propósito propuesto |
|---|---|---|
| POST | `/api/v1/firmas/solicitudes/` | Crear una solicitud de firma sobre un documento (generado o cargado), con la lista ordenada de firmantes |
| GET | `/api/v1/firmas/solicitudes/{id}/` | Consultar el estado de una solicitud de firma y su historial de firmantes |
| POST | `/api/v1/firmas/solicitudes/{id}/notificar-siguiente/` | Disparar la notificación al siguiente firmante en la secuencia (uso interno del sistema, no necesariamente expuesto al usuario final) |
| GET | `/api/v1/firmas/solicitudes/{id}/documento-original/` | Descargar el documento original sin firmar (mismo patrón de descarga autenticada que ya usan `peticiones` y la futura `declaratorias`) |
| GET | `/api/v1/firmas/solicitudes/{id}/documento-firmado/` | Descargar la última versión firmada disponible |

**Explícitamente no se propone** ningún endpoint que reciba o transmita
claves privadas, contraseñas de certificado, o archivos de certificado —
ese tipo de dato nunca transita por la API de SGT-SIAAF (ver
`SEGURIDAD_Y_PROTECCION_CLAVES.md`).

## 3. Interfaces OFICIALES de FirmaEC (externas, no controladas por SGT-SIAAF)

**No se documentan aquí contratos técnicos específicos de FirmaEC**
(endpoints, formatos de petición/respuesta, protocolos de autenticación
del proveedor) porque:

- No se ha confirmado qué modalidad de FirmaEC (si alguna) tiene
  disponible la UNL.
- Documentar un contrato técnico de un servicio externo sin verificación
  directa contra su documentación oficial vigente arriesgaría introducir
  información incorrecta o desactualizada en este repositorio.
- La integración exacta (SDK, API REST, redirección web, otro mecanismo)
  depende de lo que la UNL y el proveedor confirmen.

Cuando (y si) la UNL confirme la modalidad real disponible, este
documento debe actualizarse con una referencia a la documentación
oficial vigente del proveedor (enlace o documento institucional), nunca
reconstruyendo el contrato de memoria.

## 4. Separación de responsabilidades (resumen)

```
┌─────────────────────────┐      ┌───────────────────────────┐      ┌────────────────────┐
│  SGT-SIAAF (existente)   │      │  SGT-SIAAF (propuesto,      │      │  FirmaEC / proveedor │
│  informes/, declaratorias│ ───► │  firmas/ — NO implementado) │ ───► │  (externo, oficial,  │
│  (sin cambios)            │      │  orquesta la solicitud      │      │  contrato a confirmar)│
└─────────────────────────┘      └───────────────────────────┘      └────────────────────┘
```

SGT-SIAAF nunca sustituye ni reimplementa la interfaz oficial del
proveedor; solo la consume a través de un adaptador propio (ver
`ARQUITECTURA_PROPUESTA.md`).
