---
title: "Declaratoria de uso de IA"
---

# Declaratoria de uso responsable de Inteligencia Artificial — SGT-SIAAF

**Objetivo:** declarar de forma académica y verificable el uso de herramientas de inteligencia artificial en el desarrollo de SGT-SIAAF, distinguiendo lo que tiene evidencia directa en el repositorio de lo que es una categoría de uso general sin cita específica — conforme a la regla de no presentar como confirmado lo que no tiene respaldo documental (sección 2.2 del encargo de esta auditoría).

## 1. Principio general

La Inteligencia Artificial se usó en este proyecto como **herramienta de apoyo** al equipo de desarrollo, no como sustituto de su criterio. En todos los usos identificables en el repositorio:

- Los resultados producidos con asistencia de IA son **revisados por el equipo** antes de incorporarse (visible, por ejemplo, en `clarify.md`, donde el análisis secundario de NotebookLM se marca explícitamente como "no normativo" y "pendiente de contraste" con la fuente legal primaria — ver §2).
- Las **decisiones técnicas y normativas siguen siendo responsabilidad de los integrantes del equipo y del docente responsable**, nunca de la herramienta.
- El **código y las pruebas se verifican** por ejecución real, no por confianza en lo que una IA haya generado (evidenciado por la práctica reiterada en el propio repositorio de documentar resultados de `pytest`/`flake8`/`bandit` con comandos y salidas reales, no solo afirmaciones).
- La **documentación se contrasta contra el proyecto real**: este mismo expediente (`DOCUMENTACION/`) es un ejemplo de esa práctica — cada afirmación técnica se verificó leyendo código, ejecutando pruebas o citando una fuente concreta, y se corrigieron explícitamente varios hallazgos heredados que ya no correspondían al estado real del código (ver `CONTROL_MAESTRO_DOCUMENTACION.md` §8, hallazgos H-01 a H-15).
- El **equipo conserva la responsabilidad sobre el producto final**, incluidas las decisiones de qué usar, qué descartar y qué validar de cualquier salida generada con asistencia de IA.

## 2. NotebookLM — evidencia directa en el repositorio

**Uso verificado:** entorno de consulta y organización de fuentes documentales. Citado explícitamente en al menos dos lugares:

1. `sgt-siaaf/specs/003-frontend-titulacion/clarify.md` (DEC-14) y `specify.md` §9.2: NotebookLM se usó para un **análisis secundario** de las opciones de modalidad de titulación (`opcion_titulacion`) frente al Reglamento de Régimen Académico de la UNL (RRA-UNL). El propio proyecto es explícito sobre sus límites: *"Las síntesis de análisis (p. ej. NotebookLM) son referencias secundarias"* que **no constituyen fuente normativa** y que quedan **pendientes de contraste directo** con el texto legal vigente (la fuente primaria del RRA-UNL ni siquiera está presente en el repositorio). Como consecuencia de esa reserva, el equipo **decidió no implementar** ningún selector ni regla de elegibilidad basada en ese análisis hasta validación humana — un ejemplo concreto de revisión crítica de una salida de IA, no de aceptación automática.
2. `docs/sprint-S1/S1_01_VALIDACION_HALLAZGOS.md` (título: *"VALIDACIÓN DE HALLAZGOS DE AUDITORÍA (NotebookLM)"*): sugiere que NotebookLM también se usó como apoyo en la organización de los hallazgos de una auditoría técnica previa (`auditoria/06_AUDITORIA_SEGURIDAD_Y_CALIDAD.md`), cuyos resultados fueron sometidos a un sprint de **validación** posterior por el equipo — de nuevo, revisión explícita, no uso directo sin contraste.

## 3. Asistente de desarrollo por IA — corrección de nomenclatura respecto al encargo

El encargo de esta auditoría pide documentar el uso de una herramienta llamada **"OpenCode"**. **No se encontró ninguna mención a "OpenCode" en el repositorio.** En cambio, se encontró evidencia directa y repetida de uso de **Claude Code** (el asistente de Anthropic) como entorno de asistencia al desarrollo:

- `docs/auditoria-backend/seguridad/plan-implementacion/PLAN_MAESTRO_IMPLEMENTACION.md`: referencia "21 fichas de ejecución para Claude" (las tareas SEC-T001 a SEC-T021 de hardening de seguridad, varias de cuyas correcciones se verificaron como reales y efectivas en las Fases 6, 8 y 9 de esta misma auditoría — p. ej. SEC-T002 throttling de login, SEC-T004 separación de claves JWT, SEC-T005 resolución de IP consciente de proxies).
- `docs/auditoria-backend/seguridad/plan-implementacion/CHECKLIST_EJECUCION_Y_CIERRE.md`: registra explícitamente *"autorización emitida por el responsable del proyecto mediante esta conversación (sesión Claude Code), fecha: 2026-11-05"* — evidencia de que las sesiones de trabajo con esta herramienta quedaron documentadas con fecha y contexto, no ocultas.
- `docs/auditoria-backend/seguridad/plan-implementacion/FICHAS_TECNICAS_SEC_T001_SEC_T021.md`: instrucciones operativas dirigidas explícitamente a "Claude" como ejecutor de las tareas de hardening.
- `AGENTS.md` y `CLAUDE.md` (raíz del repositorio): son, en sí mismos, guías operativas **escritas específicamente para gobernar el comportamiento de Claude Code** en este repositorio (reglas de alcance, prohibiciones, flujo de trabajo) — su sola existencia es evidencia de un uso sistemático y gobernado de esta herramienta, no incidental.
- **Esta misma auditoría y todo este expediente `DOCUMENTACION/`** fueron producidos con Claude Code, en una sesión de trabajo por fases con un registro de control (`CONTROL_MAESTRO_DOCUMENTACION.md`) que documenta cada verificación, cada hallazgo y cada autocorrección — incluyendo al menos un caso (H-04, Fase 3→8) donde una conclusión generada por la propia herramienta en una fase se corrigió explícitamente al verificarla más a fondo en una fase posterior.

**Uso verificado:** análisis de código, apoyo en tareas técnicas (en particular, hardening de seguridad backend — las 21 fichas SEC-T), y generación/revisión de documentación e implementaciones, bajo la autorización y supervisión explícita del responsable del proyecto en cada sesión.

## 4. ChatGPT — categoría de uso declarada por el encargo, sin evidencia directa en el repositorio

El encargo de esta auditoría especifica que ChatGPT se usó como apoyo para revisar contenidos, analizar requerimientos, organizar la documentación y estructurar propuestas de implementación. **No se encontró ninguna cita, mención o artefacto en el repositorio que identifique directamente a ChatGPT** (a diferencia de NotebookLM y Claude Code, ambos citados explícitamente en archivos del propio proyecto). Se documenta aquí la categoría de uso tal como la describe el encargo, **sin presentarla como confirmada por evidencia del repositorio** — conforme a la regla de esta auditoría de no inventar ni sobre-confirmar. Si existe evidencia de su uso fuera del repositorio (conversaciones, documentos de trabajo no versionados), no está al alcance de esta auditoría documental verificarla.

## 5. Modelos concretos

No se identifican versiones o modelos específicos de IA (p. ej. "GPT-4", "Claude Opus/Sonnet X") en ningún artefacto del repositorio. Conforme a la instrucción del encargo de "identificar los modelos concretos solamente cuando existan evidencias de su utilización", no se nombra ninguno más allá de la herramienta general (Claude Code, NotebookLM).

## 6. Resumen de responsabilidad

| Aspecto | Responsable |
|---|---|
| Decisiones normativas (interpretación del RRA-UNL, reglas de negocio) | Equipo de desarrollo y docente responsable — nunca la IA (ver DEC-14, donde una propuesta de NotebookLM se dejó explícitamente sin implementar hasta validación humana) |
| Código final integrado al repositorio | Equipo de desarrollo, con verificación por ejecución real de pruebas (Fases 6-9 de esta auditoría documentan esa práctica de forma reiterada) |
| Autorización de sesiones de trabajo con IA | Responsable del proyecto, registrada con fecha en al menos un caso verificado (`CHECKLIST_EJECUCION_Y_CIERRE.md`) |
| Exactitud de la documentación generada con asistencia de IA (incluido este expediente) | Sujeta a verificación cruzada contra el código real; los errores detectados se corrigen explícitamente, no se ocultan (ver `CONTROL_MAESTRO_DOCUMENTACION.md`, autocorrección H-04) |
