# -*- coding: utf-8 -*-
"""Download TikTok oEmbed thumbnails into thumbs/{id}.jpg and write paths into videos.json."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DIR = Path(__file__).resolve().parent
JSON_PATH = DIR / "videos.json"
THUMBS = DIR / "thumbs"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"


def oembed_thumb(video_id: str, url: str) -> str:
    endpoint = "https://www.tiktok.com/oembed?url=" + urllib.parse.quote(url, safe="")
    req = urllib.request.Request(endpoint, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return (data.get("thumbnail_url") or "").strip()


def ytdlp_thumb(url: str) -> str:
    """Fallback when oEmbed has no thumbnail_url (TikTok dropped it in 2026)."""
    try:
        import yt_dlp
        from yt_dlp.networking.impersonate import ImpersonateTarget
    except ImportError:
        return ""
    opts = {"quiet": True, "no_warnings": True, "skip_download": True,
            "impersonate": ImpersonateTarget("safari", "18.0", "ios", "18.0")}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False) or {}
    except Exception as exc:
        print(f"  yt-dlp thumbnail lookup failed: {str(exc)[:160]}")
        return ""
    if info.get("thumbnail"):
        return str(info["thumbnail"])
    thumbs = [t for t in info.get("thumbnails") or [] if t.get("url")]
    return str(thumbs[-1]["url"]) if thumbs else ""


def download(src: str, dest: Path) -> None:
    req = urllib.request.Request(src, headers={"User-Agent": UA, "Referer": "https://www.tiktok.com/"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        dest.write_bytes(resp.read())
    try:
        from PIL import Image
        im = Image.open(dest).convert("RGB")
        im.thumbnail((480, 854), Image.Resampling.LANCZOS)
        im.save(dest, "JPEG", quality=72, optimize=True, progressive=True)
    except Exception:
        pass


def main() -> None:
    THUMBS.mkdir(exist_ok=True)
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    videos = payload.get("videos") or []
    ok = skip = fail = 0
    for i, v in enumerate(videos, 1):
        vid = str(v.get("id") or "")
        dest = THUMBS / f"{vid}.jpg"
        v["thumbnail"] = f"thumbs/{vid}.jpg"
        if dest.exists() and dest.stat().st_size > 1000:
            skip += 1
            print(f"[{i}/{len(videos)}] skip {vid}")
            continue
        try:
            url = v.get("url") or f"https://www.tiktok.com/@gerejayesussejati/video/{vid}"
            try:
                src = oembed_thumb(vid, url)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                src = ""
            src = src or ytdlp_thumb(url)
            if not src:
                raise RuntimeError("no thumbnail_url")
            download(src, dest)
            ok += 1
            print(f"[{i}/{len(videos)}] saved {vid} ({dest.stat().st_size} bytes)")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
            fail += 1
            v["thumbnail"] = ""
            print(f"[{i}/{len(videos)}] FAIL {vid}: {exc}")
        time.sleep(0.25)
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"done saved={ok} skipped={skip} failed={fail} total={len(videos)}")


if __name__ == "__main__":
    main()
