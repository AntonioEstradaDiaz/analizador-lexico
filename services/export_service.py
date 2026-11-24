import csv
from collections.abc import Iterable
from pathlib import Path

from core.models import AnalysisResult
from services.test_service import TestRun, describe


def write_csv(path: str | Path, headers: tuple[str, ...], rows: Iterable[tuple]) -> None:
    """Escribe CSV en UTF-8 con BOM para conservar acentos en Excel."""
    with open(path, "w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def analysis_rows(result: AnalysisResult) -> Iterable[tuple]:
    # Ambas listas ya están ordenadas. Se mezclan sin alterar el orden de origen.
    from heapq import merge

    tokens = ((x.column, "Token", x.lexeme, x.kind, "") for x in result.tokens)
    errors = ((x.column, "Error", x.lexeme, x.kind, x.description) for x in result.errors)
    yield from merge(tokens, errors)


def export_analysis(path: str | Path, result: AnalysisResult) -> None:
    write_csv(path, ("Columna", "Clase", "Lexema", "Tipo", "Descripción"),
              analysis_rows(result))


def export_runs(path: str | Path, runs: Iterable[TestRun]) -> None:
    write_csv(path, ("Caso", "Descripción", "Entrada", "Esperado", "Obtenido", "Resultado"),
              ((r.case.identifier, r.case.description, r.case.source,
                describe(r.case.expected), describe(r.actual),
                "Aprobada" if r.passed else "Fallida") for r in runs))
