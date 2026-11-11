---
system: SGT-SIAAF
type: regulatory
status: partially-verified
source: sgt-siaaf/specs/001-tramite-titulacion/specify.md §1.3
last_verified: 2026-11-11
---

# Marco institucional y fuentes normativas

> **Ningún documento normativo oficial (RRA-UNL, Estatuto, plantillas firmadas) está en el repositorio.** Todo lo que sigue procede de **citas** en las especificaciones. El texto literal de los artículos no se ha podido contrastar aquí. Distingue siempre: **normativa oficial** (citada, sin fuente primaria en el repo) · **decisión institucional** · **regla de negocio** · **propuesta técnica** · **implementación**.

## Contexto

SGT-SIAAF digitaliza la **fase administrativa** del trámite de titulación de pregrado de la **Carrera de Computación de la FEIRNNR (Facultad de la Energía, las Industrias y los Recursos Naturales No Renovables), Universidad Nacional de Loja**, integrado conceptualmente al SIAAF y **sin acceso** a las BD productivas del SGA/SIAAF. Es una **simulación académica funcional** de la asignatura Desarrollo Basado en Plataformas (specify 001 §2.1–2.2).

## Fuentes primarias declaradas (specify 001 §1.3)

| Clave | Fuente | Fecha | ¿En el repo? |
|---|---|---|---|
| `[Constitución v2.0]` | Constitución del proyecto SGT-SIAAF (20 principios) | 2026-10-20 | ✅ `sgt-siaaf/.specify/memory/constitution.md`, `specs/001/constitucion.md` |
| `[RRA-UNL]` | Reglamento de Régimen Académico UNL (aprobado OCS 27-01-2021): Arts. 231, 235, 236–237, 243–244 | 2021-01-27 | ❌ |
| `[Plantilla Providencia #590]` | Providencia e Informe de Aptitud Legal N° 590 SG-FEIRNNR-UNL | 2026-10-13 | ❌ (el backend genera PDF "modelo") |
| `[Plantilla Memorando #162]` | Memorando N° UNL-FEIRNNR-2026-162-M (declaratoria del Decano) | 2026-10-15 | ❌ |
| `[Docente]` | Transcripción de retroalimentación docente | 2026-10-15 | ❌ |
| `[Análisis SGT v3]` | Documentos de análisis 01–05 v3 | 2026-10-15 | ❌ |
| `[ACD2]` | `ACD2_DESARROLLO.pdf` (RF-01…16, RNF-01…18) | — | ❌ |
| `[Sílabo-DBP]` | Sílabo Desarrollo Basado en Plataformas (E2C4A3) | — | ❌ |
| `[Estatuto UNL]` | Estatuto Orgánico UNL | 2019-11-06 | ❌ |

## Directrices institucionales recogidas (specify 001)

- Complementar el SGA/SIAAF **sin reemplazarlo**; sin escrituras en BD legadas (RN-012).
- El promedio del SGA es inalterable (RN-005, DEC-05 de la spec 001).
- Firma autógrafa física obligatoria en actas de defensa (RN-006).
- Peticiones internas **sin correo electrónico** (DEC-01 de la spec 001: notificaciones solo in-app).
- Los documentos generados en el sistema no tienen validez legal.

## Relacionado

[[ARTICLES_AND_PROVISIONS]] · [[REGULATORY_TRACEABILITY]] · [[DEGREE_PROCESS_OVERVIEW]]
