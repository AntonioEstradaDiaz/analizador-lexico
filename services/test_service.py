"""Casos esperados y comparación con el motor léxico."""

from dataclasses import dataclass

from core.lexer import analyze
from core.models import Status, TestCase

V, I, E = Status.VALID, Status.INVALID, Status.EMPTY
ID, N, EQ, PLUS, END = "IDENTIFICADOR", "ENTERO", "ASIGNACIÓN", "SUMA", "FIN_SENTENCIA"
KEYWORD = "PALABRA RESERVADA"


# --- Definición de entradas y resultados esperados ---

def case(number: int, description: str, source: str, status: Status,
         tokens: tuple = (), errors: tuple = ()) -> TestCase:
    """Construye un caso con las expectativas definidas manualmente."""
    # Los casos de una línea omiten la línea 1 para mantener sus datos legibles.
    positioned_tokens = tuple((*token, 1) if len(token) == 3 else token for token in tokens)
    positioned_errors = tuple((*error, 1) if len(error) == 2 else error for error in errors)
    return TestCase(number, description, source, (status, positioned_tokens, positioned_errors))


CASES = (
    case(1, "Una letra", "A", V, (("A", ID, 1),)),
    case(2, "Identificador con dígito", "Total2", V, (("Total2", ID, 1),)),
    case(3, "Entero", "2026", V, (("2026", N, 1),)),
    case(4, "Asignación y suma", "Total2=15+3;", V,
         (("Total2", ID, 1), ("=", EQ, 7), ("15", N, 8), ("+", PLUS, 10),
          ("3", N, 11), (";", END, 12))),
    case(5, "Espacios internos", "x = 25 + 4;", V,
         (("x", ID, 1), ("=", EQ, 3), ("25", N, 5), ("+", PLUS, 8),
          ("4", N, 10), (";", END, 11))),
    case(6, "Tabulaciones internas", "a\t=\t5;", V,
         (("a", ID, 1), ("=", EQ, 3), ("5", N, 5), (";", END, 6))),
    case(7, "Bloque que comienza con dígito", "9abc", I, errors=(("9abc", 1),)),
    case(8, "Recuperación tras errores", "a=9abc+@;", I,
         (("a", ID, 1), ("=", EQ, 2), ("+", PLUS, 7), (";", END, 9)),
         (("9abc", 3), ("@", 8))),
    case(9, "Cadena vacía", "", E),
    case(10, "Tres espacios", "   ", E),
    case(11, "Guion bajo", "total_2", I,
         (("total", ID, 1), ("2", N, 7)), (("_", 6),)),
    case(12, "Letra no ASCII", "ñ=1;", I,
         (("=", EQ, 2), ("1", N, 3), (";", END, 4)), (("ñ", 1),)),
    case(13, "Validez léxica de x=+;", "x=+;", V,
         (("x", ID, 1), ("=", EQ, 2), ("+", PLUS, 3), (";", END, 4))),
    case(14, "Bloque inválido largo", "123abc456", I, errors=(("123abc456", 1),)),
    case(15, "Solo tabulaciones", "\t\t", E),
    case(16, "Solo errores", "@_$-*/", I,
         errors=(("@", 1), ("_", 2), ("$", 3), ("-", 4), ("*", 5), ("/", 6))),
    case(17, "Operadores consecutivos", "++==;;", V,
         (("+", PLUS, 1), ("+", PLUS, 2), ("=", EQ, 3), ("=", EQ, 4),
          (";", END, 5), (";", END, 6))),
    case(18, "Bloques de distintas longitudes", "1a 99XYZ1", I,
         errors=(("1a", 1), ("99XYZ1", 4))),
    case(19, "Mayúsculas y minúsculas", "Ab9 zZ", V,
         (("Ab9", ID, 1), ("zZ", ID, 5))),
    case(20, "Dígitos Unicode", "١２", I, errors=(("١", 1), ("２", 2))),
    case(21, "Palabras reservadas y símbolos", "if while int;", V,
         (("if", KEYWORD, 1), ("while", KEYWORD, 4), ("int", KEYWORD, 10), (";", END, 13))),
    case(22, "Coincidencia exacta de reservadas", "if2 Int whilex 9int", I,
         (("if2", ID, 1), ("Int", ID, 5), ("whilex", ID, 9)), (("9int", 16),)),
    case(23, "Saltos LF, CRLF y CR", "int\r\n\r\tif 9abc\n@;",
         I, (("int", KEYWORD, 1), ("if", KEYWORD, 2, 3), (";", END, 2, 4)),
         (("9abc", 5, 3), ("@", 1, 4))),
    case(24, "Varias líneas vacías", " \r\n\t\n", E),
    case(25, "Un salto separa bloques", "9\nabc", V, (("9", N, 1), ("abc", ID, 1, 2))),
)


# --- Ejecución y comparación de salidas ---

@dataclass(frozen=True)
class TestRun:
    """Agrupa un caso y la salida real de su ejecución."""
    case: TestCase
    actual: tuple

    @property
    def passed(self) -> bool:
        """Comprueba la coincidencia exacta de estado, tokens y errores ordenados."""
        return self.case.expected == self.actual


def run_case(test: TestCase) -> TestRun:
    """Ejecuta el motor y extrae los campos que se comparan con la expectativa."""
    result = analyze(test.source)
    return TestRun(test, (
        result.status,
        tuple((t.lexeme, t.kind, t.column, t.line) for t in result.tokens),
        tuple((e.lexeme, e.column, e.line) for e in result.errors),
    ))


def describe(snapshot: tuple) -> str:
    """Convierte una salida de prueba en texto legible para la vista y el CSV."""
    status, tokens, errors = snapshot
    token_text = ", ".join(f"{lexeme!r} · {kind} · línea {line}, col. {col}"
                           for lexeme, kind, col, line in tokens)
    error_text = ", ".join(f"{lexeme!r} · línea {line}, col. {col}"
                           for lexeme, col, line in errors)
    return (f"{status.value} | Tokens ({len(tokens)}): {token_text or '—'} | "
            f"Errores ({len(errors)}): {error_text or '—'}")
