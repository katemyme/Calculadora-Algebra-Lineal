"""Pruebas de Transformaciones Lineales (fórmula general y vectores dados) por la API.

Se ejecutan desde backend/:  python -m pruebas.pruebas_transformaciones
"""

import unittest

from fastapi.testclient import TestClient

from app.api import app


def fracciones(vector):
    return [v["fraccion"] for v in vector]


class PruebasFormula(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def enviar(self, formula, vector=""):
        return self.cliente.post("/api/tl/formula", json={"formula": formula, "vector": vector})

    def test_proyeccion_x0(self):
        datos = self.enviar("T(x, y) = (x, 0)").json()
        self.assertTrue(datos["linealidad"]["es_lineal"])
        analisis = datos["analisis"]
        self.assertEqual(analisis["valor_nulidad"], 1)
        self.assertEqual(analisis["valor_rango"], 1)
        self.assertEqual([fracciones(b) for b in analisis["base_nucleo"]], [["0", "1"]])
        self.assertEqual([fracciones(b) for b in analisis["base_imagen"]], [["1", "0"]])

    def test_ejemplo_2_con_evaluacion(self):
        datos = self.enviar("T(x,y) = (x + y, x - y, 3y)", "(2, 4)").json()
        self.assertTrue(datos["linealidad"]["es_lineal"])
        self.assertIn(r"\left(6, -2, 12\right)", datos["evaluacion"]["conclusion"])
        self.assertEqual(datos["analisis"]["valor_nulidad"], 0)

    def test_r4_en_r2(self):
        datos = self.enviar("T(x, y, z, w) = (x + z, y + w)").json()
        analisis = datos["analisis"]
        self.assertEqual(analisis["valor_nulidad"], 2)
        self.assertTrue(analisis["sobreyectiva"])
        self.assertEqual([fracciones(b) for b in analisis["base_nucleo"]],
                         [["-1", "0", "1", "0"], ["0", "-1", "0", "1"]])

    def test_codominio_real(self):
        datos = self.enviar("T(x, y) = x + y").json()
        self.assertEqual(datos["m"], 1)
        self.assertEqual(datos["analisis"]["valor_rango"], 1)

    def test_constante_no_es_lineal(self):
        datos = self.enviar("T(x, y) = (1, y)").json()
        linealidad = datos["linealidad"]
        self.assertFalse(linealidad["es_lineal"])
        self.assertFalse(linealidad["prueba_cero"]["cumple"])
        self.assertIsNone(datos["analisis"])

    def test_cuadrados_cumplen_t0_pero_no_son_lineales(self):
        datos = self.enviar("T(x, y) = (x^2, y^2)").json()
        linealidad = datos["linealidad"]
        self.assertTrue(linealidad["prueba_cero"]["cumple"])
        self.assertFalse(linealidad["aditividad"]["cumple"])
        self.assertFalse(linealidad["homogeneidad"]["cumple"])

    def test_formula_mal_escrita(self):
        respuesta = self.enviar("(x + y, 3y)")
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "formula")

    def test_vector_de_dimension_incorrecta(self):
        respuesta = self.enviar("T(x, y) = (x, y)", "(1, 2, 3)")
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "vector")


class PruebasVectores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def enviar(self, pares, vector=""):
        cuerpo = {"pares": [{"vector": b, "imagen": w} for b, w in pares], "vector": vector}
        return self.cliente.post("/api/tl/vectores", json=cuerpo)

    def test_sesion_17_ejercicio_5(self):
        datos = self.enviar([("(1, 0)", "(1, 2, 3)"), ("(0, 1)", "(-4, 0, 5)")], "(2, 4)").json()
        self.assertIn(r"\left(-14, 4, 26\right)", datos["evaluacion"]["conclusion"])
        self.assertEqual([fracciones(f) for f in datos["matriz"]["A"]],
                         [["1", "-4"], ["2", "0"], ["3", "5"]])

    def test_sesion_16_ejemplo_2(self):
        datos = self.enviar([("(1,0,0)", "(2,3)"), ("(0,1,0)", "(-1,4)"), ("(0,0,1)", "(5,-3)")],
                            "(3, -4, 5)").json()
        self.assertIn(r"\left(35, -22\right)", datos["evaluacion"]["conclusion"])
        self.assertEqual(datos["analisis"]["valor_nulidad"], 1)

    def test_base_no_canonica(self):
        datos = self.enviar([("(1, 1)", "(2, 0)"), ("(1, -1)", "(0, 2)")], "(3, 1)").json()
        self.assertEqual([fracciones(f) for f in datos["matriz"]["A"]], [["1", "1"], ["1", "-1"]])
        self.assertIn(r"\left(4, 2\right)", datos["evaluacion"]["conclusion"])

    def test_vectores_dependientes(self):
        respuesta = self.enviar([("(1, 2)", "(1, 0)"), ("(2, 4)", "(0, 1)")])
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "pares")

    def test_faltan_vectores(self):
        respuesta = self.enviar([("(1, 0, 0)", "(1, 1)")])
        self.assertEqual(respuesta.status_code, 422)

    def test_componente_invalida_indica_la_fila(self):
        respuesta = self.enviar([("(1, 0)", "(1, 2)"), ("(0, a)", "(3, 4)")])
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["fila"], 2)


if __name__ == "__main__":
    unittest.main()
