# 上場日を取得する用のスクレイピング

import bs4 # BeautifulSoupをインポート
import traceback # エラーの内容を出力するためにインポート
import time # 遅延させるためにインポート
import json # JSONを扱うためにインポート
import datetime # 日時を取得するためにインポート
from selenium import webdriver # Seleniumをインポート
from selenium.webdriver.chrome.options import Options # Chromeのオプションを設定するためにインポート
from selenium.webdriver.chrome.service import Service # Chromeドライバーのサービスを管理するためにインポート
from selenium.webdriver.support.ui import WebDriverWait # ページの読み込みを待つためにインポート
from selenium.webdriver.support import expected_conditions as EC # ページの読み込みを待つ条件を指定するためにインポート
from selenium.webdriver.common.by import By # ページの要素を指定するためにインポート
import scraping_config as config # 別ファイルに定数をまとめる場合は、config.pyなどを作成してそこに定数を記載することができます。

# 定数の定義
CHROMEDRIVER = r"C:\VSCode\WorkSpace\drivers\chromedriver.exe" # Chromeドライバーのパス
 
 
# ドライバー準備（固定）
def get_driver():
    options = Options() # オプションの作成
    # options.add_argument('--headless') # 実行時にブラウザを非表示にするオプション
    service = Service(CHROMEDRIVER) # ドライバーのパスを指定
    driver = webdriver.Chrome(service=service, options=options) # ドライバーを作成
    return driver
 
# URLからページのソースを取得する（固定）
def get_source_from_page_main(driver, url):
    driver.get(url) # URLにアクセス
    WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))) # ページが完全に読み込まれるまで待機
    page = driver.page_source # ページのソースを取得
    return page

# メインページのソースからスクレイピングする
def get_data_from_source(src):
    soup = bs4.BeautifulSoup(src, features='lxml')  #BeautifulSoupオブジェクトを作成
    try:
        stock_code = ""
        zika_gaku = ""

        # 会社基本情報 取得
        main_elem = soup.find("section", class_=config.MAIN2_CLASS)
        if main_elem: # メインコンテナが見つかった場合のみ処理を続行
            # 証券コードを取得
            stock_code_elem = main_elem.find("span", class_=config.STOCK_CODE_CLASS2)
            if stock_code_elem:
                stock_code = stock_code_elem.text

            # 時価総額を取得
            zika_gaku_elem = main_elem.find("td", class_=config.ZIKA_GAKU_CLASS)
            if zika_gaku_elem:
                zika_gaku = zika_gaku_elem.text

        info = {
            "zika": zika_gaku,
            "stock_code": stock_code
        }
    
        return info

    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None
 
# 証券コード一覧取得
def get_code_list():
    with open('data/raw/codes.txt', 'r', encoding='utf-8') as f:
        result = [line.strip() for line in f if line.strip()]
    return result

# メイン処理
if __name__ == "__main__":
 
    code_list = get_code_list()
 
    base_url = "https://kabu.hayauma.net/kabuka/"
 
    # ブラウザのdriver取得
    driver = get_driver()
 
    # ページカウンター制御
    page_counter = 0
 
    all_info = []  # すべての情報をまとめるリスト
 
    for code in code_list:
 
        page_counter = page_counter + 1
#        target_url = base_url + str(code) + "/corporate"
        target_url = base_url + str(code) + "/1996.html"

        # ページのソース取得
        try:
            source = get_source_from_page_main(driver, target_url)

        # ソースからデータ抽出
            data = get_data_from_source(source)
 
            if data:
                all_info.append(data)
        except Exception:
            print(f"timeout or fetch error: code={code}")
            continue
 
        # 改ページ処理を抜ける
        if page_counter == config.PAGE_MAX:
            break
 
        # 間隔を設ける(秒単位）
        time.sleep(config.INTERVAL_TIME)
 
    # 閉じる
    driver.quit()
 
    # 全部の情報をまとめて出力
    print(all_info)
 
    # 実行日時を取得してファイル名に追加
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f'data/processed/scraping_data_{current_time}.json'
    # JSONファイルに保存
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_info, f, ensure_ascii=False, indent=4)
