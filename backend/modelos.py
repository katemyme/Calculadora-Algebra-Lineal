"""Esquemas Pydantic de entrada y salida.

RESPONSABILIDAD: validar únicamente la FORMA de los datos en tránsito HTTP
(tipos, tamaños, campos obligatorios). Estos modelos NUNCA realizan
aritmética matricial; el cálculo es competencia exclusiva de `nucleo.py`.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from nucleo import DIMENSION_MAXIMA, DIMENSION_MINIMA


class PeticionResolver(BaseModel):
    """Cuerpo de `POST /api/resolver`.

    Los números viajan como CADENAS de texto, nunca como `float`. Así '1/3'
    llega intacto y `nucleo.py` lo convierte a `Fraction` exacto. Si se
    enviara 0.333 se perdería exactitud antes de empezar a calcular.
    """

    m: int = Field(
        ...,
        ge=DIMENSION_MINIMA,
        le=DIMENSION_MAXIMA,
        description="Número de ecuaciones (filas).",
    )
    n: int = Field(
        ...,
        ge=DIMENSION_MINIMA,
        le=DIMENSION_MAXIMA,
        description="Número de incógnitas (columnas de A).",
    )
    matriz: List[List[str]] = Field(
        ...,
        description="Filas de la matriz aumentada [A | b] como texto; "
        "cada fila debe tener n+1 valores.",
    )

    @field_validator("matriz")
    @classmethod
    def _matriz_con_contenido(cls, valor: List[List[str]]) -> List[List[str]]:
        """Comprueba que la matriz traiga al menos una fila con al menos una celda."""
        if not valor or not all(isinstance(fila, list) and fila for fila in valor):
            raise ValueError("La matriz debe tener al menos una fila con celdas.")
        return valor


class NumeroSerializado(BaseModel):
    """Representación JSON de un valor exacto (ver `serializacion.py`)."""

    fraccion: str
    decimal: float
    es_entero: bool


class RespuestaError(BaseModel):
    """Forma del error 422 devuelto ante datos inválidos del usuario.

    `fila` y `columna` (base 1) se incluyen cuando se conoce la celda
    culpable, para que el frontend pueda resaltarla.
    """

    detalle: str
    fila: Optional[int] = None
    columna: Optional[int] = None
