"""Motor de reconocimiento léxico, independiente de la interfaz."""

from time import perf_counter

from core.models import AnalysisResult, LexicalError, Status, Token
from core.patterns import BLOCK, PATTERNS, RESERVED_KIND, SYMBOLS


# --- Recorrido y clasificación de la entrada ---

def analyze(source: str) -> AnalysisResult:
    """Recorre la entrada una vez y conserva los tokens tras cada error."""
    start = perf_counter()
    tokens: list[Token] = []
    errors: list[LexicalError] = []
    index = 0
    line = 1
    line_start = 0
    while index < len(source):
        char = source[index]
        if char in "\r\n":
            # CRLF representa un solo salto de línea.
            index += 2 if source.startswith("\r\n", index) else 1
            line += 1
            line_start = index
            continue
        column = index - line_start + 1
        if char in " \t":
            index += 1
            continue

        block = BLOCK.match(source, index)
        if block:
            # Clasificar el bloque completo evita dividir 9abc en dos tokens.
            lexeme = block.group()
            index = block.end()
            # Las reservadas también cumplen el patrón general de identificador.
            for kind in (RESERVED_KIND, "IDENTIFICADOR", "ENTERO"):
                if PATTERNS[kind].fullmatch(lexeme):
                    tokens.append(Token(lexeme, kind, column, line))
                    break
            else:
                errors.append(LexicalError(
                    lexeme, "Bloque alfanumérico inválido", "Bloque inválido", column, line
                ))
            continue

        if char in SYMBOLS:
            tokens.append(Token(char, SYMBOLS[char], column, line))
        else:
            errors.append(LexicalError(
                char, "Carácter no reconocido", "Carácter inválido", column, line
            ))
        index += 1

    # Cualquier error domina el resultado, aunque se hayan reconocido tokens.
    status = Status.INVALID if errors else Status.VALID if tokens else Status.EMPTY
    return AnalysisResult(tokens, errors, status, len(source), (perf_counter() - start) * 1000)
