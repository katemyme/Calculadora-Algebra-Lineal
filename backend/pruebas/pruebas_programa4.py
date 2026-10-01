"""Pruebas del Programa 4 (Vectores → Independencia Lineal) a través de la API.

Se ejecutan desde backend/:  python -m pruebas.pruebas_programa4
"""

import unittest

from fastapi.testclient import TestClient

from app.api import app


class PruebasProgramaCuatro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def enviar(self, vectores):
        return self.cliente.post("/api/p4/independencia", json={"vectores": vectores})

    def test_base_canonica_es_li(self):
        datos = self.enviar([["1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]]).json()
        self.assertEqual(datos["veredicto"], "L.I.")
        self.assertEqual(datos["pivotes"], 3)
        self.assertEqual(datos["variables_libres"], 0)

    def test_vector_multiplo_es_ld(self):
        datos = self.enviar([["1", "2", "3"], ["2", "4", "6"], ["1", "0", "1"]]).json()
        self.assertEqual(datos["veredicto"], "L.D.")
        self.assertEqual(datos["pivotes"], 2)
        self.assertEqual(datos["columnas_libres"], [1])

    def test_mas_vectores_que_dimension_es_ld(self):
        datos = self.enviar([["1", "0"], ["0", "1"], ["2", "3"]]).json()
        self.assertEqual(datos["veredicto"], "L.D.")
        self.assertEqual(datos["variables_libres"], 1)

    def test_matriz_reducida_exacta(self):
        datos = self.enviar([["2", "4"], ["1", "3"]]).json()
        reducida = [[v["fraccion"] for v in fila] for fila in datos["matriz_reducida"]]
        self.assertEqual(reducida, [["1", "0", "0"], ["0", "1", "0"]])

    def test_pasos_detalle_trae_la_matriz_de_cada_operacion(self):
        datos = self.enviar([["2", "4"], ["1", "3"]]).json()
        detalle = datos["pasos_detalle"]
        self.assertEqual([p["notacion"] for p in detalle], datos["pasos"])
        self.assertEqual(detalle[0]["tipo"], "intercambio")
        ultima = [[v["fraccion"] for v in fila] for fila in detalle[-1]["matriz"]]
        self.assertEqual(ultima, [["1", "0", "0"], ["0", "1", "0"]])

    def test_componente_invalida_indica_celda(self):
        respuesta = self.enviar([["1", "x"], ["0", "0"]])
        self.assertEqual(respuesta.status_code, 422)
        datos = respuesta.json()
        self.assertEqual((datos["campo"], datos["fila"], datos["columna"]), ("vectores", 2, 1))


if __name__ == "__main__":
    unittest.main()
