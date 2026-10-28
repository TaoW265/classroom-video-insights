"""Generate the independent synthetic report, without network or model calls."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples/evidence-scoring"))
from scoring import aggregate


def build_report(source):
    if not isinstance(source, dict) or source.get("sample_kind") != "synthetic":
        raise ValueError("synthetic data only")
    if not isinstance(source.get("title"), str) or not source["title"].strip():
        raise ValueError("report title must be a nonempty string")
    if not isinstance(source.get("chapters"), list) or not source["chapters"]:
        raise ValueError("chapters must be a nonempty list")
    chapters, seen = [], set()
    for chapter in source["chapters"]:
        if not isinstance(chapter, dict):
            raise ValueError("each chapter must be an object")
        for field in ("id", "title", "narrative"):
            if not isinstance(chapter.get(field), str) or not chapter[field].strip():
                raise ValueError(f"chapter {field} must be a nonempty string")
        if chapter["id"] in seen:
            raise ValueError("chapter ids must be unique")
        seen.add(chapter["id"])
        signals = chapter.get("signals")
        if not isinstance(signals, list) or any(
            not isinstance(signal, dict) or not {"name", "score", "weight"} <= signal.keys()
            for signal in signals
        ):
            raise ValueError("signals must be a list of objects with name, score and weight")
        chapters.append({
            "id": chapter["id"], "title": chapter["title"], "narrative": chapter["narrative"],
            **aggregate(signals),
        })
    return {"sample_kind": "synthetic", "title": source["title"], "chapters": chapters}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated JSON without writing")
    args = parser.parse_args()
    source = json.loads((ROOT / "samples/report/signals.synthetic.json").read_text(encoding="utf-8"))
    report = build_report(source)
    expected = (json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    output = ROOT / "samples/report/report.sample.json"
    if args.check:
        if output.read_bytes() != expected:
            raise SystemExit("Report JSON is stale. Run: python3 scripts/run-demo.py")
    else:
        output.write_bytes(expected)
    subprocess.run(
        ["node", str(ROOT / "examples/report-display/print-report.mjs"), str(output)],
        check=True,
    )
    print("Synthetic input → Python aggregation → JSON → terminal display: " + ("verified" if args.check else "generated"))
    for chapter in report["chapters"]:
        score = "null" if chapter["score"] is None else f'{chapter["score"]:g}'
        print(f'{chapter["id"]}: score={score}, evaluation={chapter["evaluation"]}')


if __name__ == "__main__":
    main()
