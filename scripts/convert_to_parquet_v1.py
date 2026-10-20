import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUT_PARQUET_DIR = os.path.join(BASE_DIR, "data", "parquet_v1")

os.makedirs(OUT_PARQUET_DIR, exist_ok=True)

print("=== Chuyển đổi dữ liệu sang Parquet Version 1.0 (Chuẩn tương thích Impala 3.x) ===")

# 1. Chuyển đổi Fact Games (Partitioned by release_year)
games_csv = os.path.join(PROCESSED_DIR, "games_cleaned.csv")
print(f"Reading {games_csv}...")
df_games = pd.read_csv(games_csv, low_memory=False)

# Ép kiểu dữ liệu chuẩn
df_games['appid'] = df_games['appid'].astype('int64')
df_games['release_year'] = df_games['release_year'].fillna(0).astype('int32')
df_games['price'] = df_games['price'].fillna(0.0).astype('float64')

# Lọc bỏ năm không hợp lệ nếu có
df_games = df_games[df_games['release_year'] >= 1997]

# Xuất bảng phân vùng games_parquet
games_part_dir = os.path.join(OUT_PARQUET_DIR, "games_parquet")
os.makedirs(games_part_dir, exist_ok=True)
table_games = pa.Table.from_pandas(df_games)

print(f"Ghi Parquet partitioned by release_year vào {games_part_dir}...")
pq.write_to_dataset(
    table_games,
    root_path=games_part_dir,
    partition_cols=['release_year'],
    version='1.0',
    compression='snappy'
)
print("-> Hoàn thành games_parquet!")

# Xuất bảng games_nopart (không phân vùng)
nopart_dir = os.path.join(OUT_PARQUET_DIR, "games_nopart")
os.makedirs(nopart_dir, exist_ok=True)
pq.write_table(table_games, os.path.join(nopart_dir, "games_nopart.parquet"), version='1.0', compression='snappy')
print("-> Hoàn thành games_nopart!")

# 2. Chuyển đổi các bảng Dimension
dim_configs = [
    ("games_genres.csv", "dim_genres", "games_genres.parquet"),
    ("games_tags.csv", "dim_tags", "games_tags.parquet"),
    ("games_developers.csv", "dim_developers", "games_developers.parquet"),
    ("games_publishers.csv", "dim_publishers", "games_publishers.parquet")
]

for csv_name, folder_name, out_name in dim_configs:
    csv_path = os.path.join(PROCESSED_DIR, csv_name)
    if os.path.exists(csv_path):
        print(f"Reading {csv_name}...")
        df_dim = pd.read_csv(csv_path, low_memory=False)
        target_dir = os.path.join(OUT_PARQUET_DIR, folder_name)
        os.makedirs(target_dir, exist_ok=True)
        tbl_dim = pa.Table.from_pandas(df_dim)
        pq.write_table(tbl_dim, os.path.join(target_dir, out_name), version='1.0', compression='snappy')
        print(f"-> Hoàn thành {folder_name} ({len(df_dim):,} dòng)!")

print("=== TẤT CẢ FILE PARQUET ĐÃ SẴN SÀNG 100%! ===")
