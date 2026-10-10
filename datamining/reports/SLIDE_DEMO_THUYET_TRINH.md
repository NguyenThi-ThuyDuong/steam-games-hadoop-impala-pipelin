# TÀI LIỆU KỊCH BẢN THUYẾT TRÌNH VÀ HƯỚNG DẪN DEMO
## Đề tài: Phân tích dữ liệu trò chơi điện tử và khám phá xu hướng thị trường sử dụng Apache Impala bằng dữ liệu Steam
### Thư mục thực thi: `D:\HocTap\HK1_27\BigData\DoAnBigData\datamining`

---

## 1. DÀN Ý SLIDE THUYẾT TRÌNH (12 SLIDES CHUẨN KHOA HỌC)

### Slide 1: Trang tiêu đề
- **Tên đề tài:** Phân tích dữ liệu trò chơi điện tử và khám phá xu hướng thị trường sử dụng Apache Impala bằng dữ liệu Steam
- **Học phần:** Xử lý Dữ liệu Lớn (Big Data)
- **Sinh viên thực hiện & Giảng viên hướng dẫn**

### Slide 2: Đặt vấn đề & Mục tiêu nghiên cứu
- **Bối cảnh:** Nền tảng phân phối game Steam với hàng chục nghìn tựa game và hàng triệu người chơi đồng thời.
- **Thách thức:** Dữ liệu thô cồng kềnh, phân tán, chứa nhiều giá trị sentinel ngụy trang, thiếu sót và cấu trúc đa giá trị không chuẩn hóa.
- **Mục tiêu:** Ứng dụng quy trình Data Mining (Data Preprocessing) nghiêm ngặt để chuẩn bị dữ liệu chất lượng cao, lưu trữ tối ưu dạng Parquet và khai phá xu hướng bằng Apache Impala.

### Slide 3: Khảo sát dữ liệu thực tế (Data Profiling)
- Trình bày thông số bộ dữ liệu: 89,618 bản ghi, 47 thuộc tính, dung lượng 449 MB.
- Chỉ ra các vấn đề nghiêm trọng phát hiện được:
  - **36,419 bản ghi (40.6%)** nhận giá trị sentinel `-1` trong cột rating.
  - **86,071 bản ghi (96.0%)** nhận điểm Metacritic bằng `0`.
  - Nhiễu giá trị âm trong `required_age = -1`.

### Slide 4: Khung phương pháp luận Data Mining (Framework)
- Phân biệt rành mạch 4 giai đoạn chuẩn:
  1. **Data Cleaning:** Xử lý Sentinel, Imputation, Capping, Deduplication.
  2. **Outlier Detection:** Phân tích IQR & Z-Score (ngưỡng giá \$20.49, ngưỡng reviews 564).
  3. **Data Transformation:** Discretization phân khúc giá & xếp loại đánh giá theo chuẩn Steam.
  4. **Data Reduction & 1NF Normalization:** Loại 19 cột HTML/Media; tách 4 bảng Dimension.

### Slide 5: So sánh dữ liệu trước và sau tiền xử lý (Before vs After)
- Trình bày bảng đối sánh định lượng:
  - Triệt tiêu 100% lỗi sentinel và nhiễu logic.
  - Dung lượng lưu trữ giảm từ **449 MB (CSV) xuống ~18 MB (Parquet nén Snappy)** — tối ưu hóa **96%**.
  - Bổ sung 11 thuộc tính phân tích mới (`game_age`, `review_ratio`, `platform_count`,...).

### Slide 6: Kiến trúc hệ thống Big Data & Star Schema
- Mô hình dữ liệu Star Schema:
  - **Fact Table:** `games_parquet` (phân vùng theo `release_year` cho Partition Pruning).
  - **Dimension Tables:** `games_genres`, `games_tags`, `games_developers`, `games_publishers`.
- Định dạng Parquet: Cột nén Snappy giúp Impala chỉ đọc các cột cần thiết, tăng tốc truy vấn.

### Slide 7: Khám phá xu hướng 1 – Bùng nổ phát hành & Free-to-Play
- Biểu đồ số lượng phát hành qua các năm:
  - Năm 2014: 1,525 game -> Năm 2018: 7,443 game -> Năm 2024: **18,282 game**.
  - Tỷ lệ Free-to-Play tăng trưởng từ **8.2% lên 17.26%**.

### Slide 8: Khám phá xu hướng 2 – Cơ cấu phân khúc giá & "Điểm ngọt"
- Bảng phân phối giá:
  - Phân khúc Budget (< \$5): chiếm 43.95% thị trường.
  - Phân khúc Mid-range (\$5 - \$15) & Premium (\$15 - \$40): đạt điểm đánh giá cao nhất (78.2%).

### Slide 9: Khám phá xu hướng 3 – Ngoại lệ thị trường (Outliers)
- Nhóm game giá rẻ / F2P có lượng review khổng lồ (CS2, PUBG, Dota 2, Unturned).
- Nhóm phần mềm chuyên dụng giá cao nhưng lượng tương tác thấp.

### Slide 10: Khám phá xu hướng 4 – Lợi thế chiến lược Đa nền tảng
- So sánh Windows-only (76.95%) vs Multi-platform (23.05%):
  - Game hỗ trợ Mac/Linux có điểm đánh giá trung bình cao hơn và lượng review gấp đôi.

### Slide 11: Demo trực quan hóa các truy vấn SQL trên Apache Impala
- Trình diễn mã SQL tối ưu với hàm cửa sổ `LAG()`, hàm phân vị, và mệnh đề JOIN tối ưu.

### Slide 12: Kết luận & Hướng phát triển
- Tóm tắt kết quả đạt được.
- Đề xuất mở rộng mô hình Machine Learning dự đoán độ thành công của game mới.

---

## 2. KỊCH BẢN THUYẾT TRÌNH CHI TIẾT (SPEAKING SCRIPT)

### Phần 1: Giới thiệu (00:00 - 03:00)
> *"Kính thưa Thầy/Cô và các bạn, hôm nay nhóm em xin trình bày đề tài: 'Phân tích dữ liệu trò chơi điện tử và khám phá xu hướng thị trường sử dụng Apache Impala bằng dữ liệu Steam'. Khi tiếp cận bộ dữ liệu thực tế gồm gần 90,000 trò chơi và hơn 40 triệu đánh giá, thách thức lớn nhất mà nhóm nhận diện không phải là viết câu lệnh SQL, mà là chất lượng dữ liệu thô. Nếu đưa trực tiếp dữ liệu thô vào Impala, các phép tính thống kê sẽ bị sai lệch hoàn toàn do các giá trị sentinel và nhiễu dữ liệu. Vì vậy, nhóm đã xây dựng một pipeline Data Preprocessing chuẩn khoa học trước khi đưa vào cơ sở dữ liệu."*

### Phần 2: Phương pháp luận Tiền xử lý (03:00 - 08:00)
> *"Tại giai đoạn Data Profiling, nhóm đã phát hiện hơn 36,400 bản ghi — tương đương 40.6% toàn bộ dataset — mang giá trị -1 ở cột tỷ lệ đánh giá. Đây là giá trị sentinel quy ước của hệ thống cào dữ liệu khi game chưa có review. Nếu dùng hàm AVG() của Impala trên cột này, trung bình cộng sẽ bị kéo tụt xuống mức vô nghĩa. Nhóm đã chuyển đổi toàn bộ giá trị này về NULL để Impala tự động bỏ qua mẫu chưa đánh giá. Đồng thời, nhóm áp dụng phương pháp IQR để nhận diện 4,231 game có giá ngoại lệ và 8,492 game có lượng review ngoại lệ, gắn cờ khoa học thay vì xóa bỏ. Cuối cùng, nhóm rời rạc hóa giá thành 6 phân khúc chuẩn và chuyển đổi toàn bộ sang định dạng Parquet nén Snappy, giảm tới 96% dung lượng lưu trữ."*

### Phần 3: Trình diễn Demo Impala & Kết quả (08:00 - 15:00)
> *"Sau khi nạp vào Apache Impala với cơ sở dữ liệu steam_analytics_dm, bảng fact được phân vùng theo năm phát hành, cho phép kích hoạt cơ chế Partition Pruning giúp thời gian thực thi truy vấn chỉ tính bằng mili-giây. Dựa trên 10 câu truy vấn phân tích, nhóm đã rút ra 4 xu hướng thị trường nổi bật: Thứ nhất là sự bùng nổ của làn sóng game Indie sau năm 2014, với đỉnh điểm năm 2024 đạt hơn 18,200 tựa game. Thứ hai là tỷ lệ game Free-to-Play tăng trưởng gấp đôi trong 10 năm. Thứ ba là 'điểm ngọt' của thị trường nằm ở khoảng giá 5 đến 40 USD với độ hài lòng cao nhất. Và thứ tư là các tựa game đa nền tảng đạt mức độ tương tác cao gấp đôi so với game chỉ chạy trên Windows."*

### Phần 4: Kết luận (15:00 - 20:00)
> *"Quy trình tiền xử lý Data Mining mà nhóm thiết kế đã chứng minh vai trò tiên quyết trong việc bảo đảm tính toàn vẹn và độ tin cậy của kết quả phân tích Big Data. Nhóm xin chân thành cảm ơn Thầy/Cô đã chú ý lắng nghe và xin phép chuyển sang phần Q&A."*

---

## 3. HƯỚNG DẪN THỰC HÀNH DEMO TRỰC TIẾP (LIVE DEMO COMMANDS)

### Bước 1: Khởi chạy pipeline tiền xử lý (nếu demo lại từ đầu)
```powershell
python "D:\HocTap\HK1_27\BigData\DoAnBigData\datamining\scripts\01_data_preprocessing_pipeline.py"
```

### Bước 2: Chạy script thực thi các câu truy vấn phân tích
```powershell
python "D:\HocTap\HK1_27\BigData\DoAnBigData\datamining\scripts\02_run_market_analysis.py"
```

### Bước 3: Xem nhanh kết quả bảng số liệu mẫu trên terminal
```powershell
# Xem xu hướng phát hành theo năm và F2P
Get-Content "D:\HocTap\HK1_27\BigData\DoAnBigData\datamining\results\q1_yearly_releases_f2p.csv" -TotalCount 10

# Xem cơ cấu phân khúc giá
Get-Content "D:\HocTap\HK1_27\BigData\DoAnBigData\datamining\results\q5_price_category_summary.csv"

# Xem top Publisher
Get-Content "D:\HocTap\HK1_27\BigData\DoAnBigData\datamining\results\q7_top_publishers.csv" -TotalCount 10
```

### Bước 4: Mở Impala-shell (trên môi trường Hadoop/CDH nếu có cluster)
```bash
impala-shell -f "D:\HocTap\HK1_27\BigData\DoAnBigData\datamining\sql\01_impala_schema.sql"
impala-shell -f "D:\HocTap\HK1_27\BigData\DoAnBigData\datamining\sql\02_impala_analysis.sql"
```
