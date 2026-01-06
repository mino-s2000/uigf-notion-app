import time
import argparse
from notion_api import NotionAPI
from constants import (
    GACHA_LOG_DB_ID, SETTINGS_DB_ID, MASTER_DB_ID, MAX_IMPORT_LIMIT
)
from utils import (
    load_cache, save_cache, parse_uigf_json, normalize_item_for_notion,
    calculate_pity
)

def validate_notion_duplicates(notion):
    """
    Notion DB内の重複（Item IDが同じもの）をチェックし、フラグを立てる
    """
    print("\n" + "="*40)
    print(" 🔍 重複バリデーション")
    print("="*40)
    results = notion.fetch_all_results(GACHA_LOG_DB_ID)
    
    id_counts = {}
    for page in results:
        props = page["properties"]
        item_id_list = props.get("Item ID", {}).get("rich_text", [])
        if item_id_list:
            item_id = item_id_list[0]["plain_text"]
            if item_id not in id_counts:
                id_counts[item_id] = []
            id_counts[item_id].append(page["id"])
            
    duplicates = {iid: pids for iid, pids in id_counts.items() if len(pids) > 1}
    
    if not duplicates:
        print("[Check] 重複は見つかりませんでした。")
        return

    print(f"[Check] {len(duplicates)} 種類の重複 ID が見つかりました。")
    
    update_count = 0
    for iid, pids in duplicates.items():
        for pid in pids:
            try:
                notion.update_page(pid, {"Duplicate Flag": {"checkbox": True}})
                update_count += 1
                if update_count % 5 == 0:
                    print(f" > フラグ更新中: {update_count}/{len(duplicates)}...", end="\r")
                time.sleep(0.4)
            except Exception as e:
                print(f"\n[Error] 更新失敗 (PageID:{pid}): {e}")
                
    print(f"\n[Success] 重複バリデーション完了。{update_count} 件にフラグを立てました。")

def import_uigf_to_notion(json_file_path, skip_validation=False):
    notion = NotionAPI()
    
    # 1. JSONパース
    print("\n" + "="*40)
    print(" 🛠  UIGFインポート開始")
    print("="*40)
    uid, gacha_list, version, game_name, game_code = parse_uigf_json(json_file_path)
    if uid is None:
        print(f"[Error] UIDが見つかりませんでした (バージョン: {version})")
        return

    print(f"[System] {version} / {game_name} (UID:{uid}) を検知")

    # 2. 初期準備
    master_id_map, master_name_map = notion.get_master_mapping(MASTER_DB_ID)
    user_page_id = notion.get_or_create_user_page(SETTINGS_DB_ID, uid, game_name)
    
    existing_ids = load_cache()
    if not existing_ids:
        existing_ids = notion.fetch_existing_item_ids(GACHA_LOG_DB_ID)
        save_cache(existing_ids)
    else:
        print(f"[Cache] {len(existing_ids)} 件のIDを読み込みました。")

    # 3. 天井カウント（Pity）の計算
    print("[System] 天井カウントを算出中...")
    gacha_list = calculate_pity(gacha_list)

    # 4. インポート実行
    print(f"[System] インポートを開始します (上限: {MAX_IMPORT_LIMIT} 件)")
    
    total_items = len(gacha_list)
    new_records_count = 0
    for i, raw_item in enumerate(gacha_list):
        if new_records_count >= MAX_IMPORT_LIMIT:
            print(f"\n[Limit] 上限（{MAX_IMPORT_LIMIT}件）に達したため中断します。")
            break

        item = normalize_item_for_notion(raw_item, version)
        if item["item_id"] in existing_ids:
            continue
            
        m_id = str(raw_item.get("item_id") or "")
        m_name = raw_item.get("name", "")
        master_page_id = master_id_map.get(m_id) or master_name_map.get(m_name)
        
        try:
            notion.add_gacha_log(GACHA_LOG_DB_ID, item, user_page_id, master_page_id)
            new_records_count += 1
            print(f" [{i+1}/{total_items}] 追加: {item['name']} (Pity: {item['pity_count']})")
            
            existing_ids.add(item["item_id"])
            if new_records_count % 10 == 0:
                save_cache(existing_ids)
            
            time.sleep(0.4)
        except Exception as e:
            print(f"\n[Error] 追加失敗 (ID:{item['item_id']}): {e}")

    print(f"\n[Success] インポート完了！ 新規追加: {new_records_count} 件")
    save_cache(existing_ids)

    # 5. 重複バリデーション
    if not skip_validation:
        validate_notion_duplicates(notion)
    
    print("\n" + "="*40)
    print(" ✨ すべての処理が終了しました")
    print("="*40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UIGF JSON を Notion にインポートします。")
    parser.add_argument("file", help="インポートする JSON ファイルのパス")
    parser.add_argument("--skip-validation", action="store_true", help="インポート後の重複バリデーションをスキップします")
    args = parser.parse_args()
    
    import_uigf_to_notion(args.file, skip_validation=args.skip_validation)
