# 04 — AUDITORÍA ARQUITECTÓNICA

## 1. Arquitectura real (reconstruida desde el código)

**Monolito modular Django con arquitectura hexagonal (Ports & Adapters) por convención de carpetas**, mundo de una sola base de datos PostgreSQL y API HTTP única.

```
Entrada (HTTP)   →  src/config/urls.py  (todas las rutas centralizadas, ViewSet.as_view manual)
                 →  apps/<x>/adapters/views.py   (JWT + HasRolePermission + ScopeFilterMixin)
                 →  apps/<x>/services/<use_case>.py   (transaction.atomic + select_for_update)
                 →  apps/<x>/adapters/<models|serializers>   (ORM PostgreSQL)
Puertos/Adapters →  src/core/ports (ABC ISGALegacyPort) → src/core/adapters (mock_sga, pdf_validation,
                    local_storage PrivateMediaStorage, scope_filter)
Transversal      →  notificaciones/adapters/signals.py (EventAuditoria JSONB + fail-safe)
```

- **6 apps Django**: authentication, expedientes, peticiones, verificacion, resoluciones, notificaciones — **alineadas 1:1 con los límites modulares del plan.md §11** (mismas entidades propietarias).
- Dependencias entre apps observables (plan declaraba dependencias permitidas): peticiones→expedientes y authentication; verificacion→expedientes/peticiones; resoluciones→verificacion/expedientes/peticiones; notificaciones→vía signals (desacoplado). **Cumple** el grafo establecido, con una excepción menor: `validar_checklist_completo` importado al final de `resoluciones/adapters/views.py:224` (import tardío por orden).

## 2. Patrones verificados

| Patrón | Evidencia | Evaluación |
|---|---|---|
| Hexagonal / Ports & Adapters | ports ABC + adapters substituibles (mock SGA) | ✅ real en core; parcial en apps (domain mezclas: `plazo_calculator` usa `django.utils.timezone`) |
| Domain Service / Use-Case | `services/*.py` con `execute()` | ✅ consistente en 10 use-cases |
| State Machine | `ExpedienteTitulacion` 7 estados + máquina consultada en servicios (`enviar_expediente.py:91-95`); tests unitarios de máquina (`test_expediente_state_machine.py`) | ✅ sólida |
| Repository (implícito) | ORM directo en adapters, sin repositorios explícitos | ⚠️ aceptable para Django idiomático, aunque el plan promete inversión explícita |
| Event-driven (signals) | 9 señales post_save/pre_save | ✅ para auditoría; ❌ notifications creadas fuera del patrón en servicios |
| Singleton-ish adapters | `PDFGeneratorAdapter()` instanciado por uso con output_dir hardcodeado | ❌ configuración externa rota (hallazgo A-01) |
| Mixin transversal de scope | `ScopeFilterMixin` | ✅ pero sin soporte `SCOPE_ASIGNADO`/`SCOPE_BORRADOR` (bypass manual en 3 puntos) |

## 3. Coupling & cohesion

- **Alta cohesión** dentro de cada app (los use-cases reúnen autorización+estado+persistencia).
- **Acoplamiento choques**:
  1. **Referencias de identidad UUID como cadenas**: comparaciones de `carrera_id`/`facultad_id` manual stringify en 4 servicios (`evaluar_checklist.py:165-174`, `registrar_observacion.py:112-118`, `emitir_informe.py`, `declarar_aptitud.py:158-163`) — duplica ScopeFilterMixin y añade riesgo de drift.
  2. **Notificaciones**: `notification_service.py` define el despachador oficial; los servicios lo **esquivan** y crean `NotificacionInterna.objects.create` en línea → doble via de verdad (deuda).
  3. **Duplicación de permisos en 3 capas**: RBAC_MATRIX (permissions.py) + validación de rol dentro de servicios (`any(has_role...)` en 5 servicios) + validates de pertenencia por facultad manual. Triple validación defendida, pero regla no ejecutada desde una sola fuente.
- **Uma estructura por convención**: no hay routers DRF, ni urls por app, ni inyección de dependencias (instancia directa de servicios) — Django idiomático, más rígido pero legible.

## 4. Problemas de escalabilidad / operación

| # | Problema | Impacto | Prioridad |
|---|---|---|---|
| A-01 | `PDFGeneratorAdapter(output_dir="/media/private/resoluciones")` — path absoluto hardcodeado, `os.makedirs` en constructor y؈a no referenciado a `MEDIA_ROOT` ni a `PrivateMediaStorage` (`pdf_generator.py:48`; `emitir_informe` construye instancia con esa default) | **74 tests fallan; en host sin `/media/` monéba todo el flujo de informes declaratorias** | CRÍTICO |
| A-02 | `CMD runserver` en Dockerfile + `config.settings.local` con DEBUG=1 en compose → desplegable de auditoría sgt en modo dev; sin gunicorn | No apto para entrega; process crash sutil, security leak DEBUG | ALTO |
| A-03 | Ningún `/health/` endpoint (RNF-006) ni healthcheck del servicio backend en compose | Sin monitorización de vida; orquestación ciega | MEDIO |
| A-04 | `staticfiles` nunca recolectado: volumen `static_data` innecesario, drf-spectacular assets (Swagger UI) servidos por Django dev-server a través del proxy local | Operación débil cuando se apuntar a producción | MEDIO |
| A-05 | Sin throttling (DRF) ni rate-limit (nginx) ni rotación de refresh tokens |发散 a carga + fuerza bruta en perspectiva pública | ALTO |
| A-06 | **tests/** no copiados al artefacto Docker** (`Dockerfile` copia sólo manage.py+src): la imagen no puede correr su suite de verificación | Auditoría en contenedor imposible sin `docker cp` hacks (hallazgo verificado al ejecutar la suite) | MEDIO |
| A-07 | **`pyproject.toml` no copiado a imagen**: pytest en el contenedor falla con `ImportError: No module named 'config'` (verificado) | DevEx/QA: la imagen no es reproducible para verificación | MEDIO |
| A-08 | Nginx proxy completo sin rate-limit y expone Django Admin (migración accidental) | Superficie operativa brisk | MEDIO |
| A-09 | Sin CORS configurado (no corsheaders) | Forzaría bloqueo del frontend futuro Fase 2 con misma origen deflectada | BAJO hoy (porque no hay frontend) |
| A-10 | Sin configuración LOGGING y sin logging propagation como política (`grep` en src = 0) | Debuggability y observabilidad pobres | MEDIO |
| A-11 | Sin paginación global DRF (bandeja manual; notificaciones con `pagination_class=None`) | Riesgos de payload desenfrenado con volumen | BAJO/MEDIO |

## 5. Fortalezas arquitectónicas

1. **División app/6 límites claros y coherentes con el plan** — delega bien de modularización lógica a estructura física.
2. **Dominio puro donde importa**: `plazo_calculator.py` testeado en 100% con algoritmos puros (leve interacción con `timezone`); dataclasses frozen para dados SGA (inmutabilidad DEC-05).
3. **Transacciones + bloqueo pesimista coherentes** en 10 servicios — anti-concurrencia (AP-06) respetado sistemáticamente (`transaction.atomic` + `select_for_update`), respaldado por UPGR de tests.
4. **Mundo cerrado de seguridad** en 2 capas (RBAC_MATRIX + services) con default DENY en ambos.
5. **Desacoplamiento de auditoría** via signals fail-safe (errores de auditoría no rompen negocio).
6. **Estrategias de anti-IDOR en 404** (evita enumeración de recursos por respuestas distintas 403/404).

## 6. Deudas de arquitectura (resumen)

- Variedad de esquinas (`SECRET_KEY` = `SIGNING_KEY` JWT) para settings (hidden cooking).
- `pdf_generator.py` (796 líneas) monolítico con plantilla fija "Computación"/"FEIRNNR" — al integrar catálogos/roles (TODO en `emitir_informe.py:69-70`) necesitará refactor de plantillas.
- HistorialEstado inconsistente en emisión de informe (guarda estado nuevo como anterior) — introdujo corrupción lógica del histórico.
- Dead code (2 ViewSets sin rutas) + recursos RBAC no conectados to naturaleza de drift del design (`expedientes:enviar`, `catalogos:requisitos`).
- Notificaciones duplicadas en 2 caminos (signals vs services).
- **Comparaciones de facultad STRING vs UUID-Token** que cuentan con nulo: manual hard-coded (waived) match con nulos aceptable en composición actual pero mal escalable.
