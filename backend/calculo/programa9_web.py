"""Adaptador web del PROGRAMA 9 (Newton-Raphson).

Toda la matemática vive en ``programas/Programa9_GrupoX.py``. Este módulo llama a sus
funciones, agrega la tabla (Pandas) y la gráfica (Matplotlib, PNG en base64) a la respuesta
y traduce ``ErrorNumerico`` a ``ErrorDeCampo`` (HTTP 422).

Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

from pathlib import Path
import sys
from typing import Dict

from calculo.programa3_web import ErrorDeCampo

_RUTA_PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
if str(_RUTA_PROGRAMAS) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMAS))

import Programa9_GrupoX as p9  # noqa: E402


def resolver_newton(funcion: str, x0: str, tolerancia: str, max_iter: str) -> Dict:
    """Ejecuta Newton-Raphson y devuelve el reporte con la tabla y la gráfica."""
    try:
        reporte = p9.resolver_newton_raphson(funcion, x0, tolerancia, max_iter)
    except p9.ErrorNumerico as error:
        raise ErrorDeCampo(error.mensaje, campo=error.campo)
    reporte["tabla"] = p9.tabla_json(p9.construir_tabla(reporte["filas"]))
    reporte["grafica_png"] = p9.grafica_png(p9.datos_grafica(reporte))
    return reporte


def ejemplos() -> Dict:
    """Casos de prueba, valores predeterminados y fundamento para la interfaz."""
    return {
        "casos": p9.CASOS_NEWTON,
        "adicionales": p9.EJEMPLOS_ADICIONALES,
        "por_defecto": {
            "tolerancia": p9.TOLERANCIA_POR_DEFECTO,
            "max_iter": p9.MAX_ITER_POR_DEFECTO,
        },
        "derivada_minima": p9.DERIVADA_MINIMA,
        "fundamento": p9.FUNDAMENTO,
    }
