import os
import glob
import json
import sys

# コマンドライン引数でファイルパスを受け取る、なければデフォルト
if len(sys.argv) > 1:
    latest_file = sys.argv[1]
else:
    latest_file = os.path.join(os.path.dirname(__file__), '../../data/processed/scraping_data_20260329173837.json')

print(f"ファイルを読み込みます: {latest_file}")

# JSONファイルを読み込む
with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

    # データの分析
    print(f"読み込んだレコード数: {len(data)}")

    if data:
        # 市場ごとのカウント
        markets = {}
        for item in data:
            market = item.get('market', 'Unknown')
            markets[market] = markets.get(market, 0) + 1

        print("市場ごとのカウント:")
        for market, count in markets.items():
            print(f"  {market}: {count}")

        # 他の分析例: 会社名のリスト（最初の5つ）
        company_names = [item.get('company_name', '') for item in data if item.get('company_name')]
        print(f"\n会社名（最初の5つ）: {company_names[:5]}")

        # 市場テーマのカウント
        all_themes = []
        for item in data:
            themes = item.get('market_theme', [])
            all_themes.extend(themes)

        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        print("\n市場テーマのカウント:")
        for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {theme}: {count}")
    else:
        print("データが空です。")
