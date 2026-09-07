"""Esquemas Pydantic de entrada y salida de la API."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from nucleo import DIMENSION_MAXIMA, DIMENSION_MINIMA


class PeticionResolver(BaseModel):
    """Datos recibidos por POST /api/resolver.

    Los coeficientes y parámetros viajan como texto para conservar fracciones
    exactas como 1/3 y evitar convertirlas a float antes del cálculo.
    """

    m: int = Field(..., ge=DIMENSION_MINIMA, le=DIMENSION_MAXIMA)
    n: int = Field(..., ge=DIMENSION_MINIMA, le=DIMENSION_MAXIMA)
    matriz: List[List[str]]
    valores_parametros: Optional[List[str]] = Field(
        default=None,
        description=(
            "Valores elegidos por el usuario para t, t1, t2, etc. "
            "Solo se usan cuando el sistema tiene variables libres."
        ),
    )

    @field_validator("matriz")
    @classmethod
    def _matriz_con_contenido(cls, valor: List[List[str]]) -> List[List[str]]:
        if not valor or not all(isinstance(fila, list) and fila for fila in valor):
            raise ValueError("La matriz debe tener al menos una fila con celdas.")
        return valor


class NumeroSerializado(BaseModel):
    fraccion: str
    decimal: float
    es_entero: bool


class RespuestaError(BaseModel):
    detalle: str
    fila: Optional[int] = None
    columna: Optional[int] = None
