# PROMPT TỔNG HỢP TOÀN BỘ ĐỒ ÁN MÔN HỌC DỮ LIỆU LỚN (BIG DATA)

> **Hướng dẫn sử dụng Prompt này:**
> Bạn có thể sao chép (copy) toàn bộ nội dung từ mục `=== BẮT ĐẦU PROMPT ===` đến `=== KẾT THÚC PROMPT ===` dưới đây và dán vào ChatGPT, Claude, DeepSeek hoặc Gemini bất kỳ lúc nào để:
> 1. Yêu cầu AI viết báo cáo môn học chi tiết (Báo cáo Word / PDF).
> 2. Yêu cầu AI tạo dàn ý và nội dung từng trang Slide thuyết trình (PowerPoint / Canva).
> 3. Đóng vai giảng viên phản biện để luyện tập trả lời câu hỏi bảo vệ đồ án.
> 4. Tóm tắt nhanh nội dung dự án để nộp cho giảng viên hướng dẫn.

---

```markdown
=== BẮT ĐẦU PROMPT ===

Bạn là một Chuyên gia Kỹ thuật Dữ liệu Lớn (Senior Big Data Engineer) và Giảng viên hướng dẫn môn Dữ Liệu Lớn (Big Data). 
Dưới đây là toàn bộ thông tin chi tiết về Đồ án Môn học Big Data mà tôi đã xây dựng và hoàn thành thực tế. 
Hãy đọc kỹ toàn bộ ngữ cảnh, kiến trúc, dữ liệu, giải pháp kỹ thuật và kết quả nghiên cứu dưới đây để hỗ trợ tôi thực hiện các yêu cầu tiếp theo (viết báo cáo, làm slide, giải đáp phản biện,...):

--------------------------------------------------------------------------------
1. THÔNG TIN CHUNG VỀ ĐỀ TÀI
--------------------------------------------------------------------------------
- Tên đề tài: "Phân tích dữ liệu trò chơi điện tử và khám phá xu hướng thị trường sử dụng Apache Impala" (Steam Games Big Data Analytics).
- Mục tiêu cốt lõi:
  1. Ứng dụng công nghệ xử lý dữ liệu lớn (Big Data SQL Engine) để phân tích hành vi, định giá, thể loại và xu hướng thị trường của toàn bộ nền tảng Steam.
  2. Chứng minh tính ưu việt của Apache Impala trong việc thực thi "Truy vấn tương tác" (Interactive Querying) với độ trễ thấp (< 0.2 giây).
  3. Đánh giá và đo lường thực nghiệm (Benchmark) hiệu năng giữa định dạng lưu trữ cột (Parquet Snappy) so với định dạng văn bản (CSV), cùng kỹ thuật cắt tỉa phân vùng (Partition Pruning).

--------------------------------------------------------------------------------
2. QUY MÔ VÀ ĐẶC ĐIỂM DỮ LIỆU (DATASET)
--------------------------------------------------------------------------------
- Nguồn dữ liệu: Dữ liệu thực tế từ nền tảng Steam (Steam Games Dataset).
- Quy mô bảng dữ liệu:
  * Fact Table (games_parquet / games_csv): 89,618 bản ghi trò chơi, chứa các thuộc tính: appid, name, release_date, price, price_group, positive, negative, pct_pos_total, num_reviews_total, average_playtime_forever, peak_ccu, v.v.
  * Dimension Genres (games_genres): 258,024 bản ghi quan hệ (chuẩn hóa 1-N).
  * Dimension Tags (games_tags): 1,008,987 bản ghi nhãn cộng đồng.
  * Dimension Developers & Publishers: Hàng chục ngàn nhà phát triển và phát hành game.
- Mô hình dữ liệu: Chuẩn Star Schema (Mô hình hình sao) tối ưu cho kho dữ liệu OLAP và truy vấn phân tán.
- Chiến lược phân vùng (Partitioning):
  * Phân vùng vật lý theo năm phát hành `release_year` (gồm 27 phân vùng từ năm 1997 đến 2025).

--------------------------------------------------------------------------------
3. KIẾN TRÚC KỸ THUẬT & CÔNG NGHỆ SỬ DỤNG (TECH STACK)
--------------------------------------------------------------------------------
- Công cụ truy vấn dữ liệu lớn: Apache Impala 3.4.0 (Distributed Massively Parallel Processing - MPP Engine).
- Định dạng lưu trữ tối ưu: Apache Parquet v1.0, nén Snappy (Columnar Storage).
- Môi trường hạ tầng:
  * Container Docker (`apache/kudu:impala-latest`) chạy trên macOS (Apple Silicon M1 Max 64GB RAM).
  * Các cổng kết nối: 21000 (Impala Shell/Beeswax), 21050 (HiveServer2), 25000 (Impala Web UI Coordinator).
- Pipeline tiền xử lý: Python 3.9, Pandas, PyArrow (chuyển đổi và tối ưu schema sang Parquet v1.0).
- Giao diện trực quan hóa & tương tác: Streamlit Web Terminal & Live SQL Workbench (chạy trên port 8501).

--------------------------------------------------------------------------------
4. CÁC THÁCH THỨC KỸ THUẬT NÂNG CAO ĐÃ GIẢI QUYẾT (CHÚNG MINH KỸ NĂNG XỬ LÝ)
--------------------------------------------------------------------------------
1. Xử lý Deadlock Rosetta 2 (Apple Silicon M1 Max):
   - Vấn đề: Khi chạy container x86_64 trên Rosetta 2, các lệnh gọi `fork()` đa luồng của Impala khi ghi phân vùng động (dynamic partition) bị treo deadlock `rt_mutex`.
   - Giải pháp: Chuyển toàn bộ pipeline tiền xử lý và chia 27 thư mục phân vùng Parquet thông qua PyArrow trước, sau đó gắn External Table và dùng `ALTER TABLE ... RECOVER PARTITIONS` trong Impala.
2. Lỗi tương thích Parquet Metadata:
   - Vấn đề: Impala 3.4.0 không tương thích siêu dữ liệu Parquet 2.0+.
   - Giải pháp: Thiết lập PyArrow xuất định dạng chuẩn Parquet version `1.0`.
3. Khắc phục lỗi Spin-loop 100% CPU của Impala Catalog:
   - Vấn đề: Cờ `-invalidate_tables_on_memory_pressure=true` mặc định của image gây vòng lặp kiểm tra dọn rác vô tận.
   - Giải pháp: Tạo script custom entrypoint đè cờ thành `-invalidate_tables_on_memory_pressure=false`.
4. Tối ưu hóa truy vấn CBO (Cost-Based Optimizer):
   - Thu thập thống kê bảng đầy đủ bằng lệnh `COMPUTE STATS` trên tất cả 7 bảng để Impala tính toán chi phí join tối ưu nhất.

--------------------------------------------------------------------------------
5. KẾT QUẢ NGHIÊN CỨU & PHÂN TÍCH (7 RESEARCH QUESTIONS - RQ1 ĐẾN RQ7)
--------------------------------------------------------------------------------
- RQ1 (Xu hướng phát triển): Thị trường game Steam phát triển sơ khai (1997-2011), bùng nổ từ kỷ nguyên Steam Greenlight (2012-2016) và tăng trưởng phi mã với Steam Direct (2017-nay), đạt đỉnh trên 18,000 game phát hành riêng trong năm 2024.
- RQ2 (Cơ cấu thể loại): Thể loại game độc lập (Indie) chiếm đa số tuyệt đối (>61,000 game), theo sau là Action, Adventure và Casual.
- RQ3 (Chiến lược định giá): Game phân khúc giá rẻ (<$10) và Free-to-play chiếm tỷ trọng áp đảo nhưng vẫn đạt mức đánh giá hài lòng rất cao (~75-78%).
- RQ4 (Hiện tượng ngoại lệ - Outliers): Thị trường bị thống trị bởi các tựa game huyền thoại phân hóa cực đoan: Counter-Strike 2 (>8 triệu reviews), PUBG (>3.2 triệu CCU), Dota 2, Baldur's Gate 3.
- RQ5 (Tương quan doanh thu & tương tác): Mô hình Free-to-play kết hợp microtransactions (vật phẩm trong game) đạt hiệu suất giữ chân người dùng (engagement) vượt trội so với game trả phí truyền thống.
- RQ6 (Benchmark Định dạng CSV vs Parquet):
  * Truy vấn tính toán tổng hợp trên 89,618 dòng:
    - CSV (quét tuần tự văn bản): ~0.84 - 0.95 giây.
    - Parquet (lưu trữ cột + nén Snappy): ~0.13 - 0.15 giây.
  * Kết luận: Parquet giúp tăng tốc truy vấn gấp ~6.5 lần và tiết kiệm hơn 80% thời gian thực thi nhờ khả năng bỏ qua các cột văn bản không liên quan.
- RQ7 (Benchmark Phân Vùng - Partition Pruning):
  * Kiểm tra qua lệnh `EXPLAIN`:
    - Bảng có phân vùng (`games_parquet`): Nhận diện điều kiện lọc năm, chỉ quét đúng `partitions=1/27`, chỉ đọc 1 file dung lượng 2.18 MB.
    - Bảng không phân vùng (`games_parquet_nopart`): Buộc phải quét toàn bộ file 15.27 MB và 89k dòng.
  * Kết luận: Partition Pruning giảm hơn 85% lượng dữ liệu đọc từ ổ đĩa (I/O) và tối ưu hóa tài nguyên CPU.

--------------------------------------------------------------------------------
6. SẢN PHẨM HOÀN THIỆN ĐÃ ĐÓNG GÓI & CÁCH VẬN HÀNH DEMO
--------------------------------------------------------------------------------
1. Khởi chạy 1-Click:
   - File nhấp đúp Finder: `Run_Demo.command` (Tự động bật Docker -> Tự khởi động Impala -> Tự kích hoạt Web Browser).
   - Lệnh Terminal: `./run_demo.sh`
2. Giao diện Web tương tác trực tiếp (Streamlit):
   - Truy cập: `http://localhost:8501`
   - Tab 1: Web Terminal & Live SQL (Cho phép nhập SQL tự do, đo độ trễ Impala mili-giây, hiển thị bảng động, tự vẽ biểu đồ tức thì, thư viện câu lệnh mẫu 1-click).
   - Tab 2: Benchmark Hiệu Năng (Nút bấm so sánh CSV vs Parquet và xem cây thực thi EXPLAIN Partition Pruning trực tiếp).
   - Tab 3: Bảng điều khiển phân tích xu hướng thị trường Steam.
   - Tab 4: Kiến trúc hệ thống và thông số CSDL.
3. Giao diện giám sát nhân Impala (Coordinator):
   - Truy cập: `http://localhost:25000/queries` để quan sát kế hoạch phân tán và đồ thị tài nguyên thời gian thực.

=== KẾT THÚC PROMPT ===
```
