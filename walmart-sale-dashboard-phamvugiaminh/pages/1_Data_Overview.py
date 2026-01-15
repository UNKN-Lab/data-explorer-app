import streamlit as st
import pandas as pd
import numpy as np
from utils import get_raw_data


st.title("Data Overview")
df = get_raw_data()

# ============================
# Dataset Info
# ============================
st.subheader("Dataset Info")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Rows", f"{len(df):,}")
with col2:
    st.metric("Columns", f"{df.shape[1]:,}")
with col3:
    st.markdown("**Tables**")
    st.markdown("Walmart_Sales.csv")
with col4:
    if 'Date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Date']):
        min_d = df['Date'].min()
        max_d = df['Date'].max()
        st.markdown("**Date Range**")
        st.markdown(f"{min_d.date()} → {max_d.date()}")
    else:
        st.markdown("**Date Range**")
        st.markdown("N/A")

# ============================
# Schema / Data Dictionary
# ============================
st.subheader("Schema / Data Dictionary")

# Classify dtypes
def classify_series_dtype(s: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(s):
        return "datetime"
    if pd.api.types.is_numeric_dtype(s):
        return "numeric"
    if pd.api.types.is_bool_dtype(s):
        return "category"
    return "category"

col_descriptions = {
    "Store": "Unique store identifier",
    "Date": "Week-ending date for the record",
    "Weekly_Sales": "Sales for the store and week ($)",
    "Holiday_Flag": "1 if week includes a major holiday, else 0",
    "Temperature": "Avg weekly temperature (°F)",
    "Fuel_Price": "Regional fuel price ($)",
    "CPI": "Consumer Price Index",
    "Unemployment": "Unemployment rate (%)",
    "Climate_Group": "Cluster/group label by climate characteristics",
}

schema_df = pd.DataFrame({
    "Column": df.columns,
    "Type": [classify_series_dtype(df[c]) for c in df.columns],
    "Description": [col_descriptions.get(c, "") for c in df.columns],
})
st.dataframe(schema_df, use_container_width=True, hide_index=True)

# ============================
# Missing Values Summary
# ============================
st.subheader("Missing Values Summary")
miss_count = df.isna().sum()
miss_pct = (miss_count / len(df) * 100).round(2)
missing_df = pd.DataFrame({
    "Column": df.columns,
    "Missing": miss_count.values,
    "Missing_%": miss_pct.values
}).sort_values("Missing", ascending=False)
st.dataframe(missing_df, use_container_width=True, hide_index=True)

# ============================
# Basic Statistics
# ============================
st.subheader("Basic Statistics")
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if num_cols:
    stats = pd.DataFrame({
        "mean": df[num_cols].mean(),
        "median": df[num_cols].median(),
        "min": df[num_cols].min(),
        "max": df[num_cols].max(),
        "std": df[num_cols].std(),
    })
    stats["range"] = stats["max"] - stats["min"]
    st.dataframe(stats.round(2), use_container_width=True)
else:
    st.info("No numeric columns detected.")


# ============================
# Preview Data
# ============================
st.subheader("Preview Data")
head_n = st.slider("Rows to preview (head)", 5, 10, 5, step=1)
st.dataframe(df.head(head_n), use_container_width=True)

if st.checkbox("Show random sample"):
    sample_n = st.slider("Sample size", 5, 50, 10, step=5)
    st.dataframe(df.sample(min(sample_n, len(df)), random_state=42), use_container_width=True)

