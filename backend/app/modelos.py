"""Esquemas Pydantic de entrada y salida de la API."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from calculo.nucleo import DIMENSION_MAXIMA, DIMENSION_MINIMA


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
    campo: Optional[str] = None
    fila: Optional[int] = None
    columna: Optional[int] = None


# ---------------------------------------------------------------------------
# Programa 3
# ---------------------------------------------------------------------------
class PeticionVectores(BaseModel):
    """POST /api/p3/vectores. operacion: suma | resta | escalar."""

    operacion: Literal["suma", "resta", "escalar"]
    u: List[str] = Field(default_factory=list)
    v: List[str]
    c: Optional[str] = None


class PeticionMatrices(BaseModel):
    """POST /api/p3/matrices. operacion: suma | resta | escalar."""

    operacion: Literal["suma", "resta", "escalar"]
    A: List[List[str]]
    B: List[List[str]] = Field(default_factory=list)
    c: Optional[str] = None


class PeticionProducto(BaseModel):
    """POST /api/p3/producto."""

    A: List[List[str]]
    B: List[List[str]]


class PeticionCombinacion(BaseModel):
    """POST /api/p3/combinacion. Cada vector es una lista de n componentes."""

    vectores: List[List[str]]
    b: List[str]


class PeticionIndependencia(BaseModel):
    """POST /api/p3/independencia. ¿Son v₁…vₖ linealmente independientes?"""

    vectores: List[List[str]]
    valores_parametros: Optional[List[str]] = Field(
        default=None,
        description=(
            "Valores opcionales elegidos por el usuario para t, t1, … al evaluar "
            "la solución general del sistema homogéneo."
        ),
    )


class PeticionEcuacion(BaseModel):
    """POST /api/p3/ecuacion. Resuelve A·x = b."""

    A: List[List[str]]
    b: List[str]


class PeticionDistributiva(BaseModel):
    """POST /api/p3/distributiva. Verifica A(u + v) = A·u + A·v."""

    A: List[List[str]]
    u: List[str]
    v: List[str]


class PeticionBalanceo(BaseModel):
    """POST /api/p3/balanceo. Reacción escrita con fórmulas: "H2 + O2 -> H2O"."""

    reaccion: str = Field(..., max_length=300)


# ---------------------------------------------------------------------------
# Programa 4
# ---------------------------------------------------------------------------
class PeticionIndependenciaP4(BaseModel):
    """POST /api/p4/independencia. Cada vector es una lista de n componentes."""

    vectores: List[List[str]]


class PeticionTranspuesta(BaseModel):
    """POST /api/p3/transpuesta. Demuestra un teorema de la transpuesta."""

    teorema: Literal["doble", "suma", "escalar", "producto"]
    A: List[List[str]]
    B: List[List[str]] = Field(default_factory=list)
    r: Optional[str] = None


# ---------------------------------------------------------------------------
# Programa 5
# ---------------------------------------------------------------------------
class PeticionOperacionP5(BaseModel):
    """POST /api/p5/operacion. operacion: suma | resta | escalar | producto | transpuesta."""

    operacion: Literal["suma", "resta", "escalar", "producto", "transpuesta"]
    A: List[List[str]]
    B: List[List[str]] = Field(default_factory=list)
    k: Optional[str] = None


class PeticionDeterminanteP5(BaseModel):
    """POST /api/p5/determinante. A debe ser cuadrada."""

    A: List[List[str]]


class PeticionInversaP5(BaseModel):
    """POST /api/p5/inversa. metodo: gauss_jordan | adjunta. A debe ser cuadrada."""

    metodo: Literal["gauss_jordan", "adjunta"]
    A: List[List[str]]


class IntercambioP5(BaseModel):
    """Fᵢ ↔ Fⱼ. Las filas viajan en base 1, como las ve el usuario."""

    fila_i: int
    fila_j: int


class ReemplazoP5(BaseModel):
    """Fᵢ → Fᵢ + k·Fⱼ. El factor k viaja como texto para conservar fracciones."""

    fila_i: int
    fila_j: int
    k: str


class EscalamientoP5(BaseModel):
    """Fᵢ → k·Fᵢ, con k ≠ 0."""

    fila_i: int
    k: str


class PeticionVerificadorP5(BaseModel):
    """POST /api/p5/verificador. A y B cuadradas, invertibles y del mismo orden.

    Intercambio y reemplazo son opcionales porque una matriz 1×1 no tiene dos filas.
    """

    A: List[List[str]]
    B: List[List[str]]
    intercambio: Optional[IntercambioP5] = None
    reemplazo: Optional[ReemplazoP5] = None
    escalamiento: EscalamientoP5
