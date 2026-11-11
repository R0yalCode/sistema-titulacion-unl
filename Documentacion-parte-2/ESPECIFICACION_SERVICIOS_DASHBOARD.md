# ESPECIFICACIÓN DE SERVICIOS DASHBOARD — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `MATRIZ_INTEGRACION_KPIS_ENDPOINTS.md` + `ARQUITECTURA_DASHBOARDS_POR_ROL.md` + `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md`  

---

## 1. ARQUITECTURA GENERAL

### 1.1 Capa de Servicios (`backend/src/apps/indicadores/services/`)
```
indicadores/
├── __init__.py
├── indicadores.py              # Funciones base + utilidades compartidas
├── kpi_estudiante.py           # KPIs estudiante (KPI-EST-01 a 08)
├── kpi_secretaria.py           # KPIs secretaría carrera (KPI-SEC-01 a 08)
├── kpi_jurista.py              # KPIs secretario/analista (KPI-JUR-01 a 07)
├── kpi_decano.py               # KPIs decano (KPI-DEC-01 a 05)
├── kpi_director.py             # KPIs director carrera (KPI-DIR-01 a 07)
├── kpi_dependencia.py          # KPIs responsable dependencia (KPI-DEP-01 a 03)
├── kpi_admin.py                # KPIs admin (KPI-ADM-01 a 09)
├── kpi_modalidades.py          # KPIs modalidades (KPI-MOD-01 a 08)
└── kpi_general.py              # KPIs transversales (culminación, evolución)
```

### 1.2 Principios
- **Una función = Un KPI** (nombre: `get_kpi_<id>`)
- **Parámetros estandarizados**: `(user, ambito, filtros)` → retorna `dict` tipado
- **Sin lógica HTTP**: Solo consultas BD + cálculo
- **Reutilización**: `kpi_general` usado por múltiples roles
- **Tests unitarias** por función (casos 0, 1, N, vacíos)

---

## 2. SERVICIOS BASE (`indicadores.py`)

```python
# backend/src/apps/indicadores/services/indicadores.py

from datetime import date, datetime, timedelta
from typing import Optional
from django.db.models import Count, Avg, Q, F
from django.db.models.functions import TruncMonth
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import PeticionDocumental
from apps.verificacion.adapters.models import ChecklistVerification, ObservacionAccionable
from apps.resoluciones.adapters.models import InformeAptitud, DeclaratoriaAptitud
from apps.notificaciones.adapters.models import NotificacionInterna, EventoAuditoria
from apps.authentication.adapters.models import User, UserRole

def get_ambito_usuario(user) -> dict:
    """Deriva ámbito de consulta desde roles + atributos usuario (JWT)."""
    roles = user.get_roles()
    ambito = {'tipo': 'own', 'carrera_id': None, 'facultad_id': None}
    
    if 'ADMINISTRADOR' in roles:
        ambito['tipo'] = 'all'
    elif 'SECRETARIA_CARRERA' in roles or 'DIRECTOR_CARRERA' in roles:
        ambito['tipo'] = 'carrera'
        ambito['carrera_id'] = user.carrera_id
    elif 'SECRETARIO_ABOGADO' in roles or 'ANALISTA_APOYO' in roles or 'DECANO' in roles:
        ambito['tipo'] = 'facultad'
        ambito['facultad_id'] = user.facultad_id
    elif 'RESPONSABLE_DEPENDENCIA' in roles:
        ambito['tipo'] = 'asignado'
        # roles del usuario determinan dependencias emisoras
    # ESTUDIANTE → 'own' (default)
    
    return ambito

def filtrar_por_ambito(queryset, ambito, modelo='expediente'):
    """Aplica filtro ScopeFilterMixin equivalente en servicios."""
    if ambito['tipo'] == 'all':
        return queryset
    elif ambito['tipo'] == 'own':
        if modelo == 'expediente':
            return queryset.filter(estudiante_id=ambito.get('user_id'))
        elif modelo == 'peticion':
            return queryset.filter(expediente__estudiante_id=ambito.get('user_id'))
    elif ambito['tipo'] == 'carrera':
        carrera_id = ambito.get('carrera_id')
        if modelo == 'expediente':
            return queryset.filter(carrera_id=carrera_id)
        elif modelo == 'peticion':
            return queryset.filter(expediente__carrera_id=carrera_id)
    elif ambito['tipo'] == 'facultad':
        facultad_id = ambito.get('facultad_id')
        if modelo == 'expediente':
            return queryset.filter(facultad_id=facultad_id)
        elif modelo == 'peticion':
            return queryset.filter(expediente__facultad_id=facultad_id)
    elif ambito['tipo'] == 'asignado':
        # Requiere lógica SCOPE_ASIGNADO (ver INC-01 TASK-P0-002)
        # Filtrar peticiones por dependencia_emisora ∈ roles_usuario
        pass
    return queryset.none()

def get_periodo_filtro(desde: Optional[date], hasta: Optional[date]) -> Q:
    """Construye Q para filtro fecha_recepcion en rango."""
    q = Q()
    if desde:
        q &= Q(fecha_recepcion__date__gte=desde)
    if hasta:
        q &= Q(fecha_recepcion__date__lte=hasta)
    return q

def serie_mensual_completa(queryset, campo_fecha: str, meses: int = 12) -> list:
    """Genera serie temporal con meses en 0 (generate_series equivalente en Python)."""
    desde = (timezone.now() - timedelta(days=meses * 30)).replace(day=1)
    # Implementar con TruncMonth + generate_series SQL raw para performance
    # Placeholder: retorna lista dicts [{'mes': '2026-01', 'total': 5}, ...]
    pass
```

---

## 3. SERVICIOS POR ROL (EJEMPLOS REPRESENTATIVOS)

### 3.1 Estudiante (`kpi_estudiante.py`)
```python
# backend/src/apps/indicadores/services/kpi_estudiante.py

from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import PeticionDocumental
from apps.verificacion.adapters.models import ChecklistVerification, ObservacionAccionable
from apps.notificaciones.adapters.models import NotificacionInterna
from .indicadores import get_ambito_usuario, filtrar_por_ambito

def get_kpi_est_01_estado_actual(user) -> dict:
    """KPI-EST-01: Estado actual del trámite."""
    expediente = ExpedienteTitulacion.objects.filter(
        estudiante=user, activa=True
    ).order_by('-fecha_creacion').first()
    return {'estado': expediente.estado if expediente else None, 'expediente_id': expediente.id if expediente else None}

def get_kpi_est_02_requisitos_pendientes(user) -> int:
    """KPI-EST-02: Requisitos pendientes de entrega."""
    return PeticionDocumental.objects.filter(
        expediente__estudiante=user,
        expediente__activa=True,
        estado_peticion__in=['PENDIENTE', 'SOLICITADO']
    ).count()

def get_kpi_est_03_requisitos_observados(user) -> list:
    """KPI-EST-03: Requisitos observados con motivo."""
    observaciones = ObservacionAccionable.objects.filter(
        expediente__estudiante=user,
        expediente__activa=True,
        resuelta=False
    ).select_related('peticion__requisito').values(
        'peticion__requisito__codigo_requisito',
        'peticion__requisito__nombre',
        'motivo_observacion'
    )
    return list(observaciones)

def get_kpi_est_05_notificaciones_no_leidas(user) -> int:
    """KPI-EST-05: Notificaciones sin leer."""
    return NotificacionInterna.objects.filter(usuario_destino=user, leida=False).count()

def get_kpi_est_06_fecha_limite(user) -> dict:
    """KPI-EST-06: Fecha límite de atención + días restantes."""
    expediente = ExpedienteTitulacion.objects.filter(
        estudiante=user, activa=True
    ).order_by('-fecha_creacion').first()
    if expediente and expediente.fecha_limite_atencion:
        from django.utils import timezone
        dias_restantes = (expediente.fecha_limite_atencion.date() - timezone.now().date()).days
        return {
            'fecha_limite': expediente.fecha_limite_atencion,
            'dias_restantes': max(0, dias_restantes),
            'vencido': dias_restantes < 0
        }
    return {}

def get_kpi_est_07_progreso_checklist(user) -> dict:
    """KPI-EST-07: Progreso checklist (% verificado)."""
    expediente = ExpedienteTitulacion.objects.filter(
        estudiante=user, activa=True
    ).order_by('-fecha_creacion').first()
    if not expediente:
        return {'porcentaje': 0, 'verificados': 0, 'total': 5}
    verificados = ChecklistVerification.objects.filter(
        expediente=expediente, estado_verificacion='VERIFICADO'
    ).count()
    return {'porcentaje': round(verificados / 5 * 100), 'verificados': verificados, 'total': 5}
```

### 3.2 Secretaría Carrera (`kpi_secretaria.py`)
```python
# backend/src/apps/indicadores/services/kpi_secretaria.py

from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import PeticionDocumental
from apps.verificacion.adapters.models import ChecklistVerification
from .indicadores import get_ambito_usuario, filtrar_por_ambito, get_periodo_filtro
from django.utils import timezone
from django.db.models import Count

def get_kpi_sec_01_en_atencion(user) -> int:
    """KPI-SEC-01: Expedientes en atención (carrera)."""
    ambito = get_ambito_usuario(user)
    qs = filtrar_por_ambito(ExpedienteTitulacion.objects.filter(activa=True), ambito)
    return qs.filter(estado__in=['ENVIADA', 'EN_VERIFICACION', 'OBSERVADA']).count()

def get_kpi_sec_02_plazo_vencido(user) -> int:
    """KPI-SEC-02: Expedientes con plazo vencido."""
    ambito = get_ambito_usuario(user)
    qs = filtrar_por_ambito(ExpedienteTitulacion.objects.filter(activa=True), ambito)
    return qs.exclude(estado__in=['DECLARADA_APTA', 'CANCELADA', 'BORRADOR']).filter(
        fecha_limite_atencion__lt=timezone.now()
    ).count()

def get_kpi_sec_03_certificados_emitir(user) -> int:
    """KPI-SEC-03: Certificados por emitir (peticiones SECRETARIA_CARRERA)."""
    ambito = get_ambito_usuario(user)
    qs = filtrar_por_ambito(PeticionDocumental.objects.all(), ambito, modelo='peticion')
    return qs.filter(
        dependencia_emisora='SECRETARIA_CARRERA',
        estado_peticion__in=['PENDIENTE', 'SOLICITADO']
    ).count()

def get_kpi_sec_04_validacion_pendiente(user) -> int:
    """KPI-SEC-04: Documentos pendientes validación (checklist PENDIENTE + petición CARGADO)."""
    ambito = get_ambito_usuario(user)
    qs = filtrar_por_ambito(ChecklistVerification.objects.all(), ambito, modelo='peticion')
    return qs.filter(
        estado_verificacion='PENDIENTE',
        peticion__estado_peticion='CARGADO'
    ).count()
```

### 3.3 Modalidades (`kpi_modalidades.py`)
```python
# backend/src/apps/indicadores/services/kpi_modalidades.py

from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.adapters.models import HistorialModalidad  # Nuevo modelo INC-03
from .indicadores import get_ambito_usuario, filtrar_por_ambito
from django.db.models import Count

def get_kpi_mod_01_total_tic(user, agrupar: str = None) -> dict:
    """KPI-MOD-01: Total Trabajo Integración Curricular."""
    ambito = get_ambito_usuario(user)
    qs = filtrar_por_ambito(ExpedienteTitulacion.objects.filter(activa=True), ambito)
    qs = qs.filter(opcion_titulacion='TIC')
    if agrupar == 'carrera':
        return dict(qs.values_list('carrera_id').annotate(total=Count('id')))
    elif agrupar == 'periodo':
        # Requiere año fecha_recepcion
        pass
    return {'total': qs.count()}

def get_kpi_mod_02_total_ec(user, agrupar: str = None) -> dict:
    """KPI-MOD-02: Total Examen Complexivo."""
    ambito = get_ambito_usuario(user)
    qs = filtrar_por_ambito(ExpedienteTitulacion.objects.filter(activa=True), ambito)
    qs = qs.filter(opcion_titulacion='EC')
    if agrupar == 'carrera':
        return dict(qs.values_list('carrera_id').annotate(total=Count('id')))
    return {'total': qs.count()}

def get_kpi_mod_06_elegibles_ec(user) -> int:
    """KPI-MOD-06: Estudiantes elegibles EC (2 reprobaciones + 3ra matrícula).
    Requiere mock SGA — implementar en servicio separado `verificar_elegibilidad_ec()`.
    """
    # Placeholder: consulta a mock SGA + cruce con expedientes
    pass

def get_kpi_mod_07_habilitados_ec(user) -> int:
    """KPI-MOD-07: Expedientes habilitados EC (ya en modalidad EC, no BORRADOR)."""
    ambito = get_ambito_usuario(user)
    return filtrar_por_ambito(
        ExpedienteTitulacion.objects.filter(activa=True, opcion_titulacion='EC')
    ).exclude(estado='BORRADOR').count()

def get_kpi_mod_08_cambios_autorizados(user) -> int:
    """KPI-MOD-08: Cambios autorizados a EC."""
    ambito = get_ambito_usuario(user)
    qs = filtrar_por_ambito(HistorialModalidad.objects.all(), ambito, modelo='expediente')
    return qs.filter(modalidad_nueva='EC').count()
```

---

## 4. VIEWSETS ENDPOINTS (`indicadores/adapters/views.py`)

```python
# backend/src/apps/indicadores/adapters/views.py

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from apps.authentication.adapters.permissions import HasRolePermission
from .services import (
    kpi_estudiante, kpi_secretaria, kpi_jurista, kpi_decano,
    kpi_director, kpi_dependencia, kpi_admin, kpi_modalidades, kpi_general
)
from .serializers import DashboardMeSerializer, IndicadoresModalidadesSerializer

class DashboardViewSet(viewsets.ViewSet):
    """GET /api/v1/dashboard/me/ - Dashboard unificado por rol."""
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    rbac_resource = 'dashboard'
    
    def get_ambito(self, request):
        from .services.indicadores import get_ambito_usuario
        ambito = get_ambito_usuario(request.user)
        ambito['user_id'] = request.user.pk
        return ambito
    
    def list(self, request):
        """Componer dashboard según rol principal."""
        user = request.user
        roles = user.get_roles()
        rol_principal = self._get_rol_principal(roles)
        ambito = self.get_ambito(request)
        
        # Secciones base
        secciones = {
            'resumen': self._get_resumen(rol_principal, user, ambito),
            'tarjetas_p0': self._get_tarjetas_p0(rol_principal, user, ambito),
            'grafico_principal': self._get_grafico_principal(rol_principal, user, ambito),
            'tabla_trabajo': self._get_tabla_trabajo(rol_principal, user, ambito, request),
            'actividad_reciente': self._get_actividad_reciente(user, ambito),
            'notificaciones_no_leidas': kpi_estudiante.get_kpi_est_05_notificaciones_no_leidas(user),
            'modalidad_titulacion': self._get_modalidad_dashboard(user, ambito),
        }
        
        data = {
            'generado_en': timezone.now(),
            'ambito': ambito,
            'rol_principal': rol_principal,
            'secciones': secciones,
        }
        return Response(DashboardMeSerializer(data).data)
    
    def _get_rol_principal(self, roles):
        orden = ['ADMINISTRADOR', 'SECRETARIO_ABOGADO', 'ANALISTA_APOYO', 'DECANO', 
                 'SECRETARIA_CARRERA', 'DIRECTOR_CARRERA', 'ESTUDIANTE']
        for r in orden:
            if r in roles:
                return r
        return 'ESTUDIANTE'
    
    def _get_resumen(self, rol, user, ambito):
        # Retorna dict con 3 KPIs clave + alertas + acciones_pendientes
        pass
    
    def _get_tarjetas_p0(self, rol, user, ambito):
        # Mapea rol → lista tarjetas (ver ARQUITECTURA_DASHBOARDS_POR_ROL.md §2)
        pass
    
    def _get_grafico_principal(self, rol, user, ambito):
        # Retorna {tipo, datos, titulo} para recharts
        pass
    
    def _get_tabla_trabajo(self, rol, user, ambito, request):
        # Paginada, con columnas y acciones por rol
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 10)), 50)
        pass
    
    def _get_actividad_reciente(self, user, ambito):
        # Últimos 10 EventoAuditoria del ámbito
        from apps.notificaciones.adapters.models import EventoAuditoria
        return EventoAuditoria.objects.filter(...).order_by('-timestamp')[:10].values(...)
    
    def _get_modalidad_dashboard(self, user, ambito):
        # Modalidad actual + elegibilidad + historial (si rol autorizado)
        pass


class IndicadoresViewSet(viewsets.ViewSet):
    """Endpoints analíticos P1/P2."""
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    
    @action(detail=False, methods=['get'], url_path='modalidades')
    def modalidades(self, request):
        """GET /api/v1/indicadores/modalidades/"""
        rbac_resource = 'indicadores:modalidades'
        # Verificar permiso via HasRolePermission
        user = request.user
        ambito = get_ambito_usuario(user)
        agrupar = request.query_params.get('agrupar')
        
        data = {
            'total_tic': kpi_modalidades.get_kpi_mod_01_total_tic(user, agrupar),
            'total_ec': kpi_modalidades.get_kpi_mod_02_total_ec(user, agrupar),
            'porcentaje_tic': ...,  # calculado
            'porcentaje_ec': ...,
            'por_carrera': kpi_modalidades.get_kpi_mod_01_total_tic(user, 'carrera') if agrupar == 'carrera' else None,
            'por_periodo': ...,  # si agrupar == 'periodo'
            'elegibles_ec': kpi_modalidades.get_kpi_mod_06_elegibles_ec(user),
            'habilitados_ec': kpi_modalidades.get_kpi_mod_07_habilitados_ec(user),
            'cambios_autorizados': kpi_modalidades.get_kpi_mod_08_cambios_autorizados(user),
        }
        return Response(IndicadoresModalidadesSerializer(data).data)
    
    @action(detail=False, methods=['get'], url_path='culminacion')
    def culminacion(self, request):
        """GET /api/v1/indicadores/culminacion/"""
        # Tasa culminación + tiempo promedio por cohorte
        pass
    
    @action(detail=False, methods=['get'], url_path='evolucion')
    def evolucion(self, request):
        """GET /api/v1/indicadores/evolucion/"""
        # Serie mensual
        pass
    
    @action(detail=False, methods=['get'], url_path='elegibilidad-ec')
    def elegibilidad_ec(self, request):
        """GET /api/v1/indicadores/elegibilidad-ec/"""
        # Solo Secretario, Decano, Admin
        pass
```

---

## 5. SERIALIZERS (`indicadores/adapters/serializers.py`)

```python
# backend/src/apps/indicadores/adapters/serializers.py

from rest_framework import serializers

class AmbitoSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=['own', 'carrera', 'facultad', 'all', 'asignado'])
    carrera_id = serializers.UUIDField(allow_null=True)
    facultad_id = serializers.UUIDField(allow_null=True)

class TarjetaKPISerializer(serializers.Serializer):
    titulo = serializers.CharField()
    valor = serializers.CharField()  # string para formateo frontend
    variante = serializers.ChoiceField(choices=['neutro', 'info', 'success', 'warning', 'danger'])
    accion = serializers.DictField(required=False)  # {label, endpoint}

class GraficoSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=['bar', 'line', 'pie', 'progress'])
    datos = serializers.DictField()
    titulo = serializers.CharField()

class TablaTrabajoSerializer(serializers.Serializer):
    columnas = serializers.ListField(child=serializers.DictField())
    filas = serializers.ListField(child=serializers.DictField())
    paginacion = serializers.DictField()
    acciones = serializers.ListField(child=serializers.DictField(), required=False)

class DashboardMeSerializer(serializers.Serializer):
    generado_en = serializers.DateTimeField()
    ambito = AmbitoSerializer()
    rol_principal = serializers.CharField()
    secciones = serializers.DictField(child=serializers.JSONField())

class IndicadoresModalidadesSerializer(serializers.Serializer):
    total_tic = serializers.IntegerField()
    total_ec = serializers.IntegerField()
    porcentaje_tic = serializers.DecimalField(max_digits=5, decimal_places=2)
    porcentaje_ec = serializers.DecimalField(max_digits=5, decimal_places=2)
    por_carrera = serializers.DictField(required=False)  # {carrera_id: {tic, ec}}
    por_periodo = serializers.DictField(required=False)
    por_estado = serializers.DictField(required=False)
    elegibles_ec = serializers.IntegerField()
    habilitados_ec = serializers.IntegerField()
    cambios_autorizados = serializers.IntegerField()
```

---

## 6. PERMISOS RBAC (ACTUALIZACIÓN `authentication/permissions.py`)

```python
# Añadir a RBAC_MATRIX en authentication/permissions.py

RBAC_MATRIX = {
    # ... existentes ...
    'dashboard': {
        'GET': {
            'ESTUDIANTE': 'SCOPE_OWN',
            'SECRETARIA_CARRERA': 'SCOPE_CARRERA',
            'SECRETARIO_ABOGADO': 'SCOPE_FACULTAD',
            'ANALISTA_APOYO': 'SCOPE_FACULTAD',
            'DECANO': 'SCOPE_FACULTAD',
            'DIRECTOR_CARRERA': 'SCOPE_CARRERA',
            'RESPONSABLE_DEPENDENCIA': 'SCOPE_ASIGNADO',  # Requiere TASK-P0-002
            'ADMINISTRADOR': 'SCOPE_ALL',
        }
    },
    'indicadores:modalidades': {
        'GET': {
            'SECRETARIO_ABOGADO': 'SCOPE_FACULTAD',
            'ANALISTA_APOYO': 'SCOPE_FACULTAD',
            'DECANO': 'SCOPE_FACULTAD',
            'DIRECTOR_CARRERA': 'SCOPE_CARRERA',
            'ADMINISTRADOR': 'SCOPE_ALL',
        }
    },
    'indicadores:culminacion': {
        'GET': {
            'DECANO': 'SCOPE_FACULTAD',
            'DIRECTOR_CARRERA': 'SCOPE_CARRERA',
            'ADMINISTRADOR': 'SCOPE_ALL',
        }
    },
    'indicadores:evolucion': {
        'GET': {
            'DECANO': 'SCOPE_FACULTAD',
            'DIRECTOR_CARRERA': 'SCOPE_CARRERA',
            'ADMINISTRADOR': 'SCOPE_ALL',
        }
    },
    'indicadores:elegibilidad-ec': {
        'GET': {
            'SECRETARIO_ABOGADO': 'SCOPE_FACULTAD',
            'DECANO': 'SCOPE_FACULTAD',
            'ADMINISTRADOR': 'SCOPE_ALL',
        }
    },
}

# Añadir a ROW_TO_SCOPE en core/adapters/scope_filter.py
ROW_TO_SCOPE = {
    # ... existentes ...
    'RESPONSABLE_DEPENDENCIA': 'SCOPE_ASIGNADO',  # Requiere TASK-P1-004
}
```

---

## 7. URLS (`indicadores/adapters/urls.py`)

```python
# backend/src/apps/indicadores/adapters/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, IndicadoresViewSet

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'indicadores', IndicadoresViewSet, basename='indicadores')

urlpatterns = [
    path('', include(router.urls)),
    # Rutas explícitas para acciones @action:
    path('dashboard/me/', DashboardViewSet.as_view({'get': 'list'}), name='dashboard-me'),
    path('indicadores/modalidades/', IndicadoresViewSet.as_view({'get': 'modalidades'}), name='indicadores-modalidades'),
    path('indicadores/culminacion/', IndicadoresViewSet.as_view({'get': 'culminacion'}), name='indicadores-culminacion'),
    path('indicadores/evolucion/', IndicadoresViewSet.as_view({'get': 'evolucion'}), name='indicadores-evolucion'),
    path('indicadores/elegibilidad-ec/', IndicadoresViewSet.as_view({'get': 'elegibilidad_ec'}), name='indicadores-elegibilidad-ec'),
]
```

**Registrar en `config/urls.py`:**
```python
path('api/v1/', include('apps.indicadores.adapters.urls')),
```

---

## 8. TESTS UNITARIAS (`indicadores/tests/test_indicadores.py`)

```python
# backend/src/apps/indicadores/tests/test_indicadores.py

import pytest
from datetime import date, timedelta
from django.utils import timezone
from apps.indicadores.services import kpi_estudiante, kpi_secretaria, kpi_modalidades
from apps.expedientes.tests.factories import ExpedienteFactory, PeticionFactory
from apps.authentication.tests.factories import UserFactory

@pytest.mark.django_db
class TestKPIEstudiante:
    def test_kpi_est_01_sin_expediente(self, user_estudiante):
        result = kpi_estudiante.get_kpi_est_01_estado_actual(user_estudiante)
        assert result['estado'] is None
    
    def test_kpi_est_01_con_expediente(self, user_estudiante, expediente_borrador):
        result = kpi_estudiante.get_kpi_est_01_estado_actual(user_estudiante)
        assert result['estado'] == 'BORRADOR'
        assert result['expediente_id'] == str(expediente_borrador.id)
    
    def test_kpi_est_02_cero_pendientes(self, user_estudiante):
        assert kpi_estudiante.get_kpi_est_02_requisitos_pendientes(user_estudiante) == 0
    
    def test_kpi_est_02_con_pendientes(self, user_estudiante, expediente_con_peticiones):
        # 3 PENDIENTE, 2 SOLICITADO
        assert kpi_estudiante.get_kpi_est_02_requisitos_pendientes(user_estudiante) == 5
    
    def test_kpi_est_07_progreso_checklist(self, user_estudiante, expediente_con_checklist):
        # 3 verificados de 5
        result = kpi_estudiante.get_kpi_est_07_progreso_checklist(user_estudiante)
        assert result['verificados'] == 3
        assert result['porcentaje'] == 60

@pytest.mark.django_db
class TestKPISecretaria:
    def test_kpi_sec_01_en_atencion(self, user_secretaria, expedientes_carrera):
        # 4 ENVIADA, 2 EN_VERIFICACION, 1 OBSERVADA
        assert kpi_secretaria.get_kpi_sec_01_en_atencion(user_secretaria) == 7
    
    def test_kpi_sec_02_plazo_vencido(self, user_secretaria, expedientes_vencidos):
        assert kpi_secretaria.get_kpi_sec_02_plazo_vencido(user_secretaria) == 3

@pytest.mark.django_db
class TestKPIModalidades:
    def test_kpi_mod_01_total_tic(self, user_admin, expedientes_modalidades):
        # 15 TIC, 3 EC
        result = kpi_modalidades.get_kpi_mod_01_total_tic(user_admin)
        assert result['total'] == 15
    
    def test_kpi_mod_03_porcentajes(self, user_admin, expedientes_modalidades):
        # 15 TIC, 3 EC → 83.33% / 16.67%
        pass  # Implementar test porcentaje
```

---

## 9. CONSUMO FRONTEND (`frontend/src/features/dashboard/queries.ts`)

```typescript
// frontend/src/features/dashboard/queries.ts (actualización)

import { useQuery } from '@tanstack/react-query'
import { request } from '@/api/client'
import type { ApiRequestError } from '@/api/errors'

export interface DashboardMeResponse {
  generado_en: string
  ambito: { tipo: string; carrera_id: string | null; facultad_id: string | null }
  rol_principal: string
  secciones: {
    resumen: { kpi_clave: number; alertas: number; acciones_pendientes: number }
    tarjetas_p0: Array<{ titulo: string; valor: string; variante: string; accion?: { label: string; endpoint: string } }>
    grafico_principal: { tipo: 'bar' | 'line' | 'pie' | 'progress'; datos: any; titulo: string }
    tabla_trabajo: { columnas: any[]; filas: any[]; paginacion: any; acciones?: any[] }
    actividad_reciente: any[]
    notificaciones_no_leidas: number
    modalidad_titulacion: { actual: 'TIC' | 'EC'; elegible_ec: boolean; historial: any[] }
  }
}

export function useDashboardMe() {
  return useQuery<DashboardMeResponse, ApiRequestError>({
    queryKey: ['dashboard', 'me'],
    queryFn: () => request<DashboardMeResponse>('/api/v1/dashboard/me/'),
    staleTime: 30_000, // 30 segundos
    retry: false,
  })
}

// Hooks específicos por sección (para invalidación granular)
export function useTarjetasP0() {
  const { data } = useDashboardMe()
  return data?.secciones.tarjetas_p0 ?? []
}

export function useGraficoPrincipal() {
  const { data } = useDashboardMe()
  return data?.secciones.grafico_principal
}

export function useTablaTrabajo() {
  const { data } = useDashboardMe()
  return data?.secciones.tabla_trabajo
}

export function useModalidadDashboard() {
  const { data } = useDashboardMe()
  return data?.secciones.modalidad_titulacion
}
```

**Actualizar `StudentDashboardPage.tsx`:**
```tsx
// Reemplazar useBandejaEstudiante + useNotificaciones por:
const dashboard = useDashboardMe()
const tarjetas = useTarjetasP0()
const grafico = useGraficoPrincipal()
const tabla = useTablaTrabajo()
const modalidad = useModalidadDashboard()
// Renderizar usando datos unificados
```

---

## 10. CRITERIOS ACEPTACIÓN SERVICIOS DASHBOARD

1. **Endpoint único** `/dashboard/me/` compone todo según rol (no 7 endpoints)
2. **Servicios centralizados** en `indicadores/services/` — una función por KPI
3. **Ámbito derivado del usuario** (JWT → roles + carrera_id/facultad_id), nunca de parámetros cliente
4. **Agregaciones en BD** (Count, Avg, TruncMonth) — sin N+1, sin `len(queryset)`
5. **Filtros whitelist**: `estado` ∈ enum real, fechas con límite máx, `meses ≤ 24`
6. **Respuesta consistente** + `Cache-Control: no-store`
7. **Permisos RBAC** por recurso `dashboard` + `indicadores:*`
8. **Tests unitarias** ≥ 90% cobertura app `indicadores`
9. **Frontend consume** `/dashboard/me/` con TanStack Query (staleTime 30s)
10. **Accesibilidad AA** en componentes dashboard (ya en UI Kit)

---

## 11. PRÓXIMOS PASOS (INC-04)

1. Crear app `indicadores` + estructura carpetas
2. Migrar fórmulas de `INFORME_DISENO_KPI.md` §6 a `services/*.py`
3. Implementar `DashboardViewSet` + `IndicadoresViewSet`
4. Registrar permisos en `RBAC_MATRIX` + `ROW_TO_SCOPE`
5. Tests unitarias fórmulas (casos 0, 1, N, vacíos)
6. Integrar frontend `StudentDashboardPage` → `useDashboardMe()`
7. Extender a dashboards funcionario (INC-07)