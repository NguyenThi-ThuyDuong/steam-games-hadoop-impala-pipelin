"""
Module tải dữ liệu CSV từ thư mục datamining/results.
"""
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, '..', 'datamining', 'results')


def _load_csv(filename):
    filepath = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[WARNING] File not found: {filepath}")
        return pd.DataFrame()
    return pd.read_csv(filepath)


def load_all_data():
    data = {
        'q1_yearly': _load_csv('q1_yearly_releases_f2p.csv'),
        'q2_yoy': _load_csv('q2_yoy_growth.csv'),
        'q3_genres_era': _load_csv('q3_genres_by_era.csv'),
        'q4_genre_profile': _load_csv('q4_genre_profile.csv'),
        'q5_price': _load_csv('q5_price_category_summary.csv'),
        'q6_developers': _load_csv('q6_top_developers.csv'),
        'q7_publishers': _load_csv('q7_top_publishers.csv'),
        'q8_rating_dist': _load_csv('q8_genre_rating_distribution.csv'),
        'q9_cheap': _load_csv('q9_cheap_huge_reviews.csv'),
        'q9_expensive': _load_csv('q9_expensive_few_reviews.csv'),
        'q10_platform': _load_csv('q10_platform_strategy.csv'),
    }
    return data
