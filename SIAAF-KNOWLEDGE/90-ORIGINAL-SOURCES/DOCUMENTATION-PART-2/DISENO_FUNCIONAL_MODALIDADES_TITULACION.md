# DISEÑO FUNCIONAL: MODALIDADES DE TITULACIÓN — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` §4 + `specs/003-frontend-titulacion/clarify.md` DEC-14/INC-15 + RRA-UNL  
**Estado:** Diseño pendiente validación normativa y autorización BE-06  

---

## 1. CONTEXTO NORMATIVO (PENDIENTE VALIDACIÓN CON FUENTE PRIMARIA)

### 1.1 Referencias RRA-UNL (Arts. 39, 40, 212, 216, 233)
> **ADVERTENCIA:** Las referencias a artículos del Reglamento de Régimen Académico (RRA-UNL) **no han sido contrastadas directamente con el texto vigente** en el repositorio. El análisis secundario (NotebookLM) **no constituye fuente normativa**. Requiere validación expresa con documento oficial UNL.

| Artículo | Modalidad | Condición Preliminar (Hipótesis) |
|----------|-----------|----------------------------------|
| Art. 39 | Trabajo Integración Curricular | Opción ordinaria: 100% asignaturas aprobadas O planificación 85% horas |
| Art. 212 | Trabajo Integración Curricular | Procedimiento general de titulación |
| Art. 216 | Trabajo Integración Curricular | Requisitos de elegibilidad ordinaria |
| Art. 40 | Examen Complexivo | Excepcional: 2 reprobaciones unidad titulación + 3ra matrícula efectiva |
| Art. 212 inc. b | Examen Complexivo | Habilitación excepcional |
| Art. 233 | Examen Complexivo | Procedimiento para modalidad excepcional |

### 1.2 Decisiones Requerentes Aprobación Humana
1. **Confirmar texto exacto** Arts. 39, 40, 212, 216, 233 RRA-UNL vigente
2. **Definir "100% asignaturas" vs "85% horas planificadas"**: ¿Aplican a todas las carreras? ¿Diferencia ingenierías/licenciaturas?
3. **Definir "2 reprobaciones unidad titulación"**: ¿Unidad = materia "Titulación"? ¿En qué período?
4. **Definir "3ra matrícula efectiva"**: ¿Cómo se verifica? ¿Documento oficial?
5. **Confirmar actor autorizador**: Secretario verifica + Decano autoriza (basado en Arts. 212, 233)
6. **Descartar "Proyecto de Emprendimiento"**: No aparece en normativa consultada (INC-15)

---

## 2. DEFINICIÓN DE MODALIDADES

### 2.1 Enum Canónico
```python
class ModalidadTitulacion(models.TextChoices):
    TRABAJO_INTEGRACION_CURRICULAR = 'TIC', 'Trabajo de Integración Curricular'
    EXAMEN_COMPLEXIVO = 'EC', 'Examen Complexivo'
```

### 2.2 Características por Modalidad

| Atributo | Trabajo Integración Curricular (TIC) | Examen Complexivo (EC) |
|----------|--------------------------------------|------------------------|
| **Código** | `TIC` | `EC` |
| **Nombre completo** | Trabajo de Integración Curricular | Examen Complexivo |
| **Clasificación** | **Ordinaria** (predeterminada) | **Excepcional** (condicionada) |
| **Selección estudiante** | ✅ Automática al crear expediente | ❌ No seleccionable por estudiante |
| **Elegibilidad** | 100% asignaturas O 85% horas planificadas | 2 reprobaciones + 3ra matrícula efectiva |
| **Verificación** | Automática (mock SGA) | Manual (Secretario) + Automática (mock SGA) |
| **Autorización cambio** | No requiere (es default) | Secretario verifica + Decano autoriza |
| **Proceso académico** | Trabajo escrito + defensa (Fase 2 futura) | Examen integral ante tribunal (Fase 2 futura) |
| **Documento final** | Memorando declaratoria aptitud | Acta examen complexivo + memorando |

---

## 3. REGLAS DE NEGOCIO OBLIGATORIAS (RN-MOD)

| ID | Regla | Descripción | Validación |
|----|-------|-------------|------------|
| **RN-MOD-01** | TIC es predeterminada | Al crear expediente, `opcion_titulacion = 'TIC'` por defecto | Default en modelo + servicio `crear_expediente` |
| **RN-MOD-02** | EC no seleccionable por estudiante | UI no muestra EC como opción en V-03; backend rechaza `POST /expedientes/` con `opcion_titulacion=EC` | Servicio `crear_expediente` valida |
| **RN-MOD-03** | Elegibilidad EC verificable | Requiere: 2 reprobaciones unidad titulación + 3ra matrícula efectiva | Servicio `verificar_elegibilidad_ec()` consulta mock SGA |
| **RN-MOD-04** | Cambio modalidad solo autorizado | No se permite `PUT /expedientes/{id}/` con cambio modalidad; solo endpoint dedicado `POST /modalidad/cambiar/` | Endpoint dedicado + RBAC |
| **RN-MOD-05** | Historial inmutable | Cada cambio registra `HistorialModalidad` con evidencia académica | Modelo + servicio `cambiar_modalidad` |
| **RN-MOD-06** | Actor verificador: Secretario/a-Abogado/a | Verifica elegibilidad EC (revisa mock SGA + documentación) | RBAC: `SECRETARIO_ABOGADO` + `SCOPE_FACULTAD` |
| **RN-MOD-07** | Actor autorizador: Decano/a | Decisión final de cambio a EC | RBAC: `DECANO` + `SCOPE_FACULTAD` |
| **RN-MOD-08** | Expediente con actividades: reglas transición | Si estado ≠ BORRADOR, validar impacto cambio (ej. checklist ya evaluado) | Servicio `cambiar_modalidad` valida estado |
| **RN-MOD-09** | Protección modificación directa API | No hay `PATCH /expedientes/{id}/` para modalidad; solo endpoint controlado | No serializer field `opcion_titulacion` en update |
| **RN-MOD-10** | Evidencia académica obligatoria | Cambio a EC requiere: actas reprobaciones + resolución 3ra matrícula | `HistorialModalidad.evidencia_academica` JSON |

---

## 4. MODELO DE DATOS

### 4.1 Extensión `ExpedienteTitulacion`
```python
# backend/src/apps/expedientes/adapters/models.py (adición)

class ExpedienteTitulacion(models.Model):
    # ... campos existentes ...
    
    opcion_titulacion = models.CharField(
        max_length=3,
        choices=ModalidadTitulacion.choices,
        default=ModalidadTitulacion.TRABAJO_INTEGRACION_CURRICULAR,
        db_index=True,
        verbose_name="Modalidad de titulación"
    )
```

### 4.2 Nuevo Modelo: `HistorialModalidad`
```python
# backend/src/apps/expedientes/adapters/models.py (nuevo)

class HistorialModalidad(models.Model):
    """Trazabilidad inmutable de cambios de modalidad de titulación."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expediente = models.ForeignKey(
        'expedientes.ExpedienteTitulacion',
        on_delete=models.CASCADE,
        related_name='historial_modalidad',
    )
    modalidad_anterior = models.CharField(
        max_length=3, 
        choices=ModalidadTitulacion.choices,
    )
    modalidad_nueva = models.CharField(
        max_length=3, 
        choices=ModalidadTitulacion.choices,
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    autorizado_por = models.ForeignKey(
        'authentication.User',
        on_delete=models.PROTECT,
        related_name='modalidades_autorizadas',
    )
    justificacion = models.TextField()
    evidencia_academica = models.JSONField(
        default=dict,
        help_text="Estructura: {reprobaciones: [...], tercera_matricula: {...}, documentos_referencia: [...]}"
    )
    estado_tercera_matricula = models.BooleanField(
        default=False,
        help_text="Verificado contra SGA/mock: 3ra matrícula efectiva"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['expediente'], name='idx_hist_modalidad_expediente'),
            models.Index(fields=['fecha_cambio'], name='idx_hist_modalidad_fecha'),
        ]
        ordering = ['-fecha_cambio']
    
    def __str__(self):
        return f"{self.expediente_id}: {self.modalidad_anterior} → {self.modalidad_nueva} ({self.fecha_cambio})"
```

### 4.3 Migraciones Requeridas
1. `0005_expedientetitulacion_opcion_titulacion.py` — Add field `opcion_titulacion`
2. `0006_historialmodalidad.py` — Create model `HistorialModalidad`

---

## 5. SERVICIOS DE NEGOCIO

### 5.1 `verificar_elegibilidad_ec.py`
```python
# backend/src/apps/expedientes/services/verificar_elegibilidad_ec.py

from dataclasses import dataclass
from apps.authentication.adapters.models import User

@dataclass
class ElegibilidadEC:
    elegible: bool
    evidencia: dict  # {reprobaciones: int, tercera_matricula: bool, detalles: [...]}
    mensaje: str

def verificar_elegibilidad_ec(estudiante: User) -> ElegibilidadEC:
    """
    Consulta mock SGA para verificar:
    1. Dos reprobaciones en unidad de titulación
    2. Acceso efectivo a tercera matrícula (resolución oficial)
    
    Retorna ElegibilidadEC con evidencia estructurada.
    """
    # TODO: Implementar consulta a mock SGA (servicio simulado)
    # Estructura esperada respuesta mock SGA:
    # {
    #   "reprobaciones_titulacion": 2,
    #   "tercera_matricula": {"activa": True, "resolucion": "RES-2026-XXX", "fecha": "2026-01-15"},
    #   "detalles": [...]
    # }
    
    # Placeholder para desarrollo:
    return ElegibilidadEC(
        elegible=False,
        evidencia={},
        mensaje="Mock SGA no implementado. Requiere integración servicio simulado."
    )
```

### 5.2 `cambiar_modalidad.py`
```python
# backend/src/apps/expedientes/services/cambiar_modalidad.py

from django.db import transaction
from django.utils import timezone
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialModalidad, ModalidadTitulacion
from apps.authentication.adapters.models import User
from .verificar_elegibilidad_ec import verificar_elegibilidad_ec

class CambioModalidadNoPermitidoError(Exception):
    pass

class ElegibilidadNoVerificadaError(Exception):
    pass

def cambiar_modalidad(
    expediente: ExpedienteTitulacion,
    nueva_modalidad: str,
    autorizador: User,
    justificacion: str,
    evidencia_academica: dict,
) -> ExpedienteTitulacion:
    """
    Cambia la modalidad de titulación de un expediente.
    
    Reglas:
    - Solo permite cambio TIC → EC (EC → TIC no previsto en normativa)
    - Requiere elegibilidad EC verificada (mock SGA)
    - Requiere autorizador con rol SECRETARIO_ABOGADO (verifica) o DECANO (autoriza)
    - Registra HistorialModalidad inmutable
    - Actualiza expediente.opcion_titulacion
    """
    if nueva_modalidad not in ModalidadTitulacion.values:
        raise CambioModalidadNoPermitidoError(f"Modalidad '{nueva_modalidad}' no válida.")
    
    if expediente.opcion_titulacion == nueva_modalidad:
        raise CambioModalidadNoPermitidoError("El expediente ya tiene esa modalidad.")
    
    # Solo se permite cambio a EC (excepcional)
    if nueva_modalidad != ModalidadTitulacion.EXAMEN_COMPLEXIVO:
        raise CambioModalidadNoPermitidoError("Solo se permite cambio a Examen Complexivo (modalidad excepcional).")
    
    if expediente.opcion_titulacion != ModalidadTitulacion.TRABAJO_INTEGRACION_CURRICULAR:
        raise CambioModalidadNoPermitidoError("Solo se puede cambiar desde Trabajo Integración Curricular.")
    
    # Verificar elegibilidad EC (mock SGA)
    elegibilidad = verificar_elegibilidad_ec(expediente.estudiante)
    if not elegibilidad.elegible:
        raise ElegibilidadNoVerificadaError(
            f"El estudiante no cumple requisitos para Examen Complexivo: {elegibilidad.mensaje}"
        )
    
    # Validar estado expediente (regla RN-MOD-08)
    if expediente.estado not in ['BORRADOR', 'ENVIADA', 'EN_VERIFICACION']:
        raise CambioModalidadNoPermitidoError(
            f"No se puede cambiar modalidad en estado '{expediente.estado}'. "
            "Solo permitido en BORRADOR, ENVIADA o EN_VERIFICACION."
        )
    
    with transaction.atomic():
        # Registrar historial ANTES de cambiar
        HistorialModalidad.objects.create(
            expediente=expediente,
            modalidad_anterior=expediente.opcion_titulacion,
            modalidad_nueva=nueva_modalidad,
            autorizado_por=autorizador,
            justificacion=justificacion,
            evidencia_academica=evidencia_academica,
            estado_tercera_matricula=elegibilidad.evidencia.get('tercera_matricula', {}).get('activa', False),
        )
        
        # Actualizar expediente
        expediente.opcion_titulacion = nueva_modalidad
        expediente.save(update_fields=['opcion_titulacion'])
    
    return expediente
```

---

## 6. ENDPOINTS API

### 6.1 Serializers
```python
# backend/src/apps/expedientes/adapters/serializers.py (adición)

class ModalidadActualSerializer(serializers.Serializer):
    opcion_titulacion = serializers.ChoiceField(choices=ModalidadTitulacion.choices)
    historial = HistorialModalidadSerializer(many=True, read_only=True)

class ElegibilidadECSerializer(serializers.Serializer):
    elegible = serializers.BooleanField()
    evidencia = serializers.DictField()
    mensaje = serializers.CharField()

class CambiarModalidadRequestSerializer(serializers.Serializer):
    nueva_modalidad = serializers.ChoiceField(choices=ModalidadTitulacion.choices)
    justificacion = serializers.CharField(max_length=1000)
    evidencia_academica = serializers.JSONField()

class CambiarModalidadResponseSerializer(serializers.Serializer):
    expediente = ExpedienteDetalleSerializer()
    historial = HistorialModalidadSerializer()
```

### 6.2 ViewSet
```python
# backend/src/apps/expedientes/adapters/views.py (adición)

class ModalidadViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, HasRolePermission]
    
    def get_rbac_resource(self):
        return 'expedientes:modalidad'
    
    def get_object(self):
        return get_object_or_404(ExpedienteTitulacion, pk=self.kwargs['expediente_id'], activa=True)
    
    @action(detail=True, methods=['get'], url_path='modalidad')
    def modalidad_actual(self, request, expediente_id=None):
        """GET /expedientes/{id}/modalidad/ - Modalidad actual + historial"""
        expediente = self.get_object()
        serializer = ModalidadActualSerializer({
            'opcion_titulacion': expediente.opcion_titulacion,
            'historial': expediente.historial_modalidad.all(),
        })
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='modalidad/elegibilidad')
    def elegibilidad_ec(self, request, expediente_id=None):
        """GET /expedientes/{id}/modalidad/elegibilidad/ - Verificar elegibilidad EC"""
        expediente = self.get_object()
        from ..services.verificar_elegibilidad_ec import verificar_elegibilidad_ec
        elegibilidad = verificar_elegibilidad_ec(expediente.estudiante)
        return Response(ElegibilidadECSerializer(elegibilidad.__dict__).data)
    
    @action(detail=True, methods=['post'], url_path='modalidad/cambiar')
    def cambiar_modalidad(self, request, expediente_id=None):
        """POST /expedientes/{id}/modalidad/cambiar/ - Cambiar modalidad (Secretario/Decano)"""
        expediente = self.get_object()
        serializer = CambiarModalidadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from ..services.cambiar_modalidad import cambiar_modalidad, CambioModalidadNoPermitidoError, ElegibilidadNoVerificadaError
        try:
            expediente_actualizado = cambiar_modalidad(
                expediente=expediente,
                nueva_modalidad=serializer.validated_data['nueva_modalidad'],
                autorizador=request.user,
                justificacion=serializer.validated_data['justificacion'],
                evidencia_academica=serializer.validated_data['evidencia_academica'],
            )
        except (CambioModalidadNoPermitidoError, ElegibilidadNoVerificadaError) as e:
            return Response({'detail': str(e)}, status=400)
        
        return Response(CambiarModalidadResponseSerializer({
            'expediente': expediente_actualizado,
            'historial': expediente_actualizado.historial_modalidad.first(),
        }).data)
    
    @action(detail=False, methods=['get'], url_path='modalidades')
    def catalogo_modalidades(self, request):
        """GET /modalidades/ - Catálogo modalidades válidas"""
        return Response({
            'modalidades': [
                {'codigo': 'TIC', 'nombre': 'Trabajo de Integración Curricular', 'tipo': 'ordinaria'},
                {'codigo': 'EC', 'nombre': 'Examen Complexivo', 'tipo': 'excepcional'},
            ]
        })
```

### 6.3 URLs
```python
# backend/src/apps/expedientes/adapters/urls.py (adición)

router.register(r'expedientes', ExpedienteViewSet, basename='expediente')
# ... existentes ...

# Modalidad endpoints (ViewSet separado o @action en ExpedienteViewSet)
urlpatterns = [
    # ... existentes ...
    path('expedientes/<uuid:expediente_id>/modalidad/', ModalidadViewSet.as_view({'get': 'modalidad_actual'}), name='expediente-modalidad'),
    path('expedientes/<uuid:expediente_id>/modalidad/elegibilidad/', ModalidadViewSet.as_view({'get': 'elegibilidad_ec'}), name='expediente-modalidad-elegibilidad'),
    path('expedientes/<uuid:expediente_id>/modalidad/cambiar/', ModalidadViewSet.as_view({'post': 'cambiar_modalidad'}), name='expediente-modalidad-cambiar'),
    path('modalidades/', ModalidadViewSet.as_view({'get': 'catalogo_modalidades'}), name='modalidades-catalogo'),
]
```

---

## 7. PERMISOS RBAC

```python
# backend/src/apps/authentication/permissions.py (actualización RBAC_MATRIX)

RBAC_MATRIX = {
    # ... existentes ...
    'expedientes:modalidad': {
        'GET': {  # modalidad actual + historial + elegibilidad
            'ESTUDIANTE': 'SCOPE_OWN',           # Solo su expediente
            'SECRETARIO_ABOGADO': 'SCOPE_FACULTAD',
            'ANALISTA_APOYO': 'SCOPE_FACULTAD',
            'DECANO': 'SCOPE_FACULTAD',
            'DIRECTOR_CARRERA': 'SCOPE_CARRERA',
            'ADMINISTRADOR': 'SCOPE_ALL',
        },
        'POST': {  # cambiar modalidad
            'SECRETARIO_ABOGADO': 'SCOPE_FACULTAD',  # Verifica elegibilidad
            'DECANO': 'SCOPE_FACULTAD',              # Autoriza cambio
            'ADMINISTRADOR': 'SCOPE_ALL',
        }
    },
    'modalidades': {  # catálogo
        'GET': {
            'ESTUDIANTE': 'SCOPE_OWN',
            'SECRETARIO_ABOGADO': 'SCOPE_FACULTAD',
            'DECANO': 'SCOPE_FACULTAD',
            'DIRECTOR_CARRERA': 'SCOPE_CARRERA',
            'ADMINISTRADOR': 'SCOPE_ALL',
        }
    },
}
```

---

## 8. INTEGRACIÓN FRONTEND

### 8.1 V-03: Nueva Solicitud (`NuevaSolicitudForm.tsx`)
```tsx
// Lógica: Solo muestra selector modalidad SI backend confirma elegibilidad EC
// 1. Al cargar: GET /expedientes/{id}/modalidad/elegibilidad/ (si ya tiene expediente)
// 2. Si elegible: mostrar RadioGroup [TIC (default), EC]
// 3. Si no elegible: mostrar solo TIC + mensaje "Examen Complexivo no disponible: requiere 2 reprobaciones + 3ra matrícula"
// 4. Al enviar: POST /expedientes/ con opcion_titulacion (backend valida)
```

### 8.2 V-04: Expediente Header (`ExpedienteHeader.tsx`)
```tsx
// Badge modalidad actual + enlace "Ver historial"
// Si rol ∈ {SECRETARIO_ABOGADO, DECANO, ADMINISTRADOR} y modalidad = TIC:
//   Botón "Verificar elegibilidad EC" → GET /elegibilidad/ → si true → "Autorizar cambio a EC"
```

### 8.3 V-08: Detalle Funcionario (`AccionesRapidas`)
```tsx
// Secretario: "Verificar elegibilidad EC" + "Autorizar cambio a EC" (si elegible)
// Decano: "Cambiar modalidad a EC" (decisión final)
// Admin: Ambos
```

### 8.4 Dashboards (`ModalidadPanel`)
```tsx
// Tarjetas: Total TIC, Total EC, % cada una
// Gráfico: Distribución por carrera/período/estado
// Admin/Decano: Historial cambios + KPI-MOD-08
```

---

## 9. KPIs MODALIDADES (PARA DASHBOARDS)

| ID | Nombre | Fórmula | Endpoint |
|----|--------|---------|----------|
| KPI-MOD-01 | Total TIC | `count(opcion_titulacion='TIC')` | `/indicadores/modalidades/` |
| KPI-MOD-02 | Total EC | `count(opcion_titulacion='EC')` | `/indicadores/modalidades/` |
| KPI-MOD-03 | % TIC / % EC | `(MOD-01/total)*100` | `/indicadores/modalidades/` |
| KPI-MOD-04 | Distribución carrera | `group by carrera_id, opcion_titulacion` | `?agrupar=carrera` |
| KPI-MOD-05 | Distribución período | `group by year(fecha_recepcion), opcion_titulacion` | `?agrupar=periodo` |
| KPI-MOD-06 | Elegibles EC | `count(estudiantes 2 reprobaciones + 3ra matrícula)` | `/indicadores/elegibilidad-ec/` |
| KPI-MOD-07 | Habilitados EC | `count(opcion_titulacion='EC' estado≠BORRADOR)` | `/indicadores/modalidades/` |
| KPI-MOD-08 | Cambios autorizados | `count(HistorialModalidad modalidad_nueva='EC')` | `/indicadores/cambios-modalidad/` |

---

## 10. PRUEBAS REQUERIDAS

| Test | Descripción |
|------|-------------|
| `test_crear_expediente_default_tic` | Estudiante crea expediente → modalidad = TIC por defecto |
| `test_crear_expediente_rechaza_ec` | Estudiante intenta crear con EC → 400 |
| `test_verificar_elegibilidad_ec_true` | Mock SGA retorna 2 reprobaciones + 3ra matrícula → elegible=true |
| `test_verificar_elegibilidad_ec_false` | Mock SGA retorna 1 reprobación → elegible=false |
| `test_cambiar_modalidad_tic_a_ec_autorizado` | Secretario verifica + Decano autoriza → cambio registrado + historial |
| `test_cambiar_modalidad_tic_a_ec_sin_elegibilidad` | Intento cambio sin elegibilidad → 400 |
| `test_cambiar_modalidad_ec_a_tic_rechazado` | Intento EC → TIC → 400 (no permitido) |
| `test_cambiar_modalidad_estado_invalido` | Expediente INFORME_EMITIDO → cambio → 400 |
| `test_historial_modalidad_inmutable` | Cambio registrado → HistorialModalidad inmutable (no editable) |
| `test_permisos_estudiante_no_cambia` | Estudiante POST /cambiar/ → 403 |
| `test_permisos_secretario_verifica` | Secretario GET /elegibilidad/ → 200 |
| `test_permisos_decano_autoriza` | Decano POST /cambiar/ → 200 |
| `test_kpi_mod_01_a_08` | KPIs modalidades calculados correctamente por ámbito |

---

## 11. VALIDACIÓN NORMATIVA REQUERIDA (ANTES DE IMPLEMENTAR)

**Checklist de validación con autoridad competente (Secretaría General / Decanato / Asesoría Jurídica):**

- [ ] **Art. 39 RRA-UNL**: Texto exacto confirmado → define TIC como ordinaria
- [ ] **Art. 40 RRA-UNL**: Texto exacto confirmado → define EC como excepcional
- [ ] **Art. 212 RRA-UNL**: Incisos a/b confirmados → procedimiento general + excepcional
- [ ] **Art. 216 RRA-UNL**: Requisitos elegibilidad ordinaria confirmados (100% vs 85%)
- [ ] **Art. 233 RRA-UNL**: Procedimiento modalidad excepcional confirmado
- [ ] **Actor verificador**: Secretario/a-Abogado/a confirmado (Art. 212)
- [ ] **Actor autorizador**: Decano/a confirmado (Art. 233)
- [ ] **Evidencia 3ra matrícula**: Documento oficial definido (resolución, acta, certificado)
- [ ] **Definición "unidad de titulación"**: Materia/código específico confirmado
- [ ] **Descartar "Proyecto de Emprendimiento"**: Confirmado no aplicar

**Sin esta validación firmada, NO SE IMPLEMENTA BE-06 ni FE-T301/302** (DEC-14, CA-G-01).

---

## 12. PRÓXIMOS PASOS INMEDIATOS

1. **Solicitar documento RRA-UNL vigente** (arts. 39, 40, 212, 216, 233) a autoridad competente
2. **Agendar reunión validación** con Secretaría General + Asesoría Jurídica + Decanato
3. **Documentar respuestas** a 11 puntos §11 en acta firmada
4. **Autorizar INC-03** (Modalidades Core) para Sprint +1
5. **Diseñar mock SGA** para elegibilidad EC (2 reprobaciones + 3ra matrícula)
6. **Crear migraciones** `opcion_titulacion` + `HistorialModalidad`