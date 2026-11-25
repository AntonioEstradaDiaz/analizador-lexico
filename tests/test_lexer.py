"""Pruebas unitarias del reconocimiento léxico."""

import unittest

from core.lexer import analyze
from core.models import LexicalError, Status
from services.test_service import CASES, run_case


class LexerTests(unittest.TestCase):
    """Verifica casos académicos, diagnósticos y entradas largas."""
    def test_cases(self):
        """Compara el resultado real y esperado de los veinte casos."""
        for case in CASES:
            with self.subTest(case=case.identifier):
                self.assertEqual(run_case(case).actual, case.expected)

    def test_metrics_and_diagnostics(self):
        """Comprueba el recuento, el tiempo y los detalles de cada error."""
        result = analyze("\t9abc+@")
        self.assertEqual(result.characters, 7)
        self.assertGreaterEqual(result.elapsed_ms, 0)
        self.assertEqual(result.errors, [
            LexicalError("9abc", "Bloque alfanumérico inválido", "Bloque inválido", 2),
            LexicalError("@", "Carácter no reconocido", "Carácter inválido", 7),
        ])

    def test_long_input(self):
        """Comprueba que un bloque largo se conserva y que el análisis continúa."""
        result = analyze("9" * 100_000 + "A;")
        self.assertEqual(result.status, Status.INVALID)
        self.assertEqual(len(result.errors[0].lexeme), 100_001)
        self.assertEqual(result.tokens[0].column, 100_002)
