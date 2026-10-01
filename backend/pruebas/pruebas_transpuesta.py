"""Pruebas de los teoremas de la transpuesta (Matrices → Transpuesta).

Se ejecutan desde backend/:  python -m pruebas.pruebas_transpuesta
"""

import unittest
from fractions import Fraction

from fastapi.testclient import TestClient

from app.api import app
from calculo.transpuesta import multiplicar_matrices, transponer

A = [["1", "2", "3"], ["4", "5", "6"]]
B = [["7", "8"], ["9", "10"], ["11", "12"]]


def textos(matriz):
    return [[v["fraccion"] for v in fila] for fila in matriz]


class PruebasTranspuesta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def enviar(self, **cuerpo):
        return self.cliente.post("/api/p3/transpuesta", json=cuerpo)

    def test_operaciones_basicas(self):
        M = [[Fraction(1), Fraction(2)], [Fraction(3), Fraction(4)]]
        self.assertEqual(transponer(M), [[1, 3], [2, 4]])
        self.assertEqual(multiplicar_matrices(M, M), [[7, 10], [15, 22]])

    def test_los_cuatro_teoremas_se_cumplen(self):
        casos = {
            "doble": {"A": A},
            "suma": {"A": A, "B": [["1", "-1", "0"], ["2", "1/2", "3"]]},
            "escalar": {"A": A, "r": "-2.5"},
            "producto": {"A": A, "B": B},
        }
        for teorema, datos in casos.items():
            with self.subTest(teorema=teorema):
                respuesta = self.enviar(teorema=teorema, **datos)
                self.assertEqual(respuesta.status_code, 200)
                self.assertTrue(respuesta.json()["comparacion"]["cumple"])

    def test_producto_transpuesto(self):
        datos = self.enviar(teorema="producto", A=A, B=B).json()
        self.assertEqual(textos(datos["izquierda"][-1]["matriz"]), [["58", "139"], ["64", "154"]])
        self.assertEqual(textos(datos["derecha"][-1]["matriz"]), [["58", "139"], ["64", "154"]])

    def test_suma_trae_los_sumandos(self):
        B2 = [["1", "-1", "0"], ["2", "1/2", "3"]]
        datos = self.enviar(teorema="suma", A=A, B=B2).json()
        izquierda = datos["izquierda"][0]["suma_de"]
        self.assertEqual([s["nombre"] for s in izquierda], ["A", "B"])
        self.assertEqual(textos(izquierda[1]["matriz"]), B2)
        derecha = datos["derecha"][-1]["suma_de"]
        self.assertEqual([s["nombre"] for s in derecha], ["A^{T}", "B^{T}"])
        self.assertEqual(textos(derecha[0]["matriz"]), [["1", "4"], ["2", "5"], ["3", "6"]])
        self.assertIsNone(datos["izquierda"][1]["suma_de"])

    def test_producto_trae_los_factores(self):
        datos = self.enviar(teorema="producto", A=A, B=B).json()
        izquierda = datos["izquierda"][0]["producto_de"]
        self.assertEqual([f["nombre"] for f in izquierda], ["A", "B"])
        self.assertEqual(textos(izquierda[1]["matriz"]), B)
        derecha = datos["derecha"][-1]["producto_de"]
        self.assertEqual([f["nombre"] for f in derecha], ["B^{T}", "A^{T}"])
        self.assertEqual(textos(derecha[1]["matriz"]), [["1", "4"], ["2", "5"], ["3", "6"]])
        self.assertIsNone(datos["izquierda"][1]["producto_de"])

    def test_escalar_trae_r_y_la_matriz(self):
        datos = self.enviar(teorema="escalar", A=A, r="-1/2").json()
        izquierda = datos["izquierda"][0]["escalar_de"]
        self.assertEqual((izquierda["r"]["fraccion"], izquierda["nombre"]), ("-1/2", "A"))
        self.assertEqual(textos(izquierda["matriz"]), A)
        derecha = datos["derecha"][-1]["escalar_de"]
        self.assertEqual(derecha["nombre"], "A^{T}")
        self.assertEqual(textos(derecha["matriz"]), [["1", "4"], ["2", "5"], ["3", "6"]])
        self.assertIsNone(datos["izquierda"][1]["escalar_de"])

    def test_doble_transpuesta_es_una_cadena(self):
        datos = self.enviar(teorema="doble", A=A).json()
        self.assertEqual(datos["modo"], "cadena")
        self.assertNotIn("izquierda", datos)
        nombres = [paso["nombre"] for paso in datos["pasos"]]
        self.assertEqual(nombres, ["A", "A^{T}", "(A^{T})^{T}"])
        self.assertEqual(textos(datos["pasos"][1]["matriz"]), [["1", "4"], ["2", "5"], ["3", "6"]])
        self.assertEqual(textos(datos["pasos"][1]["transpuesta_de"]["matriz"]), A)
        self.assertEqual(textos(datos["pasos"][2]["matriz"]), A)

    def test_detalle_en_latex(self):
        datos = self.enviar(teorema="escalar", A=[["1/2"]], r="-2").json()
        self.assertEqual(
            datos["izquierda"][0]["detalle"],
            [r"(rA)_{11} = r\,a_{11} = \left(-2\right)\cdot\frac{1}{2} = -1"],
        )

    def test_suma_con_ordenes_distintos(self):
        respuesta = self.enviar(teorema="suma", A=A, B=B)
        self.assertEqual(respuesta.status_code, 422)
        self.assertIn("mismas dimensiones", respuesta.json()["detalle"])

    def test_producto_incompatible(self):
        respuesta = self.enviar(teorema="producto", A=A, B=A)
        self.assertEqual(respuesta.status_code, 422)

    def test_texto_no_numerico(self):
        datos = self.enviar(teorema="doble", A=[["1", "abc"]]).json()
        self.assertEqual((datos["campo"], datos["fila"], datos["columna"]), ("A", 1, 2))

    def test_escalar_vacio(self):
        datos = self.enviar(teorema="escalar", A=A, r=" ").json()
        self.assertEqual(datos["campo"], "r")


if __name__ == "__main__":
    unittest.main()
