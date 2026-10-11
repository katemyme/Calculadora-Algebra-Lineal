"""Adaptador web del PROGRAMA 6 (Factorización LU y solución de Ax = b).

Todo el álgebra se hace en ``backend/programa_4/modulos/modulo_lu.py``. Este archivo
solo convierte el texto recibido por HTTP en fracciones exactas, encadena las funciones
del módulo y organiza sus resultados (con el paso a paso) para el frontend.
Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional

from calculo.nucleo import ErrorDeEntrada, parsear_valor
from calculo.programa3_web import ErrorDeCampo
from calculo.programa5_web import bloques_de_teoremas
from calculo.transpuesta import _leer_matriz as leer_matriz

# El Programa 6 importa sus paquetes ("modulos", "teoremas") de forma relativa
# a la carpeta programa_4, así que esa carpeta debe estar en sys.path.
_RUTA_CALCULADORA = Path(__file__).resolve().parents[1] / "programa_4"
if str(_RUTA_CALCULADORA) not in sys.path:
    sys.path.insert(0, str(_RUTA_CALCULADORA))

from modulos import modulo_lu as p6  # noqa: E402
from modulos.modulo_matrices import formatear_fraccion, subindice  # noqa: E402

Matriz = List[List[Fraction]]
Vector = List[Fraction]


def _leer_vector(datos: List[str], campo: str, num_componentes: int) -> Vector:
    """Convierte a Fraction el vector de términos independientes y valida su tamaño."""
    if len(datos) != num_componentes:
        raise ErrorDeCampo(
            f"El vector {campo} tiene {len(datos)} componentes y se esperaban "
            f"{num_componentes} (una por cada fila de A).",
            campo=campo,
        )
    vector = []
    for indice, texto in enumerate(datos):
        try:
            vector.append(parsear_valor(str(texto or "")))
        except ErrorDeEntrada:
            raise ErrorDeCampo(
                f"La componente {indice + 1} de {campo} no es un número: "
                f"'{str(texto).strip()}'. Use enteros, decimales o fracciones "
                "(p. ej. -3, 2.5, 1/2).",
                campo=campo, fila=indice + 1,
            )
    return vector


def _factor(valor: Fraction) -> str:
    """Número entre paréntesis, para escribir productos como (2)(−3) sin ambigüedad."""
    return f"({formatear_fraccion(valor)})"


def _pasos_de_factorizacion(historial: List[Dict]) -> List[Dict]:
    """Cada reemplazo con el cálculo de su multiplicador y las matrices U y L resultantes."""
    pasos = []
    for numero, registro in enumerate(historial, start=1):
        fila, fila_pivote = registro["fila"], registro["fila_pivote"]
        nombre = f"ℓ{subindice(fila)}{subindice(fila_pivote)}"
        pasos.append({
            **registro,
            "numero": numero,
            "nombre_multiplicador": nombre,
            "cuenta_multiplicador": (
                f"{nombre} = (entrada a eliminar) / (pivote) = "
                f"{_factor(registro['entrada'])} / {_factor(registro['pivote'])} = "
                f"{formatear_fraccion(registro['multiplicador'])}"
            ),
        })
    return pasos


def _pasos_detalle(operaciones: List[str], historial: list) -> List[Dict]:
    """Cada operación de fila junto con la matriz aumentada que queda tras ella."""
    return [
        {"notacion": notacion, "tipo": tipo, "columna_pivote": columna, "matriz": estado}
        for notacion, (tipo, columna, estado) in zip(operaciones, historial)
    ]


def _ecuaciones_hacia_adelante(L: Matriz, b: Vector, y: Vector) -> List[Dict]:
    """Escribe yᵢ = bᵢ − Σ ℓᵢⱼ·yⱼ con los valores que ya calculó el módulo."""
    ecuaciones = []
    for fila in range(len(L)):
        formula = f"b{subindice(fila)}"
        cuenta = formatear_fraccion(b[fila])
        for columna in range(fila):
            # Un multiplicador 0 no aporta nada a la suma: se omite para no recargar.
            if L[fila][columna] == 0:
                continue
            formula += f" − ℓ{subindice(fila)}{subindice(columna)}·y{subindice(columna)}"
            cuenta += f" − {_factor(L[fila][columna])}{_factor(y[columna])}"
        ecuaciones.append({
            "variable": f"y{subindice(fila)}",
            "formula": formula,
            "cuenta": cuenta,
            "valor": y[fila],
        })
    return ecuaciones


def _ecuaciones_hacia_atras(U: Matriz, y: Vector, x: Vector) -> List[Dict]:
    """Escribe xᵢ = (yᵢ − Σ uᵢⱼ·xⱼ) / uᵢᵢ de la última fila a la primera."""
    orden = len(U)
    ecuaciones = []
    for fila in range(orden - 1, -1, -1):
        formula = f"y{subindice(fila)}"
        cuenta = formatear_fraccion(y[fila])
        hay_resta = False
        for columna in range(fila + 1, orden):
            if U[fila][columna] == 0:
                continue
            hay_resta = True
            formula += f" − u{subindice(fila)}{subindice(columna)}·x{subindice(columna)}"
            cuenta += f" − {_factor(U[fila][columna])}{_factor(x[columna])}"
        # El numerador solo necesita paréntesis cuando es una resta de varios términos.
        if hay_resta:
            formula = f"({formula})"
            cuenta = f"({cuenta})"
        ecuaciones.append({
            "variable": f"x{subindice(fila)}",
            "formula": f"{formula} / u{subindice(fila)}{subindice(fila)}",
            "cuenta": f"{cuenta} / {_factor(U[fila][fila])}",
            "valor": x[fila],
        })
    return ecuaciones


def _etapa_hacia_adelante(L: Matriz, b: Vector) -> Dict:
    """Etapa 1: Ly = b reduciendo [L | b]; devuelve y con su desarrollo."""
    historial: list = []
    y, operaciones = p6.sustitucion_hacia_adelante(L, b, historial)
    return {
        "aumentada_inicial": p6.construir_aumentada(L, b),
        "pasos_detalle": _pasos_detalle(operaciones, historial),
        "ecuaciones": _ecuaciones_hacia_adelante(L, b, y),
        "y": y,
    }


def _etapa_hacia_atras(U: Matriz, y: Vector) -> Optional[Dict]:
    """Etapa 2: Ux = y reduciendo [U | y]; None si U tiene un 0 en la diagonal."""
    historial: list = []
    x, operaciones = p6.sustitucion_hacia_atras(U, y, historial)
    if x is None:
        return None
    return {
        "aumentada_inicial": p6.construir_aumentada(U, y),
        "pasos_detalle": _pasos_detalle(operaciones, historial),
        "ecuaciones": _ecuaciones_hacia_atras(U, y, x),
        "x": x,
    }


def _comprobacion(A: Matriz, x: Vector, b: Vector) -> Dict:
    """Producto A·x del módulo y si coincide exactamente con b."""
    producto_ax, es_correcta = p6.verificar_solucion(A, x, b)
    return {
        "Ax": producto_ax,
        "correcta": es_correcta,
        "mensaje": p6.MENSAJE_COMPROBACION_EXITOSA if es_correcta else "A · x ≠ b",
    }


def _sistema(A: Matriz, L: Matriz, U: Matriz, b: Vector) -> Dict:
    """Solución de Ax = b en dos etapas, encadenando L, U, y, x sin volver a pedirlos."""
    adelante = _etapa_hacia_adelante(L, b)
    atras = _etapa_hacia_atras(U, adelante["y"])
    respuesta: Dict = {"b": b, "adelante": adelante, "atras": atras, "comprobacion": None}
    if atras is None:
        respuesta["motivo"] = (
            "U tiene un 0 en la diagonal, así que A es singular: Ax = b no tiene "
            "solución única y la sustitución hacia atrás no se puede completar."
        )
        return respuesta
    respuesta["comprobacion"] = _comprobacion(A, atras["x"], b)
    return respuesta


def factorizar_y_resolver(a_txt: List[List[str]], b_txt: Optional[List[str]]) -> Dict:
    """Factoriza A = LU, verifica L·U == A y, si A es cuadrada, resuelve Ax = b."""
    A = leer_matriz(a_txt, "A")
    filas, columnas = len(A), len(A[0])
    cuadrada = filas == columnas
    # El sistema solo se resuelve para matrices n×n: en otro caso b no interviene.
    b = _leer_vector(b_txt or [], "b", filas) if cuadrada else None
    respuesta: Dict = {
        "A": A,
        "m": filas,
        "n": columnas,
        "cuadrada": cuadrada,
        "teoremas": bloques_de_teoremas(p6.NUMERO_MODULO),
    }

    historial: List[Dict] = []
    try:
        L, U, operaciones = p6.factorizar_lu(A, historial)
    except p6.FactorizacionLUNoAdmitida as error:
        respuesta.update(
            admite_lu=False,
            mensaje=str(error),
            pasos=_pasos_de_factorizacion(historial),
            bloqueo={
                "fila": error.fila,
                "columna": error.columna,
                "matriz": error.matriz_parcial,
            },
        )
        return respuesta

    producto_lu, es_correcta = p6.verificar_factorizacion(A, L, U)
    respuesta.update(
        admite_lu=True,
        operaciones=operaciones,
        pasos=_pasos_de_factorizacion(historial),
        L=L,
        U=U,
        verificacion={
            "producto": producto_lu,
            "correcta": es_correcta,
            "mensaje": p6.MENSAJE_FACTORIZACION_CORRECTA if es_correcta else "L · U ≠ A",
        },
        sistema=_sistema(A, L, U, b) if cuadrada else None,
    )
    return respuesta
