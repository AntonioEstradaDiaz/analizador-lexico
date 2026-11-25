"""Navegación lateral y animación del módulo activo."""

import customtkinter as ctk

from ui import theme as t
from ui.components.icons import navigation_icon


class Sidebar(ctk.CTkFrame):
    """Presenta los accesos a los módulos y distingue la selección actual."""
    def __init__(self, parent, names: tuple[str, ...], navigate):
        """Crea la identidad visual, los botones y sus iconos."""
        super().__init__(parent, width=218, corner_radius=0, fg_color=t.SIDE)
        self.grid_propagate(False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(9, weight=1)
        ctk.CTkLabel(self, text="Analizador Lexico", text_color=t.TEXT,
                     font=ctk.CTkFont(size=20, weight="bold")).grid(
                         row=0, sticky="w", padx=18, pady=(26, 0))
        ctk.CTkLabel(self, text="Analizador léxico y\nsimulador de autómatas",
                     text_color=t.MUTED, justify="left", font=ctk.CTkFont(size=14)).grid(
                         row=1, sticky="w", padx=18, pady=(4, 26))
        self.buttons = {}
        self.icons = {}
        self.active: str | None = None
        self.animation_job: str | None = None
        for row, name in enumerate(names, 2):
            self.icons[name] = (navigation_icon(row - 2), navigation_icon(row - 2, t.ACCENT))
            action = t.button(self, name, lambda section=name: navigate(section),
                              anchor="w", image=self.icons[name][0], compound="left")
            action.grid(row=row, sticky="ew", padx=12, pady=3)
            self.buttons[name] = action
        ctk.CTkLabel(self, text="Unidad 6  ·  Versión 1.0.0", text_color=t.MUTED,
                     font=ctk.CTkFont(size=14)).grid(
            row=10, sticky="w", padx=18, pady=14)

    # --- Selección y transición de color ---

    def select(self, name: str) -> None:
        """Actualiza el icono y el borde de la selección y dispara su transición."""
        animate = self.active is not None
        self.finish_animation()
        self.active = name
        for section, action in self.buttons.items():
            active = section == name
            action.configure(fg_color=t.SELECT if active and not animate else t.SIDE,
                             image=self.icons[section][int(active)],
                             border_color=t.ACCENT if active else t.BORDER)
        if animate:
            self._animate_active(name, 1)

    def _animate_active(self, name: str, frame: int) -> None:
        """Pinta un fotograma y programa el siguiente hasta completar la transición."""
        self.animation_job = None
        self.buttons[name].configure(fg_color=t.blend(t.SIDE, t.SELECT, frame / 6))
        if frame < 6:
            self.animation_job = self.after(20, self._animate_active, name, frame + 1)

    def finish_animation(self) -> None:
        """Cancela un fotograma pendiente y aplica el color final."""
        if self.animation_job is not None:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        if self.active is not None:
            self.buttons[self.active].configure(fg_color=t.SELECT)
