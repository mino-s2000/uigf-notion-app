import json
import os
from constants import CACHE_FILE, GAME_MAP

# プロジェクトのルートディレクトリを取得 (src/ の親)
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

def _get_abs_path(filename):
    """ルートディレクトリからの相対パスを絶対パスに変換"""
    if os.path.isabs(filename):
        return filename
    return os.path.join(PROJECT_ROOT, filename)

def load_cache(filename=CACHE_FILE):
    """
    キャッシュファイルから既存の Item ID セットを読み込む
    """
    abs_path = _get_abs_path(filename)
    if os.path.exists(abs_path):
        try:
            with open(abs_path, 'r', encoding='utf-8-sig') as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_cache(data, filename=CACHE_FILE):
    """
    Item ID セットをキャッシュファイルに保存する
    """
    abs_path = _get_abs_path(filename)
    with open(abs_path, 'w', encoding='utf-8-sig') as f:
        json.dump(list(data), f)

def parse_uigf_json(json_file_path):
    """
    UIGF JSON (v3.0/v4.x) を読み込み、共通フォーマットのデータを返す
    Returns: (uid, gacha_list, version, game_name, game_code)
    """
    abs_path = _get_abs_path(json_file_path)
    # BOM付きJSONに対応するため utf-8-sig で読み込み
    with open(abs_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)
    
    info = data.get("info", {})
    version = info.get("uigf_version") or info.get("version", "v3.0")
    
    uid = None
    gacha_list = []
    game_code = "hk4e"

    if version.startswith("v4"):
        for key in GAME_MAP.keys():
            if key in data and isinstance(data[key], list) and data[key]:
                game_code = key
                target_data = data[key][0]
                uid = target_data.get("uid")
                gacha_list = target_data.get("list", [])
                break
    else:
        uid = info.get("uid")
        game_code = info.get("s_game", "hk4e")
        gacha_list = data.get("list", [])

    game_name = GAME_MAP.get(game_code, game_code)
    return uid, gacha_list, version, game_name, game_code

def calculate_pity(gacha_list):
    """
    ガチャ履歴リストに対して天井カウント（Pity）を計算し、各アイテムに付与する
    """
    # IDで昇順（古い順）にソート
    try:
        gacha_list.sort(key=lambda x: int(x.get("id", 0)))
    except Exception:
        # IDが不適切な場合は時刻で代用
        gacha_list.sort(key=lambda x: x.get("time", ""))

    pity_counters = {} # ガチャ種別ごとのカウンター
    for raw_item in gacha_list:
        # ガチャ種別の特定 (v4は uigf_gacha_type, v3は gacha_type)
        gtype = raw_item.get("uigf_gacha_type") or raw_item.get("gacha_type", "unknown")
        
        # カウントアップ
        pity_counters[gtype] = pity_counters.get(gtype, 0) + 1
        raw_item["pity_count"] = pity_counters[gtype]
        
        # 星5(rank_type="5")ならリセット
        if str(raw_item.get("rank_type", "")) == "5":
            pity_counters[gtype] = 0
    
    return gacha_list

def normalize_item_for_notion(item, version):
    """
    UIGFアイテムをNotionプロパティ作成用の辞書に整形
    """
    res = {
        "item_id": str(item.get("id") or item.get("item_id", "")),
        "name": item.get("name", "Unknown"),
        "rank_type": str(item.get("rank_type", "")),
        "item_type": item.get("item_type", ""),
        "time": item.get("time", ""),
        "pity_count": item.get("pity_count")
    }

    if version.startswith("v4"):
        res["gacha_type"] = str(item.get("uigf_gacha_type") or item.get("gacha_type", ""))
    else:
        res["gacha_type"] = str(item.get("gacha_type", ""))
    
    return res
