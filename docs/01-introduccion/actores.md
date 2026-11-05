---
title: "Actores"
---

# Actores y roles

Los roles son los definidos en el código (`backend/src/apps/authentication/adapters/models.py:7-25`) y en la Constitución (§ roles, C-004/C-005). No existen otros perfiles.

| Rol | Ámbito de datos | Responsabilidad en el trámite |
|---|---|---|
| **Estudiante** | Sus propios expedientes | Inicia la solicitud, solicita emisión de documentos, carga PDFs, subsana observaciones |
| **Secretaría de Carrera** | Su carrera | Admite trámites; emite certificados de récord académico y de director de trabajo |
| **Secretario Abogado** | Su facultad | Verifica el checklist, registra observaciones, emite el Informe de Aptitud (Providencia 590) |
| **Analista de Apoyo** | Su facultad (solo borrador) | Apoya la verificación del checklist |
| **Decano** | Su facultad | Firma la Declaratoria de Aptitud (Memorando 162) |
| **Director de Carrera** | Su carrera | Supervisa los procesos de titulación de su carrera (recibe copias de declaratorias) |
| **Responsable de Dependencia** | Denegado en bandeja | Representa unidades emisoras (vinculación, idioma, tesorería); recibe solicitudes de emisión |
| **Administrador** | Global | Administración del sistema y soporte vía consola interna |

## Sistemas externos (simulados)

| Sistema | Papel | Implementación actual |
|---|---|---|
| SGA/SIAAF institucional | Fuente del récord académico | Adaptador mock de solo lectura con datos inmutables (`core/adapters/mock_sga.py`) |
| FirmaEC | Firma electrónica del memorando | Simulado: el Decano carga el PDF ya firmado (DEC-04) |
