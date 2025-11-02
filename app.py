import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
from datetime import datetime, timedelta
#konfigurasi halamanb
st.set_page_config(
    page_title="Dashboard Analisis Penjualan",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)
# fungsi Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("data_dummy_retail_store.csv")
#load data penjualan
df_sales = load_data() # memanggil fungsi load_data
df_sales.columns = df_sales.columns.str.lower().str.replace(' ', '_') # ubah jadi lower case
df_sales['tanggal_pesanan'] = pd.to_datetime(df_sales['tanggal_pesanan']) # ubah ke datetime

# judul dashboard
st.title("Dashboard Analisis Penjualan Toko Online")
st.markdown("Dashboard ini menyediakan gambaran umum *sales performance*, **trend**, dan distribusi berdasaran berbagai macam dimensi")

st.sidebar.header("Filter & Navigasi")

pilihan_halaman = st.sidebar.radio(
    "Pilihan Halaman:",
    ("Overview Dashboard", "Prediksi Penjualan")
)

# filter (yang akan muncul hanya di halaman Overview Dashboard)
if pilihan_halaman == "Overview Dashboard":
    st.sidebar.markdown("### Filter Data Dashboard")

    # filter tanggal
    min_date = df_sales['tanggal_pesanan'].min().date()
    max_date = df_sales['tanggal_pesanan'].max().date()

    date_range = st.sidebar.date_input(
        "Pilih Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date_filter = pd.to_datetime(date_range[0])
        end_date_filter = pd.to_datetime(date_range[1])

        filtered_df = df_sales[(df_sales['tanggal_pesanan'] >= start_date_filter) & 
                               (df_sales['tanggal_pesanan'] <= end_date_filter)]
    else:
        filtered_df = df_sales

# filter berdasarkan wilayah
    selected_regions = st.sidebar.multiselect(
        "Pilih Wilayah:",
        options=df_sales['wilayah'].unique().tolist(),
        default=df_sales['wilayah'].unique().tolist()
    )

    filtered_df = filtered_df[filtered_df['wilayah'].isin(selected_regions)]
else:
    filtered_df = df_sales.copy()

# konten halaman utama 
if pilihan_halaman == "Overview Dashboard":
    # metrics utama
    st.subheader("Ringkasan Performance Penjualan")

    col1, col2, col3 = st.columns([3, 3, 3])

    total_sales = filtered_df['total_penjualan'].sum()
    total_orders = filtered_df['orderid'].nunique()
    total_products_sold = filtered_df['jumlah'].sum()

    with col1:
        st.metric(label="Total Penjualan", value=f"Rp {total_sales:,.2f}")
    with col2:
        st.metric(label="Jumlah Pesanan", value=f"{total_orders:,}")
    with col3:
        st.metric(label="Jumlah Produk Terjual", value=f"{total_products_sold:,}")

# line chart trend penjualan
    sales_by_month = filtered_df.groupby('bulan')['total_penjualan'].sum().reset_index()
    # memastikan urutan bulannya benar
    sales_by_month['bulan'] = pd.to_datetime(sales_by_month['bulan']).dt.to_period('M')
    sales_by_month = sales_by_month.sort_values('bulan')
    sales_by_month['bulan'] = sales_by_month['bulan'].astype(str)

    fig_monthly_sales = px.line(
        sales_by_month,
        x='bulan',
        y='total_penjualan',
        title='Total Penjualan per Bulan'
    )
    st.plotly_chart(fig_monthly_sales, use_container_width=True)

# visualisasi dengan tab, lebih detail
    st.subheader("Detailed Sales Performance")

    # membuat tab 1, tab 2
    tab1, tab2 = st.tabs(["Metode Pembayaran", "Wilayah"])

    with tab1:
        st.write("#### Penjualan Berdasarkan Metode Pembayaran")

        sales_by_payment = filtered_df.groupby(
            'metode_pembayaran'
            )['total_penjualan'].sum().reset_index()
        
        fig_payment = px.bar(
            sales_by_payment,
            x='metode_pembayaran',
            y='total_penjualan',
            color='metode_pembayaran'
        )

        # menampilkan bar chart
        st.plotly_chart(fig_payment, use_container_width=True)

    with tab2:
        st.write("#### Penjualan Berdasarkan Wilayah")

        sales_by_region = filtered_df.groupby(
            'wilayah'
        )['total_penjualan'].sum().reset_index()

        fig_region = px.bar(
            sales_by_region,
            x='wilayah',
            y='total_penjualan',
            color='wilayah'
        )
        st.plotly_chart(fig_region, use_container_width=True)
        