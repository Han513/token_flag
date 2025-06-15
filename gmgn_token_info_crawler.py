import re
import os
import time
import logging
import random
import requests
import schedule
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

load_dotenv()

# 設置日誌格式為 UTC+8 時區
class UTC8Formatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = time.localtime(record.created + 8 * 3600)  # 轉換為 UTC+8
        if datefmt:
            return time.strftime(datefmt, ct)
        return time.strftime('%Y-%m-%d %H:%M:%S', ct)

os.makedirs('./logs', exist_ok=True)

log_path = "./logs/token_crawler.log"
logger = logging.getLogger()
handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
formatter = UTC8Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 同時輸出到控制台
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

GET_URL = os.getenv("GET_URL")
POST_URL = os.getenv("POST_URL")
BRAND = os.getenv("BRAND", "BYD")
HEADLESS_MODE = os.getenv("HEADLESS", "true").lower() == "true"

def close_login_modal(driver, debug=False):
    try:
        x_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.chakra-modal__header .cursor-pointer'))
        )
        x_btn.click()
        if debug:
            logger.info("已精確點擊 X 關閉登入彈窗")
        time.sleep(1.2)
        return True
    except Exception as e:
        if debug:
            logger.error(f"精確點擊 X 關閉彈窗失敗: {e}")
        return False

def complete_onboarding_flow(driver, debug=False):
    try:
        # 依序點擊「下一個」按鈕
        for _ in range(5):
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'pi-btn') and .//span[text()='下一個']]"))
            )
            next_btn.click()
            if debug:
                logger.info("已點擊 下一個")
            time.sleep(random.uniform(1, 3))
        # 點擊「完成」按鈕
        finish_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'pi-btn') and .//span[text()='完成']]"))
        )
        finish_btn.click()
        if debug:
            logger.info("已點擊 完成")
        time.sleep(1.2)
    except Exception as e:
        if debug:
            logger.error(f"教學步驟點擊失敗: {e}")

def get_token_info(token_address):
    url = f"https://gmgn.ai/sol/token/{token_address}"
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--lang=zh-TW')
    if HEADLESS_MODE:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1200,900")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    try:
        # 在 Docker 環境中使用環境變數指定的 Chrome 路徑
        chrome_path = os.getenv('CHROME_BIN')
        driver_path = os.getenv('CHROMEDRIVER_PATH')
        
        if chrome_path and driver_path:
            driver = uc.Chrome(
                options=options,
                version_main=137,  # 與 Dockerfile Stable 137.0.7151.55 對應
                browser_executable_path=chrome_path,
                driver_executable_path=driver_path
            )
        else:
            driver = uc.Chrome(options=options, version_main=136)

        driver.set_window_size(1200, 900)
        driver.get(url)
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            });
        '''
        })

        # 隨機等待，模擬真人行為
        time.sleep(random.uniform(3, 6))

        # 模擬滑動頁面
        for _ in range(random.randint(2, 4)):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(random.uniform(0.5, 1))

        # 1. 關閉登入彈窗
        close_login_modal(driver, debug=True)

        # 2. 點擊教學步驟（下一個、完成）
        complete_onboarding_flow(driver, debug=True)

        # 取得整個網頁 HTML
        page_source = driver.page_source
        with open('./pages/page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        logger.info("已將網頁 HTML 存檔為 page_source.html")

        driver.quit()

        # 解析 HTML 並提取指標
        soup = BeautifulSoup(page_source, 'html.parser')
        title = soup.title.string if soup.title else ''

        # 1. DEV 狀態
        dev_status = 0
        try:
            transaction_div = soup.find('div', class_='flex undefined text-red-100')
            if not transaction_div:
                transaction_div = soup.find('div', class_='flex text-green-100')
            if transaction_div:
                svg = transaction_div.find('svg')
                transaction_type = transaction_div.get_text(strip=True).lower()
                fill_color = svg.get('fill', '').lower() if svg else ''
                if transaction_type == 'add' or transaction_type == '加池子':
                    dev_status = 4
                elif transaction_type == 'burn' or transaction_type == '燒池子':
                    dev_status = 5
                elif transaction_type == 'sell':
                    dev_status = 1
                elif transaction_type == 'buy':
                    dev_status = 2
                elif transaction_type == 'run':
                    dev_status = 3
                elif transaction_type == 'remove liq' or transaction_type == '撤池子':
                    dev_status = 6
        except Exception:
            pass

        # 2. CTO 標籤
        cto = False
        try:
            outer_divs = soup.find_all("div", class_="relative flex items-center gap-x-4px")
            for outer_div in outer_divs:
                pointer_div = outer_div.find("div", class_="flex items-center cursor-pointer")
                if not pointer_div:
                    continue
                inner_flex = pointer_div.find("div", class_="flex")
                if not inner_flex:
                    continue
                svg = inner_flex.find("svg")
                if svg:
                    svg_class = svg.get("class", [])
                    if (
                        "text-yellow-100" in svg_class and
                        svg.get("fill") == "currentColor" and
                        svg.get("height") == "12px" and
                        svg.get("width") == "12px" and
                        svg.get("viewbox") == "0 0 20 20"
                    ):
                        cto = True
                        break
        except Exception as e:
            print("Error:", e)

        # 3. 四個指標 Mint丟棄、黑名單、燒池子、Top 10
        indicators = {}
        try:
            indicator_classes = [
                'items-center', 'gap-x-4px', '!text-increase', 'font-medium',
                'text-[13px]', 'text-text-200', 'whitespace-pre'
            ]
            def class_matcher(x):
                if not x:
                    return False
                if isinstance(x, str):
                    x = x.split()
                return all(cls in x for cls in indicator_classes)
            indicator_tags = soup.find_all('div', class_=class_matcher)
            for tag in indicator_tags:
                label = None
                prev = tag.find_previous_sibling()
                if prev and prev.text:
                    label = prev.text.strip()
                if label == 'Burnt' or label == '燒池子':
                    value_div = tag.find('div')
                    value = value_div.get_text(strip=True) if value_div else tag.get_text(strip=True)
                    num_match = re.search(r"[\d.]+", value)
                    indicators['燒池子'] = float(num_match.group()) if num_match else None
                else:
                    value = tag.get_text(strip=True)
                    if label in ['NoMint', 'Mint', 'Mint丟棄']:
                        indicators['Mint丟棄'] = value in ['是', 'Yes', 'true', 'True', '有']
                    elif label == 'Blacklist' or label == '黑名單':
                        indicators['黑名單'] = value in ['是', 'Yes', 'true', 'True', '有']
                    elif label == 'Top 10':
                        num_match = re.search(r"[\d.]+", value)
                        indicators['Top 10'] = float(num_match.group()) if num_match else None
        except Exception:
            pass

        return {
            'title': title,
            'dev_status': dev_status,
            'cto': cto,
            'indicators': indicators
        }
    except Exception as e:
        logger.error(f"Chrome 初始化失敗: {e}")
        return None

def convert_result(token_address, brand, parsed_result):
    return {
        "network": "SOLANA",
        "tokenAddress": token_address,
        "cto": parsed_result["cto"],
        "devStatus": parsed_result["dev_status"],
        "burnPercentage": parsed_result["indicators"].get("燒池子", 0),
        "brand": brand
    }

def main_batch_runner():
    try:
        response = requests.get(GET_URL)
        response.raise_for_status()
        tokens = response.json().get("data", [])
    except Exception as e:
        logger.error(f"GET 請求錯誤: {e}")
        return

    results = []
    for idx, token in enumerate(tokens, start=1):
        token_address = token["tokenAddress"]
        logger.info(f"處理 {token_address} 中...")
        parsed = get_token_info(token_address)
        if parsed:
            result = convert_result(token_address, brand=BRAND, parsed_result=parsed)
            logger.info(result)
            results.append(result)

            if len(results) >= 5:
                try:
                    post_resp = requests.post(POST_URL, json=results)
                    post_resp.raise_for_status()
                    logger.info(f"已上傳 {len(results)} 筆資料")
                    results.clear()
                except Exception as e:
                    logger.error(f"POST 請求錯誤（第 {idx} 筆後）: {e}")

    if results:
        try:
            post_resp = requests.post(POST_URL, json=results)
            post_resp.raise_for_status()
            logger.info(f"最後補上傳 {len(results)} 筆資料")
        except Exception as e:
            logger.error(f"POST 最後一批請求錯誤: {e}")

def run_daily_job():
    logger.info("⏰ 執行定時任務：", time.strftime('%Y-%m-%d %H:%M:%S'))
    main_batch_runner()

if __name__ == "__main__":
    logger.info(f"🚀 啟動後立即執行一次：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    main_batch_runner()

    # 每天 UTC 16:00 = 台灣時間 00:00 執行一次
    schedule.every().day.at("16:00").do(run_daily_job)

    # 持續執行排程監聽
    while True:
        schedule.run_pending()
        time.sleep(60)