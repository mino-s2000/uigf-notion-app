import time
from notion_client import Client, APIResponseError
from constants import NOTION_TOKEN, NOTION_VERSION, PITY_COUNT_PROPERTY

class NotionAPI:
    """
    Notion APIとの通信を担当するクラス
    """
    def __init__(self):
        # notion-client のビルドインリトライ設定を活用
        self.client = Client(auth=NOTION_TOKEN, notion_version=NOTION_VERSION)

    def _safe_request(self, func, *args, **kwargs):
        """
        APIリクエストを実行し、レート制限(429)が発生した場合は待機して再試行する
        """
        max_retries = 3
        retry_delay = 1.0 # 秒
        
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except APIResponseError as e:
                if e.status == 429:
                    # レート制限が発生した場合は指数関数的に待機
                    wait_time = retry_delay * (2 ** i)
                    print(f"\n[NotionAPI] レート制限を検知しました。{wait_time}秒待機します...")
                    time.sleep(wait_time)
                    continue
                raise e
        return func(*args, **kwargs)

    def fetch_all_results(self, database_id, filter_obj=None):
        """
        指定したデータベースから全件取得する（ページネーション自動対応）
        """
        results = []
        has_more = True
        next_cursor = None
        
        while has_more:
            body = {"page_size": 100}
            if next_cursor:
                body["start_cursor"] = next_cursor
            if filter_obj:
                body["filter"] = filter_obj
                
            try:    
                response = self._safe_request(
                    self.client.request,
                    path=f"databases/{database_id}/query",
                    method="POST",
                    body=body
                )
                results.extend(response.get("results", []))
                has_more = response.get("has_more", False)
                next_cursor = response.get("next_cursor")
                print(f"取得済み: {len(results)} 件...", end="\r")
            except Exception as e:
                print(f"\n[NotionAPI] エラー: {e}")
                break
        print()
        return results

    def query_database(self, database_id, filter_obj):
        """
        データベースをクエリする（単発リクエスト）
        """
        return self._safe_request(
            self.client.request,
            path=f"databases/{database_id}/query",
            method="POST",
            body={"filter": filter_obj}
        )

    def create_page(self, database_id, properties):
        """
        新しいページを作成する
        """
        return self._safe_request(
            self.client.pages.create,
            parent={"database_id": database_id},
            properties=properties
        )

    def update_page(self, page_id, properties):
        """
        既存のページを更新する
        """
        return self._safe_request(
            self.client.pages.update,
            page_id=page_id,
            properties=properties
        )

    def get_or_create_user_page(self, settings_db_id, uid, game_name):
        """
        UIDに紐づく設定ページを取得、存在しない場合は作成する
        """
        filter_obj = {
            "property": "UID",
            "rich_text": {"equals": str(uid)}
        }
        query = self.query_database(settings_db_id, filter_obj)
        results = query.get("results")
        
        if results:
            print(f"ユーザー(UID:{uid}) が見つかりました。")
            return results[0]["id"]
        else:
            print(f"ユーザー(UID:{uid}) を新規作成します。")
            properties = {
                "Account": {"title": [{"text": {"content": f"{game_name} User ({uid})"}}]},
                "UID": {"rich_text": [{"text": {"content": str(uid)}}]},
                "Game": {"select": {"name": game_name}}
            }
            new_page = self.create_page(settings_db_id, properties)
            return new_page["id"]

    def fetch_existing_item_ids(self, gacha_db_id):
        """
        既存のガチャログから Item ID のセットを取得する
        """
        print("[Notion] 既存のIDをスキャン中...")
        results = self.fetch_all_results(gacha_db_id)
        existing_ids = {
            page["properties"]["Item ID"]["rich_text"][0]["plain_text"]
            for page in results
            if page["properties"].get("Item ID", {}).get("rich_text")
        }
        return existing_ids

    def get_master_mapping(self, master_db_id):
        """
        アイテムマスターから ID->PageID および 名前->PageID のマップを作成
        """
        print("[Notion] アイテムマスターをキャッシュ中...")
        results = self.fetch_all_results(master_db_id)
        id_map = {}
        name_map = {}
        
        for page in results:
            props = page["properties"]
            # IDによるマッピング
            item_id_list = props.get("Item ID", {}).get("rich_text", [])
            if item_id_list:
                id_val = item_id_list[0]["plain_text"]
                id_map[id_val] = page["id"]
            
            # 名前によるマッピング
            name_list = props.get("名前", {}).get("title", [])
            if name_list:
                name_val = name_list[0]["plain_text"]
                name_map[name_val] = page["id"]
                
        print(f"[Notion] キャッシュ完了: {len(id_map)} 件のマスターデータを読み込みました。")
        return id_map, name_map

    def add_gacha_log(self, gacha_db_id, item, user_page_id, master_page_id):
        """
        ガチャログをDBに追加する
        """
        # 時刻変換 (YYYY-MM-DD HH:mm:ss -> ISO 8601)
        time_iso = item["time"].replace(" ", "T") + "+09:00" if item.get("time") else None
        
        properties = {
            "Item Name": {"title": [{"text": {"content": item["name"]}}]},
            "Item ID": {"rich_text": [{"text": {"content": item["item_id"]}}]},
            "Item Type": {"select": {"name": item["item_type"]}},
            "Gacha Type": {"select": {"name": item["gacha_type"]}},
            "Rank": {"select": {"name": item["rank_type"]}},
            "Date Time": {"date": {"start": time_iso}} if time_iso else {},
            "UID": {"relation": [{"id": user_page_id}]},
            PITY_COUNT_PROPERTY: {"number": item.get("pity_count")},
            "Referenced Item": {"relation": [{"id": master_page_id}]} if master_page_id else {"relation": []}
        }
        return self.create_page(gacha_db_id, properties)
