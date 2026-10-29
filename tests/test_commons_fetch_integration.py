import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_media


class FakeResponse:
    def __init__(self, *, payload=None, body=b"valid image bytes", url=""):
        self.payload = payload
        self.content = body
        self.url = url

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, *, license_name="CC BY-SA 4.0", download_url=None, final_url=None):
        self.headers = {}
        self.license_name = license_name
        self.download_url = download_url or "https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.jpg"
        self.final_url = final_url or self.download_url

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    def get(self, url, params=None, timeout=None):
        if params is not None:
            return FakeResponse(payload={"query": {"pages": [{
                "ns": 6,
                "title": params["titles"],
                "imageinfo": [{
                    "url": self.download_url,
                    "extmetadata": {
                        "LicenseShortName": {"value": self.license_name},
                        "LicenseUrl": {"value": "https://creativecommons.org/licenses/by-sa/4.0/"},
                        "Artist": {"value": "Example photographer"},
                    },
                }],
            }]}})
        return FakeResponse(url=self.final_url)


class CommonsFetchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.original_cwd = Path.cwd()
        os.chdir(self.tmp.name)
        Path("content").mkdir()
        Path("media").mkdir()
        self.content_path = Path("content/2026-10-29.json")
        self.original = {"media": [{"commons_title": "File:Example.jpg"}]}
        self.content_path.write_text(json.dumps(self.original), encoding="utf-8")

    def tearDown(self):
        os.chdir(self.original_cwd)
        self.tmp.cleanup()

    def fetch(self, fake):
        with mock.patch.object(fetch_media.requests, "Session", return_value=fake):
            with mock.patch.object(sys, "argv", [
                "fetch_media.py", "--content", str(self.content_path), "--out", "media/episode"
            ]):
                fetch_media.main()

    def test_valid_commons_file_and_credits(self):
        self.fetch(FakeSession())
        stored = Path("media/episode/01.jpg")
        self.assertEqual(stored.read_bytes(), b"valid image bytes")
        credit = json.loads(Path("media/episode/credits.json").read_text())[0]
        self.assertEqual(credit["sha256"], hashlib.sha256(stored.read_bytes()).hexdigest())
        self.assertEqual(credit["path"], "media/episode/01.jpg")
        self.assertEqual(json.loads(self.content_path.read_text())["media"][0]["path"], credit["path"])

    def test_api_query_is_stripped_before_audited_download(self):
        canonical = "https://upload.wikimedia.org/wikipedia/commons/a/ab/Example.jpg"
        fake = FakeSession(download_url=canonical + "?token=untrusted", final_url=canonical)
        self.fetch(fake)
        credit = json.loads(Path("media/episode/credits.json").read_text())[0]
        self.assertEqual(credit["source"], canonical)
        self.assertNotIn("?", credit["source"])

    def test_unapproved_license_fails_without_publishing_media_or_content(self):
        with self.assertRaisesRegex(RuntimeError, "LICENSE_NOT_ALLOWLISTED"):
            self.fetch(FakeSession(license_name="All rights reserved"))
        self.assertFalse(Path("media/episode/01.jpg").exists())
        self.assertFalse(Path("media/episode/credits.json").exists())
        self.assertEqual(json.loads(self.content_path.read_text()), self.original)

    def test_redirected_download_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "redirected"):
            self.fetch(FakeSession(final_url="https://example.com/image.jpg"))
        self.assertFalse(Path("media/episode/credits.json").exists())

    def test_existing_media_conflict_fails_without_overwriting(self):
        directory = Path("media/episode")
        directory.mkdir()
        previous = directory / "01.jpg"
        previous.write_bytes(b"original bytes")
        with self.assertRaisesRegex(RuntimeError, "media collision"):
            self.fetch(FakeSession())
        self.assertEqual(previous.read_bytes(), b"original bytes")
        self.assertEqual(json.loads(self.content_path.read_text()), self.original)
        self.assertFalse((directory / "credits.json").exists())

    def test_off_domain_source_rejected_before_download(self):
        with self.assertRaisesRegex(RuntimeError, "non-Commons"):
            self.fetch(FakeSession(download_url="https://example.com/Example.jpg"))
        self.assertFalse(Path("media/episode/credits.json").exists())

    def test_non_commons_destination_rejected(self):
        with mock.patch.object(sys, "argv", [
            "fetch_media.py", "--content", str(self.content_path), "--out", "out"
        ]):
            with self.assertRaisesRegex(RuntimeError, "inside repository media"):
                fetch_media.main()


if __name__ == "__main__":
    unittest.main()
