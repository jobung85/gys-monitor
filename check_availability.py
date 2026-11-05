# -*- coding: utf-8 -*-
"""Check each catalog video against TikTok and mark clear unavailability.

Detection (preferred order):
1. Fetch the public video page (desktop Chrome UA, then iPhone UA).
2. Parse __UNIVERSAL_DATA_FOR_REHYDRATION__ → webapp.video-detail.
   - statusCode 0 + itemStruct  → available
   - statusCode in known set / statusMsg like status_deleted → unavailable
3. If the page is a mobile-style SSR without video-detail, fall back to
   presence of itemStruct for this id.
4. WAF interstitial ("Please wait..."), short bodies, HTTP errors, timeouts,
   and rate limits are recorded as check failures (available left unchanged /
   null) — never as unavailable.

A video is only marked available=false after UNAVAILABLE_CONFIRM_RUNS
consecutive clear unavailable results. The first hit sets available=null
(pending confirmation) and increments unavailableStreak.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DIR = Path(__file__).resolve().parent
JSON_PATH = DIR / "videos.json"

UA_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
UA_MOBILE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)

# TikTok webapp.video-detail status codes that mean the post is not public.
# 10204: deleted / does not exist (statusMsg often "status_deleted" or
#        "item doesn't exist"). Note: yt-dlp mislabels 10204 as an IP block;
#        we trust statusMsg + missing itemStruct instead.
# 10215: content violation / removed
# 10216: private post
# 10217: friends-only / restricted
# 10222: private account
UNAVAILABLE_STATUS_CODES = {10204, 10215, 10216, 10217, 10222}
UNAVAILABLE_STATUS_MSGS = {
    "status_deleted",
    "item doesn't exist",
    "item doesn\u2019t exist",
}

UNAVAILABLE_CONFIRM_RUNS = int(os.environ.get("GYS_UNAVAIL_CONFIRM", "2"))
DEFAULT_DELAY = float(os.environ.get("GYS_AVAIL_DELAY", "1.2"))
REQUEST_TIMEOUT = float(os.environ.get("GYS_AVAIL_TIMEOUT", "45"))

UNIVERSAL_RE = re.compile(
    r'<script[^>]+id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
    re.S,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def video_url(v: dict) -> str:
    if v.get("url"):
        return str(v["url"])
    account = "gerejayesussejati"
    return f"https://www.tiktok.com/@{account}/video/{v.get('id')}"


def fetch_html(url: str, ua: str) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return int(resp.status), body


def parse_detail(html: str) -> dict[str, Any] | None:
    """Return webapp.video-detail dict, or None if not present."""
    m = UNIVERSAL_RE.search(html)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    detail = (data.get("__DEFAULT_SCOPE__") or {}).get("webapp.video-detail")
    return detail if isinstance(detail, dict) else None


def classify_html(html: str, video_id: str) -> dict[str, Any]:
    """Classify a fetched page. state ∈ {available, unavailable, unknown}."""
    if not html:
        return {"state": "unknown", "reason": "empty_body"}
    if "Please wait" in html and len(html) < 5000:
        return {"state": "unknown", "reason": "waf_interstitial", "bytes": len(html)}

    # Tiny pages without embedded catalog data are usually a WAF/challenge shell.
    if len(html) < 5000 and "__UNIVERSAL_DATA_FOR_REHYDRATION__" not in html:
        return {"state": "unknown", "reason": "short_body", "bytes": len(html)}

    detail = parse_detail(html)
    if detail is not None:
        code = detail.get("statusCode")
        try:
            code_i = int(code) if code is not None else None
        except (TypeError, ValueError):
            code_i = None
        msg = str(detail.get("statusMsg") or "").strip()
        item = ((detail.get("itemInfo") or {}).get("itemStruct") or {})
        has_item = bool(item.get("id"))
        msg_l = msg.lower()
        if code_i == 0 and has_item:
            return {
                "state": "available",
                "statusCode": code_i,
                "statusMsg": msg,
                "via": "video-detail",
            }
        if (
            code_i in UNAVAILABLE_STATUS_CODES
            or msg_l in UNAVAILABLE_STATUS_MSGS
            or (code_i not in (None, 0) and not has_item)
        ):
            return {
                "state": "unavailable",
                "statusCode": code_i,
                "statusMsg": msg,
                "via": "video-detail",
            }
        return {
            "state": "unknown",
            "reason": "ambiguous_detail",
            "statusCode": code_i,
            "statusMsg": msg,
            "hasItem": has_item,
        }

    # Mobile-style SSR: no webapp.video-detail. itemStruct for this id ⇒ available.
    item_re = re.compile(
        rf'"itemStruct"\s*:\s*\{{\s*"id"\s*:\s*"{re.escape(str(video_id))}"'
    )
    if item_re.search(html):
        return {"state": "available", "via": "itemStruct"}
    if '"itemStruct"' not in html and len(html) > 80000:
        # Large page with no item at all is a strong unavailable signal on mobile SSR.
        return {"state": "unavailable", "via": "no_itemStruct", "bytes": len(html)}
    return {"state": "unknown", "reason": "no_video_detail", "bytes": len(html)}


def probe_video(url: str, video_id: str) -> dict[str, Any]:
    last_err: dict[str, Any] | None = None
    for ua_name, ua in (("desktop", UA_DESKTOP), ("mobile", UA_MOBILE)):
        try:
            status, html = fetch_html(url, ua)
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            last_err = {
                "state": "unknown",
                "reason": f"http_{exc.code}",
                "ua": ua_name,
                "bytes": len(body),
            }
            # 404 on the page itself is a clear miss.
            if exc.code == 404:
                return {
                    "state": "unavailable",
                    "statusCode": 404,
                    "statusMsg": "http_404",
                    "via": "http",
                    "ua": ua_name,
                }
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_err = {
                "state": "unknown",
                "reason": "network",
                "ua": ua_name,
                "error": type(exc).__name__,
            }
            continue
        result = classify_html(html, video_id)
        result["ua"] = ua_name
        result["http"] = status
        if result["state"] != "unknown":
            return result
        last_err = result
    return last_err or {"state": "unknown", "reason": "no_attempt"}


def apply_result(video: dict, result: dict[str, Any], now: str) -> str:
    """Mutate video availability fields. Returns a short outcome label."""
    video["lastChecked"] = now
    state = result.get("state")
    streak = int(video.get("unavailableStreak") or 0)

    if state == "available":
        video["available"] = True
        video["unavailableSince"] = None
        video["unavailableStreak"] = 0
        video.pop("availabilityReason", None)
        return "available"

    if state == "unavailable":
        streak += 1
        video["unavailableStreak"] = streak
        reason = (
            f"statusCode={result.get('statusCode')} "
            f"statusMsg={result.get('statusMsg')!r} via={result.get('via')}"
        )
        video["availabilityReason"] = reason.strip()
        if streak >= UNAVAILABLE_CONFIRM_RUNS:
            if video.get("available") is not False:
                video["unavailableSince"] = video.get("unavailableSince") or now
            video["available"] = False
            return "unavailable"
        # Pending confirmation — do not claim unavailable yet.
        video["available"] = None
        return "pending"

    # unknown / check failed: keep prior available + unavailableSince + streak.
    video["availabilityReason"] = (
        f"check_failed:{result.get('reason') or 'unknown'}"
        + (f" ua={result.get('ua')}" if result.get("ua") else "")
    )
    if "available" not in video:
        video["available"] = None
    return "unknown"


def check_catalog(
    payload: dict,
    *,
    delay: float = DEFAULT_DELAY,
    limit: int | None = None,
    only_ids: set[str] | None = None,
    force_confirm: bool = False,
) -> dict[str, int]:
    """Check videos in payload. Returns counters."""
    global UNAVAILABLE_CONFIRM_RUNS
    confirm_was = UNAVAILABLE_CONFIRM_RUNS
    if force_confirm:
        UNAVAILABLE_CONFIRM_RUNS = 1
    videos = list(payload.get("videos") or [])
    if only_ids:
        targets = [v for v in videos if str(v.get("id")) in only_ids]
    else:
        targets = videos
    if limit is not None:
        targets = targets[:limit]

    counts = {"available": 0, "unavailable": 0, "pending": 0, "unknown": 0}
    now = utc_now_iso()
    total = len(targets)
    try:
        for i, v in enumerate(targets, 1):
            vid = str(v.get("id") or "")
            url = video_url(v)
            print(f"[{i}/{total}] {vid} ...", flush=True)
            result = probe_video(url, vid)
            outcome = apply_result(v, result, now)
            counts[outcome] = counts.get(outcome, 0) + 1
            extra = ""
            if result.get("statusCode") is not None:
                extra = f" code={result.get('statusCode')} msg={result.get('statusMsg')!r}"
            elif result.get("reason"):
                extra = f" reason={result.get('reason')}"
            print(f"  → {outcome}{extra}", flush=True)
            if i < total and delay > 0:
                time.sleep(delay)
    finally:
        UNAVAILABLE_CONFIRM_RUNS = confirm_was

    payload["availabilityCheckedAt"] = now
    return counts


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", type=Path, default=JSON_PATH, help="Path to videos.json")
    p.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--ids", nargs="*", default=None, help="Only check these video ids")
    p.add_argument(
        "--force-confirm",
        action="store_true",
        help="Treat a single unavailable hit as confirmed (for local testing)",
    )
    p.add_argument("--dry-run", action="store_true", help="Do not write videos.json")
    args = p.parse_args(argv)

    path: Path = args.json
    payload = json.loads(path.read_text(encoding="utf-8"))
    only = set(args.ids) if args.ids else None
    counts = check_catalog(
        payload,
        delay=args.delay,
        limit=args.limit,
        only_ids=only,
        force_confirm=args.force_confirm,
    )
    if not args.dry_run:
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        print(f"Wrote {path}")
    print(
        "done "
        f"available={counts.get('available', 0)} "
        f"unavailable={counts.get('unavailable', 0)} "
        f"pending={counts.get('pending', 0)} "
        f"unknown={counts.get('unknown', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
