---
system: SGT-SIAAF
type: workflow
status: active
source: user-directive 2026-11-12 (DK-011, DK-012) + repository-history
last_updated: 2026-11-12
---

# Versionado: SemVer + COSMOS

> Política permanente (**DK-011**, ampliada por **DK-012**, 2026-11-12). Versión operativa: `CLAUDE.md` § "Flujo Git", regla 6.
> **Fuente única de verdad:** [`COSMOS_REGISTRO.json`](COSMOS_REGISTRO.json). Las secciones marcadas como *generadas* se producen con `scripts/cosmos/cosmos.py documentar`. No se editan a mano: `verificar` detecta cualquier diferencia con el registro.

## 1. Reglas

1. **SemVer `vX.Y.Z`.** Se versiona por **entrega integrada y validada en `main`**, nunca por commit. Sin sufijos (`-helios` sería una pre-release SemVer) ni `V` mayúscula. El incremento depende de la **magnitud y compatibilidad** del cambio, nunca del nombre astronómico.
2. **Solo documentación no genera versión** (DK-005). Si desde la última versión solo cambian `docs/`, `SIAAF-KNOWLEDGE/`, `Documentacion-parte-2/`, `DOCUMENTACION/`, archivos `.md` o la propia herramienta `scripts/cosmos/`, no se crea versión. Esa documentación entra en la siguiente versión funcional. Única excepción: v0.1.0 ORION (DK-012).
3. **Hito por propósito dominante (DK-012).**
   - Cada nombre del catálogo identifica **un único hito publicado**.
   - El hito se elige por la **temática que mejor describe el propósito dominante** de la entrega (§2), sin seguir el orden del catálogo.
   - No se inventan nombres ni se reutilizan los ya asignados, tampoco los usados sin versión (ROSETTA). Única excepción histórica: ANDROMEDA (v0.2.0 y v0.3.0).
   - La asignación se **registra y se confirma en un commit antes de publicar**; `publicar` lo comprueba.
   - Para añadir nombres hace falta una decisión en `DECISIONS_LOG`.
4. **Etiqueta anotada `vX.Y.Z` sobre el commit exacto** de la entrega en la historia principal (*first-parent*) de `main`, es decir, el merge publicado. La primera línea del mensaje es `HITO vX.Y.Z — Título`, igual que el título de la GitHub Release. Solo la versión más alta se marca como **Latest**.
5. **Las etiquetas publicadas son inmutables.** No se mueven, ni se borran, ni se reemplazan, ni se publican con `--force`. Un error se corrige con una versión nueva (PATCH).
6. **Retrospectivas.** Solo para entregas pasadas cuyo commit se ha verificado en la historia principal de `main` y con autorización expresa. El mensaje de la etiqueta y las notas indican que son retrospectivas y distinguen la fecha de la entrega de la de publicación. Las validaciones distinguen lo **reportado** en el historial de lo **re-ejecutado**. Quedan sin versión el backend `edee296` y ROSETTA.
7. **Serie 0.x y versión estable.**
   - PATCH: correcciones compatibles.
   - MINOR: funcionalidad nueva y, mientras dure la serie 0.x, también los cambios incompatibles.
   - MAJOR: solo para declarar formalmente la primera versión estable `v1.0.0`, con decisión en `DECISIONS_LOG` y el campo `primera_version_estable` del registro. Sin esa declaración, `verificar` rechaza cualquier versión ≥ 1.0.0.
   - Desde `v1.0.0` rige SemVer convencional: MAJOR para cambios incompatibles, MINOR para funcionalidad compatible y PATCH para correcciones.
8. **Autorización.** Crear o publicar etiquetas y releases exige la confirmación explícita del responsable, igual que el merge en `main`. Las herramientas son de solo lectura o simulación por defecto.
9. **Registro.** Cada versión anota: commit, fecha de entrega, descripción, cambios, validaciones, pendientes y estado (`preparada` → `publicada`). Al publicarse, `marcar-publicada` añade la fecha real, el objeto de la etiqueta y la URL de la release.

**Ejemplos de incremento** (ilustrativos; no son versiones planificadas):

| Situación (desde `v0.5.0`) | Incremento | Resultado |
|---|---|---|
| Solo corrige un error sin cambiar contratos | PATCH | `v0.5.1` |
| Añade un endpoint o una vista nueva | MINOR | `v0.6.0` |
| Cambia un contrato de la API de forma incompatible (serie 0.x) | MINOR | `v0.6.0` |
| El equipo declara formalmente la primera versión estable | MAJOR | `v1.0.0` |
| Solo documentación o `scripts/cosmos/` | ninguno | sin versión |
| Desde `v1.2.3`: cambio incompatible | MAJOR | `v2.0.0` |

**Criterio para elegir el hito:**
- Se identifica el propósito dominante de la entrega: lo que más pesa por alcance y por valor para el usuario.
- Se elige el hito disponible cuya temática lo describa mejor y se justifica en la descripción del registro.
- Si varias temáticas encajan, prevalece la del cambio de mayor impacto.

## 2. Catálogo oficial y estado (generado)

<!-- cosmos:catalogo:inicio -->
| N.º | Hito | Descripción | Temática | Estado |
|---|---|---|---|---|
| 1 | ORION | Constelación ecuatorial del cazador, visible desde ambos hemisferios. | Fundación del proyecto: estructura, constitución y especificaciones. | asignado a v0.1.0 |
| 2 | POLARIS | Estrella polar, alfa de la Osa Menor, junto al polo norte celeste. | Orientación del usuario: navegación, ayuda y guías en la interfaz. | disponible |
| 3 | SATURN | Sexto planeta del sistema solar, gigante gaseoso con un gran sistema de anillos. | Arquitectura: reorganización modular y refactorizaciones estructurales. | disponible |
| 4 | SIRIUS | Estrella más brillante del cielo nocturno, en Canis Major. | Rendimiento y optimización. | disponible |
| 5 | MERCURY | Planeta más cercano al Sol y de traslación más rápida. | Comunicación: notificaciones y mensajería. | disponible |
| 6 | PULSAR | Estrella de neutrones en rotación que emite pulsos de radiación regulares. | Procesos periódicos: plazos, tareas programadas y monitorización. | disponible |
| 7 | ROSETTA | Misión de la ESA al cometa 67P/Churyumov-Gerasimenko, nombrada por la piedra de Rosetta. | Documentación y transferencia de conocimiento. | usado sin versión |
| 8 | ANDROMEDA | Galaxia espiral M31, la gran galaxia más cercana a la Vía Láctea. | Frontend: interfaz web y vistas del trámite. | asignado a v0.2.0, v0.3.0 |
| 9 | VEGA | Estrella alfa de Lyra, referencia histórica de la escala de magnitudes. | Calidad: pruebas, estándares y criterios de aceptación. | disponible |
| 10 | QUASAR | Núcleo galáctico activo extremadamente luminoso, alimentado por un agujero negro supermasivo. | Integraciones externas de alto impacto. | disponible |
| 11 | EUROPA | Luna de Júpiter con un océano de agua bajo su corteza de hielo. | Datos y persistencia: modelo, migraciones e integridad. | disponible |
| 12 | ORBIT | Trayectoria de un cuerpo alrededor de otro bajo la acción de la gravedad. | Flujos de trabajo y máquina de estados del trámite. | disponible |
| 13 | NOVA | Aumento súbito del brillo de una enana blanca en un sistema binario. | Funcionalidad nueva: módulos o capacidades inéditas. | disponible |
| 14 | ECLIPSE | Ocultación total o parcial de un astro por otro. | Seguridad: controles, endurecimiento y protección de datos. | asignado a v0.4.0 |
| 15 | HELIOS | Personificación griega del Sol; nombre también de dos sondas solares. | Integridad y estabilidad del núcleo del sistema. | asignado a v0.5.0 |
| 16 | TRAPPIST | TRAPPIST-1, enana roja con siete planetas rocosos conocidos. | Integración entre módulos y roles. | disponible |
| 17 | SUPERNOVA | Explosión estelar que puede superar brevemente el brillo de toda su galaxia. | Entrega mayor de cierre de ciclo (candidata a la versión estable). | disponible |
| 18 | ATLAS | Luna de Saturno y titán mitológico que sostiene la bóveda celeste. | Infraestructura y despliegue. | disponible |
| 19 | TITAN | Mayor luna de Saturno, con una atmósfera densa. | Capacidad y escalabilidad. | disponible |
| 20 | PHOENIX | Constelación austral del ave fénix. | Resiliencia: recuperación ante fallos y respaldos. | disponible |
| 21 | DRACO | Constelación boreal del dragón, circumpolar en latitudes medias del norte. | Control de acceso: roles, permisos y aislamiento. | disponible |
| 22 | LYRA | Constelación de la lira, que contiene a Vega. | Accesibilidad y experiencia de usuario. | disponible |
| 23 | PEGASUS | Constelación del caballo alado, con el Gran Cuadrado de Pegaso. | Aplicación móvil. | disponible |
| 24 | CYGNUS | Constelación del cisne, sobre la Vía Láctea, donde se encuentra Cygnus X-1. | Reportes, indicadores y analítica. | disponible |
| 25 | CALLISTO | Segunda luna más grande de Júpiter, con una superficie muy craterizada. | Mantenimiento: deuda técnica y código heredado. | disponible |
| 26 | GANYMEDE | Luna de Júpiter, la mayor del sistema solar. | Módulo funcional de gran alcance (por ejemplo, modalidades de titulación). | disponible |
| 27 | ENCELADUS | Luna de Saturno con géiseres de agua en su polo sur. | Flujo de datos: importación, exportación y eventos. | disponible |
| 28 | CERES | Planeta enano, el mayor cuerpo del cinturón de asteroides. | Catálogos y datos maestros. | disponible |
| 29 | ERIS | Planeta enano del disco disperso, de masa similar a la de Plutón. | Concurrencia y resolución de conflictos. | disponible |
| 30 | ALTAIR | Estrella alfa de Aquila, de rotación muy rápida. | Búsqueda y consultas. | disponible |
| 31 | CANOPUS | Segunda estrella más brillante del cielo, usada para orientar sondas espaciales. | Auditoría y trazabilidad. | disponible |
| 32 | ARGO | Argo Navis, antigua constelación del barco de los argonautas. | Colaboración: trabajo multiusuario y asignaciones. | disponible |
| 33 | IO | Luna de Júpiter, el cuerpo con mayor actividad volcánica conocida. | Documentos y archivos: carga, almacenamiento y descarga. | disponible |
| 34 | MAKEMAKE | Planeta enano del cinturón de Kuiper. | Configuración y administración del sistema. | disponible |
| 35 | HAUMEA | Planeta enano del cinturón de Kuiper, alargado por su rápida rotación. | Cumplimiento normativo y reglas legales. | disponible |
| 36 | BETELGEUSE | Supergigante roja variable de la constelación de Orión. | Retiro de funcionalidades y fin de ciclo. | disponible |
<!-- cosmos:catalogo:fin -->

> Las temáticas son orientativas: guían la elección por propósito dominante (regla 3); la descripción es astronómica.

## 3. Versiones (generado)

<!-- cosmos:versiones:inicio -->
| Versión | Hito | Commit | Entrega | Título | Tipo | Estado | Publicación |
|---|---|---|---|---|---|---|---|
| `v0.1.0` | ORION | `0e200d9` | 2026-10-20 | Fundación del proyecto y especificaciones Spec Kit | retrospectiva | preparada | — |
| `v0.2.0` | ANDROMEDA | `b6b953a` | 2026-11-05 | Base funcional del frontend: F0–F2.5 y V-01 | retrospectiva | preparada | — |
| `v0.3.0` | ANDROMEDA | `f279090` | 2026-11-06 | Gestión de expedientes y requisitos | retrospectiva | preparada | — |
| `v0.4.0` | ECLIPSE | `d020592` | 2026-11-10 | Implementación de seguridad del backend SGT-SIAAF | retrospectiva | preparada | — |
| `v0.5.0` | HELIOS | `025de78` | 2026-11-12 | Integridad de archivos privados, errores de dominio y endurecimiento de seguridad | retrospectiva | preparada | — |
<!-- cosmos:versiones:fin -->

**Entregas sin versión:**

<!-- cosmos:sin-version:inicio -->
| Commit | Fecha | Hito | Descripción |
|---|---|---|---|
| `edee296` | 2026-11-02 | — | Backend Fase 1–2, T001–T046 (PR #11). Sin hito ni versión registrados. |
| `fe75d39` | 2026-11-11 | ROSETTA | Documentación maestra DP2 (PR #21). Solo documentación: no genera versión (DK-005). |
<!-- cosmos:sin-version:fin -->

## 4. Detalle de cada versión (generado)

<!-- cosmos:detalle:inicio -->
### ORION v0.1.0 — Fundación del proyecto y especificaciones Spec Kit

Inicio del ciclo de desarrollo: estructura del repositorio, constitución del proyecto y especificación SDD del trámite de titulación (spec 001).

Commit `0e200d9cb490224eaea0870cf457581d4ed93db8` · entrega 2026-10-20 · estado **preparada** · **retrospectiva**

Excepción de versión: DK-012: versión asignada por decisión expresa del responsable a una entrega exclusivamente documental, que por DK-005 no generaría versión. Excepción histórica no repetible.

**Cambios:**

- Constitución del proyecto (sgt-siaaf/.specify/memory/constitution.md).
- Spec 001 del trámite de titulación: specify, clarify, plan y tasks.
- Plantillas Spec Kit y ADR-001/ADR-002 (archivos vacíos en el commit).
- Retirada de docs/01-problema-contexto.md.

**Validaciones:**

- Entrega documental: no incluye código ni pruebas automatizadas.
- Contenido verificado el 2026-11-12 con git diff --stat 0e200d9^1 0e200d9: 11 archivos, 3415 inserciones y 31 eliminaciones.

**Pendientes y limitaciones conocidos:**

- Las plantillas Spec Kit y los ADR se incorporaron vacíos.

**Referencias:**

- Commit 0e200d9 chore(orion): merge de abe9a40 en main.

### ANDROMEDA v0.2.0 — Base funcional del frontend: F0–F2.5 y V-01

Primera entrega versionada: base funcional del frontend (andamiaje, autenticación, UI Kit, estados de error y pantalla de login). El merge también incorporó documentación y prototipos de diseño.

Commit `b6b953aa313e858218eb71ac6163e4873395e066` · entrega 2026-11-05 · estado **preparada** · **retrospectiva**

**Cambios:**

- F0: andamiaje, configuración y estructura del frontend.
- F1: autenticación, gestión de sesión y cliente HTTP.
- F2: UI Kit y componentes reutilizables.
- F2.5: estados de error y recuperación.
- V-01: pantalla de login.

**Validaciones:**

- Reportado en 467ec3b: 226/226 pruebas, ESLint, TypeScript y build sin errores.
- Re-ejecutado el 2026-11-12 sobre el árbol del commit: 146 pruebas aprobadas, pero 9 de 40 archivos de prueba no cargan y typecheck falla, porque falta frontend/src/lib/.
- Diagnóstico: añadiendo la frontend/src/lib/ actual (no versionada) pasan 239/239 y typecheck; no reproduce exactamente el estado de la entrega.

**Pendientes y limitaciones conocidos:**

- FE-T1213 (InlineAlert 409/412/428) bloqueada por BE-11.
- frontend/src/lib/ (15 archivos importados por 24 módulos) nunca se ha versionado: la regla 'lib/' del .gitignore raíz (plantilla de Python) lo ignora. El frontend de esta etiqueta no compila ni pasa sus pruebas a partir de Git.

**Referencias:**

- Rama release/0.2.0-andromeda; commit 467ec3b `feat(frontend): integrar F0–F2.5 y V-01`.
- Merge en main b6b953a.

### ANDROMEDA v0.3.0 — Gestión de expedientes y requisitos

Vista V-04 (FE-T401–FE-T411): detalle de expedientes, checklist de requisitos, envío, observaciones, evaluación, subsanación y descargas, sobre los contratos reales del backend.

Commit `f2790908f256a932528b0036b3a07258776b4cfc` · entrega 2026-11-06 · estado **preparada** · **retrospectiva**

Excepción de hito: ANDROMEDA abarcó v0.2.0 y v0.3.0 antes de DK-011; reutilización histórica aceptada y no repetible.

**Cambios:**

- Consulta del detalle de expedientes.
- Checklist de requisitos: envío, observaciones, evaluación y subsanación.
- Descarga autenticada de documentos y versiones.
- Matriz de acciones por rol y estado.

**Validaciones:**

- Reportado en f279090: 328/328 pruebas, cobertura de features/expediente superior al 80 %, ESLint, TypeScript y build satisfactorios.
- Re-ejecutado el 2026-11-12 sobre el árbol del commit: 22 de 51 archivos de prueba no cargan y typecheck falla, porque falta frontend/src/lib/.
- Diagnóstico: añadiendo la frontend/src/lib/ actual (no versionada) pasan 328/328 y typecheck, la cifra reportada.

**Pendientes y limitaciones conocidos:**

- INC-21 (P1): algunos errores de reglas de negocio responden HTTP 500.
- FE-T407 (P1): el estudiante no puede descubrir el checklist_verification_id para subsanar.
- Incidencia heredada P2 en queryClient.ts (status 0).
- V-05 fuera de la entrega.
- frontend/src/lib/ (15 archivos importados por 24 módulos) nunca se ha versionado: la regla 'lib/' del .gitignore raíz (plantilla de Python) lo ignora. El frontend de esta etiqueta no compila ni pasa sus pruebas a partir de Git.

**Referencias:**

- Rama release/0.3.0-andromeda; PR #14.
- afdd989 es un merge previo sin cambios; la entrega es f279090.

### ECLIPSE v0.4.0 — Implementación de seguridad del backend SGT-SIAAF

Controles de seguridad del backend: configuración de producción, throttling, JWT, validación y almacenamiento privado de PDF, RBAC con aislamiento de expedientes, máquina de estados, logging estructurado y restricción de la documentación de la API en producción.

Commit `d02059255d87b1dfd6839da1bbf604c47c7923c2` · entrega 2026-11-10 · estado **preparada** · **retrospectiva**

**Cambios:**

- HTTPS, HSTS, CSP, CORS, cookies y cabeceras de seguridad.
- Throttling de autenticación y de carga de documentos.
- JWT stateless con claves SECRET_KEY y JWT_SIGNING_KEY separadas.
- Validación de PDF (magic bytes, SHA-256, 10 MB) y almacenamiento privado.
- RBAC y aislamiento de expedientes con ScopeFilterMixin.
- Máquina de estados, plazos y protección de campos críticos.
- Logging JSON con filtros de datos sensibles y request_id.

**Validaciones:**

- Reportado en 8e1e1a2: 497 pruebas aprobadas según la matriz de trazabilidad.
- Re-ejecutado el 2026-11-12 (backend, SQLite) sobre el árbol de d020592: 484 aprobadas y 13 fallidas, 497 en total. Las 13 fallan en test_pdf_generator.py porque falta pypdf; con un lector pdftotext pasan 30/30.

**Pendientes y limitaciones conocidos:**

- SEC-T014 bloqueada por DEC-009.
- SEC-T015: verificación real de FirmaEC.
- SEC-T016: migración a RS256.
- VULN-001 a VULN-014 con coberturas diferenciadas.
- SEC-T017 a SEC-T024 pendientes.
- pypdf no declarado en las dependencias de desarrollo.
- frontend/src/lib/ (15 archivos importados por 24 módulos) nunca se ha versionado: la regla 'lib/' del .gitignore raíz (plantilla de Python) lo ignora. El frontend de esta etiqueta no compila ni pasa sus pruebas a partir de Git.

**Referencias:**

- Rama release/0.4.0-eclipse; commit 8e1e1a2; PR #16 (a develop) y PR #17 (a main).
- 4ac69d1 ('Merge branch release/0.4.0-eclipse into main') no incorporó cambios; la entrega llega a main en d020592.

### HELIOS v0.5.0 — Integridad de archivos privados, errores de dominio y endurecimiento de seguridad

Endurecimiento de seguridad P0 e inicio de la verificación, errores de dominio uniformes con bloqueo ordenado y corrección de archivos privados huérfanos con conciliación segura.

Commit `025de7887dca9acacf296e629703381ba6734ce1` · entrega 2026-11-12 · estado **preparada** · **retrospectiva**

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

**Pendientes y limitaciones conocidos:**

- D-07: reconciliar_archivos no informa de registros sin archivo (H-I3-07).
- D-09: test_postgres_infra.py depende del orden de ejecución.
- El bloqueo de reconciliar_archivos solo es efectivo en PostgreSQL.
- DK-010: sin evidencia de la notificación a los integrantes de su atribución delegada.
- pypdf no declarado en dependencias de desarrollo (E0-01).
- H-30: 8 pruebas de índices fallan en PostgreSQL.
- Decisión funcional O-1 (hoy 409) e I-4 (contracts/openapi.yaml difiere de openapi.yaml).
- AUT-01, AUT-03 y VULN-005/006/010 registradas como abiertas en d1fa86e.
- frontend/src/lib/ (15 archivos importados por 24 módulos) nunca se ha versionado: la regla 'lib/' del .gitignore raíz (plantilla de Python) lo ignora. El frontend de esta etiqueta no compila ni pasa sus pruebas a partir de Git.

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
| 3 | Elegir el hito disponible por propósito dominante | `proponer` (lista los disponibles y su temática) |
| 4 | Comprobar que la versión y el hito no estén asignados (registro y etiquetas local y remota) | `proponer`, `verificar` |
| 5 | Comprobar que el commit pertenece a la historia principal de `main` | `proponer`, `verificar` |
| 6 | Ejecutar las pruebas y anotar los resultados reales | suite del proyecto |
| 7 | **Pedir autorización explícita** al responsable (versión, hito, commit, notas) | — |
| 8 | Registrar la versión (`preparada`) y confirmarla en un commit **antes de publicar** | `cosmos.py registrar` |
| 9 | Simular la publicación | `cosmos.py publicar vX.Y.Z` |
| 10 | Crear la etiqueta anotada, publicarla con push normal y crear la GitHub Release | `publicar vX.Y.Z --ejecutar --confirmar vX.Y.Z` |
| 11 | Comprobar la etiqueta y la GitHub Release, marcar la versión como `publicada` y hacer commit del registro | `cosmos.py marcar-publicada vX.Y.Z`, `verificar --releases` |

El registro puede integrarse en `main` después del commit etiquetado: la etiqueta apunta a la entrega, no al commit que la documenta.

## 6. Herramienta `scripts/cosmos/cosmos.py`

Solo biblioteca estándar de Python 3 (sin dependencias). Códigos de salida: 0 correcto, 1 incoherencia o bloqueo, 2 error de uso o rechazo.

```bash
python3 scripts/cosmos/cosmos.py verificar               # solo lectura (consulta el remoto)
python3 scripts/cosmos/cosmos.py --sin-remoto verificar  # solo lectura, sin red
python3 scripts/cosmos/cosmos.py proponer                # versión, incremento e hitos disponibles
python3 scripts/cosmos/cosmos.py verificar --releases    # además, comprueba las GitHub Releases (gh)
python3 scripts/cosmos/cosmos.py notas v0.5.0            # notas de la release (o --formato etiqueta)
python3 scripts/cosmos/cosmos.py documentar              # regenera las secciones generadas
python3 scripts/cosmos/cosmos.py registrar --version v0.6.0 --hito <HITO> --commit <sha> \
    --titulo "…" --descripcion "…" --cambio "…" --validacion "…" --pendiente "…"
python3 scripts/cosmos/cosmos.py publicar v0.5.0         # SIMULACIÓN: no crea ni publica nada
python3 scripts/cosmos/cosmos.py publicar v0.5.0 --ejecutar --confirmar v0.5.0   # solo con autorización
python3 scripts/cosmos/cosmos.py marcar-publicada v0.5.0
```

**`verificar` comprueba:**
- **Catálogo:** cada hito con nombre, descripción y temática.
- **Formato y hitos:** formato SemVer; hito del catálogo y sin reutilizar.
- **Coherencia entre versiones:** versiones únicas e incrementos SemVer válidos; ninguna versión ≥ 1.0.0 sin declaración de estabilidad.
- **Commits:** SHA completo existente en la historia principal de `main`, cada uno descendiente del anterior, y fecha igual a la del commit.
- **Etiquetas:** anotadas, sobre el commit registrado y con la primera línea correcta; la local y la remota son el mismo objeto; ninguna etiqueta `vX.Y.Z` fuera del registro; las versiones `publicada` tienen etiqueta local y remota, y sus datos de publicación.
- **Releases (`--releases`, con `gh`):** cada versión publicada tiene su release, con la etiqueta, el título y la URL registrados, sin borrador; la Latest es la versión más alta.
- **Documento:** las secciones generadas coinciden con el registro.

**`publicar`:**
- Repite todas las comprobaciones y además exige que la etiqueta no exista en local ni en el remoto, y que el commit esté en la historia principal de `origin/main`.
- Exige que la asignación esté confirmada en un commit del registro y que no exista ya una GitHub Release para esa versión.
- Marca como **Latest** solo la versión más alta del registro (`--latest=true`); las demás se crean con `--latest=false`.
- Sin `--ejecutar --confirmar <versión idéntica>` solo simula.
- Para crear la release usa `gh` si está instalado; si no, la API de GitHub con `GITHUB_TOKEN`; y si tampoco hay token, muestra el título y las notas para crearla a mano.

**Pruebas:** `python3 -m unittest discover -s scripts/cosmos -p 'test_*.py'`.

## Relacionado

[[GIT_POLICY]] · [[DECISIONS_LOG]]
