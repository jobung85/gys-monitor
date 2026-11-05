# -*- coding: utf-8 -*-
"""Unit tests for TikTok availability classification and confirm logic."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import check_availability as ca  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"


def test_classify_deleted():
    html = (FIX / "unavailable_deleted.html").read_text(encoding="utf-8")
    r = ca.classify_html(html, "7700868891966295297")
    assert r["state"] == "unavailable"
    assert r["statusCode"] == 10204
    assert "deleted" in (r.get("statusMsg") or "")


def test_classify_available():
    html = (FIX / "available.html").read_text(encoding="utf-8")
    r = ca.classify_html(html, "7704548917362330900")
    assert r["state"] == "available"
    assert r["statusCode"] == 0


def test_classify_missing_and_private():
    r1 = ca.classify_html((FIX / "unavailable_missing.html").read_text(encoding="utf-8"), "999")
    r2 = ca.classify_html((FIX / "unavailable_private.html").read_text(encoding="utf-8"), "999")
    assert r1["state"] == "unavailable"
    assert r2["state"] == "unavailable"
    assert r2["statusCode"] == 10216


def test_waf_is_unknown_not_unavailable():
    r = ca.classify_html((FIX / "waf.html").read_text(encoding="utf-8"), "1")
    assert r["state"] == "unknown"
    assert r["reason"] == "waf_interstitial"


def test_confirm_requires_two_runs():
    v = {"id": "1", "url": "https://www.tiktok.com/@x/video/1"}
    now = "2026-11-05T12:00:00Z"
    out1 = ca.apply_result(v, {"state": "unavailable", "statusCode": 10204, "statusMsg": "status_deleted", "via": "video-detail"}, now)
    assert out1 == "pending"
    assert v["available"] is None
    assert v["unavailableStreak"] == 1
    assert v.get("unavailableSince") in (None, "")

    out2 = ca.apply_result(v, {"state": "unavailable", "statusCode": 10204, "statusMsg": "status_deleted", "via": "video-detail"}, "2026-11-05T18:00:00Z")
    assert out2 == "unavailable"
    assert v["available"] is False
    assert v["unavailableStreak"] == 2
    assert v["unavailableSince"] == "2026-11-05T18:00:00Z"


def test_available_clears_unavailable():
    v = {
        "id": "1",
        "available": False,
        "unavailableSince": "2026-11-01T00:00:00Z",
        "unavailableStreak": 3,
    }
    out = ca.apply_result(v, {"state": "available"}, "2026-11-05T12:00:00Z")
    assert out == "available"
    assert v["available"] is True
    assert v["unavailableSince"] is None
    assert v["unavailableStreak"] == 0


def test_unknown_preserves_prior_state():
    v = {
        "id": "1",
        "available": True,
        "unavailableSince": None,
        "unavailableStreak": 0,
    }
    out = ca.apply_result(v, {"state": "unknown", "reason": "waf_interstitial", "ua": "desktop"}, "2026-11-05T12:00:00Z")
    assert out == "unknown"
    assert v["available"] is True
    assert v["unavailableStreak"] == 0
    assert "check_failed" in v["availabilityReason"]


def test_generator_has_unavailable_ui():
    src = (ROOT / "generate_site.py").read_text(encoding="utf-8")
    for need in (
        "is-unavailable",
        "flag unavailable",
        "hideUnavailable",
        "Hide unavailable",
        "isUnavailable",
        "countUnavailable",
    ):
        assert need in src, need


def test_classify_i18n_phrase_not_enough():
    """i18n copy alone must not mark unavailable (appears on available pages too)."""
    html = (FIX / "unavailable_page_text.html").read_text(encoding="utf-8")
    r = ca.classify_html(html, "1")
    assert r["state"] == "unknown"


def test_classify_mobile_no_itemstruct():
    # Large HTML, no universal data, no itemStruct → unavailable
    pad = "x" * 90000
    html = f"<html><body>{pad}</body></html>"
    r = ca.classify_html(html, "1")
    assert r["state"] == "unavailable"
    assert r["via"] == "no_itemStruct"


def test_classify_mobile_with_itemstruct():
    pad = "x" * 90000
    html = f'<html><body>{pad}<script>"itemStruct":{{"id":"42"}}</script></body></html>'
    r = ca.classify_html(html, "42")
    assert r["state"] == "available"
    assert r["via"] == "itemStruct"
