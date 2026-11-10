# Programa 7 · Métodos Numéricos — Toda la lógica explicada (guía para la presentación)

> Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
> Este documento reúne **todo lo importante** del módulo para poder explicarlo en la presentación:
> cómo está organizado, qué hace cada algoritmo, por qué se tomó cada decisión y cómo se probó.
> Las referencias `archivo:línea` apuntan al código real.
> **Versión sencilla, solo con la matemática:** [`Programa7_LOGICA_MATEMATICA.md`](Programa7_LOGICA_MATEMATICA.md).
> Las capturas y las respuestas cortas de la defensa están en
> [`Programa7_apoyo_informe.md`](Programa7_apoyo_informe.md).

---

## Índice

0. [Resumen en 30 segundos](#0-resumen-en-30-segundos)
1. [Arquitectura: dónde vive cada cosa](#1-arquitectura-dónde-vive-cada-cosa)
2. [El parser seguro (sin eval)](#2-el-parser-seguro-sin-eval)
3. [Módulo A — Bisección](#3-módulo-a--bisección)
4. [Continuidad con SymPy (hipótesis de Bolzano)](#4-continuidad-con-sympy-hipótesis-de-bolzano)
5. [Módulo B — Graficador](#5-módulo-b--graficador)
6. [Módulo C — Notación posicional](#6-módulo-c--notación-posicional)
7. [Módulo D — Errores numéricos y punto flotante](#7-módulo-d--errores-numéricos-y-punto-flotante)
8. [Validación y manejo de errores de punta a punta](#8-validación-y-manejo-de-errores-de-punta-a-punta)
9. [Pruebas](#9-pruebas)
10. [Decisiones de diseño y límites conocidos](#10-decisiones-de-diseño-y-límites-conocidos)
11. [Guion sugerido para la presentación](#11-guion-sugerido-para-la-presentación)

---

## 0. Resumen en 30 segundos

- El Programa 7 añade a la calculadora un módulo de **Métodos Numéricos** con cuatro partes:
  **Bisección**, **Graficador**, **Notación posicional** y **Errores numéricos**.
- **Toda la matemática está en Python**, en **`programas/Programa7_GrupoX.py`** (secciones A → D).
  La consola y la web llaman a **las mismas funciones**, así que siempre dan el mismo resultado.
- El frontend (React) solo recoge datos y muestra resultados.
- La función f(x) que escribe el usuario **nunca se ejecuta con `eval()`**. Se analiza con un árbol
  sintáctico y una lista blanca, y no puede ejecutar código.
- Bisección está **programada desde cero**. SciPy solo se usa al final para **contrastar** la raíz.
- 309 pruebas automáticas pasan: las de los programas anteriores y las 115 nuevas del Programa 7.

---

## 1. Arquitectura: dónde vive cada cosa

```
            ┌──────────────────────────┐        ┌──────────────────────────────┐
 Usuario ──►│  Web (React + Plotly)    │        │  Consola                     │
            │  components/programa7/   │        │  programas/Programa7_GrupoX  │
            └────────────┬─────────────┘        │  → main.py → opción 6        │
                         │ JSON (texto)         │  → modulo_metodos_numericos  │
                         ▼                      │    (+ Matplotlib)            │
            ┌──────────────────────────┐        └──────────────┬───────────────┘
            │ FastAPI  app/api.py      │                       │
            │ /api/p7/...              │                       │
            │ calculo/programa7_web.py │  (traduce errores)    │
            └────────────┬─────────────┘                       │
                         ▼                                     ▼
            ┌──────────────────────────────────────────────────────────────┐
            │  TODA LA MATEMÁTICA                                          │
            │   programas/Programa7_GrupoX.py  ← ALGORITMOS (A, B, C, D)   │
            │   importa: numericos/parser_seguro.py, numericos/continuidad │
            └──────────────────────────────────────────────────────────────┘
```

| Archivo | Responsabilidad |
|---|---|
| `programas/Programa7_GrupoX.py` | **Todos los algoritmos y la matemática**: A. Bisección (validaciones 1–5, algoritmo, n_min, SciPy), B. Graficador, C. Notación posicional, D. Errores. También abre la consola. |
| `modulos/numericos/parser_seguro.py` | Lee f(x) **sin eval**; la convierte en función escalar (math), vectorial (NumPy) y simbólica (SymPy). También `leer_numero` y `leer_entero`. |
| `modulos/numericos/continuidad.py` | ¿f es continua en [a, b]? Usa `sympy.calculus.util.continuous_domain`, con límite de tiempo. |
| `modulos/modulo_metodos_numericos.py` | Consola: menús, lectura con reintento, tablas y Matplotlib. **No calcula nada.** |
| `calculo/programa7_web.py` | Adaptador web: llama a las funciones y convierte `ErrorNumerico` en HTTP 422. |
| `app/api.py`, `app/modelos.py` | Rutas `/api/p7/*` y esquemas Pydantic. |
| `frontend/src/components/programa7/` | Pestañas, formularios, tablas y gráfica (Plotly). |

**Endpoints**

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/api/p7/biseccion` | `{funcion, a, b, tolerancia, max_iter}` → diagnóstico, tabla, raíz, cota, n_min y SciPy |
| POST | `/api/p7/graficar` | `{funcion, x_min, x_max, raiz?, intervalo?, tipo_intervalo?}` → segmentos y marcas |
| POST | `/api/p7/posicional` | `{numero, base}` → descomposiciones, divisiones y verificación |
| GET  | `/api/p7/flotante` | Ejecuta en el servidor 0.1 + 0.2, ε, overflow/underflow y los tipos de error |
| POST | `/api/p7/errores` | `{xv, xa}` → Ea, Er y Er% |
| POST | `/api/p7/propagacion` | `{funcion, x, dx}` → f′(x), Δy aprox, Δy real y diferencia |
| GET  | `/api/p7/ejemplos` | Casos precargados (una sola fuente de verdad para la web) |

**¿Por qué los números viajan como texto?** Así se validan en Python con mensajes en español
(«El valor de a no es un número válido: 'abc'») y se aceptan expresiones constantes como `pi/2`.

---

## 2. El parser seguro (sin eval)

### El problema

Si se hiciera `eval("x**2 - 2")`, el usuario podría escribir `__import__('os').system('del *')` y
el servidor lo **ejecutaría**. Por eso está prohibido. `sympy.parse_expr` tampoco se usa porque
llama a `eval` por dentro.

### La solución: árbol sintáctico + lista blanca (`parser_seguro.py`)

```
texto ─► _normalizar ─► caracteres permitidos ─► ast.parse ─► _validar (lista blanca)
                                                                    │
                     ┌──────────────────────────────┬───────────────┴────────────┐
                     ▼                              ▼                            ▼
          _compilar_escalar (math)      _compilar_vector (NumPy)   _construir_simbolica (SymPy)
          Bisección, propagación        Graficador                 Continuidad, derivada
```

1. **Normalizar** (`parser_seguro.py:363`):
   - `^` se convierte en `**` y se **avisa** al usuario (en Python `^` es XOR: `2^3 = 1`).
   - Se quita el lado izquierdo de «f(x) =» y los símbolos −, ×, · y ÷ se cambian por - * /.
2. **Caracteres permitidos**: solo letras, dígitos, `. + - * / ( )` y espacios. Así quedan fuera
   las comillas, `_`, `[`, `:`, `<`… Con eso ya caen `__import__('os')` y `lambda x: x`.
3. **`ast.parse(texto, mode="eval")`** (`parser_seguro.py:404`) **solo construye el árbol**, no ejecuta
   nada. Por ejemplo, `x**3 - 2*x - 5` produce:

   ```
              (−)
             /   \
           (−)    5
          /   \
       (**)   (*)
       /  \   /  \
      x    3 2    x
   ```

4. **Lista blanca** (`_validar`, `parser_seguro.py:279`): se recorre el árbol y solo se aceptan:

   | Nodo | Permitido |
   |---|---|
   | Número | int o float reales (no `True`, no complejos `2j`, no cadenas) |
   | Nombre | `x`, `pi`, `e` |
   | Operador binario | `+ - * / **` |
   | Operador unario | `+x`, `-x` |
   | Llamada | `sin cos tan asin acos atan sinh cosh tanh exp log ln log10 sqrt abs`, con **un** argumento y sin `nombre=valor` |

   Cualquier otro nodo se rechaza con un mensaje claro:
   - atributo `x.real` → «No se permite acceder a atributos»;
   - `open(x)` → «Función no permitida: 'open'»;
   - `y + 1` → «Nombre no permitido: 'y'»;
   - `x // 2` → «Operador no permitido: '//'»;
   - `x if x else 1` → elemento no permitido.

5. **Compilar sin `exec`**: cada nodo del árbol se convierte en una función de Python (cierres
   anidados). Por ejemplo, el nodo `a / b` se convierte en `lambda x: _dividir(izq(x), der(x))`.
   Nunca se ejecuta el texto del usuario: solo se recorre su árbol ya validado.

### Tres versiones de la misma f

| Versión | Dónde se usa | Qué hace si f no existe en x |
|---|---|---|
| Escalar (módulo `math`), `FuncionSegura.evaluar` (`:428`) | Bisección, propagación | Lanza `ErrorDeEvaluacion` con el motivo exacto: «log(-1) no está definido (el dominio de log exige argumento > 0)», «división entre cero», «overflow…» |
| Vectorial (NumPy), `evaluar_vector` (`:440`) | Graficador (miles de puntos de una vez) | Devuelve `nan` en ese punto (dentro de `np.errstate(all="ignore")`); después se descarta |
| Simbólica (SymPy), `expresion` | Continuidad y derivada | — |

Detalles importantes de la versión escalar:

- `(-8) ** (1/3)` en Python da un número **complejo**: se rechaza como «potencia no real»
  (`_potencia`, `:113`).
- `1e308 * 10` da `inf` sin lanzar ningún error: se detecta después de cada operación
  (`_comprobar_finito`, `:130`).

### Límites anti-abuso

- Longitud máxima: 200 caracteres. Profundidad máxima del árbol: 40.
- En la versión simbólica, el |exponente| numérico máximo es 1000 y una potencia exacta no puede
  pasar de 10 000 cifras.
- Esto último importa porque SymPy calcularía `9**9**9` exactamente (millones de dígitos) y colgaría
  el servidor.

### Lectura de números

- `leer_numero` (`:474`) usa el mismo parser pero **sin permitir x**, así que acepta `2`, `-1.5`,
  `1e-4`, `pi/2` o `sqrt(2)`.
- `leer_entero` (`:498`) solo acepta dígitos; se usa para Nmax.

---

## 3. Módulo A — Bisección

### 3.1 Teoría (Bolzano)

Si f es **continua** en [a, b] y **f(a)·f(b) < 0**, existe c ∈ (a, b) con f(c) = 0. Bisección
aprovecha el teorema: parte el intervalo en dos y conserva la mitad donde sigue habiendo cambio de
signo, de modo que la nueva mitad vuelve a cumplir Bolzano.

### 3.2 Validaciones, en el orden exigido (`programas/Programa7_GrupoX.py:262`, `resolver_biseccion`)

```python
a = leer_numero(texto_a, "a")                 # formato: no numérico → error en el campo "a"
...
validar_datos(a, b, tolerancia, max_iter)     # 1. a < b, E > 0, Nmax ≥ 1
fa = _evaluar_extremo(funcion, a, "a")        # 2. f(a) y f(b) definidas y finitas
fb = _evaluar_extremo(funcion, b, "b")
if fa == 0 or fb == 0: ...                    # 3. raíz exacta en el extremo → termina
if signo(fa) * signo(fb) > 0: ...             # 4. sin cambio de signo → se rechaza el intervalo
continuidad = analizar_continuidad(...)       # 5. continua en [a, b]? si no → NO se ejecuta
```

| Paso | Resultado | Tipo de respuesta |
|---|---|---|
| Formato o validación 1–2 | Mensaje en el campo culpable | **Error 422** (dato inválido) |
| 3 | `estado = "raiz_en_extremo"` | Resultado válido (200) |
| 4 | `estado = "sin_cambio_signo"`: «…esto no significa que f no tenga raíces en otros intervalos» | Resultado válido (200) |
| 5 | `estado = "discontinua"`: no se cumplen las condiciones de Bolzano | Resultado válido (200) |
| 5 sin decidir | Advertencia: «el cambio de signo, por sí solo, no garantiza continuidad» y se ejecuta | — |

¿Por qué 3, 4 y 5 no son errores? Porque los datos son correctos y la respuesta **es** el
diagnóstico: así la interfaz puede mostrar f(a), f(b) y el botón para graficar la función y ver
el porqué.

### 3.3 El algoritmo (`programas/Programa7_GrupoX.py:138`, `metodo_biseccion`) — sigue el pseudocódigo exacto

```python
fa, fb = funcion(a), funcion(b)
for k in range(1, max_iter + 1):
    xr = (a + b) / 2          # punto medio
    cota = (b - a) / 2        # Eb
    fr = funcion(xr)
    ... Ea y εa ...
    filas.append({... a, b ...})      # extremos registrados ANTES de actualizar
    if fr == 0:          motivo = "raiz_exacta";  break
    if cota <= tolerancia: motivo = "tolerancia"; break
    if signo(fa) * signo(fr) < 0:
        b, fb = xr, fr        # la raíz está en [a, xr]
    else:
        a, fa = xr, fr        # la raíz está en [xr, b]
```

Puntos clave para explicar:

- **Se registra la fila antes de actualizar el intervalo.** Así cada fila muestra el [a, b] en el
  que se calculó su xr (la tabla lo indica con una nota).
- **Se guarda f(a) y f(b) en variables** (`fa`, `fb`) y se actualizan junto con el extremo. Así f se
  evalúa **una sola vez por iteración** (solo en xr).
- **Signos en vez del producto** (`programas/Programa7_GrupoX.py:183`). El pseudocódigo dice `fa·fr < 0`, pero si
  ambos valen ~1e-200 el producto hace *underflow* a 0.0 y se elegiría la mitad equivocada. Comparar
  los signos (−1, 0, 1) es matemáticamente equivalente y no tiene ese problema. Hay una prueba con
  `1e-200*(x - 0.3)` que lo demuestra.
- **Orden de los criterios.** Primero `f(xr) = 0` (raíz exacta en aritmética de máquina) y después
  `Eb ≤ E`. Si se agotan las Nmax iteraciones, el mensaje dice que el resultado es una aproximación
  **SIN garantía** de cumplir la tolerancia.

### 3.4 Errores entre iteraciones

| Columna | Fórmula | Iteración 1 | Si xr_k = 0 |
|---|---|---|---|
| Eb (cota) | (b − a)/2 | 0.5 en [2, 3] | — |
| Ea | \|xr_k − xr_{k−1}\| | «—» | normal |
| εa | \|(xr_k − xr_{k−1}) / xr_k\| | «—» | «No definido» (no se divide entre 0) |

**εa no es criterio de parada**: el criterio es Eb ≤ E, que es una cota garantizada. Ea y εa solo
describen cuánto se movió la aproximación.

Primeras filas reales con f(x) = x³ − 2x − 5 en [2, 3]:

| k | a | b | xr | f(a) | f(b) | f(xr) | Eb | Ea | εa |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 3 | 2.5 | −1 | 16 | 5.625 | 0.5 | — | — |
| 2 | 2 | 2.5 | 2.25 | −1 | 5.625 | 1.890625 | 0.25 | 0.25 | 0.1111 |
| 3 | 2 | 2.25 | 2.125 | −1 | 1.890625 | 0.345703 | 0.125 | 0.125 | 0.0588 |
| 4 | 2 | 2.125 | 2.0625 | −1 | 0.345703 | −0.351318 | 0.0625 | 0.0625 | 0.0303 |
| 5 | 2.0625 | 2.125 | 2.09375 | −0.351318 | 0.345703 | −0.008942 | 0.03125 | 0.03125 | 0.0149 |

En k = 1, f(2.5) > 0 tiene distinto signo que f(a) < 0, así que b ← 2.5. En k = 4, f(2.0625) < 0
tiene el mismo signo que f(a), así que a ← 2.0625.

### 3.5 Número mínimo de iteraciones (`programas/Programa7_GrupoX.py:205`)

Tras n iteraciones, Eb = (b₀ − a₀)/2ⁿ. Si se exige Eb ≤ E:

    2ⁿ ≥ (b₀ − a₀)/E   ⇒   n_min = ⌈log₂((b₀ − a₀)/E)⌉

- [2, 3] con E = 10⁻⁴ da ⌈log₂(10 000)⌉ = ⌈13.29⌉ = **14**.
- El programa compara n_min con las iteraciones ejecutadas: «exactamente las n_min = 14
  teóricas».
- Si **Nmax < n_min**, avisa desde el inicio que no se alcanzará la tolerancia.
- El cálculo corrige con enteros los posibles redondeos de `log2` y nunca baja de 1, porque siempre
  se calcula al menos un punto medio.

### 3.6 Contraste con SciPy (`programas/Programa7_GrupoX.py:412`)

- Solo si el método se ejecutó **y** SymPy confirmó la continuidad, se llama a
  `scipy.optimize.bisect(f, a, b, xtol=E)` y se muestra |raíz propia − raíz SciPy|.
- En los cuatro casos la diferencia es **0**.
- La interfaz aclara que SciPy **solo sirve de contraste**. Su criterio de parada añade una
  tolerancia relativa, así que podría diferir en el último dígito.

### 3.7 Resultados de los casos (E = 10⁻⁴, Nmax = 100)

| f(x) | [a, b] | Raíz del programa | Valor de referencia | Iteraciones | n_min |
|---|---|---|---|---|---|
| x³ − 2x − 5 | [2, 3] | 2.09454345703125 | 2.09455148 | 14 | 14 |
| cos(x) − x | [0, 1] | 0.73907470703125 | 0.73908513 | 14 | 14 |
| x² − 2 | [1, 2] | 1.41424560546875 | 1.41421356 | 14 | 14 |
| x³ + x − 1 | [0, 1] | 0.68231201171875 | 0.68232780 | 14 | 14 |
| x² + 1 | [−1, 1] | — rechazado: sin cambio de signo | | | |
| x² − 1 | [1, 2] | 1 (raíz exacta en el extremo a) | | | |
| 1/x | [−1, 1] | — no se ejecuta: discontinua en x = 0 | | | |
| x³ − 2x − 5, Nmax = 5 | [2, 3] | 2.09375, con Eb = 0.03125 > E: sin garantía | | 5 | 14 |

En todos los casos |raíz − referencia| ≤ Eb = 6.1·10⁻⁵.

---

## 4. Continuidad con SymPy (hipótesis de Bolzano)

`continuidad.py:66` (`analizar_continuidad`):

```python
dominio  = continuous_domain(f, x, Interval(a, b))   # parte de [a, b] donde f es continua
faltante = Complement(Interval(a, b), dominio)       # lo que falta = puntos problemáticos
```

| f en [a, b] | `faltante` | Diagnóstico |
|---|---|---|
| x³ − 2x − 5 en [2, 3] | ∅ | continua → se ejecuta |
| 1/x en [−1, 1] | {0} | discontinua en x = 0 → **no** se ejecuta |
| tan(x) en [1, 2] | {π/2} | discontinua en x = π/2 ≈ 1.5708 |
| 1/(x² − 2) en [1, 2] | {√2} | discontinua en x = √2 |

Robustez:

- El análisis corre en un **hilo con límite de 4 s**. Si SymPy tarda demasiado o no sabe restar los
  conjuntos, el resultado es «indeterminada».
- En ese caso se ejecuta el método, pero con la advertencia de que el cambio de signo no garantiza
  continuidad, y no se contrasta con SciPy.
- Se declara `x = Symbol("x", real=True)` para estudiar la función en ℝ. Además, así la derivada de
  |x| es sign(x).

---

## 5. Módulo B — Graficador

`programas/Programa7_GrupoX.py:489` (`generar_puntos`). El objetivo es dibujar f **sin unir ramas** separadas por
una asíntota y **sin dibujar** donde f no existe.

1. **Muestreo.** Se toman 2001 puntos equiespaciados (se piden ≥ 1000). Se añaden los bordes
   exactos de las zonas problemáticas que encuentra SymPy (por ejemplo x = 0 en `sqrt(x)`, para que
   la curva empiece justo en el origen).
2. **Evaluación vectorial.** Todos los puntos se evalúan de una vez con NumPy. Lo no real, no
   definido o no finito queda como `nan` y se **descarta**: así log y sqrt solo se dibujan donde
   existen.
3. **Puntos excluidos.** En `float`, `tan(π/2)` da ≈ 1.6·10¹⁶ (finito) porque π/2 no es exacto. Los
   puntos que SymPy marca como discontinuos se fuerzan a `nan` (`programas/Programa7_GrupoX.py:504`).
4. **Saltos y asíntotas.** Entre dos puntos válidos con un salto grande (más del 5 % de la escala
   de la función) se **refina** el tramo con 33 subpuntos (`hay_salto`, `programas/Programa7_GrupoX.py:465`):
   - Si una función es **continua** (aunque sea empinada), el cambio se reparte entre los subpasos
     y ninguno se lleva más de la mitad.
   - En una **asíntota o salto**, un solo subpaso se queda con casi todo el cambio, o aparece un
     valor no finito. En ese caso se corta.
   - Con esto `tanh(1000x)` no se corta y `1/x` sí.
5. **Segmentos.** El backend devuelve `segmentos: [{x: [...], y: [...]}, ...]`. La web los une con
   `null` entre ellos; Plotly no dibuja línea a través de un `null`. La consola dibuja cada segmento
   con un `plot` distinto en Matplotlib.
6. **Rango vertical sugerido** (`rango_y_sugerido`). Si una asíntota dispara los valores, se usa el rango
   entre los percentiles 2 y 98. Si no, el mínimo y el máximo con un margen.

Marcas desde Bisección:

- El botón «Graficar esta función» envía la raíz y el intervalo **inicial** o **final** (el último
  [a, b], cuyo punto medio es xr).
- La raíz se dibuja como un punto rojo y el intervalo como una zona sombreada con dos líneas
  verticales punteadas, todo con su leyenda.
- La ventana de dibujo es el intervalo con un margen del 50 %, calculada por el backend.

Ejemplos precargados, uno por tipo:

| Tipo | Ejemplo |
|---|---|
| Lineal | 2x + 1 |
| Polinómica | x³ − 2x − 5 |
| Racional | (x + 1)/(x − 1) |
| Radical | √(4 − x²) |
| Exponencial | eˣ − 2 |
| Logarítmica | ln x |
| Trigonométrica | sin x, tan x |
| Valor absoluto | \|x − 1\| − 2 |

---

## 6. Módulo C — Notación posicional

En base β, el dígito dₖ en la posición k (contando desde 0 por la derecha) vale dₖ·βᵏ:

    (dₙ…d₁d₀)_β = dₙ·βⁿ + … + d₁·β¹ + d₀·β⁰

- **Descomposición** (`programas/Programa7_GrupoX.py:647`). Se recorren los dígitos de izquierda a derecha con la
  potencia n−1, n−2, …, 0 y se acumula dígito × potencia. La potencia se calcula por
  multiplicaciones sucesivas y el dígito con `ord(c) − ord('0')`.
- **Base 2 → base 10**: la suma de la descomposición **es** el valor decimal.

  (11110011)₂ = 1·2⁷ + 1·2⁶ + 1·2⁵ + 1·2⁴ + 0·2³ + 0·2² + 1·2¹ + 1·2⁰ = 128 + 64 + 32 + 16 + 2 + 1 = (243)₁₀

- **Base 10 → base 2**: divisiones sucesivas entre 2 (`programas/Programa7_GrupoX.py:680`). Los residuos, leídos de
  **abajo hacia arriba**, son los bits. Ejemplo con 243:

  | Dividendo | Cociente | Residuo |
  |---|---|---|
  | 243 | 121 | 1 |
  | 121 | 60 | 1 |
  | 60 | 30 | 0 |
  | 30 | 15 | 0 |
  | 15 | 7 | 1 |
  | 7 | 3 | 1 |
  | 3 | 1 | 1 |
  | 1 | 0 | 1 |

  Leídos de abajo hacia arriba: **11110011**.

- **Verificación**: se descomponen **ambos** números y se comprueba que valgan lo mismo. Como
  contraste independiente se compara también con `int()` de Python (no se usa para convertir).
- **Validación**: en base 2 solo se admiten 0 y 1 («El carácter '2' (posición 4) no es válido en
  base 2»). Solo se aceptan enteros. Los ceros a la izquierda se omiten con aviso.
- **Negativos**: el signo no forma parte de la notación posicional. Se descompone |N| y se antepone
  el signo: (−243)₁₀ = −(2·10² + 4·10¹ + 3·10⁰) = (−11110011)₂.
- **Superíndices Unicode**: `str.translate` cambia `0123456789` por `⁰¹²³⁴⁵⁶⁷⁸⁹` y la base se
  escribe con subíndices (₁₀, ₂).
- Los valores viajan como **texto** porque JavaScript pierde precisión con enteros > 2⁵³.

---

## 7. Módulo D — Errores numéricos y punto flotante

Todo se **ejecuta de verdad** en el servidor (`programas/Programa7_GrupoX.py:1081`, `demostracion_flotante`); no son
textos fijos.

### 7.1 ¿0.1 + 0.2 == 0.3?

- Resultado: `False`. `repr(0.1 + 0.2)` = `'0.30000000000000004'`.
- Con `Decimal(0.1)` se muestra el valor que realmente se guarda:
  `0.1000000000000000055511151231257827…`.
- IEEE 754 (double) guarda ±1.m × 2ᵉ con 52 bits de mantisa. 0.1 = 0.000110011…₂ es periódico, así
  que se redondea, y los dos redondeos de 0.1 y 0.2 no coinciden con el de 0.3.

### 7.2 Épsilon de máquina

- `numpy.finfo(float).eps` = 2.220446049250313e-16 = 2⁻⁵². Es la distancia entre 1.0 y el
  siguiente double: `nextafter(1.0, 2.0) − 1.0`.
- Se comprueba en vivo: `1.0 + eps == 1.0` es False y `1.0 + eps/2 == 1.0` es True.

### 7.3 Overflow y underflow (resultados de ESTE equipo)

Cada experimento se ejecuta dentro de `warnings.catch_warnings(record=True)` +
`np.errstate(all="warn")` (`experimento`, `programas/Programa7_GrupoX.py:892`), y se captura el valor, la excepción y la advertencia.

| Operación | Resultado (Windows 11, Python 3.13.5, NumPy 2.3.0) |
|---|---|
| `numpy.float64(1e308) * 10` | `inf` + RuntimeWarning overflow |
| `1e308 * 10` (float de Python) | `inf` **sin aviso** |
| `math.exp(1000)` | **OverflowError** |
| `numpy.exp(1000.0)` | `inf` + RuntimeWarning |
| `2.0 ** 10000` | **OverflowError** |
| `numpy.float32(3.4e38) * 10` | `inf` (float32 desborda antes) |
| `1e-320` | subnormal (menor que 2.2250738585072014e-308) |
| `1e-320 * 1e300` | 9.99988867182683e-21 (debería ser 1e-20: el subnormal perdió precisión) |
| `5e-324 / 2` | `0.0` sin aviso |
| `numpy.float64(5e-324) / 2` | `0.0` + RuntimeWarning underflow |

**Mensaje clave:** que una operación devuelva `inf`, lance una excepción o avise **depende del tipo
y de la operación**; no es universal. Por eso la interfaz muestra el equipo y las versiones.

### 7.4 Tipos de error (con ejemplos calculados)

| Tipo | Definición | Ejemplo |
|---|---|---|
| Inherente | Viene en los datos | r = 2.0 ± 0.05 cm ⇒ A = πr² ∈ [11.95, 13.20] cm² |
| Redondeo | Dígitos finitos | Sumar 0.1 diez veces da 0.9999999999999999 |
| Truncamiento | El **método** corta un proceso infinito | e ≈ Σ_{k=0}^{5} 1/k! = 2.71667 (error 1.6·10⁻³); la cota Eb de Bisección |
| Overflow | Supera ≈1.8·10³⁰⁸ | `math.exp(1000)` |
| Underflow | Menor que el mínimo representable → subnormal o 0 | 1e-200 · 1e-200 = 0.0 |
| Modelo matemático | La **ecuación** simplifica la realidad | Péndulo a 60°: modelo lineal T = 2.0061 s frente al no lineal 2.1529 s (6.8 %) |

**Truncamiento ≠ modelación.**
- El truncamiento lo introduce el método numérico al resolver una ecuación dada, y se reduce con
  más términos o iteraciones.
- El error de modelación está en la propia ecuación elegida, y no desaparece aunque se calcule con
  precisión infinita.

### 7.5 Calculadora de errores (`programas/Programa7_GrupoX.py:1096`)

    Ea = |xv − xa|        Er = Ea / |xv|        Er% = Er · 100

Si **xv = 0**, el programa responde «Error relativo no definido»: no divide entre cero ni inventa
un porcentaje.

### 7.6 Propagación del error (`programas/Programa7_GrupoX.py:1144`)

Por Taylor:

    f(x + Δx) = f(x) + f′(x)·Δx + f″(ξ)·Δx²/2

Si se desprecia el término de orden Δx², queda la aproximación de primer orden:

    Δy aprox = f′(x)·Δx          Δy real = f(x + Δx) − f(x)

- f′(x) se obtiene con `sympy.diff`. Para sin(x) + x², la derivada es **2x + cos(x)**.
- Con x = 1 y Δx = 0.01: Δy aprox = 0.0254030, Δy real = 0.0254609, diferencia = 5.78·10⁻⁵.
- Con Δx diez veces menor, la diferencia baja unas **100 veces**, porque el error es de orden Δx².
  Una prueba automática lo comprueba.

---

## 8. Validación y manejo de errores de punta a punta

```
Python lanza ErrorNumerico(mensaje, campo="b")
   └─► programa7_web lo convierte en ErrorDeCampo
         └─► FastAPI responde 422 {"detalle": "...", "campo": "b"}
               └─► React: AvisoError muestra el mensaje y el campo "b" se pone en rojo
                   (los valores del formulario NO se borran)
```

| Situación | Mensaje (ejemplo) |
|---|---|
| Entrada no numérica | «El valor de a no es un número válido: 'abc'. Ejemplos válidos: 2, -1.5, 1e-4, pi/2.» |
| a ≥ b | «El intervalo no es válido: se necesita a < b y se recibió a = 3, b = 1.» |
| E ≤ 0 | «La tolerancia E debe ser mayor que 0 (se recibió 0).» |
| Nmax < 1 | «El máximo de iteraciones debe ser al menos 1 (se recibió 0).» |
| Función mal escrita | «Falta un operador: la multiplicación debe escribirse con * (por ejemplo 2*x en lugar de 2x…)» |
| División entre cero | «f(b) no está definida: No se puede evaluar f(1): división entre cero.» |
| Fuera del dominio | «…log(-1) no está definido (el dominio de log exige argumento > 0).» |
| No finito | «…desbordamiento (overflow): el resultado supera el mayor float…» |
| ^ en lugar de ** | Aviso visible: «Se convirtió ^ en ** porque en Python ^ no es potencia…» |

En consola ocurre lo mismo: se muestra «✗ mensaje» y se vuelve a pedir **solo** el dato culpable,
conservando los demás.

---

## 9. Pruebas

Desde `backend/`:

```powershell
python -m pytest                                  # todo: 309 pruebas
python -m pytest pruebas/pruebas_programa7.py -v  # solo el Programa 7 (115)
```

`pytest.ini` hace que pytest recoja también las pruebas antiguas (unittest y `probar_*`), así que
se verifica que **los módulos anteriores siguen funcionando**.

`pruebas_programa7.py` cubre:

- **Bisección**:
  - los 4 casos: raíz con tolerancia 10⁻⁴, 14 iteraciones y n_min = 14;
  - las 4 pruebas obligatorias;
  - la tabla (extremos antes de actualizar, Ea y εa con «—» o «No definido»);
  - el caso de underflow en el producto;
  - n_min;
  - 10 validaciones con su campo.
- **Parser seguro**:
  - rechaza 25 expresiones peligrosas o inválidas: `__import__`, `os`, `open`, `lambda`, atributos,
    `eval`, `exec`, `globals`, comprensiones, cadenas, índices, comparaciones, `True`, `2j`,
    `9**9**9`…;
  - acepta toda la lista blanca;
  - convierte ^ con aviso y da mensajes de dominio claros.
- **Graficador**:
  - 1/x en 2 segmentos que no cruzan 0;
  - tan con 5 segmentos;
  - log y sqrt solo en su dominio;
  - tanh(1000x) sin cortes;
  - los 9 ejemplos y las marcas de Bisección.
- **Posicional**: 84506 ↔ 10100101000011010, 11110011 ↔ 243 (cadenas exactas), divisiones de 243,
  negativos y dígitos inválidos.
- **Errores**: xv = 0, Ea/Er/Er%, propagación (derivada, Δy y orden Δx²) y demostración IEEE 754.
- **API**: todos los endpoints responden; los errores devuelven 422 con `campo`.
- **Consola**: el menú tiene la opción 6.

---

## 10. Decisiones de diseño y límites conocidos

- **¿Por qué un evaluador AST y no `parse_expr`?** `parse_expr` usa `eval` internamente. Con el
  AST no hay ningún `eval` ni `exec` en todo el módulo, y además se pueden dar mensajes de error
  propios.
- **¿Por qué comparar signos y no el producto?** Para evitar el underflow de `fa·fr` (ver 3.3).
- **¿Por qué SymPy para la continuidad y no solo muestreo?** Un muestreo puede «saltarse» una
  asíntota entre dos puntos. SymPy encuentra el punto exacto (x = 0, x = π/2).
- **Límite**: si SymPy no logra decidir la continuidad (expresiones muy complejas, más de 4 s),
  el método se ejecuta con una advertencia, como pide el enunciado.
- **Límite**: el graficador detecta asíntotas por SymPy y por refinamiento numérico. Una
  oscilación extremadamente rápida (como sin(1/x) cerca de 0) puede verse imperfecta con 2001
  puntos.
- **Límite**: `x**(1/3)` con x < 0 se considera no real, igual que en Python (no se usa la raíz
  cúbica real).

---

## 11. Guion sugerido para la presentación

| Min | Qué mostrar | Qué decir |
|---|---|---|
| 0–1 | Diagrama de la sección 1 | «Toda la matemática está en Python; la web y la consola usan las mismas funciones.» |
| 1–2 | Parser: escribir `x^2 - 2` y luego `__import__('os')` | Aviso de ^ → ** y rechazo del código. «No usamos eval: árbol sintáctico + lista blanca.» |
| 2–5 | Bisección: caso x³ − 2x − 5 | Tabla, nota «extremos antes de actualizar», Eb ≤ E, n_min = 14 = iteraciones, SciPy = 0 |
| 5–6 | Botones x² + 1, x² − 1 y 1/x | Las 3 validaciones; con 1/x → «Graficar esta función» muestra la asíntota |
| 6–7 | Nmax = 5 | Aviso inicial y «SIN garantía» |
| 7–8 | Graficador: racional, log y tan | Segmentos, puntos descartados y discontinuidades |
| 8–9 | Posicional: 84506 y 11110011 | Superíndices, divisiones sucesivas y verificación |
| 9–10 | Errores: 0.1 + 0.2, overflow, xv = 0 y propagación | «Depende del tipo y la operación»; primer orden |
| 10 | `python -m pytest` | 309 pruebas en verde |
