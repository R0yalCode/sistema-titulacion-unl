"""Tests para T032: Modelado relacional de InformeAptitud y DeclaratoriaAptitud.

Verifica:
- Creación de modelos con campos correctos
- Restricciones de unicidad en numero_providencia y numero_memorando
- Relación OneToOne con ExpedienteTitulacion
- ForeignKey a User (emisor/decano)
- Índices de base de datos
"""

import pytest
from django.db import IntegrityError

from apps.resoluciones.adapters.models import InformeAptitud, DeclaratoriaAptitud
from apps.expedientes.adapters.models import ExpedienteTitulacion
from apps.authentication.adapters.models import User, Role, UserRole

pytestmark = pytest.mark.django_db


@pytest.fixture
def rol_secretario_abogado():
    role, _ = Role.objects.get_or_create(name="SECRETARIO_ABOGADO")
    return role


@pytest.fixture
def rol_decano():
    role, _ = Role.objects.get_or_create(name="DECANO")
    return role


@pytest.fixture
def secretario_abogado(rol_secretario_abogado):
    user = User.objects.create_user(
        username="secretario_test",
        email="sec@test.com",
        password="pass1234",
        cedula="1234567891",
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
        cedula="1234567892",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=rol_decano)
    return user


@pytest.fixture
def estudiante():
    role, _ = Role.objects.get_or_create(name="ESTUDIANTE")
    user = User.objects.create_user(
        username="estudiante_test",
        email="est@test.com",
        password="pass1234",
        cedula="1234567890",
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
    )
    UserRole.objects.create(user=user, role=role)
    return user


@pytest.fixture
def expediente_informe_emitido(estudiante):
    """Expediente en estado INFORME_EMITIDO listo para informe/declaratoria."""
    return ExpedienteTitulacion.objects.create(
        numero_expediente="EXP-2026-0001",
        estudiante=estudiante,
        carrera_id="11111111-1111-1111-1111-111111111111",
        facultad_id="22222222-2222-2222-2222-222222222222",
        estado=ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
        activa=True,
    )


class TestInformeAptitud:
    """Tests del modelo InformeAptitud (Providencia N° 590)."""

    def test_crear_informe_aptitud_basico(self, expediente_informe_emitido, secretario_abogado):
        """Crear informe de aptitud con campos obligatorios."""
        informe = InformeAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_providencia="PROV-590-2026-0001",
            emisor=secretario_abogado,
            dictamen="APTO - El expediente cumple con todos los requisitos del Art. 235 RRA-UNL",
            archivo_informe_path="/media/private/expedientes/EXP-2026-0001/providencia_590.pdf",
        )

        assert informe.id is not None
        assert informe.expediente == expediente_informe_emitido
        assert informe.numero_providencia == "PROV-590-2026-0001"
        assert informe.emisor == secretario_abogado
        assert "APTO" in informe.dictamen
        assert informe.archivo_informe_path.endswith("providencia_590.pdf")
        assert informe.fecha_emision is not None
        assert informe.fecha_actualizacion is not None

    def test_str_representation(self, expediente_informe_emitido, secretario_abogado):
        """Representación string del informe."""
        informe = InformeAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_providencia="PROV-590-2026-0001",
            emisor=secretario_abogado,
            dictamen="APTO",
            archivo_informe_path="/tmp/test.pdf",
        )
        expected = f"Informe PROV-590-2026-0001 -> {expediente_informe_emitido.id}"
        assert str(informe) == expected

    def test_unicidad_numero_providencia(self, expediente_informe_emitido, secretario_abogado, estudiante):
        """El numero_providencia debe ser único en toda la tabla."""
        InformeAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_providencia="PROV-590-2026-0001",
            emisor=secretario_abogado,
            dictamen="APTO",
            archivo_informe_path="/tmp/test1.pdf",
        )

        # Crear otro expediente
        expediente2 = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0002",
            estudiante=estudiante,
            carrera_id="11111111-1111-1111-1111-111111111111",
            facultad_id="22222222-2222-2222-2222-222222222222",
            estado=ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
            activa=True,
        )

        with pytest.raises(IntegrityError):
            InformeAptitud.objects.create(
                expediente=expediente2,
                numero_providencia="PROV-590-2026-0001",  # Duplicado
                emisor=secretario_abogado,
                dictamen="APTO",
                archivo_informe_path="/tmp/test2.pdf",
            )

    def test_one_to_one_expediente(self, expediente_informe_emitido, secretario_abogado, estudiante):
        """Un expediente solo puede tener un InformeAptitud (OneToOne)."""
        InformeAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_providencia="PROV-590-2026-0001",
            emisor=secretario_abogado,
            dictamen="APTO",
            archivo_informe_path="/tmp/test1.pdf",
        )

        with pytest.raises(IntegrityError):
            InformeAptitud.objects.create(
                expediente=expediente_informe_emitido,  # Mismo expediente
                numero_providencia="PROV-590-2026-0002",
                emisor=secretario_abogado,
                dictamen="APTO",
                archivo_informe_path="/tmp/test2.pdf",
            )

    def test_relacion_emisor_secretario_abogado(self, expediente_informe_emitido, secretario_abogado):
        """El emisor debe ser un usuario con rol SECRETARIO_ABOGADO (validado a nivel servicio)."""
        informe = InformeAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_providencia="PROV-590-2026-0001",
            emisor=secretario_abogado,
            dictamen="APTO",
            archivo_informe_path="/tmp/test.pdf",
        )

        assert informe.emisor == secretario_abogado
        assert secretario_abogado.has_role("SECRETARIO_ABOGADO")

    def test_campos_fecha_auto_gestionados(self, expediente_informe_emitido, secretario_abogado):
        """fecha_emision (auto_now_add) y fecha_actualizacion (auto_now) se gestionan automáticamente."""
        informe = InformeAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_providencia="PROV-590-2026-0001",
            emisor=secretario_abogado,
            dictamen="APTO",
            archivo_informe_path="/tmp/test.pdf",
        )

        assert informe.fecha_emision is not None
        assert informe.fecha_actualizacion is not None
        assert informe.fecha_emision <= informe.fecha_actualizacion


class TestDeclaratoriaAptitud:
    """Tests del modelo DeclaratoriaAptitud (Memorando N° 162)."""

    def test_crear_declaratoria_aptitud_basica(self, expediente_informe_emitido, decano):
        """Crear declaratoria de aptitud con campos obligatorios."""
        declaratoria = DeclaratoriaAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_memorando="MEM-162-2026-0001",
            decano=decano,
            archivo_memorando_firmado_path="/media/private/expedientes/EXP-2026-0001/memorando_162_firmado.pdf",
        )

        assert declaratoria.id is not None
        assert declaratoria.expediente == expediente_informe_emitido
        assert declaratoria.numero_memorando == "MEM-162-2026-0001"
        assert declaratoria.decano == decano
        assert declaratoria.archivo_memorando_firmado_path.endswith("memorando_162_firmado.pdf")
        assert declaratoria.fecha_declaratoria is not None
        assert declaratoria.fecha_actualizacion is not None

    def test_str_representation(self, expediente_informe_emitido, decano):
        """Representación string de la declaratoria."""
        declaratoria = DeclaratoriaAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_memorando="MEM-162-2026-0001",
            decano=decano,
            archivo_memorando_firmado_path="/tmp/test.pdf",
        )
        expected = f"Declaratoria MEM-162-2026-0001 -> {expediente_informe_emitido.id}"
        assert str(declaratoria) == expected

    def test_unicidad_numero_memorando(self, expediente_informe_emitido, decano, estudiante):
        """El numero_memorando debe ser único en toda la tabla."""
        DeclaratoriaAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_memorando="MEM-162-2026-0001",
            decano=decano,
            archivo_memorando_firmado_path="/tmp/test1.pdf",
        )

        expediente2 = ExpedienteTitulacion.objects.create(
            numero_expediente="EXP-2026-0002",
            estudiante=estudiante,
            carrera_id="11111111-1111-1111-1111-111111111111",
            facultad_id="22222222-2222-2222-2222-222222222222",
            estado=ExpedienteTitulacion.ESTADO_INFORME_EMITIDO,
            activa=True,
        )

        with pytest.raises(IntegrityError):
            DeclaratoriaAptitud.objects.create(
                expediente=expediente2,
                numero_memorando="MEM-162-2026-0001",  # Duplicado
                decano=decano,
                archivo_memorando_firmado_path="/tmp/test2.pdf",
            )

    def test_one_to_one_expediente(self, expediente_informe_emitido, decano):
        """Un expediente solo puede tener una DeclaratoriaAptitud (OneToOne)."""
        DeclaratoriaAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_memorando="MEM-162-2026-0001",
            decano=decano,
            archivo_memorando_firmado_path="/tmp/test1.pdf",
        )

        with pytest.raises(IntegrityError):
            DeclaratoriaAptitud.objects.create(
                expediente=expediente_informe_emitido,  # Mismo expediente
                numero_memorando="MEM-162-2026-0002",
                decano=decano,
                archivo_memorando_firmado_path="/tmp/test2.pdf",
            )

    def test_relacion_decano(self, expediente_informe_emitido, decano):
        """El decano debe ser un usuario con rol DECANO (validado a nivel servicio)."""
        declaratoria = DeclaratoriaAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_memorando="MEM-162-2026-0001",
            decano=decano,
            archivo_memorando_firmado_path="/tmp/test.pdf",
        )

        assert declaratoria.decano == decano
        assert decano.has_role("DECANO")

    def test_campos_fecha_auto_gestionados(self, expediente_informe_emitido, decano):
        """fecha_declaratoria (auto_now_add) y fecha_actualizacion (auto_now) se gestionan automáticamente."""
        declaratoria = DeclaratoriaAptitud.objects.create(
            expediente=expediente_informe_emitido,
            numero_memorando="MEM-162-2026-0001",
            decano=decano,
            archivo_memorando_firmado_path="/tmp/test.pdf",
        )

        assert declaratoria.fecha_declaratoria is not None
        assert declaratoria.fecha_actualizacion is not None
        assert declaratoria.fecha_declaratoria <= declaratoria.fecha_actualizacion


class TestIndicesYConstraints:
    """Tests de índices y constraints de base de datos."""

    def test_indices_informe_aptitud(self):
        """Verificar que los índices definidos en Meta existen."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND tbl_name='resoluciones_informeaptitud'
            """)
            indices = [row[0] for row in cursor.fetchall()]

        # Debe tener índices para expediente, emisor, fecha_emision
        assert any("expediente" in idx for idx in indices)
        assert any("emisor" in idx for idx in indices)
        assert any("fecha" in idx for idx in indices)

    def test_indices_declaratoria_aptitud(self):
        """Verificar que los índices definidos en Meta existen."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND tbl_name='resoluciones_declaratoriaaptitud'
            """)
            indices = [row[0] for row in cursor.fetchall()]

        assert any("expediente" in idx for idx in indices)
        assert any("decano" in idx for idx in indices)
        assert any("fecha" in idx for idx in indices)

    def test_constraints_unicidad_providencia(self):
        """Verificar constraint único en numero_providencia."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sql FROM sqlite_master
                WHERE type='table' AND name='resoluciones_informeaptitud'
            """)
            schema = cursor.fetchone()[0]

        assert "UNIQUE" in schema.upper()
        assert "NUMERO_PROVIDENCIA" in schema.upper()

    def test_constraints_unicidad_memorando(self):
        """Verificar constraint único en numero_memorando."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sql FROM sqlite_master
                WHERE type='table' AND name='resoluciones_declaratoriaaptitud'
            """)
            schema = cursor.fetchone()[0]

        assert "UNIQUE" in schema.upper()
        assert "NUMERO_MEMORANDO" in schema.upper()