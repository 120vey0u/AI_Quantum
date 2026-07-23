# 1. Dùng hệ điều hành Python 3.10 bản nhẹ (slim)
FROM python:3.10-slim

# 2. Tạo một thư mục tên là /app bên trong Docker để chứa code
WORKDIR /app

# 3. Cài đặt các công cụ biên dịch cơ bản của Linux
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy file requirements vào và cài đặt các thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Mở cổng 8501 (cổng mặc định của Streamlit)
EXPOSE 8501

# 6. Lệnh chạy web Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
