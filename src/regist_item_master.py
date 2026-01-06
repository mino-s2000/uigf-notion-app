import json
import time
from notion_api import NotionAPI
from constants import MASTER_DB_ID
from utils import parse_uigf_json

def get_existing_master_ids(notion):
    """
    アイテムマスターDBの既存エントリのIDを取得
    """
    print("アイテムマスターDBの既存データを取得中...")
    results = notion.fetch_all_results(MASTER_DB_ID)
    existing_ids = set()
    for page in results:
        props = page["properties"]
        ids = props.get("Item ID", {}).get("rich_text", [])
        if ids:
            existing_ids.add(ids[0]["plain_text"])
    return existing_ids

def run_item_master_registration():
    notion = NotionAPI()
    
    # 1. マッピングデータの読み込み (fetch_item_master_map.pyで生成)
    try:
        with open("item_master_map.json", "r", encoding="utf-8") as f:
            master_map = json.load(f)
    except FileNotFoundError:
        print("エラー: item_master_map.json が見つかりません。fetch_item_master_map.py を先に実行してください。")
        return

    # 2. UIGFファイルから履歴にあるアイテム名を抽出
    print("UIGFファイルから履歴にあるアイテム名を抽出中...")
    UIGF_FILE_PATH = "uigf-v41.json"
    uid, gacha_list, version, game_name, game_code = parse_uigf_json(UIGF_FILE_PATH)
    
    if not gacha_list:
        print("エラー: UIGFファイルから履歴を取得できませんでした。")
        return

    # 履歴に存在する名前のセット（ID欠落時の名寄せ用）
    history_names = {item.get("name") for item in gacha_list if item.get("name")}

    # 3. すでに登録済みのIDを取得
    existing_ids = get_existing_master_ids(notion)

    # 4. 未登録のアイテムを登録
    print(f"登録を開始します... (マスタ候補: {len(master_map)} 件)")
    register_count = 0
    
    for item_id, info in master_map.items():
        name = info.get("name")
        if not name or name not in history_names or item_id in existing_ids:
            continue
            
        icon_name = info["icon"]
        item_type = info["type"]
        image_url = f"https://enka.network/ui/{icon_name}.png"
        
        try:
            notion.create_page(
                database_id=MASTER_DB_ID,
                properties={
                    "名前": {"title": [{"text": {"content": name}}]},
                    "Item ID": {"rich_text": [{"text": {"content": item_id}}]},
                    "Item Type": {"select": {"name": item_type}},
                    "Icon": {
                        "files": [
                            {
                                "name": f"{icon_name}.png",
                                "type": "external",
                                "external": {"url": image_url}
                            }
                        ]
                    }
                }
            )
            print(f"マスター登録成功: {name} ({item_type})")
            existing_ids.add(item_id)
            register_count += 1
            time.sleep(0.4)
        except Exception as e:
            print(f"エラー ({name}): {e}")

    print(f"\nアイテムマスターの更新が完了しました！ (新規登録: {register_count} 件)")

if __name__ == "__main__":
    run_item_master_registration()
