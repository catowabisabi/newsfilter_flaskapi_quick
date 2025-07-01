import requests
import json
import urllib.parse
import re
from urllib.parse import urlparse, parse_qs

class NewsFilterOAuthLogin:
    def __init__(self):
        self.session = requests.Session()
        self.auth_domain = "https://login.newsfilter.io"
        self.api_url = "https://api.newsfilter.io/public/actions"
        self.client_id = "SjBbF4rTwWSXp9zuFmLsAc6tu3eYXUUD"  # 從token中提取的client_id
        self.redirect_uri = "https://newsfilter.io/callback"
        
        # 設置headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://newsfilter.io/',
            'Origin': 'https://newsfilter.io'
        })
        
        self.access_token = None
        self.refresh_token = None
        self.id_token = None

    def start_auth_flow(self):
        """開始OAuth授權流程"""
        try:
            # 構建授權URL
            auth_params = {
                'response_type': 'code',
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'scope': 'openid profile email offline_access',
                'state': 'state123',  # 可以生成隨機狀態
                'audience': 'NewsFilter.io'
            }
            
            auth_url = f"{self.auth_domain}/authorize?" + urllib.parse.urlencode(auth_params)
            
            print(f"請訪問以下URL進行授權:")
            print(auth_url)
            print("\n授權後，請複製回調URL中的code參數")
            
            return auth_url
            
        except Exception as e:
            print(f"開始授權流程失敗: {str(e)}")
            return None

    def exchange_code_for_tokens(self, authorization_code):
        """使用授權碼換取tokens"""
        try:
            # 準備請求數據
            token_data = {
                "isPublic": True,
                "type": "getTokens",
                "code": authorization_code,
                "redirectUri": self.redirect_uri
            }
            
            # 設置請求headers
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': 'https://newsfilter.io',
                'Referer': 'https://newsfilter.io/'
            }
            
            print(f"正在向 {self.api_url} 發送請求...")
            print(f"請求數據: {json.dumps(token_data, indent=2)}")
            
            response = self.session.post(
                self.api_url,
                json=token_data,
                headers=headers,
                timeout=30
            )
            
            print(f"響應狀態碼: {response.status_code}")
            print(f"響應內容: {response.text}")
            
            if response.status_code == 200:
                token_response = response.json()
                
                # 保存tokens
                self.access_token = token_response.get('accessToken')
                self.refresh_token = token_response.get('refreshToken')
                self.id_token = token_response.get('idToken')
                
                print("✅ 成功獲取tokens!")
                return True, token_response
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.RequestException as e:
            return False, f"請求錯誤: {str(e)}"
        except json.JSONDecodeError as e:
            return False, f"JSON解析錯誤: {str(e)}"
        except Exception as e:
            return False, f"未知錯誤: {str(e)}"

    def login_with_username_password(self, username, password):
        """使用用戶名密碼直接登錄 (如果支持)"""
        try:
            # 嘗試直接登錄到Auth0
            login_url = f"{self.auth_domain}/usernamepassword/login"
            
            login_data = {
                "client_id": self.client_id,
                "username": username,
                "password": password,
                "connection": "Username-Password-Authentication",
                "grant_type": "password",
                "scope": "openid profile email offline_access"
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = self.session.post(
                login_url,
                json=login_data,
                headers=headers,
                timeout=30
            )
            
            print(f"直接登錄響應: {response.status_code}")
            print(f"響應內容: {response.text}")
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.text
                
        except Exception as e:
            return False, f"直接登錄失敗: {str(e)}"

    def refresh_access_token(self):
        """使用refresh token刷新access token"""
        if not self.refresh_token:
            return False, "沒有refresh token"
            
        try:
            refresh_data = {
                "isPublic": True,
                "type": "refreshToken",
                "refreshToken": self.refresh_token
            }
            
            response = self.session.post(
                self.api_url,
                json=refresh_data,
                timeout=30
            )
            
            if response.status_code == 200:
                token_response = response.json()
                self.access_token = token_response.get('accessToken')
                return True, token_response
            else:
                return False, response.text
                
        except Exception as e:
            return False, f"刷新token失敗: {str(e)}"

    def get_user_info(self):
        """獲取用戶信息"""
        if not self.access_token:
            return False, "沒有access token"
            
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json'
            }
            
            response = self.session.get(
                f"{self.auth_domain}/userinfo",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, response.text
                
        except Exception as e:
            return False, f"獲取用戶信息失敗: {str(e)}"

    def make_authenticated_request(self, url, method='GET', **kwargs):
        """使用access token發送認證請求"""
        if not self.access_token:
            return False, "沒有access token"
            
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, **kwargs)
            return True, response
        except Exception as e:
            return False, f"認證請求失敗: {str(e)}"

# 使用示例
if __name__ == "__main__":
    # 創建OAuth登錄客戶端
    oauth_client = NewsFilterOAuthLogin()
    
    print("NewsFilter OAuth登錄工具")
    print("=" * 50)
    
    choice = input("選擇登錄方式:\n1. OAuth授權流程\n2. 直接使用用戶名密碼\n3. 使用已有的授權碼\n請輸入選擇 (1/2/3): ")
    
    if choice == "1":
        # OAuth授權流程
        auth_url = oauth_client.start_auth_flow()
        if auth_url:
            auth_code = input("\n請輸入從回調URL中獲取的授權碼: ")
            success, result = oauth_client.exchange_code_for_tokens(auth_code)
            
            if success:
                print("\n✅ 登錄成功!")
                print(f"Access Token: {oauth_client.access_token[:50]}...")
                
                # 獲取用戶信息
                user_success, user_info = oauth_client.get_user_info()
                if user_success:
                    print(f"用戶信息: {json.dumps(user_info, indent=2)}")
            else:
                print(f"\n❌ 登錄失敗: {result}")
    
    elif choice == "2":
        # 直接用戶名密碼登錄
        username = input("請輸入用戶名/郵箱: ")
        password = input("請輸入密碼: ")
        
        success, result = oauth_client.login_with_username_password(username, password)
        if success:
            print("✅ 直接登錄成功!")
            print(f"結果: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ 直接登錄失敗: {result}")
    
    elif choice == "3":
        # 使用已有授權碼
        auth_code = input("請輸入授權碼: ")
        success, result = oauth_client.exchange_code_for_tokens(auth_code)
        
        if success:
            print("\n✅ 使用授權碼登錄成功!")
            print(f"Access Token: {oauth_client.access_token[:50]}...")
        else:
            print(f"\n❌ 使用授權碼登錄失敗: {result}")
    
    # 如果有access token，展示如何使用
    if oauth_client.access_token:
        print("\n" + "=" * 50)
        print("現在您可以使用access token發送認證請求")
        print("例如:")
        print("success, response = oauth_client.make_authenticated_request('https://api.newsfilter.io/some-endpoint')")