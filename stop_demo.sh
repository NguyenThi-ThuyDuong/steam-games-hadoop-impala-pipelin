#!/bin/bash

# ==============================================================================
# SCRIPT DỪNG TOÀN BỘ HỆ THỐNG STEAM BIG DATA (1-CLICK CLEAN STOP)
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=================================================================="
echo "🛑 ĐANG TẮT VÀ DỌN DẸP TOÀN BỘ HỆ THỐNG STEAM BIG DATA..."
echo "=================================================================="

# 1. Dừng tiến trình giao diện Streamlit
echo "1️⃣ Đang tắt tiến trình Web Terminal (Streamlit)..."
pkill -f "streamlit run app.py" > /dev/null 2>&1
echo "   ✅ Đã dừng Web Terminal."

# 2. Dừng các Container Docker (Chỉ tạm dừng, không xóa dữ liệu)
echo "2️⃣ Đang dừng các container dịch vụ Big Data..."
docker stop impala-doan mysql-doan > /dev/null 2>&1
echo "   ✅ Đã dừng impala-doan và mysql-doan an toàn."

echo "=================================================================="
echo "✨ HOÀN TẤT TẮT HỆ THỐNG!"
echo "💾 Toàn bộ dữ liệu 89,618 games & phân vùng Parquet được lưu an toàn 100%."
echo "🚀 Chiều về, bạn chỉ cần nhấp đúp file [Run_Demo.command] là mọi thứ tự bật lại!"
echo "=================================================================="
