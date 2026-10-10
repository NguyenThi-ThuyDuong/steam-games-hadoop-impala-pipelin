"""
SCRIPT THỰC THI PHÂN TÍCH THỊ TRƯỜNG TỪ DATASET PARQUET TIỀN XỬ LÝ
Lưu kết quả phân tích vào D:\\HocTap\\HK1_27\\BigData\\DoAnBigData\\datamining\\results
"""

import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import pandas as pd
import numpy as np

BASE_DIR = r"D:\HocTap\HK1_27\BigData\DoAnBigData\datamining"
PARQUET_FILE = os.path.join(BASE_DIR, "parquet", "games_parquet_nopart.parquet")
GENRES_FILE = os.path.join(BASE_DIR, "parquet", "games_genres.parquet")
DEVS_FILE = os.path.join(BASE_DIR, "parquet", "games_developers.parquet")
PUBS_FILE = os.path.join(BASE_DIR, "parquet", "games_publishers.parquet")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(RESULTS_DIR, exist_ok=True)

print("Đang đọc dữ liệu Parquet để thực thi các câu truy vấn phân tích...")
df = pd.read_parquet(PARQUET_FILE)
df_genres = pd.read_parquet(GENRES_FILE)
df_devs = pd.read_parquet(DEVS_FILE)
df_pubs = pd.read_parquet(PUBS_FILE)

# 1. Số lượng game phát hành theo năm và tỷ lệ F2P
print("1. Phân tích số lượng game phát hành theo năm...")
df_valid_years = df[(df['release_year'] >= 2000) & (df['release_year'] <= 2025)]
yearly = df_valid_years.groupby('release_year').agg(
    total_games=('appid', 'count'),
    free_games=('is_free', lambda x: x.sum()),
    paid_games=('is_free', lambda x: (~x).sum()),
    avg_paid_price=('price', lambda x: round(x[x > 0].mean(), 2) if len(x[x > 0]) > 0 else 0)
).reset_index()
yearly['free_ratio_pct'] = round(yearly['free_games'] * 100.0 / yearly['total_games'], 2)
yearly.to_csv(os.path.join(RESULTS_DIR, "q1_yearly_releases_f2p.csv"), index=False)

# 2. YoY Growth Rate
print("2. Tính toán tốc độ tăng trưởng YoY...")
yearly_yoy = df[(df['release_year'] >= 2005) & (df['release_year'] <= 2024)].groupby('release_year').size().reset_index(name='game_count')
yearly_yoy['yoy_growth'] = yearly_yoy['game_count'].diff()
yearly_yoy['yoy_growth_pct'] = round(yearly_yoy['yoy_growth'] * 100.0 / yearly_yoy['game_count'].shift(1), 2)
yearly_yoy.to_csv(os.path.join(RESULTS_DIR, "q2_yoy_growth.csv"), index=False)

# 3. Thể loại theo thời kỳ
print("3. Phân tích thể loại theo các thời kỳ...")
def get_era(y):
    if 2000 <= y <= 2009: return '1. Kỷ nguyên Cổ điển (2000-2009)'
    elif 2010 <= y <= 2014: return '2. Giai đoạn Greenlight (2010-2014)'
    elif 2015 <= y <= 2019: return '3. Giai đoạn Bùng nổ Indie (2015-2019)'
    elif y >= 2020: return '4. Kỷ nguyên Hiện đại (2020-2025)'
    return 'Other'

df_valid_years_era = df[df['release_year'] >= 2000].copy()
df_valid_years_era['period_era'] = df_valid_years_era['release_year'].apply(get_era)
merged_era = pd.merge(df_valid_years_era, df_genres, on='appid')
era_genre = merged_era.groupby(['period_era', 'genre']).agg(total_games=('appid', 'nunique')).reset_index()
era_genre = era_genre.sort_values(by=['period_era', 'total_games'], ascending=[True, False])
era_genre.to_csv(os.path.join(RESULTS_DIR, "q3_genres_by_era.csv"), index=False)

# 4. Hồ sơ thể loại toàn diện
print("4. Tổng hợp hồ sơ thể loại toàn diện...")
merged_genres = pd.merge(df, df_genres, on='appid')
genre_profile = merged_genres.groupby('genre').agg(
    total_games=('appid', 'nunique'),
    avg_price=('price', lambda x: round(x.mean(), 2)),
    avg_positive_rating=('pct_pos_total', lambda x: round(x.dropna().mean(), 2) if len(x.dropna()) > 0 else 0),
    avg_reviews=('num_reviews_total', lambda x: round(x.dropna().mean(), 0) if len(x.dropna()) > 0 else 0),
    avg_playtime_minutes=('average_playtime_forever', lambda x: round(x.mean(), 0)),
    avg_peak_ccu=('peak_ccu', lambda x: round(x.mean(), 0))
).reset_index().sort_values(by='total_games', ascending=False)
genre_profile.to_csv(os.path.join(RESULTS_DIR, "q4_genre_profile.csv"), index=False)

# 5. Phân bố cơ cấu giá game
print("5. Phân tích cơ cấu nhóm giá...")
price_cat_order = ['Free', 'Budget', 'Mid-range', 'Premium', 'High-end', 'Luxury']
price_analysis = df.groupby('price_category', observed=False).agg(
    game_count=('appid', 'count'),
    avg_reviews=('num_reviews_total', lambda x: round(x.dropna().mean(), 0) if len(x.dropna()) > 0 else 0),
    avg_positive_pct=('pct_pos_total', lambda x: round(x.dropna().mean(), 2) if len(x.dropna()) > 0 else 0),
    avg_peak_ccu=('peak_ccu', lambda x: round(x.mean(), 0))
).reset_index()
price_analysis['category_share_pct'] = round(price_analysis['game_count'] * 100.0 / len(df), 2)
price_analysis['order'] = price_analysis['price_category'].apply(lambda x: price_cat_order.index(x) if x in price_cat_order else 99)
price_analysis = price_analysis.sort_values('order').drop(columns=['order'])
price_analysis.to_csv(os.path.join(RESULTS_DIR, "q5_price_category_summary.csv"), index=False)

# 6. Top Nhà phát triển
print("6. Xếp hạng top Nhà phát triển...")
merged_devs = pd.merge(df, df_devs, on='appid')
top_devs = merged_devs[merged_devs['developer'] != 'Unknown'].groupby('developer').agg(
    total_released_games=('appid', 'nunique'),
    avg_game_price=('price', lambda x: round(x.mean(), 2)),
    avg_game_rating=('pct_pos_total', lambda x: round(x.dropna().mean(), 2) if len(x.dropna()) > 0 else 0),
    total_community_reviews=('num_reviews_total', lambda x: round(x.dropna().sum(), 0))
).reset_index().sort_values(by='total_released_games', ascending=False).head(25)
top_devs.to_csv(os.path.join(RESULTS_DIR, "q6_top_developers.csv"), index=False)

# 7. Top Nhà phát hành
print("7. Xếp hạng top Nhà phát hành theo reviews amassing...")
merged_pubs = pd.merge(df, df_pubs, on='appid')
top_pubs = merged_pubs[merged_pubs['publisher'] != 'Unknown'].groupby('publisher').agg(
    published_games=('appid', 'nunique'),
    total_reviews_amassed=('num_reviews_total', lambda x: round(x.dropna().sum(), 0)),
    avg_publisher_rating=('pct_pos_total', lambda x: round(x.dropna().mean(), 2) if len(x.dropna()) > 0 else 0)
).reset_index().sort_values(by='total_reviews_amassed', ascending=False).head(20)
top_pubs.to_csv(os.path.join(RESULTS_DIR, "q7_top_publishers.csv"), index=False)

# 8. Rating category theo Thể loại
print("8. Tổng hợp Rating Category theo Genre...")
rating_genre = merged_genres.groupby(['genre', 'rating_category']).size().unstack(fill_value=0).reset_index()
rating_genre.to_csv(os.path.join(RESULTS_DIR, "q8_genre_rating_distribution.csv"), index=False)

# 9. Outliers Analysis
print("9. Trích xuất nhóm Outlier đặc thù...")
outliers_cheap_huge = df[(df['price'] <= 5.0) & (df['is_reviews_outlier'] == True) & (df['num_reviews_total'] > 50000)][
    ['appid', 'name', 'price', 'price_category', 'num_reviews_total', 'pct_pos_total', 'peak_ccu', 'z_reviews']
].sort_values(by='num_reviews_total', ascending=False).head(20)
outliers_cheap_huge.to_csv(os.path.join(RESULTS_DIR, "q9_cheap_huge_reviews.csv"), index=False)

outliers_expensive_few = df[(df['is_price_outlier'] == True) & (df['price'] >= 100.0) & ((df['num_reviews_total'].isna()) | (df['num_reviews_total'] < 50))][
    ['appid', 'name', 'price', 'price_category', 'num_reviews_total', 'pct_pos_total', 'z_price']
].sort_values(by='price', ascending=False).head(20)
outliers_expensive_few.to_csv(os.path.join(RESULTS_DIR, "q9_expensive_few_reviews.csv"), index=False)

# 10. Multi-platform
print("10. Phân tích chiến lược đa nền tảng...")
def get_plat_name(c):
    if c == 1: return 'Chỉ 1 nền tảng (Thường là Windows)'
    elif c == 2: return '2 nền tảng (Windows + Mac/Linux)'
    else: return 'Toàn diện (Windows + Mac + Linux)'

df['platform_strategy'] = df['platform_count'].apply(get_plat_name)
plat_analysis = df.groupby('platform_strategy').agg(
    total_games=('appid', 'count'),
    avg_price=('price', lambda x: round(x.mean(), 2)),
    avg_rating=('pct_pos_total', lambda x: round(x.dropna().mean(), 2) if len(x.dropna()) > 0 else 0),
    avg_reviews=('num_reviews_total', lambda x: round(x.dropna().mean(), 0) if len(x.dropna()) > 0 else 0)
).reset_index()
plat_analysis['strategy_pct'] = round(plat_analysis['total_games'] * 100.0 / len(df), 2)
plat_analysis.to_csv(os.path.join(RESULTS_DIR, "q10_platform_strategy.csv"), index=False)

print("\nĐã thực thi và lưu tất cả 10 bảng kết quả phân tích thành công vào thư mục results!")
