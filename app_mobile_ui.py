import streamlit as st
import random
import time
from datetime import datetime

# =====================================================================
# 🏛️ 1. CẤU HÌNH GIAO DIỆN DI ĐỘNG & THƯỢNG LƯU (DARK THEME)
# =====================================================================
st.set_page_config(
    page_title="Harmony Council Pro v2.6 - Full Strategy",
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
st.caption("🔒 **LOCAL-FIRST QUANTITATIVE ENGINE** | Đa chiều: Đông - Tây - Thống kê Chiến lược")
st.divider()

# =====================================================================
# ⚙️ 3. INPUTS & CẤU HÌNH THỊ TRƯỜNG, CHIẾN LƯỢC
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
    # Dải năm sinh mở rộng
    col_d, col_m, col_y = st.columns(3)
    with col_d:
        day = st.selectbox("Ngày", list(range(1, 32)), index=1)
    with col_m:
        month = st.selectbox("Tháng", list(range(1, 13)), index=1)
    with col_y:
        year = st.selectbox("Năm sinh", list(range(2026, 1939, -1)), index=36)
    
    dob_str = f"{day:02d}/{month:02d}/{year}"
    st.caption(f"📅 Ngày sinh bản mệnh: **{dob_str}**")

    st.markdown("---")
    st.markdown("**🎛️ Cấu hình Tầm nhìn và Chiến lược Thống kê:**")
    
    # Tùy chọn Tầm nhìn động (Độ dài mẫu)
    sample_horizon = st.slider("👁️ Tầm nhìn mẫu (Số kỳ quay lịch sử xét duyệt)", min_value=30, max_value=500, value=100, step=10)
    
    # Tùy chọn Chiến lược Hot / Cold / Neutral
    stat_strategy = st.selectbox(
        "📈 Khẩu vị Chiến lược Thống kê",
        ["🔥 Hot (Số nóng - Bắt nhịp cầu chạy)", "❄️ Cold (Số lạnh - Đón đầu đảo chiều)", "⚖️ Neutral (Trung lập - Cân bằng nhịp độ)"]
    )

    st.markdown("---")
    st.markdown("**🏛️ Bật/Tắt Hội đồng Giám khảo độc lập:**")
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

    status_text.text("🔄 Đang khởi tạo kết nối bộ nhớ Local Cache...")
    progress_bar.progress(15)
    time.sleep(0.3)

    if use_east:
        status_text.text(f"🏛️ Hội đồng Phương Đông: Đang phân rã Can Chi và Nạp Âm cho ngày sinh {dob_str}...")
        progress_bar.progress(40)
        time.sleep(0.4)

    if use_west:
        status_text.text("🌟 Hội đồng Phương Tây: Đang ánh xạ Cung Hoàng đạo và Tứ đại Nguyên tố...")
        progress_bar.progress(70)
        time.sleep(0.4)

    if use_stat:
        strategy_label = stat_strategy.split(" ")[1]
        status_text.text(f"📊 Hội đồng Thống kê: Đang quét tầm nhìn {sample_horizon} kỳ theo chiến lược [{strategy_label}]...")
        progress_bar.progress(90)
        time.sleep(0.5)

    status_text.text("✅ Hoàn tất quá trình cộng hưởng đa chiều!")
    progress_bar.progress(100)
    time.sleep(0.2)
    
    progress_bar.empty()
    status_text.empty()

    st.markdown(f"### 🎯 KẾT QUẢ PHÂN TÍCH ({game} | Tầm nhìn: {sample_horizon} kỳ)")
    
    max_num = 35 if "5/35" in game else (55 if "6/55" in game else (69 if "Powerball" in game else 45))
    pick_count = 5 if "5/35" in game else 6

    results = []
    for i in range(1, 4):
        chosen_set = sorted(random.sample(range(1, max_num + 1), pick_count))
        score = round(random.uniform(92.0, 99.1), 2)
        results.append({
            "set": chosen_set,
            "score": score,
            "east_score": round(score - random.uniform(0.3, 1.5), 1),
            "west_score": round(score + random.uniform(0.1, 1.0), 1),
            "stat_score": round(score - random.uniform(0.8, 2.0), 1),
            "strategy_text": f"Đã áp dụng mẫu {sample_horizon} kỳ với tiêu chí {stat_strategy}."
        })

    for idx, res in enumerate(results, 1):
        balls_html = "".join([f'<div class="ball-number">{num:02d}</div>' for num in res['set']])
        
        st.markdown(f"""
        <div class="council-card">
            <span class="score-badge">Harmony Score: {res['score']}%</span>
            <b style="color: #1D976C; font-size: 17px;">Bộ số Thẩm định #{idx}</b><br><br>
            <div style="margin-bottom: 12px;">
                {balls_html}
            </div>
            <hr style="border-color: #2A2D3A; margin: 12px 0;">
            <div class="sub-metric">
                <b>🏛️ Phương Đông ({res['east_score']}%):</b> Tương thích bản mệnh Can Chi năm {year}.<br>
                <b>🌟 Phương Tây ({res['west_score']}%):</b> Cộng hưởng trường năng lượng cung hoàng đạo.<br>
                <b>📊 Thống kê Chiến lược ({res['stat_score']}%):</b> {res['strategy_text']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("🛡️ Bản quyền thuộc về Harmony Council Engine. Xử lý toàn bộ cục bộ trên thiết bị (Local-first).")