from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from newsfilter_api import NewsfilterApi
from typing import Dict, List, Optional
from pydantic import BaseModel

app = FastAPI(
    title="NewsFilter API",
    description="API for fetching financial news articles from NewsFilter.io",
    version="1.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 NewsfilterApi
api = NewsfilterApi()

class Article(BaseModel):
    publishedAt: str
    title: str
    description: Optional[str] = None
    source: Optional[Dict] = None
    imageUrl: Optional[str] = None
    sourceUrl: Optional[str] = None
    url: str
    html_content: Optional[str] = None

class ArticlesResponse(BaseModel):
    articles: List[Article]

@app.get("/health")
def health_check():
    """
    健康檢查端點
    Health check endpoint
    """
    return {"status": "healthy"}

@app.get("/api/news/{symbol}", response_model=ArticlesResponse)
async def get_news(symbol: str):
    """
    獲取指定股票代碼的新聞文章
    Get news articles for a specific stock symbol
    """
    try:
        articles_data = api.get_today_and_yesterday_articles(symbol)
        return articles_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 