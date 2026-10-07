#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Madrid")


def api(method, path, payload=None):
    base = os.environ["TRYPOST_BASE_URL"].rstrip("/")
    token = os.environ["TRYPOST_API_KEY"]
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base + "/api" + path,
        data=data,
        method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "github-actions-trypost-publisher/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"{method} {path} -> HTTP {exc.code}: {body}") from exc


def post_platforms(post):
    return post.get("post_platforms") or post.get("platforms") or []


def account_id_from_platform(p):
    return (
        p.get("social_account_id")
        or (p.get("social_account") or {}).get("id")
        or (p.get("account") or {}).get("id")
    )


def iter_posts(max_pages=5):
    for page in range(1, max_pages + 1):
        _, body = api("GET", f"/posts?page={page}")
        if isinstance(body, list):
            for item in body:
                yield item
            return
        items = (body or {}).get("data", [])
        for item in items:
            yield item
        meta = (body or {}).get("meta", {})
        if not items or page >= int(meta.get("last_page", page)):
            return


def already_exists(account_id, when_iso, content):
    target_minute = when_iso[:16]
    for post in iter_posts():
        scheduled = str(post.get("scheduled_at") or "")
        same_time = scheduled[:16] == target_minute
        same_content = (post.get("content") or "").strip() == content.strip()
        same_account = any(account_id_from_platform(p) == account_id for p in post_platforms(post))
        if same_account and same_time:
            print(f"EXISTS: post {post.get('id')} already targets {target_minute}")
            return True
        if same_account and same_content and scheduled:
            print(f"EXISTS: same content already scheduled as post {post.get('id')} at {scheduled}")
            return True
    return False


def validate_account(account_id):
    _, accounts = api("GET", "/social-accounts")
    if not isinstance(accounts, list):
        raise RuntimeError("Unexpected /social-accounts response")
    matches = [a for a in accounts if a.get("id") == account_id]
    if len(matches) != 1:
        raise RuntimeError(f"Configured TikTok account id {account_id} not found exactly once")
    account = matches[0]
    if account.get("platform") != "tiktok":
        raise RuntimeError(f"Configured account is {account.get('platform')}, not tiktok")
    if account.get("status") != "connected":
        raise RuntimeError(f"TikTok account is not connected: {account.get('status')}")
    if account.get("is_active") is False:
        raise RuntimeError("TikTok account is inactive")


def schedule_one(account_id, caption_file, video_file, date_str, time_str, repo_slug):
    caption = Path(caption_file).read_text(encoding="utf-8").strip()
    video_path = Path(video_file)
    if not caption:
        raise RuntimeError(f"Empty caption: {caption_file}")
    if not video_path.is_file() or video_path.stat().st_size == 0:
        print(f"WAIT: missing/empty video {video_file}")
        return False

    local_dt = datetime.fromisoformat(f"{date_str}T{time_str}:00").replace(tzinfo=TZ)
    now = datetime.now(TZ)
    if local_dt <= now:
        print(f"SKIP_PAST: {local_dt.isoformat()}")
        return False

    when_iso = local_dt.isoformat()
    if already_exists(account_id, when_iso, caption):
        return True

    meta = {
        "privacy_level": "PUBLIC_TO_EVERYONE",
        "allow_comments": True,
        "allow_duet": True,
        "allow_stitch": True,
        "auto_add_music": False,
        "is_aigc": True,
    }
    payload = {
        "status": "draft",
        "content": caption,
        "platforms": [{
            "social_account_id": account_id,
            "content_type": "tiktok_video",
            "meta": meta,
        }],
    }

    post_id = None
    try:
        _, post = api("POST", "/posts", payload)
        post_id = post["id"]
        platforms = post_platforms(post)
        if not platforms:
            raise RuntimeError("TryPost created a draft without a post platform")
        platform_id = platforms[0].get("id")
        if not platform_id:
            raise RuntimeError("TryPost post platform has no id")

        media_url = f"https://raw.githubusercontent.com/{repo_slug}/main/{video_file}"
        _, attached = api("POST", f"/posts/{post_id}/media/from-url", {
            "urls": [{"url": media_url}]
        })
        failures = (attached or {}).get("failures") or []
        failed_urls = (attached or {}).get("failed_urls") or []
        if failures or failed_urls:
            raise RuntimeError(f"Media attach failed: failures={failures} failed_urls={failed_urls}")

        _, scheduled = api("PUT", f"/posts/{post_id}", {
            "status": "scheduled",
            "scheduled_at": when_iso,
        })
        status = (scheduled or {}).get("status")
        if status != "scheduled":
            raise RuntimeError(f"Unexpected scheduled status: {status}")
        print(f"SCHEDULED: {post_id} -> {when_iso}")
        return True
    except Exception:
        if post_id:
            try:
                api("DELETE", f"/posts/{post_id}")
                print(f"ROLLBACK: deleted incomplete draft {post_id}")
            except Exception as cleanup_error:
                print(f"ROLLBACK_WARNING: {cleanup_error}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--slot", action="append", required=True,
                        help="HH:MM|caption_path|video_path")
    args = parser.parse_args()

    required = ["TRYPOST_BASE_URL", "TRYPOST_API_KEY", "TRYPOST_TIKTOK_ACCOUNT_ID"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        print("TRYPOST_NOT_CONFIGURED: missing " + ",".join(missing))
        return 0

    account_id = os.environ["TRYPOST_TIKTOK_ACCOUNT_ID"]
    validate_account(account_id)

    ok = True
    for spec in args.slot:
        time_str, caption_file, video_file = spec.split("|", 2)
        try:
            schedule_one(account_id, caption_file, video_file, args.date, time_str, args.repo)
        except Exception as exc:
            ok = False
            print(f"ERROR {time_str}: {exc}", file=sys.stderr)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
