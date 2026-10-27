#!/usr/bin/env python3
"""Offline tests for fail-closed editorial staging; no publishing or network."""
import json
import pathlib
import subprocess
import sys
import tempfile

SCRIPT = pathlib.Path(__file__).with_name("stage_daily_content.py").resolve()
DATE = "2026-10-28"

def call(queue, output, dry=False):
    args=[sys.executable,str(SCRIPT),"--date",DATE,"--queue",str(queue),"--output",str(output)]
    if dry: args.append("--dry-run")
    return subprocess.run(args,capture_output=True,text=True)

with tempfile.TemporaryDirectory() as tmp:
    root=pathlib.Path(tmp)
    queue=root/"approved"
    output=root/"content"
    queue.mkdir()
    assert call(queue,output,True).returncode==2
    assert not output.exists()
    source=queue/(DATE+".json")
    source.write_text(json.dumps({"date":"2026-10-27","sources":[{"url":"https://example.org"}],"media":[{"role":"test"}]}))
    assert call(queue,output,True).returncode==4
    assert not output.exists()
    source.write_text(json.dumps({"date":DATE,"sources":[],"media":[{"role":"test"}]}))
    assert call(queue,output,True).returncode==5
    source.write_text(json.dumps({"date":DATE,"sources":[{"url":"https://example.org"}],"media":[]}))
    assert call(queue,output,True).returncode==6
    source.write_text(json.dumps({"date":DATE,"sources":[{"url":"https://example.org"}],"media":[{"role":"test"}]}))
    assert call(queue,output,True).returncode==0
    assert not output.exists()
    output.mkdir()
    (output/(DATE+".json")).write_text("{}")
    assert call(queue,output,True).returncode==3
print("OFFLINE_STAGING_TESTS=PASS")
print("NETWORK=NONE; BUFFER_MUTATIONS=0; TIKTOK_PUBLICATIONS=0")
