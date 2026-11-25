"""Punto de entrada de la aplicación de escritorio."""

from contextlib import ExitStack, redirect_stderr
import os
import sys


def main() -> None:
    """Inicia la interfaz tanto desde Python como desde el ejecutable de Windows."""
    with ExitStack() as cleanup:
        # PyInstaller en modo ventana deja stderr sin conectar.
        if sys.stderr is None:
            diagnostics = cleanup.enter_context(open(os.devnull, "w", encoding="utf-8"))
            cleanup.enter_context(redirect_stderr(diagnostics))

        from ui.main_window import MainWindow

        MainWindow().mainloop()


# El bucle de eventos solo se inicia al ejecutar este archivo directamente.
if __name__ == "__main__":
    main()
