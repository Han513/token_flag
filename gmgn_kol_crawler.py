import requests
import json
import uuid
import os
import time
import logging
from dotenv import load_dotenv

# 加載 .env 文件
load_dotenv()

logger = logging.getLogger(__name__)

def generate_uuid():
    return str(uuid.uuid4())

def send_to_local_api(addresses, twitter_names, twitter_usernames, chain):
    smartmoney_import_url = os.getenv('smartmoney_import', 'http://127.0.0.1:8070/api/wallets/analyze-kol-wallets')
    payload = {
        "addresses": addresses,
        "twitter_names": twitter_names,
        "twitter_usernames": twitter_usernames,
        "type": "add",
        "chain": chain
    }
    logger.info(f"[DEBUG] 即將推送到本地 API, addresses: {len(addresses)}, chain: {chain}")
    try:
        response = requests.post(smartmoney_import_url, json=payload, timeout=30)
        logger.info(f"[DEBUG] Local API Status Code: {response.status_code}")
        logger.info("[DEBUG] Response: %s", json.dumps(response.json(), ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error(f"[DEBUG] 發送到本地 API 時發生錯誤: {str(e)}")

def process_gmgn_data(data, chain):
    logger.info(f"[DEBUG] 進入 process_gmgn_data, chain: {chain}")
    addresses = []
    twitter_names = []
    twitter_usernames = []
    
    if isinstance(data, dict) and 'data' in data and 'rank' in data['data']:
        items = data['data']['rank']
        logger.info(f"[DEBUG] {chain} items 數量: {len(items)}")
        for item in items:
            if 'address' in item:
                addresses.append(item['address'])
                twitter_name = item.get('twitter_name', '')
                twitter_username = item.get('twitter_username', '')
                twitter_names.append(twitter_name if twitter_name is not None else '')
                twitter_usernames.append(twitter_username if twitter_username is not None else '')
                if twitter_name or twitter_username:
                    logger.info(f"找到 Twitter 信息 - 名稱: {twitter_name}, 用戶名: {twitter_username}")
    else:
        logger.warning(f"[DEBUG] {chain} 沒有正確的 rank 結構: {data}")
    
    logger.info(f"[DEBUG] [{chain}] 解析出 addresses 數量：{len(addresses)}")
    logger.info(f"[DEBUG] [{chain}] 解析出 twitter_names 數量：{len(twitter_names)}")
    logger.info(f"[DEBUG] [{chain}] 解析出 twitter_usernames 數量：{len(twitter_usernames)}")
    
    assert len(addresses) == len(twitter_names) == len(twitter_usernames), "列表長度不匹配"
    
    for i in range(0, len(addresses), 100):
        batch_addresses = addresses[i:i+100]
        batch_twitter_names = twitter_names[i:i+100]
        batch_twitter_usernames = twitter_usernames[i:i+100]
        logger.info(f"[DEBUG] send_to_local_api: batch {i//100+1}, addresses: {len(batch_addresses)}")
        send_to_local_api(batch_addresses, batch_twitter_names, batch_twitter_usernames, chain)

def fetch_and_process_kol(chain):
    logger.info(f"[DEBUG] 進入 fetch_and_process_kol, chain: {chain}")
    chain_lower = chain.lower()
    if chain.upper() == 'SOLANA':
        chain_lower = 'sol'
    else:
        chain_lower = chain.lower()
    url = f'https://gmgn.ai/defi/quotation/v1/rank/{chain_lower}/wallets/7d?tag=renowned&tz_name=Asia%2FTaipei&tz_offset=28800&app_lang=zh-TW&os=web&orderby=pnl_7d&direction=desc'

    payload = {
        'api_key': '51ee7f520ce905877b30fe53b1526c9f',
        'url': url,
    }
    
    logger.info(f"[DEBUG] [{chain}] 開始執行爬蟲...")
    logger.info(f"[DEBUG] [{chain}] 請求 URL: {url}")
    
    try:
        r = requests.get('https://api.scraperapi.com/', params=payload)
        logger.info(f"[DEBUG] [{chain}] GMGN API Status Code: {r.status_code}")
        logger.info(f"[DEBUG] [{chain}] 原始響應內容：")
        logger.info(r.text[:1000])  # 只打印前1000個字符，避免輸出過多
        try:
            data = r.json()
            # 檢查 API 返回的錯誤碼
            if data.get('code') != 0:
                logger.warning(f"[DEBUG] [{chain}] API 返回錯誤: {data.get('msg', '未知錯誤')}")
                return
            
            if isinstance(data, dict) and 'data' in data:
                logger.info(f"[DEBUG] [{chain}] 數據結構：")
                logger.info(f"- data 字段存在: {'data' in data}")
                logger.info(f"- rank 字段存在: {'rank' in data.get('data', {})}")
                if 'data' in data and 'rank' in data['data']:
                    logger.info(f"- rank 列表長度: {len(data['data']['rank'])}")
            process_gmgn_data(data, chain)
        except Exception as e:
            logger.error(f"[DEBUG] [{chain}] JSON 解析錯誤: {str(e)}")
            logger.error(r.text)
    except Exception as e:
        logger.error(f"[DEBUG] [{chain}] 發生錯誤: {str(e)}")

if __name__ == "__main__":
    fetch_and_process_kol('SOLANA')
    time.sleep(5)
    fetch_and_process_kol('BSC')