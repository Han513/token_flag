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

### 2. 首次部署

1. 構建 Docker 映像：
```bash
docker-compose build
```

2. 啟動服務：
```bash
docker-compose up -d
```

### 3. 後續更新

如果程式碼有更新，需要重新構建並啟動：
```bash
docker-compose up -d --build
```

### 4. 查看日誌

```bash
docker-compose logs -f
```

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
