#!/bin/bash

# ==============================================================================
# SCRIPT KHỞI CHẠY DEMO HỆ THỐNG STEAM BIG DATA VỚI APACHE IMPALA
# ==============================================================================

# Chuyển về đúng thư mục chứa dự án
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=================================================================="
echo "🎮 KHỞI CHẠY HỆ THỐNG DEMO STEAM BIG DATA & APACHE IMPALA"
echo "=================================================================="

# 1. Kiểm tra xem Docker Desktop đã bật hay chưa
if ! docker info > /dev/null 2>&1; then
    echo "⚠️  Docker Desktop chưa bật! Đang mở ứng dụng Docker..."
    open -a Docker
    echo "⏳ Đang chờ Docker khởi động hoàn tất..."
    while ! docker info > /dev/null 2>&1; do
        sleep 2
    done
    echo "✅ Docker Desktop đã sẵn sàng!"
fi

# 2. Kiểm tra và khởi động container Apache Impala
if [ "$(docker ps -q -f name=impala-doan)" ]; then
    echo "🟢 Cụm Apache Impala (container: impala-doan) đang chạy sẵn."
elif [ "$(docker ps -aq -f name=impala-doan)" ]; then
    echo "🚀 Đang khởi động lại container impala-doan..."
    docker start impala-doan
    echo "⏳ Chờ Impala Daemon ổn định trong 6 giây..."
    sleep 6
    echo "✅ Apache Impala đã sẵn sàng!"
else
    echo "🚀 Đang triển khai container Impala bằng Docker Compose..."
    cd "$PROJECT_DIR/docker" && docker compose up -d && cd "$PROJECT_DIR"
    echo "⏳ Chờ cụm Impala khởi tạo trong 10 giây..."
    sleep 10
    echo "✅ Apache Impala đã khởi tạo thành công!"
fi

# 2.1 Kiểm tra và khởi động container MySQL
if [ "$(docker ps -q -f name=mysql-doan)" ]; then
    echo "🟢 MySQL 8.0 (container: mysql-doan) đang chạy sẵn."
elif [ "$(docker ps -aq -f name=mysql-doan)" ]; then
    echo "🚀 Đang khởi động lại container mysql-doan..."
    docker start mysql-doan
    echo "✅ MySQL 8.0 đã sẵn sàng!"
fi

# 3. Mở trình duyệt Web Terminal (Streamlit)
echo "------------------------------------------------------------------"
echo "🌐 Đang mở Giao diện Web Terminal tương tác tại: http://localhost:8501"
echo "💡 Trình duyệt sẽ tự động mở lên trong vài giây..."
echo "📌 Để dừng hệ thống khi demo xong: Nhấn tổ hợp phím [Ctrl + C]"
echo "=================================================================="

# Chạy Streamlit (mặc định sẽ tự kích hoạt trình duyệt Safari/Chrome)
"$PROJECT_DIR/.venv/bin/streamlit" run app.py --server.port 8501
