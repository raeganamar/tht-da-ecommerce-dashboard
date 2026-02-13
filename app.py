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
    df = pd.read_csv("tht_streamlit_small.csv", sep=",")
    df.columns = df.columns.str.strip()  # Fix hidden spaces
    return df

df = load_data()

# =============================
# SAFETY CHECK (Avoid Cloud Error)
# =============================
required_cols = [
    "order_id",
    "net_revenue",
    "gross_revenue",
    "country",
    "order_status",
    "customer_type"
]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing column in dataset: {col}")
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
# METRICS (MATCH POWER BI)
# =============================
total_net_revenue = df_filtered["net_revenue"].sum()
total_gross_revenue = df_filtered["gross_revenue"].sum()
total_orders = df_filtered["order_id"].nunique()

repeat_rate = (
    df_filtered["customer_type"]
    .value_counts(normalize=True)
    .get("Repeat", 0)
) * 100

return_rate = (
    (df_filtered["order_status"] == "Returned").sum()
    / len(df_filtered)
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

- Revenue is concentrated in specific countries (China & US dominate).
- Repeat customers contribute ~37%, indicating moderate retention.
- Return rate remains a risk factor impacting revenue quality.
- Revenue growth must be evaluated alongside return impact and customer mix.
"""
)
