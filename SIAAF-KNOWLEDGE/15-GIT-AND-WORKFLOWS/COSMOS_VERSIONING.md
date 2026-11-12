---
system: SGT-SIAAF
type: workflow
status: active
source: user-directive 2026-11-12 (DK-011) + repository-history
last_updated: 2026-11-12
---

# Versionado: SemVer + COSMOS

> Política permanente (**DK-011**, 2026-11-12). Versión operativa: `CLAUDE.md` § "Flujo Git", regla 6.
> **Fuente única de verdad:** [`COSMOS_REGISTRO.json`](COSMOS_REGISTRO.json). Las secciones marcadas como *generadas* se producen con `scripts/cosmos/cosmos.py documentar`. No se editan a mano: `verificar` detecta cualquier diferencia con el registro.

## 1. Reglas

1. **SemVer `vX.Y.Z`.** MAJOR = incompatible; MINOR = funcionalidad nueva compatible; PATCH = correcciones compatibles. Se versiona por **entrega integrada y validada en `main`**, nunca por commit. Sin sufijos (`-helios` sería una pre-release SemVer) ni `V` mayúscula.
2. **Solo documentación no genera versión** (DK-005). Si desde la última versión solo cambian `docs/`, `SIAAF-KNOWLEDGE/`, `Documentacion-parte-2/`, `DOCUMENTACION/`, archivos `.md` o la propia herramienta `scripts/cosmos/`, no se crea versión. Esa documentación entra en la siguiente versión funcional.
3. **Un hito por versión, en el orden del catálogo.** Cada versión nueva usa el **siguiente hito disponible** del catálogo (§2). No se inventan nombres ni se reutiliza un hito ya asignado, aunque sea sin versión (ORION, ROSETTA). Los hitos que la secuencia ya superó no se recuperan. Única excepción histórica: ANDROMEDA (v0.2.0 y v0.3.0). Si el catálogo se agota o hay que saltar un hito, el equipo lo decide y lo registra en `DECISIONS_LOG`.
4. **Etiqueta anotada `vX.Y.Z` sobre el commit exacto** de la entrega en la historia principal (*first-parent*) de `main`, es decir, el merge publicado. La primera línea del mensaje es `HITO vX.Y.Z — Título`, igual que el título de la GitHub Release.
5. **Las etiquetas publicadas son inmutables.** No se mueven, ni se borran, ni se reemplazan, ni se publican con `--force`. Un error se corrige con una versión nueva (PATCH).
6. **Retrospectivas.** Solo para entregas pasadas cuyo commit se ha verificado en la historia principal de `main` y con autorización expresa. El mensaje de la etiqueta y las notas indican que es retrospectiva y la fecha real de la entrega; la fecha de la etiqueta es la de su creación. No se versionan entregas sin evidencia de versión: ORION y `edee296` quedan **sin versión**.
7. **Antes de la versión estable (0.x).** Representa la etapa anterior a la primera versión estable. Un cambio incompatible incrementa MINOR. `v1.0.0` solo se publica cuando el equipo declara formalmente la primera versión estable (decisión en `DECISIONS_LOG` y campo `primera_version_estable` del registro). Sin esa declaración, `verificar` rechaza cualquier versión ≥ 1.0.0.
8. **Autorización.** Crear o publicar etiquetas y releases exige la confirmación explícita del responsable, igual que el merge en `main`. Las herramientas son de solo lectura o simulación por defecto.
9. **Registro.** Cada versión se anota en el registro con: commit, fecha, descripción, cambios, validaciones, pendientes y estado (`preparada` → `publicada`).

## 2. Catálogo oficial y estado (generado)

<!-- cosmos:catalogo:inicio -->
| N.º | Hito | Estado |
|---|---|---|
| 1 | ORION | usado sin versión |
| 2 | POLARIS | no asignado (la secuencia ya lo superó) |
| 3 | SATURN | no asignado (la secuencia ya lo superó) |
| 4 | SIRIUS | no asignado (la secuencia ya lo superó) |
| 5 | MERCURY | no asignado (la secuencia ya lo superó) |
| 6 | PULSAR | no asignado (la secuencia ya lo superó) |
| 7 | ROSETTA | usado sin versión |
| 8 | ANDROMEDA | asignado a v0.2.0, v0.3.0 |
| 9 | VEGA | no asignado (la secuencia ya lo superó) |
| 10 | QUASAR | no asignado (la secuencia ya lo superó) |
| 11 | EUROPA | no asignado (la secuencia ya lo superó) |
| 12 | ORBIT | no asignado (la secuencia ya lo superó) |
| 13 | NOVA | no asignado (la secuencia ya lo superó) |
| 14 | ECLIPSE | asignado a v0.4.0 |
| 15 | HELIOS | asignado a v0.5.0 |
| 16 | TRAPPIST | disponible |
| 17 | SUPERNOVA | disponible |
<!-- cosmos:catalogo:fin -->

> El significado temático de cada hito no está documentado. Solo constan sus usos.

## 3. Versiones (generado)

<!-- cosmos:versiones:inicio -->
| Versión | Hito | Commit | Fecha | Título | Tipo | Estado |
|---|---|---|---|---|---|---|
| `v0.2.0` | ANDROMEDA | `b6b953a` | 2026-11-05 | Base funcional del frontend: F0–F2.5 y V-01 | retrospectiva | preparada |
| `v0.3.0` | ANDROMEDA | `f279090` | 2026-11-06 | Gestión de expedientes y requisitos | retrospectiva | preparada |
| `v0.4.0` | ECLIPSE | `d020592` | 2026-11-10 | Implementación de seguridad del backend SGT-SIAAF | retrospectiva | preparada |
| `v0.5.0` | HELIOS | `025de78` | 2026-11-12 | Integridad de archivos privados, errores de dominio y endurecimiento de seguridad | ordinaria | preparada |
<!-- cosmos:versiones:fin -->

**Entregas sin versión:**

<!-- cosmos:sin-version:inicio -->
| Commit | Fecha | Hito | Descripción |
|---|---|---|---|
| `0e200d9` | 2026-10-20 | ORION | Estructura del proyecto y documentación Spec Kit (`chore(orion)`). Inicio del ciclo; sin versión registrada. |
| `edee296` | 2026-11-02 | — | Backend Fase 1–2, T001–T046 (PR #11). Sin hito ni versión registrados. |
| `fe75d39` | 2026-11-11 | ROSETTA | Documentación maestra DP2 (PR #21). Solo documentación: no genera versión (DK-005). |
<!-- cosmos:sin-version:fin -->

## 4. Detalle de cada versión (generado)

<!-- cosmos:detalle:inicio -->
### ANDROMEDA v0.2.0 — Base funcional del frontend: F0–F2.5 y V-01

Primera entrega versionada: base funcional del frontend (andamiaje, autenticación, UI Kit, estados de error y pantalla de login). El merge también incorporó documentación y prototipos de diseño.

Commit `b6b953aa313e858218eb71ac6163e4873395e066` · fecha 2026-11-05 · estado **preparada** · **retrospectiva**

**Cambios:**

- F0: andamiaje, configuración y estructura del frontend.
- F1: autenticación, gestión de sesión y cliente HTTP.
- F2: UI Kit y componentes reutilizables.
- F2.5: estados de error y recuperación.
- V-01: pantalla de login.

**Validaciones:**

- 226/226 pruebas superadas (reportado en 467ec3b).
- ESLint, TypeScript y build sin errores (reportado en 467ec3b).

**Pendientes conocidos:**

- FE-T1213 (InlineAlert 409/412/428) bloqueada por BE-11.

**Referencias:**

- Rama release/0.2.0-andromeda; commit 467ec3b `feat(frontend): integrar F0–F2.5 y V-01`.
- Merge en main b6b953a.

### ANDROMEDA v0.3.0 — Gestión de expedientes y requisitos

Vista V-04 (FE-T401–FE-T411): detalle de expedientes, checklist de requisitos, envío, observaciones, evaluación, subsanación y descargas, sobre los contratos reales del backend.

Commit `f2790908f256a932528b0036b3a07258776b4cfc` · fecha 2026-11-06 · estado **preparada** · **retrospectiva**

Excepción de hito: ANDROMEDA abarcó v0.2.0 y v0.3.0 antes de DK-011; reutilización histórica aceptada y no repetible.

**Cambios:**

- Consulta del detalle de expedientes.
- Checklist de requisitos: envío, observaciones, evaluación y subsanación.
- Descarga autenticada de documentos y versiones.
- Matriz de acciones por rol y estado.

**Validaciones:**

- 328/328 pruebas superadas; 51 nuevas (reportado en f279090).
- Cobertura de features/expediente superior al 80 % en las cuatro métricas (reportado).
- ESLint, TypeScript y build satisfactorios (reportado).

**Pendientes conocidos:**

- INC-21 (P1): algunos errores de reglas de negocio responden HTTP 500.
- FE-T407 (P1): el estudiante no puede descubrir el checklist_verification_id para subsanar.
- Incidencia heredada P2 en queryClient.ts (status 0).
- V-05 fuera de la entrega.

**Referencias:**

- Rama release/0.3.0-andromeda; PR #14.
- afdd989 es un merge previo sin cambios; la entrega es f279090.

### ECLIPSE v0.4.0 — Implementación de seguridad del backend SGT-SIAAF

Controles de seguridad del backend: configuración de producción, throttling, JWT, validación y almacenamiento privado de PDF, RBAC con aislamiento de expedientes, máquina de estados, logging estructurado y restricción de la documentación de la API en producción.

Commit `d02059255d87b1dfd6839da1bbf604c47c7923c2` · fecha 2026-11-10 · estado **preparada** · **retrospectiva**

**Cambios:**

- HTTPS, HSTS, CSP, CORS, cookies y cabeceras de seguridad.
- Throttling de autenticación y de carga de documentos.
- JWT stateless con claves SECRET_KEY y JWT_SIGNING_KEY separadas.
- Validación de PDF (magic bytes, SHA-256, 10 MB) y almacenamiento privado.
- RBAC y aislamiento de expedientes con ScopeFilterMixin.
- Máquina de estados, plazos y protección de campos críticos.
- Logging JSON con filtros de datos sensibles y request_id.

**Validaciones:**

- 497 pruebas aprobadas según la matriz de trazabilidad (reportado en 8e1e1a2).

**Pendientes conocidos:**

- SEC-T014 bloqueada por DEC-009.
- SEC-T015: verificación real de FirmaEC.
- SEC-T016: migración a RS256.
- VULN-001 a VULN-014 con coberturas diferenciadas.
- SEC-T017 a SEC-T024 pendientes.

**Referencias:**

- Rama release/0.4.0-eclipse; commit 8e1e1a2; PR #16 (a develop) y PR #17 (a main).
- 4ac69d1 ('Merge branch release/0.4.0-eclipse into main') no incorporó cambios; la entrega llega a main en d020592.

### HELIOS v0.5.0 — Integridad de archivos privados, errores de dominio y endurecimiento de seguridad

Endurecimiento de seguridad P0 e inicio de la verificación, errores de dominio uniformes con bloqueo ordenado y corrección de archivos privados huérfanos con conciliación segura.

Commit `025de7887dca9acacf296e629703381ba6734ce1` · fecha 2026-11-12 · estado **preparada**

**Cambios:**

- INC-01: throttling de operaciones mutantes, ámbito 'asignado' y verificación SHA-256 al servir PDF (d1fa86e).
- E2-06: registrar_transicion() como único punto de cambio de estado (d1fa86e).
- E2-01: POST /expedientes/{id}/iniciar-verificacion/ con checklist atómico (d1fa86e).
- PLB-E1-04 + O-2: errores de dominio {detail, code} y bloqueo expediente → petición → checklist (3317231).
- I-3: almacenamiento privado atómico, compensación de archivos y comando reconciliar_archivos (025de78).
- Documentación incluida sin versión propia (DK-005): DP2/ROSETTA, bóveda SIAAF-KNOWLEDGE y política DK-010.

**Validaciones:**

- pytest SQLite sobre main 025de78: 637 aprobadas, 13 fallidas (test_pdf_generator.py, pypdf ausente; 30/30 con lector pdftotext).
- PostgreSQL 16.15: tests/integration 13/13, tests/ 37/37, src/apps 629 aprobadas y 21 fallos conocidos (13 pypdf + 8 H-30).
- manage.py spectacular --validate: 0 errores; esquema idéntico al de develop.
- Auditoría independiente I-3: APROBADA CON OBSERVACIONES (docs/auditorias/AUDITORIA_INDEPENDIENTE_I3.md).

**Pendientes conocidos:**

- D-07: reconciliar_archivos no informa de registros sin archivo (H-I3-07).
- D-09: test_postgres_infra.py depende del orden de ejecución.
- El bloqueo de reconciliar_archivos solo es efectivo en PostgreSQL.
- DK-010: sin evidencia de la notificación a los integrantes de su atribución delegada.
- pypdf no declarado en dependencias de desarrollo (E0-01).
- H-30: 8 pruebas de índices fallan en PostgreSQL.
- Decisión funcional O-1 (hoy 409) e I-4 (contracts/openapi.yaml difiere de openapi.yaml).
- AUT-01, AUT-03 y VULN-005/006/010 registradas como abiertas en d1fa86e.

**Referencias:**

- Merges en main d1fa86e, 3317231 y 025de78.
- Rama fix/i3-archivos-huerfanos (00d7802), integrada en develop con 063f07e.
<!-- cosmos:detalle:fin -->

## 5. Procedimiento de publicación

Se aplica tras cada merge `develop` → `main` autorizado (`CLAUDE.md` § Flujo Git, paso 4):

| Paso | Acción | Herramienta |
|---|---|---|
| 1 | Identificar los cambios desde la última versión | `cosmos.py proponer` |
| 2 | Proponer el incremento SemVer (MAJOR/MINOR/PATCH), o «sin versión» si es solo documentación | `proponer` |
| 3 | Proponer el siguiente hito disponible | `proponer` |
| 4 | Comprobar que la versión y el hito no estén asignados (registro y etiquetas local y remota) | `proponer`, `verificar` |
| 5 | Comprobar que el commit pertenece a la historia principal de `main` | `proponer`, `verificar` |
| 6 | Ejecutar las pruebas y anotar los resultados reales | suite del proyecto |
| 7 | **Pedir autorización explícita** al responsable (versión, hito, commit, notas) | — |
| 8 | Registrar la versión (`preparada`), commit del registro en una rama `docs/` e integración | `cosmos.py registrar` |
| 9 | Simular la publicación | `cosmos.py publicar vX.Y.Z` |
| 10 | Crear la etiqueta anotada, publicarla con push normal y crear la GitHub Release | `publicar vX.Y.Z --ejecutar --confirmar vX.Y.Z` |
| 11 | Marcar la versión como `publicada` y hacer commit del registro | `cosmos.py marcar-publicada vX.Y.Z` |

El registro puede integrarse en `main` después del commit etiquetado: la etiqueta apunta a la entrega, no al commit que la documenta.

## 6. Herramienta `scripts/cosmos/cosmos.py`

Solo biblioteca estándar de Python 3 (sin dependencias). Códigos de salida: 0 correcto, 1 incoherencia o bloqueo, 2 error de uso o rechazo.

```bash
python3 scripts/cosmos/cosmos.py verificar               # solo lectura (consulta el remoto)
python3 scripts/cosmos/cosmos.py --sin-remoto verificar  # solo lectura, sin red
python3 scripts/cosmos/cosmos.py proponer                # siguiente versión, incremento e hito
python3 scripts/cosmos/cosmos.py notas v0.5.0            # notas de la release (o --formato etiqueta)
python3 scripts/cosmos/cosmos.py documentar              # regenera las secciones generadas
python3 scripts/cosmos/cosmos.py registrar --version v0.6.0 --hito TRAPPIST --commit <sha> \
    --titulo "…" --descripcion "…" --cambio "…" --validacion "…" --pendiente "…"
python3 scripts/cosmos/cosmos.py publicar v0.5.0         # SIMULACIÓN: no crea ni publica nada
python3 scripts/cosmos/cosmos.py publicar v0.5.0 --ejecutar --confirmar v0.5.0   # solo con autorización
python3 scripts/cosmos/cosmos.py marcar-publicada v0.5.0
```

**`verificar` comprueba:**
- **Formato y catálogo:** formato SemVer; hito del catálogo, sin reutilizar y en secuencia.
- **Coherencia entre versiones:** versiones únicas e incrementos SemVer válidos; ninguna versión ≥ 1.0.0 sin declaración de estabilidad.
- **Commits:** SHA completo existente en la historia principal de `main`, cada uno descendiente del anterior, y fecha igual a la del commit.
- **Etiquetas:** anotadas, sobre el commit registrado y con la primera línea correcta; la local y la remota son el mismo objeto; ninguna etiqueta `vX.Y.Z` fuera del registro; las versiones `publicada` tienen etiqueta local y remota.
- **Documento:** las secciones generadas coinciden con el registro.

**`publicar`:**
- Repite todas las comprobaciones y además exige que la etiqueta no exista en local ni en el remoto, y que el commit esté en la historia principal de `origin/main`.
- Sin `--ejecutar --confirmar <versión idéntica>` solo simula.
- Para crear la release usa `gh` si está instalado; si no, la API de GitHub con `GITHUB_TOKEN`; y si tampoco hay token, muestra el título y las notas para crearla a mano.

**Pruebas:** `python3 -m unittest discover -s scripts/cosmos -p 'test_*.py'`.

## Relacionado

[[GIT_POLICY]] · [[DECISIONS_LOG]]
