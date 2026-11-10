---
title: "FirmaEC — Pendientes de validación institucional"
---

# Pendientes de validación con la Dirección de Tecnologías de Información (DTI) de la UNL

**Estado: PROPUESTA / DIFERIDA. No implementada.** Esta es la lista de
bloqueos institucionales explícitos. Mientras cualquiera de estos puntos
no esté resuelto, esta propuesta **no debe avanzar a diseño detallado ni
a implementación** (ver `PLAN_IMPLEMENTACION.md`, Fase 0).

## 1. Disponibilidad real del servicio

| # | Pregunta | Riesgo si se asume sin confirmar |
|---|---|---|
| PV-01 | ¿La UNL tiene contratada o habilitada alguna modalidad de FirmaEC u otro servicio de firma electrónica certificada? | Diseñar una integración con un servicio que no existe o no está disponible para la institución |
| PV-02 | Si existe, ¿qué modalidad exacta (API, portal, SDK) y bajo qué condiciones de acceso? | Mismo riesgo — la documentación histórica del proyecto (`DEC-04`) solo describe una simulación, no un servicio real confirmado |
| PV-03 | ¿Existe un ambiente de pruebas (sandbox) separado del de producción? | Imposibilidad de desarrollar/probar sin arriesgar actos administrativos reales |

## 2. Alcance de funcionarios y certificados

| # | Pregunta | Riesgo si se asume sin confirmar |
|---|---|---|
| PV-04 | ¿Qué funcionarios (por rol: Decano, Secretario-Abogado, Director de Carrera, Responsable de Dependencia) tienen o tendrán certificado electrónico personal vigente? | Diseñar un flujo de firma que ningún funcionario pueda usar en la práctica |
| PV-05 | ¿Quién es responsable institucionalmente de emitir, renovar y revocar esos certificados? | Asumir erróneamente que SGT-SIAAF debe o puede gestionar ese ciclo de vida (explícitamente fuera de alcance, ver `SEGURIDAD_Y_PROTECCION_CLAVES.md`) |

## 3. Validez jurídica y normativa interna

| # | Pregunta | Riesgo si se asume sin confirmar |
|---|---|---|
| PV-06 | ¿La normativa interna de la UNL reconoce el Memorando 162 y la Providencia 590 como actos administrativos válidos si se firman electrónicamente por este mecanismo? | Implementar una firma técnicamente válida pero jurídicamente no reconocida por la institución |
| PV-07 | ¿Qué instancia (Procuraduría, Secretaría General) debe aprobar formalmente este cambio de modalidad de firma? | Avanzar sin la aprobación de quien tiene autoridad para autorizarlo |

## 4. Protección de datos y archivo

| # | Pregunta | Riesgo si se asume sin confirmar |
|---|---|---|
| PV-08 | ¿Qué política de retención aplica a documentos firmados electrónicamente y a sus metadatos de firma? | Diseñar una conservación documental incompatible con la política institucional real |
| PV-09 | ¿Qué tratamiento de datos personales del firmante (identidad, metadata de firma) exige la normativa ecuatoriana de protección de datos personales en este contexto institucional? | Tratamiento de datos personales sin base legal adecuada |

## 5. Continuidad operativa

| # | Pregunta | Riesgo si se asume sin confirmar |
|---|---|---|
| PV-10 | ¿Qué sucede operativamente si el proveedor de firma no está disponible y un acto administrativo es urgente? | Diseñar un sistema que bloquee procesos críticos sin una vía de contingencia institucionalmente aceptada |

## 6. Cómo se usa esta lista

Cada fila de este documento debe cerrarse con una respuesta explícita de
la DTI UNL (o la instancia correspondiente), no con una suposición del
equipo de desarrollo. Este documento se considera "vigente y sin
resolver" hasta que exista una respuesta institucional documentada para
cada punto. No se debe eliminar ninguna fila sin esa respuesta — si una
pregunta deja de aplicar, debe marcarse explícitamente como tal con su
justificación, no borrarse silenciosamente.
