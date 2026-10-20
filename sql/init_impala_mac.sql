-- ============================================================================
-- KHỞI TẠO BẢNG IMPALA TRỎ VÀO PARQUET V1.0 ĐÃ CHUẨN HÓA
-- Database: steam_analytics
-- ============================================================================

CREATE DATABASE IF NOT EXISTS steam_analytics;
USE steam_analytics;

-- 1. BẢNG FACT PARQUET CÓ PHÂN VÙNG (PARTITIONED BY release_year)
DROP TABLE IF EXISTS games_parquet;
CREATE EXTERNAL TABLE games_parquet LIKE PARQUET '/data/data/parquet_v1/games_parquet/release_year=2024/10db895631eb494a9cf17eefa917c7b7-0.parquet'
PARTITIONED BY (release_year INT)
STORED AS PARQUET
LOCATION '/data/data/parquet_v1/games_parquet';

ALTER TABLE games_parquet RECOVER PARTITIONS;

-- 2. CÁC BẢNG DIMENSION PARQUET
DROP TABLE IF EXISTS games_genres;
CREATE EXTERNAL TABLE games_genres LIKE PARQUET '/data/data/parquet_v1/dim_genres/games_genres.parquet'
STORED AS PARQUET
LOCATION '/data/data/parquet_v1/dim_genres';

DROP TABLE IF EXISTS games_tags;
CREATE EXTERNAL TABLE games_tags LIKE PARQUET '/data/data/parquet_v1/dim_tags/games_tags.parquet'
STORED AS PARQUET
LOCATION '/data/data/parquet_v1/dim_tags';

DROP TABLE IF EXISTS games_developers;
CREATE EXTERNAL TABLE games_developers LIKE PARQUET '/data/data/parquet_v1/dim_developers/games_developers.parquet'
STORED AS PARQUET
LOCATION '/data/data/parquet_v1/dim_developers';

DROP TABLE IF EXISTS games_publishers;
CREATE EXTERNAL TABLE games_publishers LIKE PARQUET '/data/data/parquet_v1/dim_publishers/games_publishers.parquet'
STORED AS PARQUET
LOCATION '/data/data/parquet_v1/dim_publishers';

-- 3. BẢNG PARQUET KHÔNG PHÂN VÙNG (PHỤC VỤ BENCHMARK)
DROP TABLE IF EXISTS games_parquet_nopart;
CREATE EXTERNAL TABLE games_parquet_nopart LIKE PARQUET '/data/data/parquet_v1/games_nopart/games_nopart.parquet'
STORED AS PARQUET
LOCATION '/data/data/parquet_v1/games_nopart';

-- 4. BẢNG CSV TEXTFILE (PHỤC VỤ SO SÁNH BENCHMARK)
DROP TABLE IF EXISTS games_csv;
CREATE EXTERNAL TABLE games_csv (
    appid BIGINT,
    name STRING,
    release_date STRING,
    release_year INT,
    price DOUBLE,
    price_group STRING,
    required_age INT,
    dlc_count INT,
    short_description STRING,
    windows BOOLEAN,
    mac BOOLEAN,
    linux BOOLEAN,
    metacritic_score INT,
    achievements INT,
    recommendations INT,
    supported_languages STRING,
    positive INT,
    negative INT,
    estimated_owners STRING,
    average_playtime_forever INT,
    average_playtime_2weeks INT,
    median_playtime_forever INT,
    median_playtime_2weeks INT,
    peak_ccu INT,
    pct_pos_total INT,
    num_reviews_total INT,
    pct_pos_recent INT,
    num_reviews_recent INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/data/processed/csv_games'
TBLPROPERTIES ('skip.header.line.count'='1');

-- 5. THỰC HIỆN COMPUTE STATS TỐI ƯU CBO
COMPUTE STATS games_parquet;
COMPUTE STATS games_genres;
COMPUTE STATS games_tags;
COMPUTE STATS games_developers;
COMPUTE STATS games_publishers;
COMPUTE STATS games_parquet_nopart;
COMPUTE STATS games_csv;

-- 6. KIỂM TRA TỔNG SỐ LƯỢNG BẢN GHI
SELECT 'games_parquet' AS table_name, COUNT(*) AS total_rows FROM games_parquet
UNION ALL
SELECT 'games_genres' AS table_name, COUNT(*) AS total_rows FROM games_genres
UNION ALL
SELECT 'games_tags' AS table_name, COUNT(*) AS total_rows FROM games_tags
UNION ALL
SELECT 'games_parquet_nopart' AS table_name, COUNT(*) AS total_rows FROM games_parquet_nopart
UNION ALL
SELECT 'games_csv' AS table_name, COUNT(*) AS total_rows FROM games_csv;
