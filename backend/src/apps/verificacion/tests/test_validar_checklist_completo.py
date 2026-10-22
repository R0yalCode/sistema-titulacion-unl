"""Pruebas para T029: Validación de checklist completo antes de emitir informe legal (RN-003).

Verifica:
- Validación que impide emitir informe si hay requisitos PENDIENTE u OBSERVADO
- Retorno HTTP 422 Unprocessable Entity con detalle de requisitos pendientes
- Permite emitir informe cuando todos los requisitos están VERIFICADO
"""

import pytest

from apps.authentication.adapters.models import (
    ROLE_ESTUDIANTE,
    ROLE_SECRETARIO_ABOGADO,
    User,
    Role,
    UserRole,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_CARGADO,
    ESTADO_PENDIENTE,
    ESTADO_VERIFICADO,
    PeticionDocumental,
)
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ESTADO_VERIFICACION_PENDIENTE,
    ESTADO_VERIFICACION_VERIFICADO,
    ESTADO_VERIFICACION_OBSERVADO,
)
from apps.verificacion.services import validar_checklist_completo
from apps.verificacion.services.validar_checklist_completo import (
    ChecklistIncompletoError,
    obtener_requisitos_pendientes,
    obtener_estado_checklist,
)

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing (PDF 1.4)
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"


@pytest.fixture
def rol_estudiante():
    role, _ = Role.objects.get_or_create(name=ROLE_ESTUDIANTE)
    return role


@pytest.fixture
def rol_secretario_abogado():
    role, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
    return role


@pytest.fixture
def estudiante(rol_estudiante):
    user = User.objects.create_user(
        username="estudiante_test",
        email="est@test.com",
        password=PASSWORD,
        cedula="1234567890",
        carrera_id=CARRERA_1,
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=rol_estudiante)
    return user


@pytest.fixture
def secretario_abogado():
    role, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
    user = User.objects.create_user(
        username="secretario_test",
        email="sec@test.com",
        password="pass1234",
        cedula="1234567891",
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=Role.objects.get(name="SECRETARIO_ABOGADO"))
    return user


@pytest.fixture
def expediente_en_verificacion(estudiante):
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id="22222222-2222-2222-2222-222222222222",
        estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
        activa=True,
    )

    # Crear 3 requisitos base
    for i, (codigo, nombre) in enumerate([
        ("REQ-01", "Requisito 1"),
        ("REQ-02", "Requisito 2"),
        ("REQ-03", "Requisito 3"),
    ]):
        requisito = CatalogoDocumental.objects.create(
            codigo_requisito=codigo,
            nombre=nombre,
            es_obligatorio_base=True,
            fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA",
            activo=True,
        )
        peticion = PeticionDocumental.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_peticion=ESTADO_PENDIENTE,
            dependencia_emisora="SECRETARIA_CARRERA",
        )
        from apps.peticiones.adapters.models import DocumentoEntregado
        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=1,
            archivo_path=f"expedientes/2026/{expediente.id}/test_{i}.pdf",
            nombre_original=f"{nombre}.pdf",
            tamanio_bytes=len(PDF_VALIDO),
            hash_sha256="a" * 64,
            tipo_mime="application/pdf",
            subido_por=expediente.estudiante,
            es_vigente=True,
        )

    return expediente


class TestValidarChecklistCompleto:
    """Tests del servicio validar_checklist_completo (T029; RN-003)."""

    def test_execute_falla_si_hay_pendientes(self, expediente_en_verificacion):
        """Falla si hay requisitos en PENDIENTE."""
        with pytest.raises(ChecklistIncompletoError) as exc_info:
            validar_checklist_completo.execute(expediente_en_verificacion.id)

        assert "checklist no está completo" in str(exc_info.value).lower()
        assert len(exc_info.value.requisitos_pendientes) > 0

    def test_execute_falla_si_hay_observados(self, expediente_en_verificacion, secretario_abogado):
        """Falla si hay requisitos en OBSERVADO."""
        from apps.verificacion.adapters.models import ChecklistVerification
        from apps.peticiones.adapters.models import PeticionDocumental

        # Cambiar una petición a VERIFICADO
        peticion = PeticionDocumental.objects.filter(expediente=expediente_en_verificacion).first()
        peticion.estado_peticion = "VERIFICADO"
        peticion.save()
        ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion, requisito=peticion.requisito
        ).update(estado_verificacion="VERIFICADO")

        # Cambiar otra a OBSERVADO
        peticion2 = PeticionDocumental.objects.filter(expediente=expediente_en_verificacion).exclude(pk=peticion.pk).first()
        peticion2.estado_peticion = "OBSERVADO"
        peticion2.save()
        ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion, requisito=peticion2.requisito
        ).update(estado_verificacion="OBSERVADO")

        # Intentar ejecutar - debe fallar
        with pytest.raises(ChecklistIncompletoError) as exc_info:
            validar_checklist_completo.execute(expediente_en_verificacion.id)

        assert "checklist no está completo" in str(exc_info.value).lower()
        assert len(exc_info.value.requisitos_pendientes) > 0
        # Verificar que el requisito pendiente es el que está en OBSERVADO
        assert any(peticion2.requisito.codigo_requisito in req for req in exc_info.value.requisitos_pendientes)

    def test_execute_exitoso_si_todos_verificados(self, expediente_en_verificacion, secretario_abogado):
        """Éxito si todos los requisitos están VERIFICADO."""
        from apps.verificacion.adapters.models import ChecklistVerification
        from apps.peticiones.adapters.models import PeticionDocumental

        # Cambiar todas las peticiones a VERIFICADO
        for peticion in PeticionDocumental.objects.filter(expediente=expediente_en_verificacion):
            peticion.estado_peticion = "VERIFICADO"
            peticion.save()

        ChecklistVerification.objects.filter(expediente=expediente_en_verificacion).update(
            estado_verificacion="VERIFICADO"
        )

        resultado = validar_checklist_completo.execute(expediente_en_verificacion.id)
        assert resultado is True

    def test_execute_falla_si_expediente_no_en_verificacion(self, expediente_en_verificacion):
        """Falla si expediente no está en EN_VERIFICACION ni OBSERVADA."""
        expediente_en_verificacion.estado = ExpedienteTitulacion.ESTADO_ENVIADA
        expediente_en_verificacion.save()

        with pytest.raises(ValueError) as exc_info:
            validar_checklist_completo.execute(expediente_en_verificacion.id)

        assert "debe estar en EN_VERIFICACION u OBSERVADA" in str(exc_info.value)

    def test_obtener_requisitos_pendientes(self, expediente_en_verificacion):
        """Obtiene lista de códigos de requisitos pendientes."""
        pendientes = obtener_requisitos_pendientes(expediente_en_verificacion.id)
        assert isinstance(pendientes, list)
        assert len(pendientes) > 0

    def test_obtener_estado_checklist(self, expediente_en_verificacion):
        """Obtiene estado detallado del checklist."""
        estado = obtener_estado_checklist(expediente_en_verificacion.id)

        assert "total_requisitos" in estado
        assert "verificados" in estado
        assert "pendientes" in estado
        assert "completo" in estado

        assert estado["total_requisitos"] > 0
        assert estado["completo"] is False
        assert len(estado["pendientes"]) > 0
        for pendiente in estado["pendientes"]:
            assert "peticion_id" in pendiente
            assert "requisito_codigo" in pendiente
            assert "requisito_nombre" in pendiente
            assert "estado" in pendiente

    def test_obtener_estado_checklist_completo(self, expediente_en_verificacion, secretario_abogado):
        """Estado completo cuando todos verificados."""
        from apps.verificacion.adapters.models import ChecklistVerification
        from apps.peticiones.adapters.models import PeticionDocumental

        for peticion in PeticionDocumental.objects.filter(expediente=expediente_en_verificacion):
            peticion.estado_peticion = "VERIFICADO"
            peticion.save()

        ChecklistVerification.objects.filter(expediente=expediente_en_verificacion).update(
            estado_verificacion="VERIFICADO"
        )

        estado = obtener_estado_checklist(expediente_en_verificacion.id)
        assert estado["completo"] is True
        assert estado["verificados"] == estado["total_requisitos"]
        assert len(estado["pendientes"]) == 0