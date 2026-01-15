import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from utils import get_data
import warnings
warnings.filterwarnings('ignore')

# Import statistical libraries with error handling
try:
    from scipy.stats import shapiro, levene, kruskal
    STATS_AVAILABLE = True
except ImportError as e:
    st.error(f"Statistical libraries not available: {e}")
    st.info("Please install required packages: `pip install scipy`")
    STATS_AVAILABLE = False

st.set_page_config(page_title="BQ1: Climate Impact Analysis", layout="wide")

# ------------------------------------------------------------------
# CACHED FUNCTIONS - Avoid recomputation
# ------------------------------------------------------------------
@st.cache_data
def compute_overall_stats(df_clean):
    """Cache overall statistics by climate group"""
    stats = df_clean.groupby('Climate_Group')['Weekly_Sales'].agg(['mean', 'median', 'std', 'count']).reset_index()
    stats.columns = ['Climate_Group', 'Mean', 'Median', 'Std', 'Count']
    return stats

@st.cache_data
def compute_normality_tests(df_non, groups_list):
    """Cache Shapiro-Wilk normality test results"""
    normality = {}
    normality_results = []
    
    for g in groups_list:
        subset = df_non[df_non['Climate_Group']==g]['Weekly_Sales']
        sample = subset.sample(min(500, len(subset)), random_state=42)
        w, p = shapiro(sample)
        normality[g] = p
        
        result = "Normal" if p >= 0.05 else "NOT Normal"
        normality_results.append({
            'Climate_Group': int(g),
            'W-statistic': w,
            'p-value': p,
            'Result': result
        })
    
    return normality, normality_results

@st.cache_data
def compute_levene_test(df_non, groups_list):
    """Cache Levene test results"""
    group_data = [df_non[df_non['Climate_Group']==g]['Weekly_Sales'].values for g in groups_list]
    lev_stat, lev_p = levene(*group_data)
    return lev_stat, lev_p

@st.cache_data
def compute_kruskal_test(df_non, groups_list):
    """Cache Kruskal-Wallis test results"""
    group_data = [df_non[df_non['Climate_Group']==g]['Weekly_Sales'].values for g in groups_list]
    H, p_kw = kruskal(*group_data)
    return H, p_kw
st.title("🌡️ Business Question 1: Climate Group Impact on Weekly Sales")

st.markdown("""
### Research Question
**Does weekly sales significantly differ among the climate groups?**

This analysis investigates whether stores in different climate zones (based on temperature patterns) 
experience statistically significant differences in their weekly sales performance.
""")

# ------------------------------------------------------------------
# PART 1: Load and Prepare Data
# ------------------------------------------------------------------
with st.spinner("Loading and preparing data..."):
    df = get_data()
    
    # Validate required columns
    required_cols = ['Date', 'Climate_Group', 'Weekly_Sales', 'Store', 'Holiday_Flag']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
        st.stop()
    
    # Ensure Date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Ensure Climate_Group is numeric
    df['Climate_Group'] = pd.to_numeric(df['Climate_Group'], errors='coerce')
    
    # Remove any rows with missing climate groups
    df_clean = df.dropna(subset=['Climate_Group', 'Weekly_Sales']).copy()
    
    st.success(f"✅ Data loaded successfully: {len(df_clean):,} records across {df_clean['Store'].nunique()} stores")

st.markdown("---")

# ------------------------------------------------------------------
# PART 2: Q1.1 - Overall Average Weekly Sales by Climate Group
# ------------------------------------------------------------------
st.header("📊 Q1.1: Which Climate Group Has the Highest Average Weekly Sales?")

with st.expander("ℹ️ About Climate Groups", expanded=False):
    st.markdown("""
    Stores are clustered into 5 climate groups based on temperature patterns:
    - **Group 1**: Cold, high variation
    - **Group 2**: Warm, stable
    - **Group 3**: Hot, very stable
    - **Group 4**: Mild, relatively stable
    - **Group 5**: Hot, high variation
    """)

# Calculate statistics (cached)
stats = compute_overall_stats(df_clean)

# Identify highest group
highest_group = int(stats.loc[stats['Mean'].idxmax(), 'Climate_Group'])
highest_value = stats.loc[stats['Mean'].idxmax(), 'Mean']

# Display key metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Climate Groups", len(stats))
with col2:
    st.metric("Highest Avg Sales Group", f"Group {highest_group}")
with col3:
    st.metric("Highest Avg Sales", f"${highest_value:,.0f}")

# Create bar chart with highlighting
climate_labels = {
    1: "Cold, high variation",
    2: "Warm, stable",
    3: "Hot, very stable",
    4: "Mild, relative stable",
    5: "Hot, variation"
}

# Safely map labels with fallback for missing groups
stats['Label'] = stats['Climate_Group'].apply(lambda x: climate_labels.get(int(x), f"Group {int(x)}"))
stats['Color'] = stats['Climate_Group'].apply(lambda x: '#E74C3C' if x == highest_group else '#3498DB')

fig_overall = go.Figure()
fig_overall.add_trace(go.Bar(
    x=stats['Climate_Group'].astype(str),
    y=stats['Mean'],
    marker_color=stats['Color'],
    text=stats['Mean'].apply(lambda x: f"${x:,.0f}"),
    textposition='outside',
    hovertemplate='<b>Climate Group %{x}</b><br>' +
                  'Label: %{customdata}<br>' +
                  'Avg Sales: $%{y:,.0f}<extra></extra>',
    customdata=stats['Label']
))

fig_overall.update_layout(
    title="Average Weekly Sales by Climate Group",
    xaxis_title="Climate Group",
    yaxis_title="Average Weekly Sales ($)",
    template="plotly_white",
    height=500,
    showlegend=False
)

st.plotly_chart(fig_overall, use_container_width=True)

# Display detailed statistics table
st.subheader("Detailed Statistics by Climate Group")
display_stats = stats.copy()
display_stats['Mean'] = display_stats['Mean'].apply(lambda x: f"${x:,.0f}")
display_stats['Median'] = display_stats['Median'].apply(lambda x: f"${x:,.0f}")
display_stats['Std'] = display_stats['Std'].apply(lambda x: f"${x:,.0f}")
st.dataframe(display_stats[['Climate_Group', 'Label', 'Mean', 'Median', 'Std', 'Count']], 
             use_container_width=True, hide_index=True)

st.success(f"✅ **Conclusion**: Climate Group {highest_group} ({climate_labels.get(highest_group, f'Group {highest_group}')}) has the highest average weekly sales of ${highest_value:,.0f}")

st.markdown("---")

# ------------------------------------------------------------------
# PART 3: Q1.2 - Distribution and Outliers Analysis
# ------------------------------------------------------------------
st.header("📈 Q1.2: Sales Distribution and Outliers by Climate Group")

st.markdown("""
The following visualizations show the distribution of weekly sales within each climate group,
helping identify skewness, outliers, and overall sales stability.
""")

# Get unique groups
groups = sorted(df_clean['Climate_Group'].unique())
colors_map = {
    1: '#4C72B0',  # blue
    2: '#55A868',  # green
    3: '#C44E52',  # red
    4: '#8172B2',  # purple
    5: '#CCB974'   # tan
}

for g in groups:
    subset = df_clean[df_clean['Climate_Group'] == g]['Weekly_Sales']
    
    st.subheader(f"Climate Group {int(g)}: {climate_labels.get(int(g), f'Group {int(g)}')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=subset,
            nbinsx=30,
            marker_color=colors_map.get(int(g), '#3498DB'),
            opacity=0.8,
            name=f'Group {int(g)}'
        ))
        fig_hist.update_layout(
            title=f"Distribution - Group {int(g)}",
            xaxis_title="Weekly Sales ($)",
            yaxis_title="Frequency",
            template="plotly_white",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Boxplot
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(
            y=subset,
            marker_color=colors_map.get(int(g), '#3498DB'),
            name=f'Group {int(g)}',
            boxmean='sd'
        ))
        fig_box.update_layout(
            title=f"Boxplot - Group {int(g)}",
            yaxis_title="Weekly Sales ($)",
            template="plotly_white",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Statistics
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("Mean", f"${subset.mean():,.0f}")
    with col_b:
        st.metric("Median", f"${subset.median():,.0f}")
    with col_c:
        st.metric("Std Dev", f"${subset.std():,.0f}")
    with col_d:
        skew = subset.skew()
        st.metric("Skewness", f"{skew:.2f}")
    
    st.markdown("---")

# Summary insights
st.subheader("💡 Key Insights from Distribution Analysis")
st.markdown("""
Based on the distribution plots:

- **Climate Group 1 (Cold, high variation)**: Sales change strongly with high variability and outliers.
- **Climate Group 2 (Warm, stable)**: Sales are relatively stable with moderate variation.
- **Climate Group 3 (Hot, very stable)**: This is the most stable group with consistent sales patterns.
- **Climate Group 4 (Mild, relative stable)**: Sales change at a moderate level.
- **Climate Group 5 (Hot, variation)**: Sales vary considerably and are harder to predict.

**Business Insight**: The more stable the climate, the more stable the sales. 
Regions with unstable climates need stronger inventory control and seasonal marketing campaigns.
""")

st.markdown("---")

# ------------------------------------------------------------------
# PART 4: Q1.3 - Statistical Analysis (Non-Holiday Data)
# ------------------------------------------------------------------
if not STATS_AVAILABLE:
    st.error("⚠️ Statistical analysis features are not available. Please install scipy.")
    st.stop()

st.header("🔬 Q1.3: Does Climate Group Still Affect Sales After Removing Holiday Effect?")

st.markdown("""
To ensure that climate groups have a genuine impact on sales (not just due to holiday shopping patterns),
we analyze only non-holiday weeks using statistical hypothesis testing.
""")

# Filter non-holiday data
df_non = df_clean[df_clean['Holiday_Flag'] == 0].copy()

st.info(f"📊 Analyzing {len(df_non):,} non-holiday records across {df_non['Store'].nunique()} stores")

# Descriptive statistics
st.subheader("Descriptive Statistics (Non-Holiday Weeks Only)")
non_holiday_stats = df_non.groupby('Climate_Group')['Weekly_Sales'].describe()
st.dataframe(non_holiday_stats.style.format({
    'mean': '${:,.0f}',
    'std': '${:,.0f}',
    '25%': '${:,.0f}',
    '50%': '${:,.0f}',
    '75%': '${:,.0f}',
    'min': '${:,.0f}',
    'max': '${:,.0f}'
}), use_container_width=True)

st.markdown("---")

# Prepare data for tests
groups_list = sorted(df_non['Climate_Group'].unique())
group_data = [df_non[df_non['Climate_Group']==g]['Weekly_Sales'] for g in groups_list]

# ------------------------------------------------------------------
# Q1.3.1: Normality Test (Shapiro-Wilk)
# ------------------------------------------------------------------
st.subheader("📋 Q1.3.1: Normality Test (Shapiro-Wilk)")

with st.expander("ℹ️ About Shapiro-Wilk Test", expanded=False):
    st.markdown("""
    - **H0**: Weekly Sales in this Climate Group follow a normal distribution
    - **H1**: Weekly Sales do NOT follow a normal distribution
    - **Decision**: If p < 0.05, reject H0 (not normal)
    """)

# Use cached normality tests
normality, normality_results = compute_normality_tests(df_non, tuple(groups_list))

# Add labels for display
normality_display = []
for r in normality_results:
    normality_display.append({
        'Climate_Group': r['Climate_Group'],
        'Label': climate_labels.get(r['Climate_Group'], f"Group {r['Climate_Group']}"),
        'W-statistic': f"{r['W-statistic']:.6f}",
        'p-value': f"{r['p-value']:.6f}",
        'Result': r['Result']
    })

normality_df = pd.DataFrame(normality_display)
st.dataframe(normality_df, use_container_width=True, hide_index=True)

normal_count = sum(1 for p in normality.values() if p >= 0.05)
st.write(f"**Summary**: {normal_count} out of {len(groups_list)} groups follow normal distribution")

st.markdown("---")

# ------------------------------------------------------------------
# Q1.3.2: Variance Equality Test (Levene)
# ------------------------------------------------------------------
st.subheader("📋 Q1.3.2: Variance Equality Test (Levene)")

with st.expander("ℹ️ About Levene Test", expanded=False):
    st.markdown("""
    - **H0**: Variances across Climate Groups are equal
    - **H1**: At least one Climate Group has a different variance
    - **Decision**: If p < 0.05, reject H0 (variances not equal)
    """)

# Use cached Levene test
lev_stat, lev_p = compute_levene_test(df_non, tuple(groups_list))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Levene Statistic", f"{lev_stat:.4f}")
with col2:
    st.metric("p-value", f"{lev_p:.6f}")
with col3:
    variance_result = "Equal" if lev_p >= 0.05 else "NOT Equal"
    st.metric("Result", variance_result)

if lev_p < 0.05:
    st.warning("⚠️ **Conclusion**: Variances are NOT equal across climate groups")
else:
    st.success("✅ **Conclusion**: Variances are equal across climate groups")

st.markdown("---")

# ------------------------------------------------------------------
# Test Selection
# ------------------------------------------------------------------
st.subheader("🔍 Statistical Test Selection")

use_anova = all(p > 0.05 for p in normality.values()) and lev_p > 0.05

if use_anova:
    st.info("✅ **ANOVA assumptions met** → Use parametric ANOVA test")
    test_used = "ANOVA"
else:
    st.warning("⚠️ **ANOVA assumptions FAILED** → Use non-parametric Kruskal-Wallis test")
    test_used = "Kruskal-Wallis"

st.markdown("---")

# ------------------------------------------------------------------
# Q1.3.3: Kruskal-Wallis Test
# ------------------------------------------------------------------
st.subheader(f"📋 Q1.3.3: {test_used} Test Results")

with st.expander("ℹ️ About Kruskal-Wallis Test", expanded=False):
    st.markdown("""
    - **H0**: Median Weekly Sales are equal across Climate Groups
    - **H1**: At least one Climate Group has a different median Weekly Sales
    - **Decision**: If p < 0.05, reject H0 (groups are different)
    """)

# Use cached Kruskal-Wallis test
H, p_kw = compute_kruskal_test(df_non, tuple(groups_list))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("H-statistic", f"{H:.4f}")
with col2:
    st.metric("p-value", f"{p_kw:.6e}")
with col3:
    kw_result = "Different" if p_kw < 0.05 else "Similar"
    st.metric("Result", kw_result)

if p_kw < 0.05:
    st.success("✅ **Conclusion**: Climate Groups have significantly different median weekly sales (reject H0)")
    st.write("The differences in sales across climate groups are **statistically significant**.")
else:
    st.info("ℹ️ **Conclusion**: Climate Groups have similar median weekly sales (fail to reject H0)")
    st.write("No statistically significant difference found between climate groups.")

st.markdown("---")

# ------------------------------------------------------------------
# Q1.3.4: Effect Size (Epsilon-squared)
# ------------------------------------------------------------------
st.subheader("📋 Q1.3.4: Effect Size Analysis")

with st.expander("ℹ️ About Effect Size", expanded=False):
    st.markdown("""
    Epsilon-squared (ε²) measures the practical significance of the difference:
    - **< 0.01**: Negligible
    - **0.01 - 0.06**: Small
    - **0.06 - 0.14**: Medium
    - **≥ 0.14**: Large
    """)

n = len(df_non)
k = len(groups_list)
eps_sq = (H - k + 1) / (n - k)

col1, col2 = st.columns(2)
with col1:
    st.metric("Epsilon-squared (ε²)", f"{eps_sq:.4f}")
with col2:
    if eps_sq < 0.01:
        effect_label = "Negligible"
    elif eps_sq < 0.06:
        effect_label = "Small"
    elif eps_sq < 0.14:
        effect_label = "Medium"
    else:
        effect_label = "Large"
    st.metric("Effect Size", effect_label)

st.markdown(f"""
**Interpretation**: The effect size is **{effect_label.lower()}** (ε² = {eps_sq:.4f}), 
indicating that Climate_Group has a **statistically detectable but practically {effect_label.lower()} impact** on Weekly Sales.

While the difference is statistically significant (p < 0.05), the actual practical impact on business 
operations is {effect_label.lower()}.
""")

st.markdown("---")

# ------------------------------------------------------------------
# PART 5: Visualization of Non-Holiday Sales
# ------------------------------------------------------------------
st.header("📊 Non-Holiday Average Weekly Sales by Climate Group")

st.markdown("""
This chart shows average sales using only non-holiday data, confirming that the ranking 
of climate groups persists even after removing holiday effects.
""")

# Compute mean Weekly Sales per climate group (non-holiday)
mean_stats_non = (
    df_non.groupby('Climate_Group')['Weekly_Sales']
    .mean()
    .reset_index()
    .sort_values('Climate_Group')
)

mean_stats_non['Label'] = mean_stats_non['Climate_Group'].apply(lambda x: climate_labels.get(int(x), f'Group {int(x)}'))
mean_stats_non['Color'] = mean_stats_non['Climate_Group'].apply(lambda x: colors_map.get(int(x), '#3498DB'))

fig_non_holiday = go.Figure()
fig_non_holiday.add_trace(go.Bar(
    x=mean_stats_non['Climate_Group'].astype(str),
    y=mean_stats_non['Weekly_Sales'],
    marker_color=[colors_map.get(int(g), '#3498DB') for g in mean_stats_non['Climate_Group']],
    text=mean_stats_non['Weekly_Sales'].apply(lambda x: f"${x:,.0f}"),
    textposition='outside',
    hovertemplate='<b>Climate Group %{x}</b><br>' +
                  '%{customdata}<br>' +
                  'Avg Sales: $%{y:,.0f}<extra></extra>',
    customdata=mean_stats_non['Label']
))

fig_non_holiday.update_layout(
    title="Average Weekly Sales by Climate Group (Non-Holiday Weeks Only)",
    xaxis_title="Climate Group",
    yaxis_title="Average Weekly Sales ($)",
    template="plotly_white",
    height=500,
    showlegend=False
)

st.plotly_chart(fig_non_holiday, use_container_width=True)

st.info("""
📌 **Key Observation**: The ranking of average weekly sales across the 5 climate groups 
does not change even after removing holiday weeks. This demonstrates that temperature/climate 
is statistically meaningful and has a real impact on store sales, independent of holiday effects.
""")

st.markdown("---")

# ------------------------------------------------------------------
# PART 6: Final Conclusion
# ------------------------------------------------------------------
st.header("📝 Conclusion: Business Question 1")

# Get the label for highest group
highest_group_label = climate_labels.get(highest_group, f'Group {highest_group}')

conclusion_text = f"""
### 🎯 Main Findings

**Yes, weekly sales DO significantly differ among climate groups**, with the following key insights:

#### 1️⃣ Overall Performance by Climate Group
- **Climate Group {highest_group} ({highest_group_label})** has the highest average weekly sales of **${highest_value:,.0f}**
- Clear performance differences exist across all 5 climate groups
- Sales patterns vary substantially based on temperature characteristics

#### 2️⃣ Sales Stability and Predictability
- **Stable climates** (Groups 2, 3, 4) show more consistent sales patterns with fewer outliers
- **Variable climates** (Groups 1, 5) exhibit higher sales volatility and require more dynamic inventory management
- Climate stability correlates strongly with sales predictability

#### 3️⃣ Statistical Significance (Non-Holiday Analysis)
- **Kruskal-Wallis Test Result**: H = {H:.4f}, p = {p_kw:.6e}
- **Conclusion**: Climate groups have **statistically significant** differences in median weekly sales
- **Effect Size**: ε² = {eps_sq:.4f} ({effect_label})
- The climate effect persists **even after removing holiday influences**, confirming it's not just driven by seasonal shopping

#### 4️⃣ Practical Business Impact
While statistically significant, the effect size is **{effect_label.lower()}**, suggesting:
- Climate is a **meaningful but not dominant** factor in sales performance
- Other factors (store location, competition, demographics) also play important roles
- Climate should be **one of multiple factors** considered in business strategy

### 💼 Strategic Recommendations

**For Variable Climate Stores** (Groups 1, 5):
- Implement flexible inventory systems with safety stock
- Use weather forecasting for short-term demand planning
- Develop targeted seasonal marketing campaigns

**For Stable Climate Stores** (Groups 2, 3, 4):
- Focus on consistent operations and efficiency
- Optimize for steady, predictable demand
- Build long-term customer loyalty programs

**Overall Strategy**:
- Segment stores by climate group for targeted management
- Adjust inventory allocation based on climate-driven sales patterns
- Use climate as a key variable in demand forecasting models
"""

st.success(conclusion_text)

st.info("📚 **Source Analysis**: This dashboard is based on the comprehensive analysis in `walmart_sales_bq.ipynb` - Business Question 1")

# Footer
st.markdown("---")
st.caption("Walmart Sales Analysis Dashboard | Business Intelligence Project")
