import unittest

from core.afd import accepts, trace
from core.models import AutomataStep


class AutomataTests(unittest.TestCase):
    def test_required_paths(self):
        for source, expected in (("A", ["q1"]), ("Total2", ["q1"] * 6),
                                 ("9abc", ["qR"] * 4)):
            with self.subTest(source=source):
                self.assertEqual([step.following for step in trace(source)], expected)
                self.assertEqual(accepts(source), expected[-1] == "q1")

    def test_empty_and_other(self):
        self.assertEqual(trace(""), [])
        for source in ("", "é", "A١", "A x", "A_"):
            with self.subTest(source=source):
                self.assertFalse(accepts(source))

    def test_step_details(self):
        self.assertEqual(trace("Az9@")[-1], AutomataStep("@", 4, "q1", "qR", "Otro"))
