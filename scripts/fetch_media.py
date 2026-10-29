#!/usr/bin/env python3
"""Fetch Commons images only after a fail-closed metadata/integrity audit.

This gate does not certify commercial rights or authorize publication.
Non-Commons assets require their own rights review.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

import requests

from audit_commons_licenses import check as check_commons_credit

API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {
    "User-Agent": "TuPerroFeliz/1.0 (https://github.com/ii2onie2/tu-perro-feliz)"
}
MAX_MEDIA_BYTES = 25 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def media_path(path, root):
    resolved = path.resolve()
    media_root = (root / "media").resolve()
    if not resolved.is_relative_to(media_root):
        raise RuntimeError("Commons output must be inside repository media/")
    return resolved.relative_to(root).as_posix()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", default="media")
    args = ap.parse_args()

    root = Path.cwd().resolve()
    content_path = Path(args.content)
    data = json.loads(content_path.read_text(encoding="utf-8"))
    items = data.get("media") or []
    if not isinstance(items, list) or not items:
        raise RuntimeError("Missing or invalid media list")
    out = Path(args.out)
    # The isolated Flow test passes an external temporary output directory;
    # Commons downloads are restricted to the controlled repository media/ tree.
    if any(isinstance(item, dict) and item.get("commons_title") is not None for item in items):
        media_path(out, root)
    out.mkdir(parents=True, exist_ok=True)
    pending = []

    # Stage all downloads; do not mutate declared content or published media
    # when any Commons image fails its validation.
    with TemporaryDirectory(prefix=".commons-staging-", dir=out) as tmp:
        staging = Path(tmp)
        with requests.Session() as session:
            session.headers.update(HEADERS)
            for index, item in enumerate(items, 1):
                if not isinstance(item, dict):
                    raise RuntimeError("Invalid media entry")
                local = item.get("flow_asset")
                if local is not None:
                    if not isinstance(local, dict) or not isinstance(local.get("manifest"), str):
                        raise ValueError("flow_asset must be an object with manifest")
                    manifest = Path(local["manifest"])
                    metadata = json.loads(manifest.read_text(encoding="utf-8"))
                    if (metadata.get("asset_status") != "IMPORTED"
                            or metadata.get("rights_review") != "PASS"
                            or metadata.get("visual_review") != "PASS"):
                        raise ValueError("Flow asset gate not passed")
                    if metadata.get("render_authorized") is not True:
                        raise ValueError("Flow asset rendering not authorized")
                    src = Path(metadata["repository_asset_path"])
                    if src.is_absolute() or ".." in src.parts or not src.is_file():
                        raise ValueError("Flow asset path invalid or missing")
                    if src.suffix.lower() not in ALLOWED_EXTENSIONS:
                        raise ValueError("Unsupported Flow asset extension")
                    payload_bytes = src.read_bytes()
                    if hashlib.sha256(payload_bytes).hexdigest() != metadata.get("sha256"):
                        raise ValueError("Flow asset SHA256 mismatch")
                    if not payload_bytes or len(payload_bytes) > MAX_MEDIA_BYTES:
                        raise ValueError("Flow media empty or exceeds size cap")
                    ext = src.suffix.lower()
                    staged_file = staging / f"{index:02d}{ext}"
                    staged_file.write_bytes(payload_bytes)
                    final_file = out / f"{index:02d}{ext}"
                    credit = {
                        "path": str(final_file),
                        "source": "local_google_flow_asset",
                        "manifest": str(manifest),
                        "sha256": metadata["sha256"],
                    }
                    pending.append((item, staged_file, final_file, credit))
                    continue

                title = item.get("commons_title")
                if title is None:
                    raise RuntimeError("Media source unresolved; no Flow manifest or Commons file title")
                if not isinstance(title, str) or not title.startswith("File:"):
                    raise RuntimeError(f"Invalid Commons title: {title!r}")
                params = {
                    "action": "query", "format": "json", "formatversion": "2",
                    "prop": "imageinfo", "iiprop": "url|extmetadata", "titles": title,
                }
                response = session.get(API, params=params, timeout=30)
                response.raise_for_status()
                try:
                    payload = response.json()
                except ValueError as exc:
                    raise RuntimeError(f"Invalid Commons API JSON for {title!r}") from exc
                pages = payload.get("query", {}).get("pages", [])
                if len(pages) != 1 or not pages[0].get("imageinfo"):
                    raise RuntimeError(f"No Commons imageinfo for {title!r}")
                page = pages[0]
                page_title = page.get("title", "")
                if page.get("ns") != 6 or page_title.replace("_", " ").casefold() != title.replace("_", " ").casefold():
                    raise RuntimeError(f"Commons title mismatch: {title!r}")
                info = page["imageinfo"][0]
                url = info.get("url", "")
                parsed = urlsplit(url)
                if (parsed.scheme != "https" or parsed.hostname != "upload.wikimedia.org"
                        or parsed.username or parsed.password or parsed.query or parsed.fragment
                        or not parsed.path.startswith("/wikipedia/commons/")):
                    raise RuntimeError("Rejected non-Commons media source URL:"
                        f" scheme={parsed.scheme!r} host={parsed.hostname!r}"
                        f" path_prefix={parsed.path[:90]!r}"
                        f" has_query={bool(parsed.query)} has_fragment={bool(parsed.fragment)}")
                ext = Path(parsed.path).suffix.lower()
                if ext not in ALLOWED_EXTENSIONS:
                    raise RuntimeError(f"Unsupported Commons media extension: {ext!r}")
                downloaded = session.get(url, timeout=60)
                downloaded.raise_for_status()
                final_url = getattr(downloaded, "url", url)
                if final_url != url:
                    raise RuntimeError("Commons download redirected; manual review required")
                payload_bytes = downloaded.content
                if not payload_bytes or len(payload_bytes) > MAX_MEDIA_BYTES:
                    raise RuntimeError("Commons media empty or exceeds safe size cap")
                staged_file = staging / f"{index:02d}{ext}"
                staged_file.write_bytes(payload_bytes)
                credit = {
                    "commons_title": title,
                    "path": media_path(staged_file, root),
                    "source": url,
                    "metadata": info.get("extmetadata", {}),
                    "sha256": hashlib.sha256(payload_bytes).hexdigest(),
                }
                ok, reason = check_commons_credit(credit, root=root)
                if not ok:
                    raise RuntimeError(f"Commons image rejected: {reason} ({title})")
                pending.append((item, staged_file, out / f"{index:02d}{ext}", credit))

        # Preserve existing valid files; never silently replace a conflicting asset.
        for _, _, final_file, credit in pending:
            if final_file.exists():
                if not final_file.is_file():
                    raise RuntimeError("Existing Commons destination is not a file")
                existing_sha = hashlib.sha256(final_file.read_bytes()).hexdigest()
                if existing_sha != credit["sha256"]:
                    raise RuntimeError(f"Existing Commons media collision: {final_file}")

        # Only commit downloaded media after every Commons item passes.
        credits = []
        for item, staged_file, final_file, credit in pending:
            if not final_file.exists():
                os.replace(staged_file, final_file)
            final_relative = (str(final_file) if credit.get("source") == "local_google_flow_asset"
                              else media_path(final_file, root))
            item["path"] = final_relative
            credit["path"] = final_relative
            credits.append(credit)

    # This is provenance evidence, not rights clearance for publication.
    (out / "credits.json").write_text(
        json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    content_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
