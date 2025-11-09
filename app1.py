import streamlit as st 
import pandas as pd 
import numpy as np 
import plotly.express as px  # type: ignore
import plotly.graph_objects as go  # type: ignore
from datetime import datetime, timedelta 

# 1. konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Penjualan Bee Cycle ",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Fungsi untuk Memuat Data (Caching agar cepat)
@st.cache_data
def load_data(file_path):
    # Membaca file CSV
    df = df = pd.read_excel("dataset_bee_cycle.xlsx")
    
    # Konversi kolom tanggal
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Mengisi nilai NaN pada kolom 'color' dan 'size_range' dengan 'NA' (Jika perlu)
    df[['color', 'size_range']] = df[['color', 'size_range']].fillna('NA')
    
    return df

# Memuat data
data_file = "dataset_bee_cycle.xlsx - Sheet1.csv"
try:
    df = load_data(data_file)
except FileNotFoundError:
    st.error(f"File {data_file} tidak ditemukan. Pastikan file berada di direktori yang sama.")
    st.stop()

# --- Judul dan Komponen Dasar ---
st.title("🚴‍♂️ Dashboard Penjualan Bee Cycle")
st.markdown("Visualisasi Interaktif dari Data Penjualan Sepeda dan Aksesori.")

# 3. Komponen Sidebar untuk Interaktivitas (Filter)
st.sidebar.header("Filter Data")

# Filter 1: Dropdown untuk territory_groups
all_groups = ['Semua'] + df['territory_groups'].unique().tolist()
selected_group = st.sidebar.selectbox(
    "Pilih Kelompok Wilayah (Territory Group):",
    all_groups
)

# Filter 2: Slider untuk rentang harga total (totalprice_rupiah)
min_price = int(df['totalprice_rupiah'].min())
max_price = int(df['totalprice_rupiah'].max())
price_range = st.sidebar.slider(
    "Pilih Rentang Harga Total (Rupiah):",
    min_price,
    max_price,
    (min_price, max_price)
)

# 4. Penerapan Filter
df_filtered = df.copy()

# Filter berdasarkan Territory Group
if selected_group != 'Semua':
    df_filtered = df_filtered[df_filtered['territory_groups'] == selected_group]

# Filter berdasarkan Rentang Harga
df_filtered = df_filtered[
    (df_filtered['totalprice_rupiah'] >= price_range[0]) & 
    (df_filtered['totalprice_rupiah'] <= price_range[1])
]

# --- Metrik Utama (Streamlit Metrics) ---
st.header("Ringkasan Utama 📈")

col1, col2, col3 = st.columns(3)

with col1:
    total_sales = df_filtered['totalprice_rupiah'].sum()
    col1.metric("💰 Total Penjualan", f"Rp {total_sales:,.0f}")

with col2:
    total_quantity = df_filtered['quantity'].sum()
    col2.metric("📦 Total Kuantitas", f"{total_quantity:,.0f}")

with col3:
    unique_customers = df_filtered['customer_id'].nunique()
    col3.metric("👨‍👩‍👧‍👦 Pelanggan Unik", f"{unique_customers:,.0f}")

st.markdown("---")

# 5. Visualisasi Interaktif (Plotly)
st.header("Visualisasi Penjualan per Kategori")

# Agregasi data untuk visualisasi
sales_by_category = df_filtered.groupby('category')['totalprice_rupiah'].sum().reset_index()
sales_by_category = sales_by_category.sort_values(by='totalprice_rupiah', ascending=False)

# Membuat Bar Chart menggunakan Plotly Express
fig = px.bar(
    sales_by_category, 
    x='category', 
    y='totalprice_rupiah',
    title='Total Penjualan Berdasarkan Kategori Produk',
    labels={'category': 'Kategori Produk', 'totalprice_rupiah': 'Total Penjualan (Rp)'},
    color='category' # Memberi warna berbeda per kategori
)

# Menyesuaikan layout (Opsional)
fig.update_layout(
    xaxis_title=None,
    yaxis_tickprefix='Rp ',
    uniformtext_minsize=8, 
    uniformtext_mode='hide'
)

# Menampilkan chart di Streamlit
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")


# 7. Visualisasi Interaktif 2: Tren Penjualan Bulanan
st.header("Tren Penjualan Bulanan 📅")

# Ekstraksi Tahun dan Bulan
df_filtered['year_month'] = df_filtered['order_date'].dt.to_period('M').astype(str)

# Agregasi data untuk tren bulanan
sales_trend = df_filtered.groupby('year_month')['totalprice_rupiah'].sum().reset_index()

# Membuat Line Chart menggunakan Plotly Express
fig_trend = px.line(
    sales_trend, 
    x='year_month', 
    y='totalprice_rupiah',
    title='Total Penjualan dari Waktu ke Waktu (Bulanan)',
    labels={'year_month': 'Bulan dan Tahun', 'totalprice_rupiah': 'Total Penjualan (Rp)'}
)

# Menambahkan titik (markers) pada garis
fig_trend.update_traces(mode='lines+markers', line=dict(color='#0083B8'))

# Menyesuaikan layout untuk time series
fig_trend.update_layout(
    xaxis_title=None,
    yaxis_tickprefix='Rp ',
    hovermode='x unified' # Interaktivitas hover yang lebih baik
)

# Menampilkan chart di Streamlit
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# 8. Komponen Teks/Data Tambahan (Lanjutkan dari sini)
st.header("Data Filtered (Tabel)")

# 9. Visualisasi Interaktif 3: Penjualan per Wilayah
st.header("Distribusi Penjualan per Kelompok Wilayah 🌎")

# Agregasi data berdasarkan territory_groups
sales_by_territory = df_filtered.groupby('territory_groups')['totalprice_rupiah'].sum().reset_index()
sales_by_territory = sales_by_territory.sort_values(by='totalprice_rupiah', ascending=False)

# Membuat Bar Chart menggunakan Plotly Express
fig_territory = px.bar(
    sales_by_territory, 
    x='territory_groups', 
    y='totalprice_rupiah',
    title='Total Penjualan Berdasarkan Territory Groups',
    labels={'territory_groups': 'Kelompok Wilayah', 'totalprice_rupiah': 'Total Penjualan (Rp)'},
    color='territory_groups' # Memberi warna berbeda per wilayah
)

# Menyesuaikan layout (Opsional)
fig_territory.update_layout(
    xaxis_title=None,
    yaxis_tickprefix='Rp ',
    uniformtext_minsize=8, 
    uniformtext_mode='hide'
)

# Menampilkan chart di Streamlit
st.plotly_chart(fig_territory, use_container_width=True)

st.markdown("---")


## 10. Visualisasi Top 10 Produk Terlaris (Berdasarkan Kuantitas) 📦

st.header("Top 10 Produk Terlaris (Kuantitas Terjual)")

# Agregasi data berdasarkan product_name dan jumlahkan quantity
top_products_qty = df_filtered.groupby('product_name')['quantity'].sum().reset_index()

# Ambil 10 produk teratas (Top 10)
top_10_products = top_products_qty.sort_values(by='quantity', ascending=False).head(10)

# Membuat Bar Chart menggunakan Plotly Express
fig_top_products = px.bar(
    top_10_products, 
    x='quantity', 
    y='product_name',
    orientation='h', # Membuat bar horizontal (lebih mudah dibaca)
    title='10 Produk dengan Kuantitas Penjualan Tertinggi',
    labels={'quantity': 'Total Kuantitas Terjual', 'product_name': 'Nama Produk'},
    color='quantity', # Memberi gradasi warna berdasarkan kuantitas
    color_continuous_scale=px.colors.sequential.Sunset # Skema warna opsional
)

# Membalik urutan Y-axis agar produk terlaris ada di paling atas
fig_top_products.update_layout(
    yaxis={'categoryorder':'total ascending'},
    xaxis_title='Total Kuantitas Terjual'
)

# Menampilkan chart di Streamlit
st.plotly_chart(fig_top_products, use_container_width=True)

# ... (Setelah Metrik Utama, sekitar baris 80)
# st.markdown("---")

## 4. Visualisasi Total Penjualan Berdasarkan Jenis Kelamin 🚻
st.header("Total Penjualan Berdasarkan Jenis Kelamin")

# Agregasi data HANYA berdasarkan jenis kelamin
sales_by_gender = df_filtered.groupby('gender')['totalprice_rupiah'].sum().reset_index()

# Membuat Bar Chart khusus Gender menggunakan Plotly Express
fig_gender = px.bar(
    sales_by_gender, 
    x='gender', 
    y='totalprice_rupiah',
    title='Perbandingan Total Penjualan (Laki-laki vs. Perempuan)',
    labels={'gender': 'Jenis Kelamin', 'totalprice_rupiah': 'Total Penjualan (Rp)'},
    color='gender', # Memberi warna berbeda untuk setiap gender
    color_discrete_map={'F': 'pink', 'M': 'blue'} # Opsional: Menetapkan warna spesifik
)

# Menyesuaikan layout
fig_gender.update_layout(
    xaxis_title=None,
    yaxis_tickprefix='Rp ',
    uniformtext_minsize=8, 
    uniformtext_mode='hide'
)

# Menampilkan chart di Streamlit
st.plotly_chart(fig_gender, use_container_width=True)

st.markdown("---")

