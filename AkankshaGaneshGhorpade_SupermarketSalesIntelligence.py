import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Supermarket Sales Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>
    .main-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 0;
    }
    .subtitle {
        color: #777;
        font-size: 16px;
        margin-bottom: 25px;
    }
    div[data-testid="stMetric"] {
        border: 1px solid #e5e5e5;
        border-radius: 12px;
        padding: 15px;
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file_path = "Supermarket.csv"
    df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = df.columns.str.strip()

    # Convert data types
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors="coerce")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")

    # Recalculate sales to validate dataset
    df["Calculated_Sales"] = (
        df["Quantity"] * df["Unit_Price"]
    ).round(2)

    # Use calculated sales as the analysis value
    df["Sales"] = df["Calculated_Sales"]

    # Derived columns
    df["Month"] = df["Date"].dt.strftime("%B")
    df["Month_Number"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day_name()

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Supermarket.csv was not found. "
        "Place Supermarket.csv in the same folder as this Python file."
    )
    st.stop()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.title("🛒 Supermarket Intelligence")

st.sidebar.markdown("### Filters")

branch_options = sorted(df["Branch"].dropna().unique())
city_options = sorted(df["City"].dropna().unique())
product_options = sorted(df["Product"].dropna().unique())
customer_options = sorted(df["Customer_Type"].dropna().unique())
payment_options = sorted(df["Payment_Method"].dropna().unique())

selected_branches = st.sidebar.multiselect(
    "Branch",
    branch_options,
    default=branch_options
)

selected_cities = st.sidebar.multiselect(
    "City",
    city_options,
    default=city_options
)

selected_products = st.sidebar.multiselect(
    "Product",
    product_options,
    default=product_options
)

selected_customers = st.sidebar.multiselect(
    "Customer Type",
    customer_options,
    default=customer_options
)

selected_payments = st.sidebar.multiselect(
    "Payment Method",
    payment_options,
    default=payment_options
)

# Date filter
min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------
filtered_df = df[
    df["Branch"].isin(selected_branches)
    & df["City"].isin(selected_cities)
    & df["Product"].isin(selected_products)
    & df["Customer_Type"].isin(selected_customers)
    & df["Payment_Method"].isin(selected_payments)
].copy()

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date)
        & (filtered_df["Date"].dt.date <= end_date)
    ]

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">🛒 Supermarket Sales Intelligence Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Data-driven analysis of products, branches, customers and sales performance'
    '</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------
total_sales = filtered_df["Sales"].sum()
total_transactions = len(filtered_df)
total_quantity = filtered_df["Quantity"].sum()
average_transaction = (
    filtered_df["Sales"].mean() if len(filtered_df) > 0 else 0
)
average_rating = (
    filtered_df["Rating"].mean() if len(filtered_df) > 0 else 0
)

# Top product
if not filtered_df.empty:
    top_product = (
        filtered_df.groupby("Product")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )
else:
    top_product = "N/A"

# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
st.subheader("Executive Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "💰 Total Sales",
        f"₹{total_sales:,.2f}"
    )

with col2:
    st.metric(
        "🧾 Transactions",
        f"{total_transactions:,}"
    )

with col3:
    st.metric(
        "📦 Quantity Sold",
        f"{total_quantity:,}"
    )

with col4:
    st.metric(
        "🛍️ Avg Transaction",
        f"₹{average_transaction:,.2f}"
    )

with col5:
    st.metric(
        "⭐ Avg Rating",
        f"{average_rating:.2f}/5"
    )

st.markdown("---")

# ---------------------------------------------------------
# MAIN CHARTS
# ---------------------------------------------------------
if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

col1, col2 = st.columns(2)

# Sales by product
with col1:
    product_sales = (
        filtered_df.groupby("Product", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig_product = px.bar(
        product_sales,
        x="Sales",
        y="Product",
        orientation="h",
        title="Sales by Product",
        text_auto=".2s"
    )

    fig_product.update_layout(
        yaxis={"categoryorder": "total ascending"},
        height=450
    )

    st.plotly_chart(
        fig_product,
        use_container_width=True
    )

# Sales by branch
with col2:
    branch_sales = (
        filtered_df.groupby(
            ["Branch", "City"],
            as_index=False
        )["Sales"].sum()
    )

    fig_branch = px.bar(
        branch_sales,
        x="Branch",
        y="Sales",
        color="City",
        title="Branch Performance",
        text_auto=".2s"
    )

    fig_branch.update_layout(height=450)

    st.plotly_chart(
        fig_branch,
        use_container_width=True
    )

# ---------------------------------------------------------
# SALES TREND
# ---------------------------------------------------------
st.subheader("📈 Sales Trend")

daily_sales = (
    filtered_df.groupby("Date", as_index=False)["Sales"]
    .sum()
    .sort_values("Date")
)

fig_trend = px.line(
    daily_sales,
    x="Date",
    y="Sales",
    markers=True,
    title="Daily Sales Trend"
)

fig_trend.update_layout(height=450)

st.plotly_chart(
    fig_trend,
    use_container_width=True
)

# ---------------------------------------------------------
# CATEGORY / PRODUCT GROUPING
# ---------------------------------------------------------
st.subheader("📊 Product Performance")

col1, col2 = st.columns(2)

with col1:
    category_sales = (
        filtered_df.groupby("Product", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig_category = px.pie(
        category_sales,
        names="Product",
        values="Sales",
        title="Sales Share by Product"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

with col2:
    payment_counts = (
        filtered_df["Payment_Method"]
        .value_counts()
        .reset_index()
    )

    payment_counts.columns = [
        "Payment_Method",
        "Transactions"
    ]

    fig_payment = px.bar(
        payment_counts,
        x="Payment_Method",
        y="Transactions",
        title="Payment Method Usage",
        text_auto=True
    )

    st.plotly_chart(
        fig_payment,
        use_container_width=True
    )

# ---------------------------------------------------------
# CUSTOMER ANALYSIS
# ---------------------------------------------------------
st.subheader("👥 Customer Analysis")

col1, col2 = st.columns(2)

with col1:
    customer_sales = (
        filtered_df.groupby("Customer_Type", as_index=False)["Sales"]
        .mean()
    )

    customer_sales.rename(
        columns={"Sales": "Average_Sales"},
        inplace=True
    )

    fig_customer = px.bar(
        customer_sales,
        x="Customer_Type",
        y="Average_Sales",
        title="Average Transaction by Customer Type",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig_customer,
        use_container_width=True
    )

with col2:
    rating_by_branch = (
        filtered_df.groupby("Branch", as_index=False)["Rating"]
        .mean()
    )

    fig_rating = px.bar(
        rating_by_branch,
        x="Branch",
        y="Rating",
        title="Average Rating by Branch",
        text_auto=".2f"
    )

    fig_rating.update_yaxes(range=[0, 5])

    st.plotly_chart(
        fig_rating,
        use_container_width=True
    )

# ---------------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------------
st.subheader("💡 Business Insights")

product_summary = (
    filtered_df.groupby("Product")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

branch_summary = (
    filtered_df.groupby("Branch")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

payment_summary = (
    filtered_df["Payment_Method"]
    .value_counts()
)

customer_summary = (
    filtered_df.groupby("Customer_Type")["Sales"]
    .mean()
)

insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    st.info(
        f"**Top Product**\n\n"
        f"{product_summary.index[0]} generated "
        f"₹{product_summary.iloc[0]:,.2f} in sales."
    )

with insight_col2:
    st.info(
        f"**Top Branch**\n\n"
        f"Branch {branch_summary.index[0]} generated "
        f"₹{branch_summary.iloc[0]:,.2f} in sales."
    )

with insight_col3:
    st.info(
        f"**Most Used Payment**\n\n"
        f"{payment_summary.index[0]} was used in "
        f"{payment_summary.iloc[0]} transactions."
    )

# ---------------------------------------------------------
# DATA TABLE
# ---------------------------------------------------------
with st.expander("🔎 View Filtered Transaction Data"):
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")

st.caption(
    "Supermarket Sales Intelligence Dashboard | "
    "Built with Python, Pandas, Plotly and Streamlit"
)
