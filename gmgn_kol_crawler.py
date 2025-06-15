import requests
import json
import uuid

def generate_uuid():
    return str(uuid.uuid4())

def send_to_local_api(addresses, twitter_names, twitter_usernames, chain):
    url = "http://127.0.0.1:8070/api/wallets/analyze-kol-wallets"
    payload = {
        "addresses": addresses,
        "twitter_names": twitter_names,
        "twitter_usernames": twitter_usernames,
        "type": "add",
        "chain": chain
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Local API Status Code: {response.status_code}")
        print("Response:", json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"發送到本地 API 時發生錯誤: {str(e)}")

def process_gmgn_data(data, chain):
    addresses = []
    twitter_names = []
    twitter_usernames = []
    
    if isinstance(data, dict) and 'data' in data and 'rank' in data['data']:
        items = data['data']['rank']
        for item in items:
            if 'address' in item:
                addresses.append(item['address'])
                twitter_names.append(item.get('twitter_name', ''))
                twitter_usernames.append(item.get('twitter_username', ''))
    
    print(f"[{chain}] 解析出 addresses 數量：", len(addresses))
    for i in range(0, len(addresses), 100):
        batch_addresses = addresses[i:i+100]
        batch_twitter_names = twitter_names[i:i+100]
        batch_twitter_usernames = twitter_usernames[i:i+100]
        send_to_local_api(batch_addresses, batch_twitter_names, batch_twitter_usernames, chain)

def fetch_and_process_kol(chain):
    chain_lower = chain.lower()
    url = f'https://gmgn.ai/defi/quotation/v1/rank/{chain_lower}/wallets/7d?tag=renowned&tz_name=Asia%2FTaipei&tz_offset=28800&app_lang=zh-TW&os=web&orderby=pnl_7d&direction=desc'

    payload = {
        'api_key': '51ee7f520ce905877b30fe53b1526c9f',
        'url': url,
    }
    
    try:
        r = requests.get('https://api.scraperapi.com/', params=payload)
        print(r.text)
        print(f"[{chain}] GMGN API Status Code: {r.status_code}")
        print("\n格式化後的回應內容：")
        try:
            data = r.json()
            process_gmgn_data(data, chain)
        except Exception:
            print(r.text)
    except Exception as e:
        print(f"[{chain}] 發生錯誤: {str(e)}")

if __name__ == "__main__":
    fetch_and_process_kol('SOLANA')
    fetch_and_process_kol('BSC')