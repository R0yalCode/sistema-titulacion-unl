---
title: "FirmaEC — Requisitos institucionales"
---

# Requisitos institucionales

**Estado: PROPUESTA / DIFERIDA. No implementada.** Este documento identifica
el marco normativo general aplicable en Ecuador a la firma electrónica y
enumera qué debe confirmarse institucionalmente antes de diseñar en detalle
cualquier integración. No afirma que la UNL tenga vigente ninguna modalidad
específica — eso se trata en `PENDIENTES_VALIDACION_UNL.md`.

## 1. Marco normativo general (nivel país, de conocimiento público)

Ecuador cuenta con un marco legal para la firma electrónica desde la
**Ley de Comercio Electrónico, Firmas Electrónicas y Mensajes de Datos**
(2002) y su reglamento, que reconoce la validez jurídica de la firma
electrónica certificada y equipara sus efectos a la firma manuscrita
cuando es emitida por una entidad de certificación acreditada. El ente
regulador de la certificación electrónica en Ecuador es la
**Agencia de Regulación y Control de las Telecomunicaciones (ARCOTEL)**
a través del esquema de entidades de certificación acreditadas, y el
servicio de firma electrónica del Estado ecuatoriano para servidores
públicos suele canalizarse mediante certificados emitidos por una entidad
de certificación acreditada (p. ej. Banco Central del Ecuador u otra
acreditada).

**Esto se describe aquí únicamente como contexto general de dominio
público.** Los detalles operativos exactos (API disponible, formato de
integración, costos, SLA, entidad certificadora específica que la UNL usa
o puede usar) **no están confirmados** y no deben asumirse a partir de
este documento.

## 2. Por qué esto importa para SGT-SIAAF

Los documentos que hoy dependen de firma (Memorando 162, Providencia 590)
son actos administrativos de una institución de educación superior
pública. Cualquier integración real de firma electrónica debe:

- Tener respaldo normativo claro de que la firma resultante es válida
  para actos administrativos de la UNL (no solo técnicamente verificable,
  sino jurídicamente aceptada por la institución y, si corresponde, por
  entes de control externos — Contraloría, CES, SENESCYT).
- Ser compatible con las políticas internas de gestión documental y
  archivo de la UNL, que no están descritas en este repositorio.
- Contemplar la gestión del ciclo de vida de los certificados de los
  funcionarios (emisión, renovación, revocación) como un proceso externo
  a SGT-SIAAF, gestionado por la institución y/o el proveedor de
  certificación, no por este sistema.

## 3. Requisitos institucionales a confirmar (no asumidos)

| # | Requisito | Por qué es necesario | Quién debe confirmarlo |
|---|---|---|---|
| RI-01 | ¿Qué modalidad de firma electrónica tiene la UNL contratada o disponible hoy (si alguna)? | Determina si existe algo real que integrar o si se requiere contratación previa | Dirección de Tecnologías de Información (DTI) UNL |
| RI-02 | ¿Qué funcionarios (roles: Decano, Secretario-Abogado, Director de Carrera, etc.) ya poseen certificado electrónico personal vigente? | La propuesta exige certificado individual por funcionario; sin esto no hay base para firmar | DTI UNL / Dirección de Talento Humano |
| RI-03 | ¿Existe un convenio o integración previa de la UNL con un proveedor de certificación o con el servicio FirmaEC del Estado? | Evita asumir un proveedor o protocolo inexistente | DTI UNL / Procuraduría o asesoría legal institucional |
| RI-04 | ¿La normativa interna de la UNL reconoce explícitamente actos administrativos firmados electrónicamente de esta forma (Memorando 162, Providencia 590)? | Validez jurídica del acto, no solo validez técnica de la firma | Procuraduría / Secretaría General UNL |
| RI-05 | ¿Qué política de retención y archivo aplica a los documentos firmados electrónicamente? | Afecta el diseño de conservación de versiones (ver `SEGURIDAD_Y_PROTECCION_CLAVES.md`) | Archivo institucional / DTI UNL |
| RI-06 | ¿Existen restricciones de protección de datos personales sobre la identidad del firmante y metadatos de firma? | Ecuador cuenta con la Ley Orgánica de Protección de Datos Personales; aplica a cualquier dato de identidad capturado | DTI UNL / Oficial de protección de datos si existe |
| RI-07 | ¿Qué ambiente de pruebas (sandbox) del proveedor de firma está disponible para desarrollo, si alguno? | Sin esto no es posible ni siquiera prototipar con seguridad | DTI UNL / proveedor de certificación |

Ninguno de estos puntos se considera resuelto por este documento. Todos
quedan listados también en `PENDIENTES_VALIDACION_UNL.md` como bloqueos
explícitos para cualquier implementación futura.
