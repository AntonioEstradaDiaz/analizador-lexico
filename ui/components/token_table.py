"""Tabla reutilizable con encabezados, franjas y barras de desplazamiento."""

from tkinter import ttk

import customtkinter as ctk

from ui import theme as t


class DataTable(ctk.CTkFrame):
    """Envuelve Treeview y concentra el formato común de las tablas."""
    def __init__(self, parent, columns: tuple[tuple[str, int], ...], height: int = 5):
        """Configura columnas, alineación, selección y desplazamiento."""
        super().__init__(parent, fg_color=t.PANEL, corner_radius=12,
                         border_width=1, border_color=t.BORDER)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        keys = tuple(str(i) for i in range(len(columns)))
        self.tree = ttk.Treeview(self, columns=keys, show="headings",
                                 height=height, selectmode="browse")
        self.tree.tag_configure("even", background=t.PANEL)
        self.tree.tag_configure("odd", background=t.TABLE_ALT)
        for key, (label, width) in zip(keys, columns):
            alignment = "center" if label in {"N.º", "Caso", "Columna", "Columna inicial",
                                              "Posición", "Desde", "Hasta", "Estado"} else "w"
            self.tree.heading(key, text=label, anchor=alignment)
            self.tree.column(key, width=width, minwidth=width, anchor=alignment,
                             stretch=width >= 100)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(2, 0), pady=(2, 0))
        vertical = ctk.CTkScrollbar(self, command=self.tree.yview, width=12)
        vertical.grid(row=0, column=1, sticky="ns", padx=(0, 2))
        horizontal = ctk.CTkScrollbar(self, command=self.tree.xview,
                                       orientation="horizontal", height=10)
        horizontal.grid(row=1, column=0, sticky="ew", padx=3, pady=(0, 2))
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)

    def clear(self) -> None:
        """Elimina las filas sin modificar la estructura de la tabla."""
        self.tree.delete(*self.tree.get_children())

    def add(self, values: tuple, tag: str = "", key: str | None = None) -> str:
        """Inserta una fila y devuelve su identificador."""
        row = self.tree.insert("", "end", iid=key, values=values)
        self.set_row(row, values, tag)
        return row

    def set_row(self, key: str, values: tuple, tag: str = "") -> None:
        """Actualiza una fila con fondo alternado y etiqueta de estado."""
        stripe = "odd" if self.tree.index(key) % 2 else "even"
        tags = (stripe, tag) if tag else (stripe,)
        self.tree.item(key, values=values, tags=tags)
