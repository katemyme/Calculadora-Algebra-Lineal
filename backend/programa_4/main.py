"""Programa 4 - Calculadora de Álgebra Lineal (interfaz de consola).

Ejecución (desde la carpeta programa_4):
    python3 main.py
"""

from modulos import (
    modulo_determinantes,
    modulo_lu,
    modulo_matrices,
    modulo_sistemas,
    modulo_vectores,
)

# PROGRAMA 7 necesita NumPy, SciPy y SymPy. Si faltan, el resto de la calculadora
# sigue funcionando y la opción 6 explica cómo instalarlas.
try:
    from modulos import modulo_metodos_numericos
except ModuleNotFoundError as error:
    _LIBRERIA_FALTANTE = error.name

    class modulo_metodos_numericos:  # noqa: N801 - sustituto con la misma interfaz
        """Sustituto de la opción 6 cuando faltan las librerías del Programa 7."""

        @staticmethod
        def iniciar_modulo() -> None:
            print(f"\nFalta la librería '{_LIBRERIA_FALTANTE}' para Métodos Numéricos.")
            print("Instálela con:  python -m pip install -r backend/requirements.txt")

# Opción del menú -> módulo que se abre (el número coincide con TEOREMAS).
MODULOS = {
    "1": modulo_sistemas,
    "2": modulo_vectores,
    "3": modulo_matrices,
    "4": modulo_determinantes,
    # PROGRAMA 6: Factorización LU y solución Ax = b.
    "5": modulo_lu,
    # PROGRAMA 7: Métodos Numéricos (Bisección, graficador, bases y errores).
    "6": modulo_metodos_numericos,
}


def mostrar_menu_principal() -> None:
    """Imprime el menú principal de la calculadora."""
    print()
    print("╔══════════════════════════════════════════╗")
    print("║      CALCULADORA DE ÁLGEBRA LINEAL       ║")
    print("╠══════════════════════════════════════════╣")
    print("║  1. Sistemas de Ecuaciones (SEL)         ║")
    print("║  2. Vectores e Independencia Lineal      ║")
    print("║  3. Álgebra de Matrices                  ║")
    print("║  4. Determinantes                        ║")
    print("║  5. Factorización LU y solución Ax = b   ║")
    print("║  6. Métodos Numéricos                    ║")
    print("║  0. Salir                                ║")
    print("╚══════════════════════════════════════════╝")


def main() -> None:
    """Bucle del menú principal."""
    while True:
        mostrar_menu_principal()
        opcion = input("Seleccione una opción: ").strip()

        if opcion in MODULOS:
            MODULOS[opcion].iniciar_modulo()
        elif opcion == "0":
            print("\n¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nPrograma finalizado por el usuario.")
