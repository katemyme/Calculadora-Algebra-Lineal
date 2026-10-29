"""Pruebas de Vectores → Demostración de subespacio a través de la API.

Se ejecutan desde backend/:  python -m pruebas.pruebas_subespacio
"""

import unittest

from fastapi.testclient import TestClient

from app.api import app


class PruebasSubespacio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def enviar(self, conjunto, hipotesis=""):
        return self.cliente.post(
            "/api/p4/subespacio", json={"conjunto": conjunto, "hipotesis": hipotesis}
        )

    def estados(self, datos):
        return [d["cumple"] for d in datos["demostraciones"]]

    # Ejemplos de la Sesión 13 -------------------------------------------------
    def test_ejemplo_1_recta_y_igual_2x(self):
        datos = self.enviar("H = (x, y)", "y = 2x").json()
        self.assertTrue(datos["es_subespacio"])
        self.assertEqual(self.estados(datos), [True, True, True, True])
        self.assertEqual(datos["estructura"]["dimension"], 1)

    def test_ejemplo_2_plano(self):
        datos = self.enviar("W = (x, y, z)", "x - y + z = 0").json()
        self.assertTrue(datos["es_subespacio"])
        estructura = datos["estructura"]
        self.assertEqual(estructura["dimension"], 2)
        base = [[v["fraccion"] for v in b] for b in estructura["base"]]
        self.assertEqual(base, [["1", "1", "0"], ["-1", "0", "1"]])
        self.assertTrue(estructura["independencia"]["trivial"])

    def test_ejemplo_3_no_contiene_al_cero(self):
        datos = self.enviar("H = (x, y, z)", "x + y - 3 = 2z").json()
        self.assertFalse(datos["es_subespacio"])
        self.assertEqual(self.estados(datos), [True, False, None, None])
        self.assertIsNone(datos["estructura"])

    def test_forma_parametrica(self):
        datos = self.enviar("H = (t - 2s, -s, t)", "t, s ∈ ℝ").json()
        self.assertTrue(datos["es_subespacio"])
        self.assertEqual(datos["modo"], "parametrica")
        self.assertEqual(datos["estructura"]["dimension"], 2)

    def test_conjunto_con_nombre_s_y_sin_hipotesis(self):
        datos = self.enviar("s=(x,y,z)").json()
        self.assertEqual(datos["nombre"], "S")
        self.assertTrue(datos["es_subespacio"])
        self.assertEqual(datos["estructura"]["dimension"], 3)

    def test_hipotesis_dentro_del_conjunto(self):
        datos = self.enviar("H = {(x, y, z) ∈ R3 : z = x - 3y}").json()
        self.assertTrue(datos["es_subespacio"])

    # Reglas no lineales y desigualdades: contraejemplos -----------------------
    def test_parabola_falla_por_contraejemplo(self):
        datos = self.enviar("H = (x, y)", "y = x^2").json()
        self.assertFalse(datos["es_subespacio"])
        self.assertEqual(self.estados(datos)[2:], [False, False])

    def test_semiplano_falla_solo_el_escalar(self):
        datos = self.enviar("H = (x, y)", "x >= 0").json()
        self.assertEqual(self.estados(datos), [True, True, True, False])

    def test_generadores_dependientes(self):
        datos = self.enviar("H = (t + s, t + s)").json()
        estructura = datos["estructura"]
        self.assertFalse(estructura["independencia"]["trivial"])
        self.assertEqual(estructura["dimension"], 1)

    # Errores de entrada ---------------------------------------------------------
    def test_variable_desconocida(self):
        respuesta = self.enviar("H = (x, y)", "z = 0")
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "hipotesis")

    def test_conjunto_mal_escrito(self):
        respuesta = self.enviar("H = (x, y", "x = y")
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "conjunto")


if __name__ == "__main__":
    unittest.main()
