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
    4: "En construcción",
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
}
