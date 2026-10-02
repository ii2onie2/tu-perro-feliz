#!/usr/bin/env python3
import json, pathlib, sys

SERIES = {
    "Tu perro feliz": "10:00",
    "Buenos modales": "16:00",
    "¿Sabías esto de tu perro?": "19:00",
}

def fail(msg):
    print("CONTENT_CHECK=FAIL:", msg)
    raise SystemExit(1)

files = sys.argv[1:]
if not files:
    fail("no content files")

for name in files:
    p = pathlib.Path(name)
    d = json.loads(p.read_text(encoding="utf-8"))
    for key in ["series","title","date","slot","hook","narration","caption","hashtags","sources","media","cta"]:
        if key not in d:
            fail(f"{name}: missing {key}")
    if d["series"] not in SERIES:
        fail(f"{name}: unknown series")
    if d["slot"] != SERIES[d["series"]]:
        fail(f"{name}: slot must be {SERIES[d['series']]}")
    if len(d["narration"].split()) < 65:
        fail(f"{name}: narration too short")
    if len(d["narration"]) > 3600:
        fail(f"{name}: narration too long")
    if not d["hook"].strip():
        fail(f"{name}: empty hook")
    if not d["hashtags"]:
        fail(f"{name}: no hashtags")
    if not d["sources"]:
        fail(f"{name}: no sources")
    if not d["media"]:
        fail(f"{name}: no media declared")
    if "Sígu" not in d["cta"] and "Sigue" not in d["cta"]:
        fail(f"{name}: CTA missing follow request")
    print(f"CONTENT_CHECK=PASS {name}")
