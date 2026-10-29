"""Adaptador web de la Demostración de Subespacio (pestaña Vectores).

Todo el álgebra se hace en ``backend/programa_4/modulos/modulo_subespacios.py``.
Este archivo solo:

- recibe el conjunto y la hipótesis tal cual los escribió el usuario,
- llama a ``demostrar_subespacio`` del módulo,
- traduce sus errores de lectura a ``ErrorDeCampo`` (campo "conjunto" o
  "hipotesis") para que la API responda 422 con un mensaje claro.
"""

import sys
from pathlib import Path
from typing import Dict

from calculo.programa3_web import ErrorDeCampo

# El módulo importa "modulos.modulo_vectores", relativo a la carpeta programa_4.
_RUTA_PROGRAMA4 = Path(__file__).resolve().parents[1] / "programa_4"
if str(_RUTA_PROGRAMA4) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMA4))

from modulos import modulo_subespacios as ms  # noqa: E402


def demostrar_subespacio(conjunto: str, hipotesis: str) -> Dict:
    """Demuestra (i)–(iv) y, si H es subespacio, obtiene generadores y base."""
    try:
        return ms.demostrar_subespacio(conjunto, hipotesis)
    except ms.ErrorDeSubespacio as error:
        raise ErrorDeCampo(error.mensaje, campo=error.campo)
