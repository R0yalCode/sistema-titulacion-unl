---
system: SGT-SIAAF
type: workflow
status: active
source: knowledge-build-session
last_updated: 2026-11-11
---

# Mantenimiento del conocimiento

## Al cerrar cada tarea

Actualiza **solo** las notas afectadas y registra:

1. Qué se investigó (archivos y secciones leídos).
2. Qué se modificó (rutas).
3. Qué pruebas se ejecutaron (comandos exactos).
4. Resultados comprobados (cifras reales, también los fallos).
5. Decisiones técnicas → [[DECISIONS_LOG]] (DK-xxx) o ADR del proyecto.
6. Documentación afectada.
7. Pendientes → [[BLOCKED_TASKS]] / [[CURRENT_STATE]].
8. Fuentes originales relacionadas.
9. Commits (hash), si los hubo.
10. Rama y versión, si corresponde ([[COSMOS_VERSIONING]]).

## Qué nota tocar según el cambio

| Cambio | Notas |
|---|---|
| Endpoint nuevo o modificado | [[API_CONTRACTS]], nota del módulo, [[PERMISSIONS_ROLES]] si cambia el RBAC |
| Modelo o migración | [[DATABASE]], [[BACKEND_ARCHITECTURE]] (máquina de estados) |
| Vista o tarea frontend | [[ROUTES]], [[03-FRONTEND/MODULES|Módulos frontend]], [[TASKS]] |
| Prueba ejecutada | [[REGRESSION_TESTS]], [[EVIDENCE_INDEX]] |
| Hallazgo de seguridad | [[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] |
| Cambio de fase o bloqueo | [[CURRENT_STATE]], [[BLOCKED_TASKS]] |
| Norma validada | [[ARTICLES_AND_PROVISIONS]], [[REGULATORY_TRACEABILITY]] |

Actualiza `last_verified` / `last_updated` en el frontmatter de cada nota tocada.

## Bitácoras de sesión

Crea `09-SESSION-LOGS/AAAA/AAAA-MM-DD-tema.md` (plantilla: [[SESSION_TEMPLATE]]) **solo** si la tarea tuvo relevancia arquitectónica, funcional, de seguridad o documental. No registres sesiones triviales.

## Integridad de fuentes copiadas

Desde el 2026-11-12 (DK-014), `Documentacion-parte-2/` ya no existe en la raíz: la copia de `90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/` es la canónica. Para comprobar que no ha derivado del original histórico:

```bash
for f in SIAAF-KNOWLEDGE/90-ORIGINAL-SOURCES/DOCUMENTATION-PART-2/*.md; do
  b=$(basename "$f"); [ "$b" = README.md ] && continue
  git show "5ef0dbd:Documentacion-parte-2/$b" | cmp -s - "$f" || echo "difiere: $b"
done
```

Si un documento cambia: registra la corrección y su motivo en [[SOURCE_CATALOG]] y revisa su nota `DP2-*`.

## Enlaces

Después de crear o renombrar notas, comprueba que no haya wikilinks rotos (script de verificación descrito en [[BUILD_REPORT]] §21). Para nombres repetidos (`MODULES`, `SECURITY_AUDIT`) usa el enlace con ruta: `[[02-BACKEND/MODULES|…]]`.

## Nunca

Copiar `.env`, secretos, tokens, claves, PDF de `media/private/` ni datos personales; reescribir notas completas sin necesidad; marcar como implementado algo que solo está planificado.
