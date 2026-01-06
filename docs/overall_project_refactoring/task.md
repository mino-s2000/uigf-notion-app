# 全体リファクタリングタスク

- [x] ドキュメント構成の整理 `[x]`
  - [x] 現状의コードベースの分析
  - [x] `task.md` の作成
  - [x] `implementation_plan.md` の作成
- [x] コアロジックの整理（`constants.py`, `notion_api.py`, `utils.py`） `[x]`
  - [x] `constants.py` の定数整理と設定クラスの導入
  - [x] `notion_api.py` の冗長なメソッドのクリーンアップと例外処理の強化
  - [x] `utils.py` への計算ロジック（天井カウント等）の移動
- [x] インポート・エクスポートスクリプトの最適化 `[x]`
  - [x] `uigf_to_notion.py` のメインループの整理
  - [x] `notion_to_uigf.py` のスキーマ準拠処理の再点検
- [x] アイテムマスター関連ツールの整理 `[x]`
  - [x] `regist_item_master.py` の NotionAPI 連携強化
- [x] 最終確認と動作テスト `[x]`
  - [x] インポート/エクスポートの正常動作確認
  - [x] バリデーション機能の確認
  - [x] `walkthrough.md` の作成
