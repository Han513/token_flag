import json

def transform_crypto_data(input_data):
    """
    轉換原始數據到指定的格式
    """
    transformed_list = []
    
    for item in input_data:
        # 1. 取得錢包地址
        address = item.get("walletAddress", "")
        
        # 2. 判斷 chainId 邏輯 (0x 開頭為 56，其餘為 501)
        chain_id = "56" if address.startswith("0x") else "501"
        
        # 3. 提取 Twitter 相關資訊 (從 't' 陣列中尋找 'k' 為 'kol' 的項目)
        twitter_name = ""
        twitter_username = ""
        
        t_list = item.get("t", [])
        for t_item in t_list:
            if t_item.get("k") == "kol":
                e_data = t_item.get("e", {})
                twitter_name = e_data.get("name", "")
                
                # 從 Twitter 連結中擷取使用者名稱 (例如從 https://x.com/Reljoooo 擷取 Reljoooo)
                twitter_link = e_data.get("kolTwitterLink", "")
                if twitter_link:
                    twitter_username = twitter_link.split("/")[-1]
                break # 找到 KOL 資訊後即可停止搜尋
        
        # 4. 組合成目標格式
        entry = {
            "address": address,
            "twittera_name": twitter_name,
            "twitter_username": twitter_username,
            "chainId": chain_id
        }
        transformed_list.append(entry)
        
    return transformed_list

# --- 使用範例 ---

# 讀取同個資料夾下的 OKX_data.txt 檔案
try:
    import re
    
    with open('OKX_data.txt', 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # 處理多個 JSON 數組（文件可能包含多個獨立的 JSON 數組，用 ]\n[ 分隔）
    all_data = []
    
    # 方法：按 ']\n[' 或 ']\r\n[' 分割成多個 JSON 數組
    # 使用正則表達式找到所有數組分隔位置
    parts = re.split(r'\]\s*\n\s*\[', file_content)
    
    for i, part in enumerate(parts):
        if i == 0:
            # 第一個部分，確保以 ] 結尾
            if not part.rstrip().endswith(']'):
                part = part.rstrip() + '\n]'
        elif i == len(parts) - 1:
            # 最後一個部分，確保以 [ 開頭
            if not part.lstrip().startswith('['):
                part = '[\n' + part.lstrip()
        else:
            # 中間部分，添加開頭和結尾
            if not part.lstrip().startswith('['):
                part = '[\n' + part.lstrip()
            if not part.rstrip().endswith(']'):
                part = part.rstrip() + '\n]'
        
        try:
            data = json.loads(part)
            if isinstance(data, list):
                all_data.extend(data)
        except json.JSONDecodeError as e:
            # 如果分割方法失敗，嘗試直接解析整個文件（單個數組的情況）
            if i == 0 and len(parts) == 1:
                try:
                    all_data = json.loads(file_content)
                    if not isinstance(all_data, list):
                        all_data = [all_data]
                    break
                except json.JSONDecodeError:
                    print(f"JSON 解析錯誤: {e}")
                    raise
            continue

    print(f"成功讀取 {len(all_data)} 筆原始資料")
    
    # 執行轉換
    result = transform_crypto_data(all_data)

    # 讀取已存在的 okx_leaderboard.json（如果存在）
    existing_data = []
    try:
        with open('okx_leaderboard.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        # 如果文件不存在，使用空列表
        existing_data = []
    except json.JSONDecodeError:
        # 如果文件格式錯誤，使用空列表
        print("警告：okx_leaderboard.json 格式錯誤，將重新建立。")
        existing_data = []

    # 使用字典以 address 為 key 來快速查找和更新
    address_dict = {}
    
    # 先將現有數據載入字典
    for item in existing_data:
        address = item.get("address", "")
        if address:
            address_dict[address] = item
    
    # 處理新轉換的數據：更新或新增
    updated_count = 0
    added_count = 0
    for item in result:
        address = item.get("address", "")
        if address:
            if address in address_dict:
                # 如果 address 已存在，進行更新
                address_dict[address] = item
                updated_count += 1
            else:
                # 如果 address 不存在，新增
                address_dict[address] = item
                added_count += 1
    
    # 將字典轉換回列表
    final_data = list(address_dict.values())
    
    # 將結果寫入 okx_leaderboard.json
    with open('okx_leaderboard.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    print(f"轉換完成！已更新 okx_leaderboard.json")
    print(f"- 本次處理 {len(result)} 筆資料")
    print(f"- 新增 {added_count} 筆")
    print(f"- 更新 {updated_count} 筆")
    print(f"- 總共 {len(final_data)} 筆資料")

except FileNotFoundError:
    print("請確認 OKX_data.txt 檔案是否存在。")
except Exception as e:
    print(f"處理過程中發生錯誤: {e}")