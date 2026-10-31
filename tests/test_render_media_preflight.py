import json
import tempfile
import unittest
from pathlib import Path

from scripts.render_media_preflight import check


class RenderPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "content.json"
        self.doc = {
            "editorial_status": "APPROVED",
            "media_rights_status": "VERIFIED",
            "publishing_status": "READY",
            "media": [{"commons_title": "File:Example_licensed_image.jpg"}],
        }

    def verify(self):
        self.path.write_text(json.dumps(self.doc), encoding="utf-8")
        check("content.json", root=self.root)

    def test_approved_commons_reference_passes_input_only(self):
        self.verify()

    def test_missing_editorial_approval_rejected(self):
        del self.doc["editorial_status"]
        with self.assertRaisesRegex(ValueError, "approval not proven editorial_status"):
            self.verify()

    def test_missing_rights_approval_rejected(self):
        self.doc["media_rights_status"] = "NOT_VERIFIED"
        with self.assertRaisesRegex(ValueError, "approval not proven media_rights_status"):
            self.verify()

    def test_unresolved_media_rejected(self):
        self.doc["media"] = []
        with self.assertRaisesRegex(ValueError, "no declared visual asset"):
            self.verify()


if __name__ == "__main__":
    unittest.main()
