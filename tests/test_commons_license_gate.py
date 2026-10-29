import hashlib
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_commons_licenses import check


class CommonsGateTests(unittest.TestCase):
    def test_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            media = root / "media" / "test"
            media.mkdir(parents=True)
            image = media / "01.jpg"
            image.write_bytes(b"test fixture")
            entry = {
                "commons_title": "File:Example.jpg",
                "source": "https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.jpg",
                "path": "media/test/01.jpg",
                "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                "metadata": {
                    "LicenseShortName": {"value": "CC BY-SA 4.0"},
                    "LicenseUrl": {"value": "https://creativecommons.org/licenses/by-sa/4.0/"},
                    "Artist": {"value": "Example author"},
                },
            }
            self.assertTrue(check(entry, root)[0])
            for field, replacement in [
                ("sha256", "0" * 64),
                ("source", "https://upload.wikimedia.org.evil.test/x.jpg"),
                ("path", "../outside.jpg"),
            ]:
                bad = dict(entry, **{field: replacement})
                self.assertFalse(check(bad, root)[0], field)
            for field, replacement in [
                ("LicenseShortName", {"value": "All rights reserved"}),
                ("LicenseUrl", {"value": "https://example.com/"}),
                ("Artist", {"value": ""}),
            ]:
                bad = dict(entry, metadata=dict(entry["metadata"], **{field: replacement}))
                self.assertFalse(check(bad, root)[0], field)


if __name__ == "__main__":
    unittest.main()
