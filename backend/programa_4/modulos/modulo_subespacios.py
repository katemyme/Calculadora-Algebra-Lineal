"""Módulo de Subespacios: ¿es H un subespacio vectorial de ℝⁿ?

Sigue la receta de la Sesión 13 (Definición de Espacio y Subespacio Vectorial):
H es subespacio de V = ℝⁿ si cumple las cuatro condiciones

    (i)   H ⊂ V                      (por definición)
    (ii)  H ≠ ∅                      (basta ver que el vector nulo 0 ∈ H)
    (iii) x, y ∈ H ⟹ x + y ∈ H       (cerradura bajo la suma)
    (iv)  x ∈ H, α ∈ ℝ ⟹ αx ∈ H      (cerradura bajo el escalar)

y cada cerradura se prueba en cuatro pasos: Hipótesis → Operación →
Verificación → Conclusión, usando vectores GENÉRICOS (con letras). Si una
condición falla, basta un contraejemplo concreto.

El conjunto se puede escribir de dos formas:
  - implícita:   H = (x, y, z)        con la hipótesis  "x - y + z = 0"
  - paramétrica: H = (t - 2s, -s, t)  con la hipótesis  "t, s ∈ ℝ" (opcional)

Cuando H es subespacio y la regla es lineal se obtienen además la forma
paramétrica, la combinación lineal que describe a cada vector de H, los
vectores generadores, la base (comprobando la solución trivial) y la dimensión.

CUMPLIMIENTO DE RESTRICCIONES ACADÉMICAS
----------------------------------------
- No se importa NumPy, SciPy, SymPy ni `math`.
- Toda la aritmética usa `fractions.Fraction` (exacta, sin tolerancias).
- Las expresiones se leen con un analizador propio y se convierten en
  polinomios con coeficientes Fraction.
- La reducción por filas reutiliza `escalonar()` del módulo de Vectores.
- Todo el texto matemático de salida se devuelve en LaTeX para la web.
"""

from fractions import Fraction
from itertools import product
from typing import Dict, List, Optional, Tuple

from modulos.modulo_vectores import construir_matriz_homogenea, escalonar

DIMENSION_MAXIMA: int = 8          # máximo de componentes / condiciones
LONGITUD_MAXIMA: int = 300         # máximo de caracteres por campo

# Escalares que se prueban para buscar un contraejemplo de (iv).
_ESCALARES_PRUEBA = [Fraction(-1), Fraction(2), Fraction(1, 2), Fraction(-2), Fraction(3)]

_REEMPLAZOS = {
    "−": "-", "–": "-", "—": "-", "·": "*", "×": "*", "⋅": "*",
    "≤": "<=", "≥": ">=", "≠": "!=", "²": "^2", "³": "^3", "ℝ": "R",
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
}

_TEX_COMPARADOR = {"=": "=", "<=": r"\le", ">=": r"\ge", "<": "<", ">": ">", "!=": r"\ne"}

_GRIEGAS = {
    "α": r"\alpha", "β": r"\beta", "γ": r"\gamma", "δ": r"\delta", "λ": r"\lambda",
    "μ": r"\mu", "θ": r"\theta", "ρ": r"\rho", "σ": r"\sigma", "φ": r"\varphi",
}

U, V = r"\mathbf{u}", r"\mathbf{v}"
CERO = r"\mathbf{0}"


class ErrorDeSubespacio(Exception):
    """Error de lectura del conjunto o de la hipótesis."""

    def __init__(self, mensaje: str, campo: str):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo


# ---------------------------------------------------------------------------
# Lectura de expresiones: texto -> tokens -> árbol
# ---------------------------------------------------------------------------
# Nodos del árbol (tuplas):
#   ("num", Fraction, texto) ("var", nombre) ("neg", a)
#   ("add", a, b) ("sub", a, b) ("mul", a, b) ("div", a, b) ("pow", a, entero)
def _normalizar(texto: str) -> str:
    for original, nuevo in _REEMPLAZOS.items():
        texto = texto.replace(original, nuevo)
    return texto


def _tokenizar(texto: str, campo: str) -> List[Tuple[str, object]]:
    tokens: List[Tuple[str, object]] = []
    i = 0
    while i < len(texto):
        ch = texto[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or (ch == "." and texto[i + 1:i + 2].isdigit()):
            j = i
            while j < len(texto) and (texto[j].isdigit() or texto[j] == "."):
                j += 1
            literal = texto[i:j]
            try:
                tokens.append(("num", (Fraction(literal), literal)))
            except ValueError:
                raise ErrorDeSubespacio(f"Número no reconocido: '{literal}'.", campo)
            i = j
        elif ch.isalpha():
            # Una variable es UNA letra seguida, opcionalmente, de dígitos
            # (x, y, x1, x_2). "xy" se lee como x·y.
            j = i + 1
            if texto[j:j + 1] == "_" and texto[j + 1:j + 2].isdigit():
                j += 1
            while j < len(texto) and texto[j].isdigit():
                j += 1
            tokens.append(("id", texto[i:j].replace("_", "")))
            i = j
        elif texto[i:i + 2] in ("<=", ">=", "!=", "=="):
            tokens.append(("cmp", "=" if texto[i:i + 2] == "==" else texto[i:i + 2]))
            i += 2
        elif ch in "=<>":
            tokens.append(("cmp", ch))
            i += 1
        elif ch in "+-*/^()":
            tokens.append(("op", ch))
            i += 1
        else:
            raise ErrorDeSubespacio(f"Carácter no reconocido: '{ch}'.", campo)
    return tokens


class _Analizador:
    """Descenso recursivo:  suma → término → unario → potencia → átomo."""

    def __init__(self, tokens, campo: str, texto: str):
        self.tokens = tokens
        self.pos = 0
        self.campo = campo
        self.texto = texto

    def _ver(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _es(self, tipo, valor=None) -> bool:
        token = self._ver()
        return token is not None and token[0] == tipo and (valor is None or token[1] == valor)

    def _error(self, detalle: str):
        raise ErrorDeSubespacio(f"No se pudo leer '{self.texto.strip()}': {detalle}.", self.campo)

    def analizar(self):
        if not self.tokens:
            self._error("la expresión está vacía")
        nodo = self._suma()
        if self._ver() is not None:
            self._error(f"sobra '{self._ver()[1] if self._ver()[0] != 'num' else self._ver()[1][1]}'")
        return nodo

    def _suma(self):
        nodo = self._termino()
        while self._es("op", "+") or self._es("op", "-"):
            operador = self.tokens[self.pos][1]
            self.pos += 1
            nodo = ("add" if operador == "+" else "sub", nodo, self._termino())
        return nodo

    def _termino(self):
        nodo = self._unario()
        while True:
            if self._es("op", "*") or self._es("op", "/"):
                operador = self.tokens[self.pos][1]
                self.pos += 1
                nodo = ("mul" if operador == "*" else "div", nodo, self._unario())
            elif self._es("id") or self._es("op", "("):
                nodo = ("mul", nodo, self._potencia())      # multiplicación implícita: 2x
            else:
                return nodo

    def _unario(self):
        if self._es("op", "-"):
            self.pos += 1
            return ("neg", self._unario())
        if self._es("op", "+"):
            self.pos += 1
            return self._unario()
        return self._potencia()

    def _potencia(self):
        base = self._atomo()
        if self._es("op", "^"):
            self.pos += 1
            if not self._es("num") or self._ver()[1][0].denominator != 1:
                self._error("el exponente debe ser un entero no negativo")
            exponente = int(self._ver()[1][0])
            self.pos += 1
            return ("pow", base, exponente)
        return base

    def _atomo(self):
        token = self._ver()
        if token is None:
            self._error("la expresión termina antes de tiempo")
        self.pos += 1
        if token[0] == "num":
            return ("num", token[1][0], token[1][1])
        if token[0] == "id":
            return ("var", token[1])
        if token == ("op", "("):
            nodo = self._suma()
            if not self._es("op", ")"):
                self._error("falta cerrar un paréntesis")
            self.pos += 1
            return nodo
        self._error(f"no se esperaba '{token[1]}'")


def _leer_expresion(texto: str, campo: str):
    return _Analizador(_tokenizar(texto, campo), campo, texto).analizar()


def _variables_de(nodo) -> List[str]:
    """Variables del árbol en orden de aparición."""
    if nodo[0] == "var":
        return [nodo[1]]
    if nodo[0] == "num":
        return []
    vistas: List[str] = []
    for hijo in nodo[1:]:
        if isinstance(hijo, tuple):
            for nombre in _variables_de(hijo):
                if nombre not in vistas:
                    vistas.append(nombre)
    return vistas


# ---------------------------------------------------------------------------
# Polinomios exactos: {exponentes (tupla de n enteros): Fraction}
# ---------------------------------------------------------------------------
def _limpiar(p: Dict) -> Dict:
    return {mono: coef for mono, coef in p.items() if coef != 0}


def _sumar(p: Dict, q: Dict, signo: int = 1) -> Dict:
    r = dict(p)
    for mono, coef in q.items():
        r[mono] = r.get(mono, Fraction(0)) + signo * coef
    return _limpiar(r)


def _multiplicar(p: Dict, q: Dict) -> Dict:
    r: Dict = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            mono = tuple(a + b for a, b in zip(m1, m2))
            r[mono] = r.get(mono, Fraction(0)) + c1 * c2
    return _limpiar(r)


def _a_polinomio(nodo, indice: Dict[str, int], campo: str) -> Dict:
    n = len(indice)
    cero = tuple([0] * n)
    tipo = nodo[0]
    if tipo == "num":
        return _limpiar({cero: nodo[1]})
    if tipo == "var":
        mono = [0] * n
        mono[indice[nodo[1]]] = 1
        return {tuple(mono): Fraction(1)}
    if tipo == "neg":
        return {m: -c for m, c in _a_polinomio(nodo[1], indice, campo).items()}
    if tipo in ("add", "sub"):
        return _sumar(_a_polinomio(nodo[1], indice, campo),
                      _a_polinomio(nodo[2], indice, campo), 1 if tipo == "add" else -1)
    if tipo == "mul":
        return _multiplicar(_a_polinomio(nodo[1], indice, campo),
                            _a_polinomio(nodo[2], indice, campo))
    if tipo == "div":
        divisor = _a_polinomio(nodo[2], indice, campo)
        if any(sum(m) > 0 for m in divisor):
            raise ErrorDeSubespacio("Solo se puede dividir entre constantes (p. ej. x/2).", campo)
        valor = divisor.get(cero, Fraction(0))
        if valor == 0:
            raise ErrorDeSubespacio("División entre cero.", campo)
        return {m: c / valor for m, c in _a_polinomio(nodo[1], indice, campo).items()}
    # pow
    resultado = {cero: Fraction(1)}
    base = _a_polinomio(nodo[1], indice, campo)
    for _ in range(nodo[2]):
        resultado = _multiplicar(resultado, base)
    return resultado


def _grado(p: Dict) -> int:
    return max((sum(m) for m in p), default=0)


def _parte_lineal(p: Dict, n: int) -> Tuple[Fraction, List[Fraction]]:
    """(término independiente, [coeficiente de cada variable]) de un polinomio de grado ≤ 1."""
    cero = tuple([0] * n)
    coefs = []
    for i in range(n):
        mono = [0] * n
        mono[i] = 1
        coefs.append(p.get(tuple(mono), Fraction(0)))
    return p.get(cero, Fraction(0)), coefs


def _evaluar(p: Dict, punto) -> Fraction:
    total = Fraction(0)
    for mono, coef in p.items():
        termino = coef
        for valor, exponente in zip(punto, mono):
            if exponente:
                termino *= Fraction(valor) ** exponente
        total += termino
    return total


def _compara(a: Fraction, operador: str, b: Fraction) -> bool:
    return {
        "=": a == b, "<=": a <= b, ">=": a >= b,
        "<": a < b, ">": a > b, "!=": a != b,
    }[operador]


# ---------------------------------------------------------------------------
# LaTeX
# ---------------------------------------------------------------------------
def _tex_numero(valor: Fraction) -> str:
    if valor.denominator == 1:
        return str(valor.numerator)
    signo = "-" if valor < 0 else ""
    return rf"{signo}\frac{{{abs(valor.numerator)}}}{{{valor.denominator}}}"


def _partes_nombre(nombre: str) -> Tuple[str, str]:
    letra = nombre[0]
    return _GRIEGAS.get(letra, letra), nombre[1:]


def _tex_variable(nombre: str) -> str:
    letra, digitos = _partes_nombre(nombre)
    return f"{letra}_{{{digitos}}}" if digitos else letra


def _tex_componente(nombre: str, k: int) -> str:
    """Componente de un vector genérico: x -> x₁ / x₂ ; x1 -> x₁' / x₁''."""
    letra, digitos = _partes_nombre(nombre)
    if digitos:
        return f"{letra}_{{{digitos}}}" + "'" * k
    return f"{letra}_{{{k}}}"


def _tex_vector(componentes: List[str]) -> str:
    return r"\left(" + ", ".join(componentes) + r"\right)"


def _tex_vector_numerico(vector: List[Fraction]) -> str:
    return _tex_vector([_tex_numero(v) for v in vector])


def _sustitucion(tex: str, tipo: str, negativo: bool = False) -> Tuple[str, str, bool]:
    """Valor que reemplaza a una variable: tipo 'nombre', 'numero' o 'compuesto'."""
    return (tex, tipo, negativo)


def _sustituir_numeros(variables: List[str], punto) -> Dict:
    return {
        nombre: _sustitucion(_tex_numero(Fraction(valor)), "numero", Fraction(valor) < 0)
        for nombre, valor in zip(variables, punto)
    }


def _tex_arbol(nodo, entorno: Optional[Dict] = None, contexto: str = "libre") -> str:
    """Escribe el árbol en LaTeX; `entorno` reemplaza variables por valores.

    contexto: 'libre' (inicio o izquierda de una suma), 'suma' (derecha de +),
    'resta' (derecha de − o tras un signo menos) o 'producto' (factor).
    """
    tipo = nodo[0]
    if tipo == "num":
        return nodo[2]
    if tipo == "var":
        if not entorno or nodo[1] not in entorno:
            return _tex_variable(nodo[1])
        tex, clase, negativo = entorno[nodo[1]]
        if clase == "nombre":
            return tex
        poner = (
            contexto == "producto"
            or (contexto in ("suma", "resta") and negativo)
            or (clase == "compuesto" and contexto == "resta")
        )
        return f"({tex})" if poner else tex

    def hijo(sub, ctx, parentesis):
        if parentesis:
            return "(" + _tex_arbol(sub, entorno, "libre") + ")"
        return _tex_arbol(sub, entorno, ctx)

    if tipo == "add":
        return f"{_tex_arbol(nodo[1], entorno, contexto)} + {hijo(nodo[2], 'suma', nodo[2][0] == 'neg')}"
    if tipo == "sub":
        derecha = hijo(nodo[2], "resta", nodo[2][0] in ("add", "sub", "neg"))
        return f"{_tex_arbol(nodo[1], entorno, contexto)} - {derecha}"
    if tipo == "neg":
        return "-" + hijo(nodo[1], "resta", nodo[1][0] in ("add", "sub", "neg"))
    if tipo == "mul":
        izquierda = hijo(nodo[1], "producto", nodo[1][0] in ("add", "sub", "neg"))
        derecha = hijo(nodo[2], "producto", nodo[2][0] in ("add", "sub", "neg"))
        separador = r" \cdot " if derecha[:1].isdigit() else " "
        return izquierda + separador + derecha
    if tipo == "div":
        return rf"\frac{{{_tex_arbol(nodo[1], entorno)}}}{{{_tex_arbol(nodo[2], entorno)}}}"
    # pow
    base = hijo(nodo[1], "producto", nodo[1][0] not in ("var", "num"))
    return f"{base}^{{{nodo[2]}}}"


def _tex_lineal(terminos: List[Tuple[Fraction, Optional[str], bool]],
                parentesis_siempre: bool = False) -> str:
    """Σ coef·factor. Cada término es (coef, factor_tex o None, factor_compuesto)."""
    partes: List[str] = []
    for coef, factor, compuesto in terminos:
        if coef == 0:
            continue
        magnitud = abs(coef)
        if factor is None:
            cuerpo = _tex_numero(magnitud)
        else:
            envolver = compuesto and (parentesis_siempre or magnitud != 1 or coef < 0)
            texto = f"({factor})" if envolver else factor
            cuerpo = texto if magnitud == 1 else f"{_tex_numero(magnitud)}{texto}"
        if not partes:
            partes.append(("-" if coef < 0 else "") + cuerpo)
        else:
            partes.append((" - " if coef < 0 else " + ") + cuerpo)
    return "".join(partes) if partes else "0"


def _tex_condicion(cond: Dict, entorno: Optional[Dict] = None) -> str:
    return (f"{_tex_arbol(cond['izq'], entorno)} {_TEX_COMPARADOR[cond['op']]} "
            f"{_tex_arbol(cond['der'], entorno)}")


def _m(tex: str) -> str:
    """Fragmento matemático dentro de una línea de texto."""
    return f"${tex}$"


def _pertenece(a: str, b: str) -> str:
    return _m(rf"{a} \in {b}")


def _no_pertenece(a: str, b: str) -> str:
    return _m(rf"{a} \notin {b}")


def _envolver(tex: str, siempre: bool = False) -> str:
    """(a + b) si el texto tiene varios términos; con `siempre`, también (a)."""
    return f"({tex})" if siempre or " + " in tex or " - " in tex else tex


def _tex_espacio(n: int) -> str:
    return rf"\mathbb{{R}}^{{{n}}}"


def _que_elementos(n: int) -> str:
    return {1: "números reales", 2: "pares ordenados de números reales",
            3: "ternas de números reales"}.get(n, f"{n}-adas de números reales")


# ---------------------------------------------------------------------------
# Lectura del conjunto y de la hipótesis
# ---------------------------------------------------------------------------
def _dividir_nivel_cero(texto: str, separadores: str) -> List[str]:
    partes, actual, nivel = [], "", 0
    for ch in texto:
        if ch == "(":
            nivel += 1
        elif ch == ")":
            nivel -= 1
        if ch in separadores and nivel == 0:
            partes.append(actual)
            actual = ""
        else:
            actual += ch
    partes.append(actual)
    return partes


def _leer_conjunto(texto: str) -> Tuple[str, List[str], str]:
    """Devuelve (nombre, componentes en texto, hipótesis escrita tras ':' o '|')."""
    limpio = _normalizar(texto).replace("{", "").replace("}", "").strip()
    if not limpio:
        raise ErrorDeSubespacio("Escriba el conjunto, por ejemplo H = (x, y, z).", "conjunto")

    extra = ""
    partes = _dividir_nivel_cero(limpio, ":|")
    if len(partes) > 1:
        limpio, extra = partes[0], ",".join(partes[1:])

    inicio = limpio.find("(")
    nombre = "H"
    if inicio < 0:
        cabeza, _, cuerpo = limpio.rpartition("=")
        interior = cuerpo
    else:
        cabeza = limpio[:inicio]
        nivel, fin = 0, -1
        for k in range(inicio, len(limpio)):
            if limpio[k] == "(":
                nivel += 1
            elif limpio[k] == ")":
                nivel -= 1
                if nivel == 0:
                    fin = k
                    break
        if fin < 0:
            raise ErrorDeSubespacio("Falta cerrar el paréntesis del conjunto.", "conjunto")
        interior = limpio[inicio + 1:fin]
        resto = limpio[fin + 1:].strip()
        if resto and not resto.startswith(("∈", "en ", "in ")):
            raise ErrorDeSubespacio(f"No se entiende '{resto}' después del vector.", "conjunto")
    if "=" in cabeza:
        candidato = cabeza.split("=")[0].strip()
        if candidato.isalpha() and len(candidato) <= 3:
            nombre = candidato.upper() if len(candidato) == 1 else candidato
    componentes = [c.strip() for c in _dividir_nivel_cero(interior, ",")]
    if any(not c for c in componentes):
        raise ErrorDeSubespacio("Hay una componente vacía en el conjunto.", "conjunto")
    if len(componentes) > DIMENSION_MAXIMA:
        raise ErrorDeSubespacio(
            f"El vector puede tener a lo sumo {DIMENSION_MAXIMA} componentes.", "conjunto")
    return nombre, componentes, extra


def _es_declaracion(pieza: str) -> Optional[List[str]]:
    """'t, s ∈ R' o 'y' sueltos -> lista de nombres; None si es una condición."""
    texto = pieza
    for marca in ("∈", " en ", " in "):
        if marca in texto:
            texto = texto.split(marca)[0]
            break
    else:
        if any(op in pieza for op in "=<>!"):
            return None
    nombres = texto.replace(" ", "")
    if nombres and all(t[0] == "id" for t in _tokenizar(nombres, "hipotesis")):
        return [t[1] for t in _tokenizar(nombres, "hipotesis")]
    return [] if not nombres else None


def _leer_condiciones(texto: str, variables: List[str]) -> Tuple[List[Dict], List[str]]:
    """Devuelve (condiciones, nombres declarados como libres 'y ∈ ℝ')."""
    condiciones: List[Dict] = []
    declarados: List[str] = []
    piezas = [p.strip() for p in _dividir_nivel_cero(_normalizar(texto), ",;\n∧") if p.strip()]
    for pieza in piezas:
        nombres = _es_declaracion(pieza)
        if nombres is not None:
            declarados.extend(nombres)
            continue
        tokens = _tokenizar(pieza, "hipotesis")
        posiciones = [k for k, t in enumerate(tokens) if t[0] == "cmp"]
        if len(posiciones) != 1:
            raise ErrorDeSubespacio(
                f"Cada condición debe tener un solo signo (=, ≤, ≥, <, >, ≠): '{pieza}'.",
                "hipotesis")
        k = posiciones[0]
        izq = _Analizador(tokens[:k], "hipotesis", pieza).analizar()
        der = _Analizador(tokens[k + 1:], "hipotesis", pieza).analizar()
        for nombre in _variables_de(izq) + _variables_de(der):
            if nombre not in variables:
                raise ErrorDeSubespacio(
                    f"La variable '{nombre}' no aparece en el conjunto "
                    f"({', '.join(variables)}).", "hipotesis")
        condiciones.append({"izq": izq, "der": der, "op": tokens[k][1], "texto": pieza})
    if len(condiciones) > DIMENSION_MAXIMA:
        raise ErrorDeSubespacio(
            f"Se admiten a lo sumo {DIMENSION_MAXIMA} condiciones.", "hipotesis")
    return condiciones, declarados


def _preparar(cond: Dict, indice: Dict[str, int]) -> None:
    """Agrega los polinomios L, R y P = L − R a la condición."""
    cond["L"] = _a_polinomio(cond["izq"], indice, "hipotesis")
    cond["R"] = _a_polinomio(cond["der"], indice, "hipotesis")
    cond["P"] = _sumar(cond["L"], cond["R"], -1)


def _cumple_todas(condiciones: List[Dict], punto) -> bool:
    return all(
        _compara(_evaluar(c["L"], punto), c["op"], _evaluar(c["R"], punto))
        for c in condiciones
    )


# ---------------------------------------------------------------------------
# Construcción de una demostración
# ---------------------------------------------------------------------------
def _paso(etiqueta: Optional[str], lineas: List[str], nota: Optional[str] = None) -> Dict:
    return {"etiqueta": etiqueta, "lineas": lineas, "nota": nota}


def _demostracion(numero: str, titulo: str, pasos: List[Dict],
                  cumple: Optional[bool], conclusion: str, omitida: bool = False) -> Dict:
    return {"numero": numero, "titulo": titulo, "pasos": pasos, "cumple": cumple,
            "conclusion": conclusion, "omitida": omitida}


def _omitida(numero: str, titulo: str) -> Dict:
    return _demostracion(
        numero, titulo,
        [_paso(None, ["No hace falta: como falla (ii), ya se sabe que el conjunto "
                      "no es un subespacio."])],
        None, "No se evalúa.", omitida=True)


TITULO_SUMA = "Cerradura bajo la suma"
ALFA_CUALQUIERA = _m(r"\alpha \in \mathbb{R}") + " cualquiera."
TITULO_ESCALAR = "Cerradura bajo la multiplicación por un escalar"


def _condicion_i(nombre: str, n: int, parametrica: bool) -> Dict:
    texto = (
        f"Sí, por definición: cada componente es un número real, así que sus "
        f"elementos son {_que_elementos(n)}."
        if parametrica else
        f"Sí, por definición: sus elementos son {_que_elementos(n)}."
    )
    return _demostracion("i", _m(rf"{nombre} \subset {_tex_espacio(n)}"),
                         [_paso(None, [texto])], True,
                         "∴ " + _m(rf"{nombre} \subset {_tex_espacio(n)}"))


def _condicion_ii_implicita(nombre: str, n: int, variables: List[str],
                            condiciones: List[Dict]) -> Dict:
    titulo = _m(rf"{nombre} \neq \emptyset")
    cero = [Fraction(0)] * n
    lineas = [f"Basta ver que el vector nulo cumple la regla de {_m(nombre)}.",
              "Vector nulo: " + _m(f"{CERO} = {_tex_vector_numerico(cero)}")]
    if not condiciones:
        lineas.append(f"No hay restricciones: todo vector de {_m(_tex_espacio(n))} está en {_m(nombre)} ✓")
        return _demostracion("ii", titulo, [_paso("Vector nulo", lineas)], True,
                             "∴ " + _pertenece(CERO, nombre))
    entorno = _sustituir_numeros(variables, cero)
    cumple = True
    for cond in condiciones:
        izquierda, derecha = _evaluar(cond["L"], cero), _evaluar(cond["R"], cero)
        bien = _compara(izquierda, cond["op"], derecha)
        cumple = cumple and bien
        valores = f"{_tex_numero(izquierda)} {_TEX_COMPARADOR[cond['op']]} {_tex_numero(derecha)}"
        lineas += [
            f"Regla: {_m(_tex_condicion(cond))}",
            f"Sustituyo {_m(CERO)}: {_m(_tex_condicion(cond, entorno))}",
            f"{_m(valores)} " + ("✓" if bien else "Falso ✗"),
        ]
    if cumple:
        conclusion = "∴ " + _pertenece(CERO, nombre)
    else:
        conclusion = ("∴ " + _no_pertenece(CERO, nombre) + f". Por tanto, {_m(nombre)} no es un "
                      f"subespacio vectorial de {_m(_tex_espacio(n))}.")
    return _demostracion("ii", titulo, [_paso("Vector nulo", lineas)], cumple, conclusion)


def _despeje(cond: Dict, variables: List[str]) -> Optional[Tuple[int, Dict]]:
    """Si la regla es 'v = E' (o 'E = v') con v ausente de E: (índice de v, E)."""
    for lado, otro in (("izq", "R"), ("der", "L")):
        nodo = cond[lado]
        if nodo[0] == "var":
            i = variables.index(nodo[1])
            if all(mono[i] == 0 for mono in cond[otro]):
                return i, cond[otro]
    return None


def _terminos(coefs: List[Fraction], factores: List[str], compuestos: bool) -> List:
    return [(c, f, compuestos) for c, f in zip(coefs, factores)]


def _cerradura_lineal(nombre: str, n: int, variables: List[str], condiciones: List[Dict],
                      suma: bool) -> Dict:
    """(iii) o (iv) cuando todas las condiciones son lineales y homogéneas."""
    m = len(condiciones)
    c1 = [_tex_componente(v, 1) for v in variables]
    c2 = [_tex_componente(v, 2) for v in variables]
    env1 = {v: _sustitucion(c, "nombre") for v, c in zip(variables, c1)}
    env2 = {v: _sustitucion(c, "nombre") for v, c in zip(variables, c2)}

    # Paso 1 · Hipótesis
    hipotesis = []
    for j, cond in enumerate(condiciones):
        hipotesis.append(_m(rf"{U} = {_tex_vector(c1)} \in {nombre} \;\Longrightarrow\; "
                            rf"{_tex_condicion(cond, env1)} \qquad ({j + 1})"))
    if suma:
        for j, cond in enumerate(condiciones):
            hipotesis.append(_m(rf"{V} = {_tex_vector(c2)} \in {nombre} \;\Longrightarrow\; "
                                rf"{_tex_condicion(cond, env2)} \qquad ({m + j + 1})"))
    else:
        hipotesis.append(ALFA_CUALQUIERA)
    if not condiciones:
        hipotesis = [_m(rf"{U} = {_tex_vector(c1)} \in {nombre}")]
        hipotesis.append(_m(rf"{V} = {_tex_vector(c2)} \in {nombre}") if suma
                         else ALFA_CUALQUIERA)

    # Paso 2 · Operación
    if suma:
        resultado = [f"{a} + {b}" for a, b in zip(c1, c2)]
        operacion = [_m(rf"{U} + {V} = {_tex_vector(resultado)}")]
        nota = "Se suma coordenada a coordenada."
        objeto = rf"{U} + {V}"
    else:
        resultado = [rf"\alpha {a}" for a in c1]
        operacion = [_m(rf"\alpha{U} = \alpha{_tex_vector(c1)} = {_tex_vector(resultado)}")]
        nota = "α multiplica cada coordenada."
        objeto = rf"\alpha{U}"

    # Paso 3 · Verificación
    verificacion: List[str] = []
    if not condiciones:
        verificacion.append(
            f"Cada componente de {_m(objeto)} es un número real, y {_m(nombre)} no impone "
            f"ninguna regla ✓")
    for j, cond in enumerate(condiciones):
        por = f"(por ({j + 1}) y ({m + j + 1}))" if suma else f"(por ({j + 1}))"
        if m > 1:
            verificacion.append(f"Regla ({j + 1}): {_m(_tex_condicion(cond))}")
        _, coefs = _parte_lineal(cond["P"], n)
        if not any(coefs):
            verificacion.append(f"La regla {_m(_tex_condicion(cond))} se cumple siempre (es una identidad) ✓")
            continue
        despeje = _despeje(cond, variables) if cond["op"] == "=" else None
        if despeje is not None:
            i, expresion = despeje
            _, e = _parte_lineal(expresion, n)
            compuesta = sum(1 for c in e if c) > 1
            if suma:
                lado = f"{c1[i]} + {c2[i]}"
                objetivo = _tex_lineal(_terminos(e, [f"{a} + {b}" for a, b in zip(c1, c2)], True))
                eu = _tex_lineal(_terminos(e, c1, False))
                ev = _tex_lineal(_terminos(e, c2, False))
                medio = f"({eu}) + ({ev})" if compuesta else f"{eu} + {ev}"
            else:
                lado = rf"\alpha {c1[i]}"
                objetivo = _tex_lineal(_terminos(e, [rf"\alpha {a}" for a in c1], False))
                medio = rf"\alpha({_tex_lineal(_terminos(e, c1, False))})"
            verificacion += [
                f"¿Cumple la regla? Debo ver que {_m(f'{lado} = {objetivo}')}.",
                f"{_m(f'{lado} = {medio} = {objetivo}')} ✓  {por}",
            ]
        else:
            simbolo = _TEX_COMPARADOR[cond["op"]]
            forma = f"{_tex_lineal(_terminos(coefs, [_tex_variable(v) for v in variables], False))} {simbolo} 0"
            if not (cond["der"][0] == "num" and cond["der"][1] == 0 and cond["L"] == cond["P"]):
                verificacion.append(f"La regla equivale a {_m(forma)}.")
            pu = _tex_lineal(_terminos(coefs, c1, False))
            if suma:
                evaluada = _tex_lineal(_terminos(coefs, [f"{a} + {b}" for a, b in zip(c1, c2)], True), True)
                pv = _tex_lineal(_terminos(coefs, c2, False))
                verificacion += [
                    f"Evalúo la regla en {_m(objeto)}:",
                    _m(evaluada),
                    _m(f"= {_envolver(pu)} + {_envolver(pv)}"),
                    _m(f"{simbolo} 0 + 0 = 0") + f" ✓  {por}",
                ]
            else:
                evaluada = _tex_lineal(_terminos(coefs, [rf"\alpha {a}" for a in c1], False))
                verificacion += [
                    f"Evalúo la regla en {_m(objeto)}:",
                    _m(rf"{evaluada} = \alpha{_envolver(pu, True)}"),
                    _m(r"= \alpha \cdot 0 = 0") + f" ✓  {por}",
                ]

    cierre = "la suma" if suma else "el escalar"
    pasos = [
        _paso("Paso 1 · Hipótesis", hipotesis),
        _paso("Paso 2 · Operación", operacion, nota),
        _paso("Paso 3 · Verificación", verificacion),
        _paso("Paso 4 · Conclusión", [_m(rf"{objeto} \in {nombre}")]),
    ]
    return _demostracion("iii" if suma else "iv", TITULO_SUMA if suma else TITULO_ESCALAR,
                         pasos, True, f"∴ {_m(nombre)} es cerrado bajo {cierre}.")


# ---------------------------------------------------------------------------
# Contraejemplos (reglas no lineales o con desigualdades)
# ---------------------------------------------------------------------------
def _radio_busqueda(n: int) -> int:
    return {1: 6, 2: 6, 3: 6, 4: 4, 5: 2}.get(n, 1)


def _puntos_de(condiciones: List[Dict], n: int) -> List[Tuple[Fraction, ...]]:
    """Vectores no nulos de H con componentes enteras pequeñas, de los más simples a los menos."""
    radio = _radio_busqueda(n)
    valores = [0] + [s * k for k in range(1, radio + 1) for s in (1, -1)]
    puntos = [
        tuple(Fraction(v) for v in punto)
        for punto in product(valores, repeat=n)
        if any(punto) and _cumple_todas(condiciones, punto)
    ]
    puntos.sort(key=lambda p: (sum(abs(v) for v in p), sum(1 for v in p if v), [v < 0 for v in p]))
    return puntos[:120]


def _lineas_pertenencia(nombre_vector: str, punto, variables: List[str], condiciones: List[Dict],
                        nombre: str) -> List[str]:
    entorno = _sustituir_numeros(variables, punto)
    lineas = ["Tomo " + _m(f"{nombre_vector} = {_tex_vector_numerico(list(punto))}") + ":"]
    for cond in condiciones:
        izquierda, derecha = _evaluar(cond["L"], punto), _evaluar(cond["R"], punto)
        bien = _compara(izquierda, cond["op"], derecha)
        valores = f"{_tex_numero(izquierda)} {_TEX_COMPARADOR[cond['op']]} {_tex_numero(derecha)}"
        lineas.append(f"{_m(_tex_condicion(cond, entorno))} ⟹ {_m(valores)} " + ("✓" if bien else "Falso ✗"))
    if all(_compara(_evaluar(c["L"], punto), c["op"], _evaluar(c["R"], punto)) for c in condiciones):
        lineas.append("∴ " + _pertenece(nombre_vector, nombre))
    else:
        lineas.append("∴ " + _no_pertenece(nombre_vector, nombre))
    return lineas


def _contraejemplo(nombre: str, n: int, variables: List[str], condiciones: List[Dict],
                   suma: bool, puntos) -> Dict:
    numero = "iii" if suma else "iv"
    titulo = TITULO_SUMA if suma else TITULO_ESCALAR
    hallado = None
    if suma:
        # Primero con u ≠ v (más ilustrativo); si no aparece, también u = v.
        for distintos in (True, False):
            for p in puntos:
                for q in puntos:
                    if distintos and p == q:
                        continue
                    r = tuple(a + b for a, b in zip(p, q))
                    if not _cumple_todas(condiciones, r):
                        hallado = (p, q, r)
                        break
                if hallado:
                    break
            if hallado:
                break
    else:
        for alfa in _ESCALARES_PRUEBA:
            for p in puntos:
                r = tuple(alfa * a for a in p)
                if not _cumple_todas(condiciones, r):
                    hallado = (p, alfa, r)
                    break
            if hallado:
                break

    if hallado is None:
        motivo = ("no se hallaron vectores no nulos de H con componentes enteras pequeñas"
                  if not puntos else
                  "no se halló un contraejemplo con componentes enteras pequeñas")
        return _demostracion(
            numero, titulo,
            [_paso(None, [
                f"La regla no es lineal, así que no se puede seguir la receta simbólica y "
                f"se buscó un contraejemplo: {motivo}.",
                "Sin contraejemplo no se puede concluir que falle; tampoco queda demostrado "
                "que se cumpla.",
            ])],
            None, "No concluyente.")

    if suma:
        p, q, r = hallado
        hipotesis = (_lineas_pertenencia(U, p, variables, condiciones, nombre)
                     + _lineas_pertenencia(V, q, variables, condiciones, nombre))
        sumas = [f"{_tex_numero(a)} + {('(' + _tex_numero(b) + ')') if b < 0 else _tex_numero(b)}"
                 for a, b in zip(p, q)]
        operacion = [_m(rf"{U} + {V} = {_tex_vector(sumas)} = {_tex_vector_numerico(list(r))}")]
        objeto = rf"{U} + {V}"
        nota = "Se suma coordenada a coordenada."
    else:
        p, alfa, r = hallado
        hipotesis = _lineas_pertenencia(U, p, variables, condiciones, nombre)
        hipotesis.append("Tomo el escalar " + _m(rf"\alpha = {_tex_numero(alfa)}") + ".")
        operacion = [_m(rf"\alpha{U} = {_tex_numero(alfa)}{_tex_vector_numerico(list(p))} "
                        rf"= {_tex_vector_numerico(list(r))}")]
        objeto = rf"\alpha{U}"
        nota = "α multiplica cada coordenada."

    verificacion = [f"¿{_m(objeto)} cumple la regla?"]
    entorno = _sustituir_numeros(variables, r)
    for cond in condiciones:
        izquierda, derecha = _evaluar(cond["L"], r), _evaluar(cond["R"], r)
        bien = _compara(izquierda, cond["op"], derecha)
        valores = f"{_tex_numero(izquierda)} {_TEX_COMPARADOR[cond['op']]} {_tex_numero(derecha)}"
        verificacion.append(f"{_m(_tex_condicion(cond, entorno))} ⟹ {_m(valores)} "
                            + ("✓" if bien else "Falso ✗"))
    pasos = [
        _paso("Paso 1 · Hipótesis", hipotesis),
        _paso("Paso 2 · Operación", operacion, nota),
        _paso("Paso 3 · Verificación", verificacion),
        _paso("Paso 4 · Conclusión", [_m(rf"{objeto} \notin {nombre}")],
              "Basta un contraejemplo concreto para que la cerradura falle."),
    ]
    cierre = "la suma" if suma else "el escalar"
    return _demostracion(numero, titulo, pasos, False,
                         f"∴ {_m(nombre)} no es cerrado bajo {cierre}.")


# ---------------------------------------------------------------------------
# Generadores, base y solución trivial
# ---------------------------------------------------------------------------
def _pasos_detalle(pasos: List[str], historial: list) -> List[Dict]:
    return [
        {"notacion": notacion, "tipo": tipo, "columna_pivote": columna, "matriz": estado}
        for notacion, (tipo, columna, estado) in zip(pasos, historial)
    ]


def _analizar_generadores(generadores: List[List[Fraction]], n: int) -> Optional[Dict]:
    """c₁v₁ + … + cₖvₖ = 0: ¿solo la solución trivial? -> L.I. y base."""
    k = len(generadores)
    if k == 0:
        return None
    matriz = construir_matriz_homogenea(generadores, n)
    historial: list = []
    reducida, pasos, pivotes = escalonar(matriz, n, k, historial)
    trivial = len(pivotes) == k
    cs = [f"c_{{{j + 1}}}" for j in range(k)]

    combinacion = " + ".join(f"{c}{_tex_vector_numerico(g)}" for c, g in zip(cs, generadores))
    sistema = [_m(rf"{combinacion} = {_tex_vector_numerico([Fraction(0)] * n)}"),
               "Igualando componentes:"]
    for fila in range(n):
        sistema.append(_m(_tex_lineal(_terminos([g[fila] for g in generadores], cs, False)) + " = 0"))

    if trivial:
        solucion = [
            _m(" = ".join(cs) + " = 0"),
            f"Hay {_contar(len(pivotes), 'pivote')} para {_contar(k, 'incógnita')}: "
            f"no hay variables libres, así que "
            f"la única solución es la trivial ⟹ los generadores son linealmente independientes "
            f"(L.I.) y forman una base.",
        ]
    else:
        libre = next(j for j in range(k) if j not in pivotes)
        valores = [Fraction(0)] * k
        valores[libre] = Fraction(1)
        for fila, columna in enumerate(pivotes):
            valores[columna] = -reducida[fila][libre]
        ejemplo = ", ".join(f"{c} = {_tex_numero(v)}" for c, v in zip(cs, valores))
        solucion = [
            f"Hay {_contar(len(pivotes), 'pivote')} para {_contar(k, 'incógnita')}: "
            f"existen soluciones no "
            f"triviales, por ejemplo {_m(ejemplo)} ⟹ los generadores son linealmente "
            f"dependientes (L.D.).",
            "Se conservan solo los generadores de las columnas pivote; esos sí son L.I. y "
            "forman la base.",
        ]
    return {
        "matriz_inicial": matriz,
        "matriz_reducida": reducida,
        "pasos_detalle": _pasos_detalle(pasos, historial),
        "columnas_pivote": pivotes,
        "sistema": sistema,
        "solucion": solucion,
        "trivial": trivial,
        "base": [generadores[j] for j in pivotes],
    }


def _contar(cantidad: int, palabra: str) -> str:
    return f"{cantidad} {palabra}" + ("" if cantidad == 1 else "s")


def _tex_conjunto_generado(vectores: List[List[Fraction]], n: int) -> str:
    if not vectores:
        return rf"\operatorname{{gen}}\{{{_tex_vector_numerico([Fraction(0)] * n)}\}}"
    return (r"\operatorname{gen}\{" + ", ".join(_tex_vector_numerico(v) for v in vectores)
            + r"\}")


def _describir(dimension: int, n: int) -> str:
    if dimension == 0:
        return "el subespacio nulo, formado solo por el vector cero"
    if dimension == n:
        superindice = str(n).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
        return f"todo el espacio ℝ{superindice}" if n > 1 else "toda la recta real"
    if dimension == 1:
        return "una recta que pasa por el origen"
    if dimension == 2:
        return "un plano que pasa por el origen"
    if dimension == n - 1:
        return "un hiperplano que pasa por el origen"
    return f"un subespacio de dimensión {dimension} que pasa por el origen"


def _estructura(nombre: str, n: int, generadores: List[List[Fraction]], combinacion: List[str],
                forma_parametrica: str, extra: Dict) -> Dict:
    independencia = _analizar_generadores(generadores, n)
    base = independencia["base"] if independencia else []
    dimension = len(base)
    vs = [f"\\mathbf{{v}}_{{{j + 1}}}" for j in range(len(generadores))]
    datos = {
        "forma_parametrica": forma_parametrica,
        "combinacion_lineal": combinacion,
        "generadores": generadores,
        "generadores_tex": [f"{v} = {_tex_vector_numerico(g)}" for v, g in zip(vs, generadores)],
        "conjunto_generado": f"{nombre} = {_tex_conjunto_generado(generadores, n)}",
        "independencia": independencia,
        "base": base,
        "base_tex": (r"\{" + ", ".join(_tex_vector_numerico(b) for b in base) + r"\}")
        if base else r"\emptyset",
        "dimension": dimension,
        "descripcion": _describir(dimension, n),
    }
    datos.update(extra)
    return datos


def _estructura_implicita(nombre: str, n: int, variables: List[str],
                          condiciones: List[Dict]) -> Dict:
    filas = []
    for cond in condiciones:
        _, coefs = _parte_lineal(cond["P"], n)
        if any(coefs):
            filas.append(coefs)
    nombres = [_tex_variable(v) for v in variables]
    sistema = None
    if filas:
        matriz = [fila + [Fraction(0)] for fila in filas]
        historial: list = []
        reducida, pasos, pivotes = escalonar(matriz, len(filas), n, historial)
        sistema = {
            "matriz_inicial": matriz,
            "matriz_reducida": reducida,
            "pasos_detalle": _pasos_detalle(pasos, historial),
            "columnas_pivote": pivotes,
            "encabezados": nombres,
        }
    else:
        reducida, pivotes = [], []
    libres = [j for j in range(n) if j not in pivotes]

    despejes = []
    componentes = list(nombres)
    for fila, columna in enumerate(pivotes):
        expresion = _tex_lineal([(-reducida[fila][f], nombres[f], False) for f in libres])
        componentes[columna] = expresion
        despejes.append(_m(f"{nombres[columna]} = {expresion}"))

    generadores = []
    for f in libres:
        vector = [Fraction(0)] * n
        vector[f] = Fraction(1)
        for fila, columna in enumerate(pivotes):
            vector[columna] = -reducida[fila][f]
        generadores.append(vector)

    general = _tex_vector(nombres)
    if libres:
        suma = " + ".join(f"{nombres[f]}\\,{_tex_vector_numerico(g)}" for f, g in zip(libres, generadores))
        combinacion = [_m(f"{general} = {_tex_vector(componentes)} = {suma}")]
        forma = (rf"{nombre} = \{{{_tex_vector(componentes)} : "
                 rf"{', '.join(nombres[f] for f in libres)} \in \mathbb{{R}}\}}")
    else:
        combinacion = [_m(f"{general} = {_tex_vector_numerico([Fraction(0)] * n)}")]
        forma = rf"{nombre} = \{{{_tex_vector_numerico([Fraction(0)] * n)}\}}"

    return _estructura(nombre, n, generadores, combinacion, forma, {
        "sistema": sistema,
        "despejes": despejes,
        "variables_libres": [nombres[f] for f in libres],
        "nota": None,
    })


# ---------------------------------------------------------------------------
# Forma implícita: H = (x, y, z) con una regla
# ---------------------------------------------------------------------------
def _demostrar_implicita(nombre: str, variables: List[str], texto_hipotesis: str) -> Dict:
    n = len(variables)
    indice = {v: i for i, v in enumerate(variables)}
    condiciones, _ = _leer_condiciones(texto_hipotesis, variables)
    for cond in condiciones:
        _preparar(cond, indice)

    reglas = ", ".join(_tex_condicion(c) for c in condiciones)
    nombres = [_tex_variable(v) for v in variables]
    if condiciones:
        conjunto_tex = rf"{nombre} = \{{{_tex_vector(nombres)} \in {_tex_espacio(n)} : {reglas}\}}"
    else:
        conjunto_tex = rf"{nombre} = \{{{_tex_vector(nombres)} \in {_tex_espacio(n)}\}}"

    lineales = all(_grado(c["P"]) <= 1 for c in condiciones)
    solo_igualdades = all(c["op"] == "=" for c in condiciones)
    ordenadas = all(c["op"] in ("=", "<=", ">=", "<", ">") for c in condiciones)

    demostraciones = [_condicion_i(nombre, n, False),
                      _condicion_ii_implicita(nombre, n, variables, condiciones)]
    estructura = None
    if not demostraciones[1]["cumple"]:
        demostraciones += [_omitida("iii", TITULO_SUMA), _omitida("iv", TITULO_ESCALAR)]
    elif lineales and solo_igualdades:
        demostraciones += [_cerradura_lineal(nombre, n, variables, condiciones, True),
                           _cerradura_lineal(nombre, n, variables, condiciones, False)]
        estructura = _estructura_implicita(nombre, n, variables, condiciones)
    else:
        puntos = _puntos_de(condiciones, n)
        if lineales and ordenadas:
            demostraciones.append(_cerradura_lineal(nombre, n, variables, condiciones, True))
        else:
            demostraciones.append(_contraejemplo(nombre, n, variables, condiciones, True, puntos))
        demostraciones.append(_contraejemplo(nombre, n, variables, condiciones, False, puntos))

    return {
        "modo": "implicita",
        "nombre": nombre,
        "n": n,
        "variables": nombres,
        "conjunto_tex": conjunto_tex,
        "demostraciones": demostraciones,
        "estructura": estructura,
    }


# ---------------------------------------------------------------------------
# Forma paramétrica: H = (t - 2s, -s, t) con t, s ∈ ℝ
# ---------------------------------------------------------------------------
def _demostrar_parametrica(nombre: str, componentes: List[str], texto_hipotesis: str) -> Dict:
    arboles = [_leer_expresion(c, "conjunto") for c in componentes]
    n = len(arboles)
    parametros: List[str] = []
    for arbol in arboles:
        for p in _variables_de(arbol):
            if p not in parametros:
                parametros.append(p)
    _, declarados = _leer_condiciones(texto_hipotesis, parametros) if texto_hipotesis.strip() \
        else ([], [])
    if texto_hipotesis.strip() and _leer_condiciones(texto_hipotesis, parametros)[0]:
        raise ErrorDeSubespacio(
            "En la forma paramétrica la hipótesis solo declara los parámetros "
            "(p. ej. t, s ∈ ℝ).", "hipotesis")
    for p in declarados:
        if p not in parametros:
            raise ErrorDeSubespacio(f"El parámetro '{p}' no aparece en el conjunto.", "hipotesis")
    if len(parametros) > DIMENSION_MAXIMA:
        raise ErrorDeSubespacio(f"Se admiten a lo sumo {DIMENSION_MAXIMA} parámetros.", "conjunto")

    k = len(parametros)
    indice = {p: i for i, p in enumerate(parametros)}
    polinomios = [_a_polinomio(a, indice, "conjunto") for a in arboles]
    if any(_grado(p) > 1 for p in polinomios):
        raise ErrorDeSubespacio(
            "En la forma paramétrica cada componente debe ser lineal en los parámetros "
            "(p. ej. t - 2s).", "conjunto")
    constantes, columnas = [], [[Fraction(0)] * n for _ in range(k)]
    for i, p in enumerate(polinomios):
        c, coefs = _parte_lineal(p, k)
        constantes.append(c)
        for j in range(k):
            columnas[j][i] = coefs[j]

    nombres_p = [_tex_variable(p) for p in parametros]
    vector_tex = _tex_vector([_tex_arbol(a) for a in arboles])
    declaracion = rf" : {', '.join(nombres_p)} \in \mathbb{{R}}" if k else ""
    conjunto_tex = rf"{nombre} = \{{{vector_tex}{declaracion}\}}"

    # (ii) ¿existe una elección de parámetros que dé el vector nulo?
    titulo_ii = _m(rf"{nombre} \neq \emptyset")
    lineas = [f"Basta ver que el vector nulo {_m(CERO)} se obtiene para algún valor de los parámetros."]
    nota = None
    if all(c == 0 for c in constantes):
        cero_p = [Fraction(0)] * k
        punto, cumple = cero_p, True
        if k:
            lineas.append(f"Con {_m(' = '.join(nombres_p) + ' = 0')}:")
    else:
        matriz = [[columnas[j][i] for j in range(k)] + [-constantes[i]] for i in range(n)]
        reducida, _, pivotes = escalonar(matriz, n, k)
        cumple = not any(all(v == 0 for v in fila[:k]) and fila[k] != 0 for fila in reducida)
        ecuaciones = ", ".join(_tex_arbol(a) + " = 0" for a in arboles)
        lineas.append(f"Se busca resolver {_m(ecuaciones)}.")
        if cumple:
            punto = [Fraction(0)] * k
            for fila, columna in enumerate(pivotes):
                punto[columna] = reducida[fila][k]
            lineas.append("El sistema es consistente; con " + _m(", ".join(
                f"{p} = {_tex_numero(v)}" for p, v in zip(nombres_p, punto))) + ":")
            nota = (f"Como el vector nulo se obtiene con esos parámetros, {_m(nombre)} coincide "
                    f"con el conjunto generado por los vectores que multiplican a "
                    f"{_m(', '.join(nombres_p))}; las cerraduras se prueban sobre esa forma "
                    f"(sin término independiente).")
        else:
            punto = None
            lineas.append("El sistema es inconsistente (aparece una fila 0 = k con k ≠ 0): "
                          "ninguna elección de parámetros da el vector nulo. Falso ✗")
    if punto is not None:
        entorno = _sustituir_numeros(parametros, punto)
        sustituido = _tex_vector([_tex_arbol(a, entorno) for a in arboles])
        lineas.append(_m(f"{sustituido} = {_tex_vector_numerico([Fraction(0)] * n)}") + " ✓")
    conclusion = ("∴ " + _pertenece(CERO, nombre) if cumple else
                  "∴ " + _no_pertenece(CERO, nombre) + f". Por tanto, {_m(nombre)} no es un "
                  f"subespacio vectorial de {_m(_tex_espacio(n))}.")
    pasos_ii = [_paso("Vector nulo", lineas, nota)]
    demostraciones = [_condicion_i(nombre, n, True),
                      _demostracion("ii", titulo_ii, pasos_ii, cumple, conclusion)]
    if not cumple:
        demostraciones += [_omitida("iii", TITULO_SUMA), _omitida("iv", TITULO_ESCALAR)]
        estructura = None
    else:
        demostraciones += [_cerradura_parametrica(nombre, n, nombres_p, columnas, True),
                           _cerradura_parametrica(nombre, n, nombres_p, columnas, False)]
        homogenea = [_tex_lineal([(columnas[j][i], nombres_p[j], False) for j in range(k)])
                     for i in range(n)]
        suma = " + ".join(f"{p}\\,{_tex_vector_numerico(g)}" for p, g in zip(nombres_p, columnas))
        combinacion = [_m(f"{_tex_vector(homogenea)} = {suma if suma else _tex_vector_numerico([Fraction(0)] * n)}")]
        forma = (rf"{nombre} = \{{{_tex_vector(homogenea)}{declaracion}\}}")
        estructura = _estructura(nombre, n, [g for g in columnas], combinacion, forma, {
            "sistema": None,
            "despejes": [],
            "variables_libres": nombres_p,
            "nota": None if all(c == 0 for c in constantes) else
            "Se usa la forma sin término independiente (el vector nulo pertenece al conjunto).",
        })
        if any(all(v == 0 for v in g) for g in columnas):
            estructura["nota"] = ((estructura["nota"] or "") +
                                  " Un generador nulo nunca forma parte de una base.").strip()

    return {
        "modo": "parametrica",
        "nombre": nombre,
        "n": n,
        "variables": nombres_p,
        "conjunto_tex": conjunto_tex,
        "demostraciones": demostraciones,
        "estructura": estructura,
    }


def _cerradura_parametrica(nombre: str, n: int, parametros: List[str],
                           columnas: List[List[Fraction]], suma: bool) -> Dict:
    k = len(parametros)
    p1 = [_tex_componente(p, 1) for p in parametros]
    p2 = [_tex_componente(p, 2) for p in parametros]

    def componentes(factores, compuesto=False, siempre=False):
        return [_tex_lineal([(columnas[j][i], factores[j], compuesto) for j in range(k)], siempre)
                for i in range(n)]

    forma = _tex_vector(componentes([_tex_variable(p) for p in parametros]))
    u = componentes(p1)
    hipotesis = [_m(rf"{U} = {_tex_vector(u)}") + (" con " + _pertenece(", ".join(p1), r"\mathbb{R}") if k else "")]
    if suma:
        v = componentes(p2)
        hipotesis.append(_m(rf"{V} = {_tex_vector(v)}") + (" con " + _pertenece(", ".join(p2), r"\mathbb{R}") if k else ""))
        crudo = [f"{_envolver(a, a.startswith('-'))} + {_envolver(b, b.startswith('-'))}"
                 for a, b in zip(u, v)]
        agrupado = componentes([f"{a} + {b}" for a, b in zip(p1, p2)], True)
        operacion = [_m(rf"{U} + {V} = {_tex_vector(crudo)}")]
        nota = "Se suma coordenada a coordenada."
        objeto = rf"{U} + {V}"
        nuevos = [f"{_tex_variable(p)} = {a} + {b}" for p, a, b in zip(parametros, p1, p2)]
    else:
        hipotesis.append(ALFA_CUALQUIERA)
        crudo = [rf"\alpha{_envolver(a, a.startswith('-'))}" if _envolver(a, a.startswith('-')) != a
                 else rf"\alpha {a}" for a in u]
        agrupado = componentes([rf"\alpha {a}" for a in p1])
        operacion = [_m(rf"\alpha{U} = {_tex_vector(crudo)}")]
        nota = "α multiplica cada coordenada."
        objeto = rf"\alpha{U}"
        nuevos = [rf"{_tex_variable(p)} = \alpha {a}" for p, a in zip(parametros, p1)]

    verificacion = [
        "Agrupando cada parámetro: " + _m(f"{objeto} = {_tex_vector(agrupado)}"),
        f"Debo ver que tiene la forma {_m(forma)}.",
    ]
    if k:
        verificacion.append(f"Sí: es la forma de {_m(nombre)} con "
                            + _m(r",\; ".join(nuevos) + r" \in \mathbb{R}") + " ✓")
    else:
        verificacion.append(f"Sí: el resultado es el vector nulo ✓")
    cierre = "la suma" if suma else "el escalar"
    pasos = [
        _paso("Paso 1 · Hipótesis", hipotesis),
        _paso("Paso 2 · Operación", operacion, nota),
        _paso("Paso 3 · Verificación", verificacion),
        _paso("Paso 4 · Conclusión", [_m(rf"{objeto} \in {nombre}")]),
    ]
    return _demostracion("iii" if suma else "iv", TITULO_SUMA if suma else TITULO_ESCALAR,
                         pasos, True, f"∴ {_m(nombre)} es cerrado bajo {cierre}.")


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------
def demostrar_subespacio(texto_conjunto: str, texto_hipotesis: str = "") -> Dict:
    """Demuestra (i)–(iv) para H y, si es subespacio, obtiene generadores y base."""
    if len(texto_conjunto) > LONGITUD_MAXIMA:
        raise ErrorDeSubespacio("El conjunto es demasiado largo.", "conjunto")
    if len(texto_hipotesis) > LONGITUD_MAXIMA:
        raise ErrorDeSubespacio("La hipótesis es demasiado larga.", "hipotesis")

    nombre, componentes, extra = _leer_conjunto(texto_conjunto)
    hipotesis = ", ".join(t for t in (extra, _normalizar(texto_hipotesis)) if t.strip())

    arboles = [_leer_expresion(c, "conjunto") for c in componentes]
    nombres = [a[1] for a in arboles if a[0] == "var"]
    implicita = len(nombres) == len(arboles) and len(set(nombres)) == len(nombres)

    if implicita:
        resultado = _demostrar_implicita(nombre, nombres, hipotesis)
    else:
        resultado = _demostrar_parametrica(nombre, componentes, hipotesis)

    estados = [d["cumple"] for d in resultado["demostraciones"]]
    n = resultado["n"]
    espacio = _m(_tex_espacio(n))
    if all(e is True for e in estados):
        es_subespacio = True
        conclusion = (f"Se cumplen (i), (ii), (iii) y (iv) ⟹ {_m(nombre)} es un subespacio "
                      f"vectorial de {espacio}")
        if resultado["estructura"]:
            conclusion += f" ({resultado['estructura']['descripcion']})"
        conclusion += "."
    elif any(e is False for e in estados):
        es_subespacio = False
        fallan = ", ".join(f"({d['numero']})" for d in resultado["demostraciones"] if d["cumple"] is False)
        conclusion = (f"Falla {fallan} ⟹ {_m(nombre)} no es un subespacio vectorial de {espacio}.")
    else:
        es_subespacio = None
        conclusion = (f"No se pudo decidir: la regla no es lineal y no se halló contraejemplo, "
                      f"así que no se puede afirmar ni negar que {_m(nombre)} sea subespacio.")
    resultado["es_subespacio"] = es_subespacio
    resultado["conclusion"] = conclusion
    return resultado
