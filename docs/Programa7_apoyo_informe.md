# Programa 7 – Apoyo para el informe (Métodos Numéricos)

> Integrantes: Grupo 1 — SaraRuiz, VictorAlcocer, MoisesValle, AndreGuido.
> Algoritmos y matemática: `programas/Programa7_GrupoX.py` (también abre la consola, opción 6)
> Web: botón **Métodos Numéricos** · Pruebas: `backend/pruebas/pruebas_programa7.py`
> Lógica matemática explicada de forma sencilla: [`Programa7_LOGICA_MATEMATICA.md`](Programa7_LOGICA_MATEMATICA.md)
> Detalle técnico completo: [`Programa7_logica_metodos_numericos.md`](Programa7_logica_metodos_numericos.md)

---

## (a) El método de Bisección (máximo 1 página)

**Fundamento: teorema de Bolzano.** Si f es **continua** en [a, b] y **f(a)·f(b) < 0** (f cambia
de signo), existe al menos un c ∈ (a, b) con f(c) = 0. Las dos hipótesis son imprescindibles:
sin continuidad, 1/x cambia de signo en [−1, 1] y no tiene raíz; sin cambio de signo, el teorema
no afirma nada.

**Condición inicial.** Antes de iterar el programa comprueba, en este orden:

1. a < b, E > 0 y Nmax ≥ 1.
2. f(a) y f(b) existen y son finitas.
3. Si f(a) = 0 o f(b) = 0, la raíz es exacta en el extremo y el programa termina.
4. Si f(a)·f(b) > 0, rechaza el intervalo. No afirma que f carezca de raíces en otros intervalos.
5. Comprueba con SymPy que f sea continua en [a, b]. Si no lo es, no ejecuta el método.

**Iteración.** En cada paso k:

    xr = (a + b)/2          (punto medio)
    Eb = (b − a)/2          (cota del error: |raíz − xr| ≤ Eb)
    si f(a)·f(xr) < 0  →  b = xr   (la raíz está en [a, xr])
    si no              →  a = xr   (la raíz está en [xr, b])

Como siempre se conserva la mitad donde f cambia de signo, el intervalo sigue cumpliendo
Bolzano y la raíz nunca se pierde.

**Criterio de parada.** El método se detiene en cuanto se cumple una de estas condiciones:

- **Eb ≤ E**: se alcanzó la tolerancia absoluta.
- **f(xr) = 0** exactamente.
- **Se agotaron Nmax iteraciones**: el resultado es una aproximación sin garantía de cumplir la tolerancia.

El error relativo εa = |(xr_k − xr_{k−1})/xr_k| se muestra como información, pero **no** es
criterio de parada.

**Número mínimo de iteraciones.** Tras n iteraciones la cota vale Eb = (b₀ − a₀)/2ⁿ. Si se
exige Eb ≤ E y se despeja n:

    (b₀ − a₀)/2ⁿ ≤ E   ⇔   2ⁿ ≥ (b₀ − a₀)/E   ⇔   n_min = ⌈log₂((b₀ − a₀)/E)⌉

Ejemplo: en [2, 3] con E = 10⁻⁴ se obtiene n_min = ⌈log₂(10 000)⌉ = ⌈13.29⌉ = 14, que coincide
con las 14 iteraciones ejecutadas en los cuatro casos de prueba.

---

## (b) Las 4 capturas que hay que tomar

Antes de empezar, levanta el backend y el frontend (ver README) y abre `http://localhost:5173`
→ **Métodos Numéricos**.

### Captura 1 – Bisección con tabla

| Campo | Valor |
|---|---|
| Pestaña | 1 · Bisección |
| f(x) | `x**3 - 2*x - 5` (o el botón «x³ − 2x − 5 en [2, 3]») |
| a / b | `2` / `3` |
| Tolerancia E / Nmax | `1e-4` / `100` |

Pulsa **Ejecutar Bisección**. En la captura deben verse el recuadro «Tolerancia alcanzada»,
n_min = 14, las 14 iteraciones, la raíz **2.09454345703125**, la cota **Eb = 6.1035e-5**, la
tabla con la nota «Extremos registrados antes de actualizar el intervalo» y el contraste con SciPy
(diferencia 0).

*Captura extra opcional:* el botón «x³ − 2x − 5 con Nmax = 5», que avisa de que no se alcanza la
tolerancia.

### Captura 2 – Gráfica racional (o con restricción de dominio)

| Campo | Valor |
|---|---|
| Pestaña | 2 · Graficador |
| f(x) | `(x + 1)/(x - 1)` (botón «Racional») |
| x mínimo / x máximo | `-5` / `5` |

Pulsa **Graficar**. Se ven 2 segmentos que no se unen en la asíntota x = 1, con
«Discontinuidades / dominio: x = 1».

*Alternativa con restricción de dominio:* `log(x)` en [`-1`, `5`] o `sqrt(4 - x**2)` en [`-3`, `3`].

*Alternativa más completa:* en Bisección, el caso `1/x` en [−1, 1] → **Graficar esta función**.
Muestra la asíntota en x = 0 dentro del intervalo sombreado: es la prueba visual de que el
cambio de signo no se debe a una raíz.

### Captura 3 – Notación posicional en base 10 y base 2

| Captura | Número | Base de origen | Resultado esperado |
|---|---|---|---|
| 3a | `84506` | 10 | (84506)₁₀ = 8·10⁴ + 4·10³ + 5·10² + 0·10¹ + 6·10⁰ = (10100101000011010)₂ |
| 3b | `11110011` | 2 | (11110011)₂ = 1·2⁷ + … + 1·2⁰ = 128 + 64 + 32 + 16 + 2 + 1 = (243)₁₀ |

Pulsa **Descomponer y convertir**. En 3a también se ve la tabla de divisiones sucesivas entre 2.

### Captura 4 – Cálculo de errores y propagación

| Sub-pestaña | Datos | Resultado esperado |
|---|---|---|
| Calculadora de errores | xv = `pi`, xa = `3.14` | Ea ≈ 0.0015927, Er ≈ 5.0696·10⁻⁴, Er% ≈ 0.0507 % |
| Calculadora de errores (caso límite) | xv = `0`, xa = `0.5` | «Error relativo no definido» |
| Propagación del error | f = `sin(x) + x**2`, x = `1`, Δx = `0.01` | f′(x) = 2x + cos(x); Δy aprox = 0.0254030; Δy real = 0.0254609; diferencia ≈ 5.78·10⁻⁵ |

---

## (c) Interpretación breve de los resultados

- **Bisección.** Los cuatro casos convergen en exactamente **14 iteraciones = n_min**, como
  predice la teoría. El error real queda por debajo de la cota: en x³ − 2x − 5,
  |2.09455148 − 2.09454346| ≈ 8·10⁻⁶ ≤ Eb = 6.1·10⁻⁵. SciPy da la misma raíz, lo que valida la
  implementación propia. Con Nmax = 5 la cota es Eb = 0.03125 > E: el programa lo advierte en
  lugar de presentar el resultado como válido.
- **Casos de rechazo.**
  - x² + 1 en [−1, 1] no cambia de signo: se rechaza el intervalo, no la existencia de raíces.
  - x² − 1 en [1, 2] tiene la raíz en el extremo a = 1.
  - 1/x en [−1, 1] cambia de signo por una **asíntota**, no por una raíz: Bolzano no aplica.
- **Graficador.** Los puntos donde f no existe se descartan (log, sqrt) y la curva se parte en
  las asíntotas. Así la gráfica no inventa una línea vertical falsa que «cruce» el eje.
- **Notación posicional.** Las dos descomposiciones dan el mismo valor (243 = 243): la conversión
  es correcta. La descomposición es el propio algoritmo de base 2 → base 10.
- **Errores.**
  - 0.1 + 0.2 = 0.30000000000000004 muestra el error de redondeo de IEEE 754.
  - La propagación da una diferencia de solo 0.23 % entre Δy aproximado y Δy real con
    Δx = 0.01, y con Δx = 0.001 la diferencia baja unas 100 veces. Es lo esperado de una
    aproximación de primer orden, cuyo error es del orden de Δx².

---

## (d) Respuestas cortas para la defensa

**¿Qué pasa si no hay cambio de signo?**
Si f(a)·f(b) > 0, Bolzano no garantiza ninguna raíz en [a, b] y el método no sabría qué mitad
conservar, así que el programa rechaza el intervalo. Eso no significa que f no tenga raíces: puede
tener un número par de ellas en [a, b] (x² − 1 en [−2, 2]) o tenerlas en otro intervalo.

**¿Por qué se reduce el intervalo a la mitad?**
El punto medio es la elección que minimiza el peor caso: sin más información sobre f, la raíz
puede estar en cualquiera de las dos mitades, y partir por el centro garantiza que el intervalo
que queda mide exactamente (b − a)/2. Así el error se reduce de forma predecible (a la mitad en
cada paso) y se puede calcular de antemano cuántas iteraciones hacen falta (n_min).

**¿Qué representa la cota del error?**
Eb = (b − a)/2 es la máxima distancia posible entre xr y la raíz verdadera, porque la raíz está
dentro de [a, b] y xr es su centro. Es una **garantía**: |raíz − xr| ≤ Eb, aunque no se conozca la
raíz. Por eso es el criterio de parada (Eb ≤ E).

**¿Cómo influye la tolerancia en el número de iteraciones?**
n_min = ⌈log₂((b − a)/E)⌉: el número de iteraciones crece con el **logaritmo** de 1/E. Cada vez que
la tolerancia se divide entre 10 hacen falta unas 3.3 iteraciones más (log₂ 10 ≈ 3.32). Con E = 10⁻⁴
son 14 iteraciones; con E = 10⁻⁸, 27.

**¿Por qué una asíntota puede producir un cambio de signo sin raíz?**
En una asíntota vertical f salta de −∞ a +∞ sin pasar por 0. Ejemplo: 1/x vale −1 en x = −1 y 1 en
x = 1, pero nunca vale 0. Falla la hipótesis de **continuidad** de Bolzano. Si se aplicara Bisección
igualmente, el método «convergería» a x = 0, que es la asíntota y no una raíz. Por eso el programa
verifica la continuidad con SymPy antes de iterar.

**¿Por qué 0.1 + 0.2 puede no ser igual a 0.3?**
Los floats se guardan en binario (IEEE 754, 52 bits de mantisa) y 0.1, 0.2 y 0.3 no tienen
representación binaria finita (0.1 = 0.000110011…₂, periódico). Se guarda la fracción binaria más
cercana. Los errores de redondeo de 0.1 y 0.2 se suman y el resultado (0.30000000000000004) es un
double distinto del que representa a 0.3. Por eso los floats se comparan con una tolerancia:
|a − b| < ε.
