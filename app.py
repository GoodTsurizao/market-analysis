from flask import Flask, render_template, request
import subprocess
import sys
import os
import re

app = Flask(__name__, template_folder='.')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['GET', 'POST'])
def scrape_page():
    output = ""
    if request.method == 'POST':
        # スクレイピングを実行
        script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'scraping', 'scraping_main.py')
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        output = "スクレイピング実行結果:\n" + result.stdout
        if result.stderr:
            output += "\nエラー:\n" + result.stderr
    return render_template('pages/scrape.html', output=output)

@app.route('/analyze', methods=['GET', 'POST'])
def analyze_page():
    # data/processed 内の JSON ファイルリストを取得
    processed_dir = os.path.join(os.path.dirname(__file__), 'data', 'processed')
    files = sorted(
        [f for f in os.listdir(processed_dir) if f.endswith('.json')],
        reverse=True
    )
    
    output = ""
    if request.method == 'POST':
        selected_file = request.form.get('file')
        if selected_file and selected_file in files:
            # 選択されたファイルのフルパス
            file_path = os.path.join(processed_dir, selected_file)
            # 分析スクリプトを実行（ファイルパスを引数として渡す）
            script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'analysis', 'data_analysis.py')
            result = subprocess.run([sys.executable, script_path, file_path], capture_output=True, text=True, cwd=os.path.dirname(__file__))
            output = result.stdout
            if result.stderr:
                output += "\nエラー:\n" + result.stderr
    return render_template('pages/analyze.html', files=files, output=output)

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    # codes.txt を読み込む
    codes_path = os.path.join(os.path.dirname(__file__), 'data', 'raw', 'codes.txt')
    try:
        with open(codes_path, 'r', encoding='utf-8') as f:
            codes = f.read()
    except FileNotFoundError:
        codes = ""
    
    # scraping_config.py を読み込む
    config_path = os.path.join(os.path.dirname(__file__), 'scripts', 'scraping', 'scraping_config.py')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        page_max_match = re.search(r'PAGE_MAX\s*=\s*(\d+)', config_content)
        interval_match = re.search(r'INTERVAL_TIME\s*=\s*(\d+)', config_content)
        page_max = page_max_match.group(1) if page_max_match else '3'
        interval_time = interval_match.group(1) if interval_match else '2'
    except FileNotFoundError:
        config_content = ""
        page_max = '3'
        interval_time = '2'
    
    output = ""
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'save_codes':
            new_codes = request.form.get('codes', '')
            with open(codes_path, 'w', encoding='utf-8') as f:
                f.write(new_codes)
            codes = new_codes
            output = "codes.txt を保存しました。"
        elif action == 'save_config':
            new_page_max = request.form.get('page_max', '3')
            new_interval = request.form.get('interval_time', '2')
            print(f"Saving config: page_max={new_page_max}, interval={new_interval}")
            config_content = re.sub(r'PAGE_MAX\s*=\s*\d+', f'PAGE_MAX = {new_page_max}', config_content)
            config_content = re.sub(r'INTERVAL_TIME\s*=\s*\d+', f'INTERVAL_TIME = {new_interval}', config_content)
            print(f"Updated content:\n{config_content}")
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            page_max = new_page_max
            interval_time = new_interval
            output = "scraping_config.py を保存しました。"
    
    return render_template('pages/settings.html', codes=codes, page_max=page_max, interval_time=interval_time, output=output)

if __name__ == '__main__':
    app.run(debug=True)
