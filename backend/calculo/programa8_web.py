"""Adaptador web del PROGRAMA 8 (Métodos Iterativos: Jacobi y Gauss-Seidel).

Toda la matemática vive en ``programas/Programa8_GrupoX.py``. Este módulo adapta
las llamadas HTTP, traduce ``ErrorIterativo`` a ``ErrorDeCampo`` (HTTP 422) y
prepara la respuesta JSON para el frontend.

Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

from pathlib import Path
import sys
from typing import Dict, List, Optional

from calculo.programa3_web import ErrorDeCampo

_RUTA_PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
if str(_RUTA_PROGRAMAS) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMAS))

import Programa8_GrupoX as p8  # noqa: E402


def resolver_iterativos(
    A: List[List[str]],
    b: List[str],
    x0: Optional[List[str]],
    tolerancia: str,
    max_iter: str,
    permitir_reordenamiento: bool = True,
) -> Dict:
    """Ejecuta Jacobi y Gauss-Seidel y devuelve tablas, diagnósticos y comparación."""
    try:
        return p8.resolver_sistemas_iterativos(
            A_raw=A,
            b_raw=b,
            x0_raw=x0,
            tolerancia_raw=tolerancia,
            max_iter_raw=max_iter,
            permitir_reordenamiento=permitir_reordenamiento,
        )
    except p8.ErrorIterativo as error:
        raise ErrorDeCampo(
            error.mensaje,
            campo=error.campo,
            fila=error.fila,
            columna=error.columna,
        )


def ejemplos() -> Dict:
    """Devuelve los 3 casos de prueba obligatorios precargados para la interfaz."""
    return {"casos": p8.CASOS_PRUEBA_P8}