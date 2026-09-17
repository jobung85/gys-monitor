# GYS TikTok Monitor

Public catalog of [tiktok.com/@gerejayesussejati](https://www.tiktok.com/@gerejayesussejati) videos from 1 January 2026.

Live site: **https://jobung85.github.io/gys-monitor/**

- Title, date, type, and direct link
- Thumbnail for each video
- Date / type / search filters
- “New” highlighting after you mark the current list as seen
- **Collect in Troopermonitor** — copies the video URL and, if Troopermonitor is installed on this PC, opens the app with that video queued

TikTok does not expose a public feed to browsers. The hosted page ships with the catalog in `videos.json`. To refresh it on your computer:

```
python watch_gys.py
python fetch_thumbnails.py
python generate_site.py
```
