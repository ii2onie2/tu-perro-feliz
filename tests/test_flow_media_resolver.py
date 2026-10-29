#!/usr/bin/env python3
"""Offline resolver tests: provenance PASS is not render authorization."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "editorial/flow-assets/golden-retriever-20261028-intake.json"
meta = json.loads(MANIFEST.read_text(encoding="utf-8"))
asset = ROOT / meta["repository_asset_path"]
assert asset.is_file(), "imported JPEG missing"
assert hashlib.sha256(asset.read_bytes()).hexdigest() == meta["sha256"]
assert meta["rights_review"] == "PASS" and meta["visual_review"] == "PASS"
assert meta["render_authorized"] is False, "fixture must remain unapproved"

with tempfile.TemporaryDirectory() as td:
    tmp = pathlib.Path(td)

    def resolve(metadata, label):
        manifest = tmp / f"{label}-manifest.json"
        manifest.write_text(json.dumps(metadata), encoding="utf-8")
        content = tmp / f"{label}-content.json"
        content.write_text(json.dumps({
            "media": [{"flow_asset": {"manifest": str(manifest)}}]
        }), encoding="utf-8")
        dest = tmp / f"{label}-media"
        result = subprocess.run([
            sys.executable, str(ROOT / "scripts/fetch_media.py"),
            "--content", str(content), "--out", str(dest)
        ], cwd=ROOT, capture_output=True, text=True)
        return result, dest

    # Real manifest is not render-authorized despite provenance and visual PASS.
    denied, denied_dir = resolve(meta, "not-authorized")
    assert denied.returncode != 0, denied.stdout
    assert "Flow asset rendering not authorized" in denied.stderr, denied.stderr
    assert not (denied_dir / "credits.json").exists()

    for label, value in (("missing", None), ("string", "true"), ("numeric", 1)):
        incomplete = dict(meta)
        if label == "missing":
            incomplete.pop("render_authorized")
        else:
            incomplete["render_authorized"] = value
        result, _ = resolve(incomplete, label)
        assert result.returncode != 0, (label, result.stdout)
        assert "Flow asset rendering not authorized" in result.stderr, (label, result.stderr)

    # Isolated positive fixture tests the resolver, NOT real render approval.
    fixture_approved = dict(meta, render_authorized=True)
    accepted, accepted_dir = resolve(fixture_approved, "synthetic-test-only")
    assert accepted.returncode == 0, accepted.stderr
    files = list(accepted_dir.glob("*.jpg"))
    assert len(files) == 1, files
    assert hashlib.sha256(files[0].read_bytes()).hexdigest() == meta["sha256"]
    credits = json.loads((accepted_dir / "credits.json").read_text(encoding="utf-8"))
    assert credits[0]["source"] == "local_google_flow_asset"

    tampered = dict(fixture_approved, sha256="0" * 64)
    rejected, _ = resolve(tampered, "bad-hash")
    assert rejected.returncode != 0, rejected.stdout
    assert "SHA256 mismatch" in rejected.stderr, rejected.stderr

print("FLOW_RESOLVER_RENDER_AUTHORIZATION_TEST=PASS")
