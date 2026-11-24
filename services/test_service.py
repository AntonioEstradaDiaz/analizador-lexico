from dataclasses import dataclass

from core.lexer import analyze
from core.models import Status, TestCase

V, I, E = Status.VALID, Status.INVALID, Status.EMPTY
ID, N, EQ, PLUS, END = "IDENTIFICADOR", "ENTERO", "ASIGNACIÓN", "SUMA", "FIN_SENTENCIA"


def case(number: int, description: str, source: str, status: Status,
         tokens: tuple = (), errors: tuple = ()) -> TestCase:
    return TestCase(number, description, source, (status, tokens, errors))


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
)


@dataclass(frozen=True)
class TestRun:
    case: TestCase
    actual: tuple

    @property
    def passed(self) -> bool:
        return self.case.expected == self.actual


def run_case(test: TestCase) -> TestRun:
    result = analyze(test.source)
    return TestRun(test, (
        result.status,
        tuple((t.lexeme, t.kind, t.column) for t in result.tokens),
        tuple((e.lexeme, e.column) for e in result.errors),
    ))


def describe(snapshot: tuple) -> str:
    status, tokens, errors = snapshot
    token_text = ", ".join(f"{lexeme!r} · {kind} · col. {col}" for lexeme, kind, col in tokens)
    error_text = ", ".join(f"{lexeme!r} · col. {col}" for lexeme, col in errors)
    return (f"{status.value} | Tokens ({len(tokens)}): {token_text or '—'} | "
            f"Errores ({len(errors)}): {error_text or '—'}")
