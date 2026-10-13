"""Adaptador web de la Regla de Cramer: xᵢ = det Aᵢ(b) / det A.

Todo el álgebra se hace en ``backend/programa_4/modulos/modulo_determinantes.py``. Este
archivo solo convierte el texto recibido por HTTP en fracciones exactas, llama al módulo
y organiza sus resultados (con el paso a paso de cada determinante) para el frontend.
"""

from fractions import Fraction
from typing import Dict, List

# programa5_web deja la carpeta programa_4 en sys.path: debe importarse antes que "modulos".
from calculo.programa5_web import (
    _leer_cuadrada as leer_cuadrada,
    _paso_det_cofactores as paso_det_cofactores,
    _paso_det_reduccion as paso_det_reduccion,
    p5m,
)
from calculo.programa6_web import _factor as factor, _leer_vector as leer_vector, p6

from modulos import modulo_determinantes as cramer  # noqa: E402
from modulos.modulo_matrices import formatear_fraccion, subindice  # noqa: E402

Matriz = List[List[Fraction]]
Vector = List[Fraction]

# Hasta 3×3 el determinante se desarrolla por cofactores (se ven los menores); desde
# 4×4 esa expansión ya no se lee bien y se muestra la reducción a forma triangular.
ORDEN_MAXIMO_POR_COFACTORES = 3


def _desarrollo(matriz: Matriz, nombre: str) -> Dict:
    """Paso a paso de det(matriz), con el método que mejor se lee para su orden."""
    if len(matriz) <= ORDEN_MAXIMO_POR_COFACTORES:
        return paso_det_cofactores(matriz, nombre, p5m.determinante_por_cofactores(matriz))
    return paso_det_reduccion(matriz, nombre)


def _incognita(
    indice: int, matriz_i: Matriz, determinante_i: Fraction, determinante_a: Fraction
) -> Dict:
    """Todo lo de xᵢ: la matriz Aᵢ(b), su determinante y, si det A ≠ 0, el cociente."""
    nombre_matriz = f"A{subindice(indice)}(b)"
    datos: Dict = {
        "indice": indice,
        "variable": f"x{subindice(indice)}",
        "nombre_matriz": nombre_matriz,
        "matriz": matriz_i,
        "determinante": determinante_i,
        "desarrollo": _desarrollo(matriz_i, nombre_matriz),
        "ecuacion": None,
    }
    if determinante_a != 0:
        datos["ecuacion"] = {
            "variable": datos["variable"],
            "formula": f"det {nombre_matriz} / det A",
            "cuenta": f"{factor(determinante_i)} / {factor(determinante_a)}",
            "valor": determinante_i / determinante_a,
        }
    return datos


def _comprobacion(A: Matriz, x: Vector, b: Vector) -> Dict:
    """Producto A·x del módulo y si coincide exactamente con b."""
    producto_ax, es_correcta = p6.verificar_solucion(A, x, b)
    return {
        "Ax": producto_ax,
        "correcta": es_correcta,
        "mensaje": cramer.MENSAJE_COMPROBACION_EXITOSA if es_correcta else "A · x ≠ b",
    }


def resolver_por_cramer(a_txt: List[List[str]], b_txt: List[str]) -> Dict:
    """Resuelve Ax = b (A cuadrada) por la Regla de Cramer, con el desarrollo de cada paso."""
    A = leer_cuadrada(a_txt, "A")
    b = leer_vector(b_txt, "b", len(A))
    determinante_a, determinantes, x = cramer.resolver_por_cramer(A, b)
    matrices = cramer.matrices_de_cramer(A, b)
    respuesta: Dict = {
        "n": len(A),
        "A": A,
        "b": b,
        "det_A": determinante_a,
        "desarrollo_A": _desarrollo(A, "A"),
        "aplicable": x is not None,
        "incognitas": [
            _incognita(indice, matrices[indice], determinantes[indice], determinante_a)
            for indice in range(len(A))
        ],
        "x": x,
        "comprobacion": None,
        "motivo": None,
    }
    if x is None:
        respuesta["motivo"] = cramer.diagnostico_sin_solucion_unica(determinantes)
        return respuesta
    respuesta["comprobacion"] = _comprobacion(A, x, b)
    return respuesta
