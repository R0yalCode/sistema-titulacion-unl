---
title: "FirmaEC — Arquitectura propuesta"
---

# Arquitectura propuesta

**Estado: PROPUESTA / DIFERIDA. No implementada.** Ningún archivo, clase,
modelo ni migración descrito aquí existe en el código. Se describe en
términos conceptuales para discusión, siguiendo los patrones ya existentes
en el backend (arquitectura hexagonal por módulo: `domain/`, `ports/`,
`adapters/`, `services/`), documentada en
`docs/adr/0001-arquitectura-hexagonal-monolito-modular.md`.

## 1. Principio rector: adaptador desacoplado

El precedente directo en este código es `core/adapters/mock_sga.py`: una
integración externa (SGA/SIAAF) implementada como adaptador sustituible,
sin que el dominio de negocio conozca si la fuente es real o simulada.

La propuesta es replicar exactamente ese patrón para FirmaEC:

```
core/
├── ports/
│   └── firma_electronica.py      # Interfaz (puerto): lo que el dominio necesita
├── adapters/
│   ├── firma_ec_mock.py          # Adaptador simulado (para pruebas/desarrollo)
│   └── firma_ec_real.py          # Adaptador real (futuro, solo si se autoriza e implementa)
```

El **puerto** define el contrato mínimo que el dominio necesita (p. ej.
"solicitar firma de un documento a un firmante", "consultar estado de una
solicitud de firma", "verificar la validez criptográfica de un documento
ya firmado"), sin acoplarse a ningún detalle de FirmaEC. El **adaptador
real** sería el único punto del sistema que hablaría con el proveedor de
firma externo; el **adaptador simulado** permitiría continuar probando el
flujo de negocio sin depender de un servicio externo, igual que hoy ocurre
con `mock_sga.py`.

## 2. Por qué este patrón y no otro

- Es coherente con la arquitectura ya auditada y aceptada del proyecto
  (`docs/adr/0001-arquitectura-hexagonal-monolito-modular.md`).
- Permite que el dominio (reglas de negocio de expedientes/resoluciones)
  no dependa de si la UNL finalmente usa FirmaEC, otro proveedor, u otra
  modalidad — solo depende del puerto.
- Permite diferir la decisión de "qué proveedor real" sin bloquear el
  diseño del resto del sistema.
- Es consistente con cómo el proyecto ya documenta su propia frontera de
  integraciones externas simuladas (`docs/02-arquitectura/c4/contexto.md`).

## 3. Entidades conceptuales nuevas (propuestas, no modeladas todavía)

Estas entidades son una propuesta de modelado conceptual, no un diseño de
base de datos definitivo ni una migración:

| Entidad conceptual | Propósito |
|---|---|
| `SolicitudFirma` | Representa el pedido de firma de un documento concreto (generado por SGT-SIAAF o cargado externamente), con su estado (`PENDIENTE`, `EN_PROCESO`, `FIRMADO`, `RECHAZADO`, `EXPIRADO`). |
| `FirmanteAsignado` | Relaciona una `SolicitudFirma` con un funcionario y su posición en la secuencia de firma (si aplica orden), sin almacenar ningún dato de su certificado o clave. |
| `VersionDocumentoFirmado` | Registra cada versión firmada del documento: hash SHA-256 del documento antes y después de firmar, referencia al archivo resultante, metadata devuelta por el proveedor (si la hay), y referencia al evento de auditoría correspondiente. |

Estas entidades, si se implementan, deberían seguir el mismo patrón ya
usado por `DocumentoEntregado` (hash SHA-256, versión, `es_vigente`) y por
`EventoAuditoria` (bitácora inmutable JSONB) — reutilizando el mecanismo
de auditoría existente en vez de crear uno paralelo.

## 4. Dónde se integraría (puntos de extensión, no cambios actuales)

| Punto de extensión | Módulo actual relacionado | Cambio propuesto (futuro) |
|---|---|---|
| Emisión de Memorando 162 | `apps.resoluciones` (`DeclaratoriaAptitud`) | En vez de requerir carga manual del PDF firmado, el servicio podría generar el PDF y disparar una `SolicitudFirma` |
| Emisión de Providencia 590 | `apps.resoluciones` (`InformeAptitud`) | Opcionalmente incorporable a firma, si la institución lo requiere |
| Auditoría | `apps.notificaciones` (`EventoAuditoria`) | Nuevas acciones de auditoría (`FIRMA_SOLICITADA`, `FIRMA_COMPLETADA`, `FIRMA_RECHAZADA`) reutilizando el modelo existente, sin crear una bitácora paralela |
| Notificaciones | `apps.notificaciones` | Notificar al siguiente firmante en una secuencia, reutilizando el mecanismo de notificación ya existente |

## 5. Qué NO cambia en esta propuesta

- No se propone modificar `core/ports/` ni `core/adapters/` ahora. Las
  rutas de archivo anteriores son ilustrativas de dónde **iría** el
  código si se autoriza, no una instrucción de creación.
- No se propone ningún cambio al modelo `EventoAuditoria` más allá de
  añadir nuevos valores a su enumeración de acciones (`Accion`), en el
  futuro y bajo autorización explícita.
- No se propone almacenamiento de claves/certificados en ninguna entidad
  (ver `SEGURIDAD_Y_PROTECCION_CLAVES.md`).
