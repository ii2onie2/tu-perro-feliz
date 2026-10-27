#!/usr/bin/env python3
"""Offline regression tests; no network, file promotion or publishing."""
import json
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = pathlib.Path(__file__).with_name("check_editorial_proposal.py").resolve()
DAY = "2030-01-01"
BASE = {
    "date": DAY, "series": "Tu perro feliz", "title": "Test title",
    "slot": "10:00", "hook": "Test hook", "narration": "Test narration",
    "caption": "Test caption", "hashtags": ["#Test"],
    "sources": [{"name": "Example", "url": "https://example.org/reference"}],
    "media": [{"commons_title": "File:Example.jpg", "license_note": "Review required"}],
    "cta": "Sigue para más"
}
with tempfile.TemporaryDirectory() as temp:
    root = pathlib.Path(temp)
    (root / "content").mkdir()
    (root / "editorial" / "approved").mkdir(parents=True)
    path = root / (DAY + ".json")
    def check(data, expected):
        path.write_text(json.dumps(data), encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), str(path)], cwd=root, capture_output=True, text=True)
        assert (result.returncode == 0) == expected, (result.stdout, result.stderr)
    check(BASE, True)
    check({**BASE, "date": "2030-01-02"}, False)
    check({**BASE, "sources": []}, False)
    check({**BASE, "sources": [{"name": "Fake", "url": "http://example.org"}]}, False)
    check({**BASE, "media": []}, False)
    check({**BASE, "hook": ""}, False)
    check(BASE, True)
    (root / "content" / (DAY + ".json")).write_text("{}")
    check(BASE, False)
print("PROPOSAL_REGRESSION=PASS; CASES=8; NETWORK=NONE; PUBLICATION=NONE")
