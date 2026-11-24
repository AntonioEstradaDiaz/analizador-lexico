import customtkinter as ctk

from ui import theme as t
from ui.views.rules_view import info_card

MEMBERS = (
    "PICHARDO TÉLLEZ IKER DONOVAN",
    "GARCIA CORTES JOSÉ ALBERTO",
    "ESTRADA DÍAZ ANTONIO",
    "GARZA ALBITER ARIEL",
    "ROJAS REYNOSO GAEL",
    "Martinez Gallardo Santiago",
)


class AboutView(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        t.heading(self, "Lexical Analyzer", "Versión 1.0.0 · Proyecto académico").pack(
            fill="x", pady=(0, 12))
        info_card(self, "Asignatura",
                  "Lenguajes y Autómatas I\n"
                  "Unidad 6 · Ingeniería en Sistemas Computacionales · Ciclo 2026")
        info_card(self, "Integrantes", "\n".join(MEMBERS))
        info_card(self, "Objetivo",
                  "Reconocer los lexemas de un lenguaje reducido, ubicar los errores "
                  "y mostrar cómo un AFD reconoce identificadores carácter por carácter.")
        info_card(self, "Tecnologías",
                  "Python, CustomTkinter, Tkinter Treeview y Canvas, expresiones regulares, "
                  "dataclasses, unittest y CSV. PyInstaller para empaquetado.")
