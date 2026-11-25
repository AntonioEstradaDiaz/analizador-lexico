"""Controles, historial y estado de la simulación del AFD."""

import tkinter as tk
from tkinter import font

import customtkinter as ctk

from core.afd import ACCEPTING, CATEGORIES, INITIAL, TRANSITIONS, trace
from core.models import AutomataStep
from ui import theme as t
from ui.components.automata_canvas import AutomataCanvas
from ui.components.token_table import DataTable


class AutomataView(ctk.CTkFrame):
    """Permite recorrer un identificador manualmente o con reproducción automática."""
    def __init__(self, parent):
        """Configura el estado inicial, el lienzo, los controles y las tablas."""
        super().__init__(parent, fg_color="transparent")
        self.steps: list[AutomataStep] = []
        self.position = 0
        self.timer: str | None = None
        self.started = False
        self.columnconfigure(0, weight=1)
        self.rowconfigure(5, weight=1)
        t.heading(self, "Autómata AFD", "Reconoce identificadores · [A-Za-z][A-Za-z0-9]*").grid(
            row=0, sticky="ew", pady=(0, 12))
        self.source = tk.StringVar(self)
        self._build_controls()
        self.canvas = AutomataCanvas(self)
        self.canvas.grid(row=3, sticky="nsew", pady=(9, 4))
        self.detail = ctk.CTkLabel(self, anchor="w", text_color=t.TEXT,
                                   font=ctk.CTkFont(size=15))
        self.detail.grid(row=4, sticky="ew")
        self._build_tables()
        self.status = ctk.CTkLabel(self, anchor="w", text_color=t.MUTED,
                                   font=ctk.CTkFont(size=15))
        self.status.grid(row=6, sticky="ew", pady=(5, 0))
        self.source.trace_add("write", self._invalidate)
        self._render()

    # --- Controles y tabla de transiciones ---

    def _build_controls(self) -> None:
        """Organiza la entrada, los ejemplos rápidos y los controles de recorrido."""
        inputs = ctk.CTkFrame(self, fg_color="transparent")
        inputs.grid(row=1, sticky="ew")
        inputs.columnconfigure(0, weight=1)
        entry = ctk.CTkEntry(inputs, textvariable=self.source, height=34,
                             font=(font.nametofont("TkFixedFont").actual("family"), 14),
                             border_color=t.INPUT_BORDER, fg_color=t.PANEL,
                             validate="key", validatecommand=(self.register(self._one_line), "%P"))
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        entry.bind("<Return>", lambda event: self.start())
        t.button(inputs, "Iniciar", self.start, primary=True, width=76).grid(row=0, column=1)
        for index, example in enumerate(("A", "Total2", "9abc"), 2):
            t.button(inputs, example, lambda value=example: self.load(value), width=60).grid(
                row=0, column=index, padx=(6, 0))

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=2, sticky="ew", pady=(8, 0))
        controls.columnconfigure(6, weight=1)
        self.actions = {}
        for column, (label, action) in enumerate((
            ("Anterior", self.previous), ("Siguiente", self.next),
            ("Reproducir", self.play), ("Pausar", self.pause), ("Reiniciar", self.start)
        )):
            button = t.button(controls, label, action, width=84)
            button.grid(row=0, column=column, padx=(0, 6))
            self.actions[label] = button
        self.speed_label = ctk.CTkLabel(controls, text="700 ms/paso", text_color=t.MUTED)
        self.speed_label.grid(row=0, column=5, padx=(6, 4))
        self.speed = ctk.CTkSlider(controls, from_=150, to=1500, number_of_steps=27,
                                   progress_color=t.SELECT, button_color=t.PRIMARY,
                                   button_hover_color=t.ACCENT,
                                   command=lambda value: self.speed_label.configure(
                                       text=f"{int(value)} ms/paso"))
        self.speed.set(700)
        self.speed.grid(row=0, column=6, sticky="ew", padx=(4, 0))

    @staticmethod
    def _one_line(value: str) -> bool:
        """Restringe el editor del simulador a una sola línea."""
        return "\n" not in value and "\r" not in value

    def _build_tables(self) -> None:
        """Presenta el historial y la tabla que define las transiciones."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=5, sticky="nsew")
        frame.columnconfigure((0, 1), weight=1)
        frame.rowconfigure(1, weight=1)
        for column, title in enumerate(("Historial de transiciones", "Tabla de transiciones")):
            ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=16, weight="bold")).grid(
                row=0, column=column, sticky="w", padx=(0 if column == 0 else 8, 0))
        self.history = DataTable(frame, (
            ("Posición", 68), ("Carácter", 75), ("Desde", 58),
            ("Categoría", 80), ("Hasta", 52)), height=3)
        self.history.grid(row=1, column=0, sticky="nsew")
        self.matrix = DataTable(frame, (("Estado", 65), *((c, 65) for c in CATEGORIES)), height=3)
        self.matrix.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        for state, edges in TRANSITIONS.items():
            self.matrix.add((state, *edges.values()))

    # --- Preparación y recorrido manual ---

    def load(self, value: str) -> None:
        """Carga un ejemplo e inicializa su recorrido."""
        self.source.set(value)
        self.start()

    def _invalidate(self, *_args) -> None:
        """Descarta el recorrido anterior cuando cambia la cadena."""
        self.pause()
        self.started = False
        self.steps = []
        self.position = 0
        self.history.clear()
        self._render()

    def start(self) -> None:
        """Calcula las transiciones desde q0 y muestra el punto de partida."""
        self.pause()
        self.steps = trace(self.source.get())
        self.started = True
        self.position = 0
        self.history.clear()
        self._render()

    def _advance(self, direction: int) -> None:
        """Mueve el cursor un paso y actualiza el historial visible."""
        target = self.position + direction
        if not self.started or not 0 <= target <= len(self.steps):
            return
        if direction > 0:
            step = self.steps[self.position]
            key = self.history.add((step.position, repr(step.character), step.previous,
                                    step.category, step.following), key=str(target))
            self.history.tree.see(key)
        else:
            self.history.tree.delete(str(self.position))
            if target:
                self.history.tree.see(str(target))
        self.position = target
        self._render()

    def next(self) -> None:
        """Pausa la reproducción y ejecuta la transición siguiente."""
        self.pause()
        self._advance(1)

    def previous(self) -> None:
        """Pausa la reproducción y retrocede una transición."""
        self.pause()
        self._advance(-1)

    # --- Reproducción automática ---

    def play(self) -> None:
        """Programa el siguiente paso con el intervalo elegido."""
        if self.timer is None and self.started and self.position < len(self.steps):
            self.timer = self.after(int(self.speed.get()), self._tick)
            self._sync_buttons()

    def _tick(self) -> None:
        """Ejecuta un paso automático y vuelve a programar si quedan caracteres."""
        self.timer = None
        self._advance(1)
        self.play()

    def pause(self) -> None:
        """Cancela el temporizador y sincroniza los controles."""
        if self.timer is not None:
            self.after_cancel(self.timer)
            self.timer = None
        self._sync_buttons()

    # --- Estado de los controles y presentación ---

    def _sync_buttons(self) -> None:
        """Habilita los controles aplicables al punto actual del recorrido."""
        remaining = self.started and self.position < len(self.steps)
        for label, enabled in (
            ("Anterior", self.position > 0), ("Siguiente", remaining),
            ("Reproducir", remaining and self.timer is None),
            ("Pausar", self.timer is not None), ("Reiniciar", self.started)
        ):
            self.actions[label].configure(state="normal" if enabled else "disabled")

    def _render(self) -> None:
        """Actualiza el lienzo, los detalles y el resultado de aceptación."""
        step = self.steps[self.position - 1] if self.position else None
        state = step.following if step else INITIAL
        self.canvas.show(state, step)
        detail = f"Estado inicial {INITIAL} · Posición 0 de {len(self.steps)}"
        if step:
            detail = (f"Carácter {step.character!r} · Posición {step.position} de {len(self.steps)}"
                      f" · Estado anterior {step.previous} · Estado siguiente {step.following}")
        self.detail.configure(text=detail)
        if not self.started:
            status, color = "Introduce una cadena o elige un ejemplo", t.MUTED
        elif self.position < len(self.steps):
            status, color = "Simulación en curso", t.ACCENT
        elif state == ACCEPTING:
            status, color = "Cadena aceptada como identificador", t.SUCCESS
        else:
            status, color = "Cadena rechazada como identificador", t.ERROR
        self.status.configure(text=status, text_color=color)
        self._sync_buttons()
