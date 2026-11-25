"""Tarjetas de cifras del análisis."""

import customtkinter as ctk

from ui import theme as t


class MetricCard(ctk.CTkFrame):
    """Muestra un indicador y su valor actual."""
    def __init__(self, parent, title: str, color: str = t.TEXT):
        """Construye el título y el valor inicial de la tarjeta."""
        super().__init__(parent, fg_color=t.PANEL, border_width=1,
                         border_color=t.BORDER, corner_radius=12)
        ctk.CTkLabel(self, text=title, text_color=t.MUTED, font=ctk.CTkFont(size=15)).pack(
            anchor="w", padx=14, pady=(8, 0))
        self.value = ctk.CTkLabel(self, text="—", text_color=color,
                                  font=ctk.CTkFont(size=24, weight="bold"))
        self.value.pack(anchor="w", padx=14, pady=(0, 8))

    def set(self, value: str) -> None:
        """Sustituye el valor visible por el texto calculado."""
        self.value.configure(text=value)
