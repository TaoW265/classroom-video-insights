"""Bounded content checks, not full privacy or legal certification."""
from pathlib import Path
import json
import subprocess
root=Path(__file__).resolve().parents[1]
sample=json.loads((root/"samples/report/report.sample.json").read_text())
assert sample["sample_kind"]=="synthetic" and len(sample["chapters"])==3
preview=root/"samples/report/report-preview.html"
before=preview.read_bytes()
subprocess.run(["node",str(root/"scripts/render-report.mjs")],check=True)
assert before==preview.read_bytes(),"preview must match source JSON"
assert "合成数据" in preview.read_text()
assert '<p class="value">待确认</p>' in preview.read_text()
assert '<p class="value">0</p>' in preview.read_text()
assert '<p class="value">50</p>' not in preview.read_text()
for name in ("assets/screenshots","assets/demo"):
    folder=root/name
    assert "占位" in (folder/"README.md").read_text()
    assert all(p.name=="README.md" for p in folder.iterdir())
assert not (root/"LICENSE").exists(),"license remains pending"
for p in root.rglob("*"):
    if not p.is_file() or any(x in p.parts for x in (".git","__pycache__")):
        continue
    assert p.suffix not in {".sqlite",".pem",".key",".mp4",".wav"}
    if p.suffix in {".md",".json",".html",".py",".mjs",".yml"}:
        s=p.read_text()
        markers=("/".join(("", "xai", "")), "."+"xai"+"-runtime", ".".join(("172","0","163"))+".")
        assert not any(marker in s for marker in markers),str(p.relative_to(root))
print("Sample, preview, placeholders and bounded checks passed.")
