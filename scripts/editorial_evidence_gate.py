#!/usr/bin/env python3
"""Read-only editorial evidence preflight; URL reachability is not fact checking."""
import argparse
import datetime as dt
import ipaddress
import json
from pathlib import Path
import socket
import sys
from urllib.parse import urlsplit

def public_https(url):
    if not isinstance(url, str):
        return False
    u = urlsplit(url)
    if u.scheme != "https" or not u.hostname or u.username or u.password or u.port not in (None, 443):
        return False
    try:
        results = socket.getaddrinfo(u.hostname, 443, type=socket.SOCK_STREAM)
        addresses = [ipaddress.ip_address(x[4][0]) for x in results]
    except (OSError, ValueError):
        return False
    return bool(addresses) and all(a.is_global for a in addresses)

def check_file(path, day):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("date") != day:
        raise ValueError("wrong date or JSON structure: " + str(path))
    sources = data.get("sources")
    media = data.get("media")
    if not isinstance(sources, list) or not sources:
        raise ValueError("missing source evidence: " + str(path))
    if not isinstance(media, list) or not media:
        raise ValueError("missing media evidence: " + str(path))
    for source in sources:
        if not isinstance(source, dict) or not source.get("name") or not public_https(source.get("url")):
            raise ValueError("invalid or non-public HTTPS source: " + str(path))
    for item in media:
        if not isinstance(item, dict) or not item.get("license_note"):
            raise ValueError("media license declaration missing: " + str(path))
        if not (item.get("commons_title") or item.get("flow_asset")):
            raise ValueError("media provenance missing: " + str(path))
    print("EVIDENCE_METADATA=PASS", path)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--profile", choices=("tal-dia", "tu-perro"), required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--input-dir", default="editorial/verified")
    args = p.parse_args()
    day = dt.date.fromisoformat(args.date).isoformat()
    suffixes = ("", "-detalle", "-sabias") if args.profile == "tal-dia" else ("", "-educacion", "-sabias")
    for suffix in suffixes:
        path = Path(args.input_dir) / (day + suffix + ".json")
        if not path.is_file():
            raise ValueError("missing editorial input: " + str(path))
        check_file(path, day)
    print("EVIDENCE_PREFLIGHT=PASS; FACT_CHECK=NOT_PERFORMED; LICENSE_VERIFICATION=NOT_PERFORMED; PUBLICATION=NONE")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print("EVIDENCE_PREFLIGHT=BLOCKED", str(e), file=sys.stderr)
        sys.exit(1)
