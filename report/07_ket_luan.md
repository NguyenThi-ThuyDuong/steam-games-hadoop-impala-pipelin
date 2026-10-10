# CHƯƠNG 7: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 7.1 Tóm Tắt Kết Quả Nghiên Cứu

Đề tài đã hoàn thành xuất sắc tất cả các mục tiêu đề ra trong đề cương:
1. **Tiền xử lý & Chuẩn hóa Dữ liệu:** Làm sạch bộ dữ liệu **89,618 trò chơi** và **40,248,484 đánh giá người dùng** từ nền tảng Steam.
2. **Xây dựng Kiến trúc Data Model:** Thiết kế mô hình Star Schema chuẩn OLAP, lưu trữ Parquet phân vùng theo `release_year` và `review_year`.
3. **Phân tích Kinh doanh & Thị trường:** Trả lời trọn vẹn các câu hỏi nghiên cứu RQ1 - RQ5, nhận diện sự bùng nổ số lượng game sau 2014, xu hướng Free-to-Play và các nhóm game bất thường.
4. **Thực nghiệm Hiệu năng Apache Impala:** Chứng minh Parquet giúp tăng tốc **10x - 16x** so với CSV, Partitioning giảm **85% thời gian truy vấn**, và `COMPUTE STATS` giúp chuyển đổi thông minh chiến lược Join từ Shuffle sang Broadcast Join.

---

## 7.2 Đóng Góp Của Đề Tài

1. **Về mặt kỹ thuật Dữ liệu lớn:** Cung cấp quy trình thực hành tốt nhất (Best Practices) cho việc xây dựng Data Pipeline phân tích trên Apache Impala và Parquet.
2. **Về mặt kinh doanh:** Cung cấp thông tin thị trường hữu ích cho các nhà phát triển game độc lập (Indie Developers) về định giá sản phẩm và kỳ vọng của cộng đồng.

---

## 7.3 Hạn Chế & Hướng Phát Triển

### Hạn chế
- Dữ liệu Steam chưa bao gồm doanh thu thực tế chính xác (do Steam không công khai doanh thu chi tiết).
- Chưa tích hợp xử lý ngôn ngữ tự nhiên (NLP) thời gian thực trên Impala cho nội dung review text.

### Hướng phát triển
1. Tích hợp **Apache Spark MLlib** để thực hiện dự đoán điểm đánh giá và mô hình gợi ý trò chơi (Recommendation System).
2. Xây dựng **Dashboard thời gian thực** kết nối Apache Impala với Apache Superset / Tableau.
