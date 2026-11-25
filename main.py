"""Punto de entrada de la aplicación de escritorio."""

from ui.main_window import MainWindow


# El bucle de eventos solo se inicia al ejecutar este archivo directamente.
if __name__ == "__main__":
    MainWindow().mainloop()
