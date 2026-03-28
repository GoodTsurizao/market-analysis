import bs4
import traceback
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
 
CHROMEDRIVER = r"C:\VSCode\WorkSpace\drivers\chromedriver.exe"
# 改ページ（最大）
PAGE_MAX = 3
# 遷移間隔（秒）
INTERVAL_TIME = 2
 
 
# ドライバー準備
def get_driver():
    options = Options()
    options.add_argument('--headless')
    service = Service(CHROMEDRIVER)
    driver = webdriver.Chrome(service=service, options=options)
    return driver
 
 
def get_source_from_page(driver, url):
    # ターゲット
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'p-contents')))
    page = driver.page_source
 
    return page
 
 
# ソースからスクレイピングする
def get_data_from_source(src):
    # スクレイピングする
    soup = bs4.BeautifulSoup(src, features='lxml')
 
    try:
        company_name = ""
        information = ""
        current = None
        rival = []
        stock = []

        main_elem = soup.find("div", class_="main")
        if main_elem:
            name_elem = main_elem.find(class_="name")
            if name_elem:
                company_name = name_elem.text
 
        information_elem = soup.find("div", class_="information")
        if information_elem:
            p_tag_all = information_elem.find_all('p')
            for p_tag in p_tag_all:
                tmp_text = p_tag.text
                if tmp_text:
                    information = information + str(tmp_text)
            # 比較会社
            rival = []
            li_tag_all = information_elem.find_all("li")
            for li_tag in li_tag_all:
                tmp_text = li_tag.text
                tmp_list = tmp_text.split(" ")
                if len(tmp_list) > 0:
                    # 会社名にスペースがある場合は会社名の一部だけ（そもそも、codeさえ取得できればOK)
                    tmp_company = {"code": tmp_list[0],
                             "name": tmp_list[1]}
                    rival.append(tmp_company)
 
        section_elem = soup.find("div", class_="section")
        if section_elem:
            current_elem = section_elem.find(class_="current")
            if current_elem:
                current = current_elem.text
            # stockの下の各行
            stock = []
            dl_tag_all = section_elem.find(class_="stock").find_all("dl")
            for dl_tag in dl_tag_all:
                dt_tag = dl_tag.find("dt")
                dd_tag = dl_tag.find("dd")
                if dt_tag and dd_tag:
                    dt_text = dt_tag.text
                    dd_text = dd_tag.text
                    tmp_row = {"title": dt_text,
                             "data": dd_text}
                    stock.append(tmp_row)
 
        info = {"name": company_name,
                "information": information,
                "rival": rival,
                "current": current,
                "stock": stock}
 
        return info
 
    except Exception as e:
 
        print("Exception\n" + traceback.format_exc())
 
        return None
 
# 証券コード一覧取得
def get_code_list():
    result = ['1375', '1376', '1377', '1379', '1380', '1381', '1382', '1383', '1384']
    return result
 
 
if __name__ == "__main__":
 
    code_list = get_code_list()
 
    base_url = "https://shikiho.jp/stocks/"
 
    # ブラウザのdriver取得
    driver = get_driver()
 
    # ページカウンター制御
    page_counter = 0
 
    for code in code_list:
 
        page_counter = page_counter + 1
        target_url = base_url + str(code) + "/"
 
        # ページのソース取得
        source = get_source_from_page(driver, target_url)
        # ソースからデータ抽出
        data = get_data_from_source(source)
 
        print(data)
 
        # 改ページ処理を抜ける
        if page_counter == PAGE_MAX:
            break
 
        # 間隔を設ける(秒単位）
        time.sleep(INTERVAL_TIME)
 
    # 閉じる
    driver.quit()