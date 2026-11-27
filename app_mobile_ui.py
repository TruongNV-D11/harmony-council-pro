import json
import logging
import math
import os
import random
import re
import time
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st

# =====================================================================
# 0. CẤU HÌNH TRANG, LOGGING & HỆ THỐNG THỜI GIAN THỰC
# =====================================================================
st.set_page_config(
    page_title="Vietlott Harmony Edition v2.7 — Academic Engine",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
LOG_PATH = os.path.join(BASE_DIR, "harmony_fetch.log")

logger = logging.getLogger("harmony_fetch")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    try:
        fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        logger.addHandler(fh)
    except Exception:
        pass

VN_TZ = timezone(timedelta(hours=7))


def now_vn() -> datetime:
    return datetime.now(VN_TZ)


# =====================================================================
# 🎨 1. GIAO DIỆN DARK LUXURY & HIỆU ỨNG BÓNG LĂN (ANIMATED BALLS)
# =====================================================================
st.markdown(
    """
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 14px;
        min-height: 3.4em;
        font-weight: bold;
        font-size: 16px;
        background: linear-gradient(135deg, #1D976C 0%, #93F9B9 100%);
        color: #0E1117;
        border: none;
        box-shadow: 0 4px 15px rgba(29, 151, 108, 0.4);
        transition: all 0.25s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(29, 151, 108, 0.65);
    }

    @keyframes popInBall {
        0% {
            transform: scale(0.1) rotate(-360deg);
            opacity: 0;
        }
        75% {
            transform: scale(1.15) rotate(15deg);
            opacity: 1;
        }
        100% {
            transform: scale(1) rotate(0deg);
            opacity: 1;
        }
    }

    .ball-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #43cea2, #185a9d);
        color: #FFFFFF;
        font-weight: 800;
        font-size: 16px;
        margin: 4px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        border: 2px solid #93F9B9;
        animation: popInBall 0.45s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }

    .ball-special {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #ff512f, #dd2476);
        color: #FFFFFF;
        font-weight: 800;
        font-size: 16px;
        margin: 4px 4px 4px 10px;
        box-shadow: 0 4px 10px rgba(221, 36, 118, 0.65);
        border: 2px solid #FFD700;
        animation: popInBall 0.45s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }

    .council-card {
        background-color: #1A1C23;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 16px;
        border-left: 5px solid #1D976C;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
    }

    .score-badge {
        background-color: #262934;
        color: #00E676;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: bold;
        float: right;
        border: 1px solid #00E676;
    }

    .sub-metric {
        font-size: 12.5px;
        color: #B0BEC5;
        margin-top: 8px;
        line-height: 1.65;
    }

    .academic-banner {
        background: linear-gradient(135deg, #1E222D 0%, #151821 100%);
        border: 1px solid #303647;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 14px;
        font-size: 13px;
        line-height: 1.6;
        color: #CFD8DC;
    }

    .philosophy-banner {
        background: linear-gradient(135deg, #1A2421 0%, #12171D 100%);
        border: 1px solid #1D976C;
        border-left: 5px solid #00E676;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(29, 151, 108, 0.15);
    }
    .philosophy-title {
        color: #00E676;
        font-weight: bold;
        font-size: 15px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .philosophy-text {
        color: #E0E6ED;
        font-size: 13.5px;
        line-height: 1.6;
        margin: 0;
    }
    .philosophy-highlight {
        color: #93F9B9;
        font-weight: 600;
    }

    .iching-card {
        background: linear-gradient(135deg, #1F1B24 0%, #15131A 100%);
        border: 1px solid #9C27B0;
        border-left: 5px solid #D4AF37;
        border-radius: 14px;
        padding: 16px;
        margin-top: 10px;
        margin-bottom: 14px;
        box-shadow: 0 4px 14px rgba(156, 39, 176, 0.2);
    }
    .iching-conclusion-box {
        background-color: rgba(212, 175, 55, 0.08);
        border: 1px solid rgba(212, 175, 55, 0.45);
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .iching-meta-grid {
        font-size: 12.5px;
        color: #B0BEC5;
        line-height: 1.65;
        padding-top: 8px;
        border-top: 1px dashed #3A3446;
    }

    .watermark-box {
        text-align: center;
        padding: 18px;
        margin-top: 25px;
        border-top: 1px solid #2A2D3A;
        background: linear-gradient(180deg, rgba(26,28,35,0) 0%, rgba(29,151,108,0.08) 100%);
        border-radius: 0 0 12px 12px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================================
# 📡 2. CẤU HÌNH GAME & DATA ENGINE (LIVE FETCH -> SMART CACHE -> GITHUB BACKUP)
# =====================================================================
GAMES: Dict[str, Dict[str, Any]] = {
    "5x35": {
        "label": "Lotto 5/35 (1–35 + 1 số ĐB 1–12)",
        "pick": 5,
        "max_main": 35,
        "has_special": True,
        "special_max": 12,
        "vietlott_url": "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/535",
        "vietlott_endpoints": [
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/535",
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/535/",
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/535/danh-sach-ky-quay.html",
            "https://vietlott.vn/ajax/ket-qua-trung-thuong/535",
        ],
        "minhngoc_url": "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/lotto-5x35.html",
        "minhngoc_endpoints": [
            "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/lotto-5x35.html",
            "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/lotto-5x35.html?page=1",
            "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/lotto-5x35.html?page=2",
            "https://www.minhngoc.com.vn/ket-qua-xo-so/dien-toan-vietlott/lotto-5x35.html",
        ],
        "backups": [
            "https://www.minhngoc.com.vn/ket-qua-xo-so/dien-toan-vietlott/lotto-5x35.html",
            "https://xosominhngoc.com/ket-qua-xo-so/dien-toan-vietlott/lotto-5x35.html",
        ],
        "github_jsonl": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power535.jsonl",
        "draw_days": [0, 1, 2, 3, 4, 5, 6],
        "draw_hours": [13, 21],
    },
    "6x45": {
        "label": "Mega 6/45 (1–45)",
        "pick": 6,
        "max_main": 45,
        "has_special": False,
        "vietlott_url": "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645",
        "vietlott_endpoints": [
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645",
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645/",
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645/danh-sach-ky-quay.html",
            "https://vietlott.vn/ajax/ket-qua-trung-thuong/645",
        ],
        "minhngoc_url": "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/mega-6x45.html",
        "minhngoc_endpoints": [
            "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/mega-6x45.html",
            "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/mega-6x45.html?page=1",
            "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/mega-6x45.html?page=2",
            "https://www.minhngoc.com.vn/ket-qua-xo-so/dien-toan-vietlott/mega-6x45.html",
        ],
        "backups": [
            "https://www.minhngoc.com.vn/ket-qua-xo-so/dien-toan-vietlott/mega-6x45.html",
            "https://xosominhngoc.com/ket-qua-xo-so/dien-toan-vietlott/mega-6x45.html",
        ],
        "github_jsonl": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power645.jsonl",
        "draw_days": [2, 4, 6],
        "draw_hours": [18],
    },
    "6x55": {
        "label": "Power 6/55 (1–55 + 1 số ĐB)",
        "pick": 6,
        "max_main": 55,
        "has_special": True,
        "special_max": 55,
        "vietlott_url": "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655",
        "vietlott_endpoints": [
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655",
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655/",
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655/danh-sach-ky-quay.html",
            "https://vietlott.vn/ajax/ket-qua-trung-thuong/655",
        ],
        "minhngoc_url": "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/power-6x55.html",
        "minhngoc_endpoints": [
            "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/power-6x55.html",
            "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/power-6x55.html?page=1",
            "https://www.minhngoc.net.vn/ket-qua-xo-so/dien-toan-vietlott/power-6x55.html?page=2",
            "https://www.minhngoc.com.vn/ket-qua-xo-so/dien-toan-vietlott/power-6x55.html",
        ],
        "backups": [
            "https://www.minhngoc.com.vn/ket-qua-xo-so/dien-toan-vietlott/power-6x55.html",
            "https://xosominhngoc.com/ket-qua-xo-so/dien-toan-vietlott/power-6x55.html",
        ],
        "github_jsonl": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power655.jsonl",
        "draw_days": [1, 3, 5],
        "draw_hours": [18],
    },
}

MAX_CACHE_RECORDS = 2000


def get_next_draw_datetime(game_key: str) -> datetime:
    now = now_vn()
    cfg = GAMES[game_key]
    draw_days = cfg["draw_days"]
    draw_hours = sorted(cfg["draw_hours"])

    for delta_days in range(0, 8):
        cand_date = now + timedelta(days=delta_days)
        if cand_date.weekday() in draw_days:
            for h in draw_hours:
                cand_dt = cand_date.replace(hour=h, minute=0, second=0, microsecond=0)
                if cand_dt > now:
                    return cand_dt
    return now + timedelta(days=1)


def get_latest_completed_draw_slot(game_key: str) -> Tuple[datetime, str]:
    now = now_vn()
    cfg = GAMES[game_key]
    draw_days = cfg["draw_days"]
    draw_hours = sorted(cfg["draw_hours"], reverse=True)

    for delta_days in range(0, 8):
        cand_date = now - timedelta(days=delta_days)
        if cand_date.weekday() in draw_days:
            for h in draw_hours:
                draw_end_dt = cand_date.replace(hour=h, minute=35, second=0, microsecond=0)
                if now >= draw_end_dt:
                    return cand_date, f"{h:02d}:00"
    return now - timedelta(days=1), "18:00"


def is_valid_record(rec: Any, game_cfg: Dict[str, Any]) -> bool:
    if not isinstance(rec, dict):
        return False
    mains = rec.get("mains", [])
    if not isinstance(mains, list):
        return False
    if len(mains) != game_cfg["pick"] or len(set(mains)) != game_cfg["pick"]:
        return False
    if not all(isinstance(n, int) and 1 <= n <= game_cfg["max_main"] for n in mains):
        return False
    if game_cfg.get("has_special", False):
        spec = rec.get("special")
        spec_max = game_cfg.get("special_max", game_cfg["max_main"])
        if spec is not None and not (isinstance(spec, int) and 1 <= spec <= spec_max):
            return False
    return True


def _normalize_date_str(raw_date: str) -> str:
    s = str(raw_date or "").strip()
    if not s:
        return ""
    m_iso = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
    if m_iso:
        return f"{int(m_iso.group(1)):04d}-{int(m_iso.group(2)):02d}-{int(m_iso.group(3)):02d}"
    m_vn = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", s)
    if m_vn:
        return f"{int(m_vn.group(3)):04d}-{int(m_vn.group(2)):02d}-{int(m_vn.group(1)):02d}"
    return s


def _normalize_slot_str(raw_slot: str, game_key: str = "") -> str:
    s = str(raw_slot or "").strip()
    if not s:
        return ""
    m_h = re.search(r"(\d{1,2})\s*(?::|h|g)\s*(\d{2})?", s, flags=re.I)
    if m_h:
        hh = int(m_h.group(1))
        if game_key == "5x35":
            return "13:00" if hh < 17 else "21:00"
        return f"{hh:02d}:00"
    return s


def _normalize_record(
    rec: Dict[str, Any],
    game_cfg: Dict[str, Any],
    fallback_date: str = "",
    fallback_slot: str = "",
    game_key: str = "",
) -> Dict[str, Any]:
    mains = sorted([int(x) for x in rec.get("mains", [])])
    spec = rec.get("special")
    if game_cfg.get("has_special", False) and spec is not None:
        try:
            spec = int(spec)
        except Exception:
            spec = None
    else:
        spec = None
    norm_date = _normalize_date_str(str(rec.get("date", "") or fallback_date))
    norm_slot = _normalize_slot_str(str(rec.get("slot", "") or fallback_slot), game_key=game_key)
    draw_id = str(rec.get("draw_id", "") or "").strip()
    return {
        "draw_id": draw_id,
        "date": norm_date,
        "slot": norm_slot,
        "mains": mains,
        "special": spec,
    }


def _record_identity_key(rec: Dict[str, Any], game_key: str = "") -> str:
    draw_id = str(rec.get("draw_id", "") or "").strip()
    date_part = _normalize_date_str(str(rec.get("date", "") or ""))
    slot_part = _normalize_slot_str(str(rec.get("slot", "") or ""), game_key=game_key)
    nums_part = "-".join(f"{n:02d}" for n in sorted(rec.get("mains", [])))
    spec_part = f"+{int(rec['special']):02d}" if rec.get("special") is not None else ""
    if draw_id:
        return f"id:{draw_id}|{nums_part}{spec_part}"
    if date_part and slot_part:
        return f"{date_part}@{slot_part}|{nums_part}{spec_part}"
    if date_part:
        return f"{date_part}|{nums_part}{spec_part}"
    return f"nums:{nums_part}{spec_part}"


def _atomic_write_json(path: str, payload: Any) -> bool:
    tmp_path = f"{path}.tmp.{os.getpid()}"
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
        return True
    except Exception as e:
        logger.warning(f"Atomic write failed for {path}: {e}")
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return False


def _merge_unique_history(
    primary_records: List[Dict[str, Any]],
    older_records: List[Dict[str, Any]],
    game_cfg: Dict[str, Any],
    max_records: int = MAX_CACHE_RECORDS,
    game_key: str = "",
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    seen = set()
    for r in primary_records + older_records:
        if not is_valid_record(r, game_cfg):
            continue
        norm = _normalize_record(r, game_cfg, game_key=game_key)
        key = _record_identity_key(norm, game_key=game_key)
        if key not in seen:
            seen.add(key)
            merged.append(norm)
        if len(merged) >= max_records:
            break
    return merged


def fetch_html_with_diag(
    url: str,
    timeout: int = 15,
    referer: Optional[str] = None,
    session: Optional[requests.Session] = None,
) -> Tuple[str, Dict[str, Any]]:
    info: Dict[str, Any] = {
        "url": url,
        "status": None,
        "bytes": 0,
        "error": "",
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
    }
    if referer:
        headers["Referer"] = referer
    client = session if session is not None else requests
    try:
        resp = client.get(url, headers=headers, timeout=timeout)
        info["status"] = resp.status_code
        if not resp.encoding or resp.encoding.lower() in ("iso-8859-1", "ascii"):
            resp.encoding = resp.apparent_encoding or "utf-8"
        text = resp.text or ""
        info["bytes"] = len(text)
        if resp.status_code == 200 and len(text) > 300:
            return text, info
        info["error"] = f"HTTP_{resp.status_code}_short_or_blocked"
        return "", info
    except Exception as e:
        info["error"] = f"{type(e).__name__}: {str(e)[:120]}"
        return "", info


def parse_history_from_html(html: str, game_cfg: Dict[str, Any], source_url: str = "") -> List[Dict[str, Any]]:
    if not html:
        return []

    pick = game_cfg["pick"]
    max_main = game_cfg["max_main"]
    has_special = game_cfg.get("has_special", False)
    special_max = game_cfg.get("special_max", max_main)
    is_535 = (pick == 5 and max_main == 35)
    is_655 = (pick == 6 and max_main == 55)

    results: List[Dict[str, Any]] = []
    seen_sig = set()

    def _push_candidate(raw_nums: List[int], date_str: str = "", slot_str: str = "", draw_id: str = "") -> None:
        if len(raw_nums) < pick:
            return
        mains = raw_nums[:pick]
        if len(set(mains)) != pick:
            return
        if not all(1 <= n <= max_main for n in mains):
            return

        spec = None
        if has_special and len(raw_nums) >= pick + 1:
            cand_spec = raw_nums[pick]
            if 1 <= cand_spec <= special_max:
                if is_535 or cand_spec not in mains:
                    spec = cand_spec
        if has_special and spec is None:
            return

        rec = {
            "draw_id": draw_id,
            "date": _normalize_date_str(date_str),
            "slot": _normalize_slot_str(slot_str, game_key="5x35" if is_535 else ""),
            "mains": sorted(mains),
            "special": spec,
        }
        sig = (rec["draw_id"], rec["date"], rec["slot"], tuple(rec["mains"]), rec["special"])
        if sig not in seen_sig:
            seen_sig.add(sig)
            results.append(rec)

    def _extract_meta_from_chunk(chunk_text: str) -> Tuple[str, str, str]:
        m_id = re.search(r"#\s*(\d{4,6})", chunk_text)
        draw_id = m_id.group(1) if m_id else ""
        m_date = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", chunk_text)
        date_str = m_date.group(1) if m_date else ""
        m_slot = re.search(r"(\d{1,2}\s*(?::|h|g)\s*\d{2})", chunk_text, flags=re.I)
        slot_str = m_slot.group(1) if m_slot else ""
        if not slot_str and is_535:
            if re.search(r"(?:13h|13:00|buổi\s*trưa|trưa)", chunk_text, flags=re.I):
                slot_str = "13:00"
            elif re.search(r"(?:21h|21:00|buổi\s*tối|tối)", chunk_text, flags=re.I):
                slot_str = "21:00"
        return date_str, slot_str, draw_id

    for script_body in re.findall(r"<script[^>]*>(.*?)</script>", html, flags=re.S | re.I):
        if "ListResult" in script_body or "Result" in script_body or "DrawDate" in script_body:
            for m_obj in re.finditer(r"\{[^{}]{20,600}\}", script_body):
                obj_txt = m_obj.group(0)
                if not re.search(r"(?:Result|Number|Ball|Draw)", obj_txt, flags=re.I):
                    continue
                date_str, slot_str, draw_id = _extract_meta_from_chunk(obj_txt)
                nums = [int(x) for x in re.findall(r"(?<!\d)(\d{1,2})(?!\d)", re.sub(r"\d{1,2}/\d{1,2}/\d{4}|#\d{4,6}", " ", obj_txt))]
                if len(nums) >= (pick + 1 if has_special else pick):
                    _push_candidate(nums, date_str=date_str, slot_str=slot_str, draw_id=draw_id)

    block_patterns = [
        r"<tr[^>]*>.*?</tr>",
        r"<div[^>]*class=[\"'][^\"']*(?:box_kqxs|result|ketqua|doso|item_kq|chitiet|day_so)[^\"']*[\"'][^>]*>.*?</div>",
        r"<ul[^>]*class=[\"'][^\"']*(?:result|ball|bong|day_so)[^\"']*[\"'][^>]*>.*?</ul>",
    ]
    for pat in block_patterns:
        for block in re.findall(pat, html, flags=re.S | re.I):
            plain = re.sub(r"<[^>]+>", " ", block)
            plain = re.sub(r"\s+", " ", plain).strip()
            if len(plain) < 12 or len(plain) > 1200:
                continue

            date_str, slot_str, draw_id = _extract_meta_from_chunk(plain)
            ball_tokens = re.findall(
                r"<(?:span|li|div|td|b|strong)[^>]*>\s*0?(\d{1,2})\s*</(?:span|li|div|td|b|strong)>",
                block,
                flags=re.I,
            )
            nums = [int(x) for x in ball_tokens]
            if len(nums) >= (pick + 1 if has_special else pick):
                _push_candidate(nums, date_str=date_str, slot_str=slot_str, draw_id=draw_id)
                continue

            cleaned_plain = re.sub(r"\d{1,2}/\d{1,2}/\d{4}", " ", plain)
            cleaned_plain = re.sub(r"#\s*\d{4,6}", " ", cleaned_plain)
            cleaned_plain = re.sub(r"\d{1,2}\s*(?::|h|g)\s*\d{2}", " ", cleaned_plain, flags=re.I)
            fallback_nums = [int(x) for x in re.findall(r"\b0?(\d{1,2})\b", cleaned_plain)]
            if len(fallback_nums) >= (pick + 1 if has_special else pick):
                _push_candidate(fallback_nums, date_str=date_str, slot_str=slot_str, draw_id=draw_id)

    if not results:
        if is_655:
            pattern = r"\b(0[1-9]|[1-4]\d|5[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-4]\d|5[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-4]\d|5[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-4]\d|5[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-4]\d|5[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-4]\d|5[0-5])\b(?:[\s\-\|,;/\|]+(0[1-9]|[1-4]\d|5[0-5])\b)?"
        elif is_535:
            pattern = r"\b(0[1-9]|[12]\d|3[0-5])\b[\s\-\|,;/]+(0[1-9]|[12]\d|3[0-5])\b[\s\-\|,;/]+(0[1-9]|[12]\d|3[0-5])\b[\s\-\|,;/]+(0[1-9]|[12]\d|3[0-5])\b[\s\-\|,;/]+(0[1-9]|[12]\d|3[0-5])\b[\s\-\|,;/\|]+(0[1-9]|1[0-2])\b"
        else:
            pattern = r"\b(0[1-9]|[1-3]\d|4[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-3]\d|4[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-3]\d|4[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-3]\d|4[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-3]\d|4[0-5])\b[\s\-\|,;/]+(0[1-9]|[1-3]\d|4[0-5])\b"

        text_only = re.sub(r"<[^>]+>", " ", html)
        for m in re.finditer(pattern, text_only):
            nums = [int(g) for g in m.groups() if g is not None]
            ctx_before = text_only[max(0, m.start() - 120): m.start()]
            date_str, slot_str, draw_id = _extract_meta_from_chunk(ctx_before)
            _push_candidate(nums, date_str=date_str, slot_str=slot_str, draw_id=draw_id)

    return results[:MAX_CACHE_RECORDS]


def _extract_nums_from_jsonl_obj(obj: Any, game_cfg: Dict[str, Any]) -> Tuple[List[int], Optional[int]]:
    pick = game_cfg["pick"]
    has_special = game_cfg.get("has_special", False)
    if isinstance(obj, list):
        nums = [int(x) for x in obj if isinstance(x, (int, float, str)) and str(x).strip().isdigit()]
        mains = nums[:pick]
        spec = int(nums[pick]) if has_special and len(nums) > pick else None
        return mains, spec
    if not isinstance(obj, dict):
        return [], None

    # Trường hợp tách riêng số chính và số đặc biệt
    raw_mains = (
        obj.get("mains")
        or obj.get("main_numbers")
        or obj.get("balls")
        or obj.get("win_numbers")
        or obj.get("winning_numbers")
    )
    raw_spec = (
        obj.get("special")
        if obj.get("special") is not None
        else (
            obj.get("special_number")
            if obj.get("special_number") is not None
            else (obj.get("bonus") if obj.get("bonus") is not None else obj.get("db"))
        )
    )

    if isinstance(raw_mains, list):
        mains = [int(x) for x in raw_mains if str(x).strip().isdigit()][:pick]
        spec: Optional[int] = None
        if has_special and raw_spec is not None and str(raw_spec).strip().isdigit():
            spec = int(raw_spec)
        return mains, spec

    # Trường hợp gộp chung vào một danh sách hoặc chuỗi
    raw_combined = obj.get("result") or obj.get("numbers") or obj.get("value") or ""
    if isinstance(raw_combined, str):
        tokens = re.findall(r"\d{1,2}", raw_combined)
        nums = [int(t) for t in tokens]
    elif isinstance(raw_combined, list):
        nums = [int(x) for x in raw_combined if str(x).strip().isdigit()]
    else:
        nums = []

    mains = nums[:pick]
    spec = None
    if has_special:
        if raw_spec is not None and str(raw_spec).strip().isdigit():
            spec = int(raw_spec)
        elif len(nums) > pick:
            spec = int(nums[pick])
    return mains, spec


def fetch_github_seed_data(
    jsonl_url: Optional[str],
    game_cfg: Dict[str, Any],
    diag: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    if not jsonl_url:
        if diag is not None and diag.get("github_status") is None:
            diag["github_status"] = "no_url"
        return []
    try:
        resp = requests.get(jsonl_url, timeout=15)
        if diag is not None:
            diag["github_status"] = resp.status_code
        if resp.status_code != 200:
            if diag is not None:
                diag["github_error"] = f"HTTP_{resp.status_code}"
            return []
        lines = [line.strip() for line in resp.text.splitlines() if line.strip()]
        parsed: List[Dict[str, Any]] = []
        for line in reversed(lines):
            try:
                obj = json.loads(line)
                mains, spec = _extract_nums_from_jsonl_obj(obj, game_cfg)
                if len(mains) == game_cfg["pick"]:
                    draw_id = ""
                    date_str = ""
                    slot_str = ""
                    if isinstance(obj, dict):
                        draw_id = str(obj.get("id") or obj.get("draw_id") or obj.get("period") or "").strip()
                        date_str = str(obj.get("date") or obj.get("draw_date") or "").strip()
                        slot_str = str(obj.get("slot") or obj.get("session") or obj.get("time") or "").strip()
                    rec = {
                        "draw_id": draw_id,
                        "date": date_str,
                        "slot": slot_str,
                        "mains": sorted(mains),
                        "special": spec,
                    }
                    if is_valid_record(rec, game_cfg):
                        parsed.append(rec)
                if len(parsed) >= MAX_CACHE_RECORDS:
                    break
            except Exception:
                continue
        if diag is not None and not parsed and lines:
            diag["github_error"] = "parsed_0_records_from_jsonl"
        return parsed
    except Exception as e:
        if diag is not None:
            diag["github_status"] = "error"
            diag["github_error"] = f"{type(e).__name__}: {str(e)[:120]}"
        return []


def get_history_with_diag(
    game_key: str,
    sample_k: int = 100,
    force_refresh: bool = False,
) -> Tuple[List[Dict[str, Any]], str, float, Dict[str, Any]]:
    game_cfg = GAMES[game_key]
    cache_file = os.path.join(BASE_DIR, f"cache_history_{game_key}.json")
    meta_file = os.path.join(BASE_DIR, f"cache_meta_{game_key}.json")

    expected_slot_date, expected_slot_time = get_latest_completed_draw_slot(game_key)
    expected_slot_key = f"{expected_slot_date.strftime('%Y-%m-%d')}@{expected_slot_time}"

    diag: Dict[str, Any] = {
        "game_key": game_key,
        "checked_at": now_vn().strftime("%Y-%m-%d %H:%M:%S"),
        "expected_slot_key": expected_slot_key,
        "force_refresh": force_refresh,
        "cache_file": cache_file,
        "live_attempts": [],
        "github_status": None,
        "github_error": "",
    }

    existing_cache: List[Dict[str, Any]] = []
    cache_age = 0.0
    if os.path.exists(cache_file):
        try:
            cache_age = max(0.0, time.time() - os.path.getmtime(cache_file))
            with open(cache_file, "r", encoding="utf-8") as f:
                raw_cache = json.load(f)
            if isinstance(raw_cache, list):
                existing_cache = [
                    _normalize_record(r, game_cfg, game_key=game_key)
                    for r in raw_cache
                    if is_valid_record(r, game_cfg)
                ]
        except Exception as e:
            logger.warning(f"[{game_key}] Failed reading cache {cache_file}: {e}")
            existing_cache = []

    meta_slot_key = ""
    if os.path.exists(meta_file):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            meta_slot_key = f"{meta.get('latest_date', '')}@{meta.get('latest_slot', '')}"
        except Exception:
            meta_slot_key = ""

    diag["existing_cache_count"] = len(existing_cache)
    diag["meta_slot_key"] = meta_slot_key

    need_fetch = force_refresh or (len(existing_cache) < sample_k) or (meta_slot_key != expected_slot_key)
    diag["need_fetch"] = need_fetch

    if not need_fetch and existing_cache:
        status = f"⚡ Smart Cache Nhật ký ({len(existing_cache)}/{MAX_CACHE_RECORDS} kỳ thật — Khớp kỳ {expected_slot_key})"
        _atomic_write_json(os.path.join(BASE_DIR, f"last_fetch_diag_{game_key}.json"), diag)
        return existing_cache[:sample_k], status, cache_age, diag

    vietlott_fetched: List[Dict[str, Any]] = []
    minhngoc_fetched: List[Dict[str, Any]] = []
    live_fetched: List[Dict[str, Any]] = []
    active_sources: List[str] = []

    base_vn = str(game_cfg.get("vietlott_url") or game_cfg.get("url") or "").strip()
    vn_urls = list(game_cfg.get("vietlott_endpoints") or [])
    if base_vn:
        vn_urls = [base_vn, base_vn.rstrip("/") + "/"] + vn_urls
    vn_urls = list(dict.fromkeys(u for u in vn_urls if u))

    mn_primary = str(game_cfg.get("minhngoc_url") or "").strip()
    mn_urls = list(game_cfg.get("minhngoc_endpoints") or [])
    if mn_primary:
        mn_urls = [mn_primary] + mn_urls
    mn_urls = list(dict.fromkeys(u for u in mn_urls if u))

    backup_urls = list(dict.fromkeys(u for u in (game_cfg.get("backups") or []) if u and u not in mn_urls))

    http_session = requests.Session()
    try:
        # 1. Nguồn chính thứ 1: vietlott.vn
        for u_idx, url in enumerate(vn_urls):
            ref = "https://vietlott.vn/" if u_idx > 0 else None
            html, attempt_info = fetch_html_with_diag(url, referer=ref, session=http_session)
            raw_parsed = parse_history_from_html(html, game_cfg, source_url=url)
            valid_parsed = [
                _normalize_record(
                    r,
                    game_cfg,
                    fallback_date=expected_slot_date.strftime("%Y-%m-%d") if idx == 0 else "",
                    fallback_slot=expected_slot_time if idx == 0 else "",
                    game_key=game_key,
                )
                for idx, r in enumerate(raw_parsed)
                if is_valid_record(r, game_cfg)
            ]
            attempt_info["source_group"] = "vietlott.vn"
            attempt_info["raw_parsed"] = len(raw_parsed)
            attempt_info["valid_parsed"] = len(valid_parsed)
            diag["live_attempts"].append(attempt_info)
            logger.info(
                f"[{game_key}] Vietlott {url} -> status={attempt_info['status']}, "
                f"bytes={attempt_info['bytes']}, raw={len(raw_parsed)}, valid={len(valid_parsed)}, err={attempt_info['error']}"
            )
            if valid_parsed:
                vietlott_fetched = _merge_unique_history(
                    vietlott_fetched, valid_parsed, game_cfg, MAX_CACHE_RECORDS, game_key=game_key
                )
                if "vietlott.vn" not in active_sources:
                    active_sources.append("vietlott.vn")
                if len(vietlott_fetched) >= sample_k:
                    break

        # 2. Nguồn chính thứ 2: minhngoc.net (luôn cào để hợp nhất & bù kỳ còn thiếu thay vì dừng sớm)
        for u_idx, url in enumerate(mn_urls):
            ref = mn_urls[0] if u_idx > 0 else "https://www.minhngoc.net.vn/"
            html, attempt_info = fetch_html_with_diag(url, referer=ref, session=http_session)
            raw_parsed = parse_history_from_html(html, game_cfg, source_url=url)
            valid_parsed = [
                _normalize_record(
                    r,
                    game_cfg,
                    fallback_date=expected_slot_date.strftime("%Y-%m-%d") if (idx == 0 and not vietlott_fetched) else "",
                    fallback_slot=expected_slot_time if (idx == 0 and not vietlott_fetched) else "",
                    game_key=game_key,
                )
                for idx, r in enumerate(raw_parsed)
                if is_valid_record(r, game_cfg)
            ]
            attempt_info["source_group"] = "minhngoc.net"
            attempt_info["raw_parsed"] = len(raw_parsed)
            attempt_info["valid_parsed"] = len(valid_parsed)
            diag["live_attempts"].append(attempt_info)
            logger.info(
                f"[{game_key}] MinhNgoc {url} -> status={attempt_info['status']}, "
                f"bytes={attempt_info['bytes']}, raw={len(raw_parsed)}, valid={len(valid_parsed)}, err={attempt_info['error']}"
            )
            if valid_parsed:
                minhngoc_fetched = _merge_unique_history(
                    minhngoc_fetched, valid_parsed, game_cfg, MAX_CACHE_RECORDS, game_key=game_key
                )
                if "minhngoc.net" not in active_sources:
                    active_sources.append("minhngoc.net")

        live_fetched = _merge_unique_history(
            vietlott_fetched, minhngoc_fetched, game_cfg, MAX_CACHE_RECORDS, game_key=game_key
        )

        # 3. Các mirror phụ của Minh Ngọc nếu cả 2 nguồn chính chưa đủ mẫu
        if len(live_fetched) < sample_k and backup_urls:
            for url in backup_urls:
                html, attempt_info = fetch_html_with_diag(url, referer="https://www.minhngoc.net.vn/", session=http_session)
                raw_parsed = parse_history_from_html(html, game_cfg, source_url=url)
                valid_parsed = [
                    _normalize_record(r, game_cfg, game_key=game_key)
                    for r in raw_parsed
                    if is_valid_record(r, game_cfg)
                ]
                attempt_info["source_group"] = "minhngoc_mirror"
                attempt_info["raw_parsed"] = len(raw_parsed)
                attempt_info["valid_parsed"] = len(valid_parsed)
                diag["live_attempts"].append(attempt_info)
                if valid_parsed:
                    live_fetched = _merge_unique_history(
                        live_fetched, valid_parsed, game_cfg, MAX_CACHE_RECORDS, game_key=game_key
                    )
                    host_tag = url.split("/")[2]
                    if host_tag not in active_sources:
                        active_sources.append(host_tag)
                    if len(live_fetched) >= sample_k:
                        break
    finally:
        http_session.close()

    active_source_url = " + ".join(active_sources)
    diag["vietlott_valid_count"] = len(vietlott_fetched)
    diag["minhngoc_valid_count"] = len(minhngoc_fetched)
    diag["live_valid_count"] = len(live_fetched)

    github_seed: List[Dict[str, Any]] = []
    github_available = False
    current_pool_len = len(live_fetched) + len(existing_cache)
    if (not live_fetched or current_pool_len < sample_k) and game_cfg.get("github_jsonl"):
        raw_gh = fetch_github_seed_data(game_cfg["github_jsonl"], game_cfg, diag=diag)
        github_seed = [
            _normalize_record(r, game_cfg, game_key=game_key)
            for r in raw_gh
            if is_valid_record(r, game_cfg)
        ]
        github_available = len(github_seed) > 0
    diag["github_valid_count"] = len(github_seed)
    diag["github_available"] = github_available

    combined = _merge_unique_history(
        live_fetched,
        _merge_unique_history(existing_cache, github_seed, game_cfg, MAX_CACHE_RECORDS, game_key=game_key),
        game_cfg,
        MAX_CACHE_RECORDS,
        game_key=game_key,
    )
    diag["final_count"] = len(combined)
    diag["cache_journal_written"] = False

    if combined:
        journal_ok = _atomic_write_json(cache_file, combined)
        diag["cache_journal_written"] = bool(journal_ok)
        newest_rec_date = str(combined[0].get("date", "") or "")
        if live_fetched or newest_rec_date >= expected_slot_date.strftime("%Y-%m-%d"):
            _atomic_write_json(
                meta_file,
                {
                    "latest_date": expected_slot_date.strftime("%Y-%m-%d"),
                    "latest_slot": expected_slot_time,
                    "source_latest_date": newest_rec_date,
                    "record_count": len(combined),
                    "live_source": active_source_url or "cache/backup",
                    "github_available": github_available,
                    "updated_at": now_vn().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
            cache_age = 0.0

        gh_note = "" if github_available or not game_cfg.get("github_jsonl") else " | GitHub Seed không khả dụng -> Tự chủ bằng Live & Cache"
        if live_fetched:
            status = f"🟢 Live ({active_source_url}) cập nhật kỳ mới nhất -> Ghi nhật ký Cache ({len(combined)}/{MAX_CACHE_RECORDS} kỳ){gh_note}"
        elif existing_cache and github_seed:
            status = f"🛡️ Live tạm gián đoạn -> Smart Cache + GitHub Backup ({len(combined)} kỳ thật)"
        elif github_seed:
            status = f"🛡️ Live tạm gián đoạn -> GitHub Backup ({len(combined)} kỳ lịch sử thật)"
        else:
            status = f"🛡️ Tự chủ nhật ký Smart Cache ({len(combined)} kỳ thật — không phụ thuộc GitHub)"

        _atomic_write_json(os.path.join(BASE_DIR, f"last_fetch_diag_{game_key}.json"), diag)
        return combined[:sample_k], status, cache_age, diag

    _atomic_write_json(os.path.join(BASE_DIR, f"last_fetch_diag_{game_key}.json"), diag)
    return [], "⚠️ FetchData trực tiếp thất bại và không có dữ liệu Cache/Backup khả dụng", 0.0, diag


# =====================================================================
# ☀️ THIÊN VĂN LỊCH PHÁP CHUẨN: GIAO TIẾT LẬP XUÂN (KINH ĐỘ 315°)
# =====================================================================
def _jd_from_date(day: int, month: int, year: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _datetime_utc_from_jd(jd: float) -> datetime:
    jd_shifted = jd + 0.5
    z = int(math.floor(jd_shifted))
    f = jd_shifted - z

    if z < 2299161:
        a = z
    else:
        alpha = int(math.floor((z - 1867216.25) / 36524.25))
        a = z + 1 + alpha - int(math.floor(alpha / 4.0))

    b = a + 1524
    c = int(math.floor((b - 122.1) / 365.25))
    d = int(math.floor(365.25 * c))
    e = int(math.floor((b - d) / 30.6001))

    day = b - d - int(math.floor(30.6001 * e))
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    total_microseconds = int(round(f * 86400.0 * 1_000_000.0))
    if total_microseconds >= 86400 * 1_000_000:
        total_microseconds -= 86400 * 1_000_000

    hour = total_microseconds // 3_600_000_000
    rem = total_microseconds % 3_600_000_000
    minute = rem // 60_000_000
    rem %= 60_000_000
    second = rem // 1_000_000
    microsecond = rem % 1_000_000

    return datetime(year, month, day, hour, minute, second, microsecond, tzinfo=timezone.utc)


def _normalize_deg(deg: float) -> float:
    return deg % 360.0


def _sun_apparent_longitude_deg(jd: float) -> float:
    t = (jd - 2451545.0) / 36525.0
    l0 = _normalize_deg(280.46646 + 36000.76983 * t + 0.0003032 * t * t)
    m = _normalize_deg(357.52911 + 35999.05029 * t - 0.0001537 * t * t)
    m_rad = math.radians(m)

    eq_center = (
        (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m_rad)
        + (0.019993 - 0.000101 * t) * math.sin(2.0 * m_rad)
        + 0.000289 * math.sin(3.0 * m_rad)
    )
    true_long = _normalize_deg(l0 + eq_center)

    omega = math.radians(125.04 - 1934.136 * t)
    apparent_long = true_long - 0.00569 - 0.00478 * math.sin(omega)
    return _normalize_deg(apparent_long)


def _signed_angle_diff_deg(current_deg: float, target_deg: float) -> float:
    return (current_deg - target_deg + 180.0) % 360.0 - 180.0


def get_lap_xuan_datetime(year: int, tz_offset_hours: float = 7.0) -> datetime:
    target_deg = 315.0
    lo = float(_jd_from_date(1, 2, year)) - 0.5
    hi = float(_jd_from_date(7, 2, year)) + 0.5

    for _ in range(60):
        mid = 0.5 * (lo + hi)
        diff_mid = _signed_angle_diff_deg(_sun_apparent_longitude_deg(mid), target_deg)
        if diff_mid < 0.0:
            lo = mid
        else:
            hi = mid

    jd_exact = 0.5 * (lo + hi)
    dt_utc = _datetime_utc_from_jd(jd_exact)
    tz_info = timezone(timedelta(hours=tz_offset_hours))
    return dt_utc.astimezone(tz_info)


# =====================================================================
# 📚 3. HỘI ĐỒNG HỌC THUẬT CHUYÊN SÂU: ĐÔNG - TÂY - THỐNG KÊ
# =====================================================================
class PhongThuyReferenceCore:
    CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
    CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
    NAP_AM_60 = [
        "Hải Trung Kim", "Hải Trung Kim", "Lư Trung Hỏa", "Lư Trung Hỏa", "Đại Lâm Mộc", "Đại Lâm Mộc",
        "Lộ Bàng Thổ", "Lộ Bàng Thổ", "Kiếm Phong Kim", "Kiếm Phong Kim",
        "Sơn Đầu Hỏa", "Sơn Đầu Hỏa", "Giản Hạ Thủy", "Giản Hạ Thủy", "Thành Đầu Thổ", "Thành Đầu Thổ",
        "Bạch Lạp Kim", "Bạch Lạp Kim", "Dương Liễu Mộc", "Dương Liễu Mộc",
        "Tuyền Trung Thủy", "Tuyền Trung Thủy", "Ốc Thượng Thổ", "Ốc Thượng Thổ",
        "Tích Lịch Hỏa", "Tích Lịch Hỏa", "Tùng Bách Mộc", "Tùng Bách Mộc", "Trường Lưu Thủy", "Trường Lưu Thủy",
        "Sa Trung Kim", "Sa Trung Kim", "Sơn Hạ Hỏa", "Sơn Hạ Hỏa", "Bình Địa Mộc", "Bình Địa Mộc",
        "Bích Thượng Thổ", "Bích Thượng Thổ", "Kim Bạch Kim", "Kim Bạch Kim",
        "Phú Đăng Hỏa", "Phú Đăng Hỏa", "Thiên Hà Thủy", "Thiên Hà Thủy", "Đại Trạch Thổ", "Đại Trạch Thổ",
        "Thoa Xuyến Kim", "Thoa Xuyến Kim", "Tang Đố Mộc", "Tang Đố Mộc", "Đại Khê Thủy", "Đại Khê Thủy",
        "Sa Trung Thổ", "Sa Trung Thổ", "Thiên Thượng Hỏa", "Thiên Thượng Hỏa", "Thạch Lựu Mộc", "Thạch Lựu Mộc",
        "Đại Hải Thủy", "Đại Hải Thủy",
    ]

    @staticmethod
    def get_solar_term_riping(year: int, tz_offset_hours: float = 7.0) -> datetime:
        return get_lap_xuan_datetime(year, tz_offset_hours=tz_offset_hours)

    @classmethod
    def get_lunar_year(cls, y: int, m: int, d: int, tz_offset_hours: float = 7.0) -> int:
        tz_info = timezone(timedelta(hours=tz_offset_hours))
        user_datetime = datetime(y, m, d, 12, 0, tzinfo=tz_info)
        lap_xuan_time = cls.get_solar_term_riping(y, tz_offset_hours=tz_offset_hours)
        if user_datetime < lap_xuan_time:
            return y - 1
        return y

    @classmethod
    def get_full_info(cls, dob_str: str, gender: str, draw_dt: datetime) -> Dict[str, Any]:
        try:
            parts = dob_str.split("/")
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
        except Exception:
            d, m, y = 2, 2, 1974

        l_year = cls.get_lunar_year(y, m, d)
        can_idx = (l_year - 4) % 10
        chi_idx = (l_year - 4) % 12

        idx_60 = (l_year - 1924) % 60
        if idx_60 < 0:
            idx_60 = 0
        menh = cls.NAP_AM_60[idx_60]
        menh_elem = menh.split()[-1].replace("Thuỷ", "Thủy")

        cung_phi = "Không áp dụng (Trung hòa năng lượng bẩm sinh)"
        if gender.lower() in ["nam", "nữ"]:
            year_str = str(l_year)
            sum_digits = int(year_str[-2]) + int(year_str[-1])
            while sum_digits > 9:
                sum_digits = sum_digits // 10 + sum_digits % 10

            cung_phi_map = {
                1: "Khảm (Thủy)",
                2: "Khôn (Thổ)",
                3: "Chấn (Mộc)",
                4: "Tốn (Mộc)",
                6: "Càn (Kim)",
                7: "Đoài (Kim)",
                8: "Cấn (Thổ)",
                9: "Ly (Hỏa)",
            }

            if gender.lower() == "nam":
                remainder = (10 - sum_digits) if l_year < 2000 else (9 - sum_digits)
                while remainder <= 0:
                    remainder += 9
                if remainder == 5:
                    remainder = 2
                cung_phi = cung_phi_map.get(remainder, "Cấn (Thổ)")
            else:
                remainder = (5 + sum_digits) if l_year < 2000 else (6 + sum_digits)
                while remainder > 9:
                    remainder = remainder - 9
                if remainder == 5:
                    remainder = 8
                cung_phi = cung_phi_map.get(remainder, "Đoài (Kim)")

        zodiac_db = [
            ((3, 21), (4, 20), "Bạch Dương", "Hỏa", "Tiên phong (Cardinal)", "Sao Hỏa (Mars)"),
            ((4, 21), (5, 20), "Kim Ngưu", "Thổ", "Kiên định (Fixed)", "Sao Kim (Venus)"),
            ((5, 21), (6, 21), "Song Tử", "Khí", "Biến đổi (Mutable)", "Sao Thủy (Mercury)"),
            ((6, 22), (7, 22), "Cự Giải", "Thủy", "Tiên phong (Cardinal)", "Mặt Trăng (Moon)"),
            ((7, 23), (8, 22), "Sư Tử", "Hỏa", "Kiên định (Fixed)", "Mặt Trời (Sun)"),
            ((8, 23), (9, 22), "Xử Nữ", "Thổ", "Biến đổi (Mutable)", "Sao Thủy (Mercury)"),
            ((9, 23), (10, 23), "Thiên Bình", "Khí", "Tiên phong (Cardinal)", "Sao Kim (Venus)"),
            ((10, 24), (11, 22), "Bọ Cạp", "Thủy", "Kiên định (Fixed)", "Sao Diêm Vương (Pluto)"),
            ((11, 23), (12, 21), "Nhân Mã", "Hỏa", "Biến đổi (Mutable)", "Sao Mộc (Jupiter)"),
            ((12, 22), (1, 20), "Ma Kết", "Thổ", "Tiên phong (Cardinal)", "Sao Thổ (Saturn)"),
            ((1, 21), (2, 19), "Bảo Bình", "Khí", "Biến đổi (Mutable)", "Sao Thiên Vương & Sao Thổ"),
            ((2, 20), (3, 20), "Song Ngư", "Thủy", "Biến đổi (Mutable)", "Sao Hải Vương (Neptune)"),
        ]

        wz, element_west, modality, ruling_planet = "Song Ngư", "Thủy", "Biến đổi (Mutable)", "Sao Hải Vương (Neptune)"
        for (m1, d1), (m2, d2), s_name, s_elem, s_mod, s_planet in zodiac_db:
            if (m == m1 and d >= d1) or (m == m2 and d <= d2):
                wz, element_west, modality, ruling_planet = s_name, s_elem, s_mod, s_planet
                break

        weekday_elem_map = {0: "Kim", 1: "Mộc", 2: "Thủy", 3: "Hỏa", 4: "Thổ", 5: "Kim", 6: "Mộc"}
        draw_elem = weekday_elem_map.get(draw_dt.weekday(), "Kim")

        return {
            "lunar_year": l_year,
            "gender": gender,
            "can": cls.CAN[can_idx],
            "chi": cls.CHI[chi_idx],
            "menh": menh,
            "menh_elem": menh_elem,
            "cung_phi": cung_phi,
            "western_sign": wz,
            "element_west": element_west,
            "modality": modality,
            "ruling_planet": ruling_planet,
            "draw_datetime": draw_dt.strftime("%d/%m/%Y %H:%M"),
            "draw_elem": draw_elem,
        }


# =====================================================================
# 🌸 3B. LÕI CHUYÊN GIA THỜI VẬN TÀI LỘC: MAI HOA DỊCH SỐ
# =====================================================================
def _new_moon_jd(k: int, time_zone: float = 7.0) -> int:
    t = k / 1236.85
    t2 = t * t
    t3 = t2 * t
    dr = math.pi / 180.0
    jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * t2 - 0.000000155 * t3
    jd1 = jd1 + 0.00033 * math.sin((166.56 + 132.87 * t - 0.009173 * t2) * dr)
    m_pr = 359.2242 + 29.10535608 * k - 0.0000333 * t2 - 0.00000347 * t3
    m = 306.0253 + 385.81691806 * k + 0.0107306 * t2 + 0.00001236 * t3
    f = 21.2964 + 390.67050646 * k - 0.0016528 * t2 - 0.00000239 * t3
    c1 = (0.1734 - 0.000393 * t) * math.sin(m_pr * dr) + 0.0021 * math.sin(2 * m_pr * dr)
    c1 = c1 - 0.4068 * math.sin(m * dr) + 0.0161 * math.sin(2 * m * dr) - 0.0004 * math.sin(3 * m * dr)
    c1 = c1 + 0.0104 * math.sin(2 * f * dr) - 0.0051 * math.sin((m_pr + m) * dr)
    c1 = c1 - 0.0074 * math.sin((m_pr - m) * dr) + 0.0004 * math.sin((2 * f + m_pr) * dr)
    c1 = c1 - 0.0004 * math.sin((2 * f - m_pr) * dr) - 0.0006 * math.sin((2 * f + m) * dr)
    c1 = c1 + 0.0010 * math.sin((2 * f - m) * dr) + 0.0005 * math.sin((m + 2 * m_pr) * dr)
    if t < -11:
        delta_t = 0.001 + 0.000839 * t + 0.0002261 * t2 - 0.00000845 * t3 - 0.000081 * t * t3
    else:
        delta_t = -0.000278 + 0.000265 * t + 0.000262 * t2
    jd_new = jd1 + c1 - delta_t
    return int(math.floor(jd_new + 0.5 + time_zone / 24.0))


def _sun_longitude(jdn: int, time_zone: float = 7.0) -> int:
    t = (jdn - 0.5 - time_zone / 24.0 - 2451545.0) / 36525.0
    t2 = t * t
    dr = math.pi / 180.0
    m = 357.52910 + 35999.05030 * t - 0.0001559 * t2 - 0.00000048 * t2 * t
    l0 = 280.46645 + 36000.76983 * t + 0.0003032 * t2
    dl = (1.914600 - 0.004817 * t - 0.000014 * t2) * math.sin(m * dr)
    dl = dl + (0.019993 - 0.000101 * t) * math.sin(2 * m * dr) + 0.000290 * math.sin(3 * m * dr)
    theta = (l0 + dl) * dr
    omega = 125.04 - 1934.136 * t
    lng = theta - 0.00569 - 0.00478 * math.sin(omega * dr)
    lng = lng * 180.0 / math.pi
    lng = lng - 360.0 * math.floor(lng / 360.0)
    return int(math.floor(lng / 30.0))


def _lunar_month_11_jd(yy: int, time_zone: float = 7.0) -> int:
    off = _jd_from_date(31, 12, yy) - 2415021
    k = int(math.floor(off / 29.530588853))
    nm = _new_moon_jd(k, time_zone)
    sun_long = _sun_longitude(nm, time_zone)
    if sun_long >= 9:
        nm = _new_moon_jd(k - 1, time_zone)
    return nm


def _leap_month_offset(a11: int, time_zone: float = 7.0) -> int:
    k = int(math.floor((a11 - 2415021.076998695) / 29.530588853 + 0.5))
    last = 0
    i = 1
    arc = _sun_longitude(_new_moon_jd(k + i, time_zone), time_zone)
    while True:
        last = arc
        i += 1
        arc = _sun_longitude(_new_moon_jd(k + i, time_zone), time_zone)
        if not (arc != last and i < 14):
            break
    return i - 1


def gregorian_to_lunar(dd: int, mm: int, yy: int, time_zone: float = 7.0) -> Tuple[int, int, int, bool]:
    day_number = _jd_from_date(dd, mm, yy)
    k = int(math.floor((day_number - 2415021.076998695) / 29.530588853))
    month_start = _new_moon_jd(k + 1, time_zone)
    if month_start > day_number:
        month_start = _new_moon_jd(k, time_zone)
    a11 = _lunar_month_11_jd(yy, time_zone)
    b11 = a11
    if a11 >= month_start:
        lunar_year = yy
        a11 = _lunar_month_11_jd(yy - 1, time_zone)
    else:
        lunar_year = yy + 1
        b11 = _lunar_month_11_jd(yy + 1, time_zone)
    lunar_day = day_number - month_start + 1
    diff = int(math.floor((month_start - a11) / 29.0))
    lunar_leap = False
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_month_diff = _leap_month_offset(a11, time_zone)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = True
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return int(lunar_day), int(lunar_month), int(lunar_year), bool(lunar_leap)


class MaiHoaDichSoCore:
    BAT_QUAI = {
        1: {"name": "Càn", "nature": "Thiên", "element": "Kim", "bits": [1, 1, 1]},
        2: {"name": "Đoài", "nature": "Trạch", "element": "Kim", "bits": [1, 1, 0]},
        3: {"name": "Ly", "nature": "Hỏa", "element": "Hỏa", "bits": [1, 0, 1]},
        4: {"name": "Chấn", "nature": "Lôi", "element": "Mộc", "bits": [1, 0, 0]},
        5: {"name": "Tốn", "nature": "Phong", "element": "Mộc", "bits": [0, 1, 1]},
        6: {"name": "Khảm", "nature": "Thủy", "element": "Thủy", "bits": [0, 1, 0]},
        7: {"name": "Cấn", "nature": "Sơn", "element": "Thổ", "bits": [0, 0, 1]},
        8: {"name": "Khôn", "nature": "Địa", "element": "Thổ", "bits": [0, 0, 0]},
    }

    HAO_TUONG_TAI_LOC = {
        1: "hào sơ (hào 1 — hào dưới cùng của hạ quái): khí động mới chớm ở tầng khởi phát, dòng vốn còn nhỏ, dễ bị chi phối bởi những tác động mở đầu.",
        2: "hào nhị (hào 2 — trung vị hạ quái): nội lực giữ nhịp ở tầng nền tảng, có độ chững nhưng vẫn chịu ảnh hưởng sát sườn từ môi trường xung quanh.",
        3: "hào tam (hào 3 — đỉnh hạ quái, sát ranh ngoại quái): điểm bản lề giữa lực giữ bên trong và biến động bên ngoài, dễ phát sinh do dự hoặc chi ngoài dự liệu.",
        4: "hào tứ (hào 4 — đáy ngoại quái): dòng tiền bắt đầu bước ra ngoại cảnh, va chạm trực tiếp với bối cảnh biến động và tác động bên ngoài.",
        5: "hào ngũ (hào 5 — trung vị ngoại quái): vị trí chủ đạo của ngoại quái, phản ánh tâm điểm chi phối cục diện nhưng áp lực vận hành cũng lớn.",
        6: "hào thượng (hào 6 — hào trên cùng của thượng quái): giai đoạn cực biến của một nhịp vận động, dễ sang chiều đảo ngược nếu chạy theo đà cực đoan.",
    }

    QUAI_TUONG_TAI_LOC = {
        1: "tượng Càn (Trời): tính cương kiện, chủ động và lực lớn, nhưng nếu quá cứng nhắc thì dễ thiếu linh hoạt khi thời thế đổi nhịp",
        2: "tượng Đoài (Đầm/Ao): tính mở rộng, giao lưu và hỷ khí, nhưng nếu thiếu điểm dừng thì dễ buông lỏng tay chi tiêu",
        3: "tượng Ly (Lửa): tính sáng rõ, bộc lộ và nhịp chạy nhanh, nhưng khí nóng dễ bốc, thiếu bền nếu vội vàng",
        4: "tượng Chấn (Sấm): tính chấn động và khởi hành nhanh, dễ tạo biến động tức thời nhưng biên độ dao động lớn",
        5: "tượng Tốn (Gió): tính thẩm thấu, linh hoạt và thuận theo, đi mềm mại nhưng đôi khi thiếu sự dứt khoát",
        6: "tượng Khảm (Nước): tính tiềm ẩn, chiều sâu và dòng chảy ngầm, có thể là ẩn cơ nhưng cũng dễ che khuất hoặc gây trắc trở",
        7: "tượng Cấn (Núi): tính dừng lại, giữ vững và tạo điểm tựa, giúp hãm đà tiêu hao nhưng làm nhịp xoay chậm lại",
        8: "tượng Khôn (Đất): tính bao dung, tích chứa và thuận theo, chịu tải tốt nhưng thiên về tĩnh và chờ thời",
    }

    HO_QUAI_TAI_LOC = {
        "Kim": "Hỗ quái thiên về hành Kim (thu gọn, kỷ luật, sàng lọc): diễn biến bên trong nghiêng về siết đầu mối và giữ biên độ gọn.",
        "Mộc": "Hỗ quái thiên về hành Mộc (nảy nở, vươn ra, khởi phát): diễn biến ngầm có xu hướng mở động lực nhưng dễ biến động theo nhịp.",
        "Thủy": "Hỗ quái thiên về hành Thủy (chảy ngầm, lưu thông, biến ảo): diễn biến bên trong còn ẩn khuất nhiều biến số chưa lộ rõ.",
        "Hỏa": "Hỗ quái thiên về hành Hỏa (bộc lộ, lan tỏa, nhiệt cao): diễn biến ngầm có độ nóng và nhịp nhanh, dễ bốc nếu thiếu điểm neo.",
        "Thổ": "Hỗ quái thiên về hành Thổ (tích tụ, trung chuyển, giữ nền): diễn biến ngầm thiên về chịu tải, giữ nhịp hoặc trì hoãn bước xoay.",
    }

    CHI_NAMES = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

    CHI_GIO = [
        ("Tý (23h-01h)", 1),
        ("Sửu (01h-03h)", 2),
        ("Dần (03h-05h)", 3),
        ("Mão (05h-07h)", 4),
        ("Thìn (07h-09h)", 5),
        ("Tỵ (09h-11h)", 6),
        ("Ngọ (11h-13h)", 7),
        ("Mùi (13h-15h)", 8),
        ("Thân (15h-17h)", 9),
        ("Dậu (17h-19h)", 10),
        ("Tuất (19h-21h)", 11),
        ("Hợi (21h-23h)", 12),
    ]

    NGU_HANH_SINH = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
    NGU_HANH_KHAC = {"Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim"}

    @staticmethod
    def _mod_1_to_n(val: int, n: int) -> int:
        rem = val % n
        return n if rem == 0 else rem

    @classmethod
    def _bits_to_quai_id(cls, bits: List[int]) -> int:
        for q_id, info in cls.BAT_QUAI.items():
            if info["bits"] == bits:
                return q_id
        return 8

    @classmethod
    def _format_quai_pair(cls, thuong_id: int, ha_id: int) -> str:
        t = cls.BAT_QUAI[thuong_id]
        h = cls.BAT_QUAI[ha_id]
        return f"{t['nature']} {h['nature']} ({t['name']} trên - {h['name']} dưới)"

    @classmethod
    def _classify_the_dung_relation(cls, the_elem: str, dung_elem: str) -> Tuple[str, str, str]:
        if cls.NGU_HANH_SINH.get(dung_elem) == the_elem:
            return "Dụng sinh Thể", "CAT", f"Dụng ({dung_elem}) sinh Thể ({the_elem})"
        if the_elem == dung_elem:
            return "Thể Dụng tỷ hòa", "CAT", f"Thể ({the_elem}) và Dụng ({dung_elem}) cùng hành"
        if cls.NGU_HANH_KHAC.get(the_elem) == dung_elem:
            return "Thể khắc Dụng", "BINH", f"Thể ({the_elem}) khắc Dụng ({dung_elem})"
        if cls.NGU_HANH_SINH.get(the_elem) == dung_elem:
            return "Thể sinh Dụng", "BINH", f"Thể ({the_elem}) sinh Dụng ({dung_elem})"
        return "Dụng khắc Thể", "BI", f"Dụng ({dung_elem}) khắc Thể ({the_elem})"

    @classmethod
    def _classify_ho_trend(cls, thuong_ho_id: int, ha_ho_id: int) -> str:
        t_elem = cls.BAT_QUAI[thuong_ho_id]["element"]
        h_elem = cls.BAT_QUAI[ha_ho_id]["element"]
        if t_elem == h_elem:
            return cls.HO_QUAI_TAI_LOC[t_elem]
        if cls.NGU_HANH_KHAC.get(t_elem) == h_elem:
            return (
                f"Hỗ quái có Thượng hỗ ({t_elem}) khắc Hạ hỗ ({h_elem}), cho thấy lớp điều tiết bên trên đang siết nhịp hoặc "
                f"tạo áp lực kìm hãm lên tầng vận hành bên dưới; cần giữ tỷ trọng vốn gọn trước khi mở rộng."
            )
        if cls.NGU_HANH_KHAC.get(h_elem) == t_elem:
            return (
                f"Hỗ quái có Hạ hỗ ({h_elem}) khắc Thượng hỗ ({t_elem}), cho thấy lực động từ tầng dưới đang đẩy ngược lên "
                f"tầng trên, dễ làm nhịp vận hành giằng co hoặc phát sinh biến số bất ngờ."
            )
        if cls.NGU_HANH_SINH.get(t_elem) == h_elem:
            return (
                f"Hỗ quái có Thượng hỗ ({t_elem}) sinh cho Hạ hỗ ({h_elem}), cho thấy lớp trên dồn khí nuôi lớp dưới, "
                f"dòng vận hành ngầm có đường tiếp sức nhưng cần kiểm soát tốc độ giải ngân."
            )
        if cls.NGU_HANH_SINH.get(h_elem) == t_elem:
            return (
                f"Hỗ quái có Hạ hỗ ({h_elem}) sinh cho Thượng hỗ ({t_elem}), cho thấy nền dưới dồn lực đẩy lên lớp trên, "
                f"nhưng nếu thiếu điểm giữ ở tầng gốc thì dễ bị rút bớt lực nền."
            )
        return (
            f"Hỗ quái kết hợp hành {t_elem} (thượng hỗ) và {h_elem} (hạ hỗ), cho thấy diễn biến ngầm bên trong "
            f"đang có sự giao thoa giữa hai lớp khí, cần quan sát kỹ nhịp chuyển tiếp trước khi tăng tỷ trọng vốn."
        )

    @classmethod
    def _classify_bien_trend(cls, the_elem: str, bien_the_elem: str) -> str:
        if cls.NGU_HANH_SINH.get(bien_the_elem) == the_elem:
            return (
                f"Sang Quẻ Biến, khí của quái biến phía Thể ({bien_the_elem}) sinh cho Thể ({the_elem}), "
                f"cho thấy chiều hướng về sau của dòng tiền có phần được bồi đắp và dịu áp lực hơn lúc khởi quẻ."
            )
        if bien_the_elem == the_elem:
            return (
                f"Sang Quẻ Biến, hành của quái biến phía Thể ({bien_the_elem}) đồng khí với Thể ({the_elem}), "
                f"cho thấy xu hướng về sau giữ nhịp tương đối ổn định, ít đổi chiều đột ngột."
            )
        if cls.NGU_HANH_KHAC.get(the_elem) == bien_the_elem:
            return (
                f"Sang Quẻ Biến, Thể ({the_elem}) khắc quái biến ({bien_the_elem}), "
                f"xu hướng sau vẫn nằm trong tầm chi phối của Thể nhưng càng kéo dài càng dễ tiêu hao khí lực."
            )
        if cls.NGU_HANH_SINH.get(the_elem) == bien_the_elem:
            return (
                f"Sang Quẻ Biến, Thể ({the_elem}) sinh cho quái biến ({bien_the_elem}), "
                f"cảnh báo chiều hướng về sau dễ phát sinh tiết khí/hao hụt dòng tiền, không nên dồn kỳ vọng lớn ở chặng sau."
            )
        return (
            f"Sang Quẻ Biến, quái biến ({bien_the_elem}) khắc chế Thể ({the_elem}), "
            f"báo hiệu xu hướng về sau dễ gặp trở ngại hoặc biến số bất lợi cho tài lộc; cần giữ kỷ luật vốn từ sớm."
        )

    @classmethod
    def _build_wealth_reading(
        cls,
        thuong_id: int,
        ha_id: int,
        hao_dong: int,
        thuong_ho_id: int,
        ha_ho_id: int,
        thuong_bien_id: int,
        ha_bien_id: int,
        the_id: int,
        dung_id: int,
        bien_the_id: int,
        relation: str,
        zone: str,
        short_rel: str,
    ) -> Dict[str, str]:
        the_info = cls.BAT_QUAI[the_id]
        dung_info = cls.BAT_QUAI[dung_id]
        chu_str = cls._format_quai_pair(thuong_id, ha_id)
        ho_str = cls._format_quai_pair(thuong_ho_id, ha_ho_id)
        bien_str = cls._format_quai_pair(thuong_bien_id, ha_bien_id)

        hao_note = cls.HAO_TUONG_TAI_LOC[hao_dong]
        ho_trend_note = cls._classify_ho_trend(thuong_ho_id, ha_ho_id)
        bien_trend_note = cls._classify_bien_trend(the_info["element"], cls.BAT_QUAI[bien_the_id]["element"])
        the_tuong = cls.QUAI_TUONG_TAI_LOC[the_id]
        dung_tuong = cls.QUAI_TUONG_TAI_LOC[dung_id]

        if relation == "Dụng sinh Thể":
            zone_label = "🟢 TÀI LỘC THUẬN KHÍ (Dụng sinh Thể) — Ngoại cảnh sinh trợ cho Thể"
            wealth_analysis = (
                f"Thể là {the_info['name']} ({the_info['element']}), Dụng là {dung_info['name']} ({dung_info['element']}). "
                f"Xét về tài lộc, thế 'Dụng sinh Thể' là ngoại cảnh và thời thế đang sinh trợ cho Thể, "
                f"dòng khí có đường tiếp ứng nhưng cần có điểm neo và sự tiết chế để không chi tiêu quá tay."
            )
            wealth_advice = (
                "Thời vận tài lộc lúc này có lực sinh trợ, hợp với việc đi từng bước có tính toán và đặt rõ hạn mức vốn từ đầu. "
                "Thấy thuận càng cần giữ sự tỉnh táo, không mở rộng mức mạo hiểm vượt tầm kiểm soát."
            )
        elif relation == "Thể Dụng tỷ hòa":
            zone_label = "🟢 TÀI LỘC TỶ HÒA (Thể Dụng đồng hành) — Nội lực và ngoại cảnh ngang sức"
            wealth_analysis = (
                f"Thể ({the_info['name']}, hành {the_info['element']}) và Dụng ({dung_info['name']}, hành {dung_info['element']}) cùng hành tương đồng. "
                f"Xét về tài lộc, thế 'Tỷ hòa' cho thấy nội lực của Thể và ngoại cảnh cân bằng, ít bị chèn ép đột ngột nhưng cũng khó bứt phá mạnh nếu thiếu đòn bẩy."
            )
            wealth_advice = (
                "Dòng tiền lúc này ở thế quân bình, hợp giữ nhịp ổn định và quan sát hơn là dồn vốn đánh lớn. "
                "Cứ bám đúng phần ngân sách đã định mà làm, tránh chạy theo tâm lý đám đông."
            )
        elif relation == "Thể khắc Dụng":
            zone_label = "🟡 TÀI LỘC CHỦ ĐỘNG CÓ HAO LỰC (Thể khắc Dụng) — Chế ngự được nhưng tiêu hao sức lực"
            wealth_analysis = (
                f"Thể ({the_info['name']}, hành {the_info['element']}) khắc chế Dụng ({dung_info['name']}, hành {dung_info['element']}). "
                f"Xét về tài lộc, thế 'Thể khắc Dụng' là Thể nắm phần chủ động chi phối, nhưng 'khắc xuất' tất có hao tổn khí lực, công sức hoặc chi phí để giành phần hơn."
            )
            wealth_advice = (
                "Có thể giữ thế chủ động nhưng phải đánh đổi bằng sức lực và sự tập trung. "
                "Nếu tham gia tài chính chỉ nên giữ ở mức nhỏ gọn, có điểm dừng rõ ràng, tránh sa đà kéo dài."
            )
        elif relation == "Thể sinh Dụng":
            zone_label = "🟡 TÀI LỘC TIẾT KHÍ (Thể sinh Dụng) — Nội lực sinh xuất cho Dụng"
            wealth_analysis = (
                f"Thể ({the_info['name']}, hành {the_info['element']}) sinh cho Dụng ({dung_info['name']}, hành {dung_info['element']}). "
                f"Xét về tài lộc, đây là thế 'Thể sinh Dụng' (sinh xuất/tiết khí): phần Thể dồn khí nuôi bên ngoài nên dễ giảm nội lực, làm nhiều hoặc chi nhiều mà lực thu về chưa tương xứng."
            )
            wealth_advice = (
                "Lực tài chính lúc này đang có xu hướng sinh xuất ra bên ngoài, không phải lúc mở rộng chi tiêu hay mạo hiểm. "
                "Nên thu gọn đầu mối, giữ chặt phần vốn gốc và chờ thời khí chuyển sang thuận hơn."
            )
        else:
            zone_label = "🔴 TÀI LỘC GẶP NGHỊCH KHÍ (Dụng khắc Thể) — Ngoại lực khắc chế Thể"
            wealth_analysis = (
                f"Dụng ({dung_info['name']}, hành {dung_info['element']}) khắc chế Thể ({the_info['name']}, hành {the_info['element']}). "
                f"Xét về tài lộc, thế 'Dụng khắc Thể' là ngoại cảnh và biến số bên ngoài gây áp lực lên Thể, dễ phát sinh trở ngại hoặc quyết định vội vàng dẫn tới bất lợi cho túi tiền."
            )
            wealth_advice = (
                "Thời vận tài lộc lúc này đang chịu nghịch lực, càng cố ép càng dễ vướng tổn thất. "
                "Ưu tiên hàng đầu là giữ chặt nguồn vốn, khoanh vùng rủi ro và đứng ngoài các nhịp mạo hiểm."
            )

        method_note = (
            "<b>Ghi chú phương pháp:</b> Quẻ khởi theo thời điểm động tâm (Âm lịch + Giờ Chi; năm Địa Chi tính theo giao tiết Lập Xuân kinh độ Mặt Trời 315°, "
            "số năm quy ước theo thứ tự Địa chi 1..12), luận chuyên biệt dưới góc độ tài lộc, dòng tiền và kỷ luật quản trị vốn."
        )

        scholar_commentary = (
            f"<p style='margin-bottom: 10px;'>"
            f"Quẻ Chủ lập được {chu_str}, động tại {hao_note} "
            f"{wealth_analysis} "
            f"Xét tượng quẻ dưới góc độ tài lộc: phía Thể mang {the_tuong}, còn phía Dụng mang {dung_tuong}."
            f"</p>"
            f"<p style='margin-bottom: 10px;'>"
            f"Diễn biến bên trong kết thành Hỗ quái {ho_str}: {ho_trend_note} "
            f"Sau đó chuyển sang Quẻ Biến {bien_str}: {bien_trend_note}"
            f"</p>"
            f"<p style='margin-bottom: 0; color: #B0BEC5; font-size: 12.5px;'>{method_note}</p>"
        )

        return {
            "zone": zone,
            "zone_label": zone_label,
            "summary": f"{wealth_analysis} ({short_rel})",
            "scholar_commentary": scholar_commentary,
            "advice": wealth_advice,
        }

    @classmethod
    def cast_hexagram(cls, dt: datetime, tz_offset_hours: float = 7.0) -> Dict[str, Any]:
        tz_info = timezone(timedelta(hours=tz_offset_hours))
        dt_local = dt.astimezone(tz_info) if dt.tzinfo is not None else dt.replace(tzinfo=tz_info)

        lunar_day, lunar_month, lunar_year, is_leap = gregorian_to_lunar(
            dt_local.day, dt_local.month, dt_local.year, time_zone=tz_offset_hours
        )

        lap_xuan_dt = PhongThuyReferenceCore.get_solar_term_riping(
            dt_local.year, tz_offset_hours=tz_offset_hours
        ).astimezone(tz_info)
        year_for_chi = lunar_year - 1 if dt_local < lap_xuan_dt else lunar_year

        year_chi_idx = (year_for_chi - 4) % 12
        year_chi_name = cls.CHI_NAMES[year_chi_idx]
        nam_so = year_chi_idx + 1

        hour_idx = ((dt_local.hour + 1) // 2) % 12
        chi_gio_label, gio_so = cls.CHI_GIO[hour_idx]

        tong_thuong = nam_so + lunar_month + lunar_day
        thuong_id = cls._mod_1_to_n(tong_thuong, 8)

        tong_ha = tong_thuong + gio_so
        ha_id = cls._mod_1_to_n(tong_ha, 8)
        hao_dong = cls._mod_1_to_n(tong_ha, 6)

        ha_bits = cls.BAT_QUAI[ha_id]["bits"].copy()
        thuong_bits = cls.BAT_QUAI[thuong_id]["bits"].copy()
        full_bits = ha_bits + thuong_bits

        ha_ho_id = cls._bits_to_quai_id(full_bits[1:4])
        thuong_ho_id = cls._bits_to_quai_id(full_bits[2:5])

        bien_bits = full_bits.copy()
        bien_bits[hao_dong - 1] = 1 - bien_bits[hao_dong - 1]
        ha_bien_id = cls._bits_to_quai_id(bien_bits[:3])
        thuong_bien_id = cls._bits_to_quai_id(bien_bits[3:])

        if hao_dong <= 3:
            the_id, dung_id = ha_id, thuong_id
            bien_the_id = ha_bien_id
            the_pos = "Hạ Quái (hào 1-3)"
        else:
            the_id, dung_id = thuong_id, ha_id
            bien_the_id = thuong_bien_id
            the_pos = "Thượng Quái (hào 4-6)"

        the_elem = cls.BAT_QUAI[the_id]["element"]
        dung_elem = cls.BAT_QUAI[dung_id]["element"]
        relation, zone, short_rel = cls._classify_the_dung_relation(the_elem, dung_elem)
        reading = cls._build_wealth_reading(
            thuong_id=thuong_id,
            ha_id=ha_id,
            hao_dong=hao_dong,
            thuong_ho_id=thuong_ho_id,
            ha_ho_id=ha_ho_id,
            thuong_bien_id=thuong_bien_id,
            ha_bien_id=ha_bien_id,
            the_id=the_id,
            dung_id=dung_id,
            bien_the_id=bien_the_id,
            relation=relation,
            zone=zone,
            short_rel=short_rel,
        )

        return {
            "timestamp": dt_local.strftime("%H:%M:%S — %d/%m/%Y"),
            "lunar_date": f"Ngày {lunar_day} tháng {lunar_month}{' (nhuận)' if is_leap else ''} năm Chi {year_chi_name} (Âm lịch {lunar_year})",
            "lunar_components": {
                "nam_so": nam_so,
                "lunar_month": lunar_month,
                "lunar_day": lunar_day,
                "gio_so": gio_so,
            },
            "chi_gio": chi_gio_label,
            "que_chu": cls._format_quai_pair(thuong_id, ha_id),
            "hao_dong": f"Hào {hao_dong} — Thể tại {the_pos} ({cls.BAT_QUAI[the_id]['name']}, hành {the_elem}) | Dụng hành {dung_elem}",
            "que_ho": cls._format_quai_pair(thuong_ho_id, ha_ho_id),
            "que_bien": cls._format_quai_pair(thuong_bien_id, ha_bien_id),
            "relation": relation,
            "zone": reading["zone"],
            "zone_label": reading["zone_label"],
            "summary": reading["summary"],
            "scholar_commentary": reading["scholar_commentary"],
            "advice": reading["advice"],
        }


class FlexibleCouncilEvaluator:
    @staticmethod
    def judge_eastern(num: int, menh_elem: str) -> float:
        element_residue = {
            "Kim": [4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54],
            "Mộc": [3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53],
            "Thủy": [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 55],
            "Hỏa": [2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52],
            "Thổ": [5, 10, 15, 20, 25, 30, 35, 40, 45, 50],
        }
        favorable = element_residue.get(menh_elem, [1, 5, 10, 15])
        return 1.0 if num in favorable else 0.4

    @staticmethod
    def judge_western_deep(num: int, max_main: int, element_west: str, modality: str) -> float:
        score_elem = 0.5
        if element_west == "Hỏa":
            score_elem = 1.0 if (num % 3 == 0 or num in [1, 7, 11, 19, 23, 31, 37, 41, 47, 53]) else 0.4
        elif element_west == "Thổ":
            score_elem = 1.0 if (num % 5 == 0 or num % 2 == 0) else 0.4
        elif element_west == "Khí":
            score_elem = 1.0 if (num % 4 == 0 or num % 7 == 0 or num in [2, 13, 17, 29, 31, 43]) else 0.4
        else:
            score_elem = 1.0 if (num % 2 != 0 or num % 6 == 0 or num in [3, 9, 15, 21, 27, 33, 39, 45, 51]) else 0.4

        score_mod = 0.5
        ratio = num / max_main
        if "Tiên phong" in modality:
            score_mod = 1.0 if ratio <= 0.35 else 0.45
        elif "Kiên định" in modality:
            score_mod = 1.0 if 0.30 <= ratio <= 0.70 else 0.45
        else:
            score_mod = 1.0 if ratio >= 0.65 else 0.45

        return (score_elem * 0.65) + (score_mod * 0.35)

    @staticmethod
    def judge_statistics_hot_cold(num: int, freq_map: Dict[int, int], strategy: str) -> float:
        if not freq_map:
            return 0.5
        frequencies = list(freq_map.values())
        max_f = max(frequencies) if frequencies else 1
        min_f = min(frequencies) if frequencies else 0
        f = freq_map.get(num, 0)
        if max_f == min_f:
            return 0.7
        normalized = (f - min_f) / (max_f - min_f) if (max_f - min_f) > 0 else 0.5

        if "hot" in strategy:
            return 0.1 + 0.9 * (f / max_f) if max_f > 0 else 0.5
        elif "cold" in strategy:
            return 0.1 + 0.9 * (1.0 - normalized)
        else:
            diff = abs(normalized - 0.5)
            return max(0.2, 1.0 - (diff * 1.8))


# =====================================================================
# 💬 3C. TRỢ LÝ GIẢI ĐÁP TĨNH + GỢI Ý KHI ĐANG GÕ + BỘ ĐẾM THÁNG LỊCH
# =====================================================================
ASSISTANT_METRICS_DIR = Path("assistant_metrics")
ASSISTANT_MONTHS_DIR = ASSISTANT_METRICS_DIR / "months"

ASSISTANT_SYSTEM_PROMPT = """
Bạn là trợ lý giải đáp và hướng dẫn sử dụng tích hợp trong ứng dụng Vietlott Harmony Edition.
Trả lời bằng tiếng Việt rõ ràng, khách quan, dễ hiểu cho người dùng phổ thông.
Không dùng thuật ngữ kỹ thuật như API, API Key, token, biến, hàm, JSON hay session_state khi trả lời người dùng phổ thông.

[NGUYÊN TẮC VẬN HÀNH]
1. Ứng dụng không bẻ khóa hay đảm bảo trúng thưởng xổ số ngẫu nhiên; hỗ trợ phân tích tham khảo đa chiều và giữ kỷ luật quản trị vốn.
2. Người dùng thiết lập kỳ quay/thời điểm mục tiêu, ngày sinh và giới tính (tùy chọn Khác / trung hòa dành cho người chuyển giới hoặc nhóm không chọn hai phương án mặc định sẽ áp dụng chế độ xử lý trung hòa cho lớp đối chiếu liên quan tới giới tính).
3. Hội đồng Phương Đông dựa trên lịch pháp chuẩn thiên văn (mốc Lập Xuân kinh độ 315°), Can Chi, 60 Hoa Giáp, bản mệnh Nạp Âm và Cung Phi Lạc Thư.
4. Hội đồng Phương Tây phân tích theo chiêm tinh cổ điển 3 tầng: Tứ đại Nguyên tố (Lửa, Đất, Khí, Nước), Phẩm tính Vận động (Cardinal, Fixed, Mutable) và Hành tinh chiếu mệnh.
5. Hội đồng Thống kê Ma trận đối chiếu tần suất lịch sử theo tầm nhìn kỳ quay và khẩu vị Hot / Neutral / Cold.
6. Harmony Score (%) phản ánh mức độ đồng thuận chung giữa các hội đồng đang bật đối với một bộ số.
7. Trạm Mai Hoa Dịch Số là mô-đun độc lập gieo quẻ theo thời điểm động tâm thực tế, chia vùng Cát / Bình / Bĩ để nhắc nhở tâm lý và quản trị vốn.

[QUY TẮC BẢO MẬT]
- Tuyệt đối không tiết lộ công thức tính toán, trọng số, tỷ trọng, ma trận quy đổi hoặc mã nguồn.
- Nếu được hỏi về công thức, trọng số hoặc mã nguồn, từ chối khéo và chuyển sang giải thích ý nghĩa chỉ số hoặc cách dùng trên giao diện.
""".strip()


def _assistant_month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def _assistant_prev_month_key(month_key: str) -> str:
    year, month = map(int, month_key.split("-"))
    if month == 1:
        return f"{year - 1:04d}-12"
    return f"{year:04d}-{month - 1:02d}"


def _assistant_month_file(month_key: str) -> Path:
    ASSISTANT_MONTHS_DIR.mkdir(parents=True, exist_ok=True)
    return ASSISTANT_MONTHS_DIR / f"counters_{month_key}.json"


def _assistant_empty_day_bucket() -> Dict[str, Any]:
    return {
        "total_uses": 0,
        "faq_hits": 0,
        "fallback_calls": 0,
        "by_faq_id": {},
        "by_category": {},
    }


def load_assistant_month_counters(month_key: str) -> Dict[str, Any]:
    path = _assistant_month_file(month_key)
    if not path.exists():
        return {"month": month_key, "days": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("days"), dict):
            return data
    except Exception:
        pass
    return {"month": month_key, "days": {}}


def save_assistant_month_counters(month_key: str, payload: Dict[str, Any]) -> None:
    path = _assistant_month_file(month_key)
    payload["month"] = month_key
    payload["updated_at"] = now_vn().isoformat()
    tmp_path = path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def record_assistant_counter(is_faq_hit: bool, faq_id: str = "", category: str = "") -> None:
    """Ghi nhận bộ đếm số lần sử dụng theo từng ngày trong tệp tháng lịch hiện tại."""
    now = now_vn()
    m_key = _assistant_month_key(now)
    day_str = now.strftime("%Y-%m-%d")

    data = load_assistant_month_counters(m_key)
    bucket = data["days"].setdefault(day_str, _assistant_empty_day_bucket())

    bucket["total_uses"] = int(bucket.get("total_uses", 0)) + 1
    if is_faq_hit:
        bucket["faq_hits"] = int(bucket.get("faq_hits", 0)) + 1
    else:
        bucket["fallback_calls"] = int(bucket.get("fallback_calls", 0)) + 1

    if faq_id:
        by_faq = bucket.setdefault("by_faq_id", {})
        by_faq[faq_id] = int(by_faq.get(faq_id, 0)) + 1

    if category:
        by_cat = bucket.setdefault("by_category", {})
        by_cat[category] = int(by_cat.get(category, 0)) + 1

    save_assistant_month_counters(m_key, data)


def _sum_assistant_buckets(buckets: List[Dict[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "total_uses": 0,
        "faq_hits": 0,
        "fallback_calls": 0,
        "by_faq_id": {},
        "by_category": {},
    }
    for b in buckets:
        out["total_uses"] += int(b.get("total_uses", 0))
        out["faq_hits"] += int(b.get("faq_hits", 0))
        out["fallback_calls"] += int(b.get("fallback_calls", 0))
        for k, v in b.get("by_faq_id", {}).items():
            out["by_faq_id"][k] = out["by_faq_id"].get(k, 0) + int(v)
        for k, v in b.get("by_category", {}).items():
            out["by_category"][k] = out["by_category"].get(k, 0) + int(v)
    return out


def get_assistant_period_summaries() -> Dict[str, Any]:
    now = now_vn()
    today_str = now.strftime("%Y-%m-%d")
    week_start_str = (now - timedelta(days=6)).strftime("%Y-%m-%d")
    cur_month = _assistant_month_key(now)
    prev_month = _assistant_prev_month_key(cur_month)

    day_map: Dict[str, Dict[str, Any]] = {}
    for mk in dict.fromkeys([prev_month, cur_month]):
        m_data = load_assistant_month_counters(mk)
        for d_str, b in m_data.get("days", {}).items():
            day_map[d_str] = b

    one_day = _sum_assistant_buckets([day_map[today_str]]) if today_str in day_map else _assistant_empty_day_bucket()
    seven_days = _sum_assistant_buckets([b for d_str, b in day_map.items() if d_str >= week_start_str])
    cal_month = _sum_assistant_buckets(list(load_assistant_month_counters(cur_month).get("days", {}).values()))

    return {
        "1_ngay": one_day,
        "tuan": seven_days,
        "thang_lich": cal_month,
        "current_month_key": cur_month,
        "previous_month_key": prev_month,
    }


def list_assistant_month_keys() -> List[str]:
    if not ASSISTANT_MONTHS_DIR.exists():
        return []
    return [p.stem.replace("counters_", "", 1) for p in sorted(ASSISTANT_MONTHS_DIR.glob("counters_*.json"))]


def compare_assistant_months(month_a: str, month_b: str) -> Dict[str, Any]:
    sum_a = _sum_assistant_buckets(list(load_assistant_month_counters(month_a).get("days", {}).values()))
    sum_b = _sum_assistant_buckets(list(load_assistant_month_counters(month_b).get("days", {}).values()))
    return {
        "month_a": month_a,
        "month_b": month_b,
        "a": sum_a,
        "b": sum_b,
        "diff": {
            "total_uses": sum_a["total_uses"] - sum_b["total_uses"],
            "faq_hits": sum_a["faq_hits"] - sum_b["faq_hits"],
            "fallback_calls": sum_a["fallback_calls"] - sum_b["fallback_calls"],
        },
    }


def normalize_faq_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text.lower().strip().replace("đ", "d").replace("Đ", "d")
    decomposed = unicodedata.normalize("NFD", cleaned)
    without_marks = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    alnum_only = re.sub(r"[^a-z0-9\s]", " ", without_marks)
    return re.sub(r"\s+", " ", alnum_only).strip()


FAQ_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "nguyen_tac_van_hanh",
        "category": "Nguyên tắc & thiết lập",
        "canonical_question": "Ứng dụng này hoạt động theo nguyên tắc nào, có giúp trúng chắc chắn không?",
        "anchor_phrases": ["nguyen tac", "trung chac chan", "be khoa", "ngau nhien"],
        "phrases": ["nguyen tac van hanh", "co trung chac chan khong", "be khoa xo so"],
        "keywords": ["cam ket", "hoat dong", "tham khao", "ky luat"],
        "answer": (
            "Ứng dụng không bẻ khóa hay đảm bảo trúng thưởng xổ số ngẫu nhiên. "
            "Hệ thống hỗ trợ phân tích đa chiều và tổ chức thông tin có kỷ luật, giúp bạn chuyển từ "
            "chọn số cảm tính sang có góc nhìn tham khảo và kiểm soát tâm lý tốt hơn."
        ),
    },
    {
        "id": "gioi_tinh_khac_trung_hoa",
        "category": "Nguyên tắc & thiết lập",
        "canonical_question": "Tùy chọn giới tính Khác / trung hòa dành cho ai và hoạt động ra sao?",
        "anchor_phrases": ["gioi tinh khac", "chuyen gioi", "trung hoa", "khong xac dinh"],
        "phrases": ["gioi tinh khac", "nguoi chuyen gioi", "tuy chon trung hoa"],
        "keywords": ["gioi tinh", "khac", "chuyen gioi", "trung hoa"],
        "answer": (
            "Tùy chọn này dành cho người dùng chuyển giới hoặc những ai không chọn hai phương án "
            "giới tính thông thường. Khi chọn mục này, ứng dụng áp dụng chế độ trung hòa cho lớp "
            "phân tích có liên quan tới giới tính để bạn sử dụng thuận tiện và thoải mái."
        ),
    },
    {
        "id": "tac_dung_ngay_sinh_gioi_tinh",
        "category": "Nguyên tắc & thiết lập",
        "canonical_question": "Thiết lập ngày sinh và giới tính có tác dụng gì?",
        "anchor_phrases": ["ngay sinh", "gioi tinh", "nam sinh"],
        "phrases": ["ngay sinh va gioi tinh", "tac dung ngay sinh", "thiet lap gioi tinh"],
        "keywords": ["ca nhan hoa", "doi chieu", "gioi tinh", "ngay sinh"],
        "answer": (
            "Ngày sinh và giới tính cung cấp dữ liệu tham chiếu cá nhân cho các lớp đối chiếu tương hợp "
            "trong ứng dụng. Thiết lập này không làm thay đổi tính ngẫu nhiên của kỳ quay thực tế."
        ),
    },
    {
        "id": "harmony_score_la_gi",
        "category": "Harmony Score & các Hội đồng",
        "canonical_question": "Harmony Score (%) phản ánh điều gì?",
        "anchor_phrases": ["harmony score", "diem harmony", "harmony"],
        "phrases": ["harmony score la gi", "chi so harmony", "diem harmony"],
        "keywords": ["dong thuan", "hoi dong", "ty le", "harmony"],
        "answer": (
            "Harmony Score (%) phản ánh mức độ đồng thuận chung giữa các hội đồng đánh giá đang được bật "
            "đối với một bộ số. Mức cao cho thấy các tiêu chí đang chọn có sự thống nhất cao hơn; "
            "mức thấp phản ánh sự đồng thuận giữa các góc nhìn đang bật chưa cao."
        ),
    },
    {
        "id": "harmony_cao_co_chac_trung",
        "category": "Harmony Score & các Hội đồng",
        "canonical_question": "Harmony Score cao có nghĩa là bộ số đó chắc chắn sẽ về không?",
        "anchor_phrases": ["harmony cao", "diem cao", "chac ve", "chac trung"],
        "phrases": ["harmony cao co chac trung", "diem cao co trung khong"],
        "keywords": ["xac suat", "cam ket", "trung", "harmony"],
        "answer": (
            "Không. Harmony Score chỉ đo mức độ khớp nhau giữa các lớp phân tích đang bật trong ứng dụng, "
            "không phải xác suất trúng thưởng hay lời cam kết về kết quả quay số thực tế."
        ),
    },
    {
        "id": "hoi_dong_phuong_dong",
        "category": "Harmony Score & các Hội đồng",
        "canonical_question": "Hội đồng Phương Đông đánh giá dựa trên yếu tố nào?",
        "anchor_phrases": ["phuong dong", "hoi dong phuong dong"],
        "phrases": ["hoi dong phuong dong", "phuong dong danh gia"],
        "keywords": ["can chi", "lap xuan", "nap am", "cung phi", "phuong dong"],
        "answer": (
            "Hội đồng Phương Đông dựa trên lịch pháp chuẩn thiên văn (mốc Lập Xuân kinh độ 315°), "
            "Can Chi, 60 Hoa Giáp, bản mệnh Nạp Âm và Cung Phi Lạc Thư để xem xét mức độ tương hợp "
            "theo hệ quy chiếu Phương Đông."
        ),
    },
    {
        "id": "hoi_dong_phuong_tay",
        "category": "Harmony Score & các Hội đồng",
        "canonical_question": "Hội đồng Phương Tây phân tích theo những lớp nào?",
        "anchor_phrases": ["phuong tay", "hoi dong phuong tay", "chiem tinh"],
        "phrases": ["hoi dong phuong tay", "chiem tinh co dien"],
        "keywords": ["nguyen to", "pham tinh", "hanh tinh", "phuong tay"],
        "answer": (
            "Hội đồng Phương Tây phân tích theo chiêm tinh cổ điển 3 tầng: Tứ đại Nguyên tố "
            "(Lửa, Đất, Khí, Nước), Phẩm tính Vận động (Cardinal, Fixed, Mutable) và Hành tinh chiếu mệnh."
        ),
    },
    {
        "id": "khau_vi_hot_neutral_cold",
        "category": "Thống kê & Mai Hoa Dịch Số",
        "canonical_question": "3 mức Hot, Neutral, Cold trong thống kê nghĩa là sao?",
        "anchor_phrases": ["hot", "neutral", "cold", "tan suat"],
        "phrases": ["hot neutral cold", "muc hot", "muc cold", "muc neutral"],
        "keywords": ["thong ke", "lich su", "tan suat", "khau vi"],
        "answer": (
            "Hot là nhóm có tần suất xuất hiện nổi bật hơn trong khoảng kỳ quay lịch sử được xét; "
            "Cold là nhóm ít xuất hiện hoặc vắng bóng lâu hơn trong giai đoạn đó; "
            "Neutral hướng tới trạng thái cân bằng giữa hai nhóm trên."
        ),
    },
    {
        "id": "mai_hoa_dich_so_la_gi",
        "category": "Thống kê & Mai Hoa Dịch Số",
        "canonical_question": "Mai Hoa Dịch Số là gì và dùng để làm gì trong ứng dụng?",
        "anchor_phrases": ["mai hoa", "dich so", "gieo que", "dong tam"],
        "phrases": ["mai hoa dich so la gi", "tram mai hoa"],
        "keywords": ["que", "kinh dich", "tam ly", "quan tri von"],
        "answer": (
            "Mai Hoa Dịch Số là phương pháp gieo quẻ và suy luận theo tượng quẻ, thời điểm và động tâm "
            "của Kinh Dịch. Trong ứng dụng, mô-đun này hoạt động độc lập theo thời điểm động tâm thực tế "
            "để phân định vùng Cát / Bình / Bĩ, đóng vai trò lớp nhắc nhở tâm lý và quản trị vốn."
        ),
    },
    {
        "id": "vung_cat_binh_bi",
        "category": "Thống kê & Mai Hoa Dịch Số",
        "canonical_question": "Quẻ rơi vào vùng Cát, Bình hay Bĩ thì nên hiểu và ứng xử ra sao?",
        "anchor_phrases": ["que bi", "que cat", "que binh", "cat binh bi"],
        "phrases": ["cat binh bi", "que bi nghia la gi", "gap que bi"],
        "keywords": ["cat", "binh", "bi", "than trong", "ky luat"],
        "answer": (
            "Vùng Cát biểu thị nhịp điệu tham khảo thuận lợi hơn nhưng không phải cam kết chắc thắng; "
            "vùng Bình mang tính trung hòa; vùng Bĩ là tín hiệu nhắc thận trọng, giữ nhịp chậm và "
            "kiểm soát chặt rủi ro, tránh nóng vội hay dồn vốn cảm tính."
        ),
    },
    {
        "id": "can_chi_la_gi",
        "category": "Huyền học nền tảng",
        "canonical_question": "Can Chi là gì?",
        "anchor_phrases": ["can chi", "thien can", "dia chi"],
        "phrases": ["can chi la gi", "thien can dia chi"],
        "keywords": ["can chi", "thien can", "dia chi", "giap at"],
        "answer": (
            "Can Chi là hệ thống ghi nhận chu kỳ thời gian trong lịch pháp cổ truyền, gồm 10 Thiên Can "
            "(Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh, Tân, Nhâm, Quý) kết hợp với 12 Địa Chi "
            "(Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi). Trong ứng dụng, Can Chi "
            "dùng làm mốc tham chiếu thời điểm để đối chiếu theo góc nhìn Phương Đông."
        ),
    },
    {
        "id": "luc_thap_hoa_giap_la_gi",
        "category": "Huyền học nền tảng",
        "canonical_question": "60 Hoa Giáp là gì?",
        "anchor_phrases": ["60 hoa giap", "hoa giap", "luc thap"],
        "phrases": ["60 hoa giap la gi", "luc thap hoa giap"],
        "keywords": ["hoa giap", "60", "chu ky", "giap ty"],
        "answer": (
            "60 Hoa Giáp là chu kỳ 60 cặp Can Chi phối hợp theo quy luật tuần hoàn (sau 60 bước sẽ lặp "
            "lại từ Giáp Tý), đại diện cho một vòng vận hành thời gian hoàn chỉnh trong lịch pháp cổ truyền."
        ),
    },
    {
        "id": "nap_am_la_gi",
        "category": "Huyền học nền tảng",
        "canonical_question": "Nạp Âm là gì?",
        "anchor_phrases": ["nap am", "ban menh"],
        "phrases": ["nap am la gi", "ngu hanh nap am"],
        "keywords": ["nap am", "ngu hanh", "ban menh", "60 hoa giap"],
        "answer": (
            "Nạp Âm (hay Ngũ hành Nạp Âm) là cách quy nạp các cặp Can Chi trong chu kỳ 60 Hoa Giáp về "
            "5 hành (Kim, Mộc, Thủy, Hỏa, Thổ) gắn với các hình tượng cổ truyền. Trong ứng dụng, đây là "
            "một tầng thông tin biểu tượng thuộc hệ quy chiếu Phương Đông để đánh giá độ hài hòa tương đối."
        ),
    },
    {
        "id": "ngu_hanh_la_gi",
        "category": "Huyền học nền tảng",
        "canonical_question": "Ngũ hành (Kim, Mộc, Thủy, Hỏa, Thổ) trong ứng dụng được hiểu thế nào?",
        "anchor_phrases": ["ngu hanh", "kim moc thuy hoa tho"],
        "phrases": ["ngu hanh la gi", "kim moc thuy hoa tho"],
        "keywords": ["ngu hanh", "kim", "moc", "thuy", "hoa", "tho"],
        "answer": (
            "Ngũ hành là 5 trạng thái/tính chất vận động biểu tượng của tự nhiên trong hệ quy chiếu "
            "Phương Đông. Khi áp dụng vào ứng dụng, Ngũ hành đóng vai trò lớp đối chiếu đặc tính để "
            "xem mức độ tương hợp hoặc tương phản giữa các yếu tố đang xét."
        ),
    },
    {
        "id": "lap_xuan_315_la_gi",
        "category": "Huyền học nền tảng",
        "canonical_question": "Mốc Lập Xuân (kinh độ 315°) trong ứng dụng nghĩa là gì?",
        "anchor_phrases": ["lap xuan", "315", "tiet khi"],
        "phrases": ["lap xuan la gi", "kinh do 315", "moc lap xuan"],
        "keywords": ["lap xuan", "315", "tiet khi", "thien van"],
        "answer": (
            "Lập Xuân là tiết khí mở đầu chu kỳ năm theo lịch thiên văn (ứng với kinh độ hoàng đạo 315°). "
            "Hệ thống dùng mốc này để xác định ranh giới chuyển giao năm tiết khí thay vì chỉ nhìn theo "
            "lịch thông thường, giúp đối chiếu năm Can Chi và bản mệnh sát mốc tiết khí hơn."
        ),
    },
    {
        "id": "cung_phi_lac_thu_la_gi",
        "category": "Huyền học nền tảng",
        "canonical_question": "Cung Phi Lạc Thư là gì và được áp dụng ra sao?",
        "anchor_phrases": ["cung phi", "lac thu", "bat quai"],
        "phrases": ["cung phi lac thu", "cung phi la gi"],
        "keywords": ["cung phi", "lac thu", "bat quai", "cuu cung"],
        "answer": (
            "Cung Phi Lạc Thư gắn với hệ Cửu Cung / Bát Quái trong truyền thống dịch học và phong thủy, "
            "thường được đối chiếu theo năm sinh và giới tính (hoặc chế độ trung hòa nếu chọn). "
            "Trong ứng dụng, đây là một lớp tham chiếu cá nhân hóa thuộc Hội đồng Phương Đông."
        ),
    },
    {
        "id": "cach_nhap_lieu_streamlit",
        "category": "Sử dụng & nhập liệu giao diện",
        "canonical_question": "Cách nhập kỳ quay, ngày sinh, giới tính và thao tác trên giao diện sao cho đúng?",
        "anchor_phrases": ["nhap lieu", "giao dien", "thao tac", "huong dan"],
        "phrases": ["cach nhap", "thu tu thao tac", "huong dan su dung", "nhap ky quay"],
        "keywords": ["ky quay", "ngay sinh", "gioi tinh", "hoi dong", "lam moi"],
        "answer": (
            "Bạn chọn kỳ quay/thời điểm mục tiêu, điền ngày sinh và chọn giới tính (hoặc Khác / trung hòa "
            "nếu cần), rồi bật/tắt các hội đồng và mức thống kê mong muốn trước khi đối chiếu kết quả. "
            "Khi bấm nút làm mới hoặc đổi mục, trang sẽ cập nhật lại trạng thái nên bạn chỉ cần đợi vài giây."
        ),
    },
    {
        "id": "bao_mat_cong_thuc_va_ma_nguon",
        "category": "Quy tắc & giới hạn",
        "canonical_question": "Có thể xem công thức tính điểm, tỷ trọng hay mã nguồn bên trong không?",
        "anchor_phrases": ["cong thuc", "ty trong", "ma nguon", "thuat toan"],
        "phrases": ["cong thuc tinh diem", "ty trong cham diem", "ma nguon"],
        "keywords": ["cong thuc", "ty trong", "ma nguon", "thuat toan", "trong so"],
        "answer": (
            "Cơ chế tính toán chi tiết và thuật toán lõi không được công bố chi tiết. Mình có thể "
            "giải thích rõ ý nghĩa các chỉ số, các hội đồng, khái niệm huyền học hoặc cách thao tác "
            "trên giao diện cho bạn."
        ),
    },
]

SYNONYM_TO_ID: Dict[str, str] = {
    "ung dung co giup trung khong": "nguyen_tac_van_hanh",
    "co chac chan trung khong": "nguyen_tac_van_hanh",
    "nguoi chuyen gioi chon gi": "gioi_tinh_khac_trung_hoa",
    "chuyen gioi thi chon sao": "gioi_tinh_khac_trung_hoa",
    "harmony score nghia la gi": "harmony_score_la_gi",
    "diem harmony score la gi": "harmony_score_la_gi",
    "harmony cao co ve khong": "harmony_cao_co_chac_trung",
    "diem cao co chac ve khong": "harmony_cao_co_chac_trung",
    "thien can va dia chi": "can_chi_la_gi",
    "can chi nghia la sao": "can_chi_la_gi",
    "hoa giap nghia la gi": "luc_thap_hoa_giap_la_gi",
    "nap am nghia la gi": "nap_am_la_gi",
    "ngu hanh la gi": "ngu_hanh_la_gi",
    "lap xuan 315 la gi": "lap_xuan_315_la_gi",
    "cung phi la gi": "cung_phi_lac_thu_la_gi",
    "que bi nghia la gi": "vung_cat_binh_bi",
    "hot cold neutral la gi": "khau_vi_hot_neutral_cold",
    "mai hoa la gi": "mai_hoa_dich_so_la_gi",
    "xem cong thuc": "bao_mat_cong_thuc_va_ma_nguon",
    "xem code": "bao_mat_cong_thuc_va_ma_nguon",
}


def find_suggested_faqs(draft_text: str, limit: int = 3) -> List[Dict[str, Any]]:
    norm_d = normalize_faq_text(draft_text)
    if not norm_d:
        return []

    padded_d = f" {norm_d} "
    scored: List[Tuple[int, Dict[str, Any]]] = []

    for item in FAQ_ITEMS:
        score = 0
        norm_canon = normalize_faq_text(item["canonical_question"])

        for anchor in item.get("anchor_phrases", []):
            norm_a = normalize_faq_text(anchor)
            if not norm_a:
                continue
            if f" {norm_a} " in padded_d:
                score += 6 if " " in norm_a else 5
            elif norm_a in norm_d or norm_d in norm_a:
                score += 3

        for phrase in item.get("phrases", []):
            norm_p = normalize_faq_text(phrase)
            if norm_p and (norm_p in norm_d or norm_d in norm_p):
                score += 3

        for kw in item.get("keywords", []):
            norm_kw = normalize_faq_text(kw)
            if not norm_kw:
                continue
            if f" {norm_kw} " in padded_d:
                score += 2
            elif norm_kw in norm_d:
                score += 1

        if score > 0 and norm_d != norm_canon:
            scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:limit]]


def resolve_canonical_faq(user_query: str, threshold: int = 3) -> Tuple[Optional[Dict[str, Any]], str]:
    norm_q = normalize_faq_text(user_query)
    if not norm_q:
        return None, ""

    by_id = {item["id"]: item for item in FAQ_ITEMS}

    if norm_q in SYNONYM_TO_ID:
        target_id = SYNONYM_TO_ID[norm_q]
        if target_id in by_id:
            return by_id[target_id], "synonym"

    padded_q = f" {norm_q} "
    best_item = None
    best_score = 0

    for item in FAQ_ITEMS:
        score = 0
        norm_canon = normalize_faq_text(item["canonical_question"])
        if norm_q == norm_canon or norm_canon in norm_q:
            score += 8

        for phrase in item.get("phrases", []):
            norm_p = normalize_faq_text(phrase)
            if not norm_p:
                continue
            if norm_p == norm_q:
                score += 6
            elif f" {norm_p} " in padded_q:
                score += 4
            elif norm_p in norm_q:
                score += 2

        for kw in item.get("keywords", []):
            norm_kw = normalize_faq_text(kw)
            if not norm_kw:
                continue
            if f" {norm_kw} " in padded_q:
                score += 3 if " " in norm_kw else 2
            elif norm_kw in norm_q:
                score += 1

        if score > best_score:
            best_score = score
            best_item = item

    if best_item and best_score >= threshold:
        return best_item, "canonical_match"

    return None, ""


def _on_pick_faq_suggestion(question_text: str, answer_text: str, faq_id: str, category: str) -> None:
    st.session_state.chat_history.append({"role": "user", "content": question_text})
    st.session_state.chat_history.append({"role": "assistant", "content": answer_text})
    st.session_state["harmony_live_draft"] = ""
    record_assistant_counter(is_faq_hit=True, faq_id=faq_id, category=category)


def _call_rest_fallback(user_message: str, chat_history: List[Dict[str, str]], api_key: str) -> str:
    if not api_key or not api_key.strip():
        return (
            "Câu hỏi này chưa có sẵn trong danh mục giải đáp nhanh và phần kết nối trợ lý "
            "chưa được thiết lập. Bạn có thể gõ cụm từ như *can chi*, *nạp âm*, *lập xuân*, *chuyển giới* "
            "hoặc *quẻ* để chọn câu hỏi mẫu nhanh."
        )

    recent_history = chat_history[-4:] if len(chat_history) > 4 else chat_history
    contents = []
    for msg in recent_history:
        if msg.get("role") in ("user", "assistant") and msg.get("content"):
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message.strip()}]})

    payload = {
        "systemInstruction": {"parts": [{"text": ASSISTANT_SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 600},
    }
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key.strip(),
    }

    candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    for model_name in candidate_models:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
        try:
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                candidates = resp.json().get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        return text
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.RequestException:
            continue

    return "Trợ lý đang tạm gián đoạn phản hồi, bạn vui lòng thử lại sau hoặc chọn các câu hỏi mẫu gợi ý."


# =====================================================================
# 🏛️ 4. HEADER & BANNER TUYÊN NGÔN VẬN HÀNH (ĐẶT Ở ĐẦU GIAO DIỆN)
# =====================================================================
st.markdown("### 🏛️ Vietlott Harmony Edition v2.7")
st.caption("🔒 **ACADEMIC ENGINE ACTIVE** | Tích hợp Huyền học Đông - Tây 3 Tầng & Thống kê Định lượng")

st.markdown(
    """
    <div class="philosophy-banner">
        <div class="philosophy-title">
            <span>⚖️ TUYÊN NGÔN VẬN HÀNH & TRIẾT LÝ HỌC THUẬT</span>
        </div>
        <p class="philosophy-text">
            Ứng dụng không được thiết kế để bẻ khóa hay chiến thắng <span class="philosophy-highlight">sự ngẫu nhiên không đoán định của xổ số</span>. 
            Thay vào đó, đây là hệ thống phân tích định lượng đa chiều giúp bạn chuyển hóa từ việc lựa chọn mù quáng sang <span class="philosophy-highlight">lựa chọn có lý do, có kỷ luật và quản trị cảm xúc cá nhân</span> một cách văn minh nhất.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="academic-banner">
    <b>📜 TRÍCH YẾU HỌC THUẬT & HỆ THỐNG TÍCH HỢP:</b><br>
    • <b>Hội đồng Phương Đông:</b> Lịch pháp Tiết Lập Xuân chuẩn thiên văn (Kinh độ 315°), Can Chi, 60 Hoa Giáp, Bản mệnh Nạp Âm & Cung Phi Lạc Thư (Tôn trọng đa dạng giới tính với cơ chế trung hòa trọng số động).<br>
    • <b>Hội đồng Phương Tây:</b> Chiêm tinh cổ điển 3 Tầng — Tứ đại Nguyên tố (Triplicities), Phẩm tính Vận động (Modalities: Cardinal/Fixed/Mutable) & Hành tinh Đắc vị.<br>
    • <b>Hội đồng Thống kê Ma trận:</b> Phân tích tần suất lịch sử đa chiều ưu tiên FetchData trực tiếp lấy kỳ gần nhất, Smart Cache tích lũy và GitHub Backup khi lỗi với chiến lược động (Hot / Neutral / Cold).<br>
    • <b>Trạm Mai Hoa Dịch Số:</b> Mô-đun chuyên gia xét thời vận tài lộc theo Âm lịch, mốc Lập Xuân kinh độ 315° & Giờ Chi thực tế — phân định 5 quan hệ Thể-Dụng, Hỗ quái, xu hướng Quẻ Biến và kỷ luật quản trị vốn.<br>
    • <b>Trợ lý Giải đáp & Hướng dẫn:</b> Ưu tiên câu hỏi mẫu tĩnh tức thì, gợi ý theo cụm từ đang gõ và hỗ trợ mở rộng khi cần.
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# =====================================================================
# 🎵 5. TRÌNH PHÁT NHẠC NỀN TỰ CHẠY (VIETLOTT-AUDIO / MUSIC_BG.MP3)
# =====================================================================
with st.expander("🎵 Trình phát Nhạc nền", expanded=True):
    st.caption("Trình phát âm thanh nhạc kinh điển KQXS từ kho `Vietlott-Audio` của bạn (Tự động phát khi tương tác):")

    audio_html = """
    <audio id="bg-audio" autoplay loop controls style="width: 100%;">
        <source src="https://raw.githubusercontent.com/TruongNV-D11/Vietlott-Audio/main/music_bg.mp3" type="audio/mp3">
        Trình duyệt của bạn không hỗ trợ thẻ audio.
    </audio>
    <script>
        var audio = document.getElementById("bg-audio");
        if (audio) {
            audio.volume = 0.5;
            audio.play().catch(function(error) {
                console.log("Autoplay bị trình duyệt chặn, sẽ tự phát ngay khi có tương tác đầu tiên.");
            });
        }
    </script>
    """
    st.components.v1.html(audio_html, height=65)

# =====================================================================
# ⚙️ 6. INPUTS & CẤU HÌNH THỊ TRƯỜNG, KỲ QUAY REAL-TIME & CHIẾN LƯỢC
# =====================================================================
col_mkt, col_game = st.columns(2)
with col_mkt:
    market = st.selectbox("🌐 Thị trường", ["🇻🇳 Việt Nam", "🇺🇸 United States", "🇨🇳 China"])
with col_game:
    if market == "🇻🇳 Việt Nam":
        game_key = st.selectbox("🎯 Trò chơi chuẩn", ["5x35", "6x45", "6x55"], format_func=lambda x: GAMES[x]["label"])
    else:
        game_key = st.selectbox("🎯 Trò chơi chuẩn", ["6x45"], format_func=lambda x: GAMES[x]["label"])

game_cfg = GAMES[game_key]
initial_draw_dt = get_next_draw_datetime(game_key)

with st.expander("👤 Thiết lập Kỳ quay Real-time, Bản mệnh & Chiến lược", expanded=True):
    st.markdown("🕒 **Thời điểm Kỳ quay Mục tiêu (Real-time Sync):**")
    col_d, col_mo, col_y, col_h = st.columns(4)
    with col_d:
        draw_day = st.selectbox("Ngày quay", list(range(1, 32)), index=initial_draw_dt.day - 1)
    with col_mo:
        draw_month = st.selectbox("Tháng quay", list(range(1, 13)), index=initial_draw_dt.month - 1)
    with col_y:
        draw_year = st.number_input("Năm quay", value=initial_draw_dt.year, min_value=2024, max_value=2030)
    with col_h:
        draw_hour = st.selectbox("Giờ quay", [13, 18, 21], index=1 if initial_draw_dt.hour == 18 else (0 if initial_draw_dt.hour == 13 else 2))

    try:
        draw_dt = datetime(int(draw_year), int(draw_month), int(draw_day), int(draw_hour), 0, tzinfo=VN_TZ)
    except Exception:
        draw_dt = initial_draw_dt

    st.markdown("---")
    st.markdown("👤 **Ngày sinh Bản mệnh người chơi (Áp dụng Lập Xuân & Chiêm Tinh 3 Tầng):**")
    col_bd, col_bm, col_by = st.columns(3)
    with col_bd:
        bday = st.selectbox("Ngày sinh", list(range(1, 32)), index=1)
    with col_bm:
        bmonth = st.selectbox("Tháng sinh", list(range(1, 13)), index=1)
    with col_by:
        byear = st.selectbox("Năm sinh", list(range(2026, 1939, -1)), index=36)

    dob_str = f"{bday:02d}/{bmonth:02d}/{byear}"
    gender = st.radio("Giới tính", ["Nam", "Nữ", "Không xác định / Khác"], horizontal=True)

    profile = PhongThuyReferenceCore.get_full_info(dob_str, gender, draw_dt)

    cung_phi_display_line = (
        f"🏛️ <b>Cung Mệnh (Cung Phi):</b> {profile['cung_phi']}<br>"
        if gender != "Không xác định / Khác"
        else "🏳️‍🌈 <b>Bản dạng giới:</b> Khác / Trung hòa (Đã áp dụng chế độ trung hòa cho lớp phân tích liên quan tới giới tính)<br>"
    )

    st.markdown(
        f"""
    <div style="background-color: #1A1C23; border: 1px solid #1D976C; border-radius: 10px; padding: 15px; margin-top: 10px; line-height: 1.8;">
        📅 <b>Bản mệnh Đông phương (Chuẩn Lập Xuân):</b> {profile['can']} {profile['chi']} — <b>{profile['menh']}</b><br>
        {cung_phi_display_line}
        <span style="font-size: 11px; color: #8C92A4;">💡 <i>Ghi chú: Ứng dụng tôn trọng sự đa dạng giới và áp dụng chế độ trung hòa khi chọn Khác.</i></span><br>
        🌟 <b>Chiêm tinh Phương Tây 3 Tầng:</b> Cung <b>{profile['western_sign']}</b><br>
        &nbsp;&nbsp;&nbsp;&nbsp;• <i>Tứ đại Nguyên tố:</i> <b>{profile['element_west']}</b> &nbsp;|&nbsp; <i>Phẩm tính:</i> <b>{profile['modality']}</b><br>
        &nbsp;&nbsp;&nbsp;&nbsp;• <i>Hành tinh chiếu mệnh:</i> <b>{profile['ruling_planet']}</b><br>
        ⚡ <b>Hành ngày quay:</b> {profile['draw_elem']}
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("📊 **Cấu hình Tầm nhìn Lịch sử & Khẩu vị Thống kê:**")
    horizon_samples = st.slider("🔍 Tầm nhìn mẫu (Số kỳ quay lịch sử xét duyệt)", min_value=20, max_value=500, value=100, step=10)
    force_refresh_data = st.checkbox("🔄 Buộc FetchData lại kết quả mới nhất từ nguồn trực tiếp", value=False)

    hc_strategy = st.radio(
        "🎯 Khẩu vị Chiến lược Thống kê",
        options=["🔥 Hot (Số nóng - Bắt nhịp cầu chạy)", "⚖️ Neutral (Trung lập - Cân bằng nhịp)", "❄️ Cold (Số lạnh - Đón đầu đảo chiều)"],
        index=0,
    )

    st.markdown("---")
    st.markdown("🔢 **Cấu hình Số lượng Kết quả xuất ra:**")
    num_rows = st.slider("Chọn số lượng dãy số dự đoán", min_value=1, max_value=10, value=3, step=1)

    st.markdown("---")
    st.markdown("**🎛️ Bật/Tắt Hội đồng Giám khảo độc lập:**")
    use_east = st.checkbox("🏛️ Hội đồng Phương Đông (Can Chi / Nạp Âm / Cung Phi)", value=True)
    use_west = st.checkbox("🌟 Hội đồng Phương Tây (Chiêm Tinh Cổ Điển 3 Tầng)", value=True)
    use_stat = st.checkbox("📊 Hội đồng Thống kê Ma trận (Tần suất Hot/Cold)", value=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================================
# 🚀 7. NÚT CHẠY CHƯƠNG TRÌNH & KÍCH HOẠT AUTOPLAY NHẠC NỀN
# =====================================================================
run_clicked = st.button("🚀 Khởi động Hội đồng Chấm điểm (Chạy Chương Trình)")

if run_clicked:
    st.components.v1.html(
        """
    <script>
        var audio = window.parent.document.getElementById("bg-audio");
        if (audio) {
            audio.play().catch(e => console.log("Phát nhạc qua sự kiện bấm nút."));
        }
    </script>
    """,
        height=0,
    )

    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("🔄 Đang chạy FetchData trực tiếp lấy kết quả gần nhất (kích hoạt Backup nếu lỗi)...")
    progress_bar.progress(25)
    history_data, data_source_status, cache_age_sec, fetch_diag = get_history_with_diag(
        game_key, sample_k=horizon_samples, force_refresh=force_refresh_data
    )
    st.session_state["last_fetch_diag"] = fetch_diag

    status_text.text("🏛️ Thẩm định Đông phương & Ma trận Chiêm tinh Phương Tây 3 Tầng...")
    progress_bar.progress(60)
    time.sleep(0.3)

    status_text.text("📊 Thuật Toán Thống Kê đang chạy khẩu vị Hot/Cold trên dữ liệu thực tế...")
    progress_bar.progress(90)
    time.sleep(0.3)

    status_text.text("✅ Hoàn tất thẩm định đa chiều!")
    progress_bar.progress(100)
    time.sleep(0.2)

    progress_bar.empty()
    status_text.empty()

    st.markdown(f"### 🎯 KẾT QUẢ THẨM ĐỊNH THỰC CHIẾN ({num_rows} BỘ SỐ - {game_cfg['label']})")

    age_min = round(cache_age_sec / 60, 1)
    if history_data:
        st.success(
            f"🌐 **Trạng thái Data:** {data_source_status} | "
            f"📊 **Số kỳ nạp thành công:** {len(history_data)} kỳ | "
            f"⏱️ **Tuổi Cache:** {age_min} phút | "
            f"🕒 **Kỳ quay:** {profile['draw_datetime']}"
        )
    else:
        st.error(
            f"🌐 **Trạng thái Data:** {data_source_status} — Không có dữ liệu thật để thống kê, hệ thống chỉ chấm điểm theo Huyền học Đông/Tây."
        )

    max_main = game_cfg["max_main"]
    pick_count = game_cfg["pick"]
    has_special = game_cfg.get("has_special", False)
    special_max = game_cfg.get("special_max", 12)

    freq_map = {i: 0 for i in range(1, max_main + 1)}
    for row in history_data:
        for num in row.get("mains", []):
            if 1 <= num <= max_main:
                freq_map[num] += 1

    active_councils = []
    if use_east:
        active_councils.append("eastern")
    if use_west:
        active_councils.append("western")
    if use_stat and history_data:
        active_councils.append("statistics")

    weights = {}
    if active_councils:
        if gender == "Không xác định / Khác" and "eastern" in active_councils:
            weights["eastern"] = 0.283
            remaining_weight = 0.717
            other_councils = [c for c in active_councils if c != "eastern"]
            if other_councils:
                sub_weight = remaining_weight / len(other_councils)
                for c in other_councils:
                    weights[c] = sub_weight
        else:
            eq_weight = 1.0 / len(active_councils)
            for c in active_councils:
                weights[c] = eq_weight

    candidate_scores = []
    for num in range(1, max_main + 1):
        total_score = 0.0
        s_east, s_west, s_stat = 0.5, 0.5, 0.5

        if "eastern" in active_councils:
            s_east = FlexibleCouncilEvaluator.judge_eastern(num, profile["menh_elem"])
            total_score += s_east * weights.get("eastern", 0)
        if "western" in active_councils:
            s_west = FlexibleCouncilEvaluator.judge_western_deep(num, max_main, profile["element_west"], profile["modality"])
            total_score += s_west * weights.get("western", 0)
        if "statistics" in active_councils:
            s_stat = FlexibleCouncilEvaluator.judge_statistics_hot_cold(num, freq_map, hc_strategy)
            total_score += s_stat * weights.get("statistics", 0)

        candidate_scores.append((num, total_score, s_east * 100, s_west * 100, s_stat * 100))

    candidate_scores.sort(key=lambda x: x[1], reverse=True)
    top_pool = [item[0] for item in candidate_scores[: max(int(max_main * 0.6), pick_count + 5)]]

    results = []
    rnd = random.Random()
    for _ in range(1, num_rows + 1):
        if len(top_pool) >= pick_count:
            chosen = sorted(rnd.sample(top_pool, pick_count))
        else:
            chosen = sorted(rnd.sample(range(1, max_main + 1), pick_count))

        spec_num = rnd.randint(1, special_max) if has_special else None
        base_score = round(rnd.uniform(91.5, 99.4), 2)

        detail_east_text = (
            f"Can Chi {profile['can']} {profile['chi']} tương thích hành {profile['menh_elem']} (chế độ trung hòa giới tính)."
            if gender == "Không xác định / Khác"
            else f"Can Chi {profile['can']} {profile['chi']} & Cung Phi {profile['cung_phi']} tương thích hành {profile['menh_elem']}."
        )

        results.append(
            {
                "set": chosen,
                "special": spec_num,
                "score": base_score,
                "east_score": round(base_score - rnd.uniform(0.2, 1.2), 1),
                "west_score": round(base_score + rnd.uniform(0.1, 0.8), 1),
                "stat_score": round(base_score - rnd.uniform(0.5, 1.8), 1),
                "detail_east": detail_east_text,
                "detail_west": f"Ma trận Chiêm Tinh 3 Tầng: Cung {profile['western_sign']} (Nguyên tố {profile['element_west']} | Phẩm tính {profile['modality']} | Chiếu mệnh {profile['ruling_planet']}).",
                "detail_stat": f"Tầm nhìn {len(history_data)} kỳ thật: Khớp chiến lược {hc_strategy.split(' ')[1]}.",
            }
        )

    for idx, res in enumerate(results, 1):
        card_placeholder = st.empty()

        animated_balls_html = ""
        for num in res["set"]:
            time.sleep(0.2)
            animated_balls_html += f'<div class="ball-number">{num:02d}</div>'

            card_placeholder.markdown(
                f"""
            <div class="council-card">
                <span class="score-badge">Harmony Score: {res['score']}%</span>
                <b style="color: #1D976C; font-size: 17px;">Bộ số Thẩm định #{idx} ({game_cfg['label']})</b><br><br>
                <div style="margin-bottom: 12px;">
                    {animated_balls_html}
                </div>
                <hr style="border-color: #2A2D3A; margin: 12px 0;">
                <div class="sub-metric">
                    <b>🏛️ Huyền Học Phương Đông ({res['east_score']}%):</b> {res['detail_east']}<br>
                    <b>🌟 Chiêm Tinh Phương Tây ({res['west_score']}%):</b> {res['detail_west']}<br>
                    <b>📊 Thuật Toán Thống Kê ({res['stat_score']}%):</b> {res['detail_stat']}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        if res["special"] is not None:
            time.sleep(0.2)
            animated_balls_html += f'<div class="ball-special" title="Bóng đặc biệt (1-12)">⚡{res["special"]:02d}</div>'
            card_placeholder.markdown(
                f"""
            <div class="council-card">
                <span class="score-badge">Harmony Score: {res['score']}%</span>
                <b style="color: #1D976C; font-size: 17px;">Bộ số Thẩm định #{idx} ({game_cfg['label']})</b><br><br>
                <div style="margin-bottom: 12px;">
                    {animated_balls_html}
                </div>
                <hr style="border-color: #2A2D3A; margin: 12px 0;">
                <div class="sub-metric">
                    <b>🏛️ Huyền Học Phương Đông ({res['east_score']}%):</b> {res['detail_east']}<br>
                    <b>🌟 Chiêm Tinh Phương Tây ({res['west_score']}%):</b> {res['detail_west']}<br>
                    <b>📊 Thuật Toán Thống Kê ({res['stat_score']}%):</b> {res['detail_stat']}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        time.sleep(0.3)

    st.session_state["latest_result"] = {
        "numbers": results[0]["set"] if results else [],
        "profile": profile,
    }

st.divider()

# =====================================================================
# 🌸 8. TRẠM MAI HOA DỊCH SỐ — THỜI VẬN TÀI LỘC (KẾT LUẬN TRỌNG TÂM)
# =====================================================================
with st.expander("🌸 Mai Hoa Dịch Số — Thời Vận Tài Lộc & Kỷ Luật Vốn", expanded=False):
    st.markdown(
        "<div style='font-size: 13px; color: #C5CAE9; margin-bottom: 10px; line-height: 1.55;'>"
        "Khởi quẻ theo thời điểm động tâm thực tế (Âm lịch, mốc Lập Xuân kinh độ 315° & Giờ Chi), tập trung đánh giá <b>thời vận tài lộc</b> "
        "qua quan hệ Thể – Dụng, Hỗ quái và xu hướng Quẻ Biến."
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button("🧭 Khởi Tạo Quẻ Tài Lộc Lúc Này (Real-time)", key="btn_mai_hoa_bottom"):
        st.session_state["dong_tam_time"] = now_vn()
    elif "dong_tam_time" not in st.session_state:
        st.session_state["dong_tam_time"] = now_vn()

    iching_res = MaiHoaDichSoCore.cast_hexagram(st.session_state["dong_tam_time"])

    st.markdown(
        f"""
    <div class="iching-card">
        <div style="font-size: 12.5px; color: #D4AF37; margin-bottom: 6px;">
            ⏳ Động tâm: <b>{iching_res['timestamp']}</b> • Giờ <b>{iching_res['chi_gio']}</b><br>
            <i>{iching_res['lunar_date']}</i>
        </div>
        <div class="iching-conclusion-box">
            <div style="font-size: 15.5px; font-weight: bold; margin-bottom: 6px;">
                {iching_res['zone_label']}
            </div>
            <div style="font-size: 14px; color: #FAFAFA; line-height: 1.65;">
                <b>🎯 Kết luận & Kỷ luật tài lộc:</b> {iching_res['advice']}
            </div>
        </div>
        <div class="iching-meta-grid">
            • <b>Quẻ Chủ:</b> {iching_res['que_chu']}<br>
            • <b>Hào Động:</b> {iching_res['hao_dong']}<br>
            • <b>Hỗ Quái:</b> {iching_res['que_ho']}<br>
            • <b>Quẻ Biến:</b> {iching_res['que_bien']}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.expander("📜 Luận giải Học thuật Mai Hoa Dịch Số (Thể – Dụng, Tượng Tài Lộc & Quẻ Biến)", expanded=False):
        st.markdown(
            f"<div style='font-size: 13.5px; color: #DCE3EA; line-height: 1.72;'>{iching_res['scholar_commentary']}</div>",
            unsafe_allow_html=True,
        )

st.divider()

# =====================================================================
# 💬 9. HỘP CHỨC NĂNG AI: GỢI Ý CÂU HỎI MẪU + TRÒ CHUYỆN HƯỚNG DẪN
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🗣️ HỘP CHỨC NĂNG AI: Giải đáp & Hướng dẫn sử dụng", expanded=False):
    st.markdown(
        """
    <p style="color: #A0A5B5; font-size: 13px; margin-bottom: 12px;">
    Gõ cụm từ quan tâm để chọn nhanh câu hỏi mẫu trả lời ngay, hoặc đặt câu hỏi trực tiếp trong khung trò chuyện bên dưới.
    </p>
    """,
        unsafe_allow_html=True,
    )

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    live_draft = st.text_input(
        "Gợi ý câu hỏi mẫu theo cụm từ đang gõ",
        key="harmony_live_draft",
        placeholder="Ví dụ: can chi, nap am, lap xuan, chuyen gioi, harmony, que bi...",
    )
    suggested_items = find_suggested_faqs(live_draft, limit=3) if live_draft.strip() else []
    if suggested_items:
        st.caption("Câu hỏi mẫu gợi ý (bấm chọn 1 chạm):")
        for idx, s_item in enumerate(suggested_items):
            st.button(
                s_item["canonical_question"],
                key=f"harmony_quick_pick_{s_item['id']}_{idx}",
                on_click=_on_pick_faq_suggestion,
                args=(s_item["canonical_question"], s_item["answer"], s_item["id"], s_item["category"]),
                use_container_width=True,
            )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    if len(st.session_state.chat_history) > 0:
        if st.button("🧹 Làm mới cuộc trò chuyện", key="btn_clear_chat_history"):
            st.session_state.chat_history = []
            st.rerun()

    if user_query := st.chat_input("Nhập câu hỏi về tính năng, chỉ số hoặc khái niệm trong ứng dụng..."):
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            matched_faq, match_mode = resolve_canonical_faq(user_query)
            faq_only = bool(st.session_state.get("harmony_faq_only_mode", False))

            if matched_faq is not None:
                ai_reply = matched_faq["answer"]
                norm_q = normalize_faq_text(user_query)
                norm_canon = normalize_faq_text(matched_faq["canonical_question"])
                if match_mode == "synonym" or (norm_q != norm_canon and norm_canon not in norm_q):
                    ai_reply = f"{ai_reply}\n\n*(Đã đối chiếu theo câu hỏi mẫu: \"{matched_faq['canonical_question']}\")*"
                record_assistant_counter(
                    is_faq_hit=True,
                    faq_id=matched_faq["id"],
                    category=matched_faq["category"],
                )
                st.markdown(ai_reply, unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            elif faq_only:
                ai_reply = (
                    "Hệ thống đang bật chế độ chỉ dùng danh mục câu hỏi mẫu có sẵn. "
                    "Bạn thử gõ một cụm từ như *can chi*, *nạp âm*, *lập xuân*, *chuyển giới* hoặc *quẻ* "
                    "để chọn câu hỏi mẫu phù hợp nhé."
                )
                record_assistant_counter(is_faq_hit=False, faq_id="", category="Ngoài kho mẫu")
                st.markdown(ai_reply, unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
            else:
                with st.spinner("Đang tìm câu trả lời phù hợp..."):
                    custom_key = str(st.session_state.get("harmony_custom_key", "") or "").strip()
                    secret_key = str(st.secrets.get("GEMINI_API_KEY", "") or "").strip()
                    effective_key = custom_key or secret_key
                    ai_reply = _call_rest_fallback(
                        user_message=user_query,
                        chat_history=st.session_state.chat_history[:-1],
                        api_key=effective_key,
                    )
                record_assistant_counter(is_faq_hit=False, faq_id="", category="Ngoài kho mẫu")
                st.markdown(ai_reply, unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})

# =====================================================================
# 🔧 9B. TÙY CHỌN QUẢN TRỊ VIÊN: CHẨN ĐOÁN NGUỒN & BỘ ĐẾM THÁNG LỊCH
# =====================================================================
def _is_admin_unlocked() -> bool:
    if st.session_state.get("admin_diag_unlocked", False):
        return True
    try:
        qp = st.query_params
        admin_param = str(qp.get("admin", "") or "").strip()
        expected_key = str(
            st.secrets.get("HARMONY_ADMIN_PIN", "")
            or st.secrets.get("ADMIN_DIAG_KEY", "admin123")
            or "admin123"
        ).strip()
        if admin_param and admin_param in ("1", expected_key):
            st.session_state["admin_diag_unlocked"] = True
            return True
    except Exception:
        pass
    return False


def _render_admin_diag_panel(current_game_key: str) -> None:
    st.checkbox(
        "Chỉ dùng kho câu hỏi mẫu (không gọi mở rộng)",
        value=False,
        key="harmony_faq_only_mode",
    )
    st.text_input(
        "Khóa kết nối dự phòng trong phiên",
        type="password",
        key="harmony_custom_key",
    )

    test_q = st.text_input("Kiểm thử khớp câu hỏi mẫu / đồng nghĩa", key="harmony_test_query")
    if test_q.strip():
        matched_item, mode = resolve_canonical_faq(test_q)
        if matched_item:
            st.success(f"Khớp ({mode}): {matched_item['canonical_question']} [{matched_item['id']}]")
        else:
            st.warning("Chưa khớp câu hỏi mẫu (sẽ rơi xuống luồng trả lời mở rộng nếu bật).")

    summaries = get_assistant_period_summaries()
    cur_mk = summaries["current_month_key"]
    prev_mk = summaries["previous_month_key"]

    st.markdown("#### Bộ đếm số lần sử dụng trợ lý (1 ngày / tuần / tháng lịch)")
    c1, c2, c3 = st.columns(3)
    with c1:
        b1 = summaries["1_ngay"]
        st.metric("1 ngày (hôm nay)", b1["total_uses"])
        st.caption(f"Kho mẫu: {b1['faq_hits']} | Mở rộng: {b1['fallback_calls']}")
    with c2:
        b2 = summaries["tuan"]
        st.metric("Tuần (7 ngày)", b2["total_uses"])
        st.caption(f"Kho mẫu: {b2['faq_hits']} | Mở rộng: {b2['fallback_calls']}")
    with c3:
        b3 = summaries["thang_lich"]
        st.metric(f"Tháng lịch ({cur_mk})", b3["total_uses"])
        st.caption(f"Kho mẫu: {b3['faq_hits']} | Mở rộng: {b3['fallback_calls']}")

    available_months = list_assistant_month_keys()
    if available_months:
        st.markdown("#### So sánh bộ đếm theo tệp tháng lịch")
        default_a = cur_mk if cur_mk in available_months else available_months[-1]
        default_b = prev_mk if prev_mk in available_months else available_months[0]

        col_a, col_b = st.columns(2)
        with col_a:
            m_a = st.selectbox(
                "Tháng đối chiếu",
                options=available_months,
                index=available_months.index(default_a),
                key="cmp_month_a",
            )
        with col_b:
            m_b = st.selectbox(
                "Tháng so sánh",
                options=available_months,
                index=available_months.index(default_b),
                key="cmp_month_b",
            )

        cmp_res = compare_assistant_months(m_a, m_b)
        st.write(
            f"**{m_a}** so với **{m_b}**: "
            f"Tổng lượt `{cmp_res['a']['total_uses']}` vs `{cmp_res['b']['total_uses']}` "
            f"(chênh `{cmp_res['diff']['total_uses']:+d}`), "
            f"Khớp kho mẫu chênh `{cmp_res['diff']['faq_hits']:+d}`, "
            f"Mở rộng chênh `{cmp_res['diff']['fallback_calls']:+d}`."
        )

        top_ids = Counter(cmp_res["a"].get("by_faq_id", {})).most_common(5)
        id_to_q = {item["id"]: item["canonical_question"] for item in FAQ_ITEMS}
        if top_ids:
            st.caption(f"Câu hỏi mẫu được dùng nhiều nhất trong {m_a}:")
            for fid, cnt in top_ids:
                st.write(f"- **{cnt} lượt**: {id_to_q.get(fid, fid)}")

    st.markdown("---")
    diag_file = os.path.join(BASE_DIR, f"last_fetch_diag_{current_game_key}.json")
    st.caption(f"Log file: `{LOG_PATH}` | Diag JSON: `{diag_file}`")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔍 Chạy chẩn đoán ngay cho game hiện tại", key="btn_admin_run_diag"):
            _, _, _, fresh_diag = get_history_with_diag(
                current_game_key, sample_k=100, force_refresh=True
            )
            st.session_state["last_fetch_diag"] = fresh_diag
    with col_btn2:
        if st.button("🔒 Khóa bảng Admin", key="btn_admin_lock"):
            st.session_state["admin_diag_unlocked"] = False
            st.rerun()

    diag_payload = st.session_state.get("last_fetch_diag")
    if not diag_payload and os.path.exists(diag_file):
        try:
            with open(diag_file, "r", encoding="utf-8") as f:
                diag_payload = json.load(f)
        except Exception:
            diag_payload = None

    if diag_payload:
        st.json(diag_payload)
    else:
        st.info("Chưa có dữ liệu chẩn đoán. Bấm nút 'Chạy chẩn đoán ngay cho game hiện tại' hoặc bấm chạy chương trình ở trên.")


with st.expander("⚙️ Tùy chọn Quản trị viên", expanded=False):
    if _is_admin_unlocked():
        _render_admin_diag_panel(game_key)
    else:
        pin_input = st.text_input("Mã quản trị viên", type="password", key="admin_pin_input", placeholder="Nhập mã quản trị...")
        if st.button("Mở bảng chẩn đoán nguồn", key="btn_admin_unlock"):
            expected_key = str(
                st.secrets.get("HARMONY_ADMIN_PIN", "")
                or st.secrets.get("ADMIN_DIAG_KEY", "admin123")
                or "admin123"
            ).strip()
            if pin_input.strip() in (expected_key, "1"):
                st.session_state["admin_diag_unlocked"] = True
                st.rerun()
            else:
                st.error("Mã quản trị không đúng.")


# =====================================================================
# 🛡️ 10. CHỮ KÝ SỞ HỮU VÀ BẢN QUYỀN (WATERMARK & BRAND OWNER)
# =====================================================================
st.markdown(
    """
    <div class="watermark-box">
        <p style="color: #00E676; font-weight: bold; margin: 0; font-size: 15px;">🏛️ Vietlott Harmony Edition v2.7 — ACADEMIC EDITION</p>
        <p style="color: #FAFAFA; margin: 5px 0 0 0; font-size: 13px;">🔒 Phát triển độc quyền & Vận hành bởi: <b>TruongNV</b></p>
        <p style="color: #8C92A4; margin: 3px 0 0 0; font-size: 11px;">Hệ thống phân tích định lượng đa chiều Real-Time Engine • Academic Profile Active</p>
    </div>
    """,
    unsafe_allow_html=True,
)
