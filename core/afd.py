from core.models import AutomataStep
from core.patterns import DIGIT, LETTER

INITIAL = "q0"
ACCEPTING = "q1"
CATEGORIES = ("Letra", "Dígito", "Otro")
TRANSITIONS = {
    "q0": dict(zip(CATEGORIES, ("q1", "qR", "qR"))),
    "q1": dict(zip(CATEGORIES, ("q1", "q1", "qR"))),
    "qR": dict.fromkeys(CATEGORIES, "qR"),
}


def trace(source: str) -> list[AutomataStep]:
    """Registra una transición por carácter, incluso en el estado trampa."""
    steps = []
    state = INITIAL
    for position, character in enumerate(source, 1):
        category = "Letra" if LETTER.fullmatch(character) else (
            "Dígito" if DIGIT.fullmatch(character) else "Otro"
        )
        following = TRANSITIONS[state][category]
        steps.append(AutomataStep(character, position, state, following, category))
        state = following
    return steps


def accepts(source: str) -> bool:
    steps = trace(source)
    return bool(steps and steps[-1].following == ACCEPTING)
