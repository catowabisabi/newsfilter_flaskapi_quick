import os
import requests
from dotenv import load_dotenv

class NewsfilterApi:
    def __init__(self):
        load_dotenv(override=True)
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.search_api_url = os.getenv("SEARCH_API_URL")

    def get_articles_by_symbol(self, symbol: str):
        headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {self.access_token}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Origin": "https://newsfilter.io",
    "Referer": "https://newsfilter.io/"
}

        payload ={
            "type":"filterArticles",
            "isPublic":False,
            "queryString":"title:\"{symbol}\" OR description:\"{symbol}\" OR symbols:\"{symbol}\"",
            "from":0,
            "size":50
            }

        print(">>> Request Headers:", headers)
        print(">>> Request Payload:", payload)

        response = requests.post(self.search_api_url, json=payload, headers=headers)
        
        print(">>> Response Status Code:", response.status_code)
        print(">>> Response Headers:", response.headers)
        print(">>> Response Text:", response.text)

        if response.status_code == 200:
            data = response.json()
            return data.get("articles", [])
        else:
            raise Exception(f"Failed to fetch articles: {response.status_code} {response.text}")


if __name__ == "__main__":
    api = NewsfilterApi()
    articles = api.get_articles_by_symbol("AAPL")
    for i, article in enumerate(articles, 1):
        print(f"\nArticle {i}:")
        print("Title:", article.get("title"))
        print("PublishedAt:", article.get("publishedAt"))
        print("URL:", article.get("url"))
