import bs4 # BeautifulSoupをインポート
import traceback # エラーの内容を出力するためにインポート
import time # 遅延させるためにインポート
import json # JSONを扱うためにインポート
from selenium import webdriver # Seleniumをインポート
from selenium.webdriver.chrome.options import Options # Chromeのオプションを設定するためにインポート
from selenium.webdriver.chrome.service import Service # Chromeドライバーのサービスを管理するためにインポート
from selenium.webdriver.support.ui import WebDriverWait # ページの読み込みを待つためにインポート
from selenium.webdriver.support import expected_conditions as EC # ページの読み込みを待つ条件を指定するためにインポート
from selenium.webdriver.common.by import By # ページの要素を指定するためにインポート
import scraping_config as config # 別ファイルに定数をまとめる場合は、config.pyなどを作成してそこに定数を記載することができます。

# 定数の定義
CHROMEDRIVER = r"C:\VSCode\WorkSpace\drivers\chromedriver.exe" # Chromeドライバーのパス
PAGE_MAX = 3 # 改ページ（最大）
INTERVAL_TIME = 2 # 遷移間隔（秒）
 
 
# ドライバー準備（固定）
def get_driver():
    options = Options() # オプションの作成
    options.add_argument('--headless') # 実行時にブラウザを非表示にするオプション
    service = Service(CHROMEDRIVER) # ドライバーのパスを指定
    driver = webdriver.Chrome(service=service, options=options) # ドライバーを作成
    return driver
 
# URLからページのソースを取得する（固定）
def get_source_from_page_main(driver, url):
    driver.get(url) # URLにアクセス
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))) # ページが完全に読み込まれるまで待機
    page = driver.page_source # ページのソースを取得
    return page

# メインページのソースからスクレイピングする
def get_data_from_source(src):
    soup = bs4.BeautifulSoup(src, features='lxml')  #BeautifulSoupオブジェクトを作成
    try:
        company_name = ""
        stock_code = ""
        market = ""
        characteristics = ""
        industry = []
        market_theme = []

        # 会社基本情報 取得
        main_elem = soup.find("div", class_=config.MAIN_CLASS)
        if main_elem: # メインコンテナが見つかった場合のみ処理を続行
            # 証券コードを取得
            stock_code_elem = main_elem.find("span", class_=config.STOCK_CODE_CLASS)
            if stock_code_elem:
                stock_code = stock_code_elem.text.strip()

            # 市場区分を取得
            market_elem = main_elem.find("span", class_=config.MARKET_CLASS)
            if market_elem:
                market = market_elem.text.strip()

            # 社名を取得
            company_name_elem = soup.find("div", class_=config.COMPANY_NAME_CLASS)
            if company_name_elem:
                company_name = company_name_elem.text
            
            # 特色を取得
            characteristics_elem = soup.find("dl", class_=config.CHARACTERISTICS_CLASS)
            if characteristics_elem:
                characteristics = characteristics_elem.text.strip().split('\n')[1].strip()

            # 所属業界を取得
            industry_elem = soup.find("div", class_=config.INDUSTRY_CLASS)
            if industry_elem:
                industry = industry_elem.text.strip()

            # 市場テーマを取得
            market_theme_elem = soup.find("div", class_=config.MARKET_THEME_CLASS)
            if market_theme_elem:
                market_theme_list = market_theme_elem.text.strip()
                for theme in market_theme_list.split('\n'):
                    if theme.strip() and theme.strip() != "他":
                        market_theme.append(theme.strip())

        info = {
            "stock_code": stock_code,
            "market": market,
            "company_name": company_name,
            "characteristics": characteristics,
#            "industry": industry,
            "market_theme": market_theme
        }
    
        return info

    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None
 
# 証券コード一覧取得
def get_code_list():
#    result = ['1375', '1376', '1377', '1379', '1380', '1381', '1382', '1383', '1384']
    result = ['431A']
    return result

# メイン処理
if __name__ == "__main__":
 
    code_list = get_code_list()
 
    base_url = "https://shikiho.toyokeizai.net/stocks/"
 
    # ブラウザのdriver取得
    driver = get_driver()
 
    # ページカウンター制御
    page_counter = 0
 
    all_info = []  # すべての情報をまとめるリスト
 
    for code in code_list:
 
        page_counter = page_counter + 1
        target_url = base_url + str(code) + "/"
 
        # ページのソース取得
        source = get_source_from_page_main(driver, target_url)

        # ソースからデータ抽出
        data = get_data_from_source(source)
 
        if data:
            all_info.append(data)
 
        # 改ページ処理を抜ける
        if page_counter == PAGE_MAX:
            break
 
        # 間隔を設ける(秒単位）
        time.sleep(INTERVAL_TIME)
 
    # 閉じる
    driver.quit()
 
    # 全部の情報をまとめて出力
    print(all_info)
 
    # JSONファイルに保存
    with open('data/processed/scraping_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_info, f, ensure_ascii=False, indent=4)
