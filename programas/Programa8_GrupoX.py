"""PROGRAMA 8 – Métodos Numéricos Integrador: Jacobi y Gauss-Seidel.

Resuelve sistemas de ecuaciones lineales Ax = b mediante los métodos iterativos
de Jacobi y Gauss-Seidel utilizando NumPy, Pandas y Matplotlib.

Funciones principales:
- Validación de dimensiones (A cuadrada n×n, b, x^(0)), tolerancia ε > 0 y Nmax ≥ 1.
- Detección de ceros en la diagonal principal y evaluación de reordenamiento de filas.
- Diagnóstico de diagonal estrictamente dominante por filas (condición suficiente,
  no necesaria).
- Implementación desde cero de Jacobi (actualización simultánea) y Gauss-Seidel
  (actualización inmediata) con norma infinito ||x^(k) - x^(k-1)||_∞ y residuo ||Ax - b||_∞.
- Manejo seguro de divergencia / valores no finitos sin cerrar la aplicación.
- Generación de tablas con Pandas, gráfica comparativa con Matplotlib y validación
  contra solución de referencia (numpy.linalg.solve).

Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
"""

from fractions import Fraction
from itertools import permutations
import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

DIMENSION_MINIMA: int = 1
DIMENSION_MAXIMA: int = 8
UMBRAL_DIVERGENCIA: float = 1e15
CERO_NUMERICO: float = 1e-15


class ErrorIterativo(ValueError):
    """Error atribuible a los datos ingresados por el usuario."""

    def __init__(
        self,
        mensaje: str,
        campo: Optional[str] = None,
        fila: Optional[int] = None,
        columna: Optional[int] = None,
    ) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo
        self.fila = fila
        self.columna = columna


# ---------------------------------------------------------------------------
# Casos de prueba obligatorios precargados
# ---------------------------------------------------------------------------
CASOS_PRUEBA_P8: List[Dict] = [
    {
        "id": "caso1_convergencia",
        "nombre": "Caso 1 · Convergencia (Matriz estrictamente diagonal dominante)",
        "descripcion": (
            "Sistema 3×3 estrictamente diagonal dominante por filas. Ambos métodos "
            "convergen a la solución exacta x = [2, 4, 3]ᵀ, observándose que "
            "Gauss-Seidel requiere menos iteraciones que Jacobi."
        ),
        "A": [
            ["4", "-1", "1"],
            ["4", "-8", "1"],
            ["-2", "1", "5"],
        ],
        "b": ["7", "-21", "15"],
        "x0": ["0", "0", "0"],
        "tolerancia": "1e-5",
        "max_iter": "50",
        "permitir_reordenamiento": True,
    },
    {
        "id": "caso2_reordenamiento",
        "nombre": "Caso 2 · Reordenamiento de filas (Cero en la diagonal inicial)",
        "descripcion": (
            "Sistema 3×3 con a₁₁ = 0 en la diagonal principal inicial. El módulo "
            "detecta el cero, evalúa permutaciones e intercambia F₁ ↔ F₂ para obtener "
            "una matriz estrictamente diagonal dominante que converge a x = [1, 2, 3]ᵀ."
        ),
        "A": [
            ["0", "5", "-1"],
            ["4", "1", "-1"],
            ["1", "-1", "6"],
        ],
        "b": ["7", "3", "17"],
        "x0": ["0", "0", "0"],
        "tolerancia": "1e-5",
        "max_iter": "50",
        "permitir_reordenamiento": True,
    },
    {
        "id": "caso3_no_convergencia",
        "nombre": "Caso 3 · Advertencia / No convergencia (Sin dominancia diagonal)",
        "descripcion": (
            "Sistema 3×3 invertible (det(A) = 4, solución exacta x = [1, 1, 1]ᵀ) que "
            "no cumple la condición suficiente de diagonal dominante bajo ningún "
            "reordenamiento posible. Ambos métodos divergen y el programa detiene el "
            "cálculo con advertencia clara sin cerrarse."
        ),
        "A": [
            ["1", "4", "4"],
            ["1", "2", "4"],
            ["1", "4", "2"],
        ],
        "b": ["9", "7", "7"],
        "x0": ["0", "0", "0"],
        "tolerancia": "1e-4",
        "max_iter": "30",
        "permitir_reordenamiento": True,
    },
]


# ---------------------------------------------------------------------------
# Parseo y validación de entradas
# ---------------------------------------------------------------------------
def parsear_real(
    texto: object,
    nombre: str,
    campo: Optional[str] = None,
    fila: Optional[int] = None,
    columna: Optional[int] = None,
) -> float:
    """Convierte enteros, decimales, notación científica o fracciones (ej. '1/3') a float."""
    if texto is None or str(texto).strip() == "":
        raise ErrorIterativo(f"Falta el valor de {nombre}.", campo=campo, fila=fila, columna=columna)

    limpio = str(texto).strip().replace(",", ".")
    try:
        if "/" in limpio:
            valor = float(Fraction(limpio))
        else:
            valor = float(limpio)
    except (ValueError, ZeroDivisionError):
        raise ErrorIterativo(
            f"Valor inválido en {nombre}: '{str(texto).strip()}'. "
            "Use números reales (ej. 4, -2.5, 1e-4, 1/3).",
            campo=campo,
            fila=fila,
            columna=columna,
        )

    if not math.isfinite(valor):
        raise ErrorIterativo(
            f"El valor de {nombre} debe ser un número finito.",
            campo=campo,
            fila=fila,
            columna=columna,
        )
    return valor


def parsear_entero_positivo(texto: object, nombre: str, campo: str) -> int:
    """Valida un entero ≥ 1."""
    if texto is None or str(texto).strip() == "":
        raise ErrorIterativo(f"Falta el valor de {nombre}.", campo=campo)
    limpio = str(texto).strip()
    try:
        valor_float = float(limpio)
        valor = int(limpio)
    except ValueError:
        raise ErrorIterativo(
            f"{nombre} debe ser un número entero positivo (ej. 50); se recibió '{limpio}'.",
            campo=campo,
        )
    if valor != valor_float or valor < 1:
        raise ErrorIterativo(
            f"{nombre} debe ser un entero mayor o igual a 1; se recibió '{limpio}'.",
            campo=campo,
        )
    return valor


def validar_y_construir_entradas(
    A_raw: List[List],
    b_raw: List,
    x0_raw: Optional[List],
    tolerancia_raw: object,
    max_iter_raw: object,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, float, int]:
    """Valida dimensiones y tipos de A (n×n), b (n), x^(0) (n), tolerancia y Nmax."""
    if not A_raw or not isinstance(A_raw, list):
        raise ErrorIterativo("La matriz de coeficientes A no puede estar vacía.", campo="A")

    n = len(A_raw)
    if not (DIMENSION_MINIMA <= n <= DIMENSION_MAXIMA):
        raise ErrorIterativo(
            f"La dimensión n de A debe estar entre {DIMENSION_MINIMA} y {DIMENSION_MAXIMA}; "
            f"se recibió {n}.",
            campo="A",
        )

    matriz_lista: List[List[float]] = []
    for i, fila in enumerate(A_raw):
        if not isinstance(fila, list) or len(fila) != n:
            recibidas = len(fila) if isinstance(fila, list) else 0
            raise ErrorIterativo(
                f"La matriz A debe ser cuadrada ({n}×{n}): la fila {i + 1} tiene "
                f"{recibidas} columnas.",
                campo="A",
                fila=i + 1,
            )
        fila_nums = [
            parsear_real(fila[j], f"A[{i + 1},{j + 1}]", campo="A", fila=i + 1, columna=j + 1)
            for j in range(n)
        ]
        matriz_lista.append(fila_nums)

    if not b_raw or len(b_raw) != n:
        recibidos = len(b_raw) if b_raw else 0
        raise ErrorIterativo(
            f"El vector b debe tener {n} componentes (coincidiendo con las filas de A); "
            f"se recibieron {recibidos}.",
            campo="b",
        )
    b_lista = [
        parsear_real(b_raw[i], f"b[{i + 1}]", campo="b", fila=i + 1)
        for i in range(n)
    ]

    if x0_raw is None or len(x0_raw) == 0:
        x0_lista = [0.0] * n
    else:
        if len(x0_raw) != n:
            raise ErrorIterativo(
                f"El vector inicial x⁽⁰⁾ debe tener {n} componentes; se recibieron {len(x0_raw)}.",
                campo="x0",
            )
        x0_lista = [
            parsear_real(x0_raw[i], f"x⁽⁰⁾[{i + 1}]", campo="x0", fila=i + 1)
            for i in range(n)
        ]

    tolerancia = parsear_real(tolerancia_raw, "la tolerancia ε", campo="tolerancia")
    if tolerancia <= 0:
        raise ErrorIterativo(
            f"La tolerancia ε debe ser un decimal positivo (> 0); se recibió {tolerancia}.",
            campo="tolerancia",
        )

    max_iter = parsear_entero_positivo(max_iter_raw, "El número máximo de iteraciones", "max_iter")

    A = np.array(matriz_lista, dtype=float)
    b = np.array(b_lista, dtype=float)
    x0 = np.array(x0_lista, dtype=float)
    return A, b, x0, tolerancia, max_iter


# ---------------------------------------------------------------------------
# Análisis de diagonal, dominancia y reordenamiento de filas
# ---------------------------------------------------------------------------
def detectar_ceros_diagonal(A: np.ndarray) -> List[int]:
    """Devuelve los índices (base 0) donde |a_ii| == 0."""
    diagonal = np.abs(np.diag(A))
    return [int(i) for i in range(len(diagonal)) if diagonal[i] <= CERO_NUMERICO]


def evaluar_dominancia_diagonal(A: np.ndarray) -> Dict:
    """Evalúa si A es estrictamente diagonal dominante por filas: |a_ii| > Σ_{j≠i} |a_ij|."""
    n = A.shape[0]
    filas_detalle: List[Dict] = []
    todas_cumplen = True

    for i in range(n):
        diag_abs = float(abs(A[i, i]))
        suma_fuera = float(np.sum(np.abs(A[i, :])) - diag_abs)
        cumple = bool(diag_abs > suma_fuera + CERO_NUMERICO)
        if not cumple:
            todas_cumplen = False
        filas_detalle.append(
            {
                "fila": i + 1,
                "diagonal_abs": diag_abs,
                "suma_otros_abs": suma_fuera,
                "margen": diag_abs - suma_fuera,
                "cumple": cumple,
            }
        )

    if todas_cumplen:
        nota_teorica = (
            "La matriz A ES estrictamente diagonal dominante por filas. "
            "Esta es una condición SUFICIENTE de convergencia: tanto Jacobi como "
            "Gauss-Seidel convergerán para cualquier vector inicial x⁽⁰⁾."
        )
    else:
        nota_teorica = (
            "La matriz A NO es estrictamente diagonal dominante por filas. "
            "Importante: la dominancia diagonal estricta es una condición SUFICIENTE "
            "pero NO NECESARIA para la convergencia; su ausencia no demuestra "
            "automáticamente que los métodos vayan a divergir, aunque no hay garantía previa."
        )

    return {
        "es_estrictamente_dominante": todas_cumplen,
        "filas": filas_detalle,
        "mensaje": nota_teorica,
    }


def _puntuar_permutacion(A_perm: np.ndarray, perm: Tuple[int, ...]) -> Tuple[int, int, float, int]:
    """Criterio de calidad de una permutación de filas (mayor es mejor)."""
    n = A_perm.shape[0]
    estrictas = 0
    debiles = 0
    margen_minimo = float("inf")

    for i in range(n):
        diag_abs = float(abs(A_perm[i, i]))
        suma_fuera = float(np.sum(np.abs(A_perm[i, :])) - diag_abs)
        margen = diag_abs - suma_fuera
        if margen > CERO_NUMERICO:
            estrictas += 1
        if margen >= -CERO_NUMERICO:
            debiles += 1
        if margen < margen_minimo:
            margen_minimo = margen

    filas_sin_mover = sum(1 for i, orig in enumerate(perm) if i == orig)
    return (estrictas, debiles, margen_minimo, filas_sin_mover)


def _describir_permutacion(perm: Tuple[int, ...]) -> str:
    """Describe en español cómo se reordenaron las ecuaciones originales."""
    cambios = [
        f"Fila {nueva + 1} ← Ecuación {orig + 1}"
        for nueva, orig in enumerate(perm)
        if nueva != orig
    ]
    return ", ".join(cambios) if cambios else "Sin cambios (orden original)"


def analizar_y_reordenar(
    A: np.ndarray, b: np.ndarray, permitir_reordenamiento: bool = True
) -> Dict:
    """Evalúa ceros en la diagonal y busca un reordenamiento válido de filas si es necesario."""
    n = A.shape[0]
    identidad = tuple(range(n))
    ceros_iniciales = detectar_ceros_diagonal(A)
    dominancia_inicial = evaluar_dominancia_diagonal(A)

    permutaciones_validas: List[Tuple[Tuple[int, ...], Tuple[int, int, float, int]]] = []
    for perm in permutations(range(n)):
        A_cand = A[list(perm), :]
        if not detectar_ceros_diagonal(A_cand):
            permutaciones_validas.append((perm, _puntuar_permutacion(A_cand, perm)))

    if not permutaciones_validas:
        return {
            "posible_sin_ceros": False,
            "reordenado": False,
            "permutacion": list(identidad),
            "descripcion_permutacion": "No existe permutación válida",
            "ceros_diagonal_inicial": [i + 1 for i in ceros_iniciales],
            "A_trabajo": A,
            "b_trabajo": b,
            "dominancia_inicial": dominancia_inicial,
            "dominancia_final": dominancia_inicial,
            "mensaje": (
                "No es posible continuar: la diagonal principal contiene ceros y no existe "
                "ningún reordenamiento de filas que elimine todos los ceros de la diagonal."
            ),
        }

    mejor_perm, mejor_puntaje = max(permutaciones_validas, key=lambda item: item[1])
    puntaje_actual = _puntuar_permutacion(A, identidad) if not ceros_iniciales else (-1, -1, -1e30, -1)

    requiere_por_ceros = len(ceros_iniciales) > 0
    mejora_estructura = (not dominancia_inicial["es_estrictamente_dominante"]) and (
        mejor_perm != identidad and mejor_puntaje[:3] > puntaje_actual[:3]
    )

    if requiere_por_ceros and not permitir_reordenamiento:
        return {
            "posible_sin_ceros": True,
            "reordenado": False,
            "permutacion": list(identidad),
            "descripcion_permutacion": _describir_permutacion(mejor_perm),
            "ceros_diagonal_inicial": [i + 1 for i in ceros_iniciales],
            "A_trabajo": A,
            "b_trabajo": b,
            "dominancia_inicial": dominancia_inicial,
            "dominancia_final": dominancia_inicial,
            "mensaje": (
                f"La diagonal principal tiene cero(s) en la(s) posición(es) "
                f"{[i + 1 for i in ceros_iniciales]}. Existe un reordenamiento válido "
                f"({_describir_permutacion(mejor_perm)}), pero está desactivado."
            ),
        }

    if (requiere_por_ceros or mejora_estructura) and permitir_reordenamiento:
        indices = list(mejor_perm)
        A_nueva = A[indices, :]
        b_nueva = b[indices]
        dominancia_final = evaluar_dominancia_diagonal(A_nueva)
        motivo = (
            f"se detectaron ceros en la diagonal (posición {[i + 1 for i in ceros_iniciales]})"
            if requiere_por_ceros
            else "se mejoró la dominancia diagonal de las filas"
        )
        return {
            "posible_sin_ceros": True,
            "reordenado": True,
            "permutacion": list(mejor_perm),
            "descripcion_permutacion": _describir_permutacion(mejor_perm),
            "ceros_diagonal_inicial": [i + 1 for i in ceros_iniciales],
            "A_trabajo": A_nueva,
            "b_trabajo": b_nueva,
            "dominancia_inicial": dominancia_inicial,
            "dominancia_final": dominancia_final,
            "mensaje": (
                f"Se reordenaron las filas ({_describir_permutacion(mejor_perm)}) porque {motivo}."
            ),
        }

    return {
        "posible_sin_ceros": True,
        "reordenado": False,
        "permutacion": list(identidad),
        "descripcion_permutacion": "Sin cambios (orden original)",
        "ceros_diagonal_inicial": [],
        "A_trabajo": A,
        "b_trabajo": b,
        "dominancia_inicial": dominancia_inicial,
        "dominancia_final": dominancia_inicial,
        "mensaje": "La diagonal principal no contiene ceros; se conserva el orden original de filas.",
    }


# ---------------------------------------------------------------------------
# Implementación de Jacobi y Gauss-Seidel
# ---------------------------------------------------------------------------
def _ejecutar_metodo_iterativo(
    metodo: str,
    A: np.ndarray,
    b: np.ndarray,
    x0: np.ndarray,
    tolerancia: float,
    max_iter: int,
) -> Dict:
    """Ejecuta Jacobi (actualización simultánea) o Gauss-Seidel (actualización inmediata)."""
    n = A.shape[0]
    x_anterior = x0.astype(float).copy()
    historial: List[Dict] = []

    estado = "max_iteraciones"
    mensaje = (
        f"Se alcanzó el máximo de {max_iter} iteraciones sin cumplir la tolerancia "
        f"ε = {tolerancia:g} (posible no convergencia o convergencia lenta)."
    )
    advertencia: Optional[str] = None
    errores_consecutivos_creciendo = 0
    error_previo: Optional[float] = None

    for k in range(1, max_iter + 1):
        with np.errstate(all="ignore"):
            if metodo == "jacobi":
                # Actualización simultánea: usa exclusivamente x^(k-1).
                x_nuevo = np.zeros(n, dtype=float)
                for i in range(n):
                    suma = np.dot(A[i, :i], x_anterior[:i]) + np.dot(
                        A[i, i + 1 :], x_anterior[i + 1 :]
                    )
                    x_nuevo[i] = (b[i] - suma) / A[i, i]
            else:
                # Actualización inmediata: usa los componentes recién calculados en k.
                x_nuevo = x_anterior.copy()
                for i in range(n):
                    suma = np.dot(A[i, :i], x_nuevo[:i]) + np.dot(
                        A[i, i + 1 :], x_nuevo[i + 1 :]
                    )
                    x_nuevo[i] = (b[i] - suma) / A[i, i]

            if not np.all(np.isfinite(x_nuevo)):
                estado = "divergencia"
                advertencia = (
                    f"Divergencia detectada en la iteración {k}: aparecieron valores no finitos "
                    "(NaN o Inf) por desbordamiento numérico."
                )
                mensaje = advertencia
                break

            error = float(np.max(np.abs(x_nuevo - x_anterior)))
            residuo = float(np.max(np.abs(A @ x_nuevo - b)))

        if (not math.isfinite(error)) or (not math.isfinite(residuo)) or error > UMBRAL_DIVERGENCIA:
            estado = "divergencia"
            advertencia = (
                f"Divergencia detectada en la iteración {k}: el error creció sin control "
                f"(||x⁽ᵏ⁾ - x⁽ᵏ⁻¹⁾||∞ > {UMBRAL_DIVERGENCIA:g})."
            )
            mensaje = advertencia
            break

        historial.append(
            {
                "k": k,
                "x": [float(val) for val in x_nuevo],
                "error": error,
                "residuo": residuo,
            }
        )

        if error_previo is not None and error > error_previo * 1.5:
            errores_consecutivos_creciendo += 1
        else:
            errores_consecutivos_creciendo = 0
        error_previo = error

        if error <= tolerancia:
            estado = "convergencia"
            mensaje = (
                f"Convergencia alcanzada en {k} iteraciones: "
                f"||x⁽ᵏ⁾ - x⁽ᵏ⁻¹⁾||∞ = {error:.6e} ≤ {tolerancia:g}."
            )
            x_anterior = x_nuevo
            break

        x_anterior = x_nuevo

    if estado == "max_iteraciones" and errores_consecutivos_creciendo >= 4:
        advertencia = (
            "Advertencia: el error creció de forma sostenida durante las iteraciones; "
            "el método presenta comportamiento divergente."
        )

    tiene_datos = len(historial) > 0
    solucion_final = historial[-1]["x"] if tiene_datos else None
    error_final = historial[-1]["error"] if tiene_datos else None
    residuo_final = historial[-1]["residuo"] if tiene_datos else None

    return {
        "metodo": metodo,
        "nombre": "Jacobi" if metodo == "jacobi" else "Gauss-Seidel",
        "convergio": estado == "convergencia",
        "estado": estado,
        "mensaje": mensaje,
        "advertencia": advertencia,
        "iteraciones_usadas": len(historial),
        "solucion": solucion_final,
        "error_final": error_final,
        "residuo_final": residuo_final,
        "historial": historial,
    }


def construir_dataframe_iteraciones(resultado_metodo: Dict) -> pd.DataFrame:
    """Construye la tabla de iteraciones usando Pandas DataFrame."""
    historial = resultado_metodo.get("historial", [])
    if not historial:
        return pd.DataFrame()

    n = len(historial[0]["x"])
    filas = []
    for paso in historial:
        fila = {"Iteración (k)": paso["k"]}
        for idx, val in enumerate(paso["x"], start=1):
            fila[f"x{idx}"] = val
        fila["Error ||x^(k)-x^(k-1)||_∞"] = paso["error"]
        fila["Residuo ||Ax-b||_∞"] = paso["residuo"]
        filas.append(fila)
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Orquestador principal (usado por consola y por la API web)
# ---------------------------------------------------------------------------
def resolver_sistemas_iterativos(
    A_raw: List[List],
    b_raw: List,
    x0_raw: Optional[List],
    tolerancia_raw: object = "1e-4",
    max_iter_raw: object = "100",
    permitir_reordenamiento: bool = True,
) -> Dict:
    """Ejecuta el flujo completo del Programa 8: validación, diagnóstico, Jacobi y Gauss-Seidel."""
    A, b, x0, tolerancia, max_iter = validar_y_construir_entradas(
        A_raw, b_raw, x0_raw, tolerancia_raw, max_iter_raw
    )
    n = A.shape[0]
    analisis_diag = analizar_y_reordenar(A, b, permitir_reordenamiento=permitir_reordenamiento)

    base_respuesta = {
        "n": n,
        "A_original": A.tolist(),
        "b_original": b.tolist(),
        "x0": x0.tolist(),
        "tolerancia": tolerancia,
        "max_iter": max_iter,
        "reordenamiento": {
            "posible_sin_ceros": analisis_diag["posible_sin_ceros"],
            "reordenado": analisis_diag["reordenado"],
            "permutacion": analisis_diag["permutacion"],
            "descripcion": analisis_diag["descripcion_permutacion"],
            "ceros_diagonal_inicial": analisis_diag["ceros_diagonal_inicial"],
            "mensaje": analisis_diag["mensaje"],
        },
        "A_utilizada": analisis_diag["A_trabajo"].tolist(),
        "b_utilizada": analisis_diag["b_trabajo"].tolist(),
        "dominancia_inicial": analisis_diag["dominancia_inicial"],
        "dominancia": analisis_diag["dominancia_final"],
    }

    # Si no se pudo evitar ceros en la diagonal, se detiene sin provocar división entre cero.
    if (not analisis_diag["posible_sin_ceros"]) or (
        len(analisis_diag["ceros_diagonal_inicial"]) > 0 and not analisis_diag["reordenado"]
    ):
        return {
            **base_respuesta,
            "ejecutado": False,
            "mensaje_general": analisis_diag["mensaje"],
            "jacobi": None,
            "gauss_seidel": None,
            "comparacion": None,
            "validacion_referencia": None,
            "grafica_error": None,
        }

    A_trab = analisis_diag["A_trabajo"]
    b_trab = analisis_diag["b_trabajo"]

    res_jacobi = _ejecutar_metodo_iterativo("jacobi", A_trab, b_trab, x0, tolerancia, max_iter)
    res_gs = _ejecutar_metodo_iterativo("gauss_seidel", A_trab, b_trab, x0, tolerancia, max_iter)

    # Validación contra solución exacta de referencia (numpy.linalg.solve)
    validacion_ref: Dict = {"disponible": False}
    try:
        x_ref = np.linalg.solve(A_trab, b_trab)
        validacion_ref = {
            "disponible": True,
            "metodo_referencia": "numpy.linalg.solve(A, b)",
            "solucion_referencia": [float(v) for v in x_ref],
            "diferencia_jacobi": (
                float(np.max(np.abs(np.array(res_jacobi["solucion"]) - x_ref)))
                if res_jacobi["solucion"] is not None
                else None
            ),
            "diferencia_gauss_seidel": (
                float(np.max(np.abs(np.array(res_gs["solucion"]) - x_ref)))
                if res_gs["solucion"] is not None
                else None
            ),
        }
    except np.linalg.LinAlgError:
        validacion_ref = {
            "disponible": False,
            "motivo": "La matriz A es singular (det(A) = 0); no existe solución única de referencia.",
        }

    # Comparación entre ambos métodos
    diferencia_entre_metodos: Optional[float] = None
    if res_jacobi["solucion"] is not None and res_gs["solucion"] is not None:
        diferencia_entre_metodos = float(
            np.max(np.abs(np.array(res_jacobi["solucion"]) - np.array(res_gs["solucion"])))
        )

    if res_jacobi["convergio"] and res_gs["convergio"]:
        it_j = res_jacobi["iteraciones_usadas"]
        it_gs = res_gs["iteraciones_usadas"]
        if it_gs < it_j:
            mas_rapido = "Gauss-Seidel"
            resumen_comp = (
                f"Ambos métodos convergieron. Gauss-Seidel necesitó menos iteraciones "
                f"({it_gs} frente a {it_j} de Jacobi, ahorrando {it_j - it_gs} iteración(es))."
            )
        elif it_j < it_gs:
            mas_rapido = "Jacobi"
            resumen_comp = (
                f"Ambos métodos convergieron. Jacobi necesitó menos iteraciones "
                f"({it_j} frente a {it_gs} de Gauss-Seidel)."
            )
        else:
            mas_rapido = "Empate"
            resumen_comp = f"Ambos métodos convergieron en exactamente {it_j} iteraciones."
    elif res_gs["convergio"] and not res_jacobi["convergio"]:
        mas_rapido = "Gauss-Seidel"
        resumen_comp = (
            "Gauss-Seidel alcanzó la convergencia mientras que Jacobi no convergió "
            "dentro de los límites establecidos."
        )
    elif res_jacobi["convergio"] and not res_gs["convergio"]:
        mas_rapido = "Jacobi"
        resumen_comp = (
            "Jacobi alcanzó la convergencia mientras que Gauss-Seidel no convergió "
            "dentro de los límites establecidos."
        )
    else:
        mas_rapido = "Ninguno"
        resumen_comp = (
            "Ninguno de los dos métodos alcanzó la tolerancia solicitada. "
            "Revise la dominancia diagonal o aumente el número máximo de iteraciones."
        )

    # Datos para gráfica comparativa cuando ambos producen historial válido
    grafica_error: Optional[Dict] = None
    if len(res_jacobi["historial"]) > 0 and len(res_gs["historial"]) > 0:
        grafica_error = {
            "disponible": True,
            "tolerancia": tolerancia,
            "jacobi": {
                "iteraciones": [p["k"] for p in res_jacobi["historial"]],
                "errores": [p["error"] for p in res_jacobi["historial"]],
            },
            "gauss_seidel": {
                "iteraciones": [p["k"] for p in res_gs["historial"]],
                "errores": [p["error"] for p in res_gs["historial"]],
            },
        }

    return {
        **base_respuesta,
        "ejecutado": True,
        "mensaje_general": "Cálculo completado.",
        "jacobi": res_jacobi,
        "gauss_seidel": res_gs,
        "comparacion": {
            "metodo_mas_rapido": mas_rapido,
            "iteraciones_jacobi": res_jacobi["iteraciones_usadas"],
            "iteraciones_gauss_seidel": res_gs["iteraciones_usadas"],
            "diferencia_soluciones_inf": diferencia_entre_metodos,
            "resumen": resumen_comp,
        },
        "validacion_referencia": validacion_ref,
        "grafica_error": grafica_error,
    }


def generar_grafica_comparativa(resultado: Dict, ruta_guardado: Optional[str] = None) -> None:
    """Dibuja con Matplotlib la comparación del error ||x^(k) - x^(k-1)||_∞ vs iteración."""
    grafica = resultado.get("grafica_error")
    if not grafica or not grafica.get("disponible"):
        print("  No hay datos válidos suficientes en ambos métodos para graficar el error.")
        return

    import matplotlib
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8.5, 5))
    k_j = grafica["jacobi"]["iteraciones"]
    err_j = grafica["jacobi"]["errores"]
    k_gs = grafica["gauss_seidel"]["iteraciones"]
    err_gs = grafica["gauss_seidel"]["errores"]

    ax.plot(k_j, err_j, marker="o", linewidth=2, color="#2563eb", label="Jacobi")
    ax.plot(k_gs, err_gs, marker="s", linewidth=2, color="#7c3aed", label="Gauss-Seidel")
    ax.axhline(
        grafica["tolerancia"],
        color="#dc2626",
        linestyle="--",
        linewidth=1.2,
        label=f"Tolerancia ε = {grafica['tolerancia']:g}",
    )

    if all(e > 0 for e in err_j + err_gs):
        ax.set_yscale("log")

    ax.set_title("Comparación de convergencia: Error ||x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾||∞ vs Iteración")
    ax.set_xlabel("Iteración (k)")
    ax.set_ylabel("Error en norma infinito")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()

    if ruta_guardado:
        fig.savefig(ruta_guardado, dpi=130)
        print(f"  Gráfica guardada en: {ruta_guardado}")
    elif matplotlib.get_backend().lower() == "agg":
        salida = "grafica_jacobi_gauss_seidel.png"
        fig.savefig(salida, dpi=130)
        print(f"  Gráfica guardada en: {salida}")
    else:
        print("  (Cierre la ventana de la gráfica para continuar.)")
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    # Permite ejecutar directamente el archivo para probar los 3 casos obligatorios
    for caso in CASOS_PRUEBA_P8:
        print("\n" + "=" * 72)
        print(caso["nombre"])
        res = resolver_sistemas_iterativos(
            caso["A"],
            caso["b"],
            caso["x0"],
            caso["tolerancia"],
            caso["max_iter"],
            caso["permitir_reordenamiento"],
        )
        print("Reordenamiento:", res["reordenamiento"]["mensaje"])
        print("Dominancia:", res["dominancia"]["mensaje"])
        if res["ejecutado"]:
            print("\n--- Tabla Jacobi ---")
            print(construir_dataframe_iteraciones(res["jacobi"]).to_string(index=False))
            print("\n--- Tabla Gauss-Seidel ---")
            print(construir_dataframe_iteraciones(res["gauss_seidel"]).to_string(index=False))
            print("\nComparación:", res["comparacion"]["resumen"])