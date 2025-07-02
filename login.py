from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from lxml import etree
import time
import tempfile
import json
import gzip
import io

class NewsfilterLogin:
    def __init__(self):
            

        options = Options()
        options.add_argument('--headless')  # 無頭
        options.add_argument('--disable-gpu')
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
        
        tmp_profile = tempfile.mkdtemp()
        options.add_argument(f'--user-data-dir={tmp_profile}')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-blink-features=AutomationControlled')


        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def login(self):
        self.driver.get("https://newsfilter.io/login")
        time.sleep(2)  # 等 JS 載完

        self.driver.find_element(By.ID, "sign-up-email").send_keys("enomars@gmail.com")
        self.driver.find_element(By.ID, "sign-up-password").send_keys("Good4me1986.")

        button_xpath = '//*[@id="root"]/div[2]/div/div/div[3]/div[3]/button'
        self.driver.find_element(By.XPATH, button_xpath).click()

        # 等待 API 請求完成
        time.sleep(5)
        
        # 尋找包含 token 的請求
        for request in self.driver.requests:
            if request.response and 'api.newsfilter.io/public/actions' in request.url:
                try:
                    # 處理可能的 gzip 壓縮
                    body = request.response.body
                    if body.startswith(b'\x1f\x8b'):  # gzip magic number
                        body = gzip.decompress(body)
                    response_body = body.decode('utf-8')
                    response_json = json.loads(response_body)
                    if 'accessToken' in response_json:
                        #print("Access Token:", response_json['accessToken'])
                        pass
                    if 'refreshToken' in response_json:
                        #print("Refresh Token:", response_json['refreshToken'])
                        pass
                        self.driver.quit()
                        return response_json['accessToken'], response_json['refreshToken']
                except Exception as e:
                    print(f"Error processing response: {e}")
                    continue

        time.sleep(2)
        self.driver.quit()


if __name__ == "__main__":
    login = NewsfilterLogin()
    access_token, refresh_token = login.login()
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")

