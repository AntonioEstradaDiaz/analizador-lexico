# Reglas léxicas

| Token | Patrón | Ejemplos |
| --- | --- | --- |
| IDENTIFICADOR | `[A-Za-z][A-Za-z0-9]*` | A, total, Total2 |
| PALABRA RESERVADA | `if\|while\|int` | if, while, int |
| ENTERO | `[0-9]+` | 0, 15, 2026 |
| ASIGNACIÓN | `=` | = |
| SUMA | `\+` | + |
| FIN_SENTENCIA | `;` | ; |

Un patrón define la forma de una categoría. El lexema es el texto concreto. En Total2, la categoría del token es IDENTIFICADOR y el lexema es Total2.

Las palabras reservadas amplían los cinco tipos de token del enunciado. Se comprueban antes de los identificadores y requieren coincidencia exacta, incluida la capitalización. `if2` e `Int` son identificadores. El AFD conserva su función de comprobar el patrón general de identificador.

Se examina el texto de izquierda a derecha. Línea y columna comienzan en 1. Con cada salto se avanza una línea y se reinicia la columna. Espacios y tabulaciones ocupan una columna cada uno. Cada bloque alfanumérico ASCII se clasifica completo. Por eso 9abc genera un solo error. Los caracteres fuera del lenguaje se reportan individualmente. En a=9abc+@; se conservan a, =, + y ; y se registran los errores 9abc (columna 3) y @ (columna 8).

Cualquier error determina el estado «Entrada léxicamente no válida». Si hay tokens y cero errores, la entrada es válida. Una cadena sin tokens ni errores está vacía. El análisis sintáctico comprueba estructura y el semántico comprueba significado. En este proyecto x=+; es léxicamente válida.
