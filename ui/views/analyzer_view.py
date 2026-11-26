"""Editor multilínea, resultados y exportación del análisis."""

import tkinter as tk
from tkinter import filedialog, font, messagebox

import customtkinter as ctk

from core.lexer import analyze
from core.models import AnalysisResult, Status
from core.patterns import RESERVED_KIND
from services.export_service import ANALYSIS_HEADERS, analysis_rows, export_analysis
from ui import theme as t
from ui.components.metric_card import MetricCard
from ui.components.token_table import DataTable

# --- Ejemplos precargados y colores por tipo ---

EXAMPLES = {
    "Asignación y suma": "Total2=15+3;",
    "Entrada con errores": "a=9abc+@;",
    "Espacios y tabulaciones": "a\t=\t5;",
    "Operadores consecutivos": "x=+;",
    "Palabras reservadas": "if while int if2 Int",
    "Varias líneas": "int total=15;\n\tif total+@;",
    "Entrada vacía": "",
}
COLORS = dict(zip(("IDENTIFICADOR", "ENTERO", "ASIGNACIÓN", "SUMA", "FIN_SENTENCIA"),
                  (t.ACCENT, t.SUCCESS, "#93C5FD", t.WARNING, t.MUTED)))
COLORS[RESERVED_KIND] = "#F9A8D4"


class AnalyzerView(ctk.CTkFrame):
    """Coordina la edición, el motor léxico y la presentación de resultados."""
    def __init__(self, parent):
        """Organiza el editor, las métricas, las tablas y las acciones."""
        super().__init__(parent, fg_color="transparent")
        self.result: AnalysisResult | None = None
        self.source = ""
        self.columnconfigure(0, weight=1)
        self.rowconfigure((3, 4), weight=1, uniform="results")
        t.heading(self, "Analizador léxico", "Reconoce tokens y localiza errores por línea y columna.").grid(
            row=0, sticky="ew", pady=(0, 14))
        self._build_editor()
        metrics = ctk.CTkFrame(self, fg_color="transparent")
        metrics.grid(row=2, sticky="ew", pady=(10, 4))
        self.metrics = []
        for column, (name, color) in enumerate((
            ("Tokens reconocidos", t.ACCENT), ("Errores detectados", t.ERROR),
            ("Caracteres procesados", t.TEXT), ("Tiempo de análisis", t.TEXT),
        )):
            metrics.columnconfigure(column, weight=1, uniform="metrics")
            card = MetricCard(metrics, name, color)
            card.grid(row=0, column=column, sticky="ew", padx=(0, 8 if column < 3 else 0))
            self.metrics.append(card)

        self.tokens = self._table(3, "Tokens", (
            ("N.º", 45), ("Lexema", 135), ("Tipo de token", 155),
            ("Línea", 62), ("Columna", 85)))
        self.errors = self._table(4, "Errores léxicos", (
            ("Lexema", 105), ("Tipo de error", 130), ("Descripción", 220),
            ("Línea", 62), ("Columna", 85)))
        self.rows = {}
        for kind, color in COLORS.items():
            self.tokens.tree.tag_configure(kind, foreground=color)
            self.editor.tag_configure(kind, foreground=color)
        self.errors.tree.tag_configure("error", foreground=t.ERROR)
        self.editor.tag_configure("error", foreground=t.ERROR, underline=True)
        self.editor.tag_configure("selected", background=t.SELECT)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=5, sticky="ew", pady=(9, 0))
        footer.columnconfigure(0, weight=1)
        self.status = ctk.CTkLabel(footer, text="Lista para analizar", text_color=t.MUTED,
                                   font=ctk.CTkFont(size=15))
        self.status.grid(row=0, column=0, sticky="w")
        self.copy_button = t.button(footer, "Copiar resultados", self.copy)
        self.export_button = t.button(footer, "Exportar CSV", self.export)
        self.copy_button.grid(row=0, column=1, padx=(0, 8))
        self.export_button.grid(row=0, column=2)
        self._actions("disabled")

    # --- Construcción del editor y las tablas ---

    def _build_editor(self) -> None:
        """Crea el editor y enlaza los atajos, el pegado y los ejemplos."""
        panel = ctk.CTkFrame(self, fg_color=t.PANEL, border_width=1,
                             border_color=t.BORDER, corner_radius=12)
        panel.grid(row=1, sticky="ew")
        panel.columnconfigure(0, weight=1)
        label = ctk.CTkLabel(panel, text="Cadena de entrada", text_color=t.TEXT,
                             font=ctk.CTkFont(weight="bold"))
        label.grid(row=0, column=0, padx=12, pady=(6, 0), sticky="w")
        mono = font.nametofont("TkFixedFont").copy()
        mono.configure(size=15)
        self.mono = mono
        self.editor = tk.Text(panel, height=3, width=1, wrap="none", undo=True,
                              font=mono, background=t.BG, foreground=t.TEXT,
                              insertbackground=t.TEXT, selectbackground=t.SELECT,
                              borderwidth=0, highlightthickness=1,
                              highlightbackground=t.INPUT_BORDER, highlightcolor=t.ACCENT,
                              padx=8, pady=6, tabs=(mono.measure("    "),))
        self.editor.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=(12, 0))
        vertical = ctk.CTkScrollbar(panel, command=self.editor.yview, width=12, height=1)
        vertical.grid(row=1, column=3, sticky="ns", padx=(2, 10))
        scrollbar = ctk.CTkScrollbar(panel, orientation="horizontal",
                                      command=self.editor.xview, height=9)
        scrollbar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=12)
        self.editor.configure(xscrollcommand=scrollbar.set, yscrollcommand=vertical.set)
        self.editor.bind("<Control-Return>", self._shortcut)
        self.editor.bind("<Control-KP_Enter>", self._shortcut)
        self.editor.bind("<Tab>", self._tab)
        self.editor.bind("<<Paste>>", self._paste)
        self.editor.bind("<<PasteSelection>>", self._paste_selection)
        self.editor.bind("<<Modified>>", self._modified)
        self.examples = ctk.CTkOptionMenu(panel, values=list(EXAMPLES),
            command=lambda name: self.load_source(EXAMPLES[name]), fg_color=t.SIDE,
            button_color=t.SELECT, button_hover_color=t.HOVER, width=200)
        self.examples.set("Cargar ejemplo")
        self.examples.grid(row=3, column=0, sticky="w", padx=12, pady=(3, 8))
        t.button(panel, "Limpiar", self.clear, width=85).grid(
            row=3, column=1, padx=(0, 8), pady=(3, 8))
        t.button(panel, "Analizar", self.run, primary=True, width=115).grid(
            row=3, column=2, padx=(0, 12), pady=(3, 8))
        ctk.CTkLabel(panel, text="Ctrl + Enter para analizar · Tab inserta una tabulación",
                     text_color=t.MUTED).grid(row=0, column=1, columnspan=2, padx=12, sticky="e")

    def _table(self, row: int, title: str, columns: tuple) -> DataTable:
        """Crea una tabla de resultados y enlaza la selección con el editor."""
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.grid(row=row, sticky="nsew", pady=(3, 0))
        section.columnconfigure(0, weight=1)
        section.rowconfigure(1, weight=1)
        ctk.CTkLabel(section, text=title, text_color=t.TEXT,
                     font=ctk.CTkFont(size=16, weight="bold")).grid(sticky="w")
        table = DataTable(section, columns, height=2)
        table.grid(row=1, sticky="nsew")
        table.tree.bind("<<TreeviewSelect>>", lambda event: self._select(table))
        return table

    # --- Entrada, pegado y atajos ---

    def _insert(self, value: str) -> str:
        """Inserta texto en el cursor o sustituye el fragmento seleccionado."""
        if self.editor.tag_ranges("sel"):
            self.editor.delete("sel.first", "sel.last")
        self.editor.insert("insert", value)
        self.editor.see("insert")
        return "break"

    def _tab(self, event) -> str:
        """Inserta una tabulación real y consume el evento de teclado."""
        return self._insert("\t")

    def _paste(self, event, selection: str = "CLIPBOARD") -> str:
        """Pega texto conservando cada salto de línea."""
        try:
            value = self.editor.selection_get(selection=selection)
        except tk.TclError:
            return "break"
        return self._insert(value.replace("\r\n", "\n").replace("\r", "\n"))

    def _paste_selection(self, event) -> str:
        """Pega la selección primaria en la posición del puntero."""
        self.editor.mark_set("insert", f"@{event.x},{event.y}")
        return self._paste(event, "PRIMARY")

    def _shortcut(self, event) -> str:
        """Ejecuta el análisis desde el teclado y evita insertar un salto."""
        self.run()
        return "break"

    # --- Vigencia del resultado y resaltado ---

    def _actions(self, state: str) -> None:
        """Habilita o deshabilita las acciones de copia y exportación."""
        self.copy_button.configure(state=state)
        self.export_button.configure(state=state)

    def _clear_highlights(self) -> None:
        """Retira las etiquetas de token, error y selección del editor."""
        for tag in (*COLORS, "error", "selected"):
            self.editor.tag_remove(tag, "1.0", "end")

    def _modified(self, event=None) -> None:
        """Invalida el resaltado si el resultado ya no corresponde a la entrada."""
        if not self.editor.edit_modified():
            return
        self.editor.edit_modified(False)
        if self.result is not None and self.editor.get("1.0", "end-1c") != self.source:
            self._clear_highlights()
            self._actions("disabled")
            self.status.configure(text="Entrada modificada · Vuelve a analizar", text_color=t.WARNING)
        elif self.result is not None:
            # Si deshacer restaura exactamente la entrada, los datos vuelven a corresponder.
            self._paint()
            self._show_status()

    def _select(self, table: DataTable) -> None:
        """Resalta el tramo de la fila seleccionada y lo lleva a la vista."""
        selection = table.tree.selection()
        if not selection or self.editor.get("1.0", "end-1c") != self.source:
            return
        row = self.rows.get((table, selection[0]))
        if row is None:
            return
        start, end = self._span(row.line, row.column, row.lexeme)
        self.editor.tag_remove("selected", "1.0", "end")
        self.editor.tag_add("selected", start, end)
        self.editor.see(start)

    def _span(self, line: int, column: int, lexeme: str) -> tuple[str, str]:
        """Convierte la posición del lexema en índices del editor."""
        start = f"{line}.0 + {column - 1} chars"
        return start, f"{start} + {len(lexeme)} chars"

    def _paint(self) -> None:
        """Aplica a cada lexema el estilo de su token o de su error."""
        self._clear_highlights()
        if self.result is None:
            return
        for token in self.result.tokens:
            self.editor.tag_add(token.kind, *self._span(token.line, token.column, token.lexeme))
        for error in self.result.errors:
            self.editor.tag_add("error", *self._span(error.line, error.column, error.lexeme))

    # --- Carga, limpieza y análisis ---

    def load_source(self, source: str) -> None:
        """Carga texto en el editor y reinicia el historial de deshacer."""
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", source.replace("\r\n", "\n").replace("\r", "\n"))
        self.editor.edit_reset()
        self.editor.focus_set()
        self._modified()

    def _reset_tables(self) -> None:
        """Borra las filas y el vínculo con sus posiciones en el editor."""
        self.tokens.clear()
        self.errors.clear()
        self.rows.clear()

    def clear(self) -> None:
        """Restablece el editor, las métricas, las tablas y el estado."""
        self.result = None
        self.source = ""
        self.load_source("")
        self.examples.set("Cargar ejemplo")
        self._reset_tables()
        self._clear_highlights()
        for metric in self.metrics:
            metric.set("—")
        self._actions("disabled")
        self.status.configure(text="Lista para analizar", text_color=t.MUTED)

    def _show_status(self) -> None:
        """Muestra el resultado final con su color y habilita las acciones."""
        if self.result is None:
            return
        color = {Status.VALID: t.SUCCESS, Status.INVALID: t.ERROR, Status.EMPTY: t.WARNING}
        self.status.configure(text=self.result.status.value, text_color=color[self.result.status])
        self._actions("normal")

    def run(self) -> None:
        """Llama al motor y refleja su salida en las tablas, métricas y editor."""
        self.source = self.editor.get("1.0", "end-1c")
        self.result = analyze(self.source)
        self._reset_tables()
        for index, token in enumerate(self.result.tokens, 1):
            key = self.tokens.add((index, token.lexeme, token.kind, token.line, token.column),
                                  token.kind)
            self.rows[(self.tokens, key)] = token
        for error in self.result.errors:
            key = self.errors.add((error.lexeme, error.kind, error.description,
                                   error.line, error.column), "error")
            self.rows[(self.errors, key)] = error
        for card, value in zip(self.metrics, (
            len(self.result.tokens), len(self.result.errors), self.result.characters,
            f"{self.result.elapsed_ms:.3f} ms"
        )):
            card.set(str(value))
        self.editor.edit_modified(False)
        self._paint()
        self._show_status()

    # --- Portapapeles y exportación ---

    def copy(self) -> None:
        """Copia al portapapeles el estado y los registros del análisis."""
        if self.result is None:
            return
        output = [self.result.status.value, "\t".join(ANALYSIS_HEADERS)]
        output.extend("\t".join(map(str, row)) for row in analysis_rows(self.result))
        self.clipboard_clear()
        self.clipboard_append("\n".join(output))
        self.status.configure(text=f"{self.result.status.value} · Copiado")

    def export(self) -> None:
        """Solicita una ruta y guarda en CSV el análisis disponible."""
        if self.result is None:
            return
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".csv",
                    filetypes=[("Archivo CSV", "*.csv")], initialfile="analisis.csv")
        if path:
            try:
                export_analysis(path, self.result)
            except OSError as error:
                messagebox.showerror("Error de exportación", str(error), parent=self)
            else:
                self.status.configure(text=f"{self.result.status.value} · CSV guardado")
