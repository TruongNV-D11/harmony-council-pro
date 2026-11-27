"""
harmony_assistant_module.py
Module trợ lý giải đáp & hướng dẫn sử dụng cho ứng dụng Vietlott Harmony.

Thiết kế:
- Một ô nhập liệu duy nhất (`st.text_input`) cho cả tìm từ khóa/câu hỏi mẫu lẫn đặt câu hỏi tự do.
- Chuẩn hóa chuỗi tiếng Việt có dấu / không dấu (`normalize_text`) để gợi ý câu hỏi tương đồng trong thư viện (`FAQ_DICT`).
- Không dùng cơ chế bắt phím từng ký tự (tránh rerun liên tục và giữ ứng dụng nhẹ).
- Ưu tiên trả lời tức thì từ kho câu hỏi có sẵn (`FAQ_DICT` + quy đổi đồng nghĩa); chỉ gọi AI fallback khi không khớp kho câu hỏi tĩnh.
- Tự dọn/xóa phần code hộp trợ lý AI cũ nếu truyền chuỗi mã nguồn file chính (`strip_legacy_assistant_box`).
- Theo dõi lượt sử dụng theo tháng lịch (`YYYY-MM`) gọn nhẹ trong `st.session_state`.
"""

from __future__ import annotations

from datetime import datetime
import os
import re
import unicodedata
from typing import Any, Callable, Dict, List, Optional

import streamlit as st


DEFAULT_FAQ_DICT: Dict[str, str] = {
    "Can Chi là gì và áp dụng ra sao trong ứng dụng?": (
        "Can Chi gồm Thiên Can (Giáp, Ất, Bính, Đinh, Mậu, Kỷ, Canh, Tân, Nhâm, Quý) "
        "và Địa Chi (Tý, Sửu, Dần, Mão, Thìn, Tỵ, Ngọ, Mùi, Thân, Dậu, Tuất, Hợi). "
        "Trong hệ thống Harmony, Can Chi dùng làm tín hiệu ngữ cảnh để đánh giá độ hòa hợp "
        "và điều chỉnh trọng số, không thay thế trục xác suất thống kê."
    ),
    "Nạp Âm trong Ngũ Hành có vai trò gì?": (
        "Nạp Âm là sự kết hợp giữa Can và Chi theo từng cặp lục thập hoa giáp để xác định "
        "hành Nạp Âm tương ứng. Trong ứng dụng, Nạp Âm giúp đối chiếu mức độ tương thích "
        "ngữ cảnh chứ không dùng để dự đoán kết quả xổ số."
    ),
    "Lập Xuân có ý nghĩa gì khi tính vận niên?": (
        "Lập Xuân đánh dấu bước chuyển tiết khí đầu năm theo lịch tiết khí truyền thống. "
        "Khi xác định năm Can Chi/vận niên cho thời điểm gần đầu năm dương lịch, cần đối chiếu "
        "mốc Lập Xuân để tránh xếp nhầm năm."
    ),
    "Chuyên gia Harmony Council hoạt động theo nguyên tắc nào?": (
        "Harmony vận hành theo nguyên tắc ưu tiên thống kê làm nền xác suất, sử dụng "
        "các lớp ngữ cảnh (Đông/Tây) có kỷ luật và cơ chế Guard để chủ động thu hẹp hoặc "
        "rút lui khi điều kiện không phù hợp."
    ),
    "Quẻ Biến / Dịch lý trong ứng dụng dùng để làm gì?": (
        "Dịch lý / Quẻ Biến cung cấp góc nhìn biến dịch và trạng thái ngữ cảnh bổ trợ, "
        "không dùng làm công cụ cam kết hay dự đoán kết quả quay số ngẫu nhiên."
    ),
    "Tại sao ứng dụng không hứa hẹn trúng thưởng?": (
        "Kết quả quay số xổ số là ngẫu nhiên độc lập. Harmony chỉ hỗ trợ tổ chức lựa chọn "
        "có trật tự, minh bạch và giải thích lý do dựa trên thống kê cùng ngữ cảnh."
    ),
}

SYNONYM_MAP: Dict[str, str] = {
    "can chi": "Can Chi là gì và áp dụng ra sao trong ứng dụng?",
    "thien can dia chi": "Can Chi là gì và áp dụng ra sao trong ứng dụng?",
    "nap am": "Nạp Âm trong Ngũ Hành có vai trò gì?",
    "ngu hanh nap am": "Nạp Âm trong Ngũ Hành có vai trò gì?",
    "lap xuan": "Lập Xuân có ý nghĩa gì khi tính vận niên?",
    "tiet lap xuan": "Lập Xuân có ý nghĩa gì khi tính vận niên?",
    "harmony": "Chuyên gia Harmony Council hoạt động theo nguyên tắc nào?",
    "harmony council": "Chuyên gia Harmony Council hoạt động theo nguyên tắc nào?",
    "chuyen gia": "Chuyên gia Harmony Council hoạt động theo nguyên tắc nào?",
    "que bien": "Quẻ Biến / Dịch lý trong ứng dụng dùng để làm gì?",
    "dich ly": "Quẻ Biến / Dịch lý trong ứng dụng dùng để làm gì?",
    "du doan": "Tại sao ứng dụng không hứa hẹn trúng thưởng?",
    "trung thuong": "Tại sao ứng dụng không hứa hẹn trúng thưởng?",
}


def normalize_text(text: Optional[str]) -> str:
    """Chuẩn hóa chuỗi tiếng Việt: bỏ dấu, chuyển thường, đổi 'đ' -> 'd', gom khoảng trắng."""
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFD", str(text))
    without_marks = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    cleaned = without_marks.lower().replace("đ", "d").replace("Đ", "d")
    cleaned = re.sub(r"[^a-z0-9\s/+-]", " ", cleaned)
    return " ".join(cleaned.split())


def _current_month_key() -> str:
    return datetime.now().strftime("%Y-%m")


def _record_usage(source_type: str) -> None:
    """Ghi nhận số lượt sử dụng theo tháng lịch (YYYY-MM) trong session_state."""
    month_key = _current_month_key()
    usage_store: Dict[str, Dict[str, int]] = st.session_state.setdefault(
        "harmony_assistant_usage", {}
    )
    month_stats = usage_store.setdefault(
        month_key, {"total": 0, "faq": 0, "ai": 0}
    )
    month_stats["total"] += 1
    if source_type == "faq":
        month_stats["faq"] += 1
    elif source_type == "ai":
        month_stats["ai"] += 1


def find_matching_questions(
    query: str,
    faq_dict: Optional[Dict[str, str]] = None,
    synonym_map: Optional[Dict[str, str]] = None,
    limit: int = 5,
) -> List[str]:
    """
    Tìm các câu hỏi có sẵn tương đồng với chuỗi ký tự người dùng đang nhập.
    Trả về danh sách câu hỏi chuẩn (canonical question) để người dùng chọn ngay.
    """
    faq = faq_dict if faq_dict is not None else DEFAULT_FAQ_DICT
    synonyms = synonym_map if synonym_map is not None else SYNONYM_MAP

    norm_q = normalize_text(query)
    if not norm_q:
        return []

    matches: List[str] = []

    def _add_match(question: str) -> None:
        if question in faq and question not in matches:
            matches.append(question)

    # 1. Đối chiếu trực tiếp từ khóa đồng nghĩa
    for syn_key, canonical_q in synonyms.items():
        norm_syn = normalize_text(syn_key)
        if norm_syn and (norm_q in norm_syn or norm_syn in norm_q):
            _add_match(canonical_q)

    # 2. Đối chiếu chuỗi con trong câu hỏi mẫu hoặc nội dung giải đáp
    for question, answer in faq.items():
        if norm_q in normalize_text(question) or norm_q in normalize_text(answer):
            _add_match(question)

    # 3. Nếu chưa đủ kết quả, khớp theo từng từ (token >= 2 ký tự)
    if len(matches) < limit:
        tokens = [tok for tok in norm_q.split() if len(tok) >= 2]
        if tokens:
            for question, answer in faq.items():
                haystack = f"{normalize_text(question)} {normalize_text(answer)}"
                if all(tok in haystack for tok in tokens):
                    _add_match(question)

    return matches[:limit]


def resolve_canonical_question(
    raw_query: str,
    faq_dict: Optional[Dict[str, str]] = None,
    synonym_map: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """
    Kiểm tra xem câu nhập có khớp chính xác hoặc ánh xạ trực tiếp tới câu hỏi
    có sẵn trong thư viện hay không. Nếu có, trả về key chuẩn trong `faq_dict`.
    """
    faq = faq_dict if faq_dict is not None else DEFAULT_FAQ_DICT
    synonyms = synonym_map if synonym_map is not None else SYNONYM_MAP

    norm_q = normalize_text(raw_query)
    if not norm_q:
        return None

    for question in faq:
        if normalize_text(question) == norm_q:
            return question

    normalized_syn_map = {normalize_text(k): v for k, v in synonyms.items()}
    if norm_q in normalized_syn_map:
        mapped = normalized_syn_map[norm_q]
        if mapped in faq:
            return mapped

    return None


def default_ai_fallback(prompt: str) -> str:
    """
    Hàm dự phòng gọi Gemini API khi câu hỏi nằm ngoài thư viện câu hỏi tĩnh.
    Tự động nhận diện gói `google-genai` hoặc `google-generativeai` nếu có sẵn.
    """
    api_key = (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or (st.secrets.get("GEMINI_API_KEY") if hasattr(st, "secrets") else None)
    )
    if not api_key:
        return (
            "Câu hỏi này chưa có sẵn trong thư viện mẫu và chưa cấu hình khóa API "
            "(`GEMINI_API_KEY`). Bạn có thể thử gõ từ khóa ngắn gọn như: "
            "`can chi`, `nap am`, `lap xuan`, `harmony`, `que bien`."
        )

    system_instruction = (
        "Bạn là Harmony Assistant, trợ lý giải đáp khái niệm và hướng dẫn sử dụng "
        "cho ứng dụng Vietlott Harmony. Trả lời ngắn gọn, rõ ràng, trung thực, "
        "không hứa hẹn kết quả xổ số."
    )

    try:
        from google import genai  # type: ignore

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_instruction}\n\nCâu hỏi người dùng: {prompt}",
        )
        text = getattr(response, "text", None)
        if text:
            return text.strip()
    except Exception:
        pass

    try:
        import google.generativeai as genai_legacy  # type: ignore

        genai_legacy.configure(api_key=api_key)
        model = genai_legacy.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            f"{system_instruction}\n\nCâu hỏi người dùng: {prompt}"
        )
        text = getattr(response, "text", None)
        if text:
            return text.strip()
    except Exception as exc:
        return f"Không thể kết nối dịch vụ AI lúc này ({exc})."

    return "Không nhận được phản hồi từ dịch vụ AI."


def strip_legacy_assistant_box(source_code: str) -> str:
    """
    Hỗ trợ gỡ khối hộp trợ lý AI cũ nếu cần làm sạch mã nguồn file giao diện chính.
    Xóa đoạn expander/block chứa tiêu đề 'HỘP CHỨC NĂNG AI' nếu xuất hiện.
    """
    if not source_code:
        return ""
    pattern = re.compile(
        r"^[ 	]*(?:with\s+st\.expander\([^
]*HỘP CHỨC NĂNG AI[^
]*\)\s*:\s*
(?:(?:[ 	]+[^
]*|\s*)
)*)",
        re.MULTILINE,
    )
    cleaned = pattern.sub("", source_code)
    return re.sub(r"
{3,}", "

", cleaned)


def _append_message(role: str, content: str, source_badge: Optional[str] = None) -> None:
    history: List[Dict[str, Any]] = st.session_state.setdefault(
        "harmony_assistant_messages", []
    )
    history.append(
        {
            "role": role,
            "content": content,
            "source": source_badge,
        }
    )


def render_assistant_widget(
    *,
    title: str = "Harmony Assistant: Giải đáp & Hướng dẫn sử dụng",
    expanded: bool = False,
    faq_dict: Optional[Dict[str, str]] = None,
    synonym_map: Optional[Dict[str, str]] = None,
    ai_callback: Optional[Callable[[str], str]] = None,
    show_usage_stats: bool = True,
    key_prefix: str = "harmony_asst",
) -> None:
    """
    Hiển thị widget trợ lý với MỘT ô nhập liệu duy nhất:
    - Đối chiếu chuỗi ký tự với kho câu hỏi có sẵn để gợi ý chọn nhanh.
    - Chỉ gọi AI fallback khi gửi câu hỏi không có trong thư viện.
    """
    faq = faq_dict if faq_dict is not None else DEFAULT_FAQ_DICT
    synonyms = synonym_map if synonym_map is not None else SYNONYM_MAP
    ask_ai_fn = ai_callback if ai_callback is not None else default_ai_fallback

    st.session_state.setdefault("harmony_assistant_messages", [])
    pending_key = f"{key_prefix}_pending_question"
    input_key = f"{key_prefix}_single_input"

    if pending_key in st.session_state and st.session_state[pending_key] is not None:
        st.session_state[input_key] = st.session_state.pop(pending_key)

    with st.expander(title, expanded=expanded):
        st.caption(
            "Nhập từ khóa (vd: can chi, nap am, lap xuan, harmony, que bien) "
            "để chọn câu hỏi có sẵn, hoặc đặt câu hỏi tự do rồi bấm Gửi."
        )

        # Ô nhập liệu duy nhất
        user_query = st.text_input(
            "Nhập từ khóa hoặc câu hỏi",
            key=input_key,
            placeholder="Ví dụ: can chi, nap am, lap xuan... hoặc nhập câu hỏi bất kỳ",
            label_visibility="collapsed",
        )

        # Gợi ý câu hỏi tương đồng theo chuỗi ký tự hiện có trong ô nhập
        suggestions = find_matching_questions(
            user_query, faq_dict=faq, synonym_map=synonyms
        )
        if user_query.strip() and suggestions:
            st.markdown("**Gợi ý câu hỏi có sẵn trong thư viện (bấm chọn để trả lời ngay):**")
            for idx, q_item in enumerate(suggestions):
                if st.button(
                    q_item,
                    key=f"{key_prefix}_sug_{idx}_{abs(hash(q_item)) % 100000}",
                    use_container_width=True,
                ):
                    answer_text = faq[q_item]
                    _record_usage("faq")
                    _append_message("user", q_item, source_badge="Thư viện")
                    _append_message("assistant", answer_text, source_badge="Thư viện")
                    st.rerun()

        col_send, col_clear = st.columns([3, 1])
        with col_send:
            send_clicked = st.button(
                "Gửi câu hỏi",
                key=f"{key_prefix}_send_btn",
                type="primary",
                use_container_width=True,
            )
        with col_clear:
            clear_clicked = st.button(
                "Xóa lịch sử",
                key=f"{key_prefix}_clear_btn",
                use_container_width=True,
            )

        if clear_clicked:
            st.session_state["harmony_assistant_messages"] = []
            st.session_state[pending_key] = ""
            st.rerun()

        if send_clicked:
            cleaned_query = (user_query or "").strip()
            if not cleaned_query:
                st.warning("Vui lòng nhập từ khóa hoặc câu hỏi trước khi gửi.")
            else:
                canonical_q = resolve_canonical_question(
                    cleaned_query, faq_dict=faq, synonym_map=synonyms
                )
                if canonical_q is not None:
                    reply = faq[canonical_q]
                    _record_usage("faq")
                    _append_message("user", canonical_q, source_badge="Thư viện")
                    _append_message("assistant", reply, source_badge="Thư viện")
                else:
                    with st.spinner("Đang truy vấn trợ lý AI..."):
                        reply = ask_ai_fn(cleaned_query)
                    _record_usage("ai")
                    _append_message("user", cleaned_query, source_badge="AI")
                    _append_message("assistant", reply, source_badge="AI")
                st.rerun()

        # Hiển thị nội dung hội thoại
        messages: List[Dict[str, Any]] = st.session_state.get(
            "harmony_assistant_messages", []
        )
        for msg in messages:
            role = msg.get("role", "assistant")
            content = msg.get("content", "")
            badge = msg.get("source")
            with st.chat_message(role):
                if badge and role == "assistant":
                    st.caption(f"Nguồn: {badge}")
                st.write(content)

        if show_usage_stats:
            month_key = _current_month_key()
            stats = st.session_state.get("harmony_assistant_usage", {}).get(
                month_key, {"total": 0, "faq": 0, "ai": 0}
            )
            st.caption(
                f"Thống kê tháng {month_key}: Tổng {stats['total']} lượt "
                f"(Thư viện: {stats['faq']} | AI: {stats['ai']})"
            )


def render_harmony_assistant(
    *,
    title: str = "Harmony Assistant: Giải đáp & Hướng dẫn sử dụng",
    expanded: bool = False,
    faq_dict: Optional[Dict[str, str]] = None,
    synonym_map: Optional[Dict[str, str]] = None,
    ai_callback: Optional[Callable[[str], str]] = None,
    show_usage_stats: bool = True,
    key_prefix: str = "harmony_asst",
) -> None:
    """Alias tương thích ngược cho `render_assistant_widget`."""
    render_assistant_widget(
        title=title,
        expanded=expanded,
        faq_dict=faq_dict,
        synonym_map=synonym_map,
        ai_callback=ai_callback,
        show_usage_stats=show_usage_stats,
        key_prefix=key_prefix,
    )
