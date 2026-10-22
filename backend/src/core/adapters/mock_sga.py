"""Adaptador Hexagonal Mock SGA para Récords Académicos (T040; DEC-05).

Implementa el puerto `ISGALegacyPort` simulando la consulta inmutable de
récords académicos del SGA institucional. No ejecuta conexiones reales;
retorna estructuras JSON ficticias precargadas desde archivo local.

Principios:
- C-002: Dominio aislado de infraestructura
- C-017: Adaptadores reemplazables sin tocar el dominio
- DEC-05: Prohibición de conexión/escritura en BD legadas del SGA/SIAAF
- RN-005: Promedio del SGA inalterable, sin recálculo
- AP-07: Promedio tomado como insumo inmutable de lectura
"""

import json
from pathlib import Path
from typing import Optional

from core.ports import (
    ISGALegacyPort,
    RecordAcademicoSGA,
    AsignaturaRecord,
    SGAValidationError,
)


class SGAMockAdapter(ISGALegacyPort):
    """Adaptador Mock del SGA para entorno de desarrollo y pruebas (MVP).

    Carga récords académicos ficticios desde un archivo JSON local y
    expone la interfaz `ISGALegacyPort` para consulta inmutable.

    Características:
    - Carga perezosa (lazy loading) del archivo JSON
    - Búsqueda O(1) por cédula usando diccionario interno
    - Inmutabilidad: retorna copias de dataclasses frozen
    - Sin dependencias externas (red, BD, servicios)
    """

    _ARCHIVO_FIXTURE = Path(__file__).parent / "fixtures" / "sga_mock_records.json"
    _cache: Optional[dict[str, RecordAcademicoSGA]] = None

    def __init__(self, archivo_fixture: Optional[Path] = None):
        """Inicializa el adaptador.

        Args:
            archivo_fixture: Ruta opcional al archivo JSON de fixtures.
                            Por defecto usa `fixtures/sga_mock_records.json`.
        """
        self._archivo_fixture = archivo_fixture or self._ARCHIVO_FIXTURE
        self._cache = None

    def _cargar_records(self) -> dict[str, RecordAcademicoSGA]:
        """Carga y parsea los récords desde el archivo JSON.

        Returns:
            Diccionario cedula -> RecordAcademicoSGA.

        Raises:
            SGAValidationError: Si el archivo no existe, es JSON inválido,
                               o la estructura de datos no cumple el contrato.
        """
        if self._cache is not None:
            return self._cache

        if not self._archivo_fixture.exists():
            raise SGAValidationError(
                f"Archivo de fixtures SGA no encontrado: {self._archivo_fixture}"
            )

        try:
            with open(self._archivo_fixture, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise SGAValidationError(f"JSON inválido en fixtures SGA: {e}") from e

        records_dict: dict[str, RecordAcademicoSGA] = {}

        for item in data.get("records", []):
            try:
                cedula = item["cedula"]
                asignaturas = tuple(
                    AsignaturaRecord(
                        codigo=a["codigo"],
                        nombre=a["nombre"],
                        creditos=int(a["creditos"]),
                        calificacion=float(a["calificacion"]),
                        estado=a["estado"],
                        fecha_aprobacion=a.get("fecha_aprobacion"),
                    )
                    for a in item["asignaturas"]
                )

                record = RecordAcademicoSGA(
                    cedula=cedula,
                    estudiante_nombre=item["estudiante_nombre"],
                    carrera=item["carrera"],
                    facultad=item["facultad"],
                    asignaturas=asignaturas,
                    promedio_final=float(item["promedio_final"]),
                    total_creditos=int(item["total_creditos"]),
                    creditos_aprobados=int(item["creditos_aprobados"]),
                    fecha_emision=item["fecha_emision"],
                )
                records_dict[cedula] = record
            except (KeyError, TypeError, ValueError) as e:
                raise SGAValidationError(
                    f"Estructura de récord inválida en fixtures para cédula "
                    f"{item.get('cedula', 'DESCONOCIDA')}: {e}"
                ) from e

        self._cache = records_dict
        return self._cache

    def obtener_record_por_cedula(self, cedula: str) -> Optional[RecordAcademicoSGA]:
        """Obtiene el récord académico completo por cédula (DEC-05, RN-005).

        Args:
            cedula: Número de cédula del estudiante (string, sin guiones).

        Returns:
            RecordAcademicoSGA inmutable si existe, None si no se encuentra.
            Nunca lanza excepción por "no encontrado".
        """
        records = self._cargar_records()
        return records.get(cedula)

    def obtener_promedio_por_cedula(self, cedula: str) -> Optional[float]:
        """Obtiene solo el promedio final del récord académico.

        Versión optimizada para consultas que solo requieren el promedio
        (ej. cálculo de nota final de titulación en Fase 2, Art. 237 RRA-UNL).

        Args:
            cedula: Número de cédula del estudiante.

        Returns:
            Promedio final (float) calculado por el SGA, o None si no existe.
        """
        record = self.obtener_record_por_cedula(cedula)
        if record is None:
            return None
        return record.promedio_final

    def listar_cedulas_disponibles(self) -> list[str]:
        """Lista todas las cédulas disponibles en el mock (útil para tests/seeds)."""
        records = self._cargar_records()
        return sorted(records.keys())

    def recargar_cache(self) -> None:
        """Fuerza la recarga del archivo JSON (útil en tests con fixtures
        modificados)."""
        self._cache = None
        self._cargar_records()
