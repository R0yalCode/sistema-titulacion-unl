# Contexto del proyecto — SGT-SIAAF

**Fuentes:** `docs/01-introduccion/introduccion.md`, `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §§2–3, `sgt-siaaf/.specify/memory/constitution.md` §1–2. No se añade información no presente en estas fuentes.

## 1. Qué es SGT-SIAAF

El **Sistema de Gestión del Trámite de Titulación integrado al SIAAF (SGT-SIAAF)** es una plataforma que digitaliza el subproceso de **Declaratoria de Aptitud Legal** (Art. 235 del Reglamento de Régimen Académico de la UNL — RRA-UNL) para la Carrera de Computación de la FEIRNNR, Universidad Nacional de Loja. Sustituye un trámite hoy manual y disperso por correo electrónico, con un expediente electrónico único, checklist digital de verificación, observaciones accionables con plazos regulatorios en días hábiles y emisión documental formal (Providencia 590, Memorando 162).

## 2. Naturaleza del proyecto — declaración obligatoria

Es una **simulación académica funcional**, desarrollada en la asignatura *Desarrollo Basado en Plataformas* (5.º ciclo, Carrera de Computación, UNL), sin validez legal institucional. Esta declaración es explícita en la Constitución del proyecto y se repite en `specify.md` §2.2: los datos son ficticios, el sistema no tiene acceso de escritura a las bases de datos productivas del SGA/SIAAF, y ningún documento generado sustituye la firma o el criterio de las autoridades universitarias reales.

## 3. Problema que aborda

Según el diagnóstico de `specify.md` §3.1, el trámite manual actual presenta cuatro deficiencias documentadas:

1. Pérdida y duplicación de documentos enviados por correo entre bandejas de secretarías.
2. Falta de trazabilidad: el estudiante desconoce el estado real de su trámite.
3. Incertidumbre sobre qué certificados se requieren, al no existir un canal centralizado.
4. Dificultad para auditar el cumplimiento del plazo de 8 días laborables del Art. 235 RRA-UNL.

## 4. Necesidad que justifica el sistema

Automatizar el flujo completo — solicitud, petición interna de certificados, checklist, observaciones/subsanación, informe legal y declaratoria — con trazabilidad inmutable y separación de responsabilidades por rol, conforme a los 18 principios no negociables de la Constitución (P-01…P-18).

## 5. Objetivos

**General** (`specify.md` §4.1): desarrollar una plataforma basada en arquitectura monolítica modular (Django REST Framework + PostgreSQL) que digitalice, controle y audite la fase administrativa del trámite de titulación, garantizando cumplimiento normativo, trazabilidad inmutable y aislamiento respecto a los sistemas legados productivos.

**Específicos** (`specify.md` §4.2, resumidos; ver detalle completo en el documento fuente):
1. Digitalizar la Fase 1 (MVP — Aptitud Legal).
2. Garantizar RBAC con JWT para 8 roles institucionales.
3. Asegurar integridad documental (validación estricta de PDF).
4. Exponer una API RESTful versionada y documentada en OpenAPI v3.
5. Asegurar calidad mediante pruebas automatizadas (meta >70 % de cobertura).

## 6. Alcance general y delimitación por fases

`specify.md` §2.3 delimita tres fases:

| Fase | Prioridad | Contenido | Estado |
|---|---|---|---|
| **Fase 1 — MVP** | Alta | Declaratoria de Aptitud Legal (Art. 235): solicitud, petición interna de certificados, checklist de 5 requisitos, observaciones, informe legal, declaratoria del Decano | **Implementada** (backend); frontend en construcción por vistas (ver `ALCANCE_INCREMENTO.md`) |
| **Fase 2** | Media | Sustentación y defensa (Arts. 236–237): tribunal, calificaciones, acta | Diseño preliminar únicamente (RF-014, RF-015); sin implementación |
| **Fase 3** | Baja | Cierre, acta consolidada y registro SENESCYT (Arts. 243–244) | Diseño preliminar únicamente (RF-016); sin implementación |

El **incremento funcional objeto de la Evaluación Sumativa 1** corresponde a la Fase 1 (backend MVP) ya implementada, documentada en detalle en `ALCANCE_INCREMENTO.md`.

## 7. Limitaciones y restricciones declaradas en las fuentes

- **R-01**: tamaño máximo de archivo adjunto 10 MB, formato estrictamente PDF.
- **R-02**: el backend debe desplegarse de forma reproducible vía `docker-compose up`.
- **S-01** (supuesto): la Universidad definirá si el plazo de 8 días se pausa o reinicia en observaciones — resuelto en `clarify.md` como `AP-01`/`DEC` (pausado, ver `SDD_GITHUB_SPEC_KIT.md`).
- Exclusiones explícitas (`specify.md` §5.3): sin gestión académica de asignaturas/matrículas, sin escritura en bases legadas, sin motor de firma PKI interno, sin decisiones automáticas de aptitud, sin notificaciones masivas SMS/WhatsApp.

## 8. Riesgos identificados en las fuentes

`clarify.md` §8 documenta 8 riesgos de decisión (`RSK-01`…`RSK-08`), de los cuales los de mayor severidad en el MVP son `RSK-01` (cómputo erróneo del plazo de 8 días) y `RSK-03` (permisos ambiguos de carga documental) — ambos ya resueltos por decisión y verificables en el código (ver `MATRIZ_TRAZABILIDAD.md`). Adicionalmente, la auditoría técnica (Fase 0 de este trabajo) identificó riesgos operativos no normativos: ausencia de throttling en login y modo de despliegue de desarrollo por defecto (ver `DOCUMENTACION/00_AUDITORIA/MATRIZ_CUMPLIMIENTO_INICIAL.md`, brechas priorizadas).

## 9. Hallazgo documental: numeración de principios inconsistente entre artefactos

Se detectó que `sgt-siaaf/specs/001-tramite-titulacion/specify.md` cita sistemáticamente principios como "Principio C-001" … "C-020", mientras que la Constitución real (`sgt-siaaf/.specify/memory/constitution.md` y su copia en `specs/001-tramite-titulacion/constitucion.md`) numera sus principios como **P-01 a P-18** (18 principios, no 20). Esta discrepancia ya había sido señalada por `auditoria/05_AUDITORIA_SDD.md` (01-nov-2026) y **sigue presente** en el repositorio a la fecha de este informe (2026-11-06): no se ha corregido. No corresponde a este trabajo de documentación resolverla editando `specify.md` (prohibido sin autorización explícita y sin citar el ID de decisión afectado, según `AGENTS.md` §3.9); se registra como hallazgo pendiente para quien tenga autoridad sobre esos artefactos.
