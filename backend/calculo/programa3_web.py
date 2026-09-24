"""Adaptador web del Programa 3.

Todo el álgebra se hace en ``programas/Programa 3_GrupoX.py``,
que se carga aquí como módulo. Este archivo solo:

- convierte el texto recibido por HTTP en listas de float,
- valida dimensiones y devuelve errores con fila/columna,
- llama a las funciones del Programa 3,
- organiza el resultado en diccionarios que el frontend puede pintar.

Los números se serializan con el mismo formato que usa el Programa 2
(``{"fraccion", "decimal", "es_entero"}``), así el frontend reutiliza sus
componentes. El campo ``fraccion`` usa el formateador racional del Programa 3
(1/3 en vez de 0.333333), mientras ``decimal`` conserva el valor float.
"""

import importlib.util
from pathlib import Path
from typing import Dict, List, Optional

from calculo.nucleo import ErrorDeEntrada

# backend/calculo/ → raíz del repositorio → programas/
_RUTA_PROGRAMA3 = (
    Path(__file__).resolve().parents[2] / "programas" / "Programa 3_GrupoX.py"
)
_especificacion = importlib.util.spec_from_file_location("programa3", _RUTA_PROGRAMA3)
p3 = importlib.util.module_from_spec(_especificacion)
_especificacion.loader.exec_module(p3)


DESCRIPCION_PASO = {
    "intercambio": (
        "Se intercambian filas para llevar a la posición pivote el elemento de "
        "mayor valor absoluto de la columna {columna} (pivoteo parcial)."
    ),
    "normalizacion": (
        "Se divide la fila pivote entre el pivote para que el elemento de la "
        "columna {columna} valga 1."
    ),
    "eliminacion": (
        "Se resta un múltiplo de la fila pivote para anular el elemento de la "
        "columna {columna}."
    ),
}


class ErrorDeCampo(ErrorDeEntrada):
    """Error de entrada que además indica qué matriz o vector lo produjo."""

    def __init__(self, mensaje, campo=None, fila=None, columna=None):
        super().__init__(mensaje, fila=fila, columna=columna)
        self.campo = campo


# ---------------------------------------------------------------------------
# Serialización
# ---------------------------------------------------------------------------
def numero(valor: float) -> Dict:
    texto = p3.formatear_fraccion(valor)
    return {
        "fraccion": texto,
        "decimal": p3.limpiar(valor),
        "es_entero": "/" not in texto,
    }


def vector_json(vector: List[float]) -> List[Dict]:
    return [numero(x) for x in vector]


def matriz_json(matriz: List[List[float]]) -> List[List[Dict]]:
    return [vector_json(fila) for fila in matriz]


# ---------------------------------------------------------------------------
# Lectura y validación
# ---------------------------------------------------------------------------
def _validar_dimension(valor: int, descripcion: str, campo: str) -> None:
    if not (p3.DIMENSION_MINIMA <= valor <= p3.DIMENSION_MAXIMA):
        raise ErrorDeCampo(
            f"{descripcion} debe estar entre {p3.DIMENSION_MINIMA} y "
            f"{p3.DIMENSION_MAXIMA}; se recibió {valor}.",
            campo=campo,
        )


def _convertir(
    texto: str, campo: str, fila: int, columna: Optional[int], etiqueta: Optional[str] = None
) -> float:
    # Igual que en el Programa 2, una celda vacía representa 0.
    if texto is None or str(texto).strip() == "":
        return 0.0
    ok, valor = p3.convertir_numero(str(texto))
    if not ok:
        ubicacion = f"fila {fila}" if columna is None else f"fila {fila}, columna {columna}"
        raise ErrorDeCampo(
            f"Valor inválido en {etiqueta or campo} ({ubicacion}): "
            f"'{str(texto).strip()}' no es un número.",
            campo=campo,
            fila=fila,
            columna=columna,
        )
    return valor


def leer_matriz(datos: List[List[str]], campo: str) -> List[List[float]]:
    if not datos or not datos[0]:
        raise ErrorDeCampo(f"La matriz {campo} está vacía.", campo=campo)
    _validar_dimension(len(datos), f"El número de filas de {campo}", campo)
    _validar_dimension(len(datos[0]), f"El número de columnas de {campo}", campo)
    columnas = len(datos[0])
    matriz = []
    for i, fila in enumerate(datos):
        if len(fila) != columnas:
            raise ErrorDeCampo(
                f"La fila {i + 1} de {campo} tiene {len(fila)} valores y se esperaban {columnas}.",
                campo=campo,
                fila=i + 1,
            )
        matriz.append([_convertir(v, campo, i + 1, j + 1) for j, v in enumerate(fila)])
    return matriz


def leer_vector(datos: List[str], campo: str) -> List[float]:
    if not datos:
        raise ErrorDeCampo(f"El vector {campo} está vacío.", campo=campo)
    _validar_dimension(len(datos), f"La dimensión de {campo}", campo)
    return [_convertir(v, campo, i + 1, None) for i, v in enumerate(datos)]


def leer_escalar(texto: str) -> float:
    if texto is None or str(texto).strip() == "":
        raise ErrorDeCampo("Debe escribir el escalar c.", campo="c")
    ok, valor = p3.convertir_numero(str(texto))
    if not ok:
        raise ErrorDeCampo(
            f"El escalar c no es válido: '{str(texto).strip()}'.", campo="c"
        )
    return valor


def _orden(matriz: List[List[float]]) -> str:
    return p3.formatear_dimension(matriz)


# ---------------------------------------------------------------------------
# 1. Vectores
# ---------------------------------------------------------------------------
def operar_vectores(operacion: str, u_txt, v_txt, c_txt) -> Dict:
    if operacion == "escalar":
        c = leer_escalar(c_txt)
        v = leer_vector(v_txt, "v")
        resultado = p3.escalar_por_vector(c, v)
        detalle = [
            f"{p3.formatear_numero(c)}·({p3.formatear_numero(v[i])}) = "
            f"{p3.formatear_numero(resultado[i])}"
            for i in range(len(v))
        ]
        return {
            "operacion": operacion,
            "formula": "(c·v)ᵢ = c·vᵢ",
            "c": numero(c),
            "v": vector_json(v),
            "resultado": vector_json(resultado),
            "detalle": detalle,
        }

    u = leer_vector(u_txt, "u")
    v = leer_vector(v_txt, "v")
    if len(u) != len(v):
        raise ErrorDeCampo(
            f"u ∈ ℝ^{len(u)} y v ∈ ℝ^{len(v)} tienen dimensiones distintas; "
            "no se pueden operar.",
            campo="v",
        )

    if operacion == "suma":
        resultado, simbolo, formula = p3.suma_vectores(u, v), "+", "(u + v)ᵢ = uᵢ + vᵢ"
    else:
        resultado, simbolo, formula = p3.resta_vectores(u, v), "−", "(u − v)ᵢ = uᵢ − vᵢ"

    detalle = [
        f"({p3.formatear_numero(u[i])}) {simbolo} ({p3.formatear_numero(v[i])}) = "
        f"{p3.formatear_numero(resultado[i])}"
        for i in range(len(u))
    ]
    return {
        "operacion": operacion,
        "formula": formula,
        "u": vector_json(u),
        "v": vector_json(v),
        "resultado": vector_json(resultado),
        "detalle": detalle,
    }


# ---------------------------------------------------------------------------
# 2. Matrices
# ---------------------------------------------------------------------------
def operar_matrices(operacion: str, a_txt, b_txt, c_txt) -> Dict:
    if operacion == "escalar":
        c = leer_escalar(c_txt)
        A = leer_matriz(a_txt, "A")
        return {
            "operacion": operacion,
            "formula": "(c·A)ᵢⱼ = c·aᵢⱼ",
            "c": numero(c),
            "A": matriz_json(A),
            "resultado": matriz_json(p3.escalar_por_matriz(c, A)),
        }

    A = leer_matriz(a_txt, "A")
    B = leer_matriz(b_txt, "B")
    if p3.dimensiones(A) != p3.dimensiones(B):
        raise ErrorDeCampo(
            f"A es {_orden(A)} y B es {_orden(B)}. Para sumar o restar, ambas "
            "deben tener el mismo orden m×n.",
            campo="B",
        )
    if operacion == "suma":
        C, formula = p3.suma_matrices(A, B), "(A + B)ᵢⱼ = aᵢⱼ + bᵢⱼ"
    else:
        C, formula = p3.resta_matrices(A, B), "(A − B)ᵢⱼ = aᵢⱼ − bᵢⱼ"
    return {
        "operacion": operacion,
        "formula": formula,
        "A": matriz_json(A),
        "B": matriz_json(B),
        "resultado": matriz_json(C),
    }


def multiplicar_matrices(a_txt, b_txt) -> Dict:
    A = leer_matriz(a_txt, "A")
    B = leer_matriz(b_txt, "B")
    if not p3.producto_compatible(A, B):
        m, n = p3.dimensiones(A)
        filas_b, _ = p3.dimensiones(B)
        raise ErrorDeCampo(
            f"A es {_orden(A)} y B es {_orden(B)}. columnas(A) = {n} ≠ "
            f"filas(B) = {filas_b}: el producto A·B no está definido.",
            campo="B",
        )

    C = p3.producto_matrices(A, B)
    m, n = p3.dimensiones(A)
    p = p3.dimensiones(B)[1]

    # Desglose de cada cᵢⱼ = Σₖ aᵢₖ·bₖⱼ para la vista interactiva.
    detalle = []
    for i in range(m):
        fila = []
        for j in range(p):
            terminos = []
            acumulado = 0.0
            for k in range(n):
                producto = A[i][k] * B[k][j]
                acumulado += producto
                terminos.append(
                    {
                        "k": k,
                        "a": numero(A[i][k]),
                        "b": numero(B[k][j]),
                        "producto": numero(producto),
                        "acumulado": numero(acumulado),
                    }
                )
            fila.append({"terminos": terminos, "valor": numero(C[i][j])})
        detalle.append(fila)

    return {
        "A": matriz_json(A),
        "B": matriz_json(B),
        "resultado": matriz_json(C),
        "dimensiones": {"A": _orden(A), "B": _orden(B), "C": _orden(C)},
        "detalle": detalle,
    }


# ---------------------------------------------------------------------------
# 3. Sistemas: combinación lineal y Ax = b
# ---------------------------------------------------------------------------
def _analizar(Ab: List[List[float]], m: int, n: int) -> Dict:
    reducida, pasos, columnas_pivote = p3.escalonar(Ab, m, n)
    rango_a, rango_ab = p3.calcular_rangos(reducida, m, n, columnas_pivote)
    tipo, titulo, explicacion = p3.clasificar(rango_a, rango_ab, n)

    fila_contradictoria = None
    for i in range(m):
        if p3.fila_contradictoria(reducida[i], n):
            fila_contradictoria = {"indice": i, "valor": numero(reducida[i][n])}
            break

    return {
        "matriz_inicial": matriz_json(Ab),
        "homogeneo": p3.es_homogeneo(Ab, m, n),
        "pasos": [
            {
                "numero": indice + 1,
                "tipo": tipo_paso,
                "notacion": notacion,
                "columna_pivote": columna,
                "descripcion": DESCRIPCION_PASO[tipo_paso].format(columna=columna + 1),
                "matriz": matriz_json(estado),
            }
            for indice, (tipo_paso, notacion, columna, estado) in enumerate(pasos)
        ],
        "matriz_reducida": matriz_json(reducida),
        "columnas_pivote": columnas_pivote,
        "rango_A": rango_a,
        "rango_Ab": rango_ab,
        "clasificacion": {
            "tipo": tipo,
            "titulo": titulo,
            "explicacion": explicacion,
            "grados_de_libertad": n - rango_a if tipo == "indeterminado" else 0,
        },
        "fila_contradictoria": fila_contradictoria,
        "_reducida": reducida,
    }


def _solucion(analisis: Dict, n: int, letra: str) -> Optional[Dict]:
    """Construye la solución (o None si es inconsistente)."""
    tipo = analisis["clasificacion"]["tipo"]
    reducida = analisis.pop("_reducida")
    if tipo == "inconsistente":
        return None

    libres, expresiones = p3.construir_solucion(reducida, n, analisis["columnas_pivote"])
    parametros = p3.nombres_parametros(len(libres)) if libres else []
    particular = p3.evaluar_solucion(libres, expresiones, n, [0.0] * len(libres))

    forma = []
    for j in range(n):
        nombre = f"{letra}{p3.subindice(j)}"
        if j in libres:
            forma.append({"variable": j, "nombre": nombre, "es_libre": True,
                          "texto": parametros[libres.index(j)]})
            continue
        for variable, constante, terminos in expresiones:
            if variable == j:
                con_nombres = [(coef, parametros[libres.index(libre)]) for coef, libre in terminos]
                forma.append({"variable": j, "nombre": nombre, "es_libre": False,
                              "texto": p3.formatear_expresion(constante, con_nombres)})

    direcciones = p3.vectores_direccion(libres, expresiones, n)
    return {
        "tipo": tipo,
        "variables_basicas": [variable for variable, _, _ in expresiones],
        "variables_libres": libres,
        "parametros": parametros,
        "valores": vector_json(particular),
        "forma_parametrica": forma,
        "forma_vectorial": {
            "particular": vector_json(particular),
            "direcciones": [
                {"parametro": parametros[i], "vector": vector_json(direcciones[i])}
                for i in range(len(libres))
            ],
        },
        "_libres": libres,
        "_expresiones": expresiones,
        "_particular": particular,
    }


def _limpiar_privados(solucion: Optional[Dict]) -> None:
    if solucion is None:
        return
    for clave in [c for c in solucion if c.startswith("_")]:
        del solucion[clave]


def combinacion_lineal(vectores_txt: List[List[str]], b_txt: List[str]) -> Dict:
    if not vectores_txt:
        raise ErrorDeCampo("Debe dar al menos un vector.", campo="vectores")
    _validar_dimension(len(vectores_txt), "La cantidad de vectores k", "vectores")
    b = leer_vector(b_txt, "b")
    vectores = []
    for j, texto in enumerate(vectores_txt):
        nombre = f"v{p3.subindice(j)}"
        if len(texto) != len(b):
            raise ErrorDeCampo(
                f"{nombre} tiene {len(texto)} componentes y b tiene {len(b)}.",
                campo="vectores",
            )
        vectores.append(
            [_convertir(v, "vectores", i + 1, j + 1, nombre) for i, v in enumerate(texto)]
        )

    n = len(b)
    k = len(vectores)
    Ab = p3.aumentada_desde_columnas(vectores, b)
    analisis = _analizar(Ab, n, k)
    solucion = _solucion(analisis, k, "c")

    verificacion = None
    expresion = None
    if solucion is not None:
        pesos = solucion["_particular"]
        expresion = "b = " + p3.texto_combinacion(pesos)
        recalculado = p3.combinar_vectores(pesos, vectores)
        verificacion = {
            "pesos": vector_json(pesos),
            "terminos": [
                {"peso": numero(pesos[j]), "vector": vector_json(vectores[j]),
                 "producto": vector_json(p3.escalar_por_vector(pesos[j], vectores[j]))}
                for j in range(k)
            ],
            "recalculado": vector_json(recalculado),
            "esperado": vector_json(b),
            "coincide": p3.vectores_iguales(recalculado, b),
        }
    _limpiar_privados(solucion)

    return {
        **analisis,
        "es_combinacion": solucion is not None,
        "solucion": solucion,
        "expresion": expresion,
        "verificaciones": [verificacion] if verificacion else [],
        "vectores": [vector_json(v) for v in vectores],
        "b": vector_json(b),
    }


def _leer_lista_de_vectores(vectores_txt: List[List[str]], n: int) -> List[List[float]]:
    """Lee k vectores de ℝⁿ dados como columnas (mismo formato que la opción 4)."""
    vectores = []
    for j, texto in enumerate(vectores_txt):
        nombre = f"v{p3.subindice(j)}"
        if len(texto) != n:
            raise ErrorDeCampo(
                f"{nombre} tiene {len(texto)} componentes y se esperaban {n}.",
                campo="vectores",
            )
        vectores.append(
            [_convertir(v, "vectores", i + 1, j + 1, nombre) for i, v in enumerate(texto)]
        )
    return vectores


def independencia_lineal(
    vectores_txt: List[List[str]], valores_parametros_txt: Optional[List[str]] = None
) -> Dict:
    """¿Son v₁, …, vₖ linealmente independientes?

    Resuelve el sistema HOMOGÉNEO [v₁ … vₖ | 0]. Al ser homogéneo siempre es
    consistente y siempre contiene la solución trivial x = 0. El veredicto
    sale de comparar rango(A) con k:

    - rango = k → solo la solución trivial → independientes;
    - rango < k → hay variables libres y soluciones no triviales → dependientes.

    Si ``valores_parametros_txt`` llega desde la interfaz, se evalúa la solución
    general para esos valores de t, t1, … y se devuelve el vector x concreto.
    """
    if not vectores_txt:
        raise ErrorDeCampo("Debe dar al menos un vector.", campo="vectores")
    _validar_dimension(len(vectores_txt), "La cantidad de vectores k", "vectores")
    if not vectores_txt[0]:
        raise ErrorDeCampo("Los vectores están vacíos.", campo="vectores")
    n = len(vectores_txt[0])
    _validar_dimension(n, "La dimensión n de los vectores", "vectores")

    vectores = _leer_lista_de_vectores(vectores_txt, n)
    k = len(vectores)
    cero = [0.0] * n

    Ab = p3.aumentada_desde_columnas(vectores, cero)
    analisis = _analizar(Ab, n, k)
    # En Programa 3 se muestran los coeficientes desconocidos como x₁, …, xₖ.
    solucion = _solucion(analisis, k, "x")
    rango = analisis["rango_A"]
    independientes = rango == k

    relacion = None
    verificacion = None
    evaluacion_parametros = None

    if not independientes:
        libres = solucion["_libres"]
        expresiones = solucion["_expresiones"]
        valores = [0.0] * len(libres)
        valores[0] = 1.0                       # primera variable libre = 1
        pesos = p3.evaluar_solucion(libres, expresiones, k, valores)
        indice_libre = libres[0]

        # vⱼ = Σ (−xᵢ)·vᵢ con i ≠ j, para pintar el despeje término a término.
        despeje = [
            {"indice": j, "nombre": f"v{p3.subindice(j)}", "coeficiente": numero(-pesos[j])}
            for j in range(k)
            if j != indice_libre and not p3.es_cero(pesos[j])
        ]
        relacion = {
            "pesos": vector_json(pesos),
            "expresion": p3.texto_combinacion(pesos) + " = 0",
            "indice_libre": indice_libre,
            "nombre_libre": f"v{p3.subindice(indice_libre)}",
            "despeje": despeje,
            "texto_despeje": p3.texto_despeje(pesos, indice_libre),
        }

        recalculado = p3.combinar_vectores(pesos, vectores)
        verificacion = {
            "pesos": vector_json(pesos),
            "terminos": [
                {"peso": numero(pesos[j]), "vector": vector_json(vectores[j]),
                 "producto": vector_json(p3.escalar_por_vector(pesos[j], vectores[j]))}
                for j in range(k)
            ],
            "recalculado": vector_json(recalculado),
            "esperado": vector_json(cero),
            "coincide": p3.vectores_iguales(recalculado, cero),
        }

        if valores_parametros_txt is not None:
            parametros = solucion["parametros"]
            if len(valores_parametros_txt) != len(parametros):
                raise ErrorDeCampo(
                    f"Se esperaban {len(parametros)} valor(es) de parámetro y se recibieron "
                    f"{len(valores_parametros_txt)}.",
                    campo="parametros",
                )
            valores_elegidos = []
            for i, texto in enumerate(valores_parametros_txt):
                if texto is None or str(texto).strip() == "":
                    raise ErrorDeCampo(
                        f"Debe escribir un valor para {parametros[i]}.",
                        campo="parametros",
                        fila=i + 1,
                    )
                valores_elegidos.append(
                    _convertir(texto, "parametros", i + 1, None, parametros[i])
                )

            vector_x = p3.evaluar_solucion(libres, expresiones, k, valores_elegidos)
            comprobacion = p3.combinar_vectores(vector_x, vectores)
            evaluacion_parametros = {
                "parametros": [
                    {"nombre": parametros[i], "valor": numero(valores_elegidos[i])}
                    for i in range(len(parametros))
                ],
                "vector": vector_json(vector_x),
                "texto_vector": p3.formatear_vector_fraccion(vector_x),
                "conjunto_solucion": "{" + p3.formatear_vector_fraccion(vector_x) + "}",
                "es_trivial": all(p3.es_cero(valor) for valor in vector_x),
                "verificacion": {
                    "recalculado": vector_json(comprobacion),
                    "esperado": vector_json(cero),
                    "coincide": p3.vectores_iguales(comprobacion, cero),
                },
            }

    _limpiar_privados(solucion)

    return {
        **analisis,
        "independientes": independientes,
        "es_homogeneo": True,
        "tiene_solucion_trivial": True,
        "solo_solucion_trivial": independientes,
        "tiene_soluciones_no_triviales": not independientes,
        "n": n,
        "k": k,
        "rango": rango,
        "dimension_generado": rango,
        "vectores_pivote": analisis["columnas_pivote"],
        "mas_vectores_que_dimensiones": k > n,
        "solucion": solucion,
        "relacion": relacion,
        "evaluacion_parametros": evaluacion_parametros,
        "verificaciones": [verificacion] if verificacion else [],
        "vectores": [vector_json(v) for v in vectores],
    }


def _verificar_ax(A, x, b, etiqueta) -> Dict:
    Ax = p3.columna_a_vector(p3.producto_matrices(A, p3.vector_a_columna(x)))
    return {
        "etiqueta": etiqueta,
        "x": vector_json(x),
        "Ax": vector_json(Ax),
        "b": vector_json(b),
        "coincide": p3.vectores_iguales(Ax, b),
    }


def resolver_ecuacion(a_txt: List[List[str]], b_txt: List[str]) -> Dict:
    A = leer_matriz(a_txt, "A")
    b = leer_vector(b_txt, "b")
    m, n = p3.dimensiones(A)
    if len(b) != m:
        raise ErrorDeCampo(
            f"A tiene {m} filas y b tiene {len(b)} componentes; deben coincidir.",
            campo="b",
        )

    Ab = p3.aumentada_desde_matriz(A, b)
    analisis = _analizar(Ab, m, n)
    solucion = _solucion(analisis, n, "x")

    verificaciones = []
    if solucion is not None:
        libres = solucion["_libres"]
        expresiones = solucion["_expresiones"]
        if not libres:
            verificaciones.append(_verificar_ax(A, solucion["_particular"], b, "Solución única"))
        else:
            parametros = solucion["parametros"]
            ceros = p3.evaluar_solucion(libres, expresiones, n, [0.0] * len(libres))
            unos = p3.evaluar_solucion(libres, expresiones, n, [1.0] * len(libres))
            verificaciones.append(_verificar_ax(
                A, ceros, b, "Solución particular (" + ", ".join(p + " = 0" for p in parametros) + ")"))
            verificaciones.append(_verificar_ax(
                A, unos, b, ", ".join(p + " = 1" for p in parametros)))
    _limpiar_privados(solucion)

    return {
        **analisis,
        "solucion": solucion,
        "verificaciones": verificaciones,
    }


# ---------------------------------------------------------------------------
# 4. Balanceo de ecuaciones químicas (sistema homogéneo)
# ---------------------------------------------------------------------------
def balancear_ecuacion(texto: str) -> Dict:
    """Mismos pasos que ``balancear_reaccion`` del Programa 3, sin imprimir.

    La reacción se convierte en el sistema homogéneo [A | 0] (una fila por
    elemento, una columna por compuesto, productos con signo −), se resuelve
    por Gauss-Jordan y la solución no trivial se lleva a enteros mínimos.
    """
    if texto is None or texto.strip() == "":
        raise ErrorDeCampo("Escriba la reacción química.", campo="reaccion")
    ok, lectura = p3.leer_reaccion(texto)
    if not ok:
        raise ErrorDeCampo(lectura[0].upper() + lectura[1:] + ".", campo="reaccion")
    reactivos, productos = lectura
    if len(reactivos) + len(productos) < 2:
        raise ErrorDeCampo("La reacción necesita al menos dos compuestos.", campo="reaccion")

    compuestos = reactivos + productos
    k = len(compuestos)
    p = len(reactivos)
    elementos, A = p3.plantear_reaccion(reactivos, productos)
    m = len(elementos)

    Ab = p3.aumentada_desde_matriz([[float(a) for a in fila] for fila in A], [0.0] * m)
    analisis = _analizar(Ab, m, k)
    solucion = _solucion(analisis, k, "x")     # el homogéneo nunca es inconsistente
    rango = analisis["rango_A"]
    dependientes = rango < k

    estado = "independientes"
    coeficientes = None
    parametro_t = None
    verificacion = []
    if dependientes:
        libres = solucion["_libres"]
        if len(libres) > 1:
            estado = "varias"
        else:
            pesos = p3.evaluar_solucion(libres, solucion["_expresiones"], k, [1.0])
            coeficientes = p3.coeficientes_enteros(pesos, libres[0])
            if coeficientes is None:
                estado = "sin_enteros"
            elif any(c <= 0 for c in coeficientes):
                estado = "no_valida"
            else:
                estado = "balanceada"
                parametro_t = coeficientes[libres[0]]
                for i in range(m):
                    izquierda = sum(coeficientes[j] * A[i][j] for j in range(p))
                    derecha = sum(-coeficientes[j] * A[i][j] for j in range(p, k))
                    verificacion.append({
                        "elemento": elementos[i],
                        "reactivos": izquierda,
                        "productos": derecha,
                        "coincide": izquierda == derecha,
                    })
    _limpiar_privados(solucion)

    ecuacion = None
    if estado == "balanceada":
        ecuacion = (p3.texto_lado(reactivos, coeficientes[:p]) + " → "
                    + p3.texto_lado(productos, coeficientes[p:]))

    return {
        **analisis,
        "compuestos": [
            {
                "indice": j,
                "variable": f"x{p3.subindice(j)}",
                "formula": formula,
                "formula_bonita": p3.formula_con_subindices(formula),
                "lado": "reactivo" if j < p else "producto",
                "vector": vector_json([float(A[i][j]) for i in range(m)]),
            }
            for j, (formula, _) in enumerate(compuestos)
        ],
        "elementos": elementos,
        "ecuaciones": [
            {"elemento": elementos[i], "texto": p3.texto_ecuacion_elemento(A[i])}
            for i in range(m)
        ],
        "n_reactivos": p,
        "k": k,
        "rango": rango,
        "dependientes": dependientes,
        "estado": estado,
        "coeficientes": coeficientes,
        "parametro_t": parametro_t,
        "ecuacion_balanceada": ecuacion,
        "solucion": solucion,
        "verificacion": verificacion,
    }


# ---------------------------------------------------------------------------
# 5. Propiedad distributiva A(u + v) = A·u + A·v
# ---------------------------------------------------------------------------
def verificar_distributiva(a_txt: List[List[str]], u_txt: List[str], v_txt: List[str]) -> Dict:
    """Mismos pasos que ``verificar_distributiva`` del Programa 3, sin imprimir."""
    A = leer_matriz(a_txt, "A")
    u = leer_vector(u_txt, "u")
    v = leer_vector(v_txt, "v")
    m, n = p3.dimensiones(A)
    for nombre, vector in (("u", u), ("v", v)):
        if len(vector) != n:
            raise ErrorDeCampo(
                f"A tiene {n} columnas y {nombre} tiene {len(vector)} componentes; "
                f"{nombre} debe estar en ℝ^{n}.",
                campo=nombre,
            )

    u_mas_v = p3.suma_vectores(u, v)
    izquierda = p3.matriz_por_vector(A, u_mas_v)     # A(u + v)
    Au = p3.matriz_por_vector(A, u)
    Av = p3.matriz_por_vector(A, v)
    derecha = p3.suma_vectores(Au, Av)               # A·u + A·v

    return {
        "A": matriz_json(A),
        "u": vector_json(u),
        "v": vector_json(v),
        "dimensiones": {"A": _orden(A), "m": m, "n": n},
        "u_mas_v": vector_json(u_mas_v),
        "izquierda": vector_json(izquierda),
        "Au": vector_json(Au),
        "Av": vector_json(Av),
        "derecha": vector_json(derecha),
        "coincide": p3.vectores_iguales(izquierda, derecha),
    }
