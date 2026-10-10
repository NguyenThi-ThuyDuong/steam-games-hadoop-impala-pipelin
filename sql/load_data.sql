-- ============================================================================
-- APACHE IMPALA DML & DATA LOADING STATEMENTS
-- ============================================================================

USE steam_analytics;

-- Enable dynamic partitioning
SET DYNAMIC_PARTITIONING = true;
SET COMPRESSION_CODEC = snappy;

-- 1. Load games data into Parquet Partitioned Table
INSERT OVERWRITE TABLE games_parquet PARTITION (release_year)
SELECT 
    appid, name, release_date, price, price_group, required_age, dlc_count,
    short_description, windows, mac, linux, metacritic_score, achievements,
    recommendations, supported_languages, positive, negative,
    estimated_owners, average_playtime_forever, average_playtime_2weeks,
    median_playtime_forever, median_playtime_2weeks, peak_ccu,
    pct_pos_total, num_reviews_total, pct_pos_recent, num_reviews_recent,
    release_year
FROM games_csv;

-- 2. Load reviews data into Parquet Partitioned Table
INSERT OVERWRITE TABLE reviews_parquet PARTITION (review_year)
SELECT 
    steamid, appid, voted_up, votes_up, votes_funny, weighted_vote_score,
    playtime_forever, playtime_at_review, num_games_owned, num_reviews,
    review_length, review_date, review_month, review_year
FROM reviews_csv;

-- 3. Load genres and tags dimension tables
INSERT OVERWRITE TABLE games_genres SELECT * FROM games_genres_csv;
INSERT OVERWRITE TABLE games_tags SELECT * FROM games_tags_csv;

-- 4. Compute Statistics for Impala Query Optimization
COMPUTE STATS games_parquet;
COMPUTE STATS reviews_parquet;
COMPUTE STATS games_parquet_nopart;
COMPUTE STATS reviews_parquet_nopart;
COMPUTE STATS games_genres;
COMPUTE STATS games_tags;
COMPUTE STATS games_csv;
COMPUTE STATS reviews_csv;
