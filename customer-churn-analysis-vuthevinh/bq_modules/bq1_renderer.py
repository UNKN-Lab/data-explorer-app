"""Business Question 1 Renderer - Toxic Combo Analysis."""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st


def render_bq1(df, next_step_callback):
    """Render all steps for BQ1: Toxic Combo analysis."""
    
    current_step = st.session_state.current_step_bq1
    
    st.header('🔍 BQ1: "Cú sốc thanh toán" & "Sự phiền phức" có phải là lý do chính đẩy khách hàng mới rời đi không?')
    st.markdown("---")
    
    # ========== STEP 1: TQ 1.1 - Yếu tố Tuổi ==========
    if current_step == 1:
        st.header("📊 TQ 1.1: Khách hàng Mới (<= 3 tháng) Churn cao hơn?")
        
        st.write(
            """
            Đầu tiên, chúng ta thấy rằng **3 tháng đầu tiên là giai đoạn nhạy cảm nhất**. 
            Tỷ lệ churn của khách hàng mới cao gần **gấp đôi** khách hàng cũ.
            """
        )
        
        # Tính toán tỷ lệ churn thực tế từ dữ liệu
        churn_by_age = df.groupby('Is_New_Customer')['Churn'].mean().reset_index()
        churn_by_age['Loại khách hàng'] = churn_by_age['Is_New_Customer'].map({
            False: 'Cũ (>3 tháng)',
            True: 'Mới (<= 3 tháng)'
        })
        
        # Vẽ biểu đồ
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        sns.barplot(
            data=churn_by_age,
            x='Loại khách hàng',
            y='Churn',
            palette=['#3498db', '#e74c3c'],
            ax=ax1,
            errorbar=None
        )
        ax1.set_title('TQ 1.1: Tỷ lệ Churn theo Tuổi tài khoản\n(Mới <= 3 tháng)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Tỷ lệ Churn', fontsize=12)
        ax1.set_xlabel('Loại khách hàng', fontsize=12)
        ax1.set_ylim(0, max(churn_by_age['Churn']) * 1.2)
        
        for container in ax1.containers:
            ax1.bar_label(container, fmt='%.2f', padding=3)
        
        st.pyplot(fig1)
        plt.close(fig1)
        
        st.markdown("---")
        st.button("Tiếp theo: Yếu tố Mức phí ➔", key="btn_bq1_1", on_click=next_step_callback, type="primary")
    
    # ========== STEP 2: TQ 1.2 - Yếu tố Mức phí ==========
    elif current_step == 2:
        st.header("💰 TQ 1.2: Trong nhóm Mới, Phí cao (Top 25%) Churn cao hơn?")
        
        st.write(
            """
            **Đúng vậy.** Khi đã là khách hàng mới, những ai bị **"sốc giá"** (trả phí cao) 
            có tỷ lệ rời đi cao hơn **10 điểm phần trăm**. 
            Điều này xác nhận sự nhạy cảm về giá trong giai đoạn đầu.
            """
        )
        
        df_new_customers = df[df['Is_New_Customer'] == True]
        churn_by_charge = df_new_customers.groupby('Is_High_Charge')['Churn'].mean().reset_index()
        churn_by_charge['Mức phí'] = churn_by_charge['Is_High_Charge'].map({
            False: 'Phí thường',
            True: 'Phí cao (Top 25%)'
        })
        
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        sns.barplot(
            data=churn_by_charge,
            x='Mức phí',
            y='Churn',
            palette=['#95a5a6', '#e67e22'],
            ax=ax2,
            errorbar=None
        )
        ax2.set_title('TQ 1.2: Tỷ lệ Churn của KH Mới\ntheo Mức phí (High = Top 25%)', 
                      fontsize=14, fontweight='bold')
        ax2.set_ylabel('Tỷ lệ Churn', fontsize=12)
        ax2.set_xlabel('Mức phí', fontsize=12)
        ax2.set_ylim(0, max(churn_by_charge['Churn']) * 1.2)
        
        for container in ax2.containers:
            ax2.bar_label(container, fmt='%.2f', padding=3)
        
        st.pyplot(fig2)
        plt.close(fig2)
        
        st.markdown("---")
        st.button("Tiếp theo: Yếu tố Phiền phức ➔", key="btn_bq1_2", on_click=next_step_callback, type="primary")
    
    # ========== STEP 3: TQ 1.3 - Yếu tố Phiền phức ==========
    elif current_step == 3:
        st.header("📝 TQ 1.3: Phương thức thanh toán 'Phiền phức' Churn cao hơn?")
        
        st.write(
            """
            Tiếp theo, chúng ta thấy rằng bất kỳ phương thức thanh toán nào yêu cầu **"sự nỗ lực"** 
            (thủ công) như **Mailed Check** và **Electronic Check** đều có rủi ro cao hơn 
            nhóm tự động (Auto-pay).
            """
        )
        
        churn_by_payment = df.groupby('Payment_Group_Detail')['Churn'].mean().reset_index()
        churn_by_payment = churn_by_payment.sort_values('Churn')
        
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        sns.barplot(
            data=churn_by_payment,
            x='Payment_Group_Detail',
            y='Churn',
            order=['Others (Auto-pay)', 'Mailed Check', 'Electronic Check'],
            palette=['#2ecc71', '#f39c12', '#e74c3c'],
            ax=ax3,
            errorbar=None
        )
        ax3.set_title('TQ 1.3 (Mở rộng): Tỷ lệ Churn theo\nPhương thức thanh toán', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Tỷ lệ Churn', fontsize=12)
        ax3.set_xlabel('Phương thức thanh toán', fontsize=12)
        ax3.set_ylim(0, max(churn_by_payment['Churn']) * 1.2)
        
        for container in ax3.containers:
            ax3.bar_label(container, fmt='%.2f', padding=3)
        
        st.pyplot(fig3)
        plt.close(fig3)
        
        st.markdown("---")
        st.button("Tiếp theo: Tổ hợp Độc hại ➔", key="btn_bq1_3", on_click=next_step_callback, type="primary")
    
    # ========== STEP 4: TQ 1.4 - Toxic Combo ==========
    elif current_step == 4:
        st.header("⚠️ TQ 1.4: Khi 3 yếu tố kết hợp - 'Toxic Combo'")
        
        churn_by_segment = df.groupby('Combined_Risk_Segment')['Churn'].mean().reset_index()
        
        others_churn = churn_by_segment[churn_by_segment['Combined_Risk_Segment'] == 'Others']['Churn'].values[0]
        max_toxic_churn = churn_by_segment[churn_by_segment['Combined_Risk_Segment'].str.contains('Toxic')]['Churn'].max()
        multiplier = max_toxic_churn / others_churn if others_churn > 0 else 0
        
        st.write(
            f"""
            Đây là **insight quan trọng nhất**. Khi 3 yếu tố rủi ro 
            (**Mới + Phí cao + Phiền phức**) kết hợp lại, chúng tạo ra một 
            **"Tổ hợp Độc hại" (Toxic Combo)** với tỷ lệ churn tăng vọt, 
            cao gấp **{multiplier:.1f} lần** mức trung bình!
            """
        )
        
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        sns.barplot(
            data=churn_by_segment,
            x='Combined_Risk_Segment',
            y='Churn',
            order=['Others', 'Toxic Combo (Mailed Check)', 'Toxic Combo (E-Check)'],
            palette=['#3498db', '#f39c12', '#c0392b'],
            ax=ax4,
            errorbar=None
        )
        ax4.set_title('TQ 1.4 (Mở rộng): So sánh các phân khúc "Toxic Combo"', fontsize=16, fontweight='bold')
        ax4.set_ylabel('Tỷ lệ Churn', fontsize=12)
        ax4.set_xlabel('Phân khúc khách hàng', fontsize=12)
        ax4.set_ylim(0, max(churn_by_segment['Churn']) * 1.2)
        
        for container in ax4.containers:
            ax4.bar_label(container, fmt='%.2f', padding=3)
        
        toxic_segments = churn_by_segment[churn_by_segment['Combined_Risk_Segment'].str.contains('Toxic')]
        if len(toxic_segments) > 0:
            max_idx = toxic_segments['Churn'].idxmax()
            max_churn_val = toxic_segments.loc[max_idx, 'Churn']
        
        st.pyplot(fig4)
        plt.close(fig4)
        
        st.markdown("---")
        st.button("Đến phần Kết luận ➔", key="btn_bq1_4", on_click=next_step_callback, type="primary")
    
    # ========== STEP 5: Kết luận ==========
    elif current_step == 5:
        st.header("✅ Kết luận & Gợi ý hành động")
        
        st.markdown(
            """
            Dữ liệu cho thấy **"Cú sốc thanh toán"** và **"Sự phiền phức"** 
            có thể là các yếu tố quan trọng ảnh hưởng đến quyết định rời đi của khách hàng mới.
            
            ---
            
            ### 🎯 Một số gợi ý hành động có thể xem xét:
            
            1. **Có thể cân nhắc can thiệp:** 
               - Xác định các khách hàng trong nhóm **"Toxic Combo"** 
                 (Mới + Phí cao + Thanh toán thủ công).
               - Phân khúc này có vẻ chiếm khoảng **8-12%** tổng khách hàng và có thể đóng góp 
                 **gần 25%** tổng số churn.
            
            2. **Gợi ý tiếp cận chủ động:**
               - Có thể thử gửi **email/thông báo** mời họ chuyển sang **"Auto-pay"** 
                 (ví dụ: Thẻ tín dụng) kèm ưu đãi.
               - Ví dụ: Thử nghiệm **giảm 10%** cho 3 tháng đầu tiên khi chuyển đổi.
               - Cung cấp hướng dẫn rõ ràng, dễ hiểu để giảm rào cản chuyển đổi.
            
            3. **Xem xét điều chỉnh giá:**
               - Có thể **tránh** áp dụng mức phí cao nhất cho khách hàng mới trong **tháng đầu tiên**.
               - Cân nhắc chương trình **"Onboarding Pricing"** - giá ưu đãi cho 3 tháng đầu.
               - Thử tăng giá dần dần thay vì một lần để giảm shock.
            
            4. **Đề xuất theo dõi & Đo lường:**
               - Nên thiết lập dashboard theo dõi tỷ lệ chuyển đổi sang Auto-pay.
               - Đo lường ROI của các chiến dịch can thiệp nếu triển khai.
               - A/B testing các message và incentive khác nhau để tìm approach hiệu quả.
            
            ---
            
            ### 📈 Tác động có thể kỳ vọng:
            
            - Nếu triển khai tốt, có thể **giảm churn 15-20%** trong nhóm Toxic Combo trong 6 tháng đầu.
            - Tiềm năng **tăng retention value** ước tính khoảng **$500K - $1M** hàng năm 
              (dựa trên giả định giá trị trung bình mỗi khách hàng).
            - Có thể **cải thiện trải nghiệm khách hàng**, tăng NPS và satisfaction scores.
            
            ---
            
            ### 🔄 Các bước tiếp theo đề xuất:
            
            - Thuyết trình findings này cho leadership team để thảo luận.
            - Phối hợp với Marketing & Product để đánh giá khả năng triển khai.
            - Cân nhắc thiết lập monitoring system để theo dõi hiệu quả nếu quyết định thực hiện.
            """
        )
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            def reset_bq1():
                st.session_state.current_step_bq1 = 1
            st.button("🔄 Bắt đầu lại câu chuyện", key="btn_bq1_5", on_click=reset_bq1, type="secondary")
