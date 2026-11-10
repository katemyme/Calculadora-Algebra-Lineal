"""Programa 7 — Calculadora de Álgebra Lineal: MÉTODOS NUMÉRICOS.

Este archivo contiene LOS ALGORITMOS Y LA MATEMÁTICA del Programa 7, ordenados para leerlos
(y explicarlos) de arriba hacia abajo:

    A. Método de Bisección ..... teorema de Bolzano, algoritmo, n_min, validaciones, SciPy
    B. Graficador .............. puntos de f(x), valores no definidos y asíntotas
    C. Notación posicional ..... dígito × base^posición, conversión base 10 ↔ base 2
    D. Errores numéricos ....... IEEE 754, épsilon, overflow/underflow, Ea/Er, propagación

La consola (opción 6 del menú principal) y la web (rutas /api/p7/...) usan ESTAS MISMAS
funciones: lo que se explica aquí es exactamente lo que se ejecuta.

Herramientas de apoyo que se importan (no son la matemática del enunciado):
    backend/programa_4/modulos/numericos/parser_seguro.py   convierte el texto que escribe el
        usuario ("x**3 - 2*x - 5") en una función f(x) SIN eval()/exec().
    backend/programa_4/modulos/numericos/continuidad.py     pregunta a SymPy si f es continua.
    backend/programa_4/modulos/modulo_metodos_numericos.py  menús de consola y gráficas.

Ejecución (desde la raíz del repositorio):
    python programas/Programa7_GrupoX.py            → menú principal completo (opción 6)
    python programas/Programa7_GrupoX.py --directo  → entra directo a Métodos Numéricos

Explicación sencilla de la matemática: docs/Programa7_LOGICA_MATEMATICA.md
Librerías externas: NumPy, SciPy, SymPy y Matplotlib (backend/requirements.txt).
Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

import math
import platform
import sys
import warnings
from decimal import Decimal
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Las herramientas de apoyo están en backend/programa_4 (paquetes "modulos" y "teoremas").
RUTA_CALCULADORA = Path(__file__).resolve().parents[1] / "backend" / "programa_4"
if str(RUTA_CALCULADORA) not in sys.path:
    sys.path.insert(0, str(RUTA_CALCULADORA))

try:
    import numpy as np
    import sympy as sp
    from scipy.optimize import bisect as scipy_bisect
    from scipy.special import ellipk
except ModuleNotFoundError as error:
    if __name__ != "__main__":
        raise
    print(f"Falta la librería '{error.name}'. Instale las dependencias con:")
    print("    python -m pip install -r backend/requirements.txt")
    sys.exit(1)

from modulos.numericos.continuidad import analizar_continuidad  # noqa: E402
from modulos.numericos.parser_seguro import (  # noqa: E402
    X,                   # el símbolo x de SymPy (para derivar)
    ErrorDeEvaluacion,   # f no existe en un punto (log(-1), 1/0, overflow...)
    ErrorNumerico,       # dato inválido escrito por el usuario (con el campo culpable)
    FuncionSegura,       # f(x) ya validada: se evalúa como funcion(x)
    analizar_funcion,    # texto → FuncionSegura
    formatear,           # número legible para los mensajes
    leer_entero,         # texto → entero (Nmax)
    leer_numero,         # texto → número real (admite pi/2, 1e-4...)
)

# A. MÉTODO DE BISECCIÓN (programado desde cero)
TOLERANCIA_POR_DEFECTO = 1e-4
MAX_ITER_POR_DEFECTO = 100
MAX_ITER_PERMITIDO = 10_000

# A.1 Casos del enunciado (E = 1e-4, Nmax = 100) y las 4 pruebas obligatorias.
CASOS_BISECCION: List[Dict] = [
    {"nombre": "x³ − 2x − 5 en [2, 3]", "funcion": "x**3 - 2*x - 5", "a": "2", "b": "3",
     "tolerancia": "1e-4", "max_iter": "100", "raiz_esperada": 2.09455148},
    {"nombre": "cos(x) − x en [0, 1]", "funcion": "cos(x) - x", "a": "0", "b": "1",
     "tolerancia": "1e-4", "max_iter": "100", "raiz_esperada": 0.73908513},
    {"nombre": "x² − 2 en [1, 2]", "funcion": "x**2 - 2", "a": "1", "b": "2",
     "tolerancia": "1e-4", "max_iter": "100", "raiz_esperada": 1.41421356},
    {"nombre": "x³ + x − 1 en [0, 1]", "funcion": "x**3 + x - 1", "a": "0", "b": "1",
     "tolerancia": "1e-4", "max_iter": "100", "raiz_esperada": 0.68232780},
    {"nombre": "x² + 1 en [−1, 1] (sin cambio de signo)", "funcion": "x**2 + 1", "a": "-1",
     "b": "1", "tolerancia": "1e-4", "max_iter": "100"},
    {"nombre": "x² − 1 en [1, 2] (raíz en el extremo)", "funcion": "x**2 - 1", "a": "1",
     "b": "2", "tolerancia": "1e-4", "max_iter": "100"},
    {"nombre": "1/x en [−1, 1] (discontinua)", "funcion": "1/x", "a": "-1", "b": "1",
     "tolerancia": "1e-4", "max_iter": "100"},
    {"nombre": "x³ − 2x − 5 con Nmax = 5", "funcion": "x**3 - 2*x - 5", "a": "2", "b": "3",
     "tolerancia": "1e-4", "max_iter": "5"},
]

NOTA_TABLA = "Extremos registrados antes de actualizar el intervalo."
NOTA_SCIPY = (
    "SciPy solo sirve de contraste: la raíz del programa se calcula con el algoritmo propio. "
    "scipy.optimize.bisect usa la misma tolerancia (xtol = E) pero un criterio de parada "
    "ligeramente distinto (añade una tolerancia relativa), por eso puede diferir en el "
    "último dígito."
)


# A.2 Signo de un número ────────────────────────────────────────────────────────────────
def signo(valor: float) -> int:
    """-1 si es negativo, 0 si es cero, 1 si es positivo."""
    return (valor > 0) - (valor < 0)


# A.3 EL ALGORITMO ──────────────────────────────────────────────────────────────────────
def metodo_biseccion(funcion: FuncionSegura, a: float, b: float, tolerancia: float,
                     max_iter: int) -> Dict:
    """Ejecuta Bisección en [a, b] (supone que las validaciones 1–5 ya se superaron).

    Devuelve la tabla de iteraciones, la raíz aproximada, f(xr), la cota del error Eb,
    el motivo de parada y el intervalo final [a_k, b_k] (cuyo punto medio es xr).
    """
    fa, fb = funcion(a), funcion(b)
    filas: List[Dict] = []
    xr_anterior: Optional[float] = None
    motivo = "max_iter"
    xr = fr = cota = None

    for k in range(1, max_iter + 1):
        xr = (a + b) / 2          # punto medio
        cota = (b - a) / 2        # Eb: la raíz está a lo sumo a media longitud de xr
        fr = funcion(xr)

        # Errores entre iteraciones: en la primera no hay xr anterior ("—").
        if xr_anterior is None:
            error_abs, error_rel, nota_rel = None, None, "—"
        else:
            error_abs = abs(xr - xr_anterior)                     # Ea
            if xr == 0:
                error_rel, nota_rel = None, "No definido"         # εa dividiría entre 0
            else:
                error_rel, nota_rel = abs((xr - xr_anterior) / xr), None   # εa (no es criterio)

        # Se registran los extremos ANTES de actualizar el intervalo.
        filas.append({
            "k": k, "a": a, "b": b, "xr": xr, "fa": fa, "fb": fb, "fr": fr,
            "Eb": cota, "Ea": error_abs, "ea_rel": error_rel, "ea_rel_nota": nota_rel,
        })
        intervalo_final = [a, b]

        if fr == 0:
            motivo = "raiz_exacta"     # raíz exacta en aritmética de máquina
            break
        if cota <= tolerancia:
            motivo = "tolerancia"      # criterio de parada: Eb ≤ E
            break

        # Se compara el SIGNO en vez del producto fa·fr (es equivalente): si ambos valores
        # son muy pequeños (p. ej. 1e-200) el producto 1e-400 no cabe en un float, se vuelve
        # 0.0 (underflow) y se elegiría la mitad equivocada.
        if signo(fa) * signo(fr) < 0:
            b, fb = xr, fr             # la raíz está en [a, xr]
        else:
            a, fa = xr, fr             # la raíz está en [xr, b]
        xr_anterior = xr

    return {
        "iteraciones": filas,
        "iteraciones_ejecutadas": len(filas),
        "raiz": xr,
        "f_raiz": fr,
        "cota_error": cota,
        "motivo": motivo,
        "intervalo_final": intervalo_final,
    }


# A.4 NÚMERO MÍNIMO DE ITERACIONES ──────────────────────────────────────────────────────
# Cada iteración parte el intervalo a la mitad: tras n iteraciones Eb = (b − a)/2ⁿ.
# Exigir Eb ≤ E  ⇔  2ⁿ ≥ (b − a)/E  ⇔  n_min = ⌈log₂((b − a)/E)⌉.
# Ejemplo: [2, 3] con E = 1e-4 → (b − a)/E = 10 000; 2¹³ = 8 192 no alcanza y
# 2¹⁴ = 16 384 sí → n_min = 14.
def iteraciones_minimas(a: float, b: float, tolerancia: float) -> int:
    """n_min = ⌈log₂((b − a)/E)⌉: el menor n con (b − a)/2ⁿ ≤ E.

    Se corrige con un ajuste entero por si log2 redondea en el último bit, y nunca es menor
    que 1 porque el método siempre calcula al menos un punto medio.
    """
    n = max(1, math.ceil(math.log2((b - a) / tolerancia)))
    while (b - a) / 2 ** n > tolerancia:
        n += 1
    while n > 1 and (b - a) / 2 ** (n - 1) <= tolerancia:
        n -= 1
    return n


# A.5 VALIDACIONES INICIALES (en el orden del enunciado) ────────────────────────────────
#   1. a < b, E > 0, Nmax ≥ 1                → si no: error en ese campo
#   2. f(a) y f(b) definidas y finitas       → si no: error en ese extremo
#   3. f(a) = 0 o f(b) = 0                   → raíz exacta en el extremo (termina)
#   4. f(a)·f(b) > 0                         → se rechaza el intervalo (sin cambio de signo)
#   5. f continua en [a, b] (SymPy)          → si no: NO se ejecuta (Bolzano no aplica)
def validar_datos(a: float, b: float, tolerancia: float, max_iter: int) -> None:
    """Validación 1: a < b, E > 0 y 1 ≤ Nmax ≤ MAX_ITER_PERMITIDO."""
    if a >= b:
        raise ErrorNumerico(
            f"El intervalo no es válido: se necesita a < b y se recibió a = {formatear(a)}, "
            f"b = {formatear(b)}.", "b"
        )
    if tolerancia <= 0:
        raise ErrorNumerico(
            f"La tolerancia E debe ser mayor que 0 (se recibió {formatear(tolerancia)}).",
            "tolerancia",
        )
    if max_iter < 1:
        raise ErrorNumerico(
            f"El máximo de iteraciones debe ser al menos 1 (se recibió {max_iter}).", "max_iter"
        )
    if max_iter > MAX_ITER_PERMITIDO:
        raise ErrorNumerico(
            f"El máximo de iteraciones no puede superar {MAX_ITER_PERMITIDO}.", "max_iter"
        )


def evaluar_extremo(funcion: FuncionSegura, valor: float, nombre: str) -> float:
    """Validación 2: f(a) o f(b) deben existir y ser finitos."""
    try:
        return funcion(valor)
    except ErrorDeEvaluacion as error:
        raise ErrorNumerico(
            f"f({nombre}) no está definida: {error.mensaje} Elija otro extremo {nombre}.", nombre
        )


# A.6 FUNCIÓN PRINCIPAL DE BISECCIÓN ────────────────────────────────────────────────────
# Es la que llaman la consola y la web: lee los textos, aplica las validaciones 1–5 en orden,
# ejecuta el algoritmo (A.3) y arma la respuesta (tabla, raíz, cota, n_min, SciPy).
# Las validaciones 3, 4 y 5 NO son errores: los datos son correctos y la respuesta ES el
# diagnóstico (así la interfaz puede mostrar f(a), f(b) y graficar la función).
def resolver_biseccion(texto_funcion: str, texto_a: str, texto_b: str,
                       texto_tolerancia: str = "1e-4", texto_max_iter: str = "100",
                       comparar_scipy: bool = True) -> Dict:
    """Lee los datos, valida en orden, ejecuta Bisección y compara con SciPy."""
    # Lectura de los datos (si alguno no es un número, error en ese campo).
    a = leer_numero(texto_a, "a")
    b = leer_numero(texto_b, "b")
    tolerancia = leer_numero(texto_tolerancia, "la tolerancia E", "tolerancia")
    max_iter = leer_entero(texto_max_iter, "el máximo de iteraciones", "max_iter")
    funcion = analizar_funcion(texto_funcion)

    # 1. a < b, E > 0, Nmax ≥ 1.
    validar_datos(a, b, tolerancia, max_iter)
    # 2. f(a) y f(b) definidas y finitas.
    fa = evaluar_extremo(funcion, a, "a")
    fb = evaluar_extremo(funcion, b, "b")

    n_min = iteraciones_minimas(a, b, tolerancia)
    salida: Dict = {
        "funcion": funcion.texto,
        "avisos": list(funcion.avisos),
        "a": a, "b": b, "tolerancia": tolerancia, "max_iter": max_iter,
        "fa": fa, "fb": fb,
        # Ventana sugerida para "Graficar esta función": el intervalo con un margen del 50 %.
        "rango_grafica": [a - 0.5 * (b - a), b + 0.5 * (b - a)],
        "n_min": n_min,
        "n_min_detalle": (f"n_min = ⌈log₂((b − a)/E)⌉ = ⌈log₂({formatear(b - a)}/{tolerancia:g})⌉ "
                          f"= ⌈{math.log2((b - a) / tolerancia):.4f}⌉ = {n_min}"),
        "advertencias": [],
        "continuidad": None,
        "ejecutado": False,
        "nota_tabla": NOTA_TABLA,
        "iteraciones": [],
        "comparacion_scipy": None,
    }

    # 3. Raíz exacta en un extremo.
    if fa == 0 or fb == 0:
        extremos = [nombre for nombre, valor in (("a", fa), ("b", fb)) if valor == 0]
        raiz = a if fa == 0 else b
        salida.update({
            "estado": "raiz_en_extremo",
            "raiz": raiz, "f_raiz": 0.0, "cota_error": 0.0,
            "mensaje": " y ".join(
                f"f({n}) = 0: raíz exacta en el extremo x = {formatear(a if n == 'a' else b)}"
                for n in extremos
            ) + ". No hace falta iterar.",
        })
        return salida

    # 4. Sin cambio de signo: se rechaza el intervalo (sin afirmar nada de otros intervalos).
    if signo(fa) * signo(fb) > 0:
        salida.update({
            "estado": "sin_cambio_signo",
            "mensaje": (
                f"El intervalo [{formatear(a)}, {formatear(b)}] no cumple la condición de cambio "
                f"de signo: f(a) = {fa:.6g} y f(b) = {fb:.6g} tienen el mismo signo "
                "(f(a)·f(b) > 0). Bisección no puede aplicarse en este intervalo; esto no "
                "significa que f no tenga raíces en otros intervalos."
            ),
        })
        return salida

    # 5. Continuidad (hipótesis de Bolzano). SymPy calcula [a, b] − (parte continua).
    continuidad = analizar_continuidad(funcion.expresion, a, b)
    salida["continuidad"] = continuidad
    if continuidad["estado"] == "discontinua":
        salida.update({
            "estado": "discontinua",
            "mensaje": (
                f"f no es continua en [{formatear(a)}, {formatear(b)}] (problema en "
                + "; ".join(continuidad["puntos"]) + "). No se cumplen las condiciones del "
                "teorema de Bolzano: el cambio de signo puede deberse a una asíntota o a un "
                "salto y no a una raíz. El método NO se ejecuta."
            ),
        })
        return salida
    if continuidad["estado"] == "indeterminada":
        salida["advertencias"].append(
            "No se pudo verificar con SymPy que f sea continua en [a, b]. El cambio de signo, "
            "por sí solo, no garantiza continuidad ni la existencia de una raíz."
        )

    if max_iter < n_min:
        salida["advertencias"].append(
            f"Nmax = {max_iter} es menor que n_min = {n_min}: el método se detendrá antes de "
            "garantizar la tolerancia pedida."
        )

    # Todo en orden: se ejecuta el algoritmo (A.3).
    try:
        resultado = metodo_biseccion(funcion, a, b, tolerancia, max_iter)
    except ErrorDeEvaluacion as error:
        # Solo puede ocurrir si la continuidad quedó indeterminada y f falla dentro de [a, b].
        raise ErrorNumerico(
            f"Durante las iteraciones f dejó de estar definida: {error.mensaje} "
            "f no es continua en [a, b].", "funcion"
        )
    estado = {"tolerancia": "convergio", "raiz_exacta": "raiz_exacta",
              "max_iter": "max_iter"}[resultado["motivo"]]
    salida.update(resultado)
    salida.update({
        "estado": estado,
        "ejecutado": True,
        "mensaje": mensaje_de_parada(resultado["motivo"], resultado, tolerancia, max_iter),
        "comparacion_n_min": comparar_n_min(resultado["motivo"],
                                            resultado["iteraciones_ejecutadas"], n_min),
    })

    # Contraste con SciPy SOLO si el intervalo es válido y la continuidad está confirmada.
    if comparar_scipy and continuidad["estado"] == "continua":
        salida["comparacion_scipy"] = comparar_con_scipy(funcion, a, b, tolerancia,
                                                         resultado["raiz"])
    elif comparar_scipy:
        salida["comparacion_scipy"] = {
            "disponible": False,
            "motivo": "No se compara con SciPy porque no se pudo confirmar la continuidad.",
            "nota": NOTA_SCIPY,
        }
    return salida


def mensaje_de_parada(motivo: str, resultado: Dict, tolerancia: float, max_iter: int) -> str:
    """Explica por qué terminó el método."""
    k = resultado["iteraciones_ejecutadas"]
    if motivo == "raiz_exacta":
        return (f"Iteración {k}: f(xr) = 0 exactamente en aritmética de máquina. "
                f"xr = {formatear(resultado['raiz'])} es una raíz exacta.")
    if motivo == "tolerancia":
        return (f"Tolerancia alcanzada en la iteración {k}: Eb = "
                f"{resultado['cota_error']:.6g} ≤ E = {tolerancia:g}.")
    return (f"Se agotaron las {max_iter} iteraciones permitidas sin alcanzar la tolerancia "
            f"(Eb = {resultado['cota_error']:.6g} > E = {tolerancia:g}). El resultado es una "
            "aproximación SIN garantía de cumplir la tolerancia pedida.")


def comparar_n_min(motivo: str, ejecutadas: int, n_min: int) -> str:
    """Compara las iteraciones ejecutadas con las teóricas (n_min)."""
    if motivo == "tolerancia" and ejecutadas == n_min:
        return f"Se ejecutaron {ejecutadas} iteraciones, exactamente las n_min = {n_min} teóricas."
    if motivo == "raiz_exacta":
        return (f"Se ejecutaron {ejecutadas} iteraciones de n_min = {n_min}: el método terminó "
                "antes porque encontró f(xr) = 0.")
    if motivo == "max_iter":
        return (f"Se ejecutaron {ejecutadas} iteraciones, menos que las n_min = {n_min} "
                "necesarias para garantizar la tolerancia.")
    return f"Se ejecutaron {ejecutadas} iteraciones; n_min = {n_min}."


# A.7 CONTRASTE CON SciPy (validación externa, NO se usa para calcular) ─────────────────
def comparar_con_scipy(funcion: FuncionSegura, a: float, b: float, tolerancia: float,
                       raiz: float) -> Dict:
    """Calcula la raíz con scipy.optimize.bisect (misma tolerancia) y la diferencia."""
    try:
        raiz_scipy = scipy_bisect(funcion.evaluar, a, b, xtol=tolerancia, maxiter=MAX_ITER_PERMITIDO)
    except (ValueError, RuntimeError, ErrorNumerico) as error:
        return {"disponible": False, "motivo": f"SciPy no pudo calcular la raíz: {error}",
                "nota": NOTA_SCIPY}
    return {
        "disponible": True,
        "raiz": raiz_scipy,
        "diferencia": abs(raiz - raiz_scipy),
        "nota": NOTA_SCIPY,
    }


# ═══════════════════════════════════════════════════════════════════════════════════════
# B. GRAFICADOR DE FUNCIONES
# ═══════════════════════════════════════════════════════════════════════════════════════
#
# IDEA: calcular f en MUCHOS puntos, descartar los que no existen y unir con líneas SOLO
# los puntos vecinos del mismo "trozo" continuo. Así no se unen las ramas de una función
# racional a través de su asíntota y log o sqrt solo se dibujan donde existen.
#
# Pasos (función generar_puntos):
#   1. 2001 puntos equiespaciados en [x_min, x_max] (el enunciado pide ≥ 1000).
#   2. Evaluar f en todos a la vez (NumPy). Lo no real / no definido / infinito queda nan
#      y se DESCARTA.
#   3. Donde SymPy dice que f no es continua (x = 0 en 1/x, x = π/2 en tan) se corta.
#   4. Red de seguridad numérica: si entre dos vecinos hay un salto grande, se miran 33
#      puntos intermedios (hay_salto). Si el salto se reparte, es una curva empinada; si
#      sigue concentrado en un paso, es una asíntota y se corta.
# El graficador NO busca raíces.
# ───────────────────────────────────────────────────────────────────────────────────────

PUNTOS_BASE = 2001           # puntos equiespaciados (el enunciado pide ≥ 1000)
SUBPUNTOS_REFINAMIENTO = 33  # subdivisiones al examinar un salto sospechoso
MAX_TRAMOS_A_REFINAR = 400

# Un ejemplo precargado por tipo de función.
EJEMPLOS_GRAFICADOR: List[Dict] = [
    {"tipo": "Lineal", "funcion": "2*x + 1", "x_min": "-5", "x_max": "5"},
    {"tipo": "Polinómica", "funcion": "x**3 - 2*x - 5", "x_min": "-3", "x_max": "3"},
    {"tipo": "Racional", "funcion": "(x + 1)/(x - 1)", "x_min": "-5", "x_max": "5"},
    {"tipo": "Radical", "funcion": "sqrt(4 - x**2)", "x_min": "-3", "x_max": "3"},
    {"tipo": "Exponencial", "funcion": "exp(x) - 2", "x_min": "-3", "x_max": "3"},
    {"tipo": "Logarítmica", "funcion": "log(x)", "x_min": "-1", "x_max": "5"},
    {"tipo": "Trigonométrica", "funcion": "sin(x)", "x_min": "-2*pi", "x_max": "2*pi"},
    {"tipo": "Trigonométrica (tan)", "funcion": "tan(x)", "x_min": "-2*pi", "x_max": "2*pi"},
    {"tipo": "Valor absoluto", "funcion": "abs(x - 1) - 2", "x_min": "-4", "x_max": "6"},
]


def hay_salto(funcion: FuncionSegura, x0: float, x1: float, salto: float) -> bool:
    """¿Entre x0 y x1 hay una asíntota o un salto (y no solo una pendiente fuerte)?"""
    xs = np.linspace(x0, x1, SUBPUNTOS_REFINAMIENTO)
    ys = funcion.evaluar_vector(xs)
    if not np.all(np.isfinite(ys)):
        return True                                   # apareció un infinito: asíntota
    mayor_paso = float(np.max(np.abs(np.diff(ys))))
    # Continua: al refinar, el cambio se reparte entre ~32 pasos (cada uno mucho menor).
    # Asíntota/salto: un solo paso se queda con casi todo el cambio (o crece).
    return mayor_paso > 0.5 * salto


def rango_y_sugerido(ys_validos: np.ndarray) -> List[float]:
    """Rango vertical: completo, salvo que una asíntota lo dispare (se usan percentiles 2–98)."""
    minimo, maximo = float(np.min(ys_validos)), float(np.max(ys_validos))
    p_bajo, p_alto = (float(v) for v in np.percentile(ys_validos, [2, 98]))
    if (maximo - minimo) > 20 * max(p_alto - p_bajo, 1e-12):
        minimo, maximo = p_bajo, p_alto        # recorta los valores enormes junto a la asíntota
    if maximo - minimo < 1e-12:
        minimo, maximo = minimo - 1, maximo + 1  # función constante
    margen = 0.08 * (maximo - minimo)
    return [minimo - margen, maximo + margen]


def generar_puntos(funcion: FuncionSegura, x_min: float, x_max: float) -> Dict:
    """Muestrea f y devuelve los segmentos continuos, las discontinuidades y el rango Y."""
    # Paso 1: malla de puntos + bordes exactos de las zonas problemáticas (x = 0 en sqrt(x)).
    continuidad = analizar_continuidad(funcion.expresion, x_min, x_max)
    xs = np.linspace(x_min, x_max, PUNTOS_BASE)
    if continuidad["bordes"]:
        xs = np.unique(np.concatenate([xs, np.array(continuidad["bordes"], dtype=float)]))

    # Paso 2: evaluar todos los puntos (lo que no existe queda nan).
    ys = funcion.evaluar_vector(xs)

    # Paso 3: en float, tan(π/2) da ≈1.6·10¹⁶ (finito) porque π/2 no es exacto: los puntos
    # donde SymPy dice que f no es continua se dejan sin valor para que corten la curva.
    # Se usa una vecindad mínima: la malla puede contener ese punto con 1 ulp de diferencia.
    vecindad = 1e-9 * (x_max - x_min)
    for punto in continuidad["excluidos"]:
        ys[np.abs(xs - punto) <= vecindad] = np.nan
    validos = np.isfinite(ys)
    if not np.any(validos):
        raise ErrorNumerico(
            f"f no toma valores reales finitos en [{formatear(x_min)}, {formatear(x_max)}]: "
            "revise el dominio de la función o elija otro intervalo.", "funcion"
        )

    # Paso 4: tramos candidatos a salto (ambos extremos válidos y cambio grande frente a la
    # escala de la función); cada candidato se refina con hay_salto().
    escala = float(np.subtract(*np.percentile(ys[validos], [95, 5]))) or 1.0
    saltos = np.abs(np.diff(ys))
    pares_validos = validos[:-1] & validos[1:]
    candidatos = np.nonzero(pares_validos & (saltos > 0.05 * escala))[0]
    if len(candidatos) > MAX_TRAMOS_A_REFINAR:   # se examinan primero los saltos mayores
        candidatos = candidatos[np.argsort(saltos[candidatos])[::-1][:MAX_TRAMOS_A_REFINAR]]
    cortes = {int(i) for i in candidatos if hay_salto(funcion, xs[i], xs[i + 1], saltos[i])}

    # Paso 5: construir los segmentos (un segmento termina en un punto no válido o un corte).
    segmentos: List[Dict] = []
    actual_x: List[float] = []
    actual_y: List[float] = []
    for i in range(len(xs)):
        if validos[i]:
            actual_x.append(float(xs[i]))
            actual_y.append(float(ys[i]))
        terminar = (not validos[i]) or i in cortes or i == len(xs) - 1
        if terminar and actual_x:
            segmentos.append({"x": actual_x, "y": actual_y})
            actual_x, actual_y = [], []

    return {
        "segmentos": segmentos,
        "puntos_evaluados": int(len(xs)),
        "puntos_validos": int(np.count_nonzero(validos)),
        "puntos_descartados": int(len(xs) - np.count_nonzero(validos)),
        "cortes_por_salto": len(cortes),
        "discontinuidades": continuidad["puntos"],
        "continuidad": continuidad["estado"],
        "rango_y": rango_y_sugerido(ys[validos]),
    }


def graficar(texto_funcion: str, texto_x_min: str, texto_x_max: str,
             raiz: Optional[float] = None, intervalo: Optional[List[float]] = None,
             tipo_intervalo: Optional[str] = None) -> Dict:
    """Función principal del graficador (consola y web): valida, muestrea y añade las marcas.

    `raiz` e `intervalo` llegan desde Bisección para marcar la raíz y el intervalo (inicial
    o final, según `tipo_intervalo`).
    """
    x_min = leer_numero(texto_x_min, "x_min")
    x_max = leer_numero(texto_x_max, "x_max")
    funcion = analizar_funcion(texto_funcion)
    if x_min >= x_max:
        raise ErrorNumerico(
            f"El rango no es válido: se necesita x_min < x_max y se recibió "
            f"x_min = {formatear(x_min)}, x_max = {formatear(x_max)}.", "x_max"
        )
    if (x_max - x_min) < 1e-9 * max(1.0, abs(x_min), abs(x_max)):
        raise ErrorNumerico("El rango [x_min, x_max] es demasiado estrecho para graficar.", "x_max")

    datos = generar_puntos(funcion, x_min, x_max)
    marcas: Dict = {}
    if raiz is not None and math.isfinite(raiz):
        try:
            y_raiz = funcion(raiz)
        except ErrorDeEvaluacion:
            y_raiz = 0.0
        marcas["raiz"] = {"x": raiz, "y": y_raiz}
        # La raíz marcada debe quedar visible aunque el rango sugerido la dejara fuera.
        bajo, alto = datos["rango_y"]
        datos["rango_y"] = [min(bajo, y_raiz), max(alto, y_raiz)]
    if intervalo and len(intervalo) == 2 and all(math.isfinite(v) for v in intervalo):
        marcas["intervalo"] = {
            "a": float(intervalo[0]), "b": float(intervalo[1]),
            "tipo": tipo_intervalo if tipo_intervalo in ("inicial", "final") else "inicial",
        }
    return {
        "funcion": funcion.texto,
        "avisos": list(funcion.avisos),
        "x_min": x_min,
        "x_max": x_max,
        **datos,
        "marcas": marcas,
    }


# ═══════════════════════════════════════════════════════════════════════════════════════
# C. NOTACIÓN POSICIONAL (base 10 ↔ base 2)
# ═══════════════════════════════════════════════════════════════════════════════════════
#
# En base β, el dígito dₖ en la posición k (contando desde 0 por la derecha) vale dₖ·βᵏ:
#
#     (dₙ…d₁d₀)_β = dₙ·βⁿ + … + d₁·β¹ + d₀·β⁰
#
#   (84506)₁₀    = 8·10⁴ + 4·10³ + 5·10² + 0·10¹ + 6·10⁰
#   (11110011)₂  = 1·2⁷ + 1·2⁶ + 1·2⁵ + 1·2⁴ + 0·2³ + 0·2² + 1·2¹ + 1·2⁰
#                = 128 + 64 + 32 + 16 + 2 + 1 = (243)₁₀
#
# - Base 2 → base 10: la descomposición misma da el valor (suma de potencias).
# - Base 10 → base 2: divisiones sucesivas entre 2; los residuos, leídos de abajo hacia
#   arriba, son los bits.
# Ambas conversiones están programadas a mano (no se usan int(texto, 2), bin() ni format()).
# int() de Python solo aparece en la verificación final como contraste independiente.
# ───────────────────────────────────────────────────────────────────────────────────────

BASES_PERMITIDAS = (10, 2)
DIGITOS_MAXIMOS = {10: 40, 2: 130}

EJEMPLOS_POSICIONAL = [
    {"numero": "84506", "base": "10"},
    {"numero": "11110011", "base": "2"},
]

_SUPERINDICES = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def superindice(numero: int) -> str:
    """4 → ⁴ (para escribir potencias como 10⁴)."""
    return str(numero).translate(_SUPERINDICES)


def subindice(numero: int) -> str:
    """10 → ₁₀ (para escribir la base, como en (84506)₁₀)."""
    return str(numero).translate(_SUBINDICES)


def notacion(digitos: str, base: int, negativo: bool = False) -> str:
    """(84506)₁₀ o (−84506)₁₀."""
    return f"({'−' if negativo else ''}{digitos}){subindice(base)}"


def potencia_entera(base: int, exponente: int) -> int:
    """βᵏ por multiplicaciones sucesivas."""
    resultado = 1
    for _ in range(exponente):
        resultado *= base
    return resultado


def descomponer(digitos: str, base: int) -> Dict:
    """Descomposición dígito × potencia de un número sin signo y su valor en base 10.

    Recorre los dígitos de izquierda a derecha: el de la izquierda tiene la potencia más alta.
    """
    n = len(digitos)
    terminos: List[Dict] = []
    valor = 0
    for indice, caracter in enumerate(digitos):
        digito = ord(caracter) - ord("0")          # '7' → 7 sin usar int()
        exponente = n - 1 - indice
        aporte = digito * potencia_entera(base, exponente)
        valor += aporte
        terminos.append({"digito": digito, "exponente": exponente, "valor": str(aporte)})

    texto_terminos = " + ".join(
        f"{t['digito']}·{base}{superindice(t['exponente'])}" for t in terminos
    )
    # En la suma de valores se omiten los términos nulos (0·βᵏ = 0).
    no_nulos = [t["valor"] for t in terminos if t["digito"] != 0]
    texto_suma = " + ".join(no_nulos) if no_nulos else "0"
    return {
        "base": base,
        "digitos": digitos,
        "notacion": notacion(digitos, base),
        "terminos": terminos,
        "descomposicion": texto_terminos,
        "suma_valores": texto_suma,
        "valor": str(valor),       # como texto: JavaScript pierde precisión con enteros > 2⁵³
        "_valor": valor,           # uso interno (entero de Python)
    }


def divisiones_sucesivas(valor: int, base: int) -> Dict:
    """Convierte un entero ≥ 0 a la base dada dividiendo y guardando los residuos.

    Ejemplo con 243 → base 2:  243 ÷ 2 = 121 r 1 · 121 ÷ 2 = 60 r 1 · 60 ÷ 2 = 30 r 0 ·
    30 ÷ 2 = 15 r 0 · 15 ÷ 2 = 7 r 1 · 7 ÷ 2 = 3 r 1 · 3 ÷ 2 = 1 r 1 · 1 ÷ 2 = 0 r 1
    → residuos de abajo hacia arriba: 11110011.
    """
    pasos: List[Dict] = []
    if valor == 0:
        return {"digitos": "0", "pasos": [{"dividendo": "0", "cociente": "0", "residuo": 0}]}
    residuos: List[int] = []
    actual = valor
    while actual > 0:
        cociente, residuo = actual // base, actual % base
        pasos.append({"dividendo": str(actual), "cociente": str(cociente), "residuo": residuo})
        residuos.append(residuo)
        actual = cociente
    # El primer residuo es el dígito de menor peso: se leen de abajo hacia arriba.
    digitos = "".join(chr(ord("0") + r) for r in reversed(residuos))
    return {"digitos": digitos, "pasos": pasos}


def validar_numero_en_base(texto: str, texto_base: str):
    """Valida base, signo y dígitos. Devuelve (base, negativo, dígitos sin ceros a la izquierda, notas)."""
    base_txt = (texto_base or "").strip()
    if base_txt not in ("10", "2"):
        raise ErrorNumerico("La base de origen debe ser 10 o 2.", "base")
    base = int(base_txt)

    numero = (texto or "").replace(" ", "").strip()
    if not numero:
        raise ErrorNumerico("Escriba un número entero.", "numero")
    negativo = numero[0] in "-−"
    if numero[0] in "+-−":
        numero = numero[1:]
    if not numero:
        raise ErrorNumerico("Después del signo debe haber al menos un dígito.", "numero")
    if any(c in ".,eE" for c in numero) and base == 10:
        raise ErrorNumerico("Solo se admiten números enteros (sin decimales ni notación científica).",
                            "numero")
    validos = "01" if base == 2 else "0123456789"
    for posicion, caracter in enumerate(numero, start=1):
        if caracter not in validos:
            permitido = "0 y 1" if base == 2 else "los dígitos del 0 al 9"
            raise ErrorNumerico(
                f"El carácter '{caracter}' (posición {posicion}) no es válido en base {base}: "
                f"solo se permiten {permitido}.", "numero"
            )
    if len(numero) > DIGITOS_MAXIMOS[base]:
        raise ErrorNumerico(
            f"El número tiene demasiados dígitos (máximo {DIGITOS_MAXIMOS[base]} en base {base}).",
            "numero"
        )
    notas: List[str] = []
    sin_ceros = numero.lstrip("0") or "0"
    if sin_ceros != numero:
        notas.append(f"Se omitieron los ceros a la izquierda: {numero} → {sin_ceros}.")
    if negativo and sin_ceros == "0":
        negativo = False
        notas.append("−0 es igual a 0: se trabaja con 0.")
    return base, negativo, sin_ceros, notas


def convertir_base(texto: str, texto_base: str) -> Dict:
    """Función principal: descompone en la base de origen, convierte a la otra y verifica.

    Negativos: el signo no forma parte de la notación posicional; se descompone |N| y al
    final se antepone el signo.
    """
    base, negativo, digitos, notas = validar_numero_en_base(texto, texto_base)
    destino_base = 2 if base == 10 else 10
    signo_texto = "−" if negativo else ""

    origen = descomponer(digitos, base)
    valor = origen.pop("_valor")

    if base == 10:
        # 10 → 2: divisiones sucesivas entre 2.
        conversion = divisiones_sucesivas(valor, 2)
        metodo = "Divisiones sucesivas entre 2 (los residuos, leídos de abajo hacia arriba, son los bits)."
        pasos = conversion["pasos"]
        digitos_destino = conversion["digitos"]
    else:
        # 2 → 10: el valor es la suma de las potencias; sus dígitos decimales se obtienen
        # con divisiones sucesivas entre 10 (también a mano).
        metodo = "Suma de potencias de 2 (la descomposición da directamente el valor decimal)."
        pasos = []
        digitos_destino = divisiones_sucesivas(valor, 10)["digitos"]

    destino = descomponer(digitos_destino, destino_base)
    valor_destino = destino.pop("_valor")

    # Verificación: ambas descomposiciones deben valer lo mismo; int() es un contraste externo.
    contraste = int(digitos, base) == valor and int(digitos_destino, destino_base) == valor
    coinciden = valor == valor_destino

    for bloque in (origen, destino):
        bloque["notacion"] = notacion(bloque["digitos"], bloque["base"], negativo)
        if negativo:
            bloque["descomposicion_con_signo"] = f"−({bloque['descomposicion']})"

    if base == 2:
        igualdad_principal = (f"{origen['notacion']} = {signo_texto}({origen['descomposicion']}) = "
                              f"{signo_texto}({origen['suma_valores']}) = {destino['notacion']}"
                              if negativo else
                              f"{origen['notacion']} = {origen['descomposicion']} = "
                              f"{origen['suma_valores']} = {destino['notacion']}")
    else:
        igualdad_principal = (f"{origen['notacion']} = {signo_texto}({origen['descomposicion']})"
                              if negativo else
                              f"{origen['notacion']} = {origen['descomposicion']}")

    return {
        "base_origen": base,
        "base_destino": destino_base,
        "negativo": negativo,
        "nota_signo": (
            "El signo no forma parte de la notación posicional: se conserva el signo, se "
            "descompone el valor absoluto |N| y al final se antepone el signo."
            if negativo else None
        ),
        "notas": notas,
        "origen": origen,
        "destino": destino,
        "igualdad_principal": igualdad_principal,
        "metodo": metodo,
        "divisiones": pasos,
        "equivalencia": f"{origen['notacion']} = {destino['notacion']}",
        "verificacion": {
            "valor_origen": f"{signo_texto}{valor}",
            "valor_destino": f"{signo_texto}{valor_destino}",
            "coinciden": coinciden,
            "contraste_python": contraste,
            "texto": (
                f"Ambas descomposiciones valen {signo_texto}{valor} en base 10"
                + (" ✓" if coinciden else " ✗")
                + ". Contraste con int() de Python: "
                + ("coincide." if contraste else "NO coincide.")
            ),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════════════
# D. ERRORES NUMÉRICOS Y PUNTO FLOTANTE
# ═══════════════════════════════════════════════════════════════════════════════════════
#
# D.1 0.1 + 0.2 == 0.3 → False. La computadora guarda los números en BINARIO con 52 bits de
#     mantisa (IEEE 754, double). 0.1 en binario es 0.000110011001100… (periódico, como
#     1/3 = 0.333… en decimal): se guarda la fracción binaria más cercana y los redondeos de
#     0.1 y 0.2 no coinciden con el de 0.3.
# D.2 Épsilon de máquina: distancia entre 1.0 y el siguiente double = 2⁻⁵² ≈ 2.22·10⁻¹⁶.
# D.3 Overflow / underflow: se EJECUTAN de verdad y se captura lo que pasa EN ESTE EQUIPO;
#     el resultado (inf, excepción o aviso) depende del tipo y de la operación.
# D.4 Tipos de error con ejemplos calculados.
# D.5 Calculadora: Ea = |xv − xa|, Er = Ea/|xv|, Er% = Er·100 (Er no existe si xv = 0).
# D.6 Propagación (Taylor de primer orden): Δy ≈ f′(x)·Δx  vs  Δy real = f(x + Δx) − f(x).
# ───────────────────────────────────────────────────────────────────────────────────────

FUNCION_PROPAGACION_POR_DEFECTO = "sin(x) + x**2"


# D.1 ¿0.1 + 0.2 == 0.3? ────────────────────────────────────────────────────────────────
def demostrar_suma_decimal() -> Dict:
    """Ejecuta 0.1 + 0.2 == 0.3 y muestra el valor exacto que se guarda (Decimal)."""
    suma = 0.1 + 0.2
    return {
        "codigo": "0.1 + 0.2 == 0.3",
        "resultado": str(suma == 0.3),
        "repr_suma": repr(suma),
        "repr_03": repr(0.3),
        "valor_exacto_01": str(Decimal(0.1)),
        "valor_exacto_suma": str(Decimal(suma)),
        "valor_exacto_03": str(Decimal(0.3)),
        "hex_01": (0.1).hex(),
        "diferencia": repr(suma - 0.3),
        "comparacion_correcta": f"abs((0.1 + 0.2) - 0.3) < 1e-9 → {abs(suma - 0.3) < 1e-9}",
        "explicacion": (
            "IEEE 754 (double) guarda cada número como ±1.m × 2ᵉ con 52 bits de mantisa. "
            "0.1 en binario es 0.000110011001100… (periódico, como 1/3 = 0.333… en decimal), "
            "así que se guarda la fracción binaria más cercana, que no es exactamente 0.1. "
            "Los errores de redondeo de 0.1 y 0.2 se suman y el resultado cae en un double "
            "distinto del que representa a 0.3. Por eso los floats se comparan con una "
            "tolerancia y no con ==."
        ),
    }


# D.2 Épsilon de máquina ────────────────────────────────────────────────────────────────
def demostrar_epsilon() -> Dict:
    """numpy.finfo(float).eps y comprobaciones de que es el salto después de 1.0."""
    eps = float(np.finfo(float).eps)
    siguiente = float(np.nextafter(1.0, 2.0))
    return {
        "codigo": "numpy.finfo(float).eps",
        "valor": repr(eps),
        "potencia": "2⁻⁵² = " + repr(2.0 ** -52),
        "siguiente_de_1": repr(siguiente),
        "comprobaciones": [
            f"numpy.nextafter(1.0, 2.0) − 1.0 = {siguiente - 1.0!r}",
            f"1.0 + eps == 1.0 → {1.0 + eps == 1.0}",
            f"1.0 + eps/2 == 1.0 → {1.0 + eps / 2 == 1.0}  (eps/2 se pierde al redondear)",
        ],
        "explicacion": (
            "El épsilon de máquina es la distancia entre 1.0 y el siguiente double "
            "representable. Con 52 bits de mantisa ese salto es 2⁻⁵² ≈ 2.22·10⁻¹⁶. Mide la "
            "precisión relativa: cerca de 1.0 no existe ningún double entre 1.0 y 1.0 + eps."
        ),
    }


# D.3 Overflow y underflow (ejecutados en este equipo) ──────────────────────────────────
def experimento(titulo: str, codigo: str, accion: Callable, explicacion: str) -> Dict:
    """Ejecuta `accion` capturando el valor, la excepción y las advertencias que produzca."""
    with warnings.catch_warnings(record=True) as capturadas:
        warnings.simplefilter("always")
        # all="warn": NumPy avisa de overflow/underflow en vez de callarlo (por defecto
        # ignora el underflow). Así se ve qué ocurre realmente en esta máquina.
        with np.errstate(all="warn"):
            try:
                valor = accion()
                resultado, tipo, excepcion = str(valor), type(valor).__name__, None
            except (OverflowError, ZeroDivisionError, FloatingPointError, ValueError) as error:
                resultado, tipo = None, None
                excepcion = f"{type(error).__name__}: {error}"
    return {
        "titulo": titulo,
        "codigo": codigo,
        "resultado": resultado,
        "tipo": tipo,
        "excepcion": excepcion,
        "advertencias": [f"{w.category.__name__}: {w.message}" for w in capturadas],
        "explicacion": explicacion,
    }


def demostrar_desbordamientos() -> List[Dict]:
    """Overflow, subnormales y underflow con float de Python, float64 y float32."""
    return [
        experimento(
            "Overflow con NumPy (float64)", "numpy.float64(1e308) * 10",
            lambda: np.float64(1e308) * 10,
            "El resultado supera el mayor double (≈1.8·10³⁰⁸): NumPy devuelve inf y emite "
            "una advertencia RuntimeWarning.",
        ),
        experimento(
            "Overflow con float de Python", "1e308 * 10",
            lambda: 1e308 * 10,
            "La multiplicación de floats de Python también da inf, pero SIN aviso: el "
            "desbordamiento pasa desapercibido si no se comprueba.",
        ),
        experimento(
            "Overflow en math.exp", "math.exp(1000)",
            lambda: math.exp(1000),
            "El módulo math lanza OverflowError en lugar de devolver inf.",
        ),
        experimento(
            "Overflow en numpy.exp", "numpy.exp(1000.0)",
            lambda: np.exp(np.float64(1000.0)),
            "La misma operación con NumPy devuelve inf con advertencia: el comportamiento "
            "depende de la librería, no solo del número.",
        ),
        experimento(
            "Overflow en una potencia", "2.0 ** 10000",
            lambda: 2.0 ** 10000,
            "La potencia de floats de Python lanza OverflowError.",
        ),
        experimento(
            "Overflow en float32", "numpy.float32(3.4e38) * numpy.float32(10)",
            lambda: np.float32(3.4e38) * np.float32(10),
            "En float32 (32 bits) el máximo es ≈3.4·10³⁸: desborda mucho antes que float64.",
        ),
        experimento(
            "Número subnormal", "1e-320",
            lambda: 1e-320,
            f"1e-320 es menor que el menor double normal ({sys.float_info.min!r}): se guarda "
            "como SUBNORMAL, con menos bits significativos (pierde precisión).",
        ),
        experimento(
            "Pérdida de precisión de un subnormal", "1e-320 * 1e300",
            lambda: 1e-320 * 1e300,
            "Exactamente debería dar 1e-20; el resultado difiere desde el 5.º dígito porque "
            "1e-320 ya se había guardado con pocos bits.",
        ),
        experimento(
            "Underflow a cero (Python)", "5e-324 / 2",
            lambda: 5e-324 / 2,
            "5e-324 es el menor subnormal positivo; su mitad no es representable y se "
            "redondea a 0.0 sin ningún aviso.",
        ),
        experimento(
            "Underflow a cero (NumPy)", "numpy.float64(5e-324) / 2",
            lambda: np.float64(5e-324) / np.float64(2),
            "Con np.errstate(under='warn') NumPy sí avisa del underflow (por defecto lo ignora).",
        ),
        experimento(
            "Underflow en un producto", "numpy.float64(1e-200) * 1e-200",
            lambda: np.float64(1e-200) * np.float64(1e-200),
            "1e-400 está por debajo incluso de los subnormales: el resultado es 0.0.",
        ),
    ]


def describir_entorno() -> Dict:
    """Límites del double y versiones: los resultados de D.3 son de ESTE equipo."""
    info = sys.float_info
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "sistema": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "max_double": repr(info.max),
        "min_double_normal": repr(info.min),
        "min_subnormal": repr(float(np.finfo(float).smallest_subnormal)),
        "digitos_decimales": info.dig,
        "bits_mantisa": info.mant_dig - 1,
        "nota": (
            "Resultados obtenidos al ejecutar el código EN ESTE EQUIPO. Que una operación "
            "devuelva inf, lance una excepción o emita una advertencia depende del tipo "
            "(float de Python, float64, float32) y de la operación o librería: no es un "
            "comportamiento universal."
        ),
    }


# D.4 Tipos de error (con ejemplos calculados) ──────────────────────────────────────────
DISTINCION_TRUNCAMIENTO_MODELO = (
    "Truncamiento ≠ modelación: el truncamiento lo introduce el MÉTODO numérico al resolver "
    "una ecuación dada (se reduce con más términos o iteraciones); el error de modelación "
    "está en la PROPIA ecuación que se eligió para representar la realidad (solo se reduce "
    "cambiando de modelo)."
)


def tipos_de_error() -> List[Dict]:
    """Definición y ejemplo calculado de cada tipo de error."""
    # Inherente: el dato ya viene con error (medición) y se arrastra al resultado.
    radio, incertidumbre = 2.0, 0.05
    area_min = math.pi * (radio - incertidumbre) ** 2
    area_max = math.pi * (radio + incertidumbre) ** 2

    # Redondeo: sumar 0.1 diez veces.
    suma = 0.0
    for _ in range(10):
        suma += 0.1

    # Truncamiento: serie de Taylor de e cortada en 6 términos (k = 0..5).
    aproximacion_e = sum(1 / math.factorial(k) for k in range(6))

    # Modelo: péndulo con la aproximación sen θ ≈ θ (ángulos pequeños) a 60°.
    longitud, gravedad, angulo = 1.0, 9.81, math.radians(60)
    periodo_modelo = 2 * math.pi * math.sqrt(longitud / gravedad)
    # Período exacto del péndulo no lineal: T = 4·√(L/g)·K(k²), k = sen(θ₀/2).
    periodo_real = 4 * math.sqrt(longitud / gravedad) * float(ellipk(math.sin(angulo / 2) ** 2))

    return [
        {
            "tipo": "Error inherente",
            "definicion": "Error que ya traen los datos de entrada (mediciones, constantes "
                          "aproximadas). El cálculo no lo crea, lo hereda.",
            "ejemplo": (f"Radio medido r = {radio} ± {incertidumbre} cm ⇒ el área πr² está "
                        f"entre {area_min:.4f} y {area_max:.4f} cm², aunque el cálculo sea exacto."),
        },
        {
            "tipo": "Error de redondeo",
            "definicion": "Error por guardar los números con una cantidad finita de dígitos "
                          "(52 bits de mantisa en un double).",
            "ejemplo": f"Sumar 0.1 diez veces da {suma!r} y no 1.0 (diferencia {1.0 - suma:.3g}).",
        },
        {
            "tipo": "Error de truncamiento",
            "definicion": "Error del MÉTODO numérico al cortar un proceso infinito (serie, "
                          "límite, iteración) en un número finito de pasos. Disminuye al "
                          "tomar más términos o más iteraciones.",
            "ejemplo": (f"e ≈ 1 + 1 + 1/2! + 1/3! + 1/4! + 1/5! = {aproximacion_e:.10f}; "
                        f"error = {abs(math.e - aproximacion_e):.3e}. La cota Eb de Bisección "
                        "también es un error de truncamiento."),
        },
        {
            "tipo": "Overflow (desbordamiento)",
            "definicion": "El resultado supera el mayor número representable (≈1.8·10³⁰⁸ "
                          "en double): se obtiene inf o una excepción.",
            "ejemplo": "math.exp(1000) → OverflowError; numpy.float64(1e308)*10 → inf.",
        },
        {
            "tipo": "Underflow (subdesbordamiento)",
            "definicion": "El resultado es tan pequeño que se vuelve subnormal (pierde "
                          "precisión) o se redondea a 0.0.",
            "ejemplo": f"1e-200 * 1e-200 = {1e-200 * 1e-200!r}; 5e-324 / 2 = {5e-324 / 2!r}.",
        },
        {
            "tipo": "Error del modelo matemático",
            "definicion": "Error de la ECUACIÓN que describe el fenómeno (simplificaciones "
                          "físicas). No desaparece aunque se calcule con precisión infinita.",
            "ejemplo": (f"Péndulo de L = 1 m soltado a 60°: el modelo lineal (sen θ ≈ θ) da "
                        f"T = 2π√(L/g) = {periodo_modelo:.4f} s; el modelo no lineal da "
                        f"{periodo_real:.4f} s (error del modelo ≈ "
                        f"{100 * abs(periodo_real - periodo_modelo) / periodo_real:.1f} %)."),
        },
    ]


def demostracion_flotante() -> Dict:
    """D.1–D.4 juntas: todo se calcula al llamar a la función (no son textos fijos)."""
    return {
        "entorno": describir_entorno(),
        "suma_decimal": demostrar_suma_decimal(),
        "epsilon": demostrar_epsilon(),
        "experimentos": demostrar_desbordamientos(),
        "tipos_de_error": tipos_de_error(),
        "distincion": DISTINCION_TRUNCAMIENTO_MODELO,
    }


# D.5 Calculadora de errores ────────────────────────────────────────────────────────────
#   Ea = |xv − xa|      Er = Ea / |xv|      Er% = Er · 100
#   Ejemplo: xv = π, xa = 3.14 → Ea ≈ 0.0015927, Er ≈ 0.000507, Er% ≈ 0.0507 %
def calcular_errores(texto_xv: str, texto_xa: str) -> Dict:
    """Ea, Er y Er%. Si xv = 0, Er no está definido (no se divide entre cero)."""
    xv = leer_numero(texto_xv, "el valor verdadero xv", "xv")
    xa = leer_numero(texto_xa, "el valor aproximado xa", "xa")
    error_absoluto = abs(xv - xa)
    salida = {
        "xv": xv,
        "xa": xa,
        "error_absoluto": error_absoluto,
        "detalle_absoluto": f"Ea = |xv − xa| = |{formatear(xv)} − ({formatear(xa)})| = {error_absoluto:.10g}",
    }
    if xv == 0:
        # No se divide entre cero ni se inventa un porcentaje.
        salida.update({
            "relativo_definido": False,
            "error_relativo": None,
            "error_porcentual": None,
            "mensaje_relativo": "Error relativo no definido: xv = 0 y Er = Ea/|xv| dividiría entre cero.",
        })
        return salida
    error_relativo = error_absoluto / abs(xv)
    salida.update({
        "relativo_definido": True,
        "error_relativo": error_relativo,
        "error_porcentual": error_relativo * 100,
        "detalle_relativo": f"Er = Ea/|xv| = {error_absoluto:.10g}/{abs(xv):.10g} = {error_relativo:.10g}",
        "detalle_porcentual": f"Er% = Er·100 = {error_relativo * 100:.10g} %",
    })
    return salida


# D.6 Propagación del error ─────────────────────────────────────────────────────────────
# Taylor: f(x + Δx) = f(x) + f′(x)·Δx + f″(ξ)·Δx²/2. Si se desprecia el término Δx² queda
# la aproximación de PRIMER ORDEN (la recta tangente):  Δy ≈ f′(x)·Δx.
# Ejemplo: f = sin(x) + x², x = 1, Δx = 0.01 → f′(x) = cos(x) + 2x = 2.5403;
#   Δy aprox = 0.025403, Δy real = 0.025461, diferencia ≈ 0.000058.
# Con Δx diez veces menor la diferencia baja ~100 veces (el error es de orden Δx²).
def valor_real(expresion: sp.Expr, x: float, descripcion: str) -> float:
    """Evalúa una expresión SymPy en x y exige un número real finito."""
    valor = sp.N(expresion.subs(X, sp.Float(x)), 17)
    if valor.has(sp.zoo, sp.nan, sp.oo, -sp.oo) or not valor.is_real:
        raise ErrorNumerico(f"{descripcion} no está definida en x = {formatear(x)}.", "x")
    resultado = float(valor)
    if not math.isfinite(resultado):
        raise ErrorNumerico(f"{descripcion} no es finita en x = {formatear(x)}.", "x")
    return resultado


def propagar_error(texto_funcion: str, texto_x: str, texto_dx: str) -> Dict:
    """f′(x) simbólica, Δy ≈ f′(x)·Δx, Δy real = f(x+Δx) − f(x) y su diferencia."""
    funcion = analizar_funcion(texto_funcion or FUNCION_PROPAGACION_POR_DEFECTO)
    x = leer_numero(texto_x, "x")
    dx = leer_numero(texto_dx, "Δx", "dx")

    # Derivada simbólica con SymPy (sin simplify(): con algunas expresiones tarda demasiado
    # y diff ya da un resultado legible, p. ej. 2*x + cos(x)).
    derivada = funcion.derivada()
    try:
        fx = funcion(x)
    except ErrorDeEvaluacion as error:
        raise ErrorNumerico(f"f(x) no está definida: {error.mensaje}", "x")
    try:
        fx_dx = funcion(x + dx)
    except ErrorDeEvaluacion as error:
        raise ErrorNumerico(f"f(x + Δx) no está definida: {error.mensaje}", "dx")
    derivada_en_x = valor_real(derivada, x, "La derivada f′(x)")

    dy_aprox = derivada_en_x * dx          # aproximación lineal (diferencial)
    dy_real = fx_dx - fx                    # cambio verdadero
    diferencia = abs(dy_real - dy_aprox)
    return {
        "funcion": funcion.texto,
        "avisos": list(funcion.avisos),
        "derivada": sp.sstr(derivada),
        "derivada_latex": sp.latex(derivada),
        "funcion_latex": sp.latex(funcion.expresion),
        "x": x,
        "dx": dx,
        "fx": fx,
        "fx_dx": fx_dx,
        "derivada_en_x": derivada_en_x,
        "dy_aprox": dy_aprox,
        "dy_real": dy_real,
        "diferencia": diferencia,
        "diferencia_relativa": (diferencia / abs(dy_real)) if dy_real != 0 else None,
        "nota": (
            "Δy ≈ f′(x)·Δx es una aproximación de PRIMER ORDEN (la recta tangente). Desprecia "
            "los términos de orden Δx², así que funciona mejor cuanto más pequeño es Δx."
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════════════
# EJECUCIÓN: abre la calculadora de consola (los menús están en
# backend/programa_4/modulos/modulo_metodos_numericos.py y llaman a las funciones de arriba)
# ═══════════════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Si la salida se redirige a un archivo en Windows (cp1252), los símbolos ², ≤, ε, ₁₀...
    # romperían el programa: se fuerza UTF-8.
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    # Los menús importan "Programa7_GrupoX": se registra este mismo archivo con ese nombre
    # para no cargarlo dos veces.
    sys.modules.setdefault("Programa7_GrupoX", sys.modules[__name__])
    import main as calculadora  # noqa: E402
    from modulos import modulo_metodos_numericos  # noqa: E402

    try:
        if "--directo" in sys.argv:
            modulo_metodos_numericos.iniciar_modulo()
        else:
            calculadora.main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nPrograma finalizado por el usuario.")
