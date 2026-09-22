"""Pruebas del Programa 3 a través de la API (sin levantar el servidor).

Se ejecutan desde backend/:  python -m pruebas.pruebas_programa3
Usa `unittest` y el TestClient de FastAPI.
"""

import unittest

from fastapi.testclient import TestClient

from app.api import app


def textos(vector):
    """Vector serializado → lista de textos ("fraccion") para comparar."""
    return [valor["fraccion"] for valor in vector]


class PruebasProgramaTres(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def enviar(self, ruta, cuerpo):
        return self.cliente.post(f"/api/p3/{ruta}", json=cuerpo)

    # --- Operaciones básicas -------------------------------------------------
    def test_suma_de_vectores(self):
        respuesta = self.enviar("vectores", {"operacion": "suma", "u": ["1", "2", "3"], "v": ["4", "5", "6"]})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(textos(respuesta.json()["resultado"]), ["5", "7", "9"])

    def test_vectores_de_dimension_distinta(self):
        respuesta = self.enviar("vectores", {"operacion": "resta", "u": ["1", "2"], "v": ["1", "2", "3"]})
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "v")

    def test_producto_de_matrices(self):
        respuesta = self.enviar("producto", {
            "A": [["1", "2", "3"], ["4", "5", "6"]],
            "B": [["7", "8"], ["9", "10"], ["11", "12"]],
        })
        self.assertEqual(respuesta.status_code, 200)
        resultado = [textos(fila) for fila in respuesta.json()["resultado"]]
        self.assertEqual(resultado, [["58", "64"], ["139", "154"]])

    def test_producto_incompatible(self):
        respuesta = self.enviar("producto", {"A": [["1", "2", "3"]], "B": [["1"], ["2"]]})
        self.assertEqual(respuesta.status_code, 422)

    # --- Sistemas ------------------------------------------------------------
    def test_combinacion_lineal(self):
        respuesta = self.enviar("combinacion", {"vectores": [["1", "0"], ["0", "1"]], "b": ["3", "-2"]})
        self.assertTrue(respuesta.json()["es_combinacion"])

    def test_vectores_dependientes(self):
        respuesta = self.enviar("independencia", {"vectores": [["1", "2"], ["2", "4"]]})
        datos = respuesta.json()
        self.assertFalse(datos["independientes"])
        self.assertTrue(datos["verificaciones"][0]["coincide"])

    def test_ecuacion_con_solucion_unica(self):
        respuesta = self.enviar("ecuacion", {"A": [["2", "0"], ["0", "4"]], "b": ["2", "8"]})
        datos = respuesta.json()
        self.assertEqual(datos["clasificacion"]["tipo"], "determinado")
        self.assertEqual(textos(datos["solucion"]["valores"]), ["1", "2"])

    # --- Propiedad distributiva (opción 11) ----------------------------------
    def test_distributiva_se_cumple(self):
        respuesta = self.enviar("distributiva", {
            "A": [["1", "2", "3"], ["0", "-1", "4"]],
            "u": ["1", "0", "2"],
            "v": ["1/2", "3", "-1"],
        })
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertTrue(datos["coincide"])
        self.assertEqual(textos(datos["u_mas_v"]), ["1.5", "3", "1"])
        self.assertEqual(textos(datos["izquierda"]), textos(datos["derecha"]))
        self.assertEqual(textos(datos["izquierda"]), ["10.5", "1"])

    def test_distributiva_con_u_de_dimension_incorrecta(self):
        respuesta = self.enviar("distributiva", {
            "A": [["1", "2"], ["3", "4"]], "u": ["1", "2", "3"], "v": ["1", "2"],
        })
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "u")

    def test_distributiva_con_valor_invalido(self):
        respuesta = self.enviar("distributiva", {
            "A": [["1", "x"], ["3", "4"]], "u": ["1", "2"], "v": ["1", "2"],
        })
        datos = respuesta.json()
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual((datos["campo"], datos["fila"], datos["columna"]), ("A", 1, 2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
