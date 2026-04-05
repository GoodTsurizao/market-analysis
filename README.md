# 市場データ収集・分析ツール

このプロジェクトは、企業ごとの市場情報を Web から取得し、取得済みデータを簡易分析できるローカル向けツールです。
`Flask` で操作画面を用意し、`Selenium` で対象ページを巡回し、取得結果を `JSON` として保存します。保存済みデータは別スクリプトで集計し、画面から確認できる構成になっています。

## できること

- 指定した証券コード一覧をもとに市場情報をスクレイピングする
- 取得結果を `data/processed/` に時刻付き JSON として保存する
- 保存済み JSON を選択して件数や市場別件数などを集計する
- 証券コード一覧とスクレイピング設定を画面上から更新する

## 想定している処理フロー

1. 設定画面で対象の証券コードとスクレイピング条件を調整する
2. スクレイピング画面からデータ収集を実行する
3. 収集結果を `data/processed/` に保存する
4. 分析画面で保存済み JSON を選び、集計結果を確認する

## プロジェクト構成

```text
.
├─ app.py
├─ README.md
├─ requirements.txt
├─ index.html
├─ pages/
│  ├─ scrape.html
│  ├─ analyze.html
│  └─ settings.html
├─ scripts/
│  ├─ scraping/
│  │  ├─ scraping_main.py
│  │  └─ scraping_config.py
│  └─ analysis/
│     └─ data_analysis.py
├─ data/
│  ├─ raw/
│  │  └─ codes.txt
│  └─ processed/
│     └─ scraping_data_*.json
├─ drivers/
│  └─ chromedriver.exe
└─ tests/
   └─ hello.py
```

## 各ディレクトリ・ファイルの役割

### ルート

- `app.py`
  Flask アプリ本体です。各画面のルーティングと、スクレイピング・分析スクリプトの呼び出しを担当します。

- `index.html`
  トップページです。スクレイピング画面、分析画面、設定画面への入口になっています。

- `requirements.txt`
  Python の依存パッケージ一覧です。現状は `flask` のみ記載されています。

### `pages/`

- `pages/scrape.html`
  スクレイピング実行用の画面です。実行ボタンを押すと `scraping_main.py` を呼び出します。

- `pages/analyze.html`
  分析対象の JSON ファイルを選択し、集計結果を表示する画面です。

- `pages/settings.html`
  証券コード一覧と、最大取得件数・待機時間などの設定を更新する画面です。

### `scripts/scraping/`

- `scripts/scraping/scraping_main.py`
  スクレイピング本体です。`codes.txt` から証券コードを読み込み、各コードのページを巡回して情報を抽出し、最終的に JSON ファイルへ保存します。

- `scripts/scraping/scraping_config.py`
  スクレイピング設定ファイルです。主に以下を管理しています。
  `PAGE_MAX`: 取得する最大件数
  `INTERVAL_TIME`: ページ間の待機秒数
  各 HTML 要素を探すための class 名

### `scripts/analysis/`

- `scripts/analysis/data_analysis.py`
  保存済み JSON を読み込み、件数集計・市場別件数・テーマ別件数・企業名の一部表示を行う分析スクリプトです。
  Flask 画面から実行されるほか、引数で JSON ファイルパスを受け取って単体実行もできます。

### `data/`

- `data/raw/codes.txt`
  スクレイピング対象の証券コード一覧です。1 行につき 1 コードを管理します。

- `data/processed/`
  スクレイピング結果の保存先です。`scraping_data_YYYYMMDDHHMMSS.json` の形式で出力されます。

### `drivers/`

- `drivers/chromedriver.exe`
  Selenium で Chrome を操作するためのドライバです。`scraping_main.py` から直接参照しています。

## プログラムの動作概要

### 1. Web アプリ側

`app.py` は 3 つの主要画面を持っています。

- `/scrape`
  `scripts/scraping/scraping_main.py` をサブプロセスで実行し、標準出力とエラー出力を画面に表示します。

- `/analyze`
  `data/processed/` にある JSON を一覧化し、選択されたファイルを `scripts/analysis/data_analysis.py` に渡して分析します。

- `/settings`
  `data/raw/codes.txt` と `scripts/scraping/scraping_config.py` を直接更新し、対象コードや取得条件を変更できるようにしています。

### 2. スクレイピング処理

`scripts/scraping/scraping_main.py` の流れは次のとおりです。

1. `codes.txt` から証券コード一覧を読み込む
2. `ChromeDriver` を使ってブラウザを起動する
3. 各コードの対象 URL にアクセスする
4. `BeautifulSoup` で HTML を解析する
5. 証券コード、市場区分、企業名、特色、市場テーマを抽出する
6. 抽出した情報をリストにまとめる
7. 実行時刻付きファイル名で `data/processed/` に JSON 保存する

現在の実装では、抽出対象 URL のベースは以下です。

```text
https://shikiho.toyokeizai.net/stocks/{code}/
```

### 3. 分析処理

`scripts/analysis/data_analysis.py` は、指定された JSON を読み込んで以下を表示します。

- 読み込んだレコード数
- 市場別の件数
- 先頭数件の企業名
- 市場テーマごとの出現件数

そのため、まずは収集結果の内容確認や傾向把握を素早く行う用途に向いています。

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

必要に応じて、実行環境に以下の追加パッケージもインストールしてください。

- `selenium`
- `beautifulsoup4`
- `lxml`

### 2. ChromeDriver の配置

`drivers/chromedriver.exe` を配置し、ローカルの Chrome バージョンと一致するものを使用してください。

### 3. アプリ起動

```bash
python app.py
```

起動後、ブラウザでローカルの Flask サーバーにアクセスして利用します。

## 今の実装で扱っている主なデータ項目

スクレイピング結果には、主に以下の情報を保存しています。

- `stock_code`
- `market`
- `company_name`
- `characteristics`
- `market_theme`

## 補足

- `scripts/scraping/scraping_main.py` では `chromedriver.exe` のパスを固定値で指定しています。
- `app.py` は `template_folder='.'` を使っており、トップページはルート直下、各画面は `pages/` 配下の HTML を参照しています。
- `tests/hello.py` は現状プレースホルダーに近く、テスト基盤はこれから拡張する前提の構成です。
