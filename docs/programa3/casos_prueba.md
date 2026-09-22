# Programa 3 — Casos de prueba (guía para capturas)

Ejecutar desde la raíz del repositorio:

```
python "programas/Programa 3_GrupoX.py"
```

En cada caso, escriba **una línea por renglón** de la columna "Teclear" y pulse
Enter. Los números de una misma fila o vector se separan con espacios (también
se aceptan comas). Para decimales use punto (`2.5`); también se aceptan
fracciones (`1/3`). Al terminar cada caso vuelve el menú; escriba `0` para salir.

Todas las salidas mostradas abajo se obtuvieron ejecutando el programa real.

> Si redirige la salida a un archivo en Windows (`> salida.txt`), ejecute antes
> `set PYTHONIOENCODING=utf-8` (cmd) o `$env:PYTHONIOENCODING="utf-8"`
> (PowerShell) para que se guarden bien los subíndices. En la consola normal no
> hace falta.

---

## Caso 1 — Producto de matrices correcto

| Pregunta | Teclear |
|---|---|
| Elija una opción | `8` |
| Filas de A | `2` |
| Columnas de A | `3` |
| Filas de B | `3` |
| Columnas de B | `2` |
| A · Fila 1 | `1 2 3` |
| A · Fila 2 | `4 5 6` |
| B · Fila 1 | `7 8` |
| B · Fila 2 | `9 10` |
| B · Fila 3 | `11 12` |

Salida esperada:

```
  A (2×3) =
    [ 1 2 3 ]
    [ 4 5 6 ]
  B (3×2) =
    [  7  8 ]
    [  9 10 ]
    [ 11 12 ]
  A·B (2×2) =
    [  58  64 ]
    [ 139 154 ]
```

## Caso 2 — Producto con dimensiones incompatibles

| Pregunta | Teclear |
|---|---|
| Elija una opción | `8` |
| Filas de A | `2` |
| Columnas de A | `3` |
| Filas de B | `2` |
| Columnas de B | `2` |

Salida esperada (no pide los datos y no opera):

```
  ✘ Error: A es 2×3 y B es 2×2. columnas(A) = 3 ≠ filas(B) = 2: el producto A·B no está definido.
```

## Caso 3 — Suma de matrices con dimensiones distintas

| Pregunta | Teclear |
|---|---|
| Elija una opción | `5` |
| Filas de A | `2` |
| Columnas de A | `2` |
| Filas de B | `3` |
| Columnas de B | `2` |

Salida esperada:

```
  ✘ Error: A es 2×2 y B es 3×2. Para sumar o restar ambas deben tener el mismo orden m×n.
```

## Caso 4 — Combinación lineal: SÍ (única)

v₁ = (1, −2, −5), v₂ = (2, 5, 6), b = (7, 4, −3)

| Pregunta | Teclear |
|---|---|
| Elija una opción | `4` |
| Dimensión n de los vectores | `3` |
| Cantidad k de vectores | `2` |
| v₁ | `1 -2 -5` |
| v₂ | `2 5 6` |
| b | `7 4 -3` |

Salida esperada (final; antes aparecen los 8 pasos de Gauss-Jordan):

```
  RREF =
    [ 1 0 | 3 ]
    [ 0 1 | 2 ]
    [ 0 0 | 0 ]
  Columnas pivote: 1, 2
  rango(A) = 2, rango(A|b) = 2
  Clasificación: Sistema Consistente Determinado
    rango(A) = rango(A|b) = 2 = n: solución única.

  RESULTADO: b SÍ es combinación lineal (pesos únicos).
    c₁ = 3
    c₂ = 2
    b = 3·v₁ + 2·v₂

  Verificación:
    Σ cᵢ·vᵢ = (7, 4, -3)
    b       = (7, 4, -3)
    ✔ Coinciden: la combinación es correcta.
```

## Caso 5 — Combinación lineal: NO

v₁ = (1, 0, 0), v₂ = (0, 1, 0), b = (0, 0, 1)

| Pregunta | Teclear |
|---|---|
| Elija una opción | `4` |
| Dimensión n de los vectores | `3` |
| Cantidad k de vectores | `2` |
| v₁ | `1 0 0` |
| v₂ | `0 1 0` |
| b | `0 0 1` |

Salida esperada:

```
  Procedimiento (Gauss-Jordan):
    (la matriz ya estaba en forma escalonada reducida)

  RREF =
    [ 1 0 | 0 ]
    [ 0 1 | 0 ]
    [ 0 0 | 1 ]
  Columnas pivote: 1, 2
  rango(A) = 2, rango(A|b) = 3
  Clasificación: Sistema Inconsistente
    rango(A) = 2 < rango(A|b) = 3: aparece 0 = k con k ≠ 0.

  RESULTADO: b NO es combinación lineal de los vectores dados.
    La fila 3 de la RREF dice 0 = 1.
```

## Caso 6 — Combinación lineal: infinitas formas

v₁ = (1, 1), v₂ = (2, 2), v₃ = (0, 1), b = (3, 4)

| Pregunta | Teclear |
|---|---|
| Elija una opción | `4` |
| Dimensión n de los vectores | `2` |
| Cantidad k de vectores | `3` |
| v₁ | `1 1` |
| v₂ | `2 2` |
| v₃ | `0 1` |
| b | `3 4` |

Salida esperada:

```
  Procedimiento (Gauss-Jordan):
    1. F₂ → F₂ - F₁
        [ 1 2 0 | 3 ]
        [ 0 0 1 | 1 ]

  RREF =
    [ 1 2 0 | 3 ]
    [ 0 0 1 | 1 ]
  Columnas pivote: 1, 3
  rango(A) = 2, rango(A|b) = 2
  Clasificación: Sistema Consistente Indeterminado
    rango(A) = rango(A|b) = 2 < n = 3: infinitas soluciones con 1 variable(s) libre(s).

  RESULTADO: b SÍ es combinación lineal (infinitas formas).
  Variables básicas: c₁, c₃
  Variables libres:  c₂

  Solución general (forma paramétrica):
    c₁ = 3 - 2t
    c₂ = t   (libre)
    c₃ = 1

  Forma vectorial:
    c = (3, 0, 1) + t·(-2, 1, 0)

  Combinación particular (variables libres = 0):
    b = 3·v₁ + 0·v₂ + 1·v₃

  Verificación:
    Σ cᵢ·vᵢ = (3, 4)
    b       = (3, 4)
    ✔ Coinciden: la combinación es correcta.
```

## Caso 7 — Ax = b con solución única

```
 2x₁ +  x₂ -  x₃ =   8
-3x₁ -  x₂ + 2x₃ = -11
-2x₁ +  x₂ + 2x₃ =  -3
```

| Pregunta | Teclear |
|---|---|
| Elija una opción | `9` |
| Filas de A | `3` |
| Columnas de A | `3` |
| Fila 1 | `2 1 -1` |
| Fila 2 | `-3 -1 2` |
| Fila 3 | `-2 1 2` |
| b | `8 -11 -3` |

Salida esperada (final; antes aparecen 11 pasos de Gauss-Jordan con pivoteo parcial):

```
  RREF =
    [ 1 0 0 |  2 ]
    [ 0 1 0 |  3 ]
    [ 0 0 1 | -1 ]
  Columnas pivote: 1, 2, 3
  rango(A) = 3, rango(A|b) = 3
  Clasificación: Sistema Consistente Determinado
    rango(A) = rango(A|b) = 3 = n: solución única.

  RESULTADO: solución única.
    x₁ = 2
    x₂ = 3
    x₃ = -1

  Verificación:
    x   = (2, 3, -1)
    A·x = (8, -11, -3)
    b   = (8, -11, -3)
    ✔ A·x = b
```

## Caso 8 — Ax = b con infinitas soluciones

```
 x₁ + 2x₂ +  x₃ = 4
2x₁ + 4x₂ + 3x₃ = 9
```

| Pregunta | Teclear |
|---|---|
| Elija una opción | `9` |
| Filas de A | `2` |
| Columnas de A | `3` |
| Fila 1 | `1 2 1` |
| Fila 2 | `2 4 3` |
| b | `4 9` |

Salida esperada:

```
  RREF =
    [ 1 2 0 | 3 ]
    [ 0 0 1 | 1 ]
  Columnas pivote: 1, 3
  rango(A) = 2, rango(A|b) = 2
  Clasificación: Sistema Consistente Indeterminado
    rango(A) = rango(A|b) = 2 < n = 3: infinitas soluciones con 1 variable(s) libre(s).

  RESULTADO: infinitas soluciones.
  Variables básicas: x₁, x₃
  Variables libres:  x₂

  Solución general (forma paramétrica):
    x₁ = 3 - 2t
    x₂ = t   (libre)
    x₃ = 1

  Forma vectorial:
    x = (3, 0, 1) + t·(-2, 1, 0)

  Verificación (solución particular, t = 0):
    x   = (3, 0, 1)
    A·x = (4, 9)
    b   = (4, 9)
    ✔ A·x = b
  Verificación (t = 1):
    x   = (1, 1, 1)
    A·x = (4, 9)
    b   = (4, 9)
    ✔ A·x = b
```

## Caso 9 — Ax = b inconsistente

```
 x₁ +  x₂ = 2
2x₁ + 2x₂ = 5
```

| Pregunta | Teclear |
|---|---|
| Elija una opción | `9` |
| Filas de A | `2` |
| Columnas de A | `2` |
| Fila 1 | `1 1` |
| Fila 2 | `2 2` |
| b | `2 5` |

Salida esperada:

```
  RREF =
    [ 1 1 |  2.5 ]
    [ 0 0 | -0.5 ]
  Columnas pivote: 1
  rango(A) = 1, rango(A|b) = 2
  Clasificación: Sistema Inconsistente
    rango(A) = 1 < rango(A|b) = 2: aparece 0 = k con k ≠ 0.

  RESULTADO: el sistema NO tiene solución.
    La fila 2 de la RREF dice 0 = -0.5.
```

(Con pivoteo parcial la fila 2, que tiene el mayor pivote, sube primero; por eso
la RREF muestra 2.5 y −0.5 en lugar de 2 y 1. Ambas formas son equivalentes.)

## Caso 10 — Opción inválida en el menú

| Pregunta | Teclear |
|---|---|
| Elija una opción | `x` |
| Elija una opción | `12` |
| Elija una opción | *(Enter sin escribir nada)* |
| Elija una opción | `0` |

Salida esperada:

```
  ✘ Opción inválida: 'x'. Elija un número del 0 al 9.
  ✘ Opción inválida: '12'. Elija un número del 0 al 9.
  ✘ Opción inválida: ''. Elija un número del 0 al 9.
  ¡Hasta luego!
```

## Caso 11 — Datos inválidos (dimensión y componentes)

| Pregunta | Teclear | Qué ocurre |
|---|---|---|
| Elija una opción | `1` | |
| Dimensión de u | `abc` | ✘ 'abc' no es un entero. Intente de nuevo. |
| Dimensión de u | `0` | ✘ La dimensión debe ser mayor que 0 (se recibió 0). |
| Dimensión de u | `-2` | ✘ La dimensión debe ser mayor que 0 (se recibió -2). |
| Dimensión de u | `2.5` | ✘ '2.5' no es un entero. Intente de nuevo. |
| Dimensión de u | `3` | aceptado |
| u (3 componentes) | `1 2` | ✘ Se esperaban 3 número(s) y se recibieron 2. … |
| u (3 componentes) | `1 dos 3` | ✘ 'dos' no es un número válido. Repita la línea. |
| u (3 componentes) | `1 2 3` | aceptado |
| Dimensión de v | `3` | |
| v (3 componentes) | `4 5 6` | |

Salida final:

```
  u = (1, 2, 3)
  v = (4, 5, 6)
  u + v = (5, 7, 9)
```

## Caso 12 — Escalar inválido

| Pregunta | Teclear | Qué ocurre |
|---|---|---|
| Elija una opción | `3` | |
| Escalar c | `hola` | ✘ 'hola' no es un número válido. Intente de nuevo. |
| Escalar c | `1/0` | ✘ '1/0' no es un número válido. Intente de nuevo. |
| Escalar c | `-1` | aceptado |
| Dimensión de v | `2` | |
| v (2 componentes) | `0 1.5` | |

Salida esperada (observe que −1·0 se imprime `0`, no `-0.0`):

```
  -1·(0, 1.5) = (0, -1.5)
```

## Caso extra — Resta de vectores con dimensiones distintas

Teclear: `2`, `2`, `1 2`, `3`, `1 2 3`

```
  ✘ Error: u ∈ ℝ^2 y v ∈ ℝ^3 tienen dimensiones distintas; no se puede operar.
```
