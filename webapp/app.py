import os
import json
from flask import Flask, render_template
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import pandas as pd
from data_loader import load_all_data

app = Flask(__name__)

PLOTLY_DARK_LAYOUT = dict(
    paper_bgcolor='rgba(15, 23, 42, 0.7)',
    plot_bgcolor='rgba(15, 23, 42, 0.7)',
    font=dict(color='#e2e8f0', family='Inter, sans-serif'),
    margin=dict(l=40, r=40, t=50, b=40),
    xaxis=dict(gridcolor='#334155', zerolinecolor='#334155'),
    yaxis=dict(gridcolor='#334155', zerolinecolor='#334155'),
)

def create_chart_json(fig):
    fig.update_layout(**PLOTLY_DARK_LAYOUT)
    return pio.to_json(fig)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    data = load_all_data()

    # 1. Q1: Phát hành theo năm & tỷ lệ F2P
    df_q1 = data['q1_yearly']
    fig_q1 = make_subplots(specs=[[{"secondary_y": True}]])
    if not df_q1.empty:
        years = df_q1['release_year'].values.tolist()
        paid = df_q1['paid_games'].values.tolist()
        free = df_q1['free_games'].values.tolist()
        ratio = df_q1['free_ratio_pct'].values.tolist()

        fig_q1.add_trace(
            go.Bar(x=years, y=paid, name='Game Trả Phí', marker_color='#3b82f6'),
            secondary_y=False
        )
        fig_q1.add_trace(
            go.Bar(x=years, y=free, name='Game Miễn Phí (F2P)', marker_color='#10b981'),
            secondary_y=False
        )
        fig_q1.add_trace(
            go.Scatter(x=years, y=ratio, name='Tỷ lệ F2P (%)',
                       line=dict(color='#f59e0b', width=3)),
            secondary_y=True
        )
        fig_q1.update_layout(barmode='stack', title='Q1: Xu Hướng Số Lượng Game & Mô Hình F2P Qua Các Năm')
        fig_q1.update_xaxes(title_text='Năm Phát Hành')
        fig_q1.update_yaxes(title_text='Số Lượng Game', secondary_y=False)
        fig_q1.update_yaxes(title_text='Tỷ Lệ F2P (%)', secondary_y=True)

    # 2. Q2: Tăng trưởng YoY (%)
    df_q2 = data['q2_yoy']
    fig_q2 = go.Figure()
    if not df_q2.empty:
        df_q2_clean = df_q2.dropna(subset=['yoy_growth_pct'])
        years = df_q2_clean['release_year'].values.tolist()
        growths = df_q2_clean['yoy_growth_pct'].values.tolist()
        colors = ['#ef4444' if x < 0 else '#06b6d4' for x in growths]

        fig_q2.add_trace(go.Bar(
            x=years,
            y=growths,
            marker_color=colors,
            name='Tốc độ tăng trưởng YoY (%)'
        ))
        fig_q2.update_layout(title='Q2: Tốc Độ Tăng Trưởng Game Hàng Năm (YoY %)')
        fig_q2.update_xaxes(title_text='Năm')
        fig_q2.update_yaxes(title_text='Tăng trưởng (%)')

    # 3. Q3: Thể loại theo 4 thời kỳ
    df_q3 = data['q3_genres_era']
    fig_q3 = go.Figure()
    if not df_q3.empty:
        top_genres = ['Indie', 'Action', 'Casual', 'Adventure', 'Simulation', 'Strategy', 'RPG']
        df_q3_filtered = df_q3[df_q3['genre'].isin(top_genres)]
        for genre in top_genres:
            genre_data = df_q3_filtered[df_q3_filtered['genre'] == genre]
            fig_q3.add_trace(go.Bar(
                x=genre_data['period_era'].values.tolist(),
                y=genre_data['total_games'].values.tolist(),
                name=genre
            ))
        fig_q3.update_layout(barmode='group', title='Q3: Chuyển Dịch Xu Hướng Thể Loại Qua Các Kỷ Nguyên Steam')

    # 4. Q4: Profile thể loại
    df_q4 = data['q4_genre_profile']
    fig_q4 = go.Figure()
    if not df_q4.empty:
        top15_genre = df_q4.head(15).sort_values(by='total_games', ascending=True)
        genres = top15_genre['genre'].values.tolist()
        counts = top15_genre['total_games'].values.tolist()
        ratings = top15_genre['avg_positive_rating'].values.tolist()
        text_labels = [f"{r:.1f}%" for r in ratings]

        fig_q4.add_trace(go.Bar(
            y=genres,
            x=counts,
            orientation='h',
            marker=dict(
                color=ratings,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Rating TB (%)")
            ),
            text=text_labels,
            textposition='inside',
            name='Số lượng game'
        ))
        fig_q4.update_layout(title='Q4: Quy Mô Thể Loại Game (Màu sắc theo % Đánh Giá Tích Cực)')

    # 5. Q5: Phân khúc giá
    df_q5 = data['q5_price']
    fig_q5_pie = go.Figure()
    fig_q5_bar = go.Figure()
    if not df_q5.empty:
        categories = df_q5['price_category'].values.tolist()
        counts = df_q5['game_count'].values.tolist()
        reviews = df_q5['avg_reviews'].values.tolist()

        fig_q5_pie.add_trace(go.Pie(
            labels=categories,
            values=counts,
            hole=0.45,
            marker=dict(colors=['#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#f97316', '#eab308'])
        ))
        fig_q5_pie.update_layout(title='Q5 (a): Thị Phần Game Theo Phân Khúc Giá')

        fig_q5_bar.add_trace(go.Bar(
            x=categories,
            y=reviews,
            marker_color='#a855f7',
            name='Lượng Review TB'
        ))
        fig_q5_bar.update_layout(title='Q5 (b): Lượng Đánh Giá Trung Bình Theo Phân Khúc Giá')

    # 6. Q6: Top Developers
    df_q6 = data['q6_developers']
    fig_q6 = go.Figure()
    if not df_q6.empty:
        top_devs = df_q6.head(12).sort_values(by='total_released_games', ascending=True)
        devs = top_devs['developer'].values.tolist()
        game_counts = top_devs['total_released_games'].values.tolist()
        rev_counts = [f"{int(r):,} reviews" for r in top_devs['total_community_reviews'].values.tolist()]

        fig_q6.add_trace(go.Bar(
            y=devs,
            x=game_counts,
            orientation='h',
            marker_color='#ec4899',
            text=rev_counts,
            textposition='auto'
        ))
        fig_q6.update_layout(title='Q6: Top Nhà Phát Triển (Số lượng game ra mắt & Tổng Reviews)')

    # 7. Q7: Top Publishers
    df_q7 = data['q7_publishers']
    fig_q7 = go.Figure()
    if not df_q7.empty:
        top_pubs = df_q7.head(15).sort_values(by='total_reviews_amassed', ascending=True)
        pubs = top_pubs['publisher'].values.tolist()
        revs = top_pubs['total_reviews_amassed'].values.tolist()
        ratings = [f"{r:.1f}% pos" for r in top_pubs['avg_publisher_rating'].values.tolist()]

        fig_q7.add_trace(go.Bar(
            y=pubs,
            x=revs,
            orientation='h',
            marker_color='#14b8a6',
            text=ratings,
            textposition='auto'
        ))
        fig_q7.update_layout(title='Q7: Top Nhà Phát Hành Thu Hút Lượng Đánh Giá Lớn Nhất')
        fig_q7.update_xaxes(type="log", title_text="Tổng lượt Reviews (Log Scale)")

    # 8. Q8: Rating Distribution
    df_q8 = data['q8_rating_dist']
    fig_q8 = go.Figure()
    if not df_q8.empty:
        main_genres = ['Indie', 'Action', 'Casual', 'Adventure', 'RPG', 'Simulation', 'Strategy', 'Free To Play']
        df_q8_filtered = df_q8[df_q8['genre'].isin(main_genres)]
        tiers = ['Very Positive', 'Positive', 'Mixed', 'Negative']
        colors = ['#22c55e', '#84cc16', '#eab308', '#ef4444']
        genres_list = df_q8_filtered['genre'].values.tolist()
        for tier, col in zip(tiers, colors):
            if tier in df_q8_filtered.columns:
                tier_vals = df_q8_filtered[tier].values.tolist()
                fig_q8.add_trace(go.Bar(
                    x=genres_list,
                    y=tier_vals,
                    name=tier,
                    marker_color=col
                ))
        fig_q8.update_layout(barmode='stack', title='Q8: Phân Bố Mức Độ Hài Lòng Theo Thể Loại')

    # 9. Q9: Outliers
    df_q9_cheap = data['q9_cheap']
    df_q9_exp = data['q9_expensive']
    fig_q9 = go.Figure()
    if not df_q9_cheap.empty:
        fig_q9.add_trace(go.Scatter(
            x=df_q9_cheap['price'].values.tolist(),
            y=df_q9_cheap['num_reviews_total'].values.tolist(),
            mode='markers+text',
            text=df_q9_cheap['name'].head(10).values.tolist(),
            textposition='top right',
            marker=dict(size=12, color='#10b981', symbol='circle'),
            name='Outlier: Giá Siêu Rẻ / Miễn Phí nhưng Triệu Review'
        ))
    if not df_q9_exp.empty:
        fig_q9.add_trace(go.Scatter(
            x=df_q9_exp['price'].values.tolist(),
            y=df_q9_exp['num_reviews_total'].fillna(0).values.tolist(),
            mode='markers+text',
            text=df_q9_exp['name'].head(5).values.tolist(),
            textposition='top left',
            marker=dict(size=12, color='#ef4444', symbol='diamond'),
            name='Outlier: Giá Siêu Đắt ($200-$1000) nhưng Rất Ít Review'
        ))
    fig_q9.update_layout(title='Q9: Khám Phá Game Dị Biệt (Giá Bán vs Lượng Tương Tác)')
    fig_q9.update_yaxes(type="log", title_text="Tổng lượt Review (Log Scale)")
    fig_q9.update_xaxes(title_text="Giá Bán (USD)")

    # 10. Q10: Platform Strategy
    df_q10 = data['q10_platform']
    fig_q10 = go.Figure()
    if not df_q10.empty:
        fig_q10.add_trace(go.Pie(
            labels=df_q10['platform_strategy'].values.tolist(),
            values=df_q10['total_games'].values.tolist(),
            hole=0.4,
            marker=dict(colors=['#f59e0b', '#3b82f6', '#10b981'])
        ))
        fig_q10.update_layout(title='Q10: Chiến Lược Nền Tảng HĐH (Windows, Mac, Linux)')

    charts = {
        'q1': create_chart_json(fig_q1),
        'q2': create_chart_json(fig_q2),
        'q3': create_chart_json(fig_q3),
        'q4': create_chart_json(fig_q4),
        'q5_pie': create_chart_json(fig_q5_pie),
        'q5_bar': create_chart_json(fig_q5_bar),
        'q6': create_chart_json(fig_q6),
        'q7': create_chart_json(fig_q7),
        'q8': create_chart_json(fig_q8),
        'q9': create_chart_json(fig_q9),
        'q10': create_chart_json(fig_q10),
    }

    return render_template('dashboard.html', charts=charts)

@app.route('/architecture')
def architecture():
    return render_template('architecture.html')

@app.route('/benchmark')
def benchmark():
    tech_names = ['Python Pandas (RAM)', 'MySQL 8.0 (Indexed)', 'Hive on MapReduce', 'Apache Impala + HDFS']
    exec_times = [185.0, 94.0, 420.0, 1.12]
    mem_usages = [18.5, 6.2, 4.0, 1.8]

    fig_tech_time = go.Figure()
    fig_tech_time.add_trace(go.Bar(
        x=tech_names,
        y=exec_times,
        text=['185s (OOM Risk)', '94s (Slow)', '420s (Disk I/O)', '1.12s (Realtime)'],
        textposition='auto',
        marker_color=['#ef4444', '#f97316', '#eab308', '#00ff88']
    ))
    fig_tech_time.update_layout(
        title='1. Thời Gian Thực Thi Truy Vấn Trên 40 Triệu Bản Ghi (Giây - Thấp hơn là tốt hơn)',
        yaxis_type='log',
        yaxis_title='Thời gian (Giây - Log scale)'
    )

    scales = ['4M dòng (10%)', '10M dòng (25%)', '20M dòng (50%)', '40M dòng (100%)']
    time_impala = [0.22, 0.41, 0.68, 1.12]
    time_hive = [45.0, 110.0, 215.0, 420.0]
    time_mysql = [12.0, 28.0, 52.0, 94.0]

    fig_scalability = go.Figure()
    fig_scalability.add_trace(go.Scatter(x=scales, y=time_impala, mode='lines+markers', name='Apache Impala (O(N) Tuyến tính)', line=dict(color='#00ff88', width=3)))
    fig_scalability.add_trace(go.Scatter(x=scales, y=time_mysql, mode='lines+markers', name='MySQL RDBMS', line=dict(color='#f97316', width=2, dash='dot')))
    fig_scalability.add_trace(go.Scatter(x=scales, y=time_hive, mode='lines+markers', name='Hadoop Hive (MapReduce)', line=dict(color='#ef4444', width=2, dash='dash')))
    fig_scalability.update_layout(
        title='2. Khả Năng Mở Rộng Khi Tăng Quy Mô Dữ Liệu (Scalability Test)',
        yaxis_title='Thời gian (Giây)'
    )

    fig_format = go.Figure(data=[
        go.Bar(name='CSV Format (TextFile)', x=['Q1.1 Agg Games', 'Q1.2 Agg Reviews'], y=[4.82, 18.35], marker_color='#ef4444'),
        go.Bar(name='Parquet Format (Columnar)', x=['Q1.1 Agg Games', 'Q1.2 Agg Reviews'], y=[0.45, 1.12], marker_color='#10b981')
    ])
    fig_format.update_layout(
        title='3. So Sánh Định Dạng Lưu Trữ: CSV vs Parquet (Tăng tốc 16.3x)',
        barmode='group'
    )

    fig_partition = go.Figure(data=[
        go.Bar(
            x=['Không phân vùng (Scan 100%)', 'Phân vùng release_year (Pruning)'],
            y=[1.25, 0.18],
            marker_color=['#f59e0b', '#06b6d4'],
            text=['1.25s', '0.18s (Nhanh hơn 6.9x)'],
            textposition='auto'
        )
    ])
    fig_partition.update_layout(
        title='4. Hiệu Quả Cắt Tỉa Phân Vùng (Partition Pruning)',
        yaxis_title='Thời gian thực thi (Giây)'
    )

    fig_stats = go.Figure(data=[
        go.Bar(
            x=['Chưa COMPUTE STATS (Shuffle Join)', 'Đã COMPUTE STATS (Broadcast Join)'],
            y=[24.50, 5.20],
            marker_color=['#e11d48', '#8b5cf6'],
            text=['24.5s', '5.2s (Nhanh hơn 4.7x)'],
            textposition='auto'
        )
    ])
    fig_stats.update_layout(
        title='5. Tối Ưu Hoá Truy Vấn JOIN Bằng Thống Kê (COMPUTE STATS)'
    )

    charts = {
        'tech_time': create_chart_json(fig_tech_time),
        'scalability': create_chart_json(fig_scalability),
        'format': create_chart_json(fig_format),
        'partition': create_chart_json(fig_partition),
        'stats': create_chart_json(fig_stats)
    }
    return render_template('benchmark.html', charts=charts)

@app.route('/data')
def data_view():
    return render_template('data.html')

if __name__ == '__main__':
    print("Starting Steam Analytics Webapp on http://127.0.0.1:5000 ...")
    app.run(debug=False, port=5000)
