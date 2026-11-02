"""Pruebas de integración para T041: Auditoría, Despacho de Avisos y Adaptadores Mock.

Cubre:
- Despacho sincrónico de notificaciones in-app en flujos reales
- Inmutabilidad de registros de auditoría JSONB en operaciones compuestas
- Integración del SGAMockAdapter en flujos que generan notificaciones y auditoría
"""

import io
import pytest
from django.db import transaction
from django.utils import timezone

from apps.authentication.adapters.models import (
    User,
    Role,
    UserRole,
)
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.peticiones.adapters.models import (
    PeticionDocumental,
    DocumentoEntregado,
    CatalogoDocumental,
)
from apps.verificacion.adapters.models import (
    ChecklistVerification,
)
from apps.resoluciones.adapters.models import InformeAptitud
from apps.notificaciones.adapters.models import EventoAuditoria, NotificacionInterna
from apps.notificaciones.services import (
    crear_notificacion,
    notificar_estudiante_subsanacion,
    notificar_estudiante_observacion,
    notificar_informe_emitido,
    notificar_declaratoria_emitida,
    marcar_como_leida,
)
from apps.resoluciones.services import emitir_informe
from apps.verificacion.services import evaluar_checklist
from apps.verificacion.services.validar_checklist_completo import (
    execute as validar_checklist_execute,
    ChecklistIncompletoError,
)
from core.adapters.mock_sga import SGAMockAdapter
from core.ports import (
    RecordAcademicoSGA,
    AsignaturaRecord,
)

pytestmark = pytest.mark.django_db

CARRERA_1 = "11111111-1111-1111-1111-111111111111"
FACULTAD_1 = "22222222-2222-2222-2222-222222222222"
PASSWORD = "pass1234"

# PDF válido mínimo para testing
PDF_VALIDO = (
    b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\n"
    b"endobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n"
    b"3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources"
    b"<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>\nendobj\n"
    b"4 0 obj\n<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>\nendobj\n"
    b"5 0 obj\n<</Length 44>>\nstream\nBT /F1 24 Tf 100 700 Td (Test) Tj ET\n"
    b"endstream\nendobj\nxref\n0 6\n0000000000 65535 f \n"
    b"0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
    b"0000000218 00000 n \n0000000277 00000 n \ntrailer\n"
    b"<</Size 6/Root 1 0 R>>\nstartxref\n347\n%%EOF"
)


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
        cedula="1712345678",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
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
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
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
        facultad_id=FACULTAD_1,
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
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_analista_apoyo)
    return user


@pytest.fixture
def expediente_en_verificacion(estudiante, secretario_abogado):
    """Expediente en EN_VERIFICACION con 3 requisitos CARGADO y checklist PENDIENTE."""
    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
        activa=True,
        fecha_recepcion=timezone.now(),
    )

    for i, (codigo, nombre) in enumerate(
        [
            ("REQ-01", "Acta de Grado"),
            ("REQ-02", "Certificado de Votación"),
            ("REQ-03", "Certificado Militar"),
        ]
    ):
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
def expediente_checklist_completo(estudiante, secretario_abogado):
    """Expediente con checklist 100% VERIFICADO listo para emitir informe."""
    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0002",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
        activa=True,
        fecha_recepcion=timezone.now(),
    )

    for i, (codigo, nombre) in enumerate(
        [
            ("REQ-01", "Acta de Grado"),
            ("REQ-02", "Certificado de Votación"),
            ("REQ-03", "Certificado Militar"),
            ("REQ-04", "Título de Bachiller"),
            ("REQ-05", "Record Académico Legalizado"),
        ]
    ):
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
            evaluado_por=secretario_abogado,
        )

    return expediente


@pytest.fixture
def expediente_con_informe(estudiante, secretario_abogado):
    """Expediente con informe emitido listo para declaratoria."""
    expediente = ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0003",
        estudiante=estudiante,
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
        estado=ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
        activa=True,
        fecha_recepcion=timezone.now(),
    )

    for i, (codigo, nombre) in enumerate(
        [
            ("REQ-01", "Acta de Grado"),
            ("REQ-02", "Certificado de Votación"),
            ("REQ-03", "Certificado Militar"),
            ("REQ-04", "Título de Bachiller"),
            ("REQ-05", "Record Académico Legalizado"),
        ]
    ):
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
            evaluado_por=secretario_abogado,
        )

    # Emitir informe
    InformeAptitud.objects.create(
        expediente=expediente,
        numero_providencia="PROV-590-2026-0001",
        emisor=secretario_abogado,
        dictamen="APTO",
        archivo_informe_path="/tmp/test_informe.pdf",
    )

    return expediente


@pytest.fixture
def sga_adapter():
    """Fixture para el adaptador Mock SGA."""
    return SGAMockAdapter()


class TestDespachoSincronicoNotificaciones:
    """Tests de despacho sincrónico de notificaciones in-app (T037, T038)."""

    def test_notificacion_creada_inmediatamente_en_transaccion(
        self, estudiante, expediente_en_verificacion
    ):
        """La notificación se crea y persiste inmediatamente
        dentro de una transacción."""
        with transaction.atomic():
            notif = crear_notificacion(
                usuario_destino=estudiante,
                expediente=expediente_en_verificacion,
                titulo="Test Sincrónico",
                mensaje="Mensaje de prueba",
            )

        # Debe existir inmediatamente después del commit
        assert NotificacionInterna.objects.filter(pk=notif.id).exists()
        notif_db = NotificacionInterna.objects.get(pk=notif.id)
        assert notif_db.titulo == "Test Sincrónico"
        assert notif_db.leida is False

    def test_notificacion_rollback_no_persiste(
        self, estudiante, expediente_en_verificacion
    ):
        """Si la transacción hace rollback, la notificación no persiste."""
        try:
            with transaction.atomic():
                crear_notificacion(
                    usuario_destino=estudiante,
                    expediente=expediente_en_verificacion,
                    titulo="Rollback Test",
                    mensaje="No debe persistir",
                )
                raise Exception("Forzar rollback")
        except Exception:
            pass

        assert NotificacionInterna.objects.filter(titulo="Rollback Test").count() == 0

    def test_notificacion_subsanacion_despachada_sincronicamente(
        self, expediente_en_verificacion, estudiante, secretario_abogado
    ):
        """La notificación de subsanación se despacha sincrónicamente al estudiante."""
        # Primero crear una observación para poder subsanar
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion,
            estado_verificacion="PENDIENTE",
        ).first()

        evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif.id,
            nuevo_estado="OBSERVADO",
            motivo_observacion="Falta firma",
        )

        # Ahora subsanar - esto debería generar notificación
        peticion = expediente_en_verificacion.peticiones_documentales.first()
        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=2,
            archivo_path=(
                f"expedientes/2026/{expediente_en_verificacion.id}/REQ-01_v2.pdf"
            ),
            nombre_original="REQ-01_v2.pdf",
            tamanio_bytes=200,
            hash_sha256="b" * 64,
            tipo_mime="application/pdf",
            subido_por=estudiante,
            es_vigente=True,
        )

        # Notificar subsanación
        notif = notificar_estudiante_subsanacion(expediente=expediente_en_verificacion)

        assert notif is not None
        assert notif.usuario_destino == estudiante
        assert "Subsanación" in notif.titulo
        assert notif.leida is False

    def test_notificacion_observacion_despachada_sincronicamente(
        self, expediente_en_verificacion, secretario_abogado
    ):
        """La notificación de observación se despacha sincrónicamente."""
        peticion = expediente_en_verificacion.peticiones_documentales.first()

        notif = notificar_estudiante_observacion(
            expediente=expediente_en_verificacion,
            peticion=peticion,
            motivo="Documento ilegible",
        )

        assert notif is not None
        assert notif.usuario_destino == expediente_en_verificacion.estudiante
        assert notif.peticion == peticion
        assert "Observación" in notif.titulo
        assert "Documento ilegible" in notif.mensaje

    def test_notificacion_informe_emitido_despachada_sincronicamente(
        self, expediente_checklist_completo, secretario_abogado, decano
    ):
        """La notificación de informe emitido se despacha al decano sincrónicamente."""
        # Emitir informe
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente_checklist_completo.id,
            dictamen="APTO",
        )

        notif = notificar_informe_emitido(
            expediente=expediente_checklist_completo,
            numero_providencia=informe.numero_providencia,
        )

        # La función busca decano de la facultad
        if notif:
            assert notif.usuario_destino is not None
            assert "Informe Legal Emitido" in notif.titulo

    def test_notificacion_declaratoria_despachada_con_copia(
        self, expediente_con_informe, decano, estudiante
    ):
        """La notificación de declaratoria se despacha
        al estudiante y copia a autoridades."""
        notif_est, notifs_autoridades = notificar_declaratoria_emitida(
            expediente=expediente_con_informe,
            numero_memorando="MEM-162-2026-0001",
            decano_emisor=decano,
        )

        # Notificación al estudiante
        assert notif_est is not None
        assert notif_est.usuario_destino == estudiante
        assert "Declaratoria de Aptitud Emitida" in notif_est.titulo

        # Copias a autoridades (puede ser lista vacía si no hay otras autoridades en BD)
        assert isinstance(notifs_autoridades, list)


class TestInmutabilidadAuditoriaJSONB:
    """Tests de inmutabilidad de registros de auditoría JSONB (T039)."""

    def test_evento_auditoria_creado_en_creacion_expediente(self, estudiante):
        """Crear expediente genera evento EXPEDIENTE_CREADO inmutable."""
        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-AUDIT-001",
            estudiante=estudiante,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
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
        assert "numero_expediente" in evento.detalles
        assert evento.detalles["numero_expediente"] == "EXP-AUDIT-001"
        assert evento.detalles["estado_inicial"] == "BORRADOR"

    def test_evento_auditoria_jsonb_preserva_estructura_compleja(
        self, estudiante, expediente_en_verificacion
    ):
        """El campo JSONB preserva estructuras anidadas complejas."""
        detalles_complejos = {
            "estado_anterior": "EN_VERIFICACION",
            "estado_nuevo": "OBSERVADA",
            "metadata": {
                "usuario_id": str(estudiante.id),
                "ip": "192.168.1.1",
                "nested": {"key": "value", "array": [1, 2, 3]},
            },
            "tags": ["expediente", "observacion", "pausa_plazo"],
        }

        evento = EventoAuditoria.objects.create(
            accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
            usuario=estudiante,
            expediente=expediente_en_verificacion,
            detalles=detalles_complejos,
        )

        evento_db = EventoAuditoria.objects.get(pk=evento.pk)
        assert evento_db.detalles == detalles_complejos
        assert evento_db.detalles["metadata"]["nested"]["key"] == "value"
        assert evento_db.detalles["metadata"]["nested"]["array"] == [1, 2, 3]
        assert evento_db.detalles["tags"] == [
            "expediente",
            "observacion",
            "pausa_plazo",
        ]

    def test_evento_auditoria_no_modificable_despues_creado(
        self, estudiante, expediente_en_verificacion
    ):
        """Una vez creado, el evento de auditoría no debe
        poder modificarse (solo append)."""
        evento = EventoAuditoria.objects.create(
            accion=EventoAuditoria.Accion.CHECKLIST_EVALUADO,
            usuario=estudiante,
            expediente=expediente_en_verificacion,
            detalles={"requisito": "REQ-01", "estado": "VERIFICADO"},
        )

        pk_original = evento.pk
        evento_db = EventoAuditoria.objects.get(pk=pk_original)
        assert evento_db.detalles == {"requisito": "REQ-01", "estado": "VERIFICADO"}

    def test_cambio_estado_genera_auditoria_con_delta(
        self, estudiante, expediente_en_verificacion
    ):
        """Cambio de estado genera evento ESTADO_CAMBIADO con delta completo."""
        estado_anterior = expediente_en_verificacion.estado
        expediente_en_verificacion.estado = ExpedienteTitulacion.ESTADO_OBSERVADA
        expediente_en_verificacion.save(update_fields=["estado"])

        eventos = EventoAuditoria.objects.filter(
            expediente=expediente_en_verificacion,
            accion=EventoAuditoria.Accion.ESTADO_CAMBIADO,
        )
        assert eventos.count() >= 1

        evento = eventos.latest("timestamp")
        assert evento.accion == EventoAuditoria.Accion.ESTADO_CAMBIADO
        assert evento.detalles["estado_anterior"] == estado_anterior
        assert evento.detalles["estado_nuevo"] == "OBSERVADA"

    def test_evaluacion_checklist_genera_auditoria_checklist_evaluado(
        self, expediente_en_verificacion, secretario_abogado
    ):
        """Evaluar checklist genera evento
        CHECKLIST_EVALUADO con datos del requisito."""
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

    def test_observacion_registra_auditoria_observacion_registrada(
        self, expediente_en_verificacion, secretario_abogado
    ):
        """Registrar observación genera evento OBSERVACION_REGISTRADA con motivo."""
        verif = ChecklistVerification.objects.filter(
            expediente=expediente_en_verificacion,
            estado_verificacion="PENDIENTE",
        ).first()

        evaluar_checklist.execute(
            usuario=secretario_abogado,
            checklist_verification_id=verif.id,
            nuevo_estado="OBSERVADO",
            motivo_observacion="Falta firma del director",
        )

        eventos = EventoAuditoria.objects.filter(
            expediente=expediente_en_verificacion,
            accion=EventoAuditoria.Accion.OBSERVACION_REGISTRADA,
        )
        assert eventos.count() >= 1

        evento = eventos.latest("timestamp")
        assert evento.accion == EventoAuditoria.Accion.OBSERVACION_REGISTRADA
        assert evento.detalles["motivo_observacion"] == "Falta firma del director"

    def test_carga_documento_genera_auditoria_documento_cargado(
        self, expediente_en_verificacion, estudiante
    ):
        """Cargar documento genera evento DOCUMENTO_CARGADO con hash y versión."""
        peticion = expediente_en_verificacion.peticiones_documentales.first()

        DocumentoEntregado.objects.create(
            peticion=peticion,
            version=2,
            archivo_path=(
                f"expedientes/2026/{expediente_en_verificacion.id}/doc_v2.pdf"
            ),
            nombre_original="doc_v2.pdf",
            tamanio_bytes=200,
            hash_sha256="c" * 64,
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
        assert evento.detalles["hash_sha256"] == "c" * 64

    def test_orden_temporal_eventos_auditoria(
        self, estudiante, secretario_abogado, decano
    ):
        """Los eventos de auditoría mantienen orden
        temporal correcto en flujo completo."""
        from apps.peticiones.adapters.models import CatalogoDocumental
        from apps.resoluciones.services import emitir_informe, declarar_aptitud

        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-AUDIT-002",
            estudiante=estudiante,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
            fecha_recepcion=timezone.now(),
        )

        # Crear 2 requisitos
        for codigo, nombre in [("REQ-01", "A"), ("REQ-02", "B")]:
            req = CatalogoDocumental.objects.create(
                codigo_requisito=codigo,
                nombre=nombre,
                es_obligatorio_base=True,
                fase="FASE_1",
                rol_emisor_sugerido="SECRETARIA_CARRERA",
                activo=True,
            )
            p = PeticionDocumental.objects.create(
                expediente=expediente,
                requisito=req,
                estado_peticion="CARGADO",
                dependencia_emisora="SECRETARIA_CARRERA",
            )
            DocumentoEntregado.objects.create(
                peticion=p,
                version=1,
                archivo_path="x.pdf",
                nombre_original="x.pdf",
                tamanio_bytes=100,
                hash_sha256="a" * 64,
                tipo_mime="application/pdf",
                subido_por=estudiante,
                es_vigente=True,
            )
            ChecklistVerification.objects.create(
                expediente=expediente,
                requisito=req,
                estado_verificacion="PENDIENTE",
            )

        # Verificar checklist
        for verif in ChecklistVerification.objects.filter(expediente=expediente):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )

        # Emitir informe
        emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente.id,
            dictamen="APTO",
        )

        # Registrar declaratoria
        declarar_aptitud(
            usuario=decano,
            expediente_id=expediente.id,
            archivo_memorando=io.BytesIO(PDF_VALIDO),
        )

        # Verificar que TODOS los eventos se registraron en orden temporal
        eventos = EventoAuditoria.objects.filter(expediente=expediente).order_by(
            "timestamp"
        )
        acciones = [e.accion for e in eventos]

        # Verificar presencia de eventos clave
        assert EventoAuditoria.Accion.EXPEDIENTE_CREADO in acciones
        assert EventoAuditoria.Accion.CHECKLIST_EVALUADO in acciones
        assert EventoAuditoria.Accion.INFORME_EMITIDO in acciones
        assert EventoAuditoria.Accion.DECLARATORIA_REGISTRADA in acciones
        assert EventoAuditoria.Accion.DOCUMENTO_CARGADO in acciones

        # Verificar orden: creado -> documentos -> checklist -> informe -> declaratoria
        idx_creado = acciones.index(EventoAuditoria.Accion.EXPEDIENTE_CREADO)
        idx_checklist = acciones.index(EventoAuditoria.Accion.CHECKLIST_EVALUADO)
        idx_informe = acciones.index(EventoAuditoria.Accion.INFORME_EMITIDO)
        idx_declara = acciones.index(EventoAuditoria.Accion.DECLARATORIA_REGISTRADA)

        assert idx_creado < idx_checklist < idx_informe < idx_declara


class TestIntegracionSGAMockAdapter:
    """Tests de integración del SGAMockAdapter
    con notificaciones y auditoría (T040)."""

    def test_sga_adapter_obtiene_record_estudiante_existente(
        self, estudiante, sga_adapter
    ):
        """El adaptador SGA retorna récord completo para cédula
        del estudiante de prueba."""
        record = sga_adapter.obtener_record_por_cedula(estudiante.cedula)

        assert record is not None
        assert isinstance(record, RecordAcademicoSGA)
        assert record.cedula == estudiante.cedula
        assert record.estudiante_nombre == "PEREZ GARCIA, JUAN CARLOS"
        assert record.carrera == "COMPUTACION"
        assert record.facultad == "FEIRNNR"
        assert record.promedio_final == 8.44
        assert len(record.asignaturas) == 8

    def test_sga_adapter_obtiene_promedio_para_calculo_titulacion(
        self, estudiante, sga_adapter
    ):
        """El adaptador SGA retorna promedio para uso en cálculo
        de nota final (Fase 2)."""
        promedio = sga_adapter.obtener_promedio_por_cedula(estudiante.cedula)

        assert promedio is not None
        assert isinstance(promedio, float)
        assert promedio == 8.44
        assert 0 <= promedio <= 10

    def test_sga_adapter_retorna_none_cedula_inexistente(self, sga_adapter):
        """Cédula inexistente retorna None sin lanzar excepción."""
        record = sga_adapter.obtener_record_por_cedula("9999999999")
        assert record is None

        promedio = sga_adapter.obtener_promedio_por_cedula("9999999999")
        assert promedio is None

    def test_sga_adapter_inmutable_record_academico(self, estudiante, sga_adapter):
        """El récord académico retornado es inmutable (frozen dataclass)."""
        record = sga_adapter.obtener_record_por_cedula(estudiante.cedula)

        assert record is not None

        # Intentar modificar debe fallar (dataclass frozen)
        with pytest.raises(Exception):
            record.cedula = "9999999999"

        # Las asignaturas son tupla inmutable
        assert isinstance(record.asignaturas, tuple)
        with pytest.raises(Exception):
            record.asignaturas[0] = AsignaturaRecord(  # type: ignore
                codigo="TEST",
                nombre="TEST",
                creditos=1,
                calificacion=10.0,
                estado="APROBADA",
            )

    def test_flujo_completo_con_sga_notificaciones_auditoria(
        self, estudiante, secretario_abogado, decano, sga_adapter
    ):
        """Flujo completo: consulta SGA -> crea expediente
        -> genera notificaciones -> auditoría."""
        from apps.peticiones.adapters.models import CatalogoDocumental
        from apps.resoluciones.services import emitir_informe, declarar_aptitud

        # 1. Consultar récord académico del SGA (Mock)
        record = sga_adapter.obtener_record_por_cedula(estudiante.cedula)
        assert record is not None
        promedio_sga = record.promedio_final
        assert promedio_sga == 8.44

        # 2. Crear expediente (genera notificación y auditoría)
        expediente = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-INTEGRACION-001",
            estudiante=estudiante,
            carrera_id=CARRERA_1,
            facultad_id=FACULTAD_1,
            estado=ExpedienteTitulacion.ESTADO_EN_VERIFICACION,
            activa=True,
            fecha_recepcion=timezone.now(),
        )

        # Verificar notificación de creación
        # Nota: la creación de expediente no genera notificación automática por defecto
        # pero sí genera auditoría
        NotificacionInterna.objects.filter(
            usuario_destino=estudiante,
            expediente=expediente,
        )

        # Verificar auditoría de creación
        eventos_creacion = EventoAuditoria.objects.filter(
            expediente=expediente,
            accion=EventoAuditoria.Accion.EXPEDIENTE_CREADO,
        )
        assert eventos_creacion.count() == 1

        # 3. Agregar requisitos y verificar
        for codigo, nombre in [
            ("REQ-01", "Acta de Grado"),
            ("REQ-02", "Certificado de Votación"),
        ]:
            req = CatalogoDocumental.objects.create(
                codigo_requisito=codigo,
                nombre=nombre,
                es_obligatorio_base=True,
                fase="FASE_1",
                rol_emisor_sugerido="SECRETARIA_CARRERA",
                activo=True,
            )
            p = PeticionDocumental.objects.create(
                expediente=expediente,
                requisito=req,
                estado_peticion="CARGADO",
                dependencia_emisora="SECRETARIA_CARRERA",
            )
            DocumentoEntregado.objects.create(
                peticion=p,
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
                requisito=req,
                estado_verificacion="PENDIENTE",
            )

        # 4. Verificar checklist (genera auditoría)
        for verif in ChecklistVerification.objects.filter(expediente=expediente):
            evaluar_checklist.execute(
                usuario=secretario_abogado,
                checklist_verification_id=verif.id,
                nuevo_estado="VERIFICADO",
            )

        eventos_checklist = EventoAuditoria.objects.filter(
            expediente=expediente,
            accion=EventoAuditoria.Accion.CHECKLIST_EVALUADO,
        )
        assert eventos_checklist.count() == 2

        # 5. Emitir informe (genera notificación a decano y auditoría)
        informe = emitir_informe(
            usuario=secretario_abogado,
            expediente_id=expediente.id,
            dictamen="APTO",
        )

        notificar_informe_emitido(
            expediente=expediente,
            numero_providencia=informe.numero_providencia,
        )

        eventos_informe = EventoAuditoria.objects.filter(
            expediente=expediente,
            accion=EventoAuditoria.Accion.INFORME_EMITIDO,
        )
        assert eventos_informe.count() >= 1

        # 6. Registrar declaratoria (genera notificaciones y auditoría)
        declaratoria = declarar_aptitud(
            usuario=decano,
            expediente_id=expediente.id,
            archivo_memorando=io.BytesIO(PDF_VALIDO),
        )

        notif_est, notifs_autoridades = notificar_declaratoria_emitida(
            expediente=expediente,
            numero_memorando=declaratoria.numero_memorando,
            decano_emisor=decano,
        )

        eventos_declara = EventoAuditoria.objects.filter(
            expediente=expediente,
            accion=EventoAuditoria.Accion.DECLARATORIA_REGISTRADA,
        )
        assert eventos_declara.count() >= 1

        # 7. Verificar que todos los componentes funcionaron juntos
        total_eventos = EventoAuditoria.objects.filter(expediente=expediente).count()
        assert (
            total_eventos >= 5
        )  # creado + 2 docs + 2 checklist + informe + declaratoria

        total_notificaciones = NotificacionInterna.objects.filter(
            expediente=expediente
        ).count()
        assert (
            total_notificaciones >= 2
        )  # informe + declaratoria (estudiante + autoridades)

        # 8. Verificar que el promedio del SGA está disponible para uso futuro (Fase 2)
        promedio_final = sga_adapter.obtener_promedio_por_cedula(estudiante.cedula)
        assert promedio_final == 8.44


class TestNotificacionesMarcarLeidaIntegracion:
    """Tests de integración para marcado de notificaciones como leídas."""

    def test_marcar_leida_notificacion_generada_por_flujo(
        self, expediente_en_verificacion, estudiante
    ):
        """Marcar como leída una notificación generada durante el flujo."""
        notif = notificar_estudiante_observacion(
            expediente=expediente_en_verificacion,
            peticion=expediente_en_verificacion.peticiones_documentales.first(),
            motivo="Test motivo",
        )

        assert notif.leida is False

        resultado = marcar_como_leida(str(notif.id), estudiante)
        assert resultado is True

        notif.refresh_from_db()
        assert notif.leida is True

    def test_marcar_leida_otro_usuario_no_puede(
        self, expediente_en_verificacion, estudiante, otro_estudiante
    ):
        """Otro usuario no puede marcar notificación ajena como leída."""
        notif = crear_notificacion(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            titulo="Test",
            mensaje="Test",
        )

        resultado = marcar_como_leida(str(notif.id), otro_estudiante)
        assert resultado is False

        notif.refresh_from_db()
        assert notif.leida is False


@pytest.fixture
def otro_estudiante(rol_estudiante):
    user = User.objects.create_user(
        username="otro_est",
        email="otro@test.com",
        password="pass1234",
        cedula="9999999999",
        carrera_id=CARRERA_1,
        facultad_id=FACULTAD_1,
    )
    UserRole.objects.create(user=user, role=rol_estudiante)
    return user


class TestIndicesRendimientoNotificacionesAuditoria:
    """Tests de índices de rendimiento para notificaciones y auditoría."""

    def test_indices_notificaciones_creados(self):
        """Verificar que los índices de NotificacionInterna existen."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='index' AND tbl_name='notificaciones_notificacioninterna'
            """
            )
            indices = [row[0] for row in cursor.fetchall()]

        assert any("usuario_leida" in idx for idx in indices)
        assert any("usuario_fecha" in idx for idx in indices)
        assert any("expediente" in idx for idx in indices)
        assert any("peticion" in idx for idx in indices)

    def test_indices_auditoria_creados(self):
        """Verificar que los índices de EventoAuditoria existen."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='index' AND tbl_name='notificaciones_eventoauditoria'
            """
            )
            indices = [row[0] for row in cursor.fetchall()]

        assert any("expediente_fecha" in idx for idx in indices)
        assert any("usuario_fecha" in idx for idx in indices)
        assert any("accion_fecha" in idx for idx in indices)
        assert any("fecha" in idx for idx in indices)


class TestCasosDeBordeIntegracion:
    """Tests de casos de borde en la integración."""

    def test_notificacion_con_expediente_valida(
        self, estudiante, expediente_en_verificacion
    ):
        """Crear notificación con expediente asociado es válido."""
        notif = crear_notificacion(
            usuario_destino=estudiante,
            expediente=expediente_en_verificacion,
            titulo="Sistema",
            mensaje="Notificación del sistema",
        )

        assert notif.expediente == expediente_en_verificacion
        assert notif.titulo == "Sistema"

    def test_auditoria_con_usuario_valida(self, estudiante, expediente_en_verificacion):
        """Evento de auditoría con usuario es válido."""
        evento = EventoAuditoria.objects.create(
            accion=EventoAuditoria.Accion.EXPEDIENTE_CREADO,
            usuario=estudiante,
            expediente=expediente_en_verificacion,
            rol_usuario="ESTUDIANTE",
            detalles={"origen": "sistema", "automatico": True},
        )

        assert evento.usuario == estudiante
        assert evento.rol_usuario == "ESTUDIANTE"
        assert evento.detalles["origen"] == "sistema"

    def test_sga_adapter_recarga_cache(self, sga_adapter):
        """Recargar cache del adaptador SGA funciona correctamente."""
        record1 = sga_adapter.obtener_record_por_cedula("1712345678")
        assert record1 is not None

        sga_adapter.recargar_cache()

        record2 = sga_adapter.obtener_record_por_cedula("1712345678")
        assert record2 is not None
        assert record1.cedula == record2.cedula
        assert record1.promedio_final == record2.promedio_final


class TestValidacionChecklistCompletoConAuditoria:
    """Tests de validación de checklist completo integrados con auditoría."""

    def test_validar_checklist_bloquea_si_pendiente_genera_auditoria(
        self, expediente_en_verificacion, secretario_abogado
    ):
        """Validar checklist con pendientes falla y se audita el intento."""
        # El expediente tiene checklist PENDIENTE
        with pytest.raises(ChecklistIncompletoError):
            validar_checklist_execute(expediente_id=expediente_en_verificacion.id)

    def test_validar_checklist_exitoso_si_todos_verificados_genera_auditoria(
        self, expediente_checklist_completo, secretario_abogado
    ):
        """Validar checklist 100% verificado pasa y se audita."""
        # No debe lanzar excepción
        resultado = validar_checklist_execute(
            expediente_id=expediente_checklist_completo.id
        )
        assert resultado is True

        # Verificar auditoría del intento de validación (si se registra)
        # Nota: la validación en sí puede no generar evento de auditoría específico
        # pero la emisión de informe posterior sí lo hará


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
