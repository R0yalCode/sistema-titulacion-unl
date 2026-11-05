---
title: "Introducción"
---

# Introducción

## Contexto

El trámite de titulación por **Declaratoria de Aptitud Legal** (Art. 235 del Reglamento de Régimen Académico de la UNL) exige al graduado reunir cinco documentos: récord académico, prácticas de vinculación, idioma extranjero nivel B1, designación de director de trabajo de titulación y certificado de no tener obligaciones con la institución (tesorería). Tradicionalmente este trámite se gestiona de forma manual entre dependencias, sin trazabilidad ni plazos controlados.

**SGT-SIAAF** digitaliza este trámite integrándose conceptualmente al sistema académico-administrativo-financiero institucional (SGA/SIAAF), con expediente electrónico único, checklist digital de verificación, observaciones accionables, plazos regulatorios en días hábiles y resolución documental (Providencia 590 y Memorando 162).

## Naturaleza del proyecto

Simulación académica funcional desarrollada en la carrera de Computación (asignatura *Desarrollo Basado en Plataformas*). No tiene validez legal. La Constitución del proyecto (`.specify/memory/constitution.md`, v2.1 en `specs/001-tramite-titulacion/constitucion.md`) define 18 principios (P-01…P-18) que gobiernan todas las decisiones técnicas.

## Alcance de la Fase 1 (MVP)

Automatización completa del flujo de Declaratoria de Aptitud Legal:

```
BORRADOR → ENVIADA → EN_VERIFICACION → OBSERVADA ⇄ EN_VERIFICACION → INFORME_EMITIDO → DECLARADA_APTA
```

Los estados `CANCELADA` (expediente) y `LEGALIZADO` (petición) están definidos en el modelo pero sin flujo que los produzca aún.

## Qué NO incluye

- Integración real con el SGA institucional (se simula con un adaptador mock de solo lectura).
- Firma electrónica real (FirmaEC se simula como PDF firmado ya cargado).
- Gestión de trabajo de titulación, sustentaciones ni registro de titulados (fases futuras).
