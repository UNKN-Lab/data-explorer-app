import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd
from lib.data import get_data


st.title("Climate Impact")
df = get_data()

if {'Temperature', 'Weekly_Sales'}.issubset(df.columns):
    color_col = 'Climate_Group' if 'Climate_Group' in df.columns else None
    sample_n = st.slider("Sample points (for speed)", 2000, 15000, 6000, step=1000)
    plot_df = df[['Temperature', 'Weekly_Sales', 'Climate_Group']].dropna().copy() if color_col else df[['Temperature', 'Weekly_Sales']].dropna().copy()
    if len(plot_df) > sample_n:
        plot_df = plot_df.sample(sample_n, random_state=42)

    fig = px.scatter(
        plot_df,
        x='Temperature', y='Weekly_Sales',
        color=color_col,
        opacity=0.45,
        template='plotly_white',
        labels={'Weekly_Sales': 'Weekly Sales ($)', 'Temperature': 'Temperature (°F)'},
        title="Temperature vs Weekly Sales"
    )
    st.plotly_chart(fig, use_container_width=True)

# Insights
st.markdown("**Insights**")
points = []
if {'Temperature', 'Weekly_Sales'}.issubset(df.columns):
    tmp = df[['Temperature', 'Weekly_Sales']].dropna().copy()
    corr = float(tmp['Temperature'].corr(tmp['Weekly_Sales']))
    direction = "positive" if corr > 0 else "negative" if corr < 0 else "neutral"
    points.append(f"Overall {direction} relationship between temperature and sales (corr {corr:.2f}).")
    if 'Climate_Group' in df.columns and df['Climate_Group'].notna().any():
        grp = df.dropna(subset=['Climate_Group'])[['Temperature', 'Weekly_Sales', 'Climate_Group']].copy()
        grp_corr = grp.groupby('Climate_Group').apply(lambda x: x['Temperature'].corr(x['Weekly_Sales'])).dropna()
        if not grp_corr.empty:
            strongest = grp_corr.abs().idxmax()
            points.append(f"Climate group {int(strongest)} shows strongest temp–sales link (corr {grp_corr.loc[strongest]:.2f}).")
for p in points[:3]:
    st.markdown(f"- {p}")

# Strategy Recommendation
st.markdown("**Strategy Recommendation**")
st.markdown("- Scale seasonal assortments in regions where warmth lifts demand.")
st.markdown("- Adjust staffing and replenishment when temperature deviates from seasonal norms.")

