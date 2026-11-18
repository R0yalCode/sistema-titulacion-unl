# Arquitectura prevista para el SAC de la UNL (Apereo CAS)

> **Estado: documentado; no implementado; pendiente de autorización institucional.**
> SGT-SIAAF **no** está registrado como servicio en el SAC. No existe código, configuración, endpoint ni ticket CAS en el repositorio, ni simulado ni real. Las capturas de `referencias/` muestran el SAC real (Apereo CAS 7.2.4) solo como referencia visual.

## 1. Punto de extensión existente

- `apps/authentication/ports/identity_provider.py` define el contrato `IdentityProvider` (`name`, `provides_mfa`, `authenticate`).
- `services/identity_providers.py` registra solo `LocalIdentityProvider`. `AUTH_IDENTITY_PROVIDER=cas` falla con `ImproperlyConfigured` y nunca degrada al proveedor local.
- `services/mfa.iniciar_sesion` aplica el principio de **no exigir un TOTP adicional** cuando `provides_mfa=True`. La prueba `test_proveedor_con_mfa_propio_no_pide_totp_adicional` lo verifica con un proveedor de prueba.

## 2. Flujo objetivo (cuando exista autorización)

1. El usuario pulsa «Ingresar al sistema» y SGT-SIAAF redirige al SAC con `service=<URL de retorno registrada>`.
2. El SAC autentica, aplica su propio 2FA institucional y vuelve con un `ticket`.
3. El **backend** valida el ticket contra el SAC (`/p3/serviceValidate` u otra variante que confirme la UNL). Nunca lo hace React.
4. Se verifica que el `service` del ticket coincida exactamente con el registrado (destinatario) y que el ticket sea de un solo uso.
5. La identidad institucional (atributo acordado, p. ej. `uid` o el correo institucional) se asocia con `User` local. Si no hay coincidencia, se deniega o se aplica un aprovisionamiento aprobado por la UNL; nunca se crea una cuenta con roles por defecto.
6. Los roles y permisos siguen saliendo de `UserRole`/`RBAC_MATRIX` de SGT-SIAAF; los atributos de CAS no conceden roles salvo acuerdo expreso.
7. SGT-SIAAF emite su sesión (JWT) con `amr=["cas","mfa"]`.
8. Cierre de sesión: logout local, más una redirección a `/logout` del SAC y, si se acuerda, Single Logout por callback.

## 3. Información que deben proporcionar los administradores de la UNL

- Autorización formal y registro de SGT-SIAAF como servicio (URL de servicio exacta por entorno).
- URL base del SAC y versión y protocolo admitidos (CAS 2/3, SAML u OIDC si existiera).
- Atributos liberados y cuál es el identificador estable.
- Política de 2FA del SAC (obligatoria para qué cuentas) y si expone un atributo o `authnContext` que lo acredite.
- Política de Single Logout y de duración de la sesión SSO.
- Entorno de pruebas y cuentas de prueba institucionales.
- Requisitos de TLS y certificados, y las IP de salida si hay listas de control.

## 4. Cambios previstos al integrar

- `CasIdentityProvider` nuevo con `provides_mfa` condicionado a la evidencia de MFA en la respuesta del SAC.
- Endpoint de callback en el backend y botón de redirección en el frontend.
- Retirar o restringir el login local según decida la UNL (p. ej. solo cuentas de servicio).

## 5. Política de confianza bajo CAS

- Si el SAC acredita el MFA, la «confianza del dispositivo» la gestiona el SAC (su SSO y su 2FA). SGT-SIAAF no emite `sgt_trusted_device` ni pide TOTP.
- Si el SAC **no** acredita el MFA en la respuesta, SGT-SIAAF puede seguir exigiendo su TOTP y la confianza de 5 días tal como funcionan hoy, con `provides_mfa=False`.
- Los autenticadores TOTP locales se conservarían como contingencia o se retirarían con `restablecer_mfa`, según decida la UNL.
