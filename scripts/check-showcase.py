"""Bounded publication checks; not full privacy, security or legal certification."""
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit


APPROVED_MEDIA = {
    "assets/screenshots/report-overview.png": ("screenshot", "user-provided-frontend-crop"),
    "assets/screenshots/teaching-mode.png": ("screenshot", "user-provided-frontend-crop"),
    "assets/screenshots/rt-ch-chart.png": ("screenshot", "user-provided-frontend-crop"),
    "assets/screenshots/speech-distribution.png": ("screenshot", "user-provided-frontend-crop"),
    "assets/screenshots/metric-details.png": ("screenshot", "user-provided-frontend-crop"),
    "assets/demo/poster.png": ("poster", "user-provided-frontend-crop"),
    "assets/demo/product-walkthrough.mp4": ("video", "user-provided-frontend-recording-edited"),
}
LOCAL_ONLY_DIRS = {"output", "截图与实录"}
TEXT_SUFFIXES = {".md", ".json", ".html", ".css", ".js", ".mjs", ".py", ".yml", ".yaml", ".txt"}


def source_files(root):
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in {".git", "__pycache__", "node_modules", ".pytest_cache"} for part in relative.parts):
            continue
        if path.name == ".DS_Store" or relative.parts[0] in LOCAL_ONLY_DIRS:
            continue
        if path.is_symlink():
            raise ValueError(f"symlinks are outside the reviewed scope: {relative}")
        if path.is_file():
            yield path


def check_media(root):
    manifest = json.loads((root / "assets/media-manifest.json").read_text())
    entries = manifest["entries"]
    if not isinstance(entries, list) or len(entries) != len(APPROVED_MEDIA):
        raise ValueError("media manifest must cover the reviewed files exactly")
    seen = set()
    for entry in entries:
        name = entry.get("path")
        if name not in APPROVED_MEDIA or name in seen:
            raise ValueError("unexpected or duplicate media path")
        seen.add(name)
        kind, source_kind = APPROVED_MEDIA[name]
        if entry.get("source_kind") != source_kind or entry.get("kind") != kind:
            raise ValueError(f"media must identify its reviewed source and kind: {name}")
        data = (root / name).read_bytes()
        if sha256(data).hexdigest() != entry.get("sha256"):
            raise ValueError(f"reviewed media hash changed: {name}")
        limit = 25 * 1024 * 1024 if name.endswith(".mp4") else 5 * 1024 * 1024
        if not data or len(data) > limit:
            raise ValueError(f"media size outside the reviewed bounds: {name}")
        if name.endswith(".png") and not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError(f"invalid PNG header: {name}")
        if name.endswith(".mp4") and data[4:8] != b"ftyp":
            raise ValueError(f"invalid MP4 header: {name}")
    actual = {str(p.relative_to(root)) for p in source_files(root) if p.suffix.lower() in {".png", ".mp4"}}
    if actual != seen:
        raise ValueError("media files and reviewed manifest differ")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.targets = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src", "poster"):
            target = attrs.get(key)
            if not target or (tag == "link" and key == "href" and attrs.get("rel") == "icon" and target == "data:,"):
                continue
            self.targets.append(target)
        if attrs.get("id"):
            self.ids.add(attrs["id"])


def check_links(root):
    root = root.resolve()
    count = 0
    for path in source_files(root):
        if path.suffix not in {".md", ".html"}:
            continue
        text = path.read_text()
        parser = Links()
        parser.feed(text)
        targets = parser.targets
        if path.suffix == ".md":
            for raw in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                targets.append(raw[1:raw.index(">")] if raw.startswith("<") else raw.split()[0])
        for target in targets:
            parsed = urlsplit(target)
            if parsed.scheme in {"http", "https", "mailto"}:
                continue
            if parsed.scheme or parsed.netloc:
                raise ValueError(f"unsupported link: {path.relative_to(root)}: {target}")
            local = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not local.is_relative_to(root.resolve()) or ".git" in local.relative_to(root).parts:
                raise ValueError(f"link escapes public content: {target}")
            parts = local.relative_to(root).parts
            if parts and parts[0] in LOCAL_ONLY_DIRS:
                raise ValueError(f"link points to excluded local source or tooling: {target}")
            if not local.exists():
                raise ValueError(f"broken local link: {path.relative_to(root)}: {target}")
            if parsed.fragment and local.suffix == ".html":
                destination = Links()
                destination.feed(local.read_text())
                if unquote(parsed.fragment) not in destination.ids:
                    raise ValueError(f"missing HTML anchor: {target}")
            count += 1
    return count


def check_content(root):
    if (root / "LICENSE").exists():
        raise ValueError("license declaration remains outside this change")
    for name in ("samples/report/report-preview.html", "scripts/render-report.mjs", "examples/report-display/render-report.test.mjs"):
        if (root / name).exists():
            raise ValueError(f"removed HTML preview must not return: {name}")
    markers = ("/".join(("", "xai", "")), "." + "xai" + "-runtime", ".".join(("172", "0", "163")) + ".")
    for path in source_files(root):
        relative = path.relative_to(root)
        if path.name == ".env" or path.name.startswith(".env.") or path.suffix.lower() in {".sqlite", ".sqlite3", ".db", ".pem", ".key", ".wav", ".log", ".jsonl"}:
            raise ValueError(f"sensitive file type is not permitted: {relative}")
        if str(relative) in APPROVED_MEDIA:
            continue
        if path.suffix not in TEXT_SUFFIXES and path.name != ".gitignore":
            raise ValueError(f"file outside the reviewed text/media scope: {relative}")
        text = path.read_text(encoding="utf-8")
        if "\0" in text or any(marker in text for marker in markers):
            raise ValueError(f"prohibited private marker: {relative}")
        if re.search(r"-----BEGIN [A-Z ]*PRIVATE" + r" KEY-----|\bsk-" + r"[A-Za-z0-9]{24,}\b", text):
            raise ValueError(f"possible credential content: {relative}")


def check_tooling_untracked(root):
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--", *sorted(LOCAL_ONLY_DIRS), ".DS_Store", ":(glob)**/.DS_Store"],
        capture_output=True, text=True, check=True,
    )
    if tracked.stdout:
        raise ValueError("original media, local tooling output and Finder metadata must not be tracked by Git")


def main():
    root = Path(__file__).resolve().parents[1]
    check_tooling_untracked(root)
    subprocess.run([sys.executable, str(root / "scripts/run-demo.py"), "--check"], check=True)
    sample = json.loads((root / "samples/report/report.sample.json").read_text())
    if sample.get("sample_kind") != "synthetic" or len(sample["chapters"]) != 4:
        raise ValueError("the generated report must contain four synthetic scenarios")
    expected = [(85, "available"), (None, "unavailable"), (80, "partial"), (0, "available")]
    if [(c["score"], c["evaluation"]) for c in sample["chapters"]] != expected:
        raise ValueError("the four evidence scenarios no longer match their documented contract")
    check_media(root)
    check_content(root)
    links = check_links(root)
    print(f"Four synthetic scenarios, reviewed media, {links} local references and bounded content checks passed.")


if __name__ == "__main__":
    main()
