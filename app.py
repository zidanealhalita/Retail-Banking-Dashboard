"""
================================================================================
 RETAIL BANKING ANALYTICS DASHBOARD
 Author  : Muhammad Zidane Alhalita
 Purpose : Interactive analytics dashboard for retail banking transaction data
           - Customer segmentation & RFM analysis
           - Product adoption (Credit Card / Mutual Fund) analytics
           - Geographic & demographic insights
           - Transaction behavior & trend analysis
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Retail Banking Analytics Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# Custom CSS for a cleaner, more "banking BI" look
# ------------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Force a consistent dark look regardless of the visitor's device/browser theme */
    html, body, .stApp, .main {
        background-color: #0E1117 !important;
        color: #E5E7EB !important;
    }

    div[data-testid="stMetric"] {
        background-color: #1B2130 !important;
        border: 1px solid #2A3244;
        border-radius: 10px;
        padding: 15px 15px 10px 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }
    div[data-testid="stMetricLabel"] * { font-weight: 600; color: #9CA3AF !important; }
    div[data-testid="stMetricValue"] * { color: #F9FAFB !important; }

    .insight-box {
        background-color: #16233B;
        border-left: 5px solid #3B82F6;
        padding: 12px 18px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-size: 0.95rem;
        color: #E5E7EB;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #F3F4F6;
        margin-top: 10px;
    }

    section[data-testid="stSidebar"] {
        background-color: #12151C !important;
    }

    button[data-baseweb="tab"] { color: #9CA3AF; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #3B82F6; }

    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

PRIMARY_COLOR = "#3B82F6"
SEQ_COLORS = px.colors.sequential.Blues
CAT_COLORS = px.colors.qualitative.Set2
PLOTLY_TEMPLATE = "plotly_dark"
px.defaults.template = PLOTLY_TEMPLATE
px.defaults.color_discrete_sequence = CAT_COLORS


# ==============================================================================
# DATA LOADING & PREPROCESSING
# ==============================================================================
@st.cache_data
def load_data(path="data/retail_banking_dataset.csv"):
    df = pd.read_csv(path)
    df["Transaction_Date"] = pd.to_datetime(df["Transaction_Date"])

    df["Year"] = df["Transaction_Date"].dt.year
    df["Month"] = df["Transaction_Date"].dt.to_period("M").astype(str)
    df["Month_Name"] = df["Transaction_Date"].dt.strftime("%b %Y")
    df["Weekday"] = df["Transaction_Date"].dt.day_name()
    df["Week_Num"] = df["Transaction_Date"].dt.isocalendar().week

    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["Weekday"] = pd.Categorical(df["Weekday"], categories=weekday_order, ordered=True)

    bins = [17, 25, 35, 45, 55, 65]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-64"]
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels, include_lowest=True)

    amt_bins = [0, 100_000, 500_000, 1_000_000, 2_500_000, 5_000_001]
    amt_labels = ["<100K", "100K-500K", "500K-1M", "1M-2.5M", ">2.5M"]
    df["Amount_Bracket"] = pd.cut(df["Amount_IDR"], bins=amt_bins, labels=amt_labels, include_lowest=True)

    df["Has_Credit_Card"] = df["Has_Credit_Card"].astype(int)
    df["Has_Mutual_Fund"] = df["Has_Mutual_Fund"].astype(int)

    return df


df_raw = load_data()

# ==============================================================================
# SIDEBAR — FILTERS
# ==============================================================================
st.sidebar.title("🏦 Bank Analytics")
st.sidebar.markdown("**Dashboard by Muhammad Zidane Alhalita**")
st.sidebar.markdown("---")
st.sidebar.header("🔎 Filter Data")

min_date, max_date = df_raw["Transaction_Date"].min(), df_raw["Transaction_Date"].max()
date_range = st.sidebar.date_input(
    "Rentang Tanggal Transaksi",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

locations = st.sidebar.multiselect(
    "Lokasi", options=sorted(df_raw["Location"].unique()), default=sorted(df_raw["Location"].unique())
)
tx_types = st.sidebar.multiselect(
    "Jenis Transaksi", options=sorted(df_raw["Transaction_Type"].unique()), default=sorted(df_raw["Transaction_Type"].unique())
)
genders = st.sidebar.multiselect(
    "Gender", options=sorted(df_raw["Gender"].unique()), default=sorted(df_raw["Gender"].unique())
)
mb_status = st.sidebar.multiselect(
    "Status Mobile Banking", options=sorted(df_raw["Mobile_Banking_Status"].unique()), default=sorted(df_raw["Mobile_Banking_Status"].unique())
)
age_range = st.sidebar.slider(
    "Rentang Usia", int(df_raw["Age"].min()), int(df_raw["Age"].max()),
    (int(df_raw["Age"].min()), int(df_raw["Age"].max()))
)
amount_range = st.sidebar.slider(
    "Rentang Nominal Transaksi (IDR)",
    float(df_raw["Amount_IDR"].min()), float(df_raw["Amount_IDR"].max()),
    (float(df_raw["Amount_IDR"].min()), float(df_raw["Amount_IDR"].max())),
    step=10000.0, format="%.0f"
)

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Reset Semua Filter"):
    st.rerun()

# Apply filters
mask = (
    (df_raw["Transaction_Date"] >= pd.to_datetime(start_date))
    & (df_raw["Transaction_Date"] <= pd.to_datetime(end_date))
    & (df_raw["Location"].isin(locations))
    & (df_raw["Transaction_Type"].isin(tx_types))
    & (df_raw["Gender"].isin(genders))
    & (df_raw["Mobile_Banking_Status"].isin(mb_status))
    & (df_raw["Age"].between(age_range[0], age_range[1]))
    & (df_raw["Amount_IDR"].between(amount_range[0], amount_range[1]))
)
df = df_raw.loc[mask].copy()

st.sidebar.markdown("---")
st.sidebar.caption(f"📊 Menampilkan **{len(df):,}** dari **{len(df_raw):,}** total transaksi")

# ==============================================================================
# HEADER
# ==============================================================================
st.title("🏦 Retail Banking Analytics Dashboard")
st.markdown(
    "Analisis interaktif atas perilaku transaksi, adopsi produk, dan segmentasi nasabah "
    "perbankan ritel — dibangun untuk mendukung pengambilan keputusan berbasis data."
)
st.markdown("---")

if df.empty:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

# ==============================================================================
# KPI ROW
# ==============================================================================
total_tx = len(df)
total_volume = df["Amount_IDR"].sum()
avg_tx_value = df["Amount_IDR"].mean()
unique_customers = df["Customer_ID"].nunique()
active_mb_pct = (df["Mobile_Banking_Status"] == "Active").mean() * 100
cc_penetration = df.drop_duplicates("Customer_ID")["Has_Credit_Card"].mean() * 100
mf_penetration = df.drop_duplicates("Customer_ID")["Has_Mutual_Fund"].mean() * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Transaksi", f"{total_tx:,}")
k2.metric("Total Volume Transaksi", f"Rp {total_volume/1e9:,.2f} M")
k3.metric("Rata-rata Nilai Transaksi", f"Rp {avg_tx_value:,.0f}")
k4.metric("Jumlah Nasabah Unik", f"{unique_customers:,}")

k5, k6, k7, k8 = st.columns(4)
k5.metric("Mobile Banking Aktif", f"{active_mb_pct:.1f}%")
k6.metric("Penetrasi Kartu Kredit", f"{cc_penetration:.1f}%")
k7.metric("Penetrasi Reksa Dana", f"{mf_penetration:.1f}%")
k8.metric("Median Nilai Transaksi", f"Rp {df['Amount_IDR'].median():,.0f}")

st.markdown("---")

# ==============================================================================
# TABS
# ==============================================================================
tab_overview, tab_trend, tab_customer, tab_product, tab_geo, tab_deep, tab_data = st.tabs(
    [
        "📈 Overview",
        "🗓️ Tren Waktu",
        "👥 Segmentasi Nasabah",
        "💳 Adopsi Produk",
        "🗺️ Analisis Geografis",
        "🔬 Deep Dive & Korelasi",
        "🧾 Data Explorer",
    ]
)

# ------------------------------------------------------------------------------
# TAB 1: OVERVIEW
# ------------------------------------------------------------------------------
with tab_overview:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="section-title">Distribusi Jenis Transaksi</p>', unsafe_allow_html=True)
        tx_counts = df["Transaction_Type"].value_counts().reset_index()
        tx_counts.columns = ["Transaction_Type", "Count"]
        fig = px.pie(
            tx_counts, names="Transaction_Type", values="Count", hole=0.45,
            color_discrete_sequence=CAT_COLORS
        )
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(showlegend=True, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        top_type = tx_counts.iloc[0]
        st.markdown(
            f'<div class="insight-box">💡 <b>{top_type["Transaction_Type"]}</b> adalah jenis transaksi paling dominan, '
            f'mencakup <b>{top_type["Count"]/total_tx*100:.1f}%</b> dari seluruh transaksi pada rentang filter saat ini.</div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown('<p class="section-title">Volume Nominal per Jenis Transaksi</p>', unsafe_allow_html=True)
        vol_by_type = df.groupby("Transaction_Type", observed=True)["Amount_IDR"].sum().sort_values(ascending=True).reset_index()
        fig = px.bar(
            vol_by_type, x="Amount_IDR", y="Transaction_Type", orientation="h",
            color="Amount_IDR", color_continuous_scale=SEQ_COLORS,
            labels={"Amount_IDR": "Total Volume (IDR)", "Transaction_Type": ""}
        )
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        top_vol_type = vol_by_type.iloc[-1]
        st.markdown(
            f'<div class="insight-box">💡 Meski volume transaksi tertinggi berbeda dari jumlah transaksi terbanyak, '
            f'<b>{top_vol_type["Transaction_Type"]}</b> menyumbang nilai nominal terbesar '
            f'(Rp {top_vol_type["Amount_IDR"]/1e9:,.2f} M), mengindikasikan nilai rata-rata per transaksi yang tinggi.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<p class="section-title">Distribusi Nominal Transaksi</p>', unsafe_allow_html=True)
        fig = px.histogram(
            df, x="Amount_IDR", nbins=50, color_discrete_sequence=[PRIMARY_COLOR],
            labels={"Amount_IDR": "Nominal Transaksi (IDR)"}
        )
        fig.add_vline(x=df["Amount_IDR"].median(), line_dash="dash", line_color="red",
                       annotation_text="Median", annotation_position="top")
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.markdown('<p class="section-title">Segmen Nominal Transaksi (Bracket)</p>', unsafe_allow_html=True)
        bracket_counts = df["Amount_Bracket"].value_counts().sort_index().reset_index()
        bracket_counts.columns = ["Bracket", "Count"]
        fig = px.bar(
            bracket_counts, x="Bracket", y="Count", color="Count",
            color_continuous_scale=SEQ_COLORS, text="Count"
        )
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    skew_note = "positively skewed (didominasi transaksi bernominal kecil dengan sejumlah transaksi besar)" \
        if df["Amount_IDR"].skew() > 0.5 else "relatif simetris"
    st.markdown(
        f'<div class="insight-box">💡 Distribusi nominal transaksi cenderung <b>{skew_note}</b>, '
        f'dengan rata-rata (Rp {df["Amount_IDR"].mean():,.0f}) berada di atas median (Rp {df["Amount_IDR"].median():,.0f}) — '
        f'ciri khas data finansial pada umumnya.</div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------------------
# TAB 2: TREN WAKTU
# ------------------------------------------------------------------------------
with tab_trend:
    st.markdown('<p class="section-title">Tren Jumlah & Volume Transaksi Bulanan</p>', unsafe_allow_html=True)
    monthly = df.groupby("Month").agg(
        Jumlah_Transaksi=("Transaction_ID", "count"),
        Volume=("Amount_IDR", "sum"),
    ).reset_index().sort_values("Month")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Jumlah_Transaksi"], name="Jumlah Transaksi",
                          marker_color=PRIMARY_COLOR, yaxis="y1", opacity=0.7))
    fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Volume"], name="Volume (IDR)",
                              mode="lines+markers", line=dict(color="#F97316", width=3), yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="Jumlah Transaksi"),
        yaxis2=dict(title="Volume (IDR)", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    trend_slope = monthly["Jumlah_Transaksi"].iloc[-3:].mean() - monthly["Jumlah_Transaksi"].iloc[:3].mean()
    trend_dir = "meningkat" if trend_slope > 0 else "menurun"
    st.markdown(
        f'<div class="insight-box">💡 Jumlah transaksi bulanan pada periode akhir cenderung <b>{trend_dir}</b> '
        f'dibandingkan periode awal filter, mengindikasikan {"pertumbuhan aktivitas nasabah" if trend_slope > 0 else "perlunya strategi re-engagement nasabah"}.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<p class="section-title">Pola Transaksi per Hari dalam Seminggu</p>', unsafe_allow_html=True)
        dow = df.groupby("Weekday", observed=True).size().reset_index(name="Count")
        fig = px.bar(dow, x="Weekday", y="Count", color="Count", color_continuous_scale=SEQ_COLORS, text="Count")
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">Heatmap: Hari vs Jenis Transaksi</p>', unsafe_allow_html=True)
        heat = df.groupby(["Weekday", "Transaction_Type"], observed=True).size().reset_index(name="Count")
        heat_pivot = heat.pivot(index="Weekday", columns="Transaction_Type", values="Count").fillna(0)
        fig = px.imshow(
            heat_pivot, color_continuous_scale=SEQ_COLORS, aspect="auto",
            labels=dict(color="Jumlah")
        )
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    busiest_day = dow.loc[dow["Count"].idxmax(), "Weekday"]
    st.markdown(
        f'<div class="insight-box">💡 <b>{busiest_day}</b> merupakan hari dengan aktivitas transaksi tertinggi, '
        f'berguna untuk perencanaan kapasitas sistem dan customer service.</div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------------------
# TAB 3: SEGMENTASI NASABAH
# ------------------------------------------------------------------------------
with tab_customer:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="section-title">Distribusi Usia Nasabah</p>', unsafe_allow_html=True)
        fig = px.histogram(df.drop_duplicates("Customer_ID"), x="Age", nbins=25, color_discrete_sequence=[PRIMARY_COLOR])
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">Komposisi Gender</p>', unsafe_allow_html=True)
        gender_counts = df.drop_duplicates("Customer_ID")["Gender"].value_counts().reset_index()
        gender_counts.columns = ["Gender", "Count"]
        fig = px.pie(gender_counts, names="Gender", values="Count", hole=0.45, color_discrete_sequence=CAT_COLORS)
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">Rata-rata Nilai Transaksi per Kelompok Usia</p>', unsafe_allow_html=True)
    age_group_avg = df.groupby("Age_Group", observed=True)["Amount_IDR"].mean().reset_index()
    fig = px.bar(age_group_avg, x="Age_Group", y="Amount_IDR", color="Amount_IDR",
                 color_continuous_scale=SEQ_COLORS, text_auto=".2s")
    fig.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">🎯 Segmentasi RFM (Recency, Frequency, Monetary)</p>', unsafe_allow_html=True)
    st.caption("RFM dihitung berdasarkan data transaksi pada rentang filter yang dipilih.")

    ref_date = df["Transaction_Date"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("Customer_ID").agg(
        Recency=("Transaction_Date", lambda x: (ref_date - x.max()).days),
        Frequency=("Transaction_ID", "count"),
        Monetary=("Amount_IDR", "sum"),
    ).reset_index()

    rfm["R_Score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1], duplicates="drop").astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4], duplicates="drop").astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4], duplicates="drop").astype(int)
    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

    def segment_customer(score):
        if score >= 10:
            return "Champions"
        elif score >= 8:
            return "Loyal Customers"
        elif score >= 6:
            return "Potential Loyalist"
        elif score >= 4:
            return "At Risk"
        else:
            return "Need Attention"

    rfm["Segment"] = rfm["RFM_Score"].apply(segment_customer)

    c3, c4 = st.columns([1, 1.3])
    with c3:
        seg_counts = rfm["Segment"].value_counts().reset_index()
        seg_counts.columns = ["Segment", "Count"]
        fig = px.bar(seg_counts.sort_values("Count"), x="Count", y="Segment", orientation="h",
                     color="Count", color_continuous_scale=SEQ_COLORS, text="Count")
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.scatter(
            rfm, x="Frequency", y="Monetary", size="Recency", color="Segment",
            hover_data=["Customer_ID"], color_discrete_sequence=CAT_COLORS,
            labels={"Frequency": "Frekuensi Transaksi", "Monetary": "Total Nilai Transaksi (IDR)"}
        )
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    top_segment = seg_counts.sort_values("Count", ascending=False).iloc[0]
    champions_pct = (rfm["Segment"] == "Champions").mean() * 100
    st.markdown(
        f'<div class="insight-box">💡 Segmen terbesar adalah <b>{top_segment["Segment"]}</b> '
        f'({top_segment["Count"]} nasabah). Sebanyak <b>{champions_pct:.1f}%</b> nasabah termasuk kategori '
        f'<b>Champions</b> — nasabah paling bernilai yang perlu dipertahankan melalui program loyalitas. '
        f'Segmen <b>At Risk</b> dan <b>Need Attention</b> berpotensi menjadi target kampanye reaktivasi.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("📋 Lihat Tabel Detail RFM per Nasabah"):
        st.dataframe(rfm.sort_values("RFM_Score", ascending=False), use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: ADOPSI PRODUK
# ------------------------------------------------------------------------------
with tab_product:
    cust_df = df.drop_duplicates("Customer_ID").copy()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="section-title">Kepemilikan Kartu Kredit</p>', unsafe_allow_html=True)
        cc_counts = cust_df["Has_Credit_Card"].map({1: "Punya", 0: "Tidak Punya"}).value_counts().reset_index()
        cc_counts.columns = ["Status", "Count"]
        fig = px.pie(cc_counts, names="Status", values="Count", hole=0.45, color_discrete_sequence=CAT_COLORS)
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">Kepemilikan Reksa Dana</p>', unsafe_allow_html=True)
        mf_counts = cust_df["Has_Mutual_Fund"].map({1: "Punya", 0: "Tidak Punya"}).value_counts().reset_index()
        mf_counts.columns = ["Status", "Count"]
        fig = px.pie(mf_counts, names="Status", values="Count", hole=0.45, color_discrete_sequence=CAT_COLORS)
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">Status Mobile Banking vs Kepemilikan Produk</p>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        cross1 = cust_df.groupby(["Mobile_Banking_Status", "Has_Credit_Card"], observed=True).size().reset_index(name="Count")
        cross1["Has_Credit_Card"] = cross1["Has_Credit_Card"].map({1: "Punya CC", 0: "Tidak Punya CC"})
        fig = px.bar(cross1, x="Mobile_Banking_Status", y="Count", color="Has_Credit_Card", barmode="group",
                     color_discrete_sequence=CAT_COLORS)
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        cross2 = cust_df.groupby(["Mobile_Banking_Status", "Has_Mutual_Fund"], observed=True).size().reset_index(name="Count")
        cross2["Has_Mutual_Fund"] = cross2["Has_Mutual_Fund"].map({1: "Punya RD", 0: "Tidak Punya RD"})
        fig = px.bar(cross2, x="Mobile_Banking_Status", y="Count", color="Has_Mutual_Fund", barmode="group",
                     color_discrete_sequence=CAT_COLORS)
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    active_cc = cust_df.loc[cust_df["Mobile_Banking_Status"] == "Active", "Has_Credit_Card"].mean() * 100 if (cust_df["Mobile_Banking_Status"] == "Active").any() else 0
    nonuser_cc = cust_df.loc[cust_df["Mobile_Banking_Status"] == "Non-User", "Has_Credit_Card"].mean() * 100 if (cust_df["Mobile_Banking_Status"] == "Non-User").any() else 0
    st.markdown(
        f'<div class="insight-box">💡 Nasabah dengan status Mobile Banking <b>Active</b> memiliki penetrasi kartu kredit '
        f'sebesar <b>{active_cc:.1f}%</b>, dibandingkan <b>{nonuser_cc:.1f}%</b> pada nasabah <b>Non-User</b>. '
        f'Hal ini menunjukkan korelasi positif antara keterlibatan digital dan kepemilikan produk finansial lanjutan.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown('<p class="section-title">Adopsi Produk berdasarkan Kelompok Usia</p>', unsafe_allow_html=True)
    age_prod = cust_df.groupby("Age_Group", observed=True)[["Has_Credit_Card", "Has_Mutual_Fund"]].mean().reset_index()
    age_prod["Has_Credit_Card"] *= 100
    age_prod["Has_Mutual_Fund"] *= 100
    age_prod_melt = age_prod.melt(id_vars="Age_Group", value_vars=["Has_Credit_Card", "Has_Mutual_Fund"],
                                   var_name="Produk", value_name="Penetrasi (%)")
    age_prod_melt["Produk"] = age_prod_melt["Produk"].map({"Has_Credit_Card": "Kartu Kredit", "Has_Mutual_Fund": "Reksa Dana"})
    fig = px.line(age_prod_melt, x="Age_Group", y="Penetrasi (%)", color="Produk", markers=True,
                  color_discrete_sequence=CAT_COLORS)
    fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    peak_age_cc = age_prod.loc[age_prod["Has_Credit_Card"].idxmax(), "Age_Group"]
    peak_age_mf = age_prod.loc[age_prod["Has_Mutual_Fund"].idxmax(), "Age_Group"]
    st.markdown(
        f'<div class="insight-box">💡 Penetrasi kartu kredit tertinggi berada pada kelompok usia <b>{peak_age_cc}</b>, '
        f'sementara reksa dana paling banyak diadopsi kelompok usia <b>{peak_age_mf}</b> — informasi berguna '
        f'untuk targeting campaign cross-sell produk investasi maupun kartu kredit.</div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------------------
# TAB 5: ANALISIS GEOGRAFIS
# ------------------------------------------------------------------------------
with tab_geo:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="section-title">Jumlah Transaksi per Lokasi</p>', unsafe_allow_html=True)
        loc_counts = df["Location"].value_counts().reset_index()
        loc_counts.columns = ["Location", "Count"]
        fig = px.bar(loc_counts, x="Location", y="Count", color="Count", color_continuous_scale=SEQ_COLORS, text="Count")
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">Treemap Volume Transaksi per Lokasi</p>', unsafe_allow_html=True)
        loc_vol = df.groupby("Location")["Amount_IDR"].sum().reset_index()
        fig = px.treemap(loc_vol, path=["Location"], values="Amount_IDR", color="Amount_IDR",
                          color_continuous_scale=SEQ_COLORS)
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">Rata-rata Nilai Transaksi & Jenis Transaksi per Lokasi</p>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        loc_avg = df.groupby("Location")["Amount_IDR"].mean().sort_values(ascending=True).reset_index()
        fig = px.bar(loc_avg, x="Amount_IDR", y="Location", orientation="h", color="Amount_IDR",
                     color_continuous_scale=SEQ_COLORS)
        fig.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        loc_type = df.groupby(["Location", "Transaction_Type"]).size().reset_index(name="Count")
        fig = px.bar(loc_type, x="Location", y="Count", color="Transaction_Type", barmode="stack",
                     color_discrete_sequence=CAT_COLORS)
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    top_loc = loc_counts.iloc[0]
    highest_avg_loc = loc_avg.iloc[-1]
    st.markdown(
        f'<div class="insight-box">💡 <b>{top_loc["Location"]}</b> mencatat jumlah transaksi terbanyak '
        f'({top_loc["Count"]:,} transaksi), sementara nasabah di <b>{highest_avg_loc["Location"]}</b> memiliki '
        f'rata-rata nilai transaksi tertinggi (Rp {highest_avg_loc["Amount_IDR"]:,.0f}) — kandidat kuat untuk '
        f'strategi ekspansi cabang premium atau layanan wealth management.</div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------------------
# TAB 6: DEEP DIVE & KORELASI
# ------------------------------------------------------------------------------
with tab_deep:
    st.markdown('<p class="section-title">Boxplot: Nominal Transaksi per Jenis Transaksi</p>', unsafe_allow_html=True)
    fig = px.box(df, x="Transaction_Type", y="Amount_IDR", color="Transaction_Type", color_discrete_sequence=CAT_COLORS,
                 points=False)
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<p class="section-title">Usia vs Nominal Transaksi</p>', unsafe_allow_html=True)
        fig = px.scatter(
            df.sample(min(1500, len(df)), random_state=42), x="Age", y="Amount_IDR", color="Gender",
            opacity=0.6, color_discrete_sequence=CAT_COLORS, trendline="ols"
        )
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-title">Matriks Korelasi (Fitur Numerik & Biner)</p>', unsafe_allow_html=True)
        corr_df = df[["Age", "Amount_IDR", "Has_Credit_Card", "Has_Mutual_Fund"]].copy()
        corr_df["Mobile_Active"] = (df["Mobile_Banking_Status"] == "Active").astype(int)
        corr = corr_df.corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">Perbandingan Nilai Transaksi: Pemilik vs Bukan Pemilik Produk</p>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        tmp = df.copy()
        tmp["Has_Credit_Card"] = tmp["Has_Credit_Card"].map({1: "Punya CC", 0: "Tidak Punya CC"})
        fig = px.violin(tmp, x="Has_Credit_Card", y="Amount_IDR", box=True, color="Has_Credit_Card",
                         color_discrete_sequence=CAT_COLORS)
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        tmp = df.copy()
        tmp["Has_Mutual_Fund"] = tmp["Has_Mutual_Fund"].map({1: "Punya RD", 0: "Tidak Punya RD"})
        fig = px.violin(tmp, x="Has_Mutual_Fund", y="Amount_IDR", box=True, color="Has_Mutual_Fund",
                         color_discrete_sequence=CAT_COLORS)
        fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    corr_amt_age = corr_df["Age"].corr(corr_df["Amount_IDR"])
    st.markdown(
        f'<div class="insight-box">💡 Korelasi antara usia dan nominal transaksi tercatat sebesar '
        f'<b>{corr_amt_age:.2f}</b> — {"cukup lemah, menunjukkan nominal transaksi tidak banyak dipengaruhi usia" if abs(corr_amt_age) < 0.2 else "menunjukkan hubungan yang perlu ditelaah lebih lanjut"}. '
        f'Gunakan matriks korelasi di atas untuk mengidentifikasi fitur mana yang paling berasosiasi dengan kepemilikan produk finansial.</div>',
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------------------------
# TAB 7: DATA EXPLORER
# ------------------------------------------------------------------------------
with tab_data:
    st.markdown('<p class="section-title">Eksplorasi Data Mentah (Sesuai Filter)</p>', unsafe_allow_html=True)
    search_col = st.text_input("🔍 Cari berdasarkan Customer ID atau Transaction ID")
    display_df = df.copy()
    if search_col:
        display_df = display_df[
            display_df["Customer_ID"].str.contains(search_col, case=False, na=False)
            | display_df["Transaction_ID"].str.contains(search_col, case=False, na=False)
        ]
    st.dataframe(display_df, use_container_width=True, height=450)

    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Data (CSV)", data=csv, file_name="filtered_retail_banking_data.csv", mime="text/csv")

    st.markdown("---")
    st.markdown('<p class="section-title">Statistik Deskriptif</p>', unsafe_allow_html=True)
    st.dataframe(display_df.describe(include="all").transpose(), use_container_width=True)

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.caption(
    "📊 Retail Banking Analytics Dashboard — Dibangun dengan Streamlit & Plotly | "
    "Dibuat oleh **Muhammad Zidane Alhalita** | "
    f"Data terakhir diperbarui: {df_raw['Transaction_Date'].max().strftime('%d %B %Y')}"
)
