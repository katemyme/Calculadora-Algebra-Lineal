"""Pruebas del Programa 9 (Newton-Raphson) con pytest.

Verifica los 3 casos obligatorios, el error absoluto cuando xᵢ₊₁ = 0, las condiciones de
fallo, las validaciones, la tabla (Pandas), la gráfica (Matplotlib) y los endpoints HTTP.
Ejecución desde backend/:
    python -m pytest pruebas/pruebas_programa9.py -v
"""

import base64
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


def resolver_caso(indice: int):
    caso = p9.CASOS_NEWTON[indice]
    return p9.resolver_newton_raphson(caso["funcion"], caso["x0"], caso["tolerancia"],
                                      caso["max_iter"])


def test_caso1_convergencia():
    r = resolver_caso(0)
    assert r["estado"] == "convergencia" and r["convergio"] is True
    assert r["derivada"] == "3*x**2 - 2"
    assert r["aproximacion"] == pytest.approx(2.0945514815, abs=1e-9)
    assert r["iteraciones"] == 4
    assert r["error_final"] <= r["tolerancia"]
    assert r["residuo"] < 1e-10
    # Se muestran solo las cifras que respalda la tolerancia (no "raíz exacta").
    assert r["aproximacion_texto"] == "2.0946"


def test_primera_fila_aplica_la_formula():
    fila = resolver_caso(0)["filas"][0]
    assert (fila["xi"], fila["fxi"], fila["dfxi"]) == (2.0, -1.0, 10.0)
    assert fila["x_siguiente"] == pytest.approx(2.1)          # 2 − (−1)/10
    assert fila["error"] == pytest.approx(0.1 / 2.1 * 100)   # εa (%)
    assert fila["tipo_error"] == "relativo"


def test_caso2_derivada_nula_se_detiene_sin_dividir():
    r = resolver_caso(1)
    assert r["estado"] == "derivada_nula" and r["convergio"] is False
    assert r["iteraciones"] == 0
    fila = r["filas"][0]
    assert fila["dfxi"] == 0 and fila["x_siguiente"] is None
    assert r["residuo"] == pytest.approx(4.0)


def test_derivada_casi_nula():
    r = p9.resolver_newton_raphson("x**2 - 4", "1e-12")
    assert r["estado"] == "derivada_nula"
    assert abs(r["filas"][0]["dfxi"]) < p9.DERIVADA_MINIMA


def test_caso3_oscilacion_agota_nmax():
    r = resolver_caso(2)
    assert r["estado"] == "max_iteraciones" and r["convergio"] is False
    assert r["iteraciones"] == 20
    assert [fila["x_siguiente"] for fila in r["filas"][:4]] == [1.0, 0.0, 1.0, 0.0]
    # xᵢ₊₁ = 0: no se divide entre cero, se usa el error absoluto.
    assert r["filas"][1]["tipo_error"] == "absoluto"
    assert r["filas"][1]["error"] == 1.0


def test_convergencia_con_error_absoluto_en_cero():
    r = p9.resolver_newton_raphson("sin(x)", "0.5")
    assert r["estado"] == "convergencia"
    assert r["aproximacion"] == 0.0
    assert r["filas"][-1]["tipo_error"] == "absoluto"


def test_fuera_de_dominio():
    r = p9.resolver_newton_raphson("log(x)", "3")
    assert r["estado"] == "fuera_de_dominio"
    assert r["filas"][-1]["fxi"] is None


def test_divergencia_por_valores_no_finitos():
    r = p9.metodo_newton_raphson(lambda x: 1e300, lambda x: 1e-9, 0.0, 1e-4, 50)
    assert r["estado"] == "divergencia"


@pytest.mark.parametrize("campo, datos", [
    ("funcion", ("x**", "1", "0.0001", "50")),
    ("funcion", ("5", "1", "0.0001", "50")),
    ("x0", ("x**2 - 4", "abc", "0.0001", "50")),
    ("x0", ("log(x)", "-1", "0.0001", "50")),
    ("tolerancia", ("x**2 - 4", "1", "0", "50")),
    ("tolerancia", ("x**2 - 4", "1", "150", "50")),
    ("max_iter", ("x**2 - 4", "1", "0.0001", "0")),
    ("max_iter", ("x**2 - 4", "1", "0.0001", "2.5")),
])
def test_validaciones(campo, datos):
    with pytest.raises(p9.ErrorNumerico) as error:
        p9.resolver_newton_raphson(*datos)
    assert error.value.campo == campo


def test_tolerancia_con_signo_de_porcentaje():
    r = p9.resolver_newton_raphson("x**2 - 2", "1", "0.0001 %", "50")
    assert r["tolerancia"] == 0.0001 and r["convergio"] is True


def test_tabla_pandas_y_grafica_matplotlib():
    r = resolver_caso(0)
    tabla = p9.construir_tabla(r["filas"])
    assert list(tabla.columns) == p9.COLUMNAS_TABLA
    assert len(tabla) == len(r["filas"])
    png = base64.b64decode(p9.grafica_png(p9.datos_grafica(r)))
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_api_newton():
    caso = p9.CASOS_NEWTON[0]
    resp = cliente.post("/api/p9/newton", json={
        "funcion": caso["funcion"], "x0": caso["x0"],
        "tolerancia": caso["tolerancia"], "max_iter": caso["max_iter"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["estado"] == "convergencia"
    assert data["tabla"]["columnas"] == p9.COLUMNAS_TABLA
    assert data["grafica_png"]

    resp_error = cliente.post("/api/p9/newton", json={"funcion": "x**2", "x0": "1",
                                                      "tolerancia": "-1"})
    assert resp_error.status_code == 422
    assert resp_error.json()["campo"] == "tolerancia"


def test_api_ejemplos():
    resp = cliente.get("/api/p9/ejemplos")
    assert resp.status_code == 200
    assert len(resp.json()["casos"]) == 3
