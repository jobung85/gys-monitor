# -*- coding: utf-8 -*-
"""Poll @gerejayesussejati and refresh videos.json for the local monitor."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DIR = Path(__file__).resolve().parent
JSON_PATH = DIR / "videos.json"
CONFIG_PATH = DIR / "tiktok_config.json"
# Legacy hard-coded location (Microsoft Store Python 3.13) — still tried as a fallback
LEGACY_YTDLP = (
    Path.home()
    / "AppData/Local/Packages/PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0"
    / "LocalCache/local-packages/Python313/Scripts/yt-dlp.exe"
)
DEFAULT_ACCOUNT = "gerejayesussejati"
# yt-dlp TikTok extraction breaks often; warn when the installed build is older than this
YTDLP_MAX_AGE_DAYS = 60


def load_watch_config() -> dict:
    """Optional keys in tiktok_config.json: "watch_account", "ytdlp_path"."""
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


_CFG = load_watch_config()
ACCOUNT = (os.environ.get("GYS_ACCOUNT") or _CFG.get("watch_account") or DEFAULT_ACCOUNT).lstrip("@")
PROFILE = f"https://www.tiktok.com/@{ACCOUNT}"
# Catalog covers posts from this date on (YYYY-MM-DD)
CATALOG_START = os.environ.get("GYS_SINCE") or _CFG.get("catalog_start") or "2026-01-01"
HASH_RE = re.compile(r"#\S+")
REPLY_RE = re.compile(r"^Replying to @([A-Za-z0-9._]+)\s*", re.I)


def ytdlp_bin() -> str:
    """Config/env path → yt-dlp on PATH → legacy Store-Python path → "yt-dlp"."""
    configured = os.environ.get("YTDLP_PATH") or _CFG.get("ytdlp_path") or ""
    if configured and Path(configured).expanduser().exists():
        return str(Path(configured).expanduser())
    found = shutil.which("yt-dlp")
    if found:
        return found
    if LEGACY_YTDLP.exists():
        return str(LEGACY_YTDLP)
    return "yt-dlp"


def check_ytdlp_version(binary: str) -> None:
    """Print the yt-dlp version and warn if it looks stale (versions are dates)."""
    try:
        out = subprocess.run([binary, "--version"], capture_output=True, text=True,
                             encoding="utf-8", timeout=30).stdout.strip()
    except Exception as e:
        print(f"Could not run yt-dlp --version: {e}", file=sys.stderr)
        return
    print("yt-dlp", out or "?")
    m = re.match(r"(\d{4})\.(\d{2})\.(\d{2})", out)
    if m:
        built = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        age = (datetime.now() - built).days
        if age > YTDLP_MAX_AGE_DAYS:
            print(f"WARNING: yt-dlp is {age} days old — TikTok often breaks old builds. "
                  'Update with: pip install -U "yt-dlp[default,curl-cffi]"', file=sys.stderr)


def tiktok_id_to_datetime(video_id: str) -> datetime | None:
    """TikTok video IDs carry the post time: upper 32 bits = unix seconds."""
    try:
        ts = int(str(video_id).strip()) >> 32
    except (TypeError, ValueError):
        return None
    if ts < 1451606400 or ts > datetime.now().timestamp() + 86400:
        return None
    return datetime.fromtimestamp(ts)


def classify(caption: str, reply_to: str) -> str:
    if "kenalanyuk" in caption.lower():
        return "Kenalan Yuk"
    if reply_to:
        return "Q&A Reply"
    return "Other"


def parse_line(line: str) -> dict | None:
    """
    Line format: upload_date \t timestamp \t id \t description.
    Flat-playlist often prints "NA" for upload_date/timestamp, so fall back to
    timestamp, then to the date encoded in the video ID.
    Old 3-field lines (date \t id \t desc) are still accepted.
    """
    parts = line.split("\t", 3)
    if len(parts) == 4:
        date_s, ts_s, vid, desc = parts
    elif len(parts) == 3:
        date_s, vid, desc = parts
        ts_s = ""
    else:
        return None
    if not vid.isdigit():
        return None
    dt = None
    if date_s.isdigit() and len(date_s) == 8:
        dt = datetime.strptime(date_s, "%Y%m%d")
    elif ts_s.isdigit():
        dt = datetime.fromtimestamp(int(ts_s))
    else:
        dt = tiktok_id_to_datetime(vid)
    if dt is None:
        return None
    caption = " ".join(desc.split()).strip()
    reply_m = REPLY_RE.match(caption)
    reply_to = reply_m.group(1) if reply_m else ""
    tags = HASH_RE.findall(caption)
    title = " ".join(HASH_RE.sub("", caption).split()).strip()
    return {
        "date": dt.strftime("%Y-%m-%d"),
        "year": dt.year,
        "month": dt.strftime("%Y-%m"),
        "month_name": dt.strftime("%B"),
        "id": vid,
        "title": title,
        "caption": caption,
        "hashtags": " ".join(tags),
        "url": f"https://www.tiktok.com/@{ACCOUNT}/video/{vid}",
        "type": classify(caption, reply_to),
        "reply_to": reply_to,
        "thumbnail": f"thumbs/{vid}.jpg",
    }


def load_existing(path: Path | None = None) -> dict:
    path = path or JSON_PATH
    if not path.exists():
        return {"videos": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"videos": []}
    if isinstance(data, list):
        return {"videos": data}
    return data if isinstance(data, dict) else {"videos": []}


def _line(e: dict) -> str:
    def s(v):
        return "NA" if v in (None, "") else str(v)
    desc = " ".join(str(e.get("description") or e.get("title") or "").split())
    return f"{s(e.get('upload_date'))}\t{s(e.get('timestamp'))}\t{s(e.get('id'))}\t{desc}"


def _fetch_lines_api() -> list[str]:
    """In-process yt-dlp (works inside the frozen Troopermonitor.exe)."""
    import yt_dlp
    from yt_dlp.networking.impersonate import ImpersonateTarget

    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "impersonate": ImpersonateTarget("safari", "18.0", "ios", "18.0"),
    }
    print("yt-dlp", yt_dlp.version.__version__, "(module)")
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(PROFILE, download=False)
    return [_line(e) for e in (info or {}).get("entries") or [] if isinstance(e, dict)]


def _fetch_lines_cli() -> list[str]:
    binary = ytdlp_bin()
    check_ytdlp_version(binary)
    cmd = [binary, "--impersonate", "Safari-18.0:Ios-18.0", "--flat-playlist", "--print",
           "%(upload_date)s\t%(timestamp)s\t%(id)s\t%(description)s", PROFILE]
    kw = {}
    if sys.platform == "win32":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", **kw)
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or "").strip().splitlines()[-5:])
        raise RuntimeError(f"yt-dlp failed with code {proc.returncode}: {tail}")
    return proc.stdout.splitlines()


def fetch() -> list[dict]:
    """Latest posts of the account, newest first, from CATALOG_START on."""
    print("Fetching", PROFILE, "...", flush=True)
    try:
        lines = _fetch_lines_api()
    except ImportError:
        lines = _fetch_lines_cli()
    rows = [r for r in (parse_line(ln.strip()) for ln in lines) if r]
    rows = [r for r in rows if r["date"] >= CATALOG_START]
    if not rows:
        raise RuntimeError("yt-dlp returned no videos (TikTok may be blocking this network)")
    rows.sort(key=lambda r: (r["date"], r["id"]), reverse=True)
    return rows


def merge(previous: list[dict], fetched: list[dict]) -> tuple[list[dict], list[dict]]:
    """Keep existing entries untouched, add fetched ones not seen before; newest first."""
    by_id = {str(v.get("id")): v for v in previous if v.get("id")}
    new_rows = [r for r in fetched if r["id"] not in by_id]
    for r in new_rows:
        by_id[r["id"]] = r
    videos = sorted(by_id.values(), key=lambda r: (str(r.get("date") or ""), str(r.get("id"))), reverse=True)
    for i, r in enumerate(videos, 1):
        r["no"] = i
    return videos, new_rows


def build_payload(videos: list[dict], previous: dict | None = None) -> dict:
    previous = previous or {}
    return {
        "account": ACCOUNT,
        "displayName": previous.get("displayName") or "Gereja Yesus Sejati Official",
        "profile": PROFILE,
        "builtAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "rangeStart": videos[-1]["date"] if videos else "",
        "rangeEnd": videos[0]["date"] if videos else "",
        "count": len(videos),
        "videos": videos,
    }


def refresh_catalog(base: dict | None = None, out_path: Path | None = None,
                    write_unchanged: bool = True) -> tuple[dict, list[dict]]:
    """Fetch + merge into `base` (default: videos.json next to this script) and write out_path.
    With write_unchanged=False the file is left alone when nothing new was found."""
    out_path = out_path or JSON_PATH
    previous = base if base is not None else load_existing(out_path)
    videos, new_rows = merge(list(previous.get("videos") or []), fetch())
    payload = build_payload(videos, previous)
    if not new_rows and not write_unchanged and previous.get("videos") and out_path.exists():
        return payload, new_rows
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, out_path)
    return payload, new_rows


def main() -> None:
    previous = load_existing()
    first = not previous.get("videos")
    # Leave videos.json untouched when nothing is new (keeps the scheduled job's commits clean)
    payload, new_rows = refresh_catalog(previous, write_unchanged=False)
    if first or new_rows:
        print(f"Wrote {payload['count']} videos to {JSON_PATH}")
    if first:
        print("First catalog. Open index.html and click Mark current as seen.")
    elif new_rows:
        print(f"NEW: {len(new_rows)} video(s)")
        for r in new_rows:
            print(f"  {r['date']}  {r['title'][:90]}")
            print(f"           {r['url']}")
    else:
        print("No new videos.")
    if "--serve" in sys.argv:
        os.chdir(DIR)
        print("Serving http://127.0.0.1:8765/  (Ctrl+C to stop)")
        from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

        ThreadingHTTPServer(("127.0.0.1", 8765), SimpleHTTPRequestHandler).serve_forever()


if __name__ == "__main__":
    main()
