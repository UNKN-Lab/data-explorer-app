import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# Optional heavy libs guarded so app can start even if not installed yet
try:
    import seaborn as sns
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    sns = None
    plt = None
try:
    from scipy.stats import levene, f_oneway
except ModuleNotFoundError:
    levene = f_oneway = None
from utils import get_data


st.set_page_config(
    page_title="Walmart Sales Explorer",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🛒 Walmart Sales Explorer")
st.caption("Unified landing & EDA quick access. Full analyses in dedicated pages.")

# Load once and share via session_state
if 'df' not in st.session_state:
    st.session_state['df'] = get_data()
df = st.session_state['df']

with st.sidebar:
    st.success(f"✅ Data loaded: {len(df):,} rows")
    if 'Date' in df.columns:
        st.info(f"Date range: {df['Date'].min().date()} → {df['Date'].max().date()}")
    if 'Store' in df.columns:
        st.info(f"Stores: {df['Store'].nunique():,}")
    st.markdown("---")
    st.markdown("**Tabs:** Overview | EDA")

overview_tab, eda_tab = st.tabs(["Overview", "EDA"])

with overview_tab:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_sales = float(df['Weekly_Sales'].sum()) if 'Weekly_Sales' in df.columns else 0.0
        st.metric("Total Sales", f"${total_sales:,.0f}")
    with col2:
        avg_weekly = float(df['Weekly_Sales'].mean()) if 'Weekly_Sales' in df.columns else 0.0
        st.metric("Avg Weekly Sales", f"${avg_weekly:,.0f}")
    with col3:
        num_weeks = df['Date'].nunique() if 'Date' in df.columns else len(df)
        st.metric("Weeks Covered", f"{int(num_weeks):,}")
    with col4:
        stores = df['Store'].nunique() if 'Store' in df.columns else 0
        st.metric("Stores", f"{int(stores):,}")

    st.markdown("---")
    if {'Date', 'Weekly_Sales'}.issubset(df.columns):
        daily = df.groupby('Date', as_index=False)['Weekly_Sales'].sum()
        fig = px.line(
            daily, x='Date', y='Weekly_Sales',
            title="Total Weekly Sales Over Time",
            template='plotly_white',
            labels={'Weekly_Sales': 'Weekly Sales ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    Use sidebar navigation for deeper dives:
    - Data_Overview: dataset structure
    - Sales_Trend: time-series focus
    - Climate_Impact: temperature clustering
    - Store_Comparison: performance ranking
    - Holiday_Impact: seasonal uplift
    - Final_Strategy: business recommendations
    """)

with eda_tab:
    st.subheader("Quick EDA Inline")
    st.caption("Condensed version of full EDA (page 7) for rapid reference.")

    # 1 Weekly Sales Over Time
    if {'Date','Weekly_Sales','Store'}.issubset(df.columns):
        store_select = st.multiselect("Stores (empty = all)", sorted(df['Store'].unique()))
        plot_df = df[df['Store'].isin(store_select)] if store_select else df
        fig_ts = px.line(plot_df, x='Date', y='Weekly_Sales', color='Store', title='Weekly Sales Over Time')
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.info("Missing Date/Store/Weekly_Sales for time-series plot.")

    # 2 Avg Weekly Sales per Store
    if 'Store' in df.columns and 'Weekly_Sales' in df.columns:
        store_avg = (df.groupby('Store')['Weekly_Sales'].mean().reset_index()
                       .rename(columns={'Weekly_Sales':'Avg_Weekly_Sales'}))
        fig_avg = px.bar(store_avg, x='Store', y='Avg_Weekly_Sales', color='Avg_Weekly_Sales',
                         title='Average Weekly Sales per Store')
        st.plotly_chart(fig_avg, use_container_width=True)
    # 3 Holiday vs Non-Holiday Avg & Total
    if 'Holiday_Flag' in df.columns and 'Weekly_Sales' in df.columns:
        holiday_avg = (df.groupby('Holiday_Flag')['Weekly_Sales'].mean().reset_index()
                         .rename(columns={'Weekly_Sales':'Avg_Weekly_Sales'}))
        fig_h_avg = px.bar(holiday_avg, x='Holiday_Flag', y='Avg_Weekly_Sales', title='Avg Weekly Sales (Holiday Flag)')
        st.plotly_chart(fig_h_avg, use_container_width=True)
    # 4 Top Sales Events
    if 'Weekly_Sales' in df.columns:
        top_df = df.nlargest(15,'Weekly_Sales')[['Date','Store','Weekly_Sales']] if 'Store' in df.columns else df.nlargest(15,'Weekly_Sales')[['Date','Weekly_Sales']]
        fig_top = px.scatter(top_df, x='Date', y='Weekly_Sales', color='Store' if 'Store' in top_df.columns else None,
                             size='Weekly_Sales', title='Top 15 Weekly Sales Events')
        st.plotly_chart(fig_top, use_container_width=True)
    # 5 Monthly Average
    if 'Date' in df.columns and 'Weekly_Sales' in df.columns:
        mdf = df.copy(); mdf['Month'] = mdf['Date'].dt.month
        month_avg = mdf.groupby('Month')['Weekly_Sales'].mean().reset_index().rename(columns={'Weekly_Sales':'Avg_Monthly_Sales'})
        fig_month = px.bar(month_avg, x='Month', y='Avg_Monthly_Sales', color='Avg_Monthly_Sales', title='Average Monthly Sales')
        st.plotly_chart(fig_month, use_container_width=True)
    # 6 Correlation (masked)
    num_df = df.select_dtypes(include=[np.number])
    if not num_df.empty:
        corr = num_df.corr()
        if sns is None or plt is None:
            fig_corr = px.imshow(corr, color_continuous_scale='viridis', aspect='auto',
                                 title='Correlation Matrix')
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            mask = np.triu(np.ones_like(corr,dtype=bool))
            fig_corr, ax = plt.subplots(figsize=(6,4))
            sns.heatmap(corr, mask=mask, cmap='viridis', annot=False, ax=ax)
            ax.set_title('Correlation (upper triangle)')
            st.pyplot(fig_corr)
    # 7 Climate Group Avg
    if 'Climate_Group' in df.columns and 'Weekly_Sales' in df.columns:
        climate_avg = (df.groupby('Climate_Group')['Weekly_Sales'].mean().reset_index()
                         .rename(columns={'Weekly_Sales':'Avg_Weekly_Sales'}))
        fig_climate = px.bar(climate_avg, x='Climate_Group', y='Avg_Weekly_Sales', color='Avg_Weekly_Sales',
                             title='Avg Weekly Sales by Climate Group')
        st.plotly_chart(fig_climate, use_container_width=True)
    # 8 Holiday Lift per Store
    if {'Store','Holiday_Flag','Weekly_Sales'}.issubset(df.columns):
        lift = (df.groupby(['Store','Holiday_Flag'])['Weekly_Sales'].mean().unstack(fill_value=0).reset_index())
        lift.columns = ['Store','NonHoliday','Holiday']
        lift['Lift'] = lift['Holiday'] - lift['NonHoliday']
        fig_lift = px.bar(lift.sort_values('Lift', ascending=False), x='Store', y='Lift', title='Holiday Lift (Avg Weekly Sales)')
        st.plotly_chart(fig_lift, use_container_width=True)
    st.markdown("---")
    st.markdown("**More detail available on dedicated 'EDA' page in sidebar (pages/7_EDA.py).**")


