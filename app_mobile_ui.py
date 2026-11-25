import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Any

VN_TZ = timezone(timedelta(hours=7))


def _jd_from_date(day: int, month: int, year: int) -> int:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


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
    """
    Lõi lập quẻ thời khắc & luận thời vận Tài lộc theo Mai Hoa Dịch Số:
    - Khởi quẻ theo thời điểm bấm quẻ (Âm lịch: số thứ tự Địa chi năm 1..12, tháng Âm, ngày Âm + số Giờ Chi 1..12).
    - Lập đủ Quẻ Chủ, Hào Động (hào 1..6 tính từ dưới lên), Hỗ Quái (hào 2-3-4 và 3-4-5), Quẻ Biến (đảo hào động).
    - Phân định 5 quan hệ Ngũ hành Thể - Dụng và đối chiếu xu hướng chuyển dịch sang Quẻ Biến dưới góc độ Tài lộc.
    """

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
        1: "hào sơ (hào 1 — hào dưới cùng của hạ quái): khí động mới manh nha ở tầng khởi phát, dòng tiền còn nhỏ và dễ bị chi phối bởi các yếu tố mở đầu.",
        2: "hào nhị (hào 2 — trung vị hạ quái): nền tảng bên trong đang giữ nhịp, có độ chững nhưng chịu tác động trực tiếp từ môi trường sát cận.",
        3: "hào tam (hào 3 — thượng vị hạ quái, giáp ranh thượng quái): điểm bản lề giữa nội lực và ngoại cảnh, dễ nảy sinh do dự hoặc phát sinh biến số chuyển giao.",
        4: "hào tứ (hào 4 — sơ vị thượng quái): bước vào tầng ngoại cảnh, dòng tiền bắt đầu va chạm với bối cảnh thị trường và tác động bên ngoài.",
        5: "hào ngũ (hào 5 — trung vị thượng quái): vị trí chủ đạo của ngoại quái, phản ánh tâm điểm chi phối cục diện nhưng cũng đi kèm áp lực lớn.",
        6: "hào thượng (hào 6 — hào trên cùng của thượng quái): giai đoạn cực biến của quẻ, dễ chuyển hóa sang chiều ngược lại nếu đi quá đà.",
    }

    QUAI_TUONG_TAI_LOC = {
        1: "tượng Càn (Trời): tính cương kiện, chủ động và lực lớn, nhưng nếu quá cứng nhắc thì dễ thiếu độ linh hoạt khi thời thế đổi nhịp",
        2: "tượng Đoài (Đầm/Ao): tính giao lưu, mở rộng và hỷ khí, nhưng nếu thiếu điểm dừng thì dễ buông lỏng tay chi tiêu",
        3: "tượng Ly (Lửa): tính sáng rõ, bộc lộ và nhịp chạy nhanh, nhưng khí nóng dễ bốc, thiếu bền nếu vội vàng",
        4: "tượng Chấn (Sấm): tính chấn động và khởi hành nhanh, dễ tạo biến động tức thời nhưng độ ổn định ngắn hạn",
        5: "tượng Tốn (Gió): tính thẩm thấu, linh hoạt và thuận theo, đi mềm mại nhưng đôi khi thiếu sự dứt khoát",
        6: "tượng Khảm (Nước): tính tiềm ẩn, chiều sâu và dòng chảy ngầm, có thể là trí tuệ/ẩn cơ nhưng cũng dễ che khuất hoặc gây trắc trở",
        7: "tượng Cấn (Núi): tính dừng lại, giữ vững và tạo điểm tựa, giúp hãm đà hao tổn nhưng làm nhịp xoay chậm lại",
        8: "tượng Khôn (Đất): tính bao dung, tích chứa và thuận theo, chịu tải tốt nhưng thiên về tĩnh và chờ thời",
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
    def _classify_bien_trend(cls, the_elem: str, bien_the_elem: str) -> str:
        if cls.NGU_HANH_SINH.get(bien_the_elem) == the_elem:
            return (
                f"Sang Quẻ Biến, khí của quái biến phía Thể ({bien_the_elem}) sinh cho Thể ({the_elem}), "
                f"cho thấy chiều hướng về sau của dòng tiền có phần được bồi đắp và bớt áp lực hơn so với lúc khởi quẻ."
            )
        if bien_the_elem == the_elem:
            return (
                f"Sang Quẻ Biến, hành của quái biến phía Thể ({bien_the_elem}) đồng khí với Thể ({the_elem}), "
                f"cho thấy xu hướng về sau giữ nhịp tương đối đều đặn, ít đổi chiều đột ngột."
            )
        if cls.NGU_HANH_KHAC.get(the_elem) == bien_the_elem:
            return (
                f"Sang Quẻ Biến, Thể ({the_elem}) khắc quái biến ({bien_the_elem}), "
                f"xu hướng sau vẫn nằm trong tầm chi phối của Thể nhưng càng kéo dài càng dễ tiêu hao khí lực."
            )
        if cls.NGU_HANH_SINH.get(the_elem) == bien_the_elem:
            return (
                f"Sang Quẻ Biến, Thể ({the_elem}) sinh cho quái biến ({bien_the_elem}), "
                f"cho thấy chiều hướng về sau dễ phát sinh tiết khí/hao hụt dòng tiền, không nên dồn kỳ vọng quá lớn về chặng sau."
            )
        return (
            f"Sang Quẻ Biến, quái biến ({bien_the_elem}) khắc chế Thể ({the_elem}), "
            f"cảnh báo xu hướng về sau dễ gặp trở ngại hoặc biến số bất lợi cho tài lộc; cần giữ kỷ luật vốn từ sớm."
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
        the_tuong = cls.QUAI_TUONG_TAI_LOC[the_id]
        dung_tuong = cls.QUAI_TUONG_TAI_LOC[dung_id]
        bien_trend_note = cls._classify_bien_trend(the_info["element"], cls.BAT_QUAI[bien_the_id]["element"])

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
                "Cứ bám đúng phần ngân sách đã định, tránh chạy theo tâm lý đám đông."
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
            "Ghi chú phương pháp: Quẻ khởi theo thời điểm động tâm (Âm lịch + Giờ Chi; số năm quy ước theo thứ tự Địa chi 1..12), "
            "luận chuyên biệt dưới góc độ tài lộc và quản trị vốn."
        )

        scholar_commentary = (
            f"Quẻ Chủ lập được {chu_str}, động tại {hao_note} "
            f"Diễn biến bên trong kết thành Hỗ quái {ho_str}, rồi chuyển sang Quẻ Biến {bien_str}. "
            f"{bien_trend_note} "
            f"{wealth_analysis} "
            f"Xét tượng quẻ dưới góc độ tài lộc: phía Thể mang {the_tuong}, còn phía Dụng mang {dung_tuong}. "
            f"{method_note}"
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
        dt_local = dt.astimezone(VN_TZ) if dt.tzinfo is not None else dt.replace(tzinfo=VN_TZ)

        lunar_day, lunar_month, lunar_year, is_leap = gregorian_to_lunar(
            dt_local.day, dt_local.month, dt_local.year, time_zone=tz_offset_hours
        )

        year_chi_idx = (lunar_year - 4) % 12
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
            "lunar_date": f"Ngày {lunar_day} tháng {lunar_month}{' (nhuận)' if is_leap else ''} năm {year_chi_name} ({lunar_year})",
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


def print_result(res: Dict[str, Any]) -> None:
    print("-" * 76)
    print(f"Dương lịch : {res['timestamp']} | Giờ: {res['chi_gio']}")
    print(f"Âm lịch    : {res['lunar_date']} | {res['lunar_components']}")
    print(f"Quẻ Chủ    : {res['que_chu']}")
    print(f"Hào Động   : {res['hao_dong']}")
    print(f"Hỗ Quái    : {res['que_ho']}")
    print(f"Quẻ Biến   : {res['que_bien']}")
    print(f"Kết luận   : {res['zone_label']}")
    print(f"Hành động  : {res['advice']}")
    print(f"Luận giải  : {res['scholar_commentary']}")


if __name__ == "__main__":
    now_local = datetime.now(VN_TZ)
    print("=== TEST THỜI ĐIỂM HIỆN TẠI ===")
    print_result(MaiHoaDichSoCore.cast_hexagram(now_local))

    sample_times = [
        datetime(2026, 11, 25, 4, 52, tzinfo=VN_TZ),
        datetime(2026, 11, 25, 13, 15, tzinfo=VN_TZ),
        datetime(2026, 11, 25, 21, 5, tzinfo=VN_TZ),
        datetime(2026, 11, 26, 18, 0, tzinfo=VN_TZ),
    ]
    print("\n=== TEST CÁC MỐC MẪU ===")
    for dt in sample_times:
        print_result(MaiHoaDichSoCore.cast_hexagram(dt))
