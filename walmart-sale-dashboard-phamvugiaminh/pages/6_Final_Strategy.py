import streamlit as st
import plotly.express as px
import pandas as pd
from lib.data import get_data


st.title("Final Strategy")
df = get_data()

# Plot: Opportunity view by Climate Group (if available), else by Store top-10
if 'Climate_Group' in df.columns and df['Climate_Group'].notna().any():
    grp = (
        df.dropna(subset=['Climate_Group'])
        .groupby('Climate_Group', as_index=False)['Weekly_Sales']
        .mean()
        .sort_values('Weekly_Sales', ascending=False)
    )
    fig = px.bar(
        grp, x='Climate_Group', y='Weekly_Sales',
        template='plotly_white',
        title="Average Weekly Sales by Climate Group",
        labels={'Weekly_Sales': 'Avg Weekly Sales ($)', 'Climate_Group': 'Climate Group'}
    )
    st.plotly_chart(fig, use_container_width=True)
elif {'Store', 'Weekly_Sales'}.issubset(df.columns):
    top = (
        df.groupby('Store', as_index=False)['Weekly_Sales']
        .mean()
        .sort_values('Weekly_Sales', ascending=False)
        .head(10)
    )
    fig = px.bar(
        top, x='Store', y='Weekly_Sales',
        template='plotly_white',
        title="Top 10 Stores by Avg Weekly Sales",
        labels={'Weekly_Sales': 'Avg Weekly Sales ($)', 'Store': 'Store'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Insights (concise roll-up)
st.markdown("**Insights**")
insights = []
if {'Date', 'Weekly_Sales'}.issubset(df.columns):
    s = df.groupby('Date')['Weekly_Sales'].sum()
    head_avg = float(s.head(4).mean())
    tail_avg = float(s.tail(4).mean())
    trend = "rising" if tail_avg > head_avg else "declining" if tail_avg < head_avg else "stable"
    insights.append(f"Overall demand is {trend} into recent periods.")
if 'Holiday_Flag' in df.columns:
    hol = df.groupby('Holiday_Flag')['Weekly_Sales'].mean()
    if 0 in hol and 1 in hol and hol[0]:
        lift = (hol[1] - hol[0]) / hol[0] * 100
        insights.append(f"Holiday lift ≈ {lift:.1f}%.")
if 'Climate_Group' in df.columns and df['Climate_Group'].notna().any():
    grp_avg = df.dropna(subset=['Climate_Group']).groupby('Climate_Group')['Weekly_Sales'].mean()
    if len(grp_avg) >= 2:
        uplift = (grp_avg.max() - grp_avg.min()) / grp_avg.min() * 100 if grp_avg.min() else 0
        insights.append(f"Climate segments differ by ≈ {uplift:.1f}% in avg sales.")
for i in insights[:3]:
    st.markdown(f"- {i}")

# Strategy Recommendation (actionable, prioritized)
st.markdown("**Strategy Recommendation**")
st.markdown("- Scale inventory and labor into peak holiday windows; pre-build 2–3 weeks ahead.")
st.markdown("- Localize seasonal assortments by climate segment; emphasize warm-weather goods where relevant.")
st.markdown("- Replicate top-store playbooks (assortment, ops cadence, promo timing) across similar markets.")
st.markdown("- Use trend momentum to time promotions; shift budgets when momentum softens.")



