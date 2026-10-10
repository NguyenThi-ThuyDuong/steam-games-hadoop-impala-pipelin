-- ============================================================================
-- APACHE IMPALA DDL STATEMENTS FOR DATA MINING PREPROCESSED STEAM DATASET
-- Database: steam_analytics_dm
-- Target Directory: D:\HocTap\HK1_27\BigData\DoAnBigData\datamining
-- ============================================================================

CREATE DATABASE IF NOT EXISTS steam_analytics_dm;
USE steam_analytics_dm;

-- ----------------------------------------------------------------------------
-- 1. EXTERNAL STAGING CSV TABLES
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS games_staging_csv;
CREATE EXTERNAL TABLE games_staging_csv (
    appid INT,
    name STRING,
    release_date STRING,
    release_year INT,
    price DOUBLE,
    price_category STRING,
    rating_category STRING,
    required_age INT,
    dlc_count INT,
    short_description STRING,
    windows BOOLEAN,
    mac BOOLEAN,
    linux BOOLEAN,
    platform_count INT,
    metacritic_score INT,
    has_metacritic BOOLEAN,
    achievements INT,
    recommendations INT,
    supported_languages STRING,
    positive INT,
    negative INT,
    total_reviews_calc INT,
    review_ratio DOUBLE,
    estimated_owners STRING,
    owners_lower BIGINT,
    owners_upper BIGINT,
    average_playtime_forever INT,
    median_playtime_forever INT,
    peak_ccu INT,
    pct_pos_total INT,
    num_reviews_total INT,
    pct_pos_recent INT,
    num_reviews_recent INT,
    game_age INT,
    is_free BOOLEAN,
    is_price_outlier BOOLEAN,
    is_reviews_outlier BOOLEAN,
    z_price DOUBLE,
    z_reviews DOUBLE
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/steam_analytics/datamining/raw_csv/games/'
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS games_genres_csv;
CREATE EXTERNAL TABLE games_genres_csv (
    appid INT,
    genre STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/steam_analytics/datamining/raw_csv/genres/'
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS games_tags_csv;
CREATE EXTERNAL TABLE games_tags_csv (
    appid INT,
    tag STRING,
    count INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/steam_analytics/datamining/raw_csv/tags/'
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS games_developers_csv;
CREATE EXTERNAL TABLE games_developers_csv (
    appid INT,
    developer STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/steam_analytics/datamining/raw_csv/developers/'
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS games_publishers_csv;
CREATE EXTERNAL TABLE games_publishers_csv (
    appid INT,
    publisher STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/steam_analytics/datamining/raw_csv/publishers/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- ----------------------------------------------------------------------------
-- 2. PARQUET FACT & DIMENSION TABLES (OPTIMIZED COLUMNAR WITH PARTITIONING)
-- ----------------------------------------------------------------------------

-- Main Fact Table: games_parquet (Partitioned by release_year for Partition Pruning)
DROP TABLE IF EXISTS games_parquet;
CREATE TABLE games_parquet (
    appid INT,
    name STRING,
    release_date STRING,
    price DOUBLE,
    price_category STRING,
    rating_category STRING,
    required_age INT,
    dlc_count INT,
    short_description STRING,
    windows BOOLEAN,
    mac BOOLEAN,
    linux BOOLEAN,
    platform_count INT,
    metacritic_score INT,
    has_metacritic BOOLEAN,
    achievements INT,
    recommendations INT,
    supported_languages STRING,
    positive INT,
    negative INT,
    total_reviews_calc INT,
    review_ratio DOUBLE,
    estimated_owners STRING,
    owners_lower BIGINT,
    owners_upper BIGINT,
    average_playtime_forever INT,
    median_playtime_forever INT,
    peak_ccu INT,
    pct_pos_total INT,
    num_reviews_total INT,
    pct_pos_recent INT,
    num_reviews_recent INT,
    game_age INT,
    is_free BOOLEAN,
    is_price_outlier BOOLEAN,
    is_reviews_outlier BOOLEAN,
    z_price DOUBLE,
    z_reviews DOUBLE
)
PARTITIONED BY (release_year INT)
STORED AS PARQUET;

-- Dimension Tables: Stored as Parquet with Snappy Compression
DROP TABLE IF EXISTS games_genres;
CREATE TABLE games_genres (
    appid INT,
    genre STRING
)
STORED AS PARQUET;

DROP TABLE IF EXISTS games_tags;
CREATE TABLE games_tags (
    appid INT,
    tag STRING,
    count INT
)
STORED AS PARQUET;

DROP TABLE IF EXISTS games_developers;
CREATE TABLE games_developers (
    appid INT,
    developer STRING
)
STORED AS PARQUET;

DROP TABLE IF EXISTS games_publishers;
CREATE TABLE games_publishers (
    appid INT,
    publisher STRING
)
STORED AS PARQUET;

-- ----------------------------------------------------------------------------
-- 3. LOAD DATA FROM STAGING TO PARQUET TABLES
-- ----------------------------------------------------------------------------

-- Dynamic Partition Insertion for games_parquet
-- Impala evaluates release_year dynamically from select list
INSERT OVERWRITE TABLE games_parquet PARTITION (release_year)
SELECT 
    appid, name, release_date, price, price_category, rating_category,
    required_age, dlc_count, short_description, windows, mac, linux,
    platform_count, metacritic_score, has_metacritic, achievements,
    recommendations, supported_languages, positive, negative,
    total_reviews_calc, review_ratio, estimated_owners, owners_lower,
    owners_upper, average_playtime_forever, median_playtime_forever,
    peak_ccu, pct_pos_total, num_reviews_total, pct_pos_recent,
    num_reviews_recent, game_age, is_free, is_price_outlier,
    is_reviews_outlier, z_price, z_reviews, release_year
FROM games_staging_csv;

-- Populate Dimension Tables
INSERT OVERWRITE TABLE games_genres SELECT * FROM games_genres_csv;
INSERT OVERWRITE TABLE games_tags SELECT * FROM games_tags_csv;
INSERT OVERWRITE TABLE games_developers SELECT * FROM games_developers_csv;
INSERT OVERWRITE TABLE games_publishers SELECT * FROM games_publishers_csv;

-- Compute statistics for query cost-based optimizer (CBO)
COMPUTE STATS games_parquet;
COMPUTE STATS games_genres;
COMPUTE STATS games_tags;
COMPUTE STATS games_developers;
COMPUTE STATS games_publishers;
