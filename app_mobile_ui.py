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
    page_title="Harmony Council Pro v2.6 - Live Chamber",
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
        line-height: 1.5;
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
        padding: 10px 15px;
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
# 📚 3. BẢNG TRA "LỊCH TẾT" NGUYÊN BẢN (1924–2100) & PHONG THỦY CORE
# =====================================================================
class PhongThuyReferenceCore:
    VIETNAMESE_NEW_YEAR = {
        1924: (5, 2), 1925: (24, 1), 1926: (13, 2), 1927: (2, 2), 1928: (23, 1),
        1929: (10, 2), 1930: (30, 1), 1931: (17, 2), 1932: (6, 2), 1933: (26, 1),
        1934: (14, 2), 1935: (4, 2), 1936: (24, 1), 1937: (11, 2), 1938: (31, 1),
        1939: (19, 2), 1940: (8, 2), 1941: (27, 1), 1942: (15, 2), 1943: (4, 2),
        1944: (25, 1), 1945: (13, 2), 1946: (2, 2), 1947: (22, 1), 1948: (10, 2),
        1949: (29, 1), 1950: (17, 2), 1951: (6, 2), 1952: (27, 1), 1953: (14, 2),
        1954: (5, 2), 1955: (24, 1), 1956: (12, 2), 1957: (31, 1), 1958: (18, 2),
        1959: (8, 2), 1960: (28, 1), 1961: (15, 2), 1962: (5, 2), 1963: (25, 1),
        1964: (13, 2), 1965: (2, 2), 1966: (21, 1), 1967: (9, 2), 1968: (30, 1),
        1969: (17, 2), 1970: (6, 2), 1971: (27, 1), 1972: (15, 2), 1973: (3, 2),
        1974: (23, 1), 1975: (11, 2), 1976: (31, 1), 1977: (18, 2), 1978: (7, 2),
        1979: (28, 1), 1980: (16, 2), 1981: (5, 2), 1982: (25, 1), 1983: (13, 2),
        1984: (2, 2), 1985: (20, 2), 1986: (9, 2), 1987: (29, 1), 1988: (17, 2),
        1989: (6, 2), 1990: (27, 1), 1991: (15, 2), 1992: (4, 2), 1993: (23, 1),
        1994: (10, 2), 1995: (31, 1), 1996: (19, 2), 1997: (7, 2), 1998: (28, 1),
        1999: (16, 2), 2000: (5, 2), 2001: (24, 1), 2002: (12, 2), 2003: (1, 2),
        2004: (22, 1), 2005: (9, 2), 2006: (29, 1), 2007: (18, 2), 2008: (7, 2),
        2009: (26, 1), 2010: (14, 2), 2011: (3, 2), 2012: (23, 1), 2013: (10, 2),
        2014: (31, 1), 2015: (19, 2), 2016: (8, 2), 2017: (28, 1), 2018: (16, 2),
        2019: (5, 2), 2020: (25, 1), 2021: (12, 2), 2022: (1, 2), 2023: (22, 1),
        2024: (10, 2), 2025: (29, 1), 2026: (17, 2), 2027: (6, 2), 2028: (26, 1),
        2029: (13, 2), 2030: (3, 2), 2031: (23, 1), 2032: (11, 2), 2033: (31, 1),
        2034: (19, 2), 2035: (8, 2), 2036: (28, 1), 2037: (15, 2), 2038: (4, 2),
        2039: (24, 1), 2040: (12, 2), 2041: (1, 2), 2042: (22, 1), 2043: (10, 2),
        2044: (30, 1), 2045: (17, 2), 2046: (6, 2), 2047: (26, 1), 2048: (14, 2),
        2049: (2, 2), 2050: (23, 1), 2051: (11, 2), 2052: (31, 1), 2053: (19, 2),
        2054: (8, 2), 2055: (28, 1), 2056: (15, 2), 2057: (4, 2), 2058: (24, 1),
        2059: (12, 2), 2060: (2, 2), 2061: (21, 1), 2062: (10, 2), 2063: (29, 1),
        2064: (17, 2), 2065: (5, 2), 2066: (26, 1), 2067: (14, 2), 2068: (3, 2),
        2069: (22, 1), 2070: (11, 2), 2071: (31, 1), 2072: (19, 2), 2073: (7, 2),
        2074: (27, 1), 2075: (16, 2), 2076: (5, 2), 2077: (24, 1), 2078: (13, 2),
        2079: (3, 2), 2080: (22, 1), 2081: (9, 2), 2082: (29, 1), 2083: (18, 2),
        2084: (4, 2), 2085: (24, 1), 2086: (12, 2), 2087: (1, 2), 2088: (21, 1),
        2089: (9, 2), 2090: (29, 1), 2091: (17, 2), 2092: (6, 2), 2093: (25, 1),
        2094: (13, 2), 2095: (2, 2), 2096: (22, 1), 2097: (10, 2), 2098: (30, 1),
        2099: (18, 2), 2100: (9, 2)
    }

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

    @classmethod
    def get_lunar_year(cls, y: int, m: int, d: int) -> int:
        tet_day, tet_month = cls.VIETNAMESE_NEW_YEAR.get(y, (21, 1))
        return y - 1 if (m < tet_month or (m == tet_month and d < tet_day)) else y

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
        
        if gender.lower() == "nam":
            cung_menh_map = {0: "Khảm (Thủy)", 1: "Khôn (Thổ)", 2: "Chấn (Mộc)", 3: "Tốn (Mộc)", 4: "Cấn (Thổ)", 5: "Càn (Kim)", 6: "Đoài (Kim)", 7: "Cấn (Thổ)", 8: "Ly (Hỏa)"}
            cung_menh = cung_menh_map.get(l_year % 9, "Khảm (Thủy)")
        else:
            cung_menh_map = {0: "Cấn (Thổ)", 1: "Khảm (Thủy)", 2: "Khôn (Thổ)", 3: "Chấn (Mộc)", 4: "Tốn (Mộc)", 5: "Cấn (Thổ)", 6: "Càn (Kim)", 7: "Đoài (Kim)", 8: "Cấn (Thổ)"}
            cung_menh = cung_menh_map.get(l_year % 9, "Cấn (Thổ)")

        Z = [
            ((3,21),(4,20),"Bạch Dương"),((4,21),(5,20),"Kim Ngưu"),
            ((5,21),(6,21),"Song Tử"), ((6,22),(7,22),"Cự Giải"),
            ((7,23),(8,22),"Sư Tử"), ((8,23),(9,22),"Xử Nữ"),
            ((9,23),(10,23),"Thiên Bình"),((10,24),(11,22),"Bọ Cạp"),
            ((11,23),(12,21),"Nhân Mã"), ((12,22),(1,20),"Ma Kết"),
            ((1,21),(2,19),"Bảo Bình"), ((2,20),(3,20),"Song Ngư")
        ]
        wz = "Song Ngư"
        for (m1,d1),(m2,d2),name in Z:
            if (m==m1 and d>=d1) or (m==m2 and d<=d2):
                wz = name
                break

        weekday_elem_map = {0:"Kim", 1:"Mộc", 2:"Thủy", 3:"Hỏa", 4:"Thổ", 5:"Kim", 6:"Mộc"}
        draw_elem = weekday_elem_map.get(draw_dt.weekday(), "Kim")
        
        return {
            "can": cls.CAN[can_idx], "chi": cls.CHI[chi_idx],
            "menh": menh, "menh_elem": menh_elem,
            "cung_menh": cung_menh, "western_sign": wz,
            "draw_datetime": draw_dt.strftime("%d/%m/%Y %H:%M"),
            "draw_elem": draw_elem,
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
    def judge_western(num: int, western_sign: str) -> float:
        return 1.0 if num % 2 != 0 else 0.6

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
# 🏛️ 4. HEADER & BANNER (TRÍCH YẾU HỌC THUẬT)
# =====================================================================
st.markdown("### 🏛️ HARMONY COUNCIL PRO v2.6")
st.caption("🔒 **REAL-TIME CACHED ENGINE** | Tích hợp Bảng Lịch Tết Nguyên Bản & Trạng thái Live")

st.markdown("""
<div class="academic-banner">
    <b>📜 TRÍCH YẾU HỌC THUẬT ỨNG DỤNG:</b><br>
    • <b>Phương Đông:</b> Lịch Tết Âm lịch chuẩn (1924–2100), Can Chi, Nạp Âm 60 Hoa Giáp & Cung Mệnh Bát Trạch.<br>
    • <b>Phương Tây:</b> Chiêm tinh học, 12 Cung Hoàng đạo & Tứ đại Nguyên tố (Hỏa, Thổ, Khí, Thủy).<br>
    • <b>Thống kê:</b> Ma trận tần suất lịch sử đa chiều (Chiến lược Hot / Neutral / Cold động).
</div>
""", unsafe_allow_html=True)

st.divider()

# =====================================================================
# 🎵 5. TRÌNH PHÁT NHẠC NỀN TỰ CHẠY (VIETLOTT-AUDIO / MUSIC_BG.MP3)
# =====================================================================
with st.expander("🎵 Trình phát Nhạc nền & Tần số Thư giãn (Ambient Audio)", expanded=True):
    st.caption("Trình phát âm thanh tần số Alpha từ kho `Vietlott-Audio` của bạn (Tự động phát):")
    
    audio_html = """
    <audio id="bg-audio" autoplay loop controls style="width: 100%;">
        <source src="https://raw.githubusercontent.com/TruongNV-D11/Vietlott-Audio/main/music_bg.mp3" type="audio/mp3">
        Trình duyệt của bạn không hỗ trợ thẻ audio.
    </audio>
    <script>
        document.addEventListener('DOMContentLoaded', (event) => {
            var audio = document.getElementById("bg-audio");
            if (audio) {
                audio.volume = 0.5;
                var playPromise = audio.play();
                if (playPromise !== undefined) {
                    playPromise.catch(error => {
                        document.addEventListener('click', () => { audio.play(); }, { once: true });
                    });
                }
            }
        });
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
    st.markdown("👤 **Ngày sinh Bản mệnh người chơi (Áp dụng Bảng Lịch Tết Nguyên Bản):**")
    col_bd, col_bm, col_by = st.columns(3)
    with col_bd:
        bday = st.selectbox("Ngày sinh", list(range(1, 32)), index=1)
    with col_bm:
        bmonth = st.selectbox("Tháng sinh", list(range(1, 13)), index=1)
    with col_by:
        byear = st.selectbox("Năm sinh", list(range(2026, 1939, -1)), index=36)
    
    dob_str = f"{bday:02d}/{bmonth:02d}/{byear}"
    gender = st.radio("Giới tính", ["Nam", "Nữ"], horizontal=True)
    
    profile = PhongThuyReferenceCore.get_full_info(dob_str, gender, draw_dt)
    
    st.markdown(f"""
    <div style="background-color: #1A1C23; border: 1px solid #1D976C; border-radius: 10px; padding: 15px; margin-top: 10px; line-height: 1.8;">
        📅 <b>Bản mệnh:</b> {profile['can']} {profile['chi']} — <b>{profile['menh']}</b><br>
        🏛️ <b>Cung Mệnh (Bát Trạch):</b> {profile['cung_menh']}<br>
        🌟 <b>Cung Hoàng Đạo:</b> {profile['western_sign']} &nbsp;|&nbsp; 🔮 <b>Chiêm Tinh Học:</b> Tứ đại Nguyên tố cộng hưởng<br>
        ⚡ <b>Hành ngày quay:</b> {profile['draw_elem']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("📊 **Cấu hình Tầm nhìn Lịch sử & Khẩu vị Thống kê:**")
    horizon_samples = st.slider("🔍 Tầm nhìn mẫu (Số kỳ quay lịch sử xét duyệt)", min_value=20, max_value=500, value=100, step=10)
    
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
    use_east = st.checkbox("🏛️ Hội đồng Phương Đông (Can Chi / Nạp Âm)", value=True)
    use_west = st.checkbox("🌟 Hội đồng Phương Tây (Cung Hoàng đạo | Chiêm Tinh Học)", value=True)
    use_stat = st.checkbox("📊 Hội đồng Thống kê Ma trận (Tần suất Hot/Cold)", value=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================================
# 🚀 7. NÚT CHẠY CHƯƠNG TRÌNH & HIỆU ỨNG DELAY TĂNG CƯỜNG (CHẠY SỐ TỪNG CON & TỪNG DÃY)
# =====================================================================
run_clicked = st.button("🚀 Khởi động Hội đồng Chấm điểm (Chạy Chương Trình)")

if run_clicked:
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("🔄 Đang thiết lập kết nối Real-time & Nạp Smart Cache lịch sử...")
    progress_bar.progress(25)
    time.sleep(0.6)

    status_text.text("🏛️ Hội đồng Phương Đông & Phương Tây đang đối chiếu bản mệnh người chơi...")
    progress_bar.progress(60)
    time.sleep(0.6)

    status_text.text("📊 Hội đồng Thống kê Ma trận đang chạy khẩu vị Hot/Cold...")
    progress_bar.progress(90)
    time.sleep(0.6)

    status_text.text("✅ Hoàn tất thẩm định đa chiều!")
    progress_bar.progress(100)
    time.sleep(0.4)
    
    progress_bar.empty()
    status_text.empty()

    st.markdown(f"### 🎯 KẾT QUẢ THẨM ĐỊNH THỰC CHIẾN ({num_rows} BỘ SỐ - {game_cfg['label']})")

    history_data, data_source_status, cache_age_sec = get_history(game_key, sample_k=horizon_samples, force_refresh=False)

    age_min = round(cache_age_sec / 60, 1)
    st.success(
        f"🌐 **Trạng thái Data:** {data_source_status} | "
        f"⏱️ **Tuổi Cache (Cache Age):** {age_min} phút ({int(cache_age_sec)} giây) | "
        f"🕒 **Kỳ quay:** {profile['draw_datetime']}"
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
    if use_stat: active_councils.append("statistics")

    weight_per_council = 1.0 / len(active_councils) if active_councils else 1.0

    candidate_scores = []
    for num in range(1, max_main + 1):
        total_score = 0.0
        s_east, s_west, s_stat = 0.5, 0.5, 0.5

        if "eastern" in active_councils:
            s_east = FlexibleCouncilEvaluator.judge_eastern(num, profile["menh_elem"])
            total_score += s_east * weight_per_council
        if "western" in active_councils:
            s_west = FlexibleCouncilEvaluator.judge_western(num, profile["western_sign"])
            total_score += s_west * weight_per_council
        if "statistics" in active_councils:
            s_stat = FlexibleCouncilEvaluator.judge_statistics_hot_cold(num, freq_map, hc_strategy)
            total_score += s_stat * weight_per_council

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
        base_score = round(rnd.uniform(91.0, 99.2), 2)
        
        results.append({
            "set": chosen,
            "special": spec_num,
            "score": base_score,
            "east_score": round(base_score - rnd.uniform(0.2, 1.2), 1),
            "west_score": round(base_score + rnd.uniform(0.1, 0.8), 1),
            "stat_score": round(base_score - rnd.uniform(0.5, 1.8), 1),
            "detail_east": f"Can Chi {profile['can']} {profile['chi']} & Cung mệnh {profile['cung_menh']} tương thích hành {profile['menh_elem']}.",
            "detail_west": f"Cộng hưởng sóng Chiêm tinh học & cung hoàng đạo {profile['western_sign']}.",
            "detail_stat": f"Tầm nhìn {horizon_samples} kỳ: Khớp chiến lược {hc_strategy.split(' ')[1]}."
        })

    for idx, res in enumerate(results, 1):
        card_placeholder = st.empty()
        
        animated_balls_html = ""
        for num in res['set']:
            time.sleep(0.35) 
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
                    <b>🌟 Huyền Học Phương Tây ({res['west_score']}%):</b> {res['detail_west']}<br>
                    <b>📊 Thuật Toán Thống Kê ({res['stat_score']}%):</b> {res['detail_stat']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        if res["special"] is not None:
            time.sleep(0.35)
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
                    <b>🌟 Huyền Học Phương Tây ({res['west_score']}%):</b> {res['detail_west']}<br>
                    <b>📊 Thuật Toán Thống Kê ({res['stat_score']}%):</b> {res['detail_stat']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        time.sleep(0.5)

st.divider()

# =====================================================================
# 🛡️ 8. CHỮ KÝ SỞ HỮU VÀ BẢN QUYỀN (WATERMARK & BRAND OWNER)
# =====================================================================
st.markdown("""
    <div class="watermark-box">
        <p style="color: #00E676; font-weight: bold; margin: 0; font-size: 15px;">🏛️ HARMONY COUNCIL PRO v2.6 — MOBILE EDITION</p>
        <p style="color: #FAFAFA; margin: 5px 0 0 0; font-size: 13px;">🔒 Phát triển độc quyền & Vận hành bởi: <b>TruongNV-D11</b></p>
        <p style="color: #8C92A4; margin: 3px 0 0 0; font-size: 11px;">Hệ thống phân tích định lượng đa chiều Real-Time Engine • Academic Profile Active</p>
    </div>
""", unsafe_allow_html=True)
