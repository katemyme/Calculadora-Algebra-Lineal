"""Adaptador web del Programa 4 (módulo Vectores: Independencia Lineal).

Todo el álgebra se hace en ``backend/programa_4/modulos/modulo_vectores.py``.
Este archivo solo:

- convierte el texto recibido por HTTP en fracciones exactas,
- valida dimensiones y devuelve errores con fila/columna,
- llama a ``construir_matriz_homogenea`` y ``escalonar`` del Programa 4,
- organiza el resultado (matriz reducida, pivotes y veredicto) para el frontend.
"""

import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List

from calculo.nucleo import parsear_valor, ErrorDeEntrada
from calculo.programa3_web import ErrorDeCampo

# El Programa 4 importa sus paquetes ("modulos", "teoremas") de forma
# relativa a su carpeta, así que esa carpeta debe estar en sys.path.
_RUTA_PROGRAMA4 = Path(__file__).resolve().parents[1] / "programa_4"
if str(_RUTA_PROGRAMA4) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMA4))

from modulos import modulo_vectores as p4v  # noqa: E402


def _validar_dimension(valor: int, descripcion: str) -> None:
    if not (p4v.DIMENSION_MINIMA <= valor <= p4v.DIMENSION_MAXIMA):
        raise ErrorDeCampo(
            f"{descripcion} debe estar entre {p4v.DIMENSION_MINIMA} y "
            f"{p4v.DIMENSION_MAXIMA}; se recibió {valor}.",
            campo="vectores",
        )


def _leer_vectores(vectores_txt: List[List[str]]) -> List[List[Fraction]]:
    """Convierte cada componente a Fraction. vᵢ ocupa la columna i de la rejilla."""
    if not vectores_txt or not vectores_txt[0]:
        raise ErrorDeCampo("Debe ingresar al menos un vector.", campo="vectores")
    k = len(vectores_txt)
    n = len(vectores_txt[0])
    _validar_dimension(k, "La cantidad de vectores k")
    _validar_dimension(n, "La dimensión n")

    vectores = []
    for j, vector in enumerate(vectores_txt):
        if len(vector) != n:
            raise ErrorDeCampo(
                f"El vector v{j + 1} tiene {len(vector)} componentes y se esperaban {n}.",
                campo="vectores",
                columna=j + 1,
            )
        componentes = []
        for i, texto in enumerate(vector):
            try:
                componentes.append(parsear_valor(str(texto or "")))
            except ErrorDeEntrada as error:
                # En la rejilla la fila es la componente y la columna el vector.
                raise ErrorDeCampo(
                    f"Componente {i + 1} de v{j + 1}: {error.mensaje}",
                    campo="vectores",
                    fila=i + 1,
                    columna=j + 1,
                )
        vectores.append(componentes)
    return vectores


def independencia_lineal(vectores_txt: List[List[str]]) -> Dict:
    """Decide si v₁ … vₖ de ℝⁿ son L.I. o L.D. reduciendo [A | 0]."""
    vectores = _leer_vectores(vectores_txt)
    k = len(vectores)
    n = len(vectores[0])

    # Sistema homogéneo c₁v₁ + … + cₖvₖ = 0  ->  [A | 0] de tamaño n × (k + 1).
    matriz = p4v.construir_matriz_homogenea(vectores, n)
    historial = []
    reducida, pasos, columnas_pivote = p4v.escalonar(matriz, n, k, historial)

    pivotes = len(columnas_pivote)
    independientes = pivotes == k

    return {
        "k": k,
        "n": n,
        "matriz_inicial": matriz,
        "matriz_reducida": reducida,
        "pasos": pasos,
        # Lo mismo que `pasos`, con la matriz que queda tras cada operación.
        "pasos_detalle": [
            {"notacion": notacion, "tipo": tipo, "columna_pivote": columna, "matriz": estado}
            for notacion, (tipo, columna, estado) in zip(pasos, historial)
        ],
        "columnas_pivote": columnas_pivote,
        "pivotes": pivotes,
        "variables_libres": k - pivotes,
        "columnas_libres": [j for j in range(k) if j not in columnas_pivote],
        "independientes": independientes,
        "veredicto": "L.I." if independientes else "L.D.",
        "teorema": p4v.TEOREMAS[p4v.NUMERO_MODULO],
    }
