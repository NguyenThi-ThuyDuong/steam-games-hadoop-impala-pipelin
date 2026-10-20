# CHƯƠNG 6: THỰC NGHIỆM HIỆU NĂNG APACHE IMPALA

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

**Nhận xét:** Kỹ thuật Partitioning kích hoạt tính năng **Partition Pruning**, giúp Impala nhảy trực tiếp tới thư mục năm tương ứng mà không phải duyệt qua dữ liệu các năm khác, giúp truy vấn hoàn thành tức thì.

---

## 6.3 Thí Nghiệm 3: Ảnh Hưởng Của COMPUTE STATS Đến Truy VẤn JOIN (RQ6)

| Trạng thái Statistics | Chiến lược JOIN được chọn | Thời gian thực thi | Tài nguyên RAM tiêu thụ |
|-----------------------|---------------------------|--------------------|-------------------------|
| **Chưa COMPUTE STATS** | Partitioned / Hash Join | 24.50 giây | Cao (Memory Spill đĩa) |
| **Sau COMPUTE STATS** | **Broadcast Join** | **5.20 giây** | Thấp & Tối ưu |

**Nhận xét:** Thông tin thống kê giúp Impala Query Planner nhận biết bảng `games_parquet` (90K dòng) nhỏ hơn nhiều so với bảng `reviews_parquet` (40M dòng), từ đó tự động chọn kịch bản **Broadcast Join** (phát bảng nhỏ tới tất cả node executor) thay vì Shuffle/Hash Join toàn bộ 40M dòng qua mạng.

---

## 6.4 Thí Nghiệm 4 & 5: Khả Năng Mở Rộng (Scalability) (RQ7)

Khi tăng quy mô dữ liệu review từ 10% (4 triệu dòng), 25%, 50%, 75% đến 100% (40.25 triệu dòng), thời gian thực thi câu lệnh Aggregation trên Impala tăng theo đường tuyến tính mượt mà ($O(N)$), thể hiện khả năng mở rộng (Scale-out) xuất sắc trên cụm HDFS phân tán.
