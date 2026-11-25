"""Ejecución de pruebas y comparación de resultados en la interfaz."""

import customtkinter as ctk
from tkinter import filedialog, messagebox

from services.export_service import export_runs
from services.test_service import CASES, TestRun, describe, run_case
from ui import theme as t
from ui.components.token_table import DataTable


class TestsView(ctk.CTkFrame):
    """Presenta los casos académicos y permite ejecutar, abrir o exportar sus resultados."""
    def __init__(self, parent, open_case):
        """Construye los controles, la tabla de casos y los paneles de comparación."""
        super().__init__(parent, fg_color="transparent")
        self.open_case = open_case
        self.runs: dict[int, TestRun] = {}
        self.columnconfigure((0, 1), weight=1, uniform="detail")
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=2)
        t.heading(self, "Pruebas léxicas", "Compara el estado, los tokens y los errores con resultados esperados.").grid(
            row=0, columnspan=2, sticky="ew", pady=(0, 12))
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=1, columnspan=2, sticky="ew", pady=(0, 8))
        for label, action, primary in (
            ("Ejecutar todas", self.run_all, True), ("Ejecutar caso", self.run_one, False),
            ("Abrir en analizador", self.open_selected, False), ("Exportar CSV", self.export, False)
        ):
            control = t.button(actions, label, action, primary)
            control.pack(side="left", padx=(0, 8))
            if label == "Exportar CSV":
                self.export_button = control
        self.export_button.configure(state="disabled")

        self.table = DataTable(self, (
            ("Caso", 56), ("Descripción", 190), ("Entrada", 120), ("Esperado", 100),
            ("Obtenido", 100), ("Coincidencia", 100)), height=5)
        self.table.grid(row=2, columnspan=2, sticky="nsew")
        self.table.tree.tag_configure("pass", foreground=t.SUCCESS)
        self.table.tree.tag_configure("fail", foreground=t.ERROR)
        self.table.tree.bind("<<TreeviewSelect>>", lambda event: self.show_detail())
        self.expected = self._detail("Resultado esperado", 0)
        self.actual = self._detail("Resultado obtenido", 1)
        self.summary = ctk.CTkLabel(self, text=f"0 de {len(CASES)} ejecutadas", text_color=t.MUTED)
        self.summary.grid(row=4, columnspan=2, sticky="w", pady=(6, 0))

        for case in CASES:
            self.table.add(self.values(case), key=str(case.identifier))
        self.table.tree.selection_set("1")
        self.show_detail()

    # --- Presentación y selección de casos ---

    def _detail(self, title: str, column: int) -> ctk.CTkTextbox:
        """Construye un panel desplazable para el resultado de un caso."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=3, column=column, sticky="nsew", padx=(0, 8 if column == 0 else 0), pady=(8, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(weight="bold")).grid(sticky="w")
        box = ctk.CTkTextbox(frame, wrap="word", fg_color=t.PANEL, height=75,
                             font=ctk.CTkFont(size=15),
                             border_width=1, border_color=t.BORDER, corner_radius=10)
        box.grid(row=1, sticky="nsew")
        return box

    @staticmethod
    def values(case, run: TestRun | None = None) -> tuple:
        """Prepara el resumen de un caso para su fila de tabla."""
        def short(snapshot: tuple) -> str:
            """Extrae del resultado la etiqueta breve del estado léxico."""
            return snapshot[0].value.replace("Entrada ", "").replace("léxicamente ", "").capitalize()

        return (case.identifier, case.description, repr(case.source), short(case.expected),
                short(run.actual) if run else "—",
                ("Aprobada" if run.passed else "Fallida") if run else "Pendiente")

    def selected(self):
        """Obtiene el caso asociado a la fila seleccionada."""
        selection = self.table.tree.selection()
        return CASES[int(selection[0]) - 1] if selection else None

    def show_detail(self) -> None:
        """Muestra lado a lado las salidas esperada y obtenida."""
        case = self.selected()
        if case is None:
            return
        run = self.runs.get(case.identifier)
        for box, content in ((self.expected, describe(case.expected)),
                             (self.actual, describe(run.actual) if run else "Pendiente")):
            box.configure(state="normal")
            box.delete("1.0", "end")
            box.insert("1.0", content)
            box.configure(state="disabled")

    # --- Ejecución y exportación ---

    def _execute(self, cases: tuple) -> None:
        """Ejecuta los casos indicados y actualiza filas, conteo y porcentaje."""
        for case in cases:
            run = run_case(case)
            self.runs[case.identifier] = run
            self.table.set_row(str(case.identifier), self.values(case, run),
                               "pass" if run.passed else "fail")
        count = len(self.runs)
        passed = sum(run.passed for run in self.runs.values())
        self.summary.configure(text=f"{count} de {len(CASES)} ejecutadas · {passed} aprobadas"
                               f" · {count - passed} fallidas · {passed / count:.0%} de éxito")
        self.export_button.configure(state="normal")
        self.show_detail()

    def run_one(self) -> None:
        """Ejecuta únicamente el caso seleccionado si existe."""
        case = self.selected()
        if case:
            self._execute((case,))

    def run_all(self) -> None:
        """Ejecuta la colección completa de casos."""
        self._execute(CASES)

    def open_selected(self) -> None:
        """Envía la entrada seleccionada al analizador."""
        case = self.selected()
        if case:
            self.open_case(case.source)

    def export(self) -> None:
        """Guarda en CSV las ejecuciones disponibles y muestra el resultado."""
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".csv",
                    filetypes=[("Archivo CSV", "*.csv")], initialfile="pruebas.csv")
        if path:
            try:
                export_runs(path, (self.runs[key] for key in sorted(self.runs)))
            except OSError as error:
                messagebox.showerror("Error de exportación", str(error), parent=self)
            else:
                messagebox.showinfo("Exportación", "CSV guardado", parent=self)
