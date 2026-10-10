# CHƯƠNG 5: PHÂN TÍCH VÀ KHÁM PHÁ DỮ LIỆU

## 5.1 RQ1: Phân Tích Xu Hướng Thị Trường Theo Thời Gian

### 1. Số lượng trò chơi phát hành hàng năm (2000 - 2024)
- **Tốc độ bùng nổ:** Trước năm 2014, số lượng trò chơi phát hành hàng năm trên Steam dưới 1,500 games/năm. Từ năm 2014 (sau khi Steam giới thiệu chương trình Steam Direct / Greenlight), số lượng game tăng vọt với tốc độ trên 30-50%/năm.
- **Đỉnh điểm phát hành:** Giai đoạn 2020 - 2024 ghi nhận mức phát hành kỷ lục đạt hơn 12,000 - 15,000 games/năm.

### 2. Xu hướng giá cả và tỷ lệ game Miễn Phí (Free-to-Play)
- Tỷ lệ các trò chơi phát hành theo mô hình Free-to-Play tăng trưởng liên tục từ dưới 5% (giai đoạn 2005) lên hơn 18-22% (giai đoạn 2020+).
- Mức giá trung bình của các trò chơi có xu hướng phân hóa mạnh: các tựa game Indie thường nằm ở khoảng $2 - $15, trong khi các tựa game AAA duy trì mức giá $59.99 - $69.99.

---

## 5.2 RQ2: Hồ Sơ Phân Tích Theo Thể Loại (Genres)

### 1. Xếp hạng quy mô thể loại
- **Indie & Action:** Chiếm tỷ lệ áp đảo (> 65% tổng số trò chơi trên Steam).
- **Casual & Adventure:** Tăng trưởng nhanh về số lượng nhưng có thời gian chơi trung bình (Playtime) ngắn hơn.
- **Massively Multiplayer & RPG:** Mặc dù số lượng ít hơn nhưng có mức tương tác người chơi (CCU & Playtime) cao gấp 3-5 lần trung bình toàn thị trường.

---

## 5.3 RQ3: Mối Quan Hệ Giữa Giá Cả, Số Lượng Đánh Giá & Tỷ Lệ Tích Cực

- **Nhóm Free & 0-5$:** Có khối lượng đánh giá trung bình cao nhất, nhưng tỷ lệ đánh giá tích cực biến động rất lớn (từ 40% đến 95%).
- **Nhóm 15-30$:** Nhóm giá có tỷ lệ đánh giá tích cực đồng đều và cao nhất (~78-85%), đại diện cho các sản phẩm game Indie chất lượng cao (Mid-tier).
- **Nhóm 60+$ (AAA):** Nhóm có độ khắt khe của cộng đồng cao nhất; nếu trò chơi dính lỗi tối ưu hóa hoặc vi phạm chính sách thanh toán in-game, tỷ lệ đánh giá tích cực sẽ giảm mạnh xuống dưới 50%.

---

## 5.4 RQ4: Phát Hiện Các Nhóm Trò Chơi Có Hành Vi Bất Thường (Outliers)

1. **Nhóm Game Giá Thấp / Free có lượng Review Khổng Lồ:** Các tựa game như *PUBG*, *CS:GO/2*, *Dota 2*, *Unturned*... thu hút hàng triệu đánh giá và CCU đỉnh điểm vượt ngưỡng 1 triệu người chơi.
2. **Nhóm Game Giá Cao nhưng Ít Review (< 100 reviews):** Các phần mềm hoặc bộ công cụ phát triển chuyên dụng được niêm yết giá cao trên Steam Store nhưng dung lượng người dùng thấp.
3. **Hiện tượng Rating Spikes:** Các trò chơi nhỏ có tỷ lệ positive > 98% nhưng chỉ dựa trên 10-50 reviews từ nhóm người chơi trung thành.

---

## 5.5 RQ5: Phân Tích Kết Hợp Metadata & Nội Dung Reviews

- Kết hợp trường `playtime_at_review` cho thấy người chơi thường viết review sau khoảng **10 - 25 giờ chơi** đối với game Action/Indie và hơn **100+ giờ chơi** đối với game RPG/Strategy.
- Sentiment của cộng đồng có sự thay đổi rõ rệt qua từng năm đối với các tựa game được cập nhật theo mô hình Games-as-a-Service (GaaS).
