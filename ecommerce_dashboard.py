# =============================
# E-COMMERCE DASHBOARD (FULL VERSION WITH DESCRIPTIONS)
# =============================

import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="E-commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 E-commerce Sales & Customer Analytics Dashboard")

st.markdown("""
Welcome to the E-commerce Analytics Dashboard.  

This dashboard helps visualize sales, revenue, customer behavior, and product trends.  

We are using a dataset with **10,000 orders** containing the following columns:
- `Invoice_Number`: Unique order ID
- `Invoice_Date`: Date of purchase
- `Customer_ID`: Unique customer identifier
- `Country`: Customer location
- `Quantity`: Number of items bought
- `Amount`: Total value of the order

**Goals of this dashboard:**
1. Track overall sales performance and revenue.
2. Understand customer behavior via RFM segmentation.
3. Identify top-selling products and regions.
4. Enable interactive analysis for better decision-making.
""")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("ecommerce_analysis.csv")

# -----------------------------
# DATA CLEANING
# -----------------------------
# Convert numeric columns
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

# Convert dates safely
df['Invoice_Date'] = pd.to_datetime(
    df['Invoice_Date'],
    dayfirst=True,
    errors='coerce'
)

# Drop rows with critical missing values
df = df.dropna(subset=['Invoice_Number', 'Invoice_Date', 'Customer_ID', 'Amount'])

# -----------------------------
# INTERACTIVE FILTERS
# -----------------------------
st.sidebar.header("🔍 Filters")

countries = st.sidebar.multiselect(
    "Select Countries",
    options=df['Country'].unique(),
    default=df['Country'].unique()
)

products = st.sidebar.multiselect(
    "Select Products",
    options=df['Product'].unique() if 'Product' in df.columns else [],
    default=df['Product'].unique() if 'Product' in df.columns else []
)

date_range = st.sidebar.date_input(
    "Invoice Date Range",
    [df['Invoice_Date'].min(), df['Invoice_Date'].max()]
)

# Apply filters
df_filtered = df[
    (df['Country'].isin(countries)) &
    ((df['Product'].isin(products)) if 'Product' in df.columns else True) &
    (df['Invoice_Date'] >= pd.to_datetime(date_range[0])) &
    (df['Invoice_Date'] <= pd.to_datetime(date_range[1]))
]

# -----------------------------
# KPI METRICS
# -----------------------------
st.header("📊 Executive KPIs")
st.markdown("""
These metrics summarize the overall business performance at a glance:
- **Total Sales:** Total revenue generated across all orders.
- **Total Orders:** Number of unique orders in the dataset.
- **Total Customers:** Number of unique customers who made purchases.
- **Average Order Value (AOV):** Average revenue per order.
""")

total_sales = df_filtered['Amount'].sum()
total_orders = df_filtered['Invoice_Number'].nunique()
total_customers = df_filtered['Customer_ID'].nunique()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"${total_sales:,.2f}")
c2.metric("Total Orders", f"{total_orders:,}")
c3.metric("Total Customers", f"{total_customers:,}")
c4.metric("Avg Order Value", f"${avg_order_value:,.2f}")

# -----------------------------
# SALES TREND
# -----------------------------
st.divider()
st.header("📈 Sales Over Time")
st.markdown("""
This chart shows **daily sales trends**.
Observe peaks and dips in sales — these may correspond to **promotional campaigns, holidays, or seasonal trends**.
Analyzing this trend helps with **forecasting and inventory planning**.
""")

sales_time = (
    df_filtered.groupby(pd.Grouper(key='Invoice_Date', freq='D'))['Amount']
    .sum()
    .reset_index()
)

fig_time = px.line(
    sales_time,
    x='Invoice_Date',
    y='Amount',
    title="Daily Sales Trend",
    markers=True
)
st.plotly_chart(fig_time, use_container_width=True)

# -----------------------------
# SALES BY COUNTRY
# -----------------------------
st.divider()
st.header("🌍 Revenue by Country")
st.markdown("""
This visualization shows the **top 10 countries by revenue**.
It helps identify which regions contribute the most to your business.
You can use this insight to **focus marketing and logistics efforts** in high-performing regions.
""")

country_sales = (
    df_filtered.groupby('Country')['Amount']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_country = px.bar(
    country_sales,
    x='Country',
    y='Amount',
    title="Top 10 Countries by Revenue",
    text='Amount'
)
fig_country.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
st.plotly_chart(fig_country, use_container_width=True)

# -----------------------------
# TOP PRODUCTS
# -----------------------------
if 'Product' in df_filtered.columns:
    st.divider()
    st.header("🛍️ Top 10 Products by Sales")
    st.markdown("""
This shows the **top 10 revenue-generating products**.
Focus on these products for **inventory planning, promotions, and marketing campaigns**.
""")

    top_products = (
        df_filtered.groupby('Product')['Amount']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig_products = px.bar(
        top_products,
        x='Product',
        y='Amount',
        title="Top 10 Products by Revenue",
        text='Amount'
    )
    fig_products.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    st.plotly_chart(fig_products, use_container_width=True)

# -----------------------------
# RFM ANALYSIS
# -----------------------------
st.divider()
st.header("🧠 Customer Segmentation (RFM Analysis)")
st.markdown("""
RFM stands for **Recency, Frequency, Monetary**:
- **Recency:** How recently a customer made a purchase (lower is better)
- **Frequency:** How often the customer makes purchases
- **Monetary:** How much revenue the customer generates

Customer segmentation helps identify:
- Loyal customers (high F and M)
- At-risk customers (high R)
- New customers (low F)

The RFM Score combines these three metrics into a single score for easier segmentation.
""")

snapshot_date = df_filtered['Invoice_Date'].max() + pd.Timedelta(days=1)

rfm = (
    df_filtered.groupby('Customer_ID')
    .agg({
        'Invoice_Date': lambda x: (snapshot_date - x.max()).days,
        'Invoice_Number': 'nunique',
        'Amount': 'sum'
    })
    .reset_index()
)
rfm.columns = ['Customer_ID', 'Recency', 'Frequency', 'Monetary']

# Rank customers (safe)
rfm['R_rank'] = rfm['Recency'].rank(method='first', ascending=True)
rfm['F_rank'] = rfm['Frequency'].rank(method='first', ascending=True)
rfm['M_rank'] = rfm['Monetary'].rank(method='first', ascending=True)

# Qcut scores (never fails)
rfm['R_Score'] = pd.qcut(rfm['R_rank'], 5, labels=[5,4,3,2,1])
rfm['F_Score'] = pd.qcut(rfm['F_rank'], 5, labels=[1,2,3,4,5])
rfm['M_Score'] = pd.qcut(rfm['M_rank'], 5, labels=[1,2,3,4,5])

rfm['RFM_Score'] = (
    rfm['R_Score'].astype(str) +
    rfm['F_Score'].astype(str) +
    rfm['M_Score'].astype(str)
)

# Optional: add segments
def rfm_segment(row):
    if int(row['R_Score']) >= 4 and int(row['F_Score']) >= 4 and int(row['M_Score']) >= 4:
        return "Best Customers"
    elif int(row['R_Score']) >= 4 and int(row['F_Score']) <= 2:
        return "New Customers"
    elif int(row['R_Score']) <= 2 and int(row['F_Score']) >= 4:
        return "Loyal Customers"
    else:
        return "Others"

rfm['Segment'] = rfm.apply(rfm_segment, axis=1)

st.subheader("RFM Table Preview")
st.dataframe(rfm[['Customer_ID', 'RFM_Score', 'Segment']].head(20))

# -----------------------------
# RFM DISTRIBUTION
# -----------------------------
fig_rfm = px.histogram(
    rfm,
    x='RFM_Score',
    title="Customer RFM Score Distribution",
    text_auto=True
)
st.plotly_chart(fig_rfm, use_container_width=True)

# -----------------------------
# BUSINESS INSIGHTS
# -----------------------------
st.divider()
st.header("📌 Business Insights & Recommendations")
st.markdown("""
From the dashboard, we can observe:

1. **Revenue & Orders:** Total sales and order count show business performance.
2. **Sales Trends:** Peaks indicate potential seasonal or marketing effects.
3. **Customer Segmentation:** Helps in **targeted marketing** and retention programs.
4. **Top Products & Countries:** Identify key revenue drivers.

**Recommendations:**
- Focus on **Best Customers** for loyalty campaigns.
- Retarget **Loyal Customers** to increase frequency.
- Analyze low-performing countries for growth opportunities.
- Use sales trend insights for **inventory & promotion planning**.
""")
