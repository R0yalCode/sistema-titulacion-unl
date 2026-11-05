---
title: "Alcance"
---

# Alcance

## Dentro del alcance (Fase 1)

| Área | Contenido |
|---|---|
| Backend | API REST `/api/v1/` con 17 operaciones: autenticación JWT, expedientes, peticiones documentales, checklist, resoluciones, notificaciones |
| Dominio | Máquina de estados del expediente (7 estados), plazos laborables, checklist, informe y declaratoria |
| Frontend | SPA React con rutas, autenticación, design system (fase F0–F1); vistas de negocio en desarrollo |
| Datos | PostgreSQL 16; almacenamiento privado de PDF con validación (10 MB, magic bytes, SHA-256) |
| Consola interna | Django Admin como consola de soporte (ADR-0009), modelos de solo lectura |

## Fuera del alcance (fases futuras)

- Integración real con SGA/SIAAF y FirmaEC (hoy simuladas por decisión de diseño: DEC-04, RN-005).
- Gestión del trabajo de titulación: tutorías, sustentaciones, calificaciones, registro de titulados.
- Modalidades de titulación distintas a la declaratoria de aptitud legal.
- Notificaciones por correo electrónico (hoy solo in-app, DEC-01).
- Aplicación móvil.

## Restricciones normativas

La jerarquía de autoridad del proyecto es: (1) Constitución, (2) especificación, (3) ADRs, (4) plan, (5) tareas. Ningún cambio técnico puede contradecir los principios P-01…P-18 (integridad transaccional, mundo cerrado RBAC, auditoría, gestión de secretos, etc.).
