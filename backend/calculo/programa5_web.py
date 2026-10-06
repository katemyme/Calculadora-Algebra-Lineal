"""Adaptador web del Programa 5 (Módulo III: Álgebra de Matrices).

Todo el álgebra se hace en ``backend/programa_4/modulos/modulo_matrices.py``. Este
archivo solo convierte el texto recibido por HTTP en fracciones exactas, llama a las
funciones de cálculo del módulo y organiza sus resultados para el frontend.
Integrantes: Grupo X — completar.
"""

import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from calculo.nucleo import ErrorDeEntrada, parsear_valor
from calculo.programa3_web import ErrorDeCampo
from calculo.transpuesta import _leer_matriz as leer_matriz

# El Programa 5 importa sus paquetes ("modulos", "teoremas") de forma relativa
# a la carpeta programa_4, así que esa carpeta debe estar en sys.path.
_RUTA_CALCULADORA = Path(__file__).resolve().parents[1] / "programa_4"
if str(_RUTA_CALCULADORA) not in sys.path:
    sys.path.insert(0, str(_RUTA_CALCULADORA))

from modulos import modulo_matrices as p5m  # noqa: E402

Matriz = List[List[Fraction]]

_OPERACIONES_BINARIAS = {
    "suma": p5m.sumar_matrices,
    "resta": p5m.restar_matrices,
    "producto": p5m.multiplicar_matrices,
}


def _orden(matriz: Matriz) -> str:
    """Dimensión de la matriz como texto 'm×n'."""
    return p5m.texto_dimension(p5m.dimension(matriz))


def _leer_cuadrada(datos: List[List[str]], campo: str) -> Matriz:
    """Lee una matriz y exige que sea cuadrada (requisito de determinante e inversa)."""
    matriz = leer_matriz(datos, campo)
    try:
        p5m.validar_cuadrada(matriz)
    except ValueError as error:
        raise ErrorDeCampo(f"Matriz {campo}: {error}", campo=campo)
    return matriz


def _leer_invertible(datos: List[List[str]], campo: str) -> Matriz:
    """Lee una matriz cuadrada y exige que sea invertible (requisito del verificador)."""
    matriz = _leer_cuadrada(datos, campo)
    if p5m.determinante_por_reduccion(matriz) == 0:
        raise ErrorDeCampo(
            f"{campo} es singular (det({campo}) = 0): el verificador necesita "
            "matrices invertibles.",
            campo=campo,
        )
    return matriz


def _leer_numero(texto: Optional[str], campo: str, nombre: str) -> Fraction:
    """Convierte a Fraction un número suelto (escalar o factor de fila)."""
    # En una rejilla la celda vacía vale 0, pero un escalar suelto vacío es un olvido.
    if texto is None or str(texto).strip() == "":
        raise ErrorDeCampo(f"Escriba un valor para {nombre}.", campo=campo)
    try:
        return parsear_valor(str(texto))
    except ErrorDeEntrada:
        raise ErrorDeCampo(
            f"{nombre} no es un número válido: '{str(texto).strip()}'. "
            "Use enteros, decimales o fracciones (p. ej. -3, 2.5, 1/2).",
            campo=campo,
        )


def _diagnostico(matriz: Matriz) -> Dict:
    """Diagnóstico de invertibilidad del módulo junto con sus posiciones pivote."""
    pivotes = p5m.contar_pivotes(matriz)
    return {
        "invertible": pivotes == len(matriz),
        "texto": p5m.diagnostico_invertibilidad(matriz),
        "pivotes": pivotes,
        "n": len(matriz),
    }


def _igualdad(nombres: Tuple[str, str], miembros: Tuple) -> Dict:
    """Arma una igualdad: sus dos miembros, si coinciden y el veredicto del módulo."""
    izquierdo, derecho = miembros
    cumple = izquierdo == derecho
    return {
        "enunciado": f"{nombres[0]} = {nombres[1]}",
        "izquierda": {"nombre": nombres[0], "valor": izquierdo},
        "derecha": {"nombre": nombres[1], "valor": derecho},
        "cumple": cumple,
        "conclusion": p5m.conclusion(cumple),
    }


def _aplicar_binaria(operacion: str, A: Matriz, B: Matriz) -> Matriz:
    """Calcula A + B, A − B o A·B; un error de dimensiones se atribuye a B."""
    try:
        return _OPERACIONES_BINARIAS[operacion](A, B)
    except ValueError as error:
        raise ErrorDeCampo(str(error), campo="B")


def _conmutatividad(A: Matriz, B: Matriz, producto_ab: Matriz) -> Dict:
    """Calcula B·A cuando está definido e indica si coincide con A·B."""
    if p5m.dimension(B)[1] != p5m.dimension(A)[0]:
        return {"definido": False}
    producto_ba = p5m.multiplicar_matrices(B, A)
    return {
        "definido": True,
        "BA": producto_ba,
        "dimension": _orden(producto_ba),
        "iguales": producto_ab == producto_ba,
    }


def operar(
    operacion: str, a_txt: List[List[str]], b_txt: List[List[str]], k_txt: Optional[str]
) -> Dict:
    """Opciones 1 a 5 del módulo: A + B, A − B, k·A, A·B o Aᵀ."""
    A = leer_matriz(a_txt, "A")
    respuesta: Dict = {"operacion": operacion, "A": A}
    if operacion == "transpuesta":
        resultado = p5m.transponer(A)
    elif operacion == "escalar":
        respuesta["k"] = _leer_numero(k_txt, "k", "el escalar k")
        resultado = p5m.multiplicar_por_escalar(respuesta["k"], A)
    else:
        respuesta["B"] = leer_matriz(b_txt, "B")
        resultado = _aplicar_binaria(operacion, A, respuesta["B"])
    if operacion == "producto":
        respuesta["conmutatividad"] = _conmutatividad(A, respuesta["B"], resultado)
    respuesta.update(resultado=resultado, dimension=_orden(resultado))
    return respuesta


def _expansion_por_cofactores(A: Matriz) -> Dict:
    """Términos a₁ⱼ·C₁ⱼ de la expansión sobre la primera fila y el determinante."""
    terminos = [
        {"entrada": A[0][columna], "cofactor": p5m.cofactor(A, 0, columna)}
        for columna in range(len(A))
    ]
    return {"terminos": terminos, "valor": p5m.determinante_por_cofactores(A)}


def _regla_de_sarrus(A: Matriz) -> Optional[Dict]:
    """Sumas de diagonales de la regla de Sarrus; None si la matriz no es 3×3."""
    if len(A) != 3:
        return None
    descendentes, ascendentes = p5m.sumas_de_sarrus(A)
    return {
        "descendentes": descendentes,
        "ascendentes": ascendentes,
        "valor": p5m.determinante_por_sarrus(A),
    }


def _reduccion_triangular(A: Matriz) -> Dict:
    """Reducción a triangular con lo necesario para mostrar det = ± producto de la diagonal."""
    triangular, intercambios, factores, operaciones = p5m.reducir_a_triangular(A)
    return {
        "operaciones": operaciones,
        "triangular": triangular,
        "diagonal": [fila[indice] for indice, fila in enumerate(triangular)],
        "producto_diagonal": p5m.producto_diagonal(triangular),
        "intercambios": intercambios,
        "signo": "+1" if intercambios % 2 == 0 else "−1",
        "factores": factores,
        "valor": p5m.determinante_desde_triangular(triangular, intercambios),
    }


def calcular_determinante(a_txt: List[List[str]]) -> Dict:
    """Opción 6: det(A) por cofactores, Sarrus (si es 3×3) y reducción triangular."""
    A = _leer_cuadrada(a_txt, "A")
    metodos = {
        "cofactores": _expansion_por_cofactores(A),
        "sarrus": _regla_de_sarrus(A),
        "reduccion": _reduccion_triangular(A),
    }
    valores = [metodo["valor"] for metodo in metodos.values() if metodo is not None]
    return {
        "A": A,
        "n": len(A),
        **metodos,
        "determinante": valores[0],
        "coinciden": valores.count(valores[0]) == len(valores),
        "diagnostico": _diagnostico(A),
    }


def _columnas_pivote(reducida: Matriz, orden: int) -> List[int]:
    """Columnas del bloque izquierdo con pivote: el primer valor no nulo de cada fila."""
    columnas = []
    for fila in reducida:
        for columna in range(orden):
            if fila[columna] != 0:
                columnas.append(columna)
                break
    return columnas


def _por_gauss_jordan(A: Matriz) -> Dict:
    """Desarrollo de la opción 7: [A | I], cada operación de fila y la matriz final."""
    historial: list = []
    inversa, reducida, pasos, pivotes = p5m.invertir_por_gauss_jordan(A, historial)
    return {
        "aumentada_inicial": p5m.construir_aumentada_con_identidad(A),
        "aumentada_final": reducida,
        "pasos": pasos,
        # Lo mismo que `pasos`, con la matriz que queda tras cada operación.
        "pasos_detalle": [
            {"notacion": notacion, "tipo": tipo, "columna_pivote": columna, "matriz": estado}
            for notacion, (tipo, columna, estado) in zip(pasos, historial)
        ],
        "columnas_pivote": _columnas_pivote(reducida, len(A)),
        "pivotes": pivotes,
        "inversa": inversa,
    }


def _por_adjunta(A: Matriz) -> Dict:
    """Desarrollo de la opción 8: cofactores, adjunta, determinante e inversa."""
    inversa, adjunta, valor_determinante = p5m.invertir_por_adjunta(A)
    return {
        # C = (adj A)ᵀ porque (Cᵀ)ᵀ = C: así no se recalculan los n² cofactores.
        "cofactores": p5m.transponer(adjunta),
        "adjunta": adjunta,
        "determinante": valor_determinante,
        "inversa": inversa,
    }


def _comprobacion(A: Matriz, inversa: Optional[Matriz]) -> Optional[Dict]:
    """Producto A·A⁻¹ y si es exactamente I; None cuando no hay inversa."""
    if inversa is None:
        return None
    producto, es_identidad = p5m.verificar_inversa(A, inversa)
    return {"producto": producto, "es_identidad": es_identidad}


def calcular_inversa(metodo: str, a_txt: List[List[str]]) -> Dict:
    """Opciones 7 y 8: A⁻¹ por Gauss-Jordan sobre [A | I] o por la matriz adjunta."""
    A = _leer_cuadrada(a_txt, "A")
    desarrollo = _por_gauss_jordan(A) if metodo == "gauss_jordan" else _por_adjunta(A)
    return {
        "metodo": metodo,
        "A": A,
        "n": len(A),
        **desarrollo,
        "comprobacion": _comprobacion(A, desarrollo["inversa"]),
        "diagnostico": _diagnostico(A),
    }


def _propiedades_de_la_inversa(A: Matriz, B: Matriz) -> List[Dict]:
    """Propiedades 1 a 4: los dos miembros de cada igualdad y su veredicto."""
    casos = [
        ("matriz", ("(A⁻¹)⁻¹", "A"), p5m.miembros_inversa_de_la_inversa(A)),
        ("matriz", ("(AB)⁻¹", "B⁻¹A⁻¹"), p5m.miembros_inversa_del_producto(A, B)),
        ("matriz", ("(Aᵀ)⁻¹", "(A⁻¹)ᵀ"), p5m.miembros_inversa_de_la_transpuesta(A)),
        ("escalar", ("det(A⁻¹)", "1/det(A)"), p5m.miembros_determinante_de_la_inversa(A)),
    ]
    return [
        {"numero": numero, "tipo": tipo, **_igualdad(nombres, miembros)}
        for numero, (tipo, nombres, miembros) in enumerate(casos, start=1)
    ]


def _indice_de_fila(numero_fila: int, orden: int, operacion: str) -> int:
    """Valida un número de fila (base 1) y lo devuelve en base 0."""
    if not 1 <= numero_fila <= orden:
        raise ErrorDeCampo(
            f"{operacion.capitalize()}: la fila {numero_fila} no existe; "
            f"elija una entre 1 y {orden}.",
            campo=operacion,
        )
    return numero_fila - 1


def _dos_filas(datos: Optional[Dict], orden: int, operacion: str) -> Tuple[int, int]:
    """Valida las dos filas distintas de un intercambio o un reemplazo (base 0)."""
    if datos is None:
        raise ErrorDeCampo(f"Indique las filas del {operacion}.", campo=operacion)
    fila_i = _indice_de_fila(datos["fila_i"], orden, operacion)
    fila_j = _indice_de_fila(datos["fila_j"], orden, operacion)
    if fila_i == fila_j:
        raise ErrorDeCampo(
            f"{operacion.capitalize()}: las dos filas deben ser distintas.", campo=operacion
        )
    return fila_i, fila_j


def _caso_de_fila(
    operacion: str, notacion: str, efecto: str, esperado: str, resultado: Tuple
) -> Dict:
    """Arma un caso de la propiedad 5 a partir del efecto que calculó el módulo."""
    modificada, det_obtenido, det_esperado = resultado
    return {
        "id": operacion,
        "notacion": notacion,
        "efecto": efecto,
        "matriz": modificada,
        **_igualdad(("det(A′)", esperado), (det_obtenido, det_esperado)),
    }


def _caso_intercambio(A: Matriz, datos: Optional[Dict]) -> Dict:
    """Propiedad 5a: Fᵢ ↔ Fⱼ cambia el signo del determinante."""
    fila_i, fila_j = _dos_filas(datos, len(A), "intercambio")
    return _caso_de_fila(
        "intercambio",
        p5m.describir_intercambio(fila_i, fila_j),
        "Intercambiar dos filas cambia el signo del determinante.",
        "−det(A)",
        p5m.efecto_de_intercambio(A, fila_i, fila_j),
    )


def _caso_reemplazo(A: Matriz, datos: Optional[Dict]) -> Dict:
    """Propiedad 5b: Fᵢ → Fᵢ + k·Fⱼ no altera el determinante."""
    fila_i, fila_j = _dos_filas(datos, len(A), "reemplazo")
    factor = _leer_numero(datos["k"], "reemplazo", "el factor k del reemplazo")
    return _caso_de_fila(
        "reemplazo",
        p5m.describir_reemplazo(fila_i, factor, fila_j),
        "Sumar a una fila un múltiplo de otra no altera el determinante.",
        "det(A)",
        p5m.efecto_de_reemplazo(A, fila_i, factor, fila_j),
    )


def _caso_escalamiento(A: Matriz, datos: Dict) -> Dict:
    """Propiedad 5c: Fᵢ → k·Fᵢ multiplica el determinante por k."""
    fila_i = _indice_de_fila(datos["fila_i"], len(A), "escalamiento")
    factor = _leer_numero(datos["k"], "escalamiento", "el factor k del escalamiento")
    # Multiplicar una fila por 0 no es una operación elemental: destruye la fila.
    if factor == 0:
        raise ErrorDeCampo(
            "Escalamiento: k debe ser distinto de 0 para escalar una fila.",
            campo="escalamiento",
        )
    return _caso_de_fila(
        "escalamiento",
        p5m.describir_escalamiento(fila_i, factor),
        "Multiplicar una fila por k multiplica el determinante por k.",
        "k·det(A)",
        p5m.efecto_de_escalamiento(A, fila_i, factor),
    )


def _operaciones_de_fila(A: Matriz, operaciones: Dict) -> Dict:
    """Propiedad 5: efecto de las tres operaciones elementales sobre det(A)."""
    casos = []
    # Intercambio y reemplazo necesitan dos filas distintas, que una matriz 1×1 no tiene.
    if len(A) >= 2:
        casos.append(_caso_intercambio(A, operaciones.get("intercambio")))
        casos.append(_caso_reemplazo(A, operaciones.get("reemplazo")))
    casos.append(_caso_escalamiento(A, operaciones["escalamiento"]))
    return {"determinante": p5m.determinante_por_cofactores(A), "casos": casos}


def _propiedad_triangular(A: Matriz) -> Dict:
    """Propiedad 6: det(A) por reducción triangular frente a la expansión por cofactores."""
    reduccion = _reduccion_triangular(A)
    nombres = ("det(A) por reducción triangular", "det(A) por cofactores")
    miembros = (reduccion["valor"], p5m.determinante_por_cofactores(A))
    return {"reduccion": reduccion, **_igualdad(nombres, miembros)}


def verificar_propiedades(
    a_txt: List[List[str]], b_txt: List[List[str]], operaciones: Dict
) -> Dict:
    """Opción 9: verifica las seis propiedades con A y B invertibles del mismo orden."""
    A = _leer_invertible(a_txt, "A")
    B = _leer_invertible(b_txt, "B")
    if len(A) != len(B):
        raise ErrorDeCampo(
            f"A es de orden {len(A)} y B de orden {len(B)}: deben tener el mismo orden n.",
            campo="B",
        )
    return {
        "n": len(A),
        "A": A,
        "B": B,
        "propiedades": _propiedades_de_la_inversa(A, B),
        "operaciones_fila": _operaciones_de_fila(A, operaciones),
        "triangular": _propiedad_triangular(A),
    }


def teoremas_clave() -> Dict:
    """Opción 0: teoremas del Módulo III agrupados en bloques {titulo, enunciados}."""
    bloques: List[Dict] = []
    for linea in p5m.TEOREMAS[p5m.NUMERO_MODULO].split("\n"):
        # En el texto de consola los enunciados llevan 4 espacios de sangría; los títulos, menos.
        if linea.startswith("    ") and bloques:
            bloques[-1]["enunciados"].append(linea.strip())
        else:
            bloques.append({"titulo": linea.strip(), "enunciados": []})
    return {"bloques": bloques}
