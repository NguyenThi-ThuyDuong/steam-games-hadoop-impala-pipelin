# TÀI LIỆU MÔ HÌNH DỮ LIỆU (STAR SCHEMA DATA MODEL)

## 1. Kiến Trúc Mô Hình Dữ Liệu Star Schema

Mô hình dữ liệu được thiết kế theo chuẩn Star Schema phục vụ truy vấn OLAP hiệu năng cao trên Apache Impala.

```
                         ┌──────────────────┐
                         │   games_genres   │
                         │──────────────────│
                         │ appid (FK)       │
                         │ genre            │
                         └────────┬─────────┘
                                  │
┌──────────────────┐     ┌────────┴─────────┐     ┌───────────────────────┐
│ games_developers │     │   fact_games     │     │     fact_reviews      │
│──────────────────│     │──────────────────│     │───────────────────────│
│ appid (FK)       │◄────┤ appid (PK)       │────►│ steamid               │
│ developer        │     │ name             │     │ appid (FK)            │
└──────────────────┘     │ release_date     │     │ voted_up              │
                         │ price            │     │ votes_up              │
┌──────────────────┐     │ price_group      │     │ votes_funny           │
│ games_publishers │     │ required_age     │     │ weighted_vote_score   │
│──────────────────│     │ dlc_count        │     │ playtime_forever      │
│ appid (FK)       │◄────┤ windows/mac/linux│     │ playtime_at_review    │
│ publisher        │     │ metacritic_score │     │ num_games_owned       │
└──────────────────┘     │ achievements     │     │ num_reviews           │
                         │ recommendations  │     │ review_length         │
┌──────────────────┐     │ positive         │     │ review_date           │
│    games_tags    │     │ negative         │     │ review_month          │
│──────────────────│     │ estimated_owners │     │ [PARTITION]           │
│ appid (FK)       │◄────┤ avg_playtime     │     │ review_year (INT)     │
│ tag              │     │ peak_ccu         │     └───────────────────────┘
│ count            │     │ pct_pos_total    │
└──────────────────┘     │ num_reviews_total│
                         │ [PARTITION]      │
                         │ release_year(INT)│
                         └──────────────────┘
```

---

## 2. Thiết Kế Partitioning & Storage Format

### 2.1 Định dạng lưu trữ Parquet (Columnar Storage)
- Toàn bộ các bảng phân tích chính được lưu trữ ở định dạng **Apache Parquet**.
- Tối ưu hóa đọc dữ liệu theo cột, nén Snappy giảm dung lượng lưu trữ HDFS từ 60-75% so với CSV.
- Cho phép vectorize read và skip data blocks khi có điều kiện FILTER.

### 2.2 Chiến lược Phân vùng (Partitioning Strategy)
- **`games_parquet`**: Partition theo `release_year` (Năm phát hành game).
  - Giúp tăng tốc các truy vấn phân tích xu hướng thị trường theo giai đoạn / thời gian (Partition Pruning).
- **`reviews_parquet`**: Partition theo `review_year` (Năm viết review).
  - Với 40+ triệu dòng dữ liệu, phân vùng theo năm giúp Impala chỉ cần quét các thư mục năm liên quan thay vì quét toàn bộ 5 GB dữ liệu.

---

## 3. Danh Mục Chi Tiết Các Bảng Dữ Liệu Trong Impala Database `steam_analytics`

1. `games_csv` — External Table trích xuất từ dữ liệu thô.
2. `reviews_csv` — External Table chứa dữ liệu reviews.
3. `games_parquet` — Main Fact Table cho Trò chơi (Partitioned by `release_year`).
4. `reviews_parquet` — Main Fact Table cho Reviews (Partitioned by `review_year`).
5. `games_parquet_nopart` — Table so sánh benchmark không partition.
6. `reviews_parquet_nopart` — Table so sánh benchmark không partition.
7. `games_genres` — Dimension Table liên kết Thể loại game.
8. `games_tags` — Dimension Table liên kết Thẻ mô tả game.
