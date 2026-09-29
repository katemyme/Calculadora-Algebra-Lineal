"""Módulo de Álgebra de Matrices (lógica matemática en construcción)."""

from teoremas.resumen_teoremas import TEOREMAS

NUMERO_MODULO: int = 3

ARTE_ASCII: str = (
    "[A][B] MÓDULO: ÁLGEBRA DE MATRICES\n"
    "[C][D] Operaciones, Traspuesta y Matriz Inversa"
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
