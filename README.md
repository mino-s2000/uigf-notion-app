# UIGF to Notion App

Genshin Impact / Honkai: Star Rail / Zenless Zone Zero のガチャ履歴 (UIGF 形式) を Notion データベースにインポート・同期するためのツールキットです。

## 主な機能

- **マルチゲーム対応**: 原神、崩壊：スターレイル、ゼンレスゾーンゼロの UIGF 形式（v3.0 / v4.x）をサポート。
- **Notion 連携**: ガチャ履歴を Notion データベースに自動登録。重複チェック機能付き。
- **天井カウントの自動計算**: 各ガチャ種別ごとの天井（Pity）を自動的に計算し、Notion に記録。
- **アイテムマスター連携**: キャラクターや武器のアイコン画像を Notion 上で自動表示（アイテムマスター DB とのリレーション）。
- **仮想環境対応**: 依存関係をクリーンに管理できる構成。

## プロジェクト構成

```text
uigf-notion-app/
├── .env                  # Notion APIキーやDB IDを設定（手動作成）
├── VERSION               # プロジェクトのバージョン情報を管理
├── requirements.txt       # Python 依存パッケージ
├── src/                  # ソースコード
│   ├── uigf_to_notion.py # インポート実行スクリプト
│   ├── notion_to_uigf.py # エクスポート実行スクリプト
│   ├── constants.py      # 設定・定数管理
│   ├── notion_api.py     # Notion API ラッパー
│   └── utils.py          # 共通ユーティリティ
└── docs/                 # 開発ドキュメント
```

## セットアップ

### 1. 仮想環境の構築とインストール

```bash
# 仮想環境の作成
python -m venv .venv

# 仮想環境の有効化 (Windows)
.venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# もし pip コマンドが直接使えない場合：
python -m pip install -r requirements.txt
```

### 2. Notion の準備

1. [Notion My Integrations](https://www.notion.so/my-integrations) で新しいインテグレーションを作成し、Internal Integration Token を取得します。
2. Notion 上で以下のデータベースを準備します：
   - **ガチャログ DB**: ガチャ履歴を保存するメイン DB
   - **設定 DB**: ユーザー/UID ごとの設定を管理する DB
   - **アイテムマスター DB**: キャラクター/武器のマスター情報を管理する DB
3. 各データベースに対し、作成したインテグレーションに閲覧・編集権限を付与（Connect）します。

### 3. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成し、以下の情報を入力します：

```env
NOTION_TOKEN=secret_your_token_here
GACHA_LOG_DB_ID=your_gacha_log_db_id
SETTINGS_DB_ID=your_settings_db_id
MASTER_DB_ID=your_master_db_id
```

## 使い方

### UIGF データのインポート

```bash
python src/uigf_to_notion.py path/to/your/uigf.json
```

オプション：

- `--skip-validation`: インポート後の重複バリデーション（フラグ立て）をスキップします。

### Notion データの UIGF エクスポート

```bash
python src/notion_to_uigf.py --version 4.1
```

## ライセンス

[MIT License](LICENSE)
