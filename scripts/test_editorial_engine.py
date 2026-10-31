#!/usr/bin/env python3
"""Offline, dependency-free editorial engine contract tests."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ENGINE = pathlib.Path(__file__).with_name("editorial_engine.py")
PROFILE = sys.argv[1] if len(sys.argv) > 1 else "tal-dia"
sys.argv = sys.argv[:1]
SUFFIXES = ("", "-detalle", "-sabias") if PROFILE == "tal-dia" else ("", "-educacion", "-sabias")
SERIES = ("Tal Día Como Hoy", "El detalle que casi nadie ve", "¿Sabías esto de España?") if PROFILE == "tal-dia" else ("Tu perro feliz", "Buenos modales", "¿Sabías esto de tu perro?")
SLOTS = ("10:00", "16:00", "19:00")
DAY = "2026-11-02"

class EditorialContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.input = self.root / "verified"
        self.output = self.root / "content"
        self.input.mkdir()
        for suffix, series, slot in zip(SUFFIXES, SERIES, SLOTS):
            obj = {"series": series, "title": "Contenido de prueba", "date": DAY, "slot": slot,
                   "hook": "Prueba editorial", "narration": " ".join(["Texto de prueba"] * 100),
                   "caption": "Prueba", "hashtags": ["#Prueba"], "sources": [{"name": "Test", "url": "https://example.org/test"}],
                   "media": [{"commons_title": "File:Example.jpg"}], "cta": "Síguenos para más",
                   "duration_target": "65-80s"}
            (self.input / (DAY + suffix + ".json")).write_text(json.dumps(obj), encoding="utf-8")

    def run_engine(self, commit=False):
        cmd = [sys.executable, str(ENGINE), "--profile", PROFILE, "--date", DAY,
               "--input-dir", str(self.input), "--output-dir", str(self.output)]
        if commit:
            cmd.append("--commit")
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_dry_run_has_no_writes(self):
        result = self.run_engine()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.output.exists())

    def test_missing_input_fails_closed(self):
        (self.input / (DAY + SUFFIXES[1] + ".json")).unlink()
        self.assertNotEqual(self.run_engine(commit=True).returncode, 0)
        self.assertFalse(self.output.exists())

    def test_wrong_date_fails_closed(self):
        path = self.input / (DAY + ".json")
        data = json.loads(path.read_text())
        data["date"] = "2026-11-01"
        path.write_text(json.dumps(data))
        self.assertNotEqual(self.run_engine(commit=True).returncode, 0)
        self.assertFalse(self.output.exists())

    def test_commit_stages_three(self):
        result = self.run_engine(commit=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(list(self.output.glob("*.json"))), 3)
        self.assertNotEqual(self.run_engine(commit=True).returncode, 0)

if __name__ == "__main__":
    unittest.main()
