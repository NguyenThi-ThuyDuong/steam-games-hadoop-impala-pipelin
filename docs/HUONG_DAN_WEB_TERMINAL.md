# Hướng Dẫn Sử Dụng Giao Diện Web Tương Tác Truy Vấn (Interactive Web SQL Console)
**Đề tài**: Phân tích dữ liệu trò chơi điện tử và khám phá xu hướng thị trường sử dụng Apache Impala  
**Nền tảng**: macOS (Apple Silicon M1 Max) • Docker Container `impala-doan` (Port 21000, 21050, 25000) • Streamlit Interactive Terminal (Port 8501)

---

## 1. Địa Chỉ Truy Cập Trực Tiếp Trên Trình Duyệt

* **Giao diện Web Terminal Tương Tác**: [http://localhost:8501](http://localhost:8501)
* **Giao diện Giám sát Truy vấn Impala Web UI**: [http://localhost:25000/queries](http://localhost:25000/queries)

---

## 2. Điểm Khác Biệt: Hoàn Toàn Không Phải Web Tĩnh!

Hệ thống web này được thiết kế theo mô hình **Interactive SQL Workbench** (tương tự Cloudera Hue, Apache Zeppelin, Databricks Workspace):

1. **Gửi lệnh SQL thật vào Daemon phân tán**:
   - Khi bạn nhập bất kỳ câu lệnh SQL nào vào ô nhập lệnh trên Web và bấm **"🚀 Thực thi lệnh"**, Web sẽ gửi trực tiếp câu lệnh đó vào tiến trình `impalad` bên trong container Docker `impala-doan`.
   - Impala phân tích cú pháp, lập kế hoạch thực thi phân tán, đọc dữ liệu từ các thư mục phân vùng Parquet và trả về kết quả thời gian thực.
2. **Đo lường thời gian thực thi thực tế**:
   - Hiển thị chính xác thời gian mà Impala Coordinator tiêu tốn (ví dụ: `0.14s`, `0.24s`).
3. **Phân tích kế hoạch `EXPLAIN Plan` tại chỗ**:
   - Bấm nút **"🔍 EXPLAIN Plan"** để xem kế hoạch thực thi phân tán: kiểm tra **Partition Pruning (`partitions=1/27`)**, số luồng, bộ nhớ ước tính.
4. **Vẽ biểu đồ động tức thì**:
   - Từ bất kỳ kết quả truy vấn SQL nào vừa chạy xong, bạn có thể chọn cột X, cột Y để hệ thống tự động sinh biểu đồ Cột (Bar), Đường (Line), hoặc Vùng (Area).
5. **Lịch sử truy vấn (Query History)**:
   - Ghi lại các câu lệnh vừa chạy trong phiên cùng trạng thái và độ trễ.

---

## 3. Cấu Trúc Các Tab Trên Giao Diện

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🎮 STEAM BIG DATA INTERACTIVE WEB TERMINAL (APACHE IMPALA)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ [💻 Web Terminal & Live SQL]  [⚡ Benchmark]  [📈 Analytics]  [🏗️ CSDL]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Tab 1: 💻 Web Terminal & Live SQL (Trọng tâm tương tác)
- **Ô nhập lệnh SQL**: Tự do gõ mọi câu lệnh Impala (`SELECT`, `SHOW TABLES`, `DESCRIBE`, `SHOW PARTITIONS`, `EXPLAIN`, `COMPUTE STATS`).
- **Sidebar Cheat-Sheet (8 câu lệnh mẫu cài sẵn)**:
  - `SHOW TABLES;`
  - `DESCRIBE games_parquet;`
  - `SHOW PARTITIONS games_parquet;`
  - [RQ1] Tăng trưởng số lượng game theo năm
  - [RQ2] Top 10 Thể loại game phổ biến
  - [RQ3] Tương quan Mức giá vs Rating
  - [RQ4] Top game Outlier nhiều đánh giá nhất (CS2, PUBG, Dota 2)
  - [RQ6] Kế hoạch phân tán Partition Pruning
- **Nút xuất dữ liệu**: Bấm **"📥 Tải kết quả CSV"** để xuất file ra máy.

### Tab 2: ⚡ Benchmark Hiệu Năng (CSV vs Parquet & Partition Pruning)
- **Thử nghiệm 1 (CSV vs Parquet)**: Bấm nút để hệ thống chạy song song 2 câu lệnh trên bảng `games_csv` và `games_parquet`. Trả về đồ thị so sánh thời gian thực thi (Parquet nhanh hơn ~6.5 lần).
- **Thử nghiệm 2 (Partition Pruning)**: Chọn 1 năm bất kỳ (ví dụ: 2024), hệ thống trích xuất kế hoạch `EXPLAIN`:
  - `games_parquet`: Chỉ đọc `partitions=1/27` (bỏ qua 26 thư mục phân vùng khác).
  - `games_parquet_nopart`: Bắt buộc quét toàn bộ file 15.27 MB và 89k dòng.

### Tab 3: 📈 Bảng Điều Khiển Trực Quan (Analytics)
- Đồ thị bùng nổ số lượng game qua từng thời kỳ (Steam Greenlight, Steam Direct).
- Đồ thị cơ cấu thể loại (Indie, Action, Adventure, v.v.).
- Bảng vinh danh Top Games huyền thoại có hàng triệu lượt đánh giá.

### Tab 4: 🏗️ Kiến Trúc Hệ Thống & CSDL
- Sơ đồ Data Pipeline: Raw CSV -> Python Data Cleaning -> PyArrow Parquet Snappy -> Apache Impala Distributed Engine -> Streamlit Interactive UI.
- Chi tiết 7 bảng trong CSDL `steam_analytics`.
