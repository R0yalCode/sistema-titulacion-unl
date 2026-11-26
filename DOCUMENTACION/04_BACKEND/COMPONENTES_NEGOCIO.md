---
title: "Componentes de negocio"
---

# Componentes de negocio — Backend SGT-SIAAF

**Fuente:** lectura directa de las firmas de función, clases de excepción y docstrings de los 11 archivos de servicio reales en `backend/src/apps/*/services/`. Cada componente corresponde a un caso de uso de `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §9–10 (HU/RF), citado explícitamente.

## 1. `crear_expediente` (expedientes)

- **Objetivo:** iniciar el trámite de aptitud legal (RF-001, HU-001).
- **Entradas:** `estudiante` (usuario autenticado), `carrera_id`.
- **Procesamiento:** valida ausencia de expediente activo (bloqueo pesimista `select_for_update()`), genera número de expediente correlativo, crea `ExpedienteTitulacion` en `BORRADOR`, inicializa 5 `PeticionDocumental` vía `bulk_create` desde el catálogo (`CatalogoDocumental`).
- **Salidas:** `ExpedienteTitulacion` creado.
- **Persistencia:** `ExpedienteTitulacion`, `PeticionDocumental` (transacción atómica).
- **Dependencias:** `authentication` (usuario), `CatalogoDocumental`.
- **Reglas de negocio:** RN-001 (5 requisitos base).
- **Excepciones de dominio:** `ExpedienteActivoExistenteError`, `CatalogoIncompletoError`.

## 2. `enviar_expediente` (expedientes)

- **Objetivo:** formalizar el envío y arrancar el plazo reglamentario (RF-002, RF-003, HU-004).
- **Entradas:** `expediente`, `ahora` (timestamp inyectable para pruebas).
- **Procesamiento:** verifica que no existan requisitos sin documento vigente (`_requisitos_sin_documento_vigente`), genera número de providencia correlativo, cambia estado a `ENVIADA`, registra `fecha_recepcion` inmutable y calcula `fecha_limite_atencion` (vía `PlazoLaboralCalculator`, RN-002).
- **Salidas:** expediente actualizado en `ENVIADA`.
- **Persistencia:** `ExpedienteTitulacion` (transacción con `select_for_update()`).
- **Dependencias:** `PlazoLaboralCalculator` (dominio puro).
- **Reglas de negocio:** RN-002, RN-010.
- **Excepciones de dominio:** `EstadoInvalidoError`, `RequisitosIncompletosError`.

## 3. `solicitar_emision` (peticiones)

- **Objetivo:** pedir un certificado a la dependencia emisora sin correo (RF-004, HU-002).
- **Procesamiento:** cambia estado de la petición a `SOLICITADO`, genera `NotificacionInterna` a la dependencia correspondiente.
- **Persistencia:** `PeticionDocumental`, `NotificacionInterna`.
- **Reglas de negocio:** RN-001.

## 4. `cargar_documento` (peticiones)

- **Objetivo:** adjuntar/versionar un PDF de certificado (RF-005, HU-003, y también usado por la subsanación RF-008).
- **Procesamiento:** valida el archivo (magic bytes `%PDF-`, tamaño ≤10 MB, hash SHA-256) vía `core/adapters/pdf_validation.py`, persiste el archivo en almacenamiento privado, crea `DocumentoEntregado` con versión incremental.
- **Persistencia:** `DocumentoEntregado`.
- **Dependencias:** `core.adapters.pdf_validation`, `core.adapters.local_storage`.
- **Reglas de negocio:** RN-009 (límite estricto de carga).

## 5. `evaluar_checklist` (verificacion)

- **Objetivo:** el jurista marca un requisito `VERIFICADO` u `OBSERVADO` (RF-006, HU-006).
- **Entradas:** `usuario`, `checklist_verification_id`, `nuevo_estado`, `motivo_observacion` (opcional).
- **Procesamiento:** valida transición de estado permitida, valida autorización del usuario, actualiza `ChecklistVerification` con bloqueo pesimista.
- **Persistencia:** `ChecklistVerification`.
- **Excepciones de dominio:** `ChecklistVerificationNotFoundError`, `InvalidVerificationStateError`, `VerificationAlreadyCompletedError`, `ExpedienteNotInVerificationError`, `UserNotAuthorizedError`.

## 6. `registrar_observacion` (verificacion)

- **Objetivo:** bloquear un requisito con un motivo accionable (RF-007, HU-007, RN-003).
- **Entradas:** `usuario`, `expediente_id`, `peticion_id`, `motivo_observacion`.
- **Procesamiento:** valida que el expediente esté en verificación, crea `ObservacionAccionable`, cambia la petición a `OBSERVADO` y el expediente a `OBSERVADA`.
- **Persistencia:** `ObservacionAccionable`, `PeticionDocumental`, `ExpedienteTitulacion`.
- **Excepciones de dominio:** `ObservacionYaExisteError`, `ExpedienteNoEnVerificacionError`, `PeticionNoEncontradaError`, `UsuarioNoAutorizadoError`.

## 7. `subsanar_requisito` (verificacion)

- **Objetivo:** el estudiante corrige un documento observado (RF-008, HU-008, RN-011).
- **Entradas:** `usuario`, `checklist_verification_id`, `archivo`, `nombre_original`.
- **Procesamiento:** valida el PDF, incrementa versión, marca la observación como resuelta, retorna el expediente a `EN_VERIFICACION`.
- **Persistencia:** `DocumentoEntregado`, `ObservacionAccionable`, `ExpedienteTitulacion`.
- **Excepciones de dominio:** `SubsanacionNoPermitidaError`, `PeticionNoEncontradaError`, `ObservacionNoEncontradaError`, `UsuarioNoAutorizadoError`, `ValidacionPDFError`.

## 8. `validar_checklist_completo` (verificacion)

- **Objetivo:** verificar que el 100 % de los requisitos estén `VERIFICADO` antes de emitir el informe (RN-003, EX-007) — es un servicio de soporte llamado por `emitir_informe`.
- **Excepciones de dominio:** `ChecklistIncompletoError`.

## 9. `emitir_informe` (resoluciones)

- **Objetivo:** generar e inmutabilizar el informe legal (RF-009, RF-010, HU-009).
- **Entradas:** `usuario`, `expediente_id`, `dictamen` (default `"APTO"`), `fundamentacion`.
- **Procesamiento:** invoca `validar_checklist_completo`, genera el PDF (ReportLab), crea `InformeAptitud`, cambia expediente a `INFORME_EMITIDO`.
- **Persistencia:** `InformeAptitud`, `ExpedienteTitulacion`.
- **Reglas de negocio:** RN-003, RN-004.
- **Excepciones de dominio:** `InformeYaExisteError`, `ExpedienteNoValidoParaInformeError`, `UsuarioNoAutorizadoError`.
- **Hallazgo heredado de Fase 1 (`HISTORIAS_Y_CASOS_DE_USO.md`):** `docs/auditoria/matriz-trazabilidad.md` señala un bug de trazabilidad N-1 en este servicio (`estado_anterior` registrado incorrectamente en `HistorialEstado`); no se verificó contra el código en esta pasada (pendiente para Fase 7, al re-ejecutar pruebas).

## 10. `declarar_aptitud` (resoluciones)

- **Objetivo:** el Decano/a registra la declaratoria con el memorando firmado (RF-011, HU-010, RN-004).
- **Entradas:** `usuario`, `expediente_id`, `archivo_memorando`, `numero_memorando` (opcional, sobreescritura manual — DEC-03).
- **Procesamiento:** valida el PDF, **persiste el archivo mediante `guardar_archivo_privado`** (confirmado en Fase 0 — corrige el hallazgo H-01 de `auditoria/01`, que señalaba que este paso no se ejecutaba), crea `DeclaratoriaAptitud`, cambia expediente a `DECLARADA_APTA`.
- **Persistencia:** `DeclaratoriaAptitud`, `ExpedienteTitulacion`.
- **Excepciones de dominio:** `DeclaratoriaYaExisteError`, `ExpedienteNoValidoParaDeclaratoriaError`, `UsuarioNoAutorizadoError`, `PDFInvalidoError`.

## 11. `notification_service` (notificaciones)

- **Objetivo:** despachar notificaciones internas y registrar auditoría (RF-012, RF-013).
- **Procesamiento:** reacciona a eventos de los demás servicios (en gran parte vía Django signals, acoplamiento débil — ver `ARQUITECTURA_BACKEND.md` §3), crea `NotificacionInterna` y `EventoAuditoria`.
- **Persistencia:** `NotificacionInterna`, `EventoAuditoria`.
- **Hallazgo heredado, corregido en Fase 9:** `docs/auditoria/matriz-trazabilidad.md` marca RF-013 como **IP** (parcial), no IV, citando 3 eventos de auditoría sin emitir y el campo `ip_origen` siempre vacío. Verificado contra el código: **la IP ya no está vacía** — `_crear_evento_auditoria()` en `signals.py` la obtiene de `resolver_ip_cliente()` vía el middleware thread-local, con lógica consciente de `TRUSTED_PROXIES` (ver `DOCUMENTACION/09_OBSERVABILIDAD/OBSERVABILIDAD.md` §3). El posible pendiente de "3 eventos sin emitir" no se reverificó.

## Componente transversal: `authentication` (sin `services/`)

No tiene casos de uso propios: su responsabilidad (autenticación JWT + autorización RBAC) se resuelve íntegramente en `adapters/permissions.py` (`RBAC_MATRIX`, mundo cerrado) y en la configuración de `djangorestframework-simplejwt`, consumida transversalmente por todas las vistas de las demás apps.
