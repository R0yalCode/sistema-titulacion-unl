---
title: "GitHub Actions"
---

# Automatización CI — SGT-SIAAF

**Fuente:** `.github/workflows/security.yml` (único workflow real, leído íntegramente), `.github/dependabot.yml`, `.github/safety-policy.yml`, `.github/PULL_REQUEST_TEMPLATE.md`. No se inventan workflows adicionales.

## 1. Único workflow existente: `security.yml`

Se ejecuta en `pull_request` y en `push` a `main`. Define **3 jobs independientes**, todos de seguridad — **ninguno ejecuta pruebas funcionales, lint de estilo ni build**:

| Job | Herramienta | Comando real |
|---|---|---|
| `safety` | Safety (escaneo de dependencias) | `safety check -r requirements.txt -r requirements-dev.txt --policy-file ../.github/safety-policy.yml` |
| `bandit` | Bandit (análisis estático) | `bandit -r src/ -c .bandit` |
| `gitleaks` | Gitleaks (detección de secretos) | Acción oficial `gitleaks/gitleaks-action@v2`, configurado con `backend/.gitleaksignore` |

Los tres jobs usan Python 3.12 (`actions/setup-python@v5`), consistente con la versión real del proyecto (a diferencia del entorno de esta auditoría en Fase 7, que usó 3.14 por no haber 3.12 disponible).

## 2. Hallazgo: no hay CI de pruebas funcionales ni de lint de estilo

**No existe ningún job que ejecute `pytest`, `flake8`, `mypy`, `npm run test`, `npm run lint` o `npm run typecheck` en GitHub Actions.** Todo el aseguramiento de calidad funcional (pruebas, cobertura, lint, tipado) depende hoy de que el desarrollador los ejecute localmente antes de integrar cambios — no hay una puerta automática en el repositorio remoto que lo garantice. Esto es consistente con lo que ya señalaba `auditoria/01_AUDITORIA_GENERAL.md` ("No hay CI, sólo plantilla PR") y con lo que confirma esta auditoría al leer el único workflow existente: cubre seguridad, no corrección funcional.

## 3. Dependabot

`.github/dependabot.yml` existe (no se detalla su contenido exhaustivamente en esta pasada); su sola presencia indica que hay automatización de actualización de dependencias configurada, complementaria al job `safety` del workflow.

## 4. Plantilla de Pull Request

`.github/PULL_REQUEST_TEMPLATE.md` existe. Por instrucción explícita del encargo (sección 2.4), el apartado de control de versiones/GitFlow/PR está excluido de esta auditoría — se menciona su existencia únicamente como parte del inventario de `.github/`, sin analizar su contenido ni su uso.

## 5. Conclusión

La automatización CI real del proyecto es exclusivamente de seguridad (3 escáneres), ejecutada en cada PR y en cada push a `main`. No hay automatización de pruebas ni de calidad de código en GitHub Actions — una brecha real, ya parcialmente señalada por el equipo, que se reconfirma aquí con lectura directa del único workflow.
