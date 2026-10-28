import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("run_demo", ROOT / "scripts/run-demo.py")
run_demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_demo)


class PipelineChecks(unittest.TestCase):
    def setUp(self):
        self.source = json.loads((ROOT / "samples/report/signals.synthetic.json").read_text(encoding="utf-8"))

    def test_four_states_reach_the_display_contract(self):
        report = run_demo.build_report(self.source)
        self.assertEqual(report["sample_kind"], "synthetic")
        self.assertEqual(
            [(chapter["id"], chapter["score"], chapter["evaluation"]) for chapter in report["chapters"]],
            [("available", 85, "available"), ("missing", None, "unavailable"),
             ("partial", 80, "partial"), ("zero", 0, "available")],
        )
        partial = report["chapters"][2]
        self.assertEqual(partial["effective_weights"], {"teacher": 1, "student": 0})
        self.assertEqual(partial["included"], ["teacher"])
        self.assertEqual(partial["excluded"], [{"name": "student", "reason": "evidence unavailable"}])

    def test_generation_preserves_synthetic_input(self):
        before = copy.deepcopy(self.source)
        run_demo.build_report(self.source)
        self.assertEqual(self.source, before)

    def test_legacy_missing_scope_is_preserved(self):
        del self.source["chapters"][3]["signals"][0]["scope"]
        zero = run_demo.build_report(self.source)["chapters"][3]
        self.assertEqual((zero["score"], zero["evaluation"]), (0, "available"))

    def test_empty_signal_list_is_unavailable(self):
        self.source["chapters"][0]["signals"] = []
        chapter = run_demo.build_report(self.source)["chapters"][0]
        self.assertIsNone(chapter["score"])
        self.assertEqual(chapter["evaluation"], "unavailable")

    def test_source_boundary_rejects_malformed_input(self):
        for field, value in (("sample_kind", "real"), ("title", ""), ("chapters", {}), ("chapters", [])):
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                run_demo.build_report({**self.source, field: value})
        for chapter in (None, {"id": "x"}, {**self.source["chapters"][0], "signals": [None]},
                        {**self.source["chapters"][0], "signals": [{"name": "x"}]}):
            with self.subTest(chapter=chapter), self.assertRaises(ValueError):
                run_demo.build_report({**self.source, "chapters": [chapter]})
        with self.assertRaises(ValueError):
            run_demo.build_report({**self.source, "chapters": self.source["chapters"] * 2})


if __name__ == "__main__":
    unittest.main()
