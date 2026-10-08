# Notas para el informe – Programa 5 (Módulo III: Álgebra de Matrices)

> Borrador de apoyo. Integrantes: Grupo X — completar.
> Cálculo: `backend/programa_4/modulos/modulo_matrices.py` · Adaptador web: `backend/calculo/programa5_web.py`
> Pruebas: `backend/pruebas/pruebas_programa5.py` (cálculo) y `backend/pruebas/pruebas_programa5_web.py` (API)

## 1. Qué hace el módulo

Es la opción 3 del menú principal de la calculadora. Ofrece suma, resta, producto por
escalar, producto matricial, transposición, determinante (tres métodos), inversa (dos
métodos) y un verificador de siete propiedades. Todo se calcula con listas anidadas y
`fractions.Fraction`, sin bibliotecas de álgebra, de modo que los resultados son exactos:
`3/2` se guarda como 3/2 y no como 1.5, y la comprobación `A·A⁻¹ = I` es una igualdad
exacta, sin tolerancias de redondeo.

El código está separado en dos capas. Las funciones de **cálculo** reciben matrices y
devuelven resultados; ninguna usa `print()` ni `input()`. Las funciones de **interfaz**
(`leer_…`, `mostrar_…`, `imprimir_…`, `opcion_…`) leen, validan e imprimen. Gracias a esa
separación el script de pruebas puede importar el cálculo y comprobarlo con `assert`.

## 2. Lógica del producto matricial

`multiplicar_matrices(A, B)` exige que las columnas de A coincidan con las filas de B: cada
entrada del resultado empareja una fila de A con una columna de B, y ambas deben tener la
misma cantidad de elementos. Si A es m×n y B es n×p, el resultado es m×p y

    cᵢⱼ = aᵢ₁·b₁ⱼ + aᵢ₂·b₂ⱼ + … + aᵢₙ·bₙⱼ

Se implementa con tres bucles anidados: el primero recorre las filas de A, el segundo las
columnas de B y el tercero acumula la suma de productos. Si las dimensiones no encajan,
la validación se hace **antes** de pedir los elementos y se muestra, por ejemplo,
`No se puede multiplicar: Columnas de A [3] ≠ Filas de B [2]`.

Tras mostrar A·B el programa calcula B·A cuando está definido y los compara. Con
A (2×3) y C (3×2) del caso de prueba, A·C es 2×2 y C·A es 3×3: el producto no es conmutativo.

## 3. Lógica de la expansión por cofactores

`determinante_por_cofactores(A)` desarrolla el determinante sobre la primera fila:

    det(A) = a₁₁·C₁₁ + a₁₂·C₁₂ + … + a₁ₙ·C₁ₙ,   con   Cᵢⱼ = (−1)^(i+j) · det(Mᵢⱼ)

- `submatriz_menor` construye Mᵢⱼ quitando la fila i y la columna j.
- `cofactor` aplica el signo, que alterna como un tablero de ajedrez (+ − + …).
- La función es **recursiva**: para un determinante n×n pide n determinantes (n−1)×(n−1),
  hasta llegar al caso base 1×1, cuyo determinante es su único elemento.

Sirve para cualquier n, pero su costo crece como n!: cada nivel multiplica el trabajo por
el tamaño de la matriz. Por eso el módulo incluye el método eficiente,
`determinante_por_reduccion`, que reduce A a triangular superior con operaciones de fila
(≈ n³ operaciones) y usa que el determinante de una triangular es el producto de su diagonal:

- un **intercambio** de filas cambia el signo, así que se cuentan y se aplica (−1)^intercambios;
- un **reemplazo** Fᵢ → Fᵢ − k·Fⱼ no altera el determinante, así que los factores k solo se registran.

Solo se intercambia cuando el pivote es 0, porque sin pivote no se puede anular la columna.
En matrices 3×3 se muestra además la regla de Sarrus, y la opción 6 comprueba que todos
los métodos coinciden. Medición en una matriz 8×8 en la máquina de desarrollo: cofactores
≈ 0.32 s frente a ≈ 0.0006 s por reducción (repetir la medición si se cita en el informe).

La misma función `cofactor` alimenta la inversa por adjunta: `matriz_de_cofactores` reúne
todos los Cᵢⱼ, su transpuesta es adj(A) y A⁻¹ = (1/det A)·adj(A) siempre que det(A) ≠ 0.

## 4. Lógica de Gauss-Jordan sobre [A | I]

`invertir_por_gauss_jordan(A)` se apoya en una idea: las operaciones de fila que convierten
A en I son las mismas que convierten I en A⁻¹. Por eso:

1. `construir_aumentada_con_identidad` pega la identidad a la derecha de A: [A | I], de n × 2n.
2. `escalonar` (la reducción que ya existía en el módulo de vectores) recorre las n columnas
   de A. En cada una elige un pivote, intercambia filas si hace falta, divide la fila para
   dejar el pivote en 1 y anula el resto de la columna, por encima y por debajo.
3. Cada operación se aplica a la fila completa, así que el bloque derecho la recibe también.
4. Si aparecen n pivotes, el bloque izquierdo es I y el derecho es A⁻¹: se extrae y se devuelve
   junto con la matriz final [I | A⁻¹] y la lista de operaciones.
5. Si aparecen menos de n pivotes, la matriz es **singular**: el bloque izquierdo no llega a I,
   la reducción se detiene y no se calcula ninguna inversa.

Después de obtener A⁻¹ (por cualquiera de los dos métodos) el programa calcula A·A⁻¹ con su
propia función de producto y la compara con I.

El diagnóstico final enlaza con el Teorema de la Matriz Invertible: det(A) ≠ 0, n posiciones
pivote, columnas L.I. y columnas que generan ℝⁿ son afirmaciones equivalentes.

## 5. Versión web

El botón **Álgebra de Matrices** de la calculadora web ofrece lo mismo que la consola,
repartido en cinco secciones: Operaciones (opciones 1–5), Determinante (6), Inversa (7 y 8),
Verificador (9) y Teoremas clave (0).

La web no repite ningún cálculo. El recorrido de un dato es:

1. El navegador envía las matrices como **texto** (`"3/2"`, `"-0.5"`) para no perder exactitud.
2. `backend/app/api.py` recibe la petición en una ruta `/api/p5/…` y valida su forma.
3. `backend/calculo/programa5_web.py` convierte el texto a `Fraction` y llama a las mismas
   funciones de `modulo_matrices.py` que usa la consola.
4. El resultado vuelve como JSON y el frontend solo lo dibuja.

Por eso los mensajes y los valores coinciden en ambas interfaces: el error
`No se puede multiplicar: Columnas de A [3] ≠ Filas de B [2]`, el diagnóstico de
invertibilidad y los veredictos «Se cumple» / «No se cumple» salen del mismo módulo.
En la inversa por Gauss-Jordan la web añade un paso a paso que muestra la matriz
[A | I] antes y después de cada operación de fila. En el verificador, cada propiedad
tiene un botón «Ver el paso a paso» con los cálculos de sus dos miembros: inversas por
Gauss-Jordan, productos fila por columna, transpuestas, determinantes por reducción
triangular y por cofactores (con cada menor M₁ⱼ) y la cuenta final. También los arma el backend.

## 6. Casos de prueba verificados

Todos están en `pruebas_programa5.py` (cálculo) y `pruebas_programa5_web.py` (API) y pasan.
Se ejecutan desde `backend/` con `python -m pruebas.pruebas_programa5` y
`python -m pruebas.pruebas_programa5_web`.

| Entrada | Resultado |
|---|---|
| A = [[1,2,3],[4,5,6]], C = [[1,0],[2,1],[0,3]] | A·C = [[5,11],[14,23]]; C·A es 3×3 |
| A 2×3 por B 2×3 | `No se puede multiplicar: Columnas de A [3] ≠ Filas de B [2]` |
| A = [[1,2,3],[0,1,4],[5,6,0]] | det = 1; A⁻¹ = [[-24,18,5],[20,-15,-4],[-5,4,1]] por ambos métodos |
| A = [[1,2],[3,4]] | adj = [[4,-2],[-3,1]]; A⁻¹ = [[-2,1],[3/2,-1/2]] |
| A = [[1,2,3],[4,5,6],[7,8,9]] | det = 0, 2 pivotes, «La matriz es singular», sin inversa |
| Verificador con A = [[1,2],[3,4]], B = [[0,1],[1,1]] | det(A) = -2; det(A⁻¹) = -1/2; (AB)⁻¹ = [[7/2,-3/2],[-2,1]]; (Aᵀ)⁻¹ = [[-2,3/2],[1,-1/2]] |
| Propiedad 5 con la misma A | intercambio → 2; F₂ → F₂ − 3F₁ → -2; F₁ por 3 → -6 |
| Propiedad 6 con A = [[1,2,3],[0,1,4],[5,6,0]] | F₃ → F₃ − 5F₁ y F₃ → F₃ + 4F₂; diagonal 1, 1, 1; det = 1 |
| Propiedad 7 con A = [[1,2],[3,4]], B = [[0,1],[1,1]] | AB = [[2,3],[4,7]]; det(AB) = 2 = (-2)·(-1) = det(A)·det(B) |

## 7. Capturas de pantalla que hay que tomar

### Consola

Ejecutar `python main.py` desde `backend/programa_4/` y entrar a la opción 3.

- [ ] Menú principal y logotipo del Módulo III con sus 11 opciones.
- [ ] Opción 0: teoremas clave.
- [ ] Opción 1: suma (usar alguna fracción, p. ej. `1/2` y `-0.5`, para que se vea el formato).
- [ ] Opción 2: resta.
- [ ] Opción 3: multiplicación por escalar (p. ej. k = `3/2`).
- [ ] Opción 4: producto A (2×3) por C (3×2), con A·C y C·A.
- [ ] Opción 4: **error de dimensiones** con A 2×3 y B 2×3.
- [ ] Opción 5: transposición de una matriz 2×3.
- [ ] Opción 6: determinante de la matriz **invertible** [[1,2,3],[0,1,4],[5,6,0]] (cofactores, Sarrus, reducción y coincidencia).
- [ ] Opción 6: determinante de la matriz **singular** [[1,2,3],[4,5,6],[7,8,9]] con su diagnóstico.
- [ ] Opción 7: inversa por Gauss-Jordan de la invertible ([A | I], operaciones, [I | A⁻¹] y comprobación).
- [ ] Opción 7: la misma opción con la singular (2 de 3 pivotes, sin inversa).
- [ ] Opción 8: inversa por adjunta de [[1,2],[3,4]] (cofactores, adj(A), A⁻¹).
- [ ] Opción 9: verificador con A = [[1,2],[3,4]] y B = [[0,1],[1,1]] (propiedades 1 a 4).
- [ ] Opción 9: propiedad 5 con las tres operaciones de fila (filas 1 y 2; i = 2, j = 1, k = -3; fila 1, k = 3).
- [ ] Opción 9: propiedad 6 con A = [[1,2,3],[0,1,4],[5,6,0]] (requiere otra corrida del verificador con n = 3).
- [ ] Opción 9: propiedad 7, det(AB) = det(A)·det(B), que sale al final de la corrida 2×2 (det(AB) = 2 = (-2)·(-1)).
- [ ] Un dato inválido que se vuelve a pedir sin cerrar el programa (p. ej. `abc` como dimensión o `1/0` como elemento).
- [ ] Salida de `python -m pruebas.pruebas_programa5` con todas las pruebas en `ok`.

### Web

Con backend y frontend en marcha, abrir el botón **Álgebra de Matrices**. Cada sección
trae botones que cargan estos mismos casos.

Ya hay una captura de cada caso en [`capturas_web/`](capturas_web/). Son de página
completa (1280 px de ancho) y se generaron con un navegador automatizado sobre la
aplicación real; conviene recortarlas al pegarlas en el informe. Las capturas 14 y 15
son anteriores a la propiedad 7 (det(AB) = det(A)·det(B)) y al paso a paso del verificador:
hay que volver a tomarlas, y conviene añadir una con un paso a paso abierto.

| Captura | Qué muestra |
|---|---|
| `00-entrada.png` | Pestaña «Álgebra de Matrices» recién abierta, con sus cinco secciones |
| `01-producto.png` | Operaciones: «A·C (2×3 · 3×2)», con A·C, C·A y la nota de no conmutatividad |
| `02-producto-error.png` | Operaciones: «Error 2×3 · 2×3», con el aviso de dimensiones |
| `03-suma.png` | Operaciones: suma con fracciones |
| `04-escalar.png` | Operaciones: multiplicación por el escalar 3/2 |
| `05-transpuesta.png` | Operaciones: transpuesta de una matriz 2×3 |
| `06-det-invertible.png` | Determinante: «Invertible 3×3» (tres métodos, coincidencia y diagnóstico) |
| `07-det-singular.png` | Determinante: «Singular 3×3» con el diagnóstico de matriz singular |
| `08-det-intercambio.png` | Determinante: «Pivote 0 (2×2)», donde un intercambio cambia el signo |
| `09-gj-invertible.png` | Inversa por Gauss-Jordan: «Invertible 3×3» con el paso a paso abierto |
| `10-gj-singular.png` | Inversa por Gauss-Jordan: «Singular 3×3» (2 de 3 pivotes, reducción detenida) |
| `11-adjunta.png` | Inversa por adjunta: «Invertible 2×2» (C, adj(A), A⁻¹ y comprobación) |
| `12-adjunta-singular.png` | Inversa por adjunta: «Singular 3×3», sin inversa |
| `13-verificador-entrada.png` | Verificador: matrices A y B y selectores de las operaciones de fila |
| `14-verificador-2x2.png` | Verificador: «Caso 2×2» con las siete propiedades en «Se cumple» |
| `15-verificador-3x3.png` | Verificador: «Caso 3×3 (propiedad 6)» con la reducción triangular |
| `16-verificador-error.png` | Verificador: «B singular (error)» con el aviso de matriz no invertible |
| `17-teoremas.png` | Teoremas clave |
