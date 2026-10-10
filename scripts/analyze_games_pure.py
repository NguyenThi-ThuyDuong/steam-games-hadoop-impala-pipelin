import csv
import os
from collections import defaultdict

GAMES_FILE = r"D:\HocTap\HK1_27\BigData\DoAnBigData\data\processed\games_cleaned.csv"
GENRES_FILE = r"D:\HocTap\HK1_27\BigData\DoAnBigData\data\processed\games_genres.csv"
RESULTS_DIR = r"D:\HocTap\HK1_27\BigData\DoAnBigData\results\analysis"

os.makedirs(RESULTS_DIR, exist_ok=True)

print("Running pure Python analysis on Games dataset...")

# Load Games
games = []
with open(GAMES_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            row['appid'] = int(row['appid'])
            row['release_year'] = int(row['release_year'])
            row['price'] = float(row['price'])
            row['pct_pos_total'] = int(float(row['pct_pos_total'] or "0"))
            row['num_reviews_total'] = int(float(row['num_reviews_total'] or "0"))
            row['average_playtime_forever'] = int(float(row['average_playtime_forever'] or "0"))
            row['peak_ccu'] = int(float(row['peak_ccu'] or "0"))
            games.append(row)
        except Exception:
            continue

print(f"Loaded {len(games):,} valid games.")

# Load Genres
genres = defaultdict(list)
with open(GENRES_FILE, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            genres[int(row['appid'])].append(row['genre'])
        except Exception:
            continue

# -----------------------------------------------------------------------------
# 1. RQ1: Yearly Releases & Prices
# -----------------------------------------------------------------------------
yearly = defaultdict(lambda: {'count': 0, 'prices': [], 'free': 0})
for g in games:
    yr = g['release_year']
    if 2000 <= yr <= 2024:
        yearly[yr]['count'] += 1
        yearly[yr]['prices'].append(g['price'])
        if g['price'] == 0:
            yearly[yr]['free'] += 1

rq1_rows = []
prev_count = None
for yr in sorted(yearly.keys()):
    cnt = yearly[yr]['count']
    prices = yearly[yr]['prices']
    avg_price = sum(prices) / len(prices) if prices else 0
    free_cnt = yearly[yr]['free']
    free_pct = (free_cnt / cnt * 100) if cnt > 0 else 0
    
    growth = (cnt - prev_count) if prev_count is not None else 0
    growth_pct = (growth / prev_count * 100) if prev_count and prev_count > 0 else 0
    prev_count = cnt
    
    rq1_rows.append([yr, cnt, round(growth, 2), round(growth_pct, 2), round(avg_price, 2), free_cnt, round(free_pct, 2)])

with open(os.path.join(RESULTS_DIR, "rq1_yearly_summary.csv"), 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["release_year", "total_games", "yoy_growth", "yoy_growth_pct", "avg_price", "free_games", "free_pct"])
    writer.writerows(rq1_rows)

print("Saved rq1_yearly_summary.csv")

# -----------------------------------------------------------------------------
# 2. RQ2: Genre Analysis
# -----------------------------------------------------------------------------
genre_stats = defaultdict(lambda: {'games': set(), 'prices': [], 'ratings': [], 'reviews': [], 'playtime': []})

for g in games:
    appid = g['appid']
    for gen in genres.get(appid, []):
        genre_stats[gen]['games'].add(appid)
        genre_stats[gen]['prices'].append(g['price'])
        if g['pct_pos_total'] > 0:
            genre_stats[gen]['ratings'].append(g['pct_pos_total'])
        genre_stats[gen]['reviews'].append(g['num_reviews_total'])
        genre_stats[gen]['playtime'].append(g['average_playtime_forever'])

rq2_rows = []
for gen, data in genre_stats.items():
    cnt = len(data['games'])
    avg_p = sum(data['prices']) / len(data['prices']) if data['prices'] else 0
    avg_r = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else 0
    avg_rev = sum(data['reviews']) / len(data['reviews']) if data['reviews'] else 0
    avg_play = sum(data['playtime']) / len(data['playtime']) if data['playtime'] else 0
    rq2_rows.append([gen, cnt, round(avg_p, 2), round(avg_r, 2), round(avg_rev, 0), round(avg_play, 0)])

rq2_rows.sort(key=lambda x: x[1], reverse=True)

with open(os.path.join(RESULTS_DIR, "rq2_genre_summary.csv"), 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["genre", "total_games", "avg_price", "avg_positive_rating", "avg_reviews", "avg_playtime_min"])
    writer.writerows(rq2_rows)

print("Saved rq2_genre_summary.csv")

# -----------------------------------------------------------------------------
# 3. RQ3: Price Groups Summary
# -----------------------------------------------------------------------------
price_groups = defaultdict(lambda: {'games': 0, 'reviews': [], 'ratings': [], 'playtime': []})

for g in games:
    pg = g['price_group']
    price_groups[pg]['games'] += 1
    price_groups[pg]['reviews'].append(g['num_reviews_total'])
    if g['pct_pos_total'] > 0:
        price_groups[pg]['ratings'].append(g['pct_pos_total'])
    price_groups[pg]['playtime'].append(g['average_playtime_forever'])

rq3_rows = []
pg_order = ['Free', '0-5', '5-15', '15-30', '30-60', '60+']
for pg in pg_order:
    data = price_groups[pg]
    cnt = data['games']
    avg_rev = sum(data['reviews']) / len(data['reviews']) if data['reviews'] else 0
    avg_rat = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else 0
    avg_play = sum(data['playtime']) / len(data['playtime']) if data['playtime'] else 0
    rq3_rows.append([pg, cnt, round(avg_rev, 0), round(avg_rat, 2), round(avg_play, 0)])

with open(os.path.join(RESULTS_DIR, "rq3_price_group_summary.csv"), 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["price_group", "total_games", "avg_reviews", "avg_positive_rating", "avg_playtime_min"])
    writer.writerows(rq3_rows)

print("Saved rq3_price_group_summary.csv")

# -----------------------------------------------------------------------------
# 4. RQ4: Anomalies (Outliers)
# -----------------------------------------------------------------------------
cheap_huge_rev = [g for g in games if g['price'] <= 5.0 and g['num_reviews_total'] > 50000]
cheap_huge_rev.sort(key=lambda x: x['num_reviews_total'], reverse=True)

rq4_anom1 = [[g['appid'], g['name'], g['price'], g['num_reviews_total'], g['pct_pos_total'], g['peak_ccu']] for g in cheap_huge_rev[:50]]

with open(os.path.join(RESULTS_DIR, "rq4_cheap_games_huge_reviews.csv"), 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["appid", "name", "price", "num_reviews_total", "pct_pos_total", "peak_ccu"])
    writer.writerows(rq4_anom1)

print("Saved rq4_cheap_games_huge_reviews.csv")

print("\nPure Python analysis completed successfully!")
