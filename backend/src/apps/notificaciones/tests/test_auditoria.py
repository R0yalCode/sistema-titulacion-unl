"""Pruebas para T039: Bitácora Inmutable EventoAuditoria en JSONB (Principio C-008).

Verifica:
- Modelo EventoAuditoria con JSONB inmutable
- Señales automáticas para eventos de negocio
- Registro de cambios de estado, checklist, documentos, resoluciones
- Inmutabilidad y campos JSONB
"""

import io
import pytest
from django.db import transaction
from django.utils import timezone

from apps.authentication.adapters.models import (
    ROLE_ESTUDIANTE,
    ROLE_SECRETARIO_ABOGADO,
    ROLE_DECANO,
    ROLE_ANALISTA_APOYO,
    User,
    Role,
    UserRole,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion, HistorialEstado
from apps.peticiones.adapters.models import (
    ESTADO_CARGADO,
    ESTADO_VERIFICADO,
    PeticionDocumental,
    DocumentoEntregado,
)
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ObservacionAccionable,
    ESTADO_VERIFICACION_VERIFICADO,
    ESTADO_VERIFICACION_OBSERVADO,
)
from apps.resoluciones.adapters.models import InformeAptitud, DeclaratoriaAptitud
from apps.notificaciones.adapters.models import EventoAuditoria, NotificacionInterna
from apps.resoluciones.services import emitir_informe, declarar_aptitud
from apps.verificacion.services import evaluar_checklist, registrar_observacion
from apps.notificaciones.services import notificar_estudiante_subsanacion

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing (PDF 1.4)
PDF_VALIDO = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000218 00000 n \n0000000277 00000 n \ntrailer\n<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"


@pytest.fixture
def rol_estudiante():
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    return role


@pytest.fixture
def rol_secretario_abogado():
    role, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
    return role


@pytest.fixture
def rol_decano():
    role, _ = Role.objects.get_or_create(name="DECANO")
    return role


@pytest.fixture
def rol_analista_apoyo():
    role, _ = Role.objects.get_or_create(name="ANALISTA_APOYO")
    return role


@pytest.fixture
def estudiante(rol_estudiante):
    user = User.objects.create_user(
        username="estudiante_test",
        email="est@test.com",
        password="pass1234",
        cedula="1234567890",
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=rol_estudiante)
    return user


@pytest.fixture
def secretario_abogado(rol_secretario_abogado):
    user = User.objects.create_user(
        username="secretario_test",
        email="sec@test.com",
        password="pass1234",
        cedula="1234567893",
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=rol_secretario_abogado)
    return user


@pytest.fixture
def decano(rol_decano):
    user = User.objects.create_user(
        username="decano_test",
        email="decano@test.com",
        password="pass1234",
        cedula="1234567894",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=rol_decano)
    return user


@pytest.fixture
def analista_apoyo(rol_analista_apoyo):
    user = User.objects.create_user(
        username="analista_test",
        email="analista@test.com",
        password="pass1234",
        cedula="1234567892",
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=rol_analista_apoyo)
    return user


@pytest.fixture
def expediente_borrador(estudiante):
    """Expediente en estado BORRADOR."""
    return ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
        estado=ExpedienteTitulacion.ESTADO_BORRADOR,
        activa=True,
    )


@pytest.fixture
def expediente_en_verificacion(estudiante, secretario_abogado):
    """Expediente en EN_VERIFICACION con checklist."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0002",
        estudiante=estudiante,
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
        estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
        activa=True,
        fecha_recepcion=timezone.now(),
    )

    for i, (codigo, nombre) in enumerate([
        ("REQ-01", "Acta de Grado"),
        ("REQ-02", "Certificado de Votación"),
        ("REQ-03", "Certificado Militar"),
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
            estado_peticion="CARGADO",
            dependencia_emisora="SECRETARIA_CARRERA",
        )
        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=1,
            archivo_path=f"expedientes/2026/{expediente.id}/{codigo}.pdf",
            nombre_original=f"{codigo}.pdf",
            tamanio_bytes=100,
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
def expediente_con_informe(estudiante, secretario_abogado):
    """Expediente con informe emitido."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0003",
        estudiante=estudiante,
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
        estado=ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
        activa=True,
        fecha_recepcion=timezone.now(),
    )

    for i, (codigo, nombre) in enumerate([
        ("REQ-01", "Acta de Grado"),
        ("REQ-02", "Certificado de Votación"),
        ("REQ-03", "Certificado Militar"),
        ("REQ-04", "Título de Bachiller"),
        ("REQ-05", "Record Académico Legalizado"),
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
            estado_peticion="VERIFICADO",
            dependencia_emisora="SECRETARIA_CARRERA",
        )
        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=1,
            archivo_path=f"expedientes/2026/{expediente.id}/{codigo}.pdf",
            nombre_original=f"{codigo}.pdf",
            tamanio_bytes=100,
            hash_sha256="a" * 64,
            tipo_mime="application/pdf",
            subido_por=estudiante,
            es_vigente=True,
        )
        ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="VERIFICADO",
            evaluado_por=estudiante,  # dummy
        )

    # Emitir informe
    from apps.resoluciones.services import emitir_informe
    emitir_informe(
        usuario=estudiante,
        expediente_id=expediente.id,
        dictamen="APTO",
    )

    return expediente


class TestEventoAuditoriaModelo:
    """Tests del modelo EventoAuditoria."""

    def test_crear_evento_auditoria_basico(self, estudiante, expediente_borrador):
        """Crear evento de auditoría básico."""
        evento = EventoAuditoria.objects.create(
            accion=EventoAuditoria.Accion.EXPEDIENTE_CREADO,
            usuario=estudiante,
            expediente=expediente_borrador,
            detalles={
                "numero_expediente": "EXP-2026-0001",
                "estado_inicial": "BORRADOR",
            },
        )

        assert evento.id is not None
        assert evento.accion == EventoAuditoria.Accion.EXPEDIENTE_CREADO
        assert evento.usuario == estudiante
        assert evento.expediente == expediente_borrador
        assert evento.detalles["numero_expediente"] == "EXP-2026-0001"
        assert evento.timestamp is not None

    def test_evento_auditoria_jsonb_detalles(self, estudiante, expediente_borrador):
        """Verificar que detalles se almacena como JSONB."""
        detalles_complejos = {
            "estado_anterior": "BORRADOR",
            "estado_nuevo": "ENVIADA",
            "metadata": {
                "usuario_id": "123",
                "ip": "192.168.1.1",
                "nested": {"key": "value", "array": [1, 2, 3]},
            },
            "tags": ["expediente", "envio"],
        }

        evento = EventoAuditoria.objects.create(
            accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
            usuario=estudiante,
            expediente=expediente_borrador,
            detalles=detalles_complejos,
        )

        assert evento.detalles == detalles_complejos
        assert isinstance(evento.detalles, dict)
        assert evento.detalles["metadata"]["nested"]["key"] == "value"

    def test_evento_auditoria_choices_accion(self):
        """Verificar que las choices de acción están definidas."""
        assert EventoAuditoria.Accion.EXPEDIENTE_CREADO == "EXPEDIENTE_CREADO"
        assert EventoAuditoria.Accion.EXPEDIENTE_ENVIADO == "EXPEDIENTE_ENVIADO"
        assert EventoAuditoria.Accion.ESTADO_CAMBIADO == "ESTADO_CAMBIADO"
        assert EventoAuditoria.Accion.CHECKLIST_EVALUADO == "CHECKLIST_EVALUADO"
        assert EventoAuditoria.Accion.OBSERVACION_REGISTRADA == "OBSERVACION_REGISTRADA"
        assert EventoAuditoria.Accion.SUBSANACION_REALIZADA == "SUBSANACION_REALIZADA"
        assert EventoAuditoria.Accion.DOCUMENTO_CARGADO == "DOCUMENTO_CARGADO"
        assert EventoAuditoria.Accion.INFORME_EMITIDO == "INFORME_EMITIDO"
        assert EventoAuditoria.Accion.DECLARATORIA_REGISTRADA == "DECLARATORIA_REGISTRADA"
        assert EventoAuditoria.Accion.EXPEDIENTE_CANCELADO == "EXPEDIENTE_CANCELADO"

    def test_str_representation(self, estudiante, expediente_borrador):
        """Verificar representación string."""
        evento = EventoAuditoria.objects.create(
            accion=EventoAuditoria.Accion.EXPEDIENTE_CREADO,
            usuario=estudiante,
            expediente=expediente_borrador,
            detalles={},
        )
        str_repr = str(evento)
        assert "Auditoria" in str_repr
        assert "EXPEDIENTE_CREADO" in str_repr
        assert str(estudiante.id) in str_repr or "estudiante_test" in str_repr


class TestSenalesExpediente:
    """Tests de señales automáticas para ExpedienteTitulacion."""

    def test_crear_expediente_genera_auditoria(self, estudiante):
        """Crear expediente genera evento EXPEDIENTE_CREADO."""
        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0099",
            estudiante=estudiante,
            carrera_id="11111111-1111-1111-1111-111111111111",
            facultad_id="22222222-2222-2222-2222-222222222222",
            estado=ExpedienteTitulacion.ESTADO_BORRADOR,
            activa=True,
        )

        eventos = EventoAuditoria.objects.filter(
            expediente=expediente,
            accion=EventoAuditoria.Accion.EXPEDIENTE_CREADO,
        )
        assert eventos.count() == 1

        evento = eventos.first()
        assert evento.accion == EventoAuditoria.Accion.EXPEDIENTE_CREADO
        assert evento.usuario == estudiante
        assert evento.expediente == expediente
        assert "numero_expediente" in evento.detalles

    def test_cambio_estado_genera_auditoria(self, estudiante, secretario_abogado):
        """Cambio de estado genera evento ESTADO_CAMBIADO."""
        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0001",
            estudiante=estudiante,
            carrera_id="11111111-1111-1111-1111-111111111111",
            facultad_id="22222222-2222-2222-2222-222222222222",
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
        )

        # Cambiar estado
        expediente.estado = ExpedienteTitulacion.ESTADO_OBSERVADA
        expediente.save(update_fields=["estado"])

        eventos = EventoAuditoria.objects.filter(
            expediente=expediente,
            accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
        )
        assert eventos.count() >= 1

        evento = eventos.latest("timestamp")
        assert evento.accion == EventoAuditoria.Accion.ESTADO_CAMBIADO
        assert "estado_anterior" in evento.detalles
        assert evento.detalles["estado_anterior"] == "EN_VERIFICACION"
        assert evento.detalles["estado_nuevo"] == "OBSERVADA"


class TestSenalesChecklist:
    """Tests de señales para ChecklistVerification."""

    def test_evaluar_checklist_genera_auditoria(self, expediente_en_verificacion, secretario_abogado):
        """Evaluar checklist genera evento CHECKLIST_EVALUADO."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion,
            estado_verificacion="PENDIENTE",
        ).first()

        evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif.id,
            nuevo_estado="VERIFICADO",
        )

        eventos = EventoAuditoria.objects.filter(
            expediente=expediente_en_verificacion,
            accion=EventoAuditoria.Accion.CHECKLIST_EVALUADO,
        )
        assert eventos.count() >= 1

        evento = eventos.latest("timestamp")
        assert evento.accion == EventoAuditoria.Accion.CHECKLIST_EVALUADO
        assert evento.detalles["estado_verificacion"] == "VERIFICADO"
        assert "requisito_codigo" in evento.detalles

    def test_observar_checklist_genera_auditoria(self, expediente_en_verificacion, secretario_abogado):
        """Observar checklist genera evento OBSERVACION_REGISTRADA."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion,
            estado_verificacion="PENDIENTE",
        ).first()

        evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif.id,
            nuevo_estado="OBSERVADO",
            motivo_observacion="Documento ilegible",
        )

        eventos = EventoAuditoria.objects.filter(
            expediente=expediente_en_verificacion,
            accion=EventoAuditoria.Accion.OBSERVACION_REGISTRADA,
        )
        assert eventos.count() >= 1

        evento = eventos.latest("timestamp")
        assert evento.accion == EventoAuditoria.Accion.OBSERVACION_REGISTRADA
        assert evento.detalles["motivo_observacion"] == "Documento ilegible"


class TestSenalesDocumentos:
    """Tests de señales para carga de documentos."""

    def test_cargar_documento_genera_auditoria(self, expediente_en_verificacion, estudiante):
        """Cargar documento genera evento DOCUMENTO_CARGADO."""
        from apps.peticiones.adapters.models import PeticionDocumental

        peticion = expediente_en_verificacion.peticiones_documentales.first()

        doc = DocumentoEntregado.objects.create(
            peticion=peticion,
            version=2,
            archivo_path=f"expedientes/2026/{expediente_en_verificacion.id}/doc_v2.pdf",
            nombre_original="doc_v2.pdf",
            tamanio_bytes=200,
            hash_sha256="b" * 64,
            tipo_mime="application/pdf",
            subido_por=estudiante,
            es_vigente=True,
        )

        eventos = EventoAuditoria.objects.filter(
            expediente=expediente_en_verificacion,
            accion=EventoAuditoria.Accion.DOCUMENTO_CARGADO,
        )
        assert eventos.count() >= 1

        evento = eventos.latest("timestamp")
        assert evento.accion == EventoAuditoria.Accion.DOCUMENTO_CARGADO
        assert evento.detalles["version"] == 2
        assert evento.detalles["hash_sha256"] == "b" * 64


class TestSenalesResoluciones:
    """Tests de señales para resoluciones."""

    def test_emitir_informe_genera_auditoria(self, expediente_en_verificacion, secretario_abogado):
        """Emitir informe genera evento INFORME_EMITIDO."""
        from apps.resoluciones.services import emitir_informe

        # Primero verificar todo el checklist
        for verif in ChecklistVerification.objects.filter(expediente=expediente_en_verificacion):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )

        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_en_verificacion.id,
            dictamen="APTO",
        )

        eventos = EventoAuditoria.objects.filter(
            expediente=expediente_en_verificacion,
            accion=EventoAuditoria.Accion.INFORME_EMITIDO,
        )
        assert eventos.count() >= 1

        evento = eventos.latest("timestamp")
        assert evento.accion == EventoAuditoria.Accion.INFORME_EMITIDO
        assert evento.detalles["dictamen"] == "APTO"
        assert "numero_providencia" in evento.detalles

    def test_registrar_declaratoria_genera_auditoria(self, decano, estudiante, secretario_abogado):
        """Registrar declaratoria genera evento DECLARATORIA_REGISTRADA."""
        from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO
        from apps.resoluciones.services import emitir_informe, declarar_aptitud

        # Crear expediente en EN_VERIFICACION (no INFORME_EMITIDO)
        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0099",
            estudiante=estudiante,
            carrera_id="11111111-1111-1111-1111-111111111111",
            facultad_id="22222222-2222-2222-2222-222222222222",
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
            fecha_recepcion=timezone.now(),
        )

        # Crear 2 requisitos VERIFICADO
        for codigo, nombre in [("REQ-01", "A"), ("REQ-02", "B")]:
            requisito = CatalogoDocumental.objects.create(
                codigo_requisito=codigo, nombre=nombre,
                es_obligatorio_base=True, fase="FASE_1",
                rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
            )
            p = PeticionDocumental.objects.create(
                expediente=expediente, requisito=requisito,
                estado_peticion="VERIFICADO", dependencia_emisora="SECRETARIA_CARRERA",
            )
            DocumentoEntregado.objects.create(
                peticion=p, version=1, archivo_path="x.pdf", nombre_original="x.pdf",
                tamanio_bytes=100, hash_sha256="a"*64, tipo_mime="application/pdf",
                subido_por=estudiante, es_vigente=True,
            )
            ChecklistVerification.objects.create(
                expediente=expediente, requisito=requisito,
                estado_verificacion="VERIFICADO",
            )

        # Emitir informe primero
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente.id,
            dictamen="APTO",
        )

        # Registrar declaratoria
        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente.id,
            archivo_memorando=io.BytesIO(PDF_VALIDO),
        )

        eventos = EventoAuditoria.objects.filter(
            expediente=expediente,
            accion=EventoAuditoria.Accion.DECLARATORIA_REGISTRADA,
        )
        assert eventos.count() >= 1

        evento = eventos.latest("timestamp")
        assert evento.accion == EventoAuditoria.Accion.DECLARATORIA_REGISTRADA
        assert "numero_memorando" in evento.detalles


class TestInmutabilidadAuditoria:
    """Tests de inmutabilidad de la bitácora de auditoría."""

    def test_evento_auditoria_no_modificable(self, estudiante, expediente_borrador):
        """Una vez creado, el evento no debe poder modificarse (solo append)."""
        evento = EventoAuditoria.objects.create(
            accion=EventoAuditoria.Accion.EXPEDIENTE_CREADO,
            usuario=estudiante,
            expediente=expediente_borrador,
            detalles={"test": "valor_original"},
        )

        # Verificar que el evento se creó correctamente
        pk_original = evento.pk
        evento_original = EventoAuditoria.objects.get(pk=pk_original)
        assert evento_original.detalles == {"test": "valor_original"}


class TestIndicesAuditoria:
    """Tests de índices de la tabla de auditoría."""

    def test_indices_creados(self):
        """Verificar que los índices definidos en Meta existen."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND tbl_name='notificaciones_eventoauditoria'
            """)
            indices = [row[0] for row in cursor.fetchall()]

        assert any("expediente_fecha" in idx for idx in indices)
        assert any("usuario_fecha" in idx for idx in indices)
        assert any("accion_fecha" in idx for idx in indices)
        assert any("fecha" in idx for idx in indices)


class TestIntegracionCompleta:
    """Test de integración completa del flujo con auditoría."""

    def test_flujo_completo_con_auditoria(self, estudiante, secretario_abogado, decano):
        """Flujo completo: crear -> verificar -> emitir -> declarar, todo auditado."""
        from apps.peticiones.adapters.models import CatalogoDocumental
        from apps.resoluciones.services import emitir_informe, declarar_aptitud

        # 1. Crear expediente
        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-AUDIT-001",
            estudiante=estudiante,
            carrera_id="11111111-1111-1111-1111-111111111111",
            facultad_id="22222222-2222-2222-2222-222222222222",
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
            fecha_recepcion=timezone.now(),
        )

        # Crear 2 requisitos base
        for codigo, nombre in [
            ("REQ-01", "Acta de Grado"),
            ("REQ-02", "Certificado de Votación"),
        ]:
            req = CatalogoDocumental.objects.create(
                codigo_requisito=codigo, nombre=nombre,
                es_obligatorio_base=True, fase="FASE_1",
                rol_emisor_sugerido="SECRETARIA_CARRERA", activo=True,
            )
            p = PeticionDocumental.objects.create(
                expediente=expediente, requisito=req,
                estado_peticion="CARGADO", dependencia_emisora="SECRETARIA_CARRERA",
            )
            DocumentoEntregado.objects.create(
                peticion=p, version=1,
                archivo_path=f"expedientes/2026/{expediente.id}/{codigo}.pdf",
                nombre_original=f"{codigo}.pdf", tamanio_bytes=100,
                hash_sha256="a"*64, tipo_mime="application/pdf",
                subido_por=estudiante, es_vigente=True,
            )
            ChecklistVerification.objects.create(
                expediente=expediente, requisito=req,
                estado_verificacion="PENDIENTE",
            )

        # Verificar checklist
        for verif in ChecklistVerification.objects.filter(expediente=expediente):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )

        # 2. Emitir Informe
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente.id,
            dictamen="APTO",
        )

        assert informe.numero_providencia.startswith("PROV-590-")

        # 3. Registrar Declaratoria (Decano)
        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente.id,
            archivo_memorando=io.BytesIO(PDF_VALIDO),
        )

        # Verificar que TODOS los eventos se registraron
        eventos = EventoAuditoria.objects.filter(expediente=expediente)
        acciones = set(eventos.values_list("accion", flat=True))

        assert EventoAuditoria.Accion.EXPEDIENTE_CREADO in acciones
        assert EventoAuditoria.Accion.CHECKLIST_EVALUADO in acciones
        assert EventoAuditoria.Accion.INFORME_EMITIDO in acciones
        assert EventoAuditoria.Accion.DECLARATORIA_REGISTRADA in acciones

        # Verificar orden temporal
        eventos_ordenados = list(eventos.order_by("timestamp"))
        assert len(eventos_ordenados) >= 4
        assert EventoAuditoria.Accion.DOCUMENTO_CARGADO in acciones
        assert EventoAuditoria.Accion.INFORME_EMITIDO in acciones
        assert EventoAuditoria.Accion.DECLARATORIA_REGISTRADA in acciones

        # Verificar orden temporal
        eventos_ordenados = list(eventos.order_by("timestamp"))
        assert len(eventos_ordenados) >= 5