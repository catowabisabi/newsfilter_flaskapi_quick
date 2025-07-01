import os
import requests
import time
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup




class NewsfilterApi:
    def __init__(self):
        load_dotenv(override=True)
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.search_api_url = os.getenv("SEARCH_API_URL")
        self.token_refresh_url = os.getenv("TOKEN_REFRESH_URL")
        self.token_file = ".env"  # 假設你用 .env 做儲存
        self.last_refresh_time = time.time()
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "Origin": "https://newsfilter.io",
            "Referer": "https://newsfilter.io/",
            "User-Agent": "Mozilla/5.0 ..."
        }

    def login(self):
        payload = {
            "type": "refreshTokens",
            "refreshToken": self.refresh_token
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(self.token_refresh_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens.get("accessToken")
            self.refresh_token = tokens.get("refreshToken")

            # 更新 .env 檔案內容
            self._update_env_token("ACCESS_TOKEN", self.access_token)
            self._update_env_token("REFRESH_TOKEN", self.refresh_token)

            self.last_refresh_time = time.time()
            print("🔁 Token refreshed successfully.")
        else:
            raise Exception(f"❌ Failed to refresh token: {response.status_code} {response.text}")

    def get_access_token(self):
        # 如果 access token 太舊（假設 12 小時），就 refresh
        if time.time() - self.last_refresh_time > 12 * 3600:
            print("⚠️ Access token 可能過期，嘗試 refresh...")
            self.login()
        return self.access_token

    def get_refresh_token(self):
        return self.refresh_token

    def _update_env_token(self, key, value):
        # 更新 .env 檔案內容
        print(f"🔍 更新 .env 檔案內容: {key} = {value}")
        print("這功能沒有實作")
        pass
        """ lines = []
        updated = False
        with open(self.token_file, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    lines.append(f"{key}={value}\n")
                    updated = True
                else:
                    lines.append(line)
        if not updated:
            lines.append(f"{key}={value}\n")
        with open(self.token_file, "w") as f:
            f.writelines(lines) """
    
    def get_articles_by_symbol(self, symbol: str):
        print(f"🔍 正在獲取 {symbol} 相關文章...")
        def call_api():
            headers = self.headers
            payload ={"type":"filterArticles","isPublic":False,"queryString":f"title:\"{symbol}\" OR description:\"{symbol}\" OR symbols:\"{symbol}\"","from":0,"size":50}

            return requests.post(self.search_api_url, json=payload, headers=headers)

        self.response = call_api()

        # 1. 如果 status code 是 401，先 login 再 retry
        if self.response.status_code == 401:
            print("⚠️ Token expired. Refreshing...")
            self.login()
            self.response = call_api()

        # 2. 如果是 200，但 articles 是空的，都試 login 再 retry
        if self.response.status_code == 200:
            self.articles_data = self.response.json()   
            if "articles" in self.articles_data and len(self.articles_data["articles"]) == 0:
                print("⚠️ 200 OK 但無內容，嘗試 refresh token 再撈...")
                self.login()
                self.response = call_api()
                self.articles_data = self.response.json()
            print(f"🔍 {symbol} 文章數量: {len(self.articles_data['articles'])}")
            return self.articles_data

        # 3. 其他錯誤
        raise Exception(f"❌ Failed to fetch articles: {self.response.status_code} {self.response.text}")
    
    def print_articles(self):
    
        if self.articles_data["articles"] == []:
            print("❌ No articles data available for today and yesterday")
            return
        for i, article in enumerate(self.articles_data.get("articles", []), 1):
            print(f"\n📰 Article {i}")
            print(f"📅 Published At : {article.get('publishedAt')}")
            print(f"🧾 Title        : {article.get('title')}")
            print(f"📝 Description  : {article.get('description')}")
            print(f"📰 Source       : {article.get('source', {}).get('name')}")
            #print(f"📈 Symbols      : {', '.join(article.get('symbols', []))}")
            #print(f"🏷️  Industries   : {', '.join(article.get('industries', [])) if 'industries' in article else 'N/A'}")
            #print(f"🏭 Sectors      : {', '.join(article.get('sectors', [])) if 'sectors' in article else 'N/A'}")
            print(f"🖼️  Image URL    : {article.get('imageUrl', 'N/A')}")
            print(f"🔗 Source URL   : {article.get('sourceUrl', 'N/A')}")
            print(f"📎 Newsfilter   : {article.get('url')}")
            print(f"📝 HTML Content : {article.get('html_content')[:100]}...")

    def filter_by_date_range(self, articles, start_date, end_date):
        filtered = []
        for article in articles:
            published_at = article.get("publishedAt")
            if published_at:
                try:
                    # 將 "Z" 改成 "+00:00"，將 "+0000" 改成 "+00:00"
                    ts = published_at.replace("Z", "+00:00").replace("+0000", "+00:00")
                    pub_date = datetime.fromisoformat(ts).date()
                    if start_date <= pub_date <= end_date:
                        filtered.append(article)
                except Exception as e:
                    print(f"⚠️ 日期解析錯誤: {published_at}")
        return filtered

    def _download_html(self,url):
        headers = self.headers
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 如果 status code 唔係 200 就會報錯
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"下載失敗：{e}")

    def get_today_and_yesterday_articles(self, symbol: str):
        all_articles_data = self.get_articles_by_symbol(symbol)
        all_articles = all_articles_data.get("articles", [])

        est = ZoneInfo("America/New_York")
        today = datetime.now(est).date()
        yesterday = today - timedelta(days=1)

        filtered_articles = self.filter_by_date_range(all_articles, yesterday, today)
        self.articles_data = {"articles": filtered_articles}
        print(f"🔍 今天與昨天的文章數量: {len(filtered_articles)}")
        self.get_html_content()
        return self.articles_data


    def get_html_content(self):

        def download_rendered_html(url):
            # 要加嘅自定 header
            headers = self.headers

            # Selenium Wire 的 header 設定
            seleniumwire_options = {
                'custom_headers': headers
            }

            options = Options()
            options.add_argument('--headless')  # 無頭
            options.add_argument('--disable-gpu')
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
            


            driver = webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.get(url)
            time.sleep(5)  # 等 JS 載完

            rendered_html = driver.page_source
                   
            soup = BeautifulSoup(rendered_html, "html.parser")
            article_div = soup.find("div", class_="col-lg-10 col-lg-offset-1")
            paragraphs = article_div.find_all("p") if article_div else []
            article_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
            driver.quit()

            return article_text


        for article in self.articles_data["articles"]:
            html_content = download_rendered_html(article["url"])
            article["html_content"] = html_content

        return self.articles_data
        








if __name__ == "__main__":
    api = NewsfilterApi()
    token = api.get_access_token()
    print(f"🔐 ACCESS_TOKEN: {token[:30]} ... ")
    articles_data = api.get_today_and_yesterday_articles("ALG")


    api.print_articles()


    



