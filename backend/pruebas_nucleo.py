"""Pruebas del núcleo matemático.

Se ejecutan sin levantar la API:  python pruebas_nucleo.py
Usa únicamente `unittest` de la biblioteca estándar.
"""

import unittest
from fractions import Fraction

from nucleo import (
    ErrorDeEntrada,
    calcular_rangos,
    construir_matriz_aumentada,
    escalonar,
    parsear_valor,
    resolver_sistema,
)


def _valores_solucion(resultado):
    """Extrae {indice_variable: Fraction} de una solución determinada."""
    return {
        item["variable"]: item["valor"]
        for item in resultado["solucion"]["valores"]
    }


class PruebasParseo(unittest.TestCase):
    """parsear_valor y construir_matriz_aumentada."""

    def test_entero_negativo_decimal_y_fraccion(self):
        self.assertEqual(parsear_valor("3"), Fraction(3))
        self.assertEqual(parsear_valor("-7"), Fraction(-7))
        self.assertEqual(parsear_valor("2.5"), Fraction(5, 2))
        self.assertEqual(parsear_valor("1/3"), Fraction(1, 3))
        self.assertEqual(parsear_valor("-4/6"), Fraction(-2, 3))

    def test_celda_vacia_es_cero(self):
        self.assertEqual(parsear_valor(""), Fraction(0))
        self.assertEqual(parsear_valor("   "), Fraction(0))

    def test_valor_invalido_lanza_error_con_texto_recibido(self):
        with self.assertRaises(ErrorDeEntrada) as contexto:
            parsear_valor("hola")
        self.assertIn("hola", str(contexto.exception))

    def test_division_entre_cero(self):
        with self.assertRaises(ErrorDeEntrada):
            parsear_valor("1/0")

    def test_celda_invalida_indica_fila_y_columna(self):
        with self.assertRaises(ErrorDeEntrada) as contexto:
            construir_matriz_aumentada(2, 2, [["1", "2", "3"], ["x", "5", "6"]])
        error = contexto.exception
        self.assertEqual(error.fila, 2)
        self.assertEqual(error.columna, 1)

    def test_dimensiones_fuera_de_rango(self):
        with self.assertRaises(ErrorDeEntrada):
            construir_matriz_aumentada(0, 2, [])
        with self.assertRaises(ErrorDeEntrada):
            construir_matriz_aumentada(2, 99, [["1"] * 100, ["1"] * 100])


class PruebasCasosDeLaTabla(unittest.TestCase):
    """Los tres casos que el estudiante debe capturar."""

    def test_solucion_unica(self):
        datos = [
            ["2", "1", "-1", "8"],
            ["-3", "-1", "2", "-11"],
            ["-2", "1", "2", "-3"],
        ]
        resultado = resolver_sistema(3, 3, datos)
        self.assertEqual(resultado["clasificacion"]["tipo"], "determinado")
        self.assertEqual(resultado["rango_A"], 3)
        self.assertEqual(resultado["rango_Ab"], 3)

        valores = _valores_solucion(resultado)
        self.assertEqual(valores[0], Fraction(2))    # x = 2
        self.assertEqual(valores[1], Fraction(3))    # y = 3
        self.assertEqual(valores[2], Fraction(-1))   # z = -1

        self.assertTrue(all(c["coincide"] for c in resultado["verificacion"]))

    def test_infinitas_soluciones(self):
        datos = [
            ["1", "2", "3", "6"],
            ["2", "4", "6", "12"],
            ["1", "1", "1", "3"],
        ]
        resultado = resolver_sistema(3, 3, datos)
        self.assertEqual(resultado["clasificacion"]["tipo"], "indeterminado")
        self.assertEqual(resultado["rango_A"], 2)
        self.assertEqual(resultado["rango_Ab"], 2)
        self.assertEqual(resultado["clasificacion"]["grados_de_libertad"], 1)
        self.assertEqual(resultado["solucion"]["variables_libres"], [2])
        self.assertTrue(all(c["coincide"] for c in resultado["verificacion"]))

    def test_sin_solucion(self):
        datos = [
            ["1", "1", "1", "3"],
            ["2", "2", "2", "7"],
            ["1", "-1", "1", "1"],
        ]
        resultado = resolver_sistema(3, 3, datos)
        self.assertEqual(resultado["clasificacion"]["tipo"], "inconsistente")
        self.assertLess(resultado["rango_A"], resultado["rango_Ab"])
        self.assertIsNotNone(resultado["solucion"]["fila_contradictoria"])
        self.assertEqual(resultado["verificacion"], [])


class PruebasSistemasNoCuadrados(unittest.TestCase):
    """m != n."""

    def test_mas_incognitas_que_ecuaciones(self):
        # 2 ecuaciones, 3 incógnitas -> como mucho rango 2 < 3 -> indeterminado.
        datos = [
            ["1", "1", "1", "1"],
            ["1", "-1", "1", "3"],
        ]
        resultado = resolver_sistema(2, 3, datos)
        self.assertEqual(resultado["clasificacion"]["tipo"], "indeterminado")
        self.assertEqual(resultado["rango_A"], 2)
        self.assertTrue(all(c["coincide"] for c in resultado["verificacion"]))

    def test_mas_ecuaciones_que_incognitas_determinado(self):
        # 3 ecuaciones, 2 incógnitas, compatibles -> solución única x=2, y=1.
        datos = [
            ["1", "1", "3"],
            ["1", "-1", "1"],
            ["2", "2", "6"],
        ]
        resultado = resolver_sistema(3, 2, datos)
        self.assertEqual(resultado["clasificacion"]["tipo"], "determinado")
        valores = _valores_solucion(resultado)
        self.assertEqual(valores[0], Fraction(2))
        self.assertEqual(valores[1], Fraction(1))
        self.assertTrue(all(c["coincide"] for c in resultado["verificacion"]))


class PruebasColumnaDeCeros(unittest.TestCase):
    """Una columna íntegramente nula produce una variable libre."""

    def test_columna_nula_es_variable_libre(self):
        # La segunda incógnita (índice 1) no aparece en ninguna ecuación.
        datos = [
            ["1", "0", "2", "5"],
            ["0", "0", "1", "1"],
        ]
        resultado = resolver_sistema(2, 3, datos)
        self.assertEqual(resultado["clasificacion"]["tipo"], "indeterminado")
        self.assertIn(1, resultado["solucion"]["variables_libres"])
        self.assertTrue(all(c["coincide"] for c in resultado["verificacion"]))


class PruebasEntradasFraccionarias(unittest.TestCase):
    """Aritmética exacta con Fraction."""

    def test_sistema_con_fracciones(self):
        # (1/2)x + (1/3)y = 1 ;  (1/4)x - y = 0
        datos = [
            ["1/2", "1/3", "1"],
            ["1/4", "-1", "0"],
        ]
        resultado = resolver_sistema(2, 2, datos)
        self.assertEqual(resultado["clasificacion"]["tipo"], "determinado")
        valores = _valores_solucion(resultado)
        # Resolviendo a mano: x = 12/7, y = 3/7.
        self.assertEqual(valores[0], Fraction(12, 7))
        self.assertEqual(valores[1], Fraction(3, 7))
        self.assertTrue(all(c["coincide"] for c in resultado["verificacion"]))


class PruebasComponentesInternos(unittest.TestCase):
    """escalonar y calcular_rangos de forma aislada."""

    def test_escalonar_deja_identidad_en_caso_determinado(self):
        Ab = construir_matriz_aumentada(
            2, 2, [["1", "1", "5"], ["1", "-1", "1"]]
        )
        reducida, pasos, columnas_pivote = escalonar(Ab, 2, 2)
        self.assertEqual(columnas_pivote, [0, 1])
        self.assertEqual(reducida[0][:2], [Fraction(1), Fraction(0)])
        self.assertEqual(reducida[1][:2], [Fraction(0), Fraction(1)])
        self.assertGreater(len(pasos), 0)

    def test_calcular_rangos_detecta_fila_contradictoria(self):
        matriz = [
            [Fraction(1), Fraction(0), Fraction(2)],
            [Fraction(0), Fraction(0), Fraction(3)],
        ]
        rango_a, rango_ab = calcular_rangos(matriz, 2, 2, [0])
        self.assertEqual(rango_a, 1)
        self.assertEqual(rango_ab, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
