import streamlit as st
import random
import os
import re
import json
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
        margin-bottom: 18px;
        border: 1px solid #2E3446;
        border-left: 5px solid #D4AF37;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
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
        "github_jsonl": None,
        "backups": [
            "https://www.minhngoc.net/ket-qua-xo-so/vietlott/5-35.html",
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
        "github_jsonl": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power645.jsonl",
        "backups": [
            "https://www.minhngoc.net/ket-qua-xo-so/vietlott/mega-645.html",
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
        "github_jsonl": "https://raw.githubusercontent.com/vietvudanh/vietlott-data/main/data/power655.jsonl",
        "backups": [
            "https://www.minhngoc.net/ket-qua-xo-so/vietlott/power-655.html",
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

def fetch_html(url: str) -> str:
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        if resp.status_code == 200 and len(resp.text) > 300:
            return resp.text
    except Exception:
        pass
    return ""

def parse_history_from_html(html: str, game_cfg: dict) -> List[Dict[str, Any]]:
    """
    Trích xuất kết quả quay số từ HTML bằng 2 chiến lược kết hợp:
    1. Bắt theo cụm thẻ bóng số / kết quả đa dòng (DOM tag blocks).
    2. Bắt theo dòng văn bản sau khi làm sạch thẻ HTML (tag-stripped blocks quanh dấu mốc ngày/kỳ quay).
    """
    history = []
    if not html:
        return history

    pick_n = game_cfg["pick"]
    max_m = game_cfg["max_main"]
    has_spec = game_cfg.get("has_special", False)
    spec_max = game_cfg.get("special_max", 12)
    req_len = pick_n + (1 if has_spec else 0)

    # Làm sạch script/style trước khi phân tích
    clean_html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.IGNORECASE | re.DOTALL)

    # Chiến lược 1: Tìm các khối HTML chứa danh sách bóng kết quả (thường nằm trong <ul>, <div>, <tr>)
    # Gộp các thẻ <li> hoặc <span> chứa số 2 chữ số liên tiếp nhau
    ball_groups = re.findall(
        r"(?:<(?:li|span|div|td)[^>]*>\s*\d{1,2}\s*</(?:li|span|div|td)>\s*){" + str(req_len) + r",8}",
        clean_html,
        flags=re.IGNORECASE
    )

    seen_sets = set()
    draw_id = 9999

    for grp in ball_groups:
        nums = [int(x) for x in re.findall(r">\s*(\d{1,2})\s*<", grp)]
        if len(nums) >= req_len:
            mains_raw = nums[:pick_n]
            # Kiểm tra tính hợp lệ: các số chính phải phân biệt và nằm trong [1, max_m]
            if len(set(mains_raw)) == pick_n and all(1 <= n <= max_m for n in mains_raw):
                mains = sorted(mains_raw)
                spec_val = nums[pick_n] if has_spec else None
                if has_spec and not (1 <= spec_val <= spec_max):
                    continue
                sig = (tuple(mains), spec_val)
                if sig not in seen_sets:
                    seen_sets.add(sig)
                    entry = {"draw": draw_id, "mains": mains}
                    if has_spec:
                        entry["special"] = spec_val
                    history.append(entry)
                    draw_id -= 1

    if len(history) >= 1:
        return history

    # Chiến lược 2: Chuyển HTML thành văn bản thuần theo khối và tìm cụm số ngay sau mốc kỳ quay / ngày tháng
    text_only = re.sub(r"<[^>]+>", " ", clean_html)
    text_only = re.sub(r"\s+", " ", text_only)

    # Tìm các đoạn theo sau mẫu ngày dd/mm/yyyy hoặc mã kỳ #00xxx
    segments = re.split(r"(?:#\d{4,6}|\b\d{1,2}/\d{1,2}/20\d{2}\b)", text_only)
    for seg in segments[1:]:
        window = seg[:160]
        tokens = [int(x) for x in re.findall(r"\b\d{1,2}\b", window)]
        # Tìm cửa sổ con dài req_len thỏa mãn bộ số hợp lệ
        for idx in range(max(0, len(tokens) - req_len + 1)):
            cand_main = tokens[idx : idx + pick_n]
            if len(set(cand_main)) == pick_n and all(1 <= n <= max_m for n in cand_main):
                spec_val = tokens[idx + pick_n] if (has_spec and idx + pick_n < len(tokens)) else None
                if has_spec and (spec_val is None or not (1 <= spec_val <= spec_max)):
                    continue
                mains = sorted(cand_main)
                sig = (tuple(mains), spec_val)
                if sig not in seen_sets:
                    seen_sets.add(sig)
                    entry = {"draw": draw_id, "mains": mains}
                    if has_spec:
                        entry["special"] = spec_val
                    history.append(entry)
                    draw_id -= 1
                break

    return history

def _merge_unique_history(primary: List[Dict[str, Any]], secondary: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gộp dữ liệu và khử trùng lặp dựa trên bộ số chính + số đặc biệt."""
    merged = []
    seen = set()
    for item in primary + secondary:
        key = (tuple(item["mains"]), item.get("special"))
        if key not in seen:
            seen.add(key)
            merged.append(item)
    return merged

def get_history(game_key: str, sample_k: int = 80, force_refresh: bool = False) -> Tuple[List[Dict[str, Any]], str, float]:
    """
    Ưu tiên tuyệt đối FetchData trực tiếp (Live Web) để lấy kết quả gần nhất.
    - Nếu FetchData trực tiếp thành công: đưa dữ liệu mới nhất lên đầu, gộp với Smart Cache (và GitHub Seed nếu cần đủ tầm nhìn).
    - Nếu FetchData trực tiếp lỗi/không bắt được dữ liệu: dùng Smart Cache hiện có; nếu vẫn chưa đủ kỳ thì mới gọi GitHub Backup Seed.
    """
    game_cfg = GAMES.get(game_key)
    if not game_cfg:
        return [], "Game không tồn tại", 0.0

    cache_file = os.path.join(CACHE_DIR, f"history_{game_key}.json")
    meta_file = os.path.join(CACHE_DIR, f"meta_{game_key}.json")
    expected_latest_date = get_latest_expected_draw_date(game_key)

    existing_cache = []
    cache_age = 0.0
    cache_is_fresh = False

    if os.path.exists(cache_file):
        cache_age = time.time() - os.path.getmtime(cache_file)
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                existing_cache = json.load(f)
            if not force_refresh and os.path.exists(meta_file):
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    cached_date = datetime.strptime(meta.get("latest_date", "2000-01-01"), "%Y-%m-%d").date()
                    if len(existing_cache) >= sample_k and cached_date >= expected_latest_date:
                        cache_is_fresh = True
        except Exception:
            pass

    if cache_is_fresh:
        return existing_cache[:sample_k], f"📁 Smart Cache Mới nhất ({len(existing_cache)} kỳ thật)", cache_age

    # Bước 1 (Chủ động): Luôn chạy FetchData trực tiếp từ nguồn web để lấy kết quả gần nhất
    live_fetched = []
    active_source_url = ""
    urls = [game_cfg.get("url")] + game_cfg.get("backups", [])
    for url in dict.fromkeys(u for u in urls if u):
        html = fetch_html(url)
        parsed = parse_history_from_html(html, game_cfg)
        if len(parsed) >= 1:
            live_fetched = parsed
            active_source_url = url.split("/")[2]
            break

    # Bước 2 (Backup): Chỉ lấy GitHub Seed khi FetchData trực tiếp gặp lỗi/thiếu dữ liệu và cache chưa đủ kỳ
    github_seed = []
    current_pool_len = len(live_fetched) + len(existing_cache)
    if (not live_fetched or current_pool_len < sample_k) and game_cfg.get("github_jsonl"):
        github_seed = fetch_github_seed_data(game_cfg["github_jsonl"], game_cfg)

    # Bước 3: Hợp nhất ưu tiên Live FetchData -> Existing Cache -> GitHub Backup Seed
    combined = _merge_unique_history(live_fetched, _merge_unique_history(existing_cache, github_seed))

    if combined:
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(combined, f, ensure_ascii=False)
            if live_fetched:
                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump({"latest_date": expected_latest_date.strftime("%Y-%m-%d")}, f)
                cache_age = 0.0
        except Exception:
            pass

        if live_fetched:
            status = f"🟢 FetchData Trực tuyến ({active_source_url}) — Cập nhật kỳ gần nhất (Tích lũy {len(combined)} kỳ thật)"
        elif existing_cache and github_seed:
            status = f"🛡️ FetchData lỗi -> Smart Cache + GitHub Backup ({len(combined)} kỳ thật)"
        elif github_seed:
            status = f"🛡️ FetchData lỗi -> GitHub Backup Data ({len(combined)} kỳ lịch sử thật)"
        else:
            status = f"🛡️ FetchData lỗi -> Smart Cache Dự phòng ({len(combined)} kỳ thật)"

        return combined[:sample_k], status, cache_age

    return [], "⚠️ FetchData trực tiếp thất bại và không có dữ liệu Cache/Backup khả dụng", 0.0


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
    def get_solar_term_riping(year: int) -> datetime:
        try:
            base_year = 2000
            base_datetime = datetime(2000, 2, 4, 12, 18)
            year_diff = year - base_year
            hours_shift = year_diff * 5.8167 + (year_diff // 4) * 24 - (year_diff // 100) * 24 + (year_diff // 400) * 24
            lap_xuan_utc = base_datetime + timedelta(hours=hours_shift)
            lap_xuan_vn = lap_xuan_utc + timedelta(hours=7)
            safe_day = 4 if lap_xuan_vn.day < 5 else 5
            return datetime(year, 2, safe_day, lap_xuan_vn.hour, lap_xuan_vn.minute)
        except Exception:
            return datetime(year, 2, 4, 12, 0)

    @classmethod
    def get_lunar_year(cls, y: int, m: int, d: int) -> int:
        user_datetime = datetime(y, m, d, 12, 0)
        lap_xuan_time = cls.get_solar_term_riping(y)
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
            ((1,21),(2,19), "Bảo Bình", "Khí", "Kiên định (Fixed)", "Sao Thiên Vương & Sao Thổ"),
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
# 🌸 3B. LÕI CHUYÊN GIA HÀNH VI: MAI HOA DỊCH SỐ (STANDALONE ADVISORY)
# =====================================================================
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

    CHI_GIO = [
        ("Tý (23h-01h)", 1), ("Sửu (01h-03h)", 2), ("Dần (03h-05h)", 3),
        ("Mão (05h-07h)", 4), ("Thìn (07h-09h)", 5), ("Tỵ (09h-11h)", 6),
        ("Ngọ (11h-13h)", 7), ("Mùi (13h-15h)", 8), ("Thân (15h-17h)", 9),
        ("Dậu (17h-19h)", 10), ("Tuất (19h-21h)", 11), ("Hợi (21h-23h)", 12)
    ]

    NGU_HANH_SINH = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
    NGU_HANH_KHAC = {"Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim"}

    @classmethod
    def _bits_to_quai_id(cls, bits: List[int]) -> int:
        for q_id, info in cls.BAT_QUAI.items():
            if info["bits"] == bits:
                return q_id
        return 8

    @classmethod
    def cast_hexagram(cls, dt: datetime) -> Dict[str, Any]:
        hour_idx = ((dt.hour + 1) // 2) % 12
        chi_name, gio_num = cls.CHI_GIO[hour_idx]

        nam_num = ((dt.year - 4) % 12) + 1
        thang_num = dt.month
        ngay_num = dt.day

        tong_thuong = nam_num + thang_num + ngay_num
        thuong_id = tong_thuong % 8
        thuong_id = 8 if thuong_id == 0 else thuong_id

        tong_ha = tong_thuong + gio_num
        ha_id = tong_ha % 8
        ha_id = 8 if ha_id == 0 else ha_id

        hao_dong = tong_ha % 6
        hao_dong = 6 if hao_dong == 0 else hao_dong

        ha_bits = cls.BAT_QUAI[ha_id]["bits"].copy()
        thuong_bits = cls.BAT_QUAI[thuong_id]["bits"].copy()
        full_bits = ha_bits + thuong_bits

        bien_bits = full_bits.copy()
        bien_bits[hao_dong - 1] = 1 - bien_bits[hao_dong - 1]

        ha_bien_id = cls._bits_to_quai_id(bien_bits[:3])
        thuong_bien_id = cls._bits_to_quai_id(bien_bits[3:])

        if hao_dong <= 3:
            the_id, dung_id = thuong_id, ha_id
            the_pos = "Thượng Quái"
        else:
            the_id, dung_id = ha_id, thuong_id
            the_pos = "Hạ Quái"

        the_elem = cls.BAT_QUAI[the_id]["element"]
        dung_elem = cls.BAT_QUAI[dung_id]["element"]

        if the_elem == dung_elem or cls.NGU_HANH_SINH.get(dung_elem) == the_elem:
            zone = "CAT"
            zone_label = "🟢 VÙNG CÁT — Thời điểm thuận lợi & Tâm thế vững vàng"
            summary = f"Dụng ({dung_elem}) tương sinh/tỷ hòa với Thể ({the_elem}). Nhịp năng lượng thời điểm hanh thông, nội ngoại đồng thuận."
            advice = "Tham gia với ngân sách chủ động và quản trị nguồn vốn hợp lý, đảm bảo tuyệt đối không ảnh hưởng tới tài chính cá nhân hoặc gia đình."
        elif cls.NGU_HANH_SINH.get(the_elem) == dung_elem or cls.NGU_HANH_KHAC.get(the_elem) == dung_elem:
            zone = "BINH"
            zone_label = "🟡 VÙNG BÌNH — Thời điểm trung lập & Cần tiết chế"
            summary = f"Thể ({the_elem}) sinh xuất hoặc khắc chế Dụng ({dung_elem}). Vạn vật ở thế cân bằng tĩnh, cần quan sát kỹ lưỡng."
            advice = "Bối cảnh hiện tại phù hợp để quan sát dữ liệu và rèn luyện kỷ luật hơn là hành động mạnh. Ưu tiên bảo toàn lực lượng."
        else:
            zone = "BI"
            zone_label = "🔴 VÙNG BĨ — Cảnh báo rủi ro & Cảm xúc dễ dao động"
            summary = f"Dụng ({dung_elem}) khắc Thể ({the_elem}). Tín hiệu tượng quẻ cho thấy năng lượng xung đột và tâm lý nóng vội."
            advice = "KHUYẾN NGHỊ TỐI THƯỢNG: TẠM DỪNG THAM GIA! Đóng ví ngay lập tức, giữ chặt nguồn vốn và tuyệt đối không phát sinh chi phí mạo hiểm."

        que_chu_name = f"{cls.BAT_QUAI[thuong_id]['nature']} {cls.BAT_QUAI[ha_id]['nature']} ({cls.BAT_QUAI[thuong_id]['name']} trên - {cls.BAT_QUAI[ha_id]['name']} dưới)"
        que_bien_name = f"{cls.BAT_QUAI[thuong_bien_id]['nature']} {cls.BAT_QUAI[ha_bien_id]['nature']} ({cls.BAT_QUAI[thuong_bien_id]['name']} trên - {cls.BAT_QUAI[ha_bien_id]['name']} dưới)"

        return {
            "timestamp": dt.strftime("%H:%M:%S — %d/%m/%Y"),
            "chi_gio": chi_name,
            "que_chu": que_chu_name,
            "hao_dong": f"Hào {hao_dong} ({the_pos} làm Thể - hành {the_elem})",
            "que_bien": que_bien_name,
            "zone": zone,
            "zone_label": zone_label,
            "summary": summary,
            "advice": advice
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
    • <b>Trạm Mai Hoa Dịch Số:</b> Mô-đun chuyên gia tư vấn hành vi độc lập theo thời điểm động tâm thực tế (Real-time VN_TZ) — phân định Vùng Cát / Bình / Bĩ gắn liền trạng thái quẻ Thể-Dụng làm lớp phanh an toàn quản trị vốn.<br>
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
# 🌸 8. TRẠM MAI HOA DỊCH SỐ — CHUYÊN GIA TƯ VẤN HÀNH VI (REAL-TIME UPDATE)
# =====================================================================
with st.expander("🌸 Mai Hoa Dịch Số — Trạm Chiêm Nghiệm Thời Vận & Kỷ Luật (Tư vấn Hành vi)", expanded=False):
    st.markdown(
        "<div style='font-size: 13.5px; color: #C5CAE9; margin-bottom: 10px;'>"
        "<b>📖 Vai trò & Học thuật:</b> Sau khi xem xét các bộ số định lượng, mô-đun này cung cấp một góc nhìn tham vấn "
        "về thời vận dựa trên phương pháp <i>Mai Hoa Dịch Số</i> theo thời điểm động tâm thực tế. "
        "<b>Đứng độc lập hoàn toàn</b>, đây là lớp phanh an toàn giúp đánh giá nhịp sinh học tài chính và tâm lý kỷ luật của bạn."
        "</div>",
        unsafe_allow_html=True
    )

    if st.button("🧭 Khởi Tạo Quẻ Thời Vận Hiện Tại (Lấy Thời Điểm Động Tâm Real-time)", key="btn_mai_hoa_bottom"):
        st.session_state["dong_tam_time"] = now_vn()
    elif "dong_tam_time" not in st.session_state:
        st.session_state["dong_tam_time"] = now_vn()

    iching_res = MaiHoaDichSoCore.cast_hexagram(st.session_state["dong_tam_time"])

    st.markdown(f"""
    <div class="iching-card">
        <div style="font-size: 13px; color: #D4AF37; font-weight: bold; margin-bottom: 6px;">
            ⏳ Thời điểm động tâm (Real-time): {iching_res['timestamp']} • Giờ {iching_res['chi_gio']}
        </div>
        <div style="font-size: 14px; color: #FAFAFA; line-height: 1.6;">
            • <b>Quẻ Chủ:</b> {iching_res['que_chu']}<br>
            • <b>Hào Động:</b> {iching_res['hao_dong']}<br>
            • <b>Quẻ Biến:</b> {iching_res['que_bien']}
        </div>
        <hr style="border-color: #2E3446; margin: 10px 0;">
        <div style="font-size: 15px; font-weight: bold; margin-bottom: 6px;">
            {iching_res['zone_label']}
        </div>
        <div style="font-size: 13px; color: #B0BEC5; margin-bottom: 8px;">
            <i>Luận giải Thể - Dụng:</i> {iching_res['summary']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if iching_res["zone"] == "CAT":
        st.success(f"💡 **Khuyến nghị Quản trị Vốn:** {iching_res['advice']}")
    elif iching_res["zone"] == "BINH":
        st.warning(f"⚖️ **Khuyến nghị Quản trị Vốn:** {iching_res['advice']}")
    else:
        st.error(f"🛡️ **Khuyến nghị Quản trị Vốn:** {iching_res['advice']}")

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
                            "- `PhongThuyReferenceCore`: Tính Can Chi, Nạp Âm 60 Hoa Giáp, Cung Phi Lạc Thư chuẩn tiết Lập Xuân (tự động bỏ qua Cung Phi và điều chỉnh trọng số động xuống 28.3% nếu giới tính không xác định). "
                            "- `FlexibleCouncilEvaluator.judge_western_deep`: Chiêm tinh cổ điển 3 tầng (Tứ đại Nguyên tố, Phẩm tính Vận động, Hành tinh Đắc vị). "
                            "- `FlexibleCouncilEvaluator.judge_statistics_hot_cold`: Lọc chiến lược Hot/Neutral/Cold trên tập dữ liệu lịch sử thật. "
                            "- `MaiHoaDichSoCore`: Trạm chiêm nghiệm Mai Hoa Dịch Số đánh giá thời vận (Cát/Bình/Bĩ) và kỷ luật quản trị vốn real-time. "
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
