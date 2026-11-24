from time import perf_counter

from core.models import AnalysisResult, LexicalError, Status, Token
from core.patterns import BLOCK, PATTERNS, SYMBOLS


def analyze(source: str) -> AnalysisResult:
    """Recorre la entrada una vez y conserva los tokens tras cada error."""
    start = perf_counter()
    tokens: list[Token] = []
    errors: list[LexicalError] = []
    index = 0
    while index < len(source):
        char = source[index]
        column = index + 1
        if char in " \t":
            index += 1
            continue

        block = BLOCK.match(source, index)
        if block:
            # Clasificar el bloque completo evita dividir 9abc en dos tokens.
            lexeme = block.group()
            index = block.end()
            for kind in ("IDENTIFICADOR", "ENTERO"):
                if PATTERNS[kind].fullmatch(lexeme):
                    tokens.append(Token(lexeme, kind, column))
                    break
            else:
                errors.append(LexicalError(
                    lexeme, "Bloque alfanumérico inválido", "Bloque inválido", column
                ))
            continue

        if char in SYMBOLS:
            tokens.append(Token(char, SYMBOLS[char], column))
        else:
            errors.append(LexicalError(
                char, "Carácter no reconocido", "Carácter inválido", column
            ))
        index += 1

    status = Status.INVALID if errors else Status.VALID if tokens else Status.EMPTY
    return AnalysisResult(tokens, errors, status, len(source), (perf_counter() - start) * 1000)
