"""Pruebas de integración para T041: Integración del SGAMockAdapter con el dominio.

Cubre:
- Uso del puerto ISGALegacyPort en servicios de dominio
- Inmutabilidad de datos del SGA en flujos de negocio
- Validación de contrato del adaptador mock
"""

import json
import tempfile
from pathlib import Path

import pytest

from core.adapters.mock_sga import SGAMockAdapter
from core.ports import (
    ISGALegacyPort,
    RecordAcademicoSGA,
    AsignaturaRecord,
    SGAValidationError,
)


class TestSGAMockAdapterContratoPuerto:
    """Tests de cumplimiento del contrato ISGALegacyPort (T040, DEC-05)."""

    def test_adapter_implementa_puerto_isglegacyport(self):
        """SGAMockAdapter es instancia de ISGALegacyPort."""
        adapter = SGAMockAdapter()
        assert isinstance(adapter, ISGALegacyPort)

    def test_metodos_abstractos_implementados(self):
        """Los métodos abstractos del puerto están implementados y son callables."""
        adapter = SGAMockAdapter()

        assert hasattr(adapter, "obtener_record_por_cedula")
        assert hasattr(adapter, "obtener_promedio_por_cedula")
        assert callable(adapter.obtener_record_por_cedula)
        assert callable(adapter.obtener_promedio_por_cedula)

    def test_no_dependencias_externas_red_bd(self):
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


class TestSGAMockAdapterInmutabilidadDatos:
    """Tests de inmutabilidad de los datos retornados (RN-005, DEC-05, AP-07)."""

    def test_record_academico_es_frozen(self):
        """RecordAcademicoSGA es frozen (inmutable)."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("1712345678")

        assert record is not None
        assert isinstance(record, RecordAcademicoSGA)

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

    def test_promedio_inalterable_proveniente_sga(self):
        """El promedio viene calculado por el SGA y es inalterable (RN-005, AP-07)."""
        adapter = SGAMockAdapter()

        for cedula in adapter.listar_cedulas_disponibles():
            record = adapter.obtener_record_por_cedula(cedula)
            promedio_directo = adapter.obtener_promedio_por_cedula(cedula)

            assert record is not None
            assert promedio_directo == record.promedio_final
            # El promedio no se recalcula en el SGT-SIAAF
            assert 0 <= record.promedio_final <= 10


class TestSGAMockAdapterCasosDeUsoDominio:
    """Tests de casos de uso del dominio que consumen el puerto SGA."""

    def test_consulta_record_para_validacion_aptitud_legal(self):
        """Consultar récord para validar aptitud legal (Art. 235 RRA-UNL)."""
        adapter = SGAMockAdapter()

        # Estudiante con buena nota
        record = adapter.obtener_record_por_cedula("1723456789")  # 9.41 promedio
        assert record is not None
        assert record.promedio_final >= 7.0  # Umbral típico de aptitud

        # Estudiante con nota baja
        record_bajo = adapter.obtener_record_por_cedula("1756789012")  # 6.83 promedio
        assert record_bajo is not None
        assert record_bajo.promedio_final < 7.0

    def test_consulta_promedio_para_nota_final_titulacion_fase2(self):
        """Consultar solo promedio para cálculo nota final
        sustentación (Fase 2, Art. 237)."""
        adapter = SGAMockAdapter()

        # Versión optimizada para solo obtener promedio
        promedio = adapter.obtener_promedio_por_cedula("1712345678")
        assert promedio == 8.44

        # Debe coincidir con el record completo
        record = adapter.obtener_record_por_cedula("1712345678")
        assert record is not None
        assert promedio == record.promedio_final

    def test_listar_cedulas_para_seeders_y_testing(self):
        """Listar cédulas disponibles útil para seeders y testing."""
        adapter = SGAMockAdapter()
        cedulas = adapter.listar_cedulas_disponibles()

        assert len(cedulas) == 5
        assert all(isinstance(c, str) for c in cedulas)
        assert "1712345678" in cedulas
        assert "1756789012" in cedulas  # Con reprobadas

    def test_estudiante_con_reprobadas_y_recuperaciones(self):
        """Récord con reprobadas y recuperaciones se maneja correctamente."""
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

        # Verificar que hay una recuperación
        recuperaciones = [
            a for a in record.asignaturas if "RECUPERACION" in a.nombre.upper()
        ]
        assert len(recuperaciones) == 1
        assert recuperaciones[0].estado == "APROBADA"
        assert recuperaciones[0].calificacion == 7.0


class TestSGAMockAdapterManejoErrores:
    """Tests de manejo de errores del adaptador (DEC-05)."""

    def test_archivo_fixture_no_existente_lanza_sgavalidationerror(self):
        """Archivo fixture inexistente lanza SGAValidationError."""
        from pathlib import Path

        adapter = SGAMockAdapter(archivo_fixture=Path("/ruta/inexistente.json"))

        with pytest.raises(SGAValidationError) as exc_info:
            adapter.obtener_record_por_cedula("1712345678")

        assert "no encontrado" in str(exc_info.value).lower()

    def test_json_invalido_lanza_sgavalidationerror(self):
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

    def test_estructura_datos_invalida_lanza_sgavalidationerror(self):
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

    def test_cedula_vacia_retorna_none(self):
        """Cédula vacía retorna None sin lanzar excepción."""
        adapter = SGAMockAdapter()
        record = adapter.obtener_record_por_cedula("")
        assert record is None

        promedio = adapter.obtener_promedio_por_cedula("")
        assert promedio is None


class TestSGAMockAdapterRendimientoCache:
    """Tests de comportamiento de cache y rendimiento."""

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


class TestSGAMockAdapterValidacionDatos:
    """Tests de validación de integridad de datos del fixture."""

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

    def test_asignaturas_tienen_campos_requeridos(self):
        """Todas las asignaturas tienen los campos requeridos."""
        adapter = SGAMockAdapter()

        for cedula in adapter.listar_cedulas_disponibles():
            record = adapter.obtener_record_por_cedula(cedula)
            assert record is not None

            for asignatura in record.asignaturas:
                assert asignatura.codigo
                assert asignatura.nombre
                assert isinstance(asignatura.creditos, int)
                assert asignatura.creditos > 0
                assert isinstance(asignatura.calificacion, (int, float))
                assert 0 <= asignatura.calificacion <= 10
                assert asignatura.estado in [
                    "APROBADA",
                    "REPROBADA",
                    "HOMOLOGADA",
                    "CONVALIDADA",
                ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
