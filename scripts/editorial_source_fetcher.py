#!/usr/bin/env python3
"""Fetch public HTTPS editorial evidence without treating retrieval as fact checking."""
import argparse
import hashlib
import ipaddress
import json
from pathlib import Path
import socket
import ssl
import sys
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPSHandler, HTTPRedirectHandler, Request

MAX_BYTES = 512_000

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("redirects forbidden")

def validate_url(url):
    if not isinstance(url, str):
        raise ValueError("URL must be text")
    u = urlsplit(url)
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.port not in (None, 443):
        raise ValueError("HTTPS public host required")
    if u.hostname.endswith(".local") or u.hostname == "localhost":
        raise ValueError("local hostname forbidden")
    addresses = [ipaddress.ip_address(r[4][0]) for r in socket.getaddrinfo(u.hostname, 443, type=socket.SOCK_STREAM)]
    if not addresses or not all(a.is_global for a in addresses):
        raise ValueError("non-public address")
    return url

def fetch(url):
    validate_url(url)
    # DNS re-resolution between validation and connect is a residual SSRF risk.
    # Do not run with access to internal networks or privileged credentials.
    opener = build_opener(HTTPSHandler(context=ssl.create_default_context()), NoRedirect())
    request = Request(url, headers={"User-Agent": "EditorialEvidenceFetcher/0.1", "Accept": "text/html,text/plain,application/pdf"})
    with opener.open(request, timeout=12) as response:
        kind = response.headers.get_content_type()
        if kind not in ("text/html", "text/plain", "application/pdf"):
            raise ValueError("unsupported document type")
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("source exceeds byte limit")
        return {"url": url, "content_type": kind, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "retrieved": True}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path, help="Candidate JSON file")
    p.add_argument("--output", required=True, type=Path, help="Evidence manifest JSON")
    p.add_argument("--offline", action="store_true", help="Only check URL syntax; do not make network calls")
    args = p.parse_args()
    if args.output.exists():
        raise ValueError("refusing to overwrite evidence manifest")
    data = json.loads(args.input.read_text(encoding="utf-8"))
    claims = data.get("claims", [])
    if not isinstance(claims, list) or not claims:
        raise ValueError("no claims")
    urls = sorted({e["url"] for c in claims for e in c.get("evidence", [])})
    if not urls or len(urls) > 15:
        raise ValueError("source count outside bounds")
    manifest = []
    for url in urls:
        if args.offline:
            u = urlsplit(url)
            if u.scheme != "https" or not u.hostname or u.username or u.password:
                raise ValueError("invalid HTTPS URL")
            manifest.append({"url": url, "retrieved": False})
        else:
            manifest.append(fetch(url))
    result = {"documents": manifest, "fact_check": "NOT_PERFORMED", "license_check": "NOT_PERFORMED", "publication": "NONE"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("EVIDENCE_MANIFEST_CREATED=" + str(args.output), "FACT_CHECK=NOT_PERFORMED")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as e:
        print("SOURCE_FETCH=BLOCKED", e, file=sys.stderr)
        sys.exit(1)
