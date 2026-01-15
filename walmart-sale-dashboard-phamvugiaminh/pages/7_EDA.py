import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Optional heavy libraries guarded
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

st.header("Exploratory Data Analysis (EDA)")

# ------------------------------------------------------------------
# Helper: access dataframe already loaded in app (per user instruction)
# ------------------------------------------------------------------
def get_df():
	# Prefer the common session keys first
	if 'df' in st.session_state:
		return st.session_state['df']
	if 'df_main' in st.session_state:
		return st.session_state['df_main']
	# Attempt to lazily load via shared data loader
	try:
		from utils import get_data
		loaded = get_data()
		# Mirror under 'df' for convenience on this page
		st.session_state['df'] = loaded
		return loaded
	except Exception:
		pass
	# Last resort: global injection fallback
	if 'df' in globals():
		return globals()['df']
	st.error("Dataset not found. Couldn't auto-load data; please open 'Home' first.")
	st.stop()

df = get_df()

# Defensive checks for required columns from notebook
required_cols = ["Date","Store","Weekly_Sales","Holiday_Flag","Fuel_Price","CPI","Unemployment"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
	st.warning(f"Missing columns for full EDA: {missing}. Some sections will be skipped.")

# Ensure Date is datetime
if 'Date' in df.columns and not np.issubdtype(df['Date'].dtype, np.datetime64):
	try:
		df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
	except Exception:
		st.warning("Could not parse 'Date' column to datetime.")

# ------------------------------------------------------------------
# Section 1: Weekly Sales of All Stores Over Time
# ------------------------------------------------------------------
st.subheader("1. Weekly Sales of All Stores Over Time")
st.write("Line chart of weekly sales for each store to reveal seasonality and peak periods (e.g., Black Friday, Christmas). Matches Notebook Section 5.1.")

stores = sorted(df['Store'].unique()) if 'Store' in df.columns else []
selected_stores = st.multiselect("Select stores to display", stores, default=stores)
plot_df = df[df['Store'].isin(selected_stores)] if selected_stores else df.copy()

if not plot_df.empty:
	fig_ts = px.line(plot_df, x="Date", y="Weekly_Sales", color='Store', title="Weekly Sales Over Time (Selected Stores)")
	st.plotly_chart(fig_ts, use_container_width=True)
	st.markdown("- Sales peak visibly around late November (Thanksgiving/Black Friday) and late December (Christmas).\n- Clear recurring seasonal uplift in Q4.")
else:
	st.info("No stores selected.")

# ------------------------------------------------------------------
# Section 2: Average Weekly Sales per Store
# ------------------------------------------------------------------
st.subheader("2. Average Weekly Sales per Store")
st.write("Bar chart of mean weekly sales per store. Matches Notebook Section 5.2.")
if 'Store' in df.columns:
	store_avg = (df.groupby('Store')['Weekly_Sales']
				   .mean()
				   .reset_index()
				   .rename(columns={'Weekly_Sales':'Avg_Weekly_Sales'}))
	fig_store_avg = px.bar(store_avg, x='Store', y='Avg_Weekly_Sales', color='Avg_Weekly_Sales',
						   title='Average Weekly Sales per Store')
	st.plotly_chart(fig_store_avg, use_container_width=True)
	st.markdown("- Most profitable stores (per notebook): 2, 4, 13, 14, 20.\n- Less profitable: 5, 33, 36, 38, 44.\n- Insight: Target marketing and inventory optimization for underperforming locations.")
else:
	st.info("Store column not found; skipping store performance section.")

# ------------------------------------------------------------------
# Section 3: Holiday vs Non-Holiday Sales Comparison
# ------------------------------------------------------------------
st.subheader("3. Holiday vs Non-Holiday Sales Comparison")
st.write("Average and total weekly sales separated by Holiday_Flag. Matches Notebook Section 5.3.")
if 'Holiday_Flag' in df.columns:
	holiday_avg = (df.groupby('Holiday_Flag')['Weekly_Sales']
					 .mean()
					 .reset_index()
					 .rename(columns={'Weekly_Sales':'Avg_Weekly_Sales'}))
	holiday_total = (df.groupby('Holiday_Flag')['Weekly_Sales']
					   .sum()
					   .reset_index()
					   .rename(columns={'Weekly_Sales':'Total_Sales'}))
	fig_h_avg = px.bar(holiday_avg, x='Holiday_Flag', y='Avg_Weekly_Sales', title='Average Weekly Sales (Holiday vs Non-Holiday)')
	fig_h_total = px.bar(holiday_total, x='Holiday_Flag', y='Total_Sales', title='Total Weekly Sales (Holiday vs Non-Holiday)')
	st.plotly_chart(fig_h_avg, use_container_width=True)
	st.plotly_chart(fig_h_total, use_container_width=True)
	st.markdown("- Holiday weeks have higher average weekly sales.\n- Total yearly sales remain dominated by non-holiday weeks due to frequency.\n- Insight: Holidays amplify demand intensity but not total share of revenue.")
else:
	st.info("Holiday_Flag column not found; skipping holiday comparison.")

# ------------------------------------------------------------------
# Section 4: Top 20 Weekly Sales Events (Outliers / Peaks)
# ------------------------------------------------------------------
st.subheader("4. Top Weekly Sales Events")
top_n = st.slider("Select number of top sales events", min_value=10, max_value=50, value=20, step=5)
top_sales_df = df.nlargest(top_n, 'Weekly_Sales')[['Date','Store','Weekly_Sales']]
fig_top = px.scatter(top_sales_df, x='Date', y='Weekly_Sales', color='Store', size='Weekly_Sales',
					 title=f'Top {top_n} Weekly Sales Events by Store')
st.plotly_chart(fig_top, use_container_width=True)
st.markdown("- Highest peaks occur near Christmas (Dec 24) and Thanksgiving (late Nov).\n- Peak clustering reflects concentrated seasonal demand spikes.")

# ------------------------------------------------------------------
# Section 5: Average Monthly Sales
# ------------------------------------------------------------------
st.subheader("5. Average Monthly Sales")
if 'Date' in df.columns:
	month_df = df.copy()
	month_df['Month'] = month_df['Date'].dt.month
	monthly_avg = (month_df.groupby('Month')['Weekly_Sales']
					 .mean()
					 .reset_index()
					 .rename(columns={'Weekly_Sales':'Avg_Monthly_Sales'}))
	fig_month = px.bar(monthly_avg, x='Month', y='Avg_Monthly_Sales', color='Avg_Monthly_Sales',
					   title='Average Monthly Sales')
	st.plotly_chart(fig_month, use_container_width=True)
	st.markdown("- Q4 (Nov & Dec) has the strongest average performance.\n- January shows the lowest average weekly sales.\n- Insight: Seasonal planning critical for end-of-year ramp-up.")
else:
	st.info("Date column missing; cannot compute monthly averages.")

# ------------------------------------------------------------------
# Section 6: Correlation Matrix
# ------------------------------------------------------------------
st.subheader("6. Correlation Matrix")
numeric_df = df.select_dtypes(include=[np.number])
if not numeric_df.empty:
	corr = numeric_df.corr()
	if sns is None or plt is None:
		fig_corr = px.imshow(corr, color_continuous_scale='viridis', title='Correlation Matrix')
		st.plotly_chart(fig_corr, use_container_width=True)
	else:
		mask = np.triu(np.ones_like(corr, dtype=bool))
		fig_corr, ax = plt.subplots(figsize=(9,6))
		sns.heatmap(corr, mask=mask, cmap='viridis', annot=True, fmt='.2f', ax=ax)
		ax.set_title('Correlation Heatmap (Upper Triangle Masked)')
		st.pyplot(fig_corr)
	st.markdown("- Fuel_Price and CPI show strong positive correlation.\n- Weekly_Sales lacks a dominant single numeric predictor.\n- Insight: Sales driven by multi-factor + seasonal effects rather than one linear driver.")
else:
	st.info("No numeric columns available for correlation heatmap.")

# ------------------------------------------------------------------
# Section 7: Economic Factors Over Time (Fuel Price, CPI, Unemployment)
# ------------------------------------------------------------------
st.subheader("7. Economic Factors Over Time")
if 'Date' in df.columns:
	econ_cols = [c for c in ['Fuel_Price','CPI','Unemployment'] if c in df.columns]
	for col,label in [('Fuel_Price','Fuel Price'),('CPI','CPI'),('Unemployment','Unemployment Rate')]:
		if col in df.columns:
			econ_ts = (df.groupby('Date')[col].mean().reset_index().rename(columns={col: f'Avg_{col}'}))
			fig_econ = px.line(econ_ts, x='Date', y=f'Avg_{col}', title=f'{label} Over Time')
			st.plotly_chart(fig_econ, use_container_width=True)
	st.markdown("- Fuel_Price and CPI trend upward together, consistent with inflation dynamics.\n- Unemployment shows mild downward drift with weak negative relation to sales.\n- Insight: Macroeconomic shifts visible but not sole sales drivers.")
else:
	st.info("Date column missing; skipping economic factor time series.")
