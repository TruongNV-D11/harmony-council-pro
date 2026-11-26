"""
===============================================================================
HỘI ĐỒNG CHIÊM TINH HỌC THUẬT TIÊU CHUẨN (STANDARD ASTRONOMICAL ASTROLOGY MODULE)
Phiên bản độc lập để kiểm thử & đối chiếu trước khi tích hợp Full App.
===============================================================================

CƠ SỞ HỌC THUẬT & NGUỒN GỐC THUẬT TOÁN CHÍNH THỐNG:
1. Thời gian Thiên văn & Hệ quy chiếu (Julian Day, GMST, LST, Obliquity):
   - Jean Meeus, "Astronomical Algorithms", 2nd Ed. (Willmann-Bell, 1998),
     Chapter 7 (Julian Day), Chapter 12 (Sidereal Time at Greenwich),
     Chapter 22 (Nutation and the Obliquity of the Ecliptic).
   - IAU 1982 / IAU 2000B chuẩn góc nghiêng hoàng đạo & thời gian sao.

2. Tọa độ Hoàng đạo Địa tâm Hành tinh (Geocentric Ecliptic Longitudes):
   - Phương trình Kepler M = E - e * sin(E) giải hội tụ Newton-Raphson
     (sai số dừng |dE| < 1e-12 rad), biến đổi tọa độ nhật tâm (Heliocentric)
     sang tọa độ địa tâm (Geocentric) theo Jean Meeus (Ch. 25, 31-33) &
     E.M. Standish (JPL Planetary Ephemeris Keplerian Elements).
   - Quỹ đạo Mặt Trăng rút gọn theo chuỗi tuần hoàn ELP-2000/82
     (Jean Meeus, Ch. 47).

3. Điểm Mọc (Ascendant - AC), Trung Thiên (Midheaven - MC) & Hệ Nhà:
   - Michael Munkasey, "An Astrological House Formulary" (1994).
   - Hệ nhà Toàn Cung (Whole Sign Houses — Hellenistic Tradition, Claudius
     Ptolemy & Vettius Valens) làm chuẩn tránh suy biến ở vĩ độ cực, đồng thời
     tính chính xác điểm AC và MC trên hoàng đạo Nhiệt đới (Tropical Zodiac).

4. Tứ đại Nguyên tố, Phẩm tính & Phẩm giá Hành tinh (Essential Dignities):
   - Claudius Ptolemy, "Tetrabiblos" (Book I, Ch. 11-20).
   - William Lilly, "Christian Astrology" (1647, Book I, Table of Essential
     Dignities: Domicile/Chủ quản, Exaltation/Vượng, Detriment/Hãm, Fall/Tử).

5. Góc chiếu & Động học Tiến/Lùi (Ptolemaic Aspects & Applying/Separating):
   - Claudius Ptolemy, "Tetrabiblos" (Book I, Ch. 13: 0°, 60°, 90°, 120°, 180°).
   - Xác định vận tốc góc ngày (deg/day) bằng sai phân trung tâm tại t ± 1 giờ
     để phân định nghịch hành (Retrograde) và trạng thái tiến gần (Applying)
     hay tách xa (Separating).

6. Giờ Hành tinh (Planetary Hours — Chaldean Order):
   - Truyền thống Chiêm tinh Hellenistic & Trung cổ (Al-Biruni, "The Book of
     Instruction in the Elements of the Art of Astrology"): thứ tự Chaldean
     (Saturn -> Jupiter -> Mars -> Sun -> Venus -> Mercury -> Moon), chia
     khoảng thời gian từ Mặt Trời mọc đến Mặt Trời lặn (Meeus, Ch. 15) thành
     12 giờ ngày không đều và 12 giờ đêm không đều tại tọa độ (lat, lon).
===============================================================================
"""

import math
import re
from datetime import datetime, date, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any

# =====================================================================
# 1. DANH MỤC TỌA ĐỘ 34 TỈNH/THÀNH VIỆT NAM & PARSER TỌA ĐỘ TOÀN CẦU
# =====================================================================
VIETNAM_PROVINCES_34: Dict[str, Tuple[float, float]] = {
    "TP. Hồ Chí Minh": (10.8231, 106.6297),
    "TP. Hà Nội": (21.0285, 105.8542),
    "TP. Hải Phòng": (20.8449, 106.6881),
    "Cao Bằng": (22.6663, 106.2522),
    "Điện Biên": (21.3860, 103.0230),
    "Lai Châu": (22.3964, 103.4703),
    "Lạng Sơn": (21.8537, 106.7615),
    "Sơn La": (21.3256, 103.9188),
    "Quảng Ninh": (20.9517, 107.0448),
    "Tuyên Quang": (21.8233, 105.2142),
    "Lào Cai": (22.4809, 103.9755),
    "Thái Nguyên": (21.5942, 105.8482),
    "Phú Thọ": (21.3227, 105.4020),
    "Bắc Ninh": (21.1861, 106.0763),
    "Hưng Yên": (20.6464, 106.0511),
    "Ninh Bình": (20.2506, 105.9745),
    "Thanh Hóa": (19.8067, 105.7852),
    "Nghệ An": (18.6796, 105.6813),
    "Hà Tĩnh": (18.3559, 105.8877),
    "Quảng Trị": (16.7403, 107.1855),
    "TP. Huế": (16.4637, 107.5909),
    "TP. Đà Nẵng": (16.0544, 108.2022),
    "Quảng Ngãi": (15.1214, 108.8044),
    "Gia Lai": (13.9833, 108.0000),
    "Đắk Lắk": (12.6667, 108.0500),
    "Khánh Hòa": (12.2388, 109.1967),
    "Lâm Đồng": (11.9404, 108.4583),
    "Đồng Nai": (10.9574, 106.8426),
    "Tây Ninh": (11.3100, 106.0989),
    "Đồng Tháp": (10.4938, 105.6882),
    "An Giang": (10.3816, 105.4356),
    "Vĩnh Long": (10.2537, 105.9722),
    "TP. Cần Thơ": (10.0452, 105.7469),
    "Cà Mau": (9.1769, 105.1500),
}


def parse_pasted_coordinates(
    raw_text: str,
    fallback_lat: float,
    fallback_lon: float,
) -> Tuple[float, float, bool, str]:
    """
    Trích xuất tọa độ địa lý (latitude, longitude) từ chuỗi dán Zalo / Google Maps
    hoặc tọa độ thập phân toàn cầu. Trả về (lat, lon, is_valid_supplement, note).
    """
    if not raw_text or not raw_text.strip():
        return fallback_lat, fallback_lon, False, "Không dán tọa độ bổ sung — dùng tọa độ tỉnh/thành"

    txt = raw_text.strip()
    url_match = re.search(
        r"(?:@|q=|ll=|center=)([-+]?\d+(?:\.\d+)?)\s*,\s*([-+]?\d+(?:\.\d+)?)", txt
    )
    if url_match:
        lat_val, lon_val = float(url_match.group(1)), float(url_match.group(2))
    else:
        nums = re.findall(r"[-+]?\d+(?:\.\d+)?", txt)
        if len(nums) < 2:
            return fallback_lat, fallback_lon, False, "Tọa độ dán chưa đủ 2 số — giữ tọa độ tỉnh/thành gốc"
        lat_val, lon_val = float(nums[0]), float(nums[1])

    upper_txt = txt.upper()
    if "S" in upper_txt and "N" not in upper_txt and lat_val > 0:
        lat_val = -abs(lat_val)
    if "W" in upper_txt and "E" not in upper_txt and lon_val > 0:
        lon_val = -abs(lon_val)

    if -90.0 <= lat_val <= 90.0 and -180.0 <= lon_val <= 180.0:
        return round(lat_val, 6), round(lon_val, 6), True, "Lớp tọa độ bổ sung hợp lệ (Zalo / Toàn cầu)"

    return fallback_lat, fallback_lon, False, "Tọa độ dán ngoài biên [-90..90, -180..180] — giữ tọa độ tỉnh/thành gốc"


def compute_supplement_coord_delta(
    base_lat: float,
    base_lon: float,
    supp_lat: float,
    supp_lon: float,
    base_chart: Dict[str, Any],
    supp_chart: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Tính độ lệch không gian & sai khác góc địa phương (AC, MC, Giờ Hành tinh)
    giữa tọa độ tỉnh/thành gốc (base) và lớp tọa độ dán bổ sung (supplement).
    Dùng khoảng cách Haversine (km) để chuẩn hóa trọng số bổ sung trong [0..0.15].
    """
    r_earth_km = 6371.0
    dlat = math.radians(supp_lat - base_lat)
    dlon = math.radians(supp_lon - base_lon)
    a_hav = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(base_lat))
        * math.cos(math.radians(supp_lat))
        * math.sin(dlon / 2.0) ** 2
    )
    dist_km = 2.0 * r_earth_km * math.asin(min(1.0, math.sqrt(a_hav)))

    # Độ lệch kinh độ địa phương (LST thay đổi ~4 phút/độ kinh), ảnh hưởng AC, MC và Giờ Hành tinh
    delta_lon_deg = round(supp_lon - base_lon, 4)
    delta_lat_deg = round(supp_lat - base_lat, 4)
    lst_shift_minutes = round(delta_lon_deg * 4.0, 2)

    # Trọng số lớp bổ sung tăng dần theo khoảng cách dịch chuyển (tối đa 0.15 tại >= 150 km)
    supp_weight = round(min(0.15, (dist_km / 150.0) * 0.15), 4)

    return {
        "distance_km": round(dist_km, 2),
        "delta_lat_deg": delta_lat_deg,
        "delta_lon_deg": delta_lon_deg,
        "lst_shift_minutes": lst_shift_minutes,
        "supp_weight": supp_weight,
        "base_ac": f"{base_chart['ascendant']['sign']} ({base_chart['ascendant']['deg_in_sign']}°)",
        "supp_ac": f"{supp_chart['ascendant']['sign']} ({supp_chart['ascendant']['deg_in_sign']}°)",
        "base_mc": f"{base_chart['midheaven']['sign']} ({base_chart['midheaven']['deg_in_sign']}°)",
        "supp_mc": f"{supp_chart['midheaven']['sign']} ({supp_chart['midheaven']['deg_in_sign']}°)",
        "base_hour": f"{base_chart['planetary_hour']['phase_label']} - {base_chart['planetary_hour']['hour_ruler']}",
        "supp_hour": f"{supp_chart['planetary_hour']['phase_label']} - {supp_chart['planetary_hour']['hour_ruler']}",
    }


# =====================================================================
# 2. LÕI THIÊN VĂN & CHIÊM TINH HỌC THUẬT CHUẨN (TẦNG A — THUẦN HỌC THUẬT)
# =====================================================================
class AstronomicalAstrologyEngine:
    """
    Tầng A: Tính toán thuần túy thiên văn vị trí & chiêm tinh cổ điển tiêu chuẩn.
    Không chứa logic chia hết hay trọng số xổ số tùy biến.

    Hệ quy chiếu:
    - Hoàng đạo Nhiệt đới (Tropical Zodiac), gốc 0° Bạch Dương tại điểm Xuân phân thực.
    - Kỷ nguyên chuẩn J2000.0 (JD 2451545.0).
    - Thang thời gian: chuyển đổi giờ địa phương (kèm tz_offset_hours) -> UTC -> JD.
    """

    # 12 Cung Hoàng đạo: (Tên tiếng Việt, Tên Latin/Anh, Nguyên tố, Phẩm tính, Chủ quản cổ điển, Chủ quản hiện đại, Số thứ tự 1..12)
    ZODIAC_SIGNS: List[Tuple[str, str, str, str, str, str, int]] = [
        ("Bạch Dương", "Aries", "Hỏa", "Tiên phong (Cardinal)", "Mars", "Mars", 1),
        ("Kim Ngưu", "Taurus", "Thổ", "Kiên định (Fixed)", "Venus", "Venus", 2),
        ("Song Tử", "Gemini", "Khí", "Biến đổi (Mutable)", "Mercury", "Mercury", 3),
        ("Cự Giải", "Cancer", "Thủy", "Tiên phong (Cardinal)", "Moon", "Moon", 4),
        ("Sư Tử", "Leo", "Hỏa", "Kiên định (Fixed)", "Sun", "Sun", 5),
        ("Xử Nữ", "Virgo", "Thổ", "Biến đổi (Mutable)", "Mercury", "Mercury", 6),
        ("Thiên Bình", "Libra", "Khí", "Tiên phong (Cardinal)", "Venus", "Venus", 7),
        ("Bọ Cạp", "Scorpio", "Thủy", "Kiên định (Fixed)", "Mars", "Pluto", 8),
        ("Nhân Mã", "Sagittarius", "Hỏa", "Biến đổi (Mutable)", "Jupiter", "Jupiter", 9),
        ("Ma Kết", "Capricorn", "Thổ", "Tiên phong (Cardinal)", "Saturn", "Saturn", 10),
        ("Bảo Bình", "Aquarius", "Khí", "Kiên định (Fixed)", "Saturn", "Uranus", 11),
        ("Song Ngư", "Pisces", "Thủy", "Biến đổi (Mutable)", "Jupiter", "Neptune", 12),
    ]

    PLANET_META: Dict[str, Tuple[str, str, str]] = {
        "Sun": ("☉", "Mặt Trời (Sun)", "#FFD54F"),
        "Moon": ("☽", "Mặt Trăng (Moon)", "#E0F7FA"),
        "Mercury": ("☿", "Thủy Tinh (Mercury)", "#80CBC4"),
        "Venus": ("♀", "Kim Tinh (Venus)", "#F48FB1"),
        "Mars": ("♂", "Hỏa Tinh (Mars)", "#FF7043"),
        "Jupiter": ("♃", "Mộc Tinh (Jupiter)", "#CE93D8"),
        "Saturn": ("♄", "Thổ Tinh (Saturn)", "#90CAF9"),
    }

    # Bảng Essential Dignities cổ điển (Claudius Ptolemy - Tetrabiblos & William Lilly - Christian Astrology)
    # Chỉ số cung: 0=Aries .. 11=Pisces
    ESSENTIAL_DIGNITIES: Dict[str, Dict[str, Any]] = {
        "Sun": {"domicile": [4], "exaltation": [0], "detriment": [10], "fall": [6]},
        "Moon": {"domicile": [3], "exaltation": [1], "detriment": [9], "fall": [7]},
        "Mercury": {"domicile": [2, 5], "exaltation": [5], "detriment": [8, 11], "fall": [11]},
        "Venus": {"domicile": [1, 6], "exaltation": [11], "detriment": [0, 7], "fall": [5]},
        "Mars": {"domicile": [0, 7], "exaltation": [9], "detriment": [1, 6], "fall": [3]},
        "Jupiter": {"domicile": [8, 11], "exaltation": [3], "detriment": [2, 5], "fall": [9]},
        "Saturn": {"domicile": [9, 10], "exaltation": [6], "detriment": [3, 4], "fall": [0]},
    }

    # Thứ tự Chaldean cho Giờ Hành tinh & Ngày Hành tinh (Al-Biruni / Hellenistic)
    CHALDEAN_ORDER: List[str] = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
    # Python weekday(): 0=Monday .. 6=Sunday -> Hành tinh chủ quản ngày
    WEEKDAY_RULERS: Dict[int, str] = {
        0: "Moon",     # Thứ Hai (Dies Lunae)
        1: "Mars",     # Thứ Ba (Dies Martis)
        2: "Mercury",  # Thứ Tư (Dies Mercurii)
        3: "Jupiter",  # Thứ Năm (Dies Iovis)
        4: "Venus",    # Thứ Sáu (Dies Veneris)
        5: "Saturn",   # Thứ Bảy (Dies Saturni)
        6: "Sun",      # Chủ Nhật (Dies Solis)
    }

    @staticmethod
    def norm_deg(deg: float) -> float:
        return deg % 360.0

    @staticmethod
    def signed_angle_diff(deg_a: float, deg_b: float) -> float:
        """Hiệu góc có dấu (deg_a - deg_b) trong khoảng [-180, 180)."""
        return (deg_a - deg_b + 180.0) % 360.0 - 180.0

    @staticmethod
    def to_julian_day(dt_input: datetime, tz_offset_hours: float = 7.0) -> float:
        """
        Quy đổi thời điểm sang Julian Day (JD) chuẩn lịch Gregory.
        Tham chiếu: Jean Meeus, Astronomical Algorithms (1998), Chapter 7, Eq. (7.1).
        """
        if dt_input.tzinfo is None:
            tz_info = timezone(timedelta(hours=tz_offset_hours))
            dt_utc = dt_input.replace(tzinfo=tz_info).astimezone(timezone.utc)
        else:
            dt_utc = dt_input.astimezone(timezone.utc)

        y = dt_utc.year
        m = dt_utc.month
        d = dt_utc.day + (
            dt_utc.hour
            + dt_utc.minute / 60.0
            + dt_utc.second / 3600.0
            + dt_utc.microsecond / 3_600_000_000.0
        ) / 24.0

        if m <= 2:
            y -= 1
            m += 12
        a = y // 100
        b = 2 - a + (a // 4)
        return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5

    @classmethod
    def mean_obliquity_deg(cls, t_cent: float) -> float:
        """
        Độ nghiêng hoàng đạo trung bình ε₀ (độ) theo công thức IAU / Laskar.
        Tham chiếu: Jean Meeus, Astronomical Algorithms (1998), Chapter 22, Eq. (22.2).
        """
        arcsec = (
            84381.448
            - 46.8150 * t_cent
            - 0.00059 * (t_cent ** 2)
            + 0.001813 * (t_cent ** 3)
        )
        return arcsec / 3600.0

    @classmethod
    def nutation_in_longitude_and_obliquity_deg(cls, t_cent: float) -> Tuple[float, float]:
        """
        Chương động kinh độ Δψ và chương động độ nghiêng Δε (độ) — chuỗi IAU 1980 rút gọn chính.
        Tham chiếu: Jean Meeus, Astronomical Algorithms (1998), Chapter 22, Table 22.A.
        """
        omega = math.radians(cls.norm_deg(125.04452 - 1934.136261 * t_cent))
        l_sun = math.radians(cls.norm_deg(280.4665 + 36000.7698 * t_cent))
        l_moon = math.radians(cls.norm_deg(218.3165 + 481267.8813 * t_cent))

        d_psi_arcsec = (
            -17.20 * math.sin(omega)
            - 1.32 * math.sin(2.0 * l_sun)
            - 0.23 * math.sin(2.0 * l_moon)
            + 0.21 * math.sin(2.0 * omega)
        )
        d_eps_arcsec = (
            9.20 * math.cos(omega)
            + 0.57 * math.cos(2.0 * l_sun)
            + 0.10 * math.cos(2.0 * l_moon)
            - 0.09 * math.cos(2.0 * omega)
        )
        return d_psi_arcsec / 3600.0, d_eps_arcsec / 3600.0

    @classmethod
    def greenwich_apparent_sidereal_time_deg(cls, jd: float) -> float:
        """
        Thời gian sao biểu kiến tại Greenwich (GAST, đơn vị độ) theo IAU 1982.
        Tham chiếu: Jean Meeus, Astronomical Algorithms (1998), Chapter 12, Eq. (12.4).
        """
        t = (jd - 2451545.0) / 36525.0
        gmst = cls.norm_deg(
            280.46061837
            + 360.98564736629 * (jd - 2451545.0)
            + 0.000387933 * (t ** 2)
            - (t ** 3) / 38710000.0
        )
        d_psi, d_eps = cls.nutation_in_longitude_and_obliquity_deg(t)
        eps_true = math.radians(cls.mean_obliquity_deg(t) + d_eps)
        gast = cls.norm_deg(gmst + d_psi * math.cos(eps_true))
        return gast

    @staticmethod
    def solve_kepler_rad(mean_anomaly_rad: float, eccentricity: float) -> float:
        """
        Giải phương trình Kepler M = E - e * sin(E) bằng phương pháp lặp Newton-Raphson.
        Tham chiếu: Jean Meeus, Astronomical Algorithms (1998), Chapter 30, Eq. (30.7).
        Ngưỡng hội tụ: |ΔE| < 1e-12 radian.
        """
        m = mean_anomaly_rad % (2.0 * math.pi)
        e_anom = m if eccentricity < 0.8 else math.pi
        for _ in range(50):
            f_val = e_anom - eccentricity * math.sin(e_anom) - m
            f_der = 1.0 - eccentricity * math.cos(e_anom)
            delta = f_val / f_der
            e_anom -= delta
            if abs(delta) < 1e-12:
                break
        return e_anom

    @classmethod
    def _heliocentric_xyz_au(
        cls,
        a_au: float,
        e: float,
        inc_deg: float,
        omega_node_deg: float,
        w_peri_deg: float,
        m_deg: float,
    ) -> Tuple[float, float, float]:
        """
        Tính tọa độ nhật tâm hoàng đạo (x, y, z) đơn vị AU từ các phần tử quỹ đạo Kepler.
        Tham chiếu: Jean Meeus, Astronomical Algorithms (1998), Chapter 33, Eq. (33.7).
        """
        e_anom = cls.solve_kepler_rad(math.radians(cls.norm_deg(m_deg)), e)
        nu = 2.0 * math.atan2(
            math.sqrt(1.0 + e) * math.sin(0.5 * e_anom),
            math.sqrt(1.0 - e) * math.cos(0.5 * e_anom),
        )
        r = a_au * (1.0 - e * math.cos(e_anom))

        om = math.radians(cls.norm_deg(omega_node_deg))
        inc = math.radians(inc_deg)
        u = nu + math.radians(cls.norm_deg(w_peri_deg))

        cos_om, sin_om = math.cos(om), math.sin(om)
        cos_u, sin_u = math.cos(u), math.sin(u)
        cos_i, sin_i = math.cos(inc), math.sin(inc)

        x = r * (cos_om * cos_u - sin_om * sin_u * cos_i)
        y = r * (sin_om * cos_u + cos_om * sin_u * cos_i)
        z = r * (sin_u * sin_i)
        return x, y, z

    @classmethod
    def compute_geocentric_longitudes(cls, jd: float) -> Dict[str, float]:
        """
        Tính kinh độ hoàng đạo biểu kiến địa tâm (độ, [0..360)) cho 7 thiên thể cổ điển:
        Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn.
        Tham chiếu:
        - Sun & Earth: Jean Meeus (1998), Ch. 25.
        - Planets (Keplerian J2000 + secular rates): E.M. Standish (JPL) / Meeus Ch. 31-33.
        - Moon: Jean Meeus (1998), Ch. 47 (ELP-2000/82 truncated periodic terms).
        """
        t = (jd - 2451545.0) / 36525.0
        d_psi, _ = cls.nutation_in_longitude_and_obliquity_deg(t)

        # 1. Tọa độ Trái Đất nhật tâm (để chiếu các hành tinh từ Nhật tâm -> Địa tâm)
        e_earth = 0.016708634 - 0.000042037 * t - 0.0000001267 * (t ** 2)
        m_earth = cls.norm_deg(357.52911 + 35999.05029 * t - 0.0001537 * (t ** 2))
        l0_earth = cls.norm_deg(280.46646 + 36000.76983 * t + 0.0003032 * (t ** 2))
        e_anom_earth = cls.solve_kepler_rad(math.radians(m_earth), e_earth)
        nu_earth = 2.0 * math.atan2(
            math.sqrt(1.0 + e_earth) * math.sin(0.5 * e_anom_earth),
            math.sqrt(1.0 - e_earth) * math.cos(0.5 * e_anom_earth),
        )
        r_earth = 1.000001018 * (1.0 - e_earth * math.cos(e_anom_earth))
        lon_earth_helio = cls.norm_deg(math.degrees(nu_earth) + (l0_earth - m_earth) + 180.0)
        xe = r_earth * math.cos(math.radians(lon_earth_helio))
        ye = r_earth * math.sin(math.radians(lon_earth_helio))
        ze = 0.0

        # Kinh độ Mặt Trời biểu kiến địa tâm (hiệu chỉnh quang sai -0.00569° và chương động d_psi)
        sun_true_lon = cls.norm_deg(lon_earth_helio + 180.0)
        sun_apparent_lon = cls.norm_deg(sun_true_lon - 0.00569 + d_psi)

        # 2. Mặt Trăng (ELP-2000/82 — Jean Meeus Ch. 47)
        lp = cls.norm_deg(218.3164477 + 481267.88123421 * t - 0.0015786 * (t ** 2) + (t ** 3) / 538841.0)
        d_el = cls.norm_deg(297.8501921 + 445267.1114034 * t - 0.0018819 * (t ** 2) + (t ** 3) / 545868.0)
        m_sun = cls.norm_deg(357.5291092 + 35999.0502909 * t - 0.0001536 * (t ** 2))
        mp = cls.norm_deg(134.9633964 + 477198.8675055 * t + 0.0087414 * (t ** 2) + (t ** 3) / 69699.0)
        f_arg = cls.norm_deg(93.2720950 + 483202.0175233 * t - 0.0036539 * (t ** 2))

        e_corr = 1.0 - 0.002516 * t - 0.0000074 * (t ** 2)
        d_r, m_r, mp_r, f_r = map(math.radians, (d_el, m_sun, mp, f_arg))

        sigma_l = (
            6288774 * math.sin(mp_r)
            + 1274027 * math.sin(2 * d_r - mp_r)
            + 658314 * math.sin(2 * d_r)
            + 213618 * math.sin(2 * mp_r)
            - 185116 * e_corr * math.sin(m_r)
            - 114332 * math.sin(2 * f_r)
            + 58793 * math.sin(2 * d_r - 2 * mp_r)
            + 57066 * e_corr * math.sin(2 * d_r - m_r - mp_r)
            + 53322 * math.sin(2 * d_r + mp_r)
            + 45758 * e_corr * math.sin(2 * d_r - m_r)
            - 40923 * e_corr * math.sin(m_r - mp_r)
            - 34720 * math.sin(d_r)
            - 30383 * e_corr * math.sin(m_r + mp_r)
            + 15327 * math.sin(2 * d_r - 2 * f_r)
            - 12528 * math.sin(mp_r + 2 * f_r)
            + 10980 * math.sin(mp_r - 2 * f_r)
        )
        moon_lon = cls.norm_deg(lp + sigma_l / 1_000_000.0 + d_psi)

        # 3. Các hành tinh Thủy, Kim, Hỏa, Mộc, Thổ (Standish / Meeus J2000 elements)
        # Format: (a, e0, e_dot, i0, i_dot, om0, om_dot, w_bar0, w_bar_dot, L0, L_dot)
        planetary_elements: Dict[str, Tuple[float, ...]] = {
            "Mercury": (
                0.38709893, 0.20563069, 0.00002527,
                7.00487, -0.005947, 48.33167, -0.125340,
                77.45645, 0.160477, 252.25084, 149472.674112,
            ),
            "Venus": (
                0.72333199, 0.00677323, -0.00004938,
                3.39471, -0.000789, 76.68069, -0.277694,
                131.53298, 0.002833, 181.97973, 58517.815387,
            ),
            "Mars": (
                1.52366231, 0.09341233, 0.00011902,
                1.85061, -0.008131, 49.57854, -0.292573,
                336.04084, 0.444411, 355.45332, 19140.302685,
            ),
            "Jupiter": (
                5.20336301, 0.04839266, -0.00012880,
                1.30530, -0.001837, 100.55615, 0.204691,
                14.75385, 0.212527, 34.40438, 3034.746128,
            ),
            "Saturn": (
                9.53707032, 0.05415060, -0.00036762,
                2.48446, 0.001936, 113.71504, -0.288678,
                92.43194, -0.418972, 49.94432, 1222.493622,
            ),
        }

        longitudes: Dict[str, float] = {
            "Sun": sun_apparent_lon,
            "Moon": moon_lon,
        }

        for p_name, elems in planetary_elements.items():
            a, e0, ed, i0, idot, om0, omd, wb0, wbd, l0, ld = elems
            e = e0 + ed * t
            inc = i0 + idot * t
            om = om0 + omd * t
            w_bar = wb0 + wbd * t
            l_mean = l0 + ld * t
            w_peri = w_bar - om
            m_anom = l_mean - w_bar

            xh, yh, zh = cls._heliocentric_xyz_au(a, e, inc, om, w_peri, m_anom)
            # Chuyển từ Nhật tâm -> Địa tâm
            xg = xh - xe
            yg = yh - ye
            zg = zh - ze
            geo_lon = cls.norm_deg(math.degrees(math.atan2(yg, xg)) + d_psi)
            longitudes[p_name] = geo_lon

        return longitudes

    @classmethod
    def classify_essential_dignity(cls, planet_key: str, sign_idx: int) -> Tuple[str, int]:
        """
        Xác định phẩm giá thiết yếu (Essential Dignity) của thiên thể tại cung Hoàng đạo
        theo Claudius Ptolemy (Tetrabiblos) & William Lilly (Christian Astrology).
        Trả về: (Nhãn phẩm giá, Điểm trọng số học thuật).
        """
        rules = cls.ESSENTIAL_DIGNITIES.get(planet_key, {})
        if sign_idx in rules.get("domicile", []):
            return "Chủ quản (Domicile +5)", 5
        if sign_idx in rules.get("exaltation", []):
            return "Vượng (Exaltation +4)", 4
        if sign_idx in rules.get("detriment", []):
            return "Hãm (Detriment -5)", -5
        if sign_idx in rules.get("fall", []):
            return "Tử (Fall -4)", -4
        return "Bình hòa (Peregrine 0)", 0

    @classmethod
    def lon_to_sign_info(cls, lon_deg: float, planet_key: Optional[str] = None) -> Dict[str, Any]:
        lon_norm = cls.norm_deg(lon_deg)
        idx = int(lon_norm // 30.0) % 12
        deg_in_sign = lon_norm % 30.0
        sign_vi, sign_en, elem, mod, trad_ruler, mod_ruler, sign_num = cls.ZODIAC_SIGNS[idx]
        dignity_label, dignity_score = (
            cls.classify_essential_dignity(planet_key, idx) if planet_key else ("", 0)
        )
        return {
            "lon": round(lon_norm, 4),
            "sign_idx": idx,
            "sign_num": sign_num,
            "sign": sign_vi,
            "sign_en": sign_en,
            "element": elem,
            "modality": mod,
            "traditional_ruler": trad_ruler,
            "modern_ruler": mod_ruler,
            "deg_in_sign": round(deg_in_sign, 2),
            "dignity_label": dignity_label,
            "dignity_score": dignity_score,
        }

    @classmethod
    def compute_angles_and_whole_sign_houses(
        cls, jd: float, lat: float, lon: float
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[int, Dict[str, Any]]]:
        """
        Tính điểm Mọc (Ascendant - AC), Trung Thiên (Midheaven - MC) và 12 Nhà Toàn Cung (Whole Sign).
        Tham chiếu:
        - Jean Meeus, Astronomical Algorithms (1998), Ch. 13.
        - Michael Munkasey, An Astrological House Formulary (1994).
        - Hệ nhà Toàn Cung (Whole Sign Houses — Hellenistic Tradition).
        """
        t = (jd - 2451545.0) / 36525.0
        _, d_eps = cls.nutation_in_longitude_and_obliquity_deg(t)
        eps_rad = math.radians(cls.mean_obliquity_deg(t) + d_eps)

        gast_deg = cls.greenwich_apparent_sidereal_time_deg(jd)
        lst_deg = cls.norm_deg(gast_deg + lon)
        lst_rad = math.radians(lst_deg)

        # Trung Thiên (Midheaven - MC)
        mc_rad = math.atan2(math.sin(lst_rad), math.cos(lst_rad) * math.cos(eps_rad))
        mc_deg = cls.norm_deg(math.degrees(mc_rad))

        # Cung Mọc (Ascendant - AC) — kiểm tra giới hạn vĩ độ vòng cực
        if abs(lat) >= 66.5:
            raise ValueError(
                f"Vĩ độ {lat}° nằm trong vòng cực (|lat| >= 66.5°), điểm Mọc hoàng đạo suy biến."
            )
        lat_rad = math.radians(lat)
        y_asc = -math.cos(lst_rad)
        x_asc = math.sin(lst_rad) * math.cos(eps_rad) + math.tan(lat_rad) * math.sin(eps_rad)
        asc_deg = cls.norm_deg(math.degrees(math.atan2(y_asc, x_asc)))

        asc_info = cls.lon_to_sign_info(asc_deg)
        mc_info = cls.lon_to_sign_info(mc_deg)

        # 12 Nhà Whole Sign: Nhà 1 là trọn vẹn cung chứa Ascendant
        first_house_sign_idx = asc_info["sign_idx"]
        houses: Dict[int, Dict[str, Any]] = {}
        for h_num in range(1, 13):
            s_idx = (first_house_sign_idx + h_num - 1) % 12
            s_vi, s_en, elem, mod, trad_r, mod_r, s_num = cls.ZODIAC_SIGNS[s_idx]
            houses[h_num] = {
                "house": h_num,
                "sign_idx": s_idx,
                "sign_num": s_num,
                "sign": s_vi,
                "sign_en": s_en,
                "element": elem,
                "ruler": trad_r,
            }

        return asc_info, mc_info, houses

    @classmethod
    def compute_planetary_hour(
        cls, dt_local: datetime, lat: float, lon: float, tz_offset_hours: float = 7.0
    ) -> Dict[str, Any]:
        """
        Tính Giờ Hành tinh (Planetary Hour) theo thứ tự Chaldean và thời điểm Mặt Trời mọc/lặn thực tế.
        Tham chiếu:
        - Jean Meeus, Astronomical Algorithms (1998), Ch. 15 (Rising, Transit, Setting, h0 = -0.8333°).
        - Al-Biruni, The Book of Instruction in the Elements of the Art of Astrology (Chaldean Hours).
        """
        if dt_local.tzinfo is None:
            tz_info = timezone(timedelta(hours=tz_offset_hours))
            dt_loc = dt_local.replace(tzinfo=tz_info)
        else:
            dt_loc = dt_local

        # Tính JD tại 0h địa phương để giải bài toán Mặt Trời mọc / lặn trong ngày
        midnight_loc = dt_loc.replace(hour=0, minute=0, second=0, microsecond=0)
        jd_0h_loc = cls.to_julian_day(midnight_loc, tz_offset_hours=tz_offset_hours)
        jd_noon_loc = jd_0h_loc + 0.5

        t = (jd_noon_loc - 2451545.0) / 36525.0
        eps_rad = math.radians(cls.mean_obliquity_deg(t))
        sun_lon_noon = cls.compute_geocentric_longitudes(jd_noon_loc)["Sun"]
        sun_lon_rad = math.radians(sun_lon_noon)

        decl_rad = math.asin(math.sin(eps_rad) * math.sin(sun_lon_rad))
        ra_rad = math.atan2(math.cos(eps_rad) * math.sin(sun_lon_rad), math.cos(sun_lon_rad))
        ra_deg = cls.norm_deg(math.degrees(ra_rad))

        h0_rad = math.radians(-0.8333)
        lat_rad = math.radians(max(-65.0, min(65.0, lat)))
        cos_h = (math.sin(h0_rad) - math.sin(lat_rad) * math.sin(decl_rad)) / (
            math.cos(lat_rad) * math.cos(decl_rad)
        )
        cos_h = max(-1.0, min(1.0, cos_h))
        h_angle_deg = math.degrees(math.acos(cos_h))

        gast_0h = cls.greenwich_apparent_sidereal_time_deg(jd_0h_loc)
        transit_frac = cls.norm_deg(ra_deg - lon - gast_0h) / 360.0
        sunrise_frac = (transit_frac - h_angle_deg / 360.0) % 1.0
        sunset_frac = (transit_frac + h_angle_deg / 360.0) % 1.0

        current_frac = (
            dt_loc.hour + dt_loc.minute / 60.0 + dt_loc.second / 3600.0
        ) / 24.0

        day_ruler = cls.WEEKDAY_RULERS[dt_loc.weekday()]
        start_idx = cls.CHALDEAN_ORDER.index(day_ruler)

        if sunrise_frac <= current_frac < sunset_frac:
            is_day = True
            day_len = max(1e-6, sunset_frac - sunrise_frac)
            hour_num_0 = int(((current_frac - sunrise_frac) / day_len) * 12.0)
            hour_num_0 = max(0, min(11, hour_num_0))
            chaldean_idx = (start_idx + hour_num_0) % 7
            phase_label = f"Giờ ngày thứ {hour_num_0 + 1}/12"
        else:
            is_day = False
            night_len = max(1e-6, 1.0 - (sunset_frac - sunrise_frac))
            if current_frac >= sunset_frac:
                elapsed_night = current_frac - sunset_frac
            else:
                elapsed_night = (1.0 - sunset_frac) + current_frac
            hour_num_0 = int((elapsed_night / night_len) * 12.0)
            hour_num_0 = max(0, min(11, hour_num_0))
            chaldean_idx = (start_idx + 12 + hour_num_0) % 7
            phase_label = f"Giờ đêm thứ {hour_num_0 + 1}/12"

        hour_ruler = cls.CHALDEAN_ORDER[chaldean_idx]
        return {
            "day_ruler": day_ruler,
            "hour_ruler": hour_ruler,
            "is_day": is_day,
            "phase_label": phase_label,
        }

    @classmethod
    def compute_aspects(
        cls,
        bodies_t0: Dict[str, Dict[str, Any]],
        bodies_t1: Dict[str, Dict[str, Any]],
        dt_hours: float = 1.0,
    ) -> List[Dict[str, Any]]:
        """
        Tính các góc chiếu Ptolemaic chuẩn (0°, 60°, 90°, 120°, 180°) kèm động học
        Applying (tiến gần) / Separating (tách xa) bằng sai phân tại t0 + dt_hours.
        Tham chiếu: Claudius Ptolemy, Tetrabiblos (Book I, Ch. 13).
        """
        aspect_defs = [
            (0.0, "Trùng tụ (Conjunction 0°)", "Hợp nhất"),
            (60.0, "Lục hợp (Sextile 60°)", "Thuận hòa"),
            (90.0, "Vuông góc (Square 90°)", "Xung lực"),
            (120.0, "Tam hợp (Trine 120°)", "Hanh thông"),
            (180.0, "Đối đỉnh (Opposition 180°)", "Đối cực"),
        ]
        # Orb phân tầng chuẩn: Luminaries (Sun/Moon) rộng hơn hành tinh
        luminaries = {"Sun", "Moon"}
        keys = list(bodies_t0.keys())
        aspects: List[Dict[str, Any]] = []

        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                k1, k2 = keys[i], keys[j]
                max_orb = 8.0 if (k1 in luminaries or k2 in luminaries) else 6.0

                diff0 = abs(cls.signed_angle_diff(bodies_t0[k1]["lon"], bodies_t0[k2]["lon"]))
                diff1 = abs(cls.signed_angle_diff(bodies_t1[k1]["lon"], bodies_t1[k2]["lon"]))

                for target_ang, asp_label, nature in aspect_defs:
                    orb0 = abs(diff0 - target_ang)
                    if orb0 <= max_orb:
                        orb1 = abs(diff1 - target_ang)
                        motion = "Applying (Tiến gần)" if orb1 < orb0 else "Separating (Tách xa)"
                        aspects.append({
                            "p1_key": k1,
                            "p2_key": k2,
                            "p1": cls.PLANET_META[k1][1],
                            "p2": cls.PLANET_META[k2][1],
                            "aspect": asp_label,
                            "nature": nature,
                            "orb": round(orb0, 2),
                            "max_orb": max_orb,
                            "motion": motion,
                        })
                        break

        # Sắp xếp ưu tiên góc chiếu chính xác nhất (orb nhỏ nhất lên đầu)
        aspects.sort(key=lambda a: a["orb"])
        return aspects

    @classmethod
    def compute_chart(
        cls,
        dt_local: datetime,
        lat: float,
        lon: float,
        tz_offset_hours: float = 7.0,
        chart_type: str = "TRANSIT",
    ) -> Dict[str, Any]:
        """
        Lập bản đồ sao thiên văn hoàn chỉnh (Transit/Event Chart hoặc Natal Chart).
        """
        jd = cls.to_julian_day(dt_local, tz_offset_hours=tz_offset_hours)
        dt_step_hours = 1.0
        jd_next = jd + (dt_step_hours / 24.0)

        lons_t0 = cls.compute_geocentric_longitudes(jd)
        lons_t1 = cls.compute_geocentric_longitudes(jd_next)

        asc_info, mc_info, houses = cls.compute_angles_and_whole_sign_houses(jd, lat, lon)
        first_house_sign_idx = asc_info["sign_idx"]

        bodies_t0: Dict[str, Dict[str, Any]] = {}
        bodies_t1: Dict[str, Dict[str, Any]] = {}

        for p_key, lon0 in lons_t0.items():
            lon1 = lons_t1[p_key]
            speed_deg_per_day = cls.signed_angle_diff(lon1, lon0) * (24.0 / dt_step_hours)
            info0 = cls.lon_to_sign_info(lon0, planet_key=p_key)
            house_num = ((info0["sign_idx"] - first_house_sign_idx) % 12) + 1
            info0["speed_deg_day"] = round(speed_deg_per_day, 4)
            info0["is_retrograde"] = bool(speed_deg_per_day < 0.0 and p_key not in ("Sun", "Moon"))
            info0["house"] = house_num
            bodies_t0[p_key] = info0
            bodies_t1[p_key] = cls.lon_to_sign_info(lon1)

        aspects = cls.compute_aspects(bodies_t0, bodies_t1, dt_hours=dt_step_hours)
        planetary_hour = cls.compute_planetary_hour(dt_local, lat, lon, tz_offset_hours=tz_offset_hours)

        return {
            "chart_type": chart_type,
            "datetime_str": dt_local.strftime("%d/%m/%Y %H:%M"),
            "tz_offset_hours": tz_offset_hours,
            "jd": round(jd, 6),
            "lat": lat,
            "lon": lon,
            "house_system": "Whole Sign Houses (Hellenistic / Ptolemy)",
            "zodiac_system": "Tropical Zodiac (0° Aries Vernal Equinox)",
            "ascendant": asc_info,
            "midheaven": mc_info,
            "houses": houses,
            "bodies": bodies_t0,
            "aspects": aspects,
            "planetary_hour": planetary_hour,
        }

    @classmethod
    def render_chart_figure(cls, chart_data: Dict[str, Any], highlight_sign: str = ""):
        """
        Vẽ bản đồ sao 360° chuẩn Hoàng đạo Nhiệt đới bằng matplotlib,
        tự động chống chồng lấn nhãn khi các hành tinh nằm gần nhau.
        Ném ImportError rõ ràng nếu môi trường thiếu matplotlib để lớp UI fallback.
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.patches import Wedge, Circle
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Thiếu thư viện 'matplotlib' trong môi trường chạy. "
                "Hãy thêm 'matplotlib' vào requirements.txt trên Streamlit Cloud."
            ) from exc

        fig, ax = plt.subplots(figsize=(6.4, 6.4), dpi=135)
        fig.patch.set_facecolor("#0E1117")
        ax.set_facecolor("#0E1117")
        ax.set_xlim(-1.38, 1.38)
        ax.set_ylim(-1.38, 1.38)
        ax.set_aspect("equal")
        ax.axis("off")

        elem_colors = {
            "Hỏa": "#3B1818",
            "Thổ": "#2A2416",
            "Khí": "#162636",
            "Thủy": "#142B29",
        }

        for idx in range(12):
            start_deg = idx * 30.0
            end_deg = (idx + 1) * 30.0
            s_vi, _, elem, _, _, _, _ = cls.ZODIAC_SIGNS[idx]
            face_col = elem_colors.get(elem, "#1A1C23")
            is_hl = s_vi == highlight_sign
            edge_col = "#FFD700" if is_hl else "#3A3F52"
            lw = 2.0 if is_hl else 0.9

            wedge = Wedge(
                (0, 0), 1.05, start_deg, end_deg, width=0.22,
                facecolor=face_col, edgecolor=edge_col, linewidth=lw
            )
            ax.add_patch(wedge)

            mid_rad = math.radians(start_deg + 15.0)
            tx = 0.94 * math.cos(mid_rad)
            ty = 0.94 * math.sin(mid_rad)
            label_txt = s_vi[:6] + ("★" if is_hl else "")
            ax.text(
                tx, ty, label_txt, color="#E5E7EB", fontsize=7.5,
                ha="center", va="center", fontweight="bold"
            )

        ax.add_patch(Circle((0, 0), 0.83, facecolor="#12151E", edgecolor="#2E3446", linewidth=1.0))
        ax.add_patch(Circle((0, 0), 0.46, facecolor="#0E1117", edgecolor="#1D976C", linewidth=1.0, linestyle="--"))

        # Trục Ascendant (AC) & Midheaven (MC)
        asc_lon = chart_data["ascendant"]["lon"]
        asc_rad = math.radians(asc_lon)
        ax.plot([0, 1.05 * math.cos(asc_rad)], [0, 1.05 * math.sin(asc_rad)], color="#00E676", linestyle=":", linewidth=1.3)
        ax.text(1.17 * math.cos(asc_rad), 1.17 * math.sin(asc_rad), "AC", color="#00E676", fontsize=8.5, ha="center", va="center", fontweight="bold")

        mc_lon = chart_data["midheaven"]["lon"]
        mc_rad = math.radians(mc_lon)
        ax.plot([0, 1.05 * math.cos(mc_rad)], [0, 1.05 * math.sin(mc_rad)], color="#FFD54F", linestyle=":", linewidth=1.1)
        ax.text(1.17 * math.cos(mc_rad), 1.17 * math.sin(mc_rad), "MC", color="#FFD54F", fontsize=8.5, ha="center", va="center", fontweight="bold")

        # Sắp xếp thiên thể theo kinh độ và phân tầng bán kính động để chống trùng chữ
        sorted_bodies = sorted(
            chart_data["bodies"].items(), key=lambda kv: kv[1]["lon"]
        )
        placed_angles: List[float] = []
        radius_tiers = [0.73, 0.62, 0.52, 0.77]

        for p_key, b_info in sorted_bodies:
            sym, _, col = cls.PLANET_META[p_key]
            lon_deg = b_info["lon"]
            ang_rad = math.radians(lon_deg)

            # Đếm số thiên thể đã đặt trong vùng lân cận ±12°
            crowd = sum(
                1 for prev_ang in placed_angles
                if abs(cls.signed_angle_diff(lon_deg, prev_ang)) < 12.0
            )
            placed_angles.append(lon_deg)
            r = radius_tiers[crowd % len(radius_tiers)]

            px = r * math.cos(ang_rad)
            py = r * math.sin(ang_rad)
            ax.scatter([px], [py], color=col, s=52, zorder=5, edgecolors="#000000", linewidth=0.6)

            rx_tag = "R" if b_info.get("is_retrograde") else ""
            lx = (r + 0.065) * math.cos(ang_rad)
            ly = (r + 0.065) * math.sin(ang_rad)
            ax.text(
                lx, ly, f"{sym}{b_info['deg_in_sign']:.0f}°{rx_tag}",
                color=col, fontsize=7.4, ha="center", va="center", fontweight="bold", zorder=6
            )

        ax.text(0, 0.06, f"{chart_data['chart_type']} CHART", color="#FFD700", fontsize=8.8, ha="center", va="center", fontweight="bold")
        ax.text(0, -0.06, f"{chart_data['lat']:.2f}, {chart_data['lon']:.2f}", color="#9CA3AF", fontsize=7.3, ha="center", va="center")
        plt.tight_layout(pad=0.2)
        return fig


# =====================================================================
# 3. MÔ HÌNH ÁNH XẠ ĐỊNH LƯỢNG CHO HỘI ĐỒNG PHƯƠNG TÂY (TẦNG B)
# =====================================================================
class WesternCouncilEvaluator:
    """
    Tầng B: Mô hình tham số hóa của ứng dụng quy đổi các đại lượng thiên văn &
    chiêm tinh học chuẩn ở Tầng A sang điểm tương hợp chuẩn hóa [0.0, 1.0] cho tập số
    ứng viên {1..max_main}.

    Nguyên tắc minh bạch học thuật:
    1. Không dùng mẹo chia hết tùy tiện (như num % 3, num % 7).
    2. Mỗi số nguyên n ∈ {1..max_main} được ánh xạ tuyến tính thành tâm cung độ trên
       vòng tròn Hoàng đạo 360°:
           theta(n) = ((n - 0.5) / max_main) * 360.0  (độ)
       qua đó xác định chính xác cung Hoàng đạo & Nhà Whole Sign tương ứng của số n.
    3. Điểm số được tổng hợp tuyến tính từ 4 tiêu chí chuẩn của Chiêm tinh học cổ điển:
       - Tương hợp Nguyên tố (Triplicity Harmony: cùng nguyên tố = 1.0, tương hỗ Khí-Hỏa / Thổ-Thủy = 0.75, khác = 0.40).
       - Tương hợp Phẩm tính (Modality Resonance: cùng phẩm tính Cardinal/Fixed/Mutable = 1.0, khác = 0.50).
       - Cộng hưởng Góc chiếu Hoàng đạo (Ptolemaic Aspect Proximity tới các thiên thể chủ chốt:
         Sun, Moon, Chủ quản lá số, Chủ quản Giờ Hành tinh — có xét Essential Dignity & Retrograde).
       - Đối chiếu Natal Chart (chỉ kích hoạt khi có giờ sinh chính xác; khi bỏ trống giờ sinh
         sẽ lược bỏ hoàn toàn và tự tái chuẩn hóa trọng số về tổng = 1.0).
    """

    COMPATIBLE_ELEMENTS: Dict[str, str] = {
        "Hỏa": "Khí",
        "Khí": "Hỏa",
        "Thổ": "Thủy",
        "Thủy": "Thổ",
    }

    @staticmethod
    def map_number_to_ecliptic_deg(num: int, max_main: int) -> float:
        """Ánh xạ tuyến tính số nguyên num ∈ [1..max_main] lên vòng tròn Hoàng đạo [0..360°)."""
        return (((num - 0.5) / float(max_main)) * 360.0) % 360.0

    @classmethod
    def _element_harmony(cls, elem_a: str, elem_b: str) -> float:
        if elem_a == elem_b:
            return 1.0
        if cls.COMPATIBLE_ELEMENTS.get(elem_a) == elem_b:
            return 0.75
        return 0.40

    @classmethod
    def _aspect_resonance_to_bodies(
        cls,
        target_deg: float,
        bodies: Dict[str, Dict[str, Any]],
        weighted_planets: Dict[str, float],
    ) -> float:
        """
        Đo độ cộng hưởng góc chiếu Ptolemaic (0°, 60°, 120° thuận; 90°, 180° căng thẳng)
        giữa tọa độ hoàng đạo của số n và các thiên thể đang vận hành.
        """
        benefic_angles = (0.0, 60.0, 120.0)
        hard_angles = (90.0, 180.0)
        orb_window = 6.0

        total_w = 0.0
        acc_score = 0.0
        for p_key, base_w in weighted_planets.items():
            b_info = bodies.get(p_key)
            if not b_info:
                continue
            # Điều chỉnh trọng số thiên thể theo Essential Dignity & trạng thái nghịch hành
            dignity_factor = 1.0 + (b_info.get("dignity_score", 0) * 0.04)
            rx_factor = 0.90 if b_info.get("is_retrograde") else 1.0
            eff_w = max(0.1, base_w * dignity_factor * rx_factor)

            diff = abs(AstronomicalAstrologyEngine.signed_angle_diff(target_deg, b_info["lon"]))
            hit_score = 0.50
            for ang in benefic_angles:
                d = abs(diff - ang)
                if d <= orb_window:
                    hit_score = max(hit_score, 0.75 + 0.25 * (1.0 - d / orb_window))
            for ang in hard_angles:
                d = abs(diff - ang)
                if d <= orb_window:
                    hit_score = min(hit_score, 0.45 - 0.15 * (1.0 - d / orb_window))

            acc_score += eff_w * hit_score
            total_w += eff_w

        return (acc_score / total_w) if total_w > 0 else 0.55

    @classmethod
    def evaluate_candidate(
        cls,
        num: int,
        max_main: int,
        natal_sun_sign_info: Dict[str, Any],
        transit_chart: Dict[str, Any],
        natal_chart: Optional[Dict[str, Any]] = None,
        supplement_chart: Optional[Dict[str, Any]] = None,
        supp_weight: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Chấm điểm chi tiết cho 1 ứng viên số `num` và trả kèm giải trình học thuật.
        """
        num_deg = cls.map_number_to_ecliptic_deg(num, max_main)
        num_sign_info = AstronomicalAstrologyEngine.lon_to_sign_info(num_deg)

        # 1. Tương hợp Nguyên tố (Triplicity) với Cung Mặt Trời & Mặt Trăng Transit
        s_elem_sun = cls._element_harmony(num_sign_info["element"], natal_sun_sign_info["element"])
        transit_moon_elem = transit_chart["bodies"]["Moon"]["element"]
        s_elem_moon = cls._element_harmony(num_sign_info["element"], transit_moon_elem)
        score_triplicity = 0.60 * s_elem_sun + 0.40 * s_elem_moon

        # 2. Tương hợp Phẩm tính (Modality) với Cung Mặt Trời & Cung Mọc Transit
        s_mod_sun = 1.0 if num_sign_info["modality"] == natal_sun_sign_info["modality"] else 0.50
        s_mod_asc = 1.0 if num_sign_info["modality"] == transit_chart["ascendant"]["modality"] else 0.55
        score_modality = 0.60 * s_mod_sun + 0.40 * s_mod_asc

        # 3. Cộng hưởng Góc chiếu Transit & Giờ Hành tinh Chaldean
        sun_ruler = natal_sun_sign_info["traditional_ruler"]
        hour_ruler = transit_chart["planetary_hour"]["hour_ruler"]
        transit_weights = {
            "Sun": 1.0,
            "Moon": 1.2,
            "Jupiter": 0.9,
            "Venus": 0.8,
            "Mercury": 0.6,
            "Mars": 0.6,
            "Saturn": 0.6,
        }
        if sun_ruler in transit_weights:
            transit_weights[sun_ruler] += 0.5
        if hour_ruler in transit_weights:
            transit_weights[hour_ruler] += 0.4

        score_transit_aspects = cls._aspect_resonance_to_bodies(
            num_deg, transit_chart["bodies"], transit_weights
        )

        # 4. Đối chiếu Natal Chart (chỉ kích hoạt khi có giờ sinh thực tế)
        if natal_chart and natal_chart.get("bodies"):
            natal_weights = {"Sun": 1.1, "Moon": 1.2, sun_ruler: 1.0}
            s_natal_aspects = cls._aspect_resonance_to_bodies(
                num_deg, natal_chart["bodies"], natal_weights
            )
            natal_ac_elem = natal_chart["ascendant"]["element"]
            s_natal_ac = cls._element_harmony(num_sign_info["element"], natal_ac_elem)
            score_natal = 0.60 * s_natal_aspects + 0.40 * s_natal_ac

            final_score = (
                0.30 * score_triplicity
                + 0.20 * score_modality
                + 0.28 * score_transit_aspects
                + 0.22 * score_natal
            )
        else:
            score_natal = None
            # Tái chuẩn hóa trọng số khi lược bỏ lớp giờ sinh
            final_score = (
                0.38 * score_triplicity
                + 0.25 * score_modality
                + 0.37 * score_transit_aspects
            )

        # 5. Lớp tọa độ dán bổ sung (chỉ kích hoạt khi có tọa độ dán hợp lệ & supplement_chart)
        score_supplement: Optional[float] = None
        if supplement_chart and supp_weight > 0.0:
            w_clamped = max(0.0, min(0.20, float(supp_weight)))
            supp_mod = 1.0 if num_sign_info["modality"] == supplement_chart["ascendant"]["modality"] else 0.55
            supp_hour_ruler = supplement_chart["planetary_hour"]["hour_ruler"]
            supp_p_weights = {
                "Sun": 1.0,
                "Moon": 1.2,
                "Jupiter": 0.9,
                "Venus": 0.8,
                supp_hour_ruler: 1.3,
            }
            supp_asp = cls._aspect_resonance_to_bodies(
                num_deg, supplement_chart["bodies"], supp_p_weights
            )
            score_supplement = 0.50 * supp_mod + 0.50 * supp_asp
            final_score = (1.0 - w_clamped) * final_score + w_clamped * score_supplement

        return {
            "num": num,
            "ecliptic_deg": round(num_deg, 2),
            "mapped_sign": num_sign_info["sign"],
            "mapped_element": num_sign_info["element"],
            "mapped_modality": num_sign_info["modality"],
            "score_triplicity": round(score_triplicity, 4),
            "score_modality": round(score_modality, 4),
            "score_transit_aspects": round(score_transit_aspects, 4),
            "score_natal": round(score_natal, 4) if score_natal is not None else None,
            "score_supplement": round(score_supplement, 4) if score_supplement is not None else None,
            "final_score": round(final_score, 4),
        }


# =====================================================================
# 4. GIAO DIỆN KIỂM THỬ ĐỘC LẬP HỘI ĐỒNG CHIÊM TINH (STANDALONE TEST UI)
# =====================================================================
def run_standalone_astrology_test():
    import streamlit as st

    st.set_page_config(
        page_title="Kiểm thử Hội đồng Chiêm Tinh Tiêu chuẩn",
        page_icon="🌌",
        layout="centered",
    )

    st.markdown("## 🌌 Kiểm thử Độc lập: Hội đồng Chiêm Tinh Học thuật Tiêu chuẩn")
    st.caption(
        "Mô-đun tách rời để kiểm định công thức Thiên văn vị trí (Meeus / JPL / IAU) & "
        "Chiêm tinh cổ điển (Ptolemy / Lilly / Al-Biruni) trước khi hợp nhất vào Full App."
    )

    with st.expander("📖 Cơ sở Học thuật & Quy chuẩn Áp dụng trong Mã nguồn", expanded=False):
        st.markdown("""
        1. **Thời gian Thiên văn (`to_julian_day`, `greenwich_apparent_sidereal_time_deg`):** Quy đổi lịch Gregory sang Julian Day, tính thế kỷ Julian $T$, độ nghiêng hoàng đạo trung bình $\varepsilon_0$ và chương động $(\Delta\psi, \Delta\varepsilon)$ theo *Jean Meeus — Astronomical Algorithms (1998), Ch. 7, 12, 22*.
        2. **Tọa độ Hành tinh Địa tâm (`solve_kepler_rad`, `compute_geocentric_longitudes`):** Giải phương trình Kepler $M = E - e\sin E$ bằng lặp Newton-Raphson ($|\Delta E| < 10^{-12}\text{ rad}$), biến đổi tọa độ Nhật tâm sang Địa tâm theo *Standish (JPL)* & *Meeus (Ch. 25, 31–33)*; Mặt Trăng tính theo chuỗi tuần hoàn *ELP-2000/82 (Meeus Ch. 47)*.
        3. **Điểm Mọc (AC), Trung Thiên (MC) & Hệ Nhà Toàn Cung (`compute_angles_and_whole_sign_houses`):** Tính góc hoàng đạo chuẩn theo *Munkasey (1994)* & hệ nhà *Whole Sign* cổ điển, có kiểm tra giới hạn vòng cực ($|\varphi| < 66.5^\circ$).
        4. **Phẩm giá Thiết yếu & Giờ Hành tinh (`classify_essential_dignity`, `compute_planetary_hour`):** Áp dụng bảng *Essential Dignities* của *Claudius Ptolemy (Tetrabiblos)* & *William Lilly (Christian Astrology)*, cùng *Giờ Hành tinh Chaldean* tính từ thời điểm Mặt Trời mọc/lặn thực tế tại tọa độ quan sát (*Meeus Ch. 15* & *Al-Biruni*).
        5. **Góc chiếu Động học (`compute_aspects`):** Phân định *Applying (tiến gần)* và *Separating (tách xa)* bằng sai phân tại $t_0 + 1\text{ giờ}$, kèm phát hiện hành tinh nghịch hành (*Retrograde*).
        6. **Tách bạch Mô hình Ánh xạ (`WesternCouncilEvaluator`):** Ánh xạ tuyến tính số $n \in \{1..N_{\max}\}$ lên vòng tròn Hoàng đạo $360^\circ$ qua $\theta(n) = \frac{n - 0.5}{N_{\max}} \times 360^\circ$, loại bỏ hoàn toàn các quy tắc chia hết tùy tiện.
        """)

    col1, col2, col3 = st.columns(3)
    with col1:
        bday = st.selectbox("Ngày sinh", list(range(1, 32)), index=1)
    with col2:
        bmonth = st.selectbox("Tháng sinh", list(range(1, 13)), index=1)
    with col3:
        byear = st.selectbox("Năm sinh", list(range(2026, 1939, -1)), index=52)

    birth_time_mode = st.radio(
        "Chế độ giờ sinh (Natal Chart)",
        ["Không rõ / Bỏ trống (Chỉ dùng Transit Chart & Cung Mặt Trời)", "Có giờ sinh chính xác (Bật đầy đủ Natal Chart)"],
        horizontal=True,
    )
    if birth_time_mode.startswith("Có giờ sinh"):
        cb1, cb2 = st.columns(2)
        with cb1:
            bhour = st.selectbox("Giờ sinh (0-23)", list(range(0, 24)), index=12)
        with cb2:
            bminute = st.selectbox("Phút sinh (0-59)", list(range(0, 60)), index=0)
        has_birth_time = True
    else:
        bhour, bminute = 12, 0
        has_birth_time = False

    st.markdown("---")
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)
    now_local = datetime.now(timezone(timedelta(hours=7)))
    with col_d1:
        draw_day = st.selectbox("Ngày quay", list(range(1, 32)), index=now_local.day - 1)
    with col_d2:
        draw_month = st.selectbox("Tháng quay", list(range(1, 13)), index=now_local.month - 1)
    with col_d3:
        draw_year = st.number_input("Năm quay", value=now_local.year, min_value=2000, max_value=2100)
    with col_d4:
        draw_hour = st.selectbox("Giờ quay", [13, 18, 21], index=1)

    tz_offset = st.number_input("Múi giờ địa phương (UTC+)", value=7.0, min_value=-12.0, max_value=14.0, step=0.5)
    province_names = list(VIETNAM_PROVINCES_34.keys())
    selected_province = st.selectbox("Tỉnh / Thành phố quan sát", province_names, index=0)
    pasted_coords = st.text_input(
        "Dán tọa độ toàn cầu / Zalo (tùy chọn)",
        value="",
        placeholder="Ví dụ: 10.8231, 106.6297 hoặc link @lat,lon",
    )
    fb_lat, fb_lon = VIETNAM_PROVINCES_34[selected_province]
    supp_lat, supp_lon, is_supp_valid, coord_note = parse_pasted_coordinates(pasted_coords, fb_lat, fb_lon)
    if is_supp_valid:
        st.caption(
            f"📍 Tọa độ gốc ({selected_province}): `({fb_lat}, {fb_lon})` | "
            f"➕ Lớp bổ sung: `({supp_lat}, {supp_lon})` — *{coord_note}*"
        )
    else:
        st.caption(f"📍 Tọa độ gốc ({selected_province}): `({fb_lat}, {fb_lon})` — *{coord_note}*")

    game_choice = st.selectbox(
        "Dải số trò chơi kiểm thử",
        ["5x35 (1..35)", "6x45 (1..45)", "6x55 (1..55)"],
        index=1,
    )
    max_main = int(game_choice.split("x")[1].split(" ")[0])

    if st.button("🔬 Chạy Kiểm định Chiêm Tinh Tiêu chuẩn"):
        tz_info = timezone(timedelta(hours=float(tz_offset)))
        draw_dt = datetime(int(draw_year), int(draw_month), int(draw_day), int(draw_hour), 0, tzinfo=tz_info)

        # Tính Cung Mặt Trời lúc sinh (tại 12h trưa địa phương nếu không có giờ sinh)
        birth_dt_ref = datetime(int(byear), int(bmonth), int(bday), int(bhour), int(bminute), tzinfo=tz_info)
        jd_birth = AstronomicalAstrologyEngine.to_julian_day(birth_dt_ref, tz_offset_hours=float(tz_offset))
        sun_lon_birth = AstronomicalAstrologyEngine.compute_geocentric_longitudes(jd_birth)["Sun"]
        natal_sun_info = AstronomicalAstrologyEngine.lon_to_sign_info(sun_lon_birth, planet_key="Sun")

        # Tọa độ chính dùng cho biểu đồ & góc địa phương: ưu tiên tọa độ bổ sung hợp lệ, mặc định dùng tỉnh/thành
        active_lat, active_lon = (supp_lat, supp_lon) if is_supp_valid else (fb_lat, fb_lon)

        base_chart = AstronomicalAstrologyEngine.compute_chart(
            draw_dt, fb_lat, fb_lon, tz_offset_hours=float(tz_offset), chart_type="BASE_CITY"
        )
        if is_supp_valid:
            supp_chart = AstronomicalAstrologyEngine.compute_chart(
                draw_dt, supp_lat, supp_lon, tz_offset_hours=float(tz_offset), chart_type="SUPP_COORD"
            )
            coord_delta = compute_supplement_coord_delta(
                fb_lat, fb_lon, supp_lat, supp_lon, base_chart, supp_chart
            )
            transit_chart = supp_chart
        else:
            supp_chart = None
            coord_delta = None
            transit_chart = base_chart

        natal_chart = (
            AstronomicalAstrologyEngine.compute_chart(
                birth_dt_ref, active_lat, active_lon, tz_offset_hours=float(tz_offset), chart_type="NATAL"
            )
            if has_birth_time
            else None
        )

        st.success(
            f"☀️ **Cung Mặt Trời bản mệnh (tính trực tiếp từ kinh độ Mặt Trời):** "
            f"{natal_sun_info['sign']} ({natal_sun_info['deg_in_sign']}°) — "
            f"Nguyên tố **{natal_sun_info['element']}** | Phẩm tính **{natal_sun_info['modality']}** | "
            f"Chủ quản cổ điển: **{natal_sun_info['traditional_ruler']}**"
        )

        ph = transit_chart["planetary_hour"]
        st.info(
            f"⏳ **Giờ Hành tinh Chaldean lúc quay:** Ngày chủ quản **{ph['day_ruler']}** • "
            f"{ph['phase_label']} thuộc quyền **{ph['hour_ruler']}** | "
            f"🌅 **AC:** {transit_chart['ascendant']['sign']} ({transit_chart['ascendant']['deg_in_sign']}°) | "
            f"🏔️ **MC:** {transit_chart['midheaven']['sign']} ({transit_chart['midheaven']['deg_in_sign']}°)"
        )

        st.markdown("### 🪐 Bảng Tọa độ Thiên thể & Phẩm giá Thiết yếu lúc quay")
        planet_rows = []
        for p_key, b_info in transit_chart["bodies"].items():
            planet_rows.append({
                "Thiên thể": AstronomicalAstrologyEngine.PLANET_META[p_key][1],
                "Cung Hoàng đạo": f"{b_info['sign']} ({b_info['deg_in_sign']}°)",
                "Kinh độ thực": f"{b_info['lon']}°",
                "Nhà (Whole Sign)": f"Nhà {b_info['house']}",
                "Vận tốc (°/ngày)": b_info["speed_deg_day"],
                "Trạng thái": "Nghịch hành (Rx)" if b_info["is_retrograde"] else "Thuận hành",
                "Phẩm giá (Essential Dignity)": b_info["dignity_label"],
            })
        st.dataframe(planet_rows, use_container_width=True)

        st.markdown("### 📐 Các Góc chiếu Ptolemaic (Sắp xếp theo độ chính xác Orb)")
        if transit_chart["aspects"]:
            asp_rows = [
                {
                    "Thiên thể 1": a["p1"],
                    "Thiên thể 2": a["p2"],
                    "Góc chiếu": a["aspect"],
                    "Tính chất": a["nature"],
                    "Sai số (Orb)": f"{a['orb']}° / {a['max_orb']}°",
                    "Động học": a["motion"],
                }
                for a in transit_chart["aspects"]
            ]
            st.dataframe(asp_rows, use_container_width=True)
        else:
            st.write("Không có góc chiếu chính trong biên độ orb tại thời điểm này.")

        st.markdown("### 🎡 Bản đồ sao Hoàng đạo 360° (Transit Chart)")
        try:
            fig = AstronomicalAstrologyEngine.render_chart_figure(
                transit_chart, highlight_sign=natal_sun_info["sign"]
            )
            st.pyplot(fig, use_container_width=True)
        except ModuleNotFoundError:
            st.warning(
                "Môi trường hiện tại chưa cài `matplotlib` nên chưa vẽ biểu đồ matplotlib. "
                "Hãy thêm `matplotlib` vào `requirements.txt` rồi reboot app trên Streamlit Cloud."
            )
            chart_summary_rows = [
                {
                    "Điểm / Thiên thể": "Ascendant (AC)",
                    "Kinh độ": f"{transit_chart['ascendant']['lon']}°",
                    "Cung": f"{transit_chart['ascendant']['sign']} ({transit_chart['ascendant']['deg_in_sign']}°)",
                    "Nhà": "Nhà 1 (Whole Sign)",
                },
                {
                    "Điểm / Thiên thể": "Midheaven (MC)",
                    "Kinh độ": f"{transit_chart['midheaven']['lon']}°",
                    "Cung": f"{transit_chart['midheaven']['sign']} ({transit_chart['midheaven']['deg_in_sign']}°)",
                    "Nhà": f"Nhà {transit_chart['midheaven']['sign_idx'] - transit_chart['ascendant']['sign_idx'] + 1 if False else ((transit_chart['midheaven']['sign_idx'] - transit_chart['ascendant']['sign_idx']) % 12) + 1}",
                },
            ]
            for p_key, b_info in transit_chart["bodies"].items():
                chart_summary_rows.append({
                    "Điểm / Thiên thể": AstronomicalAstrologyEngine.PLANET_META[p_key][1],
                    "Kinh độ": f"{b_info['lon']}°",
                    "Cung": f"{b_info['sign']} ({b_info['deg_in_sign']}°)",
                    "Nhà": f"Nhà {b_info['house']}",
                })
            st.dataframe(chart_summary_rows, use_container_width=True)

        if coord_delta is not None:
            st.markdown("### 🌐 Phân tích Lớp Tọa độ Dán Bổ sung (So với Tỉnh/Thành Gốc)")
            st.table([
                {
                    "Khoảng cách Haversine": f"{coord_delta['distance_km']} km",
                    "Độ lệch (ΔLat, ΔLon)": f"{coord_delta['delta_lat_deg']}°, {coord_delta['delta_lon_deg']}°",
                    "Lệch LST": f"{coord_delta['lst_shift_minutes']} phút",
                    "Trọng số bổ sung": coord_delta["supp_weight"],
                    "AC Gốc -> Bổ sung": f"{coord_delta['base_ac']} -> {coord_delta['supp_ac']}",
                    "MC Gốc -> Bổ sung": f"{coord_delta['base_mc']} -> {coord_delta['supp_mc']}",
                    "Giờ HT Gốc -> Bổ sung": f"{coord_delta['base_hour']} -> {coord_delta['supp_hour']}",
                }
            ])

        st.markdown(f"### 🎯 Bảng Chấm điểm Định lượng Top 12 Ứng viên (1..{max_main})")
        supp_w = coord_delta["supp_weight"] if coord_delta is not None else 0.0
        eval_rows = [
            WesternCouncilEvaluator.evaluate_candidate(
                n,
                max_main,
                natal_sun_info,
                transit_chart,
                natal_chart=natal_chart,
                supplement_chart=supp_chart,
                supp_weight=supp_w,
            )
            for n in range(1, max_main + 1)
        ]
        eval_rows.sort(key=lambda r: r["final_score"], reverse=True)
        st.dataframe(eval_rows[:12], use_container_width=True)


if __name__ == "__main__":
    run_standalone_astrology_test()
