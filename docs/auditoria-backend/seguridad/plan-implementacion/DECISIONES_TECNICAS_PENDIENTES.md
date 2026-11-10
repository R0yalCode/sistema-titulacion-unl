# DECISIONES TÉCNICAS PENDIENTES DE APROBACIÓN HUMANA

**Fecha:** 2026-11-05  
**Versión:** 1.1  
**Estado:** Parcial — DEC-002, DEC-003, DEC-004 y DEC-010 **APROBADAS** (2026-11-05, ver `DECISION_LOG.md`). El resto permanece pendiente.

---

## Resumen de Decisiones

| # | Decisión | Tareas Bloqueadas | Urgencia | Responsable |
|---|----------|-------------------|----------|-------------|
| 1 | Método validación MIME real: `python-magic` vs `pikepdf` | SEC-T007 | ALTA (inicia Semana 3) | Tech Lead / Arquitecto |
| 2 | Límite throttling login (req/min/IP) | SEC-T002 | MEDIA (inicia Semana 3) | **APROBADA 2026-11-05: 5/min/IP** (efectiva solo tras SEC-T005) |
| 3 | Límite throttling carga documentos (req/hora/user) | SEC-T008 | MEDIA (independiente) | **APROBADA 2026-11-05: 10/hora/usuario** |
| 4 | Umbral cobertura tests (`--cov-fail-under`) | SEC-T016 | BAJA (independiente) | Tech Lead / QA — **el valor del umbral sigue PENDIENTE**; lo único aprobado 2026-11-05 es la corrección documental de que DEC-004 nunca fue precondición real de SEC-T001 (error de redacción, ver sección 10bis más abajo y `DECISION_LOG.md`) |
| 5 | Política retención archivos huérfanos (días) | SEC-T019 | BAJA (post-deploy) | Tech Lead / Operaciones |
| 6 | Endpoint download declaratoria: ¿crear nuevo o reutilizar? | SEC-T009 | ALTA (pre-SEC-T009) | Tech Lead / Backend Lead |
| 7 | Evidencias ACD 4: ¿placeholders son datos reales o de prueba? | SEC-T021 | BAJA | Coordinador Académico / Responsable |
| 8 | Almacenamiento refresh token frontend: localStorage vs httpOnly cookie | SEC-T003 | MEDIA (pre-SEC-T003) | Frontend Lead + Seguridad |
| 9 | Formato mensaje error 500 para usuario final | SEC-T010 | MEDIA (pre-SEC-T010) | UX/Product Owner |
| 10 | ¿Incluir CSP (Content Security Policy) en production.py? | SEC-T001 | MEDIA (Fase 1) | **APROBADA 2026-11-05: Alternativa D** — `Content-Security-Policy-Report-Only` para el resto de directivas + `frame-ancestors 'none'` y `base-uri 'self'` como bloqueantes. Documentado expresamente: Report-Only **no bloquea** el resto de directivas, solo las reporta (sin endpoint de reportes en esta fase). |

---

## Fichas de Decisión Detalladas

---

### DEC-001: Método Validación MIME Real (SEC-T007)

**Problema:** La validación actual solo verifica magic bytes `%PDF-` y tamaño. PDFs políglotas (PDF+ZIP, PDF+JS) o con estructura maliciosa pasarían. Se requiere validación MIME real de contenido.

**Alternativas:**

| Opción | Descripción | Ventajas | Desventajas | Compatibilidad Docker |
|--------|-------------|----------|-------------|----------------------|
| **A) `python-magic` (libmagic)** | `magic.from_buffer(file.read(2048), mime=True) == "application/pdf"` | Detección MIME real estándar; detecta polyglots; ampliamente usado. | Requiere `libmagic` sistema (apt-get install libmagic1); añade dependencia OS; posible variación entre SO. | **Alpine/slim:** `apk add libmagic` — OK. Imagen ~5MB extra. |
| **B) `pikepdf`** | `pikepdf.open(io.BytesIO(file.read()))` → catch `PdfError` | Parsing PDF real; valida estructura interna; rechaza corruptos/políglotas; pure Python (sin libmagic). | Más lento (parsea todo PDF); no detecta MIME sino estructura PDF; puede ser estricto con PDFs válidos poco convencionales. | **Pure Python** — Sin deps OS. Ideal para alpine/slim. |
| **C) `PyPDF2` / `pdfplumber`** | Similar a pikepdf pero más ligero/antiguo | Pure Python; ligero. | Menos robusto parsing; PyPDF2 deprecado en partes. | Pure Python. |
| **D) Mantener solo magic bytes + hash** | No añadir validación extra | Cero deps; rápido; tests pasan. | **No cierra brecha** — PDF políglota pasa. |

**Recomendación Técnica:** **Opción B (`pikepdf`)** — Pure Python, sin dependencias OS, valida estructura PDF real, rechaza políglotas/corruptos, compatible Docker alpine/slim sin paquetes extra. `python-magic` como fallback si `pikepdf` tiene falsos positivos con PDFs institucionales válidos.

**Condiciones de Elección:**
- Si `pikepdf` rechaza PDFs válidos de la UNL (firmados digitalmente, generados por sistemas legacy) → evaluar `python-magic`.
- Ejecutar prueba con corpus de PDFs reales institucionales antes de decidir.

**Riesgo:** Falsos positivos (PDFs válidos rechazados) o falsos negativos (maliciosos pasan). Mitigar con corpus de prueba representativo.

**Tareas Bloqueadas:** SEC-T007 no puede iniciar sin decisión. SEC-T001 Dockerfile debe incluir deps según decisión.

**Responsable Aprobación:** Tech Lead / Arquitecto Backend  
**Fecha Límite:** Antes Semana 3 (inicio Fase 3)

---

### DEC-002: Límite Throttling Login (SEC-T002)

**Problema:** Auditoría referencia "5 intentos por minuto por IP" como valor de referencia, pero no hay decisión definitiva aprobada.

**Alternativas:**
| Valor | Contexto | Ventajas | Desventajas |
|-------|----------|----------|-------------|
| **5/min/IP** | Referencia auditoría / OWASP estándar | Conservador; bloquea fuerza bruta efectivo. | Puede afectar usuarios legítimos en red corporativa (NAT misma IP). |
| **10/min/IP** | Menos restrictivo | Menos falsos positivos en redes compartidas. | Ventana mayor para credential stuffing. |
| **20/min/IP** | Permisivo | Casi ningún falso positivo. | Protección débil. |
| **Configurable via env var** | `AUTH_THROTTLE_RATE="5/minute"` | Flexible por entorno. | Requiere decisión valor default. |

**Recomendación Técnica:** **5/minute por IP** como default en `production.py`, configurable via `AUTH_THROTTLE_RATE` env var. Documentar en `.env.example`.

**Consideración Crítica:** Requiere **SEC-T005 (TRUSTED_PROXIES)** funcionando para que IP real sea confiable. Sin SEC-T005, throttling por `REMOTE_ADDR` (IP proxy/Nginx) → todos usuarios misma IP → bloqueo masivo.

**Tareas Bloqueadas:** SEC-T002 implementación (valor hardcoded en config).

**Responsable Aprobación:** Product Owner + Responsable Seguridad  
**Fecha Límite:** Antes Semana 3 (inicio Fase 2)

---

### DEC-003: Límite Throttling Carga Documentos (SEC-T008)

**Problema:** Referencia "10 cargas por hora por usuario" sin decisión aprobada.

**Alternativas:**
| Valor | Justificación |
|-------|---------------|
| **10/hora/user** | Referencia auditoría; equilibra uso normal vs abuso. |
| **20/hora/user** | Más permisivo para flujos con múltiples subsanaciones. |
| **5/hora/user** | Restrictivo; protege almacenamiento agresivamente. |
| **Configurable env** | `DOCUMENT_UPLOAD_THROTTLE="10/hour"` |

**Recomendación Técnica:** **10/hora por usuario autenticado** (UserRateThrottle), configurable via `DOCUMENT_UPLOAD_THROTTLE` en `.env.example`. Throttle por user (no IP) — evita problemas NAT.

**Tareas Bloqueadas:** SEC-T008 implementación.

**Responsable Aprobación:** Product Owner + Responsable Seguridad  
**Fecha Límite:** Antes Semana 1 (independiente, puede decidirse ya)

---

### DEC-004: Umbral Cobertura Tests (SEC-T016)

**Problema:** No hay umbral `--cov-fail-under` definido. Auditoría sugiere 80% pero requiere confirmación.

**Alternativas:**
| Umbral | Contexto |
|--------|----------|
| **70%** | Mínimo aceptable; permite gaps no críticos. |
| **80%** | Estándar industria; balance calidad/velocidad. |
| **85-90%** | Exigente; módulos críticos ≥90%. |
| **Sin umbral (solo reporte)** | Informativo; no bloquea CI. |

**Recomendación Técnica:** **80% global**, con **90% para módulos críticos** (`authentication`, `peticiones`, `verificacion`, `core.adapters`). Configurar en `pyproject.toml`:
```toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-fail-under=80 --cov-report=term-missing"
```

**Tareas Bloqueadas:** SEC-T016 configuración final.

**Responsable Aprobación:** Tech Lead / QA Lead  
**Fecha Límite:** Antes Semana 1 (independiente)

---

### DEC-005: Política Retención Archivos Huérfanos (SEC-T019)

**Problema:** Management command `limpiar_archivos_huerfanos` requiere política de retención para versiones `es_vigente=False`.

**Alternativas:**
| Política | Descripción |
|----------|-------------|
| **Eliminar inmediato** | Al marcar `es_vigente=False`, borrar archivo físico en misma transacción (compensación). |
| **90 días** | Mantener 90 días para recuperación manual/auditoría; luego command borra. |
| **1 año** | Conservador; cumplo normativa archivo. |
| **Solo huérfanos (sin registro DB)** | Borrar solo archivos en disco sin `DocumentoEntregado` correspondiente; versiones con registro se mantienen. |

**Recomendación Técnica:** **Híbrida**: 1) Borrar inmediato archivos huérfanos (sin registro DB). 2) Versiones `es_vigente=False` con registro → **90 días** antes de borrado físico (configurable `ORPHAN_RETENTION_DAYS=90` env). Documentar en `OPERATIONS.md`.

**Tareas Bloqueadas:** SEC-T019 criterios de aceptación finales.

**Responsable Aprobación:** Tech Lead / Operaciones / Legal (normativa archivo UNL)  
**Fecha Límite:** Post-deploy inicial (Fase 6)

---

### DEC-006: Endpoint Download Declaratoria (SEC-T009)

**Problema:** `DeclaratoriaAptitudSerializer` expone `archivo_memorando_firmado_path`. SEC-T009 requiere sustituir por `download_url` opaco. **No existe endpoint GET /api/v1/declaratorias/{id}/documento/** en `resoluciones/views.py` actual.

**Alternativas:**
| Opción | Descripción | Esfuerzo | Impacto |
|--------|-------------|----------|---------|
| **A) Crear endpoint nuevo** | `GET /api/v1/declaratorias/{id}/documento/` en `DeclaratoriaViewSet` (similar a `descargar_documento` en peticiones). | Medio (nuevo action + serializer + permisos + tests) | Limpio; RESTful; consistente con peticiones. |
| **B) Reutilizar endpoint existente** | ¿Existe alguno? Revisar `resoluciones/views.py` — solo `create` (POST). No hay GET. | N/A | No aplica. |
| **C) Servir via endpoint genérico archivos** | Un endpoint `/api/v1/archivos/{tipo}/{id}/` que sirva cualquier archivo privado. | Alto (refactor transversal) | Over-engineering para una necesidad. |
| **D) Mantener `archivo_memorando_firmado_path` temporalmente** | No remover campo; añadir `download_url` cuando endpoint exista. | Bajo (temporal) | Deuda técnica; expone ruta interna mientras tanto. |

**Recomendación Técnica:** **Opción A** — Crear `download_documento` action en `DeclaratoriaViewSet` (copia adaptada de `PeticionViewSet.descargar_documento`). Requiere: permisos RBAC (`declaratorias` GET scope), validación ámbito (decano/analista misma facultad), `FileResponse` streaming. **Debe implementarse ANTES de SEC-T009**.

**Tareas Bloqueadas:** SEC-T009 no puede cerrar sin endpoint funcionando.

**Responsable Aprobación:** Tech Lead / Backend Lead  
**Fecha Límite:** Antes Semana 3 (pre-SEC-T009 en Fase 3)

---

### DEC-007: Evidencias ACD 4 — Placeholders vs Datos Reales (SEC-T021)

**Problema:** Identificadores `a1b2c3d`, `e4f5g6h`, `i7j8k9l`, `m0n1o2p`, `q3r4s5t` parecen placeholders (hashes cortos genéricos). No existen en historial Git.

**Alternativas:**
| Escenario | Acción |
|-----------|--------|
| **Son datos de prueba/ficticios** | Marcar SEC-T021 como "NO APLICA" o "CANCELADA". Actualizar matriz trazabilidad. |
| **Son referencias a PRs/commits reales en otra plataforma** | Solicitar mapeo real: SHA commits, URLs PRs, autores, archivos. Actualizar matriz. |
| **Faltan por registrar** | Registrar evidencias reales ahora (commits actuales de cada integrante). |

**Recomendación Técnica:** Verificar con **Coordinador Académico / Responsable del Proyecto** si estos identificadores corresponden a entregables reales del ACD 4. Si son placeholders → cancelar SEC-T021. Si son reales → solicitar evidencia y actualizar.

**Tareas Bloqueadas:** SEC-T021 definición final.

**Responsable Aprobación:** Coordinador Académico / Responsable Proyecto  
**Fecha Límite:** Cualquier momento (independiente, baja prioridad)

---

### DEC-008: Almacenamiento Refresh Token Frontend (SEC-T003)

**Problema:** SEC-T003 rota refresh token cada uso. Frontend debe guardar el **nuevo refresh token** tras cada refresh. Dónde almacenarlo afecta seguridad.

**Alternativas:**
| Opción | Seguridad | Complejidad Frontend |
|--------|-----------|---------------------|
| **A) httpOnly Cookie (SameSite=Strict/Lax)** | **Máxima** — Inaccesible a JS, XSS no roba refresh. Requiere backend enviar `Set-Cookie` en login/refresh. | Media — Interceptor no lee cookie; backend maneja automático. Login/refresh deben setear cookie. |
| **B) localStorage / sessionStorage** | Media — Accesible a JS; XSS puede robar. Requiere frontend actualizar storage en cada refresh. | Baja — Patrón actual común. |
| **C) Memoria (variable JS) + httpOnly cookie para refresh** | Alta — Access en memoria (corta vida), refresh en cookie httpOnly. | Alta — Requiere coordinación backend/frontend cookies. |

**Recomendación Técnica:** **Opción A (httpOnly Cookie)** — Máxima seguridad. Backend: `response.set_cookie('refresh_token', ..., httponly=True, secure=True, samesite='Lax')` en login y refresh. Frontend: interceptor **no** maneja refresh token; solo access token en memoria. Logout: `POST /auth/logout/` + limpiar cookie (`response.delete_cookie('refresh_token')`).

**Requiere Decisión:** Cambio arquitectura auth frontend. Si frontend usa localStorage actual → migración significativa.

**Tareas Bloqueadas:** SEC-T003 implementación completa (backend listo, frontend debe coordinar).

**Responsable Aprobación:** Frontend Lead + Responsable Seguridad  
**Fecha Límite:** Pre-SEC-T003 (Fase 2)

---

### DEC-009: Formato Mensaje Error 500 Usuario Final (SEC-T010)

**Problema:** Handler global errores (SEC-T010) estandariza formato. Mensaje 500 para usuario final debe ser institucional, sin tecnicismos, sin exponer detalles.

**Alternativas:**
| Mensaje | Tono | Información |
|---------|------|-------------|
| **"Error interno del servidor. El equipo técnico ha sido notificado."** | Formal, institucional | Mínima; tranquilidad usuario. |
| **"Ha ocurrido un error inesperado. Por favor, intente nuevamente más tarde."** | Usuario final | Genérico; no dice "interno". |
| **"Error del sistema (código: {request_id}). Contacte soporte si persiste."** | Técnico-ligero | Permite trazabilidad interna via request_id. |

**Recomendación Técnica:** **Opción 1** — "Error interno del servidor. El equipo técnico ha sido notificado." Cumple: español institucional, sin tecnicismos, no expone detalles, transmite que hay seguimiento. Incluir `request_id` en `details` opcional para soporte.

**Tareas Bloqueadas:** SEC-T010 mensaje final 500.

**Responsable Aprobación:** UX Lead / Product Owner  
**Fecha Límite:** Pre-SEC-T010 (Fase 3)

---

### DEC-010: Content Security Policy (CSP) en production.py (SEC-T001)

**Problema:** `SEC-T001` incluye headers seguridad. CSP (`Content-Security-Policy`) es potente pero complejo: puede romper frontend si no se configura correctamente (scripts inline, estilos, fuentes, conexiones).

**Alternativas:**
| Enfoque | Descripción |
|---------|-------------|
| **A) Incluir CSP estricta desde inicio** | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';` Requiere auditoría frontend para nonces/hashes scripts inline. |
| **B) Incluir CSP solo `frame-ancestors 'none'` + `base-uri 'self'`** | Mínimo protege clickjacking y base href. Bajo riesgo rompimiento. |
| **C) No incluir CSP en MVP producción** | Dejar para fase posterior; priorizar HSTS, cookies, headers básicos. Documentar como deuda técnica. |
| **D) CSP en modo `Report-Only`** | `Content-Security-Policy-Report-Only: ...` + endpoint reporte. Monitorear violaciones sin bloquear. Luego endurecer. |

**Recomendación Técnica:** **Opción D (Report-Only)** — Permite detectar violaciones reales del frontend en staging/producción sin romper funcionalidad. Tras 2-3 semanas análisis reportes → endurecer a CSP bloqueante. Incluir `frame-ancestors 'none'` y `base-uri 'self'` en modo bloqueante desde inicio (bajo riesgo).

**Tareas Bloqueadas:** SEC-T001 configuración final headers.

**Responsable Aprobación:** Responsable Seguridad / DevOps / Frontend Lead  
**Fecha Límite:** Fase 1 (Semana 1-2, durante SEC-T001)

**Resolución (2026-11-05):** **APROBADA — Opción D.** `Content-Security-Policy-Report-Only` para el resto de directivas; `frame-ancestors 'none'` y `base-uri 'self'` bloqueantes desde el inicio. Se documenta expresamente que el modo Report-Only **no proporciona protección bloqueante** para ninguna directiva distinta de `frame-ancestors`/`base-uri` — solo reporta violaciones (y, en esta fase, sin un endpoint de recepción de reportes, el reporte solo es visible manualmente vía herramientas de desarrollador). Detalle completo en `PAQUETE_APROBACION_SEC-T001_DEC_002_003_010.md` §3 y `DECISION_LOG.md`.

---

### 10bis. Nota sobre DEC-004 y su relación real con SEC-T001 (resuelta 2026-11-05)

La ficha de SEC-T001 listaba a `DEC-004` (umbral de cobertura de tests) como una de sus precondiciones. Verificación confirmada: ninguna parte del contenido real de SEC-T001 (`production.py`, Dockerfile, docker-compose, Nginx, `.env.example`) depende de un umbral de cobertura — eso es exclusivamente contenido de `SEC-T016`. Era un error de redacción en la ficha original, no una dependencia real.

**Aprobado 2026-11-05:** corregir la ficha de SEC-T001 eliminando la referencia a `DEC-004` de su lista de precondiciones, manteniendo `DEC-004` asociada únicamente a `SEC-T016` (donde ya estaba correctamente referenciada). **El valor del umbral de cobertura en sí (DEC-004) sigue sin aprobar** — esta resolución es puramente documental/estructural, no fija ningún porcentaje. Corrección aplicada en `FICHAS_TECNICAS_SEC_T001_SEC_T021.md`.

---

## Matriz de Decisiones vs Tareas Bloqueadas

| Decisión | Tareas Bloqueadas Directamente | Tareas Impactadas Indirectamente |
|----------|-------------------------------|----------------------------------|
| DEC-001 (MIME method) | SEC-T007 | SEC-T001 (Dockerfile deps) |
| DEC-002 (Throttling login rate) | SEC-T002 | SEC-T017 (tests throttling) |
| DEC-003 (Throttling upload rate) | SEC-T008 | SEC-T017 (tests throttling) |
| DEC-004 (Coverage threshold) | SEC-T016 | SEC-T017 (CI quality gate) |
| DEC-005 (Retention policy) | SEC-T019 | — |
| DEC-006 (Declaratoria download endpoint) | SEC-T009 | — |
| DEC-007 (ACD 4 placeholders) | SEC-T021 | — |
| DEC-008 (Refresh token storage) | SEC-T003 (frontend coord) | SEC-T017 (tests auth flow) |
| DEC-009 (500 message) | SEC-T010 | — |
| DEC-010 (CSP strategy) | SEC-T001 (headers) | — |

---

## Protocolo de Aprobación

1. **Responsable del proyecto** revisa esta lista.
2. Para cada decisión: **Aprobar recomendación** / **Seleccionar alternativa** / **Solicitar más análisis**.
3. Decisiones aprobadas → actualizar fichas técnicas correspondientes (SEC-TXXX) con valor decidido.
4. Decisiones pendientes → tareas permanecen **BLOQUEADAS** hasta resolución.
5. Registrar decisiones en `DECISION_LOG.md` con fecha, responsable, justificación.

---

**Firma:** opencode AI Assistant  
**Fecha:** 2026-11-05  
**Próxima acción:** Reunión de aprobación de DEC-001 a DEC-004 (bloquean inicio Fases 1-3) y DEC-008 (coordina SEC-T003).