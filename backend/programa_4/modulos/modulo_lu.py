"""PROGRAMA 6 – Factorización LU (A = LU) y solución de sistemas Ax = b.

Obtiene L y U con operaciones de reemplazo de fila, verifica L·U == A y resuelve
Ax = b en dos etapas (Ly = b hacia adelante, Ux = y hacia atrás) usando solo listas
anidadas y fractions.Fraction. Unidad: Álgebra de Matrices (Segundo Corte).
Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

from fractions import Fraction
from typing import List, Optional, Tuple

# El producto matricial, las operaciones de fila, el formato y la lectura por consola
# ya existen en la Calculadora: se importan desde modulos/ en lugar de reescribirlos.
from modulos.modulo_matrices import (
    Matriz,
    copiar_matriz,
    describir_escalamiento,
    describir_reemplazo,
    dimension,
    escalar_fila,
    formatear_fraccion,
    imprimir_matriz,
    leer_dimensiones,
    leer_fraccion,
    leer_matriz,
    matriz_identidad,
    multiplicar_matrices,
    reemplazar_fila,
    subindice,
)
from teoremas.resumen_teoremas import TEOREMAS

Vector = List[Fraction]

NUMERO_MODULO: int = 5
OPCION_VOLVER: str = "2"

MENSAJE_SIN_FACTORIZACION: str = (
    "La matriz no admite Factorización LU sin permutación "
    "(requiere pivoteo parcial PA = LU)"
)
MENSAJE_FACTORIZACION_CORRECTA: str = "La factorización es correcta (L · U == A)"
MENSAJE_COMPROBACION_EXITOSA: str = "Comprobación exitosa: A · x == b"

ARTE_ASCII: str = (
    "[1 0 0] [u u u]  MÓDULO: FACTORIZACIÓN LU\n"
    "[ℓ 1 0]·[0 u u]  A = L·U,  Ly = b (adelante),  Ux = y (atrás)\n"
    "[ℓ ℓ 1] [0 0 u]  Solución de sistemas Ax = b"
)


class FactorizacionLUNoAdmitida(ValueError):
    """La matriz necesita un intercambio de filas: no existe A = LU sin permutación.

    Guarda la posición (fila, columna) del pivote nulo y la matriz reducida hasta ahí.
    """

    def __init__(self, fila: int, columna: int, matriz_parcial: Matriz) -> None:
        super().__init__(MENSAJE_SIN_FACTORIZACION)
        self.fila = fila
        self.columna = columna
        self.matriz_parcial = matriz_parcial


def columna_requiere_intercambio(matriz: Matriz, fila_pivote: int, columna: int) -> bool:
    """Indica si, con pivote 0 en (fila_pivote, columna), hay una entrada no nula debajo."""
    for fila in range(fila_pivote + 1, len(matriz)):
        if matriz[fila][columna] != 0:
            return True
    return False


def factorizar_lu(
    matriz_a: Matriz, historial: Optional[list] = None
) -> Tuple[Matriz, Matriz, List[str]]:
    """Factoriza A (m×n) como L·U usando solo reemplazos Fᵢ → Fᵢ − ℓᵢⱼ·Fⱼ.

    Devuelve (L, U, operaciones): L triangular inferior m×m con unos en la diagonal,
    U la forma escalonada m×n y el registro en texto de los reemplazos. Lanza
    FactorizacionLUNoAdmitida si un pivote nulo exige intercambiar filas. Si se da
    `historial`, agrega un diccionario por reemplazo con el multiplicador y las
    matrices L y U que quedan tras él (lo usa el paso a paso de la web).
    """
    filas, columnas = dimension(matriz_a)
    matriz_u = copiar_matriz(matriz_a)
    matriz_l = matriz_identidad(filas)
    operaciones: List[str] = []
    fila_pivote = 0
    for columna in range(columnas):
        if fila_pivote >= filas:
            break
        pivote = matriz_u[fila_pivote][columna]
        if pivote == 0:
            # Pivote nulo
            #  con entradas debajo: solo un intercambio lo arreglaría, y un
            # intercambio rompe la forma triangular de L (haría falta PA = LU).
            if columna_requiere_intercambio(matriz_u, fila_pivote, columna):
                raise FactorizacionLUNoAdmitida(fila_pivote, columna, matriz_u)
            # Columna nula del pivote hacia abajo: no hay nada que eliminar y la misma
            # fila busca su pivote en la columna siguiente (U queda escalonada).
            continue
        for fila in range(fila_pivote + 1, filas):
            entrada = matriz_u[fila][columna]
            multiplicador = entrada / pivote
            # Se registra el multiplicador de eliminación en L antes de alterar la fila en
            # U: después del reemplazo la entrada vale 0 y el dato se perdería.
            matriz_l[fila][fila_pivote] = multiplicador
            if multiplicador == 0:
                continue
            matriz_u = reemplazar_fila(matriz_u, fila, -multiplicador, fila_pivote)
            operaciones.append(describir_reemplazo(fila, -multiplicador, fila_pivote))
            if historial is not None:
                historial.append({
                    "operacion": operaciones[-1],
                    "fila": fila,
                    "fila_pivote": fila_pivote,
                    "columna": columna,
                    "entrada": entrada,
                    "pivote": pivote,
                    "multiplicador": multiplicador,
                    "U": matriz_u,
                    "L": copiar_matriz(matriz_l),
                })
        fila_pivote += 1
    return matriz_l, matriz_u, operaciones


def verificar_factorizacion(
    matriz_a: Matriz, matriz_l: Matriz, matriz_u: Matriz
) -> Tuple[Matriz, bool]:
    """Devuelve (L·U, es_correcta) con el producto matricial de la Calculadora."""
    producto_lu = multiplicar_matrices(matriz_l, matriz_u)
    # Con Fraction la comparación con A es exacta: no hace falta tolerancia de redondeo.
    return producto_lu, producto_lu == matriz_a


def vector_a_columna(vector: Vector) -> Matriz:
    """Convierte un vector de n componentes en una matriz columna n×1."""
    return [[componente] for componente in vector]


def columna_a_vector(matriz_columna: Matriz) -> Vector:
    """Convierte una matriz columna n×1 en un vector de n componentes."""
    return [fila[0] for fila in matriz_columna]


def construir_aumentada(matriz: Matriz, vector: Vector) -> Matriz:
    """Devuelve la matriz aumentada [M | v] agregando el vector como última columna."""
    return [matriz[fila] + [vector[fila]] for fila in range(len(matriz))]


def ultima_columna(matriz: Matriz) -> Vector:
    """Devuelve la última columna de una matriz aumentada como vector."""
    return [fila[-1] for fila in matriz]


def tiene_diagonal_no_nula(matriz: Matriz) -> bool:
    """Indica si todas las entradas de la diagonal de una matriz cuadrada son ≠ 0."""
    for indice in range(len(matriz)):
        if matriz[indice][indice] == 0:
            return False
    return True


def sustitucion_hacia_adelante(
    matriz_l: Matriz, vector_b: Vector, historial: Optional[list] = None
) -> Tuple[Vector, List[str]]:
    """Resuelve Ly = b reduciendo [L | b] de arriba hacia abajo.

    Recibe L (n×n, unos en la diagonal) y b; devuelve (y, operaciones). Si se da
    `historial`, guarda (tipo, columna, matriz) tras cada operación, igual que escalonar().
    """
    aumentada = construir_aumentada(matriz_l, vector_b)
    operaciones: List[str] = []
    orden = len(matriz_l)
    # La diagonal de L ya vale 1: cada columna se anula hacia abajo solo con reemplazos,
    # de modo que y₁ queda resuelta primero y alimenta a las filas siguientes.
    for columna in range(orden):
        for fila in range(columna + 1, orden):
            factor = aumentada[fila][columna]
            if factor == 0:
                continue
            aumentada = reemplazar_fila(aumentada, fila, -factor, columna)
            operaciones.append(describir_reemplazo(fila, -factor, columna))
            if historial is not None:
                historial.append(("eliminacion", columna, aumentada))
    return ultima_columna(aumentada), operaciones


def sustitucion_hacia_atras(
    matriz_u: Matriz, vector_y: Vector, historial: Optional[list] = None
) -> Tuple[Optional[Vector], List[str]]:
    """Resuelve Ux = y reduciendo [U | y] de abajo hacia arriba.

    Recibe U (n×n triangular superior) e y; devuelve (x, operaciones). x es None si U
    tiene un 0 en la diagonal, porque entonces el sistema no tiene solución única.
    """
    if not tiene_diagonal_no_nula(matriz_u):
        return None, []
    aumentada = construir_aumentada(matriz_u, vector_y)
    operaciones: List[str] = []
    orden = len(matriz_u)
    # Se empieza por la última fila porque es la única con una sola incógnita (xₙ);
    # cada pivote se lleva a 1 y luego se anula su columna hacia arriba.
    for columna in range(orden - 1, -1, -1):
        pivote = aumentada[columna][columna]
        if pivote != 1:
            aumentada = escalar_fila(aumentada, columna, Fraction(1) / pivote)
            operaciones.append(describir_escalamiento(columna, Fraction(1) / pivote))
            if historial is not None:
                historial.append(("normalizacion", columna, aumentada))
        for fila in range(columna - 1, -1, -1):
            factor = aumentada[fila][columna]
            if factor == 0:
                continue
            aumentada = reemplazar_fila(aumentada, fila, -factor, columna)
            operaciones.append(describir_reemplazo(fila, -factor, columna))
            if historial is not None:
                historial.append(("eliminacion", columna, aumentada))
    return ultima_columna(aumentada), operaciones


def resolver_con_lu(
    matriz_l: Matriz, matriz_u: Matriz, vector_b: Vector
) -> Tuple[Vector, Optional[Vector]]:
    """Resuelve Ax = b a partir de A = LU; devuelve (y, x), con x = None si U es singular."""
    # Ax = L(Ux) = b: se llama y = Ux, se resuelve Ly = b y después Ux = y.
    vector_y, _ = sustitucion_hacia_adelante(matriz_l, vector_b)
    vector_x, _ = sustitucion_hacia_atras(matriz_u, vector_y)
    return vector_y, vector_x


def verificar_solucion(
    matriz_a: Matriz, vector_x: Vector, vector_b: Vector
) -> Tuple[Vector, bool]:
    """Devuelve (A·x, es_correcta) con el producto matricial de la Calculadora."""
    producto_ax = columna_a_vector(multiplicar_matrices(matriz_a, vector_a_columna(vector_x)))
    return producto_ax, producto_ax == vector_b


def leer_vector(nombre: str, num_componentes: int) -> Vector:
    """Pide por consola las componentes de un vector y lo devuelve como lista de Fraction."""
    print(f"\nComponentes de {nombre} ({num_componentes}):")
    return [
        leer_fraccion(f"  {nombre}{subindice(indice)}: ")
        for indice in range(num_componentes)
    ]


def imprimir_vector(titulo: str, vector: Vector) -> None:
    """Imprime un vector como matriz columna con su título."""
    imprimir_matriz(titulo, vector_a_columna(vector))


def mostrar_operaciones(operaciones: List[str]) -> None:
    """Imprime numerados los reemplazos de fila aplicados para llegar a U."""
    print("\nReemplazos de fila aplicados (cada multiplicador se guarda en L):")
    if not operaciones:
        print("  (ninguno: la matriz ya estaba en forma escalonada)")
    for numero, operacion in enumerate(operaciones, start=1):
        print(f"  {numero}. {operacion}")


def mostrar_solucion_del_sistema(
    matriz_a: Matriz, matriz_l: Matriz, matriz_u: Matriz, vector_b: Vector
) -> None:
    """Imprime y, x y la comprobación A·x == b para una matriz cuadrada."""
    vector_y, vector_x = resolver_con_lu(matriz_l, matriz_u, vector_b)
    imprimir_vector("Vector intermedio y (Ly = b, sustitución hacia adelante)", vector_y)
    if vector_x is None:
        print("\nU tiene un 0 en la diagonal: A es singular y Ax = b no tiene solución única.")
        return
    imprimir_vector("Vector solución x (Ux = y, sustitución hacia atrás)", vector_x)
    _, es_correcta = verificar_solucion(matriz_a, vector_x, vector_b)
    print(f"\n{MENSAJE_COMPROBACION_EXITOSA}" if es_correcta else "\nA · x != b ✗")


def mostrar_teoremas() -> None:
    """Opción 0: imprime los teoremas clave del módulo."""
    print("\n── TEOREMAS CLAVE ──")
    print(f"  {TEOREMAS[NUMERO_MODULO]}")


def opcion_factorizacion() -> None:
    """Opción 1: lee A (m×n) y b, muestra L y U, verifica L·U == A y resuelve Ax = b."""
    print("\n── FACTORIZACIÓN LU Y SOLUCIÓN Ax = b ──")
    dimension_a = leer_dimensiones("A")
    matriz_a = leer_matriz("A", dimension_a)
    vector_b = leer_vector("b", dimension_a[0])
    try:
        matriz_l, matriz_u, operaciones = factorizar_lu(matriz_a)
    except FactorizacionLUNoAdmitida as error:
        print(f"\n✗ {error}")
        return
    mostrar_operaciones(operaciones)
    imprimir_matriz("L (triangular inferior, unos en la diagonal)", matriz_l)
    imprimir_matriz("U (forma escalonada de A)", matriz_u)
    _, es_correcta = verificar_factorizacion(matriz_a, matriz_l, matriz_u)
    print(f"\n{MENSAJE_FACTORIZACION_CORRECTA}" if es_correcta else "\nL · U != A ✗")
    if dimension_a[0] != dimension_a[1]:
        print("\nA no es cuadrada: el sistema Ax = b solo se resuelve para matrices n×n.")
        return
    mostrar_solucion_del_sistema(matriz_a, matriz_l, matriz_u, vector_b)


def mostrar_menu() -> None:
    """Imprime las opciones del menú interno del módulo."""
    print("\n  0. Ver Teoremas Clave")
    print("  1. Factorización LU y solución Ax = b")
    print(f"  {OPCION_VOLVER}. Volver al menú principal")


# Opción del menú -> función que la atiende (mismo patrón que MODULOS en main.py).
ACCIONES = {
    "0": mostrar_teoremas,
    "1": opcion_factorizacion,
}


def iniciar_modulo() -> None:
    """Muestra el arte del módulo y ejecuta su menú interno."""
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
