import tkinter as tk
from tkinter import filedialog, font, messagebox

import customtkinter as ctk

from core.lexer import analyze
from core.models import AnalysisResult, Status
from services.export_service import analysis_rows, export_analysis
from ui import theme as t
from ui.components.metric_card import MetricCard
from ui.components.token_table import DataTable

EXAMPLES = {
    "Asignación y suma": "Total2=15+3;",
    "Entrada con errores": "a=9abc+@;",
    "Espacios y tabulaciones": "a\t=\t5;",
    "Operadores consecutivos": "x=+;",
    "Entrada vacía": "",
}
COLORS = dict(zip(("IDENTIFICADOR", "ENTERO", "ASIGNACIÓN", "SUMA", "FIN_SENTENCIA"),
                  (t.ACCENT, t.SUCCESS, "#93C5FD", t.WARNING, t.MUTED)))


class AnalyzerView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.result: AnalysisResult | None = None
        self.source = ""
        self.columnconfigure(0, weight=1)
        self.rowconfigure((3, 4), weight=1, uniform="results")
        t.heading(self, "Analizador léxico", "Reconoce tokens y localiza errores en una sola línea.").grid(
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
            ("N.º", 55), ("Lexema", 160), ("Tipo de token", 155), ("Columna inicial", 120)))
        self.errors = self._table(4, "Errores léxicos", (
            ("Lexema", 120), ("Tipo de error", 125), ("Descripción", 235), ("Columna", 75)))
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

    def _build_editor(self) -> None:
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
        self.editor = tk.Text(panel, height=1, width=1, wrap="none", undo=True,
                              font=mono, background=t.BG, foreground=t.TEXT,
                              insertbackground=t.TEXT, selectbackground=t.SELECT,
                              borderwidth=0, highlightthickness=1,
                              highlightbackground=t.INPUT_BORDER, highlightcolor=t.ACCENT,
                              padx=8, pady=6, tabs=(mono.measure("    "),))
        self.editor.grid(row=1, column=0, columnspan=3, sticky="ew", padx=12)
        scrollbar = ctk.CTkScrollbar(panel, orientation="horizontal",
                                      command=self.editor.xview, height=9)
        scrollbar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=12)
        self.editor.configure(xscrollcommand=scrollbar.set)
        self.editor.bind("<Return>", lambda event: "break")
        self.editor.bind("<KP_Enter>", lambda event: "break")
        self.editor.bind("<Control-Return>", self._shortcut)
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

    def _insert(self, value: str) -> str:
        if self.editor.tag_ranges("sel"):
            self.editor.delete("sel.first", "sel.last")
        self.editor.insert("insert", value)
        self.editor.see("insert")
        return "break"

    def _tab(self, event) -> str:
        return self._insert("\t")

    def _paste(self, event, selection: str = "CLIPBOARD") -> str:
        try:
            value = self.editor.selection_get(selection=selection)
        except tk.TclError:
            return "break"
        return self._insert(value.replace("\r\n", " ").replace("\n", " ").replace("\r", " "))

    def _paste_selection(self, event) -> str:
        self.editor.mark_set("insert", f"@{event.x},{event.y}")
        return self._paste(event, "PRIMARY")

    def _shortcut(self, event) -> str:
        self.run()
        return "break"

    def _actions(self, state: str) -> None:
        self.copy_button.configure(state=state)
        self.export_button.configure(state=state)

    def _clear_highlights(self) -> None:
        for tag in (*COLORS, "error", "selected"):
            self.editor.tag_remove(tag, "1.0", "end")

    def _modified(self, event=None) -> None:
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
        selection = table.tree.selection()
        if not selection or self.editor.get("1.0", "end-1c") != self.source:
            return
        row = self.rows.get((table, selection[0]))
        if row is None:
            return
        column, lexeme = row
        start, end = self._span(column, lexeme)
        self.editor.tag_remove("selected", "1.0", "end")
        self.editor.tag_add("selected", start, end)
        self.editor.see(start)

    def _span(self, column: int, lexeme: str) -> tuple[str, str]:
        start = f"1.0 + {column - 1} chars"
        return start, f"{start} + {len(lexeme)} chars"

    def _paint(self) -> None:
        self._clear_highlights()
        if self.result is None:
            return
        for token in self.result.tokens:
            self.editor.tag_add(token.kind, *self._span(token.column, token.lexeme))
        for error in self.result.errors:
            self.editor.tag_add("error", *self._span(error.column, error.lexeme))

    def load_source(self, source: str) -> None:
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", source)
        self.editor.edit_reset()
        self.editor.focus_set()
        self._modified()

    def _reset_tables(self) -> None:
        self.tokens.clear()
        self.errors.clear()
        self.rows.clear()

    def clear(self) -> None:
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
        if self.result is None:
            return
        color = {Status.VALID: t.SUCCESS, Status.INVALID: t.ERROR, Status.EMPTY: t.WARNING}
        self.status.configure(text=self.result.status.value, text_color=color[self.result.status])
        self._actions("normal")

    def run(self) -> None:
        self.source = self.editor.get("1.0", "end-1c")
        self.result = analyze(self.source)
        self._reset_tables()
        for index, token in enumerate(self.result.tokens, 1):
            key = self.tokens.add((index, token.lexeme, token.kind, token.column), token.kind)
            self.rows[(self.tokens, key)] = token.column, token.lexeme
        for error in self.result.errors:
            key = self.errors.add((error.lexeme, error.kind, error.description, error.column), "error")
            self.rows[(self.errors, key)] = error.column, error.lexeme
        for card, value in zip(self.metrics, (
            len(self.result.tokens), len(self.result.errors), self.result.characters,
            f"{self.result.elapsed_ms:.3f} ms"
        )):
            card.set(str(value))
        self.editor.edit_modified(False)
        self._paint()
        self._show_status()

    def copy(self) -> None:
        if self.result is None:
            return
        output = [self.result.status.value, "Columna\tClase\tLexema\tTipo\tDescripción"]
        output.extend("\t".join(map(str, row)) for row in analysis_rows(self.result))
        self.clipboard_clear()
        self.clipboard_append("\n".join(output))
        self.status.configure(text=f"{self.result.status.value} · Copiado")

    def export(self) -> None:
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
