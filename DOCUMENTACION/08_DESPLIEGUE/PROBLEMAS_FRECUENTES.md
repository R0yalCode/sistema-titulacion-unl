---
title: "Problemas frecuentes"
---

# Resolución de problemas — SGT-SIAAF

**Fuente:** problemas identificados y verificados directamente en esta auditoría (Fases 0, 3, 7 y 8) y en `docs/sprint-S1/S1_02_DIAGNOSTICO_PRUEBAS.md`/`S1_03_DIAGNOSTICO_DJANGO_ADMIN.md` (no leídos en detalle en esta pasada; citados por su propósito). Solo se documentan problemas con evidencia real, no hipotéticos.

## 1. `docker compose up` falla con "JWT_SIGNING_KEY is required"

**Causa confirmada** (`INSTALACION.md` §3): el `.env` de ejemplo en `README.md` no incluye `JWT_SIGNING_KEY`, pero `docker-compose.yml` la exige sin valor por defecto.

**Solución:** añadir al `.env` de la raíz, además de las variables que sí documenta el README:
```bash
JWT_SIGNING_KEY=<valor generado con: openssl rand -base64 32>
```
Debe ser **distinto** de `SECRET_KEY` (si coinciden, el sistema arranca pero registra una advertencia en logs, no bloquea — ver `DOCUMENTACION/06_SEGURIDAD/AUTENTICACION.md` §4).

## 2. `pytest` reporta menos pruebas de las esperadas

**Causa confirmada** (Fase 7): `testpaths = ["src/apps"]` en `pyproject.toml` excluye `src/core` (76 pruebas) del comando `pytest` sin argumentos.

**Solución:** `pytest src/apps src/core` (o `pytest src`) para el conjunto completo.

## 3. `test_pdf_generator.py` falla con 13 pruebas en rojo

**Causa confirmada mediante experimento** (Fase 7): la función auxiliar de esos tests importa `pypdf` para leer el texto del PDF generado; `pypdf` **no es una dependencia declarada** del proyecto (no está en `requirements.txt` ni `requirements-dev.txt`).

**Solución (si se desea verificar el contenido real del PDF, no solo su existencia):** `pip install pypdf` en el entorno de pruebas. El equipo del proyecto ya decidió (`clarify.md`, DEC-05) aceptar esto como deuda de entorno sin bloquear el desarrollo — no es necesario instalarlo para considerar el backend funcional.

## 4. El suite de frontend (`npm run test`) falla de forma intermitente

**Causa identificada, no resuelta** (Fase 7): 4 pruebas de `src/app/router.test.tsx` dependen de temporizadores internos (`findByRole`/`waitFor`) que compiten por recursos cuando se ejecutan junto con los otros 57 archivos de prueba bajo el pool por defecto de Vitest. Pasan siempre si se ejecuta ese archivo en aislamiento.

**Mitigación sugerida (no aplicada, requeriría modificar `vitest.config.ts`, fuera del alcance de este trabajo de documentación):** la propia salida de Vitest sugiere `pool: 'vmThreads'` con `isolate: false`, o aumentar el timeout de `waitFor` en esas pruebas específicas.

## 5. `flake8 src/` reporta cientos de hallazgos pese a que un informe previo decía "sin errores"

**Causa no determinada** (Fase 7): se verificó la discrepancia con el mismo comando documentado, sin poder establecer si se debe a cambios de código posteriores al informe, a una configuración `.flake8` distinta en aquel momento, o a un error del informe original. La mayoría de los hallazgos (538/874) son de longitud de línea (`E501`), no de corrección funcional.

**Solución práctica:** ejecutar `black src/` (ya está entre las dependencias de desarrollo) para normalizar formato antes de revisar manualmente los hallazgos `F401`/`F811`/`F841` restantes, que sí pueden indicar código muerto o importaciones redundantes.

## 6. Certificados TLS ausentes al levantar `docker-compose.prod.yml`

**Causa documentada por el propio proyecto** (comentario en `nginx/prod.conf`): Nginx de producción espera `./nginx/certs/fullchain.pem` y `privkey.pem` montados externamente; no están incluidos en el repositorio (correctamente, por seguridad). Sin ellos, el servicio `nginx` no arranca.

**Solución:** proveer certificados reales (Let's Encrypt/Certbot, o la PKI institucional) antes de desplegar en producción — no es un defecto, es el comportamiento esperado de un repositorio que no debe contener secretos ni certificados reales.
