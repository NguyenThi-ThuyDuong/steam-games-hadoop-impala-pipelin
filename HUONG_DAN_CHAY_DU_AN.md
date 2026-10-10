# HƯỚNG DẪN VẬN HÀNH TOÀN DIỆN DỰ ÁN STEAM BIG DATA & APACHE IMPALA

Tài liệu này hướng dẫn chi tiết từ A-Z cách chạy lại toàn bộ pipeline, xem kết quả trên giao diện web, và cách trình bày đồ án trước hội đồng.

---

## I. TỔNG QUAN CẤU TRÚC PIPELINE ĐÃ CHẠY

Toàn bộ quy trình Big Data của dự án đã được chạy lại thành công qua 4 bước khép kín:

```
[1. Dữ liệu thô CSV] (89,618 games & 40M+ reviews)
       │
       ▼  (Chạy: datamining/scripts/01_data_preprocessing_pipeline.py)
[2. Tiền xử lý & ETL] ──> Tách Star Schema ──> Nén Snappy Parquet (Partition theo release_year)
       │
       ▼  (Chạy: datamining/scripts/02_run_market_analysis.py)
[3. Phân tích OLAP] ──> Thực thi 10 câu truy vấn Impala (Q1 -> Q10) ──> Xuất kết quả CSV
       │
       ▼  (Chạy: benchmark_tech/run_all_benchmarks.py)
[4. Đo đạc Benchmark] ──> Đối sánh 4 công nghệ (Impala vs Pandas vs MySQL vs Hive)
       │
       ▼  (Khởi động: webapp/app.py hoặc webapp/run_webapp.bat)
[5. Trực quan hoá Web Dashboard] (http://127.0.0.1:5000)
```

---

## II. HƯỚNG DẪN 3 BƯỚC CHẠY LẠI DỰ ÁN TRÊN MÁY BẤT KỲ LÚC NÀO

### BƯỚC 1: Chạy lại Pipeline Tiền Xử Lý Dữ Liệu (ETL & Parquet)
Mở PowerShell tại thư mục dự án và gõ:
```powershell
python datamining/scripts/01_data_preprocessing_pipeline.py
```
* **Chức năng:** Làm sạch 89,618 bản ghi, phát hiện outlier giá và review (IQR/Z-Score), chuẩn hóa Star Schema tách 4 bảng chiều (Genres, Tags, Developers, Publishers) và ghi ra các file Parquet phân vùng theo năm `release_year=...`.

---

### BƯỚC 2: Chạy lại 10 Câu Truy Vấn Phân Tích Thị Trường (Q1 - Q10)
```powershell
python datamining/scripts/02_run_market_analysis.py
```
* **Chức năng:** Tự động thực thi 10 câu truy vấn OLAP khai phá thị trường game, tự động ghi đè 10 file CSV kết quả vào thư mục `datamining/results/`.

---

### BƯỚC 3: Khởi Động Giao Diện Web Dashboard
Có 2 cách cực kỳ tiện lợi:

#### Cách 3.1: Nhấp chuột (Nhanh nhất - Không cần gõ lệnh)
* Vào thư mục [`webapp/`](file:///D:/HocTap/HK1_27/BigData/DoAnBigData/webapp).
* Nhấp đúp chuột vào file: **`run_webapp.bat`**.
* Trình duyệt sẽ tự động bật lên tại địa chỉ: **`http://127.0.0.1:5000/`**.

#### Cách 3.2: Gõ lệnh dòng lệnh
```powershell
cd webapp
python app.py
```

---

## III. HƯỚNG DẪN TRÌNH CHIẾU & CÁCH XEM CÁC THÔNG SỐ KHI BÁO CÁO

Khi đứng trước thầy cô, bạn mở trang web lên và lần lượt bấm qua các mục:

### 1. Giới thiệu đề tài (Vào Menu: "Tổng Quan" - `/`)
* **Nói gì:** Đề tài phân tích thị trường trò chơi điện tử toàn cầu từ năm 1997 đến 2025 với hơn **76,119 tựa game** và tập dữ liệu đánh giá khổng lồ **hơn 40 triệu bản ghi (14+ GB)**.
* **Chỉ số cần chỉ:** 4 thẻ Metric lớn ở đầu trang (76,119 Games, 40+ Triệu Reviews, Tăng tốc 16.3x, 28 năm dữ liệu).

---

### 2. Trình bày Minh chứng Công nghệ (Vào Menu: "Thực Nghiệm Hiệu Năng" - `/benchmark`)
*(ĐÂY LÀ PHẦN QUAN TRỌNG NHẤT ĐỂ LẤY ĐIỂM TỐI ĐA VỀ MẶT KỸ THUẬT BIG DATA)*

* **Chỉ vào Biểu đồ 1 (Thời gian truy vấn 40 triệu dòng - Log Scale):**
  - **Python Pandas (185s):** Nạp toàn bộ 14GB dữ liệu cần hơn **18.5 GB RAM**, gây lỗi tràn bộ nhớ (OOM Crash) trên máy tính cá nhân.
  - **MySQL 8.0 (94s):** Quét dữ liệu theo dòng và kiểm tra cây Index B-Tree gây nghẽn đĩa I/O nghiêm trọng.
  - **Hadoop Hive (420s ~ 7 phút):** Động cơ MapReduce cổ điển sinh nhiều tác vụ JVM và liên tục ghi đĩa trung gian đệm xuống HDFS nên độ trễ rất cao.
  - **Apache Impala (1.12s):** Nhanh hơn MySQL **84 lần**, nhanh hơn Hive **375 lần**. Nhờ đọc theo cột Parquet và xử lý MPP trực tiếp trong RAM.
* **Chỉ vào Biểu đồ 2 (Scalability):** Độ dốc thời gian của Impala tăng tuyến tính rất nhẹ ($O(N)$ từ 0.22s lên 1.12s) khi tăng dữ liệu từ 4M lên 40M bản ghi, chứng minh khả năng mở rộng quy mô xuất sắc.
* **Chỉ vào 3 Biểu đồ tối ưu phía dưới:**
  - Parquet Snappy giảm 90% dung lượng I/O $\rightarrow$ tăng tốc **16.3x**.
  - Partition Pruning chỉ quét thư mục năm cần tìm $\rightarrow$ tăng tốc **6.9x**.
  - COMPUTE STATS chuyển sang Broadcast Join $\rightarrow$ tăng tốc **4.7x**.

---

### 3. Trình bày Kết quả Khai phá Thị trường (Vào Menu: "Dashboard Phân Tích" - `/dashboard`)
Nhấp qua 4 Tab tương ứng:
* **Tab Xu hướng (Q1, Q2):** Năm 2024 đạt đỉnh kỷ lục với **18,282 game ra mắt**. Tỷ lệ Free-to-Play tăng từ 4.7% lên **17.26%**. Cột mốc 2014 tăng trưởng đột biến +231.5% nhờ Steam Greenlight.
* **Tab Thể loại (Q3, Q4, Q8):** Kỷ nguyên Hiện đại (2020-2025) chứng kiến **Indie áp đảo hoàn toàn với 42,297 game**. Casual và Indie có tỷ lệ đánh giá tích cực cao nhất (>77%), MMO thấp nhất (64.7%).
* **Tab Giá bán & Outlier (Q5, Q9, Q10):** Phân khúc Budget ($0.01 - $9.99) chiếm thị phần lớn nhất (**43.95%**). Game miễn phí triệu review (CS2 8.6M reviews, Dota 2 2.4M) đối lập với game $999 không có người mua. 76.9% game chỉ hỗ trợ Windows.
* **Tab Creators (Q6, Q7):** Nhà phát hành thu hút lượng review lớn nhất là **Valve với 13.6 triệu reviews**.

---

### 4. Giải thích Kiến trúc Hệ thống (Vào Menu: "Kiến Trúc Hadoop/Impala" - `/architecture`)
* **Chỉ vào sơ đồ Pipeline:** Giải thích rõ tại sao phải cần cả Hadoop HDFS (để lưu trữ phân tán, chịu lỗi các file Parquet) và Apache Impala (để query SQL tốc độ cao).
* **Chỉ vào bảng Star Schema:** Bảng Fact `games_main` phân vùng theo `release_year` và 4 bảng Dimension liên kết qua `appid`.

---

## IV. PHƯƠNG ÁN DỰ PHÒNG KHẨN CẤP (KHI MANG MÁY ĐI BÁO CÁO)

Nếu mang laptop lên trường mà phòng thi không có mạng hoặc máy gặp trục trặc không bật được Python:
👉 **Bạn chỉ cần mở trực tiếp các file HTML trong thư mục:**
[`webapp/dist/`](file:///D:/HocTap/HK1_27/BigData/DoAnBigData/webapp/dist)
- Mở `index.html`, `dashboard.html`, `benchmark.html` bằng trình duyệt Google Chrome hoặc MS Edge.
- Toàn bộ đồ thị tương tác Plotly và giao diện sẽ hiển thị y hệt như đang chạy server mà **không cần cài đặt bất kỳ phần mềm nào**!
