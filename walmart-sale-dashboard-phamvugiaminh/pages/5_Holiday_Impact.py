import streamlit as st
import plotly.express as px
import pandas as pd
from utils import get_data


st.title("Holiday Impact")
df = get_data()

if {'Holiday_Flag', 'Weekly_Sales'}.issubset(df.columns):
    agg = (
        df.groupby('Holiday_Flag', as_index=False)['Weekly_Sales']
        .mean()
        .rename(columns={'Weekly_Sales': 'Avg_Weekly_Sales'})
    )
    agg['Week_Type'] = agg['Holiday_Flag'].map({1: 'Holiday', 0: 'Non-Holiday'})
    fig = px.bar(
        agg, x='Week_Type', y='Avg_Weekly_Sales',
        template='plotly_white',
        title="Average Weekly Sales: Holiday vs Non-Holiday",
        labels={'Avg_Weekly_Sales': 'Avg Weekly Sales ($)', 'Week_Type': 'Week Type'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Insights
st.markdown("**Insights**")
if {'Holiday_Flag', 'Weekly_Sales'}.issubset(df.columns):
    pivot = df.groupby('Holiday_Flag')['Weekly_Sales'].mean()
    hol = float(pivot.get(1, float('nan')))
    non = float(pivot.get(0, float('nan')))
    if pd.notna(hol) and pd.notna(non) and non != 0:
        lift = (hol - non) / non * 100
        st.markdown(f"- Holiday weeks average ${hol:,.0f} vs ${non:,.0f} non-holiday.")
        st.markdown(f"- Holiday lift of {lift:.1f}% over typical weeks.")
    else:
        st.markdown("- Insufficient data to compute holiday lift.")
else:
    st.markdown("- Holiday flag not available.")

# Strategy Recommendation
st.markdown("**Strategy Recommendation**")
st.markdown("- Increase inventory, staffing, and checkout capacity during holiday periods.")
st.markdown("- Launch targeted promotions 2–3 weeks pre-holiday to capture early demand.")
