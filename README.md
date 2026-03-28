# プロジェクト構成

本プロジェクトは、保守性・再利用性・拡張性を高めるために、モジュール化された構成を採用しています。

---

## ディレクトリ構成

```
project-name/
│
├── README.md              # プロジェクト概要・使い方
├── requirements.txt       # Pythonの依存関係
├── .gitignore             # Gitで管理しないファイル
│
├── data/
│   ├── raw/               # 元データ（加工しない）
│   └── processed/         # 加工済みデータ
│
├── notebooks/             # 検証・分析用（Jupyter Notebook）
│
├── src/                   # コアロジック（再利用可能なコード）
│   ├── __init__.py
│   ├── data/              # データ取得（API・スクレイピング等）
│   ├── analysis/          # 分析ロジック
│   └── utils/             # 共通処理
│
├── scripts/               # 実行用スクリプト（入口）
│   ├── run_backtest.py
│   └── update_data.py
│
└── tests/                 # テストコード（初期は空でもOK）
```

---

## 設計方針

### 1. 役割の分離

各ディレクトリの役割を明確に分けます：

* `data/` → データの保存
* `src/` → ロジック（再利用可能）
* `scripts/` → 実行処理

---

### 2. 再利用前提の設計

* `src/` 内のコードは使い回しを前提に作成する
* `scripts/` にロジックを書きすぎない

---

### 3. データの再現性を担保

* `data/raw/` のデータは絶対に変更しない
* 加工は必ず `data/processed/` に出力する

---

### 4. 実行フローの明確化

```
scripts → src → data
```

* `scripts/` が `src/` を呼び出す
* `src/` が `data/` を処理する

---

## 補足

* `notebooks/` は検証・試行用として使用する
* 安定した処理は `src/` に移動する
* `scripts/` は実行に特化させる

---

## 最小構成（小規模プロジェクト向け）

```
project-name/
├── src/
├── scripts/
└── data/
```

---

## 判断基準

迷った場合は以下で判断：

* 再利用する → `src/`
* 単発で使う → `scripts/`
