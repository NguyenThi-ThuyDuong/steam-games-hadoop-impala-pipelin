# 🎮 PHÂN TÍCH THỊ TRƯỜNG TRÒ CHƠI ĐIỆN TỬ STEAM VỚI APACHE HADOOP HDFS VÀ APACHE IMPALA

> **Đồ Án Môn Học:** Xử Lý Dữ Liệu Lớn (Big Data)  
> **Nhánh Thực Nghiệm:** `demo_dung`  
> **Giao Diện Điều Khiển:** Streamlit Web Terminal & Multi-Engine Interactive Benchmark Dashboard  

---

## 📌 1. GIỚI THIỆU TỔNG QUAN

Dự án tập trung xây dựng đường ống xử lý dữ liệu lớn (Big Data Pipeline) từ dữ liệu thô của hơn **89,618 trò chơi điện tử trên Steam**, chuyển đổi sang định dạng cột **Apache Parquet v1.0 (nén Snappy)** được **phân vùng theo năm phát hành (27 partitions từ 1997 đến 2025)**, và triển khai trên động cơ truy vấn phân tán **Apache Impala 3.4.0**.

Đồng thời, hệ thống cung cấp giao diện Web tương tác trực quan kết nối trực tiếp **bộ tứ 4 công nghệ lớn** để đo đạc và so sánh hiệu năng thực nghiệm:
1. **⚡ Apache Impala 3.4.0 (Parquet Snappy):** Động cơ chính của đề tài (MPP In-Memory, phân tán thời gian thực).
2. **🐘 Apache Hive (MapReduce):** Đại diện Big Data truyền thống trên nền tảng Hadoop.
3. **🐬 MySQL 8.0 (InnoDB):** Đại diện Cơ sở dữ liệu quan hệ truyền thống (RDBMS hàng ngang).
4. **🐼 Python Pandas 2.2+:** Đại diện Khoa học dữ liệu (Data Science xử lý trên bộ nhớ RAM).

---

## 🚀 2. HƯỚNG DẪN KHỞI CHẠY HỆ THỐNG (CHỈ VỚI 1-CLICK)

Hệ thống đã được thiết kế sẵn kịch bản tự động hóa từ A đến Z, bạn không cần phải gõ các lệnh Docker phức tạp:

### 🍎 Cách 1: Chạy 1-Click trên macOS (Dành cho máy Mac)
1. Bật ứng dụng **Docker Desktop**.
2. Nhấp đúp chuột vào file:
   ```bash
   Run_Demo.command
   ```
   *(Hoặc mở Terminal gõ: `./run_demo.sh`)*
3. **Hệ thống sẽ tự động:**
   * Khởi động container `impala-doan` (chứa Apache Impala & Apache Hive).
   * Khởi động container `mysql-doan` (chứa MySQL 8.0).
   * Tự động mở trình duyệt Web tại địa chỉ: **`http://localhost:8501`**.

---

### 🛑 Cách 2: Tắt hệ thống an toàn (1-Click Clean Stop)
Khi dùng xong hoặc kết thúc buổi báo cáo, để giải phóng RAM và pin cho máy tính:
* Nhấp đúp chuột vào file:
  ```bash
  Stop_Demo.command
  ```
  *(Hoặc mở Terminal gõ: `./stop_demo.sh`)*
* Kịch bản sẽ tắt an toàn toàn bộ container và tiến trình Streamlit, **bảo toàn nguyên vẹn 100% dữ liệu**.

---

### 💻 Cách 3: Chạy thủ công từng bước (Nếu dùng Windows / Linux)

1. **Khởi động các dịch vụ Docker:**
   ```bash
   cd docker && docker compose up -d && cd ..
   docker start mysql-doan 2>/dev/null || true
   ```
2. **Cài đặt môi trường Python:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Trên Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Khởi chạy giao diện Web:**
   ```bash
   streamlit run app.py --server.port 8501
   ```

---

## 🖥️ 3. HƯỚNG DẪN TRÌNH DIỄN CÁC PHÂN HỆ TRÊN WEBSITE DEMO

Khi truy cập vào **`http://localhost:8501`**, giao diện được chia làm 5 phân hệ chuyên nghiệp:

### 💻 Tab 1: Web Terminal & Live SQL (Trình gõ lệnh trực tiếp)
* **Tính năng:** Nhập bất kỳ câu lệnh SQL nào và nhấn nút đỏ **`🚀 Thực thi lệnh`** để gửi trực tiếp tới Impala Coordinator qua cổng `21000`.
* **Thư viện lệnh mẫu bên trái:** Bấm nút lệnh số 1 đến số 9 để tự động điền lệnh SQL mẫu (SHOW TABLES, DESCRIBE, BQ1 đến BQ5).
* **Nút `🔍 EXPLAIN Plan`:** Giải mã cây kế hoạch thực thi phân tán (Query Execution Plan) từ dưới lên trên (`00:SCAN` -> `01:AGGREGATE` -> `03:EXCHANGE` -> `04:AGGREGATE FINALIZE` -> `05:MERGING-EXCHANGE`).

---

### ⚡ Tab 2: Benchmark Đa Công Nghệ (Interactive Multi-Engine Benchmark)
Nơi so sánh hiệu năng thực tế giữa 4 công nghệ trên cùng tập dữ liệu logic:
1. **Mục 1 - Thực nghiệm Benchmark trực tiếp (Live):**
   * Chọn bài toán từ **BQ1 đến BQ6**.
   * Tick chọn các công nghệ tham gia: **Impala**, **Hive**, **MySQL**, **Pandas**.
   * Bấm nút đỏ **`🚀 Bắt Đầu Đo Đạc Thực Nghiệm`**.
   * **Kết quả đối soát:** Bảng *Result Validator* tự động kiểm chứng tính đúng đắn dữ liệu (`🟢 MATCH 100%`), đo chỉ số Median, Mean và tính hệ số tăng tốc **Speedup Ratio** (Impala nhanh gấp 40x - 170x so với Hive).
2. **Mục 2 - Thử nghiệm Partition Pruning (EXPLAIN):**
   * Đặt 2 bảng cạnh nhau: Bảng có phân vùng `games_parquet` (chỉ đọc 1/27 partition, 2.18 MB) vs Bảng không phân vùng `games_parquet_nopart` (phải quét toàn bộ 15.27 MB và 89k dòng).
3. **Mục 3 - Benchmark Tham Chiếu (Overview Reference):**
   * Bảng ma trận thời gian thực thi tổng kết, biểu đồ so sánh mức tiêu thụ Working RAM, dung lượng đọc đĩa (Disk I/O Read) và đường cong mở rộng quy mô (Scalability Curve đến 40 triệu dòng).

---

### 📈 Tab 3: Bảng Điều Khiển Trực Quan (Analytics & Market Trends)
* Đồ thị phân tích phân bố game qua 27 năm, tỷ lệ game miễn phí (Free-to-Play), tương quan giữa giá bán và đánh giá của game thủ, được truy vấn trực tiếp từ bảng `games_parquet`.

---

### 🩺 Tab 4: Kiểm Tra Môi Trường & Dữ Liệu (Health Check)
* Tự động kiểm tra trạng thái sống của các dịch vụ:
  * 🟢 **Apache Impala 3.4.0** (Port 21000/25000)
  * 🟢 **Apache Hive (MapReduce)**
  * 🟢 **MySQL 8.0 (InnoDB)** (Port 3306 - 89,618 games)
  * 🟢 **Python Pandas 2.2+**
* Hiển thị bảng **Dataset Fingerprint** chứng minh tính toàn vẹn và mức độ nén Snappy giảm 96% dung lượng so với CSV thô.

---

### 🏗️ Tab 5: Kiến Trúc Hệ Thống (Data Pipeline)
* Trình bày quy trình chuẩn Big Data qua 5 bước: Thu thập dữ liệu -> Tiền xử lý Python -> Chuẩn hóa Parquet v1.0 nén Snappy -> Triển khai Docker Impala -> Tầng giao diện Web Terminal.

---

## 📁 4. CẤU TRÚC THƯ MỤC DỰ ÁN

```text
├── app.py                      # Ứng dụng Web Dashboard & Terminal đa công nghệ chính
├── run_demo.sh                 # Script Bash tự động khởi động Impala, MySQL và mở Web
├── Run_Demo.command            # File 1-Click trên macOS Finder để khởi động demo
├── stop_demo.sh                # Script Bash tắt an toàn các dịch vụ và giải phóng RAM
├── Stop_Demo.command           # File 1-Click trên macOS Finder để dừng hệ thống
├── docker/
│   ├── docker-compose.yml      # Cấu hình container apache/kudu:impala-latest
│   └── custom-entrypoint.sh    # Script khởi tạo tối ưu RAM và nạp schema CSDL
├── sql/
│   ├── create_tables.sql       # Script khởi tạo bảng trong Hive / Impala
│   └── init_impala_mac.sql     # Script cấu hình khôi phục phân vùng cho Impala
├── scripts/
│   ├── setup_mysql.py          # Script nạp 89,618 games & bảng quan hệ vào MySQL
│   ├── convert_to_parquet_v1.py# Chuyển đổi CSV sang Parquet v1.0 Snappy
│   └── analyze_games.py        # Phân tích dữ liệu bằng Python Pandas
├── data/
│   ├── processed/              # Dữ liệu CSV đã làm sạch (games, genres, publishers, tags)
│   └── parquet_v1/             # Thư mục Parquet phân vùng theo release_year (1997-2025)
└── docs/                       # Tài liệu hướng dẫn chi tiết và kịch bản thuyết trình
```

---

## 🎯 5. THÔNG TIN CÁC CỔNG DỊCH VỤ MẠNG (PORTS)

* **Web Dashboard (Streamlit):** `http://localhost:8501`
* **Impala Coordinator (Beeswax Port):** `localhost:21000`
* **Impala HiveServer2 Endpoint:** `localhost:21050`
* **Impala Web UI Quản trị:** `http://localhost:25000`
* **MySQL 8.0 Server:** `localhost:3306` (User: `root`, Password: `rootpassword`, DB: `steam_analytics`)

---

## 👥 THÀNH VIÊN THỰC HIỆN
* **Đề tài:** Phân tích thị trường trò chơi điện tử Steam sử dụng Apache Hadoop HDFS và Apache Impala
* **Môn học:** Xử Lý Dữ Liệu Lớn (Big Data)
