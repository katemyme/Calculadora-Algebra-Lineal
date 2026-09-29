"""Módulo de Determinantes (lógica matemática en construcción)."""

from teoremas.resumen_teoremas import TEOREMAS

NUMERO_MODULO: int = 4

ARTE_ASCII: str = (
    "|a b| MÓDULO: DETERMINANTES\n"
    "|c d| det(A) = ad - bc, Cofactores y Regla de Cramer"
)


def iniciar_modulo() -> None:
    """Muestra el arte del módulo y ejecuta su menú interno."""
    print()
    print(ARTE_ASCII)
    print("\nLógica matemática en construcción")

    while True:
        print("\n  0. Ver Teoremas Clave")
        print("  1. Volver al menú principal")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            print("\n── TEOREMAS CLAVE ──")
            print(f"  {TEOREMAS[NUMERO_MODULO]}")
        elif opcion == "1":
            break
        else:
            print("Opción no válida. Intente de nuevo.")
