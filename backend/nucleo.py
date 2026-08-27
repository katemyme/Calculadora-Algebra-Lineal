"""Núcleo matemático de la calculadora de sistemas lineales Ax = b.

Este módulo resuelve un sistema de ecuaciones lineales aplicando el método
de Gauss-Jordan (eliminación por filas hasta la forma escalonada reducida).

CUMPLIMIENTO DE RESTRICCIONES ACADÉMICAS
----------------------------------------
- No se importa NumPy, SciPy ni funciones de álgebra lineal de `math`.
- Toda la aritmética matricial se implementa a mano con listas anidadas,
  bucles `for`/`while` y condicionales `if`/`else`.
- La única dependencia externa es `fractions.Fraction`, que aporta
  aritmética EXACTA: un pivote es cero o no lo es, sin tolerancias.
- Cada bloque de código lleva un comentario que relaciona la instrucción
  de Python con la operación elemental por fila equivalente:
      Fᵢ ↔ Fⱼ        (intercambio de filas)
      Fᵢ → (1/p)·Fᵢ  (normalización del pivote)
      Fₖ → Fₖ − c·Fᵢ (eliminación gaussiana)
"""

from fractions import Fraction
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constantes de configuración
# ---------------------------------------------------------------------------
DIMENSION_MINIMA: int = 1          # mínimo de ecuaciones / incógnitas admitido
DIMENSION_MAXIMA: int = 8          # máximo de ecuaciones / incógnitas admitido

# Traductor de dígitos a subíndices Unicode para escribir F₁, F₂, ...
_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


# ---------------------------------------------------------------------------
# Excepción propia
# ---------------------------------------------------------------------------
class ErrorDeEntrada(Exception):
    """Error atribuible a los datos del usuario, no a un fallo del programa.

    Cuando se conoce la ubicación del dato culpable, se guardan la fila y la
    columna (base 1) para que la interfaz pueda resaltar la celda concreta.
    """

    def __init__(
        self,
        mensaje: str,
        fila: Optional[int] = None,
        columna: Optional[int] = None,
    ) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.fila = fila
        self.columna = columna


# ---------------------------------------------------------------------------
# Utilidades internas de matrices
# ---------------------------------------------------------------------------
def _copiar_matriz(matriz: List[List[Fraction]]) -> List[List[Fraction]]:
    """Devuelve una copia profunda de la matriz.

    No implementa una operación por fila: se usa para conservar el estado
    de la matriz "después" de cada operación sin que operaciones posteriores
    lo modifiquen (las listas de Python se comparten por referencia).
    """
    # Se reconstruye fila por fila para no compartir las sublistas.
    return [fila[:] for fila in matriz]


def _validar_dimensiones(m: int, n: int) -> None:
    """Comprueba que m y n sean enteros dentro del rango permitido.

    No es una operación por fila: es una validación previa de tamaño.
    """
    for nombre, valor in (("m (ecuaciones)", m), ("n (incógnitas)", n)):
        if not isinstance(valor, int) or not (
            DIMENSION_MINIMA <= valor <= DIMENSION_MAXIMA
        ):
            raise ErrorDeEntrada(
                f"La dimensión {nombre} debe ser un entero entre "
                f"{DIMENSION_MINIMA} y {DIMENSION_MAXIMA}; se recibió '{valor}'."
            )


# ---------------------------------------------------------------------------
# Utilidades de formato (solo texto para las notaciones y descripciones)
# ---------------------------------------------------------------------------
def _subindice(indice_base_cero: int) -> str:
    """Convierte un índice de fila (base 0) en su subíndice Unicode (base 1)."""
    return str(indice_base_cero + 1).translate(_SUBINDICES)


def _formatear_fraccion(valor: Fraction) -> str:
    """Escribe una fracción como '3', '-3' o '1/2' (sin decimales)."""
    if valor.denominator == 1:               # es un entero exacto
        return str(valor.numerator)
    return f"{valor.numerator}/{valor.denominator}"


def _factor_por_fila(coeficiente: Fraction, indice_fila: int) -> str:
    """Escribe el término 'c·Fᵢ' de una operación, omitiendo el 1."""
    magnitud = _formatear_fraccion(abs(coeficiente))
    if magnitud == "1":                       # el coeficiente 1 no se escribe
        return f"F{_subindice(indice_fila)}"
    return f"{magnitud}·F{_subindice(indice_fila)}"


# ---------------------------------------------------------------------------
# Lectura de datos
# ---------------------------------------------------------------------------
def parsear_valor(texto: str) -> Fraction:
    """Convierte una cadena de texto en una fracción exacta.

    Acepta enteros ('3'), negativos ('-7'), decimales ('2.5') y fracciones
    ('1/3', '-4/6'). Una celda vacía representa el coeficiente 0. No es una
    operación por fila: prepara los coeficientes sobre los que después
    actuarán las operaciones elementales.
    """
    limpio = texto.strip()

    # Celda vacía -> ausencia de término -> coeficiente 0.
    if limpio == "":
        return Fraction(0)

    # Forma fracción 'numerador/denominador'.
    if "/" in limpio:
        partes = limpio.split("/")
        if len(partes) != 2:
            raise ErrorDeEntrada(f"Valor no reconocido: se recibió '{texto}'.")
        try:
            numerador = int(partes[0].strip())
            denominador = int(partes[1].strip())
        except ValueError:
            raise ErrorDeEntrada(f"Fracción inválida: se recibió '{texto}'.")
        if denominador == 0:
            raise ErrorDeEntrada(f"División entre cero en el valor '{texto}'.")
        return Fraction(numerador, denominador)

    # Forma entera o decimal ('2.5' -> 5/2 exacto).
    try:
        return Fraction(limpio)
    except ValueError:
        raise ErrorDeEntrada(f"Valor no reconocido: se recibió '{texto}'.")


def construir_matriz_aumentada(
    m: int, n: int, datos: List[List[str]]
) -> List[List[Fraction]]:
    """Valida dimensiones y construye la matriz aumentada [A | b].

    No aplica operaciones por fila: traduce la entrada textual a la
    estructura de listas de `Fraction` sobre la que operará la eliminación.
    La columna de índice n contiene el vector de términos independientes b.
    """
    _validar_dimensiones(m, n)

    # Debe haber exactamente m ecuaciones (filas).
    if len(datos) != m:
        raise ErrorDeEntrada(
            f"Se esperaban {m} ecuaciones (filas) y se recibieron {len(datos)}."
        )

    matriz: List[List[Fraction]] = []
    for indice_fila in range(m):
        fila_texto = datos[indice_fila]

        # Cada fila debe tener n coeficientes + 1 término independiente.
        if len(fila_texto) != n + 1:
            raise ErrorDeEntrada(
                f"La ecuación {indice_fila + 1} debe tener {n + 1} valores "
                f"(coeficientes y término independiente); tiene {len(fila_texto)}.",
                fila=indice_fila + 1,
            )

        fila: List[Fraction] = []
        for indice_columna in range(n + 1):
            try:
                fila.append(parsear_valor(fila_texto[indice_columna]))
            except ErrorDeEntrada as error:
                # Se re-lanza indicando fila y columna concretas (base 1).
                raise ErrorDeEntrada(
                    f"Celda inválida en fila {indice_fila + 1}, columna "
                    f"{indice_columna + 1}: {error.mensaje}",
                    fila=indice_fila + 1,
                    columna=indice_columna + 1,
                )
        matriz.append(fila)
    return matriz


# ---------------------------------------------------------------------------
# Registro de pasos (una operación elemental por diccionario)
# ---------------------------------------------------------------------------
def _registrar_intercambio(
    matriz: List[List[Fraction]], fila_a: int, fila_b: int, columna: int
) -> Dict:
    """Construye el registro de un paso de tipo Fᵢ ↔ Fⱼ."""
    return {
        "tipo": "intercambio",
        "notacion": f"F{_subindice(fila_a)} ↔ F{_subindice(fila_b)}",
        "descripcion": (
            f"Se intercambian las filas {fila_a + 1} y {fila_b + 1} para situar "
            f"en la posición pivote el elemento de mayor valor absoluto de la "
            f"columna {columna + 1} (pivoteo parcial)."
        ),
        "filas_afectadas": [fila_a, fila_b],
        "columna_pivote": columna,
        "matriz": _copiar_matriz(matriz),   # estado DESPUÉS del intercambio
    }


def _registrar_normalizacion(
    matriz: List[List[Fraction]], fila: int, columna: int, pivote: Fraction
) -> Dict:
    """Construye el registro de un paso de tipo Fᵢ → (1/p)·Fᵢ."""
    inverso = _formatear_fraccion(Fraction(1, 1) / pivote)
    return {
        "tipo": "normalizacion",
        "notacion": f"F{_subindice(fila)} → ({inverso})·F{_subindice(fila)}",
        "descripcion": (
            f"Se divide la fila {fila + 1} entre el pivote "
            f"{_formatear_fraccion(pivote)} para que el elemento pivote de la "
            f"columna {columna + 1} valga 1."
        ),
        "filas_afectadas": [fila],
        "columna_pivote": columna,
        "matriz": _copiar_matriz(matriz),   # estado DESPUÉS de la normalización
    }


def _registrar_eliminacion(
    matriz: List[List[Fraction]],
    fila: int,
    fila_pivote: int,
    columna: int,
    factor: Fraction,
) -> Dict:
    """Construye el registro de un paso de tipo Fₖ → Fₖ − c·Fᵢ."""
    # Si el factor es positivo se resta; si es negativo, restar un negativo suma.
    signo = "-" if factor > 0 else "+"
    return {
        "tipo": "eliminacion",
        "notacion": (
            f"F{_subindice(fila)} → F{_subindice(fila)} {signo} "
            f"{_factor_por_fila(factor, fila_pivote)}"
        ),
        "descripcion": (
            f"Se resta {_formatear_fraccion(factor)} veces la fila pivote "
            f"{fila_pivote + 1} a la fila {fila + 1} para anular su elemento "
            f"en la columna {columna + 1}."
        ),
        "filas_afectadas": [fila],
        "columna_pivote": columna,
        "matriz": _copiar_matriz(matriz),   # estado DESPUÉS de la eliminación
    }


# ---------------------------------------------------------------------------
# Eliminación de Gauss-Jordan
# ---------------------------------------------------------------------------
def _buscar_fila_pivote(
    matriz: List[List[Fraction]], m: int, fila_inicial: int, columna: int
) -> int:
    """Devuelve la fila con mayor valor absoluto en la columna dada.

    Implementa la estrategia de pivoteo parcial previa a un posible
    intercambio de filas Fᵢ ↔ Fⱼ. Solo mira de `fila_inicial` hacia abajo.
    """
    fila_maxima = fila_inicial
    valor_maximo = abs(matriz[fila_inicial][columna])
    for fila in range(fila_inicial + 1, m):
        candidato = abs(matriz[fila][columna])
        if candidato > valor_maximo:          # se guarda el máximo encontrado
            valor_maximo = candidato
            fila_maxima = fila
    return fila_maxima


def _anular_columna(
    matriz: List[List[Fraction]], m: int, fila_pivote: int, columna: int
) -> List[Dict]:
    """Aplica Fₖ → Fₖ − c·Fᵢ a todas las filas salvo la del pivote.

    Anula la columna del pivote tanto por encima como por debajo de él
    (eliminación de Gauss-Jordan, no solo de Gauss).
    """
    pasos: List[Dict] = []
    for fila in range(m):
        if fila == fila_pivote:               # la fila pivote no se toca a sí misma
            continue

        factor = matriz[fila][columna]        # c = elemento a anular
        if factor == 0:                       # ya vale 0: no hace falta operar
            continue

        # Fₖ → Fₖ − factor·Fᵢ  (resta término a término de toda la fila)
        matriz[fila] = [
            valor_fila - factor * valor_pivote
            for valor_fila, valor_pivote in zip(matriz[fila], matriz[fila_pivote])
        ]
        pasos.append(
            _registrar_eliminacion(matriz, fila, fila_pivote, columna, factor)
        )
    return pasos


def escalonar(
    Ab: List[List[Fraction]], m: int, n: int
) -> Tuple[List[List[Fraction]], List[Dict], List[int]]:
    """Lleva [A | b] a su forma escalonada reducida por filas (Gauss-Jordan).

    Devuelve (matriz_reducida, lista_de_pasos, columnas_pivote). Recorre las
    columnas de A de izquierda a derecha con un contador `fila_pivote`:
      1. Pivoteo parcial: busca el mayor |valor| de la columna.
      2. Si toda la columna es 0 -> variable libre; avanza sin subir fila_pivote.
      3. Fᵢ ↔ Fⱼ  si el pivote no está en su sitio.
      4. Fᵢ → (1/p)·Fᵢ  para dejar el pivote en 1.
      5. Fₖ → Fₖ − c·Fᵢ  para anular la columna arriba y abajo.
      6. Incrementa fila_pivote.
    """
    matriz = _copiar_matriz(Ab)               # se trabaja sobre una copia
    pasos: List[Dict] = []
    columnas_pivote: List[int] = []
    fila_pivote = 0                           # primera fila aún sin pivote fijado

    for columna in range(n):                  # solo columnas de A; b queda fuera
        if fila_pivote >= m:                  # ya no quedan filas donde poner pivotes
            break

        fila_maxima = _buscar_fila_pivote(matriz, m, fila_pivote, columna)

        # Paso 2: columna nula de fila_pivote hacia abajo -> variable libre.
        if matriz[fila_maxima][columna] == 0:
            continue                          # avanza de columna SIN subir fila_pivote

        # Paso 3: Fᵢ ↔ Fⱼ para traer el mayor pivote a la fila de trabajo.
        if fila_maxima != fila_pivote:
            matriz[fila_pivote], matriz[fila_maxima] = (
                matriz[fila_maxima],
                matriz[fila_pivote],
            )
            pasos.append(
                _registrar_intercambio(matriz, fila_pivote, fila_maxima, columna)
            )

        # Paso 4: Fᵢ → (1/p)·Fᵢ para normalizar el pivote a 1.
        pivote = matriz[fila_pivote][columna]
        if pivote != 1:
            matriz[fila_pivote] = [valor / pivote for valor in matriz[fila_pivote]]
            pasos.append(
                _registrar_normalizacion(matriz, fila_pivote, columna, pivote)
            )

        # Paso 5: Fₖ → Fₖ − c·Fᵢ para anular el resto de la columna.
        pasos.extend(_anular_columna(matriz, m, fila_pivote, columna))

        # Paso 6: esta columna ya tiene pivote; pasa a la siguiente fila.
        columnas_pivote.append(columna)
        fila_pivote += 1

    return matriz, pasos, columnas_pivote


# ---------------------------------------------------------------------------
# Rangos y clasificación (Teorema de Rouché-Frobenius)
# ---------------------------------------------------------------------------
def calcular_rangos(
    matriz_reducida: List[List[Fraction]],
    m: int,
    n: int,
    columnas_pivote: List[int],
) -> Tuple[int, int]:
    """Calcula rango(A) y rango(A|b) a partir de la forma escalonada reducida.

    No es una operación por fila: cuenta pivotes sobre la matriz ya reducida.
    - rango(A): número de columnas pivote con índice < n.
    - rango(A|b): rango(A) + 1 si existe una fila 0 0 ⋯ 0 | k con k ≠ 0.
    """
    rango_a = sum(1 for columna in columnas_pivote if columna < n)

    rango_ab = rango_a
    for fila in matriz_reducida[:m]:          # se recorren las m filas del sistema
        coeficientes_nulos = all(valor == 0 for valor in fila[:n])
        termino_no_nulo = fila[n] != 0
        if coeficientes_nulos and termino_no_nulo:   # fila del tipo 0 = k, k ≠ 0
            rango_ab = rango_a + 1
            break
    return rango_a, rango_ab


def clasificar(rango_a: int, rango_ab: int, n: int) -> Dict:
    """Clasifica el sistema comparando rango(A), rango(A|b) y n.

    No es una operación por fila: aplica el Teorema de Rouché-Frobenius.
    """
    if rango_a < rango_ab:
        return {
            "tipo": "inconsistente",
            "titulo": "Sistema Inconsistente",
            "explicacion": (
                f"Como rango(A) = {rango_a} es menor que rango(A|b) = {rango_ab}, "
                f"aparece una ecuación imposible (0 = k con k ≠ 0): el sistema "
                f"no tiene solución."
            ),
            "grados_de_libertad": 0,
        }

    if rango_a == n:
        return {
            "tipo": "determinado",
            "titulo": "Sistema Consistente Determinado",
            "explicacion": (
                f"Como rango(A) = rango(A|b) = {rango_a} y coincide con el número "
                f"de incógnitas n = {n}, el sistema tiene solución única."
            ),
            "grados_de_libertad": 0,
        }

    grados = n - rango_a                       # nº de variables libres
    return {
        "tipo": "indeterminado",
        "titulo": "Sistema Consistente Indeterminado",
        "explicacion": (
            f"Como rango(A) = rango(A|b) = {rango_a} es menor que el número de "
            f"incógnitas n = {n}, el sistema tiene infinitas soluciones con "
            f"{grados} variable(s) libre(s)."
        ),
        "grados_de_libertad": grados,
    }


# ---------------------------------------------------------------------------
# Construcción de la solución
# ---------------------------------------------------------------------------
def _solucion_determinada(
    matriz_reducida: List[List[Fraction]], n: int, columnas_pivote: List[int]
) -> Dict:
    """Lee la solución única directamente de la columna b ya reducida.

    En la forma escalonada reducida cada fila pivote queda como
    0 ⋯ 1 ⋯ 0 | valor, así que xⱼ = término independiente de esa fila
    (no hace falta sustitución hacia atrás).
    """
    valores_verificacion: List[Fraction] = [Fraction(0)] * n
    detalle: List[Dict] = []
    for indice_fila, columna in enumerate(columnas_pivote):
        valor = matriz_reducida[indice_fila][n]      # xⱼ = b reducido de la fila
        valores_verificacion[columna] = valor
        detalle.append({"variable": columna, "valor": valor})
    return {
        "tipo": "determinado",
        "valores": detalle,
        "valores_verificacion": valores_verificacion,
    }


def _solucion_indeterminada(
    matriz_reducida: List[List[Fraction]], n: int, columnas_pivote: List[int]
) -> Dict:
    """Expresa cada variable básica en función de las variables libres.

    Para una fila pivote 0 ⋯ 1 ⋯ (a) ⋯ | c, se despeja
    x_pivote = c − a·x_libre, es decir el coeficiente de x_libre es −a.
    """
    columnas_libres = [c for c in range(n) if c not in columnas_pivote]
    expresiones: List[Dict] = []
    for indice_fila, columna_pivote in enumerate(columnas_pivote):
        constante = matriz_reducida[indice_fila][n]   # término independiente c
        terminos_libres = []
        for columna_libre in columnas_libres:
            # coeficiente de x_libre al despejar = − (valor en esa columna)
            coeficiente = -matriz_reducida[indice_fila][columna_libre]
            if coeficiente != 0:
                terminos_libres.append(
                    {"variable": columna_libre, "coeficiente": coeficiente}
                )
        expresiones.append(
            {
                "variable": columna_pivote,
                "constante": constante,
                "terminos_libres": terminos_libres,
            }
        )

    # Solución particular: se asigna 0 a cada variable libre.
    particular: List[Fraction] = [Fraction(0)] * n
    for expresion in expresiones:
        # x_libre = 0  ->  x_básica = su término constante
        particular[expresion["variable"]] = expresion["constante"]

    return {
        "tipo": "indeterminado",
        "variables_libres": columnas_libres,
        "expresiones": expresiones,
        "solucion_particular": particular,
        "valores_verificacion": particular,
    }


def _solucion_inconsistente(
    matriz_reducida: List[List[Fraction]], n: int
) -> Dict:
    """Localiza la fila contradictoria 0 0 ⋯ 0 | k (k ≠ 0) que prueba la incompatibilidad."""
    for indice_fila, fila in enumerate(matriz_reducida):
        if all(valor == 0 for valor in fila[:n]) and fila[n] != 0:
            return {
                "tipo": "inconsistente",
                "fila_contradictoria": {
                    "indice": indice_fila,
                    "coeficientes": fila[:n],
                    "termino_independiente": fila[n],
                },
                "valores_verificacion": None,
            }
    return {
        "tipo": "inconsistente",
        "fila_contradictoria": None,
        "valores_verificacion": None,
    }


def resolver(
    matriz_reducida: List[List[Fraction]],
    n: int,
    columnas_pivote: List[int],
    clasificacion: Dict,
) -> Dict:
    """Devuelve la solución según la clasificación del sistema.

    No es una operación por fila: interpreta la matriz ya escalonada.
    """
    tipo = clasificacion["tipo"]
    if tipo == "inconsistente":
        return _solucion_inconsistente(matriz_reducida, n)
    if tipo == "determinado":
        return _solucion_determinada(matriz_reducida, n, columnas_pivote)
    return _solucion_indeterminada(matriz_reducida, n, columnas_pivote)


# ---------------------------------------------------------------------------
# Verificación sobre el sistema original
# ---------------------------------------------------------------------------
def verificar(
    Ab_original: List[List[Fraction]],
    valores: Optional[List[Fraction]],
    m: int,
    n: int,
) -> List[Dict]:
    """Sustituye la solución en el sistema ORIGINAL y compara término a término.

    Se usa `Ab_original` (copia previa a escalonar, ya que la matriz de
    trabajo se destruye). Con `Fraction` la comparación es exacta, sin epsilon.
    """
    if valores is None:                       # sistema inconsistente: nada que verificar
        return []

    comprobaciones: List[Dict] = []
    for indice_ecuacion in range(m):
        fila = Ab_original[indice_ecuacion]
        terminos: List[str] = []
        acumulado = Fraction(0)               # lado izquierdo de la ecuación

        for indice_variable in range(n):
            coeficiente = fila[indice_variable]
            valor = valores[indice_variable]
            acumulado += coeficiente * valor  # suma de aᵢⱼ·xⱼ
            terminos.append(
                f"({_formatear_fraccion(coeficiente)})"
                f"({_formatear_fraccion(valor)})"
            )

        esperado = fila[n]                     # término independiente original
        comprobaciones.append(
            {
                "ecuacion": indice_ecuacion + 1,
                "sustitucion": " + ".join(terminos),
                "obtenido": acumulado,
                "esperado": esperado,
                "coincide": acumulado == esperado,   # comparación exacta
            }
        )
    return comprobaciones


# ---------------------------------------------------------------------------
# Orquestador: único punto de entrada que necesita la API
# ---------------------------------------------------------------------------
def resolver_sistema(m: int, n: int, datos: List[List[str]]) -> Dict:
    """Encadena lectura, escalonamiento, clasificación, solución y verificación.

    Devuelve el resultado completo del problema Ax = b.
    """
    Ab = construir_matriz_aumentada(m, n, datos)
    Ab_original = _copiar_matriz(Ab)          # se conserva: escalonar destruye Ab

    matriz_reducida, pasos, columnas_pivote = escalonar(Ab, m, n)
    rango_a, rango_ab = calcular_rangos(matriz_reducida, m, n, columnas_pivote)
    clasificacion = clasificar(rango_a, rango_ab, n)
    solucion = resolver(matriz_reducida, n, columnas_pivote, clasificacion)
    verificacion = verificar(
        Ab_original, solucion.get("valores_verificacion"), m, n
    )

    return {
        "matriz_inicial": Ab_original,
        "pasos": pasos,
        "matriz_reducida": matriz_reducida,
        "columnas_pivote": columnas_pivote,
        "rango_A": rango_a,
        "rango_Ab": rango_ab,
        "clasificacion": clasificacion,
        "solucion": solucion,
        "verificacion": verificacion,
    }
