# プロジェクト全体のリファクタリング計画

この計画では、これまでに場当たり的に追加・修正してきたコードを一貫性のある構造に整理し、保守性と拡張性を高めます。

## 目的

1. **設定の集約**: `.env` 読み込みや定数管理をより堅牢にする。
2. **API クラスの洗練**: 冗長なメソッドを整理し、一貫したインターフェースを提供する。
3. **ロジックの適正配置**: スクリプト内の共通ロジック（天井計算など）を `utils.py` に移動。
4. **ツール群の整理**: アイテムマスター関連のスクリプトを統合し、使い勝手を向上させる。

## 提案される変更

### 1. コア・モジュール

#### [MODIFY] [constants.py](file:///c:/Git/uigf-notion-app/constants.py)

- モジュールロード時に一度だけ `.env` を読み込む構造に変更。
- 設定値を型安全に扱えるように整理。

#### [MODIFY] [notion_api.py](file:///c:/Git/uigf-notion-app/notion_api.py)

- メソッド名を一貫性のあるものに統一（例: `fetch` vs `get`）。
- API リクエスト時のリトライロジックや詳細なエラー出力を検討。

#### [MODIFY] [utils.py](file:///c:/Git/uigf-notion-app/utils.py)

- `uigf_to_notion.py` 内に記述されている「天井カウント計算（Pity）」をこちらに移動し、テスト可能にする。
- JSON パースロジックをより堅牢に（例外処理の強化）。

### 2. メインスクリプト

#### [MODIFY] [uigf_to_notion.py](file:///c:/Git/uigf-notion-app/uigf_to_notion.py)

- メインループを簡略化し、ロジックを `NotionAPI` や `utils` に委譲。
- 重複バリデーション処理の抽出。

#### [MODIFY] [notion_to_uigf.py](file:///c:/Git/uigf-notion-app/notion_to_uigf.py)

- UIGF v4.1 のスキーマに完全に準拠しているか再点検し、エクスポート処理を整理。

### 3. アイテムマスター関連

#### [MODIFY] [regist_item_master.py](file:///c:/Git/uigf-notion-app/regist_item_master.py)

- `fetch_item_master_map.py` の機能を統合し、1 つのコマンドで最新情報の取得から DB 登録まで行えるようにする（必要に応じて）。

## 検証計画

### 自動テスト

- `utils.py` のパース・天井計算ロジックが期待通り動作するか、既存の `uigf-v41.json` で確認。

### 手動検証

- インポートを実行し、天井カウントやリレーションが正しく設定されるか Notion 側で確認。
- 重複バリデーションが正しくフラグを立てるか確認。
- エクスポートされた JSON が UIGF スキーマバリデータを通るか確認。
