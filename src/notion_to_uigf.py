import time
import json
import argparse
from datetime import datetime
from notion_api import NotionAPI
from constants import (
    SETTINGS_DB_ID, GACHA_LOG_DB_ID, GAME_CODE_MAP,
    EXPORT_APP_NAME, EXPORT_APP_VERSION, DEFAULT_TIMEZONE, DEFAULT_LANG
)

def extract_item_properties(props):
    """
    Notionのプロパティからアイテム情報を抽出
    """
    item = {}
    if "Item Name" in props and props["Item Name"]["title"]:
        item["name"] = props["Item Name"]["title"][0]["plain_text"]
    
    if "Item ID" in props and props["Item ID"]["rich_text"]:
        val = props["Item ID"]["rich_text"][0]["plain_text"]
        item["id"] = val
        item["item_id"] = val
        
    if "Item Type" in props and props["Item Type"]["select"]:
        item["item_type"] = props["Item Type"]["select"]["name"]
        
    if "Rank" in props and props["Rank"]["select"]:
        item["rank_type"] = props["Rank"]["select"]["name"]
        
    if "Gacha Type" in props and props["Gacha Type"]["select"]:
        gacha_type = props["Gacha Type"]["select"]["name"]
        item["gacha_type"] = gacha_type
        item["uigf_gacha_type"] = gacha_type

    # フォールバック
    item["gacha_id"] = item.get("gacha_type", "")
        
    if "Date Time" in props and props["Date Time"]["date"]:
        dt_str = props["Date Time"]["date"]["start"]
        if dt_str:
            # ISO形式からUIGF形式へ
            item["time"] = dt_str.replace("T", " ").split("+")[0].split(".")[0]
    
    item["count"] = "1"
    return item

def export_to_uigf(version_str):
    notion = NotionAPI()
    
    # 1. ユーザー設定の取得
    print("ユーザー設定（UIDマップ）を取得中...")
    settings_results = notion.fetch_all_results(SETTINGS_DB_ID)
    settings_map = {}
    for page in settings_results:
        props = page["properties"]
        uid = props["UID"]["rich_text"][0]["plain_text"] if props.get("UID") and props["UID"]["rich_text"] else ""
        game_name = props["Game"]["select"]["name"] if props.get("Game") and props["Game"]["select"] else ""
        game_code = GAME_CODE_MAP.get(game_name, "hk4e")
        settings_map[page["id"]] = {"uid": uid, "game_code": game_code}
    
    # 2. ガチャ履歴の取得
    print("ガチャ履歴を取得中...")
    logs = notion.fetch_all_results(GACHA_LOG_DB_ID)
    
    data_by_uid = {}
    for page in logs:
        props = page["properties"]
        user_rel = props.get("UID", {}).get("relation", [])
        if not user_rel or user_rel[0]["id"] not in settings_map:
            continue
        
        user_info = settings_map[user_rel[0]["id"]]
        uid = user_info["uid"]
        if uid not in data_by_uid:
            data_by_uid[uid] = {"game_code": user_info["game_code"], "list": []}
            
        data_by_uid[uid]["list"].append(extract_item_properties(props))

    now = datetime.now()
    timestamp = int(now.timestamp())
    
    # 3. フォーマットに合わせて出力
    if version_str == "3.0":
        for uid, content in data_by_uid.items():
            if not content["list"]: continue
            export_data = {
                "info": {
                    "uid": uid,
                    "lang": DEFAULT_LANG,
                    "export_timestamp": timestamp,
                    "export_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "export_app": EXPORT_APP_NAME,
                    "export_app_version": EXPORT_APP_VERSION,
                    "uigf_version": "v3.0",
                    "region_time_zone": DEFAULT_TIMEZONE
                },
                "list": content["list"]
            }
            filename = f"uigf_v3.0_{uid}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            print(f"エクスポート完了 (v3.0): {filename} ({len(content['list'])} 件)")
            
    elif version_str == "4.1":
        export_data = {
            "info": {
                "version": "v4.1",
                "export_app": EXPORT_APP_NAME,
                "export_app_version": EXPORT_APP_VERSION,
                "export_timestamp": timestamp
            }
        }
        for uid, content in data_by_uid.items():
            if not content["list"]: continue
            gc = content["game_code"]
            if gc not in export_data: export_data[gc] = []
            export_data[gc].append({
                "uid": uid,
                "timezone": DEFAULT_TIMEZONE,
                "lang": DEFAULT_LANG,
                "list": content["list"]
            })
        filename = f"uigf_v4.1_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)
        print(f"エクスポート完了 (v4.1): {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Notion から UIGF 形式でデータをエクスポートします。")
    parser.add_argument("--version", choices=["3.0", "4.1"], default="4.1", help="UIGF バージョン")
    args = parser.parse_args()
    
    print(f"--- UIGF {args.version} エクスポート開始 ---")
    try:
        export_to_uigf(args.version)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nエラー: {e}")
