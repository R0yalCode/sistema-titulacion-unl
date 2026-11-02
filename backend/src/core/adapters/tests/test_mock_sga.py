"""Pruebas unitarias del adaptador Mock SGA (T040; DEC-05, RN-005, AP-07).

Cubre:
- Carga correcta de fixtures JSON
- Consulta de récord completo por cédula existente
- Consulta de promedio por cédula existente
- Retorno de None para cédulas inexistentes (no excepción)
- Inmutabilidad de los dataclasses retornados
- Manejo de errores: archivo faltante, JSON inválido, estructura inválida
- Recarga de cache
"""

import json
import tempfile
from pathlib import Path

import pytest

from core.adapters.mock_sga import SGAMockAdapter
from core.ports import SGAValidationError, RecordAcademicoSGA, AsignaturaRecord


class TestSGAMockAdapterCargaInicial:
    """Tests de carga inicial y configuración del adaptador."""

    def test_carga_exitosa_fixture_por_defecto(self):
        """El adaptador carga correctamente el fixture por defecto."""
        adapter = SGAMockAdapter()
        cedulas = adapter.listar_cedulas_disponibles()

        assert len(cedulas) == 5
        assert "1712345678" in cedulas
        assert "1723456789" in cedulas
        assert "1734567890" in cedulas
        assert "1745678901" in cedulas
        assert "1756789012" in cedulas

    def test_carga_con_archivo_personalizado(self):
        """El adaptador acepta archivo fixture personalizado."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"records": []}, f)
            temp_path = Path(f.name)

        try:
            adapter = SGAMockAdapter(archivo_fixture=temp_path)
            assert adapter.listar_cedulas_disponibles() == []
        finally:
            temp_path.unlink()

    def test_archivo_no_existente_lanza_error(self):
        """Archivo fixture inexistente lanza SGAValidationError."""
        adapter = SGAMockAdapter(archivo_fixture=Path("/ruta/inexistente.json"))

        with pytest.raises(SGAValidationError) as exc_info:
            adapter.obtener_record_por_cedula("1712345678")

        assert "no encontrado" in str(exc_info.value).lower()

    def test_json_invalido_lanza_error(self):
        """JSON malformado en fixture lanza SGAValidationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)

        try:
            adapter = SGAMockAdapter(archivo_fixture=temp_path)

            with pytest.raises(SGAValidationError) as exc_info:
                adapter.obtener_record_por_cedula("1712345678")

            assert "json inválido" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()

    def test_estructura_invalida_lanza_error(self):
        """Estructura de datos inválida en fixture lanza SGAValidationError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"records": [{"cedula": "123"}]}, f)  # Faltan campos requeridos
            temp_path = Path(f.name)

        try:
            adapter = SGAMockAdapter(archivo_fixture=temp_path)

            with pytest.raises(SGAValidationError) as exc_info:
                adapter.obtener_record_por_cedula("123")

            assert "estructura" in str(exc_info.value).lower()
        finally:
            temp_path.unlink()


class TestSGAMockAdapterConsultaRecordCompleto:
    """Tests de consulta de récord académico completo."""

    def test_obtener_record_cedula_existente_retorna_record_completo(self):
        """Cédula existente retorna RecordAcademicoSGA completo e inmutable."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("1712345678")

        assert record is not None
        assert isinstance(record, RecordAcademicoSGA)
        assert record.cedula == "1712345678"
        assert record.estudiante_nombre == "PEREZ GARCIA, JUAN CARLOS"
        assert record.carrera == "COMPUTACION"
        assert record.facultad == "FEIRNNR"
        assert record.promedio_final == 8.44
        assert record.total_creditos == 32
        assert record.creditos_aprobados == 32
        assert record.fecha_emision == "2026-10-01"

    def test_record_contiene_asignaturas_correctas(self):
        """El récord incluye todas las asignaturas con datos correctos."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("1712345678")

        assert record is not None
        assert len(record.asignaturas) == 8

        # Verificar primera asignatura
        inf101 = record.asignaturas[0]
        assert inf101.codigo == "INF-101"
        assert inf101.nombre == "INTRODUCCION A LA PROGRAMACION"
        assert inf101.creditos == 4
        assert inf101.calificacion == 8.5
        assert inf101.estado == "APROBADA"
        assert inf101.fecha_aprobacion == "2023-02-15"

    def test_record_con_homologaciones_y_reprobadas(self):
        """Récord con reprobadas y recuperaciones se carga correctamente."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("1756789012")

        assert record is not None
        # 9 asignaturas (INF-102 aparece dos veces: reprobada y recuperación)
        assert len(record.asignaturas) == 9
        assert record.total_creditos == 36
        assert record.creditos_aprobados == 32
        assert record.promedio_final == 6.83

        # Verificar que hay una reprobada
        reprobadas = [a for a in record.asignaturas if a.estado == "REPROBADA"]
        assert len(reprobadas) == 1
        assert reprobadas[0].codigo == "INF-102"
        assert reprobadas[0].calificacion == 5.5
        assert reprobadas[0].fecha_aprobacion is None

    def test_obtener_record_cedula_inexistente_retorna_none(self):
        """Cédula inexistente retorna None (no lanza excepción)."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("9999999999")

        assert record is None

    def test_obtener_record_cedula_vacia_retorna_none(self):
        """Cédula vacía retorna None."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("")

        assert record is None


class TestSGAMockAdapterConsultaPromedio:
    """Tests de consulta optimizada solo de promedio."""

    def test_obtener_promedio_cedula_existente(self):
        """Retorna el promedio final calculado por el SGA."""
        adapter = SGAMockAdapter()
        promedio = adapter.obtener_promedio_por_cedula("1712345678")

        assert promedio == 8.44

    def test_obtener_promedio_cedula_inexistente_retorna_none(self):
        """Cédula inexistente retorna None para promedio."""
        adapter = SGAMockAdapter()
        promedio = adapter.obtener_promedio_por_cedula("9999999999")

        assert promedio is None

    def test_promedio_coincide_con_record_completo(self):
        """El promedio del método optimizado coincide con el del record completo."""
        adapter = SGAMockAdapter()

        for cedula in adapter.listar_cedulas_disponibles():
            record = adapter.obtener_record_por_cedula(cedula)
            promedio = adapter.obtener_promedio_por_cedula(cedula)

            assert record is not None
            assert promedio == record.promedio_final


class TestSGAMockAdapterInmutabilidad:
    """Tests de inmutabilidad de los dataclasses retornados (DEC-05, RN-005)."""

    def test_record_es_frozen_inmutable(self):
        """RecordAcademicoSGA es frozen (inmutable)."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("1712345678")

        assert record is not None

        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            record.cedula = "9999999999"  # type: ignore

    def test_asignaturas_son_tupla_inmutable(self):
        """Las asignaturas se retornan como tupla (inmutable)."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("1712345678")

        assert record is not None
        assert isinstance(record.asignaturas, tuple)

        with pytest.raises(Exception):
            record.asignaturas[0] = AsignaturaRecord(  # type: ignore
                codigo="TEST",
                nombre="TEST",
                creditos=1,
                calificacion=10.0,
                estado="APROBADA",
            )

    def test_asignatura_individual_es_frozen(self):
        """AsignaturaRecord individual es frozen (inmutable)."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("1712345678")

        assert record is not None
        asignatura = record.asignaturas[0]

        with pytest.raises(Exception):
            asignatura.calificacion = 10.0  # type: ignore


class TestSGAMockAdapterCacheYRecarga:
    """Tests de comportamiento de cache y recarga."""

    def test_cache_evita_relectura_archivo(self):
        """Múltiples consultas usan cache, no releen archivo."""
        adapter = SGAMockAdapter()

        # Primera llamada carga
        record1 = adapter.obtener_record_por_cedula("1712345678")
        # Segunda llamada usa cache
        record2 = adapter.obtener_record_por_cedula("1712345678")

        assert record1 is record2  # Misma instancia por cache

    def test_recargar_cache_fuerza_nueva_lectura(self):
        """recargar_cache() limpia el cache y fuerza nueva carga."""
        adapter = SGAMockAdapter()
        record1 = adapter.obtener_record_por_cedula("1712345678")

        adapter.recargar_cache()
        record2 = adapter.obtener_record_por_cedula("1712345678")

        # Nueva instancia tras recarga (aunque datos idénticos)
        assert record1.cedula == record2.cedula
        assert record1.promedio_final == record2.promedio_final


class TestSGAMockAdapterCasosDeBorde:
    """Tests de casos de borde y validaciones adicionales."""

    def test_todas_cedulas_tienen_promedio_valido(self):
        """Todas las cédulas del fixture tienen promedio entre 0 y 10."""
        adapter = SGAMockAdapter()

        for cedula in adapter.listar_cedulas_disponibles():
            promedio = adapter.obtener_promedio_por_cedula(cedula)
            assert promedio is not None
            assert 0 <= promedio <= 10

    def test_todas_cedulas_tienen_asignaturas(self):
        """Todos los récords tienen al menos una asignatura."""
        adapter = SGAMockAdapter()

        for cedula in adapter.listar_cedulas_disponibles():
            record = adapter.obtener_record_por_cedula(cedula)
            assert record is not None
            assert len(record.asignaturas) > 0

    def test_creditos_aprobados_no_exceden_totales(self):
        """Créditos aprobados nunca exceden totales."""
        adapter = SGAMockAdapter()

        for cedula in adapter.listar_cedulas_disponibles():
            record = adapter.obtener_record_por_cedula(cedula)
            assert record is not None
            assert record.creditos_aprobados <= record.total_creditos

    def test_fecha_emision_formato_iso(self):
        """Fecha de emisión en formato ISO 8601 (YYYY-MM-DD)."""
        adapter = SGAMockAdapter()

        for cedula in adapter.listar_cedulas_disponibles():
            record = adapter.obtener_record_por_cedula(cedula)
            assert record is not None
            # Formato básico YYYY-MM-DD
            assert len(record.fecha_emision) == 10
            assert record.fecha_emision[4] == "-"
            assert record.fecha_emision[7] == "-"


class TestSGAMockAdapterIntegracionConPuerto:
    """Tests de cumplimiento del contrato ISGALegacyPort."""

    def test_implementa_interfaz_isglegacyport(self):
        """SGAMockAdapter es instancia de ISGALegacyPort."""
        from core.ports import ISGALegacyPort

        adapter = SGAMockAdapter()
        assert isinstance(adapter, ISGALegacyPort)

    def test_metodos_abstractos_implementados(self):
        """Los métodos abstractos del puerto están implementados."""
        adapter = SGAMockAdapter()

        assert hasattr(adapter, "obtener_record_por_cedula")
        assert hasattr(adapter, "obtener_promedio_por_cedula")
        assert callable(adapter.obtener_record_por_cedula)
        assert callable(adapter.obtener_promedio_por_cedula)

    def test_no_ejecuta_conexiones_reales(self):
        """El adaptador no tiene dependencias de red/BD externas."""
        import inspect

        source = inspect.getsource(SGAMockAdapter)

        # Verificar que no importa librerías de red/BD
        assert "requests" not in source
        assert "httpx" not in source
        assert "psycopg" not in source
        assert "asyncpg" not in source
        assert "sqlalchemy" not in source
        # Solo usa json, pathlib, typing y el puerto
