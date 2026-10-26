"""Sprint 2 - Tarea 3 (Facundo): validaciones y cálculo de regularidad.

Reglas:
  - La nota debe ser un número entre 1 y 10 (ambos incluidos).
  - nota >= 6  -> "Regular"
  - nota <  6  -> "Libre"
"""
import math

NOTA_MINIMA = 1
NOTA_MAXIMA = 10
NOTA_REGULAR = 6

REGULAR = "Regular"
LIBRE = "Libre"


def validar_nota(valor):
    """Valida una nota recibida (normalmente un string del formulario).

    Devuelve (True, nota_numerica) si es válida,
    o (False, mensaje_de_error) si no lo es.
    """
    if valor is None or isinstance(valor, bool):
        return False, "La nota es obligatoria."

    if isinstance(valor, str):
        texto = valor.strip().replace(",", ".")
        if texto == "":
            return False, "La nota es obligatoria."
        try:
            numero = float(texto)
        except ValueError:
            return False, "La nota debe ser un número (no se permiten letras)."
    elif isinstance(valor, (int, float)):
        numero = float(valor)
    else:
        return False, "La nota debe ser un número."

    if math.isnan(numero) or math.isinf(numero):
        return False, "La nota debe ser un número válido."

    if numero < NOTA_MINIMA or numero > NOTA_MAXIMA:
        return False, f"La nota debe estar entre {NOTA_MINIMA} y {NOTA_MAXIMA}."

    if numero.is_integer():
        numero = int(numero)
    return True, numero


def calcular_regularidad(nota):
    """Devuelve "Regular" (nota >= 6) o "Libre" (nota < 6).

    Lanza ValueError si la nota no es válida.
    """
    valida, resultado = validar_nota(nota)
    if not valida:
        raise ValueError(resultado)
    return REGULAR if resultado >= NOTA_REGULAR else LIBRE


def evaluar_nota(valor):
    """Valida la nota y calcula la regularidad en un solo paso.

    Devuelve (True, nota, regularidad) si es válida,
    o (False, None, mensaje_de_error) si no lo es.
    """
    valida, resultado = validar_nota(valor)
    if not valida:
        return False, None, resultado
    return True, resultado, calcular_regularidad(resultado)
