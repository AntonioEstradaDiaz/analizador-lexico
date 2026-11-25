"""Paleta, estilos de tablas y controles compartidos."""

import customtkinter as ctk
from tkinter import ttk

BG, SIDE, PANEL, BORDER = "#101116", "#171820", "#1C1E27", "#353744"
TABLE_HEADER, TABLE_ALT = "#29263A", "#222431"
PRIMARY, ACCENT = "#7955DC", "#A78BFA"
TEXT, MUTED = "#F4F4F5", "#9295A4"
SUCCESS, ERROR, WARNING = "#4ADE80", "#F87171", "#FBBF24"
HOVER, SELECT, INPUT_BORDER = "#6744C6", "#493578", "#65697D"


def blend(start: str, end: str, progress: float) -> str:
    """Interpola los canales RGB entre dos colores de la transición."""
    channels = []
    for index in (1, 3, 5):
        first = int(start[index:index + 2], 16)
        last = int(end[index:index + 2], 16)
        channels.append(round(first + (last - first) * progress))
    return "#{:02x}{:02x}{:02x}".format(*channels)


def configure() -> None:
    """Activa el modo oscuro y configura las tablas y sus estados de selección."""
    ctk.set_appearance_mode("dark")
    style = ttk.Style()
    style.theme_use("clam")
    row_height = round(style.master.winfo_fpixels("23p"))
    style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                    foreground=TEXT, borderwidth=0, rowheight=row_height,
                    font=("TkDefaultFont", 11))
    style.configure("Treeview.Heading", background=TABLE_HEADER, foreground=TEXT,
                    font=("TkDefaultFont", 11, "bold"), relief="flat", padding=(8, 7))
    style.map("Treeview", background=[("selected", SELECT)],
              foreground=[("selected", TEXT)])
    style.map("Treeview.Heading", background=[("active", BORDER)])


def heading(parent, title: str, subtitle: str) -> ctk.CTkFrame:
    """Construye el encabezado de una vista con título y subtítulo."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    ctk.CTkLabel(frame, text=title, text_color=TEXT,
                 font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w")
    ctk.CTkLabel(frame, text=subtitle, text_color=MUTED,
                 font=ctk.CTkFont(size=15)).pack(anchor="w")
    return frame


def button(parent, label: str, command, primary: bool = False, **kwargs) -> ctk.CTkButton:
    """Crea un botón con la variante primaria o secundaria del tema."""
    return ctk.CTkButton(parent, text=label, command=command, height=36,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         corner_radius=8, fg_color=PRIMARY if primary else SIDE,
                         hover_color=HOVER if primary else BORDER,
                         border_width=0 if primary else 1, border_color=BORDER,
                         text_color=TEXT, **kwargs)
