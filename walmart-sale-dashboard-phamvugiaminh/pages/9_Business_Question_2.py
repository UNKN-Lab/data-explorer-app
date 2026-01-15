import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from lib.data import get_data
import warnings
warnings.filterwarnings('ignore')

# Import ML libraries with error handling
try:
    import shap
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error
    ML_AVAILABLE = True
except ImportError as e:
    st.error(f"Machine Learning libraries not available: {e}")
    st.info("Please install required packages: `pip install shap scikit-learn`")
    ML_AVAILABLE = False

st.set_page_config(page_title="BQ2: Holiday Effect Analysis", layout="wide")

# ------------------------------------------------------------------
# CACHED FUNCTIONS - Avoid recomputation
# ------------------------------------------------------------------
@st.cache_data
def compute_holiday_lift(_df):
    """Cache holiday lift calculations"""
    holiday_lift = (
        _df.groupby(['Store', 'Holiday_Flag'])['Weekly_Sales']
          .mean()
          .unstack(fill_value=0)
          .reset_index()
    )
    holiday_lift.columns = ['Store', 'NonHoliday_Sales', 'Holiday_Sales']
    holiday_lift['Holiday_Lift'] = holiday_lift['Holiday_Sales'] - holiday_lift['NonHoliday_Sales']
    return holiday_lift

@st.cache_resource
def train_model(X_train, y_train):
    """Cache trained Random Forest model"""
    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    return model

@st.cache_data
def compute_shap_values(_model, _X_test):
    """Cache SHAP values computation"""
    explainer = shap.TreeExplainer(_model)
    shap_values = explainer.shap_values(_X_test)
    return shap_values

@st.cache_data
def prepare_model_data(_df, _holiday_lift):
    """Cache data preparation for model training"""
    # Merge NonHoliday_Sales back to full df
    df_all = _df.merge(_holiday_lift[['Store', 'NonHoliday_Sales']], on='Store', how='left')
    
    # Compute Holiday Uplift per row
    df_all['Holiday_Uplift'] = df_all['Weekly_Sales'] - df_all['NonHoliday_Sales']
    
    # Prepare features and target
    features = ['NonHoliday_Sales', 'CPI', 'Unemployment', 'Fuel_Price', 'Temperature']
    X = df_all[features].copy()
    y = df_all['Holiday_Uplift'].copy()
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    return df_all, X_train, X_test, y_train, y_test
st.title("🎄 Business Question 2: Holiday Effect Uniformity Across Stores")

st.markdown("""
### Research Question
**Is the holiday effect uniform across stores, or do some stores benefit more?**

This analysis investigates whether all stores experience similar sales increases during holiday weeks,
or if certain stores benefit more (or less) from holiday shopping patterns.
""")

# Load data
df = get_data()

# Add a loading message
with st.spinner("Loading and preparing data..."):
    
    # ------------------------------------------------------------------
    # PART 1: Compute Holiday Lift for ALL stores
    # ------------------------------------------------------------------
    st.header("📊 1. Holiday Lift Analysis")
    
    with st.expander("ℹ️ What is Holiday Lift?", expanded=False):
        st.markdown("""
        **Holiday Lift** measures the difference between average sales during holiday weeks versus non-holiday weeks.
        - **Positive Lift**: Store performs better during holidays
        - **Zero/Negative Lift**: Store does not benefit from holidays (or performs worse)
        """)
    
    # Use cached holiday lift calculation
    holiday_lift = compute_holiday_lift(df)
    
    # Store statistics
    stores_negative = holiday_lift[holiday_lift['Holiday_Lift'] <= 0]
    total_stores = len(holiday_lift)
    negative_count = len(stores_negative)
    
    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Stores", total_stores)
    with col2:
        st.metric("Stores with Negative/Zero Lift", negative_count, 
                  delta=f"{(negative_count/total_stores*100):.1f}%", delta_color="inverse")
    with col3:
        st.metric("Stores with Positive Lift", total_stores - negative_count,
                  delta=f"{((total_stores-negative_count)/total_stores*100):.1f}%")
    
    st.markdown("---")
    
    # Display conclusion
    if negative_count == 0:
        st.success("✅ **Conclusion:** Holidays have a positive effect on ALL stores.")
    else:
        st.warning(f"⚠️ **Conclusion:** Holidays do NOT benefit every store. {negative_count} stores receive little to no positive holiday impact.")
        
        st.markdown("**Stores with zero or negative holiday effect:**")
        display_negative = stores_negative[['Store', 'NonHoliday_Sales', 'Holiday_Sales', 'Holiday_Lift']].copy()
        display_negative['Holiday_Lift'] = display_negative['Holiday_Lift'].apply(lambda x: f"${x:,.0f}")
        display_negative['NonHoliday_Sales'] = display_negative['NonHoliday_Sales'].apply(lambda x: f"${x:,.0f}")
        display_negative['Holiday_Sales'] = display_negative['Holiday_Sales'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(display_negative, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Visualization: Holiday Lift per Store
    st.subheader("📈 Holiday Lift by Store (Sorted High → Low)")
    
    holiday_lift_sorted = holiday_lift.sort_values('Holiday_Lift', ascending=False).copy()
    
    # Create color coding: positive = green, negative/zero = red
    colors = ['#2ECC71' if lift > 0 else '#E74C3C' for lift in holiday_lift_sorted['Holiday_Lift']]
    
    fig_lift = go.Figure()
    fig_lift.add_trace(go.Bar(
        x=holiday_lift_sorted['Store'].astype(str),
        y=holiday_lift_sorted['Holiday_Lift'],
        marker_color=colors,
        text=holiday_lift_sorted['Holiday_Lift'].apply(lambda x: f"${x:,.0f}"),
        textposition='outside',
        hovertemplate='<b>Store %{x}</b><br>Holiday Lift: $%{y:,.0f}<extra></extra>'
    ))
    
    fig_lift.add_hline(y=0, line_dash="dash", line_color="black", line_width=1.5,
                       annotation_text="Zero Line", annotation_position="right")
    
    fig_lift.update_layout(
        title="Holiday Lift in Weekly Sales by Store (Holiday - Non-Holiday)",
        xaxis_title="Store ID",
        yaxis_title="Average Holiday Sales Lift ($)",
        template="plotly_white",
        height=500,
        showlegend=False,
        xaxis={'type': 'category'}
    )
    
    st.plotly_chart(fig_lift, use_container_width=True)

# ------------------------------------------------------------------
# PART 2: Prepare features and train model
# ------------------------------------------------------------------
if not ML_AVAILABLE:
    st.error("⚠️ Machine Learning features are not available. Please install required packages.")
    st.stop()

st.header("🤖 2. Understanding Factors Behind Holiday Uplift")

with st.expander("ℹ️ Methodology", expanded=False):
    st.markdown("""
    To understand **why** some stores have negative holiday uplift, we:
    1. Calculate **Holiday Uplift** = Weekly_Sales - NonHoliday_Sales (per store)
    2. Train a **Random Forest Regressor** using features:
        - NonHoliday_Sales
        - CPI (Consumer Price Index)
        - Unemployment
        - Fuel_Price
        - Temperature
    3. Use **SHAP (SHapley Additive exPlanations)** to interpret feature importance
    """)

with st.spinner("Training predictive model..."):
    # Use cached data preparation
    df_all, X_train, X_test, y_train, y_test = prepare_model_data(df, holiday_lift)
    
    # Use cached model training
    model = train_model(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    # Model performance
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Model MSE", f"${mse:,.0f}")
    with col2:
        st.metric("Model RMSE", f"${rmse:,.0f}")

st.markdown("---")

# ------------------------------------------------------------------
# PART 3: SHAP Analysis
# ------------------------------------------------------------------
st.subheader("🔍 SHAP Analysis: Feature Impact on Holiday Uplift")

st.markdown("""
The SHAP summary plot below shows which features most strongly influence holiday uplift predictions:
- **Red dots**: High feature values
- **Blue dots**: Low feature values
- **Position on x-axis**: Positive SHAP = increases uplift, Negative SHAP = decreases uplift
""")

with st.spinner("Generating SHAP analysis..."):
    # Use cached SHAP values
    shap_values = compute_shap_values(model, X_test)
    
    # Create SHAP summary plot
    fig_shap, ax = plt.subplots(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test, show=False, plot_size=(10, 6))
    st.pyplot(fig_shap, use_container_width=True)
    plt.close()

st.markdown("---")

# ------------------------------------------------------------------
# PART 4: Key Findings
# ------------------------------------------------------------------
st.header("💡 Key Findings: Why Some Stores Have Negative Holiday Uplift")

st.markdown("""
Based on the SHAP analysis and model predictions, stores with **negative or low holiday uplift** typically exhibit:

### 🔴 Primary Negative Factors:

1. **High Fuel Price** 🚗
   - When fuel prices are high, consumers travel less
   - Reduced foot traffic leads to lower in-store visits
   - Holiday shopping trips become more expensive

2. **Warm/Hot Temperature** 🌡️
   - In warmer climates, holiday shopping motivation decreases
   - Less seasonal urgency (compared to cold weather regions)
   - Reduced "holiday atmosphere" effect

3. **High Non-Holiday Sales** 📊
   - Stores already performing well year-round have less room for growth
   - Customer demand may already be saturated
   - Holiday promotions have diminishing returns

### 🟡 Ambiguous Factors:

4. **CPI (Consumer Price Index)** 💵
   - Macro-economic variable affecting all stores similarly
   - Does not create significant differentiation between stores
   - General inflation impact rather than store-specific

5. **Unemployment Rate** 📉
   - Also a macro variable with uniform regional impact
   - Affects consumer spending power broadly
   - Not a distinguishing factor for individual store performance

### 🎯 Business Insight:

The holiday uplift issue is **localized and behavioral**, not macro-economic. Stores in:
- **High fuel cost areas** with **warm climates** are most vulnerable
- **Already high-performing locations** see limited holiday boost
- **Cold climate, low fuel price regions** benefit most from holidays
""")

st.markdown("---")

# ------------------------------------------------------------------
# PART 5: Store-Level Predictions
# ------------------------------------------------------------------
st.header("📋 Store-Level Holiday Uplift Predictions")

with st.expander("View Detailed Store Predictions", expanded=False):
    results = X_test.copy()
    results['Actual_Uplift'] = y_test.values
    results['Predicted_Uplift'] = y_pred
    results['Store'] = df_all.loc[X_test.index, 'Store'].values
    
    store_summary = (
        results.groupby('Store')[['Actual_Uplift', 'Predicted_Uplift']]
        .mean()
        .reset_index()
    )
    store_summary['Difference'] = store_summary['Predicted_Uplift'] - store_summary['Actual_Uplift']
    store_summary = store_summary.sort_values('Actual_Uplift', ascending=False)
    
    # Format for display
    display_summary = store_summary.copy()
    display_summary['Actual_Uplift'] = display_summary['Actual_Uplift'].apply(lambda x: f"${x:,.0f}")
    display_summary['Predicted_Uplift'] = display_summary['Predicted_Uplift'].apply(lambda x: f"${x:,.0f}")
    display_summary['Difference'] = display_summary['Difference'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(display_summary, use_container_width=True, hide_index=True)

st.markdown("---")

# ------------------------------------------------------------------
# PART 6: Final Conclusion
# ------------------------------------------------------------------
st.header("📝 Conclusion")

st.success("""
### 🎯 Main Findings:

**The holiday effect is NOT uniform across stores.** While most stores benefit from holiday shopping patterns,
a significant subset experiences zero or negative holiday uplift.

### 🔑 Contributing Factors:

1. **Geographic/Environmental**: Fuel prices and temperature significantly impact holiday shopping behavior
2. **Baseline Performance**: High-performing stores have limited additional growth potential
3. **Non-Economic**: The effect is driven by localized behavioral patterns rather than macro-economic indicators

### 💼 Strategic Recommendations:

**For High-Uplift Stores** (Cold climate, low fuel areas):
- Maximize inventory and staffing during holiday weeks
- Invest heavily in holiday promotions
- Extend operating hours during peak periods

**For Low/Negative-Uplift Stores** (Warm climate, high fuel areas):
- Focus on year-round consistency rather than holiday peaks
- Implement online/delivery options to reduce travel burden
- Consider alternative promotional periods (non-traditional holidays)

**For High-Baseline Stores**:
- Shift from volume growth to margin optimization
- Focus on premium product mix during holidays
- Enhance customer experience rather than pure sales volume
""")

st.info("📚 **Source Analysis**: This dashboard is based on the comprehensive analysis in `walmart_sales_bq.ipynb` - Business Question 2")

# Footer
st.markdown("---")
st.caption("Walmart Sales Analysis Dashboard | Business Intelligence Project")
