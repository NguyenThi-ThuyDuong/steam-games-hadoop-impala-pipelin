# HƯỚNG DẪN THIẾT LẬP MÔI TRƯỜNG VÀ TRIỂN KHAI APACHE IMPALA

## 1. Yêu Cầu Môi Trường Cần Thiết

- **Hệ điều hành:** Linux (Ubuntu 20.04/22.04 LTS hoặc CentOS 7/RHEL 8) / Cloudera Quickstart Docker.
- **Thành phần Apache Big Data Stack:**
  - Hadoop HDFS (>= 3.x)
  - Apache Hive (Catalog & Metastore)
  - Apache Impala (>= 3.4 / 4.x)
- **Python Runtime:** Python 3.9+ (Thư viện: `pandas`, `matplotlib`, `seaborn`, `impyla`).

---

## 2. Các Bước Triển Khai Dữ Liệu Lên HDFS

### Bước 1: Tạo cấu trúc thư mục trên HDFS

```bash
hdfs dfs -mkdir -p /user/steam_analytics/raw/games
hdfs dfs -mkdir -p /user/steam_analytics/raw/reviews
hdfs dfs -mkdir -p /user/steam_analytics/raw/games_genres
hdfs dfs -mkdir -p /user/steam_analytics/raw/games_tags
```

### Bước 2: Tải dữ liệu đã tiền xử lý lên HDFS

```bash
# Upload Games data
hdfs dfs -put D:/HocTap/HK1_27/BigData/DoAnBigData/data/processed/games_cleaned.csv /user/steam_analytics/raw/games/

# Upload Reviews cleaned files
hdfs dfs -put D:/HocTap/HK1_27/BigData/DoAnBigData/data/processed/reviews_cleaned/*.csv /user/steam_analytics/raw/reviews/

# Upload Dimensions data
hdfs dfs -put D:/HocTap/HK1_27/BigData/DoAnBigData/data/processed/games_genres.csv /user/steam_analytics/raw/games_genres/
hdfs dfs -put D:/HocTap/HK1_27/BigData/DoAnBigData/data/processed/games_tags.csv /user/steam_analytics/raw/games_tags/
```

### Bước 3: Đăng ký bảng và chuyển đổi định dạng trên Impala Shell

```bash
# Chạy script tạo bảng
impala-shell -f D:/HocTap/HK1_27/BigData/DoAnBigData/sql/create_tables.sql

# Chạy script nạp dữ liệu và COMPUTE STATS
impala-shell -f D:/HocTap/HK1_27\BigData\DoAnBigData/sql/load_data.sql
```

---

## 3. Quy Trình Thực Thi Truy Vấn & Benchmark

- Phân tích kinh doanh (RQ1 - RQ5): Chạy `sql/analysis_queries.sql`.
- Benchmark hiệu năng (RQ6 - RQ7): Chạy `sql/benchmark_queries.sql`.
