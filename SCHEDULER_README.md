# KOL 爬蟲定時任務

## 概述

這個定時任務系統會每天凌晨2:00 (UTC+8) 自動執行 KOL 爬蟲，獲取 SOLANA 和 BSC 鏈上的 KOL 錢包數據。

## 環境配置

### 1. 創建 .env 文件

複製 `env.example` 文件為 `.env` 並配置參數：

```bash
cp env.example .env
```

### 2. 配置 smartmoney_import 參數

在 `.env` 文件中設置 Smart Money Import API 的 URL：

```env
# Smart Money Import API URL
smartmoney_import=http://127.0.0.1:8070/api/wallets/analyze-kol-wallets
```

## 文件說明

- `scheduler.py`: 定時任務調度器
- `start_scheduler.py`: 啟動腳本
- `Dockerfile.scheduler`: 定時任務的 Docker 配置
- `docker-compose.yml`: 包含定時任務服務的 Docker Compose 配置
- `env.example`: 環境變量配置示例
- `.env`: 環境變量配置文件（需要手動創建）

## 使用方法

### 方法一：使用 Docker Compose（推薦）

1. 啟動定時任務服務：
```bash
docker-compose up -d kol_scheduler
```

2. 查看日誌：
```bash
docker-compose logs -f kol_scheduler
```

3. 停止服務：
```bash
docker-compose down kol_scheduler
```

### 方法二：直接運行 Python 腳本

1. 安裝依賴：
```bash
pip install -r requirements.txt
```

2. 運行定時任務：
```bash
python start_scheduler.py
```

### 方法三：使用系統的 cron 任務

如果您想使用系統的 cron 任務，可以添加以下 cron 任務：

```bash
# 編輯 crontab
crontab -e

# 添加以下行（每天凌晨2:00執行）
0 2 * * * cd /path/to/your/project && python gmgn_kol_crawler.py >> logs/cron.log 2>&1
```

## 日誌文件

- `logs/scheduler.log`: 調度器運行日誌
- `logs/startup.log`: 啟動日誌
- `logs/kol_scheduler.log`: KOL 爬蟲綜合日誌

### 查看日誌

#### 方法一：使用日誌查看腳本

```bash
# 查看所有日誌
python view_logs.py

# 查看特定日誌
python view_logs.py --type scheduler
python view_logs.py --type startup
python view_logs.py --type kol

# 查看指定行數
python view_logs.py --lines 100
```

#### 方法二：直接查看文件

```bash
# 查看調度器日誌
tail -f logs/scheduler.log

# 查看啟動日誌
tail -f logs/startup.log

# 查看 KOL 爬蟲日誌
tail -f logs/kol_scheduler.log

# 查看所有日誌
tail -f logs/*.log
```

#### 方法三：Docker 日誌

```bash
# 查看容器日誌
docker-compose logs -f kol_scheduler

# 查看最近的日誌
docker-compose logs --tail=100 kol_scheduler
```

## 配置說明

### 修改執行時間

在 `scheduler.py` 中修改以下行：
```python
# 每天凌晨2:00執行
schedule.every().day.at("02:00").do(run_kol_crawler)

# 例如：每天凌晨3:00執行
schedule.every().day.at("03:00").do(run_kol_crawler)
```

### 添加更多鏈

在 `scheduler.py` 的 `run_kol_crawler()` 函數中添加：
```python
# 執行其他鏈的爬蟲
logger.info("執行 ETH 爬蟲...")
fetch_and_process_kol('ETH')
```

## 注意事項

1. 確保服務器時區設置正確（UTC+8）
2. 確保網絡連接正常
3. 確保目標 API 服務可用
4. 建議在生產環境中使用 Docker 方式運行

## 故障排除

### 查看日誌
```bash
# Docker 方式
docker-compose logs kol_scheduler

# 直接運行方式
tail -f logs/scheduler.log
```

### 手動執行測試
```bash
python gmgn_kol_crawler.py
```

### 檢查時區
```bash
# 在容器內檢查時區
docker exec -it kol_scheduler date
``` 