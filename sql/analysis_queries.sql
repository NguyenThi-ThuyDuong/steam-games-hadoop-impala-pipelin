-- ============================================================================
-- APACHE IMPALA ANALYTICAL SQL QUERIES (RQ1 TO RQ5)
-- ============================================================================

USE steam_analytics;

-- ----------------------------------------------------------------------------
-- RQ1. MARKET TRENDS OVER TIME
-- ----------------------------------------------------------------------------

-- Q1: Annual game releases count
SELECT release_year, COUNT(*) AS total_games
FROM games_parquet
WHERE release_year >= 1997 AND release_year <= 2025
GROUP BY release_year
ORDER BY release_year;

-- Q2: Year-over-Year Growth Rate
WITH yearly_stats AS (
    SELECT release_year, COUNT(*) AS game_count
    FROM games_parquet
    WHERE release_year >= 2005 AND release_year <= 2025
    GROUP BY release_year
)
SELECT 
    release_year,
    game_count,
    game_count - LAG(game_count, 1) OVER (ORDER BY release_year) AS yoy_growth,
    ROUND((game_count - LAG(game_count, 1) OVER (ORDER BY release_year)) * 100.0 / 
          NULLIF(LAG(game_count, 1) OVER (ORDER BY release_year), 0), 2) AS yoy_growth_pct
FROM yearly_stats
ORDER BY release_year;

-- Q3: Top Genres by Era / Period
SELECT 
    CASE 
        WHEN g.release_year BETWEEN 2000 AND 2009 THEN '2000-2009'
        WHEN g.release_year BETWEEN 2010 AND 2014 THEN '2010-2014'
        WHEN g.release_year BETWEEN 2015 AND 2019 THEN '2015-2019'
        WHEN g.release_year >= 2020 THEN '2020-2025'
    END AS period,
    gg.genre,
    COUNT(*) AS game_count
FROM games_parquet g
JOIN games_genres gg ON g.appid = gg.appid
WHERE g.release_year >= 2000
GROUP BY 1, gg.genre
ORDER BY period, game_count DESC;

-- Q4: Price evolution and Free vs Paid proportion over years
SELECT 
    release_year,
    ROUND(AVG(price), 2) AS avg_price,
    ROUND(STDDEV(price), 2) AS std_price,
    COUNT(CASE WHEN price = 0 THEN 1 END) AS free_games,
    COUNT(CASE WHEN price > 0 THEN 1 END) AS paid_games,
    ROUND(COUNT(CASE WHEN price = 0 THEN 1 END) * 100.0 / COUNT(*), 2) AS free_pct
FROM games_parquet
WHERE release_year BETWEEN 2005 AND 2025
GROUP BY release_year
ORDER BY release_year;


-- ----------------------------------------------------------------------------
-- RQ2. GENRE ANALYSIS
-- ----------------------------------------------------------------------------

-- Q5: Comprehensive Genre Profile
SELECT 
    gg.genre,
    COUNT(DISTINCT g.appid) AS total_games,
    ROUND(AVG(g.price), 2) AS avg_price,
    ROUND(AVG(g.pct_pos_total), 2) AS avg_positive_rating,
    ROUND(AVG(g.num_reviews_total), 0) AS avg_reviews_count,
    ROUND(AVG(g.average_playtime_forever), 0) AS avg_playtime_minutes,
    ROUND(AVG(g.peak_ccu), 0) AS avg_peak_concurrent_users
FROM games_parquet g
JOIN games_genres gg ON g.appid = gg.appid
GROUP BY gg.genre
HAVING COUNT(DISTINCT g.appid) >= 50
ORDER BY total_games DESC;

-- Q6: Genre performance across price groups
SELECT 
    g.price_group,
    gg.genre,
    COUNT(*) AS game_count,
    ROUND(AVG(g.pct_pos_total), 2) AS avg_rating
FROM games_parquet g
JOIN games_genres gg ON g.appid = gg.appid
GROUP BY g.price_group, gg.genre
ORDER BY g.price_group, game_count DESC;


-- ----------------------------------------------------------------------------
-- RQ3. PRICE VS FEEDBACK & ENGAGEMENT
-- ----------------------------------------------------------------------------

-- Q7: Price Group metrics summary
SELECT 
    price_group,
    COUNT(*) AS total_games,
    ROUND(AVG(num_reviews_total), 0) AS avg_reviews,
    ROUND(AVG(pct_pos_total), 2) AS avg_positive_pct,
    ROUND(AVG(average_playtime_forever), 0) AS avg_playtime,
    ROUND(AVG(peak_ccu), 0) AS avg_peak_ccu
FROM games_parquet
GROUP BY price_group
ORDER BY 
    CASE price_group
        WHEN 'Free' THEN 1
        WHEN '0-5' THEN 2
        WHEN '5-15' THEN 3
        WHEN '15-30' THEN 4
        WHEN '30-60' THEN 5
        WHEN '60+' THEN 6
        ELSE 7
    END;


-- ----------------------------------------------------------------------------
-- RQ4. ANOMALY DETECTION (OUTLIERS)
-- ----------------------------------------------------------------------------

-- Q9: Cheap / Free Games with Huge Review Volume
SELECT appid, name, price, num_reviews_total, pct_pos_total, peak_ccu
FROM games_parquet
WHERE price <= 5.0 AND num_reviews_total > 50000
ORDER BY num_reviews_total DESC
LIMIT 50;

-- Q10: High Price Games with Very Low Review Count
SELECT appid, name, price, num_reviews_total, pct_pos_total
FROM games_parquet
WHERE price >= 40.0 AND num_reviews_total < 100
ORDER BY price DESC
LIMIT 50;

-- Q11: Extremely High Positive Rating (Over 95%) with Moderate Reviews
SELECT appid, name, price, pct_pos_total, num_reviews_total
FROM games_parquet
WHERE pct_pos_total >= 98 AND num_reviews_total BETWEEN 50 AND 500
ORDER BY num_reviews_total DESC;

-- Q12: Statistical Outliers using Standard Deviation Z-Score
WITH stats AS (
    SELECT 
        AVG(num_reviews_total) AS mean_rev,
        STDDEV(num_reviews_total) AS std_rev,
        AVG(price) AS mean_price,
        STDDEV(price) AS std_price
    FROM games_parquet
    WHERE num_reviews_total > 0
)
SELECT 
    g.appid, g.name, g.price, g.num_reviews_total,
    ROUND((g.num_reviews_total - s.mean_rev) / s.std_rev, 2) AS z_reviews,
    ROUND((g.price - s.mean_price) / s.std_price, 2) AS z_price
FROM games_parquet g, stats s
WHERE ABS((g.num_reviews_total - s.mean_rev) / s.std_rev) > 4
   OR ABS((g.price - s.mean_price) / s.std_price) > 4
ORDER BY z_reviews DESC
LIMIT 100;


-- ----------------------------------------------------------------------------
-- RQ5. COMBINED METADATA & REVIEWS ANALYSIS
-- ----------------------------------------------------------------------------

-- Q13: Game Metadata combined with aggregated Review level details
SELECT 
    g.appid,
    g.name,
    g.price,
    g.price_group,
    g.pct_pos_total AS store_rating,
    COUNT(r.steamid) AS sample_review_count,
    ROUND(AVG(r.playtime_at_review), 0) AS avg_playtime_at_review_min,
    ROUND(AVG(r.playtime_forever), 0) AS avg_total_playtime_min,
    ROUND(SUM(CASE WHEN r.voted_up THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS actual_positive_pct,
    ROUND(AVG(r.review_length), 0) AS avg_review_text_len
FROM games_parquet g
JOIN reviews_parquet r ON g.appid = r.appid
GROUP BY g.appid, g.name, g.price, g.price_group, g.pct_pos_total
HAVING COUNT(r.steamid) >= 100
ORDER BY sample_review_count DESC
LIMIT 50;

-- Q14: Sentiment Evolution over Time for Top Games
SELECT 
    g.name,
    r.review_year,
    COUNT(*) AS yearly_reviews,
    ROUND(SUM(CASE WHEN r.voted_up THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS positive_pct
FROM games_parquet g
JOIN reviews_parquet r ON g.appid = r.appid
WHERE g.appid IN (578080, 730, 1086940, 271590, 105600) -- PUBG, CS:GO/2, Baldur's Gate 3, GTA V, Terraria
GROUP BY g.name, r.review_year
ORDER BY g.name, r.review_year;

-- Q15: Player Engagement & Loyalty by Game Price Group
SELECT 
    g.price_group,
    COUNT(DISTINCT r.steamid) AS total_reviewers,
    ROUND(AVG(r.num_games_owned), 0) AS avg_games_owned_by_reviewer,
    ROUND(AVG(r.num_reviews), 0) AS avg_reviews_written_by_reviewer,
    ROUND(AVG(r.playtime_at_review), 0) AS avg_playtime_at_review,
    ROUND(AVG(r.review_length), 0) AS avg_review_length
FROM games_parquet g
JOIN reviews_parquet r ON g.appid = r.appid
GROUP BY g.price_group
ORDER BY 
    CASE g.price_group
        WHEN 'Free' THEN 1
        WHEN '0-5' THEN 2
        WHEN '5-15' THEN 3
        WHEN '15-30' THEN 4
        WHEN '30-60' THEN 5
        WHEN '60+' THEN 6
        ELSE 7
    END;
