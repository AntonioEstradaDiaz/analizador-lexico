"""Ventana principal y coordinación de los cinco módulos."""

import customtkinter as ctk

from ui import theme as t
from ui.components.sidebar import Sidebar
from ui.views.about_view import AboutView
from ui.views.analyzer_view import AnalyzerView
from ui.views.automata_view import AutomataView
from ui.views.rules_view import RulesView
from ui.views.tests_view import TestsView


class MainWindow(ctk.CTk):
    """Mantiene las cinco vistas en una sola ventana."""
    def __init__(self):
        """Configura la ventana, registra las vistas y abre el analizador."""
        super().__init__(fg_color=t.BG)
        t.configure()
        self.title("Analizador Lexico")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.grid(row=0, column=1, sticky="nsew", padx=22, pady=16)
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)
        self.factories = {
            "Analizador": AnalyzerView,
            "Autómata AFD": AutomataView,
            "Pruebas": lambda parent: TestsView(parent, self.open_case),
            "Reglas léxicas": RulesView,
            "Acerca de": AboutView,
        }
        self.views = {}
        self.current = None
        self.sidebar = Sidebar(self, tuple(self.factories), self.navigate)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.navigate("Analizador")
        self.protocol("WM_DELETE_WINDOW", self.close)

    # --- Navegación entre módulos y cierre ---

    def navigate(self, name: str) -> None:
        """Oculta la vista actual, detiene su reproducción si corresponde y abre la elegida."""
        if self.current == name:
            return
        if self.current is not None:
            previous = self.views[self.current]
            if isinstance(previous, AutomataView):
                previous.pause()
            previous.grid_remove()
        if name not in self.views:
            self.views[name] = self.factories[name](self.content)
        self.views[name].grid(row=0, column=0, sticky="nsew")
        self.current = name
        self.sidebar.select(name)

    def open_case(self, source: str) -> None:
        """Abre la entrada de una prueba en el analizador y la procesa."""
        self.navigate("Analizador")
        analyzer = self.views["Analizador"]
        analyzer.load_source(source)
        analyzer.run()

    def close(self) -> None:
        """Cancela los eventos programados antes de destruir la ventana."""
        self.sidebar.finish_animation()
        if "Autómata AFD" in self.views:
            self.views["Autómata AFD"].pause()
        self.destroy()
