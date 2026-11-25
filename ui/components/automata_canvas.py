"""Representación gráfica de estados y transiciones del AFD."""

import tkinter as tk

from core.models import AutomataStep
from ui import theme as t


class AutomataCanvas(tk.Canvas):
    """Dibuja el AFD y destaca el estado y la arista del paso actual."""
    def __init__(self, parent):
        """Configura el lienzo y redibuja el diagrama cuando cambia su tamaño."""
        super().__init__(parent, width=1, height=175, background=t.PANEL,
                         highlightthickness=1, highlightbackground=t.BORDER)
        self.active = "q0"
        self.step: AutomataStep | None = None
        self.bind("<Configure>", lambda event: self.draw())

    # --- Renderizado de estados ---

    def show(self, state: str, step: AutomataStep | None) -> None:
        """Guarda el paso activo y actualiza el dibujo."""
        self.active, self.step = state, step
        self.draw()

    def draw(self) -> None:
        """Distribuye los estados y aristas según las dimensiones del lienzo."""
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width < 350 or height < 120:
            return
        left, middle, right = width * .18, width * .50, width * .82
        y, radius = height * .60, 22
        self._edge((left - 66, y, left - radius, y), "", (0, 0))
        self._edge((left + radius, y, middle - radius, y), "Letra",
                   ((left + middle) / 2, y - 14), ("q0", "q1"))
        self._edge((middle + radius, y, right - radius, y), "Otro",
                   ((middle + right) / 2, y - 14), ("q1", "qR"))
        bottom = min(height - 21, y + 43)
        self._edge((left + 14, y + 17, left + 44, bottom, right - 44, bottom,
                    right - 14, y + 17), "Dígito u otro", (middle, bottom + 9),
                   ("q0", "qR"), smooth=True)
        self._loop(middle, y, "Letra o dígito", "q1")
        self._loop(right, y, "Cualquiera", "qR")

        for state, x in zip(("q0", "q1", "qR"), (left, middle, right)):
            outline = t.ERROR if state == "qR" else t.SUCCESS if state == "q1" else t.ACCENT
            active = state == self.active
            self.create_oval(x-radius, y-radius, x+radius, y+radius,
                             outline=outline, width=3 if active else 1,
                             fill=t.SELECT if active else t.SIDE)
            if state == "q1":
                self.create_oval(x-17, y-17, x+17, y+17, outline=outline)
            self.create_text(x, y, text=state, fill=t.TEXT, font=("TkDefaultFont", 10, "bold"))

    # --- Trazado de transiciones ---

    def _loop(self, x: float, y: float, label: str, state: str) -> None:
        """Dibuja la transición de un estado a sí mismo."""
        self._edge((x - 13, y - 17, x - 38, y - 58, x + 38, y - 58, x + 13, y - 17),
                   label, (x, y - 65), (state, state), smooth=True)

    def _edge(self, points: tuple, label: str, label_at: tuple,
              states: tuple[str, str] | None = None, smooth: bool = False) -> None:
        """Dibuja una flecha con su etiqueta y resalta la transición ejecutada."""
        active = self.step is not None and states == (self.step.previous, self.step.following)
        color = t.ACCENT if active else t.MUTED
        self.create_line(*points, arrow=tk.LAST, smooth=smooth,
                         width=3 if active else 1.5, fill=color)
        if label:
            self.create_text(*label_at, text=label, fill=color)
