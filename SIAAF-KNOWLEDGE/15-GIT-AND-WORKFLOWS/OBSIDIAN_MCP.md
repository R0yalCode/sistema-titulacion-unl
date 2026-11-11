---
system: SGT-SIAAF
type: workflow
area: mcp
status: verified
source: claude-mcp-config + live-test
last_verified: 2026-11-11
---

# Integración Obsidian MCP

## Arquitectura

```
Claude Code ──HTTP──► http://localhost:8765/mcp ──► plugin "vault-as-mcp" (dentro de Obsidian) ──► bóveda abierta
                                                       (127.0.0.1, sin TLS)                    = <repo>/SIAAF-KNOWLEDGE
```

El servidor **vive dentro de Obsidian**: solo responde con Obsidian abierto y el plugin activo. Sirve la bóveda **abierta en ese momento**; si se abre otra bóveda, el MCP apunta a ella.

## Configuración comprobada (2026-11-11)

| Elemento | Valor |
|---|---|
| Nombre del servidor | `obsidian` |
| Alcance | Usuario (`claude mcp get obsidian` → "User config"); no hay `.mcp.json` en el repo |
| Transporte | HTTP |
| URL | `http://localhost:8765/mcp` |
| Estado | ✔ Connected (`claude mcp list`) |
| Plugin | `vault-as-mcp` 1.2.1 (`.obsidian/plugins/vault-as-mcp/`) |
| Ajustes del plugin | `serverHost 127.0.0.1`, `serverPort 8765`, `autoStart true`, `tlsEnabled false`, `pathACL` vacío (sin restricciones de ruta) |
| Autenticación | No hay clave ni token en los ajustes del plugin ni en la configuración del servidor |
| Obsidian | Flatpak (`~/.var/app/md.obsidian.Obsidian/`); bóveda abierta = `<repo>/SIAAF-KNOWLEDGE` |

No se modificó la configuración del servidor ni la del plugin.

## Herramientas disponibles

| Tipo | Herramientas |
|---|---|
| Búsqueda | `search_notes` (carpeta, encabezados, etiquetas, frontmatter, texto, mtime), `list_notes` |
| Lectura | `read_note` (sección por encabezado, ventana de líneas, `metadataOnly`), `read_multiple_notes`, `read_periodic_note`, `list_templates` |
| Escritura | `create_note`, `update_note`, `patch_note`, `append_to_note`, `rename_note`, `delete_note` |

## Funciones verificadas en esta sesión

| Operación | Prueba | Resultado |
|---|---|---|
| `list_notes("")` | Antes de la construcción | `{"notes":[],"folders":[]}`: bóveda vacía |
| `search_notes` | `folder=12-DEGREE-PROCESSES`, `frontmatterValues={status: proposal}` | 2 notas (COMPREHENSIVE_EXAMINATION, CURRICULAR_INTEGRATION_WORK) ✅ |
| `read_note` con `heading` | Sección "Petición documental" de BACKEND_ARCHITECTURE | Solo esa sección, más el frontmatter y los enlaces resueltos ✅ |
| `patch_note` | Sustitución de este párrafo por esta tabla | Aplicado; comprobado en el `.md` con `grep` ✅ |

Detalle en [[BUILD_REPORT]] §19.

## Uso recomendado (ahorro de contexto)

1. `search_notes` con `folder` y `text`, o `frontmatterValues`, para **localizar** la nota.
2. `read_note` con `metadataOnly: true` para ver el **tamaño y el esquema**.
3. `read_note` con `heading` para leer **solo la sección** necesaria.
4. `patch_note` o `append_to_note` para cambios quirúrgicos; evita `update_note` (reescribe todo).

El MCP no reduce tokens por sí solo: el ahorro viene de recuperar **solo** lo necesario.

## Diagnóstico de fallos

| Síntoma | Causa probable | Acción |
|---|---|---|
| `claude mcp list` → "Failed to connect" | Obsidian cerrado o plugin deshabilitado | Abrir Obsidian con esta bóveda; activar `vault-as-mcp` |
| Conecta, pero `list_notes("")` muestra otras notas | Hay otra bóveda abierta | Abrir `SIAAF-KNOWLEDGE` en Obsidian |
| Error de puerto | 8765 ocupado | Ajustar el puerto en el plugin **y** en `claude mcp` (decisión humana) |
| Herramienta inexistente | Versión del plugin | Ver la lista anterior |
| Error 401/403 | Hoy no aplica (no hay autenticación configurada) | — |

## Alternativa sin MCP

Lectura y escritura directa de los `.md` en `SIAAF-KNOWLEDGE/` con las herramientas de archivos (Read/Grep/Edit) o `grep -rn`. Mismo orden de consulta ([[CLAUDE_CODE_OPENCODE_GUIDE]]). Nunca bloquear una tarea por falta de MCP.

## Riesgo

El plugin escucha en `127.0.0.1` sin autenticación ni `pathACL`: cualquier proceso local puede leer o escribir la bóveda mientras Obsidian esté abierto. Aceptable en una estación personal; **no** exponer el puerto.
