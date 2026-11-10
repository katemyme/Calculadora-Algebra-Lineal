"""Parser SEGURO de expresiones f(x) escritas por el usuario (Programa 7).

Por qué no se usa eval()/exec() (ni sympy.parse_expr, que llama a eval por dentro):
el texto del usuario podría ejecutar código arbitrario, como __import__('os').system(...).
En su lugar:

1. ``ast.parse(texto, mode="eval")`` solo construye el ÁRBOL sintáctico de la expresión,
   no ejecuta nada.
2. Se recorre el árbol y se acepta ÚNICAMENTE una lista blanca de nodos: números reales,
   la variable x, las constantes pi y e, los operadores + - * / ** (y el signo) y llamadas
   a funciones matemáticas permitidas con un solo argumento. Cualquier otra cosa (atributos,
   índices, lambdas, comparaciones, cadenas, nombres desconocidos...) se rechaza.
3. Con el árbol ya validado se construyen tres versiones de f, sin ejecutar texto:
   - escalar (módulo math): la usa Bisección y lanza errores claros de dominio;
   - vectorial (NumPy): la usa el graficador para evaluar miles de puntos a la vez;
   - simbólica (SymPy): la usan la continuidad (Bolzano) y la derivada (propagación).
"""

import ast
import math
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import sympy as sp

# x real: así SymPy deriva |x| como sign(x) y estudia la continuidad en ℝ.
X = sp.Symbol("x", real=True)

LONGITUD_MAXIMA = 200        # caracteres de la expresión
PROFUNDIDAD_MAXIMA = 40      # anidamiento del árbol (evita expresiones patológicas)
EXPONENTE_MAXIMO = 1000      # |exponente| numérico máximo en la versión simbólica
CIFRAS_MAXIMAS = 10000       # cifras máximas de una potencia numérica exacta en SymPy

# Nombre -> (función escalar math, función NumPy, constructor SymPy).
FUNCIONES: Dict[str, Tuple[Callable, Callable, Callable]] = {
    "sin": (math.sin, np.sin, sp.sin),
    "cos": (math.cos, np.cos, sp.cos),
    "tan": (math.tan, np.tan, sp.tan),
    "asin": (math.asin, np.arcsin, sp.asin),
    "acos": (math.acos, np.arccos, sp.acos),
    "atan": (math.atan, np.arctan, sp.atan),
    "sinh": (math.sinh, np.sinh, sp.sinh),
    "cosh": (math.cosh, np.cosh, sp.cosh),
    "tanh": (math.tanh, np.tanh, sp.tanh),
    "exp": (math.exp, np.exp, sp.exp),
    "log": (math.log, np.log, sp.log),          # logaritmo natural
    "ln": (math.log, np.log, sp.log),           # alias de log
    "log10": (math.log10, np.log10, lambda a: sp.log(a, 10)),
    "sqrt": (math.sqrt, np.sqrt, sp.sqrt),
    "abs": (abs, np.abs, sp.Abs),
}

# Dominio de las funciones que pueden fallar, para explicar el error al usuario.
DOMINIOS: Dict[str, str] = {
    "log": "argumento > 0",
    "ln": "argumento > 0",
    "log10": "argumento > 0",
    "sqrt": "argumento ≥ 0",
    "asin": "argumento entre −1 y 1",
    "acos": "argumento entre −1 y 1",
}

CONSTANTES: Dict[str, Tuple[float, sp.Expr]] = {
    "pi": (math.pi, sp.pi),
    "e": (math.e, sp.E),
}

# Solo estos caracteres pueden aparecer: bloquea comillas, corchetes, guiones bajos, etc.
_CARACTERES_PERMITIDOS = re.compile(r"[0-9A-Za-z.+\-*/()\s]*")
# Sustituciones de símbolos que se suelen copiar de documentos.
_SUSTITUCIONES = {"−": "-", "×": "*", "·": "*", "÷": "/"}


class ErrorNumerico(ValueError):
    """Error atribuible a los datos del usuario. `campo` indica qué entrada lo causó."""

    def __init__(self, mensaje: str, campo: Optional[str] = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo


class ErrorDeExpresion(ErrorNumerico):
    """La expresión está mal escrita o usa algo fuera de la lista blanca."""


class ErrorDeEvaluacion(ErrorNumerico):
    """f(x) no se puede evaluar en un punto: dominio, división entre cero, overflow, no finito."""


class _FalloPuntual(Exception):
    """Uso interno: motivo de un fallo de evaluación (sin el valor de x)."""


def formatear(valor: float) -> str:
    """Número legible para mensajes: hasta 10 cifras significativas."""
    if valor == int(valor) and abs(valor) < 1e15:
        return str(int(valor))
    return f"{valor:.10g}"


# ---------------------------------------------------------------------------
# Evaluación escalar (math): errores claros en vez de nan silenciosos
# ---------------------------------------------------------------------------
def _dividir(numerador: float, denominador: float) -> float:
    if denominador == 0:
        raise _FalloPuntual("división entre cero")
    return numerador / denominador


def _potencia(base: float, exponente: float) -> float:
    if base == 0 and exponente < 0:
        raise _FalloPuntual("división entre cero (0 elevado a un exponente negativo)")
    # En Python, (-8) ** (1/3) devuelve un número COMPLEJO: se rechaza como "no real".
    if base < 0 and not float(exponente).is_integer():
        raise _FalloPuntual(
            f"potencia no real: base negativa ({formatear(base)}) con exponente "
            f"no entero ({formatear(exponente)})"
        )
    try:
        return base ** exponente
    except OverflowError:
        raise _FalloPuntual("desbordamiento (overflow): la potencia es demasiado grande")
    except ZeroDivisionError:
        raise _FalloPuntual("división entre cero")


def _comprobar_finito(valor: float) -> float:
    # Un overflow en +, - o * no lanza excepción en Python: produce inf. Se detecta aquí.
    if isinstance(valor, complex):
        raise _FalloPuntual("el resultado no es un número real")
    if math.isinf(valor):
        raise _FalloPuntual(
            "desbordamiento (overflow): el resultado supera el mayor float (≈1.8·10³⁰⁸) "
            "y se volvió inf"
        )
    if math.isnan(valor):
        raise _FalloPuntual("el resultado no está definido (nan)")
    return valor


def _compilar_escalar(nodo: ast.AST) -> Callable[[float], float]:
    """Convierte el árbol (ya validado) en una función de Python hecha de cierres (sin exec)."""
    if isinstance(nodo, ast.Constant):
        valor = float(nodo.value)
        return lambda x: valor
    if isinstance(nodo, ast.Name):
        if nodo.id == "x":
            return lambda x: x
        valor = CONSTANTES[nodo.id][0]
        return lambda x: valor
    if isinstance(nodo, ast.UnaryOp):
        operando = _compilar_escalar(nodo.operand)
        if isinstance(nodo.op, ast.USub):
            return lambda x: -operando(x)
        return operando
    if isinstance(nodo, ast.BinOp):
        izq, der = _compilar_escalar(nodo.left), _compilar_escalar(nodo.right)
        if isinstance(nodo.op, ast.Add):
            return lambda x: _comprobar_finito(izq(x) + der(x))
        if isinstance(nodo.op, ast.Sub):
            return lambda x: _comprobar_finito(izq(x) - der(x))
        if isinstance(nodo.op, ast.Mult):
            return lambda x: _comprobar_finito(izq(x) * der(x))
        if isinstance(nodo.op, ast.Div):
            return lambda x: _comprobar_finito(_dividir(izq(x), der(x)))
        return lambda x: _comprobar_finito(_potencia(izq(x), der(x)))
    # ast.Call: función de la lista blanca con un argumento.
    nombre = nodo.func.id
    funcion = FUNCIONES[nombre][0]
    argumento = _compilar_escalar(nodo.args[0])

    def llamar(x: float) -> float:
        valor = argumento(x)
        try:
            return _comprobar_finito(funcion(valor))
        except ValueError:
            dominio = DOMINIOS.get(nombre)
            detalle = f" (el dominio de {nombre} exige {dominio})" if dominio else ""
            raise _FalloPuntual(f"{nombre}({formatear(valor)}) no está definido{detalle}")
        except OverflowError:
            raise _FalloPuntual(
                f"desbordamiento (overflow): {nombre}({formatear(valor)}) es demasiado grande"
            )

    return llamar


# ---------------------------------------------------------------------------
# Evaluación vectorial (NumPy): para el graficador; lo no definido queda como nan
# ---------------------------------------------------------------------------
def _compilar_vector(nodo: ast.AST) -> Callable[[np.ndarray], np.ndarray]:
    if isinstance(nodo, ast.Constant):
        valor = float(nodo.value)
        return lambda xs: np.full_like(xs, valor)
    if isinstance(nodo, ast.Name):
        if nodo.id == "x":
            return lambda xs: xs
        valor = CONSTANTES[nodo.id][0]
        return lambda xs: np.full_like(xs, valor)
    if isinstance(nodo, ast.UnaryOp):
        operando = _compilar_vector(nodo.operand)
        if isinstance(nodo.op, ast.USub):
            return lambda xs: -operando(xs)
        return operando
    if isinstance(nodo, ast.BinOp):
        izq, der = _compilar_vector(nodo.left), _compilar_vector(nodo.right)
        operacion = {
            ast.Add: np.add, ast.Sub: np.subtract, ast.Mult: np.multiply,
            ast.Div: np.divide, ast.Pow: np.power,
        }[type(nodo.op)]
        return lambda xs: operacion(izq(xs), der(xs))
    funcion = FUNCIONES[nodo.func.id][1]
    argumento = _compilar_vector(nodo.args[0])
    return lambda xs: funcion(argumento(xs))


# ---------------------------------------------------------------------------
# Versión simbólica (SymPy), construida nodo a nodo (sin parse_expr)
# ---------------------------------------------------------------------------
def _cifras(numero: sp.Number) -> float:
    """Cifras decimales aproximadas de un número SymPy (sin convertirlo a texto ni a float)."""
    if numero.is_Rational:
        bits = max(abs(numero.p).bit_length(), abs(numero.q).bit_length())
        return bits * math.log10(2) + 1
    return abs(math.log10(abs(float(numero)))) + 1


def _construir_simbolica(nodo: ast.AST) -> sp.Expr:
    if isinstance(nodo, ast.Constant):
        valor = nodo.value
        if isinstance(valor, int):
            return sp.Integer(valor)
        return sp.Integer(int(valor)) if float(valor).is_integer() and abs(valor) < 1e15 \
            else sp.Float(valor)
    if isinstance(nodo, ast.Name):
        return X if nodo.id == "x" else CONSTANTES[nodo.id][1]
    if isinstance(nodo, ast.UnaryOp):
        operando = _construir_simbolica(nodo.operand)
        return -operando if isinstance(nodo.op, ast.USub) else operando
    if isinstance(nodo, ast.BinOp):
        izq, der = _construir_simbolica(nodo.left), _construir_simbolica(nodo.right)
        if isinstance(nodo.op, ast.Add):
            return izq + der
        if isinstance(nodo.op, ast.Sub):
            return izq - der
        if isinstance(nodo.op, ast.Mult):
            return izq * der
        if isinstance(nodo.op, ast.Div):
            return izq / der
        # SymPy calcula EXACTAMENTE las potencias de números (9**9**9 tendría millones de
        # dígitos y colgaría el servidor): se limitan el exponente y el tamaño del resultado.
        if der.is_Number:
            if bool(abs(der) > EXPONENTE_MAXIMO):
                raise ErrorDeExpresion(
                    f"Exponente demasiado grande: el máximo permitido es {EXPONENTE_MAXIMO} "
                    "en valor absoluto."
                )
            if izq.is_Number and izq != 0 and float(abs(der)) * _cifras(izq) > CIFRAS_MAXIMAS:
                raise ErrorDeExpresion(
                    f"La potencia es demasiado grande (tendría más de {CIFRAS_MAXIMAS} cifras)."
                )
        return izq ** der
    return FUNCIONES[nodo.func.id][2](_construir_simbolica(nodo.args[0]))


# ---------------------------------------------------------------------------
# Validación del árbol (lista blanca)
# ---------------------------------------------------------------------------
_OPERADORES_BINARIOS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
_NOMBRES_DE_OPERADOR = {
    ast.FloorDiv: "//", ast.Mod: "%", ast.MatMult: "@", ast.BitXor: "^",
    ast.BitAnd: "&", ast.BitOr: "|", ast.LShift: "<<", ast.RShift: ">>",
}


def _validar(nodo: ast.AST, permitir_x: bool, profundidad: int = 0) -> None:
    """Recorre el árbol y lanza ErrorDeExpresion ante cualquier nodo fuera de la lista blanca."""
    if profundidad > PROFUNDIDAD_MAXIMA:
        raise ErrorDeExpresion("La expresión está demasiado anidada.")
    siguiente = profundidad + 1

    if isinstance(nodo, ast.Constant):
        # bool es subclase de int en Python: se excluye explícitamente.
        if isinstance(nodo.value, bool) or not isinstance(nodo.value, (int, float)):
            if isinstance(nodo.value, complex):
                raise ErrorDeExpresion("No se permiten números complejos (como 2j).")
            raise ErrorDeExpresion("Solo se permiten números reales.")
        try:
            if not math.isfinite(float(nodo.value)):
                raise OverflowError
        except OverflowError:
            raise ErrorDeExpresion("Hay un número demasiado grande para representarlo.")
        return
    if isinstance(nodo, ast.Name):
        if nodo.id == "x":
            if not permitir_x:
                raise ErrorDeExpresion("Aquí se espera un número, no una expresión con x.")
            return
        if nodo.id in CONSTANTES:
            return
        if nodo.id in FUNCIONES:
            raise ErrorDeExpresion(f"Falta el argumento de {nodo.id}: escriba {nodo.id}(x).")
        raise ErrorDeExpresion(
            f"Nombre no permitido: '{nodo.id}'. La única variable es x; las constantes son "
            "pi y e; las funciones: " + ", ".join(sorted(FUNCIONES)) + "."
        )
    if isinstance(nodo, ast.UnaryOp):
        if not isinstance(nodo.op, (ast.UAdd, ast.USub)):
            raise ErrorDeExpresion("Operador no permitido (solo + - * / **).")
        _validar(nodo.operand, permitir_x, siguiente)
        return
    if isinstance(nodo, ast.BinOp):
        if not isinstance(nodo.op, _OPERADORES_BINARIOS):
            simbolo = _NOMBRES_DE_OPERADOR.get(type(nodo.op), "?")
            raise ErrorDeExpresion(f"Operador no permitido: '{simbolo}'. Use + - * / **.")
        _validar(nodo.left, permitir_x, siguiente)
        _validar(nodo.right, permitir_x, siguiente)
        return
    if isinstance(nodo, ast.Call):
        if isinstance(nodo.func, ast.Attribute):
            raise ErrorDeExpresion("Llamada no permitida: no se puede acceder a atributos.")
        if not isinstance(nodo.func, ast.Name):
            # (x+1)(x-1) se lee como "llamar" a (x+1): en realidad falta el operador *.
            raise ErrorDeExpresion(
                "Falta un operador: escriba (x+1)*(x-1) en lugar de (x+1)(x-1)."
            )
        if nodo.func.id not in FUNCIONES:
            raise ErrorDeExpresion(
                f"Función no permitida: '{nodo.func.id}'. Permitidas: "
                + ", ".join(sorted(FUNCIONES)) + "."
            )
        if nodo.keywords or len(nodo.args) != 1 or isinstance(nodo.args[0], ast.Starred):
            raise ErrorDeExpresion(f"{nodo.func.id} recibe exactamente un argumento.")
        _validar(nodo.args[0], permitir_x, siguiente)
        return
    if isinstance(nodo, ast.Attribute):
        raise ErrorDeExpresion("No se permite acceder a atributos (el punto solo es decimal).")
    if isinstance(nodo, ast.Lambda):
        raise ErrorDeExpresion("No se permiten funciones lambda.")
    raise ErrorDeExpresion(
        f"Elemento no permitido en la expresión ({type(nodo).__name__}). "
        "Use solo números, x, pi, e, + - * / ** y funciones matemáticas."
    )


def _pista_de_sintaxis(texto: str, error: SyntaxError) -> str:
    """Mensaje en español con una pista concreta para los errores de escritura más comunes."""
    if texto.count("(") != texto.count(")"):
        return "Los paréntesis no están balanceados: revise que cada '(' tenga su ')'."
    implicito = re.search(r"(\d\.?)\s*([A-Za-z(])|(\))\s*([A-Za-z0-9(])", texto)
    if implicito:
        return (
            "Falta un operador: la multiplicación debe escribirse con * "
            "(por ejemplo 2*x en lugar de 2x, y (x+1)*(x-1) en lugar de (x+1)(x-1))."
        )
    posicion = f" cerca de la posición {error.offset}" if error.offset else ""
    return f"La función está mal escrita{posicion}. Revise operadores y paréntesis."


def _normalizar(texto: str, avisos: List[str]) -> str:
    """Limpia el texto y aplica las conversiones con aviso (^ → **, símbolos tipográficos)."""
    texto = (texto or "").strip()
    # "f(x) = ..." o "y = ..." se aceptan quitando el lado izquierdo.
    lado_izquierdo = re.match(r"^\s*(f\s*\(\s*x\s*\)|y)\s*=", texto)
    if lado_izquierdo:
        texto = texto[lado_izquierdo.end():].strip()
        avisos.append("Se quitó el lado izquierdo «f(x) =»: basta con escribir la expresión.")
    if any(simbolo in texto for simbolo in _SUSTITUCIONES):
        for original, reemplazo in _SUSTITUCIONES.items():
            texto = texto.replace(original, reemplazo)
        avisos.append("Se reemplazaron los símbolos tipográficos (−, ×, ·, ÷) por - * /.")
    if "^" in texto:
        # En Python ^ es el XOR bit a bit, NO la potencia: 2^3 valdría 1, no 8.
        texto = texto.replace("^", "**")
        avisos.append(
            "Se convirtió ^ en ** porque en Python ^ no es potencia (es XOR bit a bit): "
            f"se evaluó «{texto}»."
        )
    return texto


def _analizar_arbol(texto: str, permitir_x: bool, campo: Optional[str]) -> Tuple[ast.Expression, str, List[str]]:
    avisos: List[str] = []
    try:
        texto = _normalizar(texto, avisos)
        if not texto:
            raise ErrorDeExpresion("Escriba una expresión.")
        if len(texto) > LONGITUD_MAXIMA:
            raise ErrorDeExpresion(f"La expresión es demasiado larga (máximo {LONGITUD_MAXIMA} caracteres).")
        if "," in texto:
            raise ErrorDeExpresion(
                "No se permiten comas: use punto como separador decimal (2.5) y recuerde "
                "que cada función recibe un solo argumento."
            )
        if "=" in texto:
            raise ErrorDeExpresion("Escriba solo la expresión, sin '=' (por ejemplo: x**2 - 2).")
        if not _CARACTERES_PERMITIDOS.fullmatch(texto):
            prohibido = next(c for c in texto if not _CARACTERES_PERMITIDOS.fullmatch(c))
            raise ErrorDeExpresion(f"Carácter no permitido: '{prohibido}'.")
        try:
            arbol = ast.parse(texto, mode="eval")
        except SyntaxError as error:
            raise ErrorDeExpresion(_pista_de_sintaxis(texto, error))
        _validar(arbol.body, permitir_x)
    except ErrorDeExpresion as error:
        error.campo = campo
        raise
    return arbol, texto, avisos


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------
@dataclass
class FuncionSegura:
    """f(x) validada, con sus versiones escalar, vectorial y simbólica."""

    texto_original: str
    texto: str
    expresion: sp.Expr
    avisos: List[str] = field(default_factory=list)
    _escalar: Callable[[float], float] = field(default=None, repr=False)
    _vectorial: Callable[[np.ndarray], np.ndarray] = field(default=None, repr=False)

    def evaluar(self, x: float) -> float:
        """f(x) real y finito; si no existe, lanza ErrorDeEvaluacion explicando el motivo."""
        try:
            return float(self._escalar(float(x)))
        except _FalloPuntual as fallo:
            raise ErrorDeEvaluacion(f"No se puede evaluar f({formatear(x)}): {fallo}.")
        except (OverflowError, ZeroDivisionError, ValueError) as fallo:
            # Red de seguridad: ningún error de Python debe llegar al usuario sin explicar.
            raise ErrorDeEvaluacion(f"No se puede evaluar f({formatear(x)}): {fallo}.")

    __call__ = evaluar

    def evaluar_vector(self, xs: np.ndarray) -> np.ndarray:
        """f en muchos puntos; donde no está definida (o no es finita) queda nan."""
        xs = np.asarray(xs, dtype=float)
        # np.errstate silencia los avisos de log(-1), 1/0, etc.: se filtran después con isfinite.
        with np.errstate(all="ignore"):
            ys = np.asarray(self._vectorial(xs), dtype=float)
        if ys.shape != xs.shape:          # f constante: se repite el valor en cada punto
            ys = np.full_like(xs, float(ys))
        ys[~np.isfinite(ys)] = np.nan
        return ys

    def derivada(self) -> sp.Expr:
        """f'(x) simbólica (SymPy)."""
        return sp.diff(self.expresion, X)


def analizar_funcion(texto: str, campo: Optional[str] = "funcion") -> FuncionSegura:
    """Valida f(x) y la devuelve lista para evaluar. Lanza ErrorDeExpresion si está mal escrita."""
    arbol, normalizado, avisos = _analizar_arbol(texto, permitir_x=True, campo=campo)
    try:
        expresion = _construir_simbolica(arbol.body)
    except ErrorDeExpresion as error:
        error.campo = campo
        raise
    return FuncionSegura(
        texto_original=texto,
        texto=normalizado,
        expresion=expresion,
        avisos=avisos,
        _escalar=_compilar_escalar(arbol.body),
        _vectorial=_compilar_vector(arbol.body),
    )


def leer_numero(texto: str, nombre: str, campo: Optional[str] = None) -> float:
    """Convierte la entrada en un número real finito.

    Acepta literales (2, -1.5, 1e-4) y expresiones constantes con pi y e (pi/2, -2*pi, e**2),
    usando el mismo parser seguro pero sin permitir x.
    """
    campo = campo or nombre
    original = (texto or "").strip()
    if not original:
        raise ErrorNumerico(f"Falta el valor de {nombre}.", campo)
    try:
        arbol, _, _ = _analizar_arbol(original, permitir_x=False, campo=campo)
        valor = _compilar_escalar(arbol.body)(0.0)
    except (ErrorDeExpresion, _FalloPuntual):
        raise ErrorNumerico(
            f"El valor de {nombre} no es un número válido: '{original}'. "
            "Ejemplos válidos: 2, -1.5, 1e-4, pi/2.",
            campo,
        )
    if not math.isfinite(valor):
        raise ErrorNumerico(f"El valor de {nombre} no es finito: '{original}'.", campo)
    return float(valor)


def leer_entero(texto: str, nombre: str, campo: Optional[str] = None) -> int:
    """Convierte la entrada en un entero (solo dígitos y signo opcional)."""
    campo = campo or nombre
    original = (texto or "").strip()
    if not original:
        raise ErrorNumerico(f"Falta el valor de {nombre}.", campo)
    if not re.fullmatch(r"[+-]?\d{1,9}", original):
        raise ErrorNumerico(
            f"{nombre[0].upper() + nombre[1:]} debe ser un número entero (por ejemplo 100): "
            f"'{original}' no lo es.",
            campo,
        )
    return int(original)
