---
system: SGT-SIAAF
type: session-log
date: 2026-11-12
agent: claude-code
branch: docs/cosmos-versionado
---

# Sesión 2026-11-12 — Versionado COSMOS formal (DK-011)

## Auditoría (fase A)

- No existía ninguna etiqueta, ni local ni remota, ni ninguna release en GitHub.
- v0.3.0 **sí** se entregó (ANDROMEDA, `f279090`, PR #14); parecía ausente porque ANDROMEDA abarcó dos versiones y porque no había etiquetas.
- `afdd989` y `4ac69d1` son merges en `main` sin cambios; las entregas reales son `f279090` (v0.3.0) y `d020592` (v0.4.0, PR #17), no `8e1e1a2`.
- Asignaciones aprobadas por el responsable y verificadas, todas en la historia principal (*first-parent*) de `main`, en orden y con su fecha:

| Versión | Hito | Commit | Fecha |
|---|---|---|---|
| v0.2.0 | ANDROMEDA | `b6b953a` | 2026-11-05 |
| v0.3.0 | ANDROMEDA | `f279090` | 2026-11-06 |
| v0.4.0 | ECLIPSE | `d020592` | 2026-11-10 |
| v0.5.0 | HELIOS | `025de78` | 2026-11-12 |

- ORION (`0e200d9`), el backend `edee296` y ROSETTA (`fe75d39`) quedan sin versión.

## Implementación (fase B)

- `COSMOS_REGISTRO.json`: fuente única de verdad.
- `scripts/cosmos/cosmos.py`: biblioteca estándar, sin dependencias. Órdenes `verificar`, `proponer`, `notas`, `documentar`, `registrar`, `publicar` (simulación por defecto) y `marcar-publicada`.
- `scripts/cosmos/test_cosmos.py`: 37 pruebas sobre repositorios temporales.
- Regla 6 de `CLAUDE.md`, `AGENTS.md`, [[GIT_POLICY]], [[COSMOS_VERSIONING]] (tablas generadas) y [[DECISIONS_LOG]] (DK-011).

## Verificación (fase C)

- `unittest`: 37/37.
- Mutaciones de cuatro salvaguardas (confirmación, *first-parent*, documento y simulación): detectadas.
- `verificar` sobre el repositorio real: 0 errores.
- Simulación de `publicar` para las cuatro versiones: correcta, sin crear nada.
- Ensayo completo en un clon aislado con remoto local: cuatro etiquetas anotadas sobre los commits exactos; repetición bloqueada; `marcar-publicada` y `verificar` en verde.
- Repositorio real: 0 etiquetas.

## Pendientes

- Autorización de la integración en `develop` y `main` (fase D).
- Autorización independiente de las etiquetas y releases (fase E). `gh` no está instalado: la release se crea con `GITHUB_TOKEN` o a mano.
- Con la secuencia estricta solo quedan TRAPPIST y SUPERNOVA: el equipo debe decidir cómo ampliar el catálogo.

## Fase E — Preparación (DK-012)

- **Auditoría:**
  - Los cinco commits (`0e200d9`, `b6b953a`, `f279090`, `d020592`, `025de78`) están en la historia principal de `main`, con sus fechas.
  - No había etiquetas ni releases.
  - ORION (`0e200d9`) es solo documentación; se registra como excepción expresa a DK-005.
- **Hallazgo:**
  - `frontend/src/lib/` (15 archivos importados por 24 módulos) **nunca se ha versionado**, porque la regla `lib/` del `.gitignore` raíz (plantilla de Python) lo ignora.
  - Re-ejecución sobre el árbol de `b6b953a` y `f279090`: hay archivos de prueba que no cargan y `typecheck` falla.
  - Añadiendo la `lib/` actual, `f279090` pasa 328/328, la cifra reportada.
  - Backend en `d020592`: 484 aprobadas y 13 fallidas por `pypdf`, 497 en total, la cifra reportada.
- **Cambios preparados:**
  - Catálogo ampliado a 36 hitos con descripción y temática.
  - Asignación por propósito dominante.
  - `publicar` exige que la asignación esté confirmada en un commit y marca Latest solo la versión más alta.
  - `marcar-publicada` comprueba la etiqueta y la GitHub Release.
  - `verificar --releases`.
  - 40 pruebas.
