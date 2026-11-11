---
system: SGT-SIAAF
type: source-note
source_file: Documentacion-parte-2/MATRIZ_REGLAS_NEGOCIO_MODALIDADES.md
source_copy: 90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/MATRIZ_REGLAS_NEGOCIO_MODALIDADES.md
source_version: "1.0"
source_date: 2026-11-09
nature: business-rules (proposal)
vigencia: propuesta; pendiente-validacion-normativa
last_verified: 2026-11-11
---

# DP2 · Matriz de reglas de negocio de modalidades

**Original:** [[MATRIZ_REGLAS_NEGOCIO_MODALIDADES]]

## Catálogo de reglas (identificadores conservados)

| Grupo | IDs | Esencia |
|---|---|---|
| Asignación inicial | RN-MOD-CRE-01…03 | TIC por defecto; EC no se puede crear desde `POST /expedientes/`; el payload de creación no lleva el campo |
| Elegibilidad EC | RN-MOD-ELE-01…04 | ≥ 2 reprobaciones de la unidad de titulación; 3.ª matrícula efectiva; evidencia documental; verificación obligatoria |
| Cambio | RN-MOD-CAM-01…07 | Solo TIC→EC (irreversible); autorización dual (Secretario verifica + Decano autoriza); justificación ≥ 50 caracteres; evidencia JSON; solo en BORRADOR/ENVIADA/EN_VERIFICACION; historial inmutable; **un solo cambio** por expediente |
| Protección | RN-MOD-PRO-01…05 | Sin PATCH directo; endpoint dedicado; validación en servidor; auditoría `MODALIDAD_CAMBIADA`; consistencia con checklist/peticiones |
| Proceso académico | RN-MOD-PRO-ACA-01…04 | TIC: trabajo escrito + defensa; EC: examen integral; acta diferenciada (Fase 2/3) |

Transiciones (§2): el cambio a EC se permite en BORRADOR, ENVIADA y EN_VERIFICACION; se prohíbe en OBSERVADA, INFORME_EMITIDO, DECLARADA_APTA y CANCELADA, y siempre de EC→TIC.
Errores (§7): `MODALIDAD_NO_SELECCIONABLE`, `MODALIDAD_CAMBIO_IRREVERSIBLE`, `ELEGIBILIDAD_NO_CUMPLIDA`, `ESTADO_EXPEDIENTE_INVALIDO`, `CAMBIO_YA_REALIZADO`, `EVIDENCIA_INCOMPLETA`, `JUSTIFICACION_INSUFICIENTE`, `SIN_PERMISO_AUTORIZACION`.

## Contradicciones internas

1. **RN-MOD-CAM-02** exige que el Decano autorice el POST de cambio, pero la matriz de permisos (§3) concede `POST /modalidad/cambiar/` también a SECRETARIO_ABOGADO y ADMINISTRADOR.
2. La nota bajo §3 dice que "ANALISTA_APOYO puede ver elegibilidad", pero la tabla le asigna ❌ en `GET /elegibilidad/`.
3. La "irreversibilidad" y el "un solo cambio" se atribuyen a "normativa", sin artículo citado.

## Estado

Ninguna regla está implementada. La §8.6 dice: "Ninguna regla se implementa sin validación firmada de Arts. 39, 40, 212, 216, 233".

## Relacionado

[[DP2-DISENO_FUNCIONAL_MODALIDADES]] · [[COMPREHENSIVE_EXAMINATION]] · [[REGULATORY_TRACEABILITY]]
