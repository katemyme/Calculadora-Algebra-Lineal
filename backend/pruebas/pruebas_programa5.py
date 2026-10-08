"""Pruebas del Programa 5 (Módulo III – Álgebra de Matrices), solo con assert.

Comprueban las funciones de cálculo de modulos/modulo_matrices.py con los casos
de prueba del enunciado. Se ejecutan desde backend/:
    python -m pruebas.pruebas_programa5
Integrantes: Grupo X — completar.
"""

import sys
from fractions import Fraction
from pathlib import Path

# El módulo importa "modulos" y "teoremas" de forma relativa a la carpeta programa_4.
RUTA_CALCULADORA = Path(__file__).resolve().parents[1] / "programa_4"
if str(RUTA_CALCULADORA) not in sys.path:
    sys.path.insert(0, str(RUTA_CALCULADORA))

from modulos import modulo_matrices as matrices  # noqa: E402


def a_fracciones(filas_de_texto):
    """Convierte una lista de filas (enteros o textos como '3/2') en una matriz de Fraction."""
    return [[Fraction(valor) for valor in fila] for fila in filas_de_texto]


MATRIZ_2X3 = a_fracciones([[1, 2, 3], [4, 5, 6]])
MATRIZ_3X2 = a_fracciones([[1, 0], [2, 1], [0, 3]])
INVERTIBLE_3X3 = a_fracciones([[1, 2, 3], [0, 1, 4], [5, 6, 0]])
INVERSA_3X3 = a_fracciones([[-24, 18, 5], [20, -15, -4], [-5, 4, 1]])
INVERTIBLE_2X2 = a_fracciones([[1, 2], [3, 4]])
INVERSA_2X2 = a_fracciones([[-2, 1], ["3/2", "-1/2"]])
SINGULAR_3X3 = a_fracciones([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
SEGUNDA_2X2 = a_fracciones([[0, 1], [1, 1]])


def probar_operaciones_basicas():
    """Suma, resta, escalar y transpuesta sobre matrices pequeñas."""
    assert matrices.sumar_matrices(MATRIZ_2X3, MATRIZ_2X3) == a_fracciones([[2, 4, 6], [8, 10, 12]])
    assert matrices.restar_matrices(MATRIZ_2X3, MATRIZ_2X3) == a_fracciones([[0, 0, 0], [0, 0, 0]])
    assert matrices.multiplicar_por_escalar(Fraction(1, 2), INVERTIBLE_2X2) == a_fracciones(
        [["1/2", 1], ["3/2", 2]]
    )
    assert matrices.transponer(MATRIZ_2X3) == a_fracciones([[1, 4], [2, 5], [3, 6]])
    assert matrices.transponer(matrices.transponer(MATRIZ_2X3)) == MATRIZ_2X3


def probar_suma_con_dimensiones_distintas():
    """La suma y la resta rechazan matrices de distinta dimensión con un mensaje claro."""
    for operacion in (matrices.sumar_matrices, matrices.restar_matrices):
        try:
            operacion(MATRIZ_2X3, MATRIZ_3X2)
        except ValueError as error:
            assert "A es 2×3 y B es 3×2" in str(error)
        else:
            assert False, "debía rechazar matrices de distinta dimensión"


def probar_producto_no_conmutativo():
    """A (2×3) · C (3×2) da 2×2, mientras que C·A es 3×3: AC ≠ CA."""
    producto_ac = matrices.multiplicar_matrices(MATRIZ_2X3, MATRIZ_3X2)
    producto_ca = matrices.multiplicar_matrices(MATRIZ_3X2, MATRIZ_2X3)
    assert producto_ac == a_fracciones([[5, 11], [14, 23]])
    assert matrices.dimension(producto_ca) == (3, 3)
    assert producto_ac != producto_ca


def probar_producto_con_dimensiones_incompatibles():
    """A 2×3 por B 2×3 produce exactamente el mensaje pedido en el enunciado."""
    try:
        matrices.multiplicar_matrices(MATRIZ_2X3, MATRIZ_2X3)
    except ValueError as error:
        assert str(error) == "No se puede multiplicar: Columnas de A [3] ≠ Filas de B [2]"
    else:
        assert False, "debía rechazar el producto 2×3 por 2×3"


def probar_determinante_por_los_tres_metodos():
    """Cofactores, Sarrus y reducción triangular dan det = 1 para la matriz 3×3."""
    assert matrices.determinante_por_cofactores(INVERTIBLE_3X3) == 1
    assert matrices.determinante_por_sarrus(INVERTIBLE_3X3) == 1
    assert matrices.determinante_por_reduccion(INVERTIBLE_3X3) == 1
    assert matrices.determinante_por_cofactores(INVERTIBLE_2X2) == -2
    assert matrices.determinante_por_reduccion(INVERTIBLE_2X2) == -2


def probar_inversa_3x3_por_ambos_metodos():
    """Gauss-Jordan y adjunta dan la misma inversa, y A·A⁻¹ = I de forma exacta."""
    por_gauss_jordan, aumentada_final, _, num_pivotes = matrices.invertir_por_gauss_jordan(
        INVERTIBLE_3X3
    )
    por_adjunta, _, determinante = matrices.invertir_por_adjunta(INVERTIBLE_3X3)
    assert por_gauss_jordan == INVERSA_3X3
    assert por_adjunta == INVERSA_3X3
    assert determinante == 1
    assert num_pivotes == 3
    assert [fila[:3] for fila in aumentada_final] == matrices.matriz_identidad(3)
    assert [fila[3:] for fila in aumentada_final] == INVERSA_3X3
    assert matrices.verificar_inversa(INVERTIBLE_3X3, por_gauss_jordan) == (
        matrices.matriz_identidad(3), True
    )


def probar_inversa_2x2_y_adjunta():
    """adj([[1,2],[3,4]]) = [[4,-2],[-3,1]] y la inversa lleva fracciones exactas."""
    por_adjunta, adjunta, determinante = matrices.invertir_por_adjunta(INVERTIBLE_2X2)
    assert adjunta == a_fracciones([[4, -2], [-3, 1]])
    assert matrices.matriz_adjunta(INVERTIBLE_2X2) == adjunta
    assert determinante == -2
    assert por_adjunta == INVERSA_2X2
    assert matrices.calcular_inversa(INVERTIBLE_2X2) == INVERSA_2X2
    assert matrices.verificar_inversa(INVERTIBLE_2X2, por_adjunta)[1] is True


def probar_matriz_singular():
    """det = 0, solo 2 pivotes, diagnóstico de singular y ninguna inversa calculada."""
    assert matrices.determinante_por_cofactores(SINGULAR_3X3) == 0
    assert matrices.determinante_por_sarrus(SINGULAR_3X3) == 0
    assert matrices.determinante_por_reduccion(SINGULAR_3X3) == 0
    assert matrices.contar_pivotes(SINGULAR_3X3) == 2
    inversa, _, _, num_pivotes = matrices.invertir_por_gauss_jordan(SINGULAR_3X3)
    assert inversa is None
    assert num_pivotes == 2
    assert matrices.invertir_por_adjunta(SINGULAR_3X3)[0] is None
    assert matrices.diagnostico_invertibilidad(SINGULAR_3X3) == (
        "La matriz es singular (no tiene inversa): det(A) = 0"
    )


def probar_diagnostico_invertible():
    """El diagnóstico de una matriz invertible usa el n real, también como superíndice."""
    assert matrices.diagnostico_invertibilidad(INVERTIBLE_3X3) == (
        "La matriz es invertible: det(A) ≠ 0, tiene 3 posiciones pivote, "
        "sus columnas son L.I. y generan ℝ³"
    )


def probar_propiedades_de_la_inversa():
    """Propiedades 1 a 4 del verificador con A = [[1,2],[3,4]] y B = [[0,1],[1,1]]."""
    izquierdo, derecho = matrices.miembros_inversa_de_la_inversa(INVERTIBLE_2X2)
    assert izquierdo == derecho == INVERTIBLE_2X2

    izquierdo, derecho = matrices.miembros_inversa_del_producto(INVERTIBLE_2X2, SEGUNDA_2X2)
    assert izquierdo == derecho == a_fracciones([["7/2", "-3/2"], [-2, 1]])

    izquierdo, derecho = matrices.miembros_inversa_de_la_transpuesta(INVERTIBLE_2X2)
    assert izquierdo == derecho == a_fracciones([[-2, "3/2"], [1, "-1/2"]])

    izquierdo, derecho = matrices.miembros_determinante_de_la_inversa(INVERTIBLE_2X2)
    assert izquierdo == derecho == Fraction(-1, 2)


def probar_operaciones_de_fila_y_determinante():
    """Propiedad 5: intercambio → −det, reemplazo → det, escalar por k → k·det."""
    determinante = matrices.determinante_por_cofactores(INVERTIBLE_2X2)
    assert determinante == -2

    intercambiada = matrices.intercambiar_filas(INVERTIBLE_2X2, 0, 1)
    assert matrices.determinante_por_cofactores(intercambiada) == 2 == -determinante

    reemplazada = matrices.reemplazar_fila(INVERTIBLE_2X2, 1, Fraction(-3), 0)
    assert reemplazada == a_fracciones([[1, 2], [0, -2]])
    assert matrices.determinante_por_cofactores(reemplazada) == -2 == determinante
    assert matrices.describir_reemplazo(1, Fraction(-3), 0) == "F₂ → F₂ - 3·F₁"

    escalada = matrices.escalar_fila(INVERTIBLE_2X2, 0, Fraction(3))
    assert matrices.determinante_por_cofactores(escalada) == -6 == 3 * determinante
    assert INVERTIBLE_2X2 == a_fracciones([[1, 2], [3, 4]]), "las operaciones no deben mutar A"


def probar_efectos_de_fila():
    """Las funciones efecto_de_… devuelven (matriz modificada, det obtenido, det esperado)."""
    assert matrices.efecto_de_intercambio(INVERTIBLE_2X2, 0, 1) == (
        a_fracciones([[3, 4], [1, 2]]), 2, 2
    )
    assert matrices.efecto_de_reemplazo(INVERTIBLE_2X2, 1, Fraction(-3), 0) == (
        a_fracciones([[1, 2], [0, -2]]), -2, -2
    )
    assert matrices.efecto_de_escalamiento(INVERTIBLE_2X2, 0, Fraction(3)) == (
        a_fracciones([[3, 6], [3, 4]]), -6, -6
    )
    assert matrices.describir_intercambio(0, 1) == "F₁ ↔ F₂"
    assert matrices.describir_escalamiento(0, Fraction(3)) == "F₁ → (3)·F₁"


def probar_historial_de_gauss_jordan():
    """El historial opcional guarda una matriz por operación y termina en [I | A⁻¹]."""
    historial = []
    inversa, aumentada_final, operaciones, _ = matrices.invertir_por_gauss_jordan(
        INVERTIBLE_3X3, historial
    )
    assert inversa == INVERSA_3X3
    assert len(historial) == len(operaciones) > 0
    assert historial[-1][2] == aumentada_final


def probar_reduccion_triangular():
    """Propiedad 6: F₃ → F₃ − 5F₁ y F₃ → F₃ + 4F₂ dejan la diagonal 1, 1, 1."""
    triangular, num_intercambios, factores, operaciones = matrices.reducir_a_triangular(
        INVERTIBLE_3X3
    )
    assert operaciones == ["F₃ → F₃ - 5·F₁", "F₃ → F₃ + 4·F₂"]
    assert factores == [5, -4]
    assert num_intercambios == 0
    assert triangular == a_fracciones([[1, 2, 3], [0, 1, 4], [0, 0, 1]])
    assert [triangular[indice][indice] for indice in range(3)] == [1, 1, 1]
    assert matrices.determinante_desde_triangular(triangular, num_intercambios) == 1
    assert matrices.determinante_por_cofactores(INVERTIBLE_3X3) == 1


def probar_reduccion_con_intercambio():
    """Un pivote 0 obliga a intercambiar filas y cada intercambio cambia el signo."""
    con_pivote_nulo = a_fracciones([[0, 2], [3, 4]])
    triangular, num_intercambios, _, operaciones = matrices.reducir_a_triangular(con_pivote_nulo)
    assert operaciones == ["F₁ ↔ F₂"]
    assert num_intercambios == 1
    assert triangular == a_fracciones([[3, 4], [0, 2]])
    assert matrices.determinante_por_reduccion(con_pivote_nulo) == -6
    assert matrices.determinante_por_cofactores(con_pivote_nulo) == -6


def probar_historial_de_la_reduccion_triangular():
    """El historial opcional guarda la matriz tras cada operación y termina en la triangular."""
    historial = []
    triangular, _, _, operaciones = matrices.reducir_a_triangular(INVERTIBLE_3X3, historial)
    assert [tipo for tipo, _, _ in historial] == ["eliminacion", "eliminacion"]
    assert len(historial) == len(operaciones)
    assert historial[-1][2] == triangular
    historial = []
    matrices.reducir_a_triangular(a_fracciones([[0, 2], [3, 4]]), historial)
    assert historial == [("intercambio", 0, a_fracciones([[3, 4], [0, 2]]))]


def probar_cofactor_con_menor():
    """Devuelve el menor M₁₂, su determinante y el mismo cofactor que cofactor()."""
    menor, det_menor, valor = matrices.cofactor_con_menor(INVERTIBLE_3X3, 0, 1)
    assert menor == a_fracciones([[0, 4], [5, 0]])
    assert (det_menor, valor) == (-20, 20)
    assert valor == matrices.cofactor(INVERTIBLE_3X3, 0, 1)


def probar_determinante_del_producto():
    """Propiedad 7: det(AB) = det(A)·det(B), también cuando un factor es singular."""
    # det(A) = -2 y det(B) = -1; AB = [[2,3],[4,7]] tiene det 2.
    assert matrices.miembros_determinante_del_producto(INVERTIBLE_2X2, SEGUNDA_2X2) == (2, 2)
    diagonal = a_fracciones([[1, 0, 0], [0, 2, 0], [0, 0, 3]])
    assert matrices.miembros_determinante_del_producto(INVERTIBLE_3X3, diagonal) == (6, 6)
    assert matrices.miembros_determinante_del_producto(SINGULAR_3X3, INVERTIBLE_3X3) == (0, 0)


def probar_metodos_coinciden_en_otras_matrices():
    """Los métodos de determinante e inversa coinciden en matrices 1×1, 4×4 y con fracciones."""
    casos = [
        a_fracciones([[7]]),
        a_fracciones([["1/2", "-0.5"], ["3/4", 2]]),
        a_fracciones([[2, 0, 1, 3], [1, -1, 0, 2], [0, 4, 1, 1], [3, 1, 2, 0]]),
        a_fracciones([[0, 0, 1], [0, 1, 0], [1, 0, 0]]),
    ]
    for matriz in casos:
        determinante = matrices.determinante_por_cofactores(matriz)
        assert determinante == matrices.determinante_por_reduccion(matriz)
        assert determinante != 0
        por_gauss_jordan = matrices.calcular_inversa(matriz)
        assert por_gauss_jordan == matrices.invertir_por_adjunta(matriz)[0]
        assert matrices.verificar_inversa(matriz, por_gauss_jordan)[1] is True


def probar_validacion_de_matriz_cuadrada():
    """Determinante e inversa rechazan una matriz que no es cuadrada."""
    for funcion in (
        matrices.determinante_por_cofactores,
        matrices.determinante_por_reduccion,
        matrices.invertir_por_gauss_jordan,
        matrices.invertir_por_adjunta,
    ):
        try:
            funcion(MATRIZ_2X3)
        except ValueError as error:
            assert "matriz cuadrada" in str(error)
        else:
            assert False, f"{funcion.__name__} debía rechazar una matriz 2×3"


def probar_formato_de_salida():
    """Fracciones como '3/2', enteros sin '/1', columnas alineadas y barra de la aumentada."""
    assert matrices.formatear_matriz(INVERSA_2X2) == ["  [  -2     1 ]", "  [ 3/2  -1/2 ]"]
    assert matrices.formatear_matriz(a_fracciones([[1, 0], [0, 1]]), 1) == [
        "  [ 1  │  0 ]",
        "  [ 0  │  1 ]",
    ]
    assert matrices.texto_dimension(matrices.dimension(MATRIZ_2X3)) == "2×3"
    assert matrices.conclusion(True) == "«Se cumple»"
    assert matrices.conclusion(False) == "«No se cumple»"


PRUEBAS = [
    probar_operaciones_basicas,
    probar_suma_con_dimensiones_distintas,
    probar_producto_no_conmutativo,
    probar_producto_con_dimensiones_incompatibles,
    probar_determinante_por_los_tres_metodos,
    probar_inversa_3x3_por_ambos_metodos,
    probar_inversa_2x2_y_adjunta,
    probar_matriz_singular,
    probar_diagnostico_invertible,
    probar_propiedades_de_la_inversa,
    probar_operaciones_de_fila_y_determinante,
    probar_efectos_de_fila,
    probar_historial_de_gauss_jordan,
    probar_reduccion_triangular,
    probar_reduccion_con_intercambio,
    probar_historial_de_la_reduccion_triangular,
    probar_cofactor_con_menor,
    probar_determinante_del_producto,
    probar_metodos_coinciden_en_otras_matrices,
    probar_validacion_de_matriz_cuadrada,
    probar_formato_de_salida,
]


def ejecutar_pruebas():
    """Ejecuta todas las pruebas; un assert fallido detiene el script con su traza."""
    for prueba in PRUEBAS:
        prueba()
        print(f"  ok  {prueba.__name__}")
    print(f"Todas las pruebas del Programa 5 pasaron ({len(PRUEBAS)} grupos).")


if __name__ == "__main__":
    ejecutar_pruebas()
