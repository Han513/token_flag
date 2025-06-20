import schedule
import time
import logging
from datetime import datetime
import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gmgn_kol_crawler import fetch_and_process_kol

# 確保 logs 目錄存在
os.makedirs('logs', exist_ok=True)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.FileHandler('logs/kol_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_kol_crawler():
    """執行 KOL 爬蟲任務"""
    logger.info("=" * 40)
    logger.info("開始執行 KOL 爬蟲任務")
    logger.info(f"執行時間: {datetime.now()}")
    logger.info("=" * 40)
    
    try:
        # 執行 SOLANA 爬蟲
        logger.info("執行 SOLANA 爬蟲...")
        fetch_and_process_kol('SOLANA')
        
        # 執行 BSC 爬蟲
        logger.info("執行 BSC 爬蟲...")
        fetch_and_process_kol('BSC')
        
        logger.info("KOL 爬蟲任務執行完成")
        logger.info("=" * 40)
    except Exception as e:
        logger.error(f"KOL 爬蟲任務執行失敗: {str(e)}")
        logger.error("=" * 40)

def main():
    """主函數"""
    logger.info("=" * 50)
    logger.info("KOL 爬蟲定時任務啟動")
    logger.info(f"啟動時間: {datetime.now()}")
    logger.info("=" * 50)
    
    # 1. 先執行一次爬蟲任務
    logger.info("執行啟動時的初始爬蟲任務...")
    run_kol_crawler()
    logger.info("初始爬蟲任務完成")
    
    # 2. 設置定時任務（每天凌晨2:00執行）
    logger.info("設置定時任務：每天凌晨2:00執行")
    schedule.every().day.at("02:00").do(run_kol_crawler)
    
    logger.info("定時任務設置完成，開始等待...")
    logger.info("=" * 50)
    
    # 3. 運行調度器
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分鐘檢查一次

if __name__ == "__main__":
    main()
else:
    logger.info("scheduler.py 被作為模塊導入") 