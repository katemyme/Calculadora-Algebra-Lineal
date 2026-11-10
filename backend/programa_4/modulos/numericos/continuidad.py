"""Continuidad de f en [a, b] con SymPy (hipótesis del teorema de Bolzano).

Se usa ``sympy.calculus.util.continuous_domain(f, x, [a, b])``, que devuelve la parte de
[a, b] donde f es continua. Lo que falta, ``[a, b] − dominio_continuo``, son los puntos
problemáticos: asíntotas (1/x en x = 0), saltos o tramos donde f no existe (log, sqrt).

Si SymPy no puede decidir (expresión no soportada o tarda demasiado) el resultado es
"indeterminada": quien llama debe advertir que el cambio de signo no garantiza continuidad.
"""

import math
import threading
from typing import Dict, List

import sympy as sp
from sympy.calculus.util import continuous_domain

from .parser_seguro import X

SEGUNDOS_MAXIMOS = 4.0   # tiempo máximo para el análisis simbólico


def _con_limite_de_tiempo(tarea, segundos: float):
    """Ejecuta `tarea` en un hilo; devuelve (terminó, resultado o excepción)."""
    caja: Dict = {}

    def trabajador():
        try:
            caja["resultado"] = tarea()
        except Exception as error:  # noqa: BLE001 - cualquier fallo de SymPy = "no se sabe"
            caja["error"] = error

    hilo = threading.Thread(target=trabajador, daemon=True)
    hilo.start()
    hilo.join(segundos)
    if hilo.is_alive():
        return False, None
    return "resultado" in caja, caja.get("resultado")


def _formatear_punto(punto: sp.Expr) -> str:
    """π/2 → «x = pi/2 ≈ 1.570796»; 0 → «x = 0»."""
    valor = float(punto)
    exacto = sp.sstr(punto)
    if punto.is_Integer or exacto == f"{valor:g}":
        return f"x = {exacto}"
    return f"x = {exacto} ≈ {valor:.6g}"


def _describir(conjunto: sp.Set) -> List[str]:
    """Texto legible de cada parte del conjunto donde f no es continua."""
    if isinstance(conjunto, sp.FiniteSet):
        return [_formatear_punto(p) for p in sorted(conjunto, key=float)]
    if isinstance(conjunto, sp.Interval):
        izq = "[" if not conjunto.left_open else "("
        der = "]" if not conjunto.right_open else ")"
        return [f"x en {izq}{float(conjunto.start):.6g}, {float(conjunto.end):.6g}{der} (f no existe ahí)"]
    if isinstance(conjunto, sp.Union):
        partes: List[str] = []
        for parte in conjunto.args:
            partes.extend(_describir(parte))
        return partes
    return [sp.sstr(conjunto)]


def analizar_continuidad(expresion: sp.Expr, a: float, b: float) -> Dict:
    """Decide si f es continua en [a, b].

    Devuelve {"estado": "continua" | "discontinua" | "indeterminada", "puntos": [...],
    "bordes": [floats], "excluidos": [floats]}. "bordes" son los extremos de las zonas
    problemáticas dentro de [a, b] y "excluidos" los bordes donde f NO es continua (x = π/2
    en tan). El graficador añade los bordes a la malla y deja los excluidos sin valor.
    """
    vacio = {"puntos": [], "bordes": [], "excluidos": []}
    intervalo = sp.Interval(sp.Float(a), sp.Float(b))

    def tarea():
        dominio = continuous_domain(expresion, X, intervalo)
        faltante = sp.Complement(intervalo, dominio)
        if isinstance(faltante, sp.Complement) or faltante.is_empty:
            return faltante, [], []
        bordes = sorted(p for p in faltante.boundary if math.isfinite(float(p)))
        excluidos = [p for p in bordes if faltante.contains(p) == sp.true]
        return faltante, bordes, excluidos

    termino, resultado = _con_limite_de_tiempo(tarea, SEGUNDOS_MAXIMOS)
    if not termino or resultado is None or isinstance(resultado[0], sp.Complement):
        # Complement sin simplificar: SymPy no supo restar los conjuntos.
        return {"estado": "indeterminada", **vacio}
    faltante, bordes, excluidos = resultado
    if faltante.is_empty:
        return {"estado": "continua", **vacio}
    try:
        return {
            "estado": "discontinua",
            "puntos": _describir(faltante),
            "bordes": [float(p) for p in bordes if a <= float(p) <= b],
            "excluidos": [float(p) for p in excluidos if a <= float(p) <= b],
        }
    except (TypeError, ValueError):
        return {"estado": "indeterminada", **vacio}
