import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['axes.unicode_minus'] = False

PROCESSED_DIR = r"D:\HocTap\HK1_27\BigData\DoAnBigData\data\processed"
RESULTS_DIR = r"D:\HocTap\HK1_27\BigData\DoAnBigData\results\analysis"
FIGURES_DIR = r"D:\HocTap\HK1_27\BigData\DoAnBigData\figures"

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

print("Loading processed games and genres data...")
df_games = pd.read_csv(os.path.join(PROCESSED_DIR, "games_cleaned.csv"), low_memory=False)
df_genres = pd.read_csv(os.path.join(PROCESSED_DIR, "games_genres.csv"), low_memory=False)

print(f"Loaded {len(df_games):,} games and {len(df_genres):,} game-genre associations.")

# =============================================================================
# 1. RQ1: MARKET TRENDS OVER TIME
# =============================================================================
print("\n--- [RQ1] Analyzing Market Trends Over Time ---")

# Q1: Annual releases (2000-2024)
df_valid_years = df_games[(df_games['release_year'] >= 2000) & (df_games['release_year'] <= 2024)]
yearly_counts = df_valid_years.groupby('release_year').size().reset_index(name='total_games')
yearly_counts.to_csv(os.path.join(RESULTS_DIR, "rq1_yearly_releases.csv"), index=False)

# YoY Growth
yearly_counts['growth'] = yearly_counts['total_games'].diff()
yearly_counts['growth_pct'] = (yearly_counts['growth'] / yearly_counts['total_games'].shift(1) * 100).round(2)
yearly_counts.to_csv(os.path.join(RESULTS_DIR, "rq1_yoy_growth.csv"), index=False)

# Chart 1: Yearly Releases & YoY Growth
fig, ax1 = plt.subplots(figsize=(12, 6))
color = '#1f77b4'
ax1.set_xlabel('Release Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Total Games Released', color=color, fontsize=12, fontweight='bold')
bars = ax1.bar(yearly_counts['release_year'], yearly_counts['total_games'], color=color, alpha=0.85, label='Total Games')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = '#d62728'
ax2.set_ylabel('YoY Growth Rate (%)', color=color, fontsize=12, fontweight='bold')
line = ax2.plot(yearly_counts['release_year'], yearly_counts['growth_pct'], color=color, marker='o', linewidth=2, label='Growth Rate (%)')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Figure 1: Steam Game Releases & YoY Growth Rate (2000 - 2024)', fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "fig1_yearly_releases_growth.png"), dpi=300)
plt.close()

# Q4: Price evolution over years
yearly_price = df_valid_years.groupby('release_year').agg(
    avg_price=('price', 'mean'),
    median_price=('price', 'median'),
    free_games=('price', lambda x: (x == 0).sum()),
    paid_games=('price', lambda x: (x > 0).sum()),
    total_games=('price', 'count')
).reset_index()
yearly_price['free_pct'] = (yearly_price['free_games'] / yearly_price['total_games'] * 100).round(2)
yearly_price.to_csv(os.path.join(RESULTS_DIR, "rq1_yearly_price_trends.csv"), index=False)

# Chart 2: Free vs Paid Percentage
plt.figure(figsize=(12, 6))
plt.plot(yearly_price['release_year'], yearly_price['free_pct'], marker='s', color='#2ca02c', linewidth=2.5, label='Free-to-Play Ratio (%)')
plt.title('Figure 2: Evolution of Free-to-Play Games Proportion on Steam (2000 - 2024)', fontsize=14, fontweight='bold')
plt.xlabel('Release Year', fontsize=12, fontweight='bold')
plt.ylabel('Free Games Percentage (%)', fontsize=12, fontweight='bold')
plt.ylim(0, max(yearly_price['free_pct']) + 5)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "fig2_free_to_play_ratio.png"), dpi=300)
plt.close()


# =============================================================================
# 2. RQ2: GENRE ANALYSIS
# =============================================================================
print("\n--- [RQ2] Analyzing Genres Profile ---")

# Merge games with genres
df_merged_genres = pd.merge(df_genres, df_games, on='appid')

genre_summary = df_merged_genres.groupby('genre').agg(
    total_games=('appid', 'nunique'),
    avg_price=('price', 'mean'),
    avg_positive_pct=('pct_pos_total', lambda x: x[x > 0].mean()),
    avg_reviews=('num_reviews_total', 'mean'),
    avg_playtime=('average_playtime_forever', 'mean'),
    avg_peak_ccu=('peak_ccu', 'mean')
).reset_index().sort_values(by='total_games', ascending=False)

genre_summary.round(2).to_csv(os.path.join(RESULTS_DIR, "rq2_genre_profile.csv"), index=False)

# Chart 3: Top 15 Genres by Game Count
top15_genres = genre_summary.head(15)
plt.figure(figsize=(12, 7))
sns.barplot(data=top15_genres, x='total_games', y='genre', palette='viridis')
plt.title('Figure 3: Top 15 Most Popular Genres on Steam', fontsize=14, fontweight='bold')
plt.xlabel('Number of Games', fontsize=12, fontweight='bold')
plt.ylabel('Genre', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "fig3_top_genres.png"), dpi=300)
plt.close()


# =============================================================================
# 3. RQ3: PRICE VS FEEDBACK & ENGAGEMENT
# =============================================================================
print("\n--- [RQ3] Analyzing Price Groups vs Feedback ---")

price_order = ['Free', '0-5', '5-15', '15-30', '30-60', '60+']
df_games['price_group'] = pd.Categorical(df_games['price_group'], categories=price_order, ordered=True)

price_group_summary = df_games.groupby('price_group', observed=False).agg(
    total_games=('appid', 'count'),
    avg_reviews=('num_reviews_total', 'mean'),
    median_reviews=('num_reviews_total', 'median'),
    avg_positive_pct=('pct_pos_total', lambda x: x[x > 0].mean()),
    avg_playtime=('average_playtime_forever', 'mean'),
    avg_peak_ccu=('peak_ccu', 'mean')
).reset_index()

price_group_summary.round(2).to_csv(os.path.join(RESULTS_DIR, "rq3_price_group_summary.csv"), index=False)

# Chart 4: Price Group vs Average Reviews & Positive Rating
fig, ax1 = plt.subplots(figsize=(10, 6))
x = np.arange(len(price_order))
width = 0.35

rects1 = ax1.bar(x - width/2, price_group_summary['avg_reviews'], width, label='Avg Reviews Count', color='#ff7f0e')
ax1.set_ylabel('Average Reviews Count', color='#ff7f0e', fontsize=12, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(price_order)
ax1.set_xlabel('Price Tier ($)', fontsize=12, fontweight='bold')

ax2 = ax1.twinx()
rects2 = ax2.plot(x, price_group_summary['avg_positive_pct'], color='#2ca02c', marker='D', linewidth=2.5, label='Avg Positive Rating (%)')
ax2.set_ylabel('Average Positive Rating (%)', color='#2ca02c', fontsize=12, fontweight='bold')
ax2.set_ylim(50, 100)

plt.title('Figure 4: Average Reviews & Rating Across Price Tiers', fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "fig4_price_tier_feedback.png"), dpi=300)
plt.close()


# =============================================================================
# 4. RQ4: ANOMALY DETECTION (OUTLIERS)
# =============================================================================
print("\n--- [RQ4] Detecting Market Anomalies ---")

# Anomaly 1: Free/Cheap games (<= $5) with massive reviews (> 50k)
anom1 = df_games[(df_games['price'] <= 5.0) & (df_games['num_reviews_total'] > 50000)][
    ['appid', 'name', 'price', 'num_reviews_total', 'pct_pos_total', 'peak_ccu']
].sort_values(by='num_reviews_total', ascending=False)
anom1.to_csv(os.path.join(RESULTS_DIR, "rq4_cheap_games_huge_reviews.csv"), index=False)

# Anomaly 2: High Price (>= $40) with very low reviews (< 100)
anom2 = df_games[(df_games['price'] >= 40.0) & (df_games['num_reviews_total'] < 100)][
    ['appid', 'name', 'price', 'num_reviews_total', 'pct_pos_total']
].sort_values(by='price', ascending=False)
anom2.to_csv(os.path.join(RESULTS_DIR, "rq4_expensive_games_low_reviews.csv"), index=False)

# Chart 5: Scatter Plot Outliers (Price vs Total Reviews)
plt.figure(figsize=(11, 7))
df_plot = df_games[df_games['num_reviews_total'] > 1000]
plt.scatter(df_plot['price'], df_plot['num_reviews_total'], alpha=0.5, c=df_plot['pct_pos_total'], cmap='RdYlGn', s=35)
cbar = plt.colorbar()
cbar.set_label('Positive Rating (%)', fontsize=11)
plt.yscale('log')
plt.title('Figure 5: Price vs Total Reviews Scatter Plot (Log Scale)', fontsize=14, fontweight='bold')
plt.xlabel('Price ($)', fontsize=12, fontweight='bold')
plt.ylabel('Total Reviews (Log Scale)', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, "fig5_price_vs_reviews_outliers.png"), dpi=300)
plt.close()

print(f"\nAnalysis complete! Results saved to '{RESULTS_DIR}' and figures to '{FIGURES_DIR}'.")
