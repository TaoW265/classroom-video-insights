import importlib.util
import json
from hashlib import sha256
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("showcase_checks", Path(__file__).with_name("check-showcase.py"))
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class PublicationChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def media(self):
        entries = []
        for name, (kind, source_kind) in checks.APPROVED_MEDIA.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            data = b"\x00\x00\x00\x18ftypisom" if name.endswith(".mp4") else b"\x89PNG\r\n\x1a\nfixture"
            path.write_bytes(data)
            entries.append({"path": name, "kind": kind, "sha256": sha256(data).hexdigest(), "source_kind": source_kind})
        self.write("assets/media-manifest.json", json.dumps({"entries": entries}))

    def test_reviewed_media_is_allowed(self):
        self.media()
        checks.check_media(self.root)

    def test_extra_media_is_rejected(self):
        self.media()
        self.write("assets/screenshots/extra.png", "unreviewed")
        with self.assertRaises(ValueError):
            checks.check_media(self.root)

    def test_changed_media_hash_is_rejected(self):
        self.media()
        (self.root / "assets/demo/poster.png").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            checks.check_media(self.root)

    def test_unreviewed_media_cannot_be_added_to_manifest(self):
        self.media()
        path = self.root / "assets/media-manifest.json"
        manifest = json.loads(path.read_text())
        manifest["entries"][0]["path"] = "assets/private.png"
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            checks.check_media(self.root)

    def test_mislabeled_media_source_is_rejected(self):
        self.media()
        path = self.root / "assets/media-manifest.json"
        manifest = json.loads(path.read_text())
        manifest["entries"][0]["source_kind"] = "synthetic-example"
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            checks.check_media(self.root)

    def test_force_added_tooling_output_is_rejected(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        self.write(".gitignore", "/output/\n")
        self.write("output/media-review/trace.txt", "tooling fixture")
        checks.check_tooling_untracked(self.root)
        subprocess.run(
            ["git", "-C", str(self.root), "add", "--force", "--", "output/media-review/trace.txt"],
            check=True,
        )
        with self.assertRaises(ValueError):
            checks.check_tooling_untracked(self.root)

    def test_force_added_original_media_is_rejected(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        self.write(".gitignore", "/截图与实录/\n")
        self.write("截图与实录/实拍.mp4", "original media fixture")
        checks.check_tooling_untracked(self.root)
        subprocess.run(
            ["git", "-C", str(self.root), "add", "--force", "--", "截图与实录/实拍.mp4"],
            check=True,
        )
        with self.assertRaises(ValueError):
            checks.check_tooling_untracked(self.root)

    def test_finder_metadata_is_ignored_locally_but_cannot_be_tracked(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        self.write(".gitignore", ".DS_Store\n")
        for name in (".DS_Store", "assets/.DS_Store"):
            self.write(name, "Finder metadata fixture")
        self.assertFalse(any(p.name == ".DS_Store" for p in checks.source_files(self.root)))
        checks.check_content(self.root)
        checks.check_tooling_untracked(self.root)
        for name in (".DS_Store", "assets/.DS_Store"):
            with self.subTest(name=name):
                subprocess.run(["git", "-C", str(self.root), "add", "--force", "--", name], check=True)
                with self.assertRaises(ValueError):
                    checks.check_tooling_untracked(self.root)
                subprocess.run(["git", "-C", str(self.root), "rm", "--cached", "--quiet", "--", name], check=True)
                self.assertTrue((self.root / name).is_file())

    def test_local_source_and_tooling_are_excluded_from_public_files(self):
        self.write("README.md", "public fixture")
        self.write("截图与实录/实拍.mp4", "original fixture")
        self.write("output/media-review/frame.png", "tooling fixture")
        self.assertEqual([str(p.relative_to(self.root)) for p in checks.source_files(self.root)], ["README.md"])

    def test_local_source_and_tooling_links_are_rejected(self):
        for name in ("截图与实录/实拍.mp4", "output/media-review/frame.png"):
            with self.subTest(name=name):
                self.write(name, "local fixture")
                self.write("README.md", f"[local]({name})")
                with self.assertRaises(ValueError):
                    checks.check_links(self.root)

    def test_removed_html_preview_cannot_return(self):
        for name in ("samples/report/report-preview.html", "scripts/render-report.mjs", "examples/report-display/render-report.test.mjs"):
            with self.subTest(name=name):
                path = self.write(name, "removed preview fixture")
                with self.assertRaises(ValueError):
                    checks.check_content(self.root)
                path.unlink()

    def test_valid_references_and_html_anchor(self):
        self.write("README.md", "[preview](samples/page.html#states) ![image](assets/figure.png)")
        self.write("samples/page.html", '<section id="states"><a href="../README.md">source</a></section>')
        self.write("assets/figure.png", "fixture")
        self.assertEqual(checks.check_links(self.root), 3)

    def test_broken_or_escaping_reference_is_rejected(self):
        for link in ("missing.md", "../outside.md", "samples/page.html#missing"):
            with self.subTest(link=link):
                self.write("README.md", f"[link]({link})")
                self.write("samples/page.html", '<section id="present"></section>')
                with self.assertRaises(ValueError):
                    checks.check_links(self.root)

    def test_empty_favicon_is_allowed(self):
        self.write("page.html", '<link rel="icon" href="data:,"><a href="README.md">source</a>')
        self.write("README.md", "Synthetic example")
        self.assertEqual(checks.check_links(self.root), 1)

    def test_other_data_links_are_rejected(self):
        for markup in (
            '<a href="data:,">link</a>',
            '<link rel="icon" href="data:text/html,content">',
            '<link rel="stylesheet" href="data:,">',
            '<img src="data:image/png;base64,content">',
        ):
            with self.subTest(markup=markup):
                self.write("page.html", markup)
                with self.assertRaises(ValueError):
                    checks.check_links(self.root)

    def test_sensitive_files_still_fail(self):
        for name in (".env", ".env.local", "dump.db", "data.sqlite3", "private.log", "key.pem", "archive.zip"):
            with self.subTest(name=name):
                path = self.write(name, "fixture")
                with self.assertRaises(ValueError):
                    checks.check_content(self.root)
                path.unlink()

    def test_sensitive_marker_and_key_are_rejected(self):
        for text in ("/".join(("", "xai", "private")), "-----BEGIN " + "PRIVATE KEY-----"):
            with self.subTest(text=text):
                self.write("README.md", text)
                with self.assertRaises(ValueError):
                    checks.check_content(self.root)


if __name__ == "__main__":
    unittest.main()
