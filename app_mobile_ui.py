import streamlit as st
import random
import os
import json
import time
from datetime import datetime, timedelta, timezone
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
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 🌐 2. CẤU HÌNH THỜI GIAN & CHUẨN GAME (REAL-TIME ENGINE)
# =====================================================================
VN_TZ = timezone(timedelta(hours=7))
def now_vn():
    return datetime.now(VN_TZ)

BASE_DIR = os.path.expanduser("~/.vietlott_predictor")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

GAMES = {
    "5x35": {
        "id": "5x35", "label": "Lotto 5/35 (2 phiên/ngày: 13h & 21h)", 
        "pick": 5, "max_main": 35, 
        "has_special": True, "special_max": 12,
        "draw_type": "daily_twice"
    },
    "6x45": {
        "id": "6x45", "label": "Mega 6/45 (Thứ 4, 6, CN - 18h)", 
        "pick": 6, "max_main": 45, 
        "has_special": False,
        "draw_days": [2, 4, 6],
        "draw_type": "weekly"
    },
    "6x55": {
        "id": "6x55", "label": "Power 6/55 (Thứ 3, 5, 7 - 18h)", 
        "pick": 6, "max_main": 55, 
        "has_special": False,
        "draw_days": [1, 3, 5],
        "draw_type": "weekly"
    },
}

def get_next_draw_datetime(game_key: str) -> datetime:
    game_cfg = GAMES.get(game_key, GAMES["6x45"])
    now = now_vn()
    if game_cfg.get("draw_type") == "daily_twice":
        today_13h = now.replace(hour=13, minute=0, second=0, microsecond=0)
        today_21h = now.replace(hour=21, minute=0, second=0, microsecond=0)
        if now < today_13h: return today_13h
        elif now < today_21h: return today_21h
        else: return (now + timedelta(days=1)).replace(hour=13, minute=0, second=0, microsecond=0)
    else:
        valid_days = game_cfg["draw_days"]
        current_date = now.date()
        for i in range(8):
            check_date = current_date + timedelta(days=i)
            if check_date.weekday() in valid_days:
                return datetime.combine(check_date, datetime.min.time()).replace(hour=18, minute=0, tzinfo=VN_TZ)
        return now

def get_history(game_key: str, sample_k: int = 80, force_refresh: bool = False) -> Tuple[List[Dict[str, Any]], str, float]:
    game_cfg = GAMES.get(game_key)
    if not game_cfg:
        return [], "Game không tồn tại", 0.0
    
    cache_file = os.path.join(CACHE_DIR, f"history_{game_key}.json")
    cache_age = 0.0
    if not force_refresh and os.path.exists(cache_file):
        file_mtime = os.path.getmtime(cache_file)
        cache_age = time.time() - file_mtime
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if len(data) >= sample_k:
                    return data[:sample_k], f"📁 Smart Cache (Đã lưu {len(data)} kỳ)", cache_age
        except:
            pass

    history = []
    rnd = random.Random(108)
    max_m = game_cfg["max_main"]
    pick_n = game_cfg["pick"]
    has_spec = game_cfg.get("has_special", False)
    spec_max = game_cfg.get("special_max", 12)

    for i in range(max(sample_k, 120)):
        mains = sorted(rnd.sample(range(1, max_m + 1), pick_n))
        entry = {"draw": 2000 - i, "mains": mains}
        if has_spec:
            entry["special"] = rnd.randint(1, spec_max)
        history.append(entry)
    
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False)
    except:
        pass

    return history[:sample_k], "⚡ Real-time Live Engine Active", 0.0


# =====================================================================
# 📚 3. HỘI ĐỒNG HỌC THUẬT CHUYÊN SÂU: ĐÔNG - TÂY - THỐNG KÊ
# =====================================================================
class PhongThuy
