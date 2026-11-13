# Comprobaciones de `tasks.md` de la spec 001

Scripts de verificación puntual de
`sgt-siaaf/specs/001-tramite-titulacion/tasks.md` (tareas T001-T046 del
backend). Se trasladaron desde la raíz del repositorio el 2026-11-12 (DK-014)
sin cambiar su nombre ni su contenido.

Abren `tasks.md` con una ruta relativa al **directorio de trabajo**, así que
deben ejecutarse desde la raíz del repositorio. Solo usan la biblioteca
estándar y solo leen archivos.

```bash
python3 scripts/spec001/audit_tasks.py
```

| Script | Comprueba |
|---|---|
| `audit_tasks.py` | IDs T001-T046 sin duplicados ni huecos y dependencias válidas |
| `audit_complete.py` | Secuencia de tareas, paquetes, requisitos RF/RNF, decisiones DEC, artículos RRA-UNL, principios y checklist |
| `check_t047.py` | Que no exista ni se mencione una tarea T047 |
| `verify_matrix.py` | Requisitos y tareas citados en la matriz de trazabilidad y checklist marcado |

Ningún workflow, script ni prueba los invoca: son herramientas manuales.

**Pendiente de decisión:** `check_files.py` y `verify_all_tasks.py` siguen en
la raíz. Tienen fija una ruta de Windows (`C:\Users\DELL\...`) y no funcionan
fuera de ese equipo. No se trasladaron, corrigieron ni eliminaron.
