"""PROGRAMA 9 – Métodos abiertos: Newton-Raphson, secante, derivadas numéricas y polinomios.

Aproxima raíces de f(x) = 0 a partir de un valor inicial x0 con Newton-Raphson,
x_(i+1) = x_i − f(x_i)/f'(x_i). SymPy interpreta f(x) y obtiene f'(x), NumPy realiza las
evaluaciones, Pandas organiza las tablas y Matplotlib dibuja las gráficas.

Secciones (temas de la Sesión 22):
    A. Newton-Raphson ......... error absoluto o relativo (%), paso a paso y convergencia
    B. Método de la secante ... sin derivada; comparación con Newton
    C. Derivadas numéricas .... hacia adelante, hacia atrás y central; error vs h
    D. Raíces de polinomios ... Horner, Newton, deflación y validación con numpy.roots
    E. Gráficas ............... f(x) con tangentes o secantes, error vs iteración, error vs h
    F. Interfaz de consola .... menú del módulo (opción 7 del menú principal)

Ejecución (desde la raíz del repositorio):
    python programas/Programa9_GrupoX.py            → menú principal (opción 7)
    python programas/Programa9_GrupoX.py --directo  → entra directo a este módulo

Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

import base64
import io
import math
import sys
import warnings
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

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

# Valores predeterminados (se muestran al usuario).
POR_DEFECTO = {
    "tipo_error": "relativo",
    "tolerancia_relativo": "0.0001",   # εs en %
    "tolerancia_absoluto": "0.0001",   # ε decimal
    "max_iter": "50",
    "h_newton": "1e-5",                # paso de la diferencia central usada en Newton
    "h_derivadas": "0.01",             # paso de la sección de derivadas numéricas
}
MAX_ITER_PERMITIDO = 1000
DERIVADA_MINIMA = 1e-10      # |f'(xi)| menor que esto se considera nula
LIMITE_DIVERGENCIA = 1e15    # |xi| mayor que esto se considera divergencia
RESIDUO_ACEPTABLE = 1e-6     # residuo que respalda una raíz aproximada
PUNTOS_GRAFICA = 1000
MAX_RECTAS = 8               # tangentes o secantes que se dibujan
GRADO_MAXIMO = 10
PASOS_H = [10.0 ** -k for k in range(1, 13)]        # h del análisis error vs h
ALTERNATIVAS_X0 = (1.0, -1.0, 0.5, -0.5, 2.0, -2.0)  # otros x0 si Newton falla (polinomios)


# ---------------------------------------------------------------------------
# Casos de prueba obligatorios y ejemplos de la clase (Sesión 22)
# ---------------------------------------------------------------------------
def _caso(id_, nombre, descripcion, funcion, x0, tipo="relativo", tolerancia="0.0001",
          max_iter="50", **extra) -> Dict:
    """Arma un caso precargado de Newton-Raphson."""
    return {"id": id_, "nombre": nombre, "descripcion": descripcion, "funcion": funcion,
            "x0": x0, "tipo_error": tipo, "tolerancia": tolerancia, "max_iter": max_iter, **extra}


CASOS_NEWTON: List[Dict] = [
    _caso("caso1_convergencia", "Caso 1 · Convergencia",
          "f(x) = x³ − 2x − 5 con x₀ = 2. Newton-Raphson converge en pocas iteraciones; se "
          "reportan la aproximación, el error alcanzado y el residuo.", "x**3 - 2*x - 5", "2"),
    _caso("caso2_derivada_nula", "Caso 2 · Derivada nula",
          "f(x) = x² − 4 con x₀ = 0: f′(0) = 0, la recta tangente es horizontal y no corta el "
          "eje x. El programa se detiene sin dividir entre cero.", "x**2 - 4", "0"),
    _caso("caso3_sin_convergencia", "Caso 3 · No alcanza el criterio",
          "f(x) = x³ − 2x + 2 con x₀ = 0: las aproximaciones oscilan 0 → 1 → 0 → 1… y se agota "
          "el máximo de iteraciones sin cumplir la tolerancia.", "x**3 - 2*x + 2", "0",
          max_iter="20"),
]

EJEMPLOS_ADICIONALES: List[Dict] = [
    _caso("extra_coseno", "cos(x) − x · x₀ = 1",
          "Converge a la raíz de cos(x) = x (≈ 0.739085) en pocas iteraciones.", "cos(x) - x", "1"),
    _caso("extra_casi_nula", "Derivada casi nula · x₀ = 1e-12",
          "f(x) = x² − 4 con x₀ = 10⁻¹²: |f′(x₀)| = 2·10⁻¹² < 10⁻¹⁰. Dividir daría un salto enorme "
          "(x₁ ≈ 2·10¹²), así que el programa se detiene.", "x**2 - 4", "1e-12"),
    _caso("extra_se_aleja", "Se aleja de la raíz · atan(x), x₀ = 2",
          "Las aproximaciones se alejan de la raíz x = 0 (2 → −3.5 → 13.9 → −279 → …) y la "
          "tangente se vuelve casi horizontal: el programa se detiene sin dar un resultado "
          "engañoso.", "atan(x)", "2"),
]

EJEMPLOS_CLASE: List[Dict] = [
    _caso("clase_ej1", "Clase · Ejemplo 1: e⁻ˣ − x",
          "Ejemplo 1 de la clase: x₀ = 0 y Eₐ < 10⁻⁴. Se detiene en la iteración 4 con "
          "x ≈ 0.567143 (Bisección en [0, 1] necesita 14).", "exp(-x) - x", "0",
          "absoluto", "0.0001"),
    _caso("clase_ej3", "Clase · Ejemplo 3: x¹⁰ − 1",
          "Ejemplo 3 de la clase: con x₀ = 0.5, f′(x₀) es muy pequeña y x₁ = 51.65 salta lejos; "
          "luego avanza despacio y cumple Eₐ < 10⁻⁴ en 42 iteraciones.", "x**10 - 1", "0.5",
          "absoluto", "0.0001", "60"),
    _caso("clase_doble", "Clase · Raíz doble: (x − 1)²",
          "Práctica 3: en una raíz doble f′(1) = 0 y la convergencia es lineal: el error se reduce "
          "a la mitad en cada paso (14 iteraciones con Eₐ < 10⁻⁴).", "(x - 1)**2", "2",
          "absoluto", "0.0001"),
    _caso("clase_ciclo_ok", "Clase · x³ − 2x + 2 con x₀ = −2",
          "Con x₀ = 0 hay un ciclo 0 ↔ 1; con x₀ = −2 sí converge a la raíz −1.769292.",
          "x**3 - 2*x + 2", "-2", "absoluto", "1e-6"),
    _caso("clase_tarea4", "Tarea 4 · eˣ − 3x con x₀ = 1",
          "Como f(1) = f′(1) = e − 3, el primer paso salta a x₁ = 0; luego converge a 0.619061.",
          "exp(x) - 3*x", "1", "absoluto", "1e-6"),
    _caso("clase_tarea7", "Tarea 7 · f′ por diferencia central",
          "x³ − 2x − 5 con x₀ = 2 y ε = 10⁻⁶, usando f′ ≈ [f(x + h) − f(x − h)]/(2h) con "
          "h = 10⁻⁵: se compara con la derivada analítica.", "x**3 - 2*x - 5", "2",
          "absoluto", "1e-6", derivada="central", h="1e-5"),
]

EJEMPLOS_SECANTE: List[Dict] = [
    {"id": "sec_practica2", "nombre": "Práctica 2 · cos(x) − x",
     "descripcion": "Secante con x₀ = 0.5, x₁ = 0.6 y Eₐ < 10⁻⁵ (la clase obtiene 4 iteraciones).",
     "funcion": "cos(x) - x", "x0": "0.5", "x1": "0.6", "tipo_error": "absoluto",
     "tolerancia": "1e-5", "max_iter": "50"},
    {"id": "sec_tarea1", "nombre": "Tarea 1 · x³ − 2x − 5",
     "descripcion": "Secante con x₀ = 2, x₁ = 3 y ε = 10⁻⁶; se compara con Newton desde x₀ = 2.",
     "funcion": "x**3 - 2*x - 5", "x0": "2", "x1": "3", "tipo_error": "absoluto",
     "tolerancia": "1e-6", "max_iter": "50"},
    {"id": "sec_exp", "nombre": "e⁻ˣ − x con x₀ = 0, x₁ = 1",
     "descripcion": "La función del Ejemplo 1 de la clase, ahora sin usar la derivada.",
     "funcion": "exp(-x) - x", "x0": "0", "x1": "1", "tipo_error": "absoluto",
     "tolerancia": "0.0001", "max_iter": "50"},
]

EJEMPLOS_DERIVADAS: List[Dict] = [
    {"id": "der_clase", "nombre": "Clase · x³ − 2x − 5 en x = 2",
     "descripcion": "Ejemplo de la clase con h = 0.01: adelante 10.0601, atrás 9.9401 y central "
                    "10.0001 frente al valor analítico f′(2) = 10.",
     "funcion": "x**3 - 2*x - 5", "x": "2", "h": "0.01"},
    {"id": "der_practica4", "nombre": "Práctica 4 · ln(x) en x = 1",
     "descripcion": "Con h = 0.1: adelante 0.9531 y central 1.0034 frente al valor analítico f′(1) = 1.",
     "funcion": "log(x)", "x": "1", "h": "0.1"},
    {"id": "der_seno", "nombre": "sin(x) en x = π/4",
     "descripcion": "Con h = 0.1 se compara con f′(π/4) = cos(π/4) ≈ 0.707107.",
     "funcion": "sin(x)", "x": "pi/4", "h": "0.1"},
]

EJEMPLOS_POLINOMIO: List[Dict] = [
    {"id": "pol_tarea6", "nombre": "Tarea 6 · x⁴ − 5x³ + 10x² − 10x + 4",
     "descripcion": "Newton con Horner y deflación desde x₀ = 0: raíces 1, 2 y 1 ± i (se validan "
                    "con numpy.roots).",
     "polinomio": "x**4 - 5*x**3 + 10*x**2 - 10*x + 4", "x0": "0", "tipo_error": "absoluto",
     "tolerancia": "1e-6", "max_iter": "50"},
    {"id": "pol_tarea3", "nombre": "Tarea 3 · x³ − 6x² + 11x − 6",
     "descripcion": "Raíces 1, 2 y 3, encontradas una por una con deflación desde x₀ = 0.",
     "polinomio": "x**3 - 6*x**2 + 11*x - 6", "x0": "0", "tipo_error": "absoluto",
     "tolerancia": "1e-6", "max_iter": "50"},
    {"id": "pol_clase", "nombre": "Clase · x⁵ − 4x⁴ + 5x³ − 6x + 4",
     "descripcion": "Polinomio del ejemplo de Horner y deflación de la clase: raíces 1, 2, −1 y 1 ± i.",
     "polinomio": "x**5 - 4*x**4 + 5*x**3 - 6*x + 4", "x0": "0", "tipo_error": "absoluto",
     "tolerancia": "1e-6", "max_iter": "50"},
]

FUNDAMENTO = (
    "NEWTON-RAPHSON (método abierto).\n"
    "    La tangente en (xᵢ, f(xᵢ)) corta el eje x en xᵢ₊₁ = xᵢ − f(xᵢ)/f′(xᵢ); requiere f′(xᵢ) ≠ 0.\n"
    "  ERRORES Y CRITERIO DE PARADA.\n"
    "    Eₐ = |xᵢ₊₁ − xᵢ| (absoluto, tolerancia decimal ε)   εₐ = |(xᵢ₊₁ − xᵢ)/xᵢ₊₁|·100 (relativo, εs en %).\n"
    "    Se detiene si el error elegido es menor que la tolerancia o al llegar a Nmax (no se mezclan % y decimales).\n"
    "    Al final se verifica el residuo |f(x)|: un error pequeño no garantiza por sí solo una raíz.\n"
    "  CONVERGENCIA.\n"
    "    Raíz simple y x₀ cercano: |Eᵢ₊₁| ≈ C·|Eᵢ|² (cuadrática). Raíz múltiple: lineal. Es local, no global.\n"
    "    Fallas: f′ ≈ 0, x₀ lejano, ciclos (x³ − 2x + 2 con x₀ = 0) o divergencia (atan(x) con x₀ = 2).\n"
    "  SECANTE. xᵢ₊₁ = xᵢ − f(xᵢ)(xᵢ₋₁ − xᵢ)/(f(xᵢ₋₁) − f(xᵢ)): no usa f′; convergencia superlineal (≈ 1.618).\n"
    "  DERIVADAS NUMÉRICAS. Adelante [f(x+h) − f(x)]/h y atrás [f(x) − f(x−h)]/h: O(h);\n"
    "    central [f(x+h) − f(x−h)]/(2h): O(h²). Con h muy pequeño domina el error de redondeo.\n"
    "  POLINOMIOS. Horner evalúa p(x) y p′(x); la deflación p(x)/(x − r) deja un polinomio de menor grado.\n"
    "  ÁNGULOS. Las funciones trigonométricas trabajan en radianes (pi/4 = 45°); en grados: sin(x*pi/180)."
)

AYUDA_FUNCIONES = ("  Funciones: sin cos tan asin acos atan sinh cosh tanh exp log ln log10 sqrt abs;"
                   " constantes pi, e; potencia ** (o ^)\n"
                   "  Las trigonométricas trabajan en radianes (x₀ = pi/4 equivale a 45°); para grados"
                   " escriba, por ejemplo, sin(x*pi/180).")


# ---------------------------------------------------------------------------
# Utilidades: formato de números y pasos
# ---------------------------------------------------------------------------
def _finito(valor: Optional[float]) -> Optional[float]:
    """El número si es finito; None si no (JSON no admite nan ni inf)."""
    return float(valor) if valor is not None and math.isfinite(valor) else None


def _cociente(a: Optional[float], b: Optional[float]) -> Optional[float]:
    """a/b si se puede calcular y es finito; None en otro caso."""
    if a is None or not b:
        return None
    try:
        return _finito(a / b)
    except (OverflowError, ZeroDivisionError):
        return None


def numero(valor: Optional[float], cifras: int = 10, vacio: str = "—") -> str:
    """Número con las cifras significativas indicadas."""
    return vacio if valor is None else f"{valor:.{cifras}g}"


def par(valor: Optional[float], cifras: int = 10) -> str:
    """Número en texto, entre paréntesis si es negativo."""
    texto = numero(valor, cifras, "no definido")
    return f"({texto})" if valor is not None and valor < 0 else texto


def tex_num(valor: Optional[float], cifras: int = 10) -> str:
    """Número en LaTeX: 1.25e-07 → 1.25 × 10⁻⁷."""
    if valor is None:
        return r"\text{no definido}"
    texto = f"{valor:.{cifras}g}"
    if "e" in texto:
        mantisa, exponente = texto.split("e")
        return f"{mantisa} \\times 10^{{{int(exponente)}}}"
    return texto


def tex_par(valor: Optional[float], cifras: int = 10) -> str:
    """Número en LaTeX, entre paréntesis si es negativo."""
    texto = tex_num(valor, cifras)
    return f"\\left({texto}\\right)" if valor is not None and valor < 0 else texto


_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_SUPERINDICES = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def x_sub(i: int) -> str:
    """x₀, x₁, … para los mensajes."""
    return "x" + str(i).translate(_SUBINDICES)


_MARCA = sp.Symbol("xvalor")


def sustituir(expresion: sp.Expr, valor: float) -> Tuple[str, str]:
    """La expresión con x reemplazada por el valor, sin evaluar (LaTeX y texto)."""
    expr = expresion.xreplace({X: _MARCA})
    v_tex, v_txt = tex_num(valor), numero(valor)
    tex = sp.latex(expr).replace(r"\left(xvalor \right)", f"\\left({v_tex}\\right)")
    texto = sp.sstr(expr).replace("(xvalor)", f"({v_txt})")
    return tex.replace("xvalor", f"\\left({v_tex}\\right)"), texto.replace("xvalor", f"({v_txt})")


def evaluacion(nombre: str, nombre_tex: str, expresion: sp.Expr, valor: float,
               resultado: Optional[float]) -> Tuple[str, str]:
    """f(2) = (2)**3 - 2*(2) - 5 = -1: la sustitución visible, en texto y en LaTeX."""
    texto, tex = f"{nombre}({numero(valor)})", f"{nombre_tex}\\left({tex_num(valor)}\\right)"
    if X in expresion.free_symbols:
        sust_tex, sust_texto = sustituir(expresion, valor)
        texto, tex = f"{texto} = {sust_texto}", f"{tex} = {sust_tex}"
    return f"{texto} = {numero(resultado, 8, 'no definido')}", f"{tex} = {tex_num(resultado, 8)}"


def paso(titulo: str, texto: str, tex: Optional[str] = None, nota: Optional[str] = None,
         tabla: Optional[Dict] = None) -> Dict:
    """Un paso del procedimiento (texto para la consola y LaTeX para la web)."""
    return {"titulo": titulo, "texto": texto, "tex": tex, "nota": nota, "tabla": tabla}


def tabla_json(tabla: pd.DataFrame) -> Dict:
    """Columnas y filas de un DataFrame de Pandas para la web."""
    return {"columnas": [str(c) for c in tabla.columns], "filas": tabla.astype(str).values.tolist()}


# ---------------------------------------------------------------------------
# Lectura y validación de datos
# ---------------------------------------------------------------------------
def preparar_funcion(texto: str, campo: str = "funcion"):
    """Interpreta f(x) con SymPy, deriva f'(x) y crea sus versiones numéricas (NumPy)."""
    funcion = analizar_funcion(texto, campo)  # expresión SymPy validada (sin eval)
    if X not in funcion.expresion.free_symbols:
        raise ErrorNumerico("La función debe depender de x (por ejemplo x**2 - 4).", campo)
    derivada = sp.diff(funcion.expresion, X)
    return (funcion, derivada, sp.lambdify(X, funcion.expresion, modules="numpy"),
            sp.lambdify(X, derivada, modules="numpy"))


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


TIPOS_ERROR = {"a": "absoluto", "abs": "absoluto", "absoluto": "absoluto",
               "r": "relativo", "rel": "relativo", "relativo": "relativo"}


def leer_criterio(tipo_error: Optional[str], tolerancia: Optional[str],
                  max_iter: Optional[str]) -> Dict:
    """Valida el tipo de error (absoluto o relativo %), la tolerancia y Nmax."""
    tipo = TIPOS_ERROR.get((tipo_error or POR_DEFECTO["tipo_error"]).strip().lower())
    if tipo is None:
        raise ErrorNumerico("El criterio de parada debe usar el error 'absoluto' o el 'relativo' (%).",
                            "tipo_error")
    texto = (tolerancia or "").strip() or POR_DEFECTO[f"tolerancia_{tipo}"]
    if tipo == "absoluto" and "%" in texto:
        raise ErrorNumerico("Con el error absoluto la tolerancia es decimal (p. ej. 0.0001), sin %: "
                            "no se mezclan porcentajes con decimales.", "tolerancia")
    valor = leer_numero(texto.rstrip("%").strip(), "la tolerancia", "tolerancia")
    if tipo == "relativo" and not 0 < valor < 100:
        raise ErrorNumerico("Con el error relativo la tolerancia εs es un porcentaje y debe cumplir "
                            f"0 < εs < 100 (se recibió {formatear(valor)}).", "tolerancia")
    if tipo == "absoluto" and valor <= 0:
        raise ErrorNumerico(f"La tolerancia ε debe ser mayor que 0 (se recibió {formatear(valor)}).",
                            "tolerancia")
    texto_n = (str(max_iter).strip() if max_iter is not None else "") or POR_DEFECTO["max_iter"]
    n = leer_entero(texto_n, "el máximo de iteraciones", "max_iter")
    if not 1 <= n <= MAX_ITER_PERMITIDO:
        raise ErrorNumerico(f"El máximo de iteraciones debe estar entre 1 y {MAX_ITER_PERMITIDO} "
                            f"(se recibió {n}).", "max_iter")
    return {"tipo": tipo, "tolerancia": valor, "max_iter": n}


def leer_paso(texto: Optional[str], campo: str = "h") -> float:
    """Valida el paso h > 0 de las diferencias finitas."""
    valor = leer_numero(texto, "el paso h", campo)
    if valor <= 0:
        raise ErrorNumerico(f"El paso h debe ser mayor que 0 (se recibió {formatear(valor)}).", campo)
    return valor


def texto_criterio(criterio: Dict, pendiente: str = "f′(xᵢ)") -> str:
    """Criterio de parada en palabras."""
    tol = criterio["tolerancia"]
    if criterio["tipo"] == "absoluto":
        regla = f"Eₐ = |xᵢ₊₁ − xᵢ| < ε = {tol:g}"
    else:
        regla = f"εₐ = |(xᵢ₊₁ − xᵢ)/xᵢ₊₁|·100 < εs = {tol:g} % (si xᵢ₊₁ = 0: Eₐ < {tol / 100:g})"
    return (f"{regla}, o al completar Nmax = {criterio['max_iter']} iteraciones. Se detiene antes si "
            f"|{pendiente}| < {DERIVADA_MINIMA:g} o si los valores dejan de ser finitos.")


# ---------------------------------------------------------------------------
# Errores y criterio de parada (Newton y secante)
# ---------------------------------------------------------------------------
def errores(x_anterior: float, x_nuevo: float) -> Tuple[float, Optional[float]]:
    """Eₐ = |xᵢ₊₁ − xᵢ| y εₐ(%) = |(xᵢ₊₁ − xᵢ)/xᵢ₊₁|·100 (None si xᵢ₊₁ = 0)."""
    absoluto = abs(x_nuevo - x_anterior)
    relativo = abs((x_nuevo - x_anterior) / x_nuevo) * 100 if x_nuevo != 0 else None
    return absoluto, relativo


def cumple_criterio(absoluto: float, relativo: Optional[float], criterio: Dict) -> bool:
    """Eₐ < ε (absoluto) o εₐ < εs (relativo); si xᵢ₊₁ = 0 se compara Eₐ < εs/100."""
    tol = criterio["tolerancia"]
    if criterio["tipo"] == "absoluto":
        return absoluto < tol
    return relativo < tol if relativo is not None else absoluto < tol / 100


def texto_comparacion(fila: Dict, criterio: Dict) -> str:
    """'Eₐ = 1.25e-07 < ε = 0.0001' o 'εₐ = 4.76 % ≥ εs = 0.0001 %'."""
    tol = criterio["tolerancia"]
    signo = "<" if fila["cumple"] else "≥"
    if criterio["tipo"] == "absoluto":
        return f"Eₐ = {numero(fila['error_abs'], 3, 'no finito')} {signo} ε = {tol:g}"
    if fila["error_rel"] is None:
        return (f"xᵢ₊₁ = 0, se usa Eₐ = {numero(fila['error_abs'], 3, 'no finito')} {signo} "
                f"εs/100 = {tol / 100:g}")
    return f"εₐ = {numero(fila['error_rel'], 3)} % {signo} εs = {tol:g} %"


# ═══════════════════════════════════════════════════════════════════════════
# A. NEWTON-RAPHSON
# ═══════════════════════════════════════════════════════════════════════════
def metodo_newton_raphson(f: Callable, df: Callable, x0: float, criterio: Dict) -> Dict:
    """Aplica xᵢ₊₁ = xᵢ − f(xᵢ)/f′(xᵢ) hasta cumplir el criterio de parada o llegar a Nmax."""
    filas: List[Dict] = []
    xi = x0
    estado = "max_iteraciones"

    for i in range(criterio["max_iter"]):
        fxi, dfxi = evaluar(f, xi), evaluar(df, xi)
        fila = {"i": i, "xi": xi, "fxi": _finito(fxi), "dfxi": _finito(dfxi), "x_siguiente": None,
                "error_abs": None, "error_rel": None, "cumple": False}
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

        absoluto, relativo = errores(xi, x_siguiente)
        cumple = cumple_criterio(absoluto, relativo, criterio)
        fila.update({"x_siguiente": x_siguiente, "error_abs": _finito(absoluto),
                     "error_rel": _finito(relativo), "cumple": cumple})
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


def derivada_central(f: Callable, h: float) -> Callable:
    """f′(x) ≈ [f(x + h) − f(x − h)]/(2h), para usar en Newton en lugar de la derivada analítica."""
    return lambda x: (evaluar(f, float(x) + h) - evaluar(f, float(x) - h)) / (2 * h)


# Paso a paso (como en la clase: evaluar, aplicar la fórmula, calcular errores y ¿detener?) ----
def pasos_error(fila: Dict, criterio: Dict, estado: str, es_ultima: bool) -> List[Dict]:
    """Pasos comunes a Newton y secante: Eₐ, εₐ(%) y decisión de parada."""
    i, xi, xs = fila["i"], fila["xi"], fila["x_siguiente"]
    a, b = f"x_{{{i + 1}}}", f"x_{{{i}}}"
    lista = [paso("Error absoluto",
                  f"Eₐ = |{x_sub(i + 1)} − {x_sub(i)}| = |{numero(xs)} − {par(xi)}| = "
                  f"{numero(fila['error_abs'], 6)}",
                  tex=f"E_a = |{a} - {b}| = |{tex_num(xs)} - {tex_par(xi)}| = "
                      f"{tex_num(fila['error_abs'], 6)}")]
    if fila["error_rel"] is None:
        lista.append(paso("Error relativo porcentual",
                          f"{x_sub(i + 1)} = 0: εₐ(%) no está definido (no se divide entre cero).",
                          nota="Se usa el error absoluto en su lugar."))
    else:
        diferencia = xs - xi
        lista.append(paso("Error relativo porcentual",
                          f"εₐ = |({x_sub(i + 1)} − {x_sub(i)})/{x_sub(i + 1)}|·100 = "
                          f"|{numero(diferencia, 6)}/{par(xs)}|·100 = {numero(fila['error_rel'], 6)} %",
                          tex=f"\\varepsilon_a = \\left|\\frac{{{a} - {b}}}{{{a}}}\\right| \\cdot 100 = "
                              f"\\left|\\frac{{{tex_num(diferencia, 6)}}}{{{tex_num(xs)}}}\\right| "
                              f"\\cdot 100 = {tex_num(fila['error_rel'], 6)}\\,\\%"))

    comparacion = texto_comparacion(fila, criterio)
    if fila["cumple"]:
        decision = f"Sí: {comparacion}. Se detiene; la aproximación es {x_sub(i + 1)} = {numero(xs)}."
    elif es_ultima and estado == "divergencia":
        decision = (f"No: {comparacion}, y |{x_sub(i + 1)}| > {LIMITE_DIVERGENCIA:g}: divergencia, "
                    "el proceso termina.")
    elif es_ultima and estado == "max_iteraciones":
        decision = (f"No: {comparacion}, y se alcanzó Nmax = {criterio['max_iter']}: el proceso "
                    "termina sin convergencia.")
    else:
        decision = f"No: {comparacion}. Se continúa con {x_sub(i + 1)} = {numero(xs)}."
    lista.append(paso("¿Se detiene?", decision))
    return lista


def pasos_newton(fila: Dict, funcion: sp.Expr, derivada: sp.Expr, criterio: Dict, estado: str,
                 es_ultima: bool, f: Optional[Callable] = None, h: Optional[float] = None) -> List[Dict]:
    """Paso a paso de una iteración de Newton."""
    i, xi = fila["i"], fila["xi"]
    nombre = x_sub(i)
    texto, tex = evaluacion("f", "f", funcion, xi, fila["fxi"])
    lista = [paso(f"Evaluar f({nombre})", texto, tex=tex)]
    if h is None:
        texto, tex = evaluacion("f′", "f'", derivada, xi, fila["dfxi"])
        lista.append(paso(f"Evaluar f′({nombre})", texto, tex=tex))
    else:
        mas, menos = _finito(evaluar(f, xi + h)), _finito(evaluar(f, xi - h))
        lista.append(paso(f"Aproximar f′({nombre}) con diferencia central",
                          f"f′({nombre}) ≈ [f({nombre} + h) − f({nombre} − h)]/(2h) = "
                          f"[{numero(mas, 8)} − {par(menos, 8)}]/(2·{h:g}) = "
                          f"{numero(fila['dfxi'], 8, 'no definido')}",
                          tex=f"f'(x_{{{i}}}) \\approx \\frac{{f(x_{{{i}}} + h) - f(x_{{{i}}} - h)}}{{2h}} = "
                              f"\\frac{{{tex_num(mas, 8)} - {tex_par(menos, 8)}}}{{2 \\cdot {tex_num(h)}}} = "
                              f"{tex_num(fila['dfxi'], 8)}"))

    if fila["fxi"] is None or fila["dfxi"] is None:
        lista[-1]["nota"] = ("No es un número real finito (fuera del dominio o desbordamiento): el "
                             "proceso se detiene.")
        return lista
    if abs(fila["dfxi"]) < DERIVADA_MINIMA:
        lista.append(paso("¿Se puede dividir?",
                          f"|f′({nombre})| = {abs(fila['dfxi']):.3g} < {DERIVADA_MINIMA:g}: no.",
                          tex=f"|f'(x_{{{i}}})| = {tex_num(abs(fila['dfxi']), 3)} < 10^{{-10}}",
                          nota="La tangente es (casi) horizontal y no corta el eje x de forma útil: "
                               "el método se detiene sin dividir."))
        return lista

    xs = fila["x_siguiente"]
    formula = f"x_{{{i + 1}}} = x_{{{i}}} - \\frac{{f(x_{{{i}}})}}{{f'(x_{{{i}}})}}"
    if xs is None:
        lista.append(paso("Aplicar la fórmula de Newton",
                          f"{x_sub(i + 1)} no es un número finito: divergencia.", tex=formula,
                          nota="El proceso termina."))
        return lista
    lista.append(paso("Aplicar la fórmula de Newton",
                      f"{x_sub(i + 1)} = {nombre} − f({nombre})/f′({nombre}) = {numero(xi)} − "
                      f"{par(fila['fxi'], 8)}/{par(fila['dfxi'], 8)} = {numero(xs)}",
                      tex=f"{formula} = {tex_num(xi)} - \\frac{{{tex_num(fila['fxi'], 8)}}}"
                          f"{{{tex_num(fila['dfxi'], 8)}}} = {tex_num(xs)}"))
    return lista + pasos_error(fila, criterio, estado, es_ultima)


# Análisis de convergencia ------------------------------------------------------------------
def analizar_convergencia(filas: List[Dict], estado: str, metodo: str = "newton") -> Dict:
    """Razones Eₐ,ᵢ₊₁/Eₐ,ᵢ y Eₐ,ᵢ₊₁/Eₐ,ᵢ², orden estimado p e interpretación."""
    errores_abs = [fila["error_abs"] for fila in filas if fila["error_abs"] is not None]
    umbral = 1e-12  # por debajo, el redondeo distorsiona las razones
    detalle = []
    for k, e in enumerate(errores_abs):
        previo = errores_abs[k - 1] if k >= 1 else None
        orden = None
        if k >= 2 and min(e, previo, errores_abs[k - 2]) > umbral:
            # p ≈ ln(eₖ/eₖ₋₁) / ln(eₖ₋₁/eₖ₋₂)
            orden = _cociente(math.log(e / previo), math.log(previo / errores_abs[k - 2]))
        detalle.append({"iteracion": k + 1, "error": e, "razon_lineal": _cociente(e, previo),
                        "razon_cuadratica": _cociente(e, previo * previo) if previo is not None else None,
                        "orden": orden})

    tabla = pd.DataFrame(
        [[d["iteracion"], numero(d["error"], 4), numero(d["razon_lineal"], 4),
          numero(d["razon_cuadratica"], 4), numero(d["orden"], 3)] for d in detalle],
        columns=["Iteración", "Eₐ", "Eₐ,ᵢ₊₁ / Eₐ,ᵢ", "Eₐ,ᵢ₊₁ / Eₐ,ᵢ²", "Orden p"])

    ordenes = [d["orden"] for d in detalle if d["orden"] is not None]
    p = ordenes[-1] if ordenes else None
    if estado != "convergencia":
        texto = ("El proceso no convergió, así que no hay orden de convergencia que estimar; las "
                 "razones muestran que el error no disminuye de forma sostenida.")
    elif p is None:
        texto = ("Hay muy pocas iteraciones con error medible para estimar el orden (se necesitan "
                 "3 errores consecutivos mayores que 10⁻¹²).")
    elif metodo == "secante" and p >= 1.3:
        texto = (f"Orden estimado p ≈ {p:.2f}: convergencia superlineal, como se espera de la secante "
                 "con una raíz simple (orden teórico ≈ 1.618): más rápida que la lineal, pero sin "
                 "llegar a la cuadrática de Newton.")
    elif p >= 1.7:
        c = next((d["razon_cuadratica"] for d in reversed(detalle)
                  if d["orden"] is not None and d["razon_cuadratica"] is not None), None)
        texto = (f"Orden estimado p ≈ {p:.2f}: convergencia cuadrática, propia de una raíz simple con "
                 f"x₀ cercano (|Eᵢ₊₁| ≈ C·|Eᵢ|², C ≈ {numero(c, 3)}): las cifras correctas casi se "
                 "duplican en cada iteración.")
    elif p >= 1.3:
        texto = (f"Orden estimado p ≈ {p:.2f}: convergencia superlineal, más rápida que la lineal "
                 "pero sin llegar todavía a la cuadrática.")
    elif p >= 0.8:
        r = next((d["razon_lineal"] for d in reversed(detalle) if d["razon_lineal"]), None)
        multiplicidad = (f" y sugiere una raíz múltiple de multiplicidad m ≈ {1 / (1 - r):.1f}"
                         if r is not None and 0 < r < 1 else "")
        texto = (f"Orden estimado p ≈ {p:.2f}: convergencia lineal. La razón Eₐ,ᵢ₊₁/Eₐ,ᵢ ≈ "
                 f"{numero(r, 3)} se mantiene casi constante{multiplicidad}.")
    else:
        texto = (f"Orden estimado p ≈ {p:.2f}: comportamiento irregular (x₀ lejano o fase inicial "
                 "antes de acercarse a la raíz).")
    return {"detalle": detalle, "tabla": tabla_json(tabla), "orden": p, "texto": texto}


# Tabla y reporte ---------------------------------------------------------------------------
def tabla_newton(filas: List[Dict], nombre: str = "f") -> Dict:
    """Tabla de iteraciones de Newton con Pandas (con los dos errores)."""
    columnas = ["i", "xᵢ", f"{nombre}(xᵢ)", f"{nombre}′(xᵢ)", "xᵢ₊₁", "Eₐ = |xᵢ₊₁ − xᵢ|", "εₐ (%)"]
    registros = [
        [fila["i"], numero(fila["xi"]), numero(fila["fxi"], 6, "no definido"),
         numero(fila["dfxi"], 6, "no definido"), numero(fila["x_siguiente"]),
         numero(fila["error_abs"], 4),
         numero(fila["error_rel"], 4, "no definido" if fila["x_siguiente"] == 0 else "—")]
        for fila in filas
    ]
    return tabla_json(pd.DataFrame(registros, columns=columnas))


TITULOS_ESTADO = {
    "convergencia": "Convergencia alcanzada",
    "derivada_nula": "Derivada nula o cercana a cero",
    "pendiente_nula": "Pendiente de la secante nula o casi nula",
    "max_iteraciones": "Máximo de iteraciones sin cumplir la tolerancia",
    "divergencia": "Comportamiento divergente",
    "fuera_de_dominio": "La aproximación salió del dominio de f",
}


def mensaje_estado(estado: str, resultado: Dict, criterio: Dict) -> str:
    """Explica por qué terminó el proceso."""
    ultima, fila = resultado["ultima"], resultado["filas"][-1]
    nombre = x_sub(fila["i"])
    if estado == "convergencia":
        return (f"Convergencia en la iteración {resultado['iteraciones']}: "
                f"{texto_comparacion(ultima, criterio)}.")
    if estado == "derivada_nula":
        texto = (f"Se detuvo antes de dividir: f′({nombre}) = {fila['dfxi']:.3g} en {nombre} = "
                 f"{fila['xi']:.6g} es nula o casi nula (|f′| < {DERIVADA_MINIMA:g}). La recta "
                 "tangente es (casi) horizontal y no corta el eje x de forma útil.")
        if fila["fxi"] == 0:
            texto += f" Además f({nombre}) = 0: {nombre} ya anula la función (posible raíz múltiple)."
        return texto
    if estado == "pendiente_nula":
        return (f"Se detuvo antes de dividir: f({x_sub(fila['i'] - 1)}) y f({nombre}) son (casi) "
                "iguales, así que la secante es horizontal y no corta el eje x.")
    if estado == "max_iteraciones":
        return (f"Se completaron las {criterio['max_iter']} iteraciones sin cumplir la tolerancia "
                f"(último error: {texto_comparacion(ultima, criterio)}). El método no alcanzó el "
                "criterio de convergencia: la última aproximación no debe tomarse como raíz.")
    if estado == "divergencia":
        return (f"Divergencia en la iteración {fila['i'] + 1}: xᵢ₊₁ dejó de ser finito o superó "
                f"{LIMITE_DIVERGENCIA:g} en valor absoluto. Las aproximaciones se alejan de la raíz; "
                "pruebe con otro valor inicial.")
    return (f"En {nombre} = {fila['xi']:.6g}, f o su pendiente no es un número real finito (fuera del "
            "dominio o desbordamiento): no se puede continuar. Pruebe con otro valor inicial.")


def presentar_aproximacion(x: Optional[float], ultima: Optional[Dict], criterio: Dict,
                           convergio: bool) -> Tuple[str, str]:
    """La aproximación con las cifras que respalda el último error (sin precisión excesiva)."""
    if x is None:
        return "no finita", "La última aproximación no es un número finito."
    if not convergio:
        return f"{x:.6g}", "No cumple el criterio de parada: no se reporta como raíz."
    ea, er = ultima["error_abs"], ultima["error_rel"]
    if criterio["tipo"] == "absoluto" or er is None:
        decimales = 10 if not ea else max(1, min(10, math.floor(-math.log10(ea))))
        return (f"{x:.{decimales}f}", f"{decimales} decimales, porque el último error absoluto fue "
                f"Eₐ = {numero(ea, 3)}. Valor calculado: {x:.12g}.")
    cifras = 10 if not er else max(1, min(10, math.floor(2 - math.log10(er / 0.5))))
    return (f"{x:.{cifras}g}", f"{cifras} cifras significativas según el último εₐ = {numero(er, 3)} % "
            f"(criterio de Scarborough). Valor calculado: {x:.12g}.")


def nota_residuo(residuo: Optional[float], convergio: bool) -> str:
    """Interpreta el residuo |f(x)| de la aproximación final."""
    if residuo is None:
        return "No se puede evaluar f en la última aproximación."
    if not convergio:
        return "Solo como referencia: el proceso no cumplió el criterio de parada."
    if residuo <= RESIDUO_ACEPTABLE:
        return f"|f(x)| ≤ {RESIDUO_ACEPTABLE:g}: el residuo respalda la raíz aproximada."
    return (f"Atención: se cumplió el criterio de error, pero |f(x)| > {RESIDUO_ACEPTABLE:g}. Un "
            "error pequeño no garantiza por sí solo una raíz (convergencia lenta u oscilatoria).")


def reporte_base(metodo: str, funcion, resultado: Dict, criterio: Dict, f: Callable) -> Dict:
    """Parte común del reporte de Newton y de la secante."""
    estado, ultima = resultado["estado"], resultado["ultima"]
    convergio = estado == "convergencia"
    aproximacion = _finito(resultado["aproximacion"])
    residuo = _finito(abs(evaluar(f, aproximacion))) if aproximacion is not None else None
    texto_aprox, detalle = presentar_aproximacion(aproximacion, ultima, criterio, convergio)
    return {
        "metodo": metodo,
        "funcion": funcion.texto,
        "funcion_latex": sp.latex(funcion.expresion),
        "avisos": list(funcion.avisos),
        "criterio": criterio,
        "estado": estado,
        "titulo_estado": TITULOS_ESTADO[estado],
        "convergio": convergio,
        "mensaje": mensaje_estado(estado, resultado, criterio),
        "iteraciones": resultado["iteraciones"],
        "aproximacion": aproximacion,
        "aproximacion_texto": texto_aprox,
        "detalle_aproximacion": detalle,
        "error_abs_final": ultima["error_abs"] if ultima else None,
        "error_rel_final": ultima["error_rel"] if ultima else None,
        "error_final_texto": texto_comparacion(ultima, criterio) if ultima else "—",
        "residuo": residuo,
        "residuo_texto": numero(residuo, 3, "no definido"),
        "nota_residuo": nota_residuo(residuo, convergio),
        "filas": resultado["filas"],
        "convergencia": analizar_convergencia(resultado["filas"], estado, metodo),
        "comparacion": None,
        "contraste_scipy": None,
    }


def resumen_metodo(nombre: str, resultado: Dict, criterio: Dict) -> Dict:
    """Resumen corto de una corrida (para comparar métodos o derivadas)."""
    convergio = resultado["estado"] == "convergencia"
    texto, _ = presentar_aproximacion(_finito(resultado["aproximacion"]), resultado["ultima"],
                                      criterio, convergio)
    clave = "error_abs" if criterio["tipo"] == "absoluto" else "error_rel"
    return {"nombre": nombre, "estado": resultado["estado"],
            "titulo_estado": TITULOS_ESTADO[resultado["estado"]],
            "iteraciones": resultado["iteraciones"], "aproximacion_texto": texto,
            "errores": [fila[clave] for fila in resultado["filas"] if fila["x_siguiente"] is not None]}


def resolver_newton_raphson(funcion: str, x0: str, tolerancia: Optional[str] = None,
                            max_iter: Optional[str] = None, tipo_error: str = "relativo",
                            derivada: str = "analitica", h: Optional[str] = None,
                            comparar_scipy: bool = True) -> Dict:
    """Función principal de Newton (consola y web): valida, itera y arma el reporte."""
    expresion, deriv_expr, f, df = preparar_funcion(funcion)
    x_inicial = leer_numero(x0, "x₀", "x0")
    criterio = leer_criterio(tipo_error, tolerancia, max_iter)
    if math.isnan(evaluar(f, x_inicial)):
        raise ErrorNumerico(f"f(x₀) no está definida o no es finita en x₀ = {formatear(x_inicial)}: "
                            "elija otro valor inicial.", "x0")
    tipo_derivada = (derivada or "analitica").strip().lower()
    if tipo_derivada[:1] not in ("a", "c"):
        raise ErrorNumerico("La derivada debe ser 'analitica' (SymPy) o 'central' (numérica).", "derivada")
    paso_h = leer_paso(h or POR_DEFECTO["h_newton"]) if tipo_derivada.startswith("c") else None
    df_usada = derivada_central(f, paso_h) if paso_h else df

    resultado = metodo_newton_raphson(f, df_usada, x_inicial, criterio)
    reporte = reporte_base("newton", expresion, resultado, criterio, f)
    filas = resultado["filas"]
    reporte.update({
        "x0": x_inicial,
        "derivada": sp.sstr(deriv_expr),
        "derivada_latex": sp.latex(deriv_expr),
        "derivada_usada": "central" if paso_h else "analitica",
        "h": paso_h,
        "criterio_parada": texto_criterio(criterio),
        "tabla": tabla_newton(filas),
        "pasos": [{"etiqueta": f"i = {fila['i']}",
                   "pasos": pasos_newton(fila, expresion.expresion, deriv_expr, criterio,
                                         resultado["estado"], k == len(filas) - 1, f, paso_h)}
                  for k, fila in enumerate(filas)],
    })
    # Tarea 7: con f′ numérica se compara contra la derivada analítica.
    if paso_h:
        analitica = metodo_newton_raphson(f, df, x_inicial, criterio)
        reporte["comparacion"] = {
            "titulo": "Derivada analítica vs. diferencia central",
            "metodos": [resumen_metodo(f"f′ por diferencia central (h = {paso_h:g})", resultado, criterio),
                        resumen_metodo("f′ analítica (SymPy)", analitica, criterio)],
            "texto": (f"Con la diferencia central se usaron {resultado['iteraciones']} iteraciones y con "
                      f"la derivada analítica {analitica['iteraciones']}: con un h pequeño la "
                      "aproximación de f′ es tan buena que el número de iteraciones casi no cambia."),
        }
    if comparar_scipy and reporte["convergio"]:
        reporte["contraste_scipy"] = comparar_con_scipy(f, df, x_inicial, reporte["aproximacion"])
    return reporte


def comparar_con_scipy(f: Callable, df: Optional[Callable], x0: float, aproximacion: float,
                       x1: Optional[float] = None) -> Dict:
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
            if df is None:  # sin derivada, SciPy usa la secante
                raiz = float(newton_scipy(lambda x: evaluar(f, x), x0, x1=x1, tol=1e-12,
                                          maxiter=MAX_ITER_PERMITIDO))
            else:
                raiz = float(newton_scipy(lambda x: evaluar(f, x), x0, fprime=lambda x: evaluar(df, x),
                                          tol=1e-12, maxiter=MAX_ITER_PERMITIDO))
    except (RuntimeError, ArithmeticError, ValueError) as error:
        return {"disponible": False, "motivo": f"SciPy no pudo calcular la raíz: {error}", "nota": nota}
    if not math.isfinite(raiz):
        return {"disponible": False, "motivo": "SciPy devolvió un valor no finito.", "nota": nota}
    diferencia = abs(raiz - aproximacion)
    return {"disponible": True, "raiz": raiz, "raiz_texto": f"{raiz:.10g}", "diferencia": diferencia,
            "diferencia_texto": f"{diferencia:.3g}", "nota": nota}


# ═══════════════════════════════════════════════════════════════════════════
# B. MÉTODO DE LA SECANTE
# ═══════════════════════════════════════════════════════════════════════════
def metodo_secante(f: Callable, x0: float, x1: float, criterio: Dict) -> Dict:
    """Aplica xᵢ₊₁ = xᵢ − f(xᵢ)(xᵢ₋₁ − xᵢ)/(f(xᵢ₋₁) − f(xᵢ)) hasta cumplir el criterio o llegar a Nmax."""
    filas: List[Dict] = []
    x_anterior, xi = x0, x1
    estado = "max_iteraciones"

    for i in range(1, criterio["max_iter"] + 1):
        f_anterior, fxi = evaluar(f, x_anterior), evaluar(f, xi)
        fila = {"i": i, "x_anterior": x_anterior, "xi": xi, "f_anterior": _finito(f_anterior),
                "fxi": _finito(fxi), "pendiente": None, "x_siguiente": None, "error_abs": None,
                "error_rel": None, "cumple": False}
        filas.append(fila)
        if math.isnan(f_anterior) or math.isnan(fxi):
            estado = "fuera_de_dominio"
            break

        # La pendiente de la secante reemplaza a f'(xi): no puede ser cero ni casi cero.
        denominador = f_anterior - fxi
        pendiente = denominador / (x_anterior - xi)
        fila["pendiente"] = _finito(pendiente)
        if denominador == 0 or abs(pendiente) < DERIVADA_MINIMA:
            estado = "pendiente_nula"
            break

        x_siguiente = xi - fxi * (x_anterior - xi) / denominador  # fórmula de la secante
        if not math.isfinite(x_siguiente):
            estado = "divergencia"
            break

        absoluto, relativo = errores(xi, x_siguiente)
        cumple = cumple_criterio(absoluto, relativo, criterio)
        fila.update({"x_siguiente": x_siguiente, "error_abs": _finito(absoluto),
                     "error_rel": _finito(relativo), "cumple": cumple})
        x_anterior, xi = xi, x_siguiente

        if abs(xi) > LIMITE_DIVERGENCIA:
            estado = "divergencia"
            break
        if cumple:
            estado = "convergencia"
            break

    completas = [fila for fila in filas if fila["x_siguiente"] is not None]
    return {"estado": estado, "filas": filas, "iteraciones": len(completas),
            "aproximacion": xi, "ultima": completas[-1] if completas else None}


def pasos_secante(fila: Dict, funcion: sp.Expr, criterio: Dict, estado: str,
                  es_ultima: bool) -> List[Dict]:
    """Paso a paso de una iteración de la secante."""
    i, xa, xi = fila["i"], fila["x_anterior"], fila["xi"]
    lista = []
    for nombre, valor, fx in ((x_sub(i - 1), xa, fila["f_anterior"]), (x_sub(i), xi, fila["fxi"])):
        texto, tex = evaluacion("f", "f", funcion, valor, fx)
        lista.append(paso(f"Evaluar f({nombre})", texto, tex=tex))
    if fila["f_anterior"] is None or fila["fxi"] is None:
        lista[-1]["nota"] = "No es un número real finito (fuera del dominio): el proceso se detiene."
        return lista

    fa, fi, xs = fila["f_anterior"], fila["fxi"], fila["x_siguiente"]
    formula = (f"x_{{{i + 1}}} = x_{{{i}}} - \\frac{{f(x_{{{i}}})\\,(x_{{{i - 1}}} - x_{{{i}}})}}"
               f"{{f(x_{{{i - 1}}}) - f(x_{{{i}}})}}")
    if xs is None:
        if estado == "pendiente_nula":
            lista.append(paso("¿Se puede dividir?",
                              f"f({x_sub(i - 1)}) − f({x_sub(i)}) = {numero(fa - fi, 3)} ≈ 0: no.",
                              tex=formula, nota="La secante es horizontal y no corta el eje x: el "
                                                "método se detiene sin dividir."))
        else:
            lista.append(paso("Aplicar la fórmula de la secante",
                              "El resultado no es finito: divergencia.", tex=formula))
        return lista
    lista.append(paso("Aplicar la fórmula de la secante",
                      f"{x_sub(i + 1)} = {x_sub(i)} − f({x_sub(i)})·({x_sub(i - 1)} − {x_sub(i)})/"
                      f"(f({x_sub(i - 1)}) − f({x_sub(i)})) = {numero(xi)} − {par(fi, 8)}·({numero(xa)} − "
                      f"{par(xi)})/({numero(fa, 8)} − {par(fi, 8)}) = {numero(xs)}",
                      tex=f"{formula} = {tex_num(xi)} - \\frac{{{tex_par(fi, 8)} \\left({tex_num(xa)} - "
                          f"{tex_par(xi)}\\right)}}{{{tex_num(fa, 8)} - {tex_par(fi, 8)}}} = {tex_num(xs)}"))
    return lista + pasos_error(fila, criterio, estado, es_ultima)


COLUMNAS_SECANTE = ["i", "xᵢ₋₁", "xᵢ", "f(xᵢ₋₁)", "f(xᵢ)", "xᵢ₊₁", "Eₐ = |xᵢ₊₁ − xᵢ|", "εₐ (%)"]


def resolver_secante(funcion: str, x0: str, x1: str, tolerancia: Optional[str] = None,
                     max_iter: Optional[str] = None, tipo_error: str = "relativo",
                     comparar_scipy: bool = True) -> Dict:
    """Función principal de la secante: valida, itera, compara con Newton y arma el reporte."""
    expresion, _, f, df = preparar_funcion(funcion)
    a, b = leer_numero(x0, "x₀", "x0"), leer_numero(x1, "x₁", "x1")
    criterio = leer_criterio(tipo_error, tolerancia, max_iter)
    if a == b:
        raise ErrorNumerico("La secante necesita dos valores iniciales distintos: x₀ ≠ x₁.", "x1")
    for valor, campo in ((a, "x0"), (b, "x1")):
        if math.isnan(evaluar(f, valor)):
            raise ErrorNumerico(f"f no está definida o no es finita en {formatear(valor)}: elija otro "
                                "valor inicial.", campo)

    resultado = metodo_secante(f, a, b, criterio)
    reporte = reporte_base("secante", expresion, resultado, criterio, f)
    filas = resultado["filas"]
    reporte.update({
        "x0": a, "x1": b,
        "criterio_parada": texto_criterio(criterio, "pendiente de la secante"),
        "tabla": tabla_json(pd.DataFrame(
            [[fila["i"], numero(fila["x_anterior"]), numero(fila["xi"]),
              numero(fila["f_anterior"], 6, "no definido"), numero(fila["fxi"], 6, "no definido"),
              numero(fila["x_siguiente"]), numero(fila["error_abs"], 4),
              numero(fila["error_rel"], 4, "no definido" if fila["x_siguiente"] == 0 else "—")]
             for fila in filas], columns=COLUMNAS_SECANTE)),
        "pasos": [{"etiqueta": f"i = {fila['i']}",
                   "pasos": pasos_secante(fila, expresion.expresion, criterio, resultado["estado"],
                                          k == len(filas) - 1)}
                  for k, fila in enumerate(filas)],
    })
    # Comparación con Newton desde x0 y el mismo criterio (práctica 2 y tarea 1 de la clase).
    newton = metodo_newton_raphson(f, df, a, criterio)
    reporte["comparacion"] = {
        "titulo": "Secante vs. Newton-Raphson",
        "metodos": [resumen_metodo("Secante", resultado, criterio),
                    resumen_metodo(f"Newton-Raphson (x₀ = {formatear(a)})", newton, criterio)],
        "texto": (f"La secante usó {resultado['iteraciones']} iteraciones y Newton "
                  f"{newton['iteraciones']}: la secante no necesita f′(x), pero suele converger un poco "
                  "más despacio (orden ≈ 1.618 frente a 2)."),
    }
    if comparar_scipy and reporte["convergio"]:
        reporte["contraste_scipy"] = comparar_con_scipy(f, None, a, reporte["aproximacion"], b)
    return reporte


# ═══════════════════════════════════════════════════════════════════════════
# C. DERIVADAS NUMÉRICAS
# ═══════════════════════════════════════════════════════════════════════════
def diferencias(f: Callable, x: float, h: float) -> Dict[str, float]:
    """Diferencias hacia adelante, hacia atrás y central (nan si f no está definida)."""
    menos, centro, mas = evaluar(f, x - h), evaluar(f, x), evaluar(f, x + h)
    with np.errstate(all="ignore"):
        return {"adelante": float(np.float64(mas - centro) / h),
                "atras": float(np.float64(centro - menos) / h),
                "central": float(np.float64(mas - menos) / (2 * h))}


FORMULAS_DERIVADA = [
    ("adelante", "Hacia adelante", "O(h)", "[f(x + h) − f(x)]/h"),
    ("atras", "Hacia atrás", "O(h)", "[f(x) − f(x − h)]/h"),
    ("central", "Central", "O(h²)", "[f(x + h) − f(x − h)]/(2h)"),
]


def analisis_paso_h(f: Callable, x: float, exacta: float) -> Dict:
    """Error de cada fórmula para h = 10⁻¹ … 10⁻¹²: truncamiento vs redondeo."""
    errores_h: Dict[str, List[Optional[float]]] = {clave: [] for clave, *_ in FORMULAS_DERIVADA}
    for h in PASOS_H:
        valores = diferencias(f, x, h)
        for clave in errores_h:
            errores_h[clave].append(_finito(abs(valores[clave] - exacta)))
    optimos = {}
    for clave in errores_h:
        validos = [(e, h) for e, h in zip(errores_h[clave], PASOS_H) if e is not None]
        optimos[clave] = min(validos)[1] if validos else None
    tabla = pd.DataFrame([[f"{h:.0e}"] + [numero(errores_h[c][k], 3) for c, *_ in FORMULAS_DERIVADA]
                          for k, h in enumerate(PASOS_H)],
                         columns=["h", "Error adelante", "Error atrás", "Error central"])
    texto = (f"Al reducir h el error de truncamiento baja (O(h) en adelante y atrás, O(h²) en la "
             f"central), pero con h muy pequeño domina el error de redondeo por restar valores casi "
             f"iguales. El menor error se obtuvo con h ≈ {numero(optimos['adelante'], 1)} (adelante), "
             f"{numero(optimos['atras'], 1)} (atrás) y {numero(optimos['central'], 1)} (central).")
    return {"h": PASOS_H, "errores": errores_h, "optimos": optimos, "tabla": tabla_json(tabla),
            "texto": texto}


def calcular_derivadas(funcion: str, x: str, h: Optional[str] = None) -> Dict:
    """Derivada numérica en x con las tres fórmulas, comparada con la derivada analítica."""
    expresion, deriv_expr, f, df = preparar_funcion(funcion)
    punto = leer_numero(x, "x", "x")
    paso_h = leer_paso(h or POR_DEFECTO["h_derivadas"])
    menos, centro, mas = evaluar(f, punto - paso_h), evaluar(f, punto), evaluar(f, punto + paso_h)
    if any(math.isnan(v) for v in (menos, centro, mas)):
        raise ErrorNumerico("f no está definida en x − h, x o x + h: elija otro punto o un h menor.", "x")
    exacta = _finito(evaluar(df, punto))

    valores = diferencias(f, punto, paso_h)
    formulas, filas_tabla = [], []
    for clave, nombre, orden, texto_formula in FORMULAS_DERIVADA:
        valor = _finito(valores[clave])
        error_abs = abs(valor - exacta) if valor is not None and exacta is not None else None
        error_rel = _cociente(error_abs * 100, abs(exacta)) if error_abs is not None else None
        formulas.append({"clave": clave, "nombre": nombre, "orden": orden, "formula": texto_formula,
                         "valor": valor, "valor_texto": numero(valor, 8, "no finito"),
                         "error_abs": _finito(error_abs), "error_rel": error_rel})
        filas_tabla.append([nombre, texto_formula, orden, numero(valor, 8, "no finito"),
                            numero(error_abs, 3), numero(error_rel, 3)])

    # Paso a paso (como en la clase: valores de f, sustitución en cada fórmula y comparación).
    h_txt, h_tex = numero(paso_h), tex_num(paso_h)
    adelante, atras, central = (_finito(valores[c]) for c in ("adelante", "atras", "central"))
    pasos = []
    for nombre, valor, v in (("x − h", punto - paso_h, menos), ("x", punto, centro),
                             ("x + h", punto + paso_h, mas)):
        texto, tex = evaluacion("f", "f", expresion.expresion, valor, v)
        pasos.append(paso(f"Evaluar f({nombre})", texto, tex=tex))
    pasos += [
        paso("Hacia adelante (O(h))",
             f"[f(x + h) − f(x)]/h = [{numero(mas, 8)} − {par(centro, 8)}]/{h_txt} = {numero(adelante, 8)}",
             tex=f"\\frac{{f(x+h) - f(x)}}{{h}} = \\frac{{{tex_num(mas, 8)} - {tex_par(centro, 8)}}}"
                 f"{{{h_tex}}} = {tex_num(adelante, 8)}"),
        paso("Hacia atrás (O(h))",
             f"[f(x) − f(x − h)]/h = [{numero(centro, 8)} − {par(menos, 8)}]/{h_txt} = {numero(atras, 8)}",
             tex=f"\\frac{{f(x) - f(x-h)}}{{h}} = \\frac{{{tex_num(centro, 8)} - {tex_par(menos, 8)}}}"
                 f"{{{h_tex}}} = {tex_num(atras, 8)}"),
        paso("Central (O(h²))",
             f"[f(x + h) − f(x − h)]/(2h) = [{numero(mas, 8)} − {par(menos, 8)}]/{numero(2 * paso_h)} = "
             f"{numero(central, 8)}",
             tex=f"\\frac{{f(x+h) - f(x-h)}}{{2h}} = \\frac{{{tex_num(mas, 8)} - {tex_par(menos, 8)}}}"
                 f"{{{tex_num(2 * paso_h)}}} = {tex_num(central, 8)}",
             nota="Se divide entre 2h porque esa es la distancia entre los dos puntos usados."),
    ]
    if exacta is not None:
        texto, tex = evaluacion("f′", "f'", deriv_expr, punto, exacta)
        pasos.append(paso("Comparar con la derivada analítica (SymPy)",
                          f"f′(x) = {sp.sstr(deriv_expr)} → {texto}",
                          tex=f"f'(x) = {sp.latex(deriv_expr)} \\;\\Rightarrow\\; {tex}",
                          nota="Errores absolutos: " + "; ".join(
                              f"{fm['nombre'].lower()} = {numero(fm['error_abs'], 3)}" for fm in formulas)
                               + ". La central es la más precisa porque su error es O(h²)."))
    if adelante is not None and atras is not None:
        promedio = (adelante + atras) / 2
        pasos.append(paso("Comprobación",
                          f"(adelante + atrás)/2 = ({numero(adelante, 8)} + {par(atras, 8)})/2 = "
                          f"{numero(promedio, 8)} = central",
                          tex=f"\\frac{{{tex_num(adelante, 8)} + {tex_par(atras, 8)}}}{{2}} = "
                              f"{tex_num(promedio, 8)} = \\text{{central}}",
                          nota="Adelante y atrás cometen errores de signo contrario; la central los compensa."))

    return {
        "metodo": "derivadas",
        "funcion": expresion.texto,
        "funcion_latex": sp.latex(expresion.expresion),
        "derivada": sp.sstr(deriv_expr),
        "derivada_latex": sp.latex(deriv_expr),
        "avisos": list(expresion.avisos),
        "x": punto,
        "h": paso_h,
        "valores": {"menos": menos, "centro": centro, "mas": mas},
        "exacta": exacta,
        "exacta_texto": numero(exacta, 10, "no definida"),
        "formulas": formulas,
        "tabla": tabla_json(pd.DataFrame(filas_tabla, columns=["Fórmula", "Expresión", "Orden", "Valor",
                                                                "Error absoluto", "Error relativo (%)"])),
        "pasos": [{"etiqueta": "Cálculo", "pasos": pasos}],
        "analisis_h": analisis_paso_h(f, punto, exacta) if exacta is not None else None,
    }


# ═══════════════════════════════════════════════════════════════════════════
# D. RAÍCES DE POLINOMIOS: HORNER, NEWTON Y DEFLACIÓN
# ═══════════════════════════════════════════════════════════════════════════
def leer_polinomio(texto: str) -> List[float]:
    """Coeficientes de p(x) de mayor a menor grado ('x**3 - 6*x**2 + 11*x - 6' o '1, -6, 11, -6')."""
    texto = (texto or "").strip()
    if not texto:
        raise ErrorNumerico("Escriba el polinomio p(x) o sus coeficientes separados por comas.", "polinomio")
    if "," in texto:
        coeficientes = [leer_numero(t, f"el coeficiente {k}", "polinomio")
                        for k, t in enumerate(texto.split(","), start=1)]
    else:
        expresion = analizar_funcion(texto, "polinomio").expresion
        try:
            coeficientes = [float(c) for c in sp.Poly(expresion, X).all_coeffs()]
        except (sp.PolynomialError, TypeError, ValueError):
            raise ErrorNumerico("p(x) debe ser un polinomio en x con coeficientes reales (potencias "
                                "enteras no negativas).", "polinomio")
    if not all(math.isfinite(c) for c in coeficientes):
        raise ErrorNumerico("Los coeficientes del polinomio deben ser números finitos.", "polinomio")
    while len(coeficientes) > 1 and coeficientes[0] == 0:
        coeficientes.pop(0)
    grado = len(coeficientes) - 1
    if not 1 <= grado <= GRADO_MAXIMO:
        raise ErrorNumerico(f"El grado del polinomio debe estar entre 1 y {GRADO_MAXIMO} "
                            f"(se recibió {grado}).", "polinomio")
    return coeficientes


def polinomio_texto(coeficientes: List[float], tex: bool = False) -> str:
    """p(x) legible a partir de sus coeficientes (de mayor a menor grado)."""
    grado, partes = len(coeficientes) - 1, []
    for k, c in enumerate(coeficientes):
        if c == 0:
            continue
        potencia = grado - k
        coef = tex_num(abs(c), 6) if tex else numero(abs(c), 6)
        if coef == "1" and potencia > 0:
            coef = ""
        if potencia == 0:
            variable = ""
        elif potencia == 1:
            variable = "x"
        else:
            variable = f"x^{{{potencia}}}" if tex else "x" + str(potencia).translate(_SUPERINDICES)
        separador = " " if tex and coef and variable else ""
        partes.append(("-" if c < 0 else "+", f"{coef}{separador}{variable}"))
    if not partes:
        return "0"
    texto = ("-" if partes[0][0] == "-" else "") + partes[0][1]
    return texto + "".join(f" {signo} {termino}" for signo, termino in partes[1:])


def horner(coeficientes, x):
    """Evalúa p(x) y p′(x) con Horner (división sintética doble): p, p′ y las filas b y c."""
    b = [coeficientes[0]]
    for a in coeficientes[1:]:
        b.append(a + x * b[-1])     # bₖ = aₖ + x·bₖ₋₁ ; p(x) = último b
    c = [b[0]]
    for bk in b[1:-1]:
        c.append(bk + x * c[-1])    # cₖ = bₖ + x·cₖ₋₁ ; p′(x) = último c
    return b[-1], c[-1], b, c


def deflacion(coeficientes: List[float], raiz: float) -> Tuple[List[float], float]:
    """Divide p(x) entre (x − r) por división sintética: cociente q(x) y residuo."""
    _, _, b, _ = horner(coeficientes, raiz)
    cociente = b[:-1]
    escala = max(abs(c) for c in cociente) or 1.0
    # Coeficientes del orden de 10⁻¹⁶·escala son residuos de redondeo: se toman como 0.
    return [0.0 if abs(c) < 1e-14 * escala else c for c in cociente], b[-1]


def refinar(coeficientes: List[float], raiz: float) -> float:
    """Pule la raíz con unas iteraciones de Newton sobre el polinomio original."""
    x = raiz
    for _ in range(5):
        p, dp, _, _ = horner(coeficientes, x)
        if dp == 0 or not (math.isfinite(p) and math.isfinite(dp)):
            break
        x_nuevo = x - p / dp
        if not math.isfinite(x_nuevo) or abs(x_nuevo - x) > 1e-3 * max(1.0, abs(x)):
            break  # se alejaría: se conserva la raíz anterior
        hecho = abs(x_nuevo - x) <= 1e-15 * max(1.0, abs(x))
        x = x_nuevo
        if hecho:
            break
    return x


def raices_cuadratica(a: float, b: float, c: float) -> Tuple[complex, complex, float]:
    """Fórmula general: raíces de ax² + bx + c (reales o complejas) y el discriminante."""
    discriminante = b * b - 4 * a * c
    raiz = math.sqrt(abs(discriminante))
    if discriminante >= 0:
        return complex((-b + raiz) / (2 * a)), complex((-b - raiz) / (2 * a)), discriminante
    return complex(-b / (2 * a), raiz / (2 * a)), complex(-b / (2 * a), -raiz / (2 * a)), discriminante


def texto_raiz(z: complex) -> str:
    """Raíz real o compleja legible: 2, 1 + 1i, 1 − 1i."""
    if abs(z.imag) <= 1e-12 * max(1.0, abs(z.real)):
        return numero(z.real, 10)
    return f"{numero(z.real, 8)} {'+' if z.imag > 0 else '−'} {numero(abs(z.imag), 8)}i"


def _columnas_potencias(n: int) -> List[str]:
    """Encabezados xⁿ … x, x⁰ de las tablas de Horner."""
    return ["x" + (str(n - k).translate(_SUPERINDICES) if n - k != 1 else "") for k in range(n + 1)]


def tabla_horner(coeficientes: List[float], x: float) -> Dict:
    """Tabla de Horner en x: coeficientes, fila b (da p(x)) y fila c (da p′(x))."""
    _, _, b, c = horner(coeficientes, x)
    filas = [["a (coeficientes)"] + [numero(v, 8) for v in coeficientes],
             ["b → p(x)"] + [numero(v, 8) for v in b],
             ["c → p′(x)"] + [numero(v, 8) for v in c] + [""]]
    return tabla_json(pd.DataFrame(filas, columns=["Fila"] + _columnas_potencias(len(coeficientes) - 1)))


def tabla_deflacion(coeficientes: List[float], raiz: float) -> Dict:
    """División sintética entre (x − r): coeficientes, productos r·b y fila b (cociente y residuo)."""
    _, _, b, _ = horner(coeficientes, raiz)
    filas = [["a (coeficientes)"] + [numero(v, 8) for v in coeficientes],
             [f"r·b (r = {numero(raiz, 8)})", ""] + [numero(raiz * v, 8) for v in b[:-1]],
             ["b = a + r·b"] + [numero(v, 8) for v in b]]
    return tabla_json(pd.DataFrame(filas, columns=["Fila"] + _columnas_potencias(len(coeficientes) - 1)))


def _raiz(z: complex, metodo: str, iteraciones: int, coeficientes: List[float]) -> Dict:
    """Registro de una raíz con su residuo en el polinomio original."""
    residuo = abs(horner(coeficientes, z)[0])
    real = abs(z.imag) <= 1e-12 * max(1.0, abs(z.real))
    return {"real": _finito(z.real), "imag": 0.0 if real else _finito(z.imag),
            "tipo": "real" if real else "compleja", "texto": texto_raiz(z), "metodo": metodo,
            "iteraciones": iteraciones, "residuo": _finito(residuo), "residuo_texto": numero(residuo, 3)}


def resolver_polinomio(polinomio: str, x0: str, tolerancia: Optional[str] = None,
                       max_iter: Optional[str] = None, tipo_error: str = "relativo") -> Dict:
    """Raíces de p(x): Newton con Horner, deflación, fórmula general y validación con numpy.roots."""
    coeficientes = leer_polinomio(polinomio)
    x_inicial = leer_numero(x0, "x₀", "x0")
    criterio = leer_criterio(tipo_error, tolerancia, max_iter)
    actual, raices, etapas, sin_resolver = list(coeficientes), [], [], None

    while len(actual) > 1:
        etiqueta = f"Raíz {len(raices) + 1}"
        texto_p, tex_p = polinomio_texto(actual), polinomio_texto(actual, tex=True)
        if len(actual) == 2:  # grado 1: se despeja
            r = -actual[1] / actual[0]
            raices.append(_raiz(complex(r), "Despeje (grado 1)", 0, coeficientes))
            etapas.append({"etiqueta": etiqueta, "pasos": [paso(
                "Polinomio de grado 1",
                f"{texto_p} = 0  →  x = −({numero(actual[1], 8)})/{par(actual[0], 8)} = {numero(r)}",
                tex=f"{tex_p} = 0 \\;\\Rightarrow\\; x = -\\frac{{{tex_num(actual[1], 8)}}}"
                    f"{{{tex_num(actual[0], 8)}}} = {tex_num(r)}")]})
            break

        coef = tuple(actual)
        pasos = [paso("Polinomio actual", f"p(x) = {texto_p}", tex=f"p(x) = {tex_p}")]
        p0, dp0, _, _ = horner(actual, x_inicial)
        pasos.append(paso(f"Horner en x₀ = {numero(x_inicial)}",
                          f"p(x₀) = {numero(p0, 8)} (último b) y p′(x₀) = {numero(dp0, 8)} (último c)",
                          tabla=tabla_horner(actual, x_inicial),
                          nota="bₖ = aₖ + x₀·bₖ₋₁ da p(x₀); repitiendo la división con la fila b se "
                               "obtiene p′(x₀). Así se evalúan p y p′ en cada iteración de Newton."))
        inicios = [x_inicial] + [x_inicial + d for d in ALTERNATIVAS_X0]
        for k, inicio in enumerate(inicios):
            resultado = metodo_newton_raphson(lambda x, c=coef: horner(c, x)[0],
                                              lambda x, c=coef: horner(c, x)[1], inicio, criterio)
            pasos.append(paso(f"Newton con Horner desde x₀ = {numero(inicio)}",
                              f"{TITULOS_ESTADO[resultado['estado']]} ({resultado['iteraciones']} "
                              "iteraciones; p y p′ se evalúan con Horner en cada una).",
                              tabla=tabla_newton(resultado["filas"], "p")))
            if resultado["estado"] == "convergencia" or len(actual) == 3:
                break  # en grado 2, si Newton falla se usa la fórmula general
            if k < len(inicios) - 1:
                pasos[-1]["nota"] = "No convergió desde este valor inicial: se prueba con otro."

        if resultado["estado"] == "convergencia":
            r = refinar(coeficientes, resultado["aproximacion"])
            cociente, residuo = deflacion(actual, r)
            raices.append(_raiz(complex(r), "Newton + Horner", resultado["iteraciones"], coeficientes))
            pasos += [
                paso("Refinar con el polinomio original",
                     f"r = {numero(resultado['aproximacion'], 12)} → {numero(r, 12)};  "
                     f"|p(r)| = {raices[-1]['residuo_texto']}",
                     nota="Los errores de la deflación se propagan; por eso cada raíz se pule con el "
                          "polinomio original."),
                paso("Deflación (división sintética)",
                     f"p(x)/(x − {par(r)}) = {polinomio_texto(cociente)};  residuo = {numero(residuo, 3)}",
                     tex=f"\\frac{{p(x)}}{{x - {tex_par(r)}}} = {polinomio_texto(cociente, tex=True)},"
                         f"\\quad \\text{{residuo}} = {tex_num(residuo, 3)}",
                     tabla=tabla_deflacion(actual, r),
                     nota="La fila b da los coeficientes del cociente; su último valor es el residuo "
                          "(≈ 0 porque r es raíz). Valores del orden de 10⁻¹⁵ son residuos de redondeo."),
            ]
            etapas.append({"etiqueta": etiqueta, "pasos": pasos})
            actual = cociente
            continue

        if len(actual) == 3:  # grado 2 sin raíz por Newton: fórmula general
            z1, z2, discriminante = raices_cuadratica(*actual)
            raices += [_raiz(z1, "Fórmula general", 0, coeficientes),
                       _raiz(z2, "Fórmula general", 0, coeficientes)]
            tex_z1, tex_z2 = (texto_raiz(z).replace("−", "-") for z in (z1, z2))
            pasos.append(paso("Fórmula general",
                              f"Δ = b² − 4ac = {numero(discriminante, 8)} → x = (−b ± √Δ)/(2a): "
                              f"{texto_raiz(z1)} y {texto_raiz(z2)}",
                              tex=f"\\Delta = b^2 - 4ac = {tex_num(discriminante, 8)},\\quad "
                                  f"x = \\frac{{-b \\pm \\sqrt{{\\Delta}}}}{{2a}} \\;\\Rightarrow\\; "
                                  f"x_1 = {tex_z1},\\; x_2 = {tex_z2}",
                              nota=("Desde un x₀ real Newton solo encuentra raíces reales; con Δ < 0 las "
                                    "raíces son complejas conjugadas.") if discriminante < 0 else None))
            etapas.append({"etiqueta": f"Raíces {len(raices) - 1} y {len(raices)}", "pasos": pasos})
            break

        pasos.append(paso("Sin convergencia",
                          f"Newton no convergió desde ninguno de los valores iniciales probados: "
                          f"{texto_p} queda sin resolver.",
                          nota="Puede no tener raíces reales; numpy.roots muestra todas sus raíces."))
        etapas.append({"etiqueta": etiqueta, "pasos": pasos})
        sin_resolver = actual
        break

    # Validación con numpy.roots (solo contraste).
    referencia = [complex(z) for z in np.roots(coeficientes)]
    libres, comparacion = list(referencia), []
    for raiz in raices:
        z = complex(raiz["real"] or 0.0, raiz["imag"] or 0.0)
        cercana = min(libres, key=lambda w: abs(w - z)) if libres else None
        if cercana is not None:
            libres.remove(cercana)
        diferencia = abs(cercana - z) if cercana is not None else None
        comparacion.append([raiz["texto"], texto_raiz(cercana) if cercana is not None else "—",
                            numero(diferencia, 3)])
    completo = sin_resolver is None
    grado = len(coeficientes) - 1
    tabla_raices = pd.DataFrame(
        [[k, r["texto"], r["tipo"], r["metodo"], r["iteraciones"] or "—", r["residuo_texto"]]
         for k, r in enumerate(raices, start=1)],
        columns=["#", "Raíz", "Tipo", "Método", "Iteraciones", "|p(r)| en p original"])
    return {
        "metodo": "polinomio",
        "polinomio": polinomio_texto(coeficientes),
        "polinomio_latex": polinomio_texto(coeficientes, tex=True),
        "coeficientes": coeficientes,
        "grado": grado,
        "x0": x_inicial,
        "criterio": criterio,
        "criterio_parada": texto_criterio(criterio, "p′(xᵢ)"),
        "estado": "completo" if completo else "incompleto",
        "titulo_estado": "Se encontraron todas las raíces" if completo else "Quedaron raíces sin encontrar",
        "mensaje": (f"Se encontraron las {len(raices)} raíces del polinomio de grado {grado}."
                    if completo else
                    f"Se encontraron {len(raices)} de {grado} raíces; {polinomio_texto(sin_resolver)} "
                    "quedó sin resolver con Newton."),
        "raices": raices,
        "tabla": tabla_json(tabla_raices),
        "pasos": etapas,
        "validacion": {
            "tabla": tabla_json(pd.DataFrame(comparacion, columns=["Raíz (programa)", "Raíz (numpy.roots)",
                                                                   "|Diferencia|"])),
            "todas": [texto_raiz(z) for z in referencia],
            "nota": "numpy.roots solo sirve para validar: las raíces se obtienen con Newton, Horner y deflación.",
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# E. GRÁFICAS (Matplotlib)
# ═══════════════════════════════════════════════════════════════════════════
COLOR_CURVA = "#6d3beb"
COLOR_RECTA = "#f59e0b"
COLOR_PUNTO = "#1d4ed8"
COLOR_APROXIMACION = "#dc2626"
COLORES_SERIES = ["#6d3beb", "#0e9f6e", "#2563eb", "#f59e0b"]


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


def rango_y(ys: np.ndarray, alturas: List[float]) -> Tuple[float, float]:
    """Rango vertical: toda la curva, salvo que una asíntota lo dispare (se recorta)."""
    validos = ys[np.isfinite(ys)]
    bajo, alto = (float(np.min(validos)), float(np.max(validos))) if validos.size else (-1.0, 1.0)
    if validos.size:
        p_bajo, p_alto = (float(v) for v in np.percentile(validos, [2, 98]))
        if alto - bajo > 20 * max(p_alto - p_bajo, 1e-12):
            bajo, alto = p_bajo, p_alto
    bajo, alto = min([bajo] + alturas), max([alto] + alturas)
    if alto - bajo < 1e-12:
        bajo, alto = bajo - 1, alto + 1
    margen = 0.12 * (alto - bajo)
    return bajo - margen, alto + margen


def datos_grafica_funcion(reporte: Dict) -> Dict:
    """Curva de f, rectas tangentes (Newton) o secantes y aproximaciones de las primeras iteraciones."""
    _, _, f, _ = preparar_funcion(reporte["funcion"])
    secante = reporte["metodo"] == "secante"
    filas = [fl for fl in reporte["filas"][:MAX_RECTAS] if fl["fxi"] is not None]
    x0, aproximacion = reporte["x0"], reporte["aproximacion"]

    # Ventana en x: x0 y las aproximaciones cercanas (las que se disparan quedan fuera).
    puntos = [x0] + [fl["x_siguiente"] for fl in filas if fl["x_siguiente"] is not None]
    puntos += [fl["x_anterior"] for fl in filas] if secante else []
    if aproximacion is not None:
        puntos.append(aproximacion)
    visibles = [p for p in puntos if abs(p - x0) <= 100 * max(1.0, abs(x0))]
    a, b = min(visibles), max(visibles)
    margen = max(0.25 * (b - a), 1.0) if b > a else 3.0
    x_min, x_max = a - margen, b + margen

    xs = np.linspace(x_min, x_max, PUNTOS_GRAFICA)
    ys = evaluar_vector(f, xs)
    alturas = [fl["fxi"] for fl in filas if x_min <= fl["xi"] <= x_max] + [0.0]
    y_min, y_max = rango_y(ys, alturas)
    with np.errstate(invalid="ignore"):  # corta la curva en las asíntotas
        salto = (np.abs(np.diff(ys)) > (y_max - y_min)) & (ys[:-1] * ys[1:] < 0)
    ys[1:][salto] = np.nan

    rectas = []
    for fl in filas:
        pendiente = fl["pendiente"] if secante else fl["dfxi"]
        if pendiente is None or not x_min <= fl["xi"] <= x_max:
            continue
        extremos = [fl["xi"]] + ([fl["x_anterior"]] if secante else [])
        if fl["x_siguiente"] is None:   # pendiente nula: recta en toda la ventana
            tx = np.array([x_min, x_max])
        else:
            extremos.append(fl["x_siguiente"])
            extra = max(0.15 * (max(extremos) - min(extremos)), 0.06 * (x_max - x_min))
            tx = np.clip([min(extremos) - extra, max(extremos) + extra], x_min, x_max)
        rectas.append({"i": fl["i"], "xi": fl["xi"], "fxi": fl["fxi"], "x_siguiente": fl["x_siguiente"],
                       "x_anterior": fl["x_anterior"] if secante else None,
                       "f_anterior": fl["f_anterior"] if secante else None,
                       "x": tx, "y": fl["fxi"] + pendiente * (tx - fl["xi"])})

    etiqueta = (f"Raíz aproximada x ≈ {reporte['aproximacion_texto']}" if reporte["convergio"]
                else "Última aproximación (no es raíz)")
    return {"funcion": reporte["funcion"], "x": xs, "y": ys, "x_min": x_min, "x_max": x_max,
            "y_min": y_min, "y_max": y_max, "rectas": rectas,
            "nombre_rectas": "Rectas secantes" if secante else "Rectas tangentes",
            "titulo": f"{'Secante' if secante else 'Newton-Raphson'}: f(x) = {reporte['funcion']}",
            "aproximacion": aproximacion if aproximacion is not None and x_min <= aproximacion <= x_max else None,
            "etiqueta_final": etiqueta, "fuera_de_ventana": len(visibles) < len(puntos)}


def dibujar_funcion(ejes, datos: Dict) -> None:
    """Dibuja f(x), el eje x, las tangentes o secantes y las aproximaciones."""
    ejes.plot(datos["x"], datos["y"], color=COLOR_CURVA, linewidth=2.2, label=f"f(x) = {datos['funcion']}")
    ejes.axhline(0, color="#334155", linewidth=1.1, label="Eje x (y = 0)")
    etiquetados: List[float] = []
    ancho = datos["x_max"] - datos["x_min"]

    def etiquetar(x: float, indice: int) -> None:
        # Nombre xᵢ bajo el eje, solo si no queda encima de otro.
        if datos["x_min"] <= x <= datos["x_max"] and all(abs(x - e) > 0.04 * ancho for e in etiquetados):
            ejes.annotate(rf"$x_{{{indice}}}$", (x, 0), textcoords="offset points", xytext=(0, -15),
                          ha="center", fontsize=10, color="#0f172a")
            etiquetados.append(x)

    for k, r in enumerate(datos["rectas"]):
        ejes.plot(r["x"], r["y"], linestyle="--", color=COLOR_RECTA, linewidth=1.4,
                  label=datos["nombre_rectas"] if k == 0 else None)
        ejes.plot([r["xi"], r["xi"]], [0, r["fxi"]], linestyle=":", color="#94a3b8", linewidth=1)
        ejes.plot(r["xi"], r["fxi"], "o", color=COLOR_PUNTO, markersize=5.5, zorder=5,
                  label=r"$(x_i,\ f(x_i))$" if k == 0 else None)
        etiquetar(r["xi"], r["i"])
        if r["x_anterior"] is not None and r["f_anterior"] is not None:
            ejes.plot(r["x_anterior"], r["f_anterior"], "o", color=COLOR_PUNTO, markersize=5.5, zorder=5)
            etiquetar(r["x_anterior"], r["i"] - 1)
        if r["x_siguiente"] is not None:
            ejes.plot(r["x_siguiente"], 0, "s", color=COLOR_RECTA, markersize=5, zorder=5,
                      label=r"Aproximaciones $x_{i+1}$" if k == 0 else None)
            etiquetar(r["x_siguiente"], r["i"] + 1)
    if datos["aproximacion"] is not None:
        ejes.plot(datos["aproximacion"], 0, "o", color=COLOR_APROXIMACION, markersize=9,
                  markeredgecolor="white", zorder=6, label=datos["etiqueta_final"])
    if datos["fuera_de_ventana"]:
        ejes.text(0.01, 0.02, "Algunas aproximaciones quedan fuera de la ventana (se alejan).",
                  transform=ejes.transAxes, fontsize=8, color="#b91c1c")
    ejes.set_xlim(datos["x_min"], datos["x_max"])
    ejes.set_ylim(datos["y_min"], datos["y_max"])
    ejes.set_title(datos["titulo"], fontsize=12)
    ejes.set_xlabel("x")
    ejes.set_ylabel("f(x)")
    ejes.grid(True, alpha=0.3)
    ejes.legend(loc="best", fontsize=8.5)


def datos_grafica_errores(reporte: Dict) -> Optional[Dict]:
    """Error por iteración (del método y del comparado) frente a la tolerancia."""
    criterio = reporte["criterio"]
    clave = "error_abs" if criterio["tipo"] == "absoluto" else "error_rel"
    metodos = reporte["comparacion"]["metodos"] if reporte.get("comparacion") else [{
        "nombre": "Newton-Raphson" if reporte["metodo"] == "newton" else "Secante",
        "iteraciones": reporte["iteraciones"],
        "errores": [fila[clave] for fila in reporte["filas"] if fila["x_siguiente"] is not None]}]
    series = []
    for k, m in enumerate(metodos):
        puntos = [(i + 1, e) for i, e in enumerate(m["errores"]) if e is not None and e > 0]
        if puntos:
            series.append({"nombre": f"{m['nombre']} ({m['iteraciones']} it.)",
                           "iteraciones": [p[0] for p in puntos], "errores": [p[1] for p in puntos],
                           "color": COLORES_SERIES[k % len(COLORES_SERIES)], "marcador": "os^d"[k % 4]})
    if not series:
        return None
    absoluto = criterio["tipo"] == "absoluto"
    return {"series": series, "tolerancia": criterio["tolerancia"],
            "etiqueta_y": r"$E_a = |x_{i+1} - x_i|$" if absoluto else r"$\varepsilon_a$ (%)",
            "etiqueta_tol": (f"Tolerancia ε = {criterio['tolerancia']:g}" if absoluto
                             else f"Tolerancia εs = {criterio['tolerancia']:g} %")}


def dibujar_errores(ejes, datos: Dict) -> None:
    """Error por iteración en escala logarítmica (convergencia rápida o lenta)."""
    from matplotlib.ticker import MaxNLocator

    for s in datos["series"]:
        ejes.semilogy(s["iteraciones"], s["errores"], marker=s["marcador"], color=s["color"],
                      linewidth=2, label=s["nombre"])
    ejes.xaxis.set_major_locator(MaxNLocator(integer=True))  # iteraciones enteras
    ejes.axhline(datos["tolerancia"], color=COLOR_APROXIMACION, linestyle="--", linewidth=1.2,
                 label=datos["etiqueta_tol"])
    ejes.set_title("Convergencia: error por iteración (escala logarítmica)", fontsize=12)
    ejes.set_xlabel("Iteración i")
    ejes.set_ylabel(datos["etiqueta_y"])
    ejes.grid(True, which="both", alpha=0.3)
    ejes.legend(loc="best", fontsize=8.5)


ESTILOS_H = {  # adelante y atrás suelen coincidir: grosor y trazo distintos para ver ambas
    "adelante": {"marker": "o", "linestyle": "-", "linewidth": 3.4, "alpha": 0.55},
    "atras": {"marker": "s", "linestyle": "--", "linewidth": 1.6, "markerfacecolor": "none"},
    "central": {"marker": "^", "linestyle": "-", "linewidth": 2},
}


def dibujar_error_h(ejes, datos: Dict) -> None:
    """Error de las tres fórmulas frente a h (log-log): truncamiento vs redondeo."""
    for k, (clave, nombre, orden, _) in enumerate(FORMULAS_DERIVADA):
        puntos = [(h, e) for h, e in zip(datos["h"], datos["errores"][clave]) if e is not None and e > 0]
        if puntos:
            ejes.loglog([p[0] for p in puntos], [p[1] for p in puntos], color=COLORES_SERIES[k],
                        label=f"{nombre} ({orden})", **ESTILOS_H[clave])
    ejes.axvline(datos["h_usuario"], color=COLOR_APROXIMACION, linestyle="--", linewidth=1.2,
                 label=f"h elegido = {datos['h_usuario']:g}")
    ejes.set_title("Error de la derivada numérica según el paso h", fontsize=12)
    ejes.set_xlabel("Paso h")
    ejes.set_ylabel("Error absoluto")
    ejes.grid(True, which="both", alpha=0.3)
    ejes.legend(loc="best", fontsize=8.5)


def datos_grafica_polinomio(reporte: Dict) -> Dict:
    """Ventana que contiene las raíces reales y la curva de p(x)."""
    reales = [r["real"] for r in reporte["raices"] if r["tipo"] == "real" and r["real"] is not None]
    centro = reales if reales else [reporte["x0"]]
    a, b = min(centro), max(centro)
    margen = max(0.3 * (b - a), 1.0)
    xs = np.linspace(a - margen, b + margen, PUNTOS_GRAFICA)
    ys = np.polyval(reporte["coeficientes"], xs)
    return {"x": xs, "y": ys, "polinomio": reporte["polinomio"], "reales": reales,
            "complejas": [r["texto"] for r in reporte["raices"] if r["tipo"] == "compleja"],
            "rango_y": rango_y(ys, [0.0])}


def dibujar_polinomio(ejes, datos: Dict) -> None:
    """Dibuja p(x) y marca las raíces reales encontradas."""
    ejes.plot(datos["x"], datos["y"], color=COLOR_CURVA, linewidth=2.2, label=f"p(x) = {datos['polinomio']}")
    ejes.axhline(0, color="#334155", linewidth=1.1)
    if datos["reales"]:
        ejes.plot(datos["reales"], [0] * len(datos["reales"]), "o", color=COLOR_APROXIMACION,
                  markersize=8, markeredgecolor="white", zorder=5, label="Raíces reales aproximadas")
    if datos["complejas"]:
        ejes.text(0.01, 0.02, "Raíces complejas: " + ", ".join(datos["complejas"]),
                  transform=ejes.transAxes, fontsize=8.5, color="#334155")
    ejes.set_ylim(*datos["rango_y"])
    ejes.set_title("Raíces del polinomio (Horner, Newton y deflación)", fontsize=12)
    ejes.set_xlabel("x")
    ejes.set_ylabel("p(x)")
    ejes.grid(True, alpha=0.3)
    ejes.legend(loc="best", fontsize=8.5)


def graficas_de(reporte: Dict) -> List[Dict]:
    """Gráficas de un reporte: título, descripción, función de dibujo y datos."""
    metodo, lista = reporte["metodo"], []
    if metodo in ("newton", "secante"):
        rectas = "tangentes" if metodo == "newton" else "secantes"
        lista.append({"id": "funcion", "titulo": "Gráfica del proceso",
                      "descripcion": f"f(x), el eje x, las rectas {rectas} de las primeras iteraciones y "
                                     "las aproximaciones obtenidas.",
                      "dibujar": dibujar_funcion, "datos": datos_grafica_funcion(reporte),
                      "archivo": f"grafica_{metodo}.png"})
        datos = datos_grafica_errores(reporte)
        if datos:
            lista.append({"id": "errores", "titulo": "Convergencia: error por iteración",
                          "descripcion": "Error de cada iteración en escala logarítmica frente a la "
                                         "tolerancia: una caída cada vez más empinada indica convergencia "
                                         "rápida (cuadrática); una recta, convergencia lineal.",
                          "dibujar": dibujar_errores, "datos": datos, "archivo": f"errores_{metodo}.png"})
    elif metodo == "derivadas" and reporte["analisis_h"]:
        lista.append({"id": "error_h", "titulo": "Error vs. paso h",
                      "descripcion": "Escala log-log: el error de truncamiento baja con h, pero con h muy "
                                     "pequeño aparece el error de redondeo.",
                      "dibujar": dibujar_error_h,
                      "datos": {**reporte["analisis_h"], "h_usuario": reporte["h"]},
                      "archivo": "derivadas_error_h.png"})
    elif metodo == "polinomio":
        lista.append({"id": "polinomio", "titulo": "Gráfica de p(x)",
                      "descripcion": "Curva del polinomio con las raíces reales encontradas.",
                      "dibujar": dibujar_polinomio, "datos": datos_grafica_polinomio(reporte),
                      "archivo": "polinomio.png"})
    return lista


def figura_png(dibujar: Callable, datos: Dict) -> str:
    """Genera la figura con Matplotlib y la devuelve como PNG en base64 (para la web)."""
    from matplotlib.figure import Figure

    figura = Figure(figsize=(9, 5.2), dpi=120)
    dibujar(figura.subplots(), datos)
    figura.tight_layout()
    buffer = io.BytesIO()
    figura.savefig(buffer, format="png")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def graficas_png(reporte: Dict) -> List[Dict]:
    """Las gráficas del reporte como imágenes PNG (base64) para la web."""
    return [{"id": g["id"], "titulo": g["titulo"], "descripcion": g["descripcion"],
             "archivo": g["archivo"], "png": figura_png(g["dibujar"], g["datos"])}
            for g in graficas_de(reporte)]


def mostrar_figura(dibujar: Callable, datos: Dict, archivo: str) -> None:
    """Abre la gráfica en una ventana (o la guarda como PNG si no hay pantalla)."""
    import matplotlib
    import matplotlib.pyplot as plt

    figura, ejes = plt.subplots(figsize=(9, 5.5))
    dibujar(ejes, datos)
    figura.tight_layout()
    if matplotlib.get_backend().lower() == "agg":
        ruta = Path.cwd() / archivo
        figura.savefig(ruta, dpi=130)
        print(f"  Gráfica guardada en: {ruta}")
    else:
        print("  (Cierre la ventana de la gráfica para continuar.)")
        plt.show()
    plt.close(figura)


# ═══════════════════════════════════════════════════════════════════════════
# F. INTERFAZ DE CONSOLA (opción 7 del menú principal)
# ═══════════════════════════════════════════════════════════════════════════
LINEA = "─" * 78
OPCION_VOLVER = "6"

ARTE_ASCII = (
    "  xᵢ₊₁ = xᵢ − f(xᵢ)/f′(xᵢ)    MÓDULO: MÉTODOS ABIERTOS (Programa 9)\n"
    "  ───●──────●──── x          Newton-Raphson · Secante · Derivadas numéricas\n"
    "    xᵢ₊₁     xᵢ              Polinomios (Horner y deflación) · Tablas y gráficas"
)

# Campo -> (pregunta, valor predeterminado mostrado al usuario).
PREGUNTAS = {
    "funcion": ("f(x) con sintaxis de SymPy (p. ej. x**3 - 2*x - 5)", None),
    "polinomio": ("p(x) (p. ej. x**3 - 6*x**2 + 11*x - 6) o sus coeficientes 1, -6, 11, -6", None),
    "x0": ("Valor inicial x0", None),
    "x1": ("Segundo valor inicial x1", None),
    "x": ("Punto x donde se deriva", None),
    "h": ("Paso h", POR_DEFECTO["h_derivadas"]),
    "tipo_error": ("Criterio de parada: absoluto o relativo", POR_DEFECTO["tipo_error"]),
    "max_iter": ("Máximo de iteraciones Nmax", POR_DEFECTO["max_iter"]),
    "derivada": ("Derivada: analitica (SymPy) o central (numérica)", "analitica"),
}


def pedir(mensaje: str, por_defecto: Optional[str] = None) -> str:
    """Lee un dato; si se deja vacío usa el valor predeterminado (mostrado entre corchetes)."""
    sufijo = f" [{por_defecto}]" if por_defecto is not None else ""
    texto = input(f"  {mensaje}{sufijo}: ").strip()
    return texto if texto or por_defecto is None else por_defecto


def pedir_tolerancia(tipo: str) -> str:
    """Pide la tolerancia en la unidad del criterio elegido (decimal o %)."""
    unidad = "decimal ε" if tipo == "absoluto" else "εs en %"
    return pedir(f"Tolerancia ({unidad})", POR_DEFECTO[f"tolerancia_{tipo}"])


def pedir_criterio() -> Dict[str, str]:
    """Pide el tipo de error, la tolerancia correspondiente y Nmax (con sus predeterminados)."""
    tipo = TIPOS_ERROR.get(pedir(*PREGUNTAS["tipo_error"]).lower(), "relativo")
    return {"tipo_error": tipo, "tolerancia": pedir_tolerancia(tipo),
            "max_iter": pedir(*PREGUNTAS["max_iter"])}


def preguntar_si(pregunta: str) -> bool:
    """Pregunta de sí o no (Enter = sí)."""
    return input(f"\n  {pregunta} (s/n) [s]: ").strip().lower() in ("", "s", "si", "sí")


def imprimir_tabla(tabla: Dict, sangria: str = "  ") -> None:
    """Imprime una tabla (columnas y filas) con Pandas."""
    texto = pd.DataFrame(tabla["filas"], columns=tabla["columnas"]).to_string(index=False)
    for linea in texto.splitlines():
        print(f"{sangria}{linea}")


def imprimir_pasos(reporte: Dict) -> None:
    """Paso a paso del procedimiento, grupo por grupo."""
    print(f"\n{LINEA}\n  PASO A PASO\n{LINEA}")
    for grupo in reporte["pasos"]:
        print(f"\n  [{grupo['etiqueta']}]")
        for k, p in enumerate(grupo["pasos"]):
            print(f"    {'abcdefghijklmnopqrstuvwxyz'[k % 26]}) {p['titulo']}: {p['texto']}")
            if p["tabla"]:
                imprimir_tabla(p["tabla"], "       ")
            if p["nota"]:
                print(f"       → {p['nota']}")


def imprimir_raiz(r: Dict) -> None:
    """Resultado de Newton o de la secante."""
    print(f"\n  {'✓' if r['convergio'] else '✗'} Estado: {r['titulo_estado']}")
    print(f"    {r['mensaje']}")
    etiqueta = "Raíz aproximada  x ≈" if r["convergio"] else "Última aproximación x ="
    print(f"\n  {etiqueta} {r['aproximacion_texto']}")
    print(f"    {r['detalle_aproximacion']}")
    print(f"  Iteraciones realizadas: {r['iteraciones']} (Nmax = {r['criterio']['max_iter']})")
    print(f"  Error alcanzado:        {r['error_final_texto']}")
    print(f"  Residuo |f(x)|:         {r['residuo_texto']}   → {r['nota_residuo']}")
    print(f"\n  Convergencia: {r['convergencia']['texto']}")
    if r["comparacion"]:
        print(f"\n  {r['comparacion']['titulo']}: {r['comparacion']['texto']}")
    contraste = r["contraste_scipy"]
    if contraste:
        detalle = (f"{contraste['raiz_texto']}   |diferencia| = {contraste['diferencia_texto']}"
                   if contraste["disponible"] else contraste["motivo"])
        print(f"  Contraste opcional con SciPy: {detalle}")


def imprimir_reporte(r: Dict) -> None:
    """Muestra el resultado según el método."""
    print(f"\n{LINEA}")
    if r["metodo"] in ("newton", "secante"):
        iniciales = (f"x₀ = {formatear(r['x0'])}" if r["metodo"] == "newton"
                     else f"x₀ = {formatear(r['x0'])}, x₁ = {formatear(r['x1'])}")
        titulo = "NEWTON-RAPHSON" if r["metodo"] == "newton" else "SECANTE"
        print(f"  {titulo}   f(x) = {r['funcion']}   {iniciales}")
        print(f"  Criterio de parada: {r['criterio_parada']}\n{LINEA}")
        for aviso in r["avisos"]:
            print(f"  ⚠ {aviso}")
        if r["metodo"] == "newton":
            usada = ("analítica (SymPy)" if r["derivada_usada"] == "analitica"
                     else f"diferencia central con h = {r['h']:g}")
            print(f"  f′(x) = {r['derivada']}   (derivada usada: {usada})\n")
        imprimir_tabla(r["tabla"])
        imprimir_raiz(r)
        print("\n  Análisis de convergencia:")
        imprimir_tabla(r["convergencia"]["tabla"], "    ")
    elif r["metodo"] == "derivadas":
        print(f"  DERIVADAS NUMÉRICAS   f(x) = {r['funcion']}   x = {formatear(r['x'])}   h = {r['h']:g}")
        print(f"{LINEA}\n  f′(x) analítica = {r['derivada']}  →  f′({formatear(r['x'])}) = {r['exacta_texto']}\n")
        imprimir_tabla(r["tabla"])
        if r["analisis_h"]:
            print("\n  Error según el paso h:")
            imprimir_tabla(r["analisis_h"]["tabla"], "    ")
            print(f"  {r['analisis_h']['texto']}")
    else:
        print(f"  RAÍCES DE POLINOMIOS   p(x) = {r['polinomio']}   x₀ = {formatear(r['x0'])}")
        print(f"  Criterio de parada: {r['criterio_parada']}\n{LINEA}")
        imprimir_tabla(r["tabla"])
        print(f"\n  {'✓' if r['estado'] == 'completo' else '✗'} {r['mensaje']}")
        print("\n  Validación con numpy.roots:")
        imprimir_tabla(r["validacion"]["tabla"], "    ")
        print(f"  {r['validacion']['nota']}")


def ejecutar_en_consola(resolver: Callable, datos: Dict[str, str]) -> None:
    """Resuelve; si un dato es inválido explica el error y vuelve a pedir solo ese dato."""
    while True:
        try:
            reporte = resolver(**datos)
            break
        except ErrorNumerico as error:
            print(f"  ✗ {error.mensaje}")
            campo = error.campo if error.campo in datos else next(iter(datos))
            if campo == "tolerancia":
                datos[campo] = pedir_tolerancia(TIPOS_ERROR.get(datos.get("tipo_error", ""), "relativo"))
            else:
                datos[campo] = pedir(*PREGUNTAS[campo])
    imprimir_reporte(reporte)
    if preguntar_si("¿Ver el paso a paso?"):
        imprimir_pasos(reporte)
    graficas = graficas_de(reporte)
    if graficas and preguntar_si(f"¿Mostrar {'la gráfica' if len(graficas) == 1 else 'las gráficas'}?"):
        for grafica in graficas:
            mostrar_figura(grafica["dibujar"], grafica["datos"], grafica["archivo"])


def elegir_ejemplo(titulo: str, ejemplos: List[Dict]) -> Optional[Dict]:
    """Muestra ejemplos numerados; devuelve el elegido o None para escribir los datos."""
    print(f"\n  {titulo}")
    for k, ejemplo in enumerate(ejemplos, start=1):
        print(f"    {k}. {ejemplo['nombre']}")
    while True:
        texto = input(f"  Ejemplo (1-{len(ejemplos)}) o Enter para escribir los datos: ").strip()
        if not texto:
            return None
        if texto.isdigit() and 1 <= int(texto) <= len(ejemplos):
            ejemplo = ejemplos[int(texto) - 1]
            print(f"\n  {ejemplo['nombre']}: {ejemplo['descripcion']}")
            return ejemplo
        print("  ✗ Opción no válida.")


def _datos_de(ejemplo: Dict, claves: List[str]) -> Dict[str, str]:
    """Solo los campos que usa el método elegido."""
    return {clave: ejemplo[clave] for clave in claves if clave in ejemplo}


def opcion_newton() -> None:
    """Newton-Raphson con datos propios (criterio, derivada y h con valores predeterminados)."""
    print("\n── NEWTON-RAPHSON ──")
    print(AYUDA_FUNCIONES)
    print(f"  Predeterminados: criterio relativo con εs = {POR_DEFECTO['tolerancia_relativo']} % "
          f"(o absoluto con ε = {POR_DEFECTO['tolerancia_absoluto']}) y Nmax = {POR_DEFECTO['max_iter']}.")
    datos = {"funcion": pedir(*PREGUNTAS["funcion"]), "x0": pedir(*PREGUNTAS["x0"]), **pedir_criterio()}
    datos["derivada"] = "central" if pedir(*PREGUNTAS["derivada"]).lower().startswith("c") else "analitica"
    if datos["derivada"] == "central":
        datos["h"] = pedir("Paso h de la diferencia central", POR_DEFECTO["h_newton"])
    ejecutar_en_consola(resolver_newton_raphson, datos)


def opcion_casos() -> None:
    """Casos obligatorios, adicionales y ejemplos de la clase para Newton."""
    ejemplo = elegir_ejemplo("Casos de Newton-Raphson:", CASOS_NEWTON + EJEMPLOS_ADICIONALES + EJEMPLOS_CLASE)
    if ejemplo:
        ejecutar_en_consola(resolver_newton_raphson, _datos_de(
            ejemplo, ["funcion", "x0", "tolerancia", "max_iter", "tipo_error", "derivada", "h"]))


def opcion_secante() -> None:
    """Método de la secante (con comparación contra Newton)."""
    print("\n── MÉTODO DE LA SECANTE ──")
    ejemplo = elegir_ejemplo("Ejemplos:", EJEMPLOS_SECANTE)
    if ejemplo:
        datos = _datos_de(ejemplo, ["funcion", "x0", "x1", "tolerancia", "max_iter", "tipo_error"])
    else:
        print(AYUDA_FUNCIONES)
        datos = {"funcion": pedir(*PREGUNTAS["funcion"]), "x0": pedir(*PREGUNTAS["x0"]),
                 "x1": pedir(*PREGUNTAS["x1"]), **pedir_criterio()}
    ejecutar_en_consola(resolver_secante, datos)


def opcion_derivadas() -> None:
    """Derivadas numéricas: hacia adelante, hacia atrás y central."""
    print("\n── DERIVADAS NUMÉRICAS ──")
    ejemplo = elegir_ejemplo("Ejemplos:", EJEMPLOS_DERIVADAS)
    if ejemplo:
        datos = _datos_de(ejemplo, ["funcion", "x", "h"])
    else:
        print(AYUDA_FUNCIONES)
        datos = {"funcion": pedir(*PREGUNTAS["funcion"]), "x": pedir(*PREGUNTAS["x"]),
                 "h": pedir(*PREGUNTAS["h"])}
    ejecutar_en_consola(calcular_derivadas, datos)


def opcion_polinomios() -> None:
    """Raíces de polinomios con Horner, Newton y deflación."""
    print("\n── RAÍCES DE POLINOMIOS (HORNER Y DEFLACIÓN) ──")
    ejemplo = elegir_ejemplo("Ejemplos:", EJEMPLOS_POLINOMIO)
    datos = _datos_de(ejemplo, ["polinomio", "x0", "tolerancia", "max_iter", "tipo_error"]) if ejemplo else {
        "polinomio": pedir(*PREGUNTAS["polinomio"]), "x0": pedir(*PREGUNTAS["x0"]), **pedir_criterio()}
    ejecutar_en_consola(resolver_polinomio, datos)


def mostrar_fundamento() -> None:
    """Opción 0: fórmulas, errores, criterio de parada, convergencia y temas relacionados."""
    print(f"\n── FUNDAMENTO MATEMÁTICO ──\n  {FUNDAMENTO}")


def mostrar_menu() -> None:
    """Imprime las opciones del módulo."""
    print("\n  0. Ver fundamento matemático")
    print("  1. Newton-Raphson con datos propios")
    print("  2. Casos de prueba de Newton-Raphson (obligatorios y de la clase)")
    print("  3. Método de la secante")
    print("  4. Derivadas numéricas (adelante, atrás y central)")
    print("  5. Raíces de polinomios (Horner y deflación)")
    print(f"  {OPCION_VOLVER}. Volver al menú principal")


# Opción del menú -> función que la atiende (mismo patrón que MODULOS en main.py).
ACCIONES = {
    "0": mostrar_fundamento,
    "1": opcion_newton,
    "2": opcion_casos,
    "3": opcion_secante,
    "4": opcion_derivadas,
    "5": opcion_polinomios,
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
