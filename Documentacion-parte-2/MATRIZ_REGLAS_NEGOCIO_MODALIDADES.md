# MATRIZ DE REGLAS DE NEGOCIO: MODALIDADES DE TITULACIÓN — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `DISENO_FUNCIONAL_MODALIDADES_TITULACION.md` + `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md`  

---

## 1. REGLAS DE NEGOCIO POR CATEGORÍA

### 1.1 Reglas de Asignación Inicial (Creación Expediente)

| ID | Regla | Descripción | Validación | Actor | Momento |
|----|-------|-------------|------------|-------|---------|
| RN-MOD-CRE-01 | **TIC por defecto** | Todo expediente nuevo se crea con `opcion_titulacion = 'TIC'` | Default modelo + servicio `crear_expediente` | Sistema (automático) | `POST /expedientes/` |
| RN-MOD-CRE-02 | **EC no creable por estudiante** | `POST /expedientes/` rechaza `opcion_titulacion = 'EC'` | Servicio `crear_expediente` valida y lanza error | Estudiante (bloqueado) | `POST /expedientes/` |
| RN-MOD-CRE-03 | **Solo TIC en creación** | Payload creación solo acepta TIC (o omitido = default) | Serializer `CrearExpedienteRequest` sin campo `opcion_titulacion` | Estudiante | `POST /expedientes/` |

### 1.2 Reglas de Elegibilidad Examen Complexivo (EC)

| ID | Regla | Descripción | Validación | Actor | Momento |
|----|-------|-------------|------------|-------|---------|
| RN-MOD-ELE-01 | **2 reprobaciones obligatorias** | Estudiante debe haber reprobado 2 veces la unidad de titulación | Mock SGA: `reprobaciones_titulacion >= 2` | Secretario (verifica) | `GET /expedientes/{id}/modalidad/elegibilidad/` |
| RN-MOD-ELE-02 | **3ra matrícula efectiva** | Estudiante debe haber accedido efectivamente a tercera matrícula | Mock SGA: `tercera_matricula.activa = true` + resolución oficial | Secretario (verifica) | `GET /expedientes/{id}/modalidad/elegibilidad/` |
| RN-MOD-ELE-03 | **Evidencia documental** | Reprobaciones y matrícula deben tener documentos oficiales | `evidencia_academica` JSON con referencias | Secretario (revisa) | `POST /expedientes/{id}/modalidad/cambiar/` |
| RN-MOD-ELE-04 | **Verificación obligatoria** | No se permite cambio a EC sin elegibilidad verificada | Servicio `cambiar_modalidad` llama `verificar_elegibilidad_ec` | Sistema (bloquea) | `POST /expedientes/{id}/modalidad/cambiar/` |

### 1.3 Reglas de Cambio de Modalidad

| ID | Regla | Descripción | Validación | Actor | Momento |
|----|-------|-------------|------------|-------|---------|
| RN-MOD-CAM-01 | **Solo TIC → EC** | Cambio solo permitido de TIC a EC (no EC → TIC) | Servicio valida `modalidad_anterior = TIC` y `modalidad_nueva = EC` | Secretario/Decano | `POST /expedientes/{id}/modalidad/cambiar/` |
| RN-MOD-CAM-02 | **Autorización dual** | Requiere: Secretario verifica elegibilidad + Decano autoriza | RBAC: `SECRETARIO_ABOGADO` (GET elegibilidad) + `DECANO` (POST cambiar) | Secretario + Decano | Flujo secuencial |
| RN-MOD-CAM-03 | **Justificación obligatoria** | Campo `justificacion` requerido en request (mín 50 chars) | Serializer `CambiarModalidadRequestSerializer` | Decano | `POST /expedientes/{id}/modalidad/cambiar/` |
| RN-MOD-CAM-04 | **Evidencia académica obligatoria** | `evidencia_academica` JSON con actas reprobaciones + resolución 3ra matrícula | Serializer + servicio valida estructura | Decano | `POST /expedientes/{id}/modalidad/cambiar/` |
| RN-MOD-CAM-05 | **Estado expediente permitido** | Solo si estado ∈ {BORRADOR, ENVIADA, EN_VERIFICACION} | Servicio valida `expediente.estado` | Sistema | `POST /expedientes/{id}/modalidad/cambiar/` |
| RN-MOD-CAM-06 | **Historial inmutable** | Cada cambio registra `HistorialModalidad` inmutable | Modelo `HistorialModalidad` + `on_delete=PROTECT` | Sistema (automático) | Transacción atómica en `cambiar_modalidad` |
| RN-MOD-CAM-07 | **Un cambio por expediente** | No se permite cambiar modalidad más de una vez (TIC→EC irreversible) | Servicio valida `!expediente.historial_modalidad.exists()` | Sistema | `POST /expedientes/{id}/modalidad/cambiar/` |

### 1.4 Reglas de Protección e Integridad

| ID | Regla | Descripción | Validación | Actor | Momento |
|----|-------|-------------|------------|-------|---------|
| RN-MOD-PRO-01 | **No modificación directa** | No existe `PATCH /expedientes/{id}/` para `opcion_titulacion` | Serializer `ExpedienteUpdateSerializer` sin campo | Sistema | Cualquier update |
| RN-MOD-PRO-02 | **Endpoint dedicado** | Cambio solo vía `POST /expedientes/{id}/modalidad/cambiar/` | RBAC + servicio dedicado | Sistema | Arquitectura |
| RN-MOD-PRO-03 | **Validación server-side** | Frontend nunca decide elegibilidad; backend es autoridad | Frontend llama `GET /elegibilidad/` y muestra resultado | Backend | `GET /elegibilidad/`, `POST /cambiar/` |
| RN-MOD-PRO-04 | **Auditoría completa** | Cambio registra `EventoAuditoria` con acción `MODALIDAD_CAMBIADA` | Signal `post_save` en `HistorialModalidad` | Sistema | Automático |
| RN-MOD-PRO-05 | **Consistencia expediente** | Si expediente tiene actividades avanzadas, validar impacto | Servicio `cambiar_modalidad` revisa `checklist_verifications`, `peticiones` | Sistema | `POST /cambiar/` |

### 1.5 Reglas de Proceso Académico por Modalidad

| ID | Regla | Modalidad | Descripción | Validación |
|----|-------|-----------|-------------|------------|
| RN-MOD-PRO-ACA-01 | **Trabajo escrito** | TIC | Requiere entrega de trabajo de integración curricular (documento) | Fase 2 futura: entidad `TrabajoTitulacion` |
| RN-MOD-PRO-ACA-02 | **Defensa oral** | TIC | Requiere sustentación ante tribunal (Fase 2) | Fase 2 futura: `TribunalEvaluador` |
| RN-MOD-PRO-ACA-03 | **Examen integral** | EC | Requiere examen complexivo ante tribunal (Fase 2) | Fase 2 futura: `ExamenComplexivo` |
| RN-MOD-PRO-ACA-04 | **Acta diferenciada** | Ambas | Acta de grado distinta según modalidad | Fase 3 futura: `ActaGrado` |

---

## 2. MATRIZ DE TRANSICIONES PERMITIDAS

| Estado Actual Expediente | Modalidad Actual | Cambio Permitido | Nueva Modalidad | Requisitos Adicionales |
|--------------------------|------------------|------------------|-----------------|------------------------|
| BORRADOR | TIC | ✅ Sí | EC | Elegibilidad verificada + Autorización Decano |
| ENVIADA | TIC | ✅ Sí | EC | Elegibilidad verificada + Autorización Decano |
| EN_VERIFICACION | TIC | ✅ Sí | EC | Elegibilidad verificada + Autorización Decano + Validar impacto checklist |
| OBSERVADA | TIC | ❌ No | — | No permitido (requiere subsanar primero) |
| INFORME_EMITIDO | TIC | ❌ No | — | Proceso avanzado; cambio invalidaría informe |
| DECLARADA_APTA | TIC | ❌ No | — | Proceso culminado |
| CANCELADA | TIC | ❌ No | — | Expediente cancelado |
| CUALQUIERA | EC | ❌ No | TIC | Cambio irreversible (normativa) |

---

## 3. MATRIZ DE PERMISOS POR ACCIÓN

| Acción | Endpoint | ESTUDIANTE | SECRETARIA_CARRERA | SECRETARIO_ABOGADO | ANALISTA_APOYO | DECANO | DIRECTOR_CARRERA | RESPONSABLE_DEPENDENCIA | ADMINISTRADOR |
|--------|----------|------------|-------------------|-------------------|----------------|--------|------------------|------------------------|---------------|
| Ver modalidad actual | `GET /expedientes/{id}/modalidad/` | ✅ (own) | ❌ | ✅ (facultad) | ✅ (facultad) | ✅ (facultad) | ✅ (carrera) | ❌ | ✅ (all) |
| Ver historial modalidad | `GET /expedientes/{id}/modalidad/` | ✅ (own) | ❌ | ✅ (facultad) | ✅ (facultad) | ✅ (facultad) | ✅ (carrera) | ❌ | ✅ (all) |
| Verificar elegibilidad EC | `GET /expedientes/{id}/modalidad/elegibilidad/` | ❌ | ❌ | ✅ (facultad) | ❌ | ✅ (facultad) | ❌ | ❌ | ✅ (all) |
| Cambiar modalidad (TIC→EC) | `POST /expedientes/{id}/modalidad/cambiar/` | ❌ | ❌ | ✅ (facultad, verifica) | ❌ | ✅ (facultad, autoriza) | ❌ | ❌ | ✅ (all) |
| Consultar catálogo modalidades | `GET /modalidades/` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Nota:** `ANALISTA_APOYO` puede ver elegibilidad pero **no** verificar/autorizar (solo Secretario/Decano).

---

## 4. ESTRUCTURA DE DATOS: EVIDENCIA ACADÉMICA

```json
{
  "reprobaciones": [
    {
      "periodo": "2025-1",
      "materia_codigo": "TIT-001",
      "materia_nombre": "Titulación I",
      "nota": 4.5,
      "acta_referencia": "ACTA-2025-001"
    },
    {
      "periodo": "2025-2",
      "materia_codigo": "TIT-001",
      "materia_nombre": "Titulación I",
      "nota": 5.0,
      "acta_referencia": "ACTA-2025-045"
    }
  ],
  "tercera_matricula": {
    "activa": true,
    "resolucion": "RES-2026-00123",
    "fecha_resolucion": "2026-02-15",
    "periodo": "2026-1",
    "documento_referencia": "DOC-2026-00456"
  },
  "documentos_referencia": [
    "DOC-2025-001 (Acta primera reprobación)",
    "DOC-2025-045 (Acta segunda reprobación)",
    "DOC-2026-00456 (Resolución tercera matrícula)"
  ],
  "verificado_por": "secretario.juridico",
  "fecha_verificacion": "2026-11-09T10:30:00Z"
}
```

---

## 5. EVENTOS DE AUDITORÍA

| Acción | EventoAuditoria.accion | Detalles JSON |
|--------|------------------------|---------------|
| Verificar elegibilidad EC | `MODALIDAD_ELEGIBILIDAD_VERIFICADA` | `{expediente_id, estudiante_id, elegible, evidencia}` |
| Cambiar modalidad TIC→EC | `MODALIDAD_CAMBIADA` | `{expediente_id, modalidad_anterior: TIC, modalidad_nueva: EC, autorizado_por_id, justificacion, evidencia_academica}` |
| Intento cambio no autorizado | `MODALIDAD_CAMBIO_INTENTO_FALLIDO` | `{expediente_id, usuario_id, razon: "no_elegible|estado_invalido|sin_permisos" }` |

---

## 6. CASOS DE PRUEBA POR REGLA

| Regla | Caso de Prueba | Resultado Esperado |
|-------|----------------|---------------------|
| RN-MOD-CRE-01 | Crear expediente sin especificar modalidad | `opcion_titulacion = 'TIC'` |
| RN-MOD-CRE-02 | Crear expediente con `opcion_titulacion = 'EC'` | HTTP 400 "Modalidad Examen Complexivo no seleccionable por estudiante" |
| RN-MOD-ELE-01 | Mock SGA: 1 reprobación | `elegible = false`, mensaje "Requiere 2 reprobaciones" |
| RN-MOD-ELE-02 | Mock SGA: 2 reprobaciones pero 3ra matrícula no activa | `elegible = false`, mensaje "Requiere tercera matrícula efectiva" |
| RN-MOD-ELE-03 | Mock SGA: 2 reprobaciones + 3ra matrícula activa | `elegible = true`, evidencia completa |
| RN-MOD-CAM-01 | POST cambiar con `nueva_modalidad = 'TIC'` (desde EC) | HTTP 400 "Cambio irreversible: no se permite EC → TIC" |
| RN-MOD-CAM-02 | POST cambiar solo Secretario (sin Decano) | HTTP 403 "Requiere autorización Decano" |
| RN-MOD-CAM-03 | POST cambiar sin `justificacion` | HTTP 400 "Justificación obligatoria (mín 50 caracteres)" |
| RN-MOD-CAM-04 | POST cambiar sin `evidencia_academica` completa | HTTP 400 "Evidencia académica incompleta: requiere actas reprobaciones y resolución 3ra matrícula" |
| RN-MOD-CAM-05 | Expediente en INFORME_EMITIDO intenta cambio | HTTP 400 "No se puede cambiar modalidad en estado INFORME_EMITIDO" |
| RN-MOD-CAM-06 | Segundo intento cambio mismo expediente | HTTP 400 "La modalidad ya fue cambiada anteriormente; no se permiten múltiples cambios" |
| RN-MOD-PRO-01 | PATCH /expedientes/{id}/ con `opcion_titulacion` | Campo ignorado / HTTP 400 "Campo no actualizable" |
| RN-MOD-PRO-03 | Frontend intenta calcular elegibilidad local | No implementado; frontend llama `GET /elegibilidad/` |
| RN-MOD-PRO-04 | Cambio autorizado → EventoAuditoria `MODALIDAD_CAMBIADA` | Evento creado con detalles completos |
| RN-MOD-PRO-05 | Expediente con checklist 100% VERIFICADO cambia modalidad | Permitido pero registra advertencia en auditoría |

---

## 7. ERRORES ESTÁNDAR

| Código | Mensaje | Cuándo Ocurre |
|--------|---------|---------------|
| `MODALIDAD_NO_SELECCIONABLE` | "La modalidad Examen Complexivo no es seleccionable por el estudiante; requiere autorización excepcional." | `POST /expedientes/` con EC |
| `MODALIDAD_CAMBIO_IRREVERSIBLE` | "El cambio de modalidad es irreversible: no se permite cambiar de Examen Complexivo a Trabajo de Integración Curricular." | POST cambiar EC→TIC |
| `ELEGIBILIDAD_NO_CUMPLIDA` | "El estudiante no cumple los requisitos para Examen Complexivo: {detalle}." | POST cambiar sin elegibilidad |
| `ESTADO_EXPEDIENTE_INVALIDO` | "No se puede cambiar la modalidad en estado {estado}; solo permitido en BORRADOR, ENVIADA o EN_VERIFICACION." | POST cambiar en estado avanzado |
| `CAMBIO_YA_REALIZADO` | "La modalidad ya fue cambiada anteriormente; no se permiten múltiples cambios." | Segundo POST cambiar |
| `EVIDENCIA_INCOMPLETA` | "Evidencia académica incompleta: requiere actas de las 2 reprobaciones y resolución de tercera matrícula." | POST cambiar sin evidencia |
| `JUSTIFICACION_INSUFICIENTE` | "La justificación debe tener al menos 50 caracteres." | POST cambiar sin justificación |
| `SIN_PERMISO_AUTORIZACION` | "Requiere autorización del Decano para cambiar a Examen Complexivo." | POST cambiar por Secretario sin Decano (o viceversa) |

---

## 8. OBSERVACIONES IMPORTANTES

1. **Frontend nunca decide**: La elegibilidad EC **solo** la determina el backend (mock SGA). Frontend muestra lo que backend retorna.
2. **Irreversibilidad**: TIC → EC es camino único. No hay retorno a TIC una vez autorizado EC.
3. **Un solo cambio**: Un expediente solo puede cambiar modalidad **una vez** en su ciclo de vida.
4. **Evidencia inmutable**: `HistorialModalidad.evidencia_academica` es JSON inmutable; no editable posterior.
5. **Fase 2 futura**: Reglas académicas específicas (trabajo escrito vs examen integral) se implementarán en Fase 2 (Sustentación/Defensa).
6. **Validación normativa obligatoria**: **Ninguna regla se implementa sin validación firmada** de Arts. 39, 40, 212, 216, 233 RRA-UNL por autoridad competente.

---

## 9. PRÓXIMOS PASOS

1. **Validar normativa** (checklist §11 DISENO_FUNCIONAL) con autoridad competente
2. **Autorizar INC-03** para implementación backend
3. **Diseñar mock SGA** para elegibilidad EC (2 reprobaciones + 3ra matrícula)
4. **Crear migraciones** y servicios base
5. **Implementar tests** de todas las reglas (§6)
5. **Integrar frontend** (INC-08) tras backend validado