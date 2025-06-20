#!/usr/bin/env python3
"""
定時任務啟動腳本
用於啟動 KOL 爬蟲的定時任務
"""

import os
import sys
import logging
from datetime import datetime

# 確保 logs 目錄存在
os.makedirs('logs', exist_ok=True)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/startup.log'),
        logging.FileHandler('logs/kol_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主函數"""
    logger.info("=" * 50)
    logger.info("KOL 爬蟲定時任務啟動")
    logger.info(f"啟動時間: {datetime.now()}")
    logger.info("=" * 50)
    
    try:
        # 導入並運行調度器
        from scheduler import main as scheduler_main
        scheduler_main()
    except KeyboardInterrupt:
        logger.info("收到中斷信號，正在關閉調度器...")
    except Exception as e:
        logger.error(f"調度器運行失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 