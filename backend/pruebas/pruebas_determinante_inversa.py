"""Pruebas del determinante (Sarrus y cofactores) y de la inversa (adjunta y Gauss-Jordan).

Recorren los siete casos de revisión por las tres capas: el módulo de cálculo, el
adaptador web y la consola. Solo usan `unittest`; la clase de la API se omite si FastAPI
no está instalado. Se ejecutan desde backend/:
    python -m pruebas.pruebas_determinante_inversa
"""

import contextlib
import io
import unittest
from fractions import Fraction
from unittest import mock

# programa5_web deja la carpeta programa_4 en sys.path y expone el módulo de cálculo.
import calculo.programa5_web as web
from calculo.nucleo import ErrorDeEntrada

matrices = web.p5m

try:
    from fastapi.testclient import TestClient

    from app.api import app
except ImportError:  # sin FastAPI se prueba todo menos las rutas HTTP
    TestClient = None

MENSAJE_SARRUS = "La regla de Sarrus solo se aplica a matrices 3×3."
MENSAJE_SINGULAR = "La matriz es singular (no tiene inversa): det(A) = 0"


def fracciones(rejilla):
    """Rejilla de enteros o textos como '1/2' → matriz de Fraction."""
    return [[Fraction(valor) for valor in fila] for fila in rejilla]


def textos(rejilla):
    """Rejilla de enteros o textos → rejilla de textos, como la envía el frontend."""
    return [[str(valor) for valor in fila] for fila in rejilla]


# Casos invertibles: (A, det(A), A⁻¹).
CASO_1 = ([[1, 2, 3], [0, 1, 4], [5, 6, 0]], 1, [[-24, 18, 5], [20, -15, -4], [-5, 4, 1]])
CASO_2 = ([[4, 7], [2, 6]], 10, [["3/5", "-7/10"], ["-1/5", "2/5"]])
CASO_3 = (
    [[1, 0, 2], [2, 1, 0], [0, 1, 1]],
    5,
    [["1/5", "2/5", "-2/5"], ["-2/5", "1/5", "4/5"], ["2/5", "-1/5", "1/5"]],
)
CASO_5 = (
    [[0, 2, 1], [1, 1, 0], [2, 0, 1]],
    -4,
    [["-1/4", "1/2", "1/4"], ["1/4", "1/2", "-1/4"], ["1/2", -1, "1/2"]],
)
INVERTIBLES = {"caso 1": CASO_1, "caso 2": CASO_2, "caso 3": CASO_3, "caso 5": CASO_5}
SINGULAR = [[2, 0, 1], [1, 3, 2], [1, 1, 1]]  # caso 4
TRIANGULAR_4X4 = [[2, 1, 0, 3], [0, 1, 4, 1], [0, 0, 3, 2], [0, 0, 0, 1]]  # caso 6
NO_CUADRADA = [[1, 2, 3], [4, 5, 6]]  # caso 7

_DIGITOS = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def aplicar_paso(matriz, paso):
    """Aplica a la matriz una operación escrita como texto ('F₃ → F₃ - 5·F₁') y la devuelve."""
    resultado = [fila[:] for fila in matriz]
    texto = paso.translate(_DIGITOS)
    if "↔" in texto:
        fila_a, fila_b = [int(parte.strip()[1:]) - 1 for parte in texto.split("↔")]
        resultado[fila_a], resultado[fila_b] = resultado[fila_b], resultado[fila_a]
        return resultado
    destino, expresion = [parte.strip() for parte in texto.split("→")]
    fila_destino = int(destino[1:]) - 1
    if expresion.startswith("("):  # escalamiento: (k)·Fᵢ
        factor = Fraction(expresion[1:expresion.index(")")])
        resultado[fila_destino] = [factor * valor for valor in resultado[fila_destino]]
        return resultado
    _, signo, termino = expresion.split(" ", 2)  # reemplazo: Fᵢ ± k·Fⱼ
    factor, origen = termino.split("·") if "·" in termino else ("1", termino)
    factor = Fraction(factor) if signo == "+" else -Fraction(factor)
    fila_origen = resultado[int(origen[1:]) - 1]
    resultado[fila_destino] = [
        valor + factor * valor_origen
        for valor, valor_origen in zip(resultado[fila_destino], fila_origen)
    ]
    return resultado


class PruebasDeterminante(unittest.TestCase):
    def test_sarrus_y_cofactores_coinciden_en_3x3(self):
        for nombre in ("caso 1", "caso 3", "caso 5"):
            rejilla, esperado, _ = INVERTIBLES[nombre]
            with self.subTest(nombre):
                A = fracciones(rejilla)
                self.assertEqual(matrices.determinante_por_sarrus(A), esperado)
                self.assertEqual(matrices.determinante_por_cofactores(A), esperado)
                self.assertEqual(matrices.determinante_por_reduccion(A), esperado)

    def test_caso_2_determinante_2x2(self):
        A = fracciones(CASO_2[0])
        self.assertEqual(matrices.determinante_por_cofactores(A), 10)
        self.assertEqual(matrices.determinante_por_reduccion(A), 10)

    def test_caso_4_determinante_cero(self):
        A = fracciones(SINGULAR)
        self.assertEqual(matrices.determinante_por_sarrus(A), 0)
        self.assertEqual(matrices.determinante_por_cofactores(A), 0)
        self.assertEqual(matrices.determinante_por_reduccion(A), 0)

    def test_caso_6_cofactores_en_4x4_y_sarrus_la_rechaza(self):
        A = fracciones(TRIANGULAR_4X4)
        self.assertEqual(matrices.determinante_por_cofactores(A), 6)
        self.assertEqual(matrices.determinante_por_reduccion(A), 6)
        with self.assertRaises(ValueError) as contexto:
            matrices.determinante_por_sarrus(A)
        self.assertEqual(str(contexto.exception), MENSAJE_SARRUS)

    def test_sarrus_rechaza_2x2(self):
        with self.assertRaises(ValueError) as contexto:
            matrices.determinante_por_sarrus(fracciones(CASO_2[0]))
        self.assertEqual(str(contexto.exception), MENSAJE_SARRUS)

    def test_diagonales_de_sarrus_del_caso_1(self):
        descendentes, ascendentes = matrices.diagonales_de_sarrus(fracciones(CASO_1[0]))
        self.assertEqual([producto for _, _, producto in descendentes], [0, 40, 0])
        self.assertEqual([producto for _, _, producto in ascendentes], [15, 24, 0])
        celdas, entradas, _ = descendentes[1]
        self.assertEqual(celdas, [(0, 1), (1, 2), (2, 3)])
        self.assertEqual(entradas, [2, 4, 5])
        self.assertEqual(ascendentes[0][0], [(2, 0), (1, 1), (0, 2)])
        self.assertEqual(matrices.sumas_de_sarrus(fracciones(CASO_1[0])), (40, 39))
        self.assertEqual(
            matrices.ampliar_para_sarrus(fracciones(CASO_1[0])),
            fracciones([[1, 2, 3, 1, 2], [0, 1, 4, 0, 1], [5, 6, 0, 5, 6]]),
        )

    def test_terminos_de_la_expansion_por_cofactores(self):
        A = fracciones(CASO_1[0])
        terminos, determinante = matrices.expansion_por_cofactores(A)
        self.assertEqual(determinante, 1)
        self.assertEqual([termino[0] for termino in terminos][1], fracciones([[0, 4], [5, 0]]))
        self.assertEqual([termino[1] for termino in terminos], [-24, -20, -5])  # det(M₁ⱼ)
        self.assertEqual([termino[2] for termino in terminos], [-24, 20, -5])  # C₁ⱼ
        self.assertEqual([termino[3] for termino in terminos], [-24, 40, -15])  # a₁ⱼ·C₁ⱼ
        self.assertEqual(matrices.describir_signo(0, 1), "(−1)¹⁺² = −1")
        self.assertEqual(matrices.describir_signo(1, 1), "(−1)²⁺² = +1")

    def test_signo_de_los_cofactores_alterna_como_un_tablero(self):
        identidad = matrices.matriz_identidad(3)
        unos = fracciones([[1, 1, 1], [1, 2, 3], [1, 4, 9]])
        self.assertEqual(matrices.cofactor(identidad, 0, 0), 1)
        self.assertEqual(matrices.cofactor(unos, 0, 1), -6)  # −(1·9 − 3·1)
        self.assertEqual(matrices.cofactor(unos, 1, 0), -5)  # −(1·9 − 1·4)
        self.assertEqual(matrices.cofactor(unos, 1, 1), 8)  # +(1·9 − 1·1)

    def test_reduccion_intercambia_solo_si_el_pivote_es_cero(self):
        _, intercambios, _, operaciones = matrices.reducir_a_triangular(fracciones(CASO_5[0]))
        self.assertEqual(operaciones[0], "F₁ ↔ F₂")
        self.assertEqual(intercambios, 1)
        _, intercambios, _, _ = matrices.reducir_a_triangular(fracciones(CASO_1[0]))
        self.assertEqual(intercambios, 0)


class PruebasInversa(unittest.TestCase):
    def test_adjunta_y_gauss_jordan_dan_la_inversa_esperada(self):
        for nombre, (rejilla, determinante, esperada) in INVERTIBLES.items():
            with self.subTest(nombre):
                A = fracciones(rejilla)
                por_adjunta, _, det_adjunta = matrices.invertir_por_adjunta(A)
                por_gauss_jordan, _, _, pivotes = matrices.invertir_por_gauss_jordan(A)
                self.assertEqual(det_adjunta, determinante)
                self.assertEqual(pivotes, len(A))
                self.assertEqual(por_adjunta, fracciones(esperada))
                self.assertEqual(por_gauss_jordan, por_adjunta)

    def test_el_producto_por_la_inversa_es_la_identidad_exacta(self):
        for nombre, (rejilla, _, _) in INVERTIBLES.items():
            with self.subTest(nombre):
                A = fracciones(rejilla)
                inversa = matrices.calcular_inversa(A)
                identidad = matrices.matriz_identidad(len(A))
                self.assertEqual(matrices.multiplicar_matrices(A, inversa), identidad)
                self.assertEqual(matrices.multiplicar_matrices(inversa, A), identidad)

    def test_la_adjunta_es_la_transpuesta_de_los_cofactores(self):
        A = fracciones(CASO_3[0])
        cofactores = matrices.matriz_de_cofactores(A)
        adjunta = matrices.matriz_adjunta(A)
        self.assertEqual(cofactores, fracciones([[1, -2, 2], [2, 1, -1], [-2, 4, 1]]))
        self.assertEqual(adjunta, fracciones([[1, 2, -2], [-2, 1, 4], [2, -1, 1]]))
        self.assertNotEqual(adjunta, cofactores)

    def test_caso_4_singular_no_tiene_inversa_en_ningun_metodo(self):
        A = fracciones(SINGULAR)
        inversa, _, determinante = matrices.invertir_por_adjunta(A)
        self.assertIsNone(inversa)
        self.assertEqual(determinante, 0)
        inversa, _, _, pivotes = matrices.invertir_por_gauss_jordan(A)
        self.assertIsNone(inversa)
        self.assertEqual(pivotes, 2)
        self.assertEqual(matrices.diagnostico_invertibilidad(A), MENSAJE_SINGULAR)

    def test_caso_5_gauss_jordan_intercambia_filas(self):
        _, _, operaciones, _ = matrices.invertir_por_gauss_jordan(fracciones(CASO_5[0]))
        self.assertIn("↔", operaciones[0])

    def test_caso_6_inversa_4x4_por_ambos_metodos(self):
        A = fracciones(TRIANGULAR_4X4)
        inversa = matrices.calcular_inversa(A)
        self.assertEqual(inversa, matrices.invertir_por_adjunta(A)[0])
        self.assertTrue(matrices.verificar_inversa(A, inversa)[1])

    def test_matriz_1x1(self):
        self.assertEqual(matrices.determinante_por_cofactores(fracciones([[5]])), 5)
        self.assertEqual(matrices.invertir_por_adjunta(fracciones([[5]]))[0], fracciones([["1/5"]]))
        self.assertEqual(matrices.calcular_inversa(fracciones([[5]])), fracciones([["1/5"]]))
        self.assertIsNone(matrices.invertir_por_adjunta(fracciones([[0]]))[0])
        self.assertIsNone(matrices.calcular_inversa(fracciones([[0]])))

    def test_entradas_fraccionarias_y_negativas(self):
        A = fracciones([["1/2", "-1/3"], [-2, "3/4"]])
        esperada = fracciones([["-18/7", "-8/7"], ["-48/7", "-12/7"]])
        self.assertEqual(matrices.determinante_por_cofactores(A), Fraction(-7, 24))
        self.assertEqual(matrices.invertir_por_adjunta(A)[0], esperada)
        self.assertEqual(matrices.calcular_inversa(A), esperada)


class PruebasPasosRegistrados(unittest.TestCase):
    """Cada operación mostrada, aplicada a la matriz anterior, da la matriz siguiente."""

    CASOS = [CASO_1[0], CASO_2[0], CASO_3[0], SINGULAR, CASO_5[0], TRIANGULAR_4X4]

    def test_pasos_de_gauss_jordan(self):
        for rejilla in self.CASOS:
            with self.subTest(rejilla):
                A = fracciones(rejilla)
                historial = []
                _, final, pasos, _ = matrices.invertir_por_gauss_jordan(A, historial)
                actual = matrices.construir_aumentada_con_identidad(A)
                self.assertEqual(len(pasos), len(historial))
                for paso, (_, _, registrada) in zip(pasos, historial):
                    actual = aplicar_paso(actual, paso)
                    self.assertEqual(actual, registrada, paso)
                self.assertEqual(actual, final)

    def test_pasos_de_la_reduccion_triangular(self):
        for rejilla in self.CASOS:
            with self.subTest(rejilla):
                A = fracciones(rejilla)
                historial = []
                triangular, _, _, pasos = matrices.reducir_a_triangular(A, historial)
                actual = A
                self.assertEqual(len(pasos), len(historial))
                for paso, (_, _, registrada) in zip(pasos, historial):
                    actual = aplicar_paso(actual, paso)
                    self.assertEqual(actual, registrada, paso)
                self.assertEqual(actual, triangular)
                for fila in range(len(A)):
                    self.assertEqual(triangular[fila][:fila], [0] * fila)


class PruebasValidacion(unittest.TestCase):
    FUNCIONES = (
        matrices.determinante_por_cofactores,
        matrices.determinante_por_reduccion,
        matrices.invertir_por_gauss_jordan,
        matrices.invertir_por_adjunta,
    )

    def rechaza(self, matriz, fragmento):
        for funcion in self.FUNCIONES:
            with self.subTest(funcion.__name__):
                with self.assertRaises(ValueError) as contexto:
                    funcion(matriz)
                self.assertIn(fragmento, str(contexto.exception))

    def test_caso_7_matriz_2x3(self):
        self.rechaza(fracciones(NO_CUADRADA), "matriz cuadrada: se recibió una de 2×3")

    def test_matriz_vacia(self):
        self.rechaza([], "matriz vacía")

    def test_filas_de_distinto_largo(self):
        self.rechaza([[Fraction(1), Fraction(2)], [Fraction(3)]], "la fila 2 tiene 1 valores")

    def test_sarrus_con_matriz_vacia_o_irregular(self):
        for matriz in ([], [[Fraction(1)] * 3, [Fraction(1)] * 2, [Fraction(1)] * 3]):
            with self.assertRaises(ValueError) as contexto:
                matrices.determinante_por_sarrus(matriz)
            self.assertEqual(str(contexto.exception), MENSAJE_SARRUS)


class PruebasAdaptadorWeb(unittest.TestCase):
    """Lo que recibe el frontend: mismos valores y el paso a paso de cada método."""

    def test_los_siete_casos(self):
        for nombre, (rejilla, determinante, esperada) in INVERTIBLES.items():
            with self.subTest(nombre):
                datos = web.calcular_determinante(textos(rejilla))
                self.assertEqual(datos["determinante"], determinante)
                self.assertTrue(datos["coinciden"])
                for metodo in ("gauss_jordan", "adjunta"):
                    inversa = web.calcular_inversa(metodo, textos(rejilla))
                    self.assertEqual(inversa["inversa"], fracciones(esperada))
                    self.assertTrue(inversa["comprobacion"]["es_identidad"])
        self.assertEqual(web.calcular_determinante(textos(TRIANGULAR_4X4))["determinante"], 6)

    def test_singular_devuelve_el_mensaje_y_ninguna_inversa(self):
        for metodo in ("gauss_jordan", "adjunta"):
            datos = web.calcular_inversa(metodo, textos(SINGULAR))
            self.assertIsNone(datos["inversa"])
            self.assertIsNone(datos["comprobacion"])
            self.assertEqual(datos["diagnostico"]["texto"], MENSAJE_SINGULAR)

    def test_errores_de_entrada(self):
        casos = [
            (textos(NO_CUADRADA), "matriz cuadrada"),
            ([], "vacía"),
            ([["1", "2"], ["3"]], "La fila 2"),
            ([["1/0", "1"], ["0", "1"]], "no es un número"),
            ([["uno", "1"], ["0", "1"]], "no es un número"),
        ]
        for rejilla, fragmento in casos:
            with self.subTest(fragmento):
                with self.assertRaises(ErrorDeEntrada) as contexto:
                    web.calcular_determinante(rejilla)
                self.assertIn(fragmento, contexto.exception.mensaje)
                with self.assertRaises(ErrorDeEntrada):
                    web.calcular_inversa("adjunta", rejilla)

    def test_fracciones_y_negativos_como_texto(self):
        datos = web.calcular_determinante([["1/2", "-1/3"], ["-2", "0.75"]])
        self.assertEqual(datos["determinante"], Fraction(-7, 24))

    def test_paso_a_paso_de_sarrus(self):
        sarrus = web.calcular_determinante(textos(CASO_1[0]))["sarrus"]
        self.assertEqual(len(sarrus["ampliada"][0]), 5)
        productos = [diagonal["producto"] for diagonal in sarrus["diagonales_descendentes"]]
        self.assertEqual(productos, [0, 40, 0])
        productos = [diagonal["producto"] for diagonal in sarrus["diagonales_ascendentes"]]
        self.assertEqual(productos, [15, 24, 0])
        self.assertEqual(sarrus["diagonales_ascendentes"][0]["celdas"], [[2, 0], [1, 1], [0, 2]])
        self.assertEqual((sarrus["descendentes"], sarrus["ascendentes"], sarrus["valor"]), (40, 39, 1))
        self.assertIsNone(web.calcular_determinante(textos(TRIANGULAR_4X4))["sarrus"])

    def test_paso_a_paso_de_cofactores(self):
        cofactores = web.calcular_determinante(textos(CASO_1[0]))["cofactores"]
        segundo = cofactores["terminos"][1]
        self.assertEqual(segundo["nombre_menor"], "M₁₂")
        self.assertEqual(segundo["regla_signo"], "(−1)¹⁺² = −1")
        self.assertEqual(segundo["desarrollo_menor"]["cuenta"], "(0)·(0) − (4)·(5) = -20")
        self.assertEqual((segundo["cofactor"], segundo["producto"]), (20, 40))
        self.assertEqual(cofactores["valor"], 1)
        self.assertIsNone(cofactores["nota_menores"])

    def test_cofactores_de_4x4_anida_el_desarrollo_de_cada_menor(self):
        cofactores = web.calcular_determinante(textos(TRIANGULAR_4X4))["cofactores"]
        primero = cofactores["terminos"][0]
        anidado = primero["desarrollo_menor"]
        self.assertEqual(anidado["tipo"], "cofactores")
        self.assertEqual(anidado["valor"], primero["det_menor"])
        self.assertEqual(anidado["terminos"][0]["nombre_menor"], "M′₁₁")
        self.assertEqual(anidado["terminos"][0]["desarrollo_menor"]["cuenta"], "(3)·(1) − (2)·(0) = 3")

    def test_desde_6x6_los_menores_no_se_despliegan(self):
        identidad = textos(matrices.matriz_identidad(6))
        cofactores = web.calcular_determinante(identidad)["cofactores"]
        self.assertIn("6 determinantes 5×5", cofactores["nota_menores"])
        self.assertIsNone(cofactores["terminos"][0]["desarrollo_menor"])
        self.assertEqual(cofactores["valor"], 1)

    def test_paso_a_paso_de_la_reduccion_triangular(self):
        reduccion = web.calcular_determinante(textos(CASO_5[0]))["reduccion"]
        notaciones = [paso["notacion"] for paso in reduccion["pasos_detalle"]]
        self.assertEqual(notaciones, ["F₁ ↔ F₂", "F₃ → F₃ - 2·F₁", "F₃ → F₃ + F₂"])
        self.assertEqual(reduccion["pasos_detalle"][-1]["matriz"], reduccion["triangular"])
        self.assertEqual((reduccion["intercambios"], reduccion["signo"]), (1, "−1"))
        self.assertEqual((reduccion["producto_diagonal"], reduccion["valor"]), (4, -4))
        self.assertEqual(reduccion["columnas_pivote"], [0, 1, 2])

    def test_pivotes_de_la_triangular_cuando_falta_uno_en_la_diagonal(self):
        reduccion = web.calcular_determinante(textos([[1, 2, 3], [0, 0, 1], [0, 0, 2]]))["reduccion"]
        self.assertEqual(reduccion["columnas_pivote"], [0])
        self.assertEqual(reduccion["valor"], 0)


class PruebasConsola(unittest.TestCase):
    """Las opciones 6, 7 y 8 del menú siguen funcionando con la entrada por teclado."""

    def ejecutar(self, opcion, lineas):
        salida = io.StringIO()
        with mock.patch("builtins.input", side_effect=lineas), contextlib.redirect_stdout(salida):
            opcion()
        return salida.getvalue()

    def test_determinante_del_caso_1(self):
        salida = self.ejecutar(matrices.opcion_determinante, ["3", "1 2 3", "0 1 4", "5 6 0"])
        self.assertIn("det(A) = (1)·(-24) + (2)·(20) + (3)·(-5) = 1", salida)
        self.assertIn("det(A) = (40) − (39) = 1", salida)
        self.assertIn("Los métodos coinciden: det(A) = 1 ✓", salida)

    def test_determinante_4x4_no_aplica_sarrus(self):
        filas = [" ".join(str(valor) for valor in fila) for fila in TRIANGULAR_4X4]
        salida = self.ejecutar(matrices.opcion_determinante, ["4", *filas])
        self.assertIn("Regla de Sarrus: no se aplica, solo vale para matrices 3×3.", salida)
        self.assertIn("Los métodos coinciden: det(A) = 6 ✓", salida)

    def test_inversa_con_fracciones_y_un_dato_invalido(self):
        lineas = ["2", "4 7", "dos 6", "2 6"]
        for opcion in (matrices.opcion_inversa_gauss_jordan, matrices.opcion_inversa_adjunta):
            salida = self.ejecutar(opcion, lineas)
            self.assertIn("Valor inválido", salida)
            self.assertIn("[  3/5  -7/10 ]", salida)
            self.assertIn("A·A⁻¹ = I ✓ (igualdad exacta)", salida)

    def test_inversa_de_la_singular(self):
        lineas = ["3", "2 0 1", "1 3 2", "1 1 1"]
        for opcion in (matrices.opcion_inversa_gauss_jordan, matrices.opcion_inversa_adjunta):
            salida = self.ejecutar(opcion, lineas)
            self.assertIn(MENSAJE_SINGULAR, salida)
            self.assertIn("no existe A⁻¹", salida)
            self.assertNotIn("Comprobación", salida)


@unittest.skipIf(TestClient is None, "FastAPI no está instalado")
class PruebasAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def test_determinante_con_el_paso_a_paso_serializado(self):
        datos = self.cliente.post("/api/p5/determinante", json={"A": textos(CASO_1[0])}).json()
        self.assertEqual(datos["determinante"]["fraccion"], "1")
        diagonal = datos["sarrus"]["diagonales_descendentes"][1]
        self.assertEqual([valor["fraccion"] for valor in diagonal["entradas"]], ["2", "4", "5"])
        self.assertEqual(diagonal["producto"]["fraccion"], "40")
        self.assertEqual(datos["cofactores"]["terminos"][1]["producto"]["fraccion"], "40")

    def test_inversa_singular_responde_200_sin_inversa(self):
        for metodo in ("gauss_jordan", "adjunta"):
            respuesta = self.cliente.post(
                "/api/p5/inversa", json={"metodo": metodo, "A": textos(SINGULAR)}
            )
            self.assertEqual(respuesta.status_code, 200)
            self.assertIsNone(respuesta.json()["inversa"])
            self.assertEqual(respuesta.json()["diagnostico"]["texto"], MENSAJE_SINGULAR)

    def test_matriz_2x3_responde_422(self):
        for ruta, cuerpo in (("determinante", {}), ("inversa", {"metodo": "adjunta"})):
            respuesta = self.cliente.post(f"/api/p5/{ruta}", json={**cuerpo, "A": textos(NO_CUADRADA)})
            self.assertEqual(respuesta.status_code, 422)
            self.assertIn("matriz cuadrada", respuesta.json()["detalle"])
            self.assertEqual(respuesta.json()["campo"], "A")


if __name__ == "__main__":
    unittest.main()
