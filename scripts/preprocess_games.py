import csv
import json
import os
import re

INPUT_FILE = r"D:\HocTap\HK1_27\BigData\archive\games_march2025_cleaned.csv"
OUTPUT_DIR = r"D:\HocTap\HK1_27\BigData\DoAnBigData\data\processed"

os.makedirs(OUTPUT_DIR, exist_ok=True)

games_out_path = os.path.join(OUTPUT_DIR, "games_cleaned.csv")
genres_out_path = os.path.join(OUTPUT_DIR, "games_genres.csv")
tags_out_path = os.path.join(OUTPUT_DIR, "games_tags.csv")
devs_out_path = os.path.join(OUTPUT_DIR, "games_developers.csv")
pubs_out_path = os.path.join(OUTPUT_DIR, "games_publishers.csv")

def parse_list_str(val):
    if not val or val.strip() == "[]":
        return []
    try:
        # evaluate stringified python list e.g. "['Action', 'Indie']"
        res = eval(val)
        if isinstance(res, list):
            return [str(x).strip() for x in res if x]
    except Exception:
        pass
    return []

def parse_tags_dict(val):
    if not val or val.strip() == "{}":
        return {}
    try:
        res = eval(val)
        if isinstance(res, dict):
            return res
    except Exception:
        pass
    return {}

def extract_year(date_str):
    if not date_str:
        return None
    # match 4 digits year e.g., '2017-12-21' or 'Dec 21, 2017'
    match = re.search(r'\b(19\d\d|20\d\d)\b', str(date_str))
    if match:
        return int(match.group(1))
    return None

def get_price_group(price):
    try:
        p = float(price)
        if p == 0:
            return "Free"
        elif p <= 5:
            return "0-5"
        elif p <= 15:
            return "5-15"
        elif p <= 30:
            return "15-30"
        elif p <= 60:
            return "30-60"
        else:
            return "60+"
    except Exception:
        return "Unknown"

print("Processing games dataset...")

games_header = [
    "appid", "name", "release_date", "release_year", "price", "price_group",
    "required_age", "dlc_count", "short_description", "windows", "mac", "linux",
    "metacritic_score", "achievements", "recommendations", "supported_languages",
    "positive", "negative", "estimated_owners", "average_playtime_forever",
    "average_playtime_2weeks", "median_playtime_forever", "median_playtime_2weeks",
    "peak_ccu", "pct_pos_total", "num_reviews_total", "pct_pos_recent", "num_reviews_recent"
]

seen_appids = set()
processed_count = 0

with open(INPUT_FILE, 'r', encoding='utf-8', errors='replace') as f_in, \
     open(games_out_path, 'w', encoding='utf-8', newline='') as f_games, \
     open(genres_out_path, 'w', encoding='utf-8', newline='') as f_genres, \
     open(tags_out_path, 'w', encoding='utf-8', newline='') as f_tags, \
     open(devs_out_path, 'w', encoding='utf-8', newline='') as f_devs, \
     open(pubs_out_path, 'w', encoding='utf-8', newline='') as f_pubs:

    reader = csv.reader(f_in)
    raw_header = next(reader)
    
    # Map column name to index
    col_idx = {name: i for i, name in enumerate(raw_header)}
    
    w_games = csv.writer(f_games)
    w_genres = csv.writer(f_genres)
    w_tags = csv.writer(f_tags)
    w_devs = csv.writer(f_devs)
    w_pubs = csv.writer(f_pubs)

    w_games.writerow(games_header)
    w_genres.writerow(["appid", "genre"])
    w_tags.writerow(["appid", "tag", "count"])
    w_devs.writerow(["appid", "developer"])
    w_pubs.writerow(["appid", "publisher"])

    for row in reader:
        if not row:
            continue
        try:
            appid = row[col_idx["appid"]].strip()
            if not appid or not appid.isdigit():
                continue
            
            appid_int = int(appid)
            if appid_int in seen_appids:
                continue
            seen_appids.add(appid_int)

            name = row[col_idx["name"]].strip()
            release_date = row[col_idx["release_date"]].strip()
            release_year = extract_year(release_date) or 0
            
            price_val = row[col_idx["price"]].strip() or "0"
            try:
                price = float(price_val)
            except ValueError:
                price = 0.0
            price_group = get_price_group(price)

            req_age = row[col_idx["required_age"]].strip() or "0"
            dlc = row[col_idx["dlc_count"]].strip() or "0"
            short_desc = row[col_idx["short_description"]].replace('\n', ' ').replace('\r', ' ').strip()
            
            win = row[col_idx["windows"]].strip().lower() in ['true', '1']
            mac = row[col_idx["mac"]].strip().lower() in ['true', '1']
            nux = row[col_idx["linux"]].strip().lower() in ['true', '1']

            meta = row[col_idx["metacritic_score"]].strip() or "0"
            ach = row[col_idx["achievements"]].strip() or "0"
            recs = row[col_idx["recommendations"]].strip() or "0"
            langs = row[col_idx["supported_languages"]].strip()
            
            pos = row[col_idx["positive"]].strip() or "0"
            neg = row[col_idx["negative"]].strip() or "0"
            owners = row[col_idx["estimated_owners"]].strip()
            
            avg_p_forever = row[col_idx["average_playtime_forever"]].strip() or "0"
            avg_p_2w = row[col_idx["average_playtime_2weeks"]].strip() or "0"
            med_p_forever = row[col_idx["median_playtime_forever"]].strip() or "0"
            med_p_2w = row[col_idx["median_playtime_2weeks"]].strip() or "0"
            
            peak = row[col_idx["peak_ccu"]].strip() or "0"
            pct_pos = row[col_idx["pct_pos_total"]].strip() or "0"
            num_revs = row[col_idx["num_reviews_total"]].strip() or "0"
            pct_pos_rec = row[col_idx["pct_pos_recent"]].strip() or "0"
            num_revs_rec = row[col_idx["num_reviews_recent"]].strip() or "0"

            w_games.writerow([
                appid_int, name, release_date, release_year, price, price_group,
                req_age, dlc, short_desc[:300], win, mac, nux,
                meta, ach, recs, langs[:150], pos, neg, owners,
                avg_p_forever, avg_p_2w, med_p_forever, med_p_2w,
                peak, pct_pos, num_revs, pct_pos_rec, num_revs_rec
            ])

            # Extract genres
            genres_list = parse_list_str(row[col_idx["genres"]])
            for g in genres_list:
                w_genres.writerow([appid_int, g])

            # Extract tags
            tags_dict = parse_tags_dict(row[col_idx["tags"]])
            for t, cnt in tags_dict.items():
                w_tags.writerow([appid_int, t, cnt])

            # Extract developers
            devs_list = parse_list_str(row[col_idx["developers"]])
            for d in devs_list:
                w_devs.writerow([appid_int, d])

            # Extract publishers
            pubs_list = parse_list_str(row[col_idx["publishers"]])
            for p in pubs_list:
                w_pubs.writerow([appid_int, p])

            processed_count += 1

        except Exception as e:
            continue

print(f"Games preprocessing complete! Processed {processed_count:,} unique games.")
