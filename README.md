# NewsFilter API 新聞過濾器 API

## Description 描述

This is a Flask-based API wrapper for NewsFilter.io that fetches and processes financial news articles.
這是一個基於 Flask 的 NewsFilter.io API 封裝器，用於獲取和處理金融新聞文章。

## Features 功能

- Fetch news articles by stock symbol 透過股票代碼獲取新聞文章
- Get today and yesterday's articles 獲取今天和昨天的文章
- Extract article content using Selenium 使用 Selenium 提取文章內容
- RESTful API endpoints RESTful API 端點

## Prerequisites 前置要求

- Python 3.9+ Python 3.9 或以上版本
- Docker (optional) Docker（可選）
- Chrome/Chromium browser Chrome/Chromium 瀏覽器

## Installation 安裝

### Local Setup 本地設置

1. Clone the repository 克隆存儲庫
```bash
git clone <repository-url>
cd newsfilter-api
```

2. Install dependencies 安裝依賴
```bash
pip install -r requirements.txt
```

3. Set up environment variables 設置環境變量
```bash
cp .env.example .env
# Edit .env with your credentials 使用您的憑證編輯 .env
```

### Docker Setup Docker 設置

1. Build the image 建立映像
```bash
docker build -t newsfilter-api .
```

2. Run the container 運行容器
```bash
docker run -p 5000:5000 --env-file .env newsfilter-api
```

## Usage 使用方法

### API Endpoints API 端點

1. Health Check 健康檢查
```
GET /health
```

2. Get News Articles 獲取新聞文章
```
GET /api/news/<symbol>
```

Example 示例:
```bash
curl http://localhost:5000/api/news/ALG
```

## Environment Variables 環境變量

See `.env.example` for required environment variables.
請參閱 `.env.example` 了解所需的環境變量。

## Contributing 貢獻

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
歡迎提交 Pull Request。對於重大更改，請先開啟一個 Issue 來討論您想要更改的內容。

## License 許可證

MIT 