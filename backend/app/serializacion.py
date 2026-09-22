"""Conversión entre `fractions.Fraction` y estructuras JSON.

Este módulo NO hace aritmética matricial. Solo traduce el resultado exacto
que produce `nucleo.py` a un formato que viaja bien por HTTP y que el
frontend puede pintar sin volver a calcular nada.

Todo número que sale del backend se serializa como:

    { "fraccion": "3/4", "decimal": 0.75, "es_entero": false }

- `fraccion` conserva el valor EXACTO (es lo que se muestra al usuario).
- `decimal` es una aproximación de apoyo (nunca se usa para calcular).
- `es_entero` permite al frontend decidir el formato sin operar.
"""

from fractions import Fraction
from typing import Any, Dict


def serializar_fraccion(valor: Fraction) -> Dict[str, Any]:
    """Traduce una fracción exacta a su representación JSON de tres campos."""
    es_entero = valor.denominator == 1
    if es_entero:
        texto = str(valor.numerator)
    else:
        texto = f"{valor.numerator}/{valor.denominator}"
    return {
        "fraccion": texto,
        "decimal": float(valor),   # solo apoyo visual, jamás entrada de cálculo
        "es_entero": es_entero,
    }


def serializar(objeto: Any) -> Any:
    """Recorre recursivamente el resultado y convierte cada `Fraction`.

    Listas y diccionarios se copian con sus elementos ya serializados; los
    tipos simples (str, int, bool, None) se devuelven tal cual.
    """
    if isinstance(objeto, Fraction):
        return serializar_fraccion(objeto)
    if isinstance(objeto, dict):
        return {clave: serializar(valor) for clave, valor in objeto.items()}
    if isinstance(objeto, list):
        return [serializar(elemento) for elemento in objeto]
    return objeto
