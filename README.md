# Analizador Lexico

Analizador léxico y simulador de autómatas para Lenguajes y Autómatas I, Unidad 6. Reconoce cinco tokens, muestra errores con sus columnas y permite recorrer el AFD de identificadores paso a paso. La interfaz incluye 20 casos verificables, exportación CSV y consulta de reglas.

## Instalación y ejecución

Requiere Python 3.10 o superior y Tk. En Windows instala Python con Tcl/Tk habilitado. En Debian o Ubuntu instala el paquete `python3-tk` si falta. `requirements.txt` instala CustomTkinter y Pillow, que prepara los iconos para distintas densidades de pantalla. La aplicación funciona sin conexión después de instalar las dependencias.

En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

En Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

Con el entorno activado, el comando de inicio es `python main.py`. En el editor, Ctrl + Enter analiza y Tab inserta una tabulación. El pegado multilínea convierte los saltos de línea en espacios.

## Ejemplos

| Entrada | Resultado |
| --- | --- |
| `Total2=15+3;` | Válida, seis tokens |
| `a=9abc+@;` | No válida, cuatro tokens y errores en las columnas 3 y 8 |
| `x=+;` | Válida en el nivel léxico |
| Cadena vacía o formada por espacios y tabulaciones | Vacía |

El motor reconoce identificadores ASCII, enteros ASCII, asignación, suma y fin de sentencia. Consulta [las reglas](docs/lexical_rules.md) para ver los patrones y [el diseño del AFD](docs/automata.md) para los recorridos.

## Estructura

- `main.py` abre la ventana.
- `core/` contiene modelos, patrones, analizador y AFD.
- `ui/` contiene las cinco vistas, el tema y los componentes reutilizables.
- `services/` contiene casos esperados, ejecución de pruebas y exportación CSV.
- `tests/` contiene pruebas unitarias sin interfaz.
- `docs/` contiene la documentación técnica.

## Pruebas

Con el entorno activado:

```bash
python -m unittest discover -v
```

La vista **Pruebas** puede ejecutar un caso o toda la colección. Comprueba el estado, la secuencia de tokens (lexema, tipo y columna) y la secuencia de errores (lexema y columna). Los resultados esperados se definen a mano.

## Empaquetado opcional

Ejecuta estos comandos en el sistema operativo de destino, con el entorno activado:

```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --windowed --onedir --collect-all customtkinter --name AnalizadorLexico main.py
```

La distribución queda en `dist/AnalizadorLexico/`. Conserva la carpeta completa al distribuirla.

## Límites

La entrada léxica ocupa una línea y las letras y dígitos válidos pertenecen a ASCII. El alcance académico excluye sintaxis, semántica y evaluación matemática. El AFD reconoce identificadores completos. La aplicación usa un tema oscuro y conserva las vistas durante la sesión.

Consulta la [arquitectura](docs/architecture.md) para seguir el flujo que conecta el editor, el motor y la presentación.

La [guía del equipo](docs/guia-del-equipo.md) explica qué hace cada parte del código, cómo demostrarla y qué pide el reporte académico.
