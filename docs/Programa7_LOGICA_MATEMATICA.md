# Programa 7 · La lógica matemática, explicada de forma sencilla

> **Para qué sirve este archivo:** para explicarle al profesor **qué matemática hace el programa y
> dónde está**. No habla de la web ni del servidor: solo de los cálculos.
>
> **Dónde está la lógica matemática en el código:** toda en **`programas/Programa7_GrupoX.py`**,
> ordenada de arriba hacia abajo en el mismo orden que este documento:
>
> | Parte | Sección del archivo | Qué calcula |
> |---|---|---|
> | A | `# A. MÉTODO DE BISECCIÓN` (línea 68) | El método de Bisección, n_min y las validaciones |
> | B | `# B. GRAFICADOR DE FUNCIONES` (línea 429) | Los puntos de la gráfica y dónde cortarla |
> | C | `# C. NOTACIÓN POSICIONAL` (línea 594) | Notación posicional y conversión base 10 ↔ base 2 |
> | D | `# D. ERRORES NUMÉRICOS` (línea 824) | Punto flotante, errores y propagación |
>
> Ese archivo importa dos herramientas de apoyo (no son la matemática del enunciado):
> `backend/programa_4/modulos/numericos/parser_seguro.py` (cómo se «lee» la f(x) que escribe el
> usuario) y `continuidad.py` (pregunta a SymPy si f es continua).
>
> El resto del proyecto (consola, web) **no calcula nada**: solo pide los datos y muestra lo que
> devuelve `Programa7_GrupoX.py`.

---

## A. Método de Bisección

### La idea en una frase

Si una función continua es **negativa en un extremo y positiva en el otro**, tiene que cruzar el
cero en algún punto intermedio. Partimos el intervalo por la mitad una y otra vez, quedándonos
siempre con la mitad donde sigue habiendo cambio de signo, hasta que el intervalo es tan pequeño
como queramos.

### El teorema que lo justifica: Bolzano

> Si **f es continua** en [a, b] y **f(a)·f(b) < 0**, existe al menos un c entre a y b con f(c) = 0.

Las dos condiciones son necesarias, por eso el programa revisa **ambas** antes de empezar:

| Caso | ¿Qué pasa? | El programa… |
|---|---|---|
| x² + 1 en [−1, 1] | f(−1) = 2 y f(1) = 2: **mismo signo** | Rechaza el intervalo (no dice que no haya raíces en otro lado) |
| x² − 1 en [1, 2] | f(1) = 0 | Avisa: «raíz exacta en el extremo x = 1» y termina |
| 1/x en [−1, 1] | Cambia de signo, pero **no es continua** en x = 0 (asíntota) | No ejecuta el método: Bolzano no se cumple |
| x³ − 2x − 5 en [2, 3] | f(2) = −1, f(3) = 16 y continua | Ejecuta el método |

¿Cómo sabe el programa si f es continua? Le pregunta a SymPy en qué parte de [a, b] f es
continua y resta: [a, b] − (parte continua) = puntos problemáticos. Para 1/x en [−1, 1] eso da
{0}, porque el denominador se anula.

### Paso a paso (una iteración)

1. **Punto medio:** xr = (a + b) / 2
2. **Cota del error:** Eb = (b − a) / 2. La raíz está como mucho a esa distancia de xr, porque xr
   es el centro del intervalo y la raíz está dentro.
3. Calcular f(xr).
4. Si f(xr) = 0 → encontramos la raíz exacta. **Fin.**
5. Si Eb ≤ E (la tolerancia) → ya es lo bastante precisa. **Fin.**
6. Si f(a) y f(xr) tienen **signos distintos** → la raíz está en [a, xr], así que b = xr.
   Si no → la raíz está en [xr, b], así que a = xr.
7. Volver al paso 1.

Si se hacen Nmax iteraciones sin llegar a Eb ≤ E, el programa avisa que el resultado **no
garantiza** la tolerancia.

### Ejemplo hecho a mano: f(x) = x³ − 2x − 5 en [2, 3], E = 0.0001

f(2) = 8 − 4 − 5 = **−1** (negativo) y f(3) = 27 − 6 − 5 = **16** (positivo): hay cambio de signo.

| k | a | b | xr = (a+b)/2 | f(xr) | Signo de f(xr) | Nuevo intervalo | Eb = (b−a)/2 |
|---|---|---|---|---|---|---|---|
| 1 | 2 | 3 | 2.5 | 15.625 − 5 − 5 = **5.625** | + (≠ f(a)) | [2, 2.5] | 0.5 |
| 2 | 2 | 2.5 | 2.25 | **1.890625** | + | [2, 2.25] | 0.25 |
| 3 | 2 | 2.25 | 2.125 | **0.345703** | + | [2, 2.125] | 0.125 |
| 4 | 2 | 2.125 | 2.0625 | **−0.351318** | − (= f(a)) | [2.0625, 2.125] | 0.0625 |
| 5 | 2.0625 | 2.125 | 2.09375 | **−0.008942** | − | [2.09375, 2.125] | 0.03125 |
| … | | | | | | | … |
| 14 | 2.094482422 | 2.094604492 | **2.09454345703125** | −0.0000896 | | | **0.000061 ≤ 0.0001 ✓** |

Resultado: **xr ≈ 2.0945435**, con la garantía |raíz − xr| ≤ 0.000061. La raíz real es 2.0945515;
el error verdadero (0.000008) es aún menor que la cota.

### ¿Cuántas iteraciones hacen falta? (n_min)

Cada iteración **parte a la mitad** el intervalo, así que después de n iteraciones:

    Eb = (b − a) / 2ⁿ

Si queremos Eb ≤ E, hace falta que 2ⁿ ≥ (b − a)/E, es decir:

    n_min = ⌈ log₂( (b − a) / E ) ⌉

En el ejemplo, (b − a)/E = 1/0.0001 = 10 000.
- 2¹³ = 8 192 no alcanza (es menor que 10 000).
- 2¹⁴ = 16 384 sí alcanza.

Así que **n_min = 14**, justo las 14 iteraciones que hizo el programa.

### Las columnas Ea y εa de la tabla

- **Ea = |xr_k − xr_(k−1)|**: cuánto se movió la aproximación respecto a la anterior.
- **εa = |(xr_k − xr_(k−1)) / xr_k|**: lo mismo, pero relativo.
- En la iteración 1 no hay xr anterior, así que se muestra «—». Si xr = 0, εa sería una división
  entre cero y se muestra «No definido».
- **No se usan para parar**: el criterio de parada es Eb ≤ E, porque Eb es una garantía y Ea no.

### El código real (`Programa7_GrupoX.py`, sección A.3, función `metodo_biseccion`)

```python
for k in range(1, max_iter + 1):
    xr = (a + b) / 2          # punto medio
    cota = (b - a) / 2        # Eb: la raíz está a lo sumo a media longitud de xr
    fr = funcion(xr)
    ...                        # (se calculan Ea y εa y se guarda la fila de la tabla)
    if fr == 0:
        motivo = "raiz_exacta"     # raíz exacta en aritmética de máquina
        break
    if cota <= tolerancia:
        motivo = "tolerancia"      # criterio de parada: Eb ≤ E
        break
    if signo(fa) * signo(fr) < 0:
        b, fb = xr, fr             # la raíz está en [a, xr]
    else:
        a, fa = xr, fr             # la raíz está en [xr, b]
```

Un detalle que puede preguntar el profesor: en vez de calcular el producto `fa * fr < 0` se
comparan los **signos** (−1, 0 o 1). Matemáticamente es lo mismo. Pero si f(a) y f(xr) son números
muy pequeños (como 10⁻²⁰⁰), su producto (10⁻⁴⁰⁰) no cabe en la computadora y se vuelve 0, y el
programa elegiría la mitad equivocada.

**Comparación con SciPy:** al final, el programa calcula la raíz también con
`scipy.optimize.bisect`, solo para **comprobar** que la nuestra está bien. En los 4 casos del
enunciado la diferencia es 0.

### Cómo decirlo al profesor

> «Comprobamos las hipótesis de Bolzano (cambio de signo y continuidad). Luego, en cada paso,
> tomamos el punto medio y nos quedamos con la mitad donde f cambia de signo. La cota del error es
> la mitad del intervalo, y paramos cuando es menor que la tolerancia. Como el intervalo se divide
> entre 2 en cada paso, sabemos de antemano que hacen falta ⌈log₂((b − a)/E)⌉ iteraciones: 14 en
> los ejemplos.»

---

## B. Graficador

### La idea en una frase

Calculamos f en **muchos puntos** (2001), tiramos los que no existen y unimos con líneas **solo**
los puntos vecinos que pertenecen al mismo «trozo» continuo de la función.

### Paso a paso

1. Repartir 2001 puntos equiespaciados entre x_min y x_max. Por ejemplo, en [−5, 5] la separación
   es h = 10/2000 = 0.005.
2. Calcular f en cada punto.
3. **Descartar** los puntos donde f no existe:
   - log o raíz de un negativo;
   - división entre 0;
   - resultados infinitos.

   Por eso log(x) solo se dibuja para x > 0 y √(4 − x²) solo entre −2 y 2.
4. **Cortar la línea** donde hay una asíntota, para no unir las dos ramas de, por ejemplo, 1/x.
   Se usan dos métodos:
   - **Exacto:** SymPy dice dónde f no es continua (x = 0 en 1/x, x = ±π/2 en tan x) y ahí se corta.
   - **Numérico (red de seguridad):** si entre dos puntos vecinos f da un salto muy grande, se
     miran 33 puntos intermedios.
     - Si la función es continua aunque sea empinada, el salto **se reparte** entre los puntos
       intermedios.
     - Si es una asíntota, el salto **sigue concentrado** en un solo paso (o aparece un infinito),
       y se corta.

### Ejemplo

f(x) = (x + 1)/(x − 1) en [−5, 5]: el denominador vale 0 en x = 1. La gráfica sale en **2 trozos**
(uno a cada lado de x = 1) y no se dibuja la falsa línea vertical que uniría −∞ con +∞.

### El código real (`Programa7_GrupoX.py`, sección B, función `hay_salto`)

```python
xs = np.linspace(x0, x1, SUBPUNTOS_REFINAMIENTO)    # 33 puntos entre los dos vecinos
ys = funcion.evaluar_vector(xs)
if not np.all(np.isfinite(ys)):
    return True                                      # apareció un infinito: asíntota
mayor_paso = float(np.max(np.abs(np.diff(ys))))
return mayor_paso > 0.5 * salto                      # el salto no se repartió: asíntota
```

### Cómo decirlo al profesor

> «Evaluamos 2001 puntos, descartamos los que no son números reales y partimos la curva donde la
> función no es continua. Así una función racional no queda unida a través de su asíntota.»

---

## C. Notación posicional (base 10 ↔ base 2)

### La idea en una frase

En un número, **cada dígito vale según su posición**: dígito × base^posición, contando las
posiciones desde 0 por la derecha.

    (dₙ … d₂ d₁ d₀)_base = dₙ·baseⁿ + … + d₂·base² + d₁·base¹ + d₀·base⁰

### Ejemplo en base 10

    (84506)₁₀ = 8·10⁴ + 4·10³ + 5·10² + 0·10¹ + 6·10⁰
              = 80 000 + 4 000 + 500 + 0 + 6 = 84 506

### De base 2 a base 10: sumar las potencias

    (11110011)₂ = 1·2⁷ + 1·2⁶ + 1·2⁵ + 1·2⁴ + 0·2³ + 0·2² + 1·2¹ + 1·2⁰
                = 128 + 64 + 32 + 16 + 0 + 0 + 2 + 1
                = (243)₁₀

La propia descomposición **es** la conversión.

### De base 10 a base 2: dividir entre 2 y guardar los residuos

| Número | ÷ 2 = | Residuo |
|---|---|---|
| 243 | 121 | **1** |
| 121 | 60 | **1** |
| 60 | 30 | **0** |
| 30 | 15 | **0** |
| 15 | 7 | **1** |
| 7 | 3 | **1** |
| 3 | 1 | **1** |
| 1 | 0 | **1** |

Se leen los residuos **de abajo hacia arriba**: 243 = **(11110011)₂**. El primer residuo es el
dígito de la posición 0 (el de la derecha), por eso se leen al revés.

**Verificación:** el programa descompone **los dos** números y comprueba que dan el mismo valor
(243 = 243).

**Números negativos:** el signo no es parte de la notación posicional. Se descompone el valor
absoluto y se pone el signo delante: (−243)₁₀ = −(2·10² + 4·10¹ + 3·10⁰) = (−11110011)₂.

### El código real (`Programa7_GrupoX.py`, sección C)

```python
# Descomposición: cada dígito por su potencia
for indice, caracter in enumerate(digitos):
    digito = ord(caracter) - ord("0")          # '7' → 7 sin usar int()
    exponente = n - 1 - indice
    aporte = digito * potencia_entera(base, exponente)
    valor += aporte

# Base 10 → base 2: divisiones sucesivas
while actual > 0:
    cociente, residuo = actual // base, actual % base
    residuos.append(residuo)
    actual = cociente
digitos = "".join(chr(ord("0") + r) for r in reversed(residuos))   # de abajo hacia arriba
```

Las dos conversiones están programadas a mano: **no** se usan `int(texto, 2)` ni `bin()`.

### Cómo decirlo al profesor

> «Cada dígito se multiplica por la base elevada a su posición. Para pasar de binario a decimal
> sumamos esas potencias; para pasar de decimal a binario dividimos entre 2 y leemos los residuos
> de abajo hacia arriba. Al final comprobamos que los dos números valen lo mismo.»

---

## D. Errores numéricos y punto flotante

### 1. ¿Por qué 0.1 + 0.2 no da exactamente 0.3?

La computadora guarda los números **en binario** con una cantidad fija de cifras (52 bits de
mantisa en el formato IEEE 754 «double»). Para pasar 0.1 a binario se multiplica por 2 y se toma
la parte entera, una y otra vez:

    0.1 × 2 = 0.2 → 0
    0.2 × 2 = 0.4 → 0
    0.4 × 2 = 0.8 → 0
    0.8 × 2 = 1.6 → 1
    0.6 × 2 = 1.2 → 1
    0.2 × 2 = 0.4 → 0   ← se repite desde aquí
    ...
    0.1 = 0.0001100110011…₂   (periódico, nunca termina)

Igual que 1/3 = 0.3333… en decimal, 0.1 **no tiene fin en binario**, y la computadora tiene que
cortarlo y redondearlo. Lo que realmente guarda es 0.1000000000000000055511…

Lo mismo pasa con 0.2 y 0.3. Al sumar, los pequeños errores no coinciden:

    0.1 + 0.2 = 0.30000000000000004   ≠   0.3

**Conclusión:** los decimales no se comparan con `==`, sino con una tolerancia: |a − b| < ε.

### 2. Épsilon de máquina

Es la distancia entre 1.0 y el **siguiente** número que la computadora puede guardar:

    ε = 2⁻⁵² ≈ 2.22 × 10⁻¹⁶

Por eso 1.0 + ε ≠ 1.0, pero 1.0 + ε/2 = 1.0: lo que se suma es tan pequeño que se pierde al
redondear.

### 3. Overflow y underflow

| Fenómeno | Qué es | Ejemplo (ejecutado en el equipo) |
|---|---|---|
| **Overflow** | El resultado es más grande que el máximo (≈ 1.8 × 10³⁰⁸) | `math.exp(1000)` da error; `1e308 * 10` da `inf` |
| **Subnormal** | Número más pequeño que el mínimo normal (≈ 2.2 × 10⁻³⁰⁸): se guarda con menos precisión | `1e-320 * 1e300` da 9.99988…e-21 en vez de 1e-20 |
| **Underflow** | El resultado es tan pequeño que se vuelve 0 | `5e-324 / 2` da `0.0` |

Que salga `inf`, un error o un aviso **depende del tipo de número y de la operación** (Python,
NumPy, float32…). Por eso el programa lo ejecuta y muestra lo que pasó en ese equipo.

### 4. Tipos de error

| Error | De dónde viene | Ejemplo |
|---|---|---|
| **Inherente** | Los datos ya vienen con error (mediciones) | Medir un radio de 2.0 ± 0.05 cm |
| **De redondeo** | Guardar los números con cifras limitadas | 0.1 + 0.2 ≠ 0.3 |
| **De truncamiento** | **El método** corta un proceso infinito | e ≈ 1 + 1 + 1/2! + 1/3! + 1/4! + 1/5! = 2.71667 (el valor real es 2.71828) |
| **Overflow / underflow** | El número no cabe | `math.exp(1000)` |
| **Del modelo** | **La ecuación** simplifica la realidad | Péndulo con sen θ ≈ θ: error del 6.8 % a 60° |

**Truncamiento vs. modelo:**
- El truncamiento es culpa del **método** y se arregla con más términos o iteraciones.
- El error del modelo es culpa de **la ecuación** que se eligió; aunque se calcule perfecto, sigue
  ahí.

### 5. Calculadora de errores

    Error absoluto     Ea  = |xv − xa|
    Error relativo     Er  = Ea / |xv|
    Error porcentual   Er% = Er × 100

Ejemplo con xv = π y xa = 3.14:
- Ea = |3.14159265 − 3.14| = **0.00159265**
- Er = 0.00159265 / 3.14159265 = **0.000507**
- Er% = **0.0507 %**

**Si xv = 0**, Er dividiría entre cero: el programa responde «Error relativo no definido» y no
inventa un porcentaje.

```python
error_absoluto = abs(xv - xa)
if xv == 0:
    ...  # "Error relativo no definido"
error_relativo = error_absoluto / abs(xv)
```

### 6. Propagación del error

Si x cambia un poquito (Δx), ¿cuánto cambia y = f(x)? La derivada es la pendiente, así que:

    Δy aproximado = f′(x) · Δx              (aproximación con la recta tangente)
    Δy real       = f(x + Δx) − f(x)

Ejemplo con f(x) = sin(x) + x², x = 1 y Δx = 0.01:

| Paso | Cálculo | Valor |
|---|---|---|
| Derivada (con SymPy) | f′(x) = cos(x) + 2x | f′(1) = 0.5403 + 2 = **2.5403** |
| Δy aproximado | 2.5403 × 0.01 | **0.025403** |
| Δy real | f(1.01) − f(1) = 1.866932 − 1.841471 | **0.025461** |
| Diferencia | \|0.025461 − 0.025403\| | **0.000058** |

La diferencia es pequeña porque la aproximación es de **primer orden**: ignora el término
f″·Δx²/2 de Taylor. Si Δx se hace 10 veces más pequeño, la diferencia se hace unas 100 veces más
pequeña.

```python
dy_aprox = derivada_en_x * dx          # aproximación lineal (diferencial)
dy_real = fx_dx - fx                    # cambio verdadero
diferencia = abs(dy_real - dy_aprox)
```

### Cómo decirlo al profesor

> «La computadora guarda los números en binario con 52 bits, y 0.1 no tiene representación
> binaria finita: por eso 0.1 + 0.2 no da exactamente 0.3. El épsilon de máquina, 2⁻⁵², mide esa
> precisión. Además calculamos los errores absoluto, relativo y porcentual (el relativo no existe
> si el valor verdadero es 0) y comparamos la propagación lineal f′(x)·Δx con el cambio real.»

---

## Extra: ¿cómo «entiende» el programa la función que escribe el usuario? (`parser_seguro.py`)

El usuario escribe un texto, por ejemplo `x**3 - 2*x - 5`. El programa **no** lo ejecuta como
código: está prohibido usar `eval()`, porque alguien podría escribir algo como
`__import__('os')` y dañar el equipo. En su lugar:

1. Si el usuario escribió `^`, se cambia por `**` y se le avisa (en Python `^` no es potencia).
2. Se convierte el texto en un **árbol** de operaciones:

   ```
              (−)
             /   \
           (−)    5
          /   \
       (**)   (*)
       /  \   /  \
      x    3 2    x
   ```

3. Se revisa que el árbol **solo** tenga cosas permitidas:
   - números y la variable x;
   - pi y e;
   - las operaciones + − × ÷ y potencia;
   - las funciones sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, exp, log, ln, log10, sqrt
     y abs.

   Cualquier otra cosa se rechaza con un mensaje.
4. Se recorre el árbol para calcular f(x). Si en algún punto no se puede (log de un negativo,
   división entre 0…), el programa dice exactamente por qué.

> «No ejecutamos el texto del usuario: lo convertimos en un árbol de operaciones, revisamos que
> solo tenga operaciones matemáticas permitidas y calculamos recorriéndolo.»
