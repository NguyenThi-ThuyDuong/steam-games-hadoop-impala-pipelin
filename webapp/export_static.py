"""
Script xuất toàn bộ dashboard ra dạng Static HTML độc lập (Offline/Online).
File html này có thể nén gửi giáo viên, đưa lên GitHub Pages hoặc mở trực tiếp trên trình duyệt mà không cần cài Python/Flask.
"""
import os
import json
from app import app

def export_static_pages():
    output_dir = os.path.join(os.path.dirname(__file__), 'dist')
    os.makedirs(output_dir, exist_ok=True)
    
    routes = {
        'index.html': '/',
        'dashboard.html': '/dashboard',
        'architecture.html': '/architecture',
        'benchmark.html': '/benchmark',
        'data.html': '/data'
    }

    with app.test_client() as client:
        for filename, route in routes.items():
            print(f"Generating static {filename} from {route}...")
            res = client.get(route)
            if res.status_code == 200:
                filepath = os.path.join(output_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(res.get_data(as_text=True))
                print(f"  -> Saved: {filepath}")
            else:
                print(f"  -> ERROR {res.status_code} for {route}")

if __name__ == '__main__':
    export_static_pages()
    print("\n[SUCCESS] Export static pages to webapp/dist/ completed successfully!")
