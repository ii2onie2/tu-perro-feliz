"""Offline regression: render must never silently produce a black video."""
from pathlib import Path

source = Path("scripts/render.py").read_text(encoding="utf-8")
assert 'RENDER_BLOCKED_NO_MEDIA' in source
assert 'RENDER_BLOCKED_UNSAFE_MEDIA' in source
assert 'resolved.is_relative_to(media_root)' in source
assert 'resolved.is_file()' in source
assert 'resolved.stat().st_size == 0' in source
assert 'bgs=bgs[:5]' in source
assert 'if bgs:' in source
assert 'color=c=0x111111' not in source, "Black background fallback remains enabled"
print("NO_BLACK_FALLBACK=PASS")
