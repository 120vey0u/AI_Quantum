import io
import os
import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 1. Mở rộng giao diện ra toàn màn hình
st.set_page_config(page_title="AIzen - Quantum Logistics", page_icon="🚀", layout="wide")

# 2. Tiêu đề chính
st.title("🚀 AIzen Team - AI Quantum Challenge 2026")
st.caption("Dự án Tối ưu hóa Logistics Thương mại Điện tử")
st.divider()

# 3. Chia bố cục trang
## Cột bên trái dành cho Bản đồ (Day 5 sẽ phát triển mạnh)
## Cột bên phải dành cho Form Upload và Điều khiển
col_map, col_control = st.columns([3, 1])

### Bảng điều khiển và Form Upload
with col_control:
    st.subheader("⚙️ Bảng Điều Khiển")
    
    # Tạo ô upload file
    uploaded_file = st.file_uploader("Upload file data_input.csv", type=["csv"], help="Cần có 4 cột: Order_ID, Latitude, Longtitude, Weight_kg")
    
    # Khởi tạo DataFrame
    df = None
    
    # Logic xử lý ưu tiên: File upload > File mặc định local > Báo trống
    if uploaded_file is not None:
        try:
            # FIX BUG 139: Đọc dữ liệu qua BytesIO để cô lập bộ nhớ RAM
            file_bytes = io.BytesIO(uploaded_file.getvalue())
            df = pd.read_csv(file_bytes, encoding="utf-8-sig", dtype=str)
            st.success("✅ Tải file upload thành công!")
        except Exception as e:
            st.error(f"❌ File hỏng hoặc lỗi định dạng: {e}")
    elif os.path.exists("data_input.csv"):
        df = pd.read_csv("data_input.csv", encoding="utf-8-sig")
        st.info("ℹ️ Đang dùng file data_input.csv mặc định.")
    else:
        st.warning("⚠️ Chưa có dữ liệu! Vui lòng upload file CSV.")
        
### Bản đồ & Preview Dữ liệu (Cột trái)
with col_map:
    st.subheader("📍 Dữ Liệu & Bản Đồ Lộ Trình")
    
    # Khởi tạo bản đồ mặc định (Khu vực Hà Nội)
    map_center = [21.0285, 105.8048]
    m = folium.Map(location=map_center, zoom_start=11)
    
    if df is not None:
        # Làm sạch tên cột
        df.columns = [str(col).strip() for col in df.columns]
       
        # Kiểm tra xem file có tọa độ Latitude/Longitude không
        if "Latitude" in df.columns and "Longitude" in df.columns:
            # Ép kiểu dữ liệu tọa độ
            df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
            df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
            valid_coords = df.dropna(subset=["Latitude", "Longitude"])
            
            if not valid_coords.empty:
                # Căn trung tâm bản đồ theo trung bình tọa độ dữ liệu
                map_center = [
                    valid_coords["Latitude"].mean(),
                    valid_coords["Longitude"].mean(),            
                ]
                m = folium.Map(location=map_center, zoom_start=11)
                
                # Vẽ tối đa 200 Marker lên bản đồ để đảm bảo hiệu năng
                for _, row in valid_coords.head(200).iterrows():
                    order_id = row.get("Order_ID", "N/A")
                    folium.Marker(
                        location=[row["Latitude"], row["Longitude"]],
                        tooltip=f"📦 Đơn hàng #{order_id}",
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(m)
                    
        st.metric(label="📊 Tổng số đơn hàng tiếp nhận", value=f"{len(df):,} đơn")
        
        # 1. Render Bảng đồ tương tác
        components.html(m._repr_html_(), height=500)
        
        # 2. Preview Bảng dữ liệu HTML
        st.markdown("#### Bảng dữ liệu đơn hàng (Preview)")
        st.write(
            df.head(10).to_html(classes="table table-striped", index=False),
            unsafe_allow_html=True,
        )
    else:
        # Hiển thị bản đồ trống khi chưa có dữ liệu
        components.html(m._repr_html_(), height=500)
        st.info(
            "Khu vực này sẽ hiển thị các điểm tọa độ sau khi nhận file có cột Latitude và Longitude."
        )



