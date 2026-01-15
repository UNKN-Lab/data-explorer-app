import streamlit as st
import plotly.express as px
import pandas as pd
from lib.data import get_data


st.title("Store Comparison")
df = get_data()

if {'Store', 'Weekly_Sales'}.issubset(df.columns):
    top_n = st.slider("Top N stores by average weekly sales", 5, 50, 15, step=5)
    store_avg = (
        df.groupby('Store', as_index=False)['Weekly_Sales']
        .mean()
        .sort_values('Weekly_Sales', ascending=False)
        .head(top_n)
    )
    fig = px.bar(
        store_avg,
        x='Store', y='Weekly_Sales',
        template='plotly_white',
        title=f"Top {top_n} Stores by Avg Weekly Sales",
        labels={'Weekly_Sales': 'Avg Weekly Sales ($)', 'Store': 'Store'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Insights
st.markdown("**Insights**")
bullets = []
if {'Store', 'Weekly_Sales'}.issubset(df.columns):
    s = df.groupby('Store')['Weekly_Sales'].mean().sort_values(ascending=False)
    lead = s.iloc[0]
    median = s.median()
    bullets.append(f"Top store averages ${lead:,.0f} per week; median store ${median:,.0f}.")
    spread = s.quantile(0.9) - s.quantile(0.1)
    bullets.append(f"Performance spread (90th–10th pct) is ${spread:,.0f}.")
for b in bullets[:2]:
    st.markdown(f"- {b}")

# Strategy Recommendation
st.markdown("**Strategy Recommendation**")
st.markdown("- Replicate winning playbooks from top stores (assortment, staffing, promos).")
st.markdown("- Support trailing stores with targeted local assortment and demand shaping.")
