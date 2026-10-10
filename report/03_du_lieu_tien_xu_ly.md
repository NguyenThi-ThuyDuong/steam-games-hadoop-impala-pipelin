# CHƯƠNG 3: DỮ LIỆU VÀ TIỀN XỬ LÝ

## 3.1 Nguồn Dữ Liệu

Nghiên cứu sử dụng bộ dữ liệu trò chơi điện tử từ nền tảng Steam (được thu thập và xuất bản trên Kaggle bởi ForgeMaster):
1. **Dữ liệu Games Metadata:** File `games_march2025_cleaned.csv` chứa thông tin chi tiết của 89,618 trò chơi phát hành từ năm 1997 đến tháng 3/2025.
2. **Dữ liệu Steam Reviews:** 11 tập tin CSV (`reviews-1-115.csv` đến `reviews-13537-27075.csv`) chứa 40,248,484 đánh giá của cộng đồng game thủ.

---

## 3.2 Quy Trình Tiền Xử Lý Dữ Liệu

Quy trình tiền xử lý được thiết kế bằng ngôn ngữ Python (`scripts/preprocess_games.py` và `scripts/preprocess_reviews.py`):

```
┌─────────────────────────┐      ┌─────────────────────────┐
│  Raw Games Data CSV     │      │   Raw Review Files CSV  │
│      (89,618 rows)      │      │    (40,248,484 rows)    │
└────────────┬────────────┘      └────────────┬────────────┘
             │                                │
             ▼                                ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│ preprocess_games.py     │      │ preprocess_reviews.py   │
│ - Clean date & price    │      │ - Parse Unix Timestamp  │
│ - Extract release_year  │      │ - Extract review_year   │
│ - Separate Multivalued  │      │ - Clean text & newlines │
│   dimensions (Genres,   │      │ - Compute review_length │
│   Tags, Devs, Pubs)     │      │                         │
└────────────┬────────────┘      └────────────┬────────────┘
             │                                │
             ▼                                ▼
┌─────────────────────────┐      ┌─────────────────────────┐
│ Output Cleaned Files:   │      │ Output Cleaned Files:   │
│ - games_cleaned.csv     │      │ - cleaned_reviews_*.csv │
│ - games_genres.csv      │      │                         │
│ - games_tags.csv        │      │                         │
│ - games_developers.csv  │      │                         │
│ - games_publishers.csv  │      │                         │
└─────────────────────────┘      └─────────────────────────┘
```

---

## 3.3 Kết Quả Profiling Dữ Liệu Đã Làm Sạch

### 1. Bảng Games (`games_cleaned.csv`)
- Tổng số bản ghi: **89,618 trò chơi duy nhất**.
- Phạm vi năm phát hành: Từ năm 1997 đến 2025.
- Mức giá: Từ $0.00 (Miễn phí) đến $999.00, phân thành 6 nhóm giá (`Free`, `0-5`, `5-15`, `15-30`, `30-60`, `60+`).

### 2. Bảng Phụ Thuộc (Dimensions)
- `games_genres.csv`: **211,842 liên kết** game - thể loại.
- `games_tags.csv`: **1,245,630 liên kết** game - thẻ mô tả.
- `games_developers.csv`: **94,112 nhà phát triển**.
- `games_publishers.csv`: **88,950 nhà phát hành**.

### 3. Bảng Reviews (`cleaned_reviews_*.csv`)
- Tổng số dòng sạch: **40,248,484 bản ghi**.
- Trường liên kết: `appid` trùng khớp hoàn toàn với bảng Games.
- Chuẩn hóa thời gian: Bổ sung trường phân vùng `review_year` và `review_month`.
