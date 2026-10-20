import pymysql
import pandas as pd
import time
import os

print("Waiting for MySQL connection...")
connected = False
for i in range(30):
    try:
        conn = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="rootpassword",
            autocommit=True
        )
        connected = True
        break
    except Exception as e:
        time.sleep(2)

if not connected:
    print("Could not connect to MySQL server within 60s.")
    exit(1)

print("MySQL connected successfully!")
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS steam_analytics;")
cursor.execute("USE steam_analytics;")

print("Creating tables in MySQL...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS games (
    appid INT PRIMARY KEY,
    name VARCHAR(255),
    release_date VARCHAR(50),
    release_year INT,
    price DOUBLE,
    price_group VARCHAR(50),
    required_age INT,
    dlc_count INT,
    metacritic_score INT,
    achievements INT,
    recommendations INT,
    positive INT,
    negative INT,
    average_playtime_forever INT,
    peak_ccu INT,
    pct_pos_total DOUBLE,
    num_reviews_total INT,
    INDEX (release_year),
    INDEX (price_group)
) ENGINE=InnoDB;
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS games_genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appid INT,
    genre VARCHAR(100),
    INDEX (appid),
    INDEX (genre)
) ENGINE=InnoDB;
""")

print("Loading games dataset into MySQL...")
df_games = pd.read_csv("/Users/hochidung/Documents/1_monhoc/BigData/DoAnBigData/data/processed/games_cleaned.csv")
cols = ['appid', 'name', 'release_date', 'release_year', 'price', 'price_group', 'required_age', 'dlc_count', 
        'metacritic_score', 'achievements', 'recommendations', 'positive', 'negative', 
        'average_playtime_forever', 'peak_ccu', 'pct_pos_total', 'num_reviews_total']
df_sub = df_games[[c for c in cols if c in df_games.columns]].fillna({
    'name': '', 'release_date': '', 'price_group': '', 'price': 0.0, 'pct_pos_total': 0.0
}).fillna(0)

cursor.execute("SELECT COUNT(*) FROM games;")
count_games = cursor.fetchone()[0]
if count_games < len(df_sub):
    print(f"Inserting {len(df_sub)} rows into MySQL games table...")
    tuples = [tuple(x) for x in df_sub.to_numpy()]
    insert_sql = """
    INSERT IGNORE INTO games (appid, name, release_date, release_year, price, price_group, required_age, dlc_count, 
                       metacritic_score, achievements, recommendations, positive, negative, 
                       average_playtime_forever, peak_ccu, pct_pos_total, num_reviews_total)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    batch_size = 5000
    for i in range(0, len(tuples), batch_size):
        cursor.executemany(insert_sql, tuples[i:i+batch_size])
    print("Games table populated!")
else:
    print(f"Games table already populated with {count_games} rows.")

print("Loading games_genres dataset into MySQL...")
df_genres = pd.read_csv("/Users/hochidung/Documents/1_monhoc/BigData/DoAnBigData/data/processed/games_genres.csv")
cursor.execute("SELECT COUNT(*) FROM games_genres;")
count_genres = cursor.fetchone()[0]
if count_genres < len(df_genres):
    print(f"Inserting {len(df_genres)} rows into MySQL games_genres table...")
    g_tuples = [tuple(x) for x in df_genres[['appid', 'genre']].to_numpy()]
    insert_g_sql = "INSERT INTO games_genres (appid, genre) VALUES (%s, %s)"
    batch_size = 10000
    for i in range(0, len(g_tuples), batch_size):
        cursor.executemany(insert_g_sql, g_tuples[i:i+batch_size])
    print("Games_genres table populated!")
else:
    print(f"Games_genres table already populated with {count_genres} rows.")

# Verify query BQ1
t0 = time.perf_counter()
cursor.execute("SELECT release_year, COUNT(*) AS total_games, ROUND(AVG(price), 2) AS avg_price FROM games WHERE release_year >= 1997 AND release_year <= 2025 GROUP BY release_year ORDER BY release_year DESC;")
res = cursor.fetchall()
t_dur = time.perf_counter() - t0
print(f"MySQL BQ1 verified! Fetched {len(res)} rows in {t_dur:.3f}s")
conn.close()
