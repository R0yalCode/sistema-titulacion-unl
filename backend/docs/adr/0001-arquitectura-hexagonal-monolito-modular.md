# ADR-0001: Arquitectura Hexagonal con Monolito Modular

- **Estado:** Aceptado
- **Fecha:** 20 de octubre de 2026
- **Tarea de origen:** `T006` en `tasks.md` v1.0.0
- **Sistema:** SGT-SIAAF — Backend de la Fase de entrega 1 (Unidad 1)

## Contexto

El backend del SGT-SIAAF debe representar los trámites de titulación con la máxima
trazabilidad, mejores condiciones de prueba y posibilidad de sustituir los
adaptadores de integración futura (`SGA/SIAAF`) sin alterar el dominio
(`DEC-05`). Se debía elegir un patrón de arquitectura entre tres alternativas
evaluadas en `plan.md` § 6.1: Monolito Modular + Hexagonal, Monolito
Tradicional por Capas y Microservicios. El proyecto es una simulación
académica con restricciones de tiempo (5 semanas, sílabo de Desarrollo Basado
en Plataformas) y sin servicios distribuidos aprobados.

## Decisión

Se adopta un **Monolito Modular con Arquitectura Hexagonal (Ports &
Adapters)**, conforme a los límites definidos en `plan.md` § 7, § 11 y § 13:

1. **El dominio es agnóstico:** `src/<módulo>/domain/` contiene datos y reglas
   de negocio puras; no importa Django, DRF ni PostgreSQL.
2. **Inversión de dependencias:** la lógica de aplicación interactúa con la
   infraestructura únicamente a través de interfaces abstractas declaradas en
   `src/<módulo>/ports/` y en `src/core/ports/`.
3. **Los adaptadores son periféricos:** DRF ViewSets, modelos ORM,
   almacenamiento de archivos y adaptadores `mock` residen en
   `src/<módulo>/adapters/` y `src/core/adapters/`; la entrega detalles
   dependen del dominio, nunca a la inversa.
4. El monolito se organiza en seis aplicaciones modulares (`authentication`,
   `expedientes`, `peticiones`, `verificacion`, `resoluciones`,
   `notificaciones`) registradas en `INSTALLED_APPS` mediante `AppConfig` de
   sus paquetes `adapters`.

## Alternativas evaluadas (plan.md § 6.1)

| Criterio | Monolito Modular + Hexagonal | Monolito por Capas | Microservicios |
| :--- | :--- | :--- | :--- |
| Mantenibilidad | Excelente | Media | Alta complejidad de consistencia |
| Tiempo de entrega (5 semanas) | Alto/Óptimo | Muy alto al inicio, riesgoso en refactoring | Muy bajo |
| Integración futura SGA | Excelente (adaptadores reemplazables) | Media (ORM acoplado a API externa) | Alta (Sagas distribuidas) |
| Pruebas automatizadas | Excelente (dominio sin servidor ni BD) | Media | Compleja |
| **Resultado** | **SELECCIONADO** | Descartado por acoplamiento | Descartado por sobreingeniería |

## Consecuencias

- Positivas: dominio verificable de forma unitaria y sin base de datos,
  adaptadores SGA/SIAAF sustituibles (`DEC-05`), límites de módulos claros
  para el trabajo del equipo y separación de responsabilidades por módulo.
- Negativas: mayor cantidad de paquetes (`domain/`, `services/`, `ports/`,
  `adapters/`) por módulo frente a un monolito por capas, que exige disciplina
  de fronteras en la revisión de código.
- El despliegue sigue siendo un único proceso Django respaldado por la base de
  datos; no se introducen servicios distribuidos.

## Referencias

- `constitucion.md` — Principios de arquitectura (sección 6) y P-12
  (interoperabilidad desacoplada), P-15 (reproducibilidad).
- `plan.md` — § 2, § 6.1, § 7, § 11 y § 13 (árbol de directorios aprobado).
- `specify.md` — `RNF-009` (Monolito Modular en Django 5.x / DRF).
- `tasks.md` — Tarea `T004` (estructura implementada y verificada).
