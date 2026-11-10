---
title: "Registro de decisiones técnicas aprobadas"
---

# Registro de decisiones técnicas aprobadas

Registro cronológico de decisiones DEC-001 a DEC-010 (plan de hardening de
seguridad backend). Solo se registran aquí decisiones **efectivamente
aprobadas** por el responsable del proyecto, con fecha, valor aprobado y
justificación. El estado "pendiente" de cada decisión sigue viviendo en
`DECISIONES_TECNICAS_PENDIENTES.md`.

---

## 2026-11-05 — Lote de aprobación para desbloquear SEC-T001

**Autorizado por:** responsable del proyecto, mediante instrucción en esta sesión.

| Decisión | Valor aprobado | Justificación registrada | Efecto |
|---|---|---|---|
| **DEC-002** | 5 solicitudes/minuto/IP para `POST /api/v1/auth/token/` | Valor de referencia OWASP ya documentado; sin datos de tráfico real de la UNL que justifiquen otro valor | **Aplicación efectiva condicionada**: solo surte efecto de protección real una vez SEC-T005 esté cerrada (IP confiable vía `TRUSTED_PROXIES`). Antes de eso, el throttle por IP usaría `REMOTE_ADDR` del proxy, no del cliente real. |
| **DEC-003** | 10 solicitudes/hora/usuario para `POST /api/v1/peticiones/{id}/documento/` | Fundamentado en el catálogo documental real: 5 requisitos obligatorios (Art. 235 RRA-UNL, `migrations/0002_catalogo_base_art235.py`); 10/hora es holgado incluso con reintentos por subsanación | Independiente de SEC-T001/SEC-T005; puede implementarse de inmediato (SEC-T008). |
| **DEC-010** | Opción D: `Content-Security-Policy-Report-Only` para el conjunto general de directivas + `frame-ancestors 'none'` y `base-uri 'self'` como directivas **bloqueantes** desde el inicio | Verificación directa del frontend (Vite, sin scripts inline, sin CDN, sin CSS-in-JS) favorece una política estricta a futuro; Report-Only permite validar sin romper nada mientras tanto | **Documentado expresamente:** el modo Report-Only no bloquea ninguna directiva salvo `frame-ancestors`/`base-uri`. Sin endpoint de recepción de reportes en esta fase — las violaciones solo son visibles manualmente (herramientas de desarrollador), no monitoreadas automáticamente. |
| **DEC-004 (corrección documental, no el umbral en sí)** | Eliminar `DEC-004` de las precondiciones de la ficha de **SEC-T001**; permanece asociada únicamente a **SEC-T016** | Verificado: ningún contenido de la ficha SEC-T001 depende de un umbral de cobertura de tests | Aplicado en `FICHAS_TECNICAS_SEC_T001_SEC_T021.md`. **El valor del umbral de cobertura (el DEC-004 real) sigue sin aprobar** — esto no lo resuelve. |
| **Ubicación de archivos de producción** | Raíz del repositorio, junto a los archivos de desarrollo existentes (no `backend/`) | Coincide con la convención real ya verificada (`Dockerfile`, `docker-compose.yml`, `nginx/` ya viven en la raíz) | Aplica a SEC-T001: `docker-compose.prod.yml` y `nginx/prod.conf` se crean en la raíz / `nginx/` existente, no en `backend/`. |
| **Formato del Dockerfile de producción** | Un único `Dockerfile` multi-stage con *targets* `development` y `production` (no un archivo `Dockerfile.prod` separado) | Evita duplicar las etapas comunes (instalación de dependencias, copia de código) entre dos archivos; coherente con que ya existe un único `Dockerfile` hoy | El `Dockerfile` existente se reestructura en etapas; `docker-compose.yml` (dev) selecciona `target: development`, `docker-compose.prod.yml` (nuevo) selecciona `target: production`. |

**No aprobado en este lote (permanece pendiente, sin cambios):** DEC-001, DEC-005, DEC-006, DEC-007, DEC-008, DEC-009, y el valor numérico real de DEC-004 (umbral de cobertura).
