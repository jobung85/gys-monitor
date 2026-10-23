# -*- coding: utf-8 -*-
"""Build the local monitor page and the publishable artifact HTML."""
from __future__ import annotations

import json
from pathlib import Path

DIR = Path(__file__).resolve().parent
DATA = json.loads((DIR / "videos.json").read_text(encoding="utf-8"))
EMBED = json.dumps(DATA, ensure_ascii=False)

CSS = r"""
:root {
  --ink: #0f2942;
  --muted: #5b7a94;
  --paper: #eaf5ff;
  --sheet: #ffffff;
  --rule: #cfe3f4;
  --sky: #0284c7;
  --sky-deep: #0369a1;
  --sky-soft: #dbeafe;
  --amber: #b45309;
  --amber-soft: #fff7ed;
  --live: #0284c7;
  --focus: #0284c7;
  --header: rgba(255, 255, 255, 0.9);
  --banner: linear-gradient(105deg, #7dd3fc 0%, #e0f2fe 42%, #ffffff 100%);
  --shadow: 0 12px 32px rgba(14, 116, 144, 0.1);
  --sans: "Plus Jakarta Sans", "Segoe UI", system-ui, sans-serif;
  --mono: "JetBrains Mono", ui-monospace, monospace;
  --radius: 16px;
}
* { box-sizing: border-box; }
html { color-scheme: light; }
body {
  margin: 0;
  background:
    radial-gradient(1200px 420px at 10% -10%, #ccebff 0%, transparent 55%),
    radial-gradient(900px 380px at 100% 0%, #dbeafe 0%, transparent 50%),
    var(--paper);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 15px;
  line-height: 1.5;
}
.topbar {
  position: sticky;
  top: env(safe-area-inset-top, 0px);
  z-index: 20;
  backdrop-filter: blur(16px);
  background: var(--header);
  border-bottom: 1px solid var(--rule);
}
.topbar-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}
.mark {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, #38bdf8, #0284c7);
  font-size: 16px;
  box-shadow: 0 8px 18px rgba(2, 132, 199, 0.28);
}
.brand-copy { min-width: 0; }
.brand-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.brand-name {
  font-weight: 800;
  font-size: 14px;
  letter-spacing: -0.02em;
}
.badge {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--sky-deep);
  background: var(--sky-soft);
  border: 1px solid var(--rule);
  border-radius: 6px;
  padding: 2px 6px;
}
.brand-sub {
  margin: 0;
  font-size: 11px;
  color: var(--muted);
}
.radar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--rule);
  background: var(--sky-soft);
  color: var(--live);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
}
.pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--sky);
  box-shadow: 0 0 0 0 color-mix(in srgb, var(--sky) 70%, transparent);
  animation: ping 1.6s ease-out infinite;
}
@keyframes ping {
  0% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--sky) 55%, transparent); }
  70% { box-shadow: 0 0 0 8px transparent; }
  100% { box-shadow: 0 0 0 0 transparent; }
}
.wrap {
  max-width: 1280px;
  margin: 0 auto;
  padding-inline: 16px;
  padding-block: 20px 64px;
  display: grid;
  gap: 16px;
}
.mast {
  overflow: hidden;
  background: var(--sheet);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}
.hero {
  height: 112px;
  background: var(--banner);
  position: relative;
}
.hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, var(--sheet), transparent 70%);
}
.live-chip {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 700;
  color: var(--sky-deep);
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--rule);
}
.mast-body {
  padding: 0 20px 20px;
  display: grid;
  gap: 14px;
}
.ident {
  display: flex;
  align-items: end;
  gap: 14px;
  margin-top: -36px;
  position: relative;
}
.avatar {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  border: 3px solid var(--sheet);
  background: linear-gradient(135deg, #38bdf8, #0369a1);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 18px;
  flex-shrink: 0;
}
h1 {
  margin: 0;
  font-size: clamp(1.2rem, 2.4vw, 1.55rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  text-wrap: balance;
}
.handle {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--muted);
}
.lede {
  margin: 0;
  max-width: 70ch;
  color: var(--muted);
  font-size: 14px;
}
.profile {
  color: var(--sky);
  font-weight: 600;
  text-decoration: none;
}
.profile:hover { text-decoration: underline; }
.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}
.stat {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: var(--paper);
  border: 1px solid var(--rule);
  border-radius: 12px;
  padding: 12px 14px;
}
.stat b {
  font-family: var(--mono);
  font-size: 1.25rem;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  color: var(--ink);
  line-height: 1;
}
.stat:nth-child(2) b { color: var(--sky-deep); }
.stat span {
  font-size: 11px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--muted);
}
.banner {
  margin: 0;
  padding: 14px 16px;
  background: var(--sky-soft);
  color: var(--ink);
  font-size: 14px;
  border-radius: 12px;
  border: 1px solid var(--rule);
}
.banner[data-kind="alert"] {
  background: #dbeafe;
  color: var(--sky-deep);
  font-weight: 600;
}
.banner[data-kind="ok"] {
  background: #f0f9ff;
  color: var(--sky-deep);
}
.banner[hidden] { display: none !important; }
.filters {
  display: grid;
  gap: 14px;
  background: var(--sheet);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  padding: 16px 18px;
  box-shadow: var(--shadow);
}
.row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: end;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
}
input, select, button {
  font: inherit;
  color: var(--ink);
}
input[type="search"], input[type="date"], select {
  background: var(--paper);
  border: 1px solid var(--rule);
  border-radius: 12px;
  padding: 8px 12px;
  min-height: 40px;
  min-width: 0;
}
input[type="search"] { width: min(100%, 340px); }
input:focus, select:focus, button:focus-visible {
  outline: 2px solid var(--focus);
  outline-offset: 2px;
}
.presets { display: flex; flex-wrap: wrap; gap: 8px; }
.chip, button {
  background: var(--paper);
  border: 1px solid var(--rule);
  border-radius: 12px;
  padding: 8px 12px;
  cursor: pointer;
  color: var(--ink);
}
.chip[aria-pressed="true"] {
  background: var(--sky-soft);
  border-color: var(--sky);
  color: var(--sky-deep);
}
.chip:hover, button:hover {
  border-color: var(--sky);
}
.actions { display: flex; flex-wrap: wrap; gap: 8px; }
.primary {
  background: var(--sky);
  color: #ffffff;
  border-color: var(--sky);
  font-weight: 700;
}
.primary:hover { filter: brightness(1.06); color: #ffffff; }
.ghost { color: var(--muted); }
.meta-line {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: var(--muted);
  font-family: var(--mono);
}
.list {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}
.item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 0 0 12px;
  background: var(--sheet);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  color: inherit;
  box-shadow: var(--shadow);
  min-width: 0;
  overflow: hidden;
}
.item.is-new {
  border-color: var(--sky);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--sky) 25%, transparent);
}
.thumb {
  position: relative;
  display: block;
  aspect-ratio: 9 / 12;
  background: linear-gradient(180deg, #bae6fd, #e0f2fe);
  overflow: hidden;
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.thumb .play {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: linear-gradient(to top, rgba(15, 41, 66, 0.35), transparent 50%);
  color: #fff;
  font-size: 28px;
  opacity: 0.92;
}
.item-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 0 12px;
}
.when {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-family: var(--mono);
  font-size: 11px;
  font-variant-numeric: tabular-nums;
  color: var(--muted);
}
.when b {
  font-family: var(--sans);
  font-size: 13px;
  color: var(--ink);
  font-weight: 700;
}
.body h2 {
  font-size: 0.98rem;
  font-weight: 700;
  margin: 0;
  text-wrap: pretty;
  color: var(--ink);
  letter-spacing: -0.02em;
}
.body h2 a {
  color: inherit;
  text-decoration: none;
}
.body h2 a:hover { color: var(--sky-deep); }
.flags { display: flex; flex-wrap: wrap; gap: 6px; }
.flag {
  font-size: 10px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-weight: 700;
  border: 1px solid var(--rule);
  border-radius: 999px;
  padding: 3px 8px;
  color: var(--muted);
}
.flag.new {
  border-color: transparent;
  background: var(--sky);
  color: #ffffff;
}
.flag.kind-qa {
  border-color: color-mix(in srgb, var(--sky) 30%, var(--rule));
  background: color-mix(in srgb, var(--sky) 10%, transparent);
  color: var(--sky);
}
.flag.kind-kenalan {
  border-color: color-mix(in srgb, var(--amber) 30%, var(--rule));
  background: var(--amber-soft);
  color: var(--amber);
}
.linkrow {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--rule);
  background: var(--paper);
  border-radius: 12px;
  padding: 8px 10px;
}
.linkrow code {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--sky);
}
.copy {
  flex-shrink: 0;
  border: 0;
  background: transparent;
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 6px;
  border-radius: 8px;
}
.copy.done { color: var(--sky-deep); }
.foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--rule);
}
.open {
  font-size: 12px;
  font-weight: 700;
  color: var(--sky);
  text-decoration: none;
}
.open:hover { text-decoration: underline; }
.empty {
  padding: 28px 8px;
  color: var(--muted);
  grid-column: 1 / -1;
}
.note {
  margin: 4px 0 0;
  padding: 16px 18px;
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  background: var(--sheet);
  color: var(--muted);
  font-size: 13px;
  max-width: none;
}
@media (max-width: 980px) {
  .list { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 800px) {
  .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .list { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}
"""

JS = r"""
const CATALOG = window.__GYS__;
const SEEN_KEY = "gys-seen-ids-v1";
const LAST_KEY = "gys-last-visit-v1";
let videos = (CATALOG && CATALOG.videos) ? CATALOG.videos.slice() : [];
let liveNote = "";

function $(id) { return document.getElementById(id); }

function readSeen() {
  try {
    const raw = localStorage.getItem(SEEN_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) { return []; }
}
function writeSeen(ids) {
  try { localStorage.setItem(SEEN_KEY, JSON.stringify(ids)); } catch (e) {}
}
function readLast() {
  try { return localStorage.getItem(LAST_KEY) || ""; } catch (e) { return ""; }
}
function writeLast() {
  try { localStorage.setItem(LAST_KEY, new Date().toISOString()); } catch (e) {}
}

function fmtDay(iso) {
  const [y, m, d] = iso.split("-");
  const dt = new Date(Number(y), Number(m) - 1, Number(d));
  const mon = dt.toLocaleString("en", { month: "short" }).toUpperCase();
  return { d, mon, y };
}

function uniqueMonths(list) {
  const seen = new Set();
  const out = [];
  for (const v of list) {
    if (!seen.has(v.month)) { seen.add(v.month); out.push(v.month); }
  }
  return out;
}

function applyPreset(name) {
  const today = "2026-09-17";
  const from = $("from");
  const to = $("to");
  if (name === "all") { from.value = "2026-01-01"; to.value = today; }
  if (name === "7") { from.value = "2026-09-10"; to.value = today; }
  if (name === "30") { from.value = "2026-08-18"; to.value = today; }
  if (name === "sep") { from.value = "2026-09-01"; to.value = today; }
  if (name === "jul") { from.value = "2026-07-01"; to.value = "2026-07-31"; }
  document.querySelectorAll(".chip").forEach((c) => {
    c.setAttribute("aria-pressed", c.dataset.preset === name ? "true" : "false");
  });
  render();
}

function filtered() {
  const q = $("q").value.trim().toLowerCase();
  const from = $("from").value || "0000-01-01";
  const to = $("to").value || "9999-12-31";
  const type = $("type").value;
  const onlyNew = $("onlyNew").checked;
  const seen = new Set(readSeen());
  const firstVisit = seen.size === 0;
  return videos.filter((v) => {
    if (v.date < from || v.date > to) return false;
    if (type !== "all" && v.type !== type) return false;
    if (q) {
      const hay = (v.title + " " + v.caption + " " + (v.reply_to || "")).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    const isNew = !firstVisit && !seen.has(v.id);
    if (onlyNew && !isNew) return false;
    v._new = isNew;
    return true;
  });
}

function render() {
  const seen = new Set(readSeen());
  const firstVisit = seen.size === 0;
  const rows = filtered();
  const newest = videos[0];
  $("countAll").textContent = String(videos.length);
  $("countShown").textContent = String(rows.length);
  $("countNew").textContent = firstVisit ? "—" : String(videos.filter((v) => !seen.has(v.id)).length);
  $("latest").textContent = newest ? newest.date : "—";
  $("built").textContent = (CATALOG && CATALOG.builtAt) ? CATALOG.builtAt : "2026-09-17";
  const last = readLast();
  $("lastVisit").textContent = last ? last.slice(0, 16).replace("T", " ") : "first visit";

  const banner = $("banner");
  if (liveNote) {
    banner.hidden = false;
    banner.dataset.kind = liveNote.startsWith("Live") || liveNote.startsWith("No new") ? "ok" : "alert";
    banner.textContent = liveNote;
  } else if (firstVisit) {
    banner.hidden = false;
    banner.dataset.kind = "ok";
    banner.textContent = "First visit. The 2026 catalog is loaded. Click “Mark current as seen” so the next new post lights up.";
  } else {
    const n = videos.filter((v) => !seen.has(v.id)).length;
    if (n) {
      banner.hidden = false;
      banner.dataset.kind = "alert";
      banner.textContent = "NEW VIDEO DETECTED · " + n + " unseen post" + (n === 1 ? "" : "s") + " since you last marked this list as seen.";
    } else {
      banner.hidden = true;
    }
  }

  const list = $("list");
  list.replaceChildren();
  if (!rows.length) {
    const empty = document.createElement("p");
    empty.className = "empty";
    empty.textContent = "No videos in this date range. Widen the filter.";
    list.appendChild(empty);
    return;
  }
  for (const v of rows) {
    const card = document.createElement("article");
    card.className = "item" + (v._new ? " is-new" : "");
    const thumb = document.createElement("a");
    thumb.className = "thumb";
    thumb.href = v.url;
    thumb.target = "_blank";
    thumb.rel = "noopener noreferrer";
    if (v.thumbnail) {
      const img = document.createElement("img");
      img.src = v.thumbnail;
      img.alt = "";
      img.loading = "lazy";
      thumb.appendChild(img);
    }
    const play = document.createElement("span");
    play.className = "play";
    play.setAttribute("aria-hidden", "true");
    play.textContent = "▶";
    thumb.appendChild(play);
    const inner = document.createElement("div");
    inner.className = "item-body";
    const day = fmtDay(v.date);
    const when = document.createElement("div");
    when.className = "when";
    when.innerHTML = "<b>" + day.d + " " + day.mon + "</b><span>" + day.y + "</span>";
    const flags = document.createElement("div");
    flags.className = "flags";
    if (v._new) {
      const f = document.createElement("span");
      f.className = "flag new";
      f.textContent = "New release";
      flags.appendChild(f);
    }
    const k = document.createElement("span");
    k.className = "flag " + (v.type === "Kenalan Yuk" ? "kind-kenalan" : "kind-qa");
    k.textContent = v.type;
    flags.appendChild(k);
    if (v.reply_to) {
      const r = document.createElement("span");
      r.className = "flag";
      r.textContent = "@" + v.reply_to;
      flags.appendChild(r);
    }
    const body = document.createElement("div");
    body.className = "body";
    const h = document.createElement("h2");
    const titleLink = document.createElement("a");
    titleLink.href = v.url;
    titleLink.target = "_blank";
    titleLink.rel = "noopener noreferrer";
    titleLink.textContent = v.title;
    h.appendChild(titleLink);
    body.appendChild(h);
    const linkrow = document.createElement("div");
    linkrow.className = "linkrow";
    const code = document.createElement("code");
    code.textContent = v.url;
    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "copy";
    copy.textContent = "Copy";
    copy.addEventListener("click", async (ev) => {
      ev.preventDefault();
      try { await navigator.clipboard.writeText(v.url); } catch (e) {}
      copy.textContent = "Copied";
      copy.classList.add("done");
      setTimeout(() => { copy.textContent = "Copy"; copy.classList.remove("done"); }, 1600);
    });
    linkrow.appendChild(code);
    linkrow.appendChild(copy);
    const foot = document.createElement("div");
    foot.className = "foot";
    const open = document.createElement("a");
    open.className = "open";
    open.href = v.url;
    open.target = "_blank";
    open.rel = "noopener noreferrer";
    open.textContent = "Open video ↗";
    foot.appendChild(open);
    inner.appendChild(when);
    inner.appendChild(flags);
    inner.appendChild(body);
    inner.appendChild(linkrow);
    inner.appendChild(foot);
    card.appendChild(thumb);
    card.appendChild(inner);
    list.appendChild(card);
  }
}

function markSeen() {
  writeSeen(videos.map((v) => v.id));
  writeLast();
  liveNote = "Marked " + videos.length + " videos as seen. The next post from @gerejayesussejati will show as New.";
  render();
}

async function tryLiveJson() {
  try {
    const res = await fetch("videos.json", { cache: "no-store" });
    if (!res.ok) return false;
    const data = await res.json();
    if (data && Array.isArray(data.videos) && data.videos.length) {
      const prev = new Set(videos.map((v) => v.id));
      videos = data.videos.slice();
      CATALOG.videos = videos;
      CATALOG.builtAt = data.builtAt || CATALOG.builtAt;
      const added = videos.filter((v) => !prev.has(v.id));
      liveNote = added.length
        ? ("Live file updated: " + added.length + " new video" + (added.length === 1 ? "" : "s") + ".")
        : "No new videos in the local catalog.";
      render();
      return true;
    }
  } catch (e) {}
  return false;
}

function bind() {
  $("q").addEventListener("input", render);
  $("from").addEventListener("change", render);
  $("to").addEventListener("change", render);
  $("type").addEventListener("change", render);
  $("onlyNew").addEventListener("change", render);
  $("markSeen").addEventListener("click", markSeen);
  $("openProfile").addEventListener("click", () => {
    window.open("https://www.tiktok.com/@gerejayesussejati", "_blank", "noopener");
  });
  $("checkLive").addEventListener("click", async () => {
    const ok = await tryLiveJson();
    if (!ok) {
      liveNote = "This hosted page cannot read TikTok directly. Open the TikTok profile, or run watch_gys.py on your computer to refresh the catalog.";
      render();
    }
  });
  document.querySelectorAll(".chip").forEach((c) => {
    c.addEventListener("click", () => applyPreset(c.dataset.preset));
  });
  applyPreset("all");
  tryLiveJson();
}

bind();
"""

BODY = """
<header class="topbar">
  <div class="topbar-inner">
    <div class="brand">
      <div class="mark" aria-hidden="true">◉</div>
      <div class="brand-copy">
        <div class="brand-row">
          <span class="brand-name">Troopermonitor</span>
          <span class="badge">MONITOR</span>
        </div>
        <p class="brand-sub">Automated video link &amp; release radar</p>
      </div>
    </div>
    <div class="radar"><span class="pulse"></span> Radar Active · @gerejayesussejati</div>
  </div>
</header>
<div class="wrap">
  <section class="mast">
    <div class="hero">
      <span class="live-chip"><span class="pulse"></span> Live monitor active</span>
    </div>
    <div class="mast-body">
      <div class="ident">
        <div class="avatar" aria-hidden="true">GYS</div>
        <div>
          <h1>Gereja Yesus Sejati Official</h1>
          <div class="handle">@gerejayesussejati · TikTok</div>
        </div>
      </div>
      <p class="lede">Every public TikTok from <a class="profile" href="https://www.tiktok.com/@gerejayesussejati" target="_blank" rel="noopener noreferrer">@gerejayesussejati</a> since 1 January 2026. Filter by date, copy the direct link, and mark the list as seen so a new release lights up.</p>
      <div class="stats">
        <div class="stat"><b id="countAll">0</b><span>Detected videos</span></div>
        <div class="stat"><b id="countNew">0</b><span>New releases</span></div>
        <div class="stat"><b id="countShown">0</b><span>Showing</span></div>
        <div class="stat"><b id="latest">—</b><span>Latest post</span></div>
      </div>
      <div id="banner" class="banner" hidden></div>
    </div>
  </section>

  <section class="filters">
    <div class="row">
      <label>Search
        <input id="q" type="search" placeholder="Roh Kudus, Sabat, baptis…" autocomplete="off">
      </label>
      <label>From
        <input id="from" type="date" value="2026-01-01" min="2026-01-01" max="2026-09-17">
      </label>
      <label>To
        <input id="to" type="date" value="2026-09-17" min="2026-01-01" max="2026-09-17">
      </label>
      <label>Type
        <select id="type">
          <option value="all">All types</option>
          <option value="Q&amp;A Reply">Q&amp;A Reply</option>
          <option value="Kenalan Yuk">Kenalan Yuk</option>
        </select>
      </label>
      <label style="flex-direction:row;align-items:center;gap:8px;letter-spacing:0;text-transform:none;font-family:var(--sans);font-size:14px;color:var(--ink);padding-bottom:8px;">
        <input id="onlyNew" type="checkbox"> New only
      </label>
    </div>
    <div class="presets" role="group" aria-label="Date presets">
      <button type="button" class="chip" data-preset="all" aria-pressed="true">All 2026</button>
      <button type="button" class="chip" data-preset="7" aria-pressed="false">Last 7 days</button>
      <button type="button" class="chip" data-preset="30" aria-pressed="false">Last 30 days</button>
      <button type="button" class="chip" data-preset="sep" aria-pressed="false">September</button>
      <button type="button" class="chip" data-preset="jul" aria-pressed="false">July</button>
    </div>
    <div class="actions">
      <button type="button" class="primary" id="markSeen">Mark current as seen</button>
      <button type="button" id="checkLive">Scan now</button>
      <button type="button" class="ghost" id="openProfile">Open TikTok profile</button>
    </div>
  </section>

  <div class="meta-line">
    <span>Catalog built <span id="built">2026-09-17</span> · last marked <span id="lastVisit">—</span></span>
    <span>Copy a card link, or open the video</span>
  </div>
  <div id="list" class="list"></div>
  <p class="note">TikTok does not expose a public feed to browsers, so this page ships with the 1 Jan–16 Sep 2026 catalog. “Scan now” reloads a local <code>videos.json</code> when you run the watcher on your computer; on the hosted page it cannot reach TikTok, so use “Open TikTok profile” or ask to refresh the catalog. Comment collection and WhatsApp still run on the PC, not on this website. Your seen-list stays in this browser only.</p>
</div>
"""


def artifact_html() -> str:
    return f"""<title>Troopermonitor Radar</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
{CSS}
</style>
{BODY}
<script>window.__GYS__ = {EMBED};</script>
<script>
{JS}
</script>
"""


def local_html() -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Troopermonitor Radar</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
{CSS}
</style>
</head>
<body>
{BODY}
<script>window.__GYS__ = {EMBED};</script>
<script>
{JS}
</script>
</body>
</html>
"""


def main() -> None:
    (DIR / "index.html").write_text(local_html(), encoding="utf-8")
    (DIR / "artifact.html").write_text(artifact_html(), encoding="utf-8")
    print("wrote", DIR / "index.html")
    print("wrote", DIR / "artifact.html")
    print("videos", DATA["count"])


if __name__ == "__main__":
    main()
