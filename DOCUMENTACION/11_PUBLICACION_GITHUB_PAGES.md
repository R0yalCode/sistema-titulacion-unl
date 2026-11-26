---
title: "Publicación en GitHub Pages"
---

# Publicación en GitHub Pages — SGT-SIAAF

**Estado al cierre de esta fase (2026-11-07):** el sitio se renderizó y verificó localmente (109 archivos, 0 errores, 0 warnings — ver `CONTROL_MAESTRO_DOCUMENTACION.md`, Fase 11). **No se ha publicado nada en GitHub Pages real**: esta sesión no tiene credenciales ni acceso de red hacia un repositorio remoto de GitHub, y esta copia de trabajo no es un repositorio Git (confirmado: no existe `.git`). Todo lo de esta página son instrucciones exactas y artefactos ya preparados para que el usuario complete la publicación.

## 1. Qué se entrega, listo para usar

| Artefacto | Ubicación | Qué es |
|---|---|---|
| Carpeta estática lista para publicar | **`/gh-pages`** (raíz del repositorio) | Copia completa del sitio ya renderizado (109 páginas, 9.5 MB), con `.nojekyll` incluido. Autocontenida: se verificó sirviéndola de forma aislada en un puerto local distinto al de `docs/_site`, sin ninguna dependencia de otras carpetas. |
| Workflow de publicación automática | `.github/workflows/publish-quarto.yml` | Renderiza `docs/` con Quarto y despliega a GitHub Pages en cada push a `main` que toque `docs/**` (o manualmente vía "Run workflow") |
| Fuente editable del sitio | `docs/` (111 archivos: 109 de contenido + `_quarto.yml` + `index.qmd`) | El proyecto Quarto real; es lo que se edita para cambiar el sitio |

**Importante sobre `/gh-pages`:** es una **fotografía** del sitio al momento de esta fase (2026-11-07). Si se modifica `docs/` después, hay que volver a renderizar y volver a copiar (instrucciones en §4) — o, mejor, usar el workflow automático de §2, que siempre publica la versión más reciente sin depender de esta carpeta.

## 2. Opción recomendada: publicación automática vía GitHub Actions

Esta es la opción sostenible: cada vez que se actualice `docs/` y se suba a `main`, el sitio se republica solo.

### Pasos en GitHub (a realizar por el usuario; esta sesión no tiene acceso)

1. Subir este repositorio a GitHub (si aún no está), incluyendo `.github/workflows/publish-quarto.yml` y la carpeta `docs/`.
2. En GitHub: **Settings → Pages**.
3. En **"Build and deployment" → "Source"**, seleccionar **"GitHub Actions"** (no "Deploy from a branch").
4. Hacer push a `main` tocando algo dentro de `docs/` (o ir a **Actions → Publish Quarto Site → Run workflow** para disparar manualmente la primera vez).
5. Esperar a que el workflow termine (pestaña **Actions**); al finalizar, la URL pública aparece en **Settings → Pages** y en el resumen del propio workflow (`steps.deployment.outputs.page_url`).
6. La URL tendrá la forma `https://<usuario-o-organización>.github.io/<nombre-del-repositorio>/` (no se puede predecir aquí el nombre exacto: depende del nombre que el usuario le dé al repositorio en GitHub, que esta sesión no conoce).

### Por qué esta opción y no "Deploy from a branch" con una carpeta

GitHub Pages, en el modo "Deploy from a branch", solo permite servir desde la **raíz** del branch o desde una carpeta llamada exactamente **`/docs`** — ninguna otra carpeta personalizada es seleccionable en la interfaz. Como `docs/` en este repositorio ya es el **proyecto fuente de Quarto** (contiene `.qmd`/`.md` y `_quarto.yml`, no HTML), apuntar Pages directamente a `/docs` serviría los archivos fuente sin procesar, no el sitio renderizado — el usuario vería código fuente en vez de páginas navegables. El workflow de Actions evita este problema por completo: renderiza primero y publica solo el resultado (`docs/_site`), sin que la estructura de carpetas del repositorio importe.

## 3. Opción alternativa: publicar la carpeta `/gh-pages` manualmente (sin depender de Actions)

Útil para una verificación inmediata o si no se quiere configurar Actions todavía.

### 3a. Como branch `gh-pages` dedicado (patrón más común)

```bash
# Desde la raíz del repositorio, con git ya inicializado y el remoto configurado:
git add gh-pages
git commit -m "Publicar sitio Quarto en gh-pages"
git subtree push --prefix gh-pages origin gh-pages
```

Luego, en GitHub: **Settings → Pages → Source → "Deploy from a branch"**, Branch = `gh-pages`, Folder = `/ (root)`.

### 3b. Con cualquier otro host estático (Netlify, Vercel, Cloudflare Pages)

La carpeta `/gh-pages` es un sitio estático genérico: arrastrarla a Netlify Drop, o apuntar Vercel/Cloudflare Pages a esa carpeta como *build output*, funciona igual sin ninguna configuración adicional — ya incluye `.nojekyll` (irrelevante fuera de GitHub, pero no estorba) y todas las rutas son relativas.

### 3c. Verificación local antes de publicar (opcional)

```bash
cd gh-pages
python3 -m http.server 8080
# abrir http://localhost:8080/
```

Así se verificó en esta sesión (capturas de pantalla reales tomadas y compartidas con el usuario en la Fase 11/12).

## 4. Cómo regenerar `/gh-pages` después de editar `docs/`

```bash
cd docs
quarto render
cd ..
rm -rf gh-pages
cp -r docs/_site gh-pages
touch gh-pages/.nojekyll
```

(El paso `touch gh-pages/.nojekyll` es imprescindible cada vez: `quarto render` no lo genera automáticamente para este tipo de proyecto, y sin él, GitHub Pages en modo "Deploy from a branch" excluiría la carpeta `_quarto/` por el procesamiento Jekyll por defecto, rompiendo el CSS del sitio — hallazgo verificado en esta fase.)

## 5. Verificación realizada en esta sesión (antes de declarar nada "listo")

| Verificación | Resultado |
|---|---|
| `quarto render` del proyecto `docs/` completo | 0 errores, 0 warnings, 109 archivos (Fase 11) |
| `/gh-pages` servida de forma aislada (puerto distinto, sin `docs/` al lado) | `index.html`, página de BPMN y un asset SVG probados: 200 OK |
| `.nojekyll` presente en `/gh-pages` | Confirmado |
| Captura de pantalla real de `/gh-pages/index.html` servida de forma aislada | Tomada y compartida con el usuario |

**No verificado en esta sesión** (fuera de su alcance, requiere credenciales/red hacia GitHub): que el workflow `publish-quarto.yml` se ejecute correctamente en el runner real de GitHub Actions, ni que la URL pública final cargue. Se deja como paso a confirmar por el usuario tras subir el repositorio.

## 6. Mantenimiento — cómo actualizar el sitio publicado tras un cambio futuro

- **Si se usa el workflow de Actions (§2):** no se requiere ninguna acción manual — cualquier push a `main` que toque `docs/**` dispara una republicación automática.
- **Si se usa la carpeta `/gh-pages` manual (§3):** repetir el procedimiento de §4 (render + copiar + `.nojekyll`) y volver a empujar la carpeta actualizada al branch/host correspondiente.
