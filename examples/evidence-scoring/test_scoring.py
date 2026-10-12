import copy
import unittest
from scoring import aggregate

def item(name, score, scope="standard", weight=1):
    return {"name": name, "score": score, "weight": weight, "scope": scope}

class ScoringChecks(unittest.TestCase):
    def test_unavailable_student_does_not_reduce_teacher(self):
        signals = [item("teacher", 80), item("student", 0, "unavailable")]
        before = copy.deepcopy(signals)
        result = aggregate(signals)
        self.assertEqual(result["score"], 80)
        self.assertEqual(result["effective_weights"], {"teacher": 1, "student": 0})
        self.assertEqual(result["evaluation"], "partial")
        self.assertEqual(signals, before)

    def test_real_zero_is_weighted(self):
        self.assertEqual(aggregate([item("a", 0, "directional"), item("b", 100)])["score"], 50)

    def test_legacy_metadata_is_not_unavailable(self):
        signal = item("a", 0)
        del signal["scope"]
        self.assertEqual(aggregate([signal])["score"], 0)

    def test_no_evidence_is_unrated(self):
        for signals in ([], [item("a", 50, "unavailable")], [item("a", None)]):
            self.assertIsNone(aggregate(signals)["score"])
            self.assertEqual(aggregate(signals)["evaluation"], "unavailable")

    def test_effective_weights(self):
        self.assertEqual(aggregate([item("a", 20), item("b", 80, weight=3), item("c", 100, "unavailable", 10)])["score"], 65)

    def test_invalid_input(self):
        for signal in (item("a", True), item("a", float("nan")), item("a", 101), item("a", 10, weight=0), item("a", 10, "bad"), item("a", 100, weight=1e308)):
            with self.assertRaises(ValueError):
                aggregate([signal])
        with self.assertRaises(ValueError):
            aggregate([item("a", 10), item("a", 20)])

if __name__ == "__main__":
    unittest.main()
