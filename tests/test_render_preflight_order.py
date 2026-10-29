#!/usr/bin/env python3
"""Offline safety invariant: reject missing content before heavyweight setup."""
from pathlib import Path
import re

workflow = Path(".github/workflows/render.yml").read_text(encoding="utf-8")
steps = re.split(r"(?=^      - name: )", workflow, flags=re.MULTILINE)
names = []
by_name = {}
for step in steps:
    match = re.match(r"^      - name: ([^\n]+)", step)
    if match:
        name = match.group(1)
        names.append(name)
        by_name[name] = step

expected = [
    "Resolve content files",
    "Set up Python",
    "Validate content quality",
    "Install FFmpeg and fonts",
    "Install Python dependencies and Piper",
    "Download Spanish Piper voice",
    "Render all resolved content files",
]
assert all(name in by_name for name in expected), names
assert [names.index(name) for name in expected] == sorted(names.index(name) for name in expected), names
assert "id: content" in by_name["Resolve content files"]
assert 'if [ "$MISSING" -ne 0 ]; then' in by_name["Resolve content files"]
assert "exit 1" in by_name["Resolve content files"]
assert 'test -s "$FILE"' in by_name["Resolve content files"]
assert "scripts/validate_content.py" in by_name["Validate content quality"]
for name in ("Set up Python", "Validate content quality", "Install FFmpeg and fonts",
             "Install Python dependencies and Piper", "Download Spanish Piper voice"):
    assert "if: steps.content.outputs.files != ''" in by_name[name], name
assert "No changed daily editorial JSON; skip rendering" in by_name["Resolve content files"]
print("RENDER_PREFLIGHT_FAIL_FAST_ORDER=PASS")
