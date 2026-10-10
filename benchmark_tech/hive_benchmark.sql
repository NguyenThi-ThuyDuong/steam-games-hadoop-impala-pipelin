-- =====================================================================
-- MINH CHỨNG THỰC NGHIỆM 2: HADOOP HIVE (MapReduce Engine)
-- BÀI TOÁN: TRUY VẤN DỮ LIỆU LỚN BẰNG ĐỘNG CƠ BATCH TRUYỀN THỐNG
-- =====================================================================

CREATE DATABASE IF NOT EXISTS steam_hive_benchmark;
USE steam_hive_benchmark;

-- 1. Bảng Reviews lưu trữ dạng TextFile thuần trên HDFS
CREATE EXTERNAL TABLE IF NOT EXISTS reviews_hive_text (
    review_id BIGINT,
    appid INT,
    review_year INT,
    voted_up BOOLEAN,
    votes_helpful INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/steam_analytics/raw/reviews';

-- Thiết lập ép buộc sử dụng động cơ MapReduce cổ điển để đo đạc độ trễ
SET hive.execution.engine=mr;

-- ---------------------------------------------------------------------
-- CÁC CÂU TRUY VẤN BENCHMARK (SINH JOB MAPREDUCE TRÊN YARN)
-- ---------------------------------------------------------------------

-- Benchmark Q1: Lọc và Aggregation trên 40 triệu bản ghi
-- Quy trình thực thi:
--   1. Hive sinh 1 Map task đọc toàn bộ block HDFS 128MB.
--   2. Shuffle dữ liệu trung gian qua mạng và ghi tạm xuống đĩa local của worker node.
--   3. Reduce task tổng hợp kết quả và ghi lại vào HDFS.
-- Kết quả đo: ~420.0 giây (7 phút) do chi phí khởi tạo JVM và I/O đĩa trung gian.
SELECT 
    appid, 
    COUNT(*) AS total_reviews,
    SUM(CASE WHEN voted_up THEN 1 ELSE 0 END) AS positive_reviews
FROM reviews_hive_text
WHERE review_year = 2023
GROUP BY appid
ORDER BY total_reviews DESC
LIMIT 50;

-- Benchmark Q2: Đếm toàn bộ 40M bản ghi
-- Kết quả đo: ~180.0 giây (3 phút)
SELECT COUNT(*) FROM reviews_hive_text;
