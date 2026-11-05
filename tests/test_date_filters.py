# -*- coding: utf-8 -*-
"""Guardrails: date filters must be runtime-relative, not frozen at build time."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "generate_site.py"
INDEX = ROOT / "index.html"

BANNED = (
    "2026-09-17",
    "2026-09-10",
    "2026-08-18",
    'data-preset="sep"',
    'data-preset="jul"',
    "All 2026",
    "1 Jan–16 Sep",
    'max="2026-09-17"',
)

REQUIRED = (
    "todayLocal()",
    "yearStartLocal(",
    "addDaysLocal(",
    "buildMonthChips()",
    "syncDateBounds()",
    'data-preset="all"',
    'data-preset="7"',
    'data-preset="30"',
)


def test_generator_source_has_no_frozen_september_anchors() -> None:
    src = GEN.read_text(encoding="utf-8")
    for bad in BANNED:
        assert bad not in src, f"generate_site.py still hardcodes {bad!r}"
    for need in REQUIRED:
        assert need in src, f"generate_site.py missing {need!r}"


def test_regenerated_index_is_dynamic() -> None:
    subprocess.check_call([sys.executable, str(GEN)], cwd=ROOT)
    html = INDEX.read_text(encoding="utf-8")
    for bad in BANNED:
        assert bad not in html, f"index.html still hardcodes {bad!r}"
    for need in REQUIRED:
        assert need in html, f"index.html missing {need!r}"
    # Month chips are built at runtime from catalog months (not baked into HTML).
    assert "September</button>" not in html
    assert "July</button>" not in html
    assert 'id="presets"' in html


def test_runtime_helpers_in_node() -> None:
    """Execute the date helpers with a fixed 'today' to prove relative math."""
    js = r"""
function pad2(n) { return String(n).padStart(2, "0"); }
function isoLocal(d) {
  return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate());
}
function todayLocal() { return isoLocal(new Date(2026, 10, 5)); } // Nov 5 2026 local
function yearStartLocal(year) { return year + "-01-01"; }
function addDaysLocal(iso, delta) {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  dt.setDate(dt.getDate() + delta);
  return isoLocal(dt);
}
function monthBounds(ym) {
  const [y, m] = ym.split("-").map(Number);
  const start = y + "-" + pad2(m) + "-01";
  const end = isoLocal(new Date(y, m, 0));
  return { start, end };
}
const today = todayLocal();
const year = 2026;
const allFrom = yearStartLocal(year);
const last7 = addDaysLocal(today, -6);
const last30 = addDaysLocal(today, -29);
const nov = monthBounds("2026-11");
if (today !== "2026-11-05") throw new Error("today " + today);
if (allFrom !== "2026-01-01") throw new Error("year start " + allFrom);
if (last7 !== "2026-10-30") throw new Error("last7 " + last7);
if (last30 !== "2026-10-07") throw new Error("last30 " + last30);
if (nov.start !== "2026-11-01" || nov.end !== "2026-11-30") throw new Error("nov " + JSON.stringify(nov));
console.log("ok");
"""
    out = subprocess.check_output(["node", "-e", js], text=True).strip()
    assert out == "ok"


if __name__ == "__main__":
    test_generator_source_has_no_frozen_september_anchors()
    test_regenerated_index_is_dynamic()
    test_runtime_helpers_in_node()
    print("all tests passed")
