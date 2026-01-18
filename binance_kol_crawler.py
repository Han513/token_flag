import requests
import json
from urllib.parse import urlparse

# 基礎 URL 和參數
base_url = "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/market/leaderboard/query"
# 預設優先嘗試較大 pageSize，失敗再降級
preferred_page_size = "50"
fallback_page_size = "25"
# 56: BSC；SOL 需使用 chainId=CT_501（對應 501）；8453: Base
chain_targets = [
    {"param": "56", "label": "56"},
    {"param": "CT_501", "label": "501"},
    {"param": "8453", "label": "8453"},
]
params = {
    "tag": "ALL",
    "chainId": None,  # 進迴圈動態設置
    "pageSize": preferred_page_size,
    "sortBy": "0",
    "orderBy": "0",
    "period": "90d"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 用來收集所有數據
all_data = []
# 依 address 去重（用字典存儲，方便更新）
address_dict = {}

# 讀取已有的 JSON 文件（如果存在）
existing_file = "binance_leaderboard.json"
try:
    with open(existing_file, "r", encoding="utf-8") as f:
        existing_data = json.load(f)
        for item in existing_data:
            addr = item.get("address")
            if addr:
                address_dict[addr] = item
        print(f"已讀取 {len(address_dict)} 個現有地址")
except FileNotFoundError:
    print("未找到現有 JSON 文件，將創建新文件")
except json.JSONDecodeError:
    print("現有 JSON 文件格式錯誤，將創建新文件")


def extract_twitter_username(url: str):
    """從 Twitter/X URL 取出用戶名"""
    if not url:
        return None
    parsed = urlparse(url)
    path = parsed.path or ""
    username = path.lstrip("/").split("/")[0]
    return username or None

for chain in chain_targets:
    chain_param = chain["param"]
    chain_label = chain["label"]
    params["chainId"] = chain_param
    params["pageSize"] = preferred_page_size
    page = 1
    while True:
        params["pageNo"] = page
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()  # 如果非 200 狀態碼，拋出異常
            json_data = response.json()

            # API 成功判定：支援原本的 success 布林以及代碼字串 "000000"
            is_success = json_data.get("success", False) or json_data.get("code") == "000000"
            if not is_success:
                # 若 50 失敗，退回 25 再試一次同頁
                if params.get("pageSize") != fallback_page_size:
                    print(f"[chainId={chain_param}] pageSize=50 取得失敗，退回 25 重試同一頁")
                    params["pageSize"] = fallback_page_size
                    continue
                print(f"[chainId={chain_param}] API 返回失敗: {json_data.get('message', '未知錯誤')}")
                break

            # 兼容範例結構 {"data": {"data": [...]}}
            data_block = json_data.get("data", {})
            items = data_block.get("data", []) if isinstance(data_block, dict) else []
            if not items:  # 如果空列表，停止
                print(f"[chainId={chain_param}] 頁碼 {page} 無數據，爬取結束。")
                break

            # 保留 address 並解析 Twitter 名稱/帳號，附 chainId，依 address 去重並更新
            filtered_count = 0
            updated_count = 0
            for item in items:
                addr = item.get("address")
                if not addr:
                    continue
                
                twitter_name = item.get("addressLabel")
                twitter_username = extract_twitter_username(item.get("addressTwitterUrl"))
                
                new_item = {
                    "address": addr,
                    "twittera_name": twitter_name,
                    "twitter_username": twitter_username,
                    "chainId": chain_label,
                }
                
                # 如果地址已存在，更新信息（優先使用新的非空值）
                if addr in address_dict:
                    existing_item = address_dict[addr]
                    # 更新 Twitter 信息（如果新值非空）
                    if twitter_name:
                        existing_item["twittera_name"] = twitter_name
                    if twitter_username:
                        existing_item["twitter_username"] = twitter_username
                    # 更新 chainId（使用最新的）
                    existing_item["chainId"] = chain_label
                    updated_count += 1
                else:
                    # 新地址，添加到字典
                    address_dict[addr] = new_item
                    filtered_count += 1

            print(f"[chainId={chain_param}] 已爬取頁碼 {page}，新增: {filtered_count}，更新: {updated_count}")
            page += 1
        
        except requests.exceptions.RequestException as e:
            # 若 50 失敗，退回 25 再試一次同頁
            if params.get("pageSize") != fallback_page_size:
                print(f"[chainId={chain_param}] pageSize=50 請求錯誤，退回 25 重試同一頁: {e}")
                params["pageSize"] = fallback_page_size
                continue
            print(f"[chainId={chain_param}] 請求錯誤: {e}")
            break

# 將字典轉換為列表並輸出到 JSON 檔案
if address_dict:
    all_data = list(address_dict.values())
    with open("binance_leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print(f"所有數據已輸出到 binance_leaderboard.json，共 {len(all_data)} 個地址")
else:
    print("無數據可輸出")