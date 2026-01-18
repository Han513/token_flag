import requests
import json
import uuid

# 收集所有 KOL 資料以輸出 JSON，依 address 去重（用字典存儲，方便更新）
all_data = []
address_dict = {}

# 讀取已有的 JSON 文件（如果存在）
existing_file = "gmgn_leaderboard.json"
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

def generate_uuid():
    return str(uuid.uuid4())

def send_to_local_api(*args, **kwargs):
    # 已停用本地 API 發送
    return

def process_gmgn_data(data, chain, tag_label):
    addresses = []
    twitter_names = []
    twitter_usernames = []
    new_count = 0
    updated_count = 0
    
    if isinstance(data, dict) and 'data' in data and 'rank' in data['data']:
        items = data['data']['rank']
        for item in items:
            if 'address' in item:
                addr = item['address']
                t_name = item.get('twitter_name', '')
                t_user = item.get('twitter_username', '')
                
                new_item = {
                    "address": addr,
                    "twittera_name": t_name,
                    "twitter_username": t_user,
                    "chain": chain,
                    "tag": tag_label,
                }
                
                # 如果地址已存在，更新信息（優先使用新的非空值）
                if addr in address_dict:
                    existing_item = address_dict[addr]
                    # 更新 Twitter 信息（如果新值非空）
                    if t_name:
                        existing_item["twittera_name"] = t_name
                    if t_user:
                        existing_item["twitter_username"] = t_user
                    # 更新 chain 和 tag（使用最新的）
                    existing_item["chain"] = chain
                    existing_item["tag"] = tag_label
                    updated_count += 1
                else:
                    # 新地址，添加到字典
                    address_dict[addr] = new_item
                    addresses.append(addr)
                    twitter_names.append(t_name)
                    twitter_usernames.append(t_user)
                    new_count += 1
    
    print(f"[{chain}][{tag_label}] 解析出 addresses 數量：新增 {new_count}，更新 {updated_count}")
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
        {
            "chain": "BASE",
            "tag": "default",
            "url": "https://gmgn.ai/defi/quotation/v1/rank/base/wallets/7d?device_id=824fc022-33bb-4de9-9120-4b10b37804e7&fp_did=66f2c28e426001e958847383245163e7&client_id=gmgn_web_20260115-9909-b6161f8&from_app=gmgn&app_ver=20260115-9909-b6161f8&tz_name=Asia%2FTaipei&tz_offset=28800&app_lang=zh-TW&os=web&worker=0&orderby=last_active&direction=desc",
        },
    ]

    for ep in endpoints:
        fetch_and_process(ep["url"], ep["chain"], ep["tag"])
    
    # 將字典轉換為列表並輸出到 JSON 檔案
    if address_dict:
        all_data = list(address_dict.values())
        with open("gmgn_leaderboard.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f"所有 GMGN KOL 數據已輸出到 gmgn_leaderboard.json，共 {len(all_data)} 個地址")
    else:
        print("無 GMGN 數據可輸出")