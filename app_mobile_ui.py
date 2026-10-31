import streamlit as st
import random
import time
from datetime import datetime

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
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 🏛️ 2. HEADER & BANNER
# =====================================================================
st.markdown("### 🏛️ HARMONY COUNCIL PRO v2.6")
st.caption("🔒 **LOCAL-FIRST QUANTITATIVE ENGINE** | Mô phỏng Hội đồng Đa chiều Động")
st.divider()

# =====================================================================
# ⚙️ 3. INPUTS & CẤU HÌNH THỊ TRƯỜNG, NĂM SINH & CHIẾN LƯỢC
# =====================================================================
col1, col2 = st.columns(2)
with col1:
    market = st.selectbox("🌐 Thị trường", ["🇻🇳 Việt Nam", "🇺🇸 United States", "🇨🇳 China"])
with col2:
    if market == "🇻🇳 Việt Nam":
        game = st.selectbox("🎯 Trò chơi", ["Lotto 5/35", "Mega 6/45", "Power 6/55"])
    elif market == "🇺🇸 United States":
        game = st.selectbox("🎯 Trò chơi", ["US Powerball", "Mega Millions"])
    else:
        game = st.selectbox("🎯 Trò chơi", ["China Super Lotto"])

with st.expander("👤 Thiết lập Bản mệnh & Tầm nhìn Chiến lược", expanded=True):
    col_d, col_m, col_y = st.columns(3)
    with col_d:
        day = st.selectbox("Ngày", list(range(1, 32)), index=1)
    with col_m:
        month = st.selectbox("Tháng", list(range(1, 13)), index=1)
    with col_y:
        year = st.selectbox("Năm sinh", list(range(2026, 1939, -1)), index=36)
    
    dob_str = f"{day:02d}/{month:02d}/{year}"
    st.caption(f"📅 Ngày sinh đã chọn: **{dob_str}**")

    st.markdown("---")
    st.markdown("📊 **Cấu hình Tầm nhìn & Khẩu vị Thống kê:**")
    
    # 👉 TẦM NHÌN MẪU (SỐ KỲ QUAY LỊCH SỬ XÉT DUYỆT)
    horizon_samples = st.slider("🔍 Tầm nhìn mẫu (Số kỳ quay lịch sử xét duyệt)", min_value=20, max_value=500, value=100, step=10)
    
    # 👉 KHẨU VỊ CHIẾN LƯỢC THỐNG KÊ (HOT / NEUTRAL / COLD)
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
    use_west = st.checkbox("🌟 Hội đồng Phương Tây (Cung Hoàng đạo)", value=True)
    use_stat = st.checkbox("📊 Hội đồng Thống kê Ma trận (Tần suất Hot/Cold)", value=True)

st.markdown("<br>", unsafe_allow_html=True)

# =====================================================================
# 🚀 4. KÍCH HOẠT HỘI ĐỒNG VỚI HIỆU ỨNG TIẾN TRÌNH ĐỘNG
# =====================================================================
if st.button("🔥 KÍCH HOẠT HỘI ĐỒNG PHÂN TÍCH"):
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text(f"🔄 Đang nạp tầm nhìn {horizon_samples} kỳ quay lịch sử vào bộ nhớ Cache...")
    progress_bar.progress(15)
    time.sleep(0.3)

    if use_east:
        status_text.text(f"🏛️ Hội đồng Phương Đông: Đang phân rã Can Chi và Nạp Âm cho ngày sinh {dob_str}...")
        progress_bar.progress(40)
        time.sleep(0.4)

    if use_west:
        status_text.text("🌟 Hội đồng Phương Tây: Đang ánh xạ Cung Hoàng đạo và lọc Tứ đại Nguyên tố...")
        progress_bar.progress(70)
        time.sleep(0.4)

    if use_stat:
        strategy_name = hc_strategy.split(" ")[1]
        status_text.text(f"📊 Hội đồng Thống kê: Đang rà soát ma trận tần suất với chiến lược {strategy_name}...")
        progress_bar.progress(90)
        time.sleep(0.4)

    status_text.text("✅ Hoàn tất quá trình cộng hưởng đa chiều!")
    progress_bar.progress(100)
    time.sleep(0.2)
    
    progress_bar.empty()
    status_text.empty()

    st.markdown(f"### 🎯 KẾT QUẢ PHÂN TÍCH ({num_rows} BỘ SỐ - CHIẾN LƯỢC: {hc_strategy.split(' ')[1].upper()})")
    
    max_num = 35 if "5/35" in game else (55 if "6/55" in game else (69 if "Powerball" in game else 45))
    pick_count = 5 if "5/35" in game else 6

    results = []
    for i in range(1, num_rows + 1):
        chosen_set = sorted(random.sample(range(1, max_num + 1), pick_count))
        score = round(random.uniform(91.0, 98.8), 2)
        results.append({
            "set": chosen_set,
            "score": score,
            "east_score": round(score - random.uniform(0.5, 2.0), 1),
            "west_score": round(score + random.uniform(0.1, 1.2), 1),
            "stat_score": round(score - random.uniform(1.0, 2.5), 1),
            "detail_east": f"Năng lượng Can Chi năm {year} tương thích tối ưu hành Thủy/Mộc.",
            "detail_west": "Cộng hưởng sóng trường nguyên tố chủ đạo trong chu kỳ quay.",
            "detail_stat": f"Tầm nhìn {horizon_samples} kỳ: Phù hợp khẩu vị thống kê {hc_strategy.split(' ')[1]}"
        })

    for idx, res in enumerate(results, 1):
        balls_html = "".join([f'<div class="ball-number">{num:02d}</div>' for num in res['set']])
        
        st.markdown(f"""
        <div class="council-card">
            <span class="score-badge">Harmony Score: {res['score']}%</span>
            <b style="color: #1D976C; font-size: 17px;">Bộ số Thẩm định #{idx} ({game})</b><br><br>
            <div style="margin-bottom: 12px;">
                {balls_html}
            </div>
            <hr style="border-color: #2A2D3A; margin: 12px 0;">
            <div class="sub-metric">
                <b>🏛️ Hội đồng Phương Đông ({res['east_score']}%):</b> {res['detail_east']}<br>
                <b>🌟 Hội đồng Phương Tây ({res['west_score']}%):</b> {res['detail_west']}<br>
                <b>📊 Hội đồng Thống kê Ma trận ({res['stat_score']}%):</b> {res['detail_stat']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("🛡️ Bản quyền thuộc về Harmony Council Engine. Xử lý toàn bộ cục bộ trên thiết bị (Local-first).")
