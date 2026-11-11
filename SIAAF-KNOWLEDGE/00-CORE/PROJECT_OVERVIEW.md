---
system: SGT-SIAAF
type: overview
status: verified
source: specify-001 + verified-code
last_verified: 2026-11-11
---

# Visión general del proyecto

## Identidad

**SGT-SIAAF**: Sistema de Gestión del Trámite de Titulación integrado al SIAAF, Universidad Nacional de Loja (UNL), Carrera de Computación, FEIRNNR. Proyecto de la asignatura **Desarrollo Basado en Plataformas** (sílabo E2C4A3).

## Antecedentes y problema (specify 001 §3)

El trámite se hacía de forma presencial y fragmentada: documentos por correo, checklist en papel y dificultad para auditar el plazo de 8 días laborables del Art. 235 RRA-UNL.

## Objetivo

Centralizar, digitalizar, controlar y auditar la fase administrativa de la titulación mediante un **expediente global** y **peticiones documentales internas** dirigidas a las dependencias (Secretaría de Carrera, Dirección de Carrera, Secretaría-Abogacía, Decanato, Tesorería, Instituto de Idiomas, Prácticas), con trazabilidad inmutable.

## Alcance

| Fase | Contenido | Estado |
|---|---|---|
| 1 (MVP) | Declaratoria de aptitud legal (Art. 235) | Backend implementado; frontend V-01…V-04 |
| 2 | Sustentación y defensa (Arts. 236–237) | Diseño preliminar |
| 3 | Acta consolidada y SENESCYT (Arts. 243–244) | Diseño preliminar |
| Transversal | Modalidades TIC/EC, KPIs/dashboards, sesiones | Propuestas (DP2) |

**Fuera de alcance:** sustituir al SGA/SIAAF, escribir en sus bases de datos o dar validez legal a los documentos generados.

## Actores

8 roles: ESTUDIANTE, SECRETARIA_CARRERA, SECRETARIO_ABOGADO, ANALISTA_APOYO, DECANO, DIRECTOR_CARRERA, RESPONSABLE_DEPENDENCIA, ADMINISTRADOR → [[PERMISSIONS_ROLES]].

## Hitos (COSMOS)

ANDROMEDA v0.2.0 (F0–F2.5 + V-01), ANDROMEDA v0.3.0 (V-04), ECLIPSE v0.4.0 (seguridad backend), ROSETTA (documentación maestra, sin versión) → [[COSMOS_VERSIONING]].

## Ver también

[[CURRENT_STATE]] · [[GENERAL_ARCHITECTURE]] · [[DEGREE_PROCESS_OVERVIEW]] · [[INSTITUTIONAL_FRAMEWORK]]
