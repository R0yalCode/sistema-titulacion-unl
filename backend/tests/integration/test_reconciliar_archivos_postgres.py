"""I-3, auditoría independiente D-03: `reconciliar_archivos` no toca carpetas
de expedientes con una operación en curso (PostgreSQL real).

Una operación que escribe archivos mantiene el bloqueo de su expediente desde
antes de escribir hasta el *commit*. Aquí otra conexión retiene ese bloqueo y,
mientras tanto, el comando se ejecuta con `--eliminar --confirmar`: el archivo
(antiguo y sin referencia) no se borra y se informa en `en_uso_omitidos`.
Al liberar el bloqueo, una nueva ejecución sí lo elimina.
"""

import importlib
import io
import json
import os
import threading
import time
from io import StringIO
from pathlib import Path

import pytest
from django.apps import apps as django_apps
from django.conf import settings
from django.core.management import call_command
from django.db import connections, transaction

from apps.authentication.adapters.models import Role, User, UserRole
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.expedientes.services import crear_expediente
from apps.peticiones.adapters.models import PeticionDocumental
from apps.peticiones.services import cargar_documento

# Sin serialized_rollback: tras pruebas transaccionales que vacían la base
# (test_postgres_infra) la restauración serializada choca con los content
# types recreados; la prueba siembra ella misma el catálogo base.
pytestmark = [pytest.mark.postgres, pytest.mark.django_db(transaction=True)]

_migracion_catalogo = importlib.import_module(
    "apps.peticiones.adapters.migrations.0002_catalogo_base_art235"
)


def _asegurar_catalogo_base():
    _migracion_catalogo.seed_catalogo_base(django_apps, None)


CARRERA = "aaaaaaaa-1307-4111-8111-111111111111"
PDF = (
    b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n"
    b"trailer\n<< /Root 1 0 R >>\n%%EOF\n"
)


def _ejecutar(*argumentos):
    salida = StringIO()
    call_command(
        "reconciliar_archivos", "--formato", "json", *argumentos, stdout=salida
    )
    return json.loads(salida.getvalue())


def test_expediente_bloqueado_no_se_toca_y_se_elimina_al_liberarse():
    _asegurar_catalogo_base()
    estudiante = User.objects.create_user(
        username="i3pg_rec", password="x", cedula="9070000001", carrera_id=CARRERA
    )
    UserRole.objects.create(
        user=estudiante, role=Role.objects.get_or_create(name="ESTUDIANTE")[0]
    )
    expediente = crear_expediente.execute(estudiante, CARRERA)
    peticion = PeticionDocumental.objects.filter(expediente=expediente).first()
    cargar_documento.execute(
        usuario=estudiante,
        peticion_id=peticion.pk,
        archivo=io.BytesIO(PDF),
        nombre_original="doc.pdf",
    )
    raiz = Path(settings.PRIVATE_MEDIA_ROOT)
    huerfano = raiz / f"expedientes/2026/{expediente.pk}/20261101_000000_viejo.pdf"
    huerfano.write_bytes(PDF)
    antiguo = time.time() - 3 * 86400
    os.utime(huerfano, (antiguo, antiguo))
    relativa = huerfano.relative_to(raiz).as_posix()

    bloqueado, liberar = threading.Event(), threading.Event()

    def operacion_en_curso():
        try:
            with transaction.atomic():
                ExpedienteTitulacion.objects.select_for_update().get(pk=expediente.pk)
                bloqueado.set()
                liberar.wait(20)
        finally:
            connections.close_all()

    hilo = threading.Thread(target=operacion_en_curso)
    hilo.start()
    assert bloqueado.wait(20)
    try:
        durante = _ejecutar("--eliminar", "--confirmar")
    finally:
        liberar.set()
        hilo.join(20)

    assert huerfano.exists()
    assert durante["eliminados"] == []
    assert durante["en_uso_omitidos"] == [relativa]

    despues = _ejecutar("--eliminar", "--confirmar")
    assert despues["eliminados"] == [relativa]
    assert not huerfano.exists()
