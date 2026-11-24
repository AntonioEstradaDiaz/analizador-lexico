# Reglas léxicas

| Token | Patrón | Ejemplos |
| --- | --- | --- |
| IDENTIFICADOR | `[A-Za-z][A-Za-z0-9]*` | A, total, Total2 |
| ENTERO | `[0-9]+` | 0, 15, 2026 |
| ASIGNACIÓN | `=` | = |
| SUMA | `\+` | + |
| FIN_SENTENCIA | `;` | ; |

Un patrón define la forma de una categoría. El lexema es el texto concreto. En Total2, la categoría del token es IDENTIFICADOR y el lexema es Total2.

Se examina toda la línea de izquierda a derecha. Espacios y tabulaciones se cuentan individualmente para la columna, que comienza en 1. Cada bloque alfanumérico ASCII se clasifica completo. Por eso 9abc genera un solo error. Los caracteres fuera del lenguaje se reportan individualmente. En a=9abc+@; se conservan a, =, + y ; y se registran los errores 9abc (columna 3) y @ (columna 8).

Cualquier error determina el estado «Entrada léxicamente no válida». Si hay tokens y cero errores, la entrada es válida. Una cadena sin tokens ni errores está vacía. El análisis sintáctico comprueba estructura y el semántico comprueba significado. En este proyecto x=+; es léxicamente válida.
