import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="E-Commerce Revenue Dashboard",
    layout="wide"
)

# =============================
# LOAD DATA (CLOUD SAFE)
# =============================
@st.cache_data
def load_data():
    df = pd.read_csv("tht_streamlit_small.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# =============================
# AUTO-DETECT IMPORTANT COLUMNS
# =============================
order_col = None
user_col = None

if "order_id" in df.columns:
    order_col = "order_id"
elif "order_item_id" in df.columns:
    order_col = "order_item_id"

if "user_id" in df.columns:
    user_col = "user_id"

required_cols = [
    "net_revenue",
    "gross_revenue",
    "country",
    "order_status"
]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# =============================
# SIDEBAR FILTER
# =============================
st.sidebar.markdown("## 📌 Filter Panel")

selected_countries = st.sidebar.multiselect(
    "Select Country",
    options=sorted(df["country"].unique()),
    default=sorted(df["country"].unique())
)

df_filtered = df[df["country"].isin(selected_countries)]

# =============================
# KPI CALCULATIONS
# =============================

# Revenue (affected by filter)
total_net_revenue = df_filtered["net_revenue"].sum()

if order_col:
    total_orders = df_filtered[order_col].nunique()
else:
    total_orders = len(df_filtered)

# =============================
# GLOBAL METRICS (NOT FILTERED)
# =============================

# ----- REPEAT CUSTOMER RATE (MATCH POWER BI) -----
# Distinct users with >1 distinct order

if user_col and order_col:

    user_order_counts = (
        df.groupby(user_col)[order_col]
        .nunique()
    )

    repeat_customers = (user_order_counts > 1).sum()
    total_customers = user_order_counts.count()

    repeat_rate = (repeat_customers / total_customers) * 100

else:
    repeat_rate = 0


# ----- RETURN RATE (ORDER LEVEL) -----

if order_col:
    order_level = df.drop_duplicates(subset=[order_col])
    return_rate = (
        (order_level["order_status"] == "Returned").sum()
        / len(order_level)
    ) * 100
else:
    return_rate = (
        (df["order_status"] == "Returned").sum()
        / len(df)
    ) * 100


# =============================
# HEADER
# =============================
st.title("📊 E-Commerce Revenue Quality Dashboard")
st.caption("Executive revenue quality monitoring dashboard")

# =============================
# KPI ROW
# =============================
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Net Revenue",
    f"${total_net_revenue:,.2f}"
)

col2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Repeat Customer Rate",
    f"{repeat_rate:.2f}%"
)

col4.metric(
    "Return Rate",
    f"{return_rate:.2f}%"
)

st.markdown("---")

# =============================
# REVENUE BY ORDER STATUS
# =============================
st.subheader("Revenue by Order Status")

status_rev = (
    df_filtered.groupby("order_status")["net_revenue"]
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

# =============================
# REVENUE BY COUNTRY
# =============================
st.subheader("Revenue by Country")

country_rev = (
    df_filtered.groupby("country")["net_revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_country = px.bar(
    country_rev,
    x="country",
    y="net_revenue",
    text_auto=".2s"
)

st.plotly_chart(fig_country, use_container_width=True)

# =============================
# FOOTER INSIGHT
# =============================
st.markdown("---")
st.markdown(
"""
### 🔎 Executive Insight

- Revenue is concentrated in key markets.
- Repeat customers represent a meaningful portion of total customers.
- Return rate directly impacts revenue quality.
- Growth should be evaluated alongside customer retention and return control.
"""
)
