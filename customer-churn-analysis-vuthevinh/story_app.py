"""Data Storytelling App - Churn Analysis với Guided Flow."""

import pandas as pd
import seaborn as sns
import streamlit as st
from bq_modules import render_bq1, render_bq2

# Cấu hình trang
st.set_page_config(
    page_title="Churn Story: Toxic Combo Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Áp dụng theme cho biểu đồ
sns.set_theme(style="whitegrid")
sns.set_palette("Set2")


# ========== LOAD & PREPARE DATA ==========
@st.cache_data(show_spinner=False)
def load_and_prepare_data():
    """Load dữ liệu từ file CSV và tạo các cột phân tích."""
    # Load data
    df = pd.read_csv("data/churn.csv")
    
    # 1. Flag khách hàng Mới (<= 3 tháng)
    df['Is_New_Customer'] = df['AccountAge'] <= 3
    
    # 2. Flag Phí cao (Top 25% toàn bộ dataset)
    high_charge_threshold = df['MonthlyCharges'].quantile(0.75)
    df['Is_High_Charge'] = df['MonthlyCharges'] > high_charge_threshold
    
    # 3. Flag các phương thức thanh toán thủ công
    df['Is_Electronic_Check'] = df['PaymentMethod'] == 'Electronic check'
    df['Is_Mailed_Check'] = df['PaymentMethod'] == 'Mailed check'
    
    # 4. Nhóm các phương thức thanh toán (để vẽ TQ 1.3)
    def payment_group_detail(row):
        if row['Is_Electronic_Check']:
            return 'Electronic Check'
        elif row['Is_Mailed_Check']:
            return 'Mailed Check'
        else:
            return 'Others (Auto-pay)'
    df['Payment_Group_Detail'] = df.apply(payment_group_detail, axis=1)
    
    # 5. Xác định các phân khúc "Toxic Combo" (để vẽ TQ 1.4)
    def combined_risk_segment(row):
        is_new = row['Is_New_Customer']
        is_high_charge = row['Is_High_Charge']
        
        if is_new and is_high_charge and row['Is_Electronic_Check']:
            return 'Toxic Combo (E-Check)'
        elif is_new and is_high_charge and row['Is_Mailed_Check']:
            return 'Toxic Combo (Mailed Check)'
        else:
            return 'Others'
    
    df['Combined_Risk_Segment'] = df.apply(combined_risk_segment, axis=1)
    
    return df


# Load data một lần duy nhất
df = load_and_prepare_data()

# Khởi tạo session state
if 'current_bq' not in st.session_state:
    st.session_state.current_bq = 1
if 'current_step_bq1' not in st.session_state:
    st.session_state.current_step_bq1 = 1
if 'current_step_bq2' not in st.session_state:
    st.session_state.current_step_bq2 = 1

# Định nghĩa các bước cho BQ1
STEPS_BQ1 = {
    1: "TQ 1.1: Yếu tố Tuổi",
    2: "TQ 1.2: Yếu tố Mức phí",
    3: "TQ 1.3: Yếu tố Phiền phức",
    4: "TQ 1.4: Toxic Combo",
    5: "Kết luận"
}

# Định nghĩa các bước cho BQ2
STEPS_BQ2 = {
    1: "TQ 2.1: Yếu tố Gắn Bó",
    2: "TQ 2.3: Thất Vọng (Rating)",
    3: "TQ 2.2: Thất Vọng (Ticket)",
    4: "BQ2: Câu trả lời",
    5: "Kết luận"
}

# Header chính
st.title('🔍 Customer Churn Analysis - Data Storytelling')
st.caption("Khám phá các yếu tố ảnh hưởng đến churn qua 2 Business Questions")
st.markdown("---")

# Chọn Business Question
col1, col2 = st.columns(2)
with col1:
    if st.button("📊 BQ1: Cú sốc thanh toán & Phiền phức", 
                 type="primary" if st.session_state.current_bq == 1 else "secondary",
                 use_container_width=True):
        st.session_state.current_bq = 1
with col2:
    if st.button("🎯 BQ2: Chán nản vs Bực bội", 
                 type="primary" if st.session_state.current_bq == 2 else "secondary",
                 use_container_width=True):
        st.session_state.current_bq = 2

st.markdown("---")

# Tạo thanh điều hướng dọc bên trái trong sidebar
with st.sidebar:
    st.markdown(f"## 📚 Điều hướng BQ{st.session_state.current_bq}")
    st.markdown("---")
    
    # Chọn STEPS dựa vào BQ hiện tại
    current_steps = STEPS_BQ1 if st.session_state.current_bq == 1 else STEPS_BQ2
    current_step_key = 'current_step_bq1' if st.session_state.current_bq == 1 else 'current_step_bq2'
    
    selected_step_label = st.radio(
        "Chọn bước phân tích:",
        options=list(current_steps.values()),
        index=st.session_state[current_step_key] - 1,
        label_visibility="visible"
    )
    
    st.markdown("---")
    st.markdown("### 💡 Hướng dẫn")
    st.caption("Sử dụng menu bên trái để điều hướng qua các bước phân tích, hoặc nhấn nút 'Tiếp theo' ở cuối mỗi bước.")

# Cập nhật current_step dựa trên lựa chọn từ radio
for step_num, step_label in current_steps.items():
    if step_label == selected_step_label:
        st.session_state[current_step_key] = step_num
        break

# Hàm callback cho các nút "Tiếp theo"
def next_step():
    current_bq = st.session_state.current_bq
    step_key = f'current_step_bq{current_bq}'
    max_steps = len(STEPS_BQ1) if current_bq == 1 else len(STEPS_BQ2)
    if st.session_state[step_key] < max_steps:
        st.session_state[step_key] += 1

def reset_story():
    current_bq = st.session_state.current_bq
    step_key = f'current_step_bq{current_bq}'
    st.session_state[step_key] = 1

# Render nội dung theo BQ và bước hiện tại
if st.session_state.current_bq == 1:
    render_bq1(df, next_step)
else:
    render_bq2(df, next_step)

# Footer
st.markdown("---")
st.caption("💡 Data Storytelling Dashboard | Powered by Streamlit & Seaborn")
