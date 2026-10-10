# CHƯƠNG 4: XÂY DỰNG MÔĨ TRƯỜNG VÀ MÔ HÌNH DỮ LIỆU

## 4.1 Kiến Trúc Môi Trường Hệ Thống

Hệ thống phân tích dữ liệu phân tán được thiết lập dựa trên Big Data Stack:
- **Cụm Hadoop Distributed File System (HDFS):** Lưu trữ tập tin định dạng CSV thô và Parquet phân vùng.
- **Apache Hive Metastore:** Quản lý Schema, DDL và định nghĩa bảng external/internal.
- **Apache Impala Engine:** Thực thi các truy vấn SQL tính toán thời gian thực.

---

## 4.2 Thiết Kế Mô Hình Dữ Liệu Star Schema

Mô hình dữ liệu được tối ưu theo kiến trúc Star Schema tiêu chuẩn cho hệ thống OLAP:

```
                          ┌─────────────────────┐
                          │    games_genres     │
                          │─────────────────────│
                          │ appid (INT, FK)     │
                          │ genre (STRING)      │
                          └──────────┬──────────┘
                                     │
┌──────────────────────┐     ┌───────┴─────────────┐     ┌────────────────────────┐
│   games_developers   │     │     fact_games      │     │      fact_reviews      │
│──────────────────────│     │─────────────────────│     │────────────────────────│
│ appid (INT, FK)      │◄────┤ appid (INT, PK)     │────►│ steamid (BIGINT)       │
│ developer (STRING)   │     │ name (STRING)       │     │ appid (INT, FK)        │
└──────────────────────┘     │ release_date(STRING)│     │ voted_up (BOOLEAN)     │
                             │ price (DOUBLE)      │     │ votes_up (INT)         │
┌──────────────────────┐     │ price_group(STRING) │     │ votes_funny (INT)      │
│   games_publishers   │     │ required_age (INT)  │     │ weighted_vote_score    │
│──────────────────────│     │ dlc_count (INT)     │     │ playtime_forever (INT) │
│ appid (INT, FK)      │◄────┤ windows/mac/linux │     │ playtime_at_review     │
│ publisher (STRING)   │     │ metacritic_score    │     │ num_games_owned (INT)  │
└──────────────────────┘     │ achievements (INT)  │     │ num_reviews (INT)      │
                             │ recommendations     │     │ review_length (INT)    │
┌──────────────────────┐     │ positive (INT)      │     │ review_date (STRING)   │
│      games_tags      │     │ negative (INT)      │     │ review_month (INT)     │
│──────────────────────│     │ estimated_owners    │     │ [PARTITION]            │
│ appid (INT, FK)      │◄────┤ avg_playtime (INT)  │     │ review_year (INT)      │
│ tag (STRING)         │     │ peak_ccu (INT)      │     └────────────────────────┘
│ count (INT)          │     │ pct_pos_total (INT) │
└──────────────────────┘     │ num_reviews_total   │
                             │ [PARTITION]         │
                             │ release_year (INT)  │
                             └─────────────────────┘
```

---

## 4.3 Script Nạp Dữ Liệu & Khởi Tạo Bảng Impala

Tất cả các truy vấn DDL và DML được lưu trữ tại:
- [`sql/create_tables.sql`](file:///D:/HocTap/HK1_27/BigData/DoAnBigData/sql/create_tables.sql): Tạo cơ sở dữ liệu `steam_analytics`, các bảng External CSV và các bảng Parquet phân vùng (`games_parquet`, `reviews_parquet`).
- [`sql/load_data.sql`](file:///D:/HocTap/HK1_27/BigData/DoAnBigData/sql/load_data.sql): Thực thi lệnh `INSERT INTO ... PARTITION` với `SET DYNAMIC_PARTITIONING = true` để nạp dữ liệu tự động theo phân vùng năm.
- **Tính toán thống kê:** Thực thi `COMPUTE STATS` trên tất cả các bảng để cung cấp metadata cho Query Planner của Impala.
