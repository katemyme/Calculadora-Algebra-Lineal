"""Calculadora de Matrices: demostración de los teoremas de la transpuesta.

    1. (Aᵀ)ᵀ = A
    2. (A + B)ᵀ = Aᵀ + Bᵀ
    3. (rA)ᵀ = r(Aᵀ)
    4. (AB)ᵀ = BᵀAᵀ

(Aᵀ)ᵀ = A trabaja con una sola matriz: se transpone dos veces (cadena
A → Aᵀ → (Aᵀ)ᵀ) y se comprueba que se recupera A. En los otros tres se
desarrollan el lado izquierdo y el lado derecho paso a paso y al final se
contrastan ambas matrices elemento por elemento.

Las fórmulas viajan en LaTeX; el frontend las dibuja con KaTeX.

CUMPLIMIENTO DE RESTRICCIONES ACADÉMICAS
----------------------------------------
- Python puro: no se importa NumPy, SciPy ni SymPy.
- Las matrices son listas de listas y cada operación se implementa con
  bucles `for` explícitos.
- `fractions.Fraction` (biblioteca estándar) da aritmética exacta, para que
  la comparación final sea una igualdad exacta y no aproximada.
"""

from fractions import Fraction
from typing import Dict, List, Optional

from calculo.nucleo import ErrorDeEntrada, parsear_valor
from calculo.programa3_web import ErrorDeCampo

Matriz = List[List[Fraction]]

DIMENSION_MINIMA: int = 1
DIMENSION_MAXIMA: int = 8

# Enunciados en LaTeX (el frontend los dibuja con KaTeX).
TEOREMAS = {
    "doble": r"(A^{T})^{T} = A",
    "suma": r"(A + B)^{T} = A^{T} + B^{T}",
    "escalar": r"(rA)^{T} = r\,A^{T}",
    "producto": r"(AB)^{T} = B^{T}A^{T}",
}

# Nombres LaTeX de las matrices intermedias.
_A, _B = "A", "B"
_AT, _BT = "A^{T}", "B^{T}"


# ---------------------------------------------------------------------------
# Formato LaTeX
# ---------------------------------------------------------------------------
def _tex(valor: Fraction) -> str:
    """Número exacto en LaTeX: enteros tal cual, fracciones con \\frac."""
    if valor.denominator == 1:
        return str(valor.numerator)
    signo = "-" if valor < 0 else ""
    return f"{signo}\\frac{{{abs(valor.numerator)}}}{{{valor.denominator}}}"


def _factor(valor: Fraction) -> str:
    """Factor dentro de una operación; los negativos van entre paréntesis."""
    texto = _tex(valor)
    return f"\\left({texto}\\right)" if valor < 0 else texto


def _entrada(nombre: str, i: int, j: int) -> str:
    """Entrada (i, j) en base 1: 'a_{12}' para A, '(A^{T})_{12}' para el resto."""
    indices = f"{i + 1}{j + 1}"
    if nombre in (_A, _B):
        return f"{nombre.lower()}_{{{indices}}}"
    return f"({nombre})_{{{indices}}}"


def _orden(M: Matriz) -> str:
    return f"{len(M)}×{len(M[0])}"


# ---------------------------------------------------------------------------
# Operaciones fundamentales (bucles nativos)
# ---------------------------------------------------------------------------
def transponer(M: Matriz) -> Matriz:
    """Intercambia filas por columnas: (Mᵀ)ᵢⱼ = Mⱼᵢ."""
    filas, columnas = len(M), len(M[0])
    resultado = []
    for i in range(columnas):
        fila = []
        for j in range(filas):
            fila.append(M[j][i])
        resultado.append(fila)
    return resultado


def sumar(M1: Matriz, M2: Matriz) -> Matriz:
    """Suma elemento a elemento; exige dimensiones idénticas."""
    if len(M1) != len(M2) or len(M1[0]) != len(M2[0]):
        raise ErrorDeEntrada(
            f"No se puede sumar una matriz {_orden(M1)} con una {_orden(M2)}: "
            "la suma exige que ambas tengan exactamente las mismas dimensiones."
        )
    resultado = []
    for i in range(len(M1)):
        fila = []
        for j in range(len(M1[0])):
            fila.append(M1[i][j] + M2[i][j])
        resultado.append(fila)
    return resultado


def multiplicar_escalar(k: Fraction, M: Matriz) -> Matriz:
    """Multiplica cada entrada de M por el número k."""
    resultado = []
    for i in range(len(M)):
        fila = []
        for j in range(len(M[0])):
            fila.append(k * M[i][j])
        resultado.append(fila)
    return resultado


def multiplicar_matrices(M1: Matriz, M2: Matriz) -> Matriz:
    """Producto fila-columna: cᵢⱼ = Σₖ M1ᵢₖ·M2ₖⱼ."""
    if len(M1[0]) != len(M2):
        raise ErrorDeEntrada(
            f"No se puede multiplicar una matriz {_orden(M1)} por una {_orden(M2)}: "
            f"las columnas de la primera ({len(M1[0])}) deben coincidir con las "
            f"filas de la segunda ({len(M2)})."
        )
    resultado = []
    for i in range(len(M1)):
        fila = []
        for j in range(len(M2[0])):
            acumulado = Fraction(0)
            for k in range(len(M2)):
                acumulado += M1[i][k] * M2[k][j]
            fila.append(acumulado)
        resultado.append(fila)
    return resultado


# ---------------------------------------------------------------------------
# Detalle aritmético de cada operación (una línea LaTeX por entrada)
# ---------------------------------------------------------------------------
def _detalle_suma(M1: Matriz, M2: Matriz, n1: str, n2: str, destino: str) -> List[str]:
    S = sumar(M1, M2)
    lineas = []
    for i in range(len(S)):
        for j in range(len(S[0])):
            lineas.append(
                f"{_entrada(destino, i, j)} = {_entrada(n1, i, j)} + {_entrada(n2, i, j)}"
                f" = {_factor(M1[i][j])} + {_factor(M2[i][j])} = {_tex(S[i][j])}"
            )
    return lineas


def _detalle_escalar(r: Fraction, M: Matriz, nombre: str, destino: str) -> List[str]:
    R = multiplicar_escalar(r, M)
    lineas = []
    for i in range(len(R)):
        for j in range(len(R[0])):
            lineas.append(
                f"{_entrada(destino, i, j)} = r\\,{_entrada(nombre, i, j)}"
                f" = {_factor(r)}\\cdot{_factor(M[i][j])} = {_tex(R[i][j])}"
            )
    return lineas


def _detalle_producto(M1: Matriz, M2: Matriz, n1: str, n2: str, destino: str) -> List[str]:
    P = multiplicar_matrices(M1, M2)
    lineas = []
    for i in range(len(P)):
        for j in range(len(P[0])):
            simbolos = " + ".join(
                f"{_entrada(n1, i, k)}{_entrada(n2, k, j)}" for k in range(len(M2))
            )
            valores = " + ".join(
                f"{_factor(M1[i][k])}\\cdot{_factor(M2[k][j])}" for k in range(len(M2))
            )
            lineas.append(
                f"{_entrada(destino, i, j)} = {simbolos} = {valores} = {_tex(P[i][j])}"
            )
    return lineas


def _paso(
    nombre: str,
    matriz: Matriz,
    descripcion: str,
    detalle: Optional[List[str]] = None,
    transpuesta_de: Optional[Dict] = None,
    suma_de: Optional[List[Dict]] = None,
    producto_de: Optional[List[Dict]] = None,
    escalar_de: Optional[Dict] = None,
) -> Dict:
    """Un paso del desarrollo.

    `nombre` es LaTeX; `descripcion` es texto con fragmentos LaTeX entre `$`.
    Si el paso es una transposición, `transpuesta_de` lleva la matriz de
    origen para que el frontend anime cómo cada fila pasa a ser columna.
    Si es una suma, `suma_de` lleva los dos sumandos para que el frontend
    muestre cómo se suma cada par de entradas. Si es un producto,
    `producto_de` lleva los dos factores para mostrar cada fila por columna.
    Si es un escalar por una matriz, `escalar_de` lleva el escalar y la matriz.
    """
    return {
        "nombre": nombre,
        "orden": _orden(matriz),
        "matriz": matriz,
        "descripcion": descripcion,
        "detalle": detalle or [],
        "transpuesta_de": transpuesta_de,
        "suma_de": suma_de,
        "producto_de": producto_de,
        "escalar_de": escalar_de,
    }


def _paso_transpuesta(origen: Matriz, n_origen: str, destino: str) -> Dict:
    T = transponer(origen)
    return _paso(
        destino, T,
        f"Cada fila de ${n_origen}$ se escribe como columna: la fila $i$ de "
        f"${n_origen}$ pasa a ser la columna $i$ de ${destino}$. "
        f"Una matriz {_orden(origen)} se convierte en una {_orden(T)}.",
        transpuesta_de={"nombre": n_origen, "matriz": origen},
    )


def _comparar(izquierda: Matriz, derecha: Matriz, n_izq: str, n_der: str) -> Dict:
    """Contrasta ambas matrices finales elemento por elemento."""
    mismas_dimensiones = (
        len(izquierda) == len(derecha) and len(izquierda[0]) == len(derecha[0])
    )
    iguales = []
    cumple = mismas_dimensiones
    if mismas_dimensiones:
        for i in range(len(izquierda)):
            fila = []
            for j in range(len(izquierda[0])):
                igual = izquierda[i][j] == derecha[i][j]
                cumple = cumple and igual
                fila.append(igual)
            iguales.append(fila)
    return {
        "nombre_izquierda": n_izq,
        "nombre_derecha": n_der,
        "izquierda": izquierda,
        "derecha": derecha,
        "orden_izquierda": _orden(izquierda),
        "orden_derecha": _orden(derecha),
        "iguales": iguales,
        "cumple": cumple,
    }


# ---------------------------------------------------------------------------
# Teoremas
# ---------------------------------------------------------------------------
def teorema_doble_transpuesta(A: Matriz) -> Dict:
    """(Aᵀ)ᵀ = A: una sola matriz que se transpone dos veces.

    No hay dos lados que desarrollar: es una cadena A → Aᵀ → (Aᵀ)ᵀ y al
    final se comprueba que se volvió a la matriz original.
    """
    ATT_nombre = r"(A^{T})^{T}"
    AT = transponer(A)
    ATT = transponer(AT)
    return {
        "modo": "cadena",
        "pasos": [
            _paso("A", A, f"Matriz original $A$ de orden {_orden(A)}."),
            _paso_transpuesta(A, _A, _AT),
            _paso_transpuesta(AT, _AT, ATT_nombre),
        ],
        "razonamiento": [
            r"\big((A^{T})^{T}\big)_{ij} = (A^{T})_{ji} = a_{ij}",
        ],
        "comparacion": _comparar(ATT, A, ATT_nombre, "A"),
    }


def teorema_suma(A: Matriz, B: Matriz) -> Dict:
    if len(A) != len(B) or len(A[0]) != len(B[0]):
        raise ErrorDeCampo(
            f"No se puede calcular A + B: A es {_orden(A)} y B es {_orden(B)}. "
            "Para sumar, ambas matrices deben tener las mismas dimensiones.",
            campo="B",
        )
    S = sumar(A, B)
    ST = transponer(S)
    AT, BT = transponer(A), transponer(B)
    SD = sumar(AT, BT)
    return {
        "modo": "lados",
        "izquierda": [
            _paso("A + B", S, "Se suman $A$ y $B$ entrada por entrada.",
                  _detalle_suma(A, B, _A, _B, "A + B"),
                  suma_de=[{"nombre": _A, "matriz": A}, {"nombre": _B, "matriz": B}]),
            _paso_transpuesta(S, "A + B", "(A + B)^{T}"),
        ],
        "derecha": [
            _paso_transpuesta(A, _A, _AT),
            _paso_transpuesta(B, _B, _BT),
            _paso("A^{T} + B^{T}", SD, "Se suman las transpuestas entrada por entrada.",
                  _detalle_suma(AT, BT, _AT, _BT, "A^{T} + B^{T}"),
                  suma_de=[{"nombre": _AT, "matriz": AT}, {"nombre": _BT, "matriz": BT}]),
        ],
        "comparacion": _comparar(ST, SD, "(A + B)^{T}", "A^{T} + B^{T}"),
    }


def teorema_escalar(A: Matriz, r: Fraction) -> Dict:
    rA = multiplicar_escalar(r, A)
    rAT = transponer(rA)
    AT = transponer(A)
    rDer = multiplicar_escalar(r, AT)
    return {
        "modo": "lados",
        "izquierda": [
            _paso("rA", rA, f"Cada entrada de $A$ se multiplica por $r = {_tex(r)}$.",
                  _detalle_escalar(r, A, _A, "rA"),
                  escalar_de={"r": r, "nombre": _A, "matriz": A}),
            _paso_transpuesta(rA, "rA", "(rA)^{T}"),
        ],
        "derecha": [
            _paso_transpuesta(A, _A, _AT),
            _paso(r"r\,A^{T}", rDer,
                  f"Cada entrada de $A^{{T}}$ se multiplica por $r = {_tex(r)}$.",
                  _detalle_escalar(r, AT, _AT, r"r\,A^{T}"),
                  escalar_de={"r": r, "nombre": _AT, "matriz": AT}),
        ],
        "comparacion": _comparar(rAT, rDer, "(rA)^{T}", r"r\,A^{T}"),
    }


def teorema_producto(A: Matriz, B: Matriz) -> Dict:
    if len(A[0]) != len(B):
        raise ErrorDeCampo(
            f"No se puede calcular AB: A es {_orden(A)} y B es {_orden(B)}. "
            f"Las columnas de A ({len(A[0])}) deben coincidir con las filas de B ({len(B)}).",
            campo="B",
        )
    AB = multiplicar_matrices(A, B)
    ABT = transponer(AB)
    BT, AT = transponer(B), transponer(A)
    BTAT = multiplicar_matrices(BT, AT)
    return {
        "modo": "lados",
        "izquierda": [
            _paso("AB", AB,
                  f"Producto fila por columna: $A$ ({_orden(A)}) por $B$ ({_orden(B)}) "
                  f"da una matriz {_orden(AB)}.",
                  _detalle_producto(A, B, _A, _B, "AB"),
                  producto_de=[{"nombre": _A, "matriz": A}, {"nombre": _B, "matriz": B}]),
            _paso_transpuesta(AB, "AB", "(AB)^{T}"),
        ],
        "derecha": [
            _paso_transpuesta(B, _B, _BT),
            _paso_transpuesta(A, _A, _AT),
            _paso(
                "B^{T}A^{T}", BTAT,
                f"¡Cambia el orden de los factores! $B^{{T}}$ ({_orden(BT)}) por "
                f"$A^{{T}}$ ({_orden(AT)}) da una matriz {_orden(BTAT)}. El producto "
                "$A^{T}B^{T}$ en general no coincide (ni siquiera tiene por qué estar definido).",
                _detalle_producto(BT, AT, _BT, _AT, "B^{T}A^{T}"),
                producto_de=[{"nombre": _BT, "matriz": BT}, {"nombre": _AT, "matriz": AT}],
            ),
        ],
        "comparacion": _comparar(ABT, BTAT, "(AB)^{T}", "B^{T}A^{T}"),
    }


# ---------------------------------------------------------------------------
# Lectura del texto recibido por HTTP
# ---------------------------------------------------------------------------
def _leer_matriz(datos: List[List[str]], campo: str) -> Matriz:
    if not datos or not datos[0]:
        raise ErrorDeCampo(f"La matriz {campo} está vacía.", campo=campo)
    for valor, que in ((len(datos), "filas"), (len(datos[0]), "columnas")):
        if not (DIMENSION_MINIMA <= valor <= DIMENSION_MAXIMA):
            raise ErrorDeCampo(
                f"El número de {que} de {campo} debe estar entre {DIMENSION_MINIMA} "
                f"y {DIMENSION_MAXIMA}; se recibió {valor}.",
                campo=campo,
            )
    columnas = len(datos[0])
    matriz = []
    for i, fila in enumerate(datos):
        if len(fila) != columnas:
            raise ErrorDeCampo(
                f"La fila {i + 1} de {campo} tiene {len(fila)} valores y se esperaban {columnas}.",
                campo=campo, fila=i + 1,
            )
        convertida = []
        for j, texto in enumerate(fila):
            try:
                convertida.append(parsear_valor(str(texto or "")))
            except ErrorDeEntrada:
                raise ErrorDeCampo(
                    f"La entrada ({i + 1}, {j + 1}) de {campo} no es un número: "
                    f"'{str(texto).strip()}'. Use enteros, decimales o fracciones (p. ej. -3, 2.5, 1/2).",
                    campo=campo, fila=i + 1, columna=j + 1,
                )
        matriz.append(convertida)
    return matriz


def _leer_escalar(texto: Optional[str]) -> Fraction:
    if texto is None or str(texto).strip() == "":
        raise ErrorDeCampo("Escriba el escalar r para este teorema.", campo="r")
    try:
        return parsear_valor(str(texto))
    except ErrorDeEntrada:
        raise ErrorDeCampo(
            f"El escalar r no es un número válido: '{str(texto).strip()}'.", campo="r"
        )


def demostrar(teorema: str, A_txt, B_txt, r_txt) -> Dict:
    """Punto de entrada web: lee los datos y desarrolla el teorema pedido."""
    A = _leer_matriz(A_txt, "A")
    if teorema == "doble":
        desarrollo = teorema_doble_transpuesta(A)
    elif teorema == "escalar":
        desarrollo = teorema_escalar(A, _leer_escalar(r_txt))
    else:
        B = _leer_matriz(B_txt, "B")
        if teorema == "suma":
            desarrollo = teorema_suma(A, B)
        else:
            desarrollo = teorema_producto(A, B)
    return {"teorema": teorema, "enunciado": TEOREMAS[teorema], **desarrollo}
