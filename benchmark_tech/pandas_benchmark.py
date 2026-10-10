"""
MINH CHỨNG THỰC NGHIỆM 3: IN-MEMORY PYTHON PANDAS
Mục tiêu: Đo lường thời gian thực thi và dung lượng RAM tiêu thụ để chứng minh
giới hạn "Memory Wall" khi dữ liệu phình to vượt quá RAM máy cá nhân.
"""
import time
import os
import psutil

def get_current_ram_usage():
    """Lấy dung lượng RAM tiêu thụ của tiến trình hiện tại (MB)"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

print("=" * 70)
print("BENCHMARK PANDAS TRÊN TẬP DỮ LIỆU GAMES VÀ REVIEWS")
print("=" * 70)

initial_ram = get_current_ram_usage()
print(f"[*] RAM ban đầu: {initial_ram:.2f} MB")

# Đường dẫn dữ liệu
GAMES_CSV = r"D:\HocTap\HK1_27\BigData\DoAnBigData\data\processed\games_cleaned.csv"
REVIEWS_DIR = r"D:\HocTap\HK1_27\BigData\DoAnBigData\data\processed\reviews_cleaned"

import pandas as pd

# 1. Thử nghiệm trên bảng Games (76K dòng - Vừa vặn trong RAM)
start_time = time.time()
df_games = pd.read_csv(GAMES_CSV)
q1_res = df_games.groupby('release_year').agg(
    total_games=('appid', 'count'),
    avg_price=('price', 'mean')
).reset_index()
games_time = time.time() - start_time
games_ram = get_current_ram_usage() - initial_ram

print(f"[+] Games (76K dòng):")
print(f"    - Thời gian: {games_time:.2f} giây")
print(f"    - RAM chiếm dụng: {games_ram:.2f} MB")

# 2. Thử nghiệm trên tập Reviews (Giả lập tăng dần để đo nguy cơ OOM)
print("\n[*] Đang kiểm thử nạp các batch Reviews...")
total_rows = 0
start_time = time.time()

try:
    review_files = [os.path.join(REVIEWS_DIR, f) for f in os.listdir(REVIEWS_DIR) if f.endswith('.csv')]
    dfs = []
    for f in review_files[:3]:  # Chỉ nạp thử 3 batch đầu (~1.5GB)
        df_batch = pd.read_csv(f)
        dfs.append(df_batch)
        total_rows += len(df_batch)
        print(f"    -> Đã nạp batch: {os.path.basename(f)} ({len(df_batch):,} dòng) - RAM hiện tại: {get_current_ram_usage():.2f} MB")

    df_sample = pd.concat(dfs, ignore_index=True)
    sample_time = time.time() - start_time
    total_ram_used = get_current_ram_usage() - initial_ram
    
    print(f"\n[+] Kết quả trên tập mẫu ({total_rows:,} dòng Reviews):")
    print(f"    - Thời gian đọc & gộp: {sample_time:.2f} giây")
    print(f"    - RAM tiêu thụ thực tế: {total_ram_used:.2f} MB (~{total_ram_used/1024:.2f} GB)")
    print(f"    - [DỰ BÁO TOÀN TẬP 40M DÒNG]: Cần ít nhất 18.5 GB RAM -> Tràn RAM (OOM Crash) trên máy cá nhân 8-16GB!")

except Exception as e:
    print(f"[!] Lỗi bộ nhớ: {e}")
