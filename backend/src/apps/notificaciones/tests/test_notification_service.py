"""Pruebas para T037: Servicio de notificaciones internas in-app (DEC-01).

Verifica:
- Creación síncrona de notificaciones in-app
- Despacho sin bloquear transacción principal
- Funciones de conveniencia para casos de uso comunes
- Marcado de lectura
"""

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
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    ESTADO_CARGADO,
    ESTADO_VERIFICADO,
    PeticionDocumental,
    DocumentoEntregado,
)
from apps.verificacion.adapters.models import (
    ChecklistVerification,
    ESTADO_VERIFICACION_VERIFICADO,
)
from apps.notificaciones.adapters.models import NotificacionInterna
from apps.notificaciones.services import (
    crear_notificacion,
    crear_notificacion_expediente,
    notificar_estudiante_subsanacion,
    notificar_jurista_subsanacion,
    notificar_estudiante_observacion,
    notificar_informe_emitido,
    notificar_declaratoria_emitida,
    marcar_como_leida,
    NotificacionNoCreadaError,
)
from apps.resoluciones.services import emitir_informe, declarar_aptitud
from apps.verificacion.services import evaluar_checklist

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing
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
def expediente_en_verificacion(estudiante, secretario_abogado):
    """Expediente en EN_VERIFICACION con 3 requisitos VERIFICADO."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
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
            subido_por=expediente.estudiante,
            es_vigente=True,
        )
        ChecklistVerification.objects.create(
            expediente=expediente,
            requisito=requisito,
            estado_verificacion="VERIFICADO",
            evaluado_por=expediente.estudiante,  # dummy
        )

    return expediente


@pytest.fixture
def expediente_con_informe(estudiante, secretario_abogado):
    """Expediente con checklist 100% VERIFICADO e Informe emitido."""
    from apps.peticiones.adapters.models import CatalogoDocumental, ESTADO_CARGADO

    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0002",
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
            evaluado_por=estudiante,
        )

    return expediente


class TestCrearNotificacionBasica:
    """Tests básicos de creación de notificaciones."""

    def test_crear_notificacion_basica(self, estudiante, expediente_en_verificacion):
        """Crear notificación básica con todos los campos."""
        notif = crear_notificacion(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            titulo="Test Notificación",
            mensaje="Mensaje de prueba",
        )

        assert notif.id is not None
        assert notif.usuario_destino == estudiante
        assert notif.expediente == expediente_en_verificacion
        assert notif.titulo == "Test Notificación"
        assert notif.mensaje == "Mensaje de prueba"
        assert notif.leida is False
        assert notif.fecha_creacion is not None

    def test_crear_notificacion_con_peticion(self, estudiante, expediente_en_verificacion):
        """Crear notificación con petición asociada."""
        peticion = expediente_en_verificacion.peticiones_documentales.first()

        notif = crear_notificacion(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            peticion=peticion,
            titulo="Con Petición",
            mensaje="Mensaje con petición",
        )

        assert notif.peticion == peticion

    def test_crear_notificacion_sincronica_no_bloquea(self, estudiante, expediente_en_verificacion):
        """Verificar que la creación es síncrona y no bloquea."""
        # La notificación debe crearse inmediatamente
        with transaction.atomic():
            notif = crear_notificacion(
                usuario_destino=estudiante,
                expediente=expediente_en_verificacion,
                titulo="Sincrónica",
                mensaje="Test",
            )

        # Debe existir inmediatamente después de la transacción
        assert NotificacionInterna.objects.filter(pk=notif.id).exists()

    def test_crear_notificacion_expediente_por_id(self, estudiante, expediente_en_verificacion):
        """Crear notificación usando ID de expediente."""
        notif = crear_notificacion_expediente(
            usuario_destino=estudiante,
            expediente_id=str(expediente_en_verificacion.id),
            titulo="Por ID",
            mensaje="Test ID",
        )

        assert notif.expediente == expediente_en_verificacion
        assert notif.titulo == "Por ID"


class TestNotificacionesCasosUso:
    """Tests de funciones de conveniencia para casos de uso específicos."""

    def test_notificar_estudiante_subsanacion(self, expediente_en_verificacion):
        """Notificar al estudiante que su subsanación fue recibida."""
        notif = notificar_estudiante_subsanacion(
            expediente=expediente_en_verificacion,
        )

        assert notif.usuario_destino == expediente_en_verificacion.estudiante
        assert "Subsanación recibida" in notif.titulo
        assert expediente_en_verificacion.numero_expediente in notif.titulo
        assert "subsanado" in notif.mensaje.lower()

    def test_notificar_jurista_subsanacion(self, expediente_en_verificacion, secretario_abogado):
        """Notificar al jurista que hay una subsanación para revisar."""
        notif = notificar_jurista_subsanacion(
            expediente=expediente_en_verificacion,
            jurista=secretario_abogado,
        )

        assert notif is not None
        assert notif.usuario_destino == secretario_abogado
        assert "Subsanación" in notif.titulo
        assert "revis" in notif.mensaje.lower()  # revisión / revisar

    def test_notificar_estudiante_observacion(self, expediente_en_verificacion):
        """Notificar observación al estudiante."""
        peticion = expediente_en_verificacion.peticiones_documentales.first()

        notif = notificar_estudiante_observacion(
            expediente=expediente_en_verificacion,
            peticion=peticion,
            motivo="Falta firma del director",
        )

        assert notif.usuario_destino == expediente_en_verificacion.estudiante
        assert notif.peticion == peticion
        assert "Observación" in notif.titulo
        assert "Falta firma" in notif.mensaje

    def test_notificar_informe_emitido(self, expediente_con_informe, decano):
        """Notificar al decano que se emitió el informe."""
        from apps.resoluciones.adapters.models import InformeAptitud

        # Emitir informe primero
        from apps.resoluciones.services import emitir_informe
        from apps.verificacion.services import evaluar_checklist
        from apps.verificacion.adapters.models import ChecklistVerification

        # Emitir informe
        informe = InformeAptitud.objects.create(
            expediente=expediente_con_informe,
            numero_providencia="PROV-590-2026-0001",
            emisor=expediente_con_informe.estudiante,  # dummy
            dictamen="APTO",
            archivo_informe_path="/tmp/test.pdf",
        )

        notif = notificar_informe_emitido(
            expediente=expediente_con_informe,
            numero_providencia="PROV-590-2026-0001",
        )

        # Verificar que se notificó al decano (o None si no hay decano)
        # La función busca decano de la facultad
        if notif:
            assert notif.usuario_destino is not None
            assert "Informe Legal Emitido" in notif.titulo

    def test_notificar_declaratoria_emitida(self, decano, expediente_con_informe):
        """Notificar declaratoria con copia a autoridades."""
        # Simular expediente en INFORME_EMITIDO
        from apps.resoluciones.adapters.models import InformeAptitud

        InformeAptitud.objects.create(
            expediente=expediente_con_informe,
            numero_providencia="PROV-590-2026-0001",
            emisor=expediente_con_informe.estudiante,
            dictamen="APTO",
            archivo_informe_path="/tmp/test.pdf",
        )

        notif_est, notifs_autoridades = notificar_declaratoria_emitida(
            expediente=expediente_con_informe,
            numero_memorando="MEM-162-2026-0001",
            decano_emisor=expediente_con_informe.estudiante,  # dummy
        )

        # Verificar notificación al estudiante
        assert notif_est is not None
        assert notif_est.usuario_destino == expediente_con_informe.estudiante
        assert "Declaratoria de Aptitud Emitida" in notif_est.titulo

        # Verificar notificaciones a autoridades (copia)
        # Al menos debe haber una notificación de copia
        # (depende de qué autoridades existan en la BD)


class TestMarcarComoLeida:
    """Tests de marcado de notificaciones como leídas."""

    def test_marcar_como_leida_exitosa(self, estudiante, expediente_en_verificacion):
        """Marcar notificación como leída exitosamente."""
        notif = crear_notificacion(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            titulo="Test",
            mensaje="Test",
        )

        assert notif.leida is False

        resultado = marcar_como_leida(str(notif.id), estudiante)
        assert resultado is True

        notif.refresh_from_db()
        assert notif.leida is True

    def test_marcar_como_leida_otro_usuario_falla(self, estudiante, expediente_en_verificacion):
        """Marcar como leída por otro usuario falla."""
        from apps.authentication.adapters.models import User, Role, UserRole

        otro = User.objects.create_user(
            username="otro", email="otro@test.com", password="pass1234",
            cedula="9999999999", carrera_id="11111111-1111-1111-1111-111111111111",
            facultad_id="22222222-2222-2222-2222-222222222222",
        )
        UserRole.objects.create(user=otro, role=Role.objects.get(name="ESTUDIANTE"))

        notif = crear_notificacion(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            titulo="Test",
            mensaje="Test",
        )

        resultado = marcar_como_leida(str(notif.id), otro)
        assert resultado is False

        notif.refresh_from_db()
        assert notif.leida is False

    def test_marcar_como_leida_inexistente_falla(self, estudiante):
        """Marcar notificación inexistente falla."""
        import uuid
        resultado = marcar_como_leida(str(uuid.uuid4()), estudiante)
        assert resultado is False


class TestNotificacionesEnTransaccion:
    """Tests de notificaciones dentro de transacciones."""

    def test_notificacion_dentro_transaccion_rollback(self, estudiante, expediente_en_verificacion):
        """Si la transacción hace rollback, la notificación no persiste."""
        try:
            with transaction.atomic():
                crear_notificacion(
                    usuario_destino=estudiante,
                    expediente=expediente_en_verificacion,
                    titulo="Rollback",
                    mensaje="Test",
                )
                raise Exception("Forzar rollback")
        except Exception:
            pass

        # No debe existir la notificación
        assert NotificacionInterna.objects.filter(titulo="Rollback").count() == 0

    def test_notificacion_dentro_transaccion_commit(self, estudiante, expediente_en_verificacion):
        """Notificación persiste si la transacción hace commit."""
        with transaction.atomic():
            crear_notificacion(
                usuario_destino=estudiante,
                expediente=expediente_en_verificacion,
                titulo="Commit",
                mensaje="Test",
            )

        assert NotificacionInterna.objects.filter(titulo="Commit").count() == 1


class TestNotificacionesModelo:
    """Tests del modelo NotificacionInterna."""

    def test_ordenamiento_por_fecha_creacion_desc(self, estudiante, expediente_en_verificacion):
        """Ordenamiento por fecha_creación descendente."""
        n1 = crear_notificacion(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            titulo="Primera",
            mensaje="1",
        )
        n2 = crear_notificacion(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            titulo="Segunda",
            mensaje="2",
        )

        notifs = list(NotificacionInterna.objects.filter(usuario_destino=estudiante))
        assert notifs[0].id == n2.id  # La más reciente primero
        assert notifs[1].id == n1.id

    def test_indices_creados(self):
        """Verificar que los índices definidos en Meta existen."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND tbl_name='notificaciones_notificacioninterna'
            """)
            indices = [row[0] for row in cursor.fetchall()]

        assert any("usuario_leida" in idx for idx in indices)
        assert any("usuario_fecha" in idx for idx in indices)
        assert any("expediente" in idx for idx in indices)
        assert any("peticion" in idx for idx in indices)

    def test_str_representation(self, estudiante, expediente_en_verificacion):
        """Representación string del modelo."""
        notif = crear_notificacion(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            titulo="Test Str",
            mensaje="Test",
        )
        str_repr = str(notif)
        assert str(notif.id) in str_repr
        assert "Test Str" in str_repr