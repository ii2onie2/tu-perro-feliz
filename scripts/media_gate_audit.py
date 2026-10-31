#!/usr/bin/env python3
"""Fail-closed, read-only media/editorial audit. No downloads or publishing."""
import argparse
import hashlib
import json
import pathlib
import re
import sys

SHA = re.compile(r"^[0-9a-f]{64}$")
VARIANTS = {"tal_dia": {"principal", "detalle", "sabias"}, "tu_perro": {"principal", "educacion", "sabias"}}

def audit(day, channel):
    errors = []
    script_path = pathlib.Path("editorial/research") / (day + "-scripts.json")
    manifest_path = pathlib.Path("editorial/research/media-manifest.json")
    report = {"date": day, "channel": channel, "status": "BLOCKED", "variants": [], "errors": errors}
    try:
        data = json.loads(script_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append("Missing or invalid input: " + str(exc))
        return report
    entries = manifest.get("medias")
    if not isinstance(entries, list) or not entries:
        errors.append("Manifest medias missing or empty")
        return report
    by_path = {}
    for media in entries:
        if not isinstance(media, dict):
            errors.append("Invalid manifest entry")
            continue
        name = media.get("filename")
        if not isinstance(name, str) or not re.fullmatch(r"media/images/[A-Za-z0-9_.-]+\.(jpg|jpeg|png)", name):
            errors.append("Invalid local media path: " + repr(name))
            continue
        if name in by_path:
            errors.append("Duplicate manifest entry: " + name)
        by_path[name] = media
        expected = media.get("sha256")
        if not isinstance(expected, str) or not SHA.fullmatch(expected):
            errors.append("Invalid SHA256: " + name)
        path = pathlib.Path(name)
        if not path.is_file() or path.is_symlink():
            errors.append("Missing or symlinked local media: " + name)
        else:
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                errors.append("SHA256 mismatch: " + name + " expected=" + str(expected) + " actual=" + actual)
        for field in ("license", "author", "source_url", "attribution_required", "rights_verified_by", "rights_verified_date"):
            value = media.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append("Missing rights metadata " + field + ": " + name)
        if media.get("rights_status") != "VERIFIED":
            errors.append("Rights not verified: " + name)
    scripts = data.get("scripts")
    if not isinstance(scripts, list) or len(scripts) != 3:
        errors.append("Exactly 3 scripts required")
        return report
    slots = [s.get("slot") for s in scripts if isinstance(s, dict)]
    if len(slots) != 3 or set(slots) != VARIANTS[channel]:
        errors.append("Unexpected or duplicate variants: " + repr(slots))
    for s in scripts:
        if not isinstance(s, dict):
            errors.append("Invalid script entry")
            continue
        slot = s.get("slot")
        image = s.get("background_image")
        digest = s.get("background_image_sha256")
        item = {"slot": slot, "background_image": image, "render_authorized": s.get("render_authorized", data.get("render_authorized", False)), "buffer_authorized": s.get("buffer_authorized", data.get("buffer_authorized", False))}
        report["variants"].append(item)
        if not isinstance(s.get("narration"), str) or not s["narration"].strip():
            errors.append("Missing narration: " + str(slot))
        if image not in by_path:
            errors.append("Image not in manifest: " + str(slot) + " " + repr(image))
        elif digest != by_path[image].get("sha256"):
            errors.append("Script/manifest SHA mismatch: " + str(slot))
        if data.get("render_authorized") is not True or item["render_authorized"] is not True:
            errors.append("Render authorization missing: " + str(slot))
        if item["render_authorized"] is not True:
            print("SKIP: render_authorized=false pour " + str(slot) + ", attente approbation éditoriale")
        if data.get("buffer_authorized") is not True or item["buffer_authorized"] is not True:
            errors.append("Buffer authorization missing: " + str(slot))
        if item["buffer_authorized"] is not True:
            print("SKIP: buffer_authorized=false pour " + str(slot) + ", attente approbation éditoriale")
    if data.get("fact_check") != "COMPLETED" or data.get("media_rights") != "VERIFIED" or data.get("status") != "APPROVED":
        errors.append("Editorial fact-check, rights, or approval incomplete")
    if not errors:
        report["status"] = "MEDIA_VERIFIED_EDITORIAL_APPROVED"
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--channel", required=True, choices=sorted(VARIANTS))
    args = parser.parse_args()
    if not re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", args.date):
        sys.exit("Invalid date")
    result = audit(args.date, args.channel)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "MEDIA_VERIFIED_EDITORIAL_APPROVED" else 1)
