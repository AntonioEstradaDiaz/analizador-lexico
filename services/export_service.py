"""Conversión de análisis y pruebas al formato CSV."""

import csv
from collections.abc import Iterable
from pathlib import Path

from core.models import AnalysisResult
from services.test_service import TestRun, describe

ANALYSIS_HEADERS = ("Línea", "Columna", "Clase", "Lexema", "Tipo", "Descripción")


def write_csv(path: str | Path, headers: tuple[str, ...], rows: Iterable[tuple]) -> None:
    """Escribe CSV en UTF-8 con BOM para conservar acentos en Excel."""
    with open(path, "w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def analysis_rows(result: AnalysisResult) -> Iterable[tuple]:
    # Ambas listas ya están ordenadas. Se mezclan sin alterar el orden de origen.
    """Combina tokens y errores en orden de línea y columna."""
    from heapq import merge

    tokens = ((x.line, x.column, "Token", x.lexeme, x.kind, "") for x in result.tokens)
    errors = ((x.line, x.column, "Error", x.lexeme, x.kind, x.description) for x in result.errors)
    yield from merge(tokens, errors)


def export_analysis(path: str | Path, result: AnalysisResult) -> None:
    """Guarda los tokens y errores del análisis seleccionado."""
    write_csv(path, ANALYSIS_HEADERS, analysis_rows(result))


def export_runs(path: str | Path, runs: Iterable[TestRun]) -> None:
    """Guarda la entrada, la comparación y el resultado de cada prueba ejecutada."""
    write_csv(path, ("Caso", "Descripción", "Entrada", "Esperado", "Obtenido", "Resultado"),
              ((r.case.identifier, r.case.description, r.case.source,
                describe(r.case.expected), describe(r.actual),
                "Aprobada" if r.passed else "Fallida") for r in runs))
