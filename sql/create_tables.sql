-- ============================================================================
-- APACHE IMPALA DDL STATEMENTS FOR STEAM GAME DATA ANALYSIS
-- ============================================================================

CREATE DATABASE IF NOT EXISTS steam_analytics;
USE steam_analytics;

-- ----------------------------------------------------------------------------
-- 1. EXTERNAL CSV TABLES (STAGING / RAW DATA)
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS games_csv;
CREATE EXTERNAL TABLE games_csv (
    appid INT,
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
LOCATION '/user/steam_analytics/raw/games/'
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS reviews_csv;
CREATE EXTERNAL TABLE reviews_csv (
    steamid BIGINT,
    appid INT,
    voted_up BOOLEAN,
    votes_up INT,
    votes_funny INT,
    weighted_vote_score DOUBLE,
    playtime_forever INT,
    playtime_at_review INT,
    num_games_owned INT,
    num_reviews INT,
    review_length INT,
    review_date STRING,
    review_year INT,
    review_month INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/steam_analytics/raw/reviews/'
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS games_genres_csv;
CREATE EXTERNAL TABLE games_genres_csv (
    appid INT,
    genre STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/steam_analytics/raw/games_genres/'
TBLPROPERTIES ('skip.header.line.count'='1');

DROP TABLE IF EXISTS games_tags_csv;
CREATE EXTERNAL TABLE games_tags_csv (
    appid INT,
    tag STRING,
    count INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/steam_analytics/raw/games_tags/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- ----------------------------------------------------------------------------
-- 2. PARQUET TABLES WITH PARTITIONING (OPTIMIZED FOR ANALYTICS)
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS games_parquet;
CREATE TABLE games_parquet (
    appid INT,
    name STRING,
    release_date STRING,
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
PARTITIONED BY (release_year INT)
STORED AS PARQUET;

DROP TABLE IF EXISTS reviews_parquet;
CREATE TABLE reviews_parquet (
    steamid BIGINT,
    appid INT,
    voted_up BOOLEAN,
    votes_up INT,
    votes_funny INT,
    weighted_vote_score DOUBLE,
    playtime_forever INT,
    playtime_at_review INT,
    num_games_owned INT,
    num_reviews INT,
    review_length INT,
    review_date STRING,
    review_month INT
)
PARTITIONED BY (review_year INT)
STORED AS PARQUET;

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

-- ----------------------------------------------------------------------------
-- 3. PARQUET TABLES WITHOUT PARTITIONING (FOR BENCHMARK EXP 2)
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS games_parquet_nopart;
CREATE TABLE games_parquet_nopart STORED AS PARQUET AS
SELECT * FROM games_csv;

DROP TABLE IF EXISTS reviews_parquet_nopart;
CREATE TABLE reviews_parquet_nopart STORED AS PARQUET AS
SELECT * FROM reviews_csv;
