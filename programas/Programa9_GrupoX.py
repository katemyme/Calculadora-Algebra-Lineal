"""PROGRAMA 9 – Método abierto: búsqueda de raíces por Newton-Raphson.

Aproxima una raíz de f(x) = 0 a partir de un valor inicial x0 con la fórmula
x_(i+1) = x_i − f(x_i)/f'(x_i). SymPy interpreta f(x) y obtiene f'(x), NumPy realiza las
evaluaciones, Pandas organiza la tabla y Matplotlib dibuja la gráfica.

Funciones principales:
- Lectura y validación de f(x), x0, tolerancia εs (%) y número máximo de iteraciones.
- Derivada simbólica f'(x) con SymPy.
- Newton-Raphson programado por el equipo: control de derivada nula o casi nula, valores
  no finitos, error aproximado εa (%) y residuo |f(x)|.
- Tabla de iteraciones (Pandas), gráfica con rectas tangentes (Matplotlib) y menú de consola.
- Contraste opcional con scipy.optimize.newton (no se usa para calcular la raíz).

Ejecución (desde la raíz del repositorio):
    python programas/Programa9_GrupoX.py            → menú principal (opción 7)
    python programas/Programa9_GrupoX.py --directo  → entra directo a Newton-Raphson

Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

import base64
import io
import math
import sys
import warnings
from pathlib import Path
from typing import Callable, Dict, List, Optional

try:
    import numpy as np
    import pandas as pd
    import sympy as sp
except ModuleNotFoundError as error:
    if __name__ != "__main__":
        raise
    print(f"Falta la librería '{error.name}'. Instale las dependencias con:")
    print("    python -m pip install -r backend/requirements.txt")
    sys.exit(1)

# El lector seguro de f(x) (sin eval) y el menú principal están en backend/programa_4.
RUTA_CALCULADORA = Path(__file__).resolve().parents[1] / "backend" / "programa_4"
if str(RUTA_CALCULADORA) not in sys.path:
    sys.path.insert(0, str(RUTA_CALCULADORA))

from modulos.numericos.parser_seguro import (  # noqa: E402
    ErrorNumerico,
    analizar_funcion,
    formatear,
    leer_entero,
    leer_numero,
)

X = sp.Symbol("x", real=True)  # variable simbólica de f(x)

TOLERANCIA_POR_DEFECTO = "0.0001"  # εs en porcentaje
MAX_ITER_POR_DEFECTO = "50"
MAX_ITER_PERMITIDO = 1000
DERIVADA_MINIMA = 1e-10      # |f'(xi)| menor que esto se considera nula
LIMITE_DIVERGENCIA = 1e15    # |xi| mayor que esto se considera divergencia
RESIDUO_ACEPTABLE = 1e-6     # residuo que respalda una raíz aproximada
PUNTOS_GRAFICA = 1000
MAX_TANGENTES = 8            # rectas tangentes que se dibujan


# ---------------------------------------------------------------------------
# Casos de prueba obligatorios y ejemplos adicionales
# ---------------------------------------------------------------------------
CASOS_NEWTON: List[Dict] = [
    {
        "id": "caso1_convergencia",
        "nombre": "Caso 1 · Convergencia",
        "descripcion": (
            "f(x) = x³ − 2x − 5 con x₀ = 2. Newton-Raphson converge en pocas iteraciones; "
            "se reportan la aproximación, el error alcanzado y el residuo."
        ),
        "funcion": "x**3 - 2*x - 5",
        "x0": "2",
        "tolerancia": "0.0001",
        "max_iter": "50",
    },
    {
        "id": "caso2_derivada_nula",
        "nombre": "Caso 2 · Derivada nula",
        "descripcion": (
            "f(x) = x² − 4 con x₀ = 0: f′(0) = 0, la recta tangente es horizontal y no corta "
            "el eje x. El programa se detiene sin dividir entre cero."
        ),
        "funcion": "x**2 - 4",
        "x0": "0",
        "tolerancia": "0.0001",
        "max_iter": "50",
    },
    {
        "id": "caso3_sin_convergencia",
        "nombre": "Caso 3 · No alcanza el criterio",
        "descripcion": (
            "f(x) = x³ − 2x + 2 con x₀ = 0: las aproximaciones oscilan 0 → 1 → 0 → 1… y se "
            "agota el máximo de iteraciones sin cumplir la tolerancia."
        ),
        "funcion": "x**3 - 2*x + 2",
        "x0": "0",
        "tolerancia": "0.0001",
        "max_iter": "20",
    },
]

EJEMPLOS_ADICIONALES: List[Dict] = [
    {
        "id": "extra_coseno",
        "nombre": "cos(x) − x · x₀ = 1",
        "descripcion": "Converge a la raíz de cos(x) = x (≈ 0.739085) en pocas iteraciones.",
        "funcion": "cos(x) - x",
        "x0": "1",
        "tolerancia": "0.0001",
        "max_iter": "50",
    },
    {
        "id": "extra_casi_nula",
        "nombre": "Derivada casi nula · x₀ = 1e-12",
        "descripcion": (
            "f(x) = x² − 4 con x₀ = 10⁻¹²: |f′(x₀)| = 2·10⁻¹² < 10⁻¹⁰. Dividir daría un salto "
            "enorme (x₁ ≈ 2·10¹²), así que el programa se detiene."
        ),
        "funcion": "x**2 - 4",
        "x0": "1e-12",
        "tolerancia": "0.0001",
        "max_iter": "50",
    },
    {
        "id": "extra_se_aleja",
        "nombre": "Se aleja de la raíz · atan(x), x₀ = 2",
        "descripcion": (
            "Las aproximaciones se alejan de la raíz x = 0 (2 → −3.5 → 13.9 → −279 → …) y la "
            "tangente se vuelve casi horizontal: el programa se detiene sin dar un resultado "
            "engañoso."
        ),
        "funcion": "atan(x)",
        "x0": "2",
        "tolerancia": "0.0001",
        "max_iter": "50",
    },
]

FUNDAMENTO = (
    "MÉTODO DE NEWTON-RAPHSON (método abierto).\n"
    "    Desde x₀ se traza la recta tangente a f en (xᵢ, f(xᵢ)); su corte con el eje x es\n"
    "    la nueva aproximación:  xᵢ₊₁ = xᵢ − f(xᵢ)/f′(xᵢ)\n"
    "  ERROR APROXIMADO.\n"
    "    εa(%) = |(xᵢ₊₁ − xᵢ)/xᵢ₊₁|·100;  si xᵢ₊₁ = 0 se usa el error absoluto |xᵢ₊₁ − xᵢ|\n"
    "  CRITERIO DE PARADA.\n"
    "    Se detiene cuando εa ≤ εs (tolerancia) o al completar Nmax iteraciones.\n"
    "    Se informa el residuo |f(x)|: cumplir εa ≤ εs no garantiza por sí solo una raíz.\n"
    "  CONDICIONES DE FALLO.\n"
    "    f′(xᵢ) = 0 o casi 0 (|f′| < 1e-10): tangente horizontal, no se divide.\n"
    "    Valores no finitos o |xᵢ| > 1e15: divergencia.  Oscilación: se agota Nmax."
)


# ---------------------------------------------------------------------------
# Lectura y validación de datos
# ---------------------------------------------------------------------------
def preparar_funcion(texto_funcion: str):
    """Interpreta f(x) con SymPy, deriva f'(x) y crea sus versiones numéricas (NumPy)."""
    funcion = analizar_funcion(texto_funcion)  # expresión SymPy validada (sin eval)
    if X not in funcion.expresion.free_symbols:
        raise ErrorNumerico("f(x) debe depender de x (por ejemplo x**2 - 4).", "funcion")
    derivada = sp.diff(funcion.expresion, X)
    f = sp.lambdify(X, funcion.expresion, modules="numpy")
    df = sp.lambdify(X, derivada, modules="numpy")
    return funcion, derivada, f, df


def evaluar(funcion_numerica: Callable, x: float) -> float:
    """Evalúa una función en x con NumPy; devuelve nan si no da un real finito."""
    with np.errstate(all="ignore"):
        try:
            valor = funcion_numerica(np.float64(x))
        except (ArithmeticError, ValueError, TypeError):
            return math.nan
    if np.iscomplexobj(valor):
        return math.nan
    valor = float(valor)
    return valor if math.isfinite(valor) else math.nan


def leer_datos(texto_funcion: str, texto_x0: str, texto_tolerancia: str,
               texto_max_iter: str) -> Dict:
    """Valida f(x), x0, εs (0 < εs < 100 %) y Nmax (1 a 1000); f(x0) debe existir."""
    funcion, derivada, f, df = preparar_funcion(texto_funcion)
    x0 = leer_numero(texto_x0, "x₀", "x0")
    tolerancia = leer_numero((texto_tolerancia or "").strip().rstrip("%"),
                             "la tolerancia εs", "tolerancia")
    max_iter = leer_entero(texto_max_iter, "el máximo de iteraciones", "max_iter")

    if not 0 < tolerancia < 100:
        raise ErrorNumerico(
            "La tolerancia εs es un porcentaje y debe cumplir 0 < εs < 100 "
            f"(se recibió {formatear(tolerancia)}).", "tolerancia")
    if not 1 <= max_iter <= MAX_ITER_PERMITIDO:
        raise ErrorNumerico(
            f"El máximo de iteraciones debe estar entre 1 y {MAX_ITER_PERMITIDO} "
            f"(se recibió {max_iter}).", "max_iter")
    if math.isnan(evaluar(f, x0)):
        raise ErrorNumerico(
            f"f(x₀) no está definida o no es finita en x₀ = {formatear(x0)}: "
            "elija otro valor inicial.", "x0")

    return {"funcion": funcion, "derivada": derivada, "f": f, "df": df,
            "x0": x0, "tolerancia": tolerancia, "max_iter": max_iter}


# ---------------------------------------------------------------------------
# Algoritmo de Newton-Raphson (programado por el equipo)
# ---------------------------------------------------------------------------
def _finito(valor: Optional[float]) -> Optional[float]:
    """El número si es finito; None si no (JSON no admite nan ni inf)."""
    return float(valor) if valor is not None and math.isfinite(valor) else None


def error_aproximado(x_anterior: float, x_nuevo: float, tolerancia: float):
    """εa (%) relativo; si x_nuevo = 0 usa el error absoluto para no dividir entre cero."""
    if x_nuevo != 0:
        error = abs((x_nuevo - x_anterior) / x_nuevo) * 100
        return error, "relativo", error <= tolerancia
    error = abs(x_nuevo - x_anterior)
    return error, "absoluto", error <= tolerancia / 100


def metodo_newton_raphson(f: Callable, df: Callable, x0: float, tolerancia: float,
                          max_iter: int) -> Dict:
    """Aplica xᵢ₊₁ = xᵢ − f(xᵢ)/f′(xᵢ) hasta cumplir εa ≤ εs o llegar a Nmax."""
    filas: List[Dict] = []
    xi = x0
    estado = "max_iteraciones"

    for i in range(max_iter):
        fxi, dfxi = evaluar(f, xi), evaluar(df, xi)
        fila = {"i": i, "xi": xi, "fxi": _finito(fxi), "dfxi": _finito(dfxi),
                "x_siguiente": None, "error": None, "tipo_error": None}
        filas.append(fila)

        # f o f' no existen en xi (fuera del dominio o desbordamiento).
        if math.isnan(fxi) or math.isnan(dfxi):
            estado = "fuera_de_dominio"
            break
        # Antes de dividir: f'(xi) no puede ser cero ni demasiado cercana a cero.
        if abs(dfxi) < DERIVADA_MINIMA:
            estado = "derivada_nula"
            break

        x_siguiente = xi - fxi / dfxi  # fórmula de Newton-Raphson
        if not math.isfinite(x_siguiente):
            estado = "divergencia"
            break

        error, tipo, cumple = error_aproximado(xi, x_siguiente, tolerancia)
        fila.update({"x_siguiente": x_siguiente, "error": _finito(error), "tipo_error": tipo})
        xi = x_siguiente

        if abs(xi) > LIMITE_DIVERGENCIA:
            estado = "divergencia"
            break
        if cumple:
            estado = "convergencia"
            break

    completas = [fila for fila in filas if fila["x_siguiente"] is not None]
    return {"estado": estado, "filas": filas, "iteraciones": len(completas),
            "aproximacion": xi, "ultima": completas[-1] if completas else None}


# ---------------------------------------------------------------------------
# Reporte de resultados (lo usan la consola y la web)
# ---------------------------------------------------------------------------
TITULOS_ESTADO = {
    "convergencia": "Convergencia alcanzada",
    "derivada_nula": "Derivada nula o cercana a cero",
    "max_iteraciones": "Máximo de iteraciones sin cumplir la tolerancia",
    "divergencia": "Comportamiento divergente",
    "fuera_de_dominio": "La aproximación salió del dominio de f",
}

_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def x_sub(i: int) -> str:
    """x₀, x₁, … para los mensajes."""
    return "x" + str(i).translate(_SUBINDICES)


def cifras_significativas(tolerancia: float) -> int:
    """Cifras que garantiza εs según Scarborough: εs = 0.5·10^(2−n) %."""
    return max(1, min(15, math.floor(2 - math.log10(tolerancia / 0.5))))


def texto_error(error: Optional[float], tipo: Optional[str]) -> str:
    """Error para mostrar: εa en % o el error absoluto cuando xᵢ₊₁ = 0."""
    if tipo is None:
        return "—"
    if error is None:
        return "no finito"
    return f"{error:.4g} %" if tipo == "relativo" else f"{error:.4g} (abs.)"


def mensaje_estado(estado: str, resultado: Dict, tolerancia: float, max_iter: int) -> str:
    """Explica por qué terminó el proceso."""
    ultima, fila = resultado["ultima"], resultado["filas"][-1]
    nombre = x_sub(fila["i"])
    if estado == "convergencia":
        k = resultado["iteraciones"]
        if ultima["tipo_error"] == "absoluto":
            return (f"Convergencia en la iteración {k}: como xᵢ₊₁ = 0 se usó el error absoluto "
                    f"|xᵢ₊₁ − xᵢ| = {ultima['error']:.3g} ≤ εs/100 = {tolerancia / 100:g}.")
        return (f"Convergencia en la iteración {k}: εa = {ultima['error']:.3g} % ≤ "
                f"εs = {tolerancia:g} %.")
    if estado == "derivada_nula":
        texto = (f"Se detuvo antes de dividir: f′({nombre}) = {fila['dfxi']:.3g} en {nombre} = "
                 f"{fila['xi']:.6g} es nula o casi nula (|f′| < {DERIVADA_MINIMA:g}). La recta "
                 "tangente es (casi) horizontal y no corta el eje x de forma útil.")
        if fila["fxi"] == 0:
            texto += f" Además f({nombre}) = 0: {nombre} ya anula la función (posible raíz múltiple)."
        return texto
    if estado == "max_iteraciones":
        ultimo = texto_error(ultima["error"], ultima["tipo_error"])
        return (f"Se completaron las {max_iter} iteraciones sin cumplir la tolerancia (último "
                f"error: {ultimo}; εs = {tolerancia:g} %). El método no alcanzó el criterio de "
                "convergencia: la última aproximación no debe tomarse como raíz.")
    if estado == "divergencia":
        return (f"Divergencia en la iteración {fila['i'] + 1}: xᵢ₊₁ dejó de ser finito o superó "
                f"{LIMITE_DIVERGENCIA:g} en valor absoluto. Las aproximaciones se alejan de la "
                "raíz; pruebe con otro x₀.")
    return (f"En {nombre} = {fila['xi']:.6g}, f({nombre}) o f′({nombre}) no es un número real "
            "finito (fuera del dominio o desbordamiento): no se puede continuar. Pruebe con otro x₀.")


def resolver_newton_raphson(texto_funcion: str, texto_x0: str,
                            texto_tolerancia: str = TOLERANCIA_POR_DEFECTO,
                            texto_max_iter: str = MAX_ITER_POR_DEFECTO,
                            comparar_scipy: bool = True) -> Dict:
    """Función principal (consola y web): valida, ejecuta el método y arma el reporte."""
    datos = leer_datos(texto_funcion, texto_x0, texto_tolerancia, texto_max_iter)
    tolerancia, max_iter = datos["tolerancia"], datos["max_iter"]
    resultado = metodo_newton_raphson(datos["f"], datos["df"], datos["x0"], tolerancia, max_iter)
    estado, ultima = resultado["estado"], resultado["ultima"]
    convergio = estado == "convergencia"

    # Residuo: la función original evaluada en la aproximación final.
    aproximacion = _finito(resultado["aproximacion"])
    residuo = _finito(abs(evaluar(datos["f"], aproximacion))) if aproximacion is not None else None

    # La aproximación se muestra con las cifras que respalda la tolerancia (sin exceso).
    if aproximacion is None:
        texto_aprox, detalle = "no finita", "La última aproximación no es un número finito."
    elif convergio and ultima["tipo_error"] == "relativo":
        cifras = cifras_significativas(tolerancia)
        texto_aprox = f"{aproximacion:.{cifras}g}"
        detalle = (f"{cifras} cifras significativas según εs = {tolerancia:g} % (criterio de "
                   f"Scarborough). Valor calculado: {aproximacion:.10g}.")
    elif convergio:
        texto_aprox = f"{aproximacion:.6g}"
        detalle = "Convergió con el error absoluto porque xᵢ₊₁ = 0."
    else:
        texto_aprox = f"{aproximacion:.6g}"
        detalle = "No cumple el criterio de parada: no se reporta como raíz."

    if residuo is None:
        nota_residuo = "No se puede evaluar f en la última aproximación."
    elif not convergio:
        nota_residuo = "Solo como referencia: el proceso no cumplió el criterio de parada."
    elif residuo <= RESIDUO_ACEPTABLE:
        nota_residuo = f"|f(x)| ≤ {RESIDUO_ACEPTABLE:g}: el residuo respalda la raíz aproximada."
    else:
        nota_residuo = (f"Atención: se cumplió εa ≤ εs, pero |f(x)| > {RESIDUO_ACEPTABLE:g}. El "
                        "criterio de error por sí solo no garantiza una raíz.")

    reporte = {
        "funcion": datos["funcion"].texto,
        "funcion_latex": sp.latex(datos["funcion"].expresion),
        "derivada": sp.sstr(datos["derivada"]),
        "derivada_latex": sp.latex(datos["derivada"]),
        "avisos": list(datos["funcion"].avisos),
        "x0": datos["x0"],
        "tolerancia": tolerancia,
        "max_iter": max_iter,
        "criterio_parada": (
            f"εa ≤ εs = {tolerancia:g} % (si xᵢ₊₁ = 0: |xᵢ₊₁ − xᵢ| ≤ {tolerancia / 100:g}) "
            f"o al completar Nmax = {max_iter} iteraciones. También se detiene si "
            f"|f′(xᵢ)| < {DERIVADA_MINIMA:g} o si los valores dejan de ser finitos."
        ),
        "estado": estado,
        "titulo_estado": TITULOS_ESTADO[estado],
        "convergio": convergio,
        "mensaje": mensaje_estado(estado, resultado, tolerancia, max_iter),
        "iteraciones": resultado["iteraciones"],
        "aproximacion": aproximacion,
        "aproximacion_texto": texto_aprox,
        "detalle_aproximacion": detalle,
        "error_final": ultima["error"] if ultima else None,
        "error_final_texto": texto_error(ultima["error"], ultima["tipo_error"]) if ultima else "—",
        "residuo": residuo,
        "residuo_texto": f"{residuo:.3g}" if residuo is not None else "no definido",
        "nota_residuo": nota_residuo,
        "filas": resultado["filas"],
        "contraste_scipy": None,
    }
    if comparar_scipy and convergio:
        reporte["contraste_scipy"] = comparar_con_scipy(datos["f"], datos["df"], datos["x0"],
                                                        aproximacion)
    return reporte


def comparar_con_scipy(f: Callable, df: Callable, x0: float, aproximacion: float) -> Dict:
    """Contraste opcional con scipy.optimize.newton; NO se usa para calcular la raíz."""
    nota = ("SciPy solo sirve de contraste: la aproximación del programa se obtiene con el "
            "algoritmo propio.")
    try:
        from scipy.optimize import newton as newton_scipy
    except ModuleNotFoundError:
        return {"disponible": False, "motivo": "SciPy no está instalado.", "nota": nota}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            raiz = float(newton_scipy(lambda x: evaluar(f, x), x0,
                                      fprime=lambda x: evaluar(df, x),
                                      tol=1e-12, maxiter=MAX_ITER_PERMITIDO))
    except (RuntimeError, ArithmeticError, ValueError) as error:
        return {"disponible": False, "motivo": f"SciPy no pudo calcular la raíz: {error}",
                "nota": nota}
    if not math.isfinite(raiz):
        return {"disponible": False, "motivo": "SciPy devolvió un valor no finito.", "nota": nota}
    diferencia = abs(raiz - aproximacion)
    return {"disponible": True, "raiz": raiz, "raiz_texto": f"{raiz:.10g}",
            "diferencia": diferencia, "diferencia_texto": f"{diferencia:.3g}", "nota": nota}


# ---------------------------------------------------------------------------
# Tabla de iteraciones (Pandas)
# ---------------------------------------------------------------------------
COLUMNAS_TABLA = ["i", "xᵢ", "f(xᵢ)", "f′(xᵢ)", "xᵢ₊₁", "Error aprox. εa"]


def numero(valor: Optional[float], cifras: int, vacio: str = "—") -> str:
    """Número con las cifras significativas indicadas."""
    return vacio if valor is None else f"{valor:.{cifras}g}"


def construir_tabla(filas: List[Dict]) -> pd.DataFrame:
    """Organiza las iteraciones en un DataFrame de Pandas, listo para mostrar."""
    registros = [
        [fila["i"], numero(fila["xi"], 10), numero(fila["fxi"], 6, "no definido"),
         numero(fila["dfxi"], 6, "no definido"), numero(fila["x_siguiente"], 10),
         texto_error(fila["error"], fila["tipo_error"])]
        for fila in filas
    ]
    return pd.DataFrame(registros, columns=COLUMNAS_TABLA)


def tabla_json(tabla: pd.DataFrame) -> Dict:
    """Columnas y filas del DataFrame para la web."""
    return {"columnas": list(tabla.columns), "filas": tabla.astype(str).values.tolist()}


# ---------------------------------------------------------------------------
# Gráfica: f(x), eje x, rectas tangentes y aproximaciones (Matplotlib)
# ---------------------------------------------------------------------------
COLOR_CURVA = "#6d3beb"
COLOR_TANGENTE = "#f59e0b"
COLOR_PUNTO = "#1d4ed8"
COLOR_APROXIMACION = "#dc2626"


def evaluar_vector(funcion_numerica: Callable, xs: np.ndarray) -> np.ndarray:
    """Evalúa f en muchos puntos con NumPy; lo no definido queda como nan."""
    with np.errstate(all="ignore"):
        try:
            ys = np.asarray(funcion_numerica(xs), dtype=float)
        except (ArithmeticError, ValueError, TypeError):
            ys = np.array([evaluar(funcion_numerica, x) for x in xs])
    if ys.shape != xs.shape:  # f constante en un tramo
        ys = np.full_like(xs, float(ys))
    ys[~np.isfinite(ys)] = np.nan
    return ys


def datos_grafica(reporte: Dict) -> Dict:
    """Ventana, curva de f y rectas tangentes de las primeras iteraciones."""
    _, _, f, _ = preparar_funcion(reporte["funcion"])
    filas = reporte["filas"][:MAX_TANGENTES]
    x0, aproximacion = reporte["x0"], reporte["aproximacion"]

    # Ventana en x: x0 y las aproximaciones cercanas (las que se disparan quedan fuera).
    puntos = [x0] + [fila["x_siguiente"] for fila in filas if fila["x_siguiente"] is not None]
    if aproximacion is not None:
        puntos.append(aproximacion)
    visibles = [p for p in puntos if abs(p - x0) <= 100 * max(1.0, abs(x0))]
    a, b = min(visibles), max(visibles)
    margen = max(0.25 * (b - a), 1.0) if b > a else 3.0
    x_min, x_max = a - margen, b + margen

    xs = np.linspace(x_min, x_max, PUNTOS_GRAFICA)
    ys = evaluar_vector(f, xs)

    # Rango en y: toda la curva, salvo que una asíntota lo dispare (se recorta).
    validos = ys[np.isfinite(ys)]
    y_bajo, y_alto = (float(np.min(validos)), float(np.max(validos))) if validos.size else (-1.0, 1.0)
    if validos.size:
        p_bajo, p_alto = (float(v) for v in np.percentile(validos, [2, 98]))
        if y_alto - y_bajo > 20 * max(p_alto - p_bajo, 1e-12):
            y_bajo, y_alto = p_bajo, p_alto
    alturas = [0.0] + [fila["fxi"] for fila in filas
                       if fila["fxi"] is not None and x_min <= fila["xi"] <= x_max]
    y_bajo, y_alto = min(y_bajo, *alturas), max(y_alto, *alturas)
    if y_alto - y_bajo < 1e-12:
        y_bajo, y_alto = y_bajo - 1, y_alto + 1
    margen_y = 0.12 * (y_alto - y_bajo)
    y_min, y_max = y_bajo - margen_y, y_alto + margen_y

    # Se corta la curva en saltos bruscos con cambio de signo (asíntotas).
    with np.errstate(invalid="ignore"):
        salto = (np.abs(np.diff(ys)) > (y_max - y_min)) & (ys[:-1] * ys[1:] < 0)
    ys[1:][salto] = np.nan

    tangentes = []
    for fila in filas:
        xi, x_sig = fila["xi"], fila["x_siguiente"]
        if fila["fxi"] is None or fila["dfxi"] is None or not x_min <= xi <= x_max:
            continue
        if x_sig is None:  # derivada nula: tangente en toda la ventana
            tx = np.array([x_min, x_max])
        else:
            extra = max(0.15 * abs(x_sig - xi), 0.06 * (x_max - x_min))
            tx = np.clip([min(xi, x_sig) - extra, max(xi, x_sig) + extra], x_min, x_max)
        tangentes.append({
            "i": fila["i"], "xi": xi, "fxi": fila["fxi"], "x_siguiente": x_sig,
            "f_siguiente": _finito(evaluar(f, x_sig)) if x_sig is not None else None,
            "x": tx, "y": fila["fxi"] + fila["dfxi"] * (tx - xi),
        })

    if reporte["convergio"]:
        etiqueta_final = f"Raíz aproximada x ≈ {reporte['aproximacion_texto']}"
    else:
        etiqueta_final = "Última aproximación (no es raíz)"
    return {
        "funcion": reporte["funcion"], "x": xs, "y": ys,
        "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max,
        "tangentes": tangentes,
        "aproximacion": aproximacion if aproximacion is not None and x_min <= aproximacion <= x_max else None,
        "etiqueta_final": etiqueta_final,
        "fuera_de_ventana": len(visibles) < len(puntos),
    }


def dibujar_grafica(ejes, datos: Dict) -> None:
    """Dibuja f(x), el eje x, las tangentes y las aproximaciones en unos ejes de Matplotlib."""
    ejes.plot(datos["x"], datos["y"], color=COLOR_CURVA, linewidth=2.2,
              label=f"f(x) = {datos['funcion']}")
    ejes.axhline(0, color="#334155", linewidth=1.1, label="Eje x (y = 0)")

    etiquetados: List[float] = []
    ancho = datos["x_max"] - datos["x_min"]

    def etiquetar(x: float, indice: int) -> None:
        # Nombre xᵢ bajo el eje, solo si no queda encima de otro.
        if datos["x_min"] <= x <= datos["x_max"] and all(abs(x - e) > 0.04 * ancho for e in etiquetados):
            ejes.annotate(rf"$x_{{{indice}}}$", (x, 0), textcoords="offset points",
                          xytext=(0, -15), ha="center", fontsize=10, color="#0f172a")
            etiquetados.append(x)

    for k, t in enumerate(datos["tangentes"]):
        ejes.plot(t["x"], t["y"], linestyle="--", color=COLOR_TANGENTE, linewidth=1.4,
                  label="Rectas tangentes" if k == 0 else None)
        ejes.plot([t["xi"], t["xi"]], [0, t["fxi"]], linestyle=":", color="#94a3b8", linewidth=1)
        ejes.plot(t["xi"], t["fxi"], "o", color=COLOR_PUNTO, markersize=5.5, zorder=5,
                  label=r"$(x_i,\ f(x_i))$" if k == 0 else None)
        etiquetar(t["xi"], t["i"])
        if t["x_siguiente"] is not None:
            ejes.plot(t["x_siguiente"], 0, "s", color=COLOR_TANGENTE, markersize=5, zorder=5,
                      label=r"Aproximaciones $x_{i+1}$" if k == 0 else None)
            etiquetar(t["x_siguiente"], t["i"] + 1)

    if datos["aproximacion"] is not None:
        ejes.plot(datos["aproximacion"], 0, "o", color=COLOR_APROXIMACION, markersize=9,
                  markeredgecolor="white", zorder=6, label=datos["etiqueta_final"])
    if datos["fuera_de_ventana"]:
        ejes.text(0.01, 0.02, "Algunas aproximaciones quedan fuera de la ventana (se alejan).",
                  transform=ejes.transAxes, fontsize=8, color="#b91c1c")

    ejes.set_xlim(datos["x_min"], datos["x_max"])
    ejes.set_ylim(datos["y_min"], datos["y_max"])
    ejes.set_title(f"Newton-Raphson: f(x) = {datos['funcion']}", fontsize=12)
    ejes.set_xlabel("x")
    ejes.set_ylabel("f(x)")
    ejes.grid(True, alpha=0.3)
    ejes.legend(loc="best", fontsize=8.5)


def grafica_png(datos: Dict) -> str:
    """Genera la figura con Matplotlib y la devuelve como PNG en base64 (para la web)."""
    from matplotlib.figure import Figure

    figura = Figure(figsize=(9, 5.2), dpi=120)
    dibujar_grafica(figura.subplots(), datos)
    figura.tight_layout()
    buffer = io.BytesIO()
    figura.savefig(buffer, format="png")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def mostrar_grafica(datos: Dict) -> None:
    """Abre la gráfica en una ventana (o la guarda como PNG si no hay pantalla)."""
    import matplotlib
    import matplotlib.pyplot as plt

    figura, ejes = plt.subplots(figsize=(9, 5.5))
    dibujar_grafica(ejes, datos)
    figura.tight_layout()
    if matplotlib.get_backend().lower() == "agg":
        ruta = Path.cwd() / "grafica_newton_raphson.png"
        figura.savefig(ruta, dpi=130)
        print(f"  Gráfica guardada en: {ruta}")
    else:
        print("  (Cierre la ventana de la gráfica para continuar.)")
        plt.show()
    plt.close(figura)


# ---------------------------------------------------------------------------
# Interfaz de consola (opción 7 del menú principal)
# ---------------------------------------------------------------------------
LINEA = "─" * 78
OPCION_VOLVER = "3"

ARTE_ASCII = (
    "  xᵢ₊₁ = xᵢ − f(xᵢ)/f′(xᵢ)    MÓDULO: MÉTODO DE NEWTON-RAPHSON (Programa 9)\n"
    "  ───●──────●──── x          Raíz aproximada de f(x) = 0 desde un valor inicial x₀\n"
    "    xᵢ₊₁     xᵢ              Tabla (Pandas) · Gráfica con tangentes (Matplotlib)"
)

# Campo -> (pregunta, valor predeterminado mostrado al usuario).
PREGUNTAS = {
    "funcion": ("f(x) con sintaxis de SymPy (p. ej. x**3 - 2*x - 5)", None),
    "x0": ("Valor inicial x0", None),
    "tolerancia": ("Tolerancia εs en %", TOLERANCIA_POR_DEFECTO),
    "max_iter": ("Máximo de iteraciones Nmax", MAX_ITER_POR_DEFECTO),
}


def pedir(mensaje: str, por_defecto: Optional[str] = None) -> str:
    """Lee un dato; si se deja vacío usa el valor predeterminado (mostrado entre corchetes)."""
    sufijo = f" [{por_defecto}]" if por_defecto is not None else ""
    texto = input(f"  {mensaje}{sufijo}: ").strip()
    return texto if texto or por_defecto is None else por_defecto


def imprimir_reporte(r: Dict) -> None:
    """Muestra función, derivada, tabla, estado, aproximación, error y residuo."""
    print(f"\n{LINEA}\n  NEWTON-RAPHSON   f(x) = {r['funcion']}   x₀ = {formatear(r['x0'])}")
    print(f"  Tolerancia εs = {r['tolerancia']:g} %   ·   Nmax = {r['max_iter']}")
    print(f"  Criterio de parada: {r['criterio_parada']}\n{LINEA}")
    for aviso in r["avisos"]:
        print(f"  ⚠ {aviso}")
    print(f"  f(x)  = {r['funcion']}")
    print(f"  f′(x) = {r['derivada']}   (derivada simbólica con SymPy)\n")
    for linea in construir_tabla(r["filas"]).to_string(index=False).splitlines():
        print(f"  {linea}")

    print(f"\n  {'✓' if r['convergio'] else '✗'} Estado: {r['titulo_estado']}")
    print(f"    {r['mensaje']}")
    etiqueta = "Raíz aproximada  x ≈" if r["convergio"] else "Última aproximación x ="
    print(f"\n  {etiqueta} {r['aproximacion_texto']}")
    print(f"    {r['detalle_aproximacion']}")
    print(f"  Iteraciones realizadas: {r['iteraciones']} (Nmax = {r['max_iter']})")
    print(f"  Error alcanzado:        {r['error_final_texto']}")
    print(f"  Residuo |f(x)|:         {r['residuo_texto']}   → {r['nota_residuo']}")

    contraste = r.get("contraste_scipy")
    if contraste:
        if contraste["disponible"]:
            print(f"\n  Contraste opcional con scipy.optimize.newton: {contraste['raiz_texto']}"
                  f"   |diferencia| = {contraste['diferencia_texto']}")
        else:
            print(f"\n  Contraste opcional con SciPy: {contraste['motivo']}")


def ejecutar_en_consola(datos: Dict[str, str]) -> None:
    """Resuelve; si un dato es inválido explica el error y vuelve a pedir solo ese dato."""
    while True:
        try:
            reporte = resolver_newton_raphson(datos["funcion"], datos["x0"],
                                              datos["tolerancia"], datos["max_iter"])
            break
        except ErrorNumerico as error:
            print(f"  ✗ {error.mensaje}")
            campo = error.campo if error.campo in datos else "funcion"
            datos[campo] = pedir(*PREGUNTAS[campo])

    imprimir_reporte(reporte)
    if input("\n  ¿Mostrar la gráfica? (s/n) [s]: ").strip().lower() in ("", "s", "si", "sí"):
        mostrar_grafica(datos_grafica(reporte))


def mostrar_fundamento() -> None:
    """Opción 0: fórmula, error, criterio de parada y condiciones de fallo."""
    print(f"\n── FUNDAMENTO MATEMÁTICO ──\n  {FUNDAMENTO}")


def opcion_datos_propios() -> None:
    """Opción 1: pide f(x), x0, εs y Nmax (con valores predeterminados visibles)."""
    print("\n── NEWTON-RAPHSON CON DATOS PROPIOS ──")
    print("  Funciones: sin cos tan asin acos atan sinh cosh tanh exp log ln log10 sqrt abs;"
          " constantes pi, e; potencia ** (o ^)")
    print(f"  Predeterminados: εs = {TOLERANCIA_POR_DEFECTO} % y Nmax = {MAX_ITER_POR_DEFECTO}"
          " (Enter para usarlos).")
    ejecutar_en_consola({campo: pedir(*PREGUNTAS[campo]) for campo in PREGUNTAS})


def opcion_casos() -> None:
    """Opción 2: ejecuta uno de los casos de prueba precargados."""
    casos = CASOS_NEWTON + EJEMPLOS_ADICIONALES
    print("\n── CASOS DE PRUEBA ──")
    for numero_caso, caso in enumerate(casos, start=1):
        print(f"  {numero_caso}. {caso['nombre']}")
    eleccion = input(f"  Caso (1-{len(casos)}): ").strip()
    if not (eleccion.isdigit() and 1 <= int(eleccion) <= len(casos)):
        print("  ✗ Opción no válida.")
        return
    caso = casos[int(eleccion) - 1]
    print(f"\n  {caso['nombre']}: {caso['descripcion']}")
    ejecutar_en_consola({campo: caso[campo] for campo in PREGUNTAS})


def mostrar_menu() -> None:
    """Imprime las opciones del módulo."""
    print("\n  0. Ver fundamento matemático")
    print("  1. Resolver f(x) = 0 con datos propios")
    print("  2. Casos de prueba (convergencia, derivada nula, sin convergencia)")
    print(f"  {OPCION_VOLVER}. Volver al menú principal")


# Opción del menú -> función que la atiende (mismo patrón que MODULOS en main.py).
ACCIONES = {
    "0": mostrar_fundamento,
    "1": opcion_datos_propios,
    "2": opcion_casos,
}


def iniciar_modulo() -> None:
    """Muestra el arte del módulo y ejecuta su menú (opción 7 del menú principal)."""
    print()
    print(ARTE_ASCII)
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        if opcion == OPCION_VOLVER:
            break
        if opcion in ACCIONES:
            ACCIONES[opcion]()
        else:
            print("Opción no válida. Intente de nuevo.")


# ---------------------------------------------------------------------------
# Ejecución directa: abre el menú principal de la calculadora
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Con salida redirigida en Windows (cp1252) los símbolos εs, xᵢ… fallarían: se usa UTF-8.
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    # El menú importa "Programa9_GrupoX": se registra este archivo con ese nombre.
    sys.modules.setdefault("Programa9_GrupoX", sys.modules[__name__])
    import main as calculadora  # noqa: E402

    try:
        if "--directo" in sys.argv:
            iniciar_modulo()
        else:
            calculadora.main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nPrograma finalizado por el usuario.")
