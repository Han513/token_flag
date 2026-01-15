import time
import json
import requests
from urllib.parse import urlparse

# OKX KOL 榜單 API
# 若使用簽名，需與瀏覽器請求主機一致，維持 web3.okx.com
base_url = "https://web3.okx.com/priapi/v1/dx/market/v2/address/search"

# 參數設定：優先使用較大 pageSize，失敗再降級
preferred_page_size = 100
fallback_page_size = 50
base_params = {
    "isAsc": "false",
    "sortType": 1,
    "isExpand": "true",
    "chainId": "all",
    "pageNum": 1,
    "pageSize": preferred_page_size,
    "tagType": 2,
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.okx.com/web3/markets/kol",
    "Origin": "https://www.okx.com",
}

def _latin1_sanitize(val: str) -> str:
    """OKX headers需符合 latin-1，去除無法編碼字元避免 UnicodeEncodeError"""
    if val is None:
        return ""
    if not isinstance(val, str):
        val = str(val)
    return val.encode("latin-1", "ignore").decode("latin-1")

# 若需要簽名/身分資訊，可在同目錄建立 okx_headers.json 追加 headers（例如 x-sign, x-ts, Cookie 等）
custom_headers_path = "okx_headers.json"
try:
    with open(custom_headers_path, "r", encoding="utf-8") as hf:
        user_headers = json.load(hf)
        if isinstance(user_headers, dict):
            safe_headers = {k: _latin1_sanitize(v) for k, v in user_headers.items() if v is not None}
            headers.update(safe_headers)
            required = [
                "Ok-Verify-Sign",
                "Ok-Verify-Token",
                "Ok-Timestamp",
                "x-device-id",
                "x-cdn",
                "x-fp-token",
                # x-fp-token-signature 視情況
                "Cookie",
            ]
            missing = [h for h in required if h not in safe_headers]
            if missing:
                print(f"缺少必要 headers 可能導致 400/50113: {missing}")
            print(f"已載入自定義 headers: {list(safe_headers.keys())}")
except FileNotFoundError:
    pass
except Exception as e:
    print(f"讀取自定義 headers 失敗: {e}")

# 收集結果（依 address 去重）
all_data = []
seen_addresses = set()


def extract_twitter_username(url: str):
    """從 Twitter/X URL 取出用戶名"""
    if not url:
        return None
    parsed = urlparse(url.strip())
    path = parsed.path or ""
    username = path.lstrip("/").split("/")[0].strip()
    return username or None


def pick_kol_info(t_list):
    """從 t 欄位中取得 kol 名稱與 Twitter 連結"""
    if not isinstance(t_list, list):
        return None, None
    for entry in t_list:
        if not isinstance(entry, dict):
            continue
        if entry.get("k") != "kol":
            continue
        e = entry.get("e") or {}
        return e.get("name"), e.get("kolTwitterLink")
    return None, None


page = 1
params = dict(base_params)
while True:
    params["pageNum"] = page
    params["t"] = int(time.time() * 1000)  # 動態時間戳，每次請求更新
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        json_data = response.json()

        # 成功條件：code == 0
        if json_data.get("code") != 0:
            if params.get("pageSize") != fallback_page_size:
                print("pageSize=100 取得失敗，退回 50 重試同一頁")
                params["pageSize"] = fallback_page_size
                continue
            print(f"API 返回失敗: {json_data.get('msg', '未知錯誤')}")
            break

        data_block = json_data.get("data", {}) if isinstance(json_data.get("data"), dict) else {}
        addresses = data_block.get("addresses", [])
        if not addresses:
            print(f"頁碼 {page} 無數據，爬取結束。")
            break

        filtered_items = []
        for addr in addresses:
            wallet = addr.get("collectAddress")
            if not wallet or wallet in seen_addresses:
                continue
            seen_addresses.add(wallet)
            twitter_name, twitter_link = pick_kol_info(addr.get("t"))
            filtered_items.append(
                {
                    "address": wallet,
                    "twittera_name": twitter_name,
                    "twitter_username": extract_twitter_username(twitter_link),
                    "chainId": addr.get("chainId"),
                }
            )

        all_data.extend(filtered_items)
        print(f"已爬取頁碼 {page}，數據數量: {len(filtered_items)}")
        page += 1

    except requests.exceptions.RequestException as e:
        if params.get("pageSize") != fallback_page_size:
            print(f"pageSize=100 請求錯誤，退回 50 重試同一頁: {e}")
            params["pageSize"] = fallback_page_size
            continue
        print(f"請求錯誤: {e}")
        break

# 輸出到 JSON 檔案
if all_data:
    with open("okx_leaderboard.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print("所有數據已輸出到 okx_leaderboard.json")
else:
    print("無數據可輸出")

