"""Pruebas de la Regla de Cramer (xᵢ = det Aᵢ(b) / det A).

Comprueban el módulo de cálculo y su ruta web sin levantar el servidor.
Se ejecutan desde backend/:  python -m pruebas.pruebas_cramer
"""

import unittest
from fractions import Fraction

from fastapi.testclient import TestClient

from app.api import app
from calculo.cramer_web import cramer

SISTEMA_2X2 = [["3", "-2"], ["-5", "4"]]
TERMINOS_2X2 = ["6", "8"]
SISTEMA_3X3 = [["2", "1", "-1"], ["-3", "-1", "2"], ["-2", "1", "2"]]
TERMINOS_3X3 = ["8", "-11", "-3"]
SISTEMA_4X4 = [
    ["1", "2", "0", "1"],
    ["2", "5", "1", "3"],
    ["0", "1", "3", "2"],
    ["1", "3", "2", "5"],
]
TERMINOS_4X4 = ["-1", "-1", "5", "2"]
SINGULAR_2X2 = [["1", "2"], ["2", "4"]]


def fracciones(rejilla):
    """Rejilla de enteros o textos → matriz de Fraction."""
    return [[Fraction(valor) for valor in fila] for fila in rejilla]


def vector(textos):
    """Lista de textos → vector de Fraction."""
    return [Fraction(valor) for valor in textos]


def texto_vector(serializado):
    """Vector serializado → lista de textos ("fraccion")."""
    return [valor["fraccion"] for valor in serializado]


class PruebasModuloCramer(unittest.TestCase):
    def test_reemplazar_columna_no_altera_la_original(self):
        A = fracciones(SISTEMA_2X2)
        self.assertEqual(
            cramer.reemplazar_columna(A, 1, vector(TERMINOS_2X2)), fracciones([[3, 6], [-5, 8]])
        )
        self.assertEqual(A, fracciones(SISTEMA_2X2))

    def test_sistema_2x2(self):
        det_a, determinantes, x = cramer.resolver_por_cramer(
            fracciones(SISTEMA_2X2), vector(TERMINOS_2X2)
        )
        self.assertEqual(det_a, 2)
        self.assertEqual(determinantes, [40, 54])
        self.assertEqual(x, [20, 27])

    def test_sistema_3x3(self):
        det_a, _, x = cramer.resolver_por_cramer(fracciones(SISTEMA_3X3), vector(TERMINOS_3X3))
        self.assertEqual(det_a, -1)
        self.assertEqual(x, [2, 3, -1])

    def test_solucion_con_fracciones(self):
        _, _, x = cramer.resolver_por_cramer(fracciones([[2, 1], [1, 3]]), vector(["1", "2"]))
        self.assertEqual(x, [Fraction(1, 5), Fraction(3, 5)])

    def test_singular_inconsistente(self):
        _, determinantes, x = cramer.resolver_por_cramer(
            fracciones(SINGULAR_2X2), vector(["3", "5"])
        )
        self.assertIsNone(x)
        self.assertEqual(
            cramer.diagnostico_sin_solucion_unica(determinantes), cramer.MENSAJE_SIN_SOLUCION
        )

    def test_singular_que_no_decide(self):
        _, determinantes, x = cramer.resolver_por_cramer(
            fracciones(SINGULAR_2X2), vector(["3", "6"])
        )
        self.assertIsNone(x)
        self.assertEqual(
            cramer.diagnostico_sin_solucion_unica(determinantes), cramer.MENSAJE_NO_DECIDE
        )

    def test_matriz_no_cuadrada(self):
        with self.assertRaises(ValueError):
            cramer.resolver_por_cramer(fracciones([[1, 2, 3], [4, 5, 6]]), vector(["1", "2"]))


class PruebasCramerWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def enviar(self, cuerpo):
        return self.cliente.post("/api/determinantes/cramer", json=cuerpo)

    def test_resuelve_y_comprueba(self):
        datos = self.enviar({"A": SISTEMA_3X3, "b": TERMINOS_3X3}).json()
        self.assertTrue(datos["aplicable"])
        self.assertEqual(datos["det_A"]["fraccion"], "-1")
        self.assertEqual(texto_vector(datos["x"]), ["2", "3", "-1"])
        self.assertTrue(datos["comprobacion"]["correcta"])
        self.assertEqual(texto_vector(datos["comprobacion"]["Ax"]), TERMINOS_3X3)

    def test_cada_incognita_trae_su_matriz_y_su_cociente(self):
        datos = self.enviar({"A": SISTEMA_2X2, "b": TERMINOS_2X2}).json()
        segunda = datos["incognitas"][1]
        self.assertEqual(segunda["variable"], "x₂")
        self.assertEqual(segunda["nombre_matriz"], "A₂(b)")
        self.assertEqual([texto_vector(fila) for fila in segunda["matriz"]], [["3", "6"], ["-5", "8"]])
        self.assertEqual(segunda["determinante"]["fraccion"], "54")
        self.assertEqual(segunda["ecuacion"]["formula"], "det A₂(b) / det A")
        self.assertEqual(segunda["ecuacion"]["cuenta"], "(54) / (2)")
        self.assertEqual(segunda["ecuacion"]["valor"]["fraccion"], "27")

    def test_desarrollo_por_cofactores_hasta_3x3(self):
        datos = self.enviar({"A": SISTEMA_3X3, "b": TERMINOS_3X3}).json()
        self.assertEqual(datos["desarrollo_A"]["tipo"], "det_cofactores")
        self.assertEqual(datos["desarrollo_A"]["valor"]["fraccion"], "-1")

    def test_desarrollo_por_reduccion_desde_4x4(self):
        datos = self.enviar({"A": SISTEMA_4X4, "b": TERMINOS_4X4}).json()
        self.assertEqual(datos["desarrollo_A"]["tipo"], "det_reduccion")
        self.assertEqual(
            datos["desarrollo_A"]["reduccion"]["valor"]["fraccion"], datos["det_A"]["fraccion"]
        )
        self.assertTrue(datos["comprobacion"]["correcta"])

    def test_singular_explica_por_que_no_se_aplica(self):
        datos = self.enviar({"A": SINGULAR_2X2, "b": ["3", "5"]}).json()
        self.assertFalse(datos["aplicable"])
        self.assertIsNone(datos["x"])
        self.assertIsNone(datos["incognitas"][0]["ecuacion"])
        self.assertIn("inconsistente", datos["motivo"])

    def test_matriz_no_cuadrada(self):
        respuesta = self.enviar({"A": [["1", "2", "3"], ["4", "5", "6"]], "b": ["1", "2"]})
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "A")

    def test_componente_invalida_de_b(self):
        respuesta = self.enviar({"A": SISTEMA_2X2, "b": ["1", "x"]})
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "b")
        self.assertEqual(respuesta.json()["fila"], 2)


if __name__ == "__main__":
    unittest.main()
