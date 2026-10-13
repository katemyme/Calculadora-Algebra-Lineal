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

# Hasta este orden el paso a paso por cofactores se anida: cada menor de orden ≥ 3 trae
# su propia expansión. Desde 6×6 serían cientos de determinantes y solo se da su valor.
ORDEN_MAXIMO_ANIDADO = 5

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


def _terminos_de_cofactores(A: Matriz) -> List[Dict]:
    """Términos a₁ⱼ·C₁ⱼ de la expansión sobre la primera fila, cada uno con su menor M₁ⱼ."""
    terminos = []
    for columna in range(len(A)):
        menor, det_menor, valor_cofactor = p5m.cofactor_con_menor(A, 0, columna)
        terminos.append({
            "entrada": A[0][columna],
            "menor": menor,
            "det_menor": det_menor,
            "signo": "+" if columna % 2 == 0 else "−",
            "cofactor": valor_cofactor,
        })
    return terminos


def _cuenta_2x2(M: Matriz, valor: Fraction) -> str:
    """Cuenta (a)·(d) − (b)·(c) = det de una matriz 2×2, con el valor que calculó el módulo."""
    texto = p5m.formatear_fraccion
    (a, b), (c, d) = M
    return f"({texto(a)})·({texto(d)}) − ({texto(b)})·({texto(c)}) = {texto(valor)}"


def _desarrollo_del_menor(
    menor: Matriz, det_menor: Fraction, anidar: bool, profundidad: int
) -> Optional[Dict]:
    """Cómo se obtiene det(menor): la cuenta si es 2×2 o su propia expansión si es mayor."""
    if len(menor) == 2:
        return {"tipo": "cuenta", "cuenta": _cuenta_2x2(menor, det_menor)}
    # Un menor 1×1 es su único elemento; uno vacío es el de una matriz 1×1.
    if len(menor) < 2 or not anidar:
        return None
    return {"tipo": "cofactores", **_desarrollo_por_cofactores(menor, anidar, profundidad)}


def _desarrollo_por_cofactores(M: Matriz, anidar: bool, profundidad: int = 0) -> Dict:
    """Expansión de det(M) sobre la fila 1: cada menor, su cofactor y el producto a₁ⱼ·C₁ⱼ.

    Con `anidar`, cada menor trae cómo se calcula su determinante. Los nombres llevan una
    prima por nivel (M₁ⱼ, M′₁ⱼ, M″₁ⱼ) para distinguir los menores de A de los de un menor.
    """
    terminos_del_modulo, valor = p5m.expansion_por_cofactores(M)
    terminos = []
    for columna, (menor, det_menor, valor_cofactor, producto) in enumerate(terminos_del_modulo):
        termino = _menor_con_cofactor(
            M, (0, columna), (menor, det_menor, valor_cofactor), anidar, profundidad
        )
        terminos.append({**termino, "producto": producto})
    return {"terminos": terminos, "valor": valor}


def _menor_con_cofactor(
    M: Matriz, posicion: Tuple[int, int], valores: Tuple, anidar: bool, profundidad: int = 0
) -> Dict:
    """Lo que se muestra de una posición (i, j) de M: entrada, menor, signo y cofactor.

    `valores` es la terna (Mᵢⱼ, det(Mᵢⱼ), Cᵢⱼ) que devuelve cofactor_con_menor del módulo.
    """
    fila, columna = posicion
    menor, det_menor, valor_cofactor = valores
    nombre = f"{'′' * profundidad}{p5m.subindice(fila)}{p5m.subindice(columna)}"
    return {
        "fila": fila,
        "columna": columna,
        "entrada": M[fila][columna],
        "menor": menor,
        "det_menor": det_menor,
        "signo": "+" if (fila + columna) % 2 == 0 else "−",
        "cofactor": valor_cofactor,
        "nombre_menor": f"M{nombre}",
        "nombre_cofactor": f"C{nombre}",
        "regla_signo": p5m.describir_signo(fila, columna),
        "desarrollo_menor": _desarrollo_del_menor(menor, det_menor, anidar, profundidad + 1),
    }


def _menores_y_cofactores(A: Matriz) -> Optional[List[List[Dict]]]:
    """Menor, signo y cofactor de cada elemento de A, fila por fila.

    None en una matriz 1×1 (no tiene menores) y desde 6×6 (serían 36 menores 5×5 o más).
    """
    orden = len(A)
    if orden == 1 or orden > ORDEN_MAXIMO_ANIDADO:
        return None
    return [
        [
            _menor_con_cofactor(A, (fila, columna), p5m.cofactor_con_menor(A, fila, columna), True)
            for columna in range(orden)
        ]
        for fila in range(orden)
    ]


def _nota_de_menores(orden: int) -> Optional[str]:
    """Por qué no se despliega cada menor en la inversa por adjunta, cuando no se hace."""
    if orden == 1:
        return (
            "Una matriz 1×1 no tiene menores: su único cofactor es C₁₁ = 1, así que "
            "adj(A) = [1] y A⁻¹ = [1/a₁₁]."
        )
    if orden > ORDEN_MAXIMO_ANIDADO:
        return (
            f"Con una matriz {orden}×{orden} son {orden * orden} menores "
            f"{orden - 1}×{orden - 1}: no se despliegan uno a uno. Cada cofactor "
            "Cᵢⱼ = (−1)ⁱ⁺ʲ·det(Mᵢⱼ) está en la matriz de cofactores del paso siguiente."
        )
    return None


def _expansion_por_cofactores(A: Matriz) -> Dict:
    """Paso a paso de det(A) por cofactores sobre la primera fila."""
    orden = len(A)
    anidar = orden <= ORDEN_MAXIMO_ANIDADO
    nota = None
    if not anidar:
        nota = (
            f"Cada det(M₁ⱼ) se calcula igual, por cofactores sobre su fila 1. Con una matriz "
            f"{orden}×{orden} son {orden} determinantes {orden - 1}×{orden - 1}: su desarrollo "
            "completo no se despliega."
        )
    return {**_desarrollo_por_cofactores(A, anidar), "nota_menores": nota}


def _diagonales(diagonales: List) -> List[Dict]:
    """Diagonales de Sarrus del módulo como diccionarios {celdas, entradas, producto}."""
    return [
        {"celdas": [list(celda) for celda in celdas], "entradas": entradas, "producto": producto}
        for celdas, entradas, producto in diagonales
    ]


def _regla_de_sarrus(A: Matriz) -> Optional[Dict]:
    """Paso a paso de la regla de Sarrus; None si la matriz no es 3×3."""
    if len(A) != 3:
        return None
    diagonales_descendentes, diagonales_ascendentes = p5m.diagonales_de_sarrus(A)
    descendentes, ascendentes = p5m.sumas_de_sarrus(A)
    return {
        "ampliada": p5m.ampliar_para_sarrus(A),
        "diagonales_descendentes": _diagonales(diagonales_descendentes),
        "diagonales_ascendentes": _diagonales(diagonales_ascendentes),
        "descendentes": descendentes,
        "ascendentes": ascendentes,
        "valor": p5m.determinante_por_sarrus(A),
    }


def _pasos_detalle(pasos: List[str], historial: list) -> List[Dict]:
    """Cada operación de fila junto con la matriz que queda tras ella (para el paso a paso)."""
    return [
        {"notacion": notacion, "tipo": tipo, "columna_pivote": columna, "matriz": estado}
        for notacion, (tipo, columna, estado) in zip(pasos, historial)
    ]


def _pivotes_en_la_diagonal(triangular: Matriz) -> List[int]:
    """Columnas con pivote en la diagonal, hasta la primera entrada diagonal nula.

    La escalera de pivotes de la web pone el pivote i en la fila i: tras una diagonal
    nula ya no hay escalera que dibujar, aunque queden entradas no nulas más abajo.
    """
    columnas = []
    for indice, fila in enumerate(triangular):
        if fila[indice] == 0:
            break
        columnas.append(indice)
    return columnas


def _reduccion_triangular(A: Matriz) -> Dict:
    """Reducción a triangular con lo necesario para mostrar det = ± producto de la diagonal."""
    historial: list = []
    triangular, intercambios, factores, operaciones = p5m.reducir_a_triangular(A, historial)
    return {
        "matriz_inicial": A,
        "operaciones": operaciones,
        "pasos_detalle": _pasos_detalle(operaciones, historial),
        "columnas_pivote": _pivotes_en_la_diagonal(triangular),
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
        "pasos_detalle": _pasos_detalle(pasos, historial),
        "columnas_pivote": _columnas_pivote(reducida, len(A)),
        "pivotes": pivotes,
        "inversa": inversa,
    }


def _por_adjunta(A: Matriz) -> Dict:
    """Desarrollo de la opción 8: determinante, menores, cofactores, adjunta e inversa."""
    inversa, adjunta, valor_determinante = p5m.invertir_por_adjunta(A)
    return {
        # det(A) = Σ a₁ⱼ·C₁ⱼ con sus productos, para mostrar de dónde sale el determinante.
        "expansion_determinante": _desarrollo_por_cofactores(A, anidar=False),
        "menores": _menores_y_cofactores(A),
        "nota_menores": _nota_de_menores(len(A)),
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
        {
            "numero": numero,
            "tipo": tipo,
            **_igualdad(nombres, miembros),
            "pasos": _PASOS_POR_PROPIEDAD[numero],
        }
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
    operacion: str,
    notacion: str,
    efecto: str,
    esperado: str,
    resultado: Tuple,
    factor: Optional[Fraction] = None,
) -> Dict:
    """Arma un caso de la propiedad 5 a partir del efecto que calculó el módulo."""
    modificada, det_obtenido, det_esperado = resultado
    return {
        "id": operacion,
        "notacion": notacion,
        "efecto": efecto,
        "matriz": modificada,
        "k": factor,
        **_igualdad(("det(A′)", esperado), (det_obtenido, det_esperado)),
        "pasos": _pasos_de_fila(operacion),
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
        factor,
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
        factor,
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
    return {
        "reduccion": reduccion,
        **_igualdad(nombres, miembros),
        "pasos": _PASOS_POR_PROPIEDAD[6],
    }


def _propiedad_del_producto(A: Matriz, B: Matriz) -> Dict:
    """Propiedad 7: det(AB) frente a det(A)·det(B); incluye AB, det(A) y det(B) para mostrarlos."""
    nombres = ("det(AB)", "det(A)·det(B)")
    return {
        "AB": p5m.multiplicar_matrices(A, B),
        "det_A": p5m.determinante_por_reduccion(A),
        "det_B": p5m.determinante_por_reduccion(B),
        **_igualdad(nombres, p5m.miembros_determinante_del_producto(A, B)),
        "pasos": _PASOS_POR_PROPIEDAD[7],
    }


# ---------------------------------------------------------------------------
# Paso a paso del verificador: cada cálculo se arma una sola vez en
# "procedimientos" y cada propiedad indica en "pasos" cuáles usó, en orden.
# ---------------------------------------------------------------------------
_PASOS_POR_PROPIEDAD = {
    1: ["inversa_A", "inversa_de_inversa_A"],
    2: ["producto_AB", "inversa_AB", "inversa_B", "inversa_A", "producto_de_inversas"],
    3: ["transpuesta_A", "inversa_de_transpuesta", "inversa_A", "transpuesta_de_inversa"],
    4: ["det_A", "inversa_A", "det_inversa_A", "cuenta_inverso_det"],
    6: ["det_A", "cofactores_A"],
    7: ["producto_AB", "det_AB", "det_A", "det_B", "cuenta_producto_det"],
}


def _pasos_de_fila(operacion: str) -> List[str]:
    """Pasos de un caso de la propiedad 5: A′, det(A′), det(A) y el miembro derecho."""
    return [f"fila_{operacion}", f"cofactores_{operacion}", "cofactores_A", f"cuenta_{operacion}"]


def _paso_inversa(M: Matriz, nombre: str, nombre_inversa: str) -> Dict:
    """M⁻¹ por Gauss-Jordan sobre [M | I], el mismo método con que el módulo invierte."""
    return {
        "tipo": "inversa",
        "titulo": f"{nombre_inversa} por Gauss-Jordan: [{nombre} | I] → [I | {nombre_inversa}]",
        "nombre_inversa": nombre_inversa,
        **_por_gauss_jordan(M),
    }


def _paso_producto(titulo: str, izquierdo: Tuple, derecho: Tuple, nombre: str) -> Dict:
    """Producto fila por columna; los nombres van en LaTeX porque los dibuja el Programa 3."""
    (X, nombre_x), (Y, nombre_y) = izquierdo, derecho
    return {
        "tipo": "producto",
        "titulo": titulo,
        "factores": [{"nombre": nombre_x, "matriz": X}, {"nombre": nombre_y, "matriz": Y}],
        "resultado": {"nombre": nombre, "matriz": p5m.multiplicar_matrices(X, Y)},
    }


def _paso_transpuesta(titulo: str, origen: Tuple, nombre: str) -> Dict:
    """Transpuesta: la fila i pasa a ser la columna i (nombres en LaTeX, como el producto)."""
    M, nombre_m = origen
    return {
        "tipo": "transpuesta",
        "titulo": titulo,
        "origen": {"nombre": nombre_m, "matriz": M},
        "destino": {"nombre": nombre, "matriz": p5m.transponer(M)},
    }


def _paso_det_reduccion(M: Matriz, nombre: str) -> Dict:
    """det(M) por reducción a forma triangular, con la matriz tras cada operación."""
    return {
        "tipo": "det_reduccion",
        "titulo": f"det({nombre}) por reducción a forma triangular",
        "nombre": nombre,
        "reduccion": _reduccion_triangular(M),
    }


def _paso_det_cofactores(M: Matriz, nombre: str, valor: Fraction) -> Dict:
    """det(M) por cofactores sobre la fila 1, con cada menor M₁ⱼ.

    `valor` es el det(M) que ya calculó el verificador por cofactores: así no se repite
    la expansión, que cuesta ≈ n! multiplicaciones.
    """
    return {
        "tipo": "det_cofactores",
        "titulo": f"det({nombre}) por cofactores sobre la fila 1",
        "nombre": nombre,
        "terminos": _terminos_de_cofactores(M),
        "valor": valor,
    }


def _paso_cuenta(titulo: str, cuenta: str) -> Dict:
    """Cuenta final escrita con valores que ya calculó el módulo."""
    return {"tipo": "cuenta", "titulo": titulo, "cuenta": cuenta}


def _cuenta_de_fila(caso: Dict, det_A: Fraction) -> str:
    """Miembro derecho de un caso de la propiedad 5 con sus valores: −det(A), det(A) o k·det(A)."""
    texto = p5m.formatear_fraccion
    esperado = texto(caso["derecha"]["valor"])
    if caso["id"] == "intercambio":
        return f"−det(A) = −({texto(det_A)}) = {esperado}"
    if caso["id"] == "reemplazo":
        return f"det(A) = {esperado}: se espera el mismo valor"
    return f"k·det(A) = ({texto(caso['k'])})·({texto(det_A)}) = {esperado}"


def _procedimientos(A: Matriz, B: Matriz, operaciones_fila: Dict) -> Dict[str, Dict]:
    """Todos los cálculos del verificador paso a paso, con la clave que citan las propiedades."""
    texto = p5m.formatear_fraccion
    inversa_A, inversa_B = p5m.calcular_inversa(A), p5m.calcular_inversa(B)
    AB = p5m.multiplicar_matrices(A, B)
    det_A, det_B = p5m.determinante_por_reduccion(A), p5m.determinante_por_reduccion(B)
    inverso_det_A = p5m.miembros_determinante_de_la_inversa(A)[1]
    producto_dets = p5m.miembros_determinante_del_producto(A, B)[1]
    procedimientos = {
        # Propiedades 1 a 3: inversas por Gauss-Jordan, productos y transpuestas.
        "inversa_A": _paso_inversa(A, "A", "A⁻¹"),
        "inversa_de_inversa_A": _paso_inversa(inversa_A, "A⁻¹", "(A⁻¹)⁻¹"),
        "producto_AB": _paso_producto("AB = A·B", (A, "A"), (B, "B"), "AB"),
        "inversa_AB": _paso_inversa(AB, "AB", "(AB)⁻¹"),
        "inversa_B": _paso_inversa(B, "B", "B⁻¹"),
        "producto_de_inversas": _paso_producto(
            "B⁻¹A⁻¹ = B⁻¹·A⁻¹", (inversa_B, "B^{-1}"), (inversa_A, "A^{-1}"), "B^{-1}A^{-1}"
        ),
        "transpuesta_A": _paso_transpuesta(
            "Aᵀ: las filas de A pasan a ser columnas", (A, "A"), "A^{T}"
        ),
        "inversa_de_transpuesta": _paso_inversa(p5m.transponer(A), "Aᵀ", "(Aᵀ)⁻¹"),
        "transpuesta_de_inversa": _paso_transpuesta(
            "(A⁻¹)ᵀ: las filas de A⁻¹ pasan a ser columnas", (inversa_A, "A^{-1}"), "(A^{-1})^{T}"
        ),
        # Propiedades 4, 6 y 7: determinantes y cuentas de los miembros derechos.
        "det_A": _paso_det_reduccion(A, "A"),
        "det_inversa_A": _paso_det_reduccion(inversa_A, "A⁻¹"),
        "det_AB": _paso_det_reduccion(AB, "AB"),
        "det_B": _paso_det_reduccion(B, "B"),
        "cofactores_A": _paso_det_cofactores(A, "A", operaciones_fila["determinante"]),
        "cuenta_inverso_det": _paso_cuenta(
            "Miembro derecho: 1/det(A)",
            f"1/det(A) = 1/({texto(det_A)}) = {texto(inverso_det_A)}",
        ),
        "cuenta_producto_det": _paso_cuenta(
            "Miembro derecho: det(A)·det(B)",
            f"det(A)·det(B) = ({texto(det_A)})·({texto(det_B)}) = {texto(producto_dets)}",
        ),
    }
    # Propiedad 5: por cada operación, A′, su determinante y el miembro derecho esperado.
    for caso in operaciones_fila["casos"]:
        operacion = caso["id"]
        procedimientos[f"fila_{operacion}"] = {
            "tipo": "operacion_fila",
            "titulo": f"A′ = A tras {caso['notacion']}",
            "notacion": caso["notacion"],
            "antes": A,
            "despues": caso["matriz"],
        }
        procedimientos[f"cofactores_{operacion}"] = _paso_det_cofactores(
            caso["matriz"], "A′", caso["izquierda"]["valor"]
        )
        procedimientos[f"cuenta_{operacion}"] = _paso_cuenta(
            f"Miembro derecho: {caso['derecha']['nombre']}", _cuenta_de_fila(caso, det_A)
        )
    return procedimientos


def verificar_propiedades(
    a_txt: List[List[str]], b_txt: List[List[str]], operaciones: Dict
) -> Dict:
    """Opción 9: verifica las siete propiedades con A y B invertibles del mismo orden."""
    A = _leer_invertible(a_txt, "A")
    B = _leer_invertible(b_txt, "B")
    if len(A) != len(B):
        raise ErrorDeCampo(
            f"A es de orden {len(A)} y B de orden {len(B)}: deben tener el mismo orden n.",
            campo="B",
        )
    operaciones_fila = _operaciones_de_fila(A, operaciones)
    return {
        "n": len(A),
        "A": A,
        "B": B,
        "propiedades": _propiedades_de_la_inversa(A, B),
        "operaciones_fila": operaciones_fila,
        "triangular": _propiedad_triangular(A),
        "determinante_producto": _propiedad_del_producto(A, B),
        "procedimientos": _procedimientos(A, B, operaciones_fila),
    }


# Módulos cuyos teoremas muestra la pestaña «Teoremas clave»: el III y, desde el
# PROGRAMA 6, el de Factorización LU (clave 5 de TEOREMAS).
_MODULOS_CON_TEOREMAS = (p5m.NUMERO_MODULO, 5)


def bloques_de_teoremas(numero_modulo: int) -> List[Dict]:
    """Teoremas de un módulo agrupados en bloques {titulo, enunciados}."""
    bloques: List[Dict] = []
    for linea in p5m.TEOREMAS[numero_modulo].split("\n"):
        # En el texto de consola los enunciados llevan 4 espacios de sangría; los títulos, menos.
        if linea.startswith("    ") and bloques:
            bloques[-1]["enunciados"].append(linea.strip())
        else:
            bloques.append({"titulo": linea.strip(), "enunciados": []})
    return bloques


def teoremas_clave() -> Dict:
    """Opción 0: teoremas del Módulo III seguidos de los de la Factorización LU."""
    bloques: List[Dict] = []
    for numero_modulo in _MODULOS_CON_TEOREMAS:
        bloques.extend(bloques_de_teoremas(numero_modulo))
    return {"bloques": bloques}
