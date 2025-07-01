# 使用 Python 3.9 的輕量級映像檔作為基礎
FROM python:3.9-slim

# 設定 DEBIAN_FRONTEND 為 noninteractive，避免在安裝過程中出現互動式提示
ENV DEBIAN_FRONTEND=noninteractive

# 安裝依賴工具和 Chrome
RUN apt-get update && \
    apt-get install -y \
    wget \
    curl \
    gnupg2 \
    unzip \
    fonts-liberation \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    --no-install-recommends && \
    \
    # 新增 Google Chrome 的官方 APT 儲存庫金鑰
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    \
    # 新增 Google Chrome 的 APT 儲存庫來源
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    \
    # 再次更新套件列表以包含 Chrome 儲存庫
    apt-get update && \
    \
    # 安裝最新穩定版的 Google Chrome
    apt-get install -y google-chrome-stable && \
    \
    # 清理 APT 快取以減少映像檔大小
    rm -rf /var/lib/apt/lists/*

# 設定對應的 ChromeDriver 版本
# 根據 Google Chrome 138.0.7204.96 版本，選擇最接近的 ChromeDriver 穩定版
ENV CHROME_DRIVER_VERSION=138.0.7204.92

# 下載並安裝 ChromeDriver
# 使用 storage.googleapis.com 上的 Chrome for Testing 官方下載連結
RUN wget -q -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    # 解壓縮到一個臨時目錄
    unzip /tmp/chromedriver.zip -d /tmp/chromedriver_extract && \
    # 將 chromedriver 可執行檔移動到 /usr/local/bin/
    mv /tmp/chromedriver_extract/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    # 移除臨時解壓縮目錄
    rm -rf /tmp/chromedriver_extract && \
    # 賦予執行權限
    chmod +x /usr/local/bin/chromedriver

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式的其他檔案
COPY . .

# 暴露應用程式使用的連接埠
EXPOSE 8000

# 定義啟動應用程式的命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
