#!/usr/bin/env python3
"""Offline Wikimedia Commons metadata gate; never authorizes publication.

Only explicitly supported CC licenses are accepted. Public-domain claims,
unknown terms and missing checksums need manual review and fail closed.
"""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

CC_LICENSES = {
    "cc by 2.0": "/licenses/by/2.0",
    "cc by 3.0": "/licenses/by/3.0",
    "cc by 4.0": "/licenses/by/4.0",
    "cc by sa 3.0": "/licenses/by-sa/3.0",
    "cc by sa 4.0": "/licenses/by-sa/4.0",
}
CC0_PATH = "/publicdomain/zero/1.0"


def plain(value):
    if isinstance(value, dict):
        value = value.get("value")
    if not isinstance(value, str):
        return ""
    return html.unescape(re.sub(r"<[^>]*>", "", value)).strip()


def norm(value):
    return re.sub(r"[\s_-]+", " ", plain(value).casefold()).strip()


def parsed_url(value):
    if not isinstance(value, str):
        return None
    try:
        url = urlsplit(value)
        if url.port is not None:
            return None
    except ValueError:
        return None
    if url.username or url.password or url.query or url.fragment:
        return None
    return url


def check(entry, root=Path(".")):
    if not isinstance(entry, dict):
        return False, "INVALID_CREDIT_RECORD"
    title = entry.get("commons_title")
    if not isinstance(title, str) or not title.startswith("File:") or not title[5:].strip():
        return False, "INVALID_COMMONS_TITLE"

    source = parsed_url(entry.get("source"))
    if (source is None or source.scheme != "https"
            or source.hostname != "upload.wikimedia.org"
            or not source.path.startswith("/wikipedia/commons/")
            or len(source.path) <= len("/wikipedia/commons/")
            or ".." in unquote(source.path).split("/")):
        return False, "INVALID_COMMONS_SOURCE"

    metadata = entry.get("metadata")
    if not isinstance(metadata, dict):
        return False, "MISSING_LICENSE_METADATA"
    name = norm(metadata.get("LicenseShortName"))
    license_url = parsed_url(plain(metadata.get("LicenseUrl")))
    if name in CC_LICENSES:
        expected = CC_LICENSES[name]
    elif name in ("cc0", "cc0 1.0"):
        expected = CC0_PATH
    else:
        return False, "LICENSE_NOT_ALLOWLISTED"
    if (license_url is None or license_url.scheme not in ("http", "https")
            or license_url.hostname != "creativecommons.org"
            or license_url.path.rstrip("/") != expected):
        return False, "LICENSE_URL_MISMATCH"
    if not (plain(metadata.get("Artist")) or plain(metadata.get("Credit"))):
        return False, "ATTRIBUTION_MISSING"

    rel = entry.get("path")
    if not isinstance(rel, str) or not rel:
        return False, "MEDIA_PATH_MISSING"
    path = Path(rel)
    if path.is_absolute() or not path.parts or path.parts[0] != "media" or ".." in path.parts:
        return False, "INVALID_MEDIA_PATH"
    root = root.resolve()
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root / "media"):
        return False, "INVALID_MEDIA_PATH"
    if not resolved.is_file() or resolved.stat().st_size == 0:
        return False, "MEDIA_FILE_MISSING_OR_EMPTY"

    declared = entry.get("sha256")
    if not isinstance(declared, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", declared):
        return False, "MEDIA_SHA256_MISSING_OR_INVALID"
    digest = hashlib.sha256()
    with resolved.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != declared.lower():
        return False, "MEDIA_SHA256_MISMATCH"
    return True, "PASS_METADATA_AND_INTEGRITY_ONLY"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("credits", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        data = json.loads(args.credits.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"FAIL_INVALID_CREDITS: {exc}") from exc
    if not isinstance(data, list) or not data:
        raise SystemExit("FAIL_EMPTY_CREDITS")
    failed = False
    for entry in data:
        ok, reason = check(entry, root=args.root)
        title = entry.get("commons_title", "") if isinstance(entry, dict) else ""
        print(f"{reason}: {title}")
        failed = failed or not ok
    if failed:
        raise SystemExit(1)
    print("PASS_METADATA_ONLY_NOT_RIGHTS_OR_PUBLICATION_CLEARANCE")


if __name__ == "__main__":
    main()
