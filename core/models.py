"""Contratos de datos que comparten el motor, las pruebas y la interfaz."""

from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    """Describe los tres estados finales posibles del análisis."""
    VALID = "Entrada léxicamente válida"
    INVALID = "Entrada léxicamente no válida"
    EMPTY = "Entrada vacía"


@dataclass(frozen=True)
class Token:
    """Guarda el lexema reconocido, su tipo y su posición inicial."""
    lexeme: str
    kind: str
    column: int
    line: int = 1


@dataclass(frozen=True)
class LexicalError:
    """Guarda el fragmento inválido, su diagnóstico y su posición inicial."""
    lexeme: str
    description: str
    kind: str
    column: int
    line: int = 1


@dataclass(frozen=True)
class AnalysisResult:
    """Reúne los tokens, los errores, el estado y las métricas de la entrada."""
    tokens: list[Token]
    errors: list[LexicalError]
    status: Status
    characters: int
    elapsed_ms: float


@dataclass(frozen=True)
class AutomataStep:
    """Representa una transición del AFD para un carácter de la entrada."""
    character: str
    position: int
    previous: str
    following: str
    category: str


@dataclass(frozen=True)
class TestCase:
    """Vincula una entrada de prueba con su resultado esperado manual."""
    identifier: int
    description: str
    source: str
    expected: tuple
