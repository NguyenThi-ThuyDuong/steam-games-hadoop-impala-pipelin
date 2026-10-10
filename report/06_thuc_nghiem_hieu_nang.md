# CHƯƠNG 6: THỰC NGHIỆM HIỆU NĂNG & MINH CHỨNG SO SÁNH CÔNG NGHỆ

## 6.0 Minh Chứng Tầm Vóc Bài Toán Big Data: So Sánh Trực Tiếp Các Công Nghệ

Để chứng minh tính tất yếu của việc sử dụng hệ sinh thái **Apache Impala + Hadoop HDFS**, đồ án thực hiện đo đạc thực nghiệm đối sánh cùng một câu truy vấn tổng hợp phức tạp (Aggregation & Filter) trên tập dữ liệu đánh giá quy mô lớn (**40.25 triệu bản ghi - 14.2 GB**) giữa 4 công nghệ đại diện:

### Bảng kết quả đối sánh toàn diện:

| Công nghệ thực nghiệm | Kiến trúc xử lý | Thời gian thực thi (Giây) | RAM tiêu thụ | Trạng thái thực thi / Giới hạn hệ thống |
| :--- | :--- | :--- | :--- | :--- |
| **Python Pandas** | In-Memory (Đơn máy) | **185.0 s** | ~18.5 GB | **Nguy cơ OOM Crash** (Tràn bộ nhớ RAM trên máy cá nhân). |
| **MySQL 8.0 (Indexed)** | RDBMS Row-based | **94.0 s** | ~6.2 GB | **Nghẽn I/O Ổ đĩa** (Chi phí quét index B-Tree và khóa bảng quá lớn). |
| **Hadoop Hive (MR)** | MapReduce trên HDFS | **420.0 s (7 phút)** | ~4.0 GB | **Độ trễ cao** (Ghi dữ liệu trung gian đệm xuống đĩa HDFS liên tục). |
| **Apache Impala + HDFS** | **MPP In-Memory + Parquet**| **1.12 s** | **~1.8 GB** | **Realtime - Phản hồi tức thì** (Nhanh hơn 84x so với MySQL, 375x so với Hive). |

> **Kết luận học thuật:** Tập dữ liệu 40 triệu bản ghi đã chạm đến ranh giới "Bức tường bộ nhớ" (Memory Wall) của các công cụ đơn máy (Pandas/MySQL). Apache Impala kết hợp HDFS là giải pháp duy nhất vừa đảm bảo lưu trữ an toàn vừa mang lại tốc độ truy vấn phục vụ người dùng cuối ở thời gian thực.

---

## 6.1 Thí Nghiệm 1: Định Dạng Lưu Trữ CSV vs Apache Parquet (RQ6)

### Kết quả đo lường thời gian thực thi (Query Execution Time)

| Truy vấn thực nghiệm | CSV Format | Parquet Format | Mức tăng tốc (Speedup) | Dung lượng quét (Bytes Scanned) |
|----------------------|------------|----------------|------------------------|---------------------------------|
| **Q1.1 - Aggregation Games** | 4.82 giây | **0.45 giây** | **10.7x** | 447 MB vs 32.5 MB |
| **Q1.2 - Filter & Agg Reviews** | 18.35 giây | **1.12 giây** | **16.3x** | 5.0 GB vs 240 MB |

**Nhận xét:** Định dạng cột Parquet kết hợp nén Snappy giúp Impala loại bỏ hoàn toàn việc đọc các cột không dùng trong câu lệnh `SELECT` (Column Pruning), giảm hơn **90% dung lượng I/O** trên đĩa HDFS.

---

## 6.2 Thí Nghiệm 2: Đánh Giá Kỹ Thuật Phân Vùng Partitioning (RQ6)

### Kết quả Partition Pruning trên bảng `reviews_parquet` (40M+ dòng)

| Cấu hình bảng | Điều kiện lọc (`WHERE`) | Thời gian thực thi | Thư mục vật lý được quét |
|---------------|-------------------------|--------------------|--------------------------|
| **Không phân vùng (`nopart`)** | `review_year = 2023` | 1.25 giây | Scanned 100% data files |
| **Có phân vùng (`reviews_parquet`)** | `review_year = 2023` | **0.18 giây** | **Chỉ quét thư mục `review_year=2023/`** |

**Nhận xét:** Kỹ thuật Partitioning kích hoạt tính năng **Partition Pruning**, giúp Impala nhảy trực tiếp tới thư mục năm tương ứng mà không phải duyệt qua dữ liệu các năm khác, giúp truy vấn hoàn thành tức thì (tăng tốc 6.9x).

---

## 6.3 Thí Nghiệm 3: Ảnh Hưởng Của COMPUTE STATS Đến Truy Vấn JOIN (RQ6)

| Trạng thái Statistics | Chiến lược JOIN được chọn | Thời gian thực thi | Tài nguyên RAM tiêu thụ |
|-----------------------|---------------------------|--------------------|-------------------------|
| **Chưa COMPUTE STATS** | Partitioned / Hash Join | 24.50 giây | Cao (Memory Spill đĩa) |
| **Sau COMPUTE STATS** | **Broadcast Join** | **5.20 giây** | Thấp & Tối ưu |

**Nhận xét:** Thông tin thống kê giúp Impala Query Planner nhận biết bảng `games_parquet` (90K dòng) nhỏ hơn nhiều so với bảng `reviews_parquet` (40M dòng), từ đó tự động chọn kịch bản **Broadcast Join** (phát bảng nhỏ tới tất cả node executor) thay vì Shuffle/Hash Join toàn bộ 40M dòng qua mạng (tăng tốc 4.7x).

---

## 6.4 Thí Nghiệm 4: Khả Năng Mở Rộng Tuyến Tính (Scalability Test) (RQ7)

Khi tăng quy mô dữ liệu review từ 10% (4 triệu dòng), 25% (10 triệu dòng), 50% (20 triệu dòng) đến 100% (40.25 triệu dòng), đồ thị thời gian thực thi của Impala duy trì độ dốc tuyến tính nhẹ ($O(N)$ từ 0.22s đến 1.12s), chứng minh khả năng mở rộng (Scale-out) vượt trội trên cụm HDFS so với sự bùng nổ theo hàm mũ của RDBMS truyền thống.
