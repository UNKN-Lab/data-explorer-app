import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from lib.data import get_data


st.title("Sales Trend")
df = get_data()

if {'Date', 'Weekly_Sales'}.issubset(df.columns):
    agg = (
        df.groupby('Date', as_index=False)['Weekly_Sales']
        .sum()
        .sort_values('Date')
    )
    window = st.slider("Smoothing window (weeks)", 2, 12, 4, step=1)
    agg['SMA'] = agg['Weekly_Sales'].rolling(window=window, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agg['Date'], y=agg['Weekly_Sales'],
        mode='lines', name='Weekly Sales',
        line=dict(color='#1f77b4', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=agg['Date'], y=agg['SMA'],
        mode='lines', name=f'{window}-wk Avg',
        line=dict(color='#ff7f0e', width=3, dash='dash')
    ))
    fig.update_layout(
        template='plotly_white',
        title="Weekly Sales and Moving Average",
        xaxis_title="Date",
        yaxis_title="Sales ($)",
        legend_title="Series"
    )
    st.plotly_chart(fig, use_container_width=True)

# Insights
st.markdown("**Insights**")
insights = []
if {'Date', 'Weekly_Sales'}.issubset(df.columns):
    s = df.groupby('Date')['Weekly_Sales'].sum().sort_index()
    recent = float(s.tail(4).mean())
    prior = float(s.tail(8).head(4).mean()) if len(s) >= 8 else float(s.head(4).mean())
    momentum = "accelerating" if recent > prior else "softening" if recent < prior else "stable"
    insights.append(f"Recent 4-week average is ${recent:,.0f} vs prior ${prior:,.0f}.")
    insights.append(f"Sales momentum appears {momentum}.")
for i in insights[:2]:
    st.markdown(f"- {i}")

# Strategy Recommendation
st.markdown("**Strategy Recommendation**")
st.markdown("- Align promotions with periods of rising momentum to maximize lift.")
st.markdown("- In softening phases, tighten inventory and focus on high-velocity SKUs.")


