"""Módulo de Vectores: Independencia Lineal mediante el sistema homogéneo Ax = 0.

Los k vectores de Rⁿ se colocan como COLUMNAS de una matriz A (n × k) y se
añade una columna de ceros para formar [A | 0]. Tras reducirla por
Gauss-Jordan se cuentan los pivotes:
    - pivotes == k  -> solo la solución trivial      -> L.I.
    - pivotes <  k  -> hay variables libres          -> L.D.

CUMPLIMIENTO DE RESTRICCIONES ACADÉMICAS
----------------------------------------
- No se importa NumPy, SciPy ni `math`.
- Toda la aritmética usa `fractions.Fraction` (exacta, sin tolerancias).
- La reducción reutiliza `escalonar()`, `_buscar_fila_pivote()` y
  `_anular_columna()` de `backend/calculo/nucleo.py`, adaptadas a consola
  (los pasos se registran como texto en lugar de diccionarios para la web).
"""

from fractions import Fraction
from typing import List, Tuple

from teoremas.resumen_teoremas import TEOREMAS

NUMERO_MODULO: int = 2

# ---------------------------------------------------------------------------
# Constantes de configuración
# ---------------------------------------------------------------------------
DIMENSION_MINIMA: int = 1          # mínimo de vectores / componentes admitido
DIMENSION_MAXIMA: int = 8          # máximo de vectores / componentes admitido

# Traductor de dígitos a subíndices Unicode para escribir F₁, v₂, c₃, ...
_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

ARTE_ASCII: str = (
    "[v₁ v₂ v₃] MÓDULO: VECTORES E INDEPENDENCIA LINEAL\n"
    "[ 0  0  0] Combinaciones Lineales, L.I. y L.D.\n"
    "   Ax = 0"
)


# ---------------------------------------------------------------------------
# Utilidades de formato (adaptadas de nucleo.py)
# ---------------------------------------------------------------------------
def _copiar_matriz(matriz: List[List[Fraction]]) -> List[List[Fraction]]:
    """Devuelve una copia profunda de la matriz (fila por fila)."""
    return [fila[:] for fila in matriz]


def _subindice(indice_base_cero: int) -> str:
    """Convierte un índice (base 0) en su subíndice Unicode (base 1)."""
    return str(indice_base_cero + 1).translate(_SUBINDICES)


def _formatear_fraccion(valor: Fraction) -> str:
    """Escribe una fracción como '3', '-3' o '1/2' (sin decimales)."""
    if valor.denominator == 1:               # es un entero exacto
        return str(valor.numerator)
    return f"{valor.numerator}/{valor.denominator}"


def _factor_por_fila(coeficiente: Fraction, indice_fila: int) -> str:
    """Escribe el término 'c·Fᵢ' de una operación, omitiendo el 1."""
    magnitud = _formatear_fraccion(abs(coeficiente))
    if magnitud == "1":                       # el coeficiente 1 no se escribe
        return f"F{_subindice(indice_fila)}"
    return f"{magnitud}·F{_subindice(indice_fila)}"


# ---------------------------------------------------------------------------
# Eliminación de Gauss-Jordan (adaptada de nucleo.py)
# ---------------------------------------------------------------------------
def _buscar_fila_pivote(
    matriz: List[List[Fraction]], m: int, fila_inicial: int, columna: int
) -> int:
    """Devuelve la fila con mayor valor absoluto en la columna dada.

    Implementa la estrategia de pivoteo parcial previa a un posible
    intercambio de filas Fᵢ ↔ Fⱼ. Solo mira de `fila_inicial` hacia abajo.
    """
    fila_maxima = fila_inicial
    valor_maximo = abs(matriz[fila_inicial][columna])
    for fila in range(fila_inicial + 1, m):
        candidato = abs(matriz[fila][columna])
        if candidato > valor_maximo:          # se guarda el máximo encontrado
            valor_maximo = candidato
            fila_maxima = fila
    return fila_maxima


def _anular_columna(
    matriz: List[List[Fraction]], m: int, fila_pivote: int, columna: int
) -> List[str]:
    """Aplica Fₖ → Fₖ − c·Fᵢ a todas las filas salvo la del pivote.

    Anula la columna del pivote tanto por encima como por debajo de él
    (eliminación de Gauss-Jordan, no solo de Gauss).
    """
    pasos: List[str] = []
    for fila in range(m):
        if fila == fila_pivote:               # la fila pivote no se toca a sí misma
            continue

        factor = matriz[fila][columna]        # c = elemento a anular
        if factor == 0:                       # ya vale 0: no hace falta operar
            continue

        # Fₖ → Fₖ − factor·Fᵢ  (resta término a término de toda la fila)
        matriz[fila] = [
            valor_fila - factor * valor_pivote
            for valor_fila, valor_pivote in zip(matriz[fila], matriz[fila_pivote])
        ]
        signo = "-" if factor > 0 else "+"
        pasos.append(
            f"F{_subindice(fila)} → F{_subindice(fila)} {signo} "
            f"{_factor_por_fila(factor, fila_pivote)}"
        )
    return pasos


def escalonar(
    Ab: List[List[Fraction]], m: int, n: int
) -> Tuple[List[List[Fraction]], List[str], List[int]]:
    """Lleva [A | 0] a su forma escalonada reducida por filas (Gauss-Jordan).

    Devuelve (matriz_reducida, lista_de_pasos, columnas_pivote). Recorre las
    columnas de A de izquierda a derecha con un contador `fila_pivote`:
      1. Pivoteo parcial: busca el mayor |valor| de la columna.
      2. Si toda la columna es 0 -> variable libre; avanza sin subir fila_pivote.
      3. Fᵢ ↔ Fⱼ  si el pivote no está en su sitio.
      4. Fᵢ → (1/p)·Fᵢ  para dejar el pivote en 1.
      5. Fₖ → Fₖ − c·Fᵢ  para anular la columna arriba y abajo.
      6. Incrementa fila_pivote.
    """
    matriz = _copiar_matriz(Ab)               # se trabaja sobre una copia
    pasos: List[str] = []
    columnas_pivote: List[int] = []
    fila_pivote = 0                           # primera fila aún sin pivote fijado

    for columna in range(n):                  # solo columnas de A; la de ceros queda fuera
        if fila_pivote >= m:                  # ya no quedan filas donde poner pivotes
            break

        fila_maxima = _buscar_fila_pivote(matriz, m, fila_pivote, columna)

        # Paso 2: columna nula de fila_pivote hacia abajo -> variable libre.
        if matriz[fila_maxima][columna] == 0:
            continue                          # avanza de columna SIN subir fila_pivote

        # Paso 3: Fᵢ ↔ Fⱼ para traer el mayor pivote a la fila de trabajo.
        if fila_maxima != fila_pivote:
            matriz[fila_pivote], matriz[fila_maxima] = (
                matriz[fila_maxima],
                matriz[fila_pivote],
            )
            pasos.append(f"F{_subindice(fila_pivote)} ↔ F{_subindice(fila_maxima)}")

        # Paso 4: Fᵢ → (1/p)·Fᵢ para normalizar el pivote a 1.
        pivote = matriz[fila_pivote][columna]
        if pivote != 1:
            matriz[fila_pivote] = [valor / pivote for valor in matriz[fila_pivote]]
            inverso = _formatear_fraccion(Fraction(1, 1) / pivote)
            pasos.append(
                f"F{_subindice(fila_pivote)} → ({inverso})·F{_subindice(fila_pivote)}"
            )

        # Paso 5: Fₖ → Fₖ − c·Fᵢ para anular el resto de la columna.
        pasos.extend(_anular_columna(matriz, m, fila_pivote, columna))

        # Paso 6: esta columna ya tiene pivote; pasa a la siguiente fila.
        columnas_pivote.append(columna)
        fila_pivote += 1

    return matriz, pasos, columnas_pivote


# ---------------------------------------------------------------------------
# Lectura de datos
# ---------------------------------------------------------------------------
def _leer_entero(mensaje: str) -> int:
    """Pide un entero dentro de [DIMENSION_MINIMA, DIMENSION_MAXIMA]."""
    while True:
        texto = input(mensaje).strip()
        try:
            valor = int(texto)
        except ValueError:
            print(f"  ✗ '{texto}' no es un número entero. Intente de nuevo.")
            continue
        if DIMENSION_MINIMA <= valor <= DIMENSION_MAXIMA:
            return valor
        print(
            f"  ✗ Debe estar entre {DIMENSION_MINIMA} y {DIMENSION_MAXIMA}. "
            "Intente de nuevo."
        )


def _leer_vector(indice: int, n: int) -> List[Fraction]:
    """Pide las n componentes de vᵢ en una línea, validando cada Fraction."""
    while True:
        texto = input(f"  v{_subindice(indice)} = ").replace(",", " ").split()
        if len(texto) != n:
            print(f"  ✗ Se esperaban {n} componentes y se recibieron {len(texto)}.")
            continue
        try:
            return [Fraction(componente) for componente in texto]
        except (ValueError, ZeroDivisionError):
            print("  ✗ Componente inválida. Use enteros, decimales o fracciones (p. ej. -3, 2.5, 1/2).")


# ---------------------------------------------------------------------------
# Construcción e impresión de la matriz
# ---------------------------------------------------------------------------
def construir_matriz_homogenea(
    vectores: List[List[Fraction]], n: int
) -> List[List[Fraction]]:
    """Coloca los vectores como COLUMNAS de A y añade la columna de ceros.

    La fila i de [A | 0] contiene la i-ésima componente de cada vector,
    seguida de un 0: vᵢ ocupa la columna i de A.
    """
    return [
        [vector[fila] for vector in vectores] + [Fraction(0)]
        for fila in range(n)
    ]


def imprimir_matriz(matriz: List[List[Fraction]], k: int) -> None:
    """Imprime [A | 0] en formato tabular con encabezados c₁ … cₖ | 0."""
    textos = [[_formatear_fraccion(valor) for valor in fila] for fila in matriz]
    encabezados = [f"c{_subindice(j)}" for j in range(k)] + ["0"]

    anchos = []
    for columna in range(k + 1):
        ancho = len(encabezados[columna])
        for fila in textos:
            ancho = max(ancho, len(fila[columna]))
        anchos.append(ancho)

    def _linea(celdas: List[str]) -> str:
        izquierda = "  ".join(celdas[j].rjust(anchos[j]) for j in range(k))
        return f"  [ {izquierda} │ {celdas[k].rjust(anchos[k])} ]"

    print(_linea(encabezados))
    for fila in textos:
        print(_linea(fila))


# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------
def mostrar_teoremas() -> None:
    """Opción 0: imprime los teoremas clave del módulo."""
    print("\n── TEOREMAS CLAVE ──")
    print(f"  {TEOREMAS[NUMERO_MODULO]}")


def evaluar_independencia_lineal() -> None:
    """Opción 1: lee k vectores de Rⁿ y decide si son L.I. o L.D."""
    print("\n── EVALUAR INDEPENDENCIA LINEAL ──")
    k = _leer_entero("Cantidad de vectores (k): ")
    n = _leer_entero("Dimensión de cada vector (n): ")

    print(f"\nIngrese las {n} componentes de cada vector separadas por espacios:")
    vectores = [_leer_vector(i, n) for i in range(k)]

    # Sistema homogéneo c₁v₁ + … + cₖvₖ = 0  ->  [A | 0] de tamaño n × (k + 1).
    matriz = construir_matriz_homogenea(vectores, n)
    print("\nMatriz aumentada [A | 0] (vectores como columnas):")
    imprimir_matriz(matriz, k)

    reducida, pasos, columnas_pivote = escalonar(matriz, n, k)

    print("\nOperaciones elementales aplicadas:")
    if pasos:
        for numero, paso in enumerate(pasos, start=1):
            print(f"  {numero}. {paso}")
    else:
        print("  (ninguna: la matriz ya estaba reducida)")

    print("\nForma escalonada reducida por filas:")
    imprimir_matriz(reducida, k)

    pivotes = len(columnas_pivote)
    print(f"\nCantidad de pivotes: {pivotes}")
    print(f"Variables libres: {k - pivotes}")

    if pivotes == k:
        print("Veredicto: Linealmente Independiente (L.I.)")
    else:
        print("Veredicto: Linealmente Dependiente (L.D.)")


# ---------------------------------------------------------------------------
# Punto de entrada del módulo
# ---------------------------------------------------------------------------
def iniciar_modulo() -> None:
    """Muestra el arte del módulo y ejecuta su menú interno."""
    print()
    print(ARTE_ASCII)

    while True:
        print("\n  0. Ver Teoremas Clave")
        print("  1. Evaluar Independencia Lineal")
        print("  2. Volver al menú principal")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            mostrar_teoremas()
        elif opcion == "1":
            evaluar_independencia_lineal()
        elif opcion == "2":
            break
        else:
            print("Opción no válida. Intente de nuevo.")
