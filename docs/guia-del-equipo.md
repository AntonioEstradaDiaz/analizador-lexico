# Guía del equipo

Analizador Lexico recibe una o varias líneas de texto. Muestra tokens y errores con su línea y columna, además del estado léxico de la entrada. También permite simular el autómata de identificadores.

## Recorrido del código

| Parte | Archivo | Qué explicar |
| --- | --- | --- |
| Arranque | [main.py](../main.py) | Crea la ventana e inicia el bucle de eventos de Tk. |
| Navegación | [ui/main_window.py](../ui/main_window.py) | Crea las vistas cuando se abren por primera vez y conserva sus datos al cambiar de módulo. |
| Editor y resultados | [ui/views/analyzer_view.py](../ui/views/analyzer_view.py) | Obtiene la línea, llama a `analyze`, llena las tablas y resalta las posiciones. |
| Patrones | [core/patterns.py](../core/patterns.py) | Define los tokens del enunciado, las palabras reservadas y los patrones ASCII que delimitan los bloques. |
| Motor léxico | [core/lexer.py](../core/lexer.py) | Recorre y clasifica la línea. Puede ejecutarse sin abrir Tk. |
| Modelos | [core/models.py](../core/models.py) | Define los datos que se intercambian, como `Token`, `LexicalError` y `AnalysisResult`. |
| AFD | [core/afd.py](../core/afd.py) | La tabla de transiciones determina el próximo estado. `trace` genera los pasos. |
| Simulación | [ui/views/automata_view.py](../ui/views/automata_view.py) y [Canvas](../ui/components/automata_canvas.py) | La vista controla el cursor del historial. Canvas dibuja y resalta estados y aristas. `after()` programa la reproducción. |
| Pruebas | [services/test_service.py](../services/test_service.py) y [tests/](../tests/) | Los resultados esperados se escriben a mano. Se comparan estado, tokens y errores, incluidos orden y columnas. |
| Exportación | [services/export_service.py](../services/export_service.py) | Convierte los datos reales del análisis y las pruebas a CSV. |

## Ejemplo para la exposición

Para encontrar una función rápidamente, busca su nombre con **Ctrl + F** o abre
la lista de símbolos de tu editor. Estas son las funciones que conviene tener a mano.

| Si preguntan por… | Busca… |
| --- | --- |
| El recorrido de la línea y la columna inicial | `analyze` en [core/lexer.py](../core/lexer.py) |
| Las transiciones de un identificador | `trace` en [core/afd.py](../core/afd.py) |
| El paso automático del simulador | `play` y `_tick` en [automata_view.py](../ui/views/automata_view.py) |
| La llamada al motor desde el botón Analizar | `run` en [analyzer_view.py](../ui/views/analyzer_view.py) |
| La comparación con resultados esperados | `run_case` y `TestRun.passed` en [test_service.py](../services/test_service.py) |

### Secuencia de demostración

1. Analicen `Total2=15+3;`. El patrón `[A-Za-z][A-Za-z0-9]*` reconoce el lexema `Total2`. Su token es de tipo IDENTIFICADOR y empieza en la columna 1.
2. Analicen `a=9abc+@;`. El motor toma `9abc` completo y lo compara con los patrones mediante `fullmatch`. Registra el bloque en la columna 3 y el carácter `@` en la columna 8. Los tokens `a`, `=`, `+` y `;` aparecen en las columnas 1, 2, 7 y 9.
3. Abran **Autómata AFD**. Recorran `A`, `Total2` y `9abc`. La aceptación se decide en el estado final. q1 acepta las dos primeras cadenas y qR rechaza la tercera. La tabla completa está en [Diseño del AFD](automata.md).
4. En **Pruebas**, ejecuten todos los casos y abran alguno en **Analizador**. La comparación incluye la salida completa esperada y la obtenida.

El índice interno comienza en cero y la columna mostrada en uno. Un espacio o tabulación hace avanzar el índice una posición. Cada bloque se consume una vez, por lo que el recorrido léxico tiene tiempo O(n).

## Cotejo con el enunciado oficial

| Requisito | Dónde verificarlo |
| --- | --- |
| Cinco patrones del enunciado y lectura de una o varias líneas | **Reglas léxicas**, **Analizador** y [patrones](../core/patterns.py) |
| Tokens en orden con lexema, tipo, línea y columna inicial | **Analizador**, casos 4 y 23 |
| Espacios y tabulaciones contados en las columnas | Casos 5 y 6 |
| Bloque inválido completo, símbolo inválido y recuperación | Casos 7 y 8 |
| Entrada válida, no válida y vacía | Casos 4, 8 y 9 |
| AFD con inicio, aceptación, rechazo y tres recorridos | **Autómata AFD** y [diseño del AFD](automata.md) |
| Al menos ocho pruebas con resultados esperados, obtenidos y coincidencia | **Pruebas** ejecuta 25 casos. Los casos 1, 2, 3, 4, 6, 7, 8 y 9 cubren el mínimo indicado. |

El enunciado identifica la actividad como **Unidad 4**. La aplicación muestra **Unidad 6**, según la identificación solicitada para el proyecto.

## Entrega académica

El enunciado pide un solo PDF para Classroom, `Proyecto_Lexico_Grupo_Equipo.pdf`. Debe incluir portada, objetivo, reglas léxicas, diseño del AFD, funcionamiento, pruebas y evidencias, y conclusión. En la portada van el grupo, los integrantes y la fecha de entrega. Incluyan al menos ocho pruebas completas y dos capturas reales en las que se distingan entrada y salida. Los casos 4 y 8 sirven para documentar una entrada válida y otra con errores. El PDF de entrega debe omitir código fuente, ejecutables y capturas del editor.
