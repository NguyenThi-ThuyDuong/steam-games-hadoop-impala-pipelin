-- ============================================================================
-- APACHE IMPALA ANALYTICAL QUERIES FOR STEAM MARKET TRENDS
-- Database: steam_analytics_dm
-- Target Directory: D:\HocTap\HK1_27\BigData\DoAnBigData\datamining\sql\02_impala_analysis.sql
-- ============================================================================

USE steam_analytics_dm;

-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 1: SỐ LƯỢNG GAME PHÁT HÀNH THEO NĂM & TỶ LỆ FREE-TO-PLAY
-- Mục tiêu: Khám phá tốc độ tăng trưởng quy mô kho game và xu hướng mô hình F2P
-- Tối ưu hóa: Lợi dụng Partition Pruning trên cột release_year
-- ----------------------------------------------------------------------------
SELECT 
    release_year,
    COUNT(*) AS total_games,
    COUNT(CASE WHEN is_free THEN 1 END) AS free_games,
    COUNT(CASE WHEN NOT is_free THEN 1 END) AS paid_games,
    ROUND(COUNT(CASE WHEN is_free THEN 1 END) * 100.0 / COUNT(*), 2) AS free_ratio_pct,
    ROUND(AVG(CASE WHEN NOT is_free THEN price END), 2) AS avg_paid_price
FROM games_parquet
WHERE release_year >= 2000 AND release_year <= 2025
GROUP BY release_year
ORDER BY release_year;


-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 2: TỐC ĐỘ TĂNG TRƯỞNG QUA CÁC NĂM (YEAR-OVER-YEAR GROWTH RATE)
-- Mục tiêu: Đo lường tốc độ bùng nổ của thị trường qua hàm cửa sổ LAG()
-- ----------------------------------------------------------------------------
WITH yearly_stats AS (
    SELECT 
        release_year,
        COUNT(*) AS game_count
    FROM games_parquet
    WHERE release_year >= 2005 AND release_year <= 2024
    GROUP BY release_year
)
SELECT 
    release_year,
    game_count,
    game_count - LAG(game_count, 1) OVER (ORDER BY release_year) AS yoy_absolute_growth,
    ROUND((game_count - LAG(game_count, 1) OVER (ORDER BY release_year)) * 100.0 / 
          NULLIF(LAG(game_count, 1) OVER (ORDER BY release_year), 0), 2) AS yoy_growth_pct
FROM yearly_stats
ORDER BY release_year;


-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 3: XU HƯỚNG THỂ LOẠI PHỔ BIẾN THEO TỪNG THỜI KỲ (ERA / PERIOD)
-- Mục tiêu: Khám phá sự dịch chuyển của thị trường game qua 4 thập kỷ/giai đoạn
-- ----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN g.release_year BETWEEN 2000 AND 2009 THEN '1. Kỷ nguyên Cổ điển (2000-2009)'
        WHEN g.release_year BETWEEN 2010 AND 2014 THEN '2. Giai đoạn Greenlight (2010-2014)'
        WHEN g.release_year BETWEEN 2015 AND 2019 THEN '3. Giai đoạn Bùng nổ Indie (2015-2019)'
        WHEN g.release_year >= 2020 THEN '4. Kỷ nguyên Hiện đại (2020-2025)'
    END AS period_era,
    gg.genre,
    COUNT(DISTINCT g.appid) AS total_games_in_era
FROM games_parquet g
JOIN games_genres gg ON g.appid = gg.appid
WHERE g.release_year >= 2000
GROUP BY 1, gg.genre
HAVING COUNT(DISTINCT g.appid) >= 50
ORDER BY period_era, total_games_in_era DESC;


-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 4: HỒ SƠ THỂ LOẠI TOÀN DIỆN & MỨC ĐỘ TƯƠNG TÁC (GENRE PROFILE)
-- Mục tiêu: Thống kê quy mô, giá trung bình, rating và mức độ tương tác CCU/Playtime
-- ----------------------------------------------------------------------------
SELECT 
    gg.genre,
    COUNT(DISTINCT g.appid) AS total_games,
    ROUND(AVG(g.price), 2) AS avg_price,
    ROUND(AVG(CASE WHEN g.pct_pos_total IS NOT NULL THEN g.pct_pos_total END), 2) AS avg_positive_rating,
    ROUND(AVG(CASE WHEN g.num_reviews_total IS NOT NULL THEN g.num_reviews_total END), 0) AS avg_reviews,
    ROUND(AVG(g.average_playtime_forever), 0) AS avg_playtime_minutes,
    ROUND(AVG(g.peak_ccu), 0) AS avg_peak_concurrent_users
FROM games_parquet g
JOIN games_genres gg ON g.appid = gg.appid
GROUP BY gg.genre
HAVING COUNT(DISTINCT g.appid) >= 100
ORDER BY total_games DESC;


-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 5: PHÂN BỐ CƠ CẤU GIÁ GAME (DISCRETIZATION ANALYSIS)
-- Mục tiêu: Phân tích tỷ trọng và đặc trưng của từng phân khúc giá game
-- ----------------------------------------------------------------------------
SELECT 
    price_category,
    COUNT(*) AS game_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS category_share_pct,
    ROUND(AVG(CASE WHEN num_reviews_total IS NOT NULL THEN num_reviews_total END), 0) AS avg_reviews,
    ROUND(AVG(CASE WHEN pct_pos_total IS NOT NULL THEN pct_pos_total END), 2) AS avg_positive_pct,
    ROUND(AVG(peak_ccu), 0) AS avg_peak_ccu
FROM games_parquet
GROUP BY price_category
ORDER BY 
    CASE price_category
        WHEN 'Free' THEN 1
        WHEN 'Budget' THEN 2
        WHEN 'Mid-range' THEN 3
        WHEN 'Premium' THEN 4
        WHEN 'High-end' THEN 5
        WHEN 'Luxury' THEN 6
        ELSE 7
    END;


-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 6: TOP NHÀ PHÁT TRIỂN (DEVELOPERS) UY TÍN & HOẠT ĐỘNG MẠNH NHẤT
-- Mục tiêu: Nhận diện các Studio dẫn đầu thị trường về số lượng tựa game
-- ----------------------------------------------------------------------------
SELECT 
    d.developer,
    COUNT(DISTINCT g.appid) AS total_released_games,
    ROUND(AVG(g.price), 2) AS avg_game_price,
    ROUND(AVG(CASE WHEN g.pct_pos_total IS NOT NULL THEN g.pct_pos_total END), 2) AS avg_game_rating,
    SUM(CASE WHEN g.num_reviews_total IS NOT NULL THEN g.num_reviews_total ELSE 0 END) AS total_community_reviews
FROM games_developers d
JOIN games_parquet g ON d.appid = g.appid
WHERE d.developer != 'Unknown'
GROUP BY d.developer
HAVING COUNT(DISTINCT g.appid) >= 10
ORDER BY total_released_games DESC
LIMIT 25;


-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 7: TOP NHÀ PHÁT HÀNH (PUBLISHERS) CÓ TỔNG REVIEWS & ẢNH HƯỞNG LỚN NHẤT
-- Mục tiêu: Khám phá các Publisher chi phối lượng người chơi lớn nhất trên Steam
-- ----------------------------------------------------------------------------
SELECT 
    p.publisher,
    COUNT(DISTINCT g.appid) AS published_games,
    SUM(CASE WHEN g.num_reviews_total IS NOT NULL THEN g.num_reviews_total ELSE 0 END) AS total_reviews_amassed,
    ROUND(AVG(CASE WHEN g.pct_pos_total IS NOT NULL THEN g.pct_pos_total END), 2) AS avg_publisher_rating
FROM games_publishers p
JOIN games_parquet g ON p.appid = g.appid
WHERE p.publisher != 'Unknown'
GROUP BY p.publisher
HAVING COUNT(DISTINCT g.appid) >= 5
ORDER BY total_reviews_amassed DESC
LIMIT 20;


-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 8: PHÂN BỐ MỨC ĐỘ ĐÁNH GIÁ (RATING CATEGORY) THEO THỂ LOẠI CHÍNH
-- Mục tiêu: Tìm hiểu tỷ lệ game chất lượng cao (Overwhelmingly Positive) theo Genre
-- ----------------------------------------------------------------------------
SELECT 
    gg.genre,
    COUNT(*) AS total_genre_games,
    COUNT(CASE WHEN g.rating_category = 'Overwhelmingly Positive' THEN 1 END) AS overwhelming_positive_games,
    COUNT(CASE WHEN g.rating_category = 'Very Positive' THEN 1 END) AS very_positive_games,
    COUNT(CASE WHEN g.rating_category = 'Mixed' THEN 1 END) AS mixed_games,
    COUNT(CASE WHEN g.rating_category IN ('Negative', 'Overwhelmingly Negative') THEN 1 END) AS negative_games,
    COUNT(CASE WHEN g.rating_category = 'Unrated / Few Reviews' THEN 1 END) AS unrated_games
FROM games_parquet g
JOIN games_genres gg ON g.appid = gg.appid
GROUP BY gg.genre
HAVING COUNT(*) >= 1000
ORDER BY total_genre_games DESC;


-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 9: PHÂN TÍCH NGOẠI LỆ THỊ TRƯỜNG (OUTLIER DETECTION INSIGHTS)
-- Mục tiêu: Khám phá các game giá rẻ nhưng lượng review khổng lồ vs game giá cao ít review
-- ----------------------------------------------------------------------------
-- Nhóm A: Outlier giá rẻ / miễn phí tạo doanh thu và sự chú ý cực đại
SELECT 
    appid,
    name,
    price,
    price_category,
    num_reviews_total,
    pct_pos_total,
    peak_ccu,
    z_reviews
FROM games_parquet
WHERE price <= 5.0 AND is_reviews_outlier = TRUE AND num_reviews_total > 50000
ORDER BY num_reviews_total DESC
LIMIT 20;

-- Nhóm B: Outlier giá rất cao (Luxury / Specialized Software) nhưng ít người quan tâm
SELECT 
    appid,
    name,
    price,
    price_category,
    num_reviews_total,
    pct_pos_total,
    z_price
FROM games_parquet
WHERE is_price_outlier = TRUE AND price >= 100.0 AND (num_reviews_total IS NULL OR num_reviews_total < 50)
ORDER BY price DESC
LIMIT 20;


-- ----------------------------------------------------------------------------
-- CÂU TRUY VẤN 10: CHIẾN LƯỢC ĐA NỀN TẢNG (MULTI-PLATFORM) & ĐỘ PHỔ BIẾN
-- Mục tiêu: So sánh mức độ thành công giữa game chỉ phát hành Windows vs Multi-platform
-- ----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN platform_count = 1 THEN 'Chỉ 1 nền tảng (Thường là Windows)'
        WHEN platform_count = 2 THEN '2 nền tảng (Windows + Mac/Linux)'
        WHEN platform_count = 3 THEN 'Toàn diện (Windows + Mac + Linux)'
    END AS platform_strategy,
    COUNT(*) AS total_games,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS strategy_pct,
    ROUND(AVG(price), 2) AS avg_price,
    ROUND(AVG(CASE WHEN pct_pos_total IS NOT NULL THEN pct_pos_total END), 2) AS avg_rating,
    ROUND(AVG(CASE WHEN num_reviews_total IS NOT NULL THEN num_reviews_total END), 0) AS avg_reviews
FROM games_parquet
GROUP BY platform_count
ORDER BY platform_count;
