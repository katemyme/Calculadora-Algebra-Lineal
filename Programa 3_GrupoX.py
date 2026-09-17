"""Programa 3 — Calculadora de Álgebra Lineal.

Operaciones algebraicas en ℝⁿ, combinación lineal y ecuaciones matriciales.

CUMPLIMIENTO DE RESTRICCIONES ACADÉMICAS
----------------------------------------
- Archivo autocontenido: no importa ningún módulo (ni NumPy, SciPy, SymPy,
  fractions ni math).
- Vectores y matrices son listas de Python; todas las operaciones se hacen
  a mano con bucles for/while, condicionales if/else y funciones.
- Se trabaja con números float. Como un float rara vez es exactamente 0,
  todo valor con |x| < EPS se trata como cero (EPS = 1e-10).
- El Gauss-Jordan es una copia de `escalonar` del Programa 2
  (backend/nucleo.py), adaptada a float:
      * `== 0` se sustituye por |x| < EPS,
      * el pivote normalizado se fija en 1.0 exacto,
      * los residuos |x| < EPS se limpian a 0.0 tras cada operación.
  Operaciones elementales por fila que aparecen en los comentarios:
      Fᵢ ↔ Fⱼ        (intercambio de filas)
      Fᵢ → (1/p)·Fᵢ  (normalización del pivote)
      Fₖ → Fₖ − c·Fᵢ (eliminación)
"""


# Constantes de configuración

EPS = 1e-10                 # tolerancia: |x| < EPS  ⇒  x se considera 0
DECIMALES = 6               # decimales máximos al imprimir un número
DIMENSION_MINIMA = 1        # mismos límites que el Programa 2
DIMENSION_MAXIMA = 8

# Traductor de dígitos a subíndices Unicode para escribir F₁, v₂, x₃, ...
_SUBINDICES = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


# Utilidades numéricas y de formato

def es_cero(valor):
    """Prueba de cero con tolerancia: x ≡ 0  ⇔  |x| < EPS."""
    return abs(valor) < EPS


def limpiar(valor):
    """Redondeo del ruido de coma flotante: si |x| < EPS entonces x := 0.0.

    Devolver 0.0 (y no -0.0) evita que se imprima "-0".
    """
    if es_cero(valor):
        return 0.0
    return valor


def formatear_numero(valor):
    """Representación textual de x ∈ ℝ: entero si x ∈ ℤ, si no hasta 6 decimales.

    Nunca produce "-0" ni "-0.0": los valores con |x| < EPS se escriben "0".
    """
    if es_cero(valor):
        return "0"
    redondeado = round(valor, DECIMALES)
    entero = int(round(redondeado))
    if redondeado == entero:                  # x ∈ ℤ (int(-0.0) == 0 → "0")
        return str(entero)
    texto = f"{redondeado:.{DECIMALES}f}".rstrip("0").rstrip(".")
    if texto == "-0":
        return "0"
    return texto


def subindice(indice_base_cero):
    """Convierte el índice i (base 0) en el subíndice Unicode de i + 1."""
    return str(indice_base_cero + 1).translate(_SUBINDICES)


def formatear_vector(vector):
    """Escribe v = (v₁, v₂, …, vₙ) como texto."""
    return "(" + ", ".join(formatear_numero(x) for x in vector) + ")"


def nombres_parametros(cantidad):
    """Nombra los parámetros de las variables libres: t si hay una; t1, t2, … si hay varias.

    Igual que en el Programa 2: x_libre = t.
    """
    if cantidad == 1:
        return ["t"]
    return [f"t{indice + 1}" for indice in range(cantidad)]


def formatear_expresion(constante, terminos):
    """Escribe c + a₁·t₁ + a₂·t₂ + … omitiendo los coeficientes nulos y el 1.

    `terminos` es una lista de pares (coeficiente, nombre_parametro).
    """
    texto = ""
    if not es_cero(constante):
        texto = formatear_numero(constante)

    for coeficiente, nombre in terminos:
        if es_cero(coeficiente):
            continue
        magnitud = formatear_numero(abs(coeficiente))
        if magnitud == "1":                   # 1·t se escribe t
            magnitud = ""
        if texto == "":                       # primer término de la expresión
            signo = "-" if coeficiente < 0 else ""
            texto = f"{signo}{magnitud}{nombre}"
        else:
            signo = " - " if coeficiente < 0 else " + "
            texto = f"{texto}{signo}{magnitud}{nombre}"

    if texto == "":                           # todo era cero
        return "0"
    return texto


def imprimir_matriz(matriz, nombre="", columnas_izquierda=None, sangria="    "):
    """Imprime una matriz m×n con las columnas alineadas a la derecha.

    Si `columnas_izquierda` = n se dibuja la barra de la aumentada [A | b]
    entre la columna n y la n + 1.
    """
    if nombre != "":
        print(f"  {nombre} =")
    if len(matriz) == 0:
        print(f"{sangria}[ ]")
        return

    columnas = len(matriz[0])
    textos = [[formatear_numero(x) for x in fila] for fila in matriz]

    # Ancho de cada columna j = longitud del texto más largo de esa columna.
    anchos = [0] * columnas
    for fila in textos:
        for j in range(columnas):
            if len(fila[j]) > anchos[j]:
                anchos[j] = len(fila[j])

    for fila in textos:
        celdas = ""
        for j in range(columnas):
            if columnas_izquierda is not None and j == columnas_izquierda:
                celdas += " |"
            celdas += " " + fila[j].rjust(anchos[j])
        print(f"{sangria}[{celdas} ]")


def imprimir_titulo(texto):
    """Encabezado de sección (sin operación algebraica)."""
    print()
    print("-" * 62)
    print(f"  {texto}")
    print("-" * 62)


# ---------------------------------------------------------------------------
# Operaciones con vectores de ℝⁿ
# ---------------------------------------------------------------------------
def suma_vectores(u, v):
    """Suma en ℝⁿ: (u + v)ᵢ = uᵢ + vᵢ,  i = 1, …, n.

    Devuelve None si dim(u) ≠ dim(v).
    """
    if len(u) != len(v):
        return None
    resultado = []
    for i in range(len(u)):                   # i recorre las n componentes
        resultado.append(limpiar(u[i] + v[i]))
    return resultado


def resta_vectores(u, v):
    """Resta en ℝⁿ: (u − v)ᵢ = uᵢ − vᵢ,  i = 1, …, n.

    Devuelve None si dim(u) ≠ dim(v).
    """
    if len(u) != len(v):
        return None
    resultado = []
    for i in range(len(u)):
        resultado.append(limpiar(u[i] - v[i]))
    return resultado


def escalar_por_vector(c, v):
    """Producto por escalar en ℝⁿ: (c·v)ᵢ = c·vᵢ."""
    resultado = []
    for i in range(len(v)):
        resultado.append(limpiar(c * v[i]))
    return resultado


def combinar_vectores(pesos, vectores):
    """Combinación lineal: c₁·v₁ + c₂·v₂ + … + cₖ·vₖ ∈ ℝⁿ.

    Se construye con las dos operaciones de ℝⁿ: acumulado := acumulado + cⱼ·vⱼ.
    """
    acumulado = [0.0] * len(vectores[0])      # vector cero de ℝⁿ
    for j in range(len(vectores)):            # j recorre los k vectores
        acumulado = suma_vectores(acumulado, escalar_por_vector(pesos[j], vectores[j]))
    return acumulado


def vectores_iguales(u, v):
    """Igualdad en ℝⁿ con tolerancia: u = v  ⇔  |uᵢ − vᵢ| < EPS para todo i."""
    if len(u) != len(v):
        return False
    for i in range(len(u)):
        if not es_cero(u[i] - v[i]):
            return False
    return True


# ---------------------------------------------------------------------------
# Operaciones con matrices
# ---------------------------------------------------------------------------
def dimensiones(matriz):
    """Orden de la matriz: A ∈ ℝ^(m×n) → (m, n)."""
    if len(matriz) == 0:
        return 0, 0
    return len(matriz), len(matriz[0])


def formatear_dimension(matriz):
    """Escribe el orden de A como "m×n"."""
    m, n = dimensiones(matriz)
    return f"{m}×{n}"


def copiar_matriz(matriz):
    """Copia elemento a elemento: Bᵢⱼ = Aᵢⱼ (sin compartir filas)."""
    return [fila[:] for fila in matriz]


def suma_matrices(A, B):
    """Suma de matrices m×n: (A + B)ᵢⱼ = aᵢⱼ + bᵢⱼ.

    Devuelve None si A y B no tienen el mismo orden.
    """
    if dimensiones(A) != dimensiones(B):
        return None
    m, n = dimensiones(A)
    C = []
    for i in range(m):                        # i recorre las filas
        fila = []
        for j in range(n):                    # j recorre las columnas
            fila.append(limpiar(A[i][j] + B[i][j]))
        C.append(fila)
    return C


def resta_matrices(A, B):
    """Resta de matrices m×n: (A − B)ᵢⱼ = aᵢⱼ − bᵢⱼ.

    Devuelve None si A y B no tienen el mismo orden.
    """
    if dimensiones(A) != dimensiones(B):
        return None
    m, n = dimensiones(A)
    C = []
    for i in range(m):
        fila = []
        for j in range(n):
            fila.append(limpiar(A[i][j] - B[i][j]))
        C.append(fila)
    return C


def escalar_por_matriz(c, A):
    """Producto por escalar: (c·A)ᵢⱼ = c·aᵢⱼ."""
    m, n = dimensiones(A)
    C = []
    for i in range(m):
        fila = []
        for j in range(n):
            fila.append(limpiar(c * A[i][j]))
        C.append(fila)
    return C


def producto_compatible(A, B):
    """A·B está definido  ⇔  columnas(A) = filas(B)."""
    return dimensiones(A)[1] == dimensiones(B)[0]


def producto_matrices(A, B):
    """Producto matricial A(m×n)·B(n×p) = C(m×p):  cᵢⱼ = Σₖ aᵢₖ·bₖⱼ,  k = 1, …, n.

    Devuelve None si columnas(A) ≠ filas(B).
    """
    if not producto_compatible(A, B):
        return None
    m, n = dimensiones(A)
    p = dimensiones(B)[1]

    C = []
    for i in range(m):                        # i: fila de A = fila de C que se llena
        fila_c = []
        for j in range(p):                    # j: columna de B = columna de C que se llena
            suma = 0.0
            for k in range(n):                # k: recorre a la vez la fila i de A y la columna j de B
                suma += A[i][k] * B[k][j]     # acumula aᵢₖ·bₖⱼ
            fila_c.append(limpiar(suma))      # cᵢⱼ = Σₖ aᵢₖ·bₖⱼ
        C.append(fila_c)
    return C


def vector_a_columna(vector):
    """Identifica x ∈ ℝⁿ con la matriz columna n×1: (X)ᵢ₁ = xᵢ."""
    return [[x] for x in vector]


def columna_a_vector(columna):
    """Identifica la matriz columna n×1 con x ∈ ℝⁿ: xᵢ = (X)ᵢ₁."""
    return [fila[0] for fila in columna]


# ---------------------------------------------------------------------------
# Matrices aumentadas
# ---------------------------------------------------------------------------
def aumentada_desde_matriz(A, b):
    """Construye [A | b]:  fila i = (aᵢ₁, …, aᵢₙ, bᵢ)."""
    return [A[i][:] + [b[i]] for i in range(len(A))]


def aumentada_desde_columnas(vectores, b):
    """Construye [v₁ v₂ … vₖ | b] con los vectores como COLUMNAS: Mᵢⱼ = (vⱼ)ᵢ, Mᵢ,ₖ₊₁ = bᵢ.

    Así el sistema c₁·v₁ + … + cₖ·vₖ = b queda escrito como [V | b].
    """
    n = len(b)
    k = len(vectores)
    matriz = []
    for i in range(n):                        # i: componente (fila)
        fila = []
        for j in range(k):                    # j: vector (columna)
            fila.append(vectores[j][i])
        fila.append(b[i])
        matriz.append(fila)
    return matriz


# ---------------------------------------------------------------------------
# Eliminación de Gauss-Jordan (copiada del Programa 2 y adaptada a float)
# ---------------------------------------------------------------------------
def _factor_por_fila(coeficiente, indice_fila):
    """Escribe el término 'c·Fᵢ' de una operación, omitiendo el 1."""
    magnitud = formatear_numero(abs(coeficiente))
    if magnitud == "1":
        return f"F{subindice(indice_fila)}"
    return f"{magnitud}·F{subindice(indice_fila)}"


def _buscar_fila_pivote(matriz, m, fila_inicial, columna):
    """Pivoteo parcial: fila r ≥ fila_inicial que maximiza |a_r,columna|.

    Prepara un posible intercambio Fᵢ ↔ Fⱼ.
    """
    fila_maxima = fila_inicial
    valor_maximo = abs(matriz[fila_inicial][columna])
    for fila in range(fila_inicial + 1, m):
        candidato = abs(matriz[fila][columna])
        if candidato > valor_maximo:
            valor_maximo = candidato
            fila_maxima = fila
    return fila_maxima


def _anular_columna(matriz, m, fila_pivote, columna):
    """Eliminación Fₖ → Fₖ − c·Fᵢ para toda fila k ≠ i (arriba y abajo del pivote).

    Devuelve la lista de pasos (tipo, notación, columna, matriz después del paso).
    """
    pasos = []
    for fila in range(m):
        if fila == fila_pivote:               # la fila pivote no se toca a sí misma
            continue

        factor = matriz[fila][columna]        # c = elemento a anular
        if es_cero(factor):                   # ya vale 0 (con tolerancia)
            continue

        # Fₖ → Fₖ − c·Fᵢ, término a término, limpiando el ruido de float.
        nueva = []
        for j in range(len(matriz[fila])):
            nueva.append(limpiar(matriz[fila][j] - factor * matriz[fila_pivote][j]))
        nueva[columna] = 0.0                  # el elemento anulado es 0 exacto
        matriz[fila] = nueva

        signo = "-" if factor > 0 else "+"
        notacion = (
            f"F{subindice(fila)} → F{subindice(fila)} {signo} "
            f"{_factor_por_fila(factor, fila_pivote)}"
        )
        pasos.append(("eliminacion", notacion, columna, copiar_matriz(matriz)))
    return pasos


def escalonar(Ab, m, n):
    """Gauss-Jordan: lleva [A | b] a su forma escalonada reducida (RREF).

    Devuelve (matriz_reducida, pasos, columnas_pivote); cada paso es la tupla
    (tipo, notación, columna, matriz). Recorre las columnas
    de A de izquierda a derecha con un contador `fila_pivote`:
      1. Pivoteo parcial: busca el mayor |valor| de la columna.
      2. Si toda la columna es ≈ 0 → variable libre; avanza sin subir fila_pivote.
      3. Fᵢ ↔ Fⱼ si el pivote no está en su sitio.
      4. Fᵢ → (1/p)·Fᵢ para dejar el pivote en 1.
      5. Fₖ → Fₖ − c·Fᵢ para anular la columna arriba y abajo.
      6. Incrementa fila_pivote.
    """
    matriz = copiar_matriz(Ab)                # se trabaja sobre una copia
    pasos = []
    columnas_pivote = []
    fila_pivote = 0

    for columna in range(n):                  # solo columnas de A; b queda fuera
        if fila_pivote >= m:                  # ya no quedan filas para pivotes
            break

        fila_maxima = _buscar_fila_pivote(matriz, m, fila_pivote, columna)

        # Paso 2: columna nula de fila_pivote hacia abajo → variable libre.
        if es_cero(matriz[fila_maxima][columna]):
            continue

        # Paso 3: Fᵢ ↔ Fⱼ.
        if fila_maxima != fila_pivote:
            matriz[fila_pivote], matriz[fila_maxima] = (
                matriz[fila_maxima],
                matriz[fila_pivote],
            )
            notacion = f"F{subindice(fila_pivote)} ↔ F{subindice(fila_maxima)}"
            pasos.append(("intercambio", notacion, columna, copiar_matriz(matriz)))

        # Paso 4: Fᵢ → (1/p)·Fᵢ.
        pivote = matriz[fila_pivote][columna]
        if not es_cero(pivote - 1.0):
            nueva = []
            for valor in matriz[fila_pivote]:
                nueva.append(limpiar(valor / pivote))
            nueva[columna] = 1.0              # el pivote queda en 1 exacto
            matriz[fila_pivote] = nueva
            texto_pivote = formatear_numero(pivote)
            if pivote < 0:
                texto_pivote = f"({texto_pivote})"
            notacion = (
                f"F{subindice(fila_pivote)} → (1/{texto_pivote})·"
                f"F{subindice(fila_pivote)}"
            )
            pasos.append(("normalizacion", notacion, columna, copiar_matriz(matriz)))
        else:
            matriz[fila_pivote][columna] = 1.0

        # Paso 5: Fₖ → Fₖ − c·Fᵢ.
        pasos.extend(_anular_columna(matriz, m, fila_pivote, columna))

        # Paso 6.
        columnas_pivote.append(columna)
        fila_pivote += 1

    return matriz, pasos, columnas_pivote


# ---------------------------------------------------------------------------
# Rangos, clasificación y solución (Rouché-Frobenius)
# ---------------------------------------------------------------------------
def calcular_rangos(matriz_reducida, m, n, columnas_pivote):
    """rango(A) = nº de columnas pivote;  rango(A|b) = rango(A) + 1 si existe una fila 0 ⋯ 0 | k con k ≠ 0."""
    rango_a = len(columnas_pivote)
    rango_ab = rango_a
    for i in range(m):
        if fila_contradictoria(matriz_reducida[i], n):
            rango_ab = rango_a + 1
            break
    return rango_a, rango_ab


def fila_contradictoria(fila, n):
    """Detecta la ecuación imposible 0·x₁ + ⋯ + 0·xₙ = k con k ≠ 0."""
    for j in range(n):
        if not es_cero(fila[j]):
            return False
    return not es_cero(fila[n])


def clasificar(rango_a, rango_ab, n):
    """Rouché-Frobenius: compara rango(A), rango(A|b) y n.

    Devuelve (tipo, titulo, explicacion) con tipo en
    {"inconsistente", "determinado", "indeterminado"}.
    """
    if rango_a < rango_ab:
        return (
            "inconsistente",
            "Sistema Inconsistente",
            f"rango(A) = {rango_a} < rango(A|b) = {rango_ab}: aparece 0 = k con k ≠ 0.",
        )
    if rango_a == n:
        return (
            "determinado",
            "Sistema Consistente Determinado",
            f"rango(A) = rango(A|b) = {rango_a} = n: solución única.",
        )
    return (
        "indeterminado",
        "Sistema Consistente Indeterminado",
        f"rango(A) = rango(A|b) = {rango_a} < n = {n}: infinitas soluciones "
        f"con {n - rango_a} variable(s) libre(s).",
    )


def construir_solucion(matriz_reducida, n, columnas_pivote):
    """Despeja cada variable básica en la RREF: x_p = dᵢ − Σ_{j libre} rᵢⱼ·xⱼ.

    Devuelve (libres, expresiones) donde cada expresión es
    (variable_basica, constante, [(coeficiente, variable_libre), ...]).
    """
    libres = [j for j in range(n) if j not in columnas_pivote]
    expresiones = []
    for i in range(len(columnas_pivote)):     # la fila i contiene el pivote i
        constante = matriz_reducida[i][n]
        terminos = []
        for j in libres:
            coeficiente = limpiar(-matriz_reducida[i][j])   # se pasa al otro lado
            if not es_cero(coeficiente):
                terminos.append((coeficiente, j))
        expresiones.append((columnas_pivote[i], constante, terminos))
    return libres, expresiones


def evaluar_solucion(libres, expresiones, n, valores_libres):
    """Evalúa x = p + Σ tⱼ·dⱼ para valores concretos de las variables libres."""
    x = [0.0] * n
    for indice in range(len(libres)):         # x_libre = t
        x[libres[indice]] = valores_libres[indice]
    for variable, constante, terminos in expresiones:
        valor = constante
        for coeficiente, libre in terminos:
            valor += coeficiente * x[libre]
        x[variable] = limpiar(valor)
    return x


def vectores_direccion(libres, expresiones, n):
    """Vectores d₁, …, d_r de x = p + t₁·d₁ + ⋯ + t_r·d_r (uno por variable libre)."""
    direcciones = []
    for libre in libres:
        d = [0.0] * n
        d[libre] = 1.0
        for variable, constante, terminos in expresiones:
            for coeficiente, variable_libre in terminos:
                if variable_libre == libre:
                    d[variable] = coeficiente
        direcciones.append(d)
    return direcciones


def analizar_sistema(Ab, m, n):
    """Resuelve [A | b] por Gauss-Jordan e imprime procedimiento, RREF, pivotes y clasificación.

    Devuelve (tipo, matriz_reducida, columnas_pivote).
    """
    imprimir_matriz(Ab, "Matriz aumentada inicial", columnas_izquierda=n)

    matriz_reducida, pasos, columnas_pivote = escalonar(Ab, m, n)

    print()
    print("  Procedimiento (Gauss-Jordan):")
    if len(pasos) == 0:
        print("    (la matriz ya estaba en forma escalonada reducida)")
    for numero in range(len(pasos)):
        tipo, notacion, columna, estado = pasos[numero]
        print(f"   {numero + 1:>2}. {notacion}")
        imprimir_matriz(estado, columnas_izquierda=n, sangria="        ")

    print()
    imprimir_matriz(matriz_reducida, "RREF", columnas_izquierda=n)

    posiciones = ", ".join(str(c + 1) for c in columnas_pivote)
    if posiciones == "":
        posiciones = "ninguna"
    print(f"  Columnas pivote: {posiciones}")

    rango_a, rango_ab = calcular_rangos(matriz_reducida, m, n, columnas_pivote)
    tipo, titulo, explicacion = clasificar(rango_a, rango_ab, n)
    print(f"  rango(A) = {rango_a}, rango(A|b) = {rango_ab}")
    print(f"  Clasificación: {titulo}")
    print(f"    {explicacion}")
    return tipo, matriz_reducida, columnas_pivote


def imprimir_solucion_parametrica(libres, expresiones, n, letra):
    """Imprime variables básicas/libres, la forma paramétrica y la forma vectorial x = p + Σ tⱼ·dⱼ."""
    parametros = nombres_parametros(len(libres))
    basicas = [variable for variable, constante, terminos in expresiones]

    print("  Variables básicas: " + ", ".join(f"{letra}{subindice(j)}" for j in basicas))
    print("  Variables libres:  " + ", ".join(f"{letra}{subindice(j)}" for j in libres))
    print()
    print("  Solución general (forma paramétrica):")

    for j in range(n):
        if j in libres:
            nombre = parametros[libres.index(j)]
            print(f"    {letra}{subindice(j)} = {nombre}   (libre)")
            continue
        for variable, constante, terminos in expresiones:
            if variable == j:
                con_nombres = []
                for coeficiente, libre in terminos:
                    con_nombres.append((coeficiente, parametros[libres.index(libre)]))
                print(f"    {letra}{subindice(j)} = {formatear_expresion(constante, con_nombres)}")

    particular = evaluar_solucion(libres, expresiones, n, [0.0] * len(libres))
    direcciones = vectores_direccion(libres, expresiones, n)
    forma = f"    {letra} = {formatear_vector(particular)}"
    for indice in range(len(libres)):
        forma += f" + {parametros[indice]}·{formatear_vector(direcciones[indice])}"
    print()
    print("  Forma vectorial:")
    print(forma)
    return parametros


# ---------------------------------------------------------------------------
# Combinación lineal y Ax = b
# ---------------------------------------------------------------------------
def texto_combinacion(pesos):
    """Escribe la expresión c₁·v₁ + c₂·v₂ + … + cₖ·vₖ."""
    texto = ""
    for j in range(len(pesos)):
        c = pesos[j]
        magnitud = formatear_numero(abs(c))
        termino = f"{magnitud}·v{subindice(j)}"
        if j == 0:
            texto = ("-" if c < 0 and not es_cero(c) else "") + termino
        elif c < 0 and not es_cero(c):
            texto += " - " + termino
        else:
            texto += " + " + termino
    return texto


def verificar_combinacion(pesos, vectores, b):
    """Comprueba Σ cᵢ·vᵢ = b recalculando la combinación con las operaciones de ℝⁿ."""
    recalculado = combinar_vectores(pesos, vectores)
    print(f"    Σ cᵢ·vᵢ = {formatear_vector(recalculado)}")
    print(f"    b       = {formatear_vector(b)}")
    if vectores_iguales(recalculado, b):
        print("    ✔ Coinciden: la combinación es correcta.")
    else:
        print("    ✘ NO coinciden.")


def resolver_combinacion_lineal(vectores, b):
    """¿b ∈ gen{v₁, …, vₖ}?  Resuelve c₁·v₁ + ⋯ + cₖ·vₖ = b con [v₁ … vₖ | b].

    - inconsistente → b no es combinación lineal;
    - única         → pesos c₁, …, cₖ;
    - infinitas     → solución general y una combinación particular (libres = 0).
    """
    n = len(b)
    k = len(vectores)
    Ab = aumentada_desde_columnas(vectores, b)
    tipo, reducida, columnas_pivote = analizar_sistema(Ab, n, k)

    print()
    if tipo == "inconsistente":
        print("  RESULTADO: b NO es combinación lineal de los vectores dados.")
        for i in range(n):
            if fila_contradictoria(reducida[i], k):
                print(f"    La fila {i + 1} de la RREF dice 0 = {formatear_numero(reducida[i][k])}.")
                break
        return

    libres, expresiones = construir_solucion(reducida, k, columnas_pivote)

    if tipo == "determinado":
        pesos = evaluar_solucion(libres, expresiones, k, [])
        print("  RESULTADO: b SÍ es combinación lineal (pesos únicos).")
        for j in range(k):
            print(f"    c{subindice(j)} = {formatear_numero(pesos[j])}")
        print(f"    b = {texto_combinacion(pesos)}")
    else:
        print("  RESULTADO: b SÍ es combinación lineal (infinitas formas).")
        imprimir_solucion_parametrica(libres, expresiones, k, "c")
        pesos = evaluar_solucion(libres, expresiones, k, [0.0] * len(libres))
        print()
        print("  Combinación particular (variables libres = 0):")
        print(f"    b = {texto_combinacion(pesos)}")

    print()
    print("  Verificación:")
    verificar_combinacion(pesos, vectores, b)


def verificar_ax_b(A, x, b, etiqueta):
    """Comprueba A·x = b calculando A·x con producto_matrices y comparando con b."""
    Ax = columna_a_vector(producto_matrices(A, vector_a_columna(x)))
    print(f"  Verificación{etiqueta}:")
    print(f"    x   = {formatear_vector(x)}")
    print(f"    A·x = {formatear_vector(Ax)}")
    print(f"    b   = {formatear_vector(b)}")
    if vectores_iguales(Ax, b):
        print("    ✔ A·x = b")
    else:
        print("    ✘ A·x ≠ b")


def resolver_ax_b(A, b):
    """Resuelve la ecuación matricial A·x = b (A m×n, b ∈ ℝᵐ) mediante [A | b]."""
    m, n = dimensiones(A)
    Ab = aumentada_desde_matriz(A, b)
    tipo, reducida, columnas_pivote = analizar_sistema(Ab, m, n)

    print()
    if tipo == "inconsistente":
        print("  RESULTADO: el sistema NO tiene solución.")
        for i in range(m):
            if fila_contradictoria(reducida[i], n):
                print(f"    La fila {i + 1} de la RREF dice 0 = {formatear_numero(reducida[i][n])}.")
                break
        return

    libres, expresiones = construir_solucion(reducida, n, columnas_pivote)

    if tipo == "determinado":
        x = evaluar_solucion(libres, expresiones, n, [])
        print("  RESULTADO: solución única.")
        for j in range(n):
            print(f"    x{subindice(j)} = {formatear_numero(x[j])}")
        print()
        verificar_ax_b(A, x, b, "")
        return

    print("  RESULTADO: infinitas soluciones.")
    parametros = imprimir_solucion_parametrica(libres, expresiones, n, "x")
    print()
    ceros = [0.0] * len(libres)
    unos = [1.0] * len(libres)
    verificar_ax_b(A, evaluar_solucion(libres, expresiones, n, ceros), b,
                   " (solución particular, " + ", ".join(p + " = 0" for p in parametros) + ")")
    verificar_ax_b(A, evaluar_solucion(libres, expresiones, n, unos), b,
                   " (" + ", ".join(p + " = 1" for p in parametros) + ")")


# ---------------------------------------------------------------------------
# Entrada validada
# ---------------------------------------------------------------------------
def leer_linea(mensaje):
    """Lee una línea del teclado; si la entrada termina (EOF) cierra el programa."""
    try:
        return input(mensaje)
    except EOFError:
        print()
        print("Fin de la entrada. ¡Hasta luego!")
        raise SystemExit(0)


def convertir_numero(texto):
    """Convierte texto en x ∈ ℝ. Acepta enteros, decimales y fracciones a/b.

    Devuelve (True, valor) o (False, None) si el texto no es un número real finito.
    """
    limpio = texto.strip()
    if limpio == "":
        return False, None

    if "/" in limpio:                         # fracción a/b = a ÷ b
        partes = limpio.split("/")
        if len(partes) != 2:
            return False, None
        ok_num, numerador = convertir_numero(partes[0])
        ok_den, denominador = convertir_numero(partes[1])
        if not ok_num or not ok_den or es_cero(denominador):
            return False, None
        return True, numerador / denominador

    try:
        valor = float(limpio)
    except ValueError:
        return False, None
    if valor - valor != 0:                    # inf − inf y nan − nan dan nan
        return False, None
    return True, valor


def leer_numero(mensaje):
    """Pide un escalar c ∈ ℝ hasta que sea válido."""
    while True:
        texto = leer_linea(mensaje)
        ok, valor = convertir_numero(texto)
        if ok:
            return valor
        print(f"  ✘ '{texto.strip()}' no es un número válido. Intente de nuevo.")


def leer_entero(mensaje):
    """Pide una dimensión entera d con DIMENSION_MINIMA ≤ d ≤ DIMENSION_MAXIMA."""
    while True:
        texto = leer_linea(mensaje).strip()
        try:
            valor = int(texto)
        except ValueError:
            print(f"  ✘ '{texto}' no es un entero. Intente de nuevo.")
            continue
        if valor < DIMENSION_MINIMA:
            print(f"  ✘ La dimensión debe ser mayor que 0 (se recibió {valor}).")
            continue
        if valor > DIMENSION_MAXIMA:
            print(f"  ✘ La dimensión máxima es {DIMENSION_MAXIMA} (se recibió {valor}).")
            continue
        return valor


def leer_fila(mensaje, cantidad):
    """Lee exactamente `cantidad` números en una línea (separados por espacios o comas)."""
    while True:
        texto = leer_linea(mensaje)
        partes = texto.replace(",", " ").split()
        if len(partes) != cantidad:
            print(f"  ✘ Se esperaban {cantidad} número(s) y se recibieron {len(partes)}. "
                  "Use punto decimal (2.5) y separe con espacios.")
            continue
        valores = []
        for parte in partes:
            ok, valor = convertir_numero(parte)
            if not ok:
                print(f"  ✘ '{parte}' no es un número válido. Repita la línea.")
                valores = None
                break
            valores.append(valor)
        if valores is not None:
            return valores


def leer_vector(nombre, n):
    """Lee v ∈ ℝⁿ componente a componente en una sola línea."""
    return leer_fila(f"  {nombre} ({n} componentes): ", n)


def leer_dimensiones_matriz(nombre):
    """Lee el orden m×n de una matriz."""
    m = leer_entero(f"  Filas de {nombre}: ")
    n = leer_entero(f"  Columnas de {nombre}: ")
    return m, n


def leer_matriz(nombre, m, n):
    """Lee A ∈ ℝ^(m×n) fila por fila."""
    print(f"  Ingrese {nombre} ({m}×{n}), una fila por línea:")
    matriz = []
    for i in range(m):
        matriz.append(leer_fila(f"    Fila {i + 1}: ", n))
    return matriz


# ---------------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------------
def opcion_operar_vectores(operacion):
    """Opciones 1 y 2: u ± v en ℝⁿ, validando dim(u) = dim(v)."""
    if operacion == "suma":
        imprimir_titulo("SUMA DE VECTORES: (u + v)ᵢ = uᵢ + vᵢ")
    else:
        imprimir_titulo("RESTA DE VECTORES: (u - v)ᵢ = uᵢ - vᵢ")

    n_u = leer_entero("  Dimensión de u: ")
    u = leer_vector("u", n_u)
    n_v = leer_entero("  Dimensión de v: ")
    v = leer_vector("v", n_v)

    if operacion == "suma":
        resultado, simbolo = suma_vectores(u, v), "+"
    else:
        resultado, simbolo = resta_vectores(u, v), "-"

    print()
    if resultado is None:
        print(f"  ✘ Error: u ∈ ℝ^{n_u} y v ∈ ℝ^{n_v} tienen dimensiones distintas; "
              "no se puede operar.")
        return
    print(f"  u = {formatear_vector(u)}")
    print(f"  v = {formatear_vector(v)}")
    print(f"  u {simbolo} v = {formatear_vector(resultado)}")


def opcion_escalar_por_vector():
    """Opción 3: c·v."""
    imprimir_titulo("ESCALAR × VECTOR: (c·v)ᵢ = c·vᵢ")
    c = leer_numero("  Escalar c: ")
    n = leer_entero("  Dimensión de v: ")
    v = leer_vector("v", n)
    print()
    print(f"  {formatear_numero(c)}·{formatear_vector(v)} = "
          f"{formatear_vector(escalar_por_vector(c, v))}")


def opcion_combinacion_lineal():
    """Opción 4: ¿b = c₁·v₁ + ⋯ + cₖ·vₖ?"""
    imprimir_titulo("COMBINACIÓN LINEAL: ¿b = c₁·v₁ + ... + cₖ·vₖ?")
    n = leer_entero("  Dimensión n de los vectores: ")
    k = leer_entero("  Cantidad k de vectores: ")
    vectores = []
    for j in range(k):
        vectores.append(leer_vector(f"v{subindice(j)}", n))
    b = leer_vector("b", n)
    print()
    print("  Se resuelve A·c = b con A = [v₁ ... vₖ] (vectores como columnas).")
    resolver_combinacion_lineal(vectores, b)


def opcion_operar_matrices(operacion):
    """Opciones 5 y 6: A ± B, validando que ambas sean m×n."""
    if operacion == "suma":
        imprimir_titulo("SUMA DE MATRICES: (A + B)ᵢⱼ = aᵢⱼ + bᵢⱼ")
    else:
        imprimir_titulo("RESTA DE MATRICES: (A - B)ᵢⱼ = aᵢⱼ - bᵢⱼ")

    m_a, n_a = leer_dimensiones_matriz("A")
    m_b, n_b = leer_dimensiones_matriz("B")
    if m_a != m_b or n_a != n_b:
        print()
        print(f"  ✘ Error: A es {m_a}×{n_a} y B es {m_b}×{n_b}. "
              "Para sumar o restar ambas deben tener el mismo orden m×n.")
        return

    A = leer_matriz("A", m_a, n_a)
    B = leer_matriz("B", m_b, n_b)
    if operacion == "suma":
        C, nombre = suma_matrices(A, B), "A + B"
    else:
        C, nombre = resta_matrices(A, B), "A - B"

    print()
    imprimir_matriz(A, "A")
    imprimir_matriz(B, "B")
    imprimir_matriz(C, nombre)


def opcion_escalar_por_matriz():
    """Opción 7: c·A."""
    imprimir_titulo("ESCALAR × MATRIZ: (c·A)ᵢⱼ = c·aᵢⱼ")
    c = leer_numero("  Escalar c: ")
    m, n = leer_dimensiones_matriz("A")
    A = leer_matriz("A", m, n)
    print()
    imprimir_matriz(A, "A")
    imprimir_matriz(escalar_por_matriz(c, A), f"{formatear_numero(c)}·A")


def opcion_producto_matrices():
    """Opción 8: A(m×n)·B(n×p), validando columnas(A) = filas(B)."""
    imprimir_titulo("PRODUCTO DE MATRICES: cᵢⱼ = Σₖ aᵢₖ·bₖⱼ")
    m_a, n_a = leer_dimensiones_matriz("A")
    m_b, n_b = leer_dimensiones_matriz("B")
    if n_a != m_b:
        print()
        print(f"  ✘ Error: A es {m_a}×{n_a} y B es {m_b}×{n_b}. "
              f"columnas(A) = {n_a} ≠ filas(B) = {m_b}: el producto A·B no está definido.")
        return

    A = leer_matriz("A", m_a, n_a)
    B = leer_matriz("B", m_b, n_b)
    C = producto_matrices(A, B)
    print()
    imprimir_matriz(A, f"A ({formatear_dimension(A)})")
    imprimir_matriz(B, f"B ({formatear_dimension(B)})")
    imprimir_matriz(C, f"A·B ({formatear_dimension(C)})")


def opcion_ax_b():
    """Opción 9: resolver A·x = b."""
    imprimir_titulo("ECUACIÓN MATRICIAL A·x = b")
    m, n = leer_dimensiones_matriz("A")
    A = leer_matriz("A", m, n)
    b = leer_vector("b", m)
    print()
    resolver_ax_b(A, b)


# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------
def mostrar_menu():
    """Imprime el menú de opciones."""
    print()
    print("=" * 62)
    print("  CALCULADORA DE ÁLGEBRA LINEAL — PROGRAMA 3")
    print("  Operaciones en ℝⁿ, combinación lineal y ecuaciones matriciales")
    print("=" * 62)
    print("  1. Suma de vectores          6. Resta de matrices")
    print("  2. Resta de vectores         7. Escalar × matriz")
    print("  3. Escalar × vector          8. Producto de matrices")
    print("  4. Combinación lineal        9. Resolver A·x = b")
    print("  5. Suma de matrices          0. Salir")
    print("-" * 62)


def main():
    """Bucle while del menú: repite hasta que se elija 0."""
    while True:
        mostrar_menu()
        opcion = leer_linea("  Elija una opción: ").strip()

        if opcion == "0":
            print("  ¡Hasta luego!")
            break
        elif opcion == "1":
            opcion_operar_vectores("suma")
        elif opcion == "2":
            opcion_operar_vectores("resta")
        elif opcion == "3":
            opcion_escalar_por_vector()
        elif opcion == "4":
            opcion_combinacion_lineal()
        elif opcion == "5":
            opcion_operar_matrices("suma")
        elif opcion == "6":
            opcion_operar_matrices("resta")
        elif opcion == "7":
            opcion_escalar_por_matriz()
        elif opcion == "8":
            opcion_producto_matrices()
        elif opcion == "9":
            opcion_ax_b()
        else:
            print(f"  ✘ Opción inválida: '{opcion}'. Elija un número del 0 al 9.")


if __name__ == "__main__":
    main()
