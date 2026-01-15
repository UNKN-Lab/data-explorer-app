# 🛒 Walmart Sales Explorer Dashboard

An interactive data analytics dashboard built with **Streamlit** for exploring and analyzing Walmart retail sales data. This project provides comprehensive insights into sales performance, climate impact, holiday effects, and actionable business strategies.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [Data Description](#-data-description)
- [Business Questions](#-business-questions)
- [Tech Stack](#-tech-stack)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)

---

## 🎯 Overview

This dashboard analyzes Walmart's historical weekly sales data across 45 stores, exploring patterns related to:

- **Temporal trends** – Weekly, monthly, and yearly sales patterns
- **Climate impact** – How temperature-based store clustering affects performance
- **Holiday effects** – Sales uplift during holiday weeks vs. non-holiday weeks
- **Store comparison** – Performance benchmarking across all stores
- **Statistical analysis** – Hypothesis testing and effect size measurements

The project answers two key business questions with rigorous statistical methods and machine learning interpretability techniques.

---

## ✨ Features

| Page | Description |
|------|-------------|
| **🏠 Home** | Landing page with overview metrics, quick EDA, and navigation guide |
| **📊 Data Overview** | Dataset structure, data types, and basic statistics |
| **📈 Sales Trend** | Time-series analysis with interactive date filtering |
| **🌡️ Climate Impact** | Sales performance segmented by climate clusters |
| **🏪 Store Comparison** | Store-level performance ranking and benchmarking |
| **🎄 Holiday Impact** | Holiday vs. non-holiday sales comparison |
| **📋 Final Strategy** | Actionable business recommendations |
| **🔍 EDA** | Comprehensive exploratory data analysis |
| **❓ Business Question 1** | Statistical analysis: Does climate group affect sales? |
| **❓ Business Question 2** | ML-powered analysis: Is holiday effect uniform across stores? |

---

## 📁 Project Structure

```
walmart-sale-dashboard/
├── Home.py                     # Main entry point / landing page
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── walmart_sales_analysis.ipynb # Jupyter notebook with full analysis
├── .streamlit/                 # Streamlit configuration
├── data/
│   ├── Walmart_Sales.csv                        # Raw dataset
│   ├── Walmart_Sales_cleaned.csv                # Cleaned dataset
│   └── Walmart_Sales_processed_with_climate.csv # Dataset with climate clusters
├── lib/
│   └── data.py                 # Data loading and caching utilities
└── pages/
    ├── 1_Data_Overview.py      # Dataset structure exploration
    ├── 2_Sales_Trend.py        # Time-series analysis
    ├── 3_Climate_Impact.py     # Climate-based segmentation
    ├── 4_Store_Comparison.py   # Store performance comparison
    ├── 5_Holiday_Impact.py     # Holiday sales analysis
    ├── 6_Final_Strategy.py     # Business recommendations
    ├── 7_EDA.py                # Exploratory data analysis
    ├── 8_Business_Question_1.py # Climate impact statistical tests
    └── 9_Business_Question_2.py # Holiday effect ML analysis
```

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/walmart-sale-dashboard.git
   cd walmart-sale-dashboard
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## 💻 Usage

### Run the Dashboard

```bash
streamlit run Home.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

### Navigation

- Use the **sidebar** to navigate between different analysis pages
- The **Home** page provides quick access to key metrics and inline EDA
- Each page is self-contained with its own visualizations and insights

---

## 📊 Data Description

### Dataset Overview

| Column | Description |
|--------|-------------|
| `Store` | Store identifier (1-45) |
| `Date` | Week of sales |
| `Weekly_Sales` | Total sales for the given store and week |
| `Holiday_Flag` | Whether the week is a special holiday week (1 = Yes, 0 = No) |
| `Temperature` | Average temperature in the region |
| `Fuel_Price` | Cost of fuel in the region |
| `CPI` | Consumer Price Index |
| `Unemployment` | Unemployment rate |
| `Climate_Group` | Temperature-based cluster (1-5) |

### Climate Groups

Stores are clustered into 5 climate groups based on temperature patterns:

| Group | Description |
|-------|-------------|
| 1 | Cold, high variation |
| 2 | Warm, stable |
| 3 | Hot, very stable |
| 4 | Mild, relatively stable |
| 5 | Hot, high variation |

### Key Statistics

- **Records**: ~6,400+ weekly observations
- **Stores**: 45 unique stores
- **Time Period**: ~2.5 years of data
- **Holiday Weeks**: Super Bowl, Labor Day, Thanksgiving, Christmas

---

## ❓ Business Questions

### Business Question 1: Climate Group Impact

> **Does weekly sales significantly differ among the climate groups?**

**Methodology:**
- Shapiro-Wilk test for normality
- Levene test for variance equality
- Kruskal-Wallis test for group differences
- Effect size analysis (Epsilon-squared)

**Key Findings:**
- Climate groups have **statistically significant** different sales patterns
- Stable climates show more predictable sales
- Effect persists even after removing holiday influences

---

### Business Question 2: Holiday Effect Uniformity

> **Is the holiday effect uniform across stores, or do some stores benefit more?**

**Methodology:**
- Holiday lift calculation per store
- Random Forest Regressor for prediction
- SHAP (SHapley Additive exPlanations) for interpretability

**Key Findings:**
- Holiday effect is **NOT uniform** across stores
- Stores with high fuel prices and warm temperatures benefit less
- High-performing stores have limited additional growth during holidays

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Framework** | Streamlit |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly, Matplotlib, Seaborn |
| **Statistical Analysis** | SciPy (Shapiro-Wilk, Levene, Kruskal-Wallis) |
| **Machine Learning** | Scikit-learn (Random Forest) |
| **Model Interpretability** | SHAP |
| **Time Series** | Statsmodels |

---

## 📸 Screenshots

### Home Dashboard
The landing page provides an overview of total sales, average weekly sales, and a time-series chart for quick insights.

### Business Question Analysis
Interactive statistical tests and SHAP visualizations help explain the factors driving sales performance.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

For questions or feedback, please open an issue in the repository.

---

