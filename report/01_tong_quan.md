# CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI

## 1.1 Lý Do Chọn Đề Tài

Trong kỷ nguyên chuyển đổi số và bùng nổ công nghệ thông tin, ngành công nghiệp trò chơi điện tử (Video Games Industry) đã phát triển mạnh mẽ trở thành một trong những ngành giải trí có doanh thu cao nhất toàn cầu. Nền tảng phân phối trò chơi trực tuyến Steam (thuộc Valve Corporation) hiện lưu trữ hàng chục nghìn trò chơi với hàng chục triệu người dùng hoạt động hàng ngày, sản sinh ra một khối lượng dữ liệu khổng lồ (Big Data) bao gồm: thông tin trò chơi (metadata, giá cả, thể loại, nhà phát hành), thống kê thời gian chơi, số lượng người chơi đồng thời (CCU) và hàng chục triệu đánh giá (reviews) từ cộng đồng.

Tuy nhiên, việc phân tích dữ liệu ở quy mô này đặt ra những thách thức lớn về khả năng lưu trữ, xử lý và tối ưu hóa truy vấn SQL trên hệ thống phân tán. Các phương pháp xử lý dữ liệu truyền thống bằng cơ sở dữ liệu quan hệ (RDBMS) không thể đáp ứng được thời gian phản hồi khi thực hiện các truy vấn phức tạp trên tập dữ liệu hàng chục triệu dòng. **Apache Impala** — engine truy vấn SQL phân tán theo kiến trúc Massively Parallel Processing (MPP) trên môi trường Apache Hadoop — đã khẳng định ưu thế vượt trội về tốc độ xử lý các truy vấn OLAP thời gian thực so với MapReduce hay Apache Hive.

Đề tài **"Phân tích dữ liệu trò chơi điện tử và khám phá xu hướng thị trường sử dụng Apache Impala"** được thực hiện nhằm mục tiêu kết hợp giữa bài toán phân tích thị trường kinh doanh game thực tế với việc nghiên cứu thực nghiệm tối ưu hóa hiệu năng truy vấn dữ liệu lớn.

---

## 1.2 Khoảng Trống Nghiên Cứu và Điểm Mới Của Đề Tài

Các nghiên cứu trước đây về dữ liệu Steam chủ yếu tập trung vào một trong hai khía cạnh độc lập:
1. Thống kê mô tả đặc điểm thị trường (giá, thể loại, điểm đánh giá) bằng các công cụ như R hoặc Python Pandas trên tập dữ liệu nhỏ.
2. Phân tích cảm xúc (Sentiment Analysis) trên nội dung review bằng Machine Learning / NLP.

**Điểm mới nổi bật của đề tài:**
- **Tích hợp đa chiều dữ liệu ở quy mô lớn:** Kết hợp bộ dữ liệu Metadata 89,618 trò chơi với bộ dữ liệu 40,248,484 đánh giá người chơi.
- **Thực nghiệm chuyên sâu kiến trúc Apache Impala:** Định lượng chính xác ảnh hưởng của các kỹ thuật tổ chức dữ liệu: định dạng lưu trữ cột (Apache Parquet), kỹ thuật phân vùng dữ liệu (Partitioning), thống kê bảng (COMPUTE STATS) và chiến lược truy vấn JOIN lớn-nhỏ.
- **Phát hiện nhóm hành vi bất thường (Anomalies):** Xây dựng tiêu chuẩn lọc các trường hợp lệch chuẩn về giá cả, số lượng đánh giá và tỷ lệ phản hồi tích cực.

---

## 1.3 Mục Tiêu Nghiên Cứu

### Mục tiêu tổng quát
Xây dựng quy trình phân tích dữ liệu trò chơi điện tử quy mô lớn bằng Apache Impala nhằm nhận diện các xu hướng thị trường, mối quan hệ giữa giá cả - đánh giá - mức độ tương tác, đồng thời đánh giá định lượng các yếu tố ảnh hưởng đến hiệu năng truy vấn dữ liệu lớn.

### Mục tiêu cụ thể
1. Tiền xử lý và chuẩn hóa bộ dữ liệu Steam (Games & Reviews).
2. Thiết kế mô hình Star Schema tối ưu cho truy vấn OLAP trên Apache Impala.
3. Chuyển đổi lưu trữ từ CSV sang Parquet phân vùng theo năm (`release_year`, `review_year`).
4. Xây dựng bộ truy vấn SQL phân tích trả lời 5 câu hỏi nghiên cứu về thị trường (RQ1 - RQ5).
5. Thực hiện 5 bài thí nghiệm benchmark hiệu năng Impala (RQ6 - RQ7).
6. Trực quan hóa kết quả và đề xuất khuyến nghị cho các nhà phát triển game.

---

## 1.4 Câu Hỏi Nghiên Cứu (Research Questions)

- **RQ1:** Thị trường trò chơi điện tử thay đổi như thế nào theo thời gian về số lượng, thể loại và mức giá?
- **RQ2:** Các thể loại trò chơi khác nhau như thế nào về giá, đánh giá và mức độ tương tác của người chơi?
- **RQ3:** Mối quan hệ giữa giá trò chơi, số lượng review và tỷ lệ đánh giá tích cực có đặc điểm gì?
- **RQ4:** Có tồn tại các nhóm trò chơi có hành vi khác biệt đáng kể so với xu hướng chung hay không?
- **RQ5:** Việc kết hợp metadata của game với dữ liệu review có giúp phát hiện thêm các xu hướng so với phân tích metadata đơn thuần hay không?
- **RQ6:** Parquet, partitioning và statistics ảnh hưởng như thế nào đến thời gian và hiệu quả truy vấn Apache Impala?
- **RQ7:** Khi quy mô dữ liệu tăng lên, khả năng xử lý của Apache Impala thay đổi như thế nào?

---

## 1.5 Đối Tượng và Phạm Vi Nghiên Cứu

- **Đối tượng:** Dữ liệu trò chơi điện tử và đánh giá người chơi trên nền tảng Steam.
- **Phạm vi công nghệ:** Tập trung vào Apache Impala, HDFS và các định dạng lưu trữ (CSV, Parquet).
