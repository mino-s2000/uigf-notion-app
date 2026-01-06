# さらなるリファクタリングと修正計画 (Refactor and Polish)

これまでのリファクタリングに基づき、さらに堅牢で使いやすいツールにするための最終調整を行います。

## 目的

1. **信頼性の向上**: Notion API のレート制限や一時的なネットワークエラーに対する耐性を高める。
2. **データの正確性**: BOM 付き JSON などの特殊なファイル形式への対応を強化する。
3. **可読性と保守性**: ログ出力の一貫性を保ち、開発者・ユーザー双方にとってわかりやすい表示にする。

## 提案される変更

### 1. 堅牢性の強化

#### [MODIFY] [notion_api.py](file:///c:/Git/uigf-notion-app/notion_api.py)

- `notion_client` の標準機能を活かしつつ、リクエスト失敗時のリトライ回数を明示的に設定（可能な場合）。
- 429 エラー（レート制限）発生時の挙動をより親切にする。

#### [MODIFY] [utils.py](file:///c:/Git/uigf-notion-app/utils.py)

- すべての `open()` 時に `encoding="utf-8-sig"` を使用するように統一し、予期せぬ文字化けや BOM エラーを防止。

### 2. ユーザー体験 (UX) の向上

#### [MODIFY] [uigf_to_notion.py](file:///c:/Git/uigf-notion-app/uigf_to_notion.py)

- インポート中の進捗表示を「[123/456] ...」の形式で統一し、残り件数などが把握しやすいようにする。

### 3. プロジェクトのクリーンアップ

#### [DELETE] [temp_update_master_relation.py](file:///c:/Git/uigf-notion-app/temp_update_master_relation.py)

- 役割を終えた一時スクリプトを安全に削除（ユーザーに確認後に実施）。

## 検証計画

### 自動テスト

- 既存の `uigf-v41.json` を使用して、リファクタリング後もインポート・天井計算が正常に動作することを確認。

### 手動検証

- 意図的にレート制限にかかりそうな挙動（高速リクエスト）をさせ、エラーハンドリングが機能するか確認。
