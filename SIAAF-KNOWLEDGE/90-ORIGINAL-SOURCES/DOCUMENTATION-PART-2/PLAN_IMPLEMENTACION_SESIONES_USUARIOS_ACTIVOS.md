# PLAN DE IMPLEMENTACIÓN: SESIONES Y USUARIOS ACTIVOS — SGT-SIAAF

**Versión:** 1.0  
**Fecha:** 2026-11-09  
**Fuente:** `PLAN_MAESTRO_IMPLEMENTACION_SGT_SIAAF.md` (INC-02) + Auditoría Seguridad (VULN-005, CTRL-004/005/006)  

---

## 1. PROBLEMA ACTUAL

**JWT Stateless sin registro de sesiones verificable:**
- Access token: 30 min (HS256, `JWT_SIGNING_KEY` separada ✅)
- Refresh token: 24h fijo, **sin rotación** (`ROTATE_REFRESH_TOKENS=False`)
- **Sin expiración por inactividad** (sliding window)
- **Sin revocación en logout** (blocklist)
- **Sin tabla de sesiones** → imposible métricas: "usuarios activos últimos 15 min", "sesiones vigentes/revocadas"
- `User.last_login` solo actualiza en admin Django, no en API JWT

---

## 2. OBJETIVOS

1. **Mecanismo verificable de sesiones** con: ID sesión, usuario, inicio, última actividad, expiración, revocación, estado
2. **Diferenciar**: registrados vs habilitados vs login hoy vs activos 15 min vs sesiones vigentes vs revocadas
3. **Estrategia eficiente**: medir actividad sin escritura en cada petición (batch/async)
4. **Reutilizar estructuras**: `EventoAuditoria` (ya tiene IP, usuario, timestamp, acción)
5. **Cerrar VULN-005** (refresh tokens huérfanos) y habilitar métricas KPI-ADM-09

---

## 3. ARQUITECTURA PROPUESTA

### 3.1 Nuevo Modelo: `SesionUsuario`
```python
# backend/src/apps/authentication/adapters/models.py (adición)

class SesionUsuario(models.Model):
    """Registro verificable de sesiones de usuario (JWT + refresh)."""
    
    ESTADO_VIGENTE = 'VIGENTE'
    ESTADO_EXPIRADA = 'EXPIRADA'
    ESTADO_REVOCADA = 'REVOCADA'
    ESTADO_CERRADA = 'CERRADA'  # Logout explícito
    
    ESTADOS_CHOICES = [
        (ESTADO_VIGENTE, 'Vigente'),
        (ESTADO_EXPIRADA, 'Expirada'),
        (ESTADO_REVOCADA, 'Revocada'),
        (ESTADO_CERRADA, 'Cerrada por logout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='sesiones',
    )
    refresh_token_jti = models.CharField(max_length=255, unique=True, db_index=True)  # JWT ID del refresh
    access_token_jti = models.CharField(max_length=255, db_index=True)  # JWT ID del access actual
    ip_origen = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_ultima_actividad = models.DateTimeField(auto_now=True)  # Se actualiza vía middleware async
    fecha_expiracion = models.DateTimeField()  # Basada en refresh lifetime (24h o sliding)
    fecha_revocacion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=16,
        choices=ESTADOS_CHOICES,
        default=ESTADO_VIGENTE,
        db_index=True,
    )
    revocada_por = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sesiones_revocadas',
    )
    motivo_revocacion = models.CharField(max_length=128, blank=True)  # 'logout', 'admin', 'expirada', 'rotacion'
    
    class Meta:
        indexes = [
            models.Index(fields=['usuario', 'estado'], name='idx_sesion_user_estado'),
            models.Index(fields=['fecha_ultima_actividad'], name='idx_sesion_ultima_act'),
            models.Index(fields=['fecha_expiracion'], name='idx_sesion_expiracion'),
        ]
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Sesión {self.id} - {self.usuario} ({self.estado})"
    
    @property
    def esta_vigente(self) -> bool:
        ahora = timezone.now()
        return (
            self.estado == self.ESTADO_VIGENTE 
            and self.fecha_expiracion > ahora
        )
    
    @property
    def minutos_inactividad(self) -> int:
        if self.fecha_ultima_actividad:
            return int((timezone.now() - self.fecha_ultima_actividad).total_seconds() / 60)
        return 0
```

### 3.2 Extensión JWT: Claims `jti` (JWT ID)
```python
# backend/src/apps/authentication/adapters/serializers.py (modificación)

class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['cedula'] = user.cedula
        token['roles'] = user.get_roles()
        # NUEVO: jti único por par access/refresh
        token['jti'] = uuid.uuid4().hex
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        # Crear/actualizar SesionUsuario al login exitoso
        refresh = self.get_token(self.user)
        access = refresh.access_token
        
        SesionUsuario.objects.create(
            usuario=self.user,
            refresh_token_jti=refresh['jti'],
            access_token_jti=access['jti'],
            ip_origen=resolver_ip_cliente(self.context['request']),
            user_agent=self.context['request'].META.get('HTTP_USER_AGENT', ''),
            fecha_expiracion=timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        )
        return data
```

### 3.3 Middleware Actualización Actividad (Batch/Async)
```python
# backend/src/core/adapters/middleware.py (nuevo o extensión)

class SesionActividadMiddleware:
    """
    Actualiza fecha_ultima_actividad de SesionUsuario SIN escritura en cada request.
    Usa cache Redis (django-cache) con TTL 5 min para batch updates.
    """
    
    CACHE_PREFIX = 'sesion_actividad_'
    BATCH_TTL = 300  # 5 minutos
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Solo para requests autenticados con JWT válido
        if hasattr(request, 'user') and request.user.is_authenticated:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                access_token = auth_header[7:]
                try:
                    # Decodificar sin verificar (solo extraer jti + exp)
                    payload = jwt_decode_handler(access_token)
                    jti = payload.get('jti')
                    if jti:
                        cache_key = f"{self.CACHE_PREFIX}{jti}"
                        # Guardar timestamp en cache (no BD)
                        cache.set(cache_key, timezone.now(), self.BATCH_TTL)
                except Exception:
                    pass  # Token inválido → middleware auth lo rechazará después
        
        return response

# Task periódica (Celery beat / cron cada 5 min) para vaciar cache a BD:
def actualizar_actividad_sesiones_batch():
    """Vacía cache de actividad a SesionUsuario.fecha_ultima_actividad."""
    # Implementar con django-redis: scan keys + bulk_update
    pass
```

### 3.4 Configuración JWT Hardening (VULN-005)
```python
# backend/src/config/settings/base.py (modificación SIMPLE_JWT)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=24),
    'ROTATE_REFRESH_TOKENS': True,           # NUEVO: rota en cada refresh
    'BLACKLIST_AFTER_ROTATION': True,        # NUEVO: añade anterior a blocklist
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': JWT_SIGNING_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    # Sliding tokens alternativa (Opción B si no se quiere rotación):
    # 'SLIDING_TOKEN_LIFETIME': timedelta(days=7),
    # 'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
```

**Requiere:** `rest_framework_simplejwt.token_blacklist` en `INSTALLED_APPS` + migración.

### 3.5 Endpoint Logout con Revocación
```python
# backend/src/apps/authentication/adapters/views.py (nuevo)

class LogoutView(APIView):
    """POST /api/v1/auth/logout/ - Revoca refresh token actual."""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token requerido.'}, status=400)
        
        try:
            token = RefreshToken(refresh_token)
            jti = token['jti']
            
            # Marcar sesión como cerrada
            sesion = SesionUsuario.objects.filter(
                refresh_token_jti=jti,
                usuario=request.user,
                estado=SesionUsuario.ESTADO_VIGENTE
            ).first()
            
            if sesion:
                sesion.estado = SesionUsuario.ESTADO_CERRADA
                sesion.fecha_revocacion = timezone.now()
                sesion.motivo_revocacion = 'logout'
                sesion.save(update_fields=['estado', 'fecha_revocacion', 'motivo_revocacion'])
            
            # Añadir a blocklist (simplejwt token_blacklist)
            token.blacklist()
            
            return Response({'detail': 'Sesión cerrada correctamente.'}, status=200)
        except TokenError:
            return Response({'detail': 'Token inválido o ya revocado.'}, status=400)
```

### 3.6 Refresh Token View Personalizado
```python
# backend/src/apps/authentication/adapters/views.py (extensión)

class CustomTokenRefreshView(TokenRefreshView):
    """Rotación + actualización SesionUsuario + blocklist anterior."""
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Obtener jti del refresh anterior
        old_refresh = request.data.get('refresh')
        old_token = RefreshToken(old_refresh)
        old_jti = old_token['jti']
        
        # Respuesta estándar (nuevo access + nuevo refresh rotado)
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            new_refresh = response.data.get('refresh')
            new_token = RefreshToken(new_refresh)
            new_jti = new_token['jti']
            new_access_jti = AccessToken(response.data['access'])['jti']
            
            # Actualizar SesionUsuario: nuevo jti + access_jti
            SesionUsuario.objects.filter(
                refresh_token_jti=old_jti,
                usuario=request.user
            ).update(
                refresh_token_jti=new_jti,
                access_token_jti=new_access_jti,
                fecha_ultima_actividad=timezone.now(),
            )
        
        return response
```

---

## 4. MÉTRICAS USUARIOS ACTIVOS (KPI-ADM-09)

### 4.1 Definiciones Operativas
| Métrica | Definición Técnica | Query |
|---------|-------------------|-------|
| **Usuarios registrados** | `count(User)` | `User.objects.count()` |
| **Usuarios habilitados** | `count(User is_active=True)` | `User.objects.filter(is_active=True).count()` |
| **Usuarios login hoy** | `count(DISTINCT usuario) WHERE fecha_inicio >= today()` | `SesionUsuario.objects.filter(fecha_inicio__date=timezone.now().date()).values('usuario').distinct().count()` |
| **Usuarios activos 15 min** | `count(DISTINCT usuario) WHERE fecha_ultima_actividad >= now() - 15min` | `SesionUsuario.objects.filter(estado=VIGENTE, fecha_ultima_actividad__gte=timezone.now()-timedelta(minutes=15)).values('usuario').distinct().count()` |
| **Sesiones vigentes** | `count(SesionUsuario estado=VIGENTE ∧ fecha_expiracion > now())` | `SesionUsuario.objects.filter(estado=VIGENTE, fecha_expiracion__gt=timezone.now()).count()` |
| **Sesiones revocadas** | `count(SesionUsuario estado∈{REVOCADA,CERRADA})` | `SesionUsuario.objects.exclude(estado=VIGENTE).count()` |

### 4.2 Endpoint Métricas (Admin)
```python
# backend/src/apps/indicadores/services/kpi_admin.py

def get_metricas_usuarios_activos(user, ambito):
    """Solo ADMINISTRADOR (SCOPE_ALL)."""
    ahora = timezone.now()
    hoy_inicio = timezone.make_aware(datetime.combine(ahora.date(), time.min))
    quince_min_atras = ahora - timedelta(minutes=15)
    
    return {
        'usuarios_registrados': User.objects.count(),
        'usuarios_habilitados': User.objects.filter(is_active=True).count(),
        'usuarios_login_hoy': SesionUsuario.objects.filter(
            fecha_inicio__gte=hoy_inicio
        ).values('usuario').distinct().count(),
        'usuarios_activos_15min': SesionUsuario.objects.filter(
            estado=SesionUsuario.ESTADO_VIGENTE,
            fecha_ultima_actividad__gte=quince_min_atras,
            fecha_expiracion__gt=ahora
        ).values('usuario').distinct().count(),
        'sesiones_vigentes': SesionUsuario.objects.filter(
            estado=SesionUsuario.ESTADO_VIGENTE,
            fecha_expiracion__gt=ahora
        ).count(),
        'sesiones_revocadas': SesionUsuario.objects.exclude(
            estado=SesionUsuario.ESTADO_VIGENTE
        ).count(),
        'generado_en': ahora,
    }
```

---

## 5. TAREAS DE IMPLEMENTACIÓN (INC-02)

| ID | Tarea | Descripción | Archivos | Prioridad |
|----|-------|-------------|----------|-----------|
| INC-02-T01 | Migración `SesionUsuario` + `token_blacklist` | Modelo + índices + migración simplejwt | `authentication/adapters/models.py`, `authentication/adapters/migrations/`, `base.py` (INSTALLED_APPS) | P1 |
| INC-02-T02 | JWT `jti` claim + `SesionUsuario` en login | `TokenObtainPairSerializer.validate()` crea sesión | `authentication/adapters/serializers.py` | P1 |
| INC-02-T03 | `ROTATE_REFRESH_TOKENS=True` + `BLACKLIST_AFTER_ROTATION=True` | Config base.py + migración token_blacklist | `base.py`, migración | P1 |
| INC-02-T04 | `CustomTokenRefreshView` + actualización sesión | Rotación + update `refresh_token_jti` + `access_token_jti` | `authentication/adapters/views.py`, `urls.py` | P1 |
| INC-02-T05 | `LogoutView` + revocación sesión + blocklist | `POST /auth/logout/` | `authentication/adapters/views.py`, `urls.py` | P1 |
| INC-02-T06 | Middleware actividad + task batch (Redis) | Cache `fecha_ultima_actividad` + bulk_update periódico | `core/adapters/middleware.py`, `core/tasks/actualizar_actividad.py`, `celery.py` | P1 |
| INC-02-T07 | Limpieza sesiones expiradas (task diaria) | `estado=EXPIRADA` donde `fecha_expiracion < now()` | `authentication/tasks/limpiar_sesiones.py` | P1 |
| INC-02-T08 | Endpoint métricas usuarios activos (Admin) | `GET /api/v1/indicadores/usuarios-activos/` | `indicadores/services/kpi_admin.py`, `indicadores/adapters/views.py` | P1 |
| INC-02-T09 | Tests: login→sesión, refresh→rotación, logout→revocación, métricas | Cobertura flujos completos | `authentication/tests/test_sesiones.py`, `indicadores/tests/test_usuarios_activos.py` | P1 |
| INC-02-T10 | Frontend: integrar logout real (ya en `AppLayout.tsx`) | `AuthContext.logout()` llama `POST /auth/logout/` | `frontend/src/auth/AuthContext.tsx`, `frontend/src/api/endpoints/auth.ts` | P1 |

---

## 6. ESTRATEGIA EFICIENCIA: SIN ESCRITURA POR PETICIÓN

### Problema
Actualizar `fecha_ultima_actividad` en **cada request** = escritura BD masiva, contención, lentitud.

### Solución: Cache + Batch Update
1. **Middleware** lee `jti` del access token → guarda `timezone.now()` en **Redis cache** (key: `sesion_actividad_{jti}`, TTL 5 min)
2. **Task Celery Beat** cada 5 min: 
   - `SCAN` keys `sesion_actividad_*`
   - `MGET` timestamps
   - `bulk_update(SesionUsuario, ['fecha_ultima_actividad'])` solo para JTIs con actividad
   - `DELETE` keys procesados
3. **Ventajas:** 
   - 1 escritura BD por sesión cada 5 min (no por request)
   - Redis soporta millones ops/seg
   - Tolerante a picos de tráfico
   - `fecha_ultima_actividad` ≈ real (máx 5 min desfasada)

### Alternativa Simple (sin Redis)
Si no hay Redis: Middleware escribe en **campo `fecha_ultima_actividad` solo si `now() - ultima_actividad > 5 min`** (check en memoria del proceso). Menos preciso, pero cero dependencias.

---

## 7. DIFERENCIACIÓN CONCEPTS

| Concepto | Definición | Fuente |
|----------|------------|--------|
| **Usuario registrado** | Existe en `authentication_user` | `User.objects.count()` |
| **Usuario habilitado** | `is_active=True` + tiene al menos un `UserRole` | `User.objects.filter(is_active=True, role_assignments__isnull=False).distinct().count()` |
| **Usuario login hoy** | Tiene `SesionUsuario` con `fecha_inicio` hoy | `SesionUsuario.objects.filter(fecha_inicio__date=hoy).values('usuario').distinct().count()` |
| **Usuario activo 15 min** | Tiene `SesionUsuario` vigente con `fecha_ultima_actividad` ≤ 15 min | Ver query §4.1 |
| **Sesión vigente** | `SesionUsuario.estado=VIGENTE ∧ fecha_expiracion > now()` | `SesionUsuario.objects.filter(...)` |
| **Sesión revocada** | `estado∈{REVOCADA,CERRADA,EXPIRADA}` | `SesionUsuario.objects.exclude(estado=VIGENTE)` |

---

## 8. PRUEBAS REQUERIDAS

| Test | Descripción |
|------|-------------|
| `test_login_crea_sesion` | Login → `SesionUsuario` creada con JTIs correctos, IP, UA, expiración 24h |
| `test_refresh_rota_sesion` | Refresh → nuevo access+refresh JTIs → sesión actualizada + anterior en blocklist |
| `test_logout_revoca_sesion` | Logout → sesión `CERRADA` + refresh en blocklist → nuevo refresh con mismo token falla 401 |
| `test_sliding_expiracion_inactividad` | (Si Opción B) Inactividad > 1d → refresh falla |
| `test_metricas_usuarios_activos` | Admin consulta endpoint → valores correctos vs conteo directo BD |
| `test_concurrencia_sesiones` | Múltiples peticiones concurrentes → `fecha_ultima_actividad` consistente (batch) |
| `test_limpieza_expiradas` | Task diaria → sesiones expiradas → `estado=EXPIRADA` |

---

## 9. DEPENDENCIAS

- **INC-01** (Seguridad P0): Throttling global debe proteger nuevo endpoint `/auth/logout/` y `/auth/token/refresh/`
- **Redis/Celery**: Para batch updates eficientes (opcional, alternativa simple disponible)
- **simplejwt.token_blacklist**: Requiere migración + `INSTALLED_APPS`

---

## 10. CRITERIOS ACEPTACIÓN INC-02

1. ✅ Login crea `SesionUsuario` con todos los campos
2. ✅ Refresh rota tokens + actualiza sesión + blocklist anterior
3. ✅ Logout revoca sesión + blocklist + frontend limpia `sessionStorage` + redirige `/login`
4. ✅ Métricas endpoint Admin devuelve 6 contadores correctos
5. ✅ `fecha_ultima_actividad` actualizada via batch (max 5 min delay)
6. ✅ Tests pasando (cobertura ≥ 90% flujos sesión)
7. ✅ No regresiones en suite 497 tests backend
8. ✅ Frontend logout funcional (ya implementado en `AppLayout.tsx`)

---

## 11. ALTERNATIVA SIMPLE (SIN REDIS/CELERY)

Si no se autoriza Redis/Celery en este sprint:

```python
# Middleware simple (en proceso, sin batch)
class SesionActividadMiddlewareSimple:
    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(request, 'user') and request.user.is_authenticated:
            auth = request.META.get('HTTP_AUTHORIZATION', '')
            if auth.startswith('Bearer '):
                try:
                    payload = jwt_decode_handler(auth[7:])
                    jti = payload.get('jti')
                    if jti:
                        # Solo actualiza si pasó > 5 min (evita escritura por request)
                        SesionUsuario.objects.filter(
                            refresh_token_jti=jti,
                            estado=SesionUsuario.ESTADO_VIGENTE,
                            fecha_ultima_actividad__lt=timezone.now() - timedelta(minutes=5)
                        ).update(fecha_ultima_actividad=timezone.now())
                except Exception:
                    pass
        return response
```

**Trade-off:** Una escritura BD por sesión cada 5 min (aprox), pero **cero dependencias externas**. Aceptable para carga moderada.

---

## 12. PRÓXIMOS PASOS

1. **Autorizar INC-02** (P1) para Sprint +1 (paralelo a INC-03 Modalidades)
2. **Decidir**: Opción A (Rotación + Blocklist) vs Opción B (Sliding Tokens)
3. **Confirmar** disponibilidad Redis/Celery para batch eficiente
4. **Crear migración** `SesionUsuario` + `token_blacklist`
5. **Implementar** serializer/login + refresh/logout views
6. **Tests** flujos completos + métricas
7. **Integrar frontend** logout real (endpoint ya existe en `AuthContext`)