#!/usr/bin/env python3
"""Prepare daily editorial packages from verified inputs, without fabricating facts."""
import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PROFILES = {
    "tal-dia": (("", "Tal Día Como Hoy", "10:00"), ("-detalle", "El detalle que casi nadie ve", "16:00"), ("-sabias", "¿Sabías esto de España?", "19:00")),
    "tu-perro": (("", "Tu perro feliz", "10:00"), ("-educacion", "Buenos modales", "16:00"), ("-sabias", "¿Sabías esto de tu perro?", "19:00")),
}
REQUIRED = ("series", "title", "date", "slot", "hook", "narration", "caption", "hashtags", "sources", "media", "cta")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, choices=PROFILES)
    parser.add_argument("--date", required=True)
    parser.add_argument("--input-dir", default="editorial/verified")
    parser.add_argument("--output-dir", default="content")
    parser.add_argument("--commit", action="store_true", help="Write only after all three inputs pass validation")
    args = parser.parse_args()
    day = dt.date.fromisoformat(args.date).isoformat()
    sources = []
    targets = []
    for suffix, series, slot in PROFILES[args.profile]:
        src = Path(args.input_dir) / (day + suffix + ".json")
        dst = Path(args.output_dir) / (day + suffix + ".json")
        if not src.is_file() or dst.exists():
            raise SystemExit("BLOCKED_MISSING_SOURCE_OR_EXISTING_TARGET=" + str(src))
        obj = json.loads(src.read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or any(not obj.get(k) for k in REQUIRED):
            raise SystemExit("BLOCKED_INCOMPLETE_EDITORIAL=" + str(src))
        if (obj["date"], obj["series"], obj["slot"]) != (day, series, slot):
            raise SystemExit("BLOCKED_WRONG_DATE_SERIES_SLOT=" + str(src))
        if not isinstance(obj["sources"], list) or not all(isinstance(s, dict) and s.get("url", "").startswith("https://") for s in obj["sources"]):
            raise SystemExit("BLOCKED_UNVERIFIED_SOURCE_FORMAT=" + str(src))
        if not isinstance(obj["media"], list) or not obj["media"]:
            raise SystemExit("BLOCKED_MISSING_MEDIA=" + str(src))
        sources.append(src)
        targets.append(dst)
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for i, src in enumerate(sources):
            path = Path(tmp) / targets[i].name
            path.write_bytes(src.read_bytes())
            paths.append(str(path))
        subprocess.run([sys.executable, "scripts/validate_content.py", *paths], check=True)
    if not args.commit:
        print("EDITORIAL_PREFLIGHT=PASS; FILES=3; WRITES=0; BUFFER_REQUESTS=0")
        return
    for src, dst in zip(sources, targets):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        print("STAGED=" + str(dst))
    print("EDITORIAL_STAGED=3; BUFFER_REQUESTS=0; TIKTOK_PUBLICATIONS=0")

if __name__ == "__main__":
    main()
