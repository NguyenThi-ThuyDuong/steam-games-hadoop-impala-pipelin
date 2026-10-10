# BÁO CÁO PHÂN TÍCH VÀ PROFILING DỮ LIỆU STEAM (DATA PROFILE REPORT)

## 1. Tổng Quan Bộ Dữ Liệu

Bộ dữ liệu nghiên cứu được khai thác từ nền tảng Steam, gồm 2 mảng thông tin chính:

| Tên bộ dữ liệu | Số lượng bản ghi | Dung lượng thô | Định dạng | Số cột |
|----------------|------------------|----------------|-----------|--------|
| **Games Metadata** (`games_march2025_cleaned.csv`) | 89,618 trò chơi | ~447 MB | CSV (UTF-8) | 47 |
| **Steam Reviews** (11 file CSV) | 40,248,484 đánh giá | ~5.0 GB | CSV (UTF-8) | 13 |

---

## 2. Chi Tiết Cấu Trúc Dữ Liệu Trò Chơi (Games Metadata)

### 2.1 Các Trường Thông Tin Chọn Lọc Cho Phân Tích

- **Mã định danh:** `appid` (INT) — Khóa chính duy nhất đại diện cho trò chơi.
- **Tên & Thông tin chung:** `name` (STRING), `release_date` (STRING), `release_year` (INT - trích xuất), `short_description` (STRING).
- **Giá & Phân nhóm giá:** `price` (DOUBLE), `price_group` (STRING: Free, 0-5, 5-15, 15-30, 30-60, 60+).
- **Hỗ trợ Nền tảng & Ngôn ngữ:** `windows` (BOOL), `mac` (BOOL), `linux` (BOOL), `supported_languages` (STRING).
- **Đánh giá & Tương tác Store:** `pct_pos_total` (INT - % tích cực), `num_reviews_total` (INT), `positive` (INT), `negative` (INT), `recommendations` (INT), `metacritic_score` (INT), `peak_ccu` (INT - peak concurrent users).
- **Thời gian chơi (Playtime):** `average_playtime_forever` (INT), `median_playtime_forever` (INT).
- **Các Chiều Phân Tích Đa Giá Trị (Multivalued Dimensions):** `genres` (Danh sách thể loại), `tags` (Dictionary thẻ phân loại + số vote), `developers` (Nhà phát triển), `publishers` (Nhà phát hành).

### 2.2 Chất Lượng & Xử Lý Dữ Liệu Trò Chơi
- Không phát hiện trùng lặp khóa chính `appid` sau khi trích xuất.
- Trường `release_date` được chuẩn hóa trích xuất `release_year` để làm cột partition.
- Các trường danh sách/dictionary dạng chuỗi (`genres`, `tags`, `developers`, `publishers`) đã được normalize thành 4 bảng dimension riêng phục vụ JOIN trong Impala.

---

## 3. Chi Tiết Cấu Trúc Dữ Liệu Đánh Giá (Steam Reviews)

### 3.1 Các Trường Thông Tin Sau Chuẩn Hóa

- `steamid` (BIGINT): Mã định danh người dùng trên Steam.
- `appid` (INT): Mã trò chơi được đánh giá (Khóa ngoại liên kết `games_parquet.appid`).
- `voted_up` (BOOLEAN): Trạng thái đánh giá (True = Khuyên dùng / Tích cực, False = Không khuyên dùng / Tiêu cực).
- `votes_up` (INT): Số lượt bình chọn hữu ích của cộng đồng cho review.
- `votes_funny` (INT): Số lượt bình chọn hài hước.
- `weighted_vote_score` (DOUBLE): Điểm số trọng số đánh giá độ tin cậy của review.
- `playtime_at_review` (INT): Thời gian chơi game tính đến thời điểm viết review (phút).
- `playtime_forever` (INT): Tổng thời gian chơi game tính đến thời điểm thu thập (phút).
- `num_games_owned` (INT): Số lượng game sở hữu bởi reviewer.
- `num_reviews` (INT): Tổng số review người dùng đó đã viết trên Steam.
- `review_length` (INT): Độ dài văn bản review (số ký tự).
- `review_date` (STRING): Ngày viết review (YYYY-MM-DD).
- `review_year` (INT): Năm viết review (Partition key).
- `review_month` (INT): Tháng viết review.

### 3.2 Khóa Liên Kết (Join Key Profiling)
- `appid` là trường liên kết 100% giữa Reviews và Games.
- Việc rút gọn loại bỏ chuỗi văn bản review thô (`review_text`) khi chuyển sang bảng làm sạch `reviews_cleaned` giúp giảm dung lượng ghi đĩa từ 5.0 GB xuống còn ~1.8 GB, tăng tốc đáng kể truy vấn SQL OLAP.

---

## 4. Kết Luận Khảo Sát
Bộ dữ liệu đã hoàn toàn đạt chuẩn cho việc lưu trữ phân tán trên HDFS và xử lý bằng Apache Impala.
