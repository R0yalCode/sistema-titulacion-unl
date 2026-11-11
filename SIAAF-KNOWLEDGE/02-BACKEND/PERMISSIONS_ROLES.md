---
system: SGT-SIAAF
type: security
area: rbac
status: verified
source: verified-code
last_verified: 2026-11-11
---

# Roles y permisos (RBAC real)

**Código:** `backend/src/apps/authentication/adapters/permissions.py` (`RBAC_MATRIX`, `get_granted_scopes`, `get_scope`), `backend/src/core/adapters/scope_filter.py` (`ScopeFilterMixin`), roles en `backend/src/apps/authentication/adapters/models.py` (`ROLE_CHOICES`).
**Especificación:** `sgt-siaaf/specs/001-tramite-titulacion/specify.md` §6.1–6.2.

## 1. Roles (8, verificados)

| Código | Nombre visible | Responsabilidad (specify 001 §6.1) |
|---|---|---|
| `ESTUDIANTE` | Estudiante | Crea solicitudes, solicita certificados, adjunta PDF, subsana, consulta estado |
| `SECRETARIA_CARRERA` | Secretaria de Carrera | Atiende peticiones de récord académico, sube documento, gestiona legalización |
| `SECRETARIO_ABOGADO` | Secretario/a-Abogado/a | Revisa checklist, legaliza récord, observa, emite informe #590, levanta actas (Fase 2) |
| `ANALISTA_APOYO` | Analista de Apoyo | Prepara borradores de informe, providencia y checklist |
| `DECANO` | Decano/a | Revisa informe y registra declaratoria con memorando firmado #162 |
| `DIRECTOR_CARRERA` | Director de Carrera | Legaliza certificado de prácticas; designa tribunal (Fase 2) |
| `RESPONSABLE_DEPENDENCIA` | Responsable de Dependencia | Unidades emisoras (Tesorería, Idiomas, Prácticas) |
| `ADMINISTRADOR` | Administrador | Usuarios, roles, parámetros, catálogo de requisitos |

Un usuario puede tener varios roles (`UserRole`); los scopes concedidos se **unen** (`get_granted_scopes`) y, para vistas de alcance único, se toma el **más restrictivo** (`get_scope`: OWN → ASIGNADO → BORRADOR → …).

## 2. Scopes

`SCOPE_OWN` (propio, `estudiante_id`), `SCOPE_CARRERA` (`carrera_id`), `SCOPE_FACULTAD` (`facultad_id`), `SCOPE_ASIGNADO` (petición asignada a la dependencia del rol), `SCOPE_BORRADOR` (solo borrador), `ALLOW` (global), `DENY`.

## 3. Matriz real (`RBAC_MATRIX`)

| Recurso / método | EST | SEC_CAR | SEC_ABO | ANALISTA | DECANO | DIR_CAR | RESP_DEP | ADMIN |
|---|---|---|---|---|---|---|---|---|
| `notificaciones` GET/PATCH | OWN | CARRERA | FACULTAD | FACULTAD | FACULTAD | CARRERA | — | ALLOW |
| `expedientes` POST | ALLOW | — | — | — | — | — | — | ALLOW |
| `expedientes` GET | OWN | CARRERA | FACULTAD | FACULTAD | FACULTAD | CARRERA | — | ALLOW |
| `expedientes:enviar` POST | OWN | — | — | — | — | — | — | — |
| `expedientes:iniciar_verificacion` POST (AUT-02, 2026-11-11) | — | — | FACULTAD | — | — | — | — | — |
| `peticiones` POST (solicitar emisión) | OWN | — | — | — | — | — | — | ALLOW |
| `peticiones:documento` POST/GET | OWN | ASIGNADO | ASIGNADO | ASIGNADO | — | ASIGNADO | — | ALLOW |
| `checklist` GET | — | — | FACULTAD | FACULTAD | — | — | — | ALLOW |
| `checklist` PUT/PATCH | — | — | ALLOW | BORRADOR | — | — | — | ALLOW |
| `checklist` POST (subsanar) | OWN | CARRERA | — | — | — | — | — | ALLOW |
| `expedientes:observar` POST | — | — | ALLOW | — | — | — | — | — |
| `informes` POST | — | — | ALLOW | BORRADOR | — | — | — | — |
| `declaratorias` POST/PUT/PATCH | — | — | — | — | ALLOW | — | — | — |
| `catalogos:requisitos` POST/PUT | — | — | — | — | — | — | — | ALLOW |

`—` = sin concesión (denegado).

## 4. Hallazgos verificados

1. **`RESPONSABLE_DEPENDENCIA` no tiene ninguna celda** en `RBAC_MATRIX` → hoy no puede operar en ningún recurso (VULN-006, IP). Contradice la [[DP2-MATRIZ_ACCIONES_RAPIDAS]], que le asigna "Cargar/Descargar documento (asignado)".
2. **`SCOPE_ASIGNADO`** no está implementado en `ScopeFilterMixin`. En `PeticionViewSet` (`backend/src/apps/peticiones/adapters/views.py`), `get_queryset()` omite el filtro de ámbito del mixin para `descargar_documento` (≈ línea 121) y la descarga valida el ámbito **manualmente** con `_validar_ambito_descarga()` (≈ líneas 200–280), que sí contempla `SCOPE_ASIGNADO` y responde 404 si no hay acceso. Las demás acciones usan el mixin. Estado VULN-002: mitigado solo en la descarga (coincide con [[DP2-MATRIZ_BRECHAS]] "validación manual solo en descarga"); la corrección general en el mixin sigue pendiente (INC-01-T02).
3. `DECANO` no tiene acceso a `peticiones:documento` ni a `checklist`.
4. La subsanación (`checklist` POST) está concedida a ESTUDIANTE y SECRETARIA_CARRERA, pero ninguno de los dos puede listar el checklist (`checklist` GET) para obtener el `checklist_verification_id` (hallazgo FE-T407; ver [[API_CONTRACTS]]).
5. **Bandeja**: además del RBAC, `BandejaExpedienteViewSet` filtra por `MAPA_INTERVENCION_POR_ROL` (`backend/src/apps/expedientes/adapters/views.py` ≈ 195): ESTUDIANTE {BORRADOR, OBSERVADA}; SEC_ABO y ANALISTA {ENVIADA, EN_VERIFICACION, OBSERVADA}; DECANO {INFORME_EMITIDO}; ADMIN {todos salvo DECLARADA_APTA/CANCELADA}; SEC_CAR, DIR_CAR y RESP_DEP **vacío** (BE-09).

## 5. Pruebas

`backend/src/apps/authentication/tests/test_rbac_permissions.py`, `test_security_controls.py`, `backend/src/apps/expedientes/tests/test_idor_isolation_expediente.py`. Resultado no reejecutado en esta sesión (ver [[REGRESSION_TESTS]]).

## Relacionado

[[06-AUDITS/SECURITY/SECURITY_AUDIT|Auditoría de seguridad]] · [[API_CONTRACTS]] · [[DP2-MATRIZ_ACCIONES_RAPIDAS]]
