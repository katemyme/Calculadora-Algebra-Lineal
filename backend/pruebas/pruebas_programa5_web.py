"""Pruebas del Programa 5 (Módulo III – Álgebra de Matrices) a través de la API.

Comprueban que la web recibe los mismos resultados que la consola, sin levantar
el servidor. Se ejecutan desde backend/:  python -m pruebas.pruebas_programa5_web
Integrantes: Grupo X — completar.
"""

import unittest

from fastapi.testclient import TestClient

from app.api import app

INVERTIBLE_3X3 = [["1", "2", "3"], ["0", "1", "4"], ["5", "6", "0"]]
INVERSA_3X3 = [["-24", "18", "5"], ["20", "-15", "-4"], ["-5", "4", "1"]]
SINGULAR_3X3 = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]
INVERTIBLE_2X2 = [["1", "2"], ["3", "4"]]
SEGUNDA_2X2 = [["0", "1"], ["1", "1"]]
OPERACIONES_DE_FILA = {
    "intercambio": {"fila_i": 1, "fila_j": 2},
    "reemplazo": {"fila_i": 2, "fila_j": 1, "k": "-3"},
    "escalamiento": {"fila_i": 1, "k": "3"},
}


def textos(matriz):
    """Matriz serializada → rejilla de textos ("fraccion") para comparar."""
    return [[valor["fraccion"] for valor in fila] for fila in matriz]


class PruebasProgramaCinco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cliente = TestClient(app)

    def enviar(self, ruta, cuerpo):
        return self.cliente.post(f"/api/p5/{ruta}", json=cuerpo)

    # --- Operaciones (opciones 1 a 5) ---------------------------------------
    def test_producto_y_no_conmutatividad(self):
        datos = self.enviar("operacion", {
            "operacion": "producto",
            "A": [["1", "2", "3"], ["4", "5", "6"]],
            "B": [["1", "0"], ["2", "1"], ["0", "3"]],
        }).json()
        self.assertEqual(textos(datos["resultado"]), [["5", "11"], ["14", "23"]])
        self.assertEqual(datos["dimension"], "2×2")
        self.assertEqual(datos["conmutatividad"]["dimension"], "3×3")
        self.assertFalse(datos["conmutatividad"]["iguales"])

    def test_producto_con_dimensiones_incompatibles(self):
        matriz_2x3 = [["1", "2", "3"], ["4", "5", "6"]]
        respuesta = self.enviar("operacion", {"operacion": "producto", "A": matriz_2x3, "B": matriz_2x3})
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(
            respuesta.json()["detalle"],
            "No se puede multiplicar: Columnas de A [3] ≠ Filas de B [2]",
        )
        self.assertEqual(respuesta.json()["campo"], "B")

    def test_producto_sin_orden_inverso(self):
        datos = self.enviar("operacion", {
            "operacion": "producto", "A": [["1", "2"]], "B": [["1", "0", "1"], ["0", "1", "1"]],
        }).json()
        self.assertEqual(datos["conmutatividad"], {"definido": False})

    def test_suma_resta_escalar_y_transpuesta(self):
        base = {"A": INVERTIBLE_2X2, "B": SEGUNDA_2X2}
        suma = self.enviar("operacion", {"operacion": "suma", **base}).json()
        resta = self.enviar("operacion", {"operacion": "resta", **base}).json()
        escalar = self.enviar("operacion", {"operacion": "escalar", "A": INVERTIBLE_2X2, "k": "3/2"}).json()
        transpuesta = self.enviar("operacion", {"operacion": "transpuesta", "A": [["1", "2", "3"]]}).json()
        self.assertEqual(textos(suma["resultado"]), [["1", "3"], ["4", "5"]])
        self.assertEqual(textos(resta["resultado"]), [["1", "1"], ["2", "3"]])
        self.assertEqual(textos(escalar["resultado"]), [["3/2", "3"], ["9/2", "6"]])
        self.assertEqual(textos(transpuesta["resultado"]), [["1"], ["2"], ["3"]])
        self.assertEqual(transpuesta["dimension"], "3×1")

    def test_suma_con_dimensiones_distintas(self):
        respuesta = self.enviar("operacion", {
            "operacion": "suma", "A": INVERTIBLE_2X2, "B": [["1", "2", "3"]],
        })
        self.assertEqual(respuesta.status_code, 422)
        self.assertIn("A es 2×2 y B es 1×3", respuesta.json()["detalle"])

    def test_escalar_vacio_o_invalido(self):
        for valor in ("", "dos"):
            respuesta = self.enviar("operacion", {"operacion": "escalar", "A": INVERTIBLE_2X2, "k": valor})
            self.assertEqual(respuesta.status_code, 422)
            self.assertEqual(respuesta.json()["campo"], "k")

    def test_celda_invalida_indica_posicion(self):
        respuesta = self.enviar("determinante", {"A": [["1", "x"], ["3", "4"]]})
        self.assertEqual(respuesta.status_code, 422)
        datos = respuesta.json()
        self.assertEqual((datos["campo"], datos["fila"], datos["columna"]), ("A", 1, 2))

    # --- Determinante (opción 6) --------------------------------------------
    def test_determinante_por_los_tres_metodos(self):
        datos = self.enviar("determinante", {"A": INVERTIBLE_3X3}).json()
        self.assertEqual(datos["determinante"]["fraccion"], "1")
        self.assertTrue(datos["coinciden"])
        self.assertEqual(datos["cofactores"]["valor"]["fraccion"], "1")
        self.assertEqual(
            [termino["cofactor"]["fraccion"] for termino in datos["cofactores"]["terminos"]],
            ["-24", "20", "-5"],
        )
        self.assertEqual(datos["sarrus"]["valor"]["fraccion"], "1")
        reduccion = datos["reduccion"]
        self.assertEqual(reduccion["operaciones"], ["F₃ → F₃ - 5·F₁", "F₃ → F₃ + 4·F₂"])
        self.assertEqual([valor["fraccion"] for valor in reduccion["diagonal"]], ["1", "1", "1"])
        self.assertEqual((reduccion["intercambios"], reduccion["signo"]), (0, "+1"))
        self.assertTrue(datos["diagnostico"]["invertible"])
        self.assertEqual(
            datos["diagnostico"]["texto"],
            "La matriz es invertible: det(A) ≠ 0, tiene 3 posiciones pivote, "
            "sus columnas son L.I. y generan ℝ³",
        )

    def test_determinante_de_matriz_singular(self):
        datos = self.enviar("determinante", {"A": SINGULAR_3X3}).json()
        self.assertEqual(datos["determinante"]["fraccion"], "0")
        self.assertTrue(datos["coinciden"])
        self.assertEqual(
            datos["diagnostico"],
            {
                "invertible": False,
                "texto": "La matriz es singular (no tiene inversa): det(A) = 0",
                "pivotes": 2,
                "n": 3,
            },
        )

    def test_sarrus_solo_en_3x3_e_intercambio_cambia_el_signo(self):
        datos = self.enviar("determinante", {"A": [["0", "2"], ["3", "4"]]}).json()
        self.assertIsNone(datos["sarrus"])
        self.assertEqual(datos["reduccion"]["operaciones"], ["F₁ ↔ F₂"])
        self.assertEqual(datos["reduccion"]["signo"], "−1")
        self.assertEqual(datos["determinante"]["fraccion"], "-6")

    def test_determinante_exige_matriz_cuadrada(self):
        respuesta = self.enviar("determinante", {"A": [["1", "2", "3"], ["4", "5", "6"]]})
        self.assertEqual(respuesta.status_code, 422)
        self.assertIn("matriz cuadrada", respuesta.json()["detalle"])

    # --- Inversa (opciones 7 y 8) -------------------------------------------
    def test_inversa_por_gauss_jordan(self):
        datos = self.enviar("inversa", {"metodo": "gauss_jordan", "A": INVERTIBLE_3X3}).json()
        self.assertEqual(textos(datos["inversa"]), INVERSA_3X3)
        self.assertEqual(datos["pivotes"], 3)
        self.assertEqual(datos["columnas_pivote"], [0, 1, 2])
        self.assertEqual([fila[3:] for fila in textos(datos["aumentada_final"])], INVERSA_3X3)
        self.assertEqual([paso["notacion"] for paso in datos["pasos_detalle"]], datos["pasos"])
        self.assertEqual(textos(datos["pasos_detalle"][-1]["matriz"]), textos(datos["aumentada_final"]))
        self.assertTrue(datos["comprobacion"]["es_identidad"])

    def test_inversa_por_adjunta_coincide(self):
        datos = self.enviar("inversa", {"metodo": "adjunta", "A": INVERTIBLE_3X3}).json()
        self.assertEqual(textos(datos["inversa"]), INVERSA_3X3)
        self.assertEqual(datos["determinante"]["fraccion"], "1")
        self.assertTrue(datos["comprobacion"]["es_identidad"])

    def test_adjunta_de_2x2(self):
        datos = self.enviar("inversa", {"metodo": "adjunta", "A": INVERTIBLE_2X2}).json()
        self.assertEqual(textos(datos["cofactores"]), [["4", "-3"], ["-2", "1"]])
        self.assertEqual(textos(datos["adjunta"]), [["4", "-2"], ["-3", "1"]])
        self.assertEqual(textos(datos["inversa"]), [["-2", "1"], ["3/2", "-1/2"]])

    def test_matriz_singular_no_tiene_inversa(self):
        for metodo in ("gauss_jordan", "adjunta"):
            datos = self.enviar("inversa", {"metodo": metodo, "A": SINGULAR_3X3}).json()
            self.assertIsNone(datos["inversa"])
            self.assertIsNone(datos["comprobacion"])
            self.assertFalse(datos["diagnostico"]["invertible"])
            self.assertEqual(datos["diagnostico"]["pivotes"], 2)
        por_gauss_jordan = self.enviar("inversa", {"metodo": "gauss_jordan", "A": SINGULAR_3X3}).json()
        self.assertEqual(por_gauss_jordan["columnas_pivote"], [0, 1])

    # --- Verificador (opción 9) ---------------------------------------------
    def verificar(self, **cambios):
        cuerpo = {"A": INVERTIBLE_2X2, "B": SEGUNDA_2X2, **OPERACIONES_DE_FILA, **cambios}
        return self.enviar("verificador", cuerpo)

    def test_propiedades_de_la_inversa(self):
        propiedades = self.verificar().json()["propiedades"]
        self.assertEqual([p["numero"] for p in propiedades], [1, 2, 3, 4])
        self.assertTrue(all(p["cumple"] and p["conclusion"] == "«Se cumple»" for p in propiedades))
        self.assertEqual(textos(propiedades[1]["izquierda"]["valor"]), [["7/2", "-3/2"], ["-2", "1"]])
        self.assertEqual(textos(propiedades[1]["derecha"]["valor"]), [["7/2", "-3/2"], ["-2", "1"]])
        self.assertEqual(textos(propiedades[2]["izquierda"]["valor"]), [["-2", "3/2"], ["1", "-1/2"]])
        self.assertEqual(propiedades[3]["izquierda"]["valor"]["fraccion"], "-1/2")
        self.assertEqual(propiedades[3]["derecha"]["valor"]["fraccion"], "-1/2")

    def test_operaciones_de_fila(self):
        operaciones = self.verificar().json()["operaciones_fila"]
        self.assertEqual(operaciones["determinante"]["fraccion"], "-2")
        casos = {caso["id"]: caso for caso in operaciones["casos"]}
        self.assertEqual(casos["intercambio"]["notacion"], "F₁ ↔ F₂")
        self.assertEqual(casos["intercambio"]["izquierda"]["valor"]["fraccion"], "2")
        self.assertEqual(casos["reemplazo"]["notacion"], "F₂ → F₂ - 3·F₁")
        self.assertEqual(casos["reemplazo"]["izquierda"]["valor"]["fraccion"], "-2")
        self.assertEqual(casos["escalamiento"]["izquierda"]["valor"]["fraccion"], "-6")
        self.assertTrue(all(caso["cumple"] for caso in casos.values()))

    def test_propiedad_triangular(self):
        triangular = self.verificar(
            A=INVERTIBLE_3X3, B=[["1", "0", "0"], ["0", "2", "0"], ["0", "0", "3"]]
        ).json()["triangular"]
        self.assertEqual(triangular["reduccion"]["operaciones"], ["F₃ → F₃ - 5·F₁", "F₃ → F₃ + 4·F₂"])
        self.assertEqual(triangular["izquierda"]["valor"]["fraccion"], "1")
        self.assertEqual(triangular["derecha"]["valor"]["fraccion"], "1")
        self.assertTrue(triangular["cumple"])

    def test_determinante_del_producto(self):
        producto = self.verificar().json()["determinante_producto"]
        self.assertEqual(textos(producto["AB"]), [["2", "3"], ["4", "7"]])
        self.assertEqual((producto["det_A"]["fraccion"], producto["det_B"]["fraccion"]), ("-2", "-1"))
        self.assertEqual(producto["enunciado"], "det(AB) = det(A)·det(B)")
        self.assertEqual(producto["izquierda"]["valor"]["fraccion"], "2")
        self.assertEqual(producto["derecha"]["valor"]["fraccion"], "2")
        self.assertTrue(producto["cumple"])

    def test_paso_a_paso(self):
        datos = self.verificar().json()
        procedimientos = datos["procedimientos"]
        # Toda clave que cita una propiedad tiene su procedimiento.
        listas = [propiedad["pasos"] for propiedad in datos["propiedades"]]
        listas += [caso["pasos"] for caso in datos["operaciones_fila"]["casos"]]
        listas += [datos["triangular"]["pasos"], datos["determinante_producto"]["pasos"]]
        self.assertTrue(all(clave in procedimientos for lista in listas for clave in lista))

        inversa_A = procedimientos["inversa_A"]
        self.assertEqual(inversa_A["titulo"], "A⁻¹ por Gauss-Jordan: [A | I] → [I | A⁻¹]")
        self.assertEqual(textos(inversa_A["inversa"]), [["-2", "1"], ["3/2", "-1/2"]])
        producto = procedimientos["producto_de_inversas"]["resultado"]["matriz"]
        self.assertEqual(textos(producto), [["7/2", "-3/2"], ["-2", "1"]])
        transpuesta = procedimientos["transpuesta_A"]["destino"]["matriz"]
        self.assertEqual(textos(transpuesta), [["1", "3"], ["2", "4"]])

        reduccion = procedimientos["det_A"]["reduccion"]
        self.assertEqual([paso["notacion"] for paso in reduccion["pasos_detalle"]], ["F₂ → F₂ - 3·F₁"])
        self.assertEqual(textos(reduccion["pasos_detalle"][-1]["matriz"]), textos(reduccion["triangular"]))

        terminos = procedimientos["cofactores_A"]["terminos"]
        self.assertEqual([textos(termino["menor"]) for termino in terminos], [[["4"]], [["3"]]])
        self.assertEqual(
            [(termino["signo"], termino["cofactor"]["fraccion"]) for termino in terminos],
            [("+", "4"), ("−", "-3")],
        )

        cuentas = {clave: p["cuenta"] for clave, p in procedimientos.items() if p["tipo"] == "cuenta"}
        self.assertEqual(cuentas["cuenta_inverso_det"], "1/det(A) = 1/(-2) = -1/2")
        self.assertEqual(cuentas["cuenta_producto_det"], "det(A)·det(B) = (-2)·(-1) = 2")
        self.assertEqual(cuentas["cuenta_intercambio"], "−det(A) = −(-2) = 2")
        self.assertEqual(cuentas["cuenta_escalamiento"], "k·det(A) = (3)·(-2) = -6")

    def test_verificador_rechaza_matriz_singular(self):
        respuesta = self.verificar(B=[["1", "2"], ["2", "4"]])
        self.assertEqual(respuesta.status_code, 422)
        self.assertEqual(respuesta.json()["campo"], "B")
        self.assertIn("singular", respuesta.json()["detalle"])

    def test_verificador_valida_filas_y_factor(self):
        casos = [
            ({"intercambio": {"fila_i": 1, "fila_j": 1}}, "intercambio", "distintas"),
            ({"reemplazo": {"fila_i": 3, "fila_j": 1, "k": "2"}}, "reemplazo", "no existe"),
            ({"escalamiento": {"fila_i": 1, "k": "0"}}, "escalamiento", "distinto de 0"),
            ({"escalamiento": {"fila_i": 1, "k": "1/0"}}, "escalamiento", "no es un número"),
        ]
        for cambios, campo, fragmento in casos:
            respuesta = self.verificar(**cambios)
            self.assertEqual(respuesta.status_code, 422)
            self.assertEqual(respuesta.json()["campo"], campo)
            self.assertIn(fragmento, respuesta.json()["detalle"])

    def test_verificador_en_1x1_omite_intercambio_y_reemplazo(self):
        respuesta = self.enviar("verificador", {
            "A": [["5"]], "B": [["2"]], "escalamiento": {"fila_i": 1, "k": "4"},
        })
        self.assertEqual(respuesta.status_code, 200)
        casos = respuesta.json()["operaciones_fila"]["casos"]
        self.assertEqual([caso["id"] for caso in casos], ["escalamiento"])
        self.assertEqual(casos[0]["izquierda"]["valor"]["fraccion"], "20")

    # --- Teoremas (opción 0) ------------------------------------------------
    def test_teoremas_clave(self):
        respuesta = self.cliente.get("/api/p5/teoremas")
        self.assertEqual(respuesta.status_code, 200)
        bloques = respuesta.json()["bloques"]
        self.assertEqual(len(bloques), 4)
        inversa = bloques[1]
        self.assertTrue(inversa["titulo"].startswith("TEOREMA DE LA INVERSA"))
        self.assertEqual(inversa["enunciados"][0], "(a) (A⁻¹)⁻¹ = A")
        self.assertEqual(bloques[3]["enunciados"], ["A⁻¹ = (1/det A)·adj(A)"])


if __name__ == "__main__":
    unittest.main()
