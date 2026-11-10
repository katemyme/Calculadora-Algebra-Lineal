"""Adaptador web del PROGRAMA 7 (Métodos Numéricos).

Toda la matemática está en ``programas/Programa7_GrupoX.py``. Este archivo solo llama a
sus funciones principales (las mismas que usa la consola) y traduce ``ErrorNumerico``
a ``ErrorDeCampo`` para que la API responda 422 con un mensaje en español y el nombre del
campo culpable (el frontend lo marca en rojo sin borrar lo escrito).
Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

import sys
from functools import wraps
from pathlib import Path
from typing import Dict, List, Optional

from calculo.programa3_web import ErrorDeCampo

# Las herramientas de apoyo ("modulos.numericos") están en la carpeta programa_4.
_RUTA_PROGRAMA4 = Path(__file__).resolve().parents[1] / "programa_4"
if str(_RUTA_PROGRAMA4) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMA4))

from modulos.numericos.parser_seguro import ErrorNumerico  # noqa: E402

# Los algoritmos y la matemática del Programa 7 están en programas/Programa7_GrupoX.py.
_RUTA_PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
if str(_RUTA_PROGRAMAS) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMAS))

import Programa7_GrupoX as p7  # noqa: E402


def _traducir_errores(funcion):
    """Convierte ErrorNumerico (dato inválido) en ErrorDeCampo → HTTP 422."""
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        try:
            return funcion(*args, **kwargs)
        except ErrorNumerico as error:
            raise ErrorDeCampo(error.mensaje, campo=error.campo)
    return envoltura


@_traducir_errores
def resolver_biseccion(funcion: str, a: str, b: str, tolerancia: str, max_iter: str) -> Dict:
    """Bisección con validaciones, tabla, n_min y contraste con SciPy."""
    return p7.resolver_biseccion(funcion, a, b, tolerancia, max_iter)


@_traducir_errores
def graficar(funcion: str, x_min: str, x_max: str, raiz: Optional[float] = None,
             intervalo: Optional[List[float]] = None,
             tipo_intervalo: Optional[str] = None) -> Dict:
    """Segmentos de f(x) y marcas opcionales (raíz e intervalo de Bisección)."""
    return p7.graficar(funcion, x_min, x_max, raiz, intervalo, tipo_intervalo)


@_traducir_errores
def convertir_base(numero: str, base: str) -> Dict:
    """Notación posicional y conversión base 10 ↔ base 2."""
    return p7.convertir_base(numero, base)


def demostracion_flotante() -> Dict:
    """0.1 + 0.2, épsilon, overflow/underflow y tipos de error (ejecutados en el servidor)."""
    return p7.demostracion_flotante()


@_traducir_errores
def calcular_errores(xv: str, xa: str) -> Dict:
    """Ea, Er y Er%."""
    return p7.calcular_errores(xv, xa)


@_traducir_errores
def propagar_error(funcion: str, x: str, dx: str) -> Dict:
    """f′(x), Δy aproximado y Δy real."""
    return p7.propagar_error(funcion, x, dx)


def ejemplos() -> Dict:
    """Casos precargados de cada pestaña (el frontend no los repite)."""
    return {
        "biseccion": [
            {k: v for k, v in caso.items() if k != "raiz_esperada"}
            for caso in p7.CASOS_BISECCION
        ],
        "graficador": p7.EJEMPLOS_GRAFICADOR,
        "posicional": p7.EJEMPLOS_POSICIONAL,
        "propagacion": {"funcion": p7.FUNCION_PROPAGACION_POR_DEFECTO, "x": "1", "dx": "0.01"},
    }
