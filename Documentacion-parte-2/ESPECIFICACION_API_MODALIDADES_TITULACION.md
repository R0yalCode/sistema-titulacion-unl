# ESPECIFICACIÓN API: MODALIDADES DE TITULACIÓN — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `DISENO_FUNCIONAL_MODALIDADES_TITULACION.md` + `MATRIZ_REGLAS_NEGOCIO_MODALIDADES.md`  
**Estado:** Diseño — Requiere validación normativa y autorización BE-06  

---

## 1. RESUMEN DE ENDPOINTS

| Endpoint | Método | Descripción | Autenticación | Roles | Permisos |
|----------|--------|-------------|---------------|-------|----------|
| `/api/v1/expedientes/{id}/modalidad/` | GET | Modalidad actual + historial | JWT | Estudiante (own), Secretario, Analista, Decano, Director, Admin | `expedientes:modalidad` GET |
| `/api/v1/expedientes/{id}/modalidad/elegibilidad/` | GET | Verificar elegibilidad EC | JWT | Secretario, Decano, Admin | `expedientes:modalidad` GET |
| `/api/v1/expedientes/{id}/modalidad/cambiar/` | POST | Cambiar modalidad TIC→EC | JWT | Secretario (verifica), Decano (autoriza), Admin | `expedientes:modalidad` POST |
| `/api/v1/modalidades/` | GET | Catálogo modalidades válidas | JWT | Todos autenticados | `modalidades` GET |

---

## 2. ESQUEMAS DE DATOS

### 2.1 ModalidadTitulacion (Enum)
```json
{
  "TIC": "Trabajo de Integración Curricular",
  "EC": "Examen Complexivo"
}
```

### 2.2 HistorialModalidad
```json
{
  "id": "uuid",
  "expediente": "uuid",
  "modalidad_anterior": "TIC",
  "modalidad_nueva": "EC",
  "fecha_cambio": "2026-11-09T14:30:00Z",
  "autorizado_por": "uuid",
  "autorizado_por_username": "secretario.juridico",
  "justificacion": "El estudiante cumple requisitos...",
  "evidencia_academica": {
    "reprobaciones": [...],
    "tercera_matricula": {...},
    "documentos_referencia": [...]
  },
  "estado_tercera_matricula": true
}
```

### 2.3 ElegibilidadEC
```json
{
  "elegible": true,
  "evidencia": {
    "reprobaciones": 2,
    "tercera_matricula": true,
    "detalles": [
      {"periodo": "2025-1", "materia": "TIT-001", "nota": 4.5},
      {"periodo": "2025-2", "materia": "TIT-001", "nota": 5.0}
    ]
  },
  "mensaje": "Estudiante cumple requisitos para Examen Complexivo"
}
```

---

## 3. ENDPOINTS DETALLADOS

### 3.1 GET /api/v1/expedientes/{id}/modalidad/

**Descripción:** Obtiene la modalidad actual del expediente y su historial de cambios.

**Parámetros de ruta:**
- `id` (UUID, requerido): ID del expediente

**Headers:**
- `Authorization: Bearer <access_token>`

**Respuesta 200 (Exitosa):**
```json
{
  "opcion_titulacion": "TIC",
  "historial": [
    {
      "id": "uuid",
      "modalidad_anterior": "TIC",
      "modalidad_nueva": "EC",
      "fecha_cambio": "2026-11-09T14:30:00Z",
      "autorizado_por": "uuid-decano",
      "autorizado_por_username": "decano.facultad",
      "justificacion": "Estudiante cumple requisitos...",
      "evidencia_academica": {...},
      "estado_tercera_matricula": true
    }
  ]
}
```

**Respuesta 403 (Sin permisos):**
```json
{
  "detail": "El rol del usuario no esta autorizado para acceder a este recurso."
}
```

**Respuesta 404 (No encontrado):**
```json
{
  "detail": "No encontrado."
}
```

**Permisos por Scope:**
| Scope | Qué Ve |
|-------|--------|
| `SCOPE_OWN` (Estudiante) | Solo su expediente |
| `SCOPE_CARRERA` (Secretaria/Director) | Expedientes de su carrera |
| `SCOPE_FACULTAD` (Secretario/Analista/Decano) | Expedientes de su facultad |
| `SCOPE_ALL` (Admin) | Todos |

---

### 3.2 GET /api/v1/expedientes/{id}/modalidad/elegibilidad/

**Descripción:** Verifica si el estudiante del expediente cumple requisitos para Examen Complexivo.

**Parámetros de ruta:**
- `id` (UUID, requerido): ID del expediente

**Headers:**
- `Authorization: Bearer <access_token>`

**Respuesta 200 (Exitosa):**
```json
{
  "elegible": true,
  "evidencia": {
    "reprobaciones": 2,
    "tercera_matricula": true,
    "detalles": [
      {"periodo": "2025-1", "materia_codigo": "TIT-001", "materia_nombre": "Titulación I", "nota": 4.5},
      {"periodo": "2025-2", "materia_codigo": "TIT-001", "materia_nombre": "Titulación I", "nota": 5.0}
    ]
  },
  "mensaje": "Estudiante cumple requisitos para Examen Complexivo: 2 reprobaciones en TIT-001 y tercera matrícula activa (RES-2026-00123)."
}
```

**Respuesta 200 (No elegible):**
```json
{
  "elegible": false,
  "evidencia": {
    "reprobaciones": 1,
    "tercera_matricula": false,
    "detalles": [
      {"periodo": "2025-2", "materia_codigo": "TIT-001", "materia_nombre": "Titulación I", "nota": 5.0}
    ]
  },
  "mensaje": "El estudiante no cumple requisitos para Examen Complexivo: requiere 2 reprobaciones en unidad de titulación (tiene 1) y tercera matrícula efectiva."
}
```

**Permisos:**
| Rol | Acceso |
|-----|--------|
| `SECRETARIO_ABOGADO` | ✅ (facultad) |
| `DECANO` | ✅ (facultad) |
| `ADMINISTRADOR` | ✅ (all) |
| `ESTUDIANTE` | ❌ (403) |
| `SECRETARIA_CARRERA` | ❌ (403) |
| `DIRECTOR_CARRERA` | ❌ (403) |

---

### 3.3 POST /api/v1/expedientes/{id}/modalidad/cambiar/

**Descripción:** Cambia la modalidad del expediente de TIC a EC (irreversible).

**Parámetros de ruta:**
- `id` (UUID, requerido): ID del expediente

**Headers:**
- `Authorization: Bearer <access_token>`
- `Content-Type: application/json`

**Body Request:**
```json
{
  "nueva_modalidad": "EC",
  "justificacion": "El estudiante ha reprobado dos veces la unidad de titulación TIT-001 (períodos 2025-1 y 2025-2) y ha accedido a tercera matrícula mediante resolución RES-2026-00123. Se autoriza cambio a Examen Complexivo conforme Art. 40 y 233 RRA-UNL.",
  "evidencia_academica": {
    "reprobaciones": [
      {"periodo": "2025-1", "materia_codigo": "TIT-001", "materia_nombre": "Titulación I", "nota": 4.5, "acta_referencia": "ACTA-2025-001"},
      {"periodo": "2025-2", "materia_codigo": "TIT-001", "materia_nombre": "Titulación I", "nota": 5.0, "acta_referencia": "ACTA-2025-045"}
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
    ]
  }
}
```

**Validaciones Request:**
| Campo | Requerido | Validación |
|-------|-----------|------------|
| `nueva_modalidad` | Sí | Debe ser `"EC"` (único valor permitido) |
| `justificacion` | Sí | String, mínimo 50 caracteres |
| `evidencia_academica` | Sí | Objeto con estructura definida (ver §2.3) |
| `evidencia_academica.reprobaciones` | Sí | Array con 2+ objetos (periodo, materia_codigo, materia_nombre, nota, acta_referencia) |
| `evidencia_academica.tercera_matricula` | Sí | Objeto con `activa: true`, `resolucion`, `fecha_resolucion`, `documento_referencia` |

**Respuesta 201 (Exitosa):**
```json
{
  "expediente": {
    "id": "uuid",
    "numero_expediente": "EXP-2026-0042",
    "opcion_titulacion": "EC",
    "estado": "EN_VERIFICACION",
    ...
  },
  "historial": {
    "id": "uuid",
    "modalidad_anterior": "TIC",
    "modalidad_nueva": "EC",
    "fecha_cambio": "2026-11-09T14:30:00Z",
    "autorizado_por": "uuid-decano",
    "autorizado_por_username": "decano.facultad",
    "justificacion": "...",
    "evidencia_academica": {...},
    "estado_tercera_matricula": true
  }
}
```

**Respuestas de Error:**

| Código | Causa | Mensaje |
|--------|-------|---------|
| 400 | `nueva_modalidad` ≠ "EC" | "Solo se permite cambio a Examen Complexivo (modalidad excepcional)." |
| 400 | Expediente ya es EC | "El expediente ya tiene esa modalidad." |
| 400 | Expediente no es TIC | "Solo se puede cambiar desde Trabajo Integración Curricular." |
| 400 | Sin elegibilidad verificada | "El estudiante no cumple los requisitos para Examen Complexivo: {detalle}." |
| 400 | Estado inválido (ej. INFORME_EMITIDO) | "No se puede cambiar la modalidad en estado INFORME_EMITIDO; solo permitido en BORRADOR, ENVIADA o EN_VERIFICACION." |
| 400 | Justificación < 50 chars | "La justificación debe tener al menos 50 caracteres." |
| 400 | Evidencia incompleta | "Evidencia académica incompleta: requiere actas de las 2 reprobaciones y resolución de tercera matrícula." |
| 400 | Cambio ya realizado | "La modalidad ya fue cambiada anteriormente; no se permiten múltiples cambios." |
| 403 | Rol no autorizado (ej. Estudiante, Secretaria) | "El rol del usuario no esta autorizado para acceder a este recurso." |
| 403 | Secretario intenta autorizar (solo Decano) | "Requiere autorización del Decano para cambiar a Examen Complexivo." |
| 404 | Expediente no encontrado | "No encontrado." |

**Permisos:**
| Rol | Acción Permitida |
|-----|------------------|
| `SECRETARIO_ABOGADO` | ✅ **Verifica** elegibilidad (GET /elegibilidad/) — NO puede POST /cambiar/ |
| `DECANO` | ✅ **Autoriza** cambio (POST /cambiar/) — Requiere elegibilidad verificada |
| `ADMINISTRADOR` | ✅ Ambos (verifica + autoriza) |
| `SECRETARIA_CARRERA` | ❌ |
| `DIRECTOR_CARRERA` | ❌ |
| `ESTUDIANTE` | ❌ |
| `ANALISTA_APOYO` | ❌ (puede ver elegibilidad GET) |

**Flujo Recomendado:**
1. Secretario: `GET /elegibilidad/` → si `elegible: true` → informa a Decano
2. Decano: `POST /cambiar/` con justificación + evidencia → 201

---

### 3.4 GET /api/v1/modalidades/

**Descripción:** Catálogo de modalidades de titulación válidas en el sistema.

**Headers:**
- `Authorization: Bearer <access_token>`

**Respuesta 200:**
```json
{
  "modalidades": [
    {
      "codigo": "TIC",
      "nombre": "Trabajo de Integración Curricular",
      "tipo": "ordinaria",
      "descripcion": "Modalidad ordinaria de titulación mediante trabajo de integración curricular (Art. 39, 212, 216 RRA-UNL)."
    },
    {
      "codigo": "EC",
      "nombre": "Examen Complexivo",
      "tipo": "excepcional",
      "descripcion": "Modalidad excepcional para estudiantes que hayan reprobado dos veces la unidad de titulación y accedan a tercera matrícula (Art. 40, 212 inc. b, 233 RRA-UNL)."
    }
  ]
}
```

**Permisos:** Todos los roles autenticados (`SCOPE_OWN` mínimo).

---

## 4. INTEGRACIÓN CON EXPEDIENTES EXISTENTES

### 4.1 Creación Expediente (`POST /api/v1/expedientes/`)
- **Cambio:** Servicio `crear_expediente` establece `opcion_titulacion = 'TIC'` por defecto
- **Validación:** Rechaza request con `opcion_titulacion = 'EC'` (HTTP 400)
- **Response:** Incluye `opcion_titulacion` en `ExpedienteBorrador`

### 4.2 Detalle Expediente (`GET /api/v1/expedientes/{id}/`)
- **Nuevo campo:** `opcion_titulacion` en `ExpedienteDetalle`
- **Historial:** No incluido (endpoint separado `/modalidad/`)

### 4.3 Bandeja Expedientes (`GET /api/v1/expedientes/bandeja/`)
- **Nuevo campo opcional:** `opcion_titulacion` en `BandejaExpediente` (para filtros dashboard)
- **Filtro query:** `?modalidad=TIC|EC` (opcional)

---

## 5. AUDITORÍA Y TRAZABILIDAD

### 5.1 Eventos Nuevos
| Acción | EventoAuditoria.accion | Detalles |
|--------|------------------------|----------|
| Verificar elegibilidad EC | `MODALIDAD_ELEGIBILIDAD_VERIFICADA` | `{expediente_id, estudiante_id, elegible, evidencia}` |
| Cambiar modalidad TIC→EC | `MODALIDAD_CAMBIADA` | `{expediente_id, modalidad_anterior, modalidad_nueva, autorizado_por, justificacion, evidencia_academica}` |
| Intento cambio fallido | `MODALIDAD_CAMBIO_INTENTO_FALLIDO` | `{expediente_id, usuario_id, razon}` |

### 5.2 Signal `post_save` HistorialModalidad
```python
# notificaciones/signals.py (adición)
@receiver(post_save, sender=HistorialModalidad)
def registrar_auditoria_modalidad(sender, instance, created, **kwargs):
    if created:
        crear_evento_auditoria(
            accion="MODALIDAD_CAMBIADA",
            usuario=instance.autorizado_por,
            expediente=instance.expediente,
            detalles={
                "modalidad_anterior": instance.modalidad_anterior,
                "modalidad_nueva": instance.modalidad_nueva,
                "justificacion": instance.justificacion,
                "evidencia_academica": instance.evidencia_academica,
            }
        )
```

---

## 6. PERMISOS RBAC (ACTUALIZACIÓN MATRIZ)

```python
# authentication/permissions.py

RBAC_MATRIX = {
    # ... existentes ...
    'expedientes:modalidad': {
        'GET': {  # modalidad actual + historial + elegibilidad
            'ESTUDIANTE': 'SCOPE_OWN',
            'SECRETARIO_ABOGADO': 'SCOPE_FACULTAD',
            'ANALISTA_APOYO': 'SCOPE_FACULTAD',  # Solo ver elegibilidad
            'DECANO': 'SCOPE_FACULTAD',
            'DIRECTOR_CARRERA': 'SCOPE_CARRERA',
            'ADMINISTRADOR': 'SCOPE_ALL',
        },
        'POST': {  # cambiar modalidad
            'SECRETARIO_ABOGADO': 'SCOPE_FACULTAD',  # Solo GET elegibilidad en práctica
            'DECANO': 'SCOPE_FACULTAD',              # POST /cambiar/
            'ADMINISTRADOR': 'SCOPE_ALL',
        }
    },
    'modalidades': {  # catálogo
        'GET': {
            'ESTUDIANTE': 'SCOPE_OWN',
            'SECRETARIA_CARRERA': 'SCOPE_CARRERA',
            'SECRETARIO_ABOGADO': 'SCOPE_FACULTAD',
            'ANALISTA_APOYO': 'SCOPE_FACULTAD',
            'DECANO': 'SCOPE_FACULTAD',
            'DIRECTOR_CARRERA': 'SCOPE_CARRERA',
            'RESPONSABLE_DEPENDENCIA': 'SCOPE_ASIGNADO',  # Requiere TASK-P1-004
            'ADMINISTRADOR': 'SCOPE_ALL',
        }
    },
}
```

---

## 7. TESTS DE CONTRATO

### 7.1 Casos por Endpoint

#### GET /expedientes/{id}/modalidad/
- [ ] 200: Estudiante ve su expediente (modalidad + historial vacío)
- [ ] 200: Secretario ve expediente facultad (modalidad + historial)
- [ ] 403: Estudiante intenta ver expediente otra carrera
- [ ] 404: ID inexistente
- [ ] Historial ordenado por fecha_cambio DESC

#### GET /expedientes/{id}/modalidad/elegibilidad/
- [ ] 200 elegible: Mock SGA 2 reprobaciones + 3ra matrícula → `elegible: true`
- [ ] 200 no elegible: Mock SGA 1 reprobación → `elegible: false` + mensaje claro
- [ ] 403: Estudiante intenta acceder
- [ ] 403: Secretaria Carrera intenta acceder
- [ ] 404: Expediente inexistente

#### POST /expedientes/{id}/modalidad/cambiar/
- [ ] 201: Decano autoriza con elegibilidad verificada + justificación + evidencia
- [ ] 400: `nueva_modalidad` ≠ "EC"
- [ ] 400: Expediente ya es EC
- [ ] 400: Expediente no es TIC
- [ ] 400: Sin elegibilidad (mock SGA false)
- [ ] 400: Estado INFORME_EMITIDO
- [ ] 400: Justificación < 50 chars
- [ ] 400: Evidencia incompleta (falta acta/reprobación/resolución)
- [ ] 400: Cambio ya realizado
- [ ] 403: Secretario intenta POST (solo Decano)
- [ ] 403: Estudiante/Secretaria/Director
- [ ] 404: Expediente inexistente
- [ ] Historial creado inmutable + EventoAuditoria `MODALIDAD_CAMBIADA`

#### GET /modalidades/
- [ ] 200: Array con 2 modalidades (TIC ordinaria, EC excepcional)
- [ ] Estructura campos: codigo, nombre, tipo, descripcion

---

## 8. DOCUMENTACIÓN OPENAPI (drf-spectacular)

```python
# Se auto-genera con @extend_schema en ViewSet
# Ejemplo manual para reference:

@extend_schema(
    summary="Obtener modalidad actual e historial",
    parameters=[OpenApiParameter(name='id', type=OpenApiTypes.UUID, location=OpenApiParameter.PATH)],
    responses={200: ModalidadActualSerializer, 403: ErrorSerializer, 404: ErrorSerializer},
    tags=['Modalidades']
)
@action(detail=True, methods=['get'], url_path='modalidad')
def modalidad_actual(self, request, expediente_id=None): ...

@extend_schema(
    summary="Verificar elegibilidad Examen Complexivo",
    responses={200: ElegibilidadECSerializer, 403: ErrorSerializer},
    tags=['Modalidades']
)
@action(detail=True, methods=['get'], url_path='modalidad/elegibilidad')
def elegibilidad_ec(self, request, expediente_id=None): ...

@extend_schema(
    summary="Cambiar modalidad a Examen Complexivo",
    request=CambiarModalidadRequestSerializer,
    responses={201: CambiarModalidadResponseSerializer, 400: ErrorSerializer, 403: ErrorSerializer},
    tags=['Modalidades']
)
@action(detail=True, methods=['post'], url_path='modalidad/cambiar')
def cambiar_modalidad(self, request, expediente_id=None): ...
```

---

## 9. CHECKLIST PRE-IMPLEMENTACIÓN

- [ ] Validación normativa RRA-UNL (arts. 39, 40, 212, 216, 233) **firmada por autoridad competente**
- [ ] Mock SGA diseñado para elegibilidad EC (2 reprobaciones + 3ra matrícula)
- [ ] Migraciones: `opcion_titulacion` + `HistorialModalidad` creadas y probadas
- [ ] Servicios `verificar_elegibilidad_ec` + `cambiar_modalidad` implementados + tests
- [ ] Endpoints en `ExpedienteViewSet`/`ModalidadViewSet` + permisos RBAC
- [ ] Signal auditoría `MODALIDAD_CAMBIADA` registrada
- [ ] Tests contrato (8 endpoints + casos error) passing
- [ ] Documentación OpenAPI actualizada
- [ ] Frontend tipos TypeScript actualizados (`ModalidadTitulacion`, `HistorialModalidad`, `ElegibilidadEC`)

---

## 10. PRÓXIMOS PASOS

1. **Validar normativa** con autoridad competente (checklist §11 DISENO_FUNCIONAL)
2. **Autorizar BE-06** (campo `opcion_titulacion` + endpoints modalidad)
3. **Implementar INC-03** (Modalidades Core Backend)
4. **Ejecutar tests contrato** contra implementación
5. **Actualizar frontend** tipos + hooks (INC-08)
6. **Integrar en dashboards** (INC-04/08)