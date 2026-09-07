"""Extensiones del Programa 2 sobre el núcleo original de Gauss-Jordan.

El archivo ``nucleo.py`` sigue realizando la reducción RREF. Este módulo añade
la interpretación pedida en el Programa 2:

- posiciones de las columnas pivote;
- variables básicas y variables libres;
- solución general en función de las variables libres;
- solución parametrizada usando t, o t1, t2, ...;
- solución vectorial;
- evaluación de los parámetros elegidos por el usuario;
- comprobación sustituyendo esos valores en el sistema ORIGINAL.

No se utiliza NumPy, SciPy ni ninguna función de álgebra lineal externa. La
aritmética se conserva exacta mediante ``fractions.Fraction``.
"""

from fractions import Fraction
from typing import Dict, List, Optional

from nucleo import (
    ErrorDeEntrada,
    parsear_valor,
    resolver_sistema as resolver_base,
    verificar,
)


def identificar_variables(n: int, columnas_pivote: List[int]) -> Dict:
    """Separa las incógnitas en básicas y libres usando índices base 0."""
    basicas = columnas_pivote[:]
    libres = [columna for columna in range(n) if columna not in columnas_pivote]
    return {"basicas": basicas, "libres": libres}


def nombres_parametros(cantidad: int) -> List[str]:
    """Usa t si hay una sola libre y t1, t2, ... si hay varias."""
    if cantidad == 1:
        return ["t"]
    return [f"t{indice + 1}" for indice in range(cantidad)]


def _expresion_por_variable(solucion: Dict) -> Dict[int, Dict]:
    """Indexa las expresiones de variables básicas que ya produjo nucleo.py."""
    return {
        expresion["variable"]: expresion
        for expresion in solucion.get("expresiones", [])
    }


def construir_formas_de_solucion(solucion: Dict, n: int) -> Dict:
    """Construye las formas general, parametrizada y vectorial.

    La forma general mantiene las variables libres como x_j. La forma
    parametrizada sustituye cada variable libre por un parámetro t, t1, ...
    La forma vectorial se escribe como p + t1*v1 + t2*v2 + ...
    """
    libres = solucion["variables_libres"]
    parametros = nombres_parametros(len(libres))

    parametro_por_variable = {
        variable: parametros[indice]
        for indice, variable in enumerate(libres)
    }
    expresiones_basicas = _expresion_por_variable(solucion)

    forma_general: List[Dict] = []
    forma_parametrizada: List[Dict] = []

    for variable in range(n):
        # Variable libre: x_j puede tomar cualquier real y luego x_j = t_k.
        if variable in libres:
            forma_general.append(
                {
                    "variable": variable,
                    "es_libre": True,
                    "constante": Fraction(0),
                    "terminos_libres": [
                        {
                            "variable": variable,
                            "coeficiente": Fraction(1),
                        }
                    ],
                }
            )
            forma_parametrizada.append(
                {
                    "variable": variable,
                    "es_libre": True,
                    "constante": Fraction(0),
                    "terminos": [
                        {
                            "parametro": parametro_por_variable[variable],
                            "coeficiente": Fraction(1),
                        }
                    ],
                }
            )
            continue

        expresion = expresiones_basicas.get(variable)
        constante = Fraction(0)
        terminos_generales: List[Dict] = []
        terminos_parametricos: List[Dict] = []

        if expresion is not None:
            constante = expresion["constante"]
            for termino in expresion["terminos_libres"]:
                terminos_generales.append(
                    {
                        "variable": termino["variable"],
                        "coeficiente": termino["coeficiente"],
                    }
                )
                terminos_parametricos.append(
                    {
                        "parametro": parametro_por_variable[termino["variable"]],
                        "coeficiente": termino["coeficiente"],
                    }
                )

        forma_general.append(
            {
                "variable": variable,
                "es_libre": False,
                "constante": constante,
                "terminos_libres": terminos_generales,
            }
        )
        forma_parametrizada.append(
            {
                "variable": variable,
                "es_libre": False,
                "constante": constante,
                "terminos": terminos_parametricos,
            }
        )

    # La solución particular corresponde a hacer 0 todas las variables libres.
    vector_particular = solucion["solucion_particular"][:]
    vectores_direccion: List[Dict] = []

    for indice, variable_libre in enumerate(libres):
        vector = [Fraction(0)] * n
        vector[variable_libre] = Fraction(1)

        for expresion in solucion.get("expresiones", []):
            for termino in expresion["terminos_libres"]:
                if termino["variable"] == variable_libre:
                    vector[expresion["variable"]] = termino["coeficiente"]
                    break

        vectores_direccion.append(
            {
                "parametro": parametros[indice],
                "variable_libre": variable_libre,
                "vector": vector,
            }
        )

    lista_parametros = [
        {
            "nombre": parametros[indice],
            "variable": variable,
        }
        for indice, variable in enumerate(libres)
    ]

    return {
        "parametros": lista_parametros,
        "forma_general": forma_general,
        "solucion_general": forma_general,
        "forma_parametrizada": forma_parametrizada,
        "solucion_parametrizada": forma_parametrizada,
        "forma_vectorial": {
            "vector_particular": vector_particular,
            "vectores_direccion": vectores_direccion,
        },
        "solucion_vectorial": {
            "vector_particular": vector_particular,
            "vectores_direccion": vectores_direccion,
        },
    }


def evaluar_parametros(
    solucion: Dict,
    valores_texto: Optional[List[str]],
    n: int,
) -> Optional[Dict]:
    """Evalúa la solución vectorial con los números dados por el usuario."""
    if valores_texto is None:
        return None

    parametros = solucion.get("parametros", [])
    if len(valores_texto) != len(parametros):
        raise ErrorDeEntrada(
            f"Se esperaban {len(parametros)} valor(es) de parámetro y se recibieron "
            f"{len(valores_texto)}."
        )

    valores_parametros: List[Fraction] = []

    for indice, texto in enumerate(valores_texto):
        nombre = parametros[indice]["nombre"]

        if texto is None or str(texto).strip() == "":
            raise ErrorDeEntrada(
                f"Debe ingresar un número para el parámetro {nombre}."
            )

        try:
            valores_parametros.append(parsear_valor(str(texto)))
        except ErrorDeEntrada as error:
            raise ErrorDeEntrada(
                f"Valor inválido para el parámetro {nombre}: {error.mensaje}"
            )

    vectorial = solucion["forma_vectorial"]
    valores_variables = vectorial["vector_particular"][:]

    # x = p + t1*v1 + t2*v2 + ...
    for indice_parametro, direccion in enumerate(vectorial["vectores_direccion"]):
        valor_parametro = valores_parametros[indice_parametro]
        for indice_variable in range(n):
            valores_variables[indice_variable] += (
                valor_parametro * direccion["vector"][indice_variable]
            )

    return {
        "parametros": [
            {
                "nombre": parametros[indice]["nombre"],
                "valor": valores_parametros[indice],
            }
            for indice in range(len(parametros))
        ],
        "valores_variables": valores_variables,
    }


def resolver_sistema(
    m: int,
    n: int,
    datos: List[List[str]],
    valores_parametros: Optional[List[str]] = None,
) -> Dict:
    """Resuelve el sistema y añade toda la salida pedida en Programa 2."""
    resultado = resolver_base(m, n, datos)

    identificacion = identificar_variables(n, resultado["columnas_pivote"])
    basicas = identificacion["basicas"]
    libres = identificacion["libres"]

    # nucleo.py trabaja con índices base 0. Para mostrarlos al usuario también
    # se incluyen las posiciones de columnas en base 1.
    resultado["columnas_pivote_posiciones"] = [
        columna + 1 for columna in resultado["columnas_pivote"]
    ]
    resultado["variables_basicas"] = basicas
    resultado["variables_libres"] = libres

    solucion = resultado["solucion"]
    solucion["variables_basicas"] = basicas
    solucion["variables_libres"] = libres

    if solucion["tipo"] == "indeterminado":
        solucion.update(construir_formas_de_solucion(solucion, n))

        evaluacion = evaluar_parametros(solucion, valores_parametros, n)
        solucion["evaluacion_parametros"] = evaluacion

        if evaluacion is not None:
            comprobacion = verificar(
                resultado["matriz_inicial"],
                evaluacion["valores_variables"],
                m,
                n,
            )
            evaluacion["verificacion"] = comprobacion
            resultado["verificacion_parametros"] = comprobacion
        else:
            resultado["verificacion_parametros"] = []
    else:
        solucion["parametros"] = []
        solucion["evaluacion_parametros"] = None
        resultado["verificacion_parametros"] = []

    return resultado
