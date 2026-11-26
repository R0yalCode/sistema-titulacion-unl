# Actores y necesidades — SGT-SIAAF

**Fuentes:** `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §6.1, `docs/01-introduccion/actores.md`, código real `backend/src/apps/authentication/adapters/{models.py,permissions.py}` (verificado). Los 8 roles coinciden entre las tres fuentes; no se inventan roles adicionales.

## 1. Actores humanos (8 roles institucionales)

| Rol | Ámbito de datos (scope) | Responsabilidad en el trámite | Necesidad que satisface el sistema |
|---|---|---|---|
| **ESTUDIANTE** | Propio (`own`) | Crea el expediente, solicita certificados internos, carga PDF, subsana observaciones, consulta estado | Visibilidad en tiempo real de su trámite; elimina el seguimiento informal por correo |
| **SECRETARIA_CARRERA** | Carrera | Atiende peticiones de récord académico, sube el documento emitido, gestiona legalización | Canal formal de recepción de solicitudes sin correo disperso |
| **SECRETARIO_ABOGADO** | Facultad | Verifica el checklist de 5 requisitos, registra observaciones, emite el informe de aptitud (#590) | Herramienta estructurada de verificación legal con trazabilidad |
| **ANALISTA_APOYO** | Facultad (solo borrador) | Prepara borradores de checklist/informe para revisión del jurista | Apoyo operativo sin autoridad de decisión final |
| **DECANO** | Facultad | Registra la declaratoria de aptitud (#162) adjuntando el memorando firmado | Resolución formal con respaldo documental verificable |
| **DIRECTOR_CARRERA** | Carrera | Legaliza certificado de prácticas; en Fase 2 designaría tribunal (no implementado) | Supervisión de los procesos de titulación de su carrera |
| **RESPONSABLE_DEPENDENCIA** | Denegado en bandeja (atiende peticiones específicas) | Representa unidades emisoras (Tesorería, Idiomas, Prácticas) | Recepción de solicitudes de emisión sin necesidad de correo institucional |
| **ADMINISTRADOR** | Global | Administra usuarios, roles RBAC y el catálogo de requisitos; soporte vía consola interna | Gobernanza y mantenimiento del sistema |

## 2. Sistemas externos (simulados, no actores humanos)

| Sistema | Papel | Implementación actual | Necesidad que cubre |
|---|---|---|---|
| **SGA/SIAAF institucional** | Fuente del récord académico | Adaptador mock de solo lectura (`core/adapters/mock_sga.py`) | Aislamiento de las bases productivas (Principio P-01/C-017) sin bloquear el flujo de verificación |
| **FirmaEC** | Firma electrónica del memorando | Simulado: el Decano carga el PDF ya firmado fuera del sistema (`DEC-04`) | Evita construir un motor criptográfico PKI dentro del alcance del MVP |

## 3. Interacciones principales por actor (resumen de los flujos FL-01…FL-05 de `specify.md` §8)

- **ESTUDIANTE** inicia (`FL-01`), pide certificados (`FL-02`) y subsana (`FL-04`).
- **SECRETARIA_CARRERA**/**RESPONSABLE_DEPENDENCIA** atienden peticiones de `FL-02`.
- **SECRETARIO_ABOGADO** ejecuta la verificación y emite el informe (`FL-03`), y registra observaciones (`FL-04`).
- **ANALISTA_APOYO** apoya en borrador dentro de `FL-03` sin poder emitir el informe final (RBAC lo restringe a `Borrador`).
- **DECANO** cierra el flujo con la declaratoria (`FL-05`).
- **DIRECTOR_CARRERA** y **ADMINISTRADOR** participan transversalmente (legalización de prácticas; administración), sin flujo propio numerado en Fase 1.

## 4. Permisos generales (matriz RBAC, resumen)

La matriz completa rol × recurso × acción × endpoint está en `specify.md` §6.2 y, con mayor detalle y verificada contra el código real (`RBAC_MATRIX` en `authentication/adapters/permissions.py`), en `docs/auditoria-backend/MATRIZ_PERMISOS_ROLES.md`. Principio rector: **mundo cerrado** — un recurso/acción no declarado en la matriz se deniega por defecto (no "se permite por omisión"). Este documento no reproduce la matriz íntegra para evitar duplicación; se referencia como fuente única en `DOCUMENTACION/06_SEGURIDAD/AUTORIZACION_PERMISOS.md` (Fase 6).

## 5. Relación con el frontend

Las 9 vistas del frontend (`specs/003-frontend-titulacion/specify.md` §9) asignan cada vista a uno o más de estos mismos 8 roles; no se definen roles adicionales para el frontend. El detalle de vistas por rol se trata en el capítulo de arquitectura frontend del portal (`docs/02-arquitectura/arquitectura-frontend.md`), no se duplica aquí.
