---
title: "FirmaEC — Flujo de firma de documentos"
---

# Flujo de firma de documentos (propuesto)

**Estado: PROPUESTA / DIFERIDA. No implementada.** Los flujos descritos
son conceptuales. No corresponden a ningún endpoint, vista ni servicio
existente.

## 1. Dos orígenes documentales contemplados

### A. Documento generado por SGT-SIAAF

Ejemplo: Providencia 590, Memorando 162 — hoy generados por ReportLab
dentro del sistema, sin firma.

```
1. El sistema genera el PDF (igual que hoy).
2. El sistema calcula el hash SHA-256 del PDF original (igual que ya
   hace DocumentoEntregado para otros documentos).
3. El sistema crea una SolicitudFirma asociada al documento, con la
   lista de firmantes requeridos (uno o varios, ver §3).
4. Para cada firmante, el adaptador de FirmaEC (puerto, §ARQUITECTURA)
   inicia el proceso de firma — el mecanismo exacto depende de la
   modalidad real que se confirme con la UNL (ver PENDIENTES_VALIDACION_UNL.md):
   puede ser una redirección del funcionario a un portal de firma, una
   notificación con enlace, u otro mecanismo del proveedor.
5. El funcionario firma usando su propio certificado, fuera del control
   de SGT-SIAAF (ver SEGURIDAD_Y_PROTECCION_CLAVES.md).
6. El proveedor devuelve (o SGT-SIAAF consulta) el documento firmado y,
   si está disponible, metadata de verificación.
7. El sistema calcula el hash SHA-256 del documento firmado, lo compara
   contra el original para registrar la relación entre ambos, y persiste
   ambas versiones (ver conservación documental, SEGURIDAD_Y_PROTECCION_CLAVES.md).
8. El sistema registra un evento de auditoría (reutilizando EventoAuditoria).
9. Si hay más firmantes pendientes en la secuencia, se repite desde el
   paso 4 con el siguiente firmante; si no, el documento queda FIRMADO.
```

### B. Documento externo cargado por el funcionario

Ejemplo: un documento de respaldo que el funcionario ya tiene y necesita
incorporar firmado al expediente, sin que SGT-SIAAF lo haya generado.

```
1. El funcionario carga el documento (reutilizando validación MIME/hash
   ya existente para cargas, igual que DocumentoEntregado).
2. El sistema calcula el hash SHA-256 del documento cargado.
3. A partir de aquí, el flujo es idéntico al de un documento generado
   por el sistema (pasos 3-9 de la sección A): se crea la SolicitudFirma,
   se gestionan los firmantes, se conservan las versiones.
```

**Nota:** si el documento ya viene firmado externamente al cargarse (el
caso actual real, DEC-04), no hay "solicitud de firma" que gestionar —
ese es precisamente el comportamiento simulado vigente hoy, que esta
propuesta busca complementar (no reemplazar de inmediato) cuando se
requiera firma dentro del flujo.

## 2. Firmas secuenciales

Algunos actos administrativos requieren más de un firmante en un orden
específico (p. ej.: primero el funcionario que elabora, luego quien
avala, luego quien resuelve). La propuesta contempla:

- Una lista ordenada de firmantes por tipo de documento (configurable,
  no hardcodeada), cada uno asociado a un rol existente en `RBAC_MATRIX`
  (no se propone un sistema de roles paralelo).
- El documento no se considera `FIRMADO` hasta que el último firmante de
  la secuencia complete su firma.
- Si un firmante rechaza o la solicitud expira, la secuencia se detiene
  y el documento queda en estado `RECHAZADO`/`EXPIRADO`, sin avanzar a
  los firmantes siguientes.
- El firmante "actual" en la secuencia es el único notificado en cada
  momento (evita notificar a todos simultáneamente cuando el orden
  importa).

## 3. Qué pasa si el proveedor de firma no está disponible

No se asume ningún comportamiento de contingencia específico todavía —
esto depende del mecanismo real que confirme la UNL (reintentos,
colas, ventanas de disponibilidad). Se deja como punto abierto en
`PENDIENTES_VALIDACION_UNL.md`.

## 4. Relación con los estados de expediente existentes

Esta propuesta no modifica la máquina de estados del expediente
(`BORRADOR`, `ENVIADO`, `OBSERVADA`, `INFORME_EMITIDO`, `DECLARADA_APTA`,
etc.). La firma de un documento sería un sub-proceso dentro de las
transiciones que ya producen ese documento (emisión de informe,
declaratoria), no un estado nuevo del expediente en sí. El diseño
detallado de esa relación queda pendiente de un análisis específico si
esta propuesta avanza.
