# GYS TikTok Monitor

Public catalog of [tiktok.com/@gerejayesussejati](https://www.tiktok.com/@gerejayesussejati) videos from 1 January 2026.

Live site: **https://jobung85.github.io/gys-monitor/**

- Title, date, type, and direct link
- Thumbnail for each video
- Date / type / search filters
- “New” highlighting after you mark the current list as seen

TikTok does not expose a public feed to browsers. The hosted page ships with the catalog in `videos.json`. To refresh it on your computer:

```
python watch_gys.py
python fetch_thumbnails.py
python generate_site.py
```

## Availability badges

On GitHub Actions, `generate_site.py` automatically runs `check_availability.py` before rebuilding the page (local runs skip this unless `GYS_RUN_AVAIL=1`). Each video page is fetched (desktop Chrome UA, then iPhone UA) and classified:

- Prefer TikTok's embedded `webapp.video-detail`: `statusCode` 0 + `itemStruct` → available; clear codes such as 10204 (`status_deleted` / item missing), 10215–10217 / 10222 (private / restricted) → unavailable candidate
- On mobile-style SSR without `video-detail`, presence of `itemStruct` for that id → available; a large page with no `itemStruct` → unavailable candidate
- WAF interstitials ("Please wait..."), short bodies, HTTP 403/5xx, and timeouts → check failed (`available` left unchanged / null); **never** recorded as unavailable

A video is only marked `available: false` after **two consecutive** clear unavailable results (override with `GYS_UNAVAIL_CONFIRM` or `--force-confirm`). When a video returns, the badge clears. The site greys unavailable cards out, shows an **Unavailable** badge, and offers a **Hide unavailable** filter. Fields added to each entry (backward compatible for the desktop app merge-by-`id`): `available`, `lastChecked`, `unavailableSince`, plus `unavailableStreak` for the confirm counter.

```
python check_availability.py          # check all
python check_availability.py --ids 7700868891966295297 --force-confirm
```

