"""Expresiones regulares y categorías del alfabeto ASCII."""

import re

# --- Patrones de los cinco tokens ---

PATTERNS = {
    "IDENTIFICADOR": re.compile(r"[A-Za-z][A-Za-z0-9]*"),
    "ENTERO": re.compile(r"[0-9]+"),
    "ASIGNACIÓN": re.compile(r"="),
    "SUMA": re.compile(r"\+"),
    "FIN_SENTENCIA": re.compile(r";"),
}
# --- Límites de bloques y categorías para el AFD ---

BLOCK = re.compile(r"[A-Za-z0-9]+")
LETTER = re.compile(r"[A-Za-z]")
DIGIT = re.compile(r"[0-9]")
SYMBOLS = {"=": "ASIGNACIÓN", "+": "SUMA", ";": "FIN_SENTENCIA"}
