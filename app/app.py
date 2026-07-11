import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).resolve().with_name("retail_dashboard.db")

st.set_page_config(page_title="Retail Sales & Customer Insights", layout="wide")
st.title("Retail Sales & Customer Insights Dashboard")

if not DB_PATH.exists():
    st.error("Database not found. Run notebooks/build_db.py first.")
    st.stop()

conn = sqlite3.connect(DB_PATH)

orders = pd.read_sql_query(
    """
    SELECT o.order_id, o.customer_id, o.order_purchase_timestamp, o.order_delivered_customer_date,
           o.order_estimated_delivery_date, o.order_status
    FROM orders o
    """,
    conn,
)
customers = pd.read_sql_query("SELECT * FROM customers", conn)
order_items = pd.read_sql_query("SELECT * FROM order_items", conn)
products = pd.read_sql_query("SELECT * FROM products", conn)
reviews = pd.read_sql_query("SELECT * FROM reviews", conn)

# Prepare derived columns
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
orders["order_delivered_customer_date"] = pd.to_datetime(orders["order_delivered_customer_date"], errors="coerce")
orders["order_estimated_delivery_date"] = pd.to_datetime(orders["order_estimated_delivery_date"], errors="coerce")
orders["delivery_days"] = (orders["order_delivered_customer_date"] - orders["order_purchase_timestamp"]).dt.days
orders["late_delivery"] = orders["order_delivered_customer_date"] > orders["order_estimated_delivery_date"]

merged = orders.merge(customers[["customer_id", "customer_state"]], on="customer_id", how="left")
merged = merged.merge(order_items, on="order_id", how="left")
merged = merged.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
merged = merged.merge(reviews[["order_id", "review_score"]], on="order_id", how="left")
merged["price"] = merged["price"].fillna(0)
merged["freight_value"] = merged["freight_value"].fillna(0)
merged["revenue_value"] = merged["price"] + merged["freight_value"]

# Sidebar filters
st.sidebar.header("Filters")
min_date = merged["order_purchase_timestamp"].min().date()
max_date = merged["order_purchase_timestamp"].max().date()
selected_date_range = st.sidebar.date_input("Date range", [min_date, max_date])
selected_state = st.sidebar.selectbox("State", ["All"] + sorted(merged["customer_state"].dropna().unique().tolist()))
selected_category = st.sidebar.selectbox("Category", ["All"] + sorted(merged["product_category_name"].dropna().unique().tolist()))

if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered = merged[(merged["order_purchase_timestamp"].dt.date >= start_date) & (merged["order_purchase_timestamp"].dt.date <= end_date)]
else:
    filtered = merged.copy()

if selected_state != "All":
    filtered = filtered[filtered["customer_state"] == selected_state]
if selected_category != "All":
    filtered = filtered[filtered["product_category_name"] == selected_category]

# KPIs
revenue = filtered["revenue_value"].sum()
orders_count = filtered["order_id"].nunique()
avg_delivery = filtered["delivery_days"].dropna().mean()
avg_review = filtered["review_score"].dropna().mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", f"R$ {revenue:,.2f}")
col2.metric("Orders", f"{orders_count:,}")
col3.metric("Avg delivery time", f"{avg_delivery:,.1f} days")
col4.metric("Avg review score", f"{avg_review:,.1f}")

# Charts
monthly = (
    filtered.groupby(filtered["order_purchase_timestamp"].dt.to_period("M"))
    .agg(revenue=("revenue_value", "sum"), orders=("order_id", "nunique"))
    .reset_index()
)
monthly["month"] = monthly["order_purchase_timestamp"].astype(str)

st.subheader("Revenue trend")
st.line_chart(monthly.set_index("month")["revenue"])

col_left, col_right = st.columns(2)
with col_left:
    category_summary = (
        filtered.groupby("product_category_name")
        .agg(revenue=("revenue_value", "sum"))
        .reset_index()
    )
    category_summary = category_summary.sort_values("revenue", ascending=False).head(10)
    st.subheader("Top categories")
    st.bar_chart(category_summary.set_index("product_category_name")["revenue"])

with col_right:
    state_summary = filtered.groupby("customer_state").agg(
        avg_delivery_days=("delivery_days", "mean"),
        avg_review_score=("review_score", "mean"),
    ).reset_index()
    st.subheader("Delivery performance by state")
    st.bar_chart(state_summary.set_index("customer_state")["avg_delivery_days"])

st.subheader("Late deliveries and review scores")
late_summary = filtered.groupby("late_delivery").agg(orders=("order_id", "nunique"), avg_review_score=("review_score", "mean")).reset_index()
st.bar_chart(late_summary.set_index("late_delivery")["avg_review_score"])

conn.close()
