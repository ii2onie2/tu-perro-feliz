#!/usr/bin/env python3
"""No-network end-to-end resolver check using the already imported Google Flow JPEG."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"editorial/flow-assets/golden-retriever-20261028-intake.json"
meta=json.loads(MANIFEST.read_text(encoding="utf-8"))
asset=ROOT/meta["repository_asset_path"]
assert asset.is_file(), "imported JPEG missing"
assert hashlib.sha256(asset.read_bytes()).hexdigest()==meta["sha256"], "original hash mismatch"
assert meta["rights_review"]=="PASS" and meta["visual_review"]=="PASS"
with tempfile.TemporaryDirectory() as td:
    tmp=pathlib.Path(td)
    payload={"media":[{"flow_asset":{"manifest":str(MANIFEST)}}]}
    content=tmp/"content.json"
    content.write_text(json.dumps(payload),encoding="utf-8")
    dest=tmp/"media"
    subprocess.run([sys.executable,str(ROOT/"scripts/fetch_media.py"),"--content",str(content),"--out",str(dest)],cwd=ROOT,check=True)
    files=list(dest.glob("*.jpg"))
    assert len(files)==1, files
    assert hashlib.sha256(files[0].read_bytes()).hexdigest()==meta["sha256"]
    credits=json.loads((dest/"credits.json").read_text(encoding="utf-8"))
    assert credits[0]["source"]=="local_google_flow_asset"
    # Negative test: tampered hash must fail closed.
    broken=dict(meta,sha256="0"*64)
    bad_manifest=tmp/"bad_manifest.json"
    bad_manifest.write_text(json.dumps(broken),encoding="utf-8")
    bad_content=tmp/"bad_content.json"
    bad_content.write_text(json.dumps({"media":[{"flow_asset":{"manifest":str(bad_manifest)}}]}),encoding="utf-8")
    result=subprocess.run([sys.executable,str(ROOT/"scripts/fetch_media.py"),"--content",str(bad_content),"--out",str(tmp/"bad-media")],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode!=0 and "SHA256 mismatch" in result.stderr, result.stderr
print("FLOW_RESOLVER_OFFLINE_TEST=PASS")
