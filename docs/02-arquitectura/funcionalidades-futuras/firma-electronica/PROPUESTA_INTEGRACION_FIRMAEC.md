---
title: "FirmaEC — Propuesta de integración"
---

# Propuesta de integración de FirmaEC

**Estado: PROPUESTA / DIFERIDA. No implementada.**

## 1. Objetivo de la propuesta

Reemplazar, en una fase futura no autorizada todavía, la simulación actual
de firma (carga manual de un PDF ya firmado, DEC-04) por una integración
real con un servicio de firma electrónica certificada, de forma que cada
documento que hoy requiere firma autógrafa o "firma electrónica externa
simulada" pueda firmarse electrónicamente dentro del flujo de SGT-SIAAF,
con validez jurídica conforme a la normativa ecuatoriana vigente (ver
`REQUISITOS_INSTITUCIONALES.md`).

## 2. Modalidad prevista

**Integrada a SGT-SIAAF**, no una redirección externa completa: el
funcionario inicia y sigue el proceso de firma desde la interfaz de
SGT-SIAAF, pero la operación criptográfica de firma la realiza siempre
el servicio externo de firma electrónica (FirmaEC o el proveedor de
certificación que la UNL tenga habilitado — **a confirmar**, ver
`PENDIENTES_VALIDACION_UNL.md`). SGT-SIAAF nunca ejecuta la operación
criptográfica de firma por sí mismo.

## 3. Principios no negociables de esta propuesta

1. **Firma individual por certificado propio.** Cada funcionario firma
   con su propio certificado electrónico personal; SGT-SIAAF no posee,
   no comparte ni sustituye certificados entre funcionarios.
2. **Cero custodia de secretos de terceros.** SGT-SIAAF **no almacena**
   claves privadas, contraseñas de firma, PIN, ni certificados personales
   de ningún funcionario, en ningún momento del flujo, ni en tránsito ni
   en reposo. El detalle de esta restricción está en
   `SEGURIDAD_Y_PROTECCION_CLAVES.md`.
3. **Dos orígenes documentales contemplados:**
   - Documentos **generados por SGT-SIAAF** (p. ej. Providencia 590,
     Memorando 162) que hoy se producen con ReportLab y quedan pendientes
     de firma.
   - Documentos **externos cargados por el funcionario** (p. ej. un PDF
     ya preparado fuera del sistema) que requieren firma dentro del
     mismo flujo de trazabilidad.
4. **Firmas secuenciales cuando corresponda.** Algunos documentos
   requieren más de un firmante en un orden determinado (p. ej. informe
   técnico + visto bueno + resolución). La propuesta contempla una
   secuencia de firmantes configurable por tipo de documento, no solo
   firma única.
5. **Arquitectura desacoplada.** La integración se diseña como un
   adaptador intercambiable (ver `ARQUITECTURA_PROPUESTA.md`), de modo
   que el dominio de negocio (expedientes, resoluciones) no conozca
   detalles del proveedor de firma. Esto permite simular en pruebas y
   sustituir el proveedor sin tocar reglas de negocio, siguiendo el
   mismo patrón ya usado para la integración simulada con el SGA/SIAAF
   (`core/adapters/mock_sga.py`).
6. **Conservación documental completa.** Se conserva el documento
   original sin firmar, cada versión firmada, y la metadata de
   verificación (hash SHA-256, sello de tiempo si el proveedor lo
   entrega, identidad del firmante). Detalle en
   `SEGURIDAD_Y_PROTECCION_CLAVES.md`.

## 4. Qué queda explícitamente fuera de esta propuesta

- No se propone que SGT-SIAAF emita certificados, sea una entidad de
  certificación, ni gestione el ciclo de vida de certificados de los
  funcionarios (eso es responsabilidad del proveedor de certificación y
  del propio funcionario).
- No se propone ninguna firma "en nombre de" un funcionario sin su
  intervención directa (sin automatización de firma por lotes sin
  presencia del firmante).
- No se propone modificar el flujo actual de DEC-04 mientras esta
  propuesta no esté aprobada: el sistema seguirá operando con carga
  manual de PDF firmado hasta que se autorice lo contrario.
- No se asume que la UNL ya tiene una modalidad de FirmaEC contratada,
  ni qué modalidad (API REST, SOAP, portal web con redirección, token
  criptográfico físico, firma en la nube) estaría disponible — eso debe
  confirmarse (`PENDIENTES_VALIDACION_UNL.md`).

## 5. Relación con el estado actual del código

| Aspecto | Estado actual (real) | Propuesta futura |
|---|---|---|
| Memorando 162 (`DeclaratoriaAptitud`) | `archivo_memorando_firmado_path`: el Decano carga un PDF ya firmado externamente (multipart, sin validación de firma criptográfica real) | El sistema orquesta la firma del PDF generado, sin requerir carga manual previa |
| Providencia 590 (`InformeAptitud`) | Generado por ReportLab, sin firma | Podría incorporarse al flujo de firma si la institución lo requiere |
| Documentos externos (`DocumentoEntregado`) | Cargados por estudiante/secretaría, validados por MIME/hash, sin firma | Fuera del alcance típico de firma de resoluciones, pero el adaptador podría reutilizarse si se requiere firmar certificados u otros documentos de respaldo |
| Integración con proveedor de firma | Ninguna (simulada, DEC-04) | Adaptador desacoplado (ver `ARQUITECTURA_PROPUESTA.md`) |
