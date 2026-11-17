"""Pruebas automatizadas del Programa 8 (Jacobi y Gauss-Seidel).

Verifica los 3 casos obligatorios, validaciones de entrada y los endpoints HTTP.
Ejecución desde backend/:
    python -m pytest pruebas/pruebas_programa8.py -v
"""

from pathlib import Path
import sys

from fastapi.testclient import TestClient
import pytest

from app.api import app

_RUTA_PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
if str(_RUTA_PROGRAMAS) not in sys.path:
    sys.path.insert(0, str(_RUTA_PROGRAMAS))

import Programa8_GrupoX as p8  # noqa: E402

cliente = TestClient(app)


def test_caso1_convergencia_diagonal_dominante():
    caso = p8.CASOS_PRUEBA_P8[0]
    res = p8.resolver_sistemas_iterativos(
        caso["A"], caso["b"], caso["x0"], caso["tolerancia"], caso["max_iter"]
    )
    assert res["ejecutado"] is True
    assert res["dominancia"]["es_estrictamente_dominante"] is True
    assert res["reordenamiento"]["reordenado"] is False
    assert res["jacobi"]["convergio"] is True
    assert res["gauss_seidel"]["convergio"] is True
    # Gauss-Seidel debe converger en menos iteraciones que Jacobi en este sistema
    assert res["gauss_seidel"]["iteraciones_usadas"] < res["jacobi"]["iteraciones_usadas"]
    assert pytest.approx(res["gauss_seidel"]["solucion"], abs=1e-4) == [2.0, 4.0, 3.0]
    assert res["validacion_referencia"]["disponible"] is True
    assert res["validacion_referencia"]["diferencia_gauss_seidel"] < 1e-4


def test_caso2_reordenamiento_por_cero_en_diagonal():
    caso = p8.CASOS_PRUEBA_P8[1]
    res = p8.resolver_sistemas_iterativos(
        caso["A"], caso["b"], caso["x0"], caso["tolerancia"], caso["max_iter"], True
    )
    assert res["ejecutado"] is True
    assert res["reordenamiento"]["reordenado"] is True
    assert 1 in res["reordenamiento"]["ceros_diagonal_inicial"]
    assert res["dominancia"]["es_estrictamente_dominante"] is True
    assert res["gauss_seidel"]["convergio"] is True
    assert pytest.approx(res["gauss_seidel"]["solucion"], abs=1e-4) == [1.0, 2.0, 3.0]


def test_caso2_sin_reordenamiento_posible_no_colapsa():
    # Columna 1 completamente nula: ninguna permutación evita el cero en la diagonal
    A_sin_sol = [
        ["0", "2", "1"],
        ["0", "3", "-1"],
        ["0", "1", "4"],
    ]
    res = p8.resolver_sistemas_iterativos(A_sin_sol, ["3", "2", "5"], ["0", "0", "0"])
    assert res["ejecutado"] is False
    assert res["reordenamiento"]["posible_sin_ceros"] is False


def test_caso3_advertencia_no_convergencia():
    caso = p8.CASOS_PRUEBA_P8[2]
    res = p8.resolver_sistemas_iterativos(
        caso["A"],
        caso["b"],
        caso["x0"],
        caso["tolerancia"],
        caso["max_iter"],
        caso["permitir_reordenamiento"],
    )
    assert res["ejecutado"] is True
    assert res["dominancia"]["es_estrictamente_dominante"] is False
    assert "SUFICIENTE pero NO NECESARIA" in res["dominancia"]["mensaje"]
    assert res["jacobi"]["convergio"] is False
    assert res["gauss_seidel"]["convergio"] is False

def test_endpoint_api_p8():
    caso = p8.CASOS_PRUEBA_P8[0]
    resp = cliente.post(
        "/api/p8/iterativos",
        json={
            "A": caso["A"],
            "b": caso["b"],
            "x0": caso["x0"],
            "tolerancia": caso["tolerancia"],
            "max_iter": caso["max_iter"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["jacobi"]["convergio"] is True
    assert data["gauss_seidel"]["convergio"] is True

    # Error de validación (tolerancia negativa -> HTTP 422)
    resp_err = cliente.post(
        "/api/p8/iterativos",
        json={"A": caso["A"], "b": caso["b"], "x0": caso["x0"], "tolerancia": "-0.01"},
    )
    assert resp_err.status_code == 422
    assert resp_err.json()["campo"] == "tolerancia"