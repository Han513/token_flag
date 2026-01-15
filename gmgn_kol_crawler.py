import requests
import json
import uuid

# 收集所有 KOL 資料以輸出 JSON，依 address 去重
all_data = []
seen_addresses = set()

def generate_uuid():
    return str(uuid.uuid4())

def send_to_local_api(*args, **kwargs):
    # 已停用本地 API 發送
    return

def process_gmgn_data(data, chain, tag_label):
    addresses = []
    twitter_names = []
    twitter_usernames = []
    
    if isinstance(data, dict) and 'data' in data and 'rank' in data['data']:
        items = data['data']['rank']
        for item in items:
            if 'address' in item:
                addr = item['address']
                t_name = item.get('twitter_name', '')
                t_user = item.get('twitter_username', '')
                if addr in seen_addresses:
                    continue
                seen_addresses.add(addr)
                addresses.append(addr)
                twitter_names.append(t_name)
                twitter_usernames.append(t_user)
                all_data.append(
                    {
                        "address": addr,
                        "twittera_name": t_name,
                        "twitter_username": t_user,
                        "chain": chain,
                        "tag": tag_label,
                    }
                )
    
    print(f"[{chain}][{tag_label}] 解析出 addresses 數量：", len(addresses))
    # 已取消本地 API 呼叫

def fetch_and_process(url, chain, tag_label):

    payload = {
        'api_key': 'b4d21e175c03905dafbca1dc561bcc44',
        'url': url,
    }
    
    try:
        r = requests.get('https://api.scraperapi.com/', params=payload)
        try:
            data = r.json()
            process_gmgn_data(data, chain, tag_label)
        except Exception:
            print(r.text)
    except Exception as e:
        print(f"[{chain}] 發生錯誤: {str(e)}")

if __name__ == "__main__":
    endpoints = [
        {
            "chain": "SOLANA",
            "tag": "smart_degen_pump_smart",
            "url": "https://gmgn.ai/defi/quotation/v1/rank/sol/wallets/7d?tag=smart_degen&tag=pump_smart&device_id=8c85142a-3582-44b5-8e5d-7141699eb961&fp_did=0434a9e00c52b961122f64fc217dd48c&client_id=gmgn_web_20251218-8915-e793f7a&from_app=gmgn&app_ver=20251218-8915-e793f7a&tz_name=Asia%2FTaipei&tz_offset=28800&app_lang=zh-TW&os=web&worker=0&is_v2=1&orderby=txs_1d&direction=desc",
        },
        {
            "chain": "SOLANA",
            "tag": "renowned",
            "url": "https://gmgn.ai/defi/quotation/v1/rank/sol/wallets/7d?tag=renowned&device_id=8c85142a-3582-44b5-8e5d-7141699eb961&fp_did=0434a9e00c52b961122f64fc217dd48c&client_id=gmgn_web_20251218-8915-e793f7a&from_app=gmgn&app_ver=20251218-8915-e793f7a&tz_name=Asia%2FTaipei&tz_offset=28800&app_lang=zh-TW&os=web&worker=0&is_v2=1&orderby=txs_1d&direction=desc",
        },
        {
            "chain": "BSC",
            "tag": "smart_degen_pump_smart",
            "url": "https://gmgn.ai/defi/quotation/v1/rank/bsc/wallets/7d?tag=smart_degen&tag=pump_smart&device_id=8c85142a-3582-44b5-8e5d-7141699eb961&fp_did=0434a9e00c52b961122f64fc217dd48c&client_id=gmgn_web_20251218-8915-e793f7a&from_app=gmgn&app_ver=20251218-8915-e793f7a&tz_name=Asia%2FTaipei&tz_offset=28800&app_lang=zh-TW&os=web&worker=0&is_v2=1&orderby=txs_1d&direction=desc",
        },
        {
            "chain": "BSC",
            "tag": "renowned",
            "url": "https://gmgn.ai/defi/quotation/v1/rank/bsc/wallets/7d?tag=renowned&device_id=8c85142a-3582-44b5-8e5d-7141699eb961&fp_did=0434a9e00c52b961122f64fc217dd48c&client_id=gmgn_web_20251218-8915-e793f7a&from_app=gmgn&app_ver=20251218-8915-e793f7a&tz_name=Asia%2FTaipei&tz_offset=28800&app_lang=zh-TW&os=web&worker=0&is_v2=1&orderby=txs_1d&direction=desc",
        },
    ]

    for ep in endpoints:
        fetch_and_process(ep["url"], ep["chain"], ep["tag"])
    
    # 輸出到 JSON 檔案
    if all_data:
        with open("gmgn_leaderboard.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print("所有 GMGN KOL 數據已輸出到 gmgn_leaderboard.json")
    else:
        print("無 GMGN 數據可輸出")