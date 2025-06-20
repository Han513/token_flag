## 系統需求

- Docker
- Docker Compose

## 快速開始

### 1. 環境設置

1. 複製環境變數範例文件：
```bash
cp .env.example .env
```

2. 編輯 `.env` 文件，設置必要的環境變數：
```env
GET_URL=your_get_url_here
POST_URL=your_post_url_here
BRAND=BYD
HEADLESS=true
```

### 2. 啟動與管理服務

- **重建並重啟所有服務（推薦日常用法）**
  ```bash
  ./restart.sh
  ```
- **重啟單一服務**
  ```bash
  ./restart.sh kol_scheduler
  ./restart.sh token_crawler
  ```
- **查看狀態**
  ```bash
  ./restart.sh status
  ```
- **查看日誌**
  ```bash
  ./restart.sh logs kol_scheduler
  ./restart.sh logs token_crawler
  ```
- **停止所有服務**
  ```bash
  ./restart.sh stop all
  ```
- **啟動所有服務**
  ```bash
  ./restart.sh start all
  ```
- **重建單一服務**
  ```bash
  ./restart.sh build kol_scheduler
  ./restart.sh build token_crawler
  ```

> 傳統的 `docker-compose build`、`docker-compose up -d`、`docker-compose restart` 等指令都可以用 `./restart.sh` 來完成，讓操作更簡單！

## 目錄結構

```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .env
├── gmgn_token_info_crawler.py
├── logs/
└── pages/
```

## 環境變數說明

| 變數名稱 | 說明 | 預設值 |
|---------|------|--------|
| GET_URL | 獲取代幣列表的 API URL | - |
| POST_URL | 上傳爬取結果的 API URL | - |
| BRAND | 品牌名稱 | BYD |
| HEADLESS | 是否使用無頭模式 | true |

## 定時任務

- 服務啟動時會立即執行一次爬取任務
- 之後會在每天 UTC 16:00（台灣時間 00:00）自動執行

# 使用說明

## 快速指令

### 重啟單一服務
```bash
./restart.sh kol_scheduler
./restart.sh token_crawler
```

### 重建並重啟所有服務
```bash
./restart.sh rebuild
```

### 預設行為（無參數）
```bash
./restart.sh
```
> 不帶任何參數時，預設會自動重建並重啟所有服務（等同於 `rebuild` 指令）

### 其他常用指令

- 啟動所有服務：
  ```bash
  ./restart.sh start all
  ```
- 停止所有服務：
  ```bash
  ./restart.sh stop all
  ```
- 查看狀態：
  ```bash
  ./restart.sh status
  ```
- 查看日誌：
  ```bash
  ./restart.sh logs kol_scheduler
  ./restart.sh logs token_crawler
  ```

## 指令說明
- `kol_scheduler`、`token_crawler`：直接輸入服務名即可重啟該服務
- `rebuild`：重建並重啟所有服務
- 無參數：預設執行 rebuild
- 其他指令（start/stop/logs/status/build/help）同原本用法

---

如有任何問題，請參考腳本內的 `show_help` 或聯絡開發者。
