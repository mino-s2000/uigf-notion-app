# バージョン管理の一元化計画 (VERSION ファイルの導入)

現在の「コード内にハードコードされたバージョン」を、「外部ファイルからの動的読み込み」に変更し、管理を一元化します。

## 目的

1. **一元管理**: バージョン変更時に `constants.py` を直接編集する必要をなくす。
2. **自動化の布石**: 将来的に CI/CD 等で Git タグをこのファイルに書き出す運用に繋げられるようにする。
3. **整合性**: `README.md` やその他のドキュメントから参照する際の「正（Source of Truth）」を明確にする。

## 変更内容

### 1. 新規ファイルの作成

#### [NEW] [VERSION](file:///c:/Git/uigf-notion-app/VERSION)

- 内容: `v1.0.0` (または任意の現在のバージョン) のみを記述。

### 2. ソースコードの修正

#### [MODIFY] [constants.py](file:///c:/Git/uigf-notion-app/src/constants.py)

- 環境変数読み込みと同様のロジックで、`PROJECT_ROOT / VERSION` ファイルを読み込む `load_version()` 関数を実装。
- `EXPORT_APP_VERSION` にその値を代入。

### 3. ドキュメント修正

#### [MODIFY] [README.md](file:///c:/Git/uigf-notion-app/README.md)

- プロジェクト構成の説明に `VERSION` ファイルを追記。

## 検証計画

- `src/constants.py` 内で `EXPORT_APP_VERSION` が正しく `v1.0.0` (等) になっているかをプリントアウト等で確認。
- `VERSION` ファイルがない場合のフォールバック（デフォルト値）が機能することを確認。
