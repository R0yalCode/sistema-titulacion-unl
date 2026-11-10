---
title: "FirmaEC — Seguridad y protección de claves"
---

# Seguridad y protección de claves

**Estado: PROPUESTA / DIFERIDA. No implementada.**

## 1. Principio central: SGT-SIAAF no custodia secretos de terceros

SGT-SIAAF **no almacenará, en ningún momento, bajo ninguna circunstancia**:

- Claves privadas de ningún funcionario.
- Contraseñas, PIN, o frases de acceso a certificados.
- Certificados personales (archivo `.p12`/`.pfx` o equivalente) de ningún
  funcionario.
- Ningún material criptográfico que permita firmar en nombre de un
  funcionario sin su participación directa en el momento de la firma.

La operación criptográfica de firma ocurre siempre fuera de SGT-SIAAF,
en el proveedor de firma electrónica (FirmaEC o el que la UNL confirme).
SGT-SIAAF actúa como orquestador del flujo (quién debe firmar, en qué
orden, sobre qué documento), nunca como ejecutor de la firma.

Esto es consistente con la separación de secretos ya aplicada en el
backend actual (SEC-T004: `JWT_SIGNING_KEY` separada de `SECRET_KEY`,
ninguna de las dos relacionada con certificados de firma de terceros) —
el mismo principio de "cada secreto pertenece a quien lo necesita, y el
sistema solo guarda lo mínimo indispensable" se extiende aquí a "el
sistema no guarda en absoluto el secreto de un tercero".

## 2. Qué SÍ conservaría el sistema

| Dato | Propósito | Precedente en el código actual |
|---|---|---|
| Documento original sin firmar | Trazabilidad, posibilidad de verificar qué se envió a firmar | Mismo patrón que el archivo original en `DocumentoEntregado` |
| Cada versión firmada del documento | Historial completo, no solo la última firma | Mismo patrón que versiones (`version`, `es_vigente`) de `DocumentoEntregado` |
| Hash SHA-256 del documento antes y después de cada firma | Permite verificar integridad y detectar alteraciones | Campo `hash_sha256` ya existente en `DocumentoEntregado` |
| Metadata de verificación devuelta por el proveedor (si la hay): sello de tiempo, identificador de transacción de firma, algoritmo usado | Permite auditar y, si es necesario, volver a validar la firma ante el proveedor o un tercero | Nuevo, propuesto |
| Identidad del firmante (usuario de SGT-SIAAF, no su certificado) y marca de tiempo de cada paso | Trazabilidad de quién firmó qué y cuándo | Mismo patrón que `EventoAuditoria` |

**Lo que el sistema conserva es evidencia de que la firma ocurrió y de
que el documento no fue alterado después — nunca el medio para producir
esa firma.**

## 3. Validación criptográfica

La propuesta contempla que, al recibir un documento firmado del
proveedor, el sistema:

1. Verifique que el hash del documento recibido corresponde al documento
   que se envió a firmar (o documente explícitamente si cambió, por
   ejemplo porque el proveedor incrustó la firma dentro del propio PDF).
2. Si el proveedor expone un mecanismo de verificación de la firma
   (p. ej. validación contra la cadena de confianza de la entidad
   certificadora), se invoque ese mecanismo y se registre el resultado.
   El mecanismo exacto depende de la modalidad real de FirmaEC, que no
   está confirmada (`PENDIENTES_VALIDACION_UNL.md`) — este documento no
   inventa un protocolo de verificación específico.
3. No se considere un documento "válidamente firmado" dentro de
   SGT-SIAAF hasta que esta verificación (o su equivalente confirmado
   institucionalmente) sea exitosa.

## 4. Trazabilidad de auditoría

Toda la actividad del flujo de firma (solicitud creada, firmante
notificado, firma completada, firma rechazada, verificación realizada)
se propone registrar en el mecanismo de auditoría **ya existente**
(`EventoAuditoria`, bitácora inmutable JSONB), con captura de IP real del
actor cuando aplique, siguiendo el mismo patrón que SEC-T005 estableció
para el resto del sistema (middleware thread-local + `TRUSTED_PROXIES`,
cuando `SEC-T001`/`SEC-T005` estén implementadas). No se propone un
sistema de auditoría paralelo.

## 5. Superficie de riesgo reconocida (a resolver si esta propuesta avanza)

- **Suplantación de firmante**: debe garantizarse, antes de iniciar una
  solicitud de firma, que el usuario autenticado en SGT-SIAAF es la misma
  persona que posee el certificado con el que firmará — este amarre
  depende del mecanismo real del proveedor y no está resuelto aquí.
- **Disponibilidad del proveedor**: un documento "en proceso de firma"
  que queda indefinidamente pendiente por una caída del proveedor externo
  necesita una política de expiración/reintento — no definida en esta
  propuesta (ver `PENDIENTES_VALIDACION_UNL.md`).
- **Protección de datos personales del firmante**: la identidad y
  metadata de firma de un funcionario es un dato personal sujeto a la
  normativa ecuatoriana de protección de datos (ver
  `REQUISITOS_INSTITUCIONALES.md`, RI-06) — su tratamiento debe revisarse
  con la institución antes de implementar.
