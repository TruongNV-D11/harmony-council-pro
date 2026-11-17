import streamlit as st
import random
import time
from datetime import datetime
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
        animation: fadeIn 0.5s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
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
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 📚 2. CƠ SỞ DỮ LIỆU & LÕI THAM CHIẾU PHONG THỦY CHÍNH THỐNG (LẬP XUÂN)
# =====================================================================
GAMES = {
    "5x35": {"label": "Lotto 5/35", "max_main": 35, "pick": 5},
    "6x45": {"label": "Mega 6/45", "max_main": 45, "pick": 6},
    "6x55": {"label": "Power 6/55", "max_main": 55, "pick": 6},
}

class PhongThuyReferenceCore:
    CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
    CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

    @staticmethod
    def get_solar_term_riping(year: int) -> datetime:
        solar_terms = {
            1974: datetime(1974, 2, 4, 12, 0),
            1975: datetime(1975, 2, 4, 17, 52),
            1976: datetime(1976, 2, 4, 23, 42),
            1977: datetime(1977, 2, 5, 5, 31),
            1978: datetime(1978, 2, 4, 11, 20),
            1979: datetime(1979, 2, 4, 17, 5),
            1980: datetime(1980, 2, 4, 22, 53),
            1981: datetime(1981, 2, 4, 4, 45),
            1982: datetime(1982, 2, 4, 10, 39),
            1983: datetime(1983, 2, 4, 16, 22),
            1984: datetime(1984, 2, 4, 22, 18),
            1985: datetime(1985, 2, 5, 4, 14),
            1986: datetime(1986, 2, 4, 10, 10),
            1987: datetime(1987, 2, 4, 15, 58),
            1988: datetime(1988, 2, 4, 21, 51),
            1989: datetime(1989, 2, 4, 3, 47),
            1990: datetime(1990, 2, 4, 9, 31),
            1991: datetime(1991, 2, 4, 15, 17),
            1992: datetime(1992, 2, 4, 21, 11),
            1993: datetime(1993, 2, 4, 3, 3),
            1994: datetime(1994, 2, 4, 8, 50),
            1995: datetime(1995, 2, 4, 14, 41),
            1996: datetime(1996, 2, 4, 20, 31),
            1997: datetime(1997, 2, 4, 2, 25),
            1998: datetime(1998, 2, 4, 8, 10),
            1999: datetime(1999, 2, 4, 13, 58),
            2000: datetime(2000, 2, 4, 19, 43),
        }
        return solar_terms.get(year, datetime(year, 2, 4, 12, 0))

    @classmethod
    def get_lunar_year_precise(cls, y: int, m: int, d: int) -> int:
        user_dt = datetime(y, m, d, 12, 0)
        lap_xuan = cls.get_solar_term_riping(y)
        if user_dt < lap_xuan:
            return y - 1
        return y

    NAP_AM_60 = [
        "Hải Trung Kim", "Hải Trung Kim", "Lư Trung Hỏa", "Lư Trung Hỏa", "Đại Lâm Mộc", "Đại Lâm Mộc",
        "Lộ Bàng Thổ", "Lộ Bàng Thổ", "Kiếm Phong Kim", "Kiếm Phong Kim", "Sơn Đầu Hỏa", "Sơn Đầu Hỏa",
        "Giản Hạ Thủy", "Giản Hạ Thủy", "Thành Thượng Thổ", "Thành Thượng Thổ", "Bạch Lạp Kim", "Bạch Lạp Kim",
        "Dương Liễu Mộc", "Dương Liễu Mộc", "Tuyền Trung Thủy", "Tuyền Trung Thủy", "Ốc Thượng Thổ", "Ốc Thượng Thổ",
        "Tích Lịch Hỏa", "Tích Lịch Hỏa", "Tùng Bách Mộc", "Tùng Bách Mộc", "Trường Lưu Thủy", "Trường Lưu Thủy",
        "Sa Trung Kim", "Sa Trung Kim", "Sơn Hạ Hỏa", "Sơn Hạ Hỏa", "Bình Địa Mộc", "Bình Địa Mộc",
        "Bích Thượng Thổ", "Bích Thượng Thổ", "Kim Bạch Kim", "Kim Bạch Kim", "Phúc Đăng Hỏa", "Phúc Đăng Hỏa",
        "Thiên Hà Thủy", "Thiên Hà Thủy", "Đại Trạch Thổ", "Đại Trạch Thổ", "Thoa Xuyến Kim", "Thoa Xuyến Kim",
        "Tang Đố Mộc", "Tang Đố Mộc", "Đại Khê Thủy", "Đại Khê Thủy", "Sa Trung Thổ", "Sa Trung Thổ",
        "Thiên Thượng Hỏa", "Thiên Thượng Hỏa", "Thạch Lựu Mộc", "Thạch Lựu Mộc", "Đại Hải Thủy", "Đại Hải Thủy"
    ]

    @classmethod
    def get_full_info(cls, dob_str: str, gender: str = "Nam") -> Dict[str, Any]:
        try:
            dt = datetime.strptime(dob_str, "%d/%m/%Y")
            day, month, year = dt.day, dt.month, dt.year
        except:
            day, month, year = 2, 2, 1974

        l_year = cls.get_lunar_year_precise(year, month, day)

        can = cls.CAN[(l_year - 4) % 10]
        chi = cls.CHI[(l_year - 4) % 12]

        idx_60 = (l_year - 4) % 60
        menh_full = cls.NAP_AM_60[idx_60] if 0 <= idx_60 < len(cls.NAP_AM_60) else "Bình Địa Mộc"

        if "Kim" in menh_full: menh_elem = "Kim"
        elif "Thủy" in menh_full or "Thuỷ" in menh_full: menh_elem = "Thủy"
        elif "Hỏa" in menh_full: menh_elem = "Hỏa"
        elif "Thổ" in menh_full: menh_elem = "Thổ"
        else: menh_elem = "Mộc"

        year_str = str(l_year)
        sum_digits = int(year_str[-2]) + int(year_str[-1])
        while sum_digits > 9:
            sum_digits = sum_digits // 10 + sum_digits % 10

        cung_map = {
            1: "Khảm (Thủy)", 2: "Khôn (Thổ)", 3: "Chấn (Mộc)", 
            4: "Tốn (Mộc)", 6: "Càn (Kim)", 7: "Đoài (Kim)", 
            8: "Cấn (Thổ)", 9: "Ly (Hỏa)"
        }

        g_lower = gender.lower()
        if "nam" in g_lower:
            remainder = 10 - sum_digits
            if remainder == 5: remainder = 2
            cung_menh = cung_map.get(remainder, "Cấn (Thổ)")
        elif "nữ" in g_lower or "nu" in g_lower:
            remainder = 5 + sum_digits
            while remainder > 9:
                remainder = remainder // 10 + remainder % 10
            if remainder == 5: remainder = 8
            cung_menh = cung_map.get(remainder, "Đoài (Kim)")
        else: # Không xác định / Khác (Quy về hằng số trung tính / Nam)
            remainder = 10 - sum_digits
            if remainder == 5: remainder = 2
            cung_menh = cung_map.get(remainder, "Cấn (Thổ)") + " [Trung tính/Khác]"

        western_sign = "Bảo Bình"
        if (month == 3 and day >= 21) or (month == 4 and day <= 19): western_sign = "Bạch Dương"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20): western_sign = "Kim Ngưu"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20): western_sign = "Song Tử"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22): western_sign = "Cự Giải"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22): western_sign = "Sư Tử"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22): western_sign = "Xử Nữ"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22): western_sign = "Thiên Bình"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21): western_sign = "Bọ Cạp"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21): western_sign = "Nhân Mã"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19): western_sign = "Ma Kết"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18): western_sign = "Bảo Bình"
        else: western_sign = "Song Ngư"

        return {
            "lunar_year": l_year,
            "gender": gender,
            "can": can,
            "chi": chi,
            "menh": menh_full,
            "menh_elem": menh_elem,
            "cung_menh": cung_menh,
            "western_sign": western_sign
        }

# =====================================================================
# 🌸 2B. LÕI CHUYÊN GIA HÀNH VI: MAI HOA DỊCH SỐ (STANDALONE ADVISORY)
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
            summary = f"Dụng ({dung_elem}) tương sinh/tỷ hòa với Thể ({the_elem}). Nhịp năng lượng thời điểm hanh thông, tâm lý ổn định."
            advice = "Bạn đang ở trạng thái tinh thần tỉnh táo và chủ động. Có thể cân nhắc tham gia trải nghiệm trong đúng giới hạn ngân sách giải trí tối thiểu đã hoạch định từ trước."
        elif cls.NGU_HANH_SINH.get(the_elem) == dung_elem or cls.NGU_HANH_KHAC.get(the_elem) == dung_elem:
            zone = "BINH"
            zone_label = "🟡 VÙNG BÌNH — Thời điểm trung lập & Cần tiết chế"
            summary = f"Thể ({the_elem}) sinh xuất hoặc khắc chế Dụng ({dung_elem}). Vạn vật đang ở thế cân bằng tĩnh."
            advice = "Bối cảnh hiện tại phù hợp để quan sát dữ liệu và rèn luyện kỷ luật hơn là hành động mạnh. Ưu tiên bảo toàn nguồn vốn cá nhân."
        else:
            zone = "BI"
            zone_label = "🔴 VÙNG BĨ — Cảnh báo rủi ro & Cảm xúc dễ dao động"
            summary = f"Dụng ({dung_elem}) khắc Thể ({the_elem}). Tín hiệu năng lượng cho thấy tâm lý đang nóng vội."
            advice = "KHUYẾN NGHỊ TỐI THƯỢNG: TẠM DỪNG THAM GIA! Đóng ví ngay lập tức, giữ chặt nguồn vốn và dành thời gian nghỉ ngơi."

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

# =====================================================================
# 🏛️ 3. LÕI HỘI ĐỒNG THẨM ĐỊNH ĐA CHIỀU (FLEXIBLE COUNCIL EVALUATOR)
# =====================================================================
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
        favorable = element_residue.get(menh_elem, [])
        return 1.0 if num in favorable else 0.4

    @staticmethod
    def judge_western(num: int, western_sign: str) -> float:
        ZMAP_ELEMENT = {
            "Bạch Dương": "Hỏa", "Sư Tử": "Hỏa", "Nhân Mã": "Hỏa",
            "Kim Ngưu": "Thổ", "Xử Nữ": "Thổ", "Ma Kết": "Thổ",
            "Song Tử": "Khí", "Thiên Bình": "Khí", "Bảo Bình": "Khí",
            "Cự Giải": "Thủy", "Bọ Cạp": "Thủy", "Song Ngư": "Thủy"
        }
        elem = ZMAP_ELEMENT.get(western_sign, "Khí")
        if elem == "Hỏa" and num % 3 == 0: return 1.0
        if elem == "Thổ" and num % 5 == 0: return 1.0
        if elem == "Khí" and num % 2 != 0: return 0.9
        if elem == "Thủy" and num % 2 == 0: return 0.9
        return 0.5

    @staticmethod
    def judge_statistics_hot_cold(num: int, freq_map: Dict[int, int], strategy: str) -> float:
        if not freq_map: return 0.5
        frequencies = list(freq_map.values())
        max_f = max(frequencies) if frequencies else 1
        min_f = min(frequencies) if frequencies else 0
        f = freq_map.get(num, 0)
        
        if max_f == min_f: return 0.7
        normalized = (f - min_f) / (max_f - min_f) if (max_f - min_f) > 0 else 0.5

        if "hot" in strategy.lower():
            return 0.1 + 0.9 * (f / max_f) if max_f > 0 else 0.5
        elif "cold" in strategy.lower():
            return 0.1 + 0.9 * (1.0 - normalized)
        else:
            diff = abs(normalized - 0.5)
            return max(0.2, 1.0 - (diff * 1.8))

# =====================================================================
# ⚡ 4. HỆ THỐNG CACHE LỊCH SỬ QUAY THƯỞNG (CACHED LOCAL ENGINE)
# =====================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_cached_history(game_key: str, sample_k: int):
    time.sleep(0.1)
    mock_history = []
    max_val = GAMES[game_key]["max_main"]
    pick_num = GAMES[game_key]["pick"]
    
    rnd = random.Random(42)
    for _ in range(sample_k):
        mock_history.append({
            "mains": sorted(rnd.sample(range(1, max_val + 1), pick_num))
        })
    return mock_history

# =====================================================================
# 🏛️ 5. HEADER & BANNER
# =====================================================================
st.markdown("### 🏛️ HARMONY COUNCIL PRO v2.6")
st.caption("🔒 **CACHED REAL CORE ENGINE** | Phân tích Định lượng Học thuật & Kỷ luật Hành vi")
st.divider()

# =====================================================================
# 🎵 6. TRÌNH PHÁT NHẠC NỀN (AMBIENT AUDIO)
# =====================================================================
with st.expander("🎵 Trình phát Nhạc nền & Tần số Thư giãn (Ambient Audio)", expanded=False):
    st.caption("Kích hoạt âm thanh nền tần số Alpha giúp giữ tâm thế tĩnh tại:")
    st.audio("https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf756.mp3?filename=lofi-study-112191.mp3", format="audio/mp3")

# =====================================================================
# ⚙️ 7. INPUTS & CẤU HÌNH THỊ TRƯỜNG, NĂM SINH, GIỚI TÍNH & CHIẾN LƯỢC
# =====================================================================
col1, col2 = st.columns(2)
with col1:
    market = st.selectbox("🌐 Thị trường", ["🇻🇳 Việt Nam", "🇺🇸 United States", "🇨🇳 China"])
with col2:
    if market == "🇻🇳 Việt Nam":
        game_label = st.selectbox("🎯 Trò chơi", ["Lotto 5/35", "Mega 6/45", "Power 6/55"])
        game_key = "5x35" if "5/35" in game_label else ("6x45" if "6/45" in game_label else "6x55")
    elif market == "🇺🇸 United States":
        game_label = st.selectbox("🎯 Trò chơi", ["US Powerball", "Mega Millions"])
        game_key = "6x45"
    else:
        game_label = st.selectbox("🎯 Trò chơi", ["China Super Lotto"])
        game_key = "6x45"

with st.expander("👤 Thiết lập Bản mệnh (Tiết Lập Xuân), Giới tính & Tầm nhìn", expanded=True):
    col_d, col_m, col_y = st.columns(3)
    with col_d:
        day = st.selectbox("Ngày", list(range(1, 32)), index=1)
    with col_m:
        month = st.selectbox("Tháng", list(range(1, 13)), index=1)
    with col_y:
        year = st.selectbox("Năm sinh", list(range(2026, 1939, -1)), index=36)
    
    gender = st.radio(
        "⚧ Giới tính (Phục vụ định lượng Cung Mệnh Bát Trạch chuẩn thư tịch)", 
        options=["Nam", "Nữ", "Không xác định / Khác"], 
        horizontal=True
    )

    dob_str = f"{day:02d}/{month:02d}/{year}"
    profile = PhongThuyReferenceCore.get_full_info(dob_str, gender)
    st.info(
        f"📅 Bản mệnh (Tiết Lập Xuân - Năm Âm {profile['lunar_year']}): "
        f"**{profile['can']} {profile['chi']}** — **{profile['menh']}** | "
        f"🏛️ Cung Mệnh: **{profile['cung_menh']}** | 🌟 Cung Hoàng đạo: **{profile['western_sign']}**"
    )

    st.markdown("---")
    st.markdown("📊 **Cấu hình Tầm nhìn & Khẩu vị Thống kê:**")
    horizon_samples = st.slider("🔍 Tầm nhìn mẫu (Số kỳ dữ liệu lịch sử xét duyệt)", min_value=20, max_value=500, value=100, step=10)
    
    hc_strategy = st.radio(
        "🎯 Khẩu vị Chiến lược Thống kê",
        options=["🔥 Hot (Tần suất cao - Bắt nhịp xu hướng)", "⚖️ Neutral (Trung lập
