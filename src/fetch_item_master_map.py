import requests
import json

def fetch_and_create_mapping():
    print("最新のマッピングデータを取得中...")
    
    # 1. UIGF 辞書 (名前 -> ID) の取得
    dict_url = "https://api.uigf.org/dict/genshin/jp.json"
    # 2. Dimbreath データの取得 (ID -> アイコン)
    base_url = "https://gitlab.com/Dimbreath/AnimeGameData/-/raw/master/ExcelBinOutput"
    avatar_url = f"{base_url}/AvatarExcelConfigData.json"
    weapon_url = f"{base_url}/WeaponExcelConfigData.json"
    
    def get_json_safely(url):
        print(f"取得中: {url}")
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code} for {url}")
        content = resp.content.decode("utf-8-sig")
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # エラー時に内容の冒頭を出力して助けにする
            print(f"JSONパースエラー。内容の冒頭: {content[:100]}")
            raise e

    try:
        # 名前 -> ID の辞書
        jp_dict = get_json_safely(dict_url)
        # ID -> 名前の逆引きを作成
        id_to_name = {str(v): k for k, v in jp_dict.items()}

        mapping = {}

        # キャラクターデータの処理
        avatars = get_json_safely(avatar_url)
        for char in avatars:
            char_id = str(char["id"])
            if "iconName" in char and (len(char_id) >= 8 or char_id in id_to_name):
                mapping[char_id] = {
                    "icon": char["iconName"],
                    "type": "キャラクター",
                    "name": id_to_name.get(char_id, "")
                }

        # 武器データの処理
        weapons = get_json_safely(weapon_url)
        for wp in weapons:
            wp_id = str(wp["id"])
            if "icon" in wp:
                mapping[wp_id] = {
                    "icon": wp["icon"],
                    "type": "武器",
                    "name": id_to_name.get(wp_id, "")
                }

        # ローカルに保存
        with open("item_master_map.json", "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=4)
        
        print(f"成功: {len(mapping)} 件のアイテムを登録しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    fetch_and_create_mapping()