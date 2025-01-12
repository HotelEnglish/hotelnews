from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import random
from openai import OpenAI
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class AISummarizer:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )

    def generate_summary(self, content):
        try:
            time.sleep(2)  # 增加延迟以避免 API 限制
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻摘要生成器，请用50字以内概括新闻内容"},
                    {"role": "user", "content": f"请为以下新闻生成摘要：\n{content}"}
                ],
                max_tokens=60
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "暂无摘要"

class TravelDailyScraper:
    def __init__(self):
        self.base_url = "https://www.traveldaily.cn"
        try:
            chrome_path = r"D:\电脑工具\Chrome\App\chrome.exe"
            print(f"TravelDaily: Chrome browser found at: {chrome_path}")
            
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
            options.binary_location = chrome_path
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("TravelDaily: Chrome WebDriver initialized successfully")
            
        except Exception as e:
            print(f"TravelDaily: Error initializing Chrome WebDriver: {e}")
            raise

    def get_news(self):
        try:
            # 预定义一些最新的文章ID
            # 这些ID可以通过观察网站最新文章来确定
            article_ids = [
                "185571", "185570", "185569", "185568", "185567",
                "185566", "185565", "185564", "185563", "185562"
            ]
            
            news_items = []
            for article_id in article_ids:
                try:
                    article_url = f"{self.base_url}/article/{article_id}"
                    print(f"TravelDaily: Processing article: {article_url}")
                    
                    # 访问文章页面
                    self.driver.get(article_url)
                    
                    # 等待文章内容加载
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "articleTitle"))
                    )
                    
                    # 获取标题和内容
                    title = self.driver.find_element(By.CLASS_NAME, "articleTitle").text.strip()
                    content = self.driver.find_element(By.CLASS_NAME, "articleContent").text.strip()
                    
                    # 检查是否是酒店相关新闻
                    if not any(keyword in title.lower() or keyword in content.lower() 
                             for keyword in ['酒店', '度假', '旅游', '民宿', 'hotel']):
                        continue
                    
                    # 获取发布时间
                    try:
                        time_str = self.driver.find_element(By.CLASS_NAME, "articleTime").text.strip()
                        if len(time_str) == 10:  # 格式: YYYY-MM-DD
                            time_str += ' 00:00:00'
                    except:
                        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 解析时间
                    pub_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    china_tz = pytz.timezone('Asia/Shanghai')
                    pub_time = china_tz.localize(pub_time)
                    
                    # 生成摘要
                    summarizer = AISummarizer()
                    summary = summarizer.generate_summary(content)
                    
                    news_items.append({
                        'title': title,
                        'pub_time': pub_time,
                        'summary': summary,
                        'url': article_url
                    })
                    print(f"TravelDaily: Added news: {title[:30]}...")
                    
                    # 短暂延迟
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"TravelDaily: Error processing article {article_id}: {e}")
                    continue
            
            print(f"TravelDaily: Successfully collected {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            print(f"TravelDaily: Error scraping news: {e}")
            return []
            
        finally:
            time.sleep(1)

    def __del__(self):
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
                print("TravelDaily: Chrome WebDriver closed successfully")
        except Exception as e:
            print(f"TravelDaily: Error closing Chrome WebDriver: {e}")
