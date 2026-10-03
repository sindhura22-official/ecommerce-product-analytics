import streamlit as st
import pandas as pd


# Page configuration
st.set_page_config(
    page_title="E-Commerce Product Analytics",
    page_icon="📊",
    layout="wide"
)


# Title
st.title("📊 E-Commerce Product Analytics Dashboard")

st.markdown(
    """
    Analyze revenue, products, customers, and cancellations
    using transaction-level e-commerce data.
    """
)


# Load datasets
sales = pd.read_csv(
    "data/processed/clean_sales.csv"
)

product_performance = pd.read_csv(
    "data/processed/product_performance.csv"
)

product_health = pd.read_csv(
    "data/processed/product_health.csv"
)

rfm = pd.read_csv(
    "data/processed/customer_rfm.csv"
)

monthly_business_health = pd.read_csv(
    "data/processed/monthly_business_health.csv"
)


# Convert dates
sales["InvoiceDate"] = pd.to_datetime(
    sales["InvoiceDate"]
)


# Basic KPIs
total_revenue = sales["Revenue"].sum()
total_orders = sales["InvoiceNo"].nunique()
total_units = sales["Quantity"].sum()
total_customers = sales["CustomerID"].nunique()


# KPI cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Revenue",
        f"£{total_revenue:,.0f}"
    )

with col2:
    st.metric(
        "Orders",
        f"{total_orders:,}"
    )

with col3:
    st.metric(
        "Units Sold",
        f"{total_units:,}"
    )

with col4:
    st.metric(
        "Customers",
        f"{total_customers:,}"
    )


st.divider()

st.subheader("Dataset Overview")

st.write(
    f"Sales transactions: {len(sales):,}"
)

st.write(
    f"Products analyzed: {len(product_performance):,}"
)

st.write(
    f"Customers analyzed: {len(rfm):,}"
)
# ============================================================
# MONTHLY BUSINESS PERFORMANCE
# ============================================================

st.divider()

st.header("📈 Monthly Business Performance")

# Create monthly metrics
sales["YearMonth"] = sales["InvoiceDate"].dt.to_period("M").astype(str)

monthly_kpis = (
    sales
    .groupby("YearMonth")
    .agg(
        Revenue=("Revenue", "sum"),
        Orders=("InvoiceNo", "nunique"),
        Units=("Quantity", "sum")
    )
    .reset_index()
)

# Average Order Value
monthly_kpis["AOV"] = (
    monthly_kpis["Revenue"] /
    monthly_kpis["Orders"]
)

# Revenue growth
monthly_kpis["Revenue_Growth_%"] = (
    monthly_kpis["Revenue"]
    .pct_change()
    * 100
)

# Display table
st.subheader("Monthly KPI Summary")

display_kpis = monthly_kpis.copy()

display_kpis["Revenue"] = display_kpis["Revenue"].round(2)
display_kpis["AOV"] = display_kpis["AOV"].round(2)
display_kpis["Revenue_Growth_%"] = (
    display_kpis["Revenue_Growth_%"].round(2)
)

st.dataframe(
    display_kpis,
    use_container_width=True
)
# Revenue trend
st.subheader("Monthly Revenue Trend")

revenue_chart = monthly_kpis.set_index("YearMonth")[["Revenue"]]

st.line_chart(
    revenue_chart,
    use_container_width=True
)
# Orders and units trend

st.subheader("Monthly Orders and Units")

orders_units_chart = monthly_kpis.set_index(
    "YearMonth"
)[["Orders", "Units"]]

st.line_chart(
    orders_units_chart,
    use_container_width=True
)
# Revenue growth

st.subheader("Monthly Revenue Growth")

growth_chart = (
    monthly_kpis
    .dropna(subset=["Revenue_Growth_%"])
    .set_index("YearMonth")[["Revenue_Growth_%"]]
)

st.bar_chart(
    growth_chart,
    use_container_width=True
)
st.divider()

st.header("Product Performance")

st.subheader("Top Products by Revenue")

top_products = (
    product_performance
    .sort_values("Revenue", ascending=False)
    .head(10)
)
display_cols = [
    col for col in
    ["StockCode", "Description", "Revenue", "Units", "Orders"]
    if col in top_products.columns
]

st.dataframe(
    top_products[display_cols],
    use_container_width=True
)
st.subheader("Top 10 Products by Revenue")

product_chart = (
    top_products
    .set_index("Description")[["Revenue"]]
)

st.bar_chart(
    product_chart,
    use_container_width=True
)
st.divider()

st.header("Product Health")

# Product Health summary metrics

total_products = len(product_health)

high_revenue_products = (
    product_health["Revenue_Level"]
    .eq("High Revenue")
    .sum()
)

low_revenue_products = (
    product_health["Revenue_Level"]
    .eq("Low Revenue")
    .sum()
)

products_with_cancellations = (
    product_health["Cancellation_Units"] > 0
).sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Products",
        f"{total_products:,}"
    )

with col2:
    st.metric(
        "High Revenue Products",
        f"{high_revenue_products:,}"
    )

with col3:
    st.metric(
        "Low Revenue Products",
        f"{low_revenue_products:,}"
    )

with col4:
    st.metric(
        "Products with Cancellations",
        f"{products_with_cancellations:,}"
    )

st.subheader("Product Health Analysis")

st.dataframe(
    product_health,
    use_container_width=True
)
st.subheader("Product Health Overview")

col1, col2 = st.columns(2)

# Revenue level distribution
revenue_level_chart = (
    product_health["Revenue_Level"]
    .value_counts()
    .rename_axis("Revenue Level")
    .to_frame("Products")
)

with col1:
    st.bar_chart(
        revenue_level_chart,
        use_container_width=True
    )

# Cancellation rate distribution
cancellation_chart = (
    product_health[
        product_health["Cancellation_Rate_%"] > 0
    ]
    .sort_values(
        "Cancellation_Rate_%",
        ascending=False
    )
    .head(10)
    .set_index("Description")[
        ["Cancellation_Rate_%"]
    ]
)

with col2:
    st.bar_chart(
        cancellation_chart,
        use_container_width=True
    )
    st.subheader("Products with Highest Cancellation Rates")

high_cancellation = (
    product_health[
        product_health["Cancellation_Rate_%"] > 0
    ]
    .sort_values(
        "Cancellation_Rate_%",
        ascending=False
    )
    .head(10)
)


st.dataframe(
    high_cancellation[
        [
            "StockCode",
            "Description",
            "Revenue",
            "Units_Sold",
            "Orders",
            "Cancellation_Units",
            "Cancellation_Value",
            "Cancellation_Rate_%"
        ]
    ],
    use_container_width=True
)
st.divider()

st.header("Customer Analysis")

st.subheader("Customer Overview")

customer_rfm = pd.read_csv(
    "data/processed/customer_rfm.csv"
)

# Customer KPIs

total_customers = customer_rfm["CustomerID"].nunique()

average_customer_revenue = customer_rfm["Monetary"].mean()

repeat_customers = (
    customer_rfm["Frequency"] > 1
).sum()

high_value_customers = (
    customer_rfm["Segment"]
    .isin([
        "High-Value Active",
        "Recent High-Value",
        "At-Risk High-Value"
    ])
).sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Customers", f"{total_customers:,}")

with col2:
    st.metric(
        "Avg Customer Revenue",
        f"£{average_customer_revenue:,.2f}"
    )

with col3:
    st.metric(
        "Repeat Customers",
        f"{repeat_customers:,}"
    )

with col4:
    st.metric(
        "High-Value Customers",
        f"{high_value_customers:,}"
    )
st.subheader("Customer Segmentation")

segment_counts = (
    customer_rfm["Segment"]
    .value_counts()
    .rename_axis("Segment")
    .to_frame("Customers")
)

st.bar_chart(
    segment_counts,
    use_container_width=True
)
st.subheader("Top Customers by Monetary Value")

top_customers = (
    customer_rfm
    .sort_values("Monetary", ascending=False)
    .head(10)
)

st.dataframe(
    top_customers[
        [
            "CustomerID",
            "Recency",
            "Frequency",
            "Monetary",
            "RFM_Score",
            "Segment"
        ]
    ],
    use_container_width=True
)
st.subheader("Customer Segment Distribution")

segment_counts = (
    customer_rfm["Segment"]
    .value_counts()
    .rename_axis("Segment")
    .to_frame("Customers")
)

st.bar_chart(
    segment_counts,
    width="stretch"
)
st.divider()

st.header("Cancellation Analysis")
st.subheader("Cancellation Overview")

total_cancelled_units = product_health["Cancellation_Units"].sum()

total_cancellation_value = product_health["Cancellation_Value"].sum()

avg_cancellation_rate = product_health[
    "Cancellation_Rate_%"
].mean()

high_cancellation_products = (
    product_health["Cancellation_Rate_%"] > 20
).sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Cancelled Units",
        f"{total_cancelled_units:,.0f}"
    )

with col2:
    st.metric(
        "Cancellation Value",
        f"£{total_cancellation_value:,.2f}"
    )

with col3:
    st.metric(
        "Avg Cancellation Rate",
        f"{avg_cancellation_rate:.2f}%"
    )

with col4:
    st.metric(
        "High Cancellation Products",
        f"{high_cancellation_products:,}"
    )
    st.subheader("Products with Highest Cancellation Rates")

high_cancellation = (
    product_health[
        product_health["Cancellation_Rate_%"] > 0
    ]
    .sort_values(
        "Cancellation_Rate_%",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    high_cancellation[
        [
            "StockCode",
            "Description",
            "Revenue",
            "Units_Sold",
            "Orders",
            "Cancellation_Units",
            "Cancellation_Value",
            "Cancellation_Rate_%"
        ]
    ],
    width="stretch"
)
cancellation_chart = (
    high_cancellation
    .set_index("Description")[
        ["Cancellation_Rate_%"]
    ]
)

st.bar_chart(
    cancellation_chart,
    width="stretch"
)  
st.divider()
st.header("Dashboard Summary")

st.write("""
This dashboard provides an overview of revenue, product performance,
customer behavior, and cancellation patterns using transaction-level
e-commerce data.
""")  