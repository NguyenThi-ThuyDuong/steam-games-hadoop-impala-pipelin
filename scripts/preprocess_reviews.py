import csv
import os
import sys
from datetime import datetime, timezone

# Set field size limit to 2^31 - 1 for Windows C long compatibility
csv.field_size_limit(2147483647)

ARCHIVE_DIR = r"D:\HocTap\HK1_27\BigData\archive"
OUTPUT_DIR = r"D:\HocTap\HK1_27\BigData\DoAnBigData\data\processed\reviews_cleaned"

os.makedirs(OUTPUT_DIR, exist_ok=True)

review_files = sorted([f for f in os.listdir(ARCHIVE_DIR) if f.startswith('reviews-') and f.endswith('.csv')])

reviews_header = [
    "steamid", "appid", "voted_up", "votes_up", "votes_funny",
    "weighted_vote_score", "playtime_forever", "playtime_at_review",
    "num_games_owned", "num_reviews", "review_length", "review_date",
    "review_year", "review_month"
]

total_processed = 0

print(f"Found {len(review_files)} review files to process.")

for fname in review_files:
    in_path = os.path.join(ARCHIVE_DIR, fname)
    out_fname = f"cleaned_{fname}"
    out_path = os.path.join(OUTPUT_DIR, out_fname)
    
    file_processed = 0
    print(f"Processing {fname} -> {out_fname}...")
    
    with open(in_path, 'r', encoding='utf-8', errors='replace') as f_in, \
         open(out_path, 'w', encoding='utf-8', newline='') as f_out:
        
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        
        try:
            raw_header = next(reader)
        except StopIteration:
            continue
            
        col_idx = {name.strip(): i for i, name in enumerate(raw_header)}
        
        writer.writerow(reviews_header)
        
        for row in reader:
            if not row or len(row) < len(raw_header):
                continue
            try:
                steamid = row[col_idx["steamid"]].strip()
                appid = row[col_idx["appid"]].strip()
                
                if not steamid or not appid or not appid.isdigit():
                    continue
                
                voted_up = row[col_idx["voted_up"]].strip().lower() in ['true', '1']
                votes_up = int(float(row[col_idx["votes_up"]].strip() or "0"))
                votes_funny = int(float(row[col_idx["votes_funny"]].strip() or "0"))
                weighted_score = float(row[col_idx["weighted_vote_score"]].strip() or "0.0")
                
                playtime_forever = int(float(row[col_idx["playtime_forever"]].strip() or "0"))
                playtime_at_review = int(float(row[col_idx["playtime_at_review"]].strip() or "0"))
                num_games_owned = int(float(row[col_idx["num_games_owned"]].strip() or "0"))
                num_reviews = int(float(row[col_idx["num_reviews"]].strip() or "0"))
                
                review_text = row[col_idx["review"]].strip()
                review_len = len(review_text)
                
                timestamp = int(float(row[col_idx["unix_timestamp_created"]].strip() or "0"))
                
                if timestamp > 0:
                    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                    review_date = dt.strftime('%Y-%m-%d')
                    review_year = dt.year
                    review_month = dt.month
                else:
                    review_date = "1970-01-01"
                    review_year = 1970
                    review_month = 1
                
                writer.writerow([
                    steamid, int(appid), voted_up, votes_up, votes_funny,
                    weighted_score, playtime_forever, playtime_at_review,
                    num_games_owned, num_reviews, review_len, review_date,
                    review_year, review_month
                ])
                
                file_processed += 1
                total_processed += 1
                
            except Exception:
                continue

    print(f"Finished {fname}: {file_processed:,} reviews processed.")

print(f"\nAll review files processed successfully! Total: {total_processed:,} reviews.")
