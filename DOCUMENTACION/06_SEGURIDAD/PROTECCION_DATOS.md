---
title: "Protección de datos"
---

# Protección de datos — SGT-SIAAF

**Fuentes:** `backend/.env.example`, `backend/src/config/settings/base.py`, `backend/src/core/adapters/{pdf_validation.py,local_storage.py}`, `docs/06-seguridad/consideraciones-seguridad.md`. No se reproduce ningún secreto real; todos los valores citados de `.env.example` son placeholders explícitos (`change-me-in-dev`).

## 1. Variables de entorno y gestión de secretos

Patrón 12-factor vía `django-environ`: toda configuración sensible se lee de variables de entorno, ninguna hardcodeada en el código fuente (confirmado por Gitleaks, `AUDITORIA_SEGURIDAD.md` §1). Variables obligatorias sin valor por defecto en el código (Django no arranca si faltan): `SECRET_KEY`, `JWT_SIGNING_KEY`. Variables con valores por defecto seguros si se omiten: `DEBUG` (por defecto `False`), `ALLOWED_HOSTS` (por defecto `[]`).

| Variable | Propósito | Obligatoriedad |
|---|---|---|
| `SECRET_KEY` | Firma de sesiones/CSRF/cookies Django | Obligatoria, sin default |
| `JWT_SIGNING_KEY` | Firma de JWT (independiente de `SECRET_KEY`, SEC-T004) | Obligatoria, sin default |
| `DB_PASSWORD` | Credencial de PostgreSQL | Obligatoria en la práctica (sin ella la conexión a BD falla) |
| `DOCUMENT_UPLOAD_THROTTLE` | Límite de carga de documentos | Opcional, default `10/hour` |
| `AUTH_THROTTLE_RATE` | Límite de intentos de login | Opcional, default `5/minute` |
| `ALLOWED_HOSTS` (producción) | Dominios reales autorizados | Obligatoria en `config.settings.production` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes HTTPS del frontend | Obligatoria en producción |
| `TRUSTED_PROXIES` | Proxies de confianza para throttling consciente de IP real | Configurada en producción (SEC-T005) |
| `CORS_ALLOWED_ORIGINS` | Orígenes permitidos para CORS | Solo aplica en `config.settings.production` (`corsheaders` no está en `INSTALLED_APPS`/`MIDDLEWARE` de `base.py`/`local.py`) |

## 2. Información sensible manejada por el sistema

- **Datos personales de estudiantes y funcionarios**: nombre de usuario, correo, cédula (como claim JWT según `docs/06-seguridad/autenticacion.md`), rol institucional. El proyecto se declara explícitamente una **simulación académica con datos ficticios** (`specify.md` §2.2) — no hay datos reales de personas en el entorno de desarrollo/pruebas.
- **Documentos PDF de certificados**: contienen potencialmente datos académicos y financieros del estudiante. Protegidos mediante almacenamiento privado sin URL pública (`PrivateMediaStorage.url()` lanza `NotImplementedError`, verificado en Fase 0) y acceso solo vía endpoint autenticado con verificación de ámbito (`AUTORIZACION_PERMISOS.md` §4).
- **Bitácora de auditoría (`EventoAuditoria`)**: incluye `usuario`, `rol_ejecutado`, `accion`, `detalles_json`, `ip_origen` — es en sí misma información sensible (quién hizo qué y cuándo) que debe protegerse con el mismo rigor que los datos primarios; no se verificó en esta pasada si el acceso a esta tabla está restringido más allá del RBAC general (no tiene endpoint propio expuesto, confirmado en `MATRIZ_TRAZABILIDAD.md`).

## 3. Validación de entradas

- **Archivos PDF**: validación en servidor (no confiar en extensión ni `Content-Type` declarado por el cliente) — magic bytes `%PDF-`, límite estricto de 10 MB, cálculo de hash SHA-256 para integridad (`core/adapters/pdf_validation.py`, verificado Fase 0/4).
- **Campos de formulario**: validación vía serializers DRF (no se auditó cada serializer individualmente en esta pasada).

## 4. Manejo de errores y exposición de información

Ver `DOCUMENTACION/05_API/CONTRATO_API.md` §3: existen casos donde excepciones de dominio responden **500** en vez de un código semántico 400/422. Con `DEBUG=False` (configuración por defecto verificada), Django no debería incluir el traceback completo en la respuesta HTTP — pero esto **no se verificó empíricamente** en esta auditoría (requeriría provocar el error real contra una instancia en ejecución, tarea de Fase 7). Se señala como punto a confirmar, no como vulnerabilidad confirmada.

## 5. Protección de credenciales

- Contraseñas de usuario: gestionadas por el sistema de autenticación de Django (`AbstractUser`), que aplica hashing (PBKDF2 por defecto en Django) — no se verificó si se cambió el algoritmo de hashing por defecto.
- **Cuentas demo**: `docs/06-seguridad/consideraciones-seguridad.md` señala que las cuentas demo del script de carga inicial (`seed_initial_data.py`) tienen contraseña pública/conocida, marcadas explícitamente como no productivas en el propio script. Riesgo real únicamente si el `seed` se ejecuta en un entorno expuesto públicamente — no aplica al uso académico declarado del proyecto, pero debe documentarse como riesgo operativo si alguna vez se despliega fuera de ese contexto.

## 6. Higiene de secretos en el repositorio (hallazgo heredado, reverificado parcialmente)

`auditoria/01_AUDITORIA_GENERAL.md` señaló `backend/gitleaks.exe` (binario de Windows, ~16 MB) comiteado en el repositorio. Se confirmó su presencia en el inventario de la Fase 0 (`find` lo listó dentro de `backend/`). No es en sí mismo un secreto expuesto, pero es un problema de higiene de repositorio (binario innecesario versionado) que no se corrige en este trabajo (no se eliminan archivos, regla 2.3).
