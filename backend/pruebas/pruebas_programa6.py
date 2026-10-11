"""Pruebas del PROGRAMA 6 (Factorización LU y solución de Ax = b).

Comprueban el módulo de cálculo y su ruta web sin levantar el servidor.
Se ejecutan desde backend/:  python -m pruebas.pruebas_programa6
Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

import unittest
from fractions import Fraction

from fastapi.testclient import TestClient

from app.api import app
from calculo.programa6_web import p6

SISTEMA_3X3 = [["2", "1", "-1"], ["-3", "-1", "2"], ["-2", "1", "2"]]
TERMINOS_3X3 = ["8", "-11", "-3"]


def fracciones(rejilla):
    """Rejilla de enteros o textos → matriz de Fraction."""
    return [[Fraction(valor) for valor in fila] for fila in rejilla]


def textos(matriz):
    """Matriz serializada → rejilla de textos ("fraccion") para comparar."""
    return [[valor["fraccion"] for valor in fila] for fila in matriz]


def texto_vector(vector):
    """Vector serializado → lista de textos ("fraccion")."""
    return [valor["fraccion"] for valor in vector]


class PruebasModuloLU(unittest.TestCase):
    def test_factorizacion_3x3(self):
        A = fracciones(SISTEMA_3X3)
        L, U, operaciones = p6.factorizar_lu(A)
        self.assertEqual(L, fracciones([[1, 0, 0], ["-3/2", 1, 0], [-1, 4, 1]]))
        self.assertEqual(U, fracciones([[2, 1, -1], [0, "1/2", "1/2"], [0, 0, -1]]))
        self.assertEqual(len(operaciones), 3)
        self.assertTrue(p6.verificar_factorizacion(A, L, U)[1])

    def test_l_tiene_unos_en_la_diagonal_y_ceros_arriba(self):
        L, _, _ = p6.factorizar_lu(fracciones([[4, 3, 2], [8, 7, 9], [12, 5, 1]]))
        for fila in range(3):
            self.assertEqual(L[fila][fila], 1)
            for columna in range(fila + 1, 3):
                self.assertEqual(L[fila][columna], 0)

    def test_pivote_nulo_exige_permutacion(self):
        with self.assertRaises(p6.FactorizacionLUNoAdmitida) as contexto:
            p6.factorizar_lu(fracciones([[0, 2], [3, 4]]))
        self.assertEqual(str(contexto.exception), p6.MENSAJE_SIN_FACTORIZACION)
        self.assertEqual((contexto.exception.fila, contexto.exception.columna), (0, 0))

    def test_pivote_nulo_tras_eliminar(self):
        with self.assertRaises(p6.FactorizacionLUNoAdmitida) as contexto:
            p6.factorizar_lu(fracciones([[1, 2, 3], [2, 4, 5], [1, 1, 1]]))
        self.assertEqual((contexto.exception.fila, contexto.exception.columna), (1, 1))

    def test_matriz_rectangular(self):
        A = fracciones([[1, 2, 3], [2, 4, 7]])
        L, U, _ = p6.factorizar_lu(A)
        self.assertEqual(L, fracciones([[1, 0], [2, 1]]))
        self.assertEqual(U, fracciones([[1, 2, 3], [0, 0, 1]]))
        self.assertTrue(p6.verificar_factorizacion(A, L, U)[1])

    def test_matriz_alta(self):
        A = fracciones([[1, 2], [3, 4], [5, 6]])
        L, U, _ = p6.factorizar_lu(A)
        self.assertEqual(p6.dimension(L), (3, 3))
        self.assertEqual(p6.dimension(U), (3, 2))
        self.assertTrue(p6.verificar_factorizacion(A, L, U)[1])

    def test_doble_sustitucion(self):
        A = fracciones(SISTEMA_3X3)
        b = [Fraction(valor) for valor in TERMINOS_3X3]
        L, U, _ = p6.factorizar_lu(A)
        y, x = p6.resolver_con_lu(L, U, b)
        self.assertEqual(y, [Fraction(8), Fraction(1), Fraction(1)])
        self.assertEqual(x, [Fraction(2), Fraction(3), Fraction(-1)])
        self.assertEqual(p6.verificar_solucion(A, x, b), (b, True))

    def test_matriz_singular_no_tiene_solucion_unica(self):
        L, U, _ = p6.factorizar_lu(fracciones([[1, 2], [2, 4]]))
        _, x = p6.resolver_con_lu(L, U, [Fraction(1), Fraction(2)])
        self.assertIsNone(x)


class PruebasProgramaSeisWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def enviar(self, cuerpo):
        return self.cliente.post("/api/p6/lu", json=cuerpo)

    def test_factoriza_y_resuelve(self):
        datos = self.enviar({"A": SISTEMA_3X3, "b": TERMINOS_3X3}).json()
        self.assertTrue(datos["admite_lu"])
        self.assertEqual(textos(datos["L"]), [["1", "0", "0"], ["-3/2", "1", "0"], ["-1", "4", "1"]])
        self.assertEqual(datos["verificacion"]["mensaje"], "La factorización es correcta (L · U == A)")
        self.assertEqual(texto_vector(datos["sistema"]["adelante"]["y"]), ["8", "1", "1"])
        self.assertEqual(texto_vector(datos["sistema"]["atras"]["x"]), ["2", "3", "-1"])
        self.assertEqual(datos["sistema"]["comprobacion"]["mensaje"], "Comprobación exitosa: A · x == b")

    def test_cada_paso_trae_su_multiplicador(self):
        datos = self.enviar({"A": SISTEMA_3X3, "b": TERMINOS_3X3}).json()
        primero = datos["pasos"][0]
        self.assertEqual(primero["nombre_multiplicador"], "ℓ₂₁")
        self.assertEqual(primero["multiplicador"]["fraccion"], "-3/2")
        self.assertEqual(len(datos["pasos"]), len(datos["operaciones"]))

    def test_matriz_sin_factorizacion(self):
        datos = self.enviar({"A": [["0", "2"], ["3", "4"]], "b": ["1", "2"]}).json()
        self.assertFalse(datos["admite_lu"])
        self.assertEqual(
            datos["mensaje"],
            "La matriz no admite Factorización LU sin permutación "
            "(requiere pivoteo parcial PA = LU)",
        )
        self.assertEqual((datos["bloqueo"]["fila"], datos["bloqueo"]["columna"]), (0, 0))

    def test_rectangular_no_resuelve_sistema(self):
        datos = self.enviar({"A": [["1", "2", "3"], ["2", "4", "7"]]}).json()
        self.assertTrue(datos["verificacion"]["correcta"])
        self.assertIsNone(datos["sistema"])

    def test_singular_explica_por_que_no_hay_x(self):
        datos = self.enviar({"A": [["1", "2"], ["2", "4"]], "b": ["1", "2"]}).json()
        self.assertIsNone(datos["sistema"]["atras"])
        self.assertIn("singular", datos["sistema"]["motivo"])

    def test_componente_invalida_de_b(self):
        respuesta = self.enviar({"A": [["1", "2"], ["2", "5"]], "b": ["1", "x"]})
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "b")
        self.assertEqual(respuesta.json()["fila"], 2)

    def test_teoremas_incluyen_la_factorizacion_lu(self):
        bloques = self.cliente.get("/api/p5/teoremas").json()["bloques"]
        self.assertTrue(any(bloque["titulo"].startswith("FACTORIZACIÓN LU") for bloque in bloques))


if __name__ == "__main__":
    unittest.main()
