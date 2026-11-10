"""Pruebas del Programa 7 (Métodos Numéricos) con pytest.

Desde backend/:
    python -m pytest pruebas/pruebas_programa7.py -v
Cubre: los 4 casos de Bisección y las 4 pruebas obligatorias, el parser seguro, el
graficador, la notación posicional, los errores numéricos, la propagación y la API.
"""

import math
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

RUTA_PROGRAMA4 = Path(__file__).resolve().parents[1] / "programa_4"
if str(RUTA_PROGRAMA4) not in sys.path:
    sys.path.insert(0, str(RUTA_PROGRAMA4))

from app.api import app  # noqa: E402

RUTA_PROGRAMAS = Path(__file__).resolve().parents[2] / "programas"
if str(RUTA_PROGRAMAS) not in sys.path:
    sys.path.insert(0, str(RUTA_PROGRAMAS))

import Programa7_GrupoX as p7  # noqa: E402
from modulos.numericos.parser_seguro import (  # noqa: E402
    ErrorDeEvaluacion,
    ErrorDeExpresion,
    ErrorNumerico,
    analizar_funcion,
    leer_numero,
)

TOLERANCIA = 1e-4


@pytest.fixture(scope="module")
def cliente():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Módulo A — Bisección: los 4 casos del enunciado
# ---------------------------------------------------------------------------
CASOS = [
    ("x**3 - 2*x - 5", "2", "3", 2.09455148),
    ("cos(x) - x", "0", "1", 0.73908513),
    ("x**2 - 2", "1", "2", 1.41421356),
    ("x**3 + x - 1", "0", "1", 0.68232780),
]


@pytest.mark.parametrize("funcion, a, b, raiz_esperada", CASOS)
def test_casos_del_enunciado(funcion, a, b, raiz_esperada):
    r = p7.resolver_biseccion(funcion, a, b, "1e-4", "100")
    assert r["estado"] == "convergio"
    assert abs(r["raiz"] - raiz_esperada) <= TOLERANCIA
    assert r["iteraciones_ejecutadas"] == 14
    assert r["n_min"] == 14
    assert r["cota_error"] <= TOLERANCIA
    # La raíz verdadera está dentro de la cota garantizada |raíz − xr| ≤ Eb.
    assert abs(r["raiz"] - raiz_esperada) <= r["cota_error"] + 1e-8
    # SciPy es solo contraste y debe coincidir dentro de la tolerancia.
    assert r["comparacion_scipy"]["disponible"]
    assert r["comparacion_scipy"]["diferencia"] <= TOLERANCIA


def test_tabla_registra_extremos_antes_de_actualizar():
    r = p7.resolver_biseccion("x**3 - 2*x - 5", "2", "3")
    primera, segunda = r["iteraciones"][0], r["iteraciones"][1]
    assert (primera["a"], primera["b"], primera["xr"]) == (2.0, 3.0, 2.5)
    assert primera["Ea"] is None and primera["ea_rel"] is None
    assert primera["ea_rel_nota"] == "—"
    # f(2.5) > 0 → b = xr: la fila 2 muestra el intervalo ya actualizado [2, 2.5].
    assert (segunda["a"], segunda["b"]) == (2.0, 2.5)
    assert segunda["Ea"] == pytest.approx(0.25)
    assert segunda["ea_rel"] == pytest.approx(0.25 / 2.25)
    # Eb se reduce a la mitad en cada iteración.
    for anterior, actual in zip(r["iteraciones"], r["iteraciones"][1:]):
        assert actual["Eb"] == pytest.approx(anterior["Eb"] / 2)
    assert r["nota_tabla"] == "Extremos registrados antes de actualizar el intervalo."


def test_error_relativo_no_definido_si_xr_es_cero():
    # [-3, 1]: xr₁ = −1 (a = −1), xr₂ = 0 → f(0) = 0, raíz exacta y εa "No definido".
    r = p7.resolver_biseccion("x", "-3", "1")
    assert r["estado"] == "raiz_exacta"
    ultima = r["iteraciones"][-1]
    assert ultima["xr"] == 0.0
    assert ultima["ea_rel"] is None and ultima["ea_rel_nota"] == "No definido"


def test_signo_robusto_frente_a_underflow():
    # f(a)·f(xr) ≈ 1e-401 hace underflow a 0.0; comparar signos evita elegir mal la mitad.
    r = p7.resolver_biseccion("1e-200*(x - 0.3)", "0", "1")
    assert abs(r["raiz"] - 0.3) <= TOLERANCIA


@pytest.mark.parametrize("a, b, tolerancia, esperado", [
    (2, 3, 1e-4, 14), (0, 1, 0.5, 1), (0, 1, 0.125, 3), (0, 1, 2, 1),
])
def test_iteraciones_minimas(a, b, tolerancia, esperado):
    assert p7.iteraciones_minimas(a, b, tolerancia) == esperado


# ---------------------------------------------------------------------------
# Módulo A — Las 4 pruebas obligatorias
# ---------------------------------------------------------------------------
def test_sin_cambio_de_signo_rechaza_el_intervalo():
    r = p7.resolver_biseccion("x**2 + 1", "-1", "1")
    assert r["estado"] == "sin_cambio_signo"
    assert not r["ejecutado"] and r["iteraciones"] == []
    assert "no significa que f no tenga raíces en otros intervalos" in r["mensaje"]


def test_raiz_exacta_en_el_extremo():
    r = p7.resolver_biseccion("x**2 - 1", "1", "2")
    assert r["estado"] == "raiz_en_extremo"
    assert r["raiz"] == 1.0 and r["f_raiz"] == 0.0
    assert "raíz exacta en el extremo" in r["mensaje"]
    assert not r["ejecutado"]


def test_discontinuidad_no_ejecuta_el_metodo():
    r = p7.resolver_biseccion("1/x", "-1", "1")
    assert r["estado"] == "discontinua"
    assert r["continuidad"]["estado"] == "discontinua"
    assert "x = 0" in r["continuidad"]["puntos"]
    assert "Bolzano" in r["mensaje"]
    assert not r["ejecutado"] and r["iteraciones"] == []
    assert r["comparacion_scipy"] is None


def test_nmax_insuficiente_no_garantiza_la_tolerancia():
    r = p7.resolver_biseccion("x**3 - 2*x - 5", "2", "3", "1e-4", "5")
    assert r["estado"] == "max_iter"
    assert r["iteraciones_ejecutadas"] == 5
    assert r["cota_error"] > TOLERANCIA
    assert "SIN garantía" in r["mensaje"]
    assert any("menor que n_min" in aviso for aviso in r["advertencias"])


@pytest.mark.parametrize("args, campo", [
    (("x", "1", "1"), "b"),                       # a ≥ b
    (("x", "2", "1"), "b"),
    (("x", "0", "1", "0"), "tolerancia"),         # E ≤ 0
    (("x", "0", "1", "-1e-3"), "tolerancia"),
    (("x", "0", "1", "1e-4", "0"), "max_iter"),   # Nmax < 1
    (("x", "0", "1", "1e-4", "2.5"), "max_iter"), # Nmax no entero
    (("x", "abc", "1"), "a"),                     # no numérico
    (("log(x)", "-1", "1"), "a"),                 # f(a) fuera del dominio
    (("1/(x-1)", "0", "1"), "b"),                 # f(b): división entre cero
    (("2x", "0", "1"), "funcion"),                # función mal escrita
])
def test_validaciones_de_biseccion(args, campo):
    with pytest.raises(ErrorNumerico) as error:
        p7.resolver_biseccion(*args)
    assert error.value.campo == campo
    assert error.value.mensaje


# ---------------------------------------------------------------------------
# Parser seguro
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("peligrosa", [
    "__import__('os')",
    "__import__('os').system('dir')",
    "os.system('dir')",
    "os",
    "open('archivo.txt')",
    "open(x)",
    "lambda x: x",
    "x.real",
    "(1).__class__",
    "sin.__globals__",
    "eval('1+1')",
    "exec('x=1')",
    "globals()",
    "getattr(x, 'real')",
    "[x for x in range(10)]",
    "x if x else 1",
    "'texto'",
    "x[0]",
    "x < 1",
    "x // 2",
    "sin(x, 2)",
    "y + 1",
    "True",
    "2j",
    "9**9**9",
])
def test_parser_rechaza_codigo_peligroso(peligrosa):
    with pytest.raises(ErrorDeExpresion):
        analizar_funcion(peligrosa)


@pytest.mark.parametrize("expresion, x, esperado", [
    ("x**2 - 2", 3, 7),
    ("sin(x) + cos(x)", 0, 1),
    ("tan(x) + exp(x)", 0, 1),
    ("log(e)", 5, 1),
    ("ln(x)", 1, 0),
    ("log10(x)", 1000, 3),
    ("sqrt(x) + abs(-x)", 4, 6),
    ("asin(x) + acos(x)", 0.5, math.pi / 2),
    ("atan(x) + sinh(x) + cosh(x) + tanh(x)", 0, 1),
    ("pi*x", 1, math.pi),
    ("-x**2", 3, -9),
    ("(x + 1)/(x - 1)", 3, 2),
])
def test_parser_acepta_la_lista_blanca(expresion, x, esperado):
    assert analizar_funcion(expresion)(x) == pytest.approx(esperado)


def test_parser_convierte_circunflejo_y_avisa():
    f = analizar_funcion("x^2 - 2")
    assert f.texto == "x**2 - 2"
    assert f(3) == 7          # con ^ como XOR daría otra cosa
    assert any("^" in aviso and "**" in aviso for aviso in f.avisos)


def test_parser_explica_la_multiplicacion_implicita():
    with pytest.raises(ErrorDeExpresion, match=r"2\*x"):
        analizar_funcion("2x + 1")


@pytest.mark.parametrize("expresion, x, fragmento", [
    ("1/x", 0, "división entre cero"),
    ("log(x)", -1, "dominio de log"),
    ("sqrt(x)", -4, "dominio de sqrt"),
    ("x**(1/3)", -8, "no real"),
    ("exp(x)", 1000, "overflow"),
    ("1e308*x", 10, "overflow"),
])
def test_errores_de_evaluacion_claros(expresion, x, fragmento):
    with pytest.raises(ErrorDeEvaluacion, match=fragmento):
        analizar_funcion(expresion)(x)


def test_leer_numero_acepta_constantes_y_rechaza_texto():
    assert leer_numero("pi/2", "a") == pytest.approx(math.pi / 2)
    assert leer_numero("1e-4", "E") == 1e-4
    for invalido in ("abc", "x", "1/0", "", "2,5"):
        with pytest.raises(ErrorNumerico):
            leer_numero(invalido, "a")


# ---------------------------------------------------------------------------
# Módulo B — Graficador
# ---------------------------------------------------------------------------
def test_racional_no_une_las_ramas():
    g = p7.graficar("1/x", "-2", "2")
    assert g["puntos_evaluados"] >= 1000
    assert len(g["segmentos"]) == 2
    izquierda, derecha = g["segmentos"]
    assert max(izquierda["x"]) < 0 < min(derecha["x"])
    assert "x = 0" in g["discontinuidades"]


def test_tan_se_corta_en_cada_asintota():
    g = p7.graficar("tan(x)", "-2*pi", "2*pi")
    assert len(g["segmentos"]) == 5          # asíntotas en ±π/2 y ±3π/2
    assert all(len(s["x"]) > 1 for s in g["segmentos"])


def test_log_y_sqrt_solo_donde_estan_definidas():
    g = p7.graficar("log(x)", "-1", "5")
    assert min(min(s["x"]) for s in g["segmentos"]) > 0
    assert g["puntos_descartados"] > 0
    g = p7.graficar("sqrt(4 - x**2)", "-3", "3")
    xs = [x for s in g["segmentos"] for x in s["x"]]
    assert min(xs) == pytest.approx(-2) and max(xs) == pytest.approx(2)


def test_funcion_continua_empinada_no_se_corta():
    assert len(p7.graficar("tanh(1000*x)", "-1", "1")["segmentos"]) == 1


@pytest.mark.parametrize("ejemplo", p7.EJEMPLOS_GRAFICADOR, ids=lambda e: e["tipo"])
def test_ejemplos_de_cada_tipo(ejemplo):
    g = p7.graficar(ejemplo["funcion"], ejemplo["x_min"], ejemplo["x_max"])
    assert g["segmentos"]
    for segmento in g["segmentos"]:
        assert all(math.isfinite(y) for y in segmento["y"])


def test_marcas_de_biseccion():
    g = p7.graficar("x**2 - 2", "0", "3", raiz=1.41421, intervalo=[1, 2],
                            tipo_intervalo="inicial")
    assert g["marcas"]["raiz"]["x"] == 1.41421
    assert g["marcas"]["intervalo"] == {"a": 1.0, "b": 2.0, "tipo": "inicial"}


def test_rango_invalido():
    with pytest.raises(ErrorNumerico) as error:
        p7.graficar("x", "5", "1")
    assert error.value.campo == "x_max"


# ---------------------------------------------------------------------------
# Módulo C — Notación posicional
# ---------------------------------------------------------------------------
def test_base_10_84506():
    r = p7.convertir_base("84506", "10")
    assert r["igualdad_principal"] == "(84506)₁₀ = 8·10⁴ + 4·10³ + 5·10² + 0·10¹ + 6·10⁰"
    assert r["destino"]["digitos"] == "10100101000011010"
    assert r["verificacion"]["coinciden"] and r["verificacion"]["contraste_python"]


def test_base_2_11110011_es_243():
    r = p7.convertir_base("11110011", "2")
    assert r["igualdad_principal"] == (
        "(11110011)₂ = 1·2⁷ + 1·2⁶ + 1·2⁵ + 1·2⁴ + 0·2³ + 0·2² + 1·2¹ + 1·2⁰ = "
        "128 + 64 + 32 + 16 + 2 + 1 = (243)₁₀"
    )
    assert r["destino"]["descomposicion"] == "2·10² + 4·10¹ + 3·10⁰"
    assert r["verificacion"]["valor_destino"] == "243"


def test_243_a_binario():
    r = p7.convertir_base("243", "10")
    assert r["equivalencia"] == "(243)₁₀ = (11110011)₂"
    # Divisiones sucesivas: el primer residuo es el bit de menor peso.
    assert [p["residuo"] for p in r["divisiones"]] == [1, 1, 0, 0, 1, 1, 1, 1]


def test_negativo_conserva_el_signo():
    r = p7.convertir_base("-243", "10")
    assert r["negativo"] and r["nota_signo"]
    assert r["equivalencia"] == "(−243)₁₀ = (−11110011)₂"


@pytest.mark.parametrize("numero, base", [("1012", "2"), ("12a", "10"), ("1.5", "10"),
                                          ("", "10"), ("101", "8")])
def test_digitos_invalidos(numero, base):
    with pytest.raises(ErrorNumerico):
        p7.convertir_base(numero, base)


# ---------------------------------------------------------------------------
# Módulo D — Errores numéricos
# ---------------------------------------------------------------------------
def test_error_relativo_con_xv_cero():
    r = p7.calcular_errores("0", "0.5")
    assert r["error_absoluto"] == 0.5
    assert not r["relativo_definido"]
    assert r["error_relativo"] is None and r["error_porcentual"] is None
    assert "Error relativo no definido" in r["mensaje_relativo"]


def test_errores_absoluto_relativo_y_porcentual():
    r = p7.calcular_errores("pi", "3.14")
    assert r["error_absoluto"] == pytest.approx(math.pi - 3.14)
    assert r["error_relativo"] == pytest.approx((math.pi - 3.14) / math.pi)
    assert r["error_porcentual"] == pytest.approx(100 * (math.pi - 3.14) / math.pi)


def test_propagacion_por_defecto():
    r = p7.propagar_error("sin(x) + x**2", "1", "0.01")
    assert r["derivada"] == "2*x + cos(x)"
    assert r["derivada_en_x"] == pytest.approx(math.cos(1) + 2)
    assert r["dy_aprox"] == pytest.approx((math.cos(1) + 2) * 0.01)
    assert r["dy_real"] == pytest.approx(math.sin(1.01) + 1.01 ** 2 - math.sin(1) - 1)
    assert r["diferencia"] == pytest.approx(abs(r["dy_real"] - r["dy_aprox"]))
    # Primer orden: con Δx diez veces menor la diferencia baja ~100 veces (orden Δx²).
    menor = p7.propagar_error("sin(x) + x**2", "1", "0.001")
    assert menor["diferencia"] < r["diferencia"] / 50


def test_propagacion_fuera_del_dominio():
    with pytest.raises(ErrorNumerico):
        p7.propagar_error("log(x)", "1", "-2")


def test_demostracion_de_punto_flotante():
    d = p7.demostracion_flotante()
    assert d["suma_decimal"]["resultado"] == "False"
    assert d["suma_decimal"]["repr_suma"] == "0.30000000000000004"
    assert float(d["epsilon"]["valor"]) == 2.0 ** -52
    codigos = {e["codigo"]: e for e in d["experimentos"]}
    assert codigos["math.exp(1000)"]["excepcion"].startswith("OverflowError")
    assert codigos["5e-324 / 2"]["resultado"] == "0.0"
    assert len(d["tipos_de_error"]) == 6


# ---------------------------------------------------------------------------
# API y consola
# ---------------------------------------------------------------------------
def test_api_biseccion(cliente):
    datos = cliente.post("/api/p7/biseccion",
                         json={"funcion": "cos(x) - x", "a": "0", "b": "1"}).json()
    assert datos["estado"] == "convergio" and datos["iteraciones_ejecutadas"] == 14


@pytest.mark.parametrize("ruta, cuerpo, campo", [
    ("/api/p7/biseccion", {"funcion": "x", "a": "3", "b": "2"}, "b"),
    ("/api/p7/biseccion", {"funcion": "__import__('os')", "a": "0", "b": "1"}, "funcion"),
    ("/api/p7/graficar", {"funcion": "x", "x_min": "1", "x_max": "0"}, "x_max"),
    ("/api/p7/posicional", {"numero": "102", "base": "2"}, "numero"),
    ("/api/p7/errores", {"xv": "abc", "xa": "1"}, "xv"),
    ("/api/p7/propagacion", {"funcion": "sqrt(x)", "x": "-1", "dx": "0.1"}, "x"),
])
def test_api_errores_422_en_espanol(cliente, ruta, cuerpo, campo):
    respuesta = cliente.post(ruta, json=cuerpo)
    assert respuesta.status_code == 422
    assert respuesta.json()["campo"] == campo
    assert respuesta.json()["detalle"]


@pytest.mark.parametrize("metodo, ruta, cuerpo", [
    ("post", "/api/p7/graficar", {"funcion": "(x + 1)/(x - 1)", "x_min": "-5", "x_max": "5"}),
    ("post", "/api/p7/posicional", {"numero": "11110011", "base": "2"}),
    ("get", "/api/p7/flotante", None),
    ("post", "/api/p7/errores", {"xv": "0", "xa": "0.1"}),
    ("post", "/api/p7/propagacion", {"funcion": "sin(x) + x**2", "x": "1", "dx": "0.01"}),
    ("get", "/api/p7/ejemplos", None),
])
def test_api_endpoints_responden(cliente, metodo, ruta, cuerpo):
    respuesta = getattr(cliente, metodo)(ruta, json=cuerpo) if cuerpo else getattr(cliente, metodo)(ruta)
    assert respuesta.status_code == 200


def test_menu_de_consola_tiene_la_opcion_6():
    import main
    assert main.MODULOS["6"].__name__ == "modulos.modulo_metodos_numericos"


def test_consola_y_web_usan_el_mismo_programa7():
    # Una sola copia de la matemática: la consola y la web usan programas/Programa7_GrupoX.py.
    import main
    from calculo import programa7_web
    assert main.MODULOS["6"].p7 is p7
    assert programa7_web.p7 is p7
    assert Path(p7.__file__).name == "Programa7_GrupoX.py"
