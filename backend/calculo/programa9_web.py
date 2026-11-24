"""Adaptador web del PROGRAMA 9 (métodos abiertos).

Toda la matemática vive en ``programas/Programa9_GrupoX.py`` (Newton-Raphson, secante,
derivadas numéricas y raíces de polinomios). Este módulo llama a sus funciones, agrega las
gráficas (Matplotlib, PNG en base64) a la respuesta y traduce ``ErrorNumerico`` a
``ErrorDeCampo`` (HTTP 422).

Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

from pathlib import Path
import sys
from typing import Callable, Dict

from calculo.programa3_web import ErrorDeCampo

_RUTA_PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
if str(_RUTA_PROGRAMAS) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMAS))

import Programa9_GrupoX as p9  # noqa: E402


def _con_graficas(calcular: Callable, *datos: str) -> Dict:
    """Ejecuta un cálculo del Programa 9 y agrega sus gráficas; un dato inválido marca su campo."""
    try:
        reporte = calcular(*datos)
    except p9.ErrorNumerico as error:
        raise ErrorDeCampo(error.mensaje, campo=error.campo)
    reporte["graficas"] = p9.graficas_png(reporte)
    return reporte


def resolver_newton(funcion: str, x0: str, tolerancia: str, max_iter: str, tipo_error: str,
                    derivada: str, h: str) -> Dict:
    """Newton-Raphson con derivada analítica (SymPy) o por diferencia central."""
    return _con_graficas(p9.resolver_newton_raphson, funcion, x0, tolerancia, max_iter, tipo_error,
                         derivada, h)


def resolver_secante(funcion: str, x0: str, x1: str, tolerancia: str, max_iter: str,
                     tipo_error: str) -> Dict:
    """Método de la secante, comparado con Newton-Raphson."""
    return _con_graficas(p9.resolver_secante, funcion, x0, x1, tolerancia, max_iter, tipo_error)


def calcular_derivadas(funcion: str, x: str, h: str) -> Dict:
    """Derivadas numéricas hacia adelante, hacia atrás y central, con el análisis del paso h."""
    return _con_graficas(p9.calcular_derivadas, funcion, x, h)


def resolver_polinomio(polinomio: str, x0: str, tolerancia: str, max_iter: str,
                       tipo_error: str) -> Dict:
    """Raíces de un polinomio con Horner, Newton y deflación (validadas con numpy.roots)."""
    return _con_graficas(p9.resolver_polinomio, polinomio, x0, tolerancia, max_iter, tipo_error)


def ejemplos() -> Dict:
    """Casos de prueba, ejemplos de la clase, valores predeterminados y fundamento."""
    return {
        "casos": p9.CASOS_NEWTON,
        "adicionales": p9.EJEMPLOS_ADICIONALES,
        "clase": p9.EJEMPLOS_CLASE,
        "secante": p9.EJEMPLOS_SECANTE,
        "derivadas": p9.EJEMPLOS_DERIVADAS,
        "polinomios": p9.EJEMPLOS_POLINOMIO,
        "por_defecto": p9.POR_DEFECTO,
        "derivada_minima": p9.DERIVADA_MINIMA,
        "fundamento": p9.FUNDAMENTO,
    }
