---
system: SGT-SIAAF
type: audit
area: security
status: partially-verified
source: repository-docs + verified-code
last_verified: 2026-11-11
---

# Auditoría de seguridad — estado consolidado

> Esta nota **no** reemplaza los informes originales: los indexa, contrasta sus afirmaciones con el código y registra las contradicciones. Cifras y estados de controles son los de cada fuente, con su fecha.

## 1. Fuentes

| Fuente | Ruta | Fecha | Contenido |
|---|---|---|---|
| Matriz de trazabilidad de seguridad | `docs/auditoria-backend/seguridad/MATRIZ_TRAZABILIDAD_SEGURIDAD.md` | 2026-11-05 | 77 controles en 11 dominios; 34 verificados, 18 pendientes, 11 fallidos, 8 parciales, 5 no verificables, 1 sin prueba |
| Backlog de tareas de seguridad | `docs/auditoria-backend/TASKS_SEGURIDAD.md` | — | SEC-T001…SEC-T021 (tabla de estados "Pendiente": instantánea previa a la implementación) |
| Plan de implementación y cierre | `docs/auditoria-backend/seguridad/plan-implementacion/` (11 docs) | — | Fichas SEC-T001…T021, decisiones DEC-002/003/010, acta de cierre SEC-T004, checklist |
| Informes de seguridad | `docs/auditoria-backend/{AUDITORIA_SEGURIDAD,INFORME_FINAL_VALIDACION}.md`, `seguridad/{INFORME_HARDENING_SEGURIDAD,INFORME_PRUEBAS_SEGURIDAD,CHECKLIST_SEGURIDAD_DETALLADA,BACKLOG_BRECHAS_SEGURIDAD}.md` | — | Hallazgos, pruebas y hardening |
| Configuración de seguridad | `docs/06-seguridad/SECURITY_CONFIG.md`, `docs/security_report.md` | — | — |
| Commit ECLIPSE | `8e1e1a2` `feat(security): integrar controles de seguridad del backend SGT-SIAAF` | — | Lista de controles implementados y pendientes |
| Plan maestro (DP2) | [[DP2-PLAN_MAESTRO]] §2.2, §3.2 | 2026-11-09 | "87 controles, 73,6 %", "~85 % OWASP ASVS L2", VULN-001…014 |

## 2. Controles verificados en código (2026-11-11)

| Control | Evidencia |
|---|---|
| JWT access 30 min / refresh 24 h, HS256, `JWT_SIGNING_KEY` separada | `backend/src/config/settings/base.py` (`SIMPLE_JWT`) |
| Throttling login 5/min por IP real | `TokenPairView` con `TrustedProxyScopedRateThrottle`, `throttle_scope="auth"` |
| Throttling de carga de documentos 10/h | `PeticionViewSet` → `ScopedRateThrottle`, `document_upload` |
| Validación PDF (tamaño, magic bytes, SHA-256 en carga) | `core/adapters/pdf_validation.py`, `peticiones/services/cargar_documento.py:115` |
| RBAC + aislamiento por ámbito | [[PERMISSIONS_ROLES]] |
| Auditoría inmutable con IP | `notificaciones` `EventoAuditoria` |
| Swagger/ReDoc protegidos | `authentication/tests/test_swagger_protection.py` (prueba existente; no reejecutada) |

## 3. Brechas abiertas (confirmadas en código)

| ID | Brecha | Verificación |
|---|---|---|
| VULN-001 | Sin throttling para endpoints mutantes (enviar, observar, checklist, informes, declaratorias) | Solo hay throttles `auth` y `document_upload`; no existe `MutantOperationThrottle` |
| VULN-002 | `SCOPE_ASIGNADO` no implementado en `ScopeFilterMixin` | Mitigación manual solo en la descarga ([[PERMISSIONS_ROLES]] §4) |
| VULN-003 | Sin verificación de hash al descargar | Sin comparación de SHA-256 en `descargar_documento` (grep sin coincidencias) |
| VULN-005 | Refresh sin rotación, sin blacklist, sin logout | `ROTATE_REFRESH_TOKENS=False`; no hay rutas |
| VULN-006 | `RESPONSABLE_DEPENDENCIA` sin celdas en `RBAC_MATRIX` | Verificado |
| VULN-010 | FirmaEC no verificada en la declaratoria | `declarar_aptitud.py` valida solo el PDF; ver [[FIRMA_EC]] |
| VULN-004, 011–014 | CSP report-uri, RS256, sellado RFC 3161, tests de mass assignment/BOLA, historial de modelos maestros | Según [[DP2-MATRIZ_BRECHAS]]; no reverificados uno a uno |

## 4. Contradicciones entre fuentes

1. **Recuento de controles**: 77 (matriz del 2026-11-05) frente a 87 con 73,6 % (plan maestro del 2026-11-09). No se encontró la fuente de los 87.
2. **Documentos citados que no existen**: DP2 cita `INFORME_TECNICO_AUDITORIA_SEGURIDAD.md` (TEST-02) y `MATRIZ_ESTADO_CONTROLES_SEGURIDAD.md` (plan maestro §12): **no están** en el repositorio (`find` vacío). El catálogo VULN-001…014 solo aparece en DP2 y en el commit ECLIPSE.
3. **Numeración SEC-T inconsistente**: en `TASKS_SEGURIDAD.md`, SEC-T014 = CI/CD Security, SEC-T015 = Dependabot, SEC-T016 = Cobertura. El commit ECLIPSE usa SEC-T014 = "bloqueada por DEC-009", SEC-T015 = "FirmaEC", SEC-T016 = "RS256", y menciona SEC-T017…T024 (el backlog llega a T021).
4. **Estados desactualizados**: `TASKS_SEGURIDAD.md` marca SEC-T002, SEC-T004 y SEC-T008 como "Pendiente", pero el código los implementa (throttle de login, clave JWT separada, throttle de carga). La matriz del 2026-11-05 aún los cuenta como pendientes o fallidos.

**Pendiente de verificación humana:** cuál es la fuente vigente para el estado de controles. Esta nota toma el **código** como verdad para lo implementado.

## Relacionado

[[06-AUDITS/BACKEND/BACKEND_AUDITS|Auditorías backend]] · [[FIRMA_EC]] · [[PERMISSIONS_ROLES]] · [[DECISIONS_LOG]]
