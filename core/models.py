from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    VALID = "Entrada léxicamente válida"
    INVALID = "Entrada léxicamente no válida"
    EMPTY = "Entrada vacía"


@dataclass(frozen=True)
class Token:
    lexeme: str
    kind: str
    column: int


@dataclass(frozen=True)
class LexicalError:
    lexeme: str
    description: str
    kind: str
    column: int


@dataclass(frozen=True)
class AnalysisResult:
    tokens: list[Token]
    errors: list[LexicalError]
    status: Status
    characters: int
    elapsed_ms: float


@dataclass(frozen=True)
class AutomataStep:
    character: str
    position: int
    previous: str
    following: str
    category: str


@dataclass(frozen=True)
class TestCase:
    identifier: int
    description: str
    source: str
    expected: tuple
