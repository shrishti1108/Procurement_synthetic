
import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(page_title="Procurement Risk Analytics Dashboard",
                   layout="wide")

st.title("Procurement Risk Analytics Dashboard")

# ----------------------------
# Load Data
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("procurement_synthetic_data.csv")
    df["PO_Date"] = pd.to_datetime(df["PO_Date"], dayfirst=True)
    return df

df = load_data()

# ----------------------------
# Sidebar Filters
# ----------------------------
st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Select Region",
    df["Region"].unique(),
    default=df["Region"].unique()
)

vendor = st.sidebar.multiselect(
    "Select Vendor",
    df["Vendor_Name"].unique(),
    default=df["Vendor_Name"].unique()
)

status = st.sidebar.multiselect(
    "PO Status",
    df["PO_Status"].unique(),
    default=df["PO_Status"].unique()
)

filtered_df = df[
    (df["Region"].isin(region)) &
    (df["Vendor_Name"].isin(vendor)) &
    (df["PO_Status"].isin(status))
]

# ----------------------------
# KPI Metrics
# ----------------------------
total_spend = filtered_df["Total_PO_Amount"].sum()
total_pos = filtered_df["PO_ID"].nunique()
vendors = filtered_df["Vendor_Name"].nunique()
high_value_pos = filtered_df[filtered_df["Total_PO_Amount"] > 500000].shape[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Procurement Spend", f"₹{total_spend:,.0f}")
col2.metric("Total Purchase Orders", total_pos)
col3.metric("Active Vendors", vendors)
col4.metric("High Value POs (>500k)", high_value_pos)

st.markdown("---")

# ----------------------------
# Spend by Vendor
# ----------------------------
vendor_spend = (
    filtered_df.groupby("Vendor_Name")["Total_PO_Amount"]
    .sum()
    .reset_index()
)

fig_vendor = px.bar(
    vendor_spend,
    x="Vendor_Name",
    y="Total_PO_Amount",
    title="Spend by Vendor"
)

# ----------------------------
# Spend by Region
# ----------------------------
region_spend = (
    filtered_df.groupby("Region")["Total_PO_Amount"]
    .sum()
    .reset_index()
)

fig_region = px.pie(
    region_spend,
    names="Region",
    values="Total_PO_Amount",
    title="Spend by Region"
)

col1, col2 = st.columns(2)
col1.plotly_chart(fig_vendor, use_container_width=True)
col2.plotly_chart(fig_region, use_container_width=True)

# ----------------------------
# Vendor Category Distribution
# ----------------------------
vendor_cat = (
    filtered_df.groupby("Vendor_Category")["Vendor_Name"]
    .count()
    .reset_index()
)

fig_vendor_cat = px.pie(
    vendor_cat,
    names="Vendor_Category",
    values="Vendor_Name",
    title="Vendor Category Distribution"
)

# ----------------------------
# Spend by Business Unit
# ----------------------------
bu_spend = (
    filtered_df.groupby("Business_Unit")["Total_PO_Amount"]
    .sum()
    .reset_index()
)

fig_bu = px.bar(
    bu_spend,
    x="Business_Unit",
    y="Total_PO_Amount",
    title="Spend by Business Unit"
)

col1, col2 = st.columns(2)
col1.plotly_chart(fig_vendor_cat, use_container_width=True)
col2.plotly_chart(fig_bu, use_container_width=True)

# ----------------------------
# PO Status Monitoring
# ----------------------------
status_dist = (
    filtered_df.groupby("PO_Status")["PO_ID"]
    .count()
    .reset_index()
)

fig_status = px.pie(
    status_dist,
    names="PO_Status",
    values="PO_ID",
    title="PO Status Distribution"
)

# ----------------------------
# Buyer Activity
# ----------------------------
buyer_activity = (
    filtered_df.groupby("Buyer")["PO_ID"]
    .count()
    .reset_index()
)

fig_buyer = px.bar(
    buyer_activity,
    x="Buyer",
    y="PO_ID",
    title="POs by Buyer"
)

col1, col2 = st.columns(2)
col1.plotly_chart(fig_status, use_container_width=True)
col2.plotly_chart(fig_buyer, use_container_width=True)

# ----------------------------
# Procurement Trend Over Time
# ----------------------------
trend = (
    filtered_df.groupby(filtered_df["PO_Date"].dt.to_period("M"))["Total_PO_Amount"]
    .sum()
    .reset_index()
)

trend["PO_Date"] = trend["PO_Date"].astype(str)

fig_trend = px.line(
    trend,
    x="PO_Date",
    y="Total_PO_Amount",
    title="Procurement Spend Trend"
)

st.plotly_chart(fig_trend, use_container_width=True)

# ----------------------------
# High Value Transactions Table
# ----------------------------
st.subheader("High Value Purchase Orders (Risk Monitoring)")

high_value = filtered_df[filtered_df["Total_PO_Amount"] > 500000]

st.dataframe(high_value[[
    "PO_ID",
    "PO_Date",
    "Vendor_Name",
    "Business_Unit",
    "Buyer",
    "Region",
    "Total_PO_Amount"
]])
