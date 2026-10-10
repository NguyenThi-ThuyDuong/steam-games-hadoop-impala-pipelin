"""
DATA PREPROCESSING PIPELINE FOR STEAM DATASET (DATA MINING STANDARD)
Dự án Big Data: Phân tích dữ liệu trò chơi điện tử và xu hướng thị trường sử dụng Apache Impala
Vị trí lưu trữ: D:\\HocTap\\HK1_27\\BigData\\DoAnBigData\\datamining
"""

import os
import sys

# Configure UTF-8 stdout for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import re
import csv
import json
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime

# Tăng giới hạn trường CSV cho văn bản dài
csv.field_size_limit(2147483647)

BASE_DIR = r"D:\HocTap\HK1_27\BigData"
RAW_FILE = os.path.join(BASE_DIR, "archive", "games_march2025_cleaned.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "DoAnBigData", "datamining")
DATA_DIR = os.path.join(OUTPUT_DIR, "data")
PARQUET_DIR = os.path.join(OUTPUT_DIR, "parquet")
METRICS_DIR = os.path.join(OUTPUT_DIR, "metrics")

for d in [DATA_DIR, PARQUET_DIR, METRICS_DIR]:
    os.makedirs(d, exist_ok=True)

print("=" * 80)
print("KHỞI ĐỘNG PIPELINE TIỀN XỬ LÝ DỮ LIỆU DATA MINING CHO STEAM DATASET")
print("=" * 80)

def parse_list_str(val):
    if not val or val.strip() in ("[]", "None", ""):
        return []
    try:
        res = eval(val)
        if isinstance(res, list):
            return [str(x).strip() for x in res if str(x).strip()]
    except Exception:
        pass
    return []

def parse_tags_dict(val):
    if not val or val.strip() in ("{}", "None", ""):
        return {}
    try:
        res = eval(val)
        if isinstance(res, dict):
            return {str(k).strip(): int(v) for k, v in res.items() if str(k).strip()}
    except Exception:
        pass
    return {}

def parse_owners_range(val):
    if not val:
        return 0, 0
    m = re.search(r'(\d+)\s*-\s*(\d+)', str(val))
    if m:
        return int(m.group(1)), int(m.group(2))
    return 0, 0

# Bước 1: Thu thập thông tin ban đầu & kiểm tra chất lượng
print("\n[Bước 1/6] Đọc và khảo sát toàn bộ dữ liệu thô...")

total_raw_rows = 0
seen_appids = set()
duplicate_appids_count = 0
sentinel_pct_pos_count = 0
sentinel_num_reviews_count = 0
sentinel_recent_count = 0
metacritic_zero_count = 0
negative_age_count = 0
invalid_dates_count = 0

games_rows = []
genres_rows = []
tags_rows = []
devs_rows = []
pubs_rows = []

# Giá trị tạm để tính toán IQR và Z-Score
all_prices = []
all_reviews = []
all_ccu = []

with open(RAW_FILE, 'r', encoding='utf-8', errors='replace') as f:
    reader = csv.reader(f)
    raw_header = next(reader)
    col_idx = {name.strip(): i for i, name in enumerate(raw_header)}

    for row in reader:
        if not row:
            continue
        total_raw_rows += 1

        try:
            appid_str = row[col_idx["appid"]].strip()
            if not appid_str or not appid_str.isdigit():
                continue
            appid = int(appid_str)
            if appid in seen_appids:
                duplicate_appids_count += 1
                continue
            seen_appids.add(appid)

            name = row[col_idx["name"]].strip() or "Unknown Game"
            release_date = row[col_idx["release_date"]].strip()

            # Trích xuất release_year
            year_match = re.search(r'\b(19\d\d|20\d\d)\b', release_date)
            release_year = int(year_match.group(1)) if year_match else 0
            if release_year == 0 or release_year > 2026:
                invalid_dates_count += 1

            # Giá bán
            price_str = row[col_idx["price"]].strip()
            try:
                price = float(price_str)
                if price < 0:
                    price = 0.0
            except ValueError:
                price = 0.0
            all_prices.append(price)

            # Sentinel values: -1 trong rating và reviews
            pct_pos_str = row[col_idx["pct_pos_total"]].strip()
            num_rev_str = row[col_idx["num_reviews_total"]].strip()

            try:
                pct_pos_val = int(float(pct_pos_str))
            except (ValueError, TypeError):
                pct_pos_val = -1

            try:
                num_rev_val = int(float(num_rev_str))
            except (ValueError, TypeError):
                num_rev_val = -1

            if pct_pos_val == -1:
                sentinel_pct_pos_count += 1
            if num_rev_val == -1:
                sentinel_num_reviews_count += 1
            elif num_rev_val > 0:
                all_reviews.append(num_rev_val)

            pct_pos_rec_str = row[col_idx["pct_pos_recent"]].strip()
            num_rev_rec_str = row[col_idx["num_reviews_recent"]].strip()
            try:
                pct_pos_rec = int(float(pct_pos_rec_str))
            except:
                pct_pos_rec = -1
            try:
                num_rev_rec = int(float(num_rev_rec_str))
            except:
                num_rev_rec = -1

            if pct_pos_rec == -1 or num_rev_rec == -1:
                sentinel_recent_count += 1

            # Required age
            try:
                req_age = int(float(row[col_idx["required_age"]].strip() or "0"))
                if req_age < 0:
                    negative_age_count += 1
                    req_age = 0
            except:
                req_age = 0

            # Metacritic score
            try:
                meta = int(float(row[col_idx["metacritic_score"]].strip() or "0"))
            except:
                meta = 0
            if meta == 0:
                metacritic_zero_count += 1

            # Playtime & CCU
            try:
                peak_ccu = int(float(row[col_idx["peak_ccu"]].strip() or "0"))
            except:
                peak_ccu = 0
            if peak_ccu > 0:
                all_ccu.append(peak_ccu)

            try:
                avg_playtime = int(float(row[col_idx["average_playtime_forever"]].strip() or "0"))
                med_playtime = int(float(row[col_idx["median_playtime_forever"]].strip() or "0"))
            except:
                avg_playtime, med_playtime = 0, 0

            # Reviews positive / negative
            try:
                pos = int(float(row[col_idx["positive"]].strip() or "0"))
                neg = int(float(row[col_idx["negative"]].strip() or "0"))
            except:
                pos, neg = 0, 0

            # Platform
            win = row[col_idx["windows"]].strip().lower() in ['true', '1']
            mac = row[col_idx["mac"]].strip().lower() in ['true', '1']
            nux = row[col_idx["linux"]].strip().lower() in ['true', '1']

            dlc = int(float(row[col_idx["dlc_count"]].strip() or "0"))
            ach = int(float(row[col_idx["achievements"]].strip() or "0"))
            recs = int(float(row[col_idx["recommendations"]].strip() or "0"))
            langs = row[col_idx["supported_languages"]].strip()
            desc = row[col_idx["short_description"]].replace('\n', ' ').replace('\r', ' ').strip()
            owners_str = row[col_idx["estimated_owners"]].strip()

            # Lưu hàng thô đã chuẩn hóa sơ bộ
            games_rows.append({
                "appid": appid,
                "name": name,
                "release_date": release_date,
                "release_year": release_year,
                "price": price,
                "required_age": req_age,
                "dlc_count": dlc,
                "short_description": desc[:300],
                "windows": win,
                "mac": mac,
                "linux": nux,
                "metacritic_score": meta,
                "achievements": ach,
                "recommendations": recs,
                "supported_languages": langs[:150],
                "positive": pos,
                "negative": neg,
                "estimated_owners": owners_str,
                "average_playtime_forever": avg_playtime,
                "median_playtime_forever": med_playtime,
                "peak_ccu": peak_ccu,
                "pct_pos_total_raw": pct_pos_val,
                "num_reviews_total_raw": num_rev_val,
                "pct_pos_recent_raw": pct_pos_rec,
                "num_reviews_recent_raw": num_rev_rec
            })

            # Tách multi-valued dimensions
            for g in parse_list_str(row[col_idx["genres"]]):
                genres_rows.append({"appid": appid, "genre": g})

            for t, cnt in parse_tags_dict(row[col_idx["tags"]]).items():
                tags_rows.append({"appid": appid, "tag": t, "count": cnt})

            for d in parse_list_str(row[col_idx["developers"]]):
                devs_rows.append({"appid": appid, "developer": d})

            for p in parse_list_str(row[col_idx["publishers"]]):
                pubs_rows.append({"appid": appid, "publisher": p})

        except Exception as e:
            continue

print(f"-> Tổng bản ghi thô đọc được: {total_raw_rows:,}")
print(f"-> Số bản ghi trùng AppID đã loại bỏ: {duplicate_appids_count}")
print(f"-> Số bản ghi duy nhất: {len(games_rows):,}")
print(f"-> Số bản ghi có sentinel -1 ở pct_pos_total: {sentinel_pct_pos_count:,} ({sentinel_pct_pos_count/len(games_rows)*100:.1f}%)")
print(f"-> Số bản ghi có metacritic = 0 (no data): {metacritic_zero_count:,} ({metacritic_zero_count/len(games_rows)*100:.1f}%)")

# Bước 2: Phân tích Outlier Detection (IQR & Z-Score)
print("\n[Bước 2/6] Tính toán Outlier Detection (IQR & Z-Score)...")

# IQR cho Price (chỉ xét game có phí > 0)
paid_prices = [p for p in all_prices if p > 0]
q1_price, q3_price = np.percentile(paid_prices, [25, 75])
iqr_price = q3_price - q1_price
upper_price_iqr = q3_price + 1.5 * iqr_price

# Z-Score cho Price
mean_price = np.mean(all_prices)
std_price = np.std(all_prices)

# IQR & Z-Score cho Reviews
q1_rev, q3_rev = np.percentile(all_reviews, [25, 75])
iqr_rev = q3_rev - q1_rev
upper_rev_iqr = q3_rev + 1.5 * iqr_rev
mean_rev = np.mean(all_reviews)
std_rev = np.std(all_reviews)

print(f"   [Price] Q1: ${q1_price:.2f}, Q3: ${q3_price:.2f}, IQR: ${iqr_price:.2f}, Ngưỡng Outlier IQR: ${upper_price_iqr:.2f}")
print(f"   [Reviews] Q1: {q1_rev:.0f}, Q3: {q3_rev:.0f}, IQR: {iqr_rev:.0f}, Ngưỡng Outlier IQR: {upper_rev_iqr:.0f}")

# Bước 3: Data Transformation & Attribute Construction
print("\n[Bước 3/6] Biến đổi dữ liệu (Transformation) & Xây dựng thuộc tính mới (Construction)...")

cleaned_games = []

for g in games_rows:
    # 1. Xử lý Missing Value / Sentinel ở Rating
    pct_pos = g["pct_pos_total_raw"] if g["pct_pos_total_raw"] != -1 else None
    num_rev = g["num_reviews_total_raw"] if g["num_reviews_total_raw"] != -1 else None
    pct_pos_rec = g["pct_pos_recent_raw"] if g["pct_pos_recent_raw"] != -1 else None
    num_rev_rec = g["num_reviews_recent_raw"] if g["num_reviews_recent_raw"] != -1 else None

    # 2. Xử lý Metacritic
    meta_score = g["metacritic_score"] if g["metacritic_score"] > 0 else None
    has_metacritic = (meta_score is not None)

    # 3. Attribute Construction: review_ratio & total_reviews_calc
    total_calc = g["positive"] + g["negative"]
    review_ratio = round(g["positive"] / total_calc, 4) if total_calc > 0 else None

    # 4. Attribute Construction: game_age
    game_age = (2025 - g["release_year"]) if g["release_year"] >= 1990 else None

    # 5. Attribute Construction: platform_count & is_free
    plat_count = int(g["windows"]) + int(g["mac"]) + int(g["linux"])
    is_free = (g["price"] == 0.0)

    # 6. Parse estimated owners
    own_lower, own_upper = parse_owners_range(g["estimated_owners"])

    # 7. Discretization: price_category (Quantile-based chuẩn thực tế)
    p = g["price"]
    if p == 0.0:
        price_cat = "Free"
    elif p <= 4.99:
        price_cat = "Budget"
    elif p <= 14.99:
        price_cat = "Mid-range"
    elif p <= 39.99:
        price_cat = "Premium"
    elif p <= 69.99:
        price_cat = "High-end"
    else:
        price_cat = "Luxury"

    # 8. Discretization: rating_category (Chuẩn chính thức Steam)
    if num_rev is None or num_rev < 10:
        rating_cat = "Unrated / Few Reviews"
    elif pct_pos is not None:
        if pct_pos >= 95:
            rating_cat = "Overwhelmingly Positive"
        elif pct_pos >= 80:
            rating_cat = "Very Positive"
        elif pct_pos >= 70:
            rating_cat = "Positive"
        elif pct_pos >= 40:
            rating_cat = "Mixed"
        elif pct_pos >= 20:
            rating_cat = "Negative"
        else:
            rating_cat = "Overwhelmingly Negative"
    else:
        rating_cat = "Unrated / Few Reviews"

    # 9. Outlier Flags (giữ nguyên dữ liệu, chỉ gắn nhãn khoa học)
    is_price_outlier = (p > upper_price_iqr) if p > 0 else False
    is_rev_outlier = (num_rev > upper_rev_iqr) if num_rev is not None else False

    # Z-scores
    z_price = round((p - mean_price) / std_price, 2) if std_price > 0 else 0.0
    z_rev = round((num_rev - mean_rev) / std_rev, 2) if (num_rev is not None and std_rev > 0) else None

    cleaned_games.append({
        "appid": g["appid"],
        "name": g["name"],
        "release_date": g["release_date"],
        "release_year": g["release_year"],
        "price": g["price"],
        "price_category": price_cat,
        "rating_category": rating_cat,
        "required_age": g["required_age"],
        "dlc_count": g["dlc_count"],
        "short_description": g["short_description"],
        "windows": g["windows"],
        "mac": g["mac"],
        "linux": g["linux"],
        "platform_count": plat_count,
        "metacritic_score": meta_score,
        "has_metacritic": has_metacritic,
        "achievements": g["achievements"],
        "recommendations": g["recommendations"],
        "supported_languages": g["supported_languages"],
        "positive": g["positive"],
        "negative": g["negative"],
        "total_reviews_calc": total_calc,
        "review_ratio": review_ratio,
        "estimated_owners": g["estimated_owners"],
        "owners_lower": own_lower,
        "owners_upper": own_upper,
        "average_playtime_forever": g["average_playtime_forever"],
        "median_playtime_forever": g["median_playtime_forever"],
        "peak_ccu": g["peak_ccu"],
        "pct_pos_total": pct_pos,
        "num_reviews_total": num_rev,
        "pct_pos_recent": pct_pos_rec,
        "num_reviews_recent": num_rev_rec,
        "game_age": game_age,
        "is_free": is_free,
        "is_price_outlier": is_price_outlier,
        "is_reviews_outlier": is_rev_outlier,
        "z_price": z_price,
        "z_reviews": z_rev
    })

df_clean_games = pd.DataFrame(cleaned_games)
df_genres = pd.DataFrame(genres_rows)
df_tags = pd.DataFrame(tags_rows)
df_devs = pd.DataFrame(devs_rows)
df_pubs = pd.DataFrame(pubs_rows)

print(f"-> Tổng trò chơi sạch: {len(df_clean_games):,}")
print(f"-> Thể loại (Genre associations): {len(df_genres):,}")
print(f"-> Thẻ cộng đồng (Tag associations): {len(df_tags):,}")
print(f"-> Nhà phát triển (Developers): {len(df_devs):,}")
print(f"-> Nhà phát hành (Publishers): {len(df_pubs):,}")

# Bước 4: Lưu dữ liệu sạch định dạng CSV
print("\n[Bước 4/6] Xuất dữ liệu đã làm sạch sang CSV...")

games_clean_csv = os.path.join(DATA_DIR, "games_cleaned_v2.csv")
genres_csv = os.path.join(DATA_DIR, "games_genres.csv")
tags_csv = os.path.join(DATA_DIR, "games_tags.csv")
devs_csv = os.path.join(DATA_DIR, "games_developers.csv")
pubs_csv = os.path.join(DATA_DIR, "games_publishers.csv")

df_clean_games.to_csv(games_clean_csv, index=False, encoding='utf-8')
df_genres.to_csv(genres_csv, index=False, encoding='utf-8')
df_tags.to_csv(tags_csv, index=False, encoding='utf-8')
df_devs.to_csv(devs_csv, index=False, encoding='utf-8')
df_pubs.to_csv(pubs_csv, index=False, encoding='utf-8')
print("-> Đã xuất 5 file CSV thành công.")

# Bước 5: Chuyển đổi và tối ưu hóa sang định dạng Apache Parquet
print("\n[Bước 5/6] Chuyển đổi sang Apache Parquet chuẩn nén Snappy...")

# 5.1 Main Fact Table games_parquet (Partitioned by release_year)
parquet_games_root = os.path.join(PARQUET_DIR, "games_parquet")
os.makedirs(parquet_games_root, exist_ok=True)

# Ghi partitioned parquet
pq.write_to_dataset(
    pa.Table.from_pandas(df_clean_games),
    root_path=parquet_games_root,
    partition_cols=['release_year'],
    compression='snappy'
)
print(f"-> Đã ghi Parquet games_parquet phân vùng theo release_year tại: {parquet_games_root}")

# 5.2 Không phân vùng (phục vụ benchmark)
pq.write_table(
    pa.Table.from_pandas(df_clean_games),
    os.path.join(PARQUET_DIR, "games_parquet_nopart.parquet"),
    compression='snappy'
)

# 5.3 Dimension Tables
pq.write_table(pa.Table.from_pandas(df_genres), os.path.join(PARQUET_DIR, "games_genres.parquet"), compression='snappy')
pq.write_table(pa.Table.from_pandas(df_tags), os.path.join(PARQUET_DIR, "games_tags.parquet"), compression='snappy')
pq.write_table(pa.Table.from_pandas(df_devs), os.path.join(PARQUET_DIR, "games_developers.parquet"), compression='snappy')
pq.write_table(pa.Table.from_pandas(df_pubs), os.path.join(PARQUET_DIR, "games_publishers.parquet"), compression='snappy')
print("-> Đã ghi toàn bộ bảng Parquet Dimensions thành công.")

# Bước 6: Lưu báo cáo tổng hợp chỉ số Preprocessing Metrics JSON
print("\n[Bước 6/6] Ghi nhận chỉ số định lượng tiền xử lý...")

metrics = {
    "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "raw_total_records": total_raw_rows,
    "raw_attributes_count": len(raw_header),
    "clean_total_records": len(df_clean_games),
    "clean_attributes_count": len(df_clean_games.columns),
    "duplicates_removed": duplicate_appids_count,
    "sentinel_values_handled": {
        "pct_pos_total_sentinel_negative_1": sentinel_pct_pos_count,
        "num_reviews_total_sentinel_negative_1": sentinel_num_reviews_count,
        "recent_reviews_sentinel_negative_1": sentinel_recent_count
    },
    "noise_values_corrected": {
        "required_age_negative_1": negative_age_count
    },
    "metacritic_missing_classified": metacritic_zero_count,
    "outlier_thresholds": {
        "price_upper_iqr": float(round(upper_price_iqr, 2)),
        "reviews_upper_iqr": float(round(upper_rev_iqr, 2))
    },
    "outliers_flagged": {
        "price_outliers_count": int(df_clean_games["is_price_outlier"].sum()),
        "reviews_outliers_count": int(df_clean_games["is_reviews_outlier"].sum())
    },
    "price_distribution": df_clean_games["price_category"].value_counts().to_dict(),
    "rating_distribution": df_clean_games["rating_category"].value_counts().to_dict()
}

metrics_path = os.path.join(METRICS_DIR, "preprocessing_metrics.json")
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=4, ensure_ascii=False)

print(f"-> Đã xuất báo cáo metrics: {metrics_path}")
print("\n" + "=" * 80)
print("PIPELINE TIỀN XỬ LÝ DỮ LIỆU ĐÃ HOÀN TẤT THÀNH CÔNG VƯỢT TRỘI!")
print("=" * 80)
