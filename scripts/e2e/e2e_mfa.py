"""Prueba E2E real por HTTP del inicio de sesión con TOTP (AUTH-D).

El cliente calcula los códigos desde la clave manual del registro, igual que
Google Authenticator. No usa datos de demostración: el usuario y su
contraseña los crea quien ejecuta la prueba en una base desechable.

Uso (backend en http://127.0.0.1:8765 con un usuario "e2e_estudiante"):
    python scripts/e2e/e2e_mfa.py "<contraseña del usuario de prueba>"

Requiere `pyotp`. Tarda unos 95 s: espera un periodo TOTP (anti-reutilización)
y la ventana del límite de 5 inicios de sesión por minuto.
"""
import http.cookiejar
import json
import sys
import time
import urllib.error
import urllib.request

import pyotp

BASE = "http://127.0.0.1:8765/api/v1/auth"
UA = "Mozilla/5.0 E2E-SGT"
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def post(path, body=None):
    data = json.dumps(body or {}).encode()
    req = urllib.request.Request(
        BASE + path, data=data, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": UA},
    )
    try:
        with opener.open(req) as r:
            return r.status, json.loads(r.read()), dict(r.headers)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw), dict(e.headers)
        except ValueError:
            return e.code, {}, dict(e.headers)


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        sys.exit(1)


creds = {"username": "e2e_estudiante", "password": sys.argv[1]}

s, b, _ = post("/login/", {"username": "e2e_estudiante", "password": "mala"})
ok(s == 401 and b["code"] == "credenciales_invalidas", "1. contraseña incorrecta -> 401 genérico")

s, b, _ = post("/login/", creds)
ok(s == 200 and b["status"] == "mfa_setup_required" and "access" not in b, "2. primer login -> registro TOTP, sin JWT")
reto = b["challenge"]

s, b, h = post("/mfa/setup/", {"challenge": reto})
ok(s == 200 and b["qr_svg"].startswith("data:image/svg+xml"), "3. QR SVG generado por el backend")
ok(h.get("Cache-Control") == "no-store", "3b. respuesta del QR con Cache-Control: no-store")
app = pyotp.TOTP(b["manual_key"].replace(" ", ""))  # "Google Authenticator"

s, b, _ = post("/mfa/setup/confirm/", {"challenge": reto, "code": "000000"})
ok(s == 400 and b["code"] == "codigo_mfa_invalido", "4. código inválido rechazado en el registro")

s, b, h = post("/mfa/setup/confirm/", {"challenge": reto, "code": app.now(), "trust_device": True})
ok(s == 200 and b["status"] == "authenticated" and len(b["recovery_codes"]) == 10, "5. primer código válido -> MFA activo, JWT y 10 códigos")
codigos = b["recovery_codes"]
cookie = next((c for c in jar if c.name == "sgt_trusted_device"), None)
ok(cookie is not None and cookie.has_nonstandard_attr("HttpOnly"), "6. cookie de confianza HttpOnly emitida")

s, b, _ = post("/login/", creds)
ok(s == 200 and b["status"] == "authenticated", "7. login con dispositivo de confianza vigente -> sin TOTP")

s, b, h = post("/logout/")
ok(s == 200, "8. logout revoca la confianza")

s, b, _ = post("/login/", creds)
ok(b["status"] == "mfa_required" and "access" not in b, "9. tras logout -> se exige TOTP")
reto = b["challenge"]

# Esperar al siguiente periodo: el código del registro ya fue usado.
time.sleep(30 - (time.time() % 30) + 1)
codigo = app.now()
s, b, _ = post("/mfa/verify/", {"challenge": reto, "code": codigo})
ok(s == 200 and b["status"] == "authenticated", "10. TOTP actual válido -> sesión")

s, b, _ = post("/login/", creds)
reto = b["challenge"]
s, b, _ = post("/mfa/verify/", {"challenge": reto, "code": codigo})
ok(s == 400 and b["code"] == "codigo_mfa_invalido", "11. reutilización del mismo código rechazada")

expirado = app.at(time.time() - 120)
s, b, _ = post("/mfa/verify/", {"challenge": reto, "code": expirado})
ok(s == 400, "12. código vencido (fuera de la ventana) rechazado")

s, b, _ = post("/login/", creds)
ok(s == 429, "12b. sexto login en el mismo minuto -> 429 (throttle por IP)")
time.sleep(61)

s, b, _ = post("/login/", creds)
reto = b["challenge"]
s, b, _ = post("/mfa/recovery/", {"challenge": reto, "recovery_code": codigos[0]})
ok(s == 200 and b["status"] == "mfa_setup_required", "13. código de recuperación -> reinscripción obligatoria")

s, b, _ = post("/login/", creds)
ok(b["status"] == "mfa_setup_required", "14. autenticador anterior revocado")

s, b, _ = post("/token/", creds)
ok(s == 404, "15. /auth/token/ (sin segundo factor) ya no existe")
print("E2E completo")
