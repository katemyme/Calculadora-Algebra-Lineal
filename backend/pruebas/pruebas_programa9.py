"""Pruebas del Programa 9 (métodos abiertos) con pytest.

Verifica los 3 casos obligatorios, los ejemplos de la clase (Sesión 22), los dos criterios de
parada, el paso a paso, la convergencia, la secante, las derivadas numéricas, los polinomios
(Horner y deflación), las validaciones, las gráficas (Matplotlib) y los endpoints HTTP.
Ejecución desde backend/:
    python -m pytest pruebas/pruebas_programa9.py -v
"""

import base64
import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import app

_RUTA_PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
if str(_RUTA_PROGRAMAS) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMAS))

import Programa9_GrupoX as p9  # noqa: E402

cliente = TestClient(app)


def newton(caso):
    """Resuelve un caso precargado de Newton-Raphson."""
    return p9.resolver_newton_raphson(caso["funcion"], caso["x0"], caso["tolerancia"], caso["max_iter"],
                                      caso["tipo_error"], caso.get("derivada", "analitica"), caso.get("h"))


def buscar(lista, id_):
    """Ejemplo precargado por su id."""
    return next(caso for caso in lista if caso["id"] == id_)


# --- Newton-Raphson: casos obligatorios ---------------------------------------------------
def test_caso1_convergencia():
    r = newton(p9.CASOS_NEWTON[0])
    assert r["estado"] == "convergencia" and r["convergio"] is True
    assert r["derivada"] == "3*x**2 - 2"
    assert r["aproximacion"] == pytest.approx(2.0945514815, abs=1e-9)
    assert r["iteraciones"] == 4
    assert r["error_rel_final"] < r["criterio"]["tolerancia"]
    assert r["residuo"] < 1e-10
    assert r["convergencia"]["orden"] == pytest.approx(2, abs=0.1)  # convergencia cuadrática


def test_primera_fila_tiene_los_dos_errores():
    fila = newton(p9.CASOS_NEWTON[0])["filas"][0]
    assert (fila["xi"], fila["fxi"], fila["dfxi"]) == (2.0, -1.0, 10.0)
    assert fila["x_siguiente"] == pytest.approx(2.1)              # 2 − (−1)/10
    assert fila["error_abs"] == pytest.approx(0.1)                # Eₐ = |x₁ − x₀|
    assert fila["error_rel"] == pytest.approx(0.1 / 2.1 * 100)    # εₐ (%)


def test_caso2_derivada_nula_se_detiene_sin_dividir():
    r = newton(p9.CASOS_NEWTON[1])
    assert r["estado"] == "derivada_nula" and r["convergio"] is False
    assert r["iteraciones"] == 0
    fila = r["filas"][0]
    assert fila["dfxi"] == 0 and fila["x_siguiente"] is None
    assert r["residuo"] == pytest.approx(4.0)
    assert r["pasos"][0]["pasos"][-1]["titulo"] == "¿Se puede dividir?"


def test_derivada_casi_nula():
    r = p9.resolver_newton_raphson("x**2 - 4", "1e-12")
    assert r["estado"] == "derivada_nula"
    assert abs(r["filas"][0]["dfxi"]) < p9.DERIVADA_MINIMA


def test_caso3_oscilacion_agota_nmax():
    r = newton(p9.CASOS_NEWTON[2])
    assert r["estado"] == "max_iteraciones" and r["convergio"] is False
    assert r["iteraciones"] == 20
    assert [fila["x_siguiente"] for fila in r["filas"][:4]] == [1.0, 0.0, 1.0, 0.0]
    # xᵢ₊₁ = 0: εₐ(%) no se calcula (no se divide entre cero) y se usa Eₐ.
    assert r["filas"][1]["error_rel"] is None and r["filas"][1]["error_abs"] == 1.0


def test_convergencia_con_error_absoluto_en_cero():
    r = p9.resolver_newton_raphson("sin(x)", "0.5")
    assert r["estado"] == "convergencia"
    assert r["aproximacion"] == 0.0
    assert r["filas"][-1]["error_rel"] is None


def test_fuera_de_dominio():
    r = p9.resolver_newton_raphson("log(x)", "3")
    assert r["estado"] == "fuera_de_dominio"
    assert r["filas"][-1]["fxi"] is None


def test_divergencia_por_valores_no_finitos():
    criterio = {"tipo": "relativo", "tolerancia": 1e-4, "max_iter": 50}
    r = p9.metodo_newton_raphson(lambda x: 1e300, lambda x: 1e-9, 0.0, criterio)
    assert r["estado"] == "divergencia"


# --- Ejemplos de la clase, criterio de parada y convergencia -------------------------------
@pytest.mark.parametrize("id_, iteraciones, raiz", [
    ("clase_ej1", 4, 0.567143),
    ("clase_ej3", 42, 1.0),
    ("clase_doble", 14, 1.0),
    ("clase_ciclo_ok", 4, -1.769292),
    ("clase_tarea4", 6, 0.619061),
])
def test_ejemplos_de_la_clase(id_, iteraciones, raiz):
    r = newton(buscar(p9.EJEMPLOS_CLASE, id_))
    assert r["estado"] == "convergencia"
    assert r["iteraciones"] == iteraciones
    assert r["aproximacion"] == pytest.approx(raiz, abs=1e-4)


def test_cifras_segun_el_error_alcanzado():
    r = newton(buscar(p9.EJEMPLOS_CLASE, "clase_ej1"))
    assert r["aproximacion_texto"] == "0.567143"   # Eₐ = 1.25e-07 → 6 decimales


def test_criterio_absoluto_vs_relativo():
    absoluto = p9.resolver_newton_raphson("x**10 - 1", "0.5", "0.0001", "60", "absoluto")
    relativo = p9.resolver_newton_raphson("x**10 - 1", "0.5", "0.0001", "60", "relativo")
    assert absoluto["criterio"]["tipo"] == "absoluto" and absoluto["iteraciones"] == 42
    assert relativo["criterio"]["tipo"] == "relativo" and relativo["iteraciones"] == 43


def test_raiz_doble_converge_linealmente():
    r = newton(buscar(p9.EJEMPLOS_CLASE, "clase_doble"))
    assert r["convergencia"]["orden"] == pytest.approx(1, abs=0.05)
    assert "multiplicidad m ≈ 2.0" in r["convergencia"]["texto"]


def test_newton_con_diferencia_central():
    r = newton(buscar(p9.EJEMPLOS_CLASE, "clase_tarea7"))
    assert r["derivada_usada"] == "central" and r["h"] == 1e-5
    assert r["aproximacion"] == pytest.approx(2.0945514815, abs=1e-9)
    central, analitica = r["comparacion"]["metodos"]
    assert central["iteraciones"] == analitica["iteraciones"]


def test_paso_a_paso_de_newton():
    r = newton(p9.CASOS_NEWTON[0])
    assert len(r["pasos"]) == len(r["filas"])
    titulos = [p["titulo"] for p in r["pasos"][0]["pasos"]]
    assert titulos == ["Evaluar f(x₀)", "Evaluar f′(x₀)", "Aplicar la fórmula de Newton",
                       "Error absoluto", "Error relativo porcentual", "¿Se detiene?"]
    assert r["pasos"][0]["pasos"][0]["texto"] == "f(2) = (2)**3 - 2*(2) - 5 = -1"
    assert r["pasos"][-1]["pasos"][-1]["texto"].startswith("Sí:")


@pytest.mark.parametrize("campo, datos", [
    ("funcion", ("x**", "1")),
    ("funcion", ("5", "1")),
    ("x0", ("x**2 - 4", "abc")),
    ("x0", ("log(x)", "-1")),
    ("tolerancia", ("x**2 - 4", "1", "0")),
    ("tolerancia", ("x**2 - 4", "1", "150")),
    ("tolerancia", ("x**2 - 4", "1", "0.01 %", "50", "absoluto")),
    ("max_iter", ("x**2 - 4", "1", "0.0001", "0")),
    ("max_iter", ("x**2 - 4", "1", "0.0001", "2.5")),
    ("tipo_error", ("x**2 - 4", "1", "0.0001", "50", "cuadratico")),
    ("derivada", ("x**2 - 4", "1", "0.0001", "50", "relativo", "simbolica")),
    ("h", ("x**2 - 4", "1", "0.0001", "50", "relativo", "central", "0")),
])
def test_validaciones(campo, datos):
    with pytest.raises(p9.ErrorNumerico) as error:
        p9.resolver_newton_raphson(*datos)
    assert error.value.campo == campo


def test_tolerancia_con_signo_de_porcentaje():
    r = p9.resolver_newton_raphson("x**2 - 2", "1", "0.0001 %", "50")
    assert r["criterio"]["tolerancia"] == 0.0001 and r["convergio"] is True


# --- Secante --------------------------------------------------------------------------------
@pytest.mark.parametrize("id_, iteraciones, raiz, iteraciones_newton", [
    ("sec_practica2", 4, 0.7390851, 4),
    ("sec_tarea1", 6, 2.0945514815, 4),
])
def test_secante_ejemplos_de_la_clase(id_, iteraciones, raiz, iteraciones_newton):
    c = buscar(p9.EJEMPLOS_SECANTE, id_)
    r = p9.resolver_secante(c["funcion"], c["x0"], c["x1"], c["tolerancia"], c["max_iter"], c["tipo_error"])
    assert r["estado"] == "convergencia" and r["iteraciones"] == iteraciones
    assert r["aproximacion"] == pytest.approx(raiz, abs=1e-6)
    assert r["comparacion"]["metodos"][1]["iteraciones"] == iteraciones_newton
    assert r["filas"][0]["i"] == 1        # la secante numera desde 1 (usa x₀ y x₁)


def test_secante_pendiente_nula_y_validacion():
    r = p9.resolver_secante("x**2 - 4", "-1", "1")
    assert r["estado"] == "pendiente_nula" and r["iteraciones"] == 0
    with pytest.raises(p9.ErrorNumerico) as error:
        p9.resolver_secante("x**2 - 4", "1", "1")
    assert error.value.campo == "x1"


# --- Derivadas numéricas ------------------------------------------------------------------
def test_derivadas_ejemplo_de_la_clase():
    r = p9.calcular_derivadas("x**3 - 2*x - 5", "2", "0.01")
    valores = {f["clave"]: f["valor"] for f in r["formulas"]}
    assert valores["adelante"] == pytest.approx(10.0601)
    assert valores["atras"] == pytest.approx(9.9401)
    assert valores["central"] == pytest.approx(10.0001)
    assert r["exacta"] == 10


def test_derivadas_practica4_logaritmo():
    r = p9.calcular_derivadas("log(x)", "1", "0.1")
    valores = {f["clave"]: f["valor"] for f in r["formulas"]}
    assert round(valores["adelante"], 4) == 0.9531
    assert round(valores["central"], 4) == 1.0034


def test_central_es_mas_precisa_y_analisis_de_h():
    r = p9.calcular_derivadas("sin(x)", "pi/4", "0.1")
    errores = {f["clave"]: f["error_abs"] for f in r["formulas"]}
    assert errores["central"] < errores["adelante"] and errores["central"] < errores["atras"]
    # El h óptimo de la central (O(h²)) es mayor que el de adelante (O(h)).
    assert r["analisis_h"]["optimos"]["central"] > r["analisis_h"]["optimos"]["adelante"]


# --- Polinomios: Horner, Newton y deflación -----------------------------------------------
def test_horner_evalua_p_y_su_derivada():
    p, dp, _, _ = p9.horner([1, -6, 11, -6], 4)
    assert (p, dp) == (6, 11)     # p(4) = 64 − 96 + 44 − 6 ; p′(4) = 48 − 48 + 11
    cociente, residuo = p9.deflacion([1, -6, 11, -6], 1)
    assert cociente == [1, -5, 6] and residuo == 0


def _raices(reporte):
    return sorted((round(z["real"], 6), round(z["imag"], 6)) for z in reporte["raices"])


@pytest.mark.parametrize("id_, esperadas", [
    ("pol_tarea6", [(1, -1), (1, 0), (1, 1), (2, 0)]),
    ("pol_tarea3", [(1, 0), (2, 0), (3, 0)]),
    ("pol_clase", [(-1, 0), (1, -1), (1, 0), (1, 1), (2, 0)]),
])
def test_polinomios_horner_y_deflacion(id_, esperadas):
    c = buscar(p9.EJEMPLOS_POLINOMIO, id_)
    r = p9.resolver_polinomio(c["polinomio"], c["x0"], c["tolerancia"], c["max_iter"], c["tipo_error"])
    assert r["estado"] == "completo"
    assert _raices(r) == [(float(a), float(b)) for a, b in esperadas]
    assert all(z["residuo"] < 1e-9 for z in r["raices"])
    assert len(r["validacion"]["todas"]) == r["grado"]


def test_polinomio_por_coeficientes_y_validaciones():
    r = p9.resolver_polinomio("1, -6, 11, -6", "0")
    assert r["polinomio"] == "x³ - 6x² + 11x - 6"
    for texto in ("sin(x)", "x**11 + 1", "5"):
        with pytest.raises(p9.ErrorNumerico) as error:
            p9.resolver_polinomio(texto, "0")
        assert error.value.campo == "polinomio"


# --- Gráficas (Matplotlib) y respuestas JSON ------------------------------------------------
def test_graficas_matplotlib_y_json_sin_nan():
    reportes = [newton(p9.CASOS_NEWTON[2]),
                p9.resolver_secante("cos(x) - x", "0.5", "0.6"),
                p9.calcular_derivadas("log(x)", "1", "0.1"),
                p9.resolver_polinomio("x**3 - 6*x**2 + 11*x - 6", "0")]
    for reporte in reportes:
        graficas = p9.graficas_png(reporte)
        assert graficas
        for grafica in graficas:
            assert base64.b64decode(grafica["png"])[:8] == b"\x89PNG\r\n\x1a\n"
        json.dumps(reporte, allow_nan=False)


# --- Endpoints HTTP -------------------------------------------------------------------------
def test_api_newton():
    resp = cliente.post("/api/p9/newton", json={"funcion": "exp(-x) - x", "x0": "0", "tolerancia": "0.0001",
                                               "max_iter": "50", "tipo_error": "absoluto"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["estado"] == "convergencia" and data["iteraciones"] == 4
    assert data["tabla"]["columnas"][5] == "Eₐ = |xᵢ₊₁ − xᵢ|"
    assert [g["id"] for g in data["graficas"]] == ["funcion", "errores"]
    assert data["pasos"][0]["etiqueta"] == "i = 0"

    error = cliente.post("/api/p9/newton", json={"funcion": "x**2", "x0": "1", "tolerancia": "-1"})
    assert error.status_code == 422 and error.json()["campo"] == "tolerancia"


def test_api_secante_derivadas_y_polinomio():
    resp = cliente.post("/api/p9/secante", json={"funcion": "cos(x) - x", "x0": "0.5", "x1": "0.6",
                                                "tolerancia": "1e-5", "tipo_error": "absoluto"})
    assert resp.status_code == 200 and resp.json()["iteraciones"] == 4
    resp = cliente.post("/api/p9/derivadas", json={"funcion": "x**3 - 2*x - 5", "x": "2", "h": "0.01"})
    assert resp.status_code == 200 and resp.json()["exacta"] == 10
    resp = cliente.post("/api/p9/polinomio", json={"polinomio": "x**3 - 6*x**2 + 11*x - 6", "x0": "0"})
    assert resp.status_code == 200 and resp.json()["estado"] == "completo"
    error = cliente.post("/api/p9/secante", json={"funcion": "x", "x0": "1", "x1": "1"})
    assert error.status_code == 422 and error.json()["campo"] == "x1"


def test_api_ejemplos():
    resp = cliente.get("/api/p9/ejemplos")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["casos"]) == 3
    assert {"clase", "secante", "derivadas", "polinomios", "por_defecto"} <= set(data)
