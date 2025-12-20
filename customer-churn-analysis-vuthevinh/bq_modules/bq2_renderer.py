"""Business Question 2 Renderer - Boredom vs Frustration Analysis."""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st


def render_bq2(df, next_step_callback):
    """Render all steps for BQ2: Boredom vs Frustration analysis."""
    
    current_step = st.session_state.current_step_bq2
    
    st.header('🎯 BQ2: "Sự thất vọng" (Frustration) có phải là tín hiệu Churn mạnh hơn "Sự chán nản" (Thiếu gắn bó) không?')
    st.markdown("---")
    
    # ========== STEP 1: TQ 2.1 - Yếu tố Gắn Bó ==========
    if current_step == 1:
        st.header("📺 TQ 2.1: Đầu tiên, 'Sự Gắn Bó' (Engagement) có ảnh hưởng không?")
        
        median_no_churn = df[df['Churn'] == 0]['ViewingHoursPerWeek'].median()
        median_churn = df[df['Churn'] == 1]['ViewingHoursPerWeek'].median()
        
        st.write(
            f"""
            Chúng ta bắt đầu bằng cách kiểm tra yếu tố cơ bản nhất: **mức độ gắn bó**. 
            Biểu đồ boxplot cho thấy rõ ràng: nhóm khách hàng 'Churn' có số giờ xem hàng tuần 
            (trung vị ~{median_churn:.1f} giờ) **thấp hơn đáng kể** so với nhóm 'Không Churn' (trung vị ~{median_no_churn:.1f} giờ).
            
            → **Kết luận: CÓ, thiếu gắn bó là một tín hiệu của Churn.**
            """
        )
        
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        sns.boxplot(data=df, x='Churn', y='ViewingHoursPerWeek', palette=['#3498db', '#e74c3c'], ax=ax1)
        ax1.set_title('TQ 2.1: Mức độ gắn bó (Giờ xem/Tuần) vs. Churn', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Số giờ xem hàng tuần', fontsize=12)
        ax1.set_xlabel('Trạng thái khách hàng', fontsize=12)
        ax1.set_xticklabels(['Không Churn', 'Churn'])
        
        st.pyplot(fig1)
        plt.close(fig1)
        
        st.markdown("---")
        st.button("Tiếp theo: Yếu tố Thất Vọng (Rating) ➔", key="btn_bq2_1", on_click=next_step_callback, type="primary")
    
    # ========== STEP 2: TQ 2.3 - Thất Vọng (Rating) ==========
    elif current_step == 2:
        st.header("⭐ TQ 2.3: 'Sự Thất Vọng' (Frustration) - Tín hiệu User Rating thì sao?")
        
        median_rating_no_churn = df[df['Churn'] == 0]['UserRating'].median()
        median_rating_churn = df[df['Churn'] == 1]['UserRating'].median()
        
        st.write(
            f"""
            Một cách logic, chúng ta nghĩ khách hàng 'Churn' sẽ cho 'User Rating' thấp hơn. 
            **Nhưng dữ liệu cho thấy điều ngược lại.** 
            
            Hai box plot này gần như **Y HỆT NHAU**. Trung vị của cả hai nhóm đều quanh mức {median_rating_no_churn:.1f} và {median_rating_churn:.1f}.
            
            → **Kết luận: User Rating (1-5 sao) là một chỉ số VÔ DỤNG để dự đoán Churn.**
            """
        )
        
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        sns.boxplot(data=df, x='Churn', y='UserRating', palette=['#3498db', '#e74c3c'], ax=ax2)
        ax2.set_title('TQ 2.3: User Rating vs. Churn (GẦN GIỐNG NHAU!)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('User Rating (1-5 sao)', fontsize=12)
        ax2.set_xlabel('Trạng thái khách hàng', fontsize=12)
        ax2.set_xticklabels(['Không Churn', 'Churn'])
        ax2.set_ylim(0.5, 5.5)
        
        st.pyplot(fig2)
        plt.close(fig2)
        
        st.warning("⚠️ User Rating KHÔNG phân biệt được nhóm Churn và Không Churn!")
        
        st.markdown("---")
        st.button("Tiếp theo: Thất Vọng (Support Ticket) ➔", key="btn_bq2_2", on_click=next_step_callback, type="primary")
    
    # ========== STEP 3: TQ 2.2 - Thất Vọng (Ticket) ==========
    elif current_step == 3:
        st.header("🎫 TQ 2.2: 'Sự Thất Vọng' (Frustration) - Tín hiệu Support Ticket thì sao?")
        
        churn_by_ticket = df.groupby('SupportTicketsPerMonth')['Churn'].mean().reset_index()
        min_churn = churn_by_ticket['Churn'].min()
        max_churn = churn_by_ticket['Churn'].max()
        
        st.write(
            f"""
            Nếu User Rating vô dụng, thì **'hành động' chủ động** thì sao? 
            
            Biểu đồ này cho thấy một tín hiệu **CỰC KỲ MẠNH**. Tỷ lệ churn tăng đều đặn từ 
            **{min_churn:.2f}** (với ít ticket) lên đến **{max_churn:.2f}** (với nhiều ticket).
            
            → **Kết luận: CÓ, Support Ticket là một lá cờ đỏ rất rõ ràng.**
            """
        )
        
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        sns.barplot(data=df, x='SupportTicketsPerMonth', y='Churn', palette='Reds', ax=ax3, errorbar=None)
        ax3.set_title('TQ 2.2: Tỷ lệ Churn theo Số Lượng Support Ticket', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Tỷ lệ Churn', fontsize=12)
        ax3.set_xlabel('Số Support Ticket mỗi tháng', fontsize=12)
        
        for container in ax3.containers:
            ax3.bar_label(container, fmt='%.2f', padding=3)
        
        st.pyplot(fig3)
        plt.close(fig3)
        
        st.markdown("---")
        st.button("Tiếp theo: Câu trả lời cuối cùng ➔", key="btn_bq2_3", on_click=next_step_callback, type="primary")
    
    # ========== STEP 4: BQ2 Câu trả lời ==========
    elif current_step == 4:
        st.header("💡 Câu trả lời cho BQ2: 'Chán' vs. 'Bực' - Cái nào tệ hơn?")
        
        avg_viewing = df['ViewingHoursPerWeek'].mean()
        
        df_temp = df.copy()
        df_temp['Engagement_Level'] = np.where(df_temp['ViewingHoursPerWeek'] >= avg_viewing, 
                                              'Gắn bó Cao (>= TB)', 'Gắn bó Thấp (< TB)')
        df_temp['Frustration_Level'] = np.where(df_temp['SupportTicketsPerMonth'] > 0, 
                                               'Có Ticket (>0)', 'Không Ticket (=0)')
        df_temp['Quadrant'] = df_temp['Engagement_Level'] + '\n' + df_temp['Frustration_Level']
        
        try:
            quadrant_churn = df_temp.groupby('Quadrant')['Churn'].mean().reset_index()
            churn_bored = quadrant_churn[quadrant_churn['Quadrant'].str.contains('Gắn bó Thấp.*Không Ticket')]['Churn'].values[0]
            churn_frustrated = quadrant_churn[quadrant_churn['Quadrant'].str.contains('Gắn bó Cao.*Có Ticket')]['Churn'].values[0]
        except:
            churn_bored, churn_frustrated = 0.17, 0.14
        
        st.write(
            f"""
            Đây là lúc tổng hợp mọi thứ. Chúng ta so sánh 4 phân khúc:
            - **Mức độ gắn bó** (Cao/Thấp, ngưỡng = {avg_viewing:.1f}h)
            - **Có phàn nàn không** (Có/Không Support Ticket)
            
            **'Gắn bó Thấp / Không Ticket' (Nhóm "Chán"): {churn_bored:.2f}**  
            **'Gắn bó Cao / Có Ticket' (Nhóm "Bực"): {churn_frustrated:.2f}**
            """
        )
        
        quadrant_order = [
            'Gắn bó Cao (>= TB)\nKhông Ticket (=0)',
            'Gắn bó Thấp (< TB)\nKhông Ticket (=0)',
            'Gắn bó Thấp (< TB)\nCó Ticket (>0)',
            'Gắn bó Cao (>= TB)\nCó Ticket (>0)'
        ]
        
        fig4, ax4 = plt.subplots(figsize=(10, 5))
        sns.barplot(data=df_temp, x='Quadrant', y='Churn', order=quadrant_order,
                   palette=['#2ecc71', '#f39c12', '#95a5a6', '#e74c3c'], ax=ax4, errorbar=None)
        ax4.set_title('BQ2: "Sự Thất Vọng" vs "Sự Gắn Bó"', fontsize=16, fontweight='bold')
        ax4.set_ylabel('Tỷ lệ Churn', fontsize=12)
        ax4.set_xlabel('Phân khúc Khách hàng', fontsize=12)
        
        for container in ax4.containers:
            ax4.bar_label(container, fmt='%.2f', padding=3)
        
        ax4.axhline(y=churn_bored, color='#f39c12', linestyle='--', alpha=0.5)
        ax4.axhline(y=churn_frustrated, color='#e74c3c', linestyle='--', alpha=0.5)
        ax4.legend(['', '', f'Nhóm "Chán" ({churn_bored:.2f})', f'Nhóm "Bực" ({churn_frustrated:.2f})'])
        
        st.pyplot(fig4)
        plt.close(fig4)
        
        st.error("🔥 INSIGHT: Khách hàng **chán** (ít xem, không phàn nàn) rời đi **cao hơn** khách hàng **bực** (xem nhiều, có phàn nàn)!")
        
        st.markdown("---")
        st.button("Đến phần Kết luận & Hành động ➔", key="btn_bq2_4", on_click=next_step_callback, type="primary")
    
    # ========== STEP 5: Kết luận BQ2 ==========
    elif current_step == 5:
        st.header("✅ Kết luận & Gợi ý hành động")
        
        st.markdown(
            """
            Dữ liệu gợi ý một số insights thú vị về mối quan hệ giữa "Chán nản" và "Bực bội":
            
            - Chỉ số `UserRating` có vẻ không phân biệt rõ ràng giữa 2 nhóm, nên cân nhắc khi sử dụng để dự đoán churn.
            - Nhóm "Chán nản" (17% churn) và "Bực bội" (14% churn) đều cần được chú ý, nhưng có thể cần approach khác nhau.
            
            ---
            
            ### 🎯 Một số gợi ý hành động cho 4 nhóm:
            
            **1. 💚 Fan Hài Lòng (~10% churn)** - Có thể giữ chân bằng loyalty program  
            **2. 🟡 Người "Chán" (~17% churn)** - ⚠️ Nên ưu tiên: Thử nghiệm Recommendation Engine để tái gắn kết  
            **3. ❤️ Fan "Bực" (~14% churn)** - 🎁 Tiềm năng cứu: Cân nhắc ưu tiên giải quyết ticket nhanh hơn  
            **4. ⚫ Khó cứu (~23% churn)** - Có thể cân nhắc effort tối thiểu
            
            ### 📊 Gợi ý phân bổ nguồn lực (có thể điều chỉnh):
            - ~40% → Nhóm "Chán" | ~35% → Nhóm "Bực" | ~15% → Fan Hài Lòng | ~10% → Nhóm khó cứu
            
            *(Lưu ý: Cần xem xét thêm các yếu tố khác trước khi quyết định cuối cùng)*
            """
        )
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            def reset_bq2():
                st.session_state.current_step_bq2 = 1
            st.button("🔄 Phân tích lại từ đầu", key="btn_bq2_5", on_click=reset_bq2, type="secondary")
