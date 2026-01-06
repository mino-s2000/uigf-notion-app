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

Notion 上で 3 つのデータベース作成と連携設定が必要です。

#### 1. 事前準備：Notion API の有効化

1. [Notion My Integrations](https://www.notion.so/my-integrations) で新しいインテグレーションを作成し、**「シークレット（Internal Integration Token）」**をメモします。
2. 作成する 3 つのデータベースの右上メニュー `...` → `接続先を追加` から、作成したインテグレーションを招待してください。

#### 2. データベースの構成

**① 設定用データベース (Settings DB)**  
各ユーザーの UID や全体統計を管理します。

| プロパティ名   | 型           | 役割                                     |
| :------------- | :----------- | :--------------------------------------- |
| **Account**    | タイトル     | ユーザー名や識別名（自動生成）           |
| **UID**        | テキスト     | ゲームの UID（重複チェックに使用）       |
| **Game**       | セレクト     | 原神 / スターレイル / ゼンレスゾーンゼロ |
| **Gacha Logs** | リレーション | 「ガチャ履歴 DB」と双方向リレーション    |

**② アイテムマスター DB (Master DB)**  
キャラクターや武器の画像・図鑑情報を管理します。

| プロパティ名  | 型                 | 役割                                   |
| :------------ | :----------------- | :------------------------------------- |
| **名前**      | タイトル           | キャラクター・武器の正式名称           |
| **Item ID**   | テキスト           | UIGF 準拠のアイテム ID（画像紐付け用） |
| **Item Type** | セレクト           | キャラクター / 武器                    |
| **Icon**      | ファイル＆メディア | Enka.Network 等の外部リンクを保存      |

**③ ガチャ履歴データベース (Gacha Logs DB)**  
全ガチャ記録が保存されるメインのデータベースです。

| プロパティ名        | 型               | 役割                                            |
| :------------------ | :--------------- | :---------------------------------------------- |
| **Item Name**       | タイトル         | 排出されたアイテム名                            |
| **Item ID**         | テキスト         | 重複チェック用の固有 ID                         |
| **Gacha Type**      | セレクト         | ガチャの種類 (301, 200 等)                      |
| **Rank**            | セレクト         | レアリティ (5, 4, 3)                            |
| **Date Time**       | 日付             | ガチャを引いた日時                              |
| **Pity**            | 数値             | 天井カウント                                    |
| **UID**             | リレーション     | 「設定用 DB」へ接続（制限：1 ページ）           |
| **Referenced Item** | リレーション     | 「アイテムマスター DB」へ接続（制限：1 ページ） |
| **Image Preview**   | ロールアップ     | リレーション「アイテム参照」の「画像」を表示    |
| **Duplicate Flag**  | チェックボックス | 重複チェック用フラグ                            |

#### 3. リレーションとロールアップの設定詳細

**ガチャ履歴 DB での画像表示設定**

1. **「Referenced Item」プロパティ**を作成し、`アイテムマスターDB` を選択します。
2. **「Image Preview」プロパティ**を種類：`ロールアップ` で作成します。
   - リレーション：`Referenced Item`
   - プロパティ：`Icon`
   - 計算：`オリジナルを表示`

**設定用 DB での統計計算（任意）**

1. **「合計回数」プロパティ**（ロールアップ）
   - リレーション：`Gacha Logs`
   - プロパティ：`Item Name`
   - 計算：`カウント`
2. **「星 5 数」プロパティ**（関数/Formula）
   - 数式：`prop("Gacha Logs").filter(current.prop("Rank") == "5").length()`

#### 4. おすすめのビュー設定

**🎴 ギャラリービュー（ガチャ結果一覧）**  
「ガチャ履歴 DB」にギャラリービューを追加するとアプリらしくなります。

- **カードプレビュー**: `Image Preview`（ロールアップ）に設定
- **カードサイズ**: `小` または `中`
- **表示するプロパティ**: `Item Name`, `Rank`, `Date Time`
- **フィルター**: `Rank` が `5` のみ表示する「星 5 コレクション」ビューを別途作ると見栄えが良くなります。

**📊 ダッシュボード（設定用 DB）**  
「設定用 DB」をギャラリービューにし、プロパティに「合計回数」や「星 5 排出率」を表示させると、アカウントごとのサマリーページとして機能します。

👉 [**ダッシュボードの詳細設定ガイドはこちら**](docs/dashboard_setup.md)

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
