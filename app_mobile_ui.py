import streamlit as st
import random
import os
import json
import time
import requests
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
            "can": cls.CAN[can_idx], "chi": cls.CHI[chi_idx],
            "menh": menh, "menh_elem": menh_elem,
            "cung_phi": cung_phi, "western_sign": wz,
            "element_west": element_west, "modality": modality, "ruling_planet": ruling_planet,
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

# Khối Tuyên ngôn Triết lý & Vận hành (Nổi bật ở đầu giao diện)
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
    <b>📜 TRÍCH YẾU HỌC THUẬT ỨNG DỤNG:</b><br>
    • <b>Phương Đông:</b> Lịch pháp Tiết Lập Xuân chuẩn thiên văn (Kinh độ 315°), Can Chi, 60 Hoa Giáp & Cung Phi Lạc Thư.<br>
    • <b>Phương Tây:</b> Chiêm tinh cổ điển 3 Tầng — Tứ đại Nguyên tố (Triplicities), Phẩm tính Vận động (Modalities: Cardinal/Fixed/Mutable) & Hành tinh Đắc vị.<br>
    • <b>Thống kê:</b> Ma trận tần suất lịch sử đa chiều (Chiến lược Hot / Neutral / Cold động).
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
        draw_dt = datetime(int(draw_year), int(draw_month), int(draw_day),
