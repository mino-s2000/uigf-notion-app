import os

# --- 環境変数の読み込み (.env対応) ---
def load_env():
    # スクリプトがある src/ から見て、一つ上の親ディレクトリ（ルート）の .env を探す
    base_dir = os.path.dirname(os.path.dirname(__file__))
    env_path = os.path.join(base_dir, ".env")
    
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
                    except ValueError:
                        continue

load_env()

# --- Notion API 設定 ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
SETTINGS_DB_ID = os.getenv("SETTINGS_DB_ID", "")
GACHA_LOG_DB_ID = os.getenv("GACHA_LOG_DB_ID", "")
MASTER_DB_ID = os.getenv("MASTER_DB_ID", "")
NOTION_VERSION = "2022-06-28"

if not NOTION_TOKEN:
    print("警告: NOTION_TOKEN が設定されていません。")

# --- ゲーム設定 ---
GAME_MAP = {
    "hk4e": "原神",
    "hkrpg": "スターレイル",
    "nap": "ゼンレスゾーンゼロ"
}
# 逆引き（名前 -> コード）
GAME_CODE_MAP = {v: k for k, v in GAME_MAP.items()}

# --- インポート/エクスポート設定 ---
MAX_IMPORT_LIMIT = 500
CACHE_FILE = "uigf_cache.json"
PITY_COUNT_PROPERTY = "Pity"  # Notion側のプロパティ名

# --- バージョンの読み込み (VERSIONファイル対応) ---
def load_version():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    version_path = os.path.join(base_dir, "VERSION")
    if os.path.exists(version_path):
        try:
            with open(version_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass
    return "v1.0.0" # フォールバック

EXPORT_APP_NAME = "uigf-notion-app"
EXPORT_APP_VERSION = load_version()
DEFAULT_TIMEZONE = 9  # JST
DEFAULT_LANG = "ja-jp"
