---
title: "CI de seguridad (SEC-T014)"
---

# CI de seguridad

**Estado: implementado (2026-11-05).** Pipeline `.github/workflows/security.yml`
con tres jobs independientes, ejecutados en cada PR y en cada push a `main` y `develop`
(ampliado a `develop` el 2026-11-12, DK-014).

## Jobs

| Job | Herramienta | Qué verifica | Falla si |
|---|---|---|---|
| `safety` | `safety check` (deprecado por el proveedor, pero funcional; ver nota abajo) | Vulnerabilidades conocidas en `requirements.txt`/`requirements-dev.txt` | Cualquier vulnerabilidad reportada, incluidas las que solo afectan a parte de un rango de versiones no fijado (`.github/safety-policy.yml`) |
| `bandit` | `bandit -r src/ -c .bandit` | Patrones de código inseguro (SAST) | Por defecto de bandit (no se configuró un umbral de severidad explícito en el workflow; recomendado revisar hallazgos manualmente hasta fijar uno) |
| `gitleaks` | `gitleaks/gitleaks-action@v2` | Secretos commiteados al repositorio | Cualquier hallazgo no cubierto por `.gitleaks.toml` (raíz; sustituye desde el 2026-11-12 a `backend/.gitleaksignore`, cuyo formato inválido anulaba todas las reglas, DK-014) |

## Hallazgo real durante la implementación: `.bandit` estaba en formato incorrecto

El archivo `backend/.bandit` existía con sintaxis estilo INI (`[bandit]` +
`exclude_dirs = "..."`), pero bandit 1.9.x (la versión actual) espera que
el archivo pasado con `-c` sea **YAML**. Con el formato anterior, bandit
fallaba inmediatamente al arrancar (`Error parsing file`) — el pipeline
tal como estaba documentado originalmente **nunca habría funcionado**.
Corregido a:

```yaml
exclude_dirs:
  - tests
  - migrations
skips:
  - B101
```

Verificado localmente tras la corrección: `bandit -r src/ -c .bandit` →
**0 HIGH, 0 MEDIUM, 1 LOW** (contraseña de la cuenta demo
`seed_initial_data.py`, ya documentada en otros lugares como no
productiva — no es un secreto real, es un dato de siembra de desarrollo).

## Hallazgo real: `safety check` ignora por defecto vulnerabilidades en rangos no fijados

`requirements.txt` usa rangos (`Django>=5.2,<5.3`, etc.), no versiones
exactas. El comportamiento por defecto de `safety check` es **no reportar**
vulnerabilidades que solo afectan a parte de un rango así — en este
proyecto eso ocultaba **42 vulnerabilidades conocidas** (37 solo en
Django) que nunca aparecían en un `safety check` simple. Se añadió
`.github/safety-policy.yml` (`ignore-unpinned-requirements: false`) para
que el pipeline las evalúe de verdad.

### Corrección aplicada a `requirements.txt` (pisos de versión mínimos, sin tocar el techo del rango)

| Paquete | Antes | Ahora | Motivo |
|---|---|---|---|
| `Django` | `>=5.2,<5.3` | `>=5.2.19,<5.3` | Corrige 4 CVEs reales dentro del rango (incluye 2 de inyección SQL); `5.2.19` es la versión ya instalada/usada en la práctica — no cambia el comportamiento actual |
| `djangorestframework` | `>=3.16,<4.0` | `>=3.17.2,<4.0` | Corrige 2 CVEs (divulgación de información, validación de entrada); `3.18.3` ya instalado satisface el nuevo piso |
| `djangorestframework-simplejwt` | `>=5.5,<6.0` | `>=5.5.1,<6.0` | Corrige CVE-2024-22513 (divulgación de información); `5.5.1` ya instalado coincide exactamente con el piso nuevo |

Verificado tras el ajuste: **42 → 2 vulnerabilidades reportadas** (las 2
restantes son en `pytest` y `black`, herramientas de desarrollo/test, no
desplegadas en producción; corregirlas requeriría subir el **techo** del
rango, no solo el piso — un cambio de alcance mayor, no aplicado aquí).
Suite completa (492/492) sin regresión tras los tres ajustes.

## Limitaciones de esta verificación

- **`gitleaks` no se pudo ejecutar localmente** en este entorno (no hay
  binario disponible vía gestor de paquetes, y no se descargó un
  ejecutable de internet para evitar ejecutar binarios de origen no
  verificado). El job del workflow usa la acción oficial de GitHub
  (`gitleaks/gitleaks-action@v2`), que sí se ejecutará en CI real; no se
  simula ni se inventa un resultado aquí.
- `safety check` está marcado como **deprecado** por el proveedor (sin
  soporte después de junio 2024), en favor de `safety scan`. Se mantuvo
  `check` porque sigue siendo funcional y es lo que especifica la ficha
  SEC-T014; migrar a `scan` es una mejora futura razonable (requiere
  evaluar su modelo de cuenta/API del proveedor).
- El pipeline no se ejecutó dentro de GitHub Actions real (no hay forma
  de disparar un workflow de GitHub desde este entorno); se verificó cada
  herramienta localmente con los mismos comandos/configuración que usa
  el workflow.
