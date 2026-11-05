---
title: "Objetivos"
---

# Objetivos

## Objetivo general

Automatizar el trámite de Declaratoria de Aptitud Legal garantizando trazabilidad, plazos regulatorios y separación de responsabilidades por rol.

## Objetivos específicos

1. **Expediente único**: cada estudiante tiene a lo sumo un expediente activo, con numeración correlativa anual verificable.
2. **Requisitos atómicos**: cada documento del Art. 235 es una petición independiente con estados propios y versionado de entregas.
3. **Verificación profesional**: el jurista evalúa un checklist digital con bloqueo pesimista (sin condiciones de carrera) y observaciones accionables.
4. **Plazos regulatorios**: el plazo de atención de 8 días hábiles (COA Art. 160) se calcula, pausa al observar y reanuda al subsanar.
5. **Resolución documental**: generación automática de la Providencia 590 y recepción del Memorando 162 firmado, con persistencia y hash.
6. **Trazabilidad integral**: historial de estados, bitácora de auditoría inmutable (JSONB) y notificaciones in-app.
7. **Seguridad por diseño**: RBAC de mundo cerrado, aislamiento por ámbito (own/carrera/facultad) y protección IDOR con semántica 404.

## Objetivos de calidad

| Objetivo | Meta | Estado verificado |
|---|---|---|
| Cobertura de pruebas backend | ≥ 70 % (DoD S1) | **93 %** |
| Suite verde | 0 fallos | **526/526** |
| Contrato OpenAPI sincronizado | 0 divergencias | **Verificado** |
| Accesibilidad frontend | AA + axe por componente | Implementado en el design system |
