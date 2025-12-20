# 🔍 Customer Churn Analysis - Data Storytelling

Ứng dụng phân tích dữ liệu tương tác được xây dựng bằng Streamlit, nghiên cứu các yếu tố ảnh hưởng đến tình trạng rời bỏ dịch vụ (churn) của khách hàng thông qua phương pháp Data Storytelling.

## �‍💻 Tác giả

- **Sinh viên thực hiện**: Vũ Thế Vinh
- **Giảng viên hướng dẫn**: Trần Hưng Nghiệp

## �📋 Tổng quan

Project này phân tích dữ liệu churn của khách hàng qua 2 Business Questions chính:

- **BQ1**: "Cú sốc thanh toán" & "Sự phiền phức" có phải là lý do chính đẩy khách hàng mới rời đi không?
- **BQ2**: "Sự thất vọng" (Frustration) có phải là tín hiệu Churn mạnh hơn "Sự chán nản" (Thiếu gắn bó) không?

## ✨ Tính năng

- 📊 **Guided Flow Analysis**: Hướng dẫn từng bước phân tích dữ liệu
- 📈 **Interactive Visualizations**: Biểu đồ tương tác với Matplotlib & Seaborn
- 🎯 **Business-Focused Questions**: Tập trung vào các câu hỏi kinh doanh thực tế
- 💡 **Data Storytelling**: Trình bày phân tích theo cách dễ hiểu và có cấu trúc

## 🚀 Cài đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- pip hoặc conda

### Các bước cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd project-1-eda
```

2. Tạo môi trường ảo (khuyến nghị):
```bash
# Sử dụng venv
python -m venv venv

# Kích hoạt môi trường ảo
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## 📦 Dependencies

Tạo file `requirements.txt` với nội dung sau:

```
streamlit>=1.28.0
pandas>=2.0.0
seaborn>=0.12.0
matplotlib>=3.7.0
numpy>=1.24.0
```

## 🎮 Sử dụng

Chạy ứng dụng Streamlit:

```bash
streamlit run story_app.py
```

Ứng dụng sẽ mở tại địa chỉ: `http://localhost:8501`

## 📁 Cấu trúc thư mục

```
project-1-eda/
│
├── story_app.py              # File chính của ứng dụng Streamlit
├── bq_modules/               # Modules xử lý các Business Questions
│   ├── __init__.py
│   ├── bq1_renderer.py       # Renderer cho BQ1 (Toxic Combo Analysis)
│   └── bq2_renderer.py       # Renderer cho BQ2 (Frustration Analysis)
│
├── data/                     # Dữ liệu
│   └── churn.csv            # Dataset churn
│
├── requirements.txt          # Dependencies
├── .gitignore               # Git ignore file
└── README.md                # Tài liệu này
```

## 📊 Dữ liệu

Dataset `churn.csv` chứa thông tin về khách hàng với các trường:

- **AccountAge**: Tuổi tài khoản (tháng)
- **MonthlyCharges**: Phí hàng tháng
- **PaymentMethod**: Phương thức thanh toán
- **ViewingHoursPerWeek**: Số giờ xem hàng tuần
- **Churn**: Trạng thái churn (0: không, 1: có)
- Và các trường khác...

## 🔍 Phân tích chính

### Business Question 1: Toxic Combo Analysis

Phân tích ảnh hưởng của "cú sốc thanh toán" và "sự phiền phức" đối với khách hàng mới:

- **TQ 1.1**: Yếu tố tuổi tài khoản
- **TQ 1.2**: Yếu tố mức phí
- **TQ 1.3**: Yếu tố phiền phức (phương thức thanh toán)
- **TQ 1.4**: Toxic Combo (kết hợp các yếu tố)

### Business Question 2: Frustration vs Boredom Analysis

So sánh tín hiệu churn giữa "sự thất vọng" và "thiếu gắn bó":

- **TQ 2.1**: Yếu tố gắn bó (Viewing Hours)
- **TQ 2.2**: Thất vọng qua Support Tickets
- **TQ 2.3**: Thất vọng qua User Rating

## 🛠️ Công nghệ sử dụng

- **Streamlit**: Framework web app cho Data Science
- **Pandas**: Xử lý và phân tích dữ liệu
- **Seaborn & Matplotlib**: Visualization
- **NumPy**: Tính toán số học

## 📝 License

Dự án này được phát triển cho mục đích học tập và nghiên cứu.

