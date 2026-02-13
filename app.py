import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(
    page_title="E-commerce Revenue Dashboard",
    page_icon="📊",
    layout="wide"
)

# =====================================
# CUSTOM STYLE (Premium Feel)
# =====================================
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
        }
        .metric-card {
            background-color: #111827;
            padding: 20px;
            border-radius: 12px;
            color: white;
        }
        .metric-title {
            font-size: 14px;
            color: #9CA3AF;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# =====================================
# LOAD DATA
# =====================================
@st.cache_data
def load_data():
    df = pd.read_csv("tht_streamlit_small.csv")
    df["year_month"] = pd.to_datetime(df["year_month"])
    return df

df = load_data()

# =====================================
# SIDEBAR FILTER
# =====================================
st.sidebar.title("📌 Filter Panel")

selected_country = st.sidebar.multiselect(
    "Select Country",
    options=sorted(df["country"].unique()),
    default=sorted(df["country"].unique())
)

df_filtered = df[df["country"].isin(selected_country)]

# =====================================
# KPI CALCULATION (FINAL CORRECT LOGIC)
# =====================================

total_net_revenue = df_filtered["net_revenue"].sum()
total_orders = df_filtered["order_id"].nunique()

# ---- REPEAT RATE (UNIQUE CUSTOMER BASED) ----
customer_summary = (
    df_filtered
    .groupby("user_id")["customer_type"]
    .first()
)

repeat_rate = (
    (customer_summary == "Repeat").sum()
    / customer_summary.count()
) * 100

# ---- RETURN RATE (PER ORDER) ----
return_rate = (
    (df_filtered["order_status"] == "Returned").sum()
    / df_filtered["order_id"].nunique()
) * 100

# =====================================
# TITLE
# =====================================
st.title("📊 E-commerce Revenue Dashboard")
st.markdown("Executive revenue quality monitoring dashboard")

# =====================================
# KPI ROW
# =====================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Net Revenue", f"${total_net_revenue:,.2f}")

with col2:
    st.metric("Total Orders", f"{total_orders:,}")

with col3:
    st.metric("Repeat Customer Rate", f"{repeat_rate:.2f}%")

with col4:
    st.metric("Return Rate", f"{return_rate:.2f}%")

st.markdown("---")

# =====================================
# REVENUE BY ORDER STATUS
# =====================================
st.subheader("Revenue by Order Status")

status_rev = (
    df_filtered
    .groupby("order_status")["net_revenue"]
    .sum()
    .reset_index()
)

fig_status = px.bar(
    status_rev,
    x="order_status",
    y="net_revenue",
    color="order_status",
    text_auto=".2s"
)

fig_status.update_layout(showlegend=False)

st.plotly_chart(fig_status, use_container_width=True)

# =====================================
# REVENUE BY COUNTRY
# =====================================
st.subheader("Revenue by Country")

country_rev = (
    df_filtered
    .groupby("country")["net_revenue"]
    .sum()
    .reset_index()
    .sort_values(by="net_revenue", ascending=False)
)

fig_country = px.bar(
    country_rev,
    x="country",
    y="net_revenue",
    color="country",
    text_auto=".2s"
)

st.plotly_chart(fig_country, use_container_width=True)

st.markdown("---")

# =====================================
# REVENUE TREND
# =====================================
st.subheader("Revenue Trend Over Time")

trend = (
    df_filtered
    .groupby("year_month")["net_revenue"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend,
    x="year_month",
    y="net_revenue"
)

st.plotly_chart(fig_trend, use_container_width=True)

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption("Built for Take Home Test – Data Analyst | Revenue Quality Monitoring")
