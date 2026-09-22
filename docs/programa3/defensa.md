# Programa 3 — Preguntas probables de defensa

### 1. ¿Por qué el producto matricial necesita tres bucles y qué recorre cada uno?

`i` recorre las filas de A (fila de C que se llena), `j` recorre las columnas de
B (columna de C que se llena) y `k` recorre a la vez la fila i de A y la columna
j de B para acumular `cᵢⱼ = Σₖ aᵢₖ·bₖⱼ`. Con dos bucles solo se puede ubicar la
celda cᵢⱼ; el tercero calcula el producto punto que la llena. Coste: m·n·p
multiplicaciones (O(n³) para matrices cuadradas).

### 2. ¿Qué pasa si columnas(A) ≠ filas(B)?

El producto no está definido, porque `A[i][k]` y `B[k][j]` usan el mismo `k` y
las longitudes no coinciden. `opcion_producto_matrices` lo detecta en cuanto se
leen las dimensiones: muestra, por ejemplo, "A es 2×3 y B es 2×2" y vuelve al menú
sin pedir los datos. Además, `producto_matrices` vuelve a comprobarlo con
`producto_compatible` y devuelve `None`, así que la función es segura aunque se
llame desde otro sitio.

### 3. ¿Cómo decide el programa si b es combinación lineal de v₁, …, vₖ?

`c₁·v₁ + ⋯ + cₖ·vₖ = b` es un sistema lineal cuya matriz tiene los vectores como
**columnas**. `aumentada_desde_columnas` arma `[v₁ … vₖ | b]` y se aplica
Gauss-Jordan (`escalonar`):
- si aparece una fila `0 ⋯ 0 | k` con k ≠ 0, el sistema es inconsistente y b no es combinación lineal;
- si hay pivote en todas las columnas, los pesos son únicos;
- si hay columnas sin pivote, hay infinitos pesos: se muestra la solución general
  y la combinación con las variables libres = 0.

### 4. ¿Por qué los vectores van como columnas y no como filas?

En `c₁·v₁ + c₂·v₂ = b`, la ecuación de la componente i es
`c₁·(v₁)ᵢ + c₂·(v₂)ᵢ = bᵢ`. Los coeficientes de la incógnita cⱼ son las
componentes de vⱼ, así que vⱼ tiene que ocupar la columna j. Si se pusieran como
filas se resolvería otro sistema (con la matriz traspuesta), que responde a otra
pregunta.

### 5. ¿Cómo clasifica el sistema Ax = b?

Con Rouché-Frobenius sobre la RREF (`calcular_rangos` y `clasificar`):
rango(A) = número de columnas pivote; rango(A|b) = rango(A) + 1 si existe una fila
contradictoria.
- rango(A) < rango(A|b) → inconsistente;
- rango(A) = rango(A|b) = n → única;
- rango(A) = rango(A|b) < n → infinitas, con n − rango variables libres.

### 6. ¿Por qué se usa EPS = 1e-10 y cómo se evita imprimir -0.0?

Con `float`, operaciones como 0.1 + 0.2 no dan resultados exactos, así que un
pivote que debería ser 0 puede quedar en 1e-17. `es_cero(x)` considera cero
cualquier |x| < EPS. Así se decide si hay pivote, si hay que anular un elemento,
si una fila es contradictoria y si A·x coincide con b. `limpiar(x)` devuelve
`0.0` en esos casos (nunca `-0.0`) y `formatear_numero` escribe `"0"`. Por eso
−1·0 se muestra como `0`.

### 7. ¿Qué cambió respecto al Gauss-Jordan del Programa 2?

La lógica es la misma: pivoteo parcial, intercambio Fᵢ ↔ Fⱼ, normalización
Fᵢ → (1/p)·Fᵢ y eliminación arriba y abajo Fₖ → Fₖ − c·Fᵢ. El Programa 2 usaba
`fractions.Fraction`, que aquí está prohibido, así que la función se copió
adaptada a `float`:
1. cada `== 0` pasa a ser `es_cero(...)`;
2. tras normalizar, el pivote se fija en `1.0` exacto y el elemento anulado en `0.0`;
3. los residuos |x| < EPS se limpian después de cada operación.

Sin estos cambios, un residuo de 1e-16 podría tomarse como pivote y dar una
clasificación errónea. Además, el archivo es autocontenido: la función se copió, no se importó.

### 8. ¿Cómo se verifica la solución?

- **Ax = b:** x se convierte en una matriz columna n×1 y se calcula A·x con la
  **misma** `producto_matrices`; luego se compara con b componente a componente
  (`vectores_iguales`, con tolerancia EPS). Con infinitas soluciones se verifican
  dos: t = 0 (particular) y t = 1, lo que comprueba también el vector dirección.
- **Combinación lineal:** se recalcula Σ cᵢ·vᵢ con `escalar_por_vector` y
  `suma_vectores` y se compara con b.

En ambos casos se usan los datos originales y no la RREF, así que un error en la
eliminación se notaría en la verificación.

### Pregunta extra: ¿qué validaciones de entrada hay?

`leer_entero` repite la pregunta si el texto no es un entero o si la dimensión
es ≤ 0 (o > 8, el mismo límite del Programa 2). `leer_fila` exige exactamente la
cantidad de números pedida y repite la línea si alguno no es numérico.
`convertir_numero` acepta enteros, decimales y fracciones `a/b` y rechaza `1/0`,
`inf` y `nan`. El menú rechaza cualquier opción fuera de 0–9. Si la entrada se
termina (EOF), el programa cierra con un mensaje en lugar de fallar.
