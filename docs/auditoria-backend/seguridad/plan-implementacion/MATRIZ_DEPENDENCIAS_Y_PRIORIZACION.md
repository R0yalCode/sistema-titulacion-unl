# MATRIZ DE DEPENDENCIAS Y PRIORIZACIÓN — SEC-T001 a SEC-T021

**Fecha:** 2026-11-05  
**Versión:** 1.0  
**Fuente:** BACKLOG_BRECHAS_SEGURIDAD.md, INFORME_HARDENING_SEGURIDAD.md

---

## 1. Dependencias Completas entre Tareas

| ID Tarea | Nombre | Prioridad | Dependencias Directas (Deben estar CERRADAS) | Bloquea a | Tipo Dependencia |
|----------|--------|-----------|---------------------------------------------|-----------|------------------|
| SEC-T001 | Configuración Producción Completa | CRÍTICA | Ninguna | SEC-T005, SEC-T007, SEC-T010, SEC-T011, SEC-T013, SEC-T014, SEC-T019, SEC-T020 | Infraestructura base |
| SEC-T002 | Throttling Login | ALTA | SEC-T005 (IP real via TRUSTED_PROXIES) | SEC-T017 (Tests) | Técnica (IP confiable) |
| SEC-T003 | Rotación + Blacklist Refresh | ALTA | SEC-T004 (JWT_SIGNING_KEY separada) | SEC-T017 (Tests) | Criptográfica (clave firma) |
| SEC-T004 | JWT_SIGNING_KEY Separada | ALTA | **Ninguna** | SEC-T003, SEC-T006, SEC-T018 | Base seguridad JWT |
| SEC-T005 | IP Auditoría + Middleware + TRUSTED_PROXIES | ALTA | SEC-T001 (production.py + Nginx proxy real) | SEC-T002 (Throttling IP), SEC-T017 (Tests) | Infraestructura + Middleware |
| SEC-T006 | Access Token 30 min | MEDIA | SEC-T004 (JWT_SIGNING_KEY separada) | — | Configuración JWT |
| SEC-T007 | Validación MIME Real | MEDIA | SEC-T001 (Dockerfile para libmagic/pikepdf) | — | Dependencia sistema |
| SEC-T008 | Throttling Carga Documentos | MEDIA | **Ninguna** | — | Independiente |
| SEC-T009 | Remover Rutas Internas Serializers | MEDIA | SEC-T001 (endpoint download declaratoria) | — | API/Contrato |
| SEC-T010 | Handler Global Excepciones | MEDIA | SEC-T001 (production.py DEBUG=False para test 500) | — | Configuración |
| SEC-T011 | Logging Estructurado | MEDIA | SEC-T012 (eliminar print) | — | Código |
| SEC-T012 | Eliminar print() evaluar_checklist.py | MEDIA | **Ninguna** | SEC-T011 | Código |
| SEC-T013 | Protección Swagger/ReDoc/Schema | MEDIA | SEC-T001 (production.py) | SEC-T017 (Tests) | Configuración |
| SEC-T014 | CI/CD Security (Safety+Bandit+Gitleaks) | MEDIA | SEC-T001 (Dockerfile para CI env consistente) | SEC-T015 | Pipeline |
| SEC-T015 | Dependabot Configurado | MEDIA | SEC-T014 (CI tests para auto-merge) | — | Pipeline |
| SEC-T016 | Cobertura Tests + testpaths | MEDIA | **Ninguna** | — | Configuración |
| SEC-T017 | Tests Seguridad Faltantes | MEDIA | SEC-T002, SEC-T003, SEC-T005, SEC-T013 | — | Tests requieren controles |
| SEC-T018 | Procedimiento Rotación Secretos | BAJA | SEC-T004 (JWT_SIGNING_KEY separada) | — | Documentación |
| SEC-T019 | Limpieza Archivos Huérfanos | BAJA | SEC-T001 (Dockerfile cron) | — | Operaciones |
| SEC-T020 | Verificación PermissionError Docker | BAJA | SEC-T001 (Dockerfile + docker-compose) | — | Validación |
| SEC-T021 | Evidencias ACD 4 Reales | BAJA | **Ninguna** | — | Trazabilidad |

---

## 2. Gráfico de Dependencias (Topológico)

```
NIVEL 0 (Independientes - Inicio Inmediato)
├── SEC-T004  ← JWT_SIGNING_KEY separada
├── SEC-T008  ← Throttling carga documentos
├── SEC-T012  ← Eliminar print() evaluar_checklist.py
└── SEC-T016  ← Cobertura tests + testpaths
└── SEC-T021  ← Evidencias ACD 4

NIVEL 1 (Requieren NIVEL 0)
├── SEC-T001  ← Configuración producción (CRÍTICA - inicia Fase 1)
└── SEC-T003  ← Rotación/Blacklist (requiere SEC-T004)
└── SEC-T006  ← Access token 30min (requiere SEC-T004)
└── SEC-T018  ← Proc. rotación (requiere SEC-T004)
└── SEC-T011  ← Logging (requiere SEC-T012)

NIVEL 2 (Requieren SEC-T001 completada)
├── SEC-T005  ← IP Auditoría + Middleware + TRUSTED_PROXIES
├── SEC-T007  ← Validación MIME real (Dockerfile libmagic)
├── SEC-T010  ← Exception handler (production.py DEBUG=False)
├── SEC-T013  ← Swagger protection (production.py)
├── SEC-T014  ← CI/CD Security (Dockerfile)
├── SEC-T019  ← Limpieza huérfanos (Dockerfile cron)
└── SEC-T020  ← PermissionError Docker (docker-compose)

NIVEL 3 (Requieren SEC-T005)
├── SEC-T002  ← Throttling login (IP real via TRUSTED_PROXIES)
└── SEC-T009  ← Serializers (requiere endpoint download declaratoria - pendiente análisis)

NIVEL 4 (Requieren controles implementados)
├── SEC-T017  ← Tests seguridad (requiere SEC-T002, T003, T005, T013)
└── SEC-T015  ← Dependabot (requiere SEC-T014 CI tests)
```

---

## 3. Justificación de Prioridad

### CRÍTICA (1 tarea)
| Tarea | Justificación |
|-------|---------------|
| SEC-T001 | **Bloquea 9 tareas**. Sin production.py, Dockerfile, Nginx, TLS, usuario no-root: backend NO desplegable en producción. Riesgo CRÍTICO. |

### ALTA (4 tareas)
| Tarea | Justificación |
|-------|---------------|
| SEC-T004 | Base criptográfica: separar JWT_SIGNING_KEY de SECRET_KEY. Compromiso actual = control total (JWT + sesiones Django). Desbloquea SEC-T003 y SEC-T006. |
| SEC-T003 | Rotación + blacklist refresh tokens: sin esto, refresh token robado = acceso indefinido. Requiere SEC-T004. |
| SEC-T005 | IP auditoría suplantable: sin TRUSTED_PROXIES + middleware, trazabilidad comprometida. Requiere SEC-T001 (Nginx real). Desbloquea SEC-T002. |
| SEC-T002 | Throttling login: fuerza bruta/credential stuffing sin límite. Requiere SEC-T005 para IP confiable. |

### MEDIA (12 tareas)
| Tarea | Justificación |
|-------|---------------|
| SEC-T006 | Access token 60min vs 30min ACD: ventana exposición 2x. Requiere SEC-T004. |
| SEC-T007 | Validación MIME real: magic bytes insuficientes para PDF políglotas. Requiere SEC-T001 Dockerfile. |
| SEC-T008 | Throttling carga docs: DoS almacenamiento. Independiente, bajo esfuerzo. |
| SEC-T009 | Rutas internas expuestas: fuga estructura almacenamiento. Requiere SEC-T001 endpoint declaratoria. |
| SEC-T010 | Handler excepciones unificado: formato errores consistente + sin fuga 500. Requiere SEC-T001. |
| SEC-T011 | Logging estructurado: rotación, JSON, filtros PII. Requiere SEC-T012. |
| SEC-T012 | Eliminar print(): fuga username/roles/facultad en stdout. Independiente, rápido. |
| SEC-T013 | Swagger público: superficie ataque expuesta. Requiere SEC-T001 production.py. |
| SEC-T014 | CI/CD security: detección automática vulnerabilidades. Requiere SEC-T001 Dockerfile. |
| SEC-T015 | Dependabot: actualizaciones automáticas deps. Requiere SEC-T014. |
| SEC-T016 | Cobertura + testpaths: medir y enforzar calidad tests. Independiente. |
| SEC-T017 | Tests controles seguridad: validación automática. Requiere controles implementados. |

### BAJA (4 tareas)
| Tarea | Justificación |
|-------|---------------|
| SEC-T018 | Documentación procedimiento rotación. Requiere SEC-T004. Post-deploy. |
| SEC-T019 | Limpieza huérfanos: gestión almacenamiento largo plazo. Requiere SEC-T001. |
| SEC-T020 | Verificación PermissionError: validación ops. Requiere SEC-T001. |
| SEC-T021 | Trazabilidad ACD 4: placeholders → evidencia real. Independiente. |

---

## 4. Tareas Paralelizables vs Secuenciales

### Paralelizables (pueden ejecutarse simultáneamente por diferentes agentes/desarrolladores)

| Grupo | Tareas | Condición |
|-------|--------|-----------|
| **Grupo Independencia Inicial** | SEC-T004, SEC-T008, SEC-T012, SEC-T016, SEC-T021 | Sin dependencias; pueden iniciar ya. |
| **Post-SEC-T004** | SEC-T003, SEC-T006, SEC-T018 | Solo requieren SEC-T004 cerrada. |
| **Post-SEC-T001 + SEC-T004** | SEC-T007, SEC-T010, SEC-T013, SEC-T014, SEC-T019, SEC-T020 | Requieren production.py/Dockerfile listos. |
| **Post-SEC-T012** | SEC-T011 | Solo requiere print() eliminado. |

### Secuenciales Estrictas (orden obligatorio)

| Cadena | Orden | Razón |
|--------|-------|-------|
| **Infra → Auth** | SEC-T001 → SEC-T005 → SEC-T002 | Nginx real → TRUSTED_PROXIES → IP real para throttling. |
| **JWT Key → Rotación** | SEC-T004 → SEC-T003 | Rotación usa clave firma JWT. |
| **JWT Key → Lifetime** | SEC-T004 → SEC-T006 | Cambio lifetime invalida tokens; clave separada evita impacto sesiones. |
| **Print → Logging** | SEC-T012 → SEC-T011 | Logging limpio sin prints en stdout. |
| **Controles → Tests** | SEC-T002,T003,T005,T013 → SEC-T017 | Tests requieren controles funcionando. |
| **CI → Dependabot** | SEC-T014 → SEC-T015 | Auto-merge necesita CI tests pasando. |

---

## 5. Análisis de Conflictos Potenciales

| Conflicto | Tareas Involucradas | Descripción | Resolución |
|-----------|---------------------|-------------|------------|
| **Archivos settings/ modificados por múltiples tareas** | SEC-T001, SEC-T004, SEC-T006, SEC-T010, SEC-T011, SEC-T013 | production.py, base.py editados por varias | SEC-T001 crea production.py base; resto añaden configs específicas en production.py. Usar PRs pequeños y revisados. |
| **Middleware MIDDLEWARE[] orden** | SEC-T005 (ThreadLocalRequestMiddleware first) | ThreadLocal debe ser primero para capturar request temprano | Documentar en SEC-T005: insertar en MIDDLEWARE[0]. Verificar no rompe otros middlewares. |
| **REST_FRAMEWORK config** | SEC-T001, SEC-T002, SEC-T008, SEC-T010, SEC-T013 | DEFAULT_THROTTLE_RATES, EXCEPTION_HANDLER, SERVE_PERMISSIONS | SEC-T001 define base en production.py; tareas añaden/actualizan claves específicas. |
| **Serializers peticiones/resoluciones** | SEC-T009 | Remover archivo_path, añadir download_url | Coordinar con frontend; considerar deprecation temporal con ambos campos. |
| **Tests nuevos vs existentes** | SEC-T017 | 473 tests existentes + nuevos | Ejecutar suite completa tras cada tarea; no modificar tests existentes salvo asserts por formato errores (SEC-T010). |
| **Migraciones token_blacklist** | SEC-T003 | Nueva app en INSTALLED_APPS | Ejecutar `python manage.py migrate` en entrypoint Docker; documentar en DEPLOY_PRODUCTION.md. |

---

## 6. Orden Recomendado de Implementación (Secuencia Final)

| Orden | ID | Tarea | Fase | Estimación Esfuerzo | Ventana Recomendada |
|-------|----|-------|------|---------------------|---------------------|
| 1 | SEC-T004 | JWT_SIGNING_KEY Separada | 0 | Bajo (1-2 días) | Semana 1, Día 1-2 |
| 2 | SEC-T012 | Eliminar print() evaluar_checklist.py | 0 | Muy Bajo (0.5 días) | Semana 1, Día 1 |
| 3 | SEC-T016 | Cobertura Tests + testpaths | 0 | Bajo (1 día) | Semana 1, Día 2 |
| 4 | SEC-T008 | Throttling Carga Documentos | 0 | Bajo (1-2 días) | Semana 1, Día 2-3 |
| 5 | SEC-T021 | Evidencias ACD 4 Reales | 0 | Bajo (1 día) | Semana 1, Día 3 |
| 6 | **SEC-T001** | **Configuración Producción Completa** | **1** | **Alto (5-7 días)** | **Semana 1-2** |
| 7 | SEC-T003 | Rotación + Blacklist Refresh | 1 | Medio (3-4 días) | Semana 2 (tras SEC-T004) |
| 8 | SEC-T006 | Access Token 30 min | 1 | Muy Bajo (0.5 días) | Semana 2 (tras SEC-T004) |
| 9 | SEC-T018 | Procedimiento Rotación Secretos | 1 | Bajo (1-2 días) | Semana 2 (tras SEC-T004) |
| 10 | SEC-T005 | IP Auditoría + Middleware + TRUSTED_PROXIES | 2 | Medio (3-4 días) | Semana 2-3 (tras SEC-T001) |
| 11 | SEC-T002 | Throttling Login | 2 | Bajo (1-2 días) | Semana 3 (tras SEC-T005) |
| 12 | SEC-T007 | Validación MIME Real | 3 | Medio (3-5 días) | Semana 3-4 (tras SEC-T001) |
| 13 | SEC-T009 | Remover Rutas Internas Serializers | 3 | Bajo (2-3 días) | Semana 3-4 (tras SEC-T001) |
| 14 | SEC-T010 | Handler Global Excepciones | 3 | Medio (2-3 días) | Semana 3-4 (tras SEC-T001) |
| 15 | SEC-T011 | Logging Estructurado | 3 | Medio (2-3 días) | Semana 3-4 (tras SEC-T012 + SEC-T001) |
| 16 | SEC-T013 | Protección Swagger/ReDoc/Schema | 4 | Bajo (1-2 días) | Semana 4 (tras SEC-T001) |
| 17 | SEC-T014 | CI/CD Security (Safety+Bandit+Gitleaks) | 4 | Medio (3-4 días) | Semana 4 (tras SEC-T001) |
| 18 | SEC-T015 | Dependabot Configurado | 4 | Bajo (1 día) | Semana 4 (tras SEC-T014) |
| 19 | SEC-T017 | Tests Seguridad Faltantes | 5 | Medio (3-5 días) | Semana 4-5 (tras T002,T003,T005,T013) |
| 20 | SEC-T019 | Limpieza Archivos Huérfanos | 6 | Medio (2-3 días) | Post-deploy inicial |
| 21 | SEC-T020 | Verificación PermissionError Docker | 6 | Medio (2-3 días) | Post-deploy inicial |

---

## 7. Hitos de Validación

| Hito | Tareas Incluidas | Criterio de Validación |
|------|------------------|------------------------|
| **Hito 0: Base Independiente** | SEC-T004, T008, T012, T016, T021 | 5 tareas cerradas; tests pasando; coverage ≥80%; sin prints en verificacion/services. |
| **Hito 1: Producción Lista** | SEC-T001 | Docker build OK; docker-compose staging up; HTTPS + headers seguridad; Swagger 403 anónimo; healthcheck 200. |
| **Hito 2: Autenticación Segura** | SEC-T003, T004, T005, T006 | Rotación+blacklist funcionando; JWT key separada; IP auditoría real; access token 30min; logout endpoint. |
| **Hito 3: Throttling Operativo** | SEC-T002, T008 | Login 5/min/IP 429; Carga docs 10/hora/user 429; IP real via TRUSTED_PROXIES. |
| **Hito 4: Controles Medios + Errores/Logging** | SEC-T007, T009, T010, T011, T013 | MIME real; serializers limpios; handler global; logging JSON rotativo; Swagger protegido. |
| **Hito 5: CI/CD Security** | SEC-T014, T015 | Pipeline safety/bandit/gitleaks pasando; Dependabot activo auto-merge patch. |
| **Hito 6: Tests Seguridad Completos** | SEC-T017 | Tests throttling, rotación, IP auditoría, Swagger pasando en CI. |
| **Hito 7: Operaciones** | SEC-T019, T020 | Command limpieza funcionando; PermissionError validado en staging. |

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05