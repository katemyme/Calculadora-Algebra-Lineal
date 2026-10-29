"""Módulo de Transformaciones Lineales: linealidad, T(v), núcleo, nulidad, imagen y rango.

Sigue las Sesiones 16 y 17 (Transformaciones Lineales · Propiedades · Nulidad
y Rango). T se puede dar de dos formas:

  - Fórmula general:  T(x, y) = (x + y, x - y, 3y)
      1. Se prueba la linealidad con la receta de cuatro pasos:
         Hipótesis → Lado izquierdo → Lado derecho → Comparar, para
         (1) T(u + v) = T(u) + T(v)  y  (2) T(αu) = αT(u).
         Prueba rápida: si T(0) ≠ 0, T no es lineal. Si falla, basta un
         contraejemplo concreto.
  - Vectores dados:   T(1, 0) = (1, 2, 3),  T(0, 1) = (-4, 0, 5)
      Las imágenes de una base determinan T (teorema); T(v) se calcula en
      cuatro pasos: Descomponer → Linealidad (propiedad iii) → Sustituir →
      Resultado, con la comprobación A·v.

Si T es lineal se aplica la receta de cinco pasos:
  1. Matriz A de T: sus columnas son T(e₁), …, T(eₙ), y T(x) = Ax.
  2. Núcleo: se resuelve Ax = 0 por Gauss-Jordan.
  3. La solución como combinación lineal da la base de nu(T).
  4. Nulidad ν = número de variables libres; rango ρ = n − ν.
  5. Imagen: base = columnas de A con pivote; si ρ = dim W, im(T) = W.

CUMPLIMIENTO DE RESTRICCIONES ACADÉMICAS
----------------------------------------
- No se importa NumPy, SciPy, SymPy ni `math`.
- Toda la aritmética usa `fractions.Fraction` (exacta, sin tolerancias).
- Las expresiones se leen con el analizador del módulo de Subespacios.
- La reducción por filas reutiliza `escalonar()` del módulo de Vectores.
"""

import re
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

from modulos.modulo_subespacios import (
    DIMENSION_MAXIMA,
    LONGITUD_MAXIMA,
    ErrorDeSubespacio as ErrorDeLectura,
    _dividir_nivel_cero,
    _evaluar,
    _leer_expresion,
    _limpiar,
    _m,
    _multiplicar,
    _normalizar,
    _paso,
    _pasos_detalle,
    _sumar,
    _sustitucion,
    _sustituir_numeros,
    _tex_arbol,
    _tex_componente,
    _tex_espacio,
    _tex_lineal,
    _tex_numero,
    _tex_variable,
    _tex_vector,
    _variables_de,
)
from modulos.modulo_vectores import escalonar

U, V = r"\mathbf{u}", r"\mathbf{v}"
ALFA = r"\alpha"
REALES = r"\mathbb{R}"
FLECHA = r"\;\Longrightarrow\;"

# Escalares que se prueban para buscar un contraejemplo de la homogeneidad.
_ESCALARES_PRUEBA = [Fraction(2), Fraction(-1), Fraction(3), Fraction(1, 2)]


# ---------------------------------------------------------------------------
# Utilidades de LaTeX
# ---------------------------------------------------------------------------
def _tex_imagen(componentes: List[str]) -> str:
    """Un vector de W; si W = ℝ se escribe como número, sin paréntesis."""
    return componentes[0] if len(componentes) == 1 else _tex_vector(componentes)


def _tex_imagen_numerica(vector: List[Fraction]) -> str:
    return _tex_imagen([_tex_numero(v) for v in vector])


def _tex_dominio(vector: List[Fraction]) -> str:
    return _tex_vector([_tex_numero(v) for v in vector])


def _tex_gen(vectores: List[List[Fraction]], imagen: bool = False) -> str:
    escribir = _tex_imagen_numerica if imagen else _tex_dominio
    return r"\operatorname{gen}\{" + ", ".join(escribir(v) for v in vectores) + r"\}"


def _tex_e(j: int) -> str:
    return f"\\mathbf{{e}}_{{{j + 1}}}"


def _nombres_por_defecto(n: int) -> List[str]:
    """x, y, z, w para n ≤ 4 (como en las diapositivas); x1 … xn en otro caso."""
    return ["x", "y", "z", "w"][:n] if n <= 4 else [f"x{j + 1}" for j in range(n)]


def _tex_por(coef: Fraction, valor: Fraction) -> str:
    """'1·2' o '(−4)·4': un producto de la comprobación A·v."""
    a = _tex_numero(coef)
    b = _tex_numero(valor)
    a = f"({a})" if coef < 0 else a
    b = f"({b})" if valor < 0 else b
    return rf"{a} \cdot {b}"


def _tex_combinacion(coefs: List[Fraction], factores: List[str], punto: bool = False) -> str:
    """c₁·f₁ + c₂·f₂ + … omitiendo los coeficientes nulos ('·' opcional)."""
    partes: List[str] = []
    for c, f in zip(coefs, factores):
        if c == 0:
            continue
        magnitud = _tex_numero(abs(c))
        cuerpo = f if (magnitud == "1" and not punto) else (
            f"{magnitud} \\cdot {f}" if punto else f"{magnitud}{f}")
        if not partes:
            partes.append(("-" if c < 0 else "") + cuerpo)
        else:
            partes.append((" - " if c < 0 else " + ") + cuerpo)
    return "".join(partes) if partes else "0"


def _ordenar_monomios(p: Dict, prioridad: List[int]):
    return sorted(p.items(), key=lambda t: (-sum(t[0]), [-t[0][i] for i in prioridad]))


def _tex_polinomio(p: Dict, nombres: List[str], prioridad: Optional[List[int]] = None) -> str:
    """Polinomio exacto en LaTeX: 2x_1^{2} + \\alpha y_1 - 3."""
    prioridad = prioridad if prioridad is not None else list(range(len(nombres)))
    partes: List[str] = []
    for mono, coef in _ordenar_monomios(_limpiar(p), prioridad):
        variables = " ".join(
            nombres[i] + (f"^{{{e}}}" if e > 1 else "")
            for i in prioridad for e in [mono[i]] if e
        )
        magnitud = abs(coef)
        if not variables:
            cuerpo = _tex_numero(magnitud)
        elif magnitud == 1:
            cuerpo = variables
        else:
            cuerpo = f"{_tex_numero(magnitud)}{variables}"
        if not partes:
            partes.append(("-" if coef < 0 else "") + cuerpo)
        else:
            partes.append((" - " if coef < 0 else " + ") + cuerpo)
    return "".join(partes) if partes else "0"


# ---------------------------------------------------------------------------
# Polinomios: componer una componente de T con sustitutos polinómicos
# ---------------------------------------------------------------------------
def _componer(nodo, sustitutos: Dict[str, Dict], cero: tuple) -> Dict:
    """Polinomio de la componente al reemplazar cada variable por un polinomio."""
    tipo = nodo[0]
    if tipo == "num":
        return _limpiar({cero: nodo[1]})
    if tipo == "var":
        return dict(sustitutos[nodo[1]])
    if tipo == "neg":
        return {m: -c for m, c in _componer(nodo[1], sustitutos, cero).items()}
    if tipo in ("add", "sub"):
        return _sumar(_componer(nodo[1], sustitutos, cero),
                      _componer(nodo[2], sustitutos, cero), 1 if tipo == "add" else -1)
    if tipo == "mul":
        return _multiplicar(_componer(nodo[1], sustitutos, cero),
                            _componer(nodo[2], sustitutos, cero))
    if tipo == "div":
        divisor = _componer(nodo[2], sustitutos, cero)
        if any(sum(m) > 0 for m in divisor):
            raise ErrorDeLectura("Solo se puede dividir entre constantes (p. ej. x/2).", "formula")
        valor = divisor.get(cero, Fraction(0))
        if valor == 0:
            raise ErrorDeLectura("División entre cero en la fórmula.", "formula")
        return {m: c / valor for m, c in _componer(nodo[1], sustitutos, cero).items()}
    resultado = {cero: Fraction(1)}
    base = _componer(nodo[1], sustitutos, cero)
    for _ in range(nodo[2]):
        resultado = _multiplicar(resultado, base)
    return resultado


def _monomio(tamano: int, *indices: int) -> tuple:
    mono = [0] * tamano
    for i in indices:
        mono[i] += 1
    return tuple(mono)


# ---------------------------------------------------------------------------
# Lectura de datos
# ---------------------------------------------------------------------------
def _leer_vector_numerico(texto: str, campo: str, fila: Optional[int] = None,
                          que: str = "El vector") -> List[Fraction]:
    limpio = _normalizar(texto or "").strip()
    if not limpio:
        raise _error(f"{que} está vacío.", campo, fila)
    if limpio.startswith("(") and limpio.endswith(")"):
        limpio = limpio[1:-1]
    piezas = [p.strip() for p in _dividir_nivel_cero(limpio, ",;")]
    if len(piezas) > DIMENSION_MAXIMA:
        raise _error(f"{que} tiene más de {DIMENSION_MAXIMA} componentes.", campo, fila)
    valores = []
    for pieza in piezas:
        if not pieza:
            raise _error(f"{que} tiene una componente vacía.", campo, fila)
        try:
            arbol = _leer_expresion(pieza, campo)
        except ErrorDeLectura as error:
            raise _error(error.mensaje, campo, fila)
        if _variables_de(arbol):
            raise _error(f"{que} solo admite números: '{pieza}'.", campo, fila)
        p = _componer(arbol, {}, ())
        valores.append(p.get((), Fraction(0)))
    return valores


def _error(mensaje: str, campo: str, fila: Optional[int] = None) -> ErrorDeLectura:
    error = ErrorDeLectura(mensaje, campo)
    error.fila = fila
    return error


_PATRON_IZQUIERDA = re.compile(r"([^\W\d_])\s*\(([^()]*)\)\s*$")


def _leer_formula(texto: str) -> Tuple[str, List[str], List]:
    """'T(x, y) = (x + y, 3y)' -> ('T', ['x', 'y'], [árbol₁, árbol₂])."""
    limpio = _normalizar(texto or "").strip()
    if not limpio:
        raise ErrorDeLectura("Escriba la fórmula, por ejemplo T(x, y) = (x + y, x - y, 3y).",
                             "formula")
    partes = _dividir_nivel_cero(limpio, "=")
    if len(partes) != 2:
        raise ErrorDeLectura("La fórmula debe tener la forma T(x, y) = (…), con un solo '='.",
                             "formula")
    izquierda, derecha = partes[0].strip(), partes[1].strip()
    coincidencia = _PATRON_IZQUIERDA.search(izquierda)
    if not coincidencia:
        raise ErrorDeLectura("A la izquierda del '=' escriba T(x, y, …) con las variables.",
                             "formula")
    nombre = coincidencia.group(1)
    variables = []
    for pieza in coincidencia.group(2).split(","):
        arbol = _leer_expresion(pieza.strip(), "formula")
        if arbol[0] != "var":
            raise ErrorDeLectura(f"'{pieza.strip()}' no es una variable de T(…).", "formula")
        if arbol[1] in variables:
            raise ErrorDeLectura(f"La variable '{arbol[1]}' está repetida.", "formula")
        variables.append(arbol[1])
    if len(variables) > DIMENSION_MAXIMA:
        raise ErrorDeLectura(f"Se admiten a lo sumo {DIMENSION_MAXIMA} variables.", "formula")

    cuerpo = derecha
    if cuerpo.startswith("(") and cuerpo.endswith(")"):
        interior = cuerpo[1:-1]
        nivel, cierra_al_final = 0, True
        for k, ch in enumerate(interior):
            nivel += ch == "("
            nivel -= ch == ")"
            if nivel < 0:
                cierra_al_final = False
                break
        if cierra_al_final:
            cuerpo = interior
    componentes = [c.strip() for c in _dividir_nivel_cero(cuerpo, ",")]
    if any(not c for c in componentes):
        raise ErrorDeLectura("Hay una componente vacía en T(…).", "formula")
    if len(componentes) > DIMENSION_MAXIMA:
        raise ErrorDeLectura(f"T puede tener a lo sumo {DIMENSION_MAXIMA} componentes.",
                             "formula")
    arboles = [_leer_expresion(c, "formula") for c in componentes]
    for arbol in arboles:
        for v in _variables_de(arbol):
            if v not in variables:
                raise ErrorDeLectura(
                    f"La variable '{v}' no aparece en {nombre}({', '.join(variables)}).", "formula")
    return nombre, variables, arboles


# ---------------------------------------------------------------------------
# Secciones
# ---------------------------------------------------------------------------
def _seccion(titulo: str, pasos: List[Dict], conclusion: str,
             cumple: Optional[bool] = None) -> Dict:
    return {"titulo": titulo, "pasos": pasos, "conclusion": conclusion, "cumple": cumple}


def _paso_con(etiqueta: str, lineas: List[str], nota: Optional[str] = None,
              reduccion: Optional[Dict] = None) -> Dict:
    paso = _paso(etiqueta, lineas, nota)
    paso["reduccion"] = reduccion
    return paso


def _reduccion(matriz: List[List[Fraction]], filas: int, columnas: int,
               encabezados: List[str]) -> Tuple[Dict, List[List[Fraction]], List[int]]:
    historial: list = []
    reducida, pasos, pivotes = escalonar(matriz, filas, columnas, historial)
    datos = {
        "matriz_inicial": matriz,
        "matriz_reducida": reducida,
        "pasos_detalle": _pasos_detalle(pasos, historial),
        "columnas_pivote": pivotes,
        "encabezados": encabezados,
    }
    return datos, reducida, pivotes


# ---------------------------------------------------------------------------
# Linealidad (solo fórmula general)
# ---------------------------------------------------------------------------
def _candidatos(n: int) -> List[List[Fraction]]:
    canonicos = [[Fraction(1 if i == j else 0) for i in range(n)] for j in range(n)]
    unos = [Fraction(1)] * n
    otros = [[Fraction(2 if i == j else 0) for i in range(n)] for j in range(n)]
    negativos = [[Fraction(-1 if i == j else 0) for i in range(n)] for j in range(n)]
    lista = canonicos + [unos] + otros + negativos
    vistos, unicos = set(), []
    for v in lista:
        if tuple(v) not in vistos:
            vistos.add(tuple(v))
            unicos.append(v)
    return unicos


def _linealidad(nombre: str, variables: List[str], arboles: List) -> Dict:
    n, m = len(variables), len(arboles)
    nombres = [_tex_variable(v) for v in variables]
    c1 = [_tex_componente(v, 1) for v in variables]
    c2 = [_tex_componente(v, 2) for v in variables]
    indice = {v: i for i, v in enumerate(variables)}
    cero_n = tuple([0] * n)
    base_n = {v: {_monomio(n, i): Fraction(1)} for v, i in indice.items()}
    polinomios = [_componer(a, base_n, cero_n) for a in arboles]

    def aplicar(entorno):
        return _tex_imagen([_tex_arbol(a, entorno) for a in arboles])

    def valores_en(punto):
        return [_evaluar(p, punto) for p in polinomios]

    T = nombre
    env1 = {v: _sustitucion(c, "nombre") for v, c in zip(variables, c1)}
    env2 = {v: _sustitucion(c, "nombre") for v, c in zip(variables, c2)}

    # Prueba rápida · T(0)
    cero = [Fraction(0)] * n
    t_cero = valores_en(cero)
    nulo_w = _tex_imagen_numerica([Fraction(0)] * m)
    sustituido_cero = aplicar(_sustituir_numeros(variables, cero))
    valor_cero = _tex_imagen_numerica(t_cero)
    lineas_cero = [_m(f"{T}{_tex_dominio(cero)} = " + (
        valor_cero if sustituido_cero == valor_cero else f"{sustituido_cero} = {valor_cero}"))]
    cero_ok = all(v == 0 for v in t_cero)

    # (1) Aditividad: espacio de 2n variables (las de u y luego las de v).
    t2 = 2 * n
    cero_2n = tuple([0] * t2)
    suma_sust = {v: {_monomio(t2, i): Fraction(1), _monomio(t2, n + i): Fraction(1)}
                 for v, i in indice.items()}
    u_sust = {v: {_monomio(t2, i): Fraction(1)} for v, i in indice.items()}
    v_sust = {v: {_monomio(t2, n + i): Fraction(1)} for v, i in indice.items()}
    izquierda = [_componer(a, suma_sust, cero_2n) for a in arboles]
    derecha = [_sumar(_componer(a, u_sust, cero_2n), _componer(a, v_sust, cero_2n))
               for a in arboles]
    nombres_2n = c1 + c2
    intercalado = [k for i in range(n) for k in (i, n + i)]
    sumas = [f"{a} + {b}" for a, b in zip(c1, c2)]
    env_suma = {v: _sustitucion(s, "compuesto") for v, s in zip(variables, sumas)}

    lado_izq = [_m(rf"{T}({U} + {V}) = {T}{_tex_vector(sumas)}")]
    sustituido = aplicar(env_suma)
    expandido_izq = _tex_imagen([_tex_polinomio(p, nombres_2n, intercalado) for p in izquierda])
    if sustituido != expandido_izq:
        lado_izq.append(_m(f"= {sustituido}"))
    lado_izq.append(_m(f"= {expandido_izq}"))
    expandido_der = _tex_imagen([_tex_polinomio(p, nombres_2n) for p in derecha])
    lado_der = [_m(rf"{T}({U}) + {T}({V}) = {aplicar(env1)} + {aplicar(env2)}"),
                _m(f"= {expandido_der}")]
    aditiva = izquierda == derecha
    comparar_1 = _comparar(aditiva, rf"{T}({U} + {V}) = {T}({U}) + {T}({V})",
                           expandido_izq, expandido_der)
    if not aditiva:
        comparar_1.append(_contraejemplo_suma(T, n, polinomios))
    aditividad = _seccion(
        "(1) Aditividad: T(u + v) = T(u) + T(v)",
        [
            _paso_con("Hipótesis", [_m(rf"{U} = {_tex_vector(c1)},\quad {V} = {_tex_vector(c2)} "
                                       rf"\in {_espacio(n)}")]),
            _paso_con("Aditividad · lado izquierdo", lado_izq,
                      "Primero se suman los vectores y luego se aplica T."),
            _paso_con("Aditividad · lado derecho", lado_der,
                      "Primero se aplica T a cada vector y luego se suman."),
            _paso_con("Comparar", comparar_1),
        ],
        "Se cumple (1)." if aditiva else "No se cumple (1).", aditiva)

    # (2) Homogeneidad: espacio de n + 1 variables (α y las de u).
    t1 = n + 1
    cero_1 = tuple([0] * t1)
    alfa_u = {v: {_monomio(t1, 0, 1 + i): Fraction(1)} for v, i in indice.items()}
    solo_u = {v: {_monomio(t1, 1 + i): Fraction(1)} for v, i in indice.items()}
    alfa = {_monomio(t1, 0): Fraction(1)}
    izq_h = [_componer(a, alfa_u, cero_1) for a in arboles]
    der_h = [_multiplicar(alfa, _componer(a, solo_u, cero_1)) for a in arboles]
    nombres_h = [ALFA] + c1
    escalados = [f"{ALFA} {c}" for c in c1]
    env_alfa = {v: _sustitucion(s, "compuesto") for v, s in zip(variables, escalados)}
    expandido_izq_h = _tex_imagen([_tex_polinomio(p, nombres_h) for p in izq_h])
    lado_izq_h = [_m(rf"{T}({ALFA}{U}) = {T}{_tex_vector(escalados)}")]
    sustituido_h = aplicar(env_alfa)
    if sustituido_h != expandido_izq_h:
        lado_izq_h.append(_m(f"= {sustituido_h}"))
    lado_izq_h.append(_m(f"= {expandido_izq_h}"))
    t_u = aplicar(env1)
    expandido_der_h = _tex_imagen([_tex_polinomio(p, nombres_h) for p in der_h])
    lado_der_h = [_m(rf"{ALFA} {T}({U}) = {ALFA}" + (t_u if m > 1 else f"({t_u})")),
                  _m(f"= {expandido_der_h}")]
    homogenea = izq_h == der_h
    comparar_2 = _comparar(homogenea, rf"{T}({ALFA}{U}) = {ALFA} {T}({U})",
                           expandido_izq_h, expandido_der_h)
    if not homogenea:
        comparar_2.append(_contraejemplo_escalar(T, n, polinomios))
    homogeneidad = _seccion(
        "(2) Homogeneidad: T(αu) = αT(u)",
        [
            _paso_con("Hipótesis", [_m(rf"{U} = {_tex_vector(c1)} \in {_espacio(n)}") +
                                    " y " + _m(rf"{ALFA} \in {REALES}") + " cualquiera."]),
            _paso_con("Homogeneidad · lado izquierdo", lado_izq_h,
                      "Primero se multiplica por α y luego se aplica T."),
            _paso_con("Homogeneidad · lado derecho", lado_der_h,
                      "Primero se aplica T y luego se multiplica por α."),
            _paso_con("Comparar", comparar_2),
        ],
        "Se cumple (2)." if homogenea else "No se cumple (2).", homogenea)

    if cero_ok:
        lineas_cero.append("✓ " + (
            "Como debe ser: toda transformación lineal cumple T(0) = 0." if aditiva and homogenea
            else "Pero no basta: T(0) = 0 no garantiza que T sea lineal."))
    else:
        lineas_cero.append(_m(rf"{valor_cero} \neq {nulo_w}") + " ✗ Toda transformación lineal cumple "
                           "T(0) = 0: aquí falla, así que T no es lineal.")
    prueba_cero = _seccion("Prueba rápida · T(0)", [_paso_con("Vector nulo", lineas_cero)],
                           "T(0) = 0 ✓" if cero_ok else "T(0) ≠ 0 ✗", cero_ok)

    es_lineal = aditiva and homogenea
    if es_lineal:
        conclusion = "Se cumplen (1) y (2): T es una transformación lineal."
    else:
        fallan = " ni ".join(x for x, ok in (("(1)", aditiva), ("(2)", homogenea)) if not ok)
        conclusion = f"No se cumple {fallan}: T no es una transformación lineal."
    return {
        "prueba_cero": prueba_cero,
        "aditividad": aditividad,
        "homogeneidad": homogeneidad,
        "es_lineal": es_lineal,
        "conclusion": conclusion,
        "polinomios": polinomios,
    }


def _comparar(iguales: bool, identidad: str, izquierdo: str, derecho: str) -> List[str]:
    if iguales:
        return [f"Coinciden ✓  {_m(identidad)}"]
    return [_m(rf"{izquierdo} \neq {derecho}") + " en general.",
            "Basta un caso concreto que falle (contraejemplo):"]


def _contraejemplo_suma(T: str, n: int, polinomios: List[Dict]) -> str:
    candidatos = _candidatos(n)
    for u in candidatos:
        for v in candidatos:
            if u != v and candidatos.index(v) < candidatos.index(u):
                continue
            s = [a + b for a, b in zip(u, v)]
            izq = [_evaluar(p, s) for p in polinomios]
            der = [_evaluar(p, u) + _evaluar(p, v) for p in polinomios]
            if izq != der:
                tu = [_evaluar(p, u) for p in polinomios]
                tv = [_evaluar(p, v) for p in polinomios]
                inicio = (rf"{U} = {V} = {_tex_dominio(u)}" if u == v else
                          rf"{U} = {_tex_dominio(u)},\; {V} = {_tex_dominio(v)}")
                return ("Ej.: " + _m(
                    rf"{inicio} \Rightarrow {T}({U} + {V}) = {T}{_tex_dominio(s)} = "
                    rf"{_tex_imagen_numerica(izq)}") + ", pero " + _m(
                    rf"{T}({U}) + {T}({V}) = {_tex_imagen_numerica(tu)} + "
                    rf"{_tex_imagen_numerica(tv)} = {_tex_imagen_numerica(der)}"))
    return "No se halló un contraejemplo con vectores pequeños, pero las expresiones no coinciden."


def _contraejemplo_escalar(T: str, n: int, polinomios: List[Dict]) -> str:
    candidatos = _candidatos(n)
    unos = candidatos.pop(n)            # primero (1, 1, …), como en las diapositivas
    candidatos.insert(0, unos)
    for alfa in _ESCALARES_PRUEBA:
        for u in candidatos:
            au = [alfa * a for a in u]
            izq = [_evaluar(p, au) for p in polinomios]
            tu = [_evaluar(p, u) for p in polinomios]
            der = [alfa * t for t in tu]
            if izq != der:
                a = _tex_numero(alfa)
                return ("Ej.: " + _m(
                    rf"{U} = {_tex_dominio(u)},\; {ALFA} = {a} \Rightarrow "
                    rf"{T}({a}{U}) = {T}{_tex_dominio(au)} = {_tex_imagen_numerica(izq)}")
                    + ", pero " + _m(
                    rf"{a}{T}({U}) = {a}" + (_tex_imagen_numerica(tu) if len(tu) > 1 else
                                             f"({_tex_imagen_numerica(tu)})")
                    + f" = {_tex_imagen_numerica(der)}"))
    return "No se halló un contraejemplo con vectores pequeños, pero las expresiones no coinciden."


# ---------------------------------------------------------------------------
# Matriz de T, evaluación y receta de cinco pasos
# ---------------------------------------------------------------------------
def _matriz_desde_polinomios(polinomios: List[Dict], n: int) -> List[List[Fraction]]:
    return [[p.get(_monomio(n, i), Fraction(0)) for i in range(n)] for p in polinomios]


def _columna(A: List[List[Fraction]], j: int) -> List[Fraction]:
    return [fila[j] for fila in A]


def _formula_tex(T: str, nombres: List[str], A: List[List[Fraction]]) -> str:
    componentes = [_tex_lineal([(a, x, False) for a, x in zip(fila, nombres)]) for fila in A]
    return f"{T}{_tex_vector(nombres)} = {_tex_imagen(componentes)}"


def _tex_matriz(A: List[List[Fraction]]) -> str:
    filas = r" \\ ".join(" & ".join(_tex_numero(v) for v in fila) for fila in A)
    return r"\begin{bmatrix} " + filas + r" \end{bmatrix}"


def _comprobacion_matriz(A: List[List[Fraction]], v: List[Fraction]) -> str:
    resultado = [sum(a * x for a, x in zip(fila, v)) for fila in A]
    productos = [" + ".join(_tex_por(a, x) for a, x in zip(fila, v)) for fila in A]
    return ("Comprobación con la matriz: " + _m(
        rf"A{_tex_dominio(v)} = {_tex_imagen(productos)} = {_tex_imagen_numerica(resultado)}")
        + " ✓")


def _seccion_matriz(T: str, nombres: List[str], A: List[List[Fraction]],
                    lineas_extra: Optional[List[str]] = None, columnas: bool = True) -> Dict:
    n = len(nombres)
    lineas = list(lineas_extra or [])
    if columnas:
        lineas += [_m(f"{T}({_tex_e(j)}) = {_tex_imagen_numerica(_columna(A, j))}")
                   for j in range(n)]
    lineas.append(_m(f"A = {_tex_matriz(A)}"))
    lineas.append("Entonces " + _m(rf"{T}(\mathbf{{x}}) = A\mathbf{{x}}") + ", es decir, "
                  + _m(_formula_tex(T, nombres, A)) + ".")
    return _seccion("Paso 1 · Matriz A de T", [_paso_con(
        "Columnas T(eⱼ)", lineas, "Las columnas de A son las imágenes de la base canónica.")],
        f"A es de orden {len(A)} × {n}.")


def _analisis(T: str, nombres: List[str], A: List[List[Fraction]]) -> Dict:
    """Pasos 2 a 5: núcleo, nulidad, imagen y rango a partir de A."""
    m, n = len(A), len(nombres)
    Rn, Rm = _espacio(n), _espacio(m)
    componentes = [_tex_lineal([(a, x, False) for a, x in zip(fila, nombres)]) for fila in A]
    nulo_w = _tex_imagen_numerica([Fraction(0)] * m)
    general = _tex_vector(nombres)

    # Núcleo
    planteamiento = [
        _m(rf"\operatorname{{nu}}({T}) = \{{\mathbf{{v}} \in {Rn} : {T}(\mathbf{{v}}) = \mathbf{{0}}\}}"),
        _m(f"{T}{general} = {nulo_w} {FLECHA} {_tex_imagen(componentes)} = {nulo_w}"),
    ]
    ecuaciones = [c + " = 0" for c in componentes if c != "0"]
    if ecuaciones:
        planteamiento.append("Sistema homogéneo: " + _m(r",\quad ".join(ecuaciones)) + ".")
    matriz = [fila + [Fraction(0)] for fila in A]
    reduccion, reducida, pivotes = _reduccion(matriz, m, n, nombres)
    libres = [j for j in range(n) if j not in pivotes]
    gauss = ["Matriz " + _m(r"[A \mid \mathbf{0}]") + " (columnas " + _m(", ".join(nombres)) + "):"]
    nota_gauss = ("Ya está en forma escalonada reducida: no hay que operar."
                  if not reduccion["pasos_detalle"] else
                  f"Se aplicaron {len(reduccion['pasos_detalle'])} operaciones elementales.")
    texto_piv = ("Pivote en " if len(pivotes) == 1 else "Pivotes en ") + (
        _m(", ".join(nombres[j] for j in pivotes)) if pivotes else "ninguna columna")
    if libres:
        texto_piv += "; " + _m(", ".join(nombres[j] for j in libres)) + (
            " es variable libre." if len(libres) == 1 else " son variables libres.")
    else:
        texto_piv += "; no hay variables libres."
    gauss.append(texto_piv)

    vector_general = list(nombres)
    despejes = []
    for fila, columna in enumerate(pivotes):
        expresion = _tex_lineal([(-reducida[fila][f], nombres[f], False) for f in libres])
        vector_general[columna] = expresion
        despejes.append(f"{nombres[columna]} = {expresion}")
    generadores = []
    for f in libres:
        vector = [Fraction(0)] * n
        vector[f] = Fraction(1)
        for fila, columna in enumerate(pivotes):
            vector[columna] = -reducida[fila][f]
        generadores.append(vector)
    resolver = []
    if despejes or libres:
        resolver.append(_m(r",\quad ".join(despejes + [
            f"{nombres[f]}" + r"\text{ libre}" for f in libres])))
    if libres:
        combinacion = " + ".join(f"{nombres[f]} \\cdot {_tex_dominio(g)}"
                                 for f, g in zip(libres, generadores))
        resolver.append(_m(f"{general} = {_tex_vector(vector_general)} = {combinacion}"))
        nu_tex = (rf"\operatorname{{nu}}({T}) = \{{{_tex_vector(vector_general)} : "
                  rf"{', '.join(nombres[f] for f in libres)} \in {REALES}\}} = {_tex_gen(generadores)}")
    else:
        resolver.append(_m(f"{general} = {_tex_dominio([Fraction(0)] * n)}") +
                        ": solo la solución trivial.")
        nu_tex = rf"\operatorname{{nu}}({T}) = \{{{_tex_dominio([Fraction(0)] * n)}\}}"
    nucleo = _seccion("Paso 2 · Núcleo nu(T)", [
        _paso_con("Planteamiento", planteamiento),
        _paso_con("Gauss–Jordan", gauss, nota_gauss, reduccion),
        _paso_con("Resolver", resolver),
    ], "Respuesta: " + _m(nu_tex))

    # Nulidad y teorema de la dimensión
    nulidad = len(libres)
    rango = n - nulidad
    nulidad_s = _seccion("Paso 3 · Nulidad ν(T)", [
        _paso_con("Nulidad", [
            _m(rf"\nu({T}) = \dim \operatorname{{nu}}({T})"),
            ("No hay variables libres: el núcleo solo contiene al vector cero." if nulidad == 0
             else "Una variable libre, un vector base:" if nulidad == 1
             else f"{nulidad} variables libres, {nulidad} vectores base independientes:"),
            _m(rf"\nu({T}) = {nulidad}"),
        ]),
        _paso_con("Teorema de la dimensión", [
            _m(rf"\nu({T}) + \rho({T}) = \dim {Rn} = {n}"),
            _m(rf"{nulidad} + \rho({T}) = {n} \Rightarrow \rho({T}) = {rango}"),
        ]),
    ], _m(rf"\nu({T}) = {nulidad}"))

    # Imagen
    base_imagen = [_columna(A, j) for j in pivotes]
    directo = _tex_combinacion([Fraction(1)] * n,
                               [f"{x} \\cdot {_tex_imagen_numerica(_columna(A, j))}"
                                for j, x in enumerate(nombres)])
    imagen_lineas = []
    if rango:
        imagen_lineas.append(("Columna de A con pivote: " if rango == 1 else
                              "Columnas de A con pivote: ") +
                             _m(", ".join(_tex_imagen_numerica(b) for b in base_imagen)) + ".")
        im_tex = rf"\operatorname{{im}}({T}) = {_tex_gen(base_imagen, True)}"
        if rango == m:
            imagen_lineas.append(
                _m(rf"\operatorname{{im}}({T}) \subset {Rm}") + " y " +
                _m(rf"\dim \operatorname{{im}}({T}) = {rango} = \dim {Rm}") + " ⟹ " +
                _m(rf"\operatorname{{im}}({T}) = {Rm}"))
            im_tex += rf" = {Rm}"
        imagen_lineas.append(_m(im_tex))
    else:
        im_tex = rf"\operatorname{{im}}({T}) = \{{{nulo_w}\}}"
        imagen_lineas.append("Ninguna columna tiene pivote (A es la matriz cero): " + _m(im_tex))
    imagen_lineas.append("Directo: " + _m(f"{T}{general} = {directo}") + ".")
    imagen = _seccion("Paso 4 · Imagen im(T)", [_paso_con("Imagen", imagen_lineas,
        "La imagen la generan las columnas de A; las que tienen pivote forman una base.")],
        "Respuesta: " + _m(im_tex))

    rango_s = _seccion("Paso 5 · Rango ρ(T)", [_paso_con("Rango", [
        _m(rf"\rho({T}) = \dim \operatorname{{im}}({T}) = {rango}"),
        ("Base de la imagen: " + _m(r"\{" + ", ".join(_tex_imagen_numerica(b) for b in base_imagen)
                                    + r"\}") + " (columnas con pivote).") if rango else
        "La base de la imagen es vacía.",
        f"Coincide con el teorema de la dimensión: {nulidad} + {rango} = {n} ✓",
    ])], _m(rf"\rho({T}) = {rango}"))

    respuesta = (_m(nu_tex.split(" = ")[0] + " = " + nu_tex.split(" = ")[-1]) + ",  " +
                 _m(rf"\nu({T}) = {nulidad}") + ",  " +
                 _m(im_tex.split(" = ")[0] + " = " + im_tex.split(" = ")[-1]) + ",  " +
                 _m(rf"\rho({T}) = {rango}"))
    return {
        "nucleo": nucleo,
        "nulidad": nulidad_s,
        "imagen": imagen,
        "rango": rango_s,
        "respuesta": respuesta,
        "valor_nulidad": nulidad,
        "valor_rango": rango,
        "base_nucleo": generadores,
        "base_imagen": base_imagen,
        "inyectiva": nulidad == 0,
        "sobreyectiva": rango == m,
    }


def _espacio(k: int) -> str:
    """ℝ (sin exponente) cuando k = 1, como en las diapositivas; ℝᵏ en otro caso."""
    return REALES if k == 1 else _tex_espacio(k)


def _definicion(T: str, n: int, m: int) -> str:
    return rf"{T}: {_espacio(n)} \to {_espacio(m)}"


# ---------------------------------------------------------------------------
# Punto de entrada · fórmula general
# ---------------------------------------------------------------------------
def analizar_formula(texto_formula: str, texto_vector: str = "") -> Dict:
    """Linealidad de T(x, …) = (…), T(v) opcional y, si es lineal, núcleo … rango."""
    if len(texto_formula or "") > LONGITUD_MAXIMA:
        raise ErrorDeLectura("La fórmula es demasiado larga.", "formula")
    T, variables, arboles = _leer_formula(texto_formula)
    n, m = len(variables), len(arboles)
    nombres = [_tex_variable(v) for v in variables]
    linealidad = _linealidad(T, variables, arboles)
    polinomios = linealidad.pop("polinomios")

    vector = None
    if (texto_vector or "").strip():
        vector = _leer_vector_numerico(texto_vector, "vector", que="El vector a evaluar")
        if len(vector) != n:
            raise ErrorDeLectura(
                f"El vector a evaluar debe tener {n} componentes (T va de ℝ^{n}).", "vector")

    definicion = (_definicion(T, n, m) + ",\\quad " + T + _tex_vector(nombres) + " = "
                  + _tex_imagen([_tex_arbol(a) for a in arboles]))
    resultado = {
        "modo": "formula",
        "nombre": T,
        "n": n,
        "m": m,
        "variables": nombres,
        "definicion_tex": definicion,
        "linealidad": linealidad,
        "evaluacion": None,
        "matriz": None,
        "analisis": None,
    }

    if vector is not None:
        imagen = [_evaluar(p, vector) for p in polinomios]
        entorno = _sustituir_numeros(variables, vector)
        lineas = [_m(f"{T}{_tex_dominio(vector)} = "
                     f"{_tex_imagen([_tex_arbol(a, entorno) for a in arboles])} "
                     f"= {_tex_imagen_numerica(imagen)}")]
        pasos = [_paso_con("Sustituir", lineas,
                           "Se reemplaza cada variable por la componente del vector.")]
        if linealidad["es_lineal"]:
            A = _matriz_desde_polinomios(polinomios, n)
            pasos.append(_paso_con("Comprobación", [_comprobacion_matriz(A, vector)]))
        resultado["evaluacion"] = _seccion(
            "Evaluación de " + _m(f"{T}{_tex_dominio(vector)}"),
            pasos, "Resultado: " + _m(f"{T}{_tex_dominio(vector)} = {_tex_imagen_numerica(imagen)}"))

    if linealidad["es_lineal"]:
        A = _matriz_desde_polinomios(polinomios, n)
        resultado["matriz"] = _seccion_matriz(T, nombres, A)
        resultado["matriz"]["A"] = A
        resultado["analisis"] = _analisis(T, nombres, A)
    return resultado


# ---------------------------------------------------------------------------
# Punto de entrada · vectores dados
# ---------------------------------------------------------------------------
def analizar_vectores(pares: List[Dict], texto_vector: str = "", nombre: str = "T") -> Dict:
    """T dada por T(bᵢ) = wᵢ en una base {bᵢ} de ℝⁿ; T(v) opcional, núcleo … rango."""
    if not pares:
        raise ErrorDeLectura("Agregue al menos un vector con su imagen.", "pares")
    if len(pares) > DIMENSION_MAXIMA:
        raise ErrorDeLectura(f"Se admiten a lo sumo {DIMENSION_MAXIMA} vectores.", "pares")
    base, imagenes = [], []
    for k, par in enumerate(pares, start=1):
        base.append(_leer_vector_numerico(par.get("vector", ""), "pares", k, f"El vector {k}"))
        imagenes.append(_leer_vector_numerico(par.get("imagen", ""), "pares", k, f"La imagen {k}"))
    n, m = len(base[0]), len(imagenes[0])
    for k, (b, w) in enumerate(zip(base, imagenes), start=1):
        if len(b) != n:
            raise _error(f"El vector {k} tiene {len(b)} componentes y el primero {n}.", "pares", k)
        if len(w) != m:
            raise _error(f"La imagen {k} tiene {len(w)} componentes y la primera {m}.", "pares", k)
    if len(base) != n:
        raise ErrorDeLectura(
            f"Para determinar T: ℝ^{n} → ℝ^{m} se necesitan las imágenes de {n} vectores que "
            f"formen una base de ℝ^{n}; se dieron {len(base)}.", "pares")

    # ¿Los vectores dados forman una base? Se reduce [B | I] (B con los bᵢ como columnas).
    identidad = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]
    B = [[b[i] for b in base] for i in range(n)]
    reducida, _, pivotes = escalonar([B[i] + identidad[i] for i in range(n)], n, n)
    if len(pivotes) < n:
        raise ErrorDeLectura(
            "Los vectores dados son linealmente dependientes: no forman una base de "
            f"ℝ^{n}, así que no determinan T.", "pares")
    inversa = [fila[n:] for fila in reducida]          # B⁻¹
    canonica = all(sum(1 for v in b if v != 0) == 1 and any(v == 1 for v in b) for b in base)

    T = nombre
    nombres = [_tex_variable(v) for v in _nombres_por_defecto(n)]
    tex_b = [_tex_dominio(b) for b in base]
    tex_w = [_tex_imagen_numerica(w) for w in imagenes]
    tex_Tb = [f"{T}{t}" for t in tex_b]
    datos = [_m(f"{tb} = {tw}") for tb, tw in zip(tex_Tb, tex_w)]

    # A = W·B⁻¹ (columna j = T(eⱼ)).
    A = [[sum(imagenes[k][i] * inversa[k][j] for k in range(n)) for j in range(n)]
         for i in range(m)]
    extra = []
    if canonica:
        extra.append("Los vectores dados son la base canónica, así que sus imágenes son "
                     "directamente las columnas de A.")
    else:
        extra.append("Los vectores dados no son la base canónica: se escribe cada "
                     + _m(r"\mathbf{e}_j") + " como combinación de ellos y se aplica la "
                     "propiedad (iii).")
        for j in range(n):
            coefs = [inversa[k][j] for k in range(n)]
            extra.append(_m(
                f"{_tex_e(j)} = {_tex_combinacion(coefs, tex_b)} {FLECHA} "
                f"{T}({_tex_e(j)}) = {_tex_combinacion(coefs, tex_Tb)} = "
                f"{_tex_imagen_numerica(_columna(A, j))}"))

    resultado = {
        "modo": "vectores",
        "nombre": T,
        "n": n,
        "m": m,
        "variables": nombres,
        "definicion_tex": _definicion(T, n, m),
        "datos": datos,
        "linealidad": None,
        "evaluacion": None,
        "matriz": None,
        "analisis": None,
    }

    if (texto_vector or "").strip():
        v = _leer_vector_numerico(texto_vector, "vector", que="El vector a evaluar")
        if len(v) != n:
            raise ErrorDeLectura(
                f"El vector a evaluar debe tener {n} componentes (T va de ℝ^{n}).", "vector")
        resultado["evaluacion"] = _evaluar_con_base(T, v, base, imagenes, inversa, canonica, A)

    seccion = _seccion_matriz(T, nombres, A, extra, columnas=canonica)
    seccion["A"] = A
    resultado["matriz"] = seccion
    resultado["analisis"] = _analisis(T, nombres, A)
    return resultado


def _evaluar_con_base(T: str, v: List[Fraction], base, imagenes, inversa, canonica,
                      A) -> Dict:
    n = len(v)
    coefs = [sum(inversa[k][j] * v[j] for j in range(n)) for k in range(n)]
    tex_v = _tex_dominio(v)
    tex_b = [_tex_dominio(b) for b in base]
    tex_Tb = [f"{T}{t}" for t in tex_b]
    resultado = [sum(c * w[i] for c, w in zip(coefs, imagenes)) for i in range(len(imagenes[0]))]

    reduccion = None
    if canonica:
        nota = "Se escribe en la base canónica."
    else:
        nota = "Se resuelve el sistema [b₁ … bₙ | v] por Gauss-Jordan para hallar los coeficientes."
        matriz = [[b[i] for b in base] + [v[i]] for i in range(n)]
        reduccion, _, _ = _reduccion(matriz, n, n, [f"c_{{{k + 1}}}" for k in range(n)])
    descomponer = [_m(f"{tex_v} = {_tex_combinacion(coefs, tex_b)}")]
    linealidad = [_m(f"{T}{tex_v} = {_tex_combinacion(coefs, tex_Tb, punto=True)}")]
    escalados = [[c * x for x in w] for c, w in zip(coefs, imagenes)]
    sustituir = [
        _m(f"{T}{tex_v} = {_tex_combinacion(coefs, [_tex_imagen_numerica(w) for w in imagenes])}"),
        _m("= " + " + ".join(_tex_imagen_numerica(e) for c, e in zip(coefs, escalados) if c != 0)
           if any(coefs) else "= 0"),
    ]
    pasos = [
        _paso_con("Paso 1 · Descomponer", descomponer, nota, reduccion),
        _paso_con("Paso 2 · Linealidad", linealidad, "Propiedad (iii)."),
        _paso_con("Paso 3 · Sustituir", sustituir),
        _paso_con("Paso 4 · Resultado", [_m(f"{T}{tex_v} = {_tex_imagen_numerica(resultado)}")]),
        _paso_con("Comprobación", [_comprobacion_matriz(A, v)]),
    ]
    return _seccion("Cálculo de " + _m(f"{T}{tex_v}"), pasos,
                    "Resultado: " + _m(f"{T}{tex_v} = {_tex_imagen_numerica(resultado)}"))
