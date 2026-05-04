# 設定ファイル
# スクレイピングで使用するクラス名などの設定

# スクレイピング設定
PAGE_MAX = 884 # 改ページ（最大）
INTERVAL_TIME = 1 # 遷移間隔（秒）

# ----------------------------------------------------------------------

# mainのコンテナ
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

# ----------------------------------------------------------------------

# main2のコンテナ
MAIN2_CLASS = "clearfix"
ZIKA_GAKU_CLASS = "v_zika2" # 時価総額(td)
STOCK_CODE_CLASS2 = "inline-block" # 証券コード(span)

# ----------------------------------------------------------------------

# main3のコンテナ
MAIN3_CLASS = "clearfix"
MAIN3__CLASS = "v_zika2" # 時価総額(td)
MAIN3__CLASS = "inline-block" # 証券コード(span)


