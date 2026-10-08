"""Módulo III – Álgebra de Matrices de la Calculadora de Álgebra Lineal (Programa 5).

Implementa suma, resta, producto por escalar, producto matricial, transposición,
determinante (cofactores, Sarrus y reducción triangular) e inversa (Gauss-Jordan
y adjunta) usando solo listas anidadas y fractions.Fraction (aritmética exacta).
Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

from fractions import Fraction
from typing import Callable, List, Optional, Tuple

# El formato de fracciones, la lectura de enteros y la reducción de Gauss-Jordan
# ya existen en el módulo de vectores: se reutilizan en lugar de duplicarlos.
from modulos.modulo_vectores import (
    _copiar_matriz as copiar_matriz,
    _factor_por_fila as factor_por_fila,
    _formatear_fraccion as formatear_fraccion,
    _leer_entero as leer_entero,
    _subindice as subindice,
    escalonar,
)
from teoremas.resumen_teoremas import TEOREMAS

Matriz = List[List[Fraction]]
Dimension = Tuple[int, int]

NUMERO_MODULO: int = 3
OPCION_VOLVER: str = "10"

_SUPERINDICES = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

ARTE_ASCII: str = (
    "[A][B] MÓDULO: ÁLGEBRA DE MATRICES\n"
    "[C][D] Operaciones, Traspuesta y Matriz Inversa"
)


def dimension(matriz: Matriz) -> Dimension:
    """Devuelve la dimensión (filas, columnas) de la matriz recibida."""
    return len(matriz), len(matriz[0])


def texto_dimension(dimension_matriz: Dimension) -> str:
    """Escribe una dimensión (filas, columnas) como texto 'm×n'."""
    return f"{dimension_matriz[0]}×{dimension_matriz[1]}"


def matriz_identidad(orden: int) -> Matriz:
    """Devuelve la matriz identidad Iₙ del orden recibido."""
    identidad = []
    for fila in range(orden):
        fila_identidad = []
        for columna in range(orden):
            fila_identidad.append(Fraction(1) if fila == columna else Fraction(0))
        identidad.append(fila_identidad)
    return identidad


def validar_misma_dimension(dimension_a: Dimension, dimension_b: Dimension) -> None:
    """Lanza ValueError si A y B no tienen la misma dimensión (requisito de suma y resta)."""
    if dimension_a != dimension_b:
        raise ValueError(
            f"No se puede sumar ni restar: A es {texto_dimension(dimension_a)} y B es "
            f"{texto_dimension(dimension_b)}; ambas deben tener la misma dimensión."
        )


def validar_producto(dimension_a: Dimension, dimension_b: Dimension) -> None:
    """Lanza ValueError si las columnas de A no coinciden con las filas de B."""
    columnas_a, filas_b = dimension_a[1], dimension_b[0]
    # Cada entrada de A·B empareja una fila de A con una columna de B: deben medir lo mismo.
    if columnas_a != filas_b:
        raise ValueError(
            f"No se puede multiplicar: Columnas de A [{columnas_a}] ≠ Filas de B [{filas_b}]"
        )


def validar_cuadrada(matriz: Matriz) -> None:
    """Lanza ValueError si la matriz no es cuadrada (requisito de determinante e inversa)."""
    filas, columnas = dimension(matriz)
    if filas != columnas:
        raise ValueError(
            f"Se requiere una matriz cuadrada: se recibió una de {filas}×{columnas}."
        )


def sumar_matrices(matriz_a: Matriz, matriz_b: Matriz) -> Matriz:
    """Devuelve A + B sumando entrada por entrada dos matrices de igual dimensión."""
    validar_misma_dimension(dimension(matriz_a), dimension(matriz_b))
    filas, columnas = dimension(matriz_a)
    suma = []
    for fila in range(filas):
        fila_suma = []
        for columna in range(columnas):
            fila_suma.append(matriz_a[fila][columna] + matriz_b[fila][columna])
        suma.append(fila_suma)
    return suma


def multiplicar_por_escalar(escalar: Fraction, matriz: Matriz) -> Matriz:
    """Devuelve k·A multiplicando cada entrada de la matriz por el escalar."""
    filas, columnas = dimension(matriz)
    producto = []
    for fila in range(filas):
        fila_producto = []
        for columna in range(columnas):
            fila_producto.append(escalar * matriz[fila][columna])
        producto.append(fila_producto)
    return producto


def restar_matrices(matriz_a: Matriz, matriz_b: Matriz) -> Matriz:
    """Devuelve A − B para dos matrices de igual dimensión."""
    # A − B = A + (−1)·B: así la resta reutiliza la suma y el producto por escalar.
    return sumar_matrices(matriz_a, multiplicar_por_escalar(Fraction(-1), matriz_b))


def multiplicar_matrices(matriz_a: Matriz, matriz_b: Matriz) -> Matriz:
    """Devuelve A·B (m×p) a partir de A (m×n) y B (n×p) con el producto fila por columna."""
    validar_producto(dimension(matriz_a), dimension(matriz_b))
    filas_a, columnas_a = dimension(matriz_a)
    columnas_b = len(matriz_b[0])
    producto = []
    for fila in range(filas_a):
        fila_producto = []
        for columna in range(columnas_b):
            entrada = Fraction(0)
            for indice in range(columnas_a):
                entrada += matriz_a[fila][indice] * matriz_b[indice][columna]
            fila_producto.append(entrada)
        producto.append(fila_producto)
    return producto


def transponer(matriz: Matriz) -> Matriz:
    """Devuelve Aᵀ: la fila i de la matriz pasa a ser la columna i del resultado."""
    filas, columnas = dimension(matriz)
    transpuesta = []
    for columna in range(columnas):
        fila_transpuesta = []
        for fila in range(filas):
            fila_transpuesta.append(matriz[fila][columna])
        transpuesta.append(fila_transpuesta)
    return transpuesta


def intercambiar_filas(matriz: Matriz, fila_a: int, fila_b: int) -> Matriz:
    """Devuelve una copia de la matriz con las dos filas indicadas intercambiadas."""
    resultado = copiar_matriz(matriz)
    resultado[fila_a], resultado[fila_b] = resultado[fila_b], resultado[fila_a]
    return resultado


def escalar_fila(matriz: Matriz, fila: int, factor: Fraction) -> Matriz:
    """Devuelve una copia de la matriz con la fila indicada multiplicada por el factor."""
    resultado = copiar_matriz(matriz)
    for columna in range(len(matriz[fila])):
        resultado[fila][columna] = factor * matriz[fila][columna]
    return resultado


def reemplazar_fila(
    matriz: Matriz, fila_destino: int, factor: Fraction, fila_origen: int
) -> Matriz:
    """Devuelve una copia de la matriz tras el reemplazo Fᵢ → Fᵢ + k·Fⱼ (i destino, j origen)."""
    resultado = copiar_matriz(matriz)
    for columna in range(len(matriz[fila_destino])):
        resultado[fila_destino][columna] += factor * matriz[fila_origen][columna]
    return resultado


def describir_intercambio(fila_a: int, fila_b: int) -> str:
    """Devuelve el texto 'Fᵢ ↔ Fⱼ' del intercambio (filas en base 0)."""
    return f"F{subindice(fila_a)} ↔ F{subindice(fila_b)}"


def describir_reemplazo(fila_destino: int, factor: Fraction, fila_origen: int) -> str:
    """Devuelve el texto 'Fᵢ → Fᵢ ± k·Fⱼ' del reemplazo (filas en base 0)."""
    signo = "+" if factor >= 0 else "-"
    destino = f"F{subindice(fila_destino)}"
    return f"{destino} → {destino} {signo} {factor_por_fila(factor, fila_origen)}"


def describir_escalamiento(fila: int, factor: Fraction) -> str:
    """Devuelve el texto 'Fᵢ → (k)·Fᵢ' del escalamiento (fila en base 0)."""
    return f"F{subindice(fila)} → ({formatear_fraccion(factor)})·F{subindice(fila)}"


def submatriz_menor(matriz: Matriz, fila_eliminada: int, columna_eliminada: int) -> Matriz:
    """Devuelve el menor Mᵢⱼ: la matriz sin la fila ni la columna indicadas."""
    menor = []
    for fila in range(len(matriz)):
        if fila == fila_eliminada:
            continue
        fila_menor = []
        for columna in range(len(matriz[fila])):
            if columna != columna_eliminada:
                fila_menor.append(matriz[fila][columna])
        menor.append(fila_menor)
    return menor


def cofactor_con_menor(
    matriz: Matriz, fila: int, columna: int
) -> Tuple[Matriz, Fraction, Fraction]:
    """Devuelve (Mᵢⱼ, det(Mᵢⱼ), Cᵢⱼ): el menor, su determinante y el cofactor de la posición."""
    menor = submatriz_menor(matriz, fila, columna)
    # El menor de una matriz 1×1 queda vacío; su determinante vale 1 para que adj([a]) = [1].
    determinante_menor = determinante_por_cofactores(menor) if menor else Fraction(1)
    # El signo (-1)**(fila + columna) sigue el patrón de cofactores: alterna como un tablero.
    return menor, determinante_menor, (-1) ** (fila + columna) * determinante_menor


def cofactor(matriz: Matriz, fila: int, columna: int) -> Fraction:
    """Devuelve el cofactor Cᵢⱼ = (−1)^(i+j)·det(Mᵢⱼ) de la posición indicada."""
    return cofactor_con_menor(matriz, fila, columna)[2]


def determinante_por_cofactores(matriz: Matriz) -> Fraction:
    """Devuelve det(A) por expansión recursiva de cofactores sobre la primera fila.

    Vale para cualquier n, pero cuesta ≈ n! multiplicaciones; el método eficiente
    es determinante_por_reduccion, que solo necesita ≈ n³ operaciones.
    """
    validar_cuadrada(matriz)
    if len(matriz) == 1:
        return matriz[0][0]
    determinante = Fraction(0)
    for columna in range(len(matriz)):
        determinante += matriz[0][columna] * cofactor(matriz, 0, columna)
    return determinante


def sumas_de_sarrus(matriz: Matriz) -> Tuple[Fraction, Fraction]:
    """Devuelve (suma de diagonales descendentes, suma de ascendentes) de una matriz 3×3."""
    if dimension(matriz) != (3, 3):
        raise ValueError("La regla de Sarrus solo se aplica a matrices 3×3.")
    suma_descendentes = Fraction(0)
    suma_ascendentes = Fraction(0)
    for desplazamiento in range(3):
        producto_descendente = Fraction(1)
        producto_ascendente = Fraction(1)
        for fila in range(3):
            # El índice módulo 3 equivale a copiar las dos primeras columnas a la derecha.
            columna = (fila + desplazamiento) % 3
            producto_descendente *= matriz[fila][columna]
            producto_ascendente *= matriz[2 - fila][columna]
        suma_descendentes += producto_descendente
        suma_ascendentes += producto_ascendente
    return suma_descendentes, suma_ascendentes


def determinante_por_sarrus(matriz: Matriz) -> Fraction:
    """Devuelve det(A) de una matriz 3×3 con la regla de Sarrus."""
    suma_descendentes, suma_ascendentes = sumas_de_sarrus(matriz)
    return suma_descendentes - suma_ascendentes


def buscar_fila_con_pivote(matriz: Matriz, columna: int) -> Optional[int]:
    """Devuelve la primera fila, de la diagonal hacia abajo, con entrada no nula en la columna.

    Devuelve None si la columna vale 0 desde la diagonal hasta la última fila.
    """
    for fila in range(columna, len(matriz)):
        if matriz[fila][columna] != 0:
            return fila
    return None


def eliminar_debajo_del_pivote(
    matriz: Matriz, fila_pivote: int, historial: Optional[list] = None
) -> Tuple[Matriz, List[Fraction], List[str]]:
    """Anula la columna del pivote por debajo de él con reemplazos Fᵢ → Fᵢ − k·Fₚ.

    Recibe la matriz y la posición diagonal del pivote; devuelve
    (matriz, factores k usados, operaciones en texto). Si se da `historial`,
    guarda en él la matriz tras cada reemplazo.
    """
    resultado = copiar_matriz(matriz)
    factores: List[Fraction] = []
    operaciones: List[str] = []
    pivote = resultado[fila_pivote][fila_pivote]
    for fila in range(fila_pivote + 1, len(resultado)):
        factor = resultado[fila][fila_pivote] / pivote
        if factor == 0:
            continue
        resultado = reemplazar_fila(resultado, fila, -factor, fila_pivote)
        factores.append(factor)
        operaciones.append(describir_reemplazo(fila, -factor, fila_pivote))
        if historial is not None:
            historial.append(("eliminacion", fila_pivote, resultado))
    return resultado, factores, operaciones


def reducir_a_triangular(
    matriz: Matriz, historial: Optional[list] = None
) -> Tuple[Matriz, int, List[Fraction], List[str]]:
    """Reduce una matriz cuadrada a triangular superior con intercambios y reemplazos.

    Devuelve (triangular, num_intercambios, factores, operaciones): los factores k de
    cada reemplazo Fᵢ → Fᵢ − k·Fⱼ y el registro en texto de las operaciones aplicadas.
    Si se da `historial`, guarda (tipo, columna, matriz) tras cada operación, igual que
    escalonar(); lo usa el paso a paso de la web.
    """
    validar_cuadrada(matriz)
    triangular = copiar_matriz(matriz)
    num_intercambios = 0
    factores: List[Fraction] = []
    operaciones: List[str] = []
    for columna in range(len(triangular)):
        fila_pivote = buscar_fila_con_pivote(triangular, columna)
        # Columna sin pivote: la diagonal queda en 0 y el determinante será 0.
        if fila_pivote is None:
            continue
        # Se intercambian filas si el pivote es 0: sin pivote no se puede eliminar la columna.
        if fila_pivote != columna:
            triangular = intercambiar_filas(triangular, columna, fila_pivote)
            num_intercambios += 1
            operaciones.append(describir_intercambio(columna, fila_pivote))
            if historial is not None:
                historial.append(("intercambio", columna, triangular))
        triangular, factores_nuevos, pasos_nuevos = eliminar_debajo_del_pivote(
            triangular, columna, historial
        )
        factores.extend(factores_nuevos)
        operaciones.extend(pasos_nuevos)
    return triangular, num_intercambios, factores, operaciones


def producto_diagonal(matriz: Matriz) -> Fraction:
    """Devuelve el producto de las entradas de la diagonal principal."""
    producto = Fraction(1)
    for indice in range(len(matriz)):
        producto *= matriz[indice][indice]
    return producto


def determinante_desde_triangular(triangular: Matriz, num_intercambios: int) -> Fraction:
    """Devuelve det(A) a partir de su forma triangular y del número de intercambios hechos."""
    # Cada intercambio cambia el signo del determinante; los reemplazos no lo alteran.
    signo = (-1) ** num_intercambios
    return signo * producto_diagonal(triangular)


def determinante_por_reduccion(matriz: Matriz) -> Fraction:
    """Devuelve det(A) reduciendo a forma triangular: el método eficiente (≈ n³ operaciones)."""
    triangular, num_intercambios, _, _ = reducir_a_triangular(matriz)
    return determinante_desde_triangular(triangular, num_intercambios)


def contar_pivotes(matriz: Matriz) -> int:
    """Devuelve el número de posiciones pivote de la matriz."""
    filas, columnas = dimension(matriz)
    _, _, columnas_pivote = escalonar(matriz, filas, columnas)
    return len(columnas_pivote)


def diagnostico_invertibilidad(matriz: Matriz) -> str:
    """Devuelve el diagnóstico textual de una matriz cuadrada: invertible o singular."""
    orden = len(matriz)
    if determinante_por_reduccion(matriz) == 0:
        return "La matriz es singular (no tiene inversa): det(A) = 0"
    return (
        f"La matriz es invertible: det(A) ≠ 0, tiene {orden} posiciones pivote, "
        f"sus columnas son L.I. y generan ℝ{str(orden).translate(_SUPERINDICES)}"
    )


def construir_aumentada_con_identidad(matriz: Matriz) -> Matriz:
    """Devuelve la matriz aumentada [A | I] de tamaño n × 2n."""
    identidad = matriz_identidad(len(matriz))
    return [matriz[fila] + identidad[fila] for fila in range(len(matriz))]


def invertir_por_gauss_jordan(
    matriz: Matriz, historial: Optional[list] = None
) -> Tuple[Optional[Matriz], Matriz, List[str], int]:
    """Reduce [A | I] por Gauss-Jordan hasta [I | A⁻¹].

    Devuelve (inversa, aumentada_reducida, operaciones, num_pivotes); la inversa es
    None cuando A es singular. Si se da `historial`, escalonar() guarda en él la matriz
    tras cada operación (lo usa la web para el paso a paso; la consola no).
    """
    validar_cuadrada(matriz)
    orden = len(matriz)
    aumentada = construir_aumentada_con_identidad(matriz)
    # escalonar() solo busca pivotes en las n columnas de A; el bloque I recibe las mismas
    # operaciones de fila y por eso termina convertido en A⁻¹.
    reducida, operaciones, columnas_pivote = escalonar(aumentada, orden, orden, historial)
    num_pivotes = len(columnas_pivote)
    # Sin n pivotes la matriz es singular: el bloque izquierdo no llega a I y se detiene aquí.
    if num_pivotes < orden:
        return None, reducida, operaciones, num_pivotes
    inversa = [fila[orden:] for fila in reducida]
    return inversa, reducida, operaciones, num_pivotes


def matriz_de_cofactores(matriz: Matriz) -> Matriz:
    """Devuelve la matriz C formada por los cofactores Cᵢⱼ de una matriz cuadrada."""
    validar_cuadrada(matriz)
    orden = len(matriz)
    cofactores = []
    for fila in range(orden):
        fila_cofactores = []
        for columna in range(orden):
            fila_cofactores.append(cofactor(matriz, fila, columna))
        cofactores.append(fila_cofactores)
    return cofactores


def matriz_adjunta(matriz: Matriz) -> Matriz:
    """Devuelve adj(A): la transpuesta de la matriz de cofactores."""
    return transponer(matriz_de_cofactores(matriz))


def invertir_por_adjunta(matriz: Matriz) -> Tuple[Optional[Matriz], Matriz, Fraction]:
    """Calcula A⁻¹ = (1/det A)·adj(A).

    Devuelve (inversa, adjunta, determinante); la inversa es None si det(A) = 0.
    """
    determinante = determinante_por_cofactores(matriz)
    adjunta = matriz_adjunta(matriz)
    # Solo se divide entre det(A) si es distinto de 0: una matriz singular no tiene inversa.
    if determinante == 0:
        return None, adjunta, determinante
    inversa = multiplicar_por_escalar(Fraction(1) / determinante, adjunta)
    return inversa, adjunta, determinante


def verificar_inversa(matriz: Matriz, inversa: Matriz) -> Tuple[Matriz, bool]:
    """Devuelve (A·A⁻¹, es_identidad) usando el producto matricial del propio módulo."""
    producto = multiplicar_matrices(matriz, inversa)
    # Con Fraction la comparación con I es exacta: no hace falta tolerancia de redondeo.
    return producto, producto == matriz_identidad(len(matriz))


def calcular_inversa(matriz: Matriz) -> Optional[Matriz]:
    """Devuelve A⁻¹ por Gauss-Jordan, o None si la matriz es singular."""
    return invertir_por_gauss_jordan(matriz)[0]


def miembros_inversa_de_la_inversa(matriz_a: Matriz) -> Tuple[Matriz, Matriz]:
    """Devuelve los dos miembros de (A⁻¹)⁻¹ = A para una matriz invertible."""
    return calcular_inversa(calcular_inversa(matriz_a)), matriz_a


def miembros_inversa_del_producto(matriz_a: Matriz, matriz_b: Matriz) -> Tuple[Matriz, Matriz]:
    """Devuelve los dos miembros de (AB)⁻¹ = B⁻¹A⁻¹ para A y B invertibles."""
    miembro_izquierdo = calcular_inversa(multiplicar_matrices(matriz_a, matriz_b))
    # El orden se invierte: para deshacer "primero B, luego A" se deshace A y después B.
    miembro_derecho = multiplicar_matrices(calcular_inversa(matriz_b), calcular_inversa(matriz_a))
    return miembro_izquierdo, miembro_derecho


def miembros_inversa_de_la_transpuesta(matriz_a: Matriz) -> Tuple[Matriz, Matriz]:
    """Devuelve los dos miembros de (Aᵀ)⁻¹ = (A⁻¹)ᵀ para una matriz invertible."""
    return calcular_inversa(transponer(matriz_a)), transponer(calcular_inversa(matriz_a))


def miembros_determinante_de_la_inversa(matriz_a: Matriz) -> Tuple[Fraction, Fraction]:
    """Devuelve los dos miembros de det(A⁻¹) = 1/det(A) para una matriz invertible."""
    determinante = determinante_por_reduccion(matriz_a)
    return determinante_por_reduccion(calcular_inversa(matriz_a)), Fraction(1) / determinante


def miembros_determinante_del_producto(
    matriz_a: Matriz, matriz_b: Matriz
) -> Tuple[Fraction, Fraction]:
    """Devuelve los dos miembros de det(AB) = det(A)·det(B) para A y B de orden n."""
    # Vale para cualquier par n×n: si A o B es singular, ambos miembros dan 0.
    miembro_izquierdo = determinante_por_reduccion(multiplicar_matrices(matriz_a, matriz_b))
    miembro_derecho = determinante_por_reduccion(matriz_a) * determinante_por_reduccion(matriz_b)
    return miembro_izquierdo, miembro_derecho


def efecto_de_intercambio(
    matriz: Matriz, fila_i: int, fila_j: int
) -> Tuple[Matriz, Fraction, Fraction]:
    """Intercambia dos filas; devuelve (matriz modificada, su det, −det(A) esperado)."""
    modificada = intercambiar_filas(matriz, fila_i, fila_j)
    esperado = -determinante_por_cofactores(matriz)
    return modificada, determinante_por_cofactores(modificada), esperado


def efecto_de_reemplazo(
    matriz: Matriz, fila_i: int, factor: Fraction, fila_j: int
) -> Tuple[Matriz, Fraction, Fraction]:
    """Aplica Fᵢ → Fᵢ + k·Fⱼ; devuelve (matriz modificada, su det, det(A) esperado)."""
    modificada = reemplazar_fila(matriz, fila_i, factor, fila_j)
    esperado = determinante_por_cofactores(matriz)
    return modificada, determinante_por_cofactores(modificada), esperado


def efecto_de_escalamiento(
    matriz: Matriz, fila_i: int, factor: Fraction
) -> Tuple[Matriz, Fraction, Fraction]:
    """Multiplica una fila por k; devuelve (matriz modificada, su det, k·det(A) esperado)."""
    modificada = escalar_fila(matriz, fila_i, factor)
    esperado = factor * determinante_por_cofactores(matriz)
    return modificada, determinante_por_cofactores(modificada), esperado


def conclusion(se_cumple: bool) -> str:
    """Devuelve el veredicto «Se cumple» o «No se cumple» de una propiedad."""
    return "«Se cumple»" if se_cumple else "«No se cumple»"


def formatear_matriz(matriz: Matriz, columna_division: Optional[int] = None) -> List[str]:
    """Devuelve las líneas de texto de la matriz con las columnas alineadas a la derecha.

    Si se indica columna_division, se dibuja antes de ella la barra │ de una aumentada.
    """
    textos = [[formatear_fraccion(valor) for valor in fila] for fila in matriz]
    anchos = [max(len(fila[columna]) for fila in textos) for columna in range(len(textos[0]))]
    lineas = []
    for fila in textos:
        celdas = [fila[columna].rjust(anchos[columna]) for columna in range(len(fila))]
        if columna_division is not None:
            celdas.insert(columna_division, "│")
        lineas.append("  [ " + "  ".join(celdas) + " ]")
    return lineas


def imprimir_matriz(titulo: str, matriz: Matriz, columna_division: Optional[int] = None) -> None:
    """Imprime el título con la dimensión de la matriz y después sus filas alineadas."""
    print(f"\n{titulo} ({texto_dimension(dimension(matriz))}):")
    for linea in formatear_matriz(matriz, columna_division):
        print(linea)


def leer_fraccion(mensaje: str) -> Fraction:
    """Pide un número (entero, decimal o fracción) hasta que sea válido; devuelve Fraction."""
    while True:
        texto = input(mensaje).strip()
        try:
            return Fraction(texto)
        # ZeroDivisionError cubre las fracciones con denominador 0, como "1/0".
        except (ValueError, ZeroDivisionError):
            print(f"  ✗ '{texto}' no es un número válido. Use p. ej. -3, 2.5 o 1/2.")


def leer_fila(numero_fila: int, columnas: int) -> List[Fraction]:
    """Pide en una línea los valores de una fila y los devuelve como lista de Fraction."""
    while True:
        textos = input(f"  Fila {numero_fila}: ").replace(",", " ").split()
        if len(textos) != columnas:
            print(f"  ✗ Se esperaban {columnas} valores y se recibieron {len(textos)}.")
            continue
        try:
            return [Fraction(texto) for texto in textos]
        except (ValueError, ZeroDivisionError):
            print("  ✗ Valor inválido. Use enteros, decimales o fracciones (p. ej. -3, 2.5, 1/2).")


def leer_dimensiones(nombre: str) -> Dimension:
    """Pide el número de filas y de columnas de una matriz; devuelve (filas, columnas)."""
    filas = leer_entero(f"Filas de {nombre} (m): ")
    columnas = leer_entero(f"Columnas de {nombre} (n): ")
    return filas, columnas


def leer_matriz(nombre: str, dimension_matriz: Dimension) -> Matriz:
    """Lee fila por fila los elementos de una matriz de la dimensión indicada."""
    filas, columnas = dimension_matriz
    print(f"\nElementos de {nombre} ({filas}×{columnas}), separados por espacios:")
    return [leer_fila(numero_fila, columnas) for numero_fila in range(1, filas + 1)]


def leer_matriz_cuadrada(nombre: str) -> Matriz:
    """Pide solo el orden n y lee una matriz cuadrada n×n."""
    orden = leer_entero(f"Orden de {nombre} (n): ")
    return leer_matriz(nombre, (orden, orden))


def leer_dos_matrices(
    validar_dimensiones: Callable[[Dimension, Dimension], None]
) -> Optional[Tuple[Matriz, Matriz]]:
    """Lee A y B; devuelve None si sus dimensiones no admiten la operación.

    Recibe la función que valida las dimensiones y la aplica antes de pedir los elementos.
    """
    dimension_a = leer_dimensiones("A")
    dimension_b = leer_dimensiones("B")
    # Se valida antes de leer los elementos: no tiene sentido teclear matrices incompatibles.
    try:
        validar_dimensiones(dimension_a, dimension_b)
    except ValueError as error:
        print(f"  ✗ {error}")
        return None
    return leer_matriz("A", dimension_a), leer_matriz("B", dimension_b)


def leer_matriz_invertible(nombre: str, orden: int) -> Matriz:
    """Lee una matriz n×n y la vuelve a pedir mientras sea singular."""
    while True:
        matriz = leer_matriz(nombre, (orden, orden))
        if determinante_por_reduccion(matriz) != 0:
            return matriz
        print(f"  ✗ {nombre} es singular (det({nombre}) = 0): ingrese una matriz invertible.")


def leer_indice_de_fila(mensaje: str, orden: int) -> int:
    """Pide un número de fila entre 1 y n hasta que sea válido; devuelve el índice en base 0."""
    while True:
        texto = input(mensaje).strip()
        try:
            numero_fila = int(texto)
        except ValueError:
            numero_fila = 0
        if 1 <= numero_fila <= orden:
            return numero_fila - 1
        print(f"  ✗ '{texto}' no es una fila válida: escriba un entero entre 1 y {orden}.")


def leer_dos_filas_distintas(orden: int) -> Tuple[int, int]:
    """Pide dos filas distintas i y j; devuelve sus índices en base 0."""
    fila_i = leer_indice_de_fila("   Fila i: ", orden)
    while True:
        fila_j = leer_indice_de_fila("   Fila j (distinta de i): ", orden)
        if fila_j != fila_i:
            return fila_i, fila_j
        print("  ✗ Las dos filas deben ser distintas.")


def leer_factor_no_nulo(mensaje: str) -> Fraction:
    """Pide un factor k hasta que sea distinto de 0 y lo devuelve como Fraction."""
    while True:
        factor = leer_fraccion(mensaje)
        if factor != 0:
            return factor
        # Multiplicar una fila por 0 no es una operación elemental: destruye la fila.
        print("  ✗ k debe ser distinto de 0 para escalar una fila.")


def mostrar_operaciones(operaciones: List[str]) -> None:
    """Imprime numerada la lista de operaciones elementales aplicadas."""
    print("\nOperaciones elementales aplicadas:")
    if not operaciones:
        print("  (ninguna: la matriz ya estaba reducida)")
    for numero, operacion in enumerate(operaciones, start=1):
        print(f"  {numero}. {operacion}")


def mostrar_diagnostico(matriz: Matriz) -> None:
    """Imprime el diagnóstico de invertibilidad; si A es singular indica sus pivotes."""
    print(f"\nDiagnóstico: {diagnostico_invertibilidad(matriz)}")
    num_pivotes = contar_pivotes(matriz)
    if num_pivotes < len(matriz):
        print(f"Solo tiene {num_pivotes} de {len(matriz)} posiciones pivote: no existe A⁻¹.")


def mostrar_resultado_inversa(matriz: Matriz, inversa: Optional[Matriz]) -> None:
    """Imprime A⁻¹ con la comprobación A·A⁻¹ = I (si existe) y el diagnóstico de A."""
    if inversa is not None:
        imprimir_matriz("A⁻¹", inversa)
        producto, es_identidad = verificar_inversa(matriz, inversa)
        imprimir_matriz("Comprobación A·A⁻¹", producto)
        print("A·A⁻¹ = I ✓ (igualdad exacta)" if es_identidad else "A·A⁻¹ ≠ I ✗")
    mostrar_diagnostico(matriz)


def mostrar_conmutatividad(matriz_a: Matriz, matriz_b: Matriz, producto_ab: Matriz) -> None:
    """Imprime B·A cuando está definido e indica si coincide con A·B."""
    if dimension(matriz_b)[1] != dimension(matriz_a)[0]:
        print("\nB·A no está definido: el producto matricial no es conmutativo.")
        return
    producto_ba = multiplicar_matrices(matriz_b, matriz_a)
    imprimir_matriz("En el otro orden, B·A", producto_ba)
    if producto_ab == producto_ba:
        print("En este caso A·B = B·A.")
    else:
        print("A·B ≠ B·A: el producto matricial no es conmutativo.")


def mostrar_determinante_por_cofactores(matriz: Matriz) -> Fraction:
    """Imprime la expansión por cofactores sobre la fila 1 y devuelve det(A)."""
    terminos = []
    for columna in range(len(matriz)):
        entrada = formatear_fraccion(matriz[0][columna])
        valor_cofactor = formatear_fraccion(cofactor(matriz, 0, columna))
        terminos.append(f"({entrada})·({valor_cofactor})")
    determinante = determinante_por_cofactores(matriz)
    print("   det(A) = Σ a₁ⱼ·C₁ⱼ (entrada de la fila 1 por su cofactor)")
    print(f"   det(A) = {' + '.join(terminos)} = {formatear_fraccion(determinante)}")
    return determinante


def mostrar_determinante_por_sarrus(matriz: Matriz) -> Fraction:
    """Imprime las dos sumas de la regla de Sarrus de una matriz 3×3 y devuelve det(A)."""
    suma_descendentes, suma_ascendentes = sumas_de_sarrus(matriz)
    determinante = determinante_por_sarrus(matriz)
    print(f"   Diagonales descendentes (↘): {formatear_fraccion(suma_descendentes)}")
    print(f"   Diagonales ascendentes  (↗): {formatear_fraccion(suma_ascendentes)}")
    print(
        f"   det(A) = ({formatear_fraccion(suma_descendentes)}) − "
        f"({formatear_fraccion(suma_ascendentes)}) = {formatear_fraccion(determinante)}"
    )
    return determinante


def mostrar_determinante_por_reduccion(matriz: Matriz) -> Fraction:
    """Imprime la reducción a triangular (operaciones, diagonal y corrección) y devuelve det(A)."""
    triangular, num_intercambios, factores, operaciones = reducir_a_triangular(matriz)
    determinante = determinante_desde_triangular(triangular, num_intercambios)
    mostrar_operaciones(operaciones)
    imprimir_matriz("Matriz triangular", triangular)
    diagonal = [f"({formatear_fraccion(fila[indice])})" for indice, fila in enumerate(triangular)]
    producto = formatear_fraccion(producto_diagonal(triangular))
    signo = "+1" if num_intercambios % 2 == 0 else "−1"
    lista_factores = ", ".join(formatear_fraccion(factor) for factor in factores) or "ninguno"
    print(f"Producto de la diagonal: {'·'.join(diagonal)} = {producto}")
    print(f"Intercambios de fila: {num_intercambios} → signo {signo}")
    print(f"Factores de los reemplazos: {lista_factores} (un reemplazo no altera det)")
    print(f"det(A) = ({signo})·({producto}) = {formatear_fraccion(determinante)}")
    return determinante


def mostrar_igualdad_matricial(
    nombre_izquierdo: str, nombre_derecho: str, miembros: Tuple[Matriz, Matriz]
) -> None:
    """Imprime los dos miembros (matrices) de una igualdad y concluye si se cumple."""
    miembro_izquierdo, miembro_derecho = miembros
    imprimir_matriz(f"Miembro izquierdo {nombre_izquierdo}", miembro_izquierdo)
    imprimir_matriz(f"Miembro derecho {nombre_derecho}", miembro_derecho)
    print(f"Conclusión: {conclusion(miembro_izquierdo == miembro_derecho)}")


def mostrar_igualdad_escalar(
    nombre_izquierdo: str, nombre_derecho: str, miembros: Tuple[Fraction, Fraction]
) -> None:
    """Imprime los dos miembros (números) de una igualdad y concluye si se cumple."""
    miembro_izquierdo, miembro_derecho = miembros
    print(f"   {nombre_izquierdo} = {formatear_fraccion(miembro_izquierdo)}")
    print(f"   {nombre_derecho} = {formatear_fraccion(miembro_derecho)}")
    print(f"   Conclusión: {conclusion(miembro_izquierdo == miembro_derecho)}")


def verificar_propiedades_de_la_inversa(matriz_a: Matriz, matriz_b: Matriz) -> None:
    """Propiedades 1 a 4: imprime ambos miembros de cada igualdad y su conclusión."""
    print("\n1. (A⁻¹)⁻¹ = A")
    mostrar_igualdad_matricial("(A⁻¹)⁻¹", "A", miembros_inversa_de_la_inversa(matriz_a))
    print("\n2. (AB)⁻¹ = B⁻¹A⁻¹")
    mostrar_igualdad_matricial(
        "(AB)⁻¹", "B⁻¹A⁻¹", miembros_inversa_del_producto(matriz_a, matriz_b)
    )
    print("\n3. (Aᵀ)⁻¹ = (A⁻¹)ᵀ")
    mostrar_igualdad_matricial(
        "(Aᵀ)⁻¹", "(A⁻¹)ᵀ", miembros_inversa_de_la_transpuesta(matriz_a)
    )
    print("\n4. det(A⁻¹) = 1/det(A)")
    print(f"   det(A) = {formatear_fraccion(determinante_por_reduccion(matriz_a))}")
    mostrar_igualdad_escalar(
        "det(A⁻¹)", "1/det(A)", miembros_determinante_de_la_inversa(matriz_a)
    )


def verificar_intercambio(matriz: Matriz) -> None:
    """Propiedad 5a: intercambia dos filas elegidas y comprueba que det cambia de signo."""
    print("\n   a) Intercambio Fᵢ ↔ Fⱼ: el determinante cambia de signo")
    fila_i, fila_j = leer_dos_filas_distintas(len(matriz))
    modificada, obtenido, esperado = efecto_de_intercambio(matriz, fila_i, fila_j)
    imprimir_matriz(f"A tras {describir_intercambio(fila_i, fila_j)}", modificada)
    mostrar_igualdad_escalar("det(A modificada)", "−det(A)", (obtenido, esperado))


def verificar_reemplazo(matriz: Matriz) -> None:
    """Propiedad 5b: aplica Fᵢ → Fᵢ + k·Fⱼ y comprueba que det no cambia."""
    print("\n   b) Reemplazo Fᵢ → Fᵢ + k·Fⱼ: el determinante no cambia")
    fila_i, fila_j = leer_dos_filas_distintas(len(matriz))
    factor = leer_fraccion("   Factor k: ")
    modificada, obtenido, esperado = efecto_de_reemplazo(matriz, fila_i, factor, fila_j)
    imprimir_matriz(f"A tras {describir_reemplazo(fila_i, factor, fila_j)}", modificada)
    mostrar_igualdad_escalar("det(A modificada)", "det(A)", (obtenido, esperado))


def verificar_escalamiento(matriz: Matriz) -> None:
    """Propiedad 5c: multiplica una fila por k ≠ 0 y comprueba que det se multiplica por k."""
    print("\n   c) Escalamiento Fᵢ → k·Fᵢ: el determinante se multiplica por k")
    fila_i = leer_indice_de_fila("   Fila i: ", len(matriz))
    factor = leer_factor_no_nulo("   Factor k (≠ 0): ")
    modificada, obtenido, esperado = efecto_de_escalamiento(matriz, fila_i, factor)
    imprimir_matriz(f"A tras {describir_escalamiento(fila_i, factor)}", modificada)
    mostrar_igualdad_escalar("det(A modificada)", "k·det(A)", (obtenido, esperado))


def verificar_operaciones_de_fila(matriz: Matriz) -> None:
    """Propiedad 5: aplica las operaciones de fila que elige el usuario y compara los det."""
    print("\n5. Efecto de las operaciones de fila sobre det(A)")
    print(f"   det(A) = {formatear_fraccion(determinante_por_cofactores(matriz))}")
    # Intercambio y reemplazo necesitan dos filas distintas, que una matriz 1×1 no tiene.
    if len(matriz) >= 2:
        verificar_intercambio(matriz)
        verificar_reemplazo(matriz)
    else:
        print("   Con n = 1 no hay dos filas distintas: se omiten intercambio y reemplazo.")
    verificar_escalamiento(matriz)


def verificar_matriz_triangular(matriz: Matriz) -> None:
    """Propiedad 6: compara det(A) por reducción triangular con la expansión por cofactores."""
    print("\n6. Matriz triangular: det(A) = ± producto de la diagonal")
    por_reduccion = mostrar_determinante_por_reduccion(matriz)
    por_cofactores = determinante_por_cofactores(matriz)
    mostrar_igualdad_escalar(
        "det(A) por reducción triangular", "det(A) por cofactores",
        (por_reduccion, por_cofactores),
    )


def verificar_determinante_del_producto(matriz_a: Matriz, matriz_b: Matriz) -> None:
    """Propiedad 7: muestra AB, det(A) y det(B), y compara det(AB) con det(A)·det(B)."""
    print("\n7. det(AB) = det(A)·det(B)")
    imprimir_matriz("AB", multiplicar_matrices(matriz_a, matriz_b))
    print(f"   det(A) = {formatear_fraccion(determinante_por_reduccion(matriz_a))}")
    print(f"   det(B) = {formatear_fraccion(determinante_por_reduccion(matriz_b))}")
    mostrar_igualdad_escalar(
        "det(AB)", "det(A)·det(B)", miembros_determinante_del_producto(matriz_a, matriz_b)
    )


def mostrar_teoremas() -> None:
    """Opción 0: imprime los teoremas clave del módulo."""
    print("\n── TEOREMAS CLAVE ──")
    print(f"  {TEOREMAS[NUMERO_MODULO]}")


def opcion_suma() -> None:
    """Opción 1: lee A y B de igual dimensión y muestra A + B."""
    print("\n── SUMA A + B ──")
    matrices = leer_dos_matrices(validar_misma_dimension)
    if matrices is not None:
        imprimir_matriz("Resultado A + B", sumar_matrices(matrices[0], matrices[1]))


def opcion_resta() -> None:
    """Opción 2: lee A y B de igual dimensión y muestra A − B."""
    print("\n── RESTA A − B ──")
    matrices = leer_dos_matrices(validar_misma_dimension)
    if matrices is not None:
        imprimir_matriz("Resultado A − B", restar_matrices(matrices[0], matrices[1]))


def opcion_escalar() -> None:
    """Opción 3: lee una matriz A y un escalar k y muestra k·A."""
    print("\n── MULTIPLICACIÓN POR ESCALAR k·A ──")
    matriz = leer_matriz("A", leer_dimensiones("A"))
    escalar = leer_fraccion("Escalar k: ")
    titulo = f"Resultado ({formatear_fraccion(escalar)})·A"
    imprimir_matriz(titulo, multiplicar_por_escalar(escalar, matriz))


def opcion_producto() -> None:
    """Opción 4: lee A (m×n) y B (n×p), muestra A·B y lo compara con B·A."""
    print("\n── PRODUCTO MATRICIAL A·B ──")
    matrices = leer_dos_matrices(validar_producto)
    if matrices is None:
        return
    matriz_a, matriz_b = matrices
    producto_ab = multiplicar_matrices(matriz_a, matriz_b)
    imprimir_matriz("Resultado A·B", producto_ab)
    mostrar_conmutatividad(matriz_a, matriz_b, producto_ab)


def opcion_transposicion() -> None:
    """Opción 5: lee una matriz A y muestra su transpuesta Aᵀ."""
    print("\n── TRANSPOSICIÓN Aᵀ ──")
    matriz = leer_matriz("A", leer_dimensiones("A"))
    imprimir_matriz("Resultado Aᵀ", transponer(matriz))


def opcion_determinante() -> None:
    """Opción 6: calcula det(A) por cofactores, Sarrus (si es 3×3) y reducción, y los compara."""
    print("\n── DETERMINANTE ──")
    matriz = leer_matriz_cuadrada("A")
    imprimir_matriz("A", matriz)
    print("\na) Expansión por cofactores (≈ n! multiplicaciones):")
    determinantes = [mostrar_determinante_por_cofactores(matriz)]
    if len(matriz) == 3:
        print("\nb) Regla de Sarrus (solo para 3×3):")
        determinantes.append(mostrar_determinante_por_sarrus(matriz))
    else:
        print("\nb) Regla de Sarrus: no se aplica, solo vale para matrices 3×3.")
    print("\nc) Reducción a forma triangular (método eficiente, ≈ n³ operaciones):")
    determinantes.append(mostrar_determinante_por_reduccion(matriz))
    if determinantes.count(determinantes[0]) == len(determinantes):
        print(f"\nd) Los métodos coinciden: det(A) = {formatear_fraccion(determinantes[0])} ✓")
    else:
        print("\nd) Los métodos NO coinciden ✗")
    mostrar_diagnostico(matriz)


def opcion_inversa_gauss_jordan() -> None:
    """Opción 7: reduce [A | I] hasta [I | A⁻¹] y comprueba la inversa obtenida."""
    print("\n── INVERSA POR GAUSS-JORDAN ──")
    matriz = leer_matriz_cuadrada("A")
    orden = len(matriz)
    imprimir_matriz("Matriz aumentada [A | I]", construir_aumentada_con_identidad(matriz), orden)
    inversa, reducida, operaciones, num_pivotes = invertir_por_gauss_jordan(matriz)
    mostrar_operaciones(operaciones)
    titulo = "Matriz final [I | A⁻¹]" if inversa is not None else "Reducción detenida antes de I"
    imprimir_matriz(titulo, reducida, orden)
    print(f"\nPosiciones pivote encontradas: {num_pivotes} de {orden}")
    mostrar_resultado_inversa(matriz, inversa)


def opcion_inversa_adjunta() -> None:
    """Opción 8: calcula A⁻¹ = (1/det A)·adj(A) mostrando cofactores, adjunta y determinante."""
    print("\n── INVERSA POR MATRIZ ADJUNTA ──")
    matriz = leer_matriz_cuadrada("A")
    imprimir_matriz("A", matriz)
    inversa, adjunta, determinante = invertir_por_adjunta(matriz)
    # C se recupera como (adj A)ᵀ porque (Cᵀ)ᵀ = C: así no se recalculan los n² cofactores.
    imprimir_matriz("Matriz de cofactores C", transponer(adjunta))
    imprimir_matriz("adj(A) = Cᵀ", adjunta)
    print(f"\ndet(A) = {formatear_fraccion(determinante)}")
    if inversa is not None:
        factor = formatear_fraccion(Fraction(1) / determinante)
        print(f"A⁻¹ = (1/det A)·adj(A) = ({factor})·adj(A)")
    mostrar_resultado_inversa(matriz, inversa)


def opcion_verificador() -> None:
    """Opción 9: verifica las siete propiedades con A y B invertibles del mismo orden."""
    print("\n── VERIFICADOR DE PROPIEDADES ──")
    print("Se piden A y B cuadradas e invertibles del mismo orden n.")
    orden = leer_entero("Orden de A y B (n): ")
    matriz_a = leer_matriz_invertible("A", orden)
    matriz_b = leer_matriz_invertible("B", orden)
    verificar_propiedades_de_la_inversa(matriz_a, matriz_b)
    verificar_operaciones_de_fila(matriz_a)
    verificar_matriz_triangular(matriz_a)
    verificar_determinante_del_producto(matriz_a, matriz_b)


def mostrar_menu() -> None:
    """Imprime las opciones del menú interno del módulo."""
    print("\n  0. Ver Teoremas Clave")
    print("  1. Suma (A + B)")
    print("  2. Resta (A − B)")
    print("  3. Multiplicación por escalar (k·A)")
    print("  4. Producto matricial (A·B)")
    print("  5. Transposición (Aᵀ)")
    print("  6. Determinante")
    print("  7. Inversa por Gauss-Jordan")
    print("  8. Inversa por matriz adjunta")
    print("  9. Verificador de propiedades")
    print(f" {OPCION_VOLVER}. Volver al menú principal")


# Opción del menú -> función que la atiende (mismo patrón que MODULOS en main.py).
ACCIONES = {
    "0": mostrar_teoremas,
    "1": opcion_suma,
    "2": opcion_resta,
    "3": opcion_escalar,
    "4": opcion_producto,
    "5": opcion_transposicion,
    "6": opcion_determinante,
    "7": opcion_inversa_gauss_jordan,
    "8": opcion_inversa_adjunta,
    "9": opcion_verificador,
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
