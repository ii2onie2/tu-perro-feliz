"""Behavioral regression for the no-black-video media gate (offline)."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest import mock

spec = importlib.util.spec_from_file_location("renderer", "scripts/render.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

class FakePiper:
    returncode = 0
    def __init__(self, *args, **kwargs):
        pass
    def communicate(self, text):
        return ("", "")

def exercise(media, files=None, expected=None):
    files = files or {}
    with tempfile.TemporaryDirectory() as directory:
        old = os.getcwd()
        try:
            os.chdir(directory)
            Path("media").mkdir()
            for name, payload in files.items():
                target = Path("media") / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
            Path("input.json").write_text(json.dumps({
                "narration": "Prueba segura.", "media": media
            }), encoding="utf-8")
            with mock.patch.object(sys, "argv", ["render.py", "--content", "input.json", "--voice-model", "mock.onnx"]), \
                 mock.patch.object(renderer.subprocess, "Popen", FakePiper), \
                 mock.patch.object(renderer, "probe_duration", return_value=10.0), \
                 mock.patch.object(renderer, "run") as ffmpeg:
                if expected:
                    try:
                        renderer.main()
                    except SystemExit as exc:
                        assert expected in str(exc), (expected, exc)
                    else:
                        raise AssertionError(f"Expected rejection: {expected}")
                    ffmpeg.assert_not_called()
                else:
                    renderer.main()
                    assert ffmpeg.call_count == 1, "Approved visual must reach FFmpeg"
                    assert ffmpeg.call_args.args[0][0] == "ffmpeg"
        finally:
            os.chdir(old)

exercise([], expected="RENDER_BLOCKED_NO_MEDIA")
exercise([{}], expected="RENDER_BLOCKED_NO_MEDIA")
exercise([{"path": "media/missing.jpg"}], expected="RENDER_BLOCKED_NO_MEDIA")
exercise([{"path": "media/empty.jpg"}], {"empty.jpg": b""}, "RENDER_BLOCKED_NO_MEDIA")
exercise([{"path": "../outside.jpg"}], expected="RENDER_BLOCKED_UNSAFE_MEDIA")
exercise([{"path": "/tmp/outside.jpg"}], expected="RENDER_BLOCKED_UNSAFE_MEDIA")
exercise([{"path": "media/file.txt"}], {"file.txt": b"not an image"}, "RENDER_BLOCKED_UNSAFE_MEDIA")
exercise([{"path": "media/valid.png"}], {"valid.png": b"test fixture"})
# Legacy P3.11 uses media=[] and must be updated to provide a local visual fixture.
# This test explicitly preserves the rejection contract until that workflow is corrected.
print("NO_BLACK_FALLBACK_BEHAVIOR=PASS")
