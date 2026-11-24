import customtkinter as ctk

from core.patterns import PATTERNS
from ui import theme as t
from ui.components.token_table import DataTable


def info_card(parent, title: str, text: str) -> None:
    card = ctk.CTkFrame(parent, fg_color=t.PANEL, corner_radius=12,
                        border_color=t.BORDER, border_width=1)
    card.pack(fill="x", pady=(0, 8))
    ctk.CTkLabel(card, text=title, text_color=t.ACCENT,
                 font=ctk.CTkFont(size=15, weight="bold")).pack(
                     anchor="w", padx=14, pady=(9, 2))
    body = ctk.CTkLabel(card, text=text, justify="left", anchor="w", text_color=t.TEXT,
                        font=ctk.CTkFont(size=16))
    body.pack(fill="x", padx=14, pady=(0, 10))
    body.bind("<Configure>", lambda event: body.configure(wraplength=event.width))


class RulesView(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        t.heading(self, "Reglas léxicas", "Patrones, ejemplos y posiciones del lenguaje.").pack(
            fill="x", pady=(0, 12))
        table = DataTable(self, (("Tipo", 145), ("Patrón", 180),
                                 ("Ejemplos válidos", 140), ("Inválido para este tipo", 165)))
        table.pack(fill="x", pady=(0, 10))
        examples = (("A, Total2", "9abc"), ("0, 2026", "12x"),
                    ("=", "≠"), ("+", "-"), (";", ":"))
        for (kind, pattern), (valid, invalid) in zip(PATTERNS.items(), examples):
            table.add((kind, pattern.pattern, valid, invalid))
        info_card(self, "Patrón, lexema y token",
                  "Un patrón describe la forma de una categoría. Un lexema es el fragmento "
                  "concreto de la entrada. En Total2, el lexema corresponde a IDENTIFICADOR.")
        info_card(self, "Bloques ASCII y columnas",
                  "El recorrido va de izquierda a derecha. El motor consume todo bloque "
                  "alfanumérico ASCII antes de clasificarlo. 9abc produce un solo error. "
                  "Los caracteres ajenos al alfabeto se reportan por separado y el análisis continúa. "
                  "Las columnas comienzan en 1. Cada espacio y tabulación ocupa una columna.")
        info_card(self, "Análisis léxico, sintáctico y semántico",
                  "El análisis léxico reconoce tokens. El sintáctico verifica la estructura "
                  "de la secuencia. El semántico comprueba su significado. x=+; es léxicamente "
                  "válida porque cada símbolo pertenece al lenguaje.")
