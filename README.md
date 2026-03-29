# 株データ分析プロジェクト

このプロジェクトは、Webスクレイピングにより株データを自動収集し、分析を行うWebアプリケーションです。Flaskフレームワークを使用したシンプルなUIで、スクレイピング実行、データ分析、設定編集が可能です。

## 機能

- **スクレイピング実行**: 指定された証券コードの株データを収集
- **データ分析**: 収集したデータを分析し、市場別カウントやテーマ別カウントを表示
- **設定編集**: スクレイピングの設定（改ページ最大、遷移間隔）とコードリストを編集

## 使用技術

- **Python**: メイン言語
- **Flask**: Webフレームワーク
- **Selenium**: Webブラウザ自動操作
- **BeautifulSoup**: HTML解析
- **ChromeDriver**: ブラウザドライバ

## インストールと実行

1. 依存関係のインストール:
   ```
   pip install -r requirements.txt
   ```

2. ChromeDriverの配置:
   `drivers/chromedriver.exe` にChromeDriverを配置

3. 実行:
   ```
   python app.py
   ```

4. ブラウザでアクセス:
   http://127.0.0.1:5000/

## ディレクトリ構成

```
project/
│
├── README.md              # プロジェクト概要
├── requirements.txt       # Python依存関係
├── app.py                 # Flask Webアプリケーション
│
├── data/
│   ├── raw/               # 元データ（codes.txt: 証券コードリスト）
│   └── processed/         # 加工済みデータ（JSONファイル）
│
├── drivers/               # ChromeDriver
│   └── chromedriver.exe
│
├── scripts/               # 実行スクリプト
│   ├── scraping/          # スクレイピング関連
│   │   ├── scraping_main.py
│   │   └── scraping_config.py
│   └── analysis/          # 分析関連
│       └── data_analysis.py
│
├── templates/             # HTMLテンプレート
│   ├── index.html         # メインページ
│   ├── scrape.html        # スクレイピングページ
│   ├── analyze.html       # 分析ページ
│   └── settings.html      # 設定ページ
│
└── tests/                 # テストコード（未実装）
```

## 設計方針

### 1. 役割の分離

- `scripts/` : 実行スクリプト（スクレイピングと分析のエントリーポイント）
- `data/` : データの保存
- `templates/` : UIテンプレート
- `app.py` : Webアプリのルーティングと処理

### 2. 設定の外部化

- `scraping_config.py` : スクレイピング設定
- `codes.txt` : 証券コードリスト

### 3. データの再現性

- 元データは `data/raw/` に保存
- 加工データは `data/processed/` に保存

## 使用方法

1. メインページから各機能にアクセス
2. 設定ページでコードリストとスクレイピング設定を編集
3. スクレイピングページでデータを収集
4. 分析ページで収集したデータを分析

## 注意事項

- スクレイピングは対象サイトの利用規約を確認してください
- 大量のアクセスは避け、適切な間隔を設定してください
