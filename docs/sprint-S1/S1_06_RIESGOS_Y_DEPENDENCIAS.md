# S1-06 — RIESGOS Y DEPENDENCIAS DEL SPRINT S1

**Fecha:** 02-nov-2026 · Referencias: plan.md §25 (RSK-ARC-01..03), auditoria/04 (A-08), S1_01 (C1-C4).

## 1. Dependencias técnicas y de gobernanza

| ID | Relación | Tipo |
| :--- | :--- | :--- |
| D-1 | S1-T02 y S1-T03 ← S1-T01 (línea base aprobada) | Bloqueante de arranque |
| D-2 | S1-T02 ← Independiente de S1-T03 | Paralelo permitido |
| D-3 | S1-T05a (config de pruebas) ← independiente; S1-T05b (regresión final) ← S1-T02, S1-T03 | Secuencia |
| D-4 | S1-T04 ← Decisión gobernanza C1 (exclusión tasks.md §4.2) + middleware/INSTALLED_APPS | **Decisión humana es bloqueante** |
| D-5 | S1-T02 ← aprobación de migración opcional (hash en Informe/Declaratoria) | Decisión técnica menor |
| D-6 | S1-T03 ← clarificación alcance `RESPONSABLE_DEPENDENCIA` para GET checklist | Decisión menor (default deny documentado) |
| D-7 | S1-T06 ← S1-T02, S1-T03, S1-T05b | Final |

**Cadena crítica:** C1 (decisión Admin) → S1-T01 → [S1-T02 ∥ S1-T03 ∥ S1-T05a] → S1-T05b → S1-T04 → S1-T06.

## 2. Matriz de riesgos

| ID | Descripción | Prob. | Impacto | Mitigación | Responsable |
| :--- | :--- | :--- | :--- | :--- | :--- |
| RSK-S1-01 | Decisiones pendientes (C1-C4, migración de hash, `RESPONSABLE_DEPENDENCIA` en GET) bloqueen el sprint a mitad de camino | Alta | Medio | Bloquear la gobernanza en S1-T01 con respuestas documentadas antes de escribir código | Arquitectura |
| RSK-S1-02 | Cambiar `MIDDLEWARE`/`INSTALLED_APPS` para Admin rompe JWT-pure stateless (sesiones ya se usan parcialmente; mensajes no) o filtros existentes | Media | Alto | Cambio aislado en PR separado; suite completa; no exponer admin fuera de entornos de soporte | Backend |
| RSK-S1-03 | Corrección de almacenamiento con *doble persistencia* (informe final en storage + borradores) o legacy paths en BD | Media | Alto | Estrategia única de escritura: `guardar_archivo_privado()` o `PrivateMediaStorage` directo; script de verificación de paths de BD en test | Backend |
| RSK-S1-04 | Over-permission en RBAC: conceder GET checklist más amplio que el isolation de expedientes (IDOR) | Baja | Alto | Scopes espejo de `expedientes:GET`; tests IDOR; negación para roles no justificados | Seguridad |
| RSK-S1-05 | La corrección de `emitir_informe` (HistorialEstado estado_anterior incorrecto — hallazgo nuevo) queda fuera del alcance de S1-T02 | Media | Medio | Elevar a decisión: incluir en S1-T02 (fachada mínima, 3 líneas) o tarea separada | Arquitectura |
| RSK-S1-06 | `Service de declaratoria` permite `ANALISTA_APOYO` (contradicción C3 con matriz 6.2): si se "corrige" por conveniencia se rompen los tests actuales | Alta | Medio | Decisión explícita (C3): alinear código a specify (denegar analista) O actualizar spec con justificación; **no decidir en código** | Arquitectura/Equipo |
| RSK-S1-07 | Entornos: variable `DJANGO_SETTINGS_MODULE=local` en contenedor sigue forzando PostgreSQL en CI/CD de otros devs | Alta | Medio | Eliminar variable del `Dockerfile`/`docker-compose.yml` (o fijarla en `python -m pytest` invocation del script de CI) — cambio de config planificado | DevOps |
| RSK-S1-08 | Exposición de Django Admin vía Nginx en producción (auditoría A-08 previnotica) | Baja | Alto | No activar en compose de producción; ruta admin restringida; documentación de despliegue | DevOps |
| RSK-S1-09 | Data histórica: rutas absolutas guardadas en BD previo al fix (registros de `archivo_informe_path` con `/media/...`) quedarán inconsistentas | Media | Medio | Data migration o script one-off de normalización **con aprobación**; en entorno de simulación académica, riesgo bajo | Backend |
| RSK-S1-10 | `RESPONSABLE_DEPENDENCIA` ausente en matrices actuales (`permissions.py` no lo lista en ninguna celda como permitir hasta DENY implícito) — endpoint GET checklist estará deny, correcto, pero documentarlo | Alta | Bajo | Test paramétrico incluye el rol con DENY y comentario de referencia a C6/decisión | Seguridad |
| RSK-S1-11 | pypdf nos fuerza a mantener PDFs "borrador" — si el equipo quiere el PDF byte-verificado, prestarcompleto (dependency chain de parsing) estándar pypdf está bien mantenido | Baja | Bajo | Pin versionado; reevaluación en fase 2 | Tech lead |

## 3. Hallazgos nuevos adicional a la auditoría NotebookLM (para trazabilidad completa)

| ID | Hallazgo | Evidencia |
| :--- | :--- | :--- |
| N-1 | `HistorialEstado.estado_anterior` en `emitir_informe` guarda el estado ya mutado (estado_anterior == estado_nuevo == INFORME_EMITIDO) | `emitir_informe.py:199-211`; test `test_emitir_informe.py:357` lo asserta (falló por PermissionError, la aserción real se revelará tras S1-T02) |
| N-2 | `metadata` de `validar_pdf_completo()` descartada en declaratoria (hash disponible, no persistido) | `declarar_aptitud.py:167-171` |
| N-3 | `roles_permitidos` definida y no usada en `declarar_aptitud.py:123` (duplicación con la condición en línea 124) | idem |
| N-4 | El suite corre sobre Postgres contra la intención test.py por issue de env var (causa C2) | contenedor `env` |
| N-5 | Nginx ya presente en el repo (`nginx/`) — config a revisar si Admin se activa (A-08) | `nginx/nginx.conf` |
| N-6 | El modelo conceptual del plan No incluye hash en Informe/Declaratoria: la brecha de SEC-01 es también una *brecha de spec* que merecía decisión temprana | plan.md §12 ER |

## 4. Archivos NO tocados en esta fase (recordatorio)

Ningún archivo del backend fue modificado. Todo lo anterior es inspección: los cambios descritos pertenecen a tareas futuras sin estado de ejecución.
