# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

## 2.1 Tổng Quan Về Dữ Liệu Lớn (Big Data)

Dữ liệu lớn (Big Data) được định nghĩa bởi đặc trưng 5V tiêu chuẩn:
1. **Volume (Dung lượng):** Khối lượng dữ liệu khổng lồ đạt ngưỡng Terabytes đến Petabytes.
2. **Velocity (Tốc độ):** Tốc độ sinh ra và xử lý dữ liệu theo thời gian thực hoặc gần thời gian thực.
3. **Variety (Đa dạng):** Sự kết hợp giữa dữ liệu có cấu trúc, bán cấu trúc và phi cấu trúc.
4. **Veracity (Độ tin cậy):** Tính chính xác, sạch sẽ và chất lượng của dữ liệu.
5. **Value (Giá trị):** Giá trị tri thức trích xuất được từ quá trình phân tích.

---

## 2.2 Kiến Trúc Apache Hadoop & HDFS

Hệ sinh thái Apache Hadoop là nền tảng điện toán phân tán cốt lõi:
- **Hadoop Distributed File System (HDFS):** Hệ thống tập tin phân tán cho phép lưu trữ tập tin dung lượng lớn trên cụm máy chủ (Cluster) theo cơ chế chia khối (Block Size, mặc định 128MB) và nhân bản (Replication Factor, mặc định 3).
- **YARN (Yet Another Resource Negotiator):** Hệ thống quản lý tài nguyên và điều phối công việc trên toàn cụm.

---

## 2.3 Apache Impala & Kiến Trúc Truy VẤn MPP

**Apache Impala** là một engine truy vấn SQL nguồn mở hiệu năng cao dành cho dữ liệu lưu trữ trên HDFS và Apache HBase.

```
                  ┌────────────────────────┐
                  │      Impala Client     │
                  └───────────┬────────────┘
                              │ SQL Query
                              ▼
                  ┌────────────────────────┐
                  │    Impala Daemon       │
                  │   (Coordinator Node)   │
                  └─────┬────────────┬─────┘
                        │            │
             Query Plan │            │ Query Plan
                        ▼            ▼
         ┌──────────────────┐    ┌──────────────────┐
         │  Impala Daemon   │    │  Impala Daemon   │
         │  (Executor Node) │    │  (Executor Node) │
         └────────┬─────────┘    └────────┬─────────┘
                  │                       │
                  ▼                       ▼
            ┌───────────┐           ┌───────────┐
            │ Data Block│           │ Data Block│
            │   (HDFS)  │           │   (HDFS)  │
            └───────────┘           └───────────┘
```

### Ưu thế vượt trội của Impala:
1. **Kiến trúc Massively Parallel Processing (MPP):** Đọc và xử lý dữ liệu trực tiếp từ HDFS bằng C++ native code mà không cần thông qua các bước trung gian MapReduce hay Tez.
2. **In-Memory Computing:** Thực hiện tính toán Join, Aggregation trực tiếp trên RAM của các node executor.
3. **Tích hợp Hive Metastore:** Sử dụng chung Metadata DDL với Apache Hive.

---

## 2.4 Định Dạng Lưu Trữ Apache Parquet & Nén Snappy

Apache Parquet là định dạng lưu trữ dạng cột (Columnar Storage Format) tối ưu hóa cho truy vấn OLAP:
- **Column Pruning:** Chỉ đọc đúng các cột được yêu cầu trong câu lệnh `SELECT`, bỏ qua các cột không liên quan.
- **Data Compression:** Tốc độ nén và giải nén cực nhanh với thuật toán Snappy.
- **Encoding:** Áp dụng Dictionary Encoding, Run Length Encoding (RLE) giúp giảm đáng kể kích thước dữ liệu.

---

## 2.5 Kỹ Thuật Tối Ưu Truy VẤn Trong Impala

1. **Partitioning (Phân vùng):** Chia nhỏ dữ liệu thành các thư mục vật lý theo trường phân vùng (`release_year`, `review_year`). Giúp kích hoạt cơ chế **Partition Pruning** — chỉ quét các phân vùng thỏa mãn điều kiện `WHERE`.
2. **COMPUTE STATS (Thống kê dữ liệu):** Thu thập số lượng dòng (cardinality), số lượng giá trị duy nhất (NDV), tỷ lệ NULL. Dựa vào thông tin này, Impala Query Planner sẽ đưa ra kịch bản JOIN tối ưu nhất (Broadcast Join vs Partitioned/Hash Join).
3. **EXPLAIN & SUMMARY:** Công cụ hỗ trợ lập trình viên phân tích kế hoạch truy vấn (Execution Plan) và theo dõi tài nguyên tiêu thụ thời gian thực.
