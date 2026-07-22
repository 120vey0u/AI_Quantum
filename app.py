import os
import pandas as pd
import streamlit as st

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
            df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            st.success("✅ Tải file upload thành công!")
        except Exception as e:
            st.error(f"❌ File hỏng hoặc lỗi định dạng: {e}")
    elif os.path.exists("data_input.csv"):
        df = pd.read_csv("data_input.csv", encoding="utf-8-sig")
        st.info("ℹ️ Đang dùng file data_input.csv mặc định.")
    else:
        st.warning("⚠️ Chưa có dữ liệu! Vui lòng upload file CSV.")
        
### Hiển thị kết quả map và xem trước dữ liệu
with col_map:
    st.subheader("📍 Dữ Liệu & Lộ Trình")
    
    if df is not None:
        # Báo chỉ số nhanh
        st.metric(label="📊 Tổng số đơn hàng tiếp nhận", value=len(df))
        
        # Xem bảng dữ liệu
        st.markdown("#### Bảng dữ liệu đơn hàng (Preview)")

        # Chuyển đổi tên cột thành chuỗi sạch
        df.columns = [str(col).strip() for col in df.columns]

        # Hiển thị 10 dòng đầu tiên bằng HTML table chuẩn
        st.table(df.head(10))
        
    else:
        st.info("Khu vực này sẽ hiển thị bảng dữ liệu và bản đồ sau khi nhận file.")




