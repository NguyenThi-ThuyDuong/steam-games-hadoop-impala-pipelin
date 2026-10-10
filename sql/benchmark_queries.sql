-- ============================================================================
-- APACHE IMPALA BENCHMARK EXPERIMENTS (RQ6 & RQ7)
-- ============================================================================

USE steam_analytics;

-- ----------------------------------------------------------------------------
-- EXPERIMENT 1: CSV VS PARQUET FILE FORMAT PERFORMANCE
-- ----------------------------------------------------------------------------

-- Query 1.1: Aggregation on Games (CSV)
EXPLAIN SELECT release_year, COUNT(*), AVG(price) 
FROM games_csv GROUP BY release_year;

SELECT release_year, COUNT(*), AVG(price) 
FROM games_csv GROUP BY release_year;

SUMMARY;

-- Query 1.2: Aggregation on Games (Parquet)
EXPLAIN SELECT release_year, COUNT(*), AVG(price) 
FROM games_parquet GROUP BY release_year;

SELECT release_year, COUNT(*), AVG(price) 
FROM games_parquet GROUP BY release_year;

SUMMARY;

-- Query 1.3: Filter & Aggregation on Reviews (CSV)
EXPLAIN SELECT appid, COUNT(*), AVG(playtime_forever) 
FROM reviews_csv WHERE appid = 578080 GROUP BY appid;

SELECT appid, COUNT(*), AVG(playtime_forever) 
FROM reviews_csv WHERE appid = 578080 GROUP BY appid;

SUMMARY;

-- Query 1.4: Filter & Aggregation on Reviews (Parquet)
EXPLAIN SELECT appid, COUNT(*), AVG(playtime_forever) 
FROM reviews_parquet WHERE appid = 578080 GROUP BY appid;

SELECT appid, COUNT(*), AVG(playtime_forever) 
FROM reviews_parquet WHERE appid = 578080 GROUP BY appid;

SUMMARY;


-- ----------------------------------------------------------------------------
-- EXPERIMENT 2: PARTITIONING IMPACT (PARTITION PRUNING)
-- ----------------------------------------------------------------------------

-- Query 2.1: Partitioned Table (Specific Year Filter)
EXPLAIN SELECT release_year, COUNT(*), AVG(price) 
FROM games_parquet WHERE release_year = 2023 GROUP BY release_year;

SELECT release_year, COUNT(*), AVG(price) 
FROM games_parquet WHERE release_year = 2023 GROUP BY release_year;

SUMMARY;

-- Query 2.2: Non-Partitioned Table (Specific Year Filter)
EXPLAIN SELECT release_year, COUNT(*), AVG(price) 
FROM games_parquet_nopart WHERE release_year = 2023 GROUP BY release_year;

SELECT release_year, COUNT(*), AVG(price) 
FROM games_parquet_nopart WHERE release_year = 2023 GROUP BY release_year;

SUMMARY;

-- Query 2.3: Partitioned Reviews Table (Specific Review Year)
EXPLAIN SELECT review_year, COUNT(*), AVG(playtime_forever) 
FROM reviews_parquet WHERE review_year = 2023 GROUP BY review_year;

SELECT review_year, COUNT(*), AVG(playtime_forever) 
FROM reviews_parquet WHERE review_year = 2023 GROUP BY review_year;

SUMMARY;

-- Query 2.4: Non-Partitioned Reviews Table (Specific Review Year)
EXPLAIN SELECT review_year, COUNT(*), AVG(playtime_forever) 
FROM reviews_parquet_nopart WHERE review_year = 2023 GROUP BY review_year;

SELECT review_year, COUNT(*), AVG(playtime_forever) 
FROM reviews_parquet_nopart WHERE review_year = 2023 GROUP BY review_year;

SUMMARY;


-- ----------------------------------------------------------------------------
-- EXPERIMENT 3: COMPUTE STATISTICS IMPACT (JOIN OPTIMIZATION)
-- ----------------------------------------------------------------------------

-- Step 3.1: Drop Stats to test unoptimized query execution
DROP STATS games_parquet;
DROP STATS reviews_parquet;

EXPLAIN SELECT g.price_group, COUNT(r.steamid) AS total_reviews, AVG(r.playtime_forever) AS avg_playtime
FROM games_parquet g
JOIN reviews_parquet r ON g.appid = r.appid
GROUP BY g.price_group;

SELECT g.price_group, COUNT(r.steamid) AS total_reviews, AVG(r.playtime_forever) AS avg_playtime
FROM games_parquet g
JOIN reviews_parquet r ON g.appid = r.appid
GROUP BY g.price_group;

SUMMARY;

-- Step 3.2: Re-compute Stats and compare plan & execution time
COMPUTE STATS games_parquet;
COMPUTE STATS reviews_parquet;

EXPLAIN SELECT g.price_group, COUNT(r.steamid) AS total_reviews, AVG(r.playtime_forever) AS avg_playtime
FROM games_parquet g
JOIN reviews_parquet r ON g.appid = r.appid
GROUP BY g.price_group;

SELECT g.price_group, COUNT(r.steamid) AS total_reviews, AVG(r.playtime_forever) AS avg_playtime
FROM games_parquet g
JOIN reviews_parquet r ON g.appid = r.appid
GROUP BY g.price_group;

SUMMARY;


-- ----------------------------------------------------------------------------
-- EXPERIMENT 4: LARGE-SCALE JOIN EXECUTION (GAMES X REVIEWS)
-- ----------------------------------------------------------------------------

EXPLAIN SELECT g.name, gg.genre, COUNT(r.steamid) AS review_count, AVG(r.playtime_at_review) AS avg_playtime
FROM games_parquet g
JOIN games_genres gg ON g.appid = gg.appid
JOIN reviews_parquet r ON g.appid = r.appid
WHERE g.release_year >= 2020
GROUP BY g.name, gg.genre
ORDER BY review_count DESC
LIMIT 50;

SELECT g.name, gg.genre, COUNT(r.steamid) AS review_count, AVG(r.playtime_at_review) AS avg_playtime
FROM games_parquet g
JOIN games_genres gg ON g.appid = gg.appid
JOIN reviews_parquet r ON g.appid = r.appid
WHERE g.release_year >= 2020
GROUP BY g.name, gg.genre
ORDER BY review_count DESC
LIMIT 50;

SUMMARY;


-- ----------------------------------------------------------------------------
-- EXPERIMENT 5: SCALABILITY BENCHMARK (10%, 25%, 50%, 75%, 100% DATA VOLUME)
-- ----------------------------------------------------------------------------

-- Sub-experiment queries on sample datasets
-- Query run on 10% sample
SELECT appid, COUNT(*), AVG(playtime_forever), SUM(CASE WHEN voted_up THEN 1 ELSE 0 END)
FROM reviews_parquet TABLESAMPLE SYSTEM(10)
GROUP BY appid;

-- Query run on 25% sample
SELECT appid, COUNT(*), AVG(playtime_forever), SUM(CASE WHEN voted_up THEN 1 ELSE 0 END)
FROM reviews_parquet TABLESAMPLE SYSTEM(25)
GROUP BY appid;

-- Query run on 50% sample
SELECT appid, COUNT(*), AVG(playtime_forever), SUM(CASE WHEN voted_up THEN 1 ELSE 0 END)
FROM reviews_parquet TABLESAMPLE SYSTEM(50)
GROUP BY appid;

-- Query run on 75% sample
SELECT appid, COUNT(*), AVG(playtime_forever), SUM(CASE WHEN voted_up THEN 1 ELSE 0 END)
FROM reviews_parquet TABLESAMPLE SYSTEM(75)
GROUP BY appid;

-- Query run on 100% full dataset
SELECT appid, COUNT(*), AVG(playtime_forever), SUM(CASE WHEN voted_up THEN 1 ELSE 0 END)
FROM reviews_parquet
GROUP BY appid;
