FROM python:3.10-slim

# 安裝必要的系統依賴
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxshmfence1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Chrome
RUN wget https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.55/linux64/chrome-linux64.zip \
    && unzip chrome-linux64.zip \
    && mv chrome-linux64 /opt/chrome \
    && ln -s /opt/chrome/chrome /usr/bin/chromium-browser \
    && rm chrome-linux64.zip

RUN wget https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.55/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/bin/chromedriver \
    && chmod +x /usr/bin/chromedriver \
    && rm -rf chromedriver-linux64 chromedriver-linux64.zip

# 設置 Python 環境
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 安裝 Python 依賴
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 創建必要的目錄
RUN mkdir -p /app/logs /app/pages

# 複製應用程式代碼
COPY . .

# 設置環境變數
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

