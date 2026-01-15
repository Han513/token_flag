import requests
import json
from urllib.parse import urlparse

# 基礎 URL 和參數
base_url = "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/market/leaderboard/query"
# 預設優先嘗試較大 pageSize，失敗再降級
preferred_page_size = "50"
fallback_page_size = "25"
# 56: BSC；SOL 需使用 chainId=CT_501（對應 501）
chain_targets = [
    {"param": "56", "label": "56"},
    {"param": "CT_501", "label": "501"},
]
params = {
    "tag": "ALL",
    "chainId": None,  # 進迴圈動態設置
    "pageSize": preferred_page_size,
    "sortBy": "0",
    "orderBy": "0",
    "period": "7d"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 用來收集所有數據
all_data = []
# 依 address 去重
seen_addresses = set()


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
                    print(f"[chainId={chain_id}] pageSize=50 取得失敗，退回 25 重試同一頁")
                    params["pageSize"] = fallback_page_size
                    continue
                print(f"[chainId={chain_id}] API 返回失敗: {json_data.get('message', '未知錯誤')}")
                break

            # 兼容範例結構 {"data": {"data": [...]}}
            data_block = json_data.get("data", {})
            items = data_block.get("data", []) if isinstance(data_block, dict) else []
            if not items:  # 如果空列表，停止
                print(f"[chainId={chain_param}] 頁碼 {page} 無數據，爬取結束。")
                break

            # 保留 address 並解析 Twitter 名稱/帳號，附 chainId，依 address 去重
            filtered_items = []
            for item in items:
                addr = item.get("address")
                if not addr or addr in seen_addresses:
                    continue
                seen_addresses.add(addr)
                filtered_items.append(
                    {
                        "address": addr,
                        "twittera_name": item.get("addressLabel"),
                        "twitter_username": extract_twitter_username(
                            item.get("addressTwitterUrl")
                        ),
                        "chainId": chain_label,
                    }
                )

            all_data.extend(filtered_items)
            print(f"[chainId={chain_param}] 已爬取頁碼 {page}，數據數量: {len(filtered_items)}")
            page += 1
        
        except requests.exceptions.RequestException as e:
            # 若 50 失敗，退回 25 再試一次同頁
            if params.get("pageSize") != fallback_page_size:
                print(f"[chainId={chain_param}] pageSize=50 請求錯誤，退回 25 重試同一頁: {e}")
                params["pageSize"] = fallback_page_size
                continue
            print(f"[chainId={chain_param}] 請求錯誤: {e}")
            break

# 輸出到 JSON 檔案
if all_data:
    with open("binance_leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("所有數據已輸出到 binance_leaderboard.json")
else:
    print("無數據可輸出")