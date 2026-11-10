"""Resumen de los teoremas clave de cada módulo de la calculadora.

Cada módulo muestra su entrada con la opción 0 «Ver Teoremas Clave». La clave 3
reúne los teoremas del Módulo III: transpuesta, inversa y determinante; la clave 5,
los de la Factorización LU (Programa 6).
Integrantes: Grupo X — completar.
"""

# Clave = número del módulo en el menú principal.
TEOREMAS: dict = {
    1: "En construcción",
    2: (
        "Teorema de Independencia Lineal: Un conjunto de k vectores en ℝⁿ es "
        "L.I. si y solo si la única solución a c₁v₁ + c₂v₂ + ... + cₖvₖ = 0 es "
        "la trivial (sin variables libres)."
    ),
    # Las líneas llevan su propia sangría porque el módulo imprime "  " + texto.
    3: (
        "TRANSPUESTA: (Aᵀ)ᵀ = A, (A + B)ᵀ = Aᵀ + Bᵀ, (rA)ᵀ = r·Aᵀ, (AB)ᵀ = BᵀAᵀ.\n"
        "  TEOREMA DE LA INVERSA (Sesión 10). Si A y B son invertibles de orden n:\n"
        "    (a) (A⁻¹)⁻¹ = A\n"
        "    (b) (AB)⁻¹ = B⁻¹A⁻¹  (el orden de los factores se invierte)\n"
        "    (c) (Aᵀ)⁻¹ = (A⁻¹)ᵀ\n"
        "  TEOREMA DE LA MATRIZ INVERTIBLE (*). A de orden n es invertible ⇔\n"
        "    (c) A tiene n posiciones pivote\n"
        "    (e) las columnas de A son linealmente independientes (L.I.)\n"
        "    (h) las columnas de A generan ℝⁿ\n"
        "  DETERMINANTE E INVERSA. A es invertible ⇔ det(A) ≠ 0, y entonces\n"
        "    A⁻¹ = (1/det A)·adj(A)"
    ),
    # Regla de Cramer. Misma sangría que la clave 3: títulos con 2 espacios, enunciados con 4.
    4: (
        "REGLA DE CRAMER. Si A es de orden n e invertible (det A ≠ 0), para todo b en ℝⁿ "
        "la única solución x de Ax = b tiene entradas:\n"
        "    xᵢ = det Aᵢ(b) / det A,   i = 1, 2, …, n\n"
        "    Aᵢ(b) es la matriz A con su columna i reemplazada por el vector b\n"
        "  CUÁNDO NO SE APLICA.\n"
        "    Si det A = 0, A no es invertible y Ax = b no tiene solución única"
    ),
    # PROGRAMA 6. Misma sangría que la clave 3: títulos con 2 espacios, enunciados con 4.
    5: (
        "FACTORIZACIÓN LU (Programa 6). Si A (m×n) se reduce a una forma escalonada U "
        "solo con reemplazos Fᵢ → Fᵢ − ℓᵢⱼ·Fⱼ (sin intercambiar filas), entonces A = LU:\n"
        "    L es triangular inferior m×m con unos en la diagonal y guarda los "
        "multiplicadores ℓᵢⱼ = (entrada a eliminar)/(pivote)\n"
        "    U es la forma escalonada de A (m×n)\n"
        "  SOLUCIÓN DE Ax = b CON A = LU. Como Ax = L(Ux) = b, con y = Ux se resuelve "
        "en dos etapas:\n"
        "    (1) Ly = b  por sustitución hacia adelante  →  vector intermedio y\n"
        "    (2) Ux = y  por sustitución hacia atrás     →  solución x\n"
        "  EXISTENCIA Y DETERMINANTE.\n"
        "    Si un pivote vale 0 y hay que intercambiar filas, A no admite LU sin "
        "permutación: se requiere pivoteo parcial PA = LU\n"
        "    Si A es n×n, det(A) = det(L)·det(U) = u₁₁·u₂₂·…·uₙₙ, porque det(L) = 1"
    ),
    # PROGRAMA 7. Misma sangría que la clave 3: títulos con 2 espacios, enunciados con 4.
    6: (
        "TEOREMA DE BOLZANO (valor intermedio). Si f es continua en [a, b] y "
        "f(a)·f(b) < 0, existe al menos un c ∈ (a, b) con f(c) = 0.\n"
        "    Sin continuidad no aplica: 1/x cambia de signo en [−1, 1] y no tiene raíz\n"
        "    Sin cambio de signo no se concluye nada: puede haber 0, 2, 4… raíces\n"
        "  MÉTODO DE BISECCIÓN.\n"
        "    xr = (a + b)/2 y cota del error Eb = (b − a)/2; se conserva la mitad con cambio de signo\n"
        "    Tras n iteraciones Eb = (b₀ − a₀)/2ⁿ, así que n_min = ⌈log₂((b₀ − a₀)/E)⌉\n"
        "  PUNTO FLOTANTE (IEEE 754, double).\n"
        "    52 bits de mantisa: épsilon de máquina = 2⁻⁵² ≈ 2.22·10⁻¹⁶\n"
        "    0.1 no tiene representación binaria finita: 0.1 + 0.2 ≠ 0.3"
    ),
}
