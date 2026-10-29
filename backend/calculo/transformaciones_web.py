"""Adaptador web de Transformaciones Lineales (fórmula general y vectores dados).

Todo el álgebra se hace en
``backend/programa_4/modulos/modulo_transformaciones.py``. Este archivo solo
llama a sus dos puntos de entrada y traduce los errores de lectura a
``ErrorDeCampo`` (campo "formula", "vector" o "pares", con la fila del par
cuando corresponde) para que la API responda 422 con un mensaje claro.
"""

import sys
from pathlib import Path
from typing import Dict, List

from calculo.programa3_web import ErrorDeCampo

# El módulo importa "modulos.…", relativo a la carpeta programa_4.
_RUTA_PROGRAMA4 = Path(__file__).resolve().parents[1] / "programa_4"
if str(_RUTA_PROGRAMA4) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMA4))

from modulos import modulo_subespacios as ms  # noqa: E402
from modulos import modulo_transformaciones as mt  # noqa: E402


def _traducir(error: ms.ErrorDeSubespacio) -> ErrorDeCampo:
    return ErrorDeCampo(error.mensaje, campo=error.campo, fila=getattr(error, "fila", None))


def analizar_formula(formula: str, vector: str) -> Dict:
    """T(x, …) = (…): linealidad, T(v) opcional y núcleo, nulidad, imagen y rango."""
    try:
        return mt.analizar_formula(formula, vector)
    except ms.ErrorDeSubespacio as error:
        raise _traducir(error)


def analizar_vectores(pares: List[Dict], vector: str) -> Dict:
    """T(bᵢ) = wᵢ en una base: T(v) opcional y núcleo, nulidad, imagen y rango."""
    try:
        return mt.analizar_vectores(pares, vector)
    except ms.ErrorDeSubespacio as error:
        raise _traducir(error)
