# 設定ファイル
# スクレイピングで使用するクラス名などの設定

# スクレイピング設定
PAGE_MAX = 4445 # 改ページ（最大）
INTERVAL_TIME = 2 # 遷移間隔（秒）

# メインぺージのコンテナ
MAIN_CLASS = "overview__main"

# メインページ
STOCK_CODE_CLASS = "head__top__item__code" # 証券コード(span)
MARKET_CLASS = "head__top__item__name" # 市場区分(span)
COMPANY_NAME_CLASS = "head__main__left__title" # 会社名(div)
CHARACTERISTICS_CLASS = "information__list" # 特色(div)
INDUSTRY_CLASS = "industry__items" # 所属業界(div)
MARKET_THEME_CLASS = "theme__items" # 市場テーマ(div)

# プロフィールページのコンテナ
COMPANY_INFO_CLASS = "company-content"
COMPANY_INFO_ID = "companyBasicInformation"

#プロフィール
LISTING_DATE_CLASS = "company-content__profile"




