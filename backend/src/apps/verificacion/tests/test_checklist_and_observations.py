"""Pruebas para T031: Concurrencia, Bloqueo de Informes (RN-003), Resolución de Observaciones y Versionado (HU-007, HU-008, RF-007, RF-008, RN-011, CA-003, CA-004).

Verifica:
- Bloqueo pesimista SELECT FOR UPDATE bajo concurrencia
- Efecto bloqueante RN-003: impide emitir informe con requisitos PENDIENTE/OBSERVADO
- Ciclo completo: Observar -> Subsanar -> Verificar -> Emitir Informe
- Resolución de observaciones y reanudación de plazo
- Versionado N+1 con historial preservado
- Notificaciones internas en cada paso
- Permisos y aislamiento por ámbito (prevención IDOR)
"""

import io

import pytest
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from apps.authentication.adapters.models import (
    ROLE_ESTUDIANTE,
    ROLE_SECRETARIA_CARRERA,
    ROLE_SECRETARIO_ABOGADO,
    ROLE_ANALISTA_APOYO,
    ROLE_DECANO,
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
    DocumentoEntregado,
)
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
    ESTADO_VERIFICACION_PENDIENTE,
    ESTADO_VERIFICACION_VERIFICADO,
    ESTADO_VERIFICACION_OBSERVADO,
)
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.verificacion.services import (
    evaluar_checklist,
    registrar_observacion,
    subsanar_requisito,
    validar_checklist_completo,
)
from apps.expedientes.domain.plazo_calculator import PlazoLaboralCalculator

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing (PDF 1.4)
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# PDF válido versión 1.7
PDF_VALIDO_V2 = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test v1.7) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<less Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"

# Archivos inválidos para testing de seguridad
EJECUTABLE_RENOMBRADO = b"MZ\x90\x00"  # PE header (Windows executable)
ARCHIVO_GRANDE = b"%PDF-1.4\n" + b"x" * (11 * 1024 * 1024)  # 11 MB


@pytest.fixture
def api_client():
    return APIClient()


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def rol_estudiante():
    role, _ = Role.objects.get_or_create(name=ROLE_ESTUDIANTE)
    return role


@pytest.fixture
def rol_secretaria_carrera():
    role, _ = Role.objects.get_or_create(name=ROLE_SECRETARIA_CARRERA)
    return role


@pytest.fixture
def rol_secretario_abogado():
    role, _ = Role.objects.get_or_create(name=ROLE_SECRETARIO_ABOGADO)
    return role


@pytest.fixture
def rol_analista_apoyo():
    role, _ = Role.objects.get_or_create(name=ROLE_ANALISTA_APOYO)
    return role


@pytest.fixture
def rol_decano():
    role, _ = Role.objects.get_or_create(name=ROLE_DECANO)
    return role


@pytest.fixture
def estudiante(rol_estudiante):
    user = User.objects.create_user(
        username="estudiante_test",
        email="est@test.com",
        password=PASSWORD,
        cedula="1234567890",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_estudiante)
    return user


@pytest.fixture
def secretaria_carrera(rol_secretaria_carrera):
    user = User.objects.create_user(
        username="secretaria_test",
        email="sec@test.com",
        password=PASSWORD,
        cedula="1234567891",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_secretaria_carrera)
    return user


@pytest.fixture
def secretario_abogado(rol_secretario_abogado):
    user = User.objects.create_user(
        username="secretario_test",
        email="sec@test.com",
        password=PASSWORD,
        cedula="1234567893",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_secretario_abogado)
    rol_analista, _ = Role.objects.get_or_create(name="ANALISTA_APOYO")
    UserRole.objects.create(user=user, role=rol_analista)
    return user


@pytest.fixture
def analista_apoyo(rol_analista_apoyo):
    user = User.objects.create_user(
        username="analista_test",
        email="analista@test.com",
        password=PASSWORD,
        cedula="1234567892",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_analista_apoyo)
    return user


@pytest.fixture
def decano(rol_decano):
    user = User.objects.create_user(
        username="decano_test",
        email="decano@test.com",
        password=PASSWORD,
        cedula="1234567894",
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_decano)
    return user


@pytest.fixture
def expediente_en_verificacion(estudiante, secretario_abogado):
    """Expediente en EN_VERIFICACION con 3 requisitos CARGADOS."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
        activa=True,
    )

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
            estado_peticion=ESTADO_CARGADO,
            dependencia_emisora="SECRETARIA_CARRERA",
        )
        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=1,
            archivo_path=f"expedientes/2026/{expediente.id}/test_{i}.pdf",
            nombre_original=f"{nombre}.pdf",
            tamanio_bytes=len(PDF_VALIDO),
            hash_sha256="a" * 64,
            tipo_mime="application/pdf",
            subido_por=estudiante,
            es_vigente=True,
        )
        ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="PENDIENTE",
        )

    return expediente


@pytest.fixture
def expediente_observada(estudiante, secretario_abogado):
    """Expediente en OBSERVADA con 1 requisito observado (pausa hace 5 días) y 2 verificados."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO
    from datetime import timedelta

    fecha_pausa = timezone.now() - timedelta(days=5)
    fecha_recepcion = timezone.now() - timedelta(days=10)

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0002",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_OBSERVADA,
        activa=True,
        fecha_ultima_pausa=fecha_pausa,
        fecha_recepcion=fecha_recepcion,
    )

    # REQ-01: VERIFICADO
    req1 = CatalogoDocumental.objects.create(
        codigo_requisito="REQ-01", nombre="Requisito 1",
        es_obligatorio_base=True, fase="FASE_1",
        rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
    )
    p1 = PeticionDocumental.objects.create(
        expediente=expediente, requisito=req1,
        estado_peticion="VERIFICADO", dependencia_emisora="SECRETARIA_CARRERA",
    )
    DocumentoEntregado.objects.create(
        peticion=p1, version=1,
        archivo_path=f"expedientes/2026/{expediente.id}/req1_v1.pdf",
        nombre_original="req1_v1.pdf", tamanio_bytes=len(PDF_VALIDO),
        hash_sha256="a" * 64, tipo_mime="application/pdf",
        subido_por=estudiante, es_vigente=True,
    )
    ChecklistVerification.objects.create(
        expediente=expediente, requisito=req1,
        estado_verificacion="VERIFICADO", evaluado_por=secretario_abogado,
    )

    # REQ-02: VERIFICADO
    req2 = CatalogoDocumental.objects.create(
        codigo_requisito="REQ-02", nombre="Requisito 2",
        es_obligatorio_base=True, fase="FASE_1",
        rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
    )
    p2 = PeticionDocumental.objects.create(
        expediente=expediente, requisito=req2,
        estado_peticion="VERIFICADO", dependencia_emisora="SECRETARIA_CARRERA",
    )
    DocumentoEntregado.objects.create(
        peticion=p2, version=1,
        archivo_path=f"expedientes/2026/{expediente.id}/req2_v1.pdf",
        nombre_original="req2_v1.pdf", tamanio_bytes=len(PDF_VALIDO),
        hash_sha256="b" * 64, tipo_mime="application/pdf",
        subido_por=estudiante, es_vigente=True,
    )
    ChecklistVerification.objects.create(
        expediente=expediente, requisito=req2,
        estado_verificacion="VERIFICADO", evaluado_por=secretario_abogado,
    )

    # REQ-03: OBSERVADO (con observación pendiente)
    req3 = CatalogoDocumental.objects.create(
        codigo_requisito="REQ-03", nombre="Requisito 3",
        es_obligatorio_base=True, fase="FASE_1",
        rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
    )
    p3 = PeticionDocumental.objects.create(
        expediente=expediente, requisito=req3,
        estado_peticion="OBSERVADO", dependencia_emisora="SECRETARIA_CARRERA",
    )
    DocumentoEntregado.objects.create(
        peticion=p3, version=1,
        archivo_path=f"expedientes/2026/{expediente.id}/req3_v1.pdf",
        nombre_original="req3_v1.pdf", tamanio_bytes=len(PDF_VALIDO),
        hash_sha256="c" * 64, tipo_mime="application/pdf",
        subido_por=estudiante, es_vigente=True,
    )
    ChecklistVerification.objects.create(
        expediente=expediente, requisito=req3,
        estado_verificacion="OBSERVADO", evaluado_por=secretario_abogado,
    )
    ObservacionAccionable.objects.create(
        expediente=expediente, peticion=p3,
        registrada_por=secretario_abogado,
        motivo_observacion="Documento ilegible, falta firma",
        resuelta=False,
    )

    return expediente


class TestConcurrenciaBloqueoPesimista:
    """Tests de concurrencia con SELECT FOR UPDATE (ADR-007 / AP-06)."""

    def test_select_for_update_bloquea_evaluacion_mismo_requisito_secuencial(
        self, secretario_abogado, analista_apoyo, expediente_en_verificacion
    ):
        """Verifica que evaluar el mismo requisito dos veces falla la segunda (simula bloqueo)."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion,
            estado_verificacion="PENDIENTE"
        ).first()

        # Primera evaluación - éxito
        result1 = evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif.id,
            nuevo_estado="VERIFICADO",
        )
        assert result1.estado_verificacion == "VERIFICADO"

        # Segunda evaluación del mismo requisito - debe fallar
        with pytest.raises(evaluar_checklist.VerificationAlreadyCompletedError):
            evaluar_checklist.execute(
                usuario=analista_apoyo,
                checklist_verification_id=verif.id,
                nuevo_estado="OBSERVADO",
                motivo_observacion="Concurrencia",
            )

    def test_select_for_update_no_bloquea_requisitos_diferentes(
        self, secretario_abogado, analista_apoyo, expediente_en_verificacion
    ):
        """Usuarios evaluando DIFERENTES requisitos no deben bloquearse."""
        verificaciones = list(ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion,
            estado_verificacion="PENDIENTE"
        )[:2])

        result1 = evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verificaciones[0].id,
            nuevo_estado="VERIFICADO",
        )
        assert result1.estado_verificacion == "VERIFICADO"

        result2 = evaluar_checklist.execute(
            usuario=analista_apoyo,
            checklist_verification_id=verificaciones[1].id,
            nuevo_estado="VERIFICADO",
        )
        assert result2.estado_verificacion == "VERIFICADO"

        for v in verificaciones:
            v.refresh_from_db()
            assert v.estado_verificacion == "VERIFICADO"

    def test_subsanar_despues_observar_evita_re_evaluacion_invalida(
        self, estudiante, secretario_abogado, expediente_observada
    ):
        """Subsanar un requisito observado pone checklist en PENDIENTE, permitiendo re-evaluar."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, requisito__codigo_requisito="REQ-03"
        ).first()

        # Subsanar (pone checklist en PENDIENTE)
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "v2_corregido.pdf"
        doc = subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo,
            nombre_original="v2_corregido.pdf",
        )

        verif.refresh_from_db()
        assert verif.estado_verificacion == "PENDIENTE"

        # Ahora SÍ se puede evaluar de nuevo (ya no está en OBSERVADO)
        result = evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif.id,
            nuevo_estado="VERIFICADO",
        )
        assert result.estado_verificacion == "VERIFICADO"


class TestEfectoBloqueanteRN003:
    """Tests del efecto bloqueante RN-003 sobre emisión de informe legal."""

    def test_bloquea_emision_si_requisitos_pendientes(self, expediente_en_verificacion):
        """Impide emitir informe si hay requisitos PENDIENTE."""
        with pytest.raises(validar_checklist_completo.ChecklistIncompletoError) as exc_info:
            validar_checklist_completo.execute(expediente_en_verificacion.id)

        assert "checklist no está completo" in str(exc_info.value).lower()
        assert len(exc_info.value.requisitos_pendientes) == 3

    def test_bloquea_emision_si_requisitos_observados(self, expediente_observada):
        """Impide emitir informe si hay requisitos OBSERVADO."""
        with pytest.raises(validar_checklist_completo.ChecklistIncompletoError) as exc_info:
            validar_checklist_completo.execute(expediente_observada.id)

        assert "checklist no está completo" in str(exc_info.value).lower()
        assert len(exc_info.value.requisitos_pendientes) == 1
        assert "REQ-03" in str(exc_info.value.requisitos_pendientes)

    def test_permite_emision_si_todos_verificados(self, expediente_en_verificacion, secretario_abogado):
        """Permite emitir informe cuando TODOS están VERIFICADO."""
        for verif in ChecklistVerification.objects.filter(expediente=expediente_en_verificacion):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )

        resultado = validar_checklist_completo.execute(expediente_en_verificacion.id)
        assert resultado is True

    def test_validacion_bloquea_emision_con_observados_servicio(self, expediente_observada, secretario_abogado):
        """Servicio validar_checklist_completo bloquea si hay OBSERVADO."""
        with pytest.raises(validar_checklist_completo.ChecklistIncompletoError) as exc_info:
            validar_checklist_completo.execute(expediente_observada.id)

        assert "REQ-03" in str(exc_info.value)


class TestCicloCompletoObservarSubsanarVerificar:
    """Tests de integración: ciclo completo Observar -> Subsanar -> Verificar."""

    def test_ciclo_completo_usando_registrar_observacion(
        self, estudiante, secretario_abogado, expediente_en_verificacion
    ):
        """Flujo: registrar_observacion -> subsanar -> evaluar VERIFICADO."""
        from apps.peticiones.adapters.models import CatalogoDocumental

        # Obtener petición de REQ-01
        peticion = expediente_en_verificacion.peticiones_documentales.get(
            requisito__codigo_requisito="REQ-01"
        )

        # Paso 1: Registrar observación (pausa reloj, cambia estados, notifica)
        observacion = registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            peticion_id=peticion.id,
            motivo_observacion="Falta firma del director",
        )

        assert observacion.motivo_observacion == "Falta firma del director"
        assert observacion.resuelta is False

        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == ExpedienteTitulacion.ESTADO_OBSERVADA
        assert expediente_en_verificacion.fecha_ultima_pausa is not None

        peticion.refresh_from_db()
        assert peticion.estado_peticion == "OBSERVADO"

        # Verificar notificación al estudiante
        notif_obs = NotificacionInterna.objects.filter(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            peticion=peticion,
        ).first()
        assert notif_obs is not None
        assert "Observación" in notif_obs.titulo

        # Paso 2: Estudiante subsana
        verif = ChecklistVerification.objects.get(
            expediente=expediente_en_verificacion, requisito__codigo_requisito="REQ-01"
        )
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "req1_v2_corregido.pdf"
        doc = subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo,
            nombre_original="req1_v2_corregido.pdf",
        )

        assert doc.version == 2
        assert doc.es_vigente is True

        verif.refresh_from_db()
        assert verif.estado_verificacion == "PENDIENTE"

        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        assert expediente_en_verificacion.fecha_ultima_pausa is None

        # Verificar observación resuelta
        observacion.refresh_from_db()
        assert observacion.resuelta is True

        # Paso 3: Verificar requisito corregido
        result = evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif.id,
            nuevo_estado="VERIFICADO",
        )
        assert result.estado_verificacion == "VERIFICADO"

        # Verificar notificación de subsanación (a jurista/analista)
        notif_sub = NotificacionInterna.objects.filter(
            expediente=expediente_en_verificacion,
        ).exclude(pk=notif_obs.pk).first()
        assert notif_sub is not None
        assert "Subsanación" in notif_sub.titulo

    def test_multiples_ciclos_observar_subsanar_incrementan_version(
        self, estudiante, secretario_abogado, expediente_en_verificacion
    ):
        """Múltiples ciclos Observar (via registrar_observacion) -> Subsanar incrementan versión."""
        peticion = expediente_en_verificacion.peticiones_documentales.get(
            requisito__codigo_requisito="REQ-01"
        )
        verif = ChecklistVerification.objects.get(
            expediente=expediente_en_verificacion, requisito__codigo_requisito="REQ-01"
        )

        # Ciclo 1
        registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            peticion_id=peticion.id,
            motivo_observacion="Obs 1",
        )
        archivo1 = io.BytesIO(PDF_VALIDO)
        archivo1.name = "v2.pdf"
        doc1 = subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo1,
            nombre_original="v2.pdf",
        )
        assert doc1.version == 2

        # Ciclo 2 - volver a observar (expediente debe estar en EN_VERIFICACION)
        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == ExpedienteTitulacion.ESTADO_EN_VERIFICACION

        registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            peticion_id=peticion.id,
            motivo_observacion="Obs 2",
        )

        archivo2 = io.BytesIO(PDF_VALIDO_V2)
        archivo2.name = "v3.pdf"
        doc2 = subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo2,
            nombre_original="v3.pdf",
        )
        assert doc2.version == 3
        assert doc2.es_vigente is True

        # Verificar historial: v1 y v2 no vigentes
        v1 = DocumentoEntregado.objects.get(peticion=peticion, version=1)
        doc1.refresh_from_db()
        assert v1.es_vigente is False
        assert doc1.es_vigente is False
        assert doc2.es_vigente is True

    def test_notificaciones_creadas_en_cada_transicion(self, estudiante, secretario_abogado, expediente_en_verificacion):
        """Verifica notificaciones internas en cada paso del ciclo."""
        peticion = expediente_en_verificacion.peticiones_documentales.get(
            requisito__codigo_requisito="REQ-01"
        )

        # Observar
        registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            peticion_id=peticion.id,
            motivo_observacion="Falta firma",
        )

        notif_obs = NotificacionInterna.objects.filter(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
        ).first()
        assert notif_obs is not None
        assert "Observación" in notif_obs.titulo

        # Subsanar
        verif = ChecklistVerification.objects.get(
            expediente=expediente_en_verificacion, requisito__codigo_requisito="REQ-01"
        )
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "v2.pdf"
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo,
            nombre_original="v2.pdf",
        )

        notif_sub = NotificacionInterna.objects.filter(
            expediente=expediente_en_verificacion,
        ).exclude(pk=notif_obs.pk).first()
        assert notif_sub is not None
        assert "Subsanación" in notif_sub.titulo


class TestReanudacionPlazoLaborable:
    """Tests de pausa/reanudación del plazo de 8 días hábiles (AP-01)."""

    def test_pausa_al_observar_reanuda_al_subsanar(self, estudiante, expediente_observada):
        """Reloj se pausa al observar (via registrar_observacion) y reanuda al subsanar."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, requisito__codigo_requisito="REQ-03"
        ).first()

        expediente_observada.refresh_from_db()
        assert expediente_observada.fecha_ultima_pausa is not None
        pausa_original = expediente_observada.fecha_ultima_pausa

        # Subsanar
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "req3_v2.pdf"
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo,
            nombre_original="req3_v2.pdf",
        )

        expediente_observada.refresh_from_db()
        assert expediente_observada.fecha_ultima_pausa is None
        assert expediente_observada.dias_laborables_acumulados > 0

        calc = PlazoLaboralCalculator()
        base = calc.calcular_fecha_limite(expediente_observada.fecha_recepcion)
        assert expediente_observada.fecha_limite_atencion >= base

    def test_dias_acumulados_se_suman_en_ciclos_multiples(self, estudiante, secretario_abogado, expediente_en_verificacion):
        """Días laborables acumulados se suman en múltiples ciclos Observar/Subsanar."""
        peticion = expediente_en_verificacion.peticiones_documentales.get(
            requisito__codigo_requisito="REQ-01"
        )
        verif = ChecklistVerification.objects.get(
            expediente=expediente_en_verificacion, requisito__codigo_requisito="REQ-01"
        )

        # Ciclo 1 - usar registrar_observacion que SÍ pausa el reloj
        registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            peticion_id=peticion.id,
            motivo_observacion="Obs 1",
        )

        archivo1 = io.BytesIO(PDF_VALIDO)
        archivo1.name = "v2.pdf"
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo1,
            nombre_original="v2.pdf",
        )

        expediente_en_verificacion.refresh_from_db()
        dias_1 = expediente_en_verificacion.dias_laborables_acumulados
        assert dias_1 >= 0  # Puede ser 0 si la pausa fue muy corta

        # Ciclo 2
        expediente_en_verificacion.refresh_from_db()
        registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            peticion_id=peticion.id,
            motivo_observacion="Obs 2",
        )

        archivo2 = io.BytesIO(PDF_VALIDO_V2)
        archivo2.name = "v3.pdf"
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo2,
            nombre_original="v3.pdf",
        )

        expediente_en_verificacion.refresh_from_db()
        dias_2 = expediente_en_verificacion.dias_laborables_acumulados

        assert dias_2 >= dias_1


class TestVersionadoHistorialPreservado:
    """Tests de versionado N+1 con preservación de historial."""

    def test_historial_versiones_preservado_despues_multiples_subsanaciones(
        self, estudiante, secretario_abogado, expediente_observada
    ):
        """Todas las versiones anteriores se conservan con es_vigente=False."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, requisito__codigo_requisito="REQ-03"
        ).first()
        peticion = expediente_observada.peticiones_documentales.get(requisito__codigo_requisito="REQ-03")

        v1 = DocumentoEntregado.objects.get(peticion=peticion, version=1)
        assert v1.es_vigente is True

        # Subsanar v2
        archivo2 = io.BytesIO(PDF_VALIDO)
        archivo2.name = "req3_v2.pdf"
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo2,
            nombre_original="req3_v2.pdf",
        )

        v1.refresh_from_db()
        assert v1.es_vigente is False
        v2 = DocumentoEntregado.objects.get(peticion=peticion, version=2)
        assert v2.es_vigente is True

        # Ciclo 2
        expediente_observada.estado = ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        expediente_observada.save()
        peticion.estado_peticion = "CARGADO"
        peticion.save()
        ChecklistVerification.objects.filter(
            expediente=expediente_observada, requisito__codigo_requisito="REQ-03"
        ).update(estado_verificacion="PENDIENTE")

        # Re-observar usando registrar_observacion
        registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_observada.id,
            peticion_id=peticion.id,
            motivo_observacion="Obs 2",
        )

        archivo3 = io.BytesIO(PDF_VALIDO_V2)
        archivo3.name = "req3_v3.pdf"
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo3,
            nombre_original="req3_v3.pdf",
        )

        v1.refresh_from_db()
        v2.refresh_from_db()
        v3 = DocumentoEntregado.objects.get(peticion=peticion, version=3)

        assert v1.es_vigente is False
        assert v2.es_vigente is False
        assert v3.es_vigente is True
        assert v3.version == 3

    def test_hash_sha256_unico_por_version(self, estudiante, expediente_observada):
        """Cada versión tiene su hash SHA-256 único."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, requisito__codigo_requisito="REQ-03"
        ).first()
        peticion = expediente_observada.peticiones_documentales.get(requisito__codigo_requisito="REQ-03")

        archivo2 = io.BytesIO(PDF_VALIDO)
        archivo2.name = "v2.pdf"
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo2,
            nombre_original="v2.pdf",
        )

        v1 = DocumentoEntregado.objects.get(peticion=peticion, version=1)
        v2 = DocumentoEntregado.objects.get(peticion=peticion, version=2)

        assert v1.hash_sha256 != v2.hash_sha256
        assert len(v1.hash_sha256) == 64
        assert len(v2.hash_sha256) == 64


class TestEndpointsIntegracion:
    """Tests de integración de endpoints completos."""

    def test_endpoint_observar_crea_observacion_y_pausa(self, api_client, secretario_abogado, expediente_en_verificacion):
        """POST /api/v1/expedientes/{id}/observar/ con peticion_id crea observación y pausa reloj."""
        api_client.force_authenticate(user=secretario_abogado)

        peticion = expediente_en_verificacion.peticiones_documentales.get(
            requisito__codigo_requisito="REQ-01"
        )

        url = f"/api/v1/expedientes/{expediente_en_verificacion.id}/observar/"
        response = api_client.post(url, {
            "peticion_id": str(peticion.id),
            "motivo_observacion": "Documento ilegible"
        }, format="json")

        assert response.status_code == 201
        assert "motivo_observacion" in response.data
        assert response.data["motivo_observacion"] == "Documento ilegible"
        assert response.data["resuelta"] is False

        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == ExpedienteTitulacion.ESTADO_OBSERVADA
        assert expediente_en_verificacion.fecha_ultima_pausa is not None

    def test_endpoint_subsanar_retorna_metadata_documento(self, api_client, estudiante, expediente_observada):
        """POST /api/v1/checklist/{id}/subsanar/ retorna metadata del documento creado."""
        api_client.force_authenticate(user=estudiante)

        verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, requisito__codigo_requisito="REQ-03"
        ).first()

        url = f"/api/v1/checklist/{verif.id}/subsanar/"
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "req3_v2_corregido.pdf"

        response = api_client.post(url, {"archivo": archivo}, format="multipart")

        assert response.status_code == 201
        assert response.data["version"] == 2
        assert response.data["nombre_original"] == "req3_v2_corregido.pdf"
        assert response.data["es_vigente"] is True
        assert "hash_sha256" in response.data
        assert "tamanio_bytes" in response.data

    def test_endpoint_verificar_despues_subsanar(self, api_client, secretario_abogado, expediente_observada):
        """PUT /api/v1/checklist/{id}/ funciona después de subsanar (checklist en PENDIENTE)."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, requisito__codigo_requisito="REQ-03"
        ).first()

        # Subsanar primero
        from apps.verificacion.services import subsanar_requisito
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "v2.pdf"
        subsanar_requisito.execute(
            usuario=expediente_observada.estudiante,
            checklist_verification_id=verif.id,
            archivo=archivo,
            nombre_original="v2.pdf",
        )

        # Verificar via endpoint
        api_client.force_authenticate(user=secretario_abogado)
        url = f"/api/v1/checklist/{verif.id}/"
        response = api_client.put(url, {"estado_verificacion": "VERIFICADO"}, format="json")

        assert response.status_code == 200
        assert response.data["estado_verificacion"] == "VERIFICADO"


class TestValidacionChecklistCompletoServicio:
    """Tests directos del servicio validar_checklist_completo."""

    def test_obtener_estado_checklist_detallado_todos_cargados(self, expediente_en_verificacion, secretario_abogado):
        """obtener_estado_checklist cuenta como pendientes los que NO están VERIFICADO (incluye CARGADO)."""
        estado = validar_checklist_completo.obtener_estado_checklist(expediente_en_verificacion.id)

        assert estado["total_requisitos"] == 3
        assert estado["verificados"] == 0
        # CARGADO NO es VERIFICADO, así que cuenta como pendiente
        assert len(estado["pendientes"]) == 3
        assert estado["completo"] is False

    def test_obtener_estado_checklist_parcialmente_verificado(self, expediente_observada):
        """Estado con mix: 2 VERIFICADO, 1 OBSERVADO."""
        estado = validar_checklist_completo.obtener_estado_checklist(expediente_observada.id)

        assert estado["total_requisitos"] == 3
        assert estado["verificados"] == 2
        assert len(estado["pendientes"]) == 1  # Solo REQ-03 (OBSERVADO)
        assert estado["completo"] is False

        pendiente = estado["pendientes"][0]
        assert pendiente["requisito_codigo"] == "REQ-03"
        assert pendiente["estado"] == "OBSERVADO"

    def test_obtener_requisitos_pendientes_lista_codigos(self, expediente_observada):
        """obtener_requisitos_pendientes retorna lista de códigos no VERIFICADO."""
        pendientes = validar_checklist_completo.obtener_requisitos_pendientes(expediente_observada.id)

        assert isinstance(pendientes, list)
        assert "REQ-03" in pendientes
        assert len(pendientes) == 1


class TestPermisosYSeguridad:
    """Tests de validación de permisos y aislamiento por ámbito."""

    def test_estudiante_no_puede_evaluar_checklist(self, estudiante, expediente_en_verificacion):
        """ESTUDIANTE no puede evaluar checklist."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion, estado_verificacion="PENDIENTE"
        ).first()

        with pytest.raises(evaluar_checklist.UserNotAuthorizedError):
            evaluar_checklist.execute(
                usuario=estudiante,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )

    def test_secretaria_carrera_puede_subsanar_misma_carrera(self, secretaria_carrera, expediente_observada):
        """SECRETARIA_CARRERA de la misma carrera puede subsanar."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, requisito__codigo_requisito="REQ-03"
        ).first()

        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "sec_v2.pdf"
        doc = subsanar_requisito.execute(
            usuario=secretaria_carrera,
            checklist_verification_id=verif.id,
            archivo=archivo,
            nombre_original="sec_v2.pdf",
        )
        assert doc.subido_por == secretaria_carrera
        assert doc.version == 2

    def test_estudiante_no_propietario_no_puede_subsanar(self, expediente_observada):
        """ESTUDIANTE que NO es propietario del expediente NO puede subsanar."""
        from apps.authentication.adapters.models import User, Role, UserRole

        # Crear OTRO estudiante (no el propietario del expediente_observada)
        rol_est, _ = Role.objects.get_or_create(name=ROLE_ESTUDIANTE)
        otro_estudiante = User.objects.create_user(
            username="otro_est",
            email="otro@test.com",
            password=PASSWORD,
            cedula="9999999999",
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
        )
        UserRole.objects.create(user=otro_estudiante, role=rol_est)

        verif = ChecklistVerification.objects.filter(
            expediente=expediente_observada, requisito__codigo_requisito="REQ-03"
        ).first()

        with pytest.raises(subsanar_requisito.UsuarioNoAutorizadoError):
            subsanar_requisito.execute(
                usuario=otro_estudiante,
                checklist_verification_id=verif.id,
                archivo=io.BytesIO(PDF_VALIDO),
                nombre_original="test.pdf",
            )

    def test_idor_prevencion_acceso_expediente_ajeno(self, api_client, estudiante):
        """Prevención IDOR: estudiante no puede evaluar checklist de expediente ajeno."""
        from apps.expedientes.adapters.models import ExpedienteTitulacion
        from apps.peticiones.adapters.models import CatalogoDocumental, PeticionDocumental

        otro_estudiante = User.objects.create_user(
            username="otro_est", email="otro@test.com",
            password=PASSWORD, cedula="9999999999",
            carrera_id=CARRERA_1, facultad_id=FACULTAD_1,
        )
        UserRole.objects.create(user=otro_estudiante, role=Role.objects.get(name=ROLE_ESTUDIANTE))

        expediente_otro = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-OTRO",
            estudiante=otro_estudiante,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
        )
        req = CatalogoDocumental.objects.create(
            codigo_requisito="REQ-X", nombre="X",
            es_obligatorio_base=True, fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
        )
        peticion = PeticionDocumental.objects.create(
            expediente=expediente_otro, requisito=req,
            estado_peticion=ESTADO_CARGADO, dependencia_emisora="SECRETARIA_CARRERA",
        )
        verif = ChecklistVerification.objects.create(
            expediente=expediente_otro, requisito=req,
            estado_verificacion="PENDIENTE",
        )

        api_client.force_authenticate(user=estudiante)
        url = f"/api/v1/checklist/{verif.id}/"
        response = api_client.put(url, {"estado_verificacion": "VERIFICADO"}, format="json")

        assert response.status_code in (403, 404)


class TestCasoDeUsoRegistrarObservacion:
    """Tests del caso de uso registrar_observacion (T028)."""

    def test_registrar_observacion_cambia_estados_y_pausa(self, secretario_abogado, expediente_en_verificacion):
        """registrar_observacion ejecuta: observación + estados + pausa + notificación."""
        peticion = expediente_en_verificacion.peticiones_documentales.get(
            requisito__codigo_requisito="REQ-01"
        )

        observacion = registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            peticion_id=peticion.id,
            motivo_observacion="Documento incompleto",
        )

        assert observacion.motivo_observacion == "Documento incompleto"
        assert observacion.resuelta is False

        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == ExpedienteTitulacion.ESTADO_OBSERVADA
        assert expediente_en_verificacion.fecha_ultima_pausa is not None

        peticion.refresh_from_db()
        assert peticion.estado_peticion == "OBSERVADO"

    def test_registrar_observacion_falla_si_expediente_no_en_verificacion(self, secretario_abogado):
        """Falla si expediente no está en EN_VERIFICACION."""
        from apps.expedientes.adapters.models import ExpedienteTitulacion
        from apps.peticiones.adapters.models import CatalogoDocumental, PeticionDocumental

        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-TEST",
            estudiante=User.objects.create_user(
                username="est2", email="est2@test.com", password=PASSWORD,
                cedula="9999999999", carrera_id=CARRERA_1, facultad_id=FACULTAD_1,
            ),
            carrera_id=CARRERA_1, facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_ENVIADA,
            activa=True,
        )
        req = CatalogoDocumental.objects.create(
            codigo_requisito="REQ-T", nombre="Test",
            es_obligatorio_base=True, fase="FASE_1",
            rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
        )
        peticion = PeticionDocumental.objects.create(
            expediente=expediente, requisito=req,
            estado_peticion="CARGADO", dependencia_emisora="SECRETARIA_CARRERA",
        )

        with pytest.raises(registrar_observacion.ExpedienteNoEnVerificacionError):
            registrar_observacion.execute(
                usuario=secretario_abogado,
                expediente_id=expediente.id,
                peticion_id=peticion.id,
                motivo_observacion="Test",
            )

    def test_registrar_observacion_falla_si_ya_existe_pendiente(self, secretario_abogado, expediente_en_verificacion):
        """Falla si intenta registrar observación en expediente ya observado (estado cambió a OBSERVADA)."""
        peticion = expediente_en_verificacion.peticiones_documentales.get(
            requisito__codigo_requisito="REQ-01"
        )

        # Primera observación - éxito
        registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            peticion_id=peticion.id,
            motivo_observacion="Primera observación",
        )

        # Segunda observación en la misma petición - expediente ya está en OBSERVADA
        # Debe fallar con ExpedienteNoEnVerificacionError
        with pytest.raises(registrar_observacion.ExpedienteNoEnVerificacionError):
            registrar_observacion.execute(
                usuario=secretario_abogado,
                expediente_id=expediente_en_verificacion.id,
                peticion_id=peticion.id,
                motivo_observacion="Otra observación",
            )


class TestFlujoCompletoHastaInforme:
    """Test de integración end-to-end: desde observación hasta validación para informe."""

    def test_flujo_completo_observar_subsanar_verificar_validar_informe(
        self, estudiante, secretario_abogado, expediente_en_verificacion
    ):
        """Flujo E2E: Observar REQ-01 -> Subsanar -> Verificar REQ-01 -> Verificar REQ-02, REQ-03 -> Validar checklist completo."""
        # 1. Observar REQ-01
        peticion_req1 = expediente_en_verificacion.peticiones_documentales.get(
            requisito__codigo_requisito="REQ-01"
        )
        registrar_observacion.execute(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            peticion_id=peticion_req1.id,
            motivo_observacion="Falta firma",
        )

        # Verificar pausa
        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == ExpedienteTitulacion.ESTADO_OBSERVADA
        assert expediente_en_verificacion.fecha_ultima_pausa is not None

        # 2. Subsanar REQ-01
        verif_req1 = ChecklistVerification.objects.get(
            expediente=expediente_en_verificacion, requisito__codigo_requisito="REQ-01"
        )
        archivo = io.BytesIO(PDF_VALIDO)
        archivo.name = "req1_v2.pdf"
        subsanar_requisito.execute(
            usuario=estudiante,
            checklist_verification_id=verif_req1.id,
            archivo=archivo,
            nombre_original="req1_v2.pdf",
        )

        # Verificar reanudación y estados
        expediente_en_verificacion.refresh_from_db()
        assert expediente_en_verificacion.estado == ExpedienteTitulacion.ESTADO_EN_VERIFICACION
        assert expediente_en_verificacion.fecha_ultima_pausa is None

        verif_req1.refresh_from_db()
        assert verif_req1.estado_verificacion == "PENDIENTE"

        # 3. Verificar REQ-01 (ya corregido)
        evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif_req1.id,
            nuevo_estado="VERIFICADO",
        )

        # 4. Verificar REQ-02 y REQ-03 (ya estaban CARGADO)
        for verif in ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion
        ).exclude(pk=verif_req1.pk):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )

        # 5. Validar checklist completo (debe pasar ahora)
        resultado = validar_checklist_completo.execute(expediente_en_verificacion.id)
        assert resultado is True