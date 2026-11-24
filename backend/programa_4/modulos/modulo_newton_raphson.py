"""PROGRAMA 9 – Newton-Raphson (opción 7 del menú principal).

Todo el módulo (algoritmo, tabla, gráfica y menú) está en programas/Programa9_GrupoX.py;
este archivo solo lo conecta con el menú de la calculadora.
Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

import sys
from pathlib import Path

_RUTA_PROGRAMAS = Path(__file__).resolve().parents[3] / "programas"
if str(_RUTA_PROGRAMAS) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMAS))

from Programa9_GrupoX import iniciar_modulo  # noqa: E402,F401
