# Programa 3 — Explicación técnica del producto matricial

Archivo: `programas/Programa 3_GrupoX.py` · función `producto_matrices(A, B)`

## 1. Definición algebraica

Sean A ∈ ℝ^(m×n) y B ∈ ℝ^(n×p). El producto C = A·B es la matriz m×p cuyo elemento
de la fila i y la columna j es

```
cᵢⱼ = Σₖ aᵢₖ·bₖⱼ ,   k = 1, …, n
```

Es decir, cᵢⱼ es el **producto punto de la fila i de A con la columna j de B**.
Para que ese producto punto exista, la fila de A (n elementos) y la columna de B
(filas(B) elementos) deben tener la misma longitud: **columnas(A) = filas(B)**.
Si no se cumple, el programa muestra las dos dimensiones y no opera
(`producto_compatible` y la validación de `opcion_producto_matrices`).

## 2. Código

```python
def producto_matrices(A, B):
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
```

## 3. Papel de cada bucle

| Bucle | Rango | Qué recorre | Qué produce |
|---|---|---|---|
| `i` (externo) | 0 … m−1 | las filas de A | una fila completa de C (`fila_c`) |
| `j` (intermedio) | 0 … p−1 | las columnas de B | un elemento cᵢⱼ dentro de esa fila |
| `k` (interno) | 0 … n−1 | **a la vez** las columnas de A (`A[i][k]`) y las filas de B (`B[k][j]`) | los n sumandos aᵢₖ·bₖⱼ del producto punto |

Puntos clave:

- **`k` es el índice compartido.** En `A[i][k]` es una columna y en `B[k][j]` es
  una fila. Por eso el bucle interno solo tiene sentido si columnas(A) = filas(B).
- **`suma` se reinicia a 0.0 para cada par (i, j).** Si se reiniciara fuera del
  bucle `j`, cada elemento arrastraría los sumandos del anterior.
- **Orden de llenado.** C se construye fila por fila: `fila_c` se vacía al entrar
  en cada `i` y se agrega a `C` al salir del bucle `j`.
- **Tamaño del resultado.** Hay m iteraciones de `i` y p de `j`, así que C es m×p.
- **Coste.** El cuerpo interno se ejecuta m·p·n veces, es decir O(m·n·p). Para
  matrices cuadradas n×n eso es O(n³).
- **`limpiar(suma)`** convierte en 0.0 cualquier resultado con |x| < EPS = 1e-10,
  así que no se imprime ruido de coma flotante ni `-0.0`.

## 4. Traza paso a paso: A(2×3) · B(3×2)

```
A = [ 1  2  3 ]        B = [  7   8 ]
    [ 4  5  6 ]            [  9  10 ]
                           [ 11  12 ]
```

m = 2, n = 3, p = 2 ⇒ C es 2×2 y hay 2·2·3 = 12 multiplicaciones.
En la traza los índices se escriben en base 1 (igual que en el álgebra); en
Python son `i-1`, `j-1`, `k-1`.

### i = 1 (fila 1 de A = [1, 2, 3])

**j = 1** (columna 1 de B = [7, 9, 11]), `suma = 0`

| k | a₁ₖ | bₖ₁ | a₁ₖ·bₖ₁ | suma acumulada |
|---|---|---|---|---|
| 1 | 1 | 7  | 7  | 7  |
| 2 | 2 | 9  | 18 | 25 |
| 3 | 3 | 11 | 33 | **58** |

c₁₁ = 58 → `fila_c = [58]`

**j = 2** (columna 2 de B = [8, 10, 12]), `suma = 0`

| k | a₁ₖ | bₖ₂ | a₁ₖ·bₖ₂ | suma acumulada |
|---|---|---|---|---|
| 1 | 1 | 8  | 8  | 8  |
| 2 | 2 | 10 | 20 | 28 |
| 3 | 3 | 12 | 36 | **64** |

c₁₂ = 64 → `fila_c = [58, 64]` → `C = [[58, 64]]`

### i = 2 (fila 2 de A = [4, 5, 6])

**j = 1** (columna 1 de B = [7, 9, 11]), `suma = 0`

| k | a₂ₖ | bₖ₁ | a₂ₖ·bₖ₁ | suma acumulada |
|---|---|---|---|---|
| 1 | 4 | 7  | 28 | 28  |
| 2 | 5 | 9  | 45 | 73  |
| 3 | 6 | 11 | 66 | **139** |

c₂₁ = 139 → `fila_c = [139]`

**j = 2** (columna 2 de B = [8, 10, 12]), `suma = 0`

| k | a₂ₖ | bₖ₂ | a₂ₖ·bₖ₂ | suma acumulada |
|---|---|---|---|---|
| 1 | 4 | 8  | 32 | 32  |
| 2 | 5 | 10 | 50 | 82  |
| 3 | 6 | 12 | 72 | **154** |

c₂₂ = 154 → `fila_c = [139, 154]` → `C = [[58, 64], [139, 154]]`

### Resultado

```
A·B = [  58   64 ]
      [ 139  154 ]
```

Coincide con la salida real del programa (opción 8).

## 5. Reutilización del producto en Ax = b

La opción 9 verifica la solución con la **misma** función. El vector x ∈ ℝⁿ se
convierte en una matriz columna n×1 (`vector_a_columna`) y se calcula
A(m×n)·X(n×1) = (m×1). En ese caso p = 1, así que el bucle `j` se ejecuta una
sola vez y cada fila del resultado es

```
(A·x)ᵢ = Σₖ aᵢₖ·xₖ
```

es decir, el lado izquierdo de la ecuación i. Ese resultado se compara
componente a componente con b usando la tolerancia EPS (`vectores_iguales`).
