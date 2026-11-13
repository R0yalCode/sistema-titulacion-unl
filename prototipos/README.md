# Prototipos de referencia (HTML/CSS/JS)

Maquetas estáticas que sirvieron de referencia visual y de comportamiento para
el frontend React. **No forman parte de la aplicación**: no se compilan, no se
despliegan y no se conectan al backend. Se trasladaron desde la raíz del
repositorio el 2026-11-12 (DK-014) sin modificar su contenido. Solo se quitó
la carpeta envoltorio que dejaba el ZIP original:

| Carpeta | Ubicación anterior | Prototipo |
|---|---|---|
| `prototipo-general/` | `SGT_SIAAF_Prototipo_HTML_CSS_JS/SGT_SIAAF_Prototipo_Web/` | **A**: 9 vistas navegables del trámite (acceso, estudiante no habilitado, inicio, nueva solicitud, expediente, peticiones, bandeja y detalle del funcionario) con perfiles y datos ficticios |
| `vistas-errores-unl/` | `SGT_SIAAF_8_Vistas_Errores_UNL_HTML_CSS_JS/SGT_SIAAF_Errores_HTML_UNL/` | **B**: kit de estados de error (401, 403, 404, 500, 503 como página; 409, 412 y 428 dentro de formulario), galería, capturas y las ilustraciones originales de la mascota |

## Reglas de uso

- Son **referencia de tono y comportamiento**, no código reutilizable
  (`AGENTS.md` regla 4; `clarify.md` DEC-11). El código React se escribe desde
  cero con los tokens del design system.
- Sus datos y perfiles son ficticios. Nada de su contenido se traslada a la
  aplicación (CA-G-01, cero simulación).
- `vistas-errores-unl/assets/img/mascota-*.png` son los **originales** de las
  ilustraciones copiadas en `frontend/public/assets/mascotas/`. Deben
  conservarse para mantener la trazabilidad de procedencia
  (`frontend/docs/assets-mascotas.md`, DEC-15).
- Las vistas 409, 412 y 428 de `vistas-errores-unl/` son el único diseño de
  referencia de esos estados. Su implementación (FE-T1213) sigue bloqueada
  por BE-11.

## Cómo abrirlos

Abre el `index.html` de cada carpeta en el navegador. No requieren
dependencias. En `prototipo-general/`, si el navegador restringe
`sessionStorage` en archivos locales, sírvelo desde un servidor local:

```bash
python3 -m http.server 5500 --bind 127.0.0.1 --directory prototipos/prototipo-general
```

Los `README.md` internos de cada prototipo conservan su documentación
original, incluidas las instrucciones del ZIP de distribución.
