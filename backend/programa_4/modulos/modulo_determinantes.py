"""Módulo IV – Determinantes: Regla de Cramer para sistemas Ax = b.

Resuelve un sistema n×n con xᵢ = det Aᵢ(b) / det A, i = 1, 2, …, n, donde Aᵢ(b) es
la matriz A con su columna i reemplazada por b. Usa solo listas anidadas y
fractions.Fraction (aritmética exacta).
"""

from fractions import Fraction
from typing import List, Optional, Tuple

# El determinante, la lectura por consola y la comprobación A·x == b ya existen en la
# Calculadora: se importan desde modulos/ en lugar de reescribirlos.
from modulos.modulo_lu import Vector, imprimir_vector, leer_vector, verificar_solucion
from modulos.modulo_matrices import (
    Matriz,
    copiar_matriz,
    determinante_por_reduccion,
    formatear_fraccion,
    imprimir_matriz,
    leer_matriz_cuadrada,
    subindice,
    validar_cuadrada,
)
from teoremas.resumen_teoremas import TEOREMAS

NUMERO_MODULO: int = 4
OPCION_VOLVER: str = "2"

MENSAJE_SIN_SOLUCION: str = (
    "det A = 0 y algún det Aᵢ(b) ≠ 0: el sistema es inconsistente (no tiene solución)."
)
MENSAJE_NO_DECIDE: str = (
    "det A = 0 y todos los det Aᵢ(b) = 0: la Regla de Cramer no decide. El sistema no "
    "tiene solución única (puede tener infinitas soluciones o ninguna); resuélvalo por "
    "Gauss-Jordan."
)
MENSAJE_COMPROBACION_EXITOSA: str = "Comprobación exitosa: A · x == b"

ARTE_ASCII: str = (
    "|a b| MÓDULO: DETERMINANTES\n"
    "|c d| det(A) = ad - bc, Cofactores y Regla de Cramer"
)


def reemplazar_columna(matriz: Matriz, columna: int, vector: Vector) -> Matriz:
    """Devuelve Aᵢ(b): una copia de la matriz con la columna indicada (base 0) cambiada por b."""
    resultado = copiar_matriz(matriz)
    for fila in range(len(matriz)):
        resultado[fila][columna] = vector[fila]
    return resultado


def matrices_de_cramer(matriz_a: Matriz, vector_b: Vector) -> List[Matriz]:
    """Devuelve [A₁(b), A₂(b), …, Aₙ(b)], una matriz por cada incógnita."""
    return [
        reemplazar_columna(matriz_a, columna, vector_b) for columna in range(len(matriz_a))
    ]


def resolver_por_cramer(
    matriz_a: Matriz, vector_b: Vector
) -> Tuple[Fraction, List[Fraction], Optional[Vector]]:
    """Resuelve Ax = b (A de orden n) con xᵢ = det Aᵢ(b) / det A.

    Devuelve (det A, [det A₁(b), …, det Aₙ(b)], x). x es None si det A = 0, porque
    entonces la regla no se puede aplicar: no hay solución única.
    """
    validar_cuadrada(matriz_a)
    determinante_a = determinante_por_reduccion(matriz_a)
    determinantes = [
        determinante_por_reduccion(matriz_i)
        for matriz_i in matrices_de_cramer(matriz_a, vector_b)
    ]
    # Dividir entre det A solo tiene sentido si es distinto de 0 (A invertible).
    if determinante_a == 0:
        return determinante_a, determinantes, None
    return determinante_a, determinantes, [valor / determinante_a for valor in determinantes]


def diagnostico_sin_solucion_unica(determinantes: List[Fraction]) -> str:
    """Explica qué se sabe del sistema cuando det A = 0, a partir de los det Aᵢ(b)."""
    # Si Ax = b tuviera solución, det Aᵢ(b) = xᵢ·det A = 0 para toda i: basta un
    # det Aᵢ(b) ≠ 0 para saber que no hay ninguna.
    for valor in determinantes:
        if valor != 0:
            return MENSAJE_SIN_SOLUCION
    return MENSAJE_NO_DECIDE


def mostrar_teoremas() -> None:
    """Opción 0: imprime los teoremas clave del módulo."""
    print("\n── TEOREMAS CLAVE ──")
    print(f"  {TEOREMAS[NUMERO_MODULO]}")


def opcion_cramer() -> None:
    """Opción 1: lee A (n×n) y b, muestra cada Aᵢ(b) con su determinante y la solución x."""
    print("\n── REGLA DE CRAMER: xᵢ = det Aᵢ(b) / det A ──")
    matriz_a = leer_matriz_cuadrada("A")
    vector_b = leer_vector("b", len(matriz_a))
    determinante_a, determinantes, vector_x = resolver_por_cramer(matriz_a, vector_b)
    print(f"\ndet A = {formatear_fraccion(determinante_a)}")
    matrices = matrices_de_cramer(matriz_a, vector_b)
    for indice in range(len(matrices)):
        nombre = f"A{subindice(indice)}(b)"
        imprimir_matriz(f"{nombre}: columna {indice + 1} de A reemplazada por b", matrices[indice])
        print(f"  det {nombre} = {formatear_fraccion(determinantes[indice])}")
    if vector_x is None:
        print(f"\n✗ {diagnostico_sin_solucion_unica(determinantes)}")
        return
    print()
    for indice in range(len(vector_x)):
        print(
            f"  x{subindice(indice)} = det A{subindice(indice)}(b) / det A = "
            f"({formatear_fraccion(determinantes[indice])}) / "
            f"({formatear_fraccion(determinante_a)}) = {formatear_fraccion(vector_x[indice])}"
        )
    imprimir_vector("Vector solución x", vector_x)
    _, es_correcta = verificar_solucion(matriz_a, vector_x, vector_b)
    print(f"\n{MENSAJE_COMPROBACION_EXITOSA}" if es_correcta else "\nA · x != b ✗")


def mostrar_menu() -> None:
    """Imprime las opciones del menú interno del módulo."""
    print("\n  0. Ver Teoremas Clave")
    print("  1. Regla de Cramer (solución de Ax = b)")
    print(f"  {OPCION_VOLVER}. Volver al menú principal")


# Opción del menú -> función que la atiende (mismo patrón que MODULOS en main.py).
ACCIONES = {
    "0": mostrar_teoremas,
    "1": opcion_cramer,
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
