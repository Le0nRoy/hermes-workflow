"""Identical contract suite for planted-defect and fixed fixtures."""
import argparse
import importlib.util
from pathlib import Path
import unittest
from typing import Callable

HANDLER: Callable

class QuantityContract(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(HANDLER({"quantity": 7}), (201, {"quantity": 7}))

    def test_lower_boundary(self):
        self.assertEqual(HANDLER({"quantity": 1}), (201, {"quantity": 1}))

    def test_upper_boundary(self):
        self.assertEqual(HANDLER({"quantity": 100}), (201, {"quantity": 100}))

    def test_reject_bool(self):
        for value in (True, False):
            with self.subTest(value=value):
                self.assertEqual(HANDLER({"quantity": value}), (400, {"error": "invalid quantity"}))

    def test_reject_non_integer(self):
        for value in ("1", 1.0, None, [], {}, float("nan")):
            with self.subTest(value=value):
                self.assertEqual(HANDLER({"quantity": value}), (400, {"error": "invalid quantity"}))

    def test_reject_out_of_range(self):
        for value in (0, -1, 101):
            with self.subTest(value=value):
                self.assertEqual(HANDLER({"quantity": value}), (400, {"error": "invalid quantity"}))

    def test_reject_missing(self):
        self.assertEqual(HANDLER({}), (400, {"error": "invalid quantity"}))

    def test_reject_payload(self):
        for value in (None, [], "quantity=1", 1):
            with self.subTest(value=value):
                self.assertEqual(HANDLER(value), (400, {"error": "invalid quantity"}))

    def test_no_mutation(self):
        payload = {"quantity": 5, "note": "synthetic"}
        before = payload.copy()
        self.assertEqual(HANDLER(payload), (201, {"quantity": 5}))
        self.assertEqual(payload, before)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("baseline", "fixed"), default="fixed")
    args = parser.parse_args()
    path = Path(__file__).parent / "fixtures" / (args.variant + ".py")
    spec = importlib.util.spec_from_file_location("quantity_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    HANDLER = module.submit
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(QuantityContract))
    raise SystemExit(0 if result.wasSuccessful() and result.testsRun == 9 and not result.skipped else 1)
