# 05 — AUDITORÍA DE CUMPLIMIENTO SDD (Spec-Driven Development)

Alcance: `sgt-siaaf/.specify/`, `sgt-siaaf/specs/001-tramite-titulacion/`, ADRs `docs/` y `backend/docs/`, y contraste con el código.

## 1. Inventario de artefactos SDD

| Artefacto | Estado material | Contenido |
|---|---|---|
| **Constitution.md** (v2.0) | ✓ existe, densa | 18 principios **P-01..P-18**, 3 fases de entrega, modelo de 11 entidades, matriz rol×acción×recurso×dependencia, 10 criterios de éxito, flujo SDD de 7 etapas, gestión del cambio de 6 pasos |
| **specify.md** (v2.0.0) | ✓ existe, densa | RF-001..RF-016, RNF-001..RNF-018, HU-001..HU-010, RN-001..RN-012, EX-001..EX-010, CA-001..CA-008, matriz de trazabilidad integral §15, asuntos pendientes AP-01..AP-04, enums (7 estados expediente, 6 estados petición), 8 roles |
| **plan.md** (v1.0.0) | ✓ existe | Decisiones técnicas (hexagonal+monolito, SimpleJWT, ReportLab, pytest), 5 paquetes semanales, límites modulares §11, matriz de trazabilidad arquitectónica, lista de **8 ADRs declarados "Aceptados"** |
| **tasks.md** (v1.0.0) | ✓ existe | **T001..T046** en 8 paquetes, todas con prioridad y "Entrega: MVP", matriz §8 RF/RNF↔T, checklist de validación §12 |
| **clarify.md** (v1.0.0) | ✓ existe | 8 asuntos (AP-01..AP-08), **5 decisiones DEC-01..DEC-05**, riesgos RSK-01..08, condiciones de cierre |
| **adr/ (spec-level)** | ❌ **DDDD 0 bytes** | `ADR-001-arquitectura.md` y `ADR-002-limites-modulares.md` están **vacíos** |
| **.specify/templates/** | ❌ **0 bytes** | 3 plantillas (spec/plan/tasks) vacías |
| **ADRs backend/docs/adr/** | ⚠️ 3 de 8 | Existen 0001 (hexagonal), 0002 (stack), 0003 (JWT). **Faltan 0004..0008** que plan.md lista como "Aceptados" (T006/T042 exigirían crearlos) |
| **ADRs docs/adr/** | ⚠️ duplicados divergentes | 0001 y 0002 con contenido distinto (no idéntico, verificado con diff) a los de backend/docs |
| **security_report.md** (T044) | ✓ único en `docs/` | Gitleaks/Bandit/Safety ejecutados el 22-oct-2026; DRF 3.16.1 con 2 CVEs documentados |

## 2. Evaluación de trazabilidad plan→código (verificación por muestreo)

| Tarea (tasks.md) | Evidencia verificada | Veredicto |
|---|---|---|
| T001-T005 (infraestructura Docker) | Dockerfile, compose, se levanta OK | ✓ realizada |
| T006 (ADR-001/002) | `backend/docs/adr/0001,0002` (duplicados divergentes en `docs/adr/`) | ✓ realizada con deuda (duplicación) |
| T007-T012 (JWT+RBAC, migración custom user) | `authentication/…` completo; `test_jwt.py`, `test_rbac_permissions.py` | ✓ realizada |
| T013-T019 (expedientes + motor de plazos) | modelos, servicios, `plazo_calculator.py`, 6 suites de test | ✓ realizada |
| T020-T025 (peticiones + PDF) | models/serializers/views/services + 4 suites con seguridad (magic bytes, IDOR) | ✓ realizada |
| T026-T031 (checklist/observaciones) | 4 services + 4 suites; **T028 "API checklist consultar" quedó inoperable** (sin celda GET en RBAC) | ⚠ parcial |
| T032-T036 (resoluciones + PDF) | services + pdf_generator; pero suite de tests rota (74 fallos) y memorando no persistido | ⚠ parcial |
| T037-T041 (notificaciones + Mock SGA) | signals + notification_service + SGAMockAdapter + fixtures | ✓ realizada |
| T042-T046 (OpenAPI, E2E, seguridad, cierre) | openapi.yaml ✓; E2E existe pero **excluido de la corrida** (`testpaths=["src/apps"]`) y 1/4 falla; security_report T044 ✓ | ⚠ parcial |

**Conclusión de trazabilidad:** elevada correspondencia tasks↔módulos实现的o: no se detectó **funcionalidad de código sin tarea autorizada** (toda funcionalidad presente mapea a un RF con tarea). Sí existen **declaraciones plan que no tienen implementación** (ADRs 0004-0008, health check, RNF-005/006, producción con gunicorn).

## 3. Contradicciones documentales (entre fuentes, ambas versiones citadas)

| # | Contradicción | Versión A | Versión B |
|---|---|---|---|
| CD-01 | **Esquema de principios constitucionales** | Constitución define **P-01..P-18** | specify/plan/tasks/clarify citan sistemáticamente **"Principios C-001..C-020"** (p. ej. C-004=RBAC, C-008=auditoría…) — identificadores **inexistentes** en la constitución. (Clarify usa P-11 en DEC-01, mezclado con C-XXX) |
| CD-02 | **Estado de la Constitución** | constitution.md: "Propuesta para revisión y aprobación del equipo" | specify.md: "Constitución v2.0.0 **Oficial**" |
| CD-03 | **Plazo con pausa (AP-01)** | RN-002 titulada "Plazo **Ininterrumpido** de 8 días laborables" | clarify DEC/T014/RN aplican **pausa** del plazo en OBSERVADA (el código SÍ implementa pausa, alineada con B) — el specify no fue actualizado |
| CD-04 | **Estado de AP-01** | clarify: `PARCIALMENTE RESUELTO (descr. válido normativa)` | §9 de tasks: " tweeting **RESUELTO**" |
| CD-05 | **Nominación de campos de plazo** | plan.md: `dias_laborables_acumulados`/`.fecha_ultima_pausa` | clarify F-01: `dias_laborables_consumidos` (el código usa los de plan) |
| CD-06 | **ACompetencia de certificados (AP-03)** | clarify DEC-02 y código: estudiante **o SECRETARIA_CARRERA** | tasks/RBAC: sólo ESTUDIANTE cell en `peticiones POST` propia; `subsanar` sí desglosa ambas — parcial desalineado |
| CD-07 | **Périmetro de producción** | plan.md ADR-0002: "Nginx + Gunicorn" (tabla docs/adr/0002) | Dockerfile: `CMD runserver` |
| CD-08 | **README vs realidad** | README: "468 tests, 95% cobertura" | Medido: 494 tests en total, **88%**, con 74 fallos |
| CD-09 | **commit_msg.txt vs realidad** | "200+ tests passing (>80% cobertura)" | Caracterizado como afirmación puntual: la suite actual está en fallo |
| CD-10 | **ADR-0002 narrator vs tasks** | 8 ADRs "Aceptados" en backend/docs/adr | 3 archivos existen |

## 4. Cumplimiento de RNF (verificado por muestreo)

| RNF | Declara | Cumplimiento real | Evidencia |
|---|---|---|---|
| RNF-001/002/003 | JWT, RBAC, anti-IDOR | ✓ alto | permissions.py, scope_filter.py, tests IDOR |
| RNF-004 | magic bytes | ✓ | pdf_validation.py |
| RNF-005 | p95<500ms, 50 usu., Locust | **No verificable** | No ensuedfulness de pruebas de carga en el repo |
| RNF-006 | disponibilidad + `/health/` | **No implementado** | ausente en urls.py |
| RNF-007 | REST/OpenAPI v3 /api/v1/ | ✓ | drf-spectacular + openapi.yaml |
| RNF-008 | Adapters/Mocks | ✓ | mock_sga |
| RNF-009 | Django 5.x monolito modular | ✓ | settings |
| RNF-010 | Docker reproducible | ⚠ parcial | despliegue vía runserver/DEBUG; pyproject/tests no empaquetados |
| RNF-011 | PEP8/typing | ⚠ parcial | flake8/mypy configurados pero **sin workflow CI se verifica su ejecución en la auditoría**. mypy no corrido |
| RNF-012 | cobertura >70% | ✓ **88% medido** (des PoC) — aunque la afirmación interna de ">80% por módulo" falla en `declarar_aptitud` (35%) y `verificacion views` (65%) |
| RNF-013 | WCAG (frontend) | n/a | sin frontend |
| RNF-014 | secretos .env + gitleaks | ✓ con defectos | `.env.example` ok; pero `gitleaks.exe` commiteado, `.gitleaksignore` formato inválido, secretos de prueba en `verify_all_tasks.py:391-392` |
| RNF-015 | logging sin stacktraces | **No implementado** | sin LOGGING en settings; `print()` de debug en producción |
| RNF-016 | HTTPS/TLS 1.3 | **No implementado** | nginx sin TLS; X-Forwarded-Proto sí se paser but no sandwich |
| RNF-017 | gobernanza SDD/auditoría IA-código | ❌ | sin repositorio git en la copia: no hay historia de cambios |
| RNF-018 | ADRs en docs/adr/ | ⚠ 3/8 | faltan 4 ADRs del plan |

## 5. Estados de tareas

Estructura declarada en tasks.md §5: `[ ] Pendiente / [/] En progreso / [x] Completado`. **Ninguna de las 46 tareas lleva marca de estado** → formalmente 0/46 completadas, lo que contradice la realidad del código (la Fase 1 MVP está sustancialmente construida) y **viola propio flujo SDD** de la constitución (etapas Implement/Validate con registro de estado).

## 6. Innovaciones y debilidades metodológicas

- **Debilidad mayor:** la **copia de trabajo no es repositorio Git** (no hay `.git`): el estándar SDD/PR template (`.github/PULL_REQUEST_TEMPLATE.md` exige tareas/RF por PR) no puede surtir efecto. La trazabilidad verificable vía commits está rota.
- **Debilidad media:** plantillas del Spec Kit vacías ⇒ la forma de artefactos es autoral, no metódica.
- **Debilidad media:** doble ubicación de ADRs con contenido divergente (`docs/adr` vs `backend/docs/adr`) — la única ubicación oficial según RNF-018 es `docs/adr/`; T006 dice "backend/docs/adr".
- **Fuerte:** densidad de vinculación HU↔RF↔RN↔EX↔CA↔T en specify/plan/tasks (§15) — muy por encima del estándar académico.
- **Fuerte:** clarify gestionó 8 asuntos con decisiones cerradas y riesgos documentados (RSK-01..08); el código implementó las decisiones DEC-01..DEC-05 verificables en servicios (pausa del plazo, in-app, sin recálculo de promedios, firma externa).
