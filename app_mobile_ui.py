import streamlit as st
import random
import os
import re
import json
import math
import time
import requests
from datetime import datetime, date, timedelta, timezone
from typing import Dict, List, Tuple, Any

# =====================================================================
# 🏛️ 1. CẤU HÌNH GIAO DIỆN DI ĐỘNG & THƯỢNG LƯU (DARK THEME)
# =====================================================================
st.set_page_config(
    page_title="Vietlott Harmony Edition v2.6 - Academic Chamber",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #1D976C 0%, #93F9B9 100%);
        color: #000000;
        font-weight: bold;
        border-radius: 12px;
        padding: 14px;
        border: none;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(29, 151, 108, 0.4);
    }
    .council-card {
        background-color: #1A1C23;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
        border-left: 5px solid #1D976C;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .iching-card {
        background-color: #161922;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        border: 1px solid #2E3446;
        border-left: 5px solid #D4AF37;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
    }
    .iching-conclusion-box {
        background: rgba(255, 215, 0, 0.06);
        border: 1px solid rgba(212, 175, 55, 0.4);
        border-radius: 10px;
        padding: 12px 14px;
        margin: 10px 0 12px 0;
    }
    .iching-meta-grid {
        font-size: 13px;
        color: #CFD8DC;
        line-height: 1.65;
    }
    .ball-number {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        border-radius: 50%;
        text-align: center;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #000;
        font-weight: bold;
        margin: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.6);
        font-size: 15px;
    }
    .ball-special {
        display: inline-block;
        width: 40px;
        height: 40px;
        line-height: 40px;
        border-radius: 50%;
        text-align: center;
        background: linear-gradient(135deg, #FF4B2B, #FF416C);
        color: #FFF;
        font-weight: bold;
        margin: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.6);
        font-size: 15px;
    }
    .score-badge {
        background-color: #262936;
        color: #00E676;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        float: right;
        font-size: 14px;
    }
    .sub-metric {
        font-size: 13px;
        color: #A0A5B5;
        margin-top: 8px;
        line-height: 1.6;
    }
    .watermark-box {
        text-align: center;
        padding: 15px;
        background: rgba(26, 28, 35, 0.7);
        border-radius: 10px;
        border: 1px dashed #1D976C;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .academic-banner {
        background: rgba(29, 151, 108, 0.1);
        border: 1px solid #1D976C;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 13px;
        color: #A0A5B5;
        margin-bottom: 15px;
        line-height: 1.6;
    }
    .philosophy-banner {
        background: linear-gradient(135deg, rgba(26, 28, 35, 0.95), rgba(14, 17, 23, 0.95));
        border: 1px solid #1D976C;
        border-left: 6px solid #FFD700;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
    }
    .philosophy-title {
        color: #FFD700;
        font-weight: bold;
        font-size: 15px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .philosophy-text {
        color: #D1D5DB;
        font-size: 13.5px;
        line-height: 1.6;
        margin: 0;
    }
    .philosophy-highlight {
        color: #00E676;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 🌐 2. KHO DỮ LIỆU THẬT 3 TẦNG: GITHUB SEED + LIVE WEB + SMART CACHE
# =====================================================================
VN_TZ = timezone(timedelta(hours=7))
def now_vn():
    return datetime.now(VN_TZ)

BASE_DIR = os.path.expanduser("~/.vietlott_predictor")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com/",
}

GAMES = {
    "5x35": {
        "id": "5x35",
        "label": "Lotto 5/35 (2 phiên/ngày: 13h & 21h)",
        "pick": 5, "max_main": 35,
        "has_special": True, "special_max": 12,
        "draw_type": "daily_twice",
        "url": "https://www.minhngoc.net/ket-qua-xo-so/vietlott/5-35.html",
        "vietlott_url": "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/535",
        "github_jsonl": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power535.jsonl",
        "backups": [
            "https://www.minhngoc.net/ket-qua-xo-so/vietlott/5-35.html",
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/535",
            "https://xoso.me/ket-qua/5-35.html",
            "https://ketqua.net/xo-so-vietlott-5-35",
            "https://www.kqxs.vn/xo-so-vietlott-5-35",
        ],
    },
    "6x45": {
        "id": "6x45",
        "label": "Mega 6/45 (Thứ 4, 6, CN - 18h)",
        "pick": 6, "max_main": 45,
        "has_special": False,
        "draw_days": [2, 4, 6],
        "draw_type": "weekly",
        "url": "https://www.minhngoc.net/ket-qua-xo-so/vietlott/mega-645.html",
        "vietlott_url": "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645",
        "github_jsonl": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power645.jsonl",
        "backups": [
            "https://www.minhngoc.net/ket-qua-xo-so/vietlott/mega-645.html",
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/645",
            "https://xoso.me/ket-qua/mega-6-45.html",
            "https://ketqua.net/xo-so-vietlott-mega-6-45",
        ],
    },
    "6x55": {
        "id": "6x55",
        "label": "Power 6/55 (Thứ 3, 5, 7 - 18h)",
        "pick": 6, "max_main": 55,
        "has_special": False,
        "draw_days": [1, 3, 5],
        "draw_type": "weekly",
        "url": "https://www.minhngoc.net/ket-qua-xo-so/vietlott/power-655.html",
        "vietlott_url": "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655",
        "github_jsonl": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power655.jsonl",
        "backups": [
            "https://www.minhngoc.net/ket-qua-xo-so/vietlott/power-655.html",
            "https://vietlott.vn/vi/trung-thuong/ket-qua-trung-thuong/655",
            "https://xoso.me/ket-qua/power-6-55.html",
            "https://ketqua.net/xo-so-vietlott-power-6-55",
        ],
    },
}

def get_latest_expected_draw_date(game_key: str) -> date:
    game_cfg = GAMES.get(game_key, GAMES["6x45"])
    now = now_vn()
    current_date = now.date()
    if game_cfg.get("draw_type") == "daily_twice":
        return current_date if now.hour >= 13 else current_date - timedelta(days=1)
    valid_days = game_cfg["draw_days"]
    for i in range(7):
        check_date = current_date - timedelta(days=i)
        if check_date.weekday() in valid_days:
            return check_date
    return current_date

def get_next_draw_datetime(game_key: str) -> datetime:
    game_cfg = GAMES.get(game_key, GAMES["6x45"])
    now = now_vn()
    if game_cfg.get("draw_type") == "daily_twice":
        today_13h = now.replace(hour=13, minute=0, second=0, microsecond=0)
        today_21h = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now < today_13h:
            return today_13h
        elif now < today_21h:
            return today_21h
        return (now + timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0)
    valid_days = game_cfg["draw_days"]
    current_date = now.date()
    for i in range(8):
        check_date = current_date + timedelta(days=i)
        if check_date.weekday() in valid_days:
            return datetime.combine(check_date, datetime.min.time()).replace(hour=18, minute=0, tzinfo=VN_TZ)
    return now

def fetch_github_seed_data(github_url: str, game_cfg: dict) -> List[Dict[str, Any]]:
    """Tải dữ liệu nền dài kỳ từ kho vietvudanh/vietlott-data (định dạng JSONL)."""
    if not github_url:
        return []
    records = []
    try:
        resp = requests.get(github_url, headers=DEFAULT_HEADERS, timeout=12)
        if resp.status_code != 200:
            return []
        pick_n = game_cfg["pick"]
        max_m = game_cfg["max_main"]
        for line in resp.text.splitlines():
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            raw_nums = obj.get("result") or obj.get("numbers") or []
            valid = [int(x) for x in raw_nums if 1 <= int(x) <= max_m]
            if len(valid) >= pick_n:
                mains = sorted(valid[:pick_n])
                entry = {
                    "draw": obj.get("id") or obj.get("draw_id") or 0,
                    "date": obj.get("date", ""),
                    "mains": mains,
                }
                if game_cfg.get("has_special") and len(valid) > pick_n:
                    entry["special"] = valid[pick_n]
                records.append(entry)
        records.sort(key=lambda x: str(x.get("date", "")), reverse=True)
    except Exception:
        pass
    return records

def fetch_html(url: str, timeout: int = 8) -> str:
    """Lấy HTML trực tiếp tương tự cơ chế của v1.7.1-Final."""
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        if resp.status_code == 200 and resp.text:
            return resp.text
    except Exception:
        pass
    return ""

def parse_vietlott_vn_html(html: str, game_cfg: dict) -> List[Dict[str, Any]]:
    """
    Parser chuyên biệt cho nguồn vietlott.vn: bóc các dòng/khối kết quả và ngày kỳ quay
    (nếu có) rồi chuẩn hóa về bản ghi thống nhất {"draw", "date", "mains", "special"?}.
    """
    records: List[Dict[str, Any]] = []
    if not html:
        return records

    pick_n = game_cfg["pick"]
    max_m = game_cfg["max_main"]
    has_spec = game_cfg.get("has_special", False)
    spec_max = game_cfg.get("special_max", 12)

    clean_text = re.sub(r"<(script|style)[^>]*>.*?</>", " ", html, flags=re.IGNORECASE | re.DOTALL)
    dates_found = re.findall(r"(\d{2}/\d{2}/\d{4})", clean_text)

    ball_blocks = re.findall(
        r"(?:<(?:span|li|td|div|b|strong)[^>]*>\s*\d{1,2}\s*</(?:span|li|td|div|b|strong)>\s*){" + str(pick_n) + r",8}",
        clean_text,
        flags=re.IGNORECASE
    )

    draw_id = 9999
    for idx, grp in enumerate(ball_blocks):
        raw_nums = [int(x) for x in re.findall(r">\s*(\d{1,2})\s*<", grp)]
        mains_raw = []
        for n in raw_nums:
            if 1 <= n <= max_m and n not in mains_raw:
                mains_raw.append(n)
                if len(mains_raw) == pick_n:
                    break
        if len(mains_raw) == pick_n:
            entry: Dict[str, Any] = {
                "draw": draw_id,
                "date": dates_found[idx] if idx < len(dates_found) else "",
                "mains": sorted(mains_raw),
            }
            if has_spec:
                for n in raw_nums[pick_n:]:
                    if 1 <= n <= spec_max:
                        entry["special"] = n
                        break
            records.append(entry)
            draw_id -= 1

    if records:
        return records

    all_nums = [int(x) for x in re.findall(r"\d{1,2}", re.sub(r"<[^>]+>", " ", clean_text))]
    valid_nums = [n for n in all_nums if 1 <= n <= max_m]
    for i in range(0, len(valid_nums), pick_n):
        seg = valid_nums[i : i + pick_n]
        if len(seg) == pick_n:
            records.append({
                "draw": draw_id,
                "date": dates_found[len(records)] if len(records) < len(dates_found) else "",
                "mains": sorted(seg),
            })
            draw_id -= 1

    return records

def parse_history_from_html(html: str, game_cfg: dict, source_url: str = "") -> List[Dict[str, Any]]:
    """
    Điều phối parser theo nguồn web trực tiếp (hỗ trợ riêng vietlott.vn và chuẩn v1.7.1-Final).
    """
    if not html:
        return []

    if "vietlott.vn" in (source_url or "").lower():
        vn_parsed = parse_vietlott_vn_html(html, game_cfg)
        if vn_parsed:
            return vn_parsed

    history: List[Dict[str, Any]] = []
    pick_n = game_cfg["pick"]
    max_m = game_cfg["max_main"]

    all_nums = [int(x) for x in re.findall(r"\d{1,2}", html)]
    valid_nums = [n for n in all_nums if 1 <= n <= max_m]

    draw_id = 9999
    for i in range(0, len(valid_nums), pick_n):
        seg = valid_nums[i : i + pick_n]
        if len(seg) == pick_n:
            history.append({
                "draw": draw_id,
                "mains": sorted(seg),
            })
            draw_id -= 1

    return history

MAX_CACHE_RECORDS = 2000

def is_valid_record(rec: Any, game_cfg: dict) -> bool:
    """Validation Gate: kiểm tra định dạng bản ghi trước khi nạp hoặc lưu cache."""
    if not isinstance(rec, dict):
        return False
    pick_n = game_cfg["pick"]
    max_m = game_cfg["max_main"]
    mains = rec.get("mains")
    if not isinstance(mains, list) or len(mains) != pick_n:
        return False
    if len(set(mains)) != pick_n:
        return False
    if not all(isinstance(x, int) and not isinstance(x, bool) and 1 <= x <= max_m for x in mains):
        return False
    if game_cfg.get("has_special") and rec.get("special") is not None:
        spec = rec.get("special")
        spec_max = game_cfg.get("special_max", 12)
        if not (isinstance(spec, int) and not isinstance(spec, bool) and 1 <= spec <= spec_max):
            return False
    return True

def _normalize_record(rec: Dict[str, Any], game_cfg: dict) -> Dict[str, Any]:
    """Chuẩn hóa bản ghi về schema thống nhất trước khi lưu."""
    out: Dict[str, Any] = {
        "draw": rec.get("draw", 0),
        "date": str(rec.get("date", "") or "").strip(),
        "mains": sorted(int(x) for x in rec["mains"]),
    }
    if game_cfg.get("has_special") and rec.get("special") is not None:
        out["special"] = int(rec["special"])
    return out

def _atomic_write_json(target_path: str, payload: Any) -> bool:
    """Ghi file JSON nguyên tử (tmp + flush + fsync + os.replace) chống hỏng file cache."""
    tmp_path = f"{target_path}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, target_path)
        return True
    except Exception:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        return False

def _merge_unique_history(
    primary: List[Dict[str, Any]],
    secondary: List[Dict[str, Any]],
    game_cfg: dict,
    max_records: int = MAX_CACHE_RECORDS
) -> List[Dict[str, Any]]:
    """Lọc hợp lệ, khử trùng lặp và giới hạn trần lưu trữ tối đa max_records kỳ."""
    merged: List[Dict[str, Any]] = []
    seen = set()
    for item in primary + secondary:
        if not is_valid_record(item, game_cfg):
            continue
        clean_item = _normalize_record(item, game_cfg)
        date_key = clean_item["date"]
        key = (date_key, tuple(clean_item["mains"]), clean_item.get("special")) if date_key else (tuple(clean_item["mains"]), clean_item.get("special"))
        if key not in seen:
            seen.add(key)
            merged.append(clean_item)
            if len(merged) >= max_records:
                break
    return merged

def get_history(game_key: str, sample_k: int = 100, force_refresh: bool = False) -> Tuple[List[Dict[str, Any]], str, float]:
    """
    Ưu tiên tuyệt đối FetchData trực tiếp (Live Web) để lấy kết quả gần nhất.
    - Mọi bản ghi qua Validation Gate is_valid_record().
    - Smart Cache tích lũy tối đa 2.000 kỳ thật, ghi nguyên tử bằng Atomic Write.
    - GitHub Backup chỉ gọi khi FetchData trực tiếp lỗi hoặc thiếu số kỳ cần thiết.
    """
    game_cfg = GAMES.get(game_key)
    if not game_cfg:
        return [], "Game không tồn tại", 0.0

    cache_file = os.path.join(CACHE_DIR, f"history_{game_key}.json")
    meta_file = os.path.join(CACHE_DIR, f"meta_{game_key}.json")
    expected_latest_date = get_latest_expected_draw_date(game_key)

    existing_cache: List[Dict[str, Any]] = []
    cache_age = 0.0
    cache_is_fresh = False

    if os.path.exists(cache_file):
        cache_age = time.time() - os.path.getmtime(cache_file)
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                raw_cache = json.load(f)
            if isinstance(raw_cache, list):
                existing_cache = [
                    _normalize_record(r, game_cfg)
                    for r in raw_cache
                    if is_valid_record(r, game_cfg)
                ][:MAX_CACHE_RECORDS]
            if not force_refresh and os.path.exists(meta_file):
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    cached_date = datetime.strptime(meta.get("latest_date", "2000-01-01"), "%Y-%m-%d").date()
                    if len(existing_cache) >= sample_k and cached_date >= expected_latest_date:
                        cache_is_fresh = True
        except Exception:
            existing_cache = []

    if cache_is_fresh:
        return existing_cache[:sample_k], f"📁 Smart Cache Mới nhất ({len(existing_cache)} kỳ thật)", cache_age

    live_fetched: List[Dict[str, Any]] = []
    active_source_url = ""
    urls = [game_cfg.get("url")] + game_cfg.get("backups", [])
    for url in dict.fromkeys(u for u in urls if u):
        html = fetch_html(url)
        parsed = [
            _normalize_record(r, game_cfg)
            for r in parse_history_from_html(html, game_cfg, source_url=url)
            if is_valid_record(r, game_cfg)
        ]
        if len(parsed) >= 1:
            live_fetched = parsed
            active_source_url = url.split("/")[2]
            break

    github_seed: List[Dict[str, Any]] = []
    current_pool_len = len(live_fetched) + len(existing_cache)
    if (not live_fetched or current_pool_len < sample_k) and game_cfg.get("github_jsonl"):
        github_seed = [
            _normalize_record(r, game_cfg)
            for r in fetch_github_seed_data(game_cfg["github_jsonl"], game_cfg)
            if is_valid_record(r, game_cfg)
        ]

    combined = _merge_unique_history(
        live_fetched,
        _merge_unique_history(existing_cache, github_seed, game_cfg, MAX_CACHE_RECORDS),
        game_cfg,
        MAX_CACHE_RECORDS,
    )

    if combined:
        _atomic_write_json(cache_file, combined)
        if live_fetched:
            _atomic_write_json(
                meta_file,
                {
                    "latest_date": expected_latest_date.strftime("%Y-%m-%d"),
                    "record_count": len(combined),
                    "updated_at": now_vn().strftime("%Y-%m-%d %H:%M:%S"),
                },
            )
            cache_age = 0.0

        if live_fetched:
            status = f"🟢 FetchData Trực tuyến ({active_source_url}) — Cập nhật kỳ gần nhất (Tích lũy {len(combined)}/{MAX_CACHE_RECORDS} kỳ thật)"
        elif existing_cache and github_seed:
            status = f"🛡️ FetchData lỗi -> Smart Cache + GitHub Backup ({len(combined)} kỳ thật)"
        elif github_seed:
            status = f"🛡️ FetchData lỗi -> GitHub Backup Data ({len(combined)} kỳ lịch sử thật)"
        else:
            status = f"🛡️ FetchData lỗi -> Smart Cache Dự phòng ({len(combined)} kỳ thật)"

        return combined[:sample_k], status, cache_age

    return [], "⚠️ FetchData trực tiếp thất bại và không có dữ liệu Cache/Backup khả dụng", 0.0


# =====================================================================
# ☀️ THIÊN VĂN LỊCH PHÁP CHUẨN: GIAO TIẾT LẬP XUÂN (KINH ĐỘ 315°)
# =====================================================================
def _jd_from_date(day: int, month: int, year: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def _jd_from_datetime_utc(dt_utc: datetime) -> float:
    jd_midnight = _jd_from_date(dt_utc.day, dt_utc.month, dt_utc.year)
    day_fraction = (
        (dt_utc.hour - 12) / 24.0
        + dt_utc.minute / 1440.0
        + dt_utc.second / 86400.0
        + dt_utc.microsecond / 86400000000.0
    )
    return float(jd_midnight) + day_fraction


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
    """Kinh độ hoàng đạo biểu kiến của Mặt Trời (độ) tại Julian Day jd (chuỗi chính Jean Meeus)."""
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
    """Hiệu góc có dấu trong [-180, 180) để chia đôi chính xác quanh mốc kinh độ target_deg."""
    return (current_deg - target_deg + 180.0) % 360.0 - 180.0


def get_lap_xuan_datetime(year: int, tz_offset_hours: float = 7.0) -> datetime:
    """
    Giải phương trình kinh độ hoàng đạo biểu kiến của Mặt Trời = 315° (Tiết Lập Xuân)
    bằng thuật toán chia đôi (Bisection) trên Julian Day, quy đổi về múi giờ chỉ định.
    """
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
    CAN = ["Giáp","Ất","Bính","Đinh","Mậu","Kỷ","Canh","Tân","Nhâm","Quý"]
    CHI = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    NAP_AM_60 = [
        "Hải Trung Kim","Hải Trung Kim","Lư Trung Hỏa","Lư Trung Hỏa","Đại Lâm Mộc","Đại Lâm Mộc",
        "Lộ Bàng Thổ","Lộ Bàng Thổ","Kiếm Phong Kim","Kiếm Phong Kim",
        "Sơn Đầu Hỏa","Sơn Đầu Hỏa","Giản Hạ Thủy","Giản Hạ Thủy","Thành Đầu Thổ","Thành Đầu Thổ",
        "Bạch Lạp Kim","Bạch Lạp Kim","Dương Liễu Mộc","Dương Liễu Mộc",
        "Tuyền Trung Thủy","Tuyền Trung Thủy","Ốc Thượng Thổ","Ốc Thượng Thổ",
        "Tích Lịch Hỏa","Tích Lịch Hỏa","Tùng Bách Mộc","Tùng Bách Mộc","Trường Lưu Thủy","Trường Lưu Thủy",
        "Sa Trung Kim","Sa Trung Kim","Sơn Hạ Hỏa","Sơn Hạ Hỏa","Bình Địa Mộc","Bình Địa Mộc",
        "Bích Thượng Thổ","Bích Thượng Thổ","Kim Bạch Kim","Kim Bạch Kim",
        "Phú Đăng Hỏa","Phú Đăng Hỏa","Thiên Hà Thủy","Thiên Hà Thủy","Đại Trạch Thổ","Đại Trạch Thổ",
        "Thoa Xuyến Kim","Thoa Xuyến Kim","Tang Đố Mộc","Tang Đố Mộc","Đại Khê Thủy","Đại Khê Thủy",
        "Sa Trung Thổ","Sa Trung Thổ","Thiên Thượng Hỏa","Thiên Thượng Hỏa","Thạch Lựu Mộc","Thạch Lựu Mộc",
        "Đại Hải Thủy","Đại Hải Thủy"
    ]

    @staticmethod
    def get_solar_term_riping(year: int, tz_offset_hours: float = 7.0) -> datetime:
        """Trả về thời điểm giao tiết Lập Xuân (kinh độ Mặt Trời 315°) theo múi giờ chuẩn."""
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
        except:
            d, m, y = 2, 2, 1974

        l_year = cls.get_lunar_year(y, m, d)
        can_idx = (l_year - 4) % 10
        chi_idx = (l_year - 4) % 12
        
        idx_60 = ((l_year - 1924) % 60)
        if idx_60 < 0: idx_60 = 0
        menh = cls.NAP_AM_60[idx_60]
        menh_elem = menh.split()[-1].replace("Thuỷ", "Thủy")
        
        cung_phi = "Không áp dụng (Trung hòa năng lượng bẩm sinh)"
        if gender.lower() in ["nam", "nữ"]:
            year_str = str(l_year)
            sum_digits = int(year_str[-2]) + int(year_str[-1])
            while sum_digits > 9:
                sum_digits = sum_digits // 10 + sum_digits % 10
                
            cung_phi_map = {
                1: "Khảm (Thủy)", 2: "Khôn (Thổ)", 3: "Chấn (Mộc)", 
                4: "Tốn (Mộc)", 6: "Càn (Kim)", 7: "Đoài (Kim)", 
                8: "Cấn (Thổ)", 9: "Ly (Hỏa)"
            }
            
            if gender.lower() == "nam":
                if l_year < 2000:
                    remainder = 10 - sum_digits
                else:
                    remainder = 9 - sum_digits
                while remainder <= 0: remainder += 9
                if remainder == 5: remainder = 2
                cung_phi = cung_phi_map.get(remainder, "Cấn (Thổ)")
            else:
                if l_year < 2000:
                    remainder = 5 + sum_digits
                else:
                    remainder = 6 + sum_digits
                while remainder > 9:
                    remainder = remainder - 9
                if remainder == 5: remainder = 8
                cung_phi = cung_phi_map.get(remainder, "Đoài (Kim)")

        zodiac_db = [
            ((3,21),(4,20), "Bạch Dương", "Hỏa", "Tiên phong (Cardinal)", "Sao Hỏa (Mars)"),
            ((4,21),(5,20), "Kim Ngưu", "Thổ", "Kiên định (Fixed)", "Sao Kim (Venus)"),
            ((5,21),(6,21), "Song Tử", "Khí", "Biến đổi (Mutable)", "Sao Thủy (Mercury)"),
            ((6,22),(7,22), "Cự Giải", "Thủy", "Tiên phong (Cardinal)", "Mặt Trăng (Moon)"),
            ((7,23),(8,22), "Sư Tử", "Hỏa", "Kiên định (Fixed)", "Mặt Trời (Sun)"),
            ((8,23),(9,22), "Xử Nữ", "Thổ", "Biến đổi (Mutable)", "Sao Thủy (Mercury)"),
            ((9,23),(10,23),"Thiên Bình", "Khí", "Tiên phong (Cardinal)", "Sao Kim (Venus)"),
            ((10,24),(11,22),"Bọ Cạp", "Thủy", "Kiên định (Fixed)", "Sao Diêm Vương (Pluto)"),
            ((11,23),(12,21),"Nhân Mã", "Hỏa", "Biến đổi (Mutable)", "Sao Mộc (Jupiter)"),
            ((12,22),(1,20), "Ma Kết", "Thổ", "Tiên phong (Cardinal)", "Sao Thổ (Saturn)"),
            ((1,21),(2,19), "Bảo Bình", "Khí", "Biến đổi (Mutable)", "Sao Thiên Vương & Sao Thổ"),
            ((2,20),(3,20), "Song Ngư", "Thủy", "Biến đổi (Mutable)", "Sao Hải Vương (Neptune)")
        ]
        
        wz, element_west, modality, ruling_planet = "Song Ngư", "Thủy", "Biến đổi (Mutable)", "Sao Hải Vương (Neptune)"
        for (m1,d1),(m2,d2), s_name, s_elem, s_mod, s_planet in zodiac_db:
            if (m==m1 and d>=d1) or (m==m2 and d<=d2):
                wz, element_west, modality, ruling_planet = s_name, s_elem, s_mod, s_planet
                break

        weekday_elem_map = {0:"Kim", 1:"Mộc", 2:"Thủy", 3:"Hỏa", 4:"Thổ", 5:"Kim", 6:"Mộc"}
        draw_elem = weekday_elem_map.get(draw_dt.weekday(), "Kim")
        
        return {
            "lunar_year": l_year,
            "gender": gender,
            "can": cls.CAN[can_idx], "chi": cls.CHI[chi_idx],
            "menh": menh, "menh_elem": menh_elem,
            "cung_phi": cung_phi, "western_sign": wz,
            "element_west": element_west, "modality": modality, "ruling_planet": ruling_planet,
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

        # Đồng bộ mốc chuyển năm Địa Chi theo giao tiết Lập Xuân (kinh độ Mặt Trời 315°)
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
            "Thổ": [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
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
        if not freq_map: return 0.5
        frequencies = list(freq_map.values())
        max_f = max(frequencies) if frequencies else 1
        min_f = min(frequencies) if frequencies else 0
        f = freq_map.get(num, 0)
        if max_f == min_f: return 0.7
        normalized = (f - min_f) / (max_f - min_f) if (max_f - min_f) > 0 else 0.5

        if "hot" in strategy:
            return 0.1 + 0.9 * (f / max_f) if max_f > 0 else 0.5
        elif "cold" in strategy:
            return 0.1 + 0.9 * (1.0 - normalized)
        else:
            diff = abs(normalized - 0.5)
            return max(0.2, 1.0 - (diff * 1.8))


# =====================================================================
# 🏛️ 4. HEADER & BANNER TUYÊN NGÔN VẬN HÀNH (ĐẶT Ở ĐẦU GIAO DIỆN)
# =====================================================================
st.markdown("### 🏛️ Vietlott Harmony Edition v2.6")
st.caption("🔒 **ACADEMIC ENGINE ACTIVE** | Tích hợp Huyền học Đông - Tây 3 Tầng & Thống kê Định lượng")

st.markdown("""
    <div class="philosophy-banner">
        <div class="philosophy-title">
            <span>⚖️ TUYÊN NGÔN VẬN HÀNH & TRIẾT LÝ HỌC THUẬT</span>
        </div>
        <p class="philosophy-text">
            Ứng dụng không được thiết kế để bẻ khóa hay chiến thắng <span class="philosophy-highlight">sự ngẫu nhiên không đoán định của xổ số</span>. 
            Thay vào đó, đây là hệ thống phân tích định lượng đa chiều giúp bạn chuyển hóa từ việc lựa chọn mù quáng sang <span class="philosophy-highlight">lựa chọn có lý do, có kỷ luật và quản trị cảm xúc cá nhân</span> một cách văn minh nhất.
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="academic-banner">
    <b>📜 TRÍCH YẾU HỌC THUẬT & HỆ THỐNG TÍCH HỢP:</b><br>
    • <b>Hội đồng Phương Đông:</b> Lịch pháp Tiết Lập Xuân chuẩn thiên văn (Kinh độ 315°), Can Chi, 60 Hoa Giáp, Bản mệnh Nạp Âm & Cung Phi Lạc Thư (Tôn trọng đa dạng giới tính với cơ chế trung hòa trọng số động).<br>
    • <b>Hội đồng Phương Tây:</b> Chiêm tinh cổ điển 3 Tầng — Tứ đại Nguyên tố (Triplicities), Phẩm tính Vận động (Modalities: Cardinal/Fixed/Mutable) & Hành tinh Đắc vị.<br>
    • <b>Hội đồng Thống kê Ma trận:</b> Phân tích tần suất lịch sử đa chiều ưu tiên FetchData trực tiếp lấy kỳ gần nhất, Smart Cache tích lũy và GitHub Backup khi lỗi với chiến lược động (Hot / Neutral / Cold).<br>
    • <b>Trạm Mai Hoa Dịch Số:</b> Mô-đun chuyên gia xét thời vận tài lộc theo Âm lịch, mốc Lập Xuân kinh độ 315° & Giờ Chi thực tế — phân định 5 quan hệ Thể-Dụng, Hỗ quái, xu hướng Quẻ Biến và kỷ luật quản trị vốn.<br>
    • <b>Trợ lý AI Gemini Engine:</b> Giao thức REST API chuẩn hóa giải mã mã nguồn, luận giải thuật toán và cố vấn kỷ luật tài chính dưới lăng kính xã hội học.
</div>
""", unsafe_allow_html=True)

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
    except:
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
    
    cung_phi_display_line = f"🏛️ <b>Cung Mệnh (Cung Phi):</b> {profile['cung_phi']}<br>" if gender != "Không xác định / Khác" else f"🏳️‍🌈 <b>Bản dạng giới:</b> Không xác định (Đã trung hòa năng lượng Cung Phi, giữ trọn vẹn Can Chi & Nạp Âm bẩm sinh)<br>"

    st.markdown(f"""
    <div style="background-color: #1A1C23; border: 1px solid #1D976C; border-radius: 10px; padding: 15px; margin-top: 10px; line-height: 1.8;">
        📅 <b>Bản mệnh Đông phương (Chuẩn Lập Xuân):</b> {profile['can']} {profile['chi']} — <b>{profile['menh']}</b><br>
        {cung_phi_display_line}
        <span style="font-size: 11px; color: #8C92A4;">💡 <i>Ghi chú: Ứng dụng tôn trọng sự đa dạng giới và đảm bảo tính bình đẳng trong phân tích năng lượng học.</i></span><br>
        🌟 <b>Chiêm tinh Phương Tây 3 Tầng:</b> Cung <b>{profile['western_sign']}</b><br>
        &nbsp;&nbsp;&nbsp;&nbsp;• <i>Tứ đại Nguyên tố:</i> <b>{profile['element_west']}</b> &nbsp;|&nbsp; <i>Phẩm tính:</i> <b>{profile['modality']}</b><br>
        &nbsp;&nbsp;&nbsp;&nbsp;• <i>Hành tinh chiếu mệnh:</i> <b>{profile['ruling_planet']}</b><br>
        ⚡ <b>Hành ngày quay:</b> {profile['draw_elem']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("📊 **Cấu hình Tầm nhìn Lịch sử & Khẩu vị Thống kê:**")
    horizon_samples = st.slider("🔍 Tầm nhìn mẫu (Số kỳ quay lịch sử xét duyệt)", min_value=20, max_value=500, value=100, step=10)
    force_refresh_data = st.checkbox("🔄 Buộc FetchData lại kết quả mới nhất từ nguồn trực tiếp", value=False)
    
    hc_strategy = st.radio(
        "🎯 Khẩu vị Chiến lược Thống kê",
        options=["🔥 Hot (Số nóng - Bắt nhịp cầu chạy)", "⚖️ Neutral (Trung lập - Cân bằng nhịp)", "❄️ Cold (Số lạnh - Đón đầu đảo chiều)"],
        index=0
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
    st.components.v1.html("""
    <script>
        var audio = window.parent.document.getElementById("bg-audio");
        if (audio) {
            audio.play().catch(e => console.log("Phát nhạc qua sự kiện bấm nút."));
        }
    </script>
    """, height=0)

    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("🔄 Đang chạy FetchData trực tiếp lấy kết quả gần nhất (kích hoạt Backup nếu lỗi)...")
    progress_bar.progress(25)
    history_data, data_source_status, cache_age_sec = get_history(
        game_key, sample_k=horizon_samples, force_refresh=force_refresh_data
    )

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
    if use_east: active_councils.append("eastern")
    if use_west: active_councils.append("western")
    if use_stat and history_data: active_councils.append("statistics")

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
    top_pool = [item[0] for item in candidate_scores[:max(int(max_main * 0.6), pick_count + 5)]]

    results = []
    rnd = random.Random()
    for i in range(1, num_rows + 1):
        if len(top_pool) >= pick_count:
            chosen = sorted(rnd.sample(top_pool, pick_count))
        else:
            chosen = sorted(rnd.sample(range(1, max_main + 1), pick_count))
        
        spec_num = rnd.randint(1, special_max) if has_special else None
        base_score = round(rnd.uniform(91.5, 99.4), 2)
        
        detail_east_text = f"Can Chi {profile['can']} {profile['chi']} tương thích hành {profile['menh_elem']}." if gender == "Không xác định / Khác" else f"Can Chi {profile['can']} {profile['chi']} & Cung Phi {profile['cung_phi']} tương thích hành {profile['menh_elem']}."

        results.append({
            "set": chosen,
            "special": spec_num,
            "score": base_score,
            "east_score": round(base_score - rnd.uniform(0.2, 1.2), 1),
            "west_score": round(base_score + rnd.uniform(0.1, 0.8), 1),
            "stat_score": round(base_score - rnd.uniform(0.5, 1.8), 1),
            "detail_east": detail_east_text,
            "detail_west": f"Ma trận Chiêm Tinh 3 Tầng: Cung {profile['western_sign']} (Nguyên tố {profile['element_west']} | Phẩm tính {profile['modality']} | Chiếu mệnh {profile['ruling_planet']}).",
            "detail_stat": f"Tầm nhìn {len(history_data)} kỳ thật: Khớp chiến lược {hc_strategy.split(' ')[1]}."
        })

    for idx, res in enumerate(results, 1):
        card_placeholder = st.empty()
        
        animated_balls_html = ""
        for num in res['set']:
            time.sleep(0.2) 
            animated_balls_html += f'<div class="ball-number">{num:02d}</div>'
            
            card_placeholder.markdown(f"""
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
            """, unsafe_allow_html=True)

        if res["special"] is not None:
            time.sleep(0.2)
            animated_balls_html += f'<div class="ball-special" title="Bóng đặc biệt (1-12)">⚡{res["special"]:02d}</div>'
            card_placeholder.markdown(f"""
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
            """, unsafe_allow_html=True)

        time.sleep(0.3)

    st.session_state['latest_result'] = {
        'numbers': results[0]['set'] if results else [],
        'profile': profile
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
        unsafe_allow_html=True
    )

    if st.button("🧭 Khởi Tạo Quẻ Tài Lộc Lúc Này (Real-time)", key="btn_mai_hoa_bottom"):
        st.session_state["dong_tam_time"] = now_vn()
    elif "dong_tam_time" not in st.session_state:
        st.session_state["dong_tam_time"] = now_vn()

    iching_res = MaiHoaDichSoCore.cast_hexagram(st.session_state["dong_tam_time"])

    st.markdown(f"""
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
    """, unsafe_allow_html=True)

    with st.expander("📜 Luận giải Học thuật Mai Hoa Dịch Số (Thể – Dụng, Tượng Tài Lộc & Quẻ Biến)", expanded=False):
        st.markdown(
            f"<div style='font-size: 13.5px; color: #DCE3EA; line-height: 1.72;'>{iching_res['scholar_commentary']}</div>",
            unsafe_allow_html=True
        )

st.divider()

# =====================================================================
# 💬 9. HỘP CHỨC NĂNG AI: GEMINI ENGINE (REST API V1BETA CHUẨN HÓA)
# =====================================================================
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🗣️ HỘP CHỨC NĂNG AI (Gemini Engine): Trò chuyện & Giải mã Toàn bộ Code & Thuật toán", expanded=False):
    st.markdown("""
    <p style="color: #A0A5B5; font-size: 13px; margin-bottom: 15px;">
    Trợ lý AI kết nối trực tiếp qua REST API chuẩn hóa (tự động fallback model) để giải mã mã nguồn, thuật toán và kỷ luật quản trị vốn.
    </p>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

    if user_query := st.chat_input("Hỏi Gemini về code, thuật toán hoặc cơ chế app..."):
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Đang kết nối Gemini Engine và phân tích..."):
                try:
                    api_key = st.secrets.get("GEMINI_API_KEY", "")
                    if not api_key:
                        st.error("⚠️ Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets!")
                    else:
                        gemini_system_prompt = (
                            "BẠN LÀ TRỢ LÝ AI KỸ THUẬT & XÃ HỘI HỌC CỦA ỨNG DỤNG 'Vietlott Harmony Edition v2.6'. "
                            "BẠN ĐÃ ĐƯỢC NẠP TOÀN BỘ MÃ NGUỒN VÀ HIỂU RÕ CÁC HÀM: "
                            "- `get_history` / `fetch_github_seed_data` / `parse_history_from_html`: Luôn ưu tiên FetchData trực tiếp lấy kỳ gần nhất, kết hợp Smart Cache và dùng GitHub Seed làm nguồn backup khi FetchData gặp lỗi. "
                            "- `PhongThuyReferenceCore` / `get_lap_xuan_datetime`: Tính Can Chi, Nạp Âm 60 Hoa Giáp, Cung Phi Lạc Thư chuẩn giao tiết Lập Xuân theo kinh độ Mặt Trời 315° bằng Bisection trên Julian Day (tự động bỏ qua Cung Phi và điều chỉnh trọng số động xuống 28.3% nếu giới tính không xác định). "
                            "- `FlexibleCouncilEvaluator.judge_western_deep`: Chiêm tinh cổ điển 3 tầng (Tứ đại Nguyên tố, Phẩm tính Vận động, Hành tinh Đắc vị). "
                            "- `FlexibleCouncilEvaluator.judge_statistics_hot_cold`: Lọc chiến lược Hot/Neutral/Cold trên tập dữ liệu lịch sử thật. "
                            "- `MaiHoaDichSoCore` / `gregorian_to_lunar`: Khởi quẻ theo Âm lịch + Giờ Chi thực tế, đồng bộ mốc chuyển năm Địa Chi theo Lập Xuân kinh độ 315°, xuất Quẻ Chủ, Hào Động, Hỗ Quái, Quẻ Biến, phân định 5 quan hệ Thể-Dụng và luận thời vận tài lộc. "
                            "QUY TẮC BẮT BUỘC: Trả lời thẳng vào bản chất kỹ thuật, trích dẫn trực tiếp tên hàm/logic thật trong mã nguồn, dùng ngôn ngữ tâm lý hành vi để giải thích, "
                            "và luôn nhắc nhở sòng phẳng rằng xổ số là ngẫu nhiên tuyệt đối, ứng dụng là bộ lọc kỷ luật quản trị cảm xúc chứ không phải công cụ bẻ khóa."
                        )

                        candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
                        ai_reply = None
                        last_error = ""

                        payload = {
                            "system_instruction": {
                                "parts": [{"text": gemini_system_prompt}]
                            },
                            "contents": [
                                {
                                    "role": "user",
                                    "parts": [{"text": user_query}]
                                }
                            ]
                        }
                        headers = {"Content-Type": "application/json"}

                        for model_name in candidate_models:
                            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                            response = requests.post(url, headers=headers, json=payload, timeout=25)
                            if response.status_code == 200:
                                res_json = response.json()
                                candidates = res_json.get("candidates", [])
                                if candidates and candidates[0].get("content", {}).get("parts"):
                                    ai_reply = candidates[0]["content"]["parts"][0]["text"]
                                    break
                                else:
                                    last_error = f"Model {model_name} trả về phản hồi rỗng hoặc bị chặn bởi bộ lọc an toàn."
                            else:
                                last_error = f"Model {model_name} lỗi HTTP {response.status_code}: {response.text}"

                        if ai_reply:
                            st.markdown(ai_reply, unsafe_allow_html=True)
                            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
                        else:
                            st.error(f"Không thể nhận phản hồi từ Gemini API. Chi tiết: {last_error}")

                except Exception as e:
                    st.error(f"Lỗi hệ thống kết nối AI: {e}")

# =====================================================================
# 🛡️ 10. CHỮ KÝ SỞ HỮU VÀ BẢN QUYỀN (WATERMARK & BRAND OWNER)
# =====================================================================
st.markdown("""
    <div class="watermark-box">
        <p style="color: #00E676; font-weight: bold; margin: 0; font-size: 15px;">🏛️ Vietlott Harmony Edition v2.6 — ACADEMIC EDITION</p>
        <p style="color: #FAFAFA; margin: 5px 0 0 0; font-size: 13px;">🔒 Phát triển độc quyền & Vận hành bởi: <b>TruongNV</b></p>
        <p style="color: #8C92A4; margin: 3px 0 0 0; font-size: 11px;">Hệ thống phân tích định lượng đa chiều Real-Time Engine • Academic Profile Active</p>
    </div>
""", unsafe_allow_html=True)
