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
            # 添加1秒延迟以避免API速率限制
            time.sleep(1)
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

class MeadinScraper:
    def __init__(self):
        self.base_url = "https://www.meadin.com/jd/"
        # 初始化 Chrome WebDriver
        try:
            chrome_path = r"D:\电脑工具\Chrome\App\chrome.exe"  # 替换为你的 Chrome 路径
            print(f"Chrome browser found at: {chrome_path}")
            
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # 无界面模式
            options.add_argument('--disable-gpu')
            options.binary_location = chrome_path
            
            # 使用 webdriver_manager 自动管理 ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            print("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Chrome WebDriver: {e}")
            raise

    def get_news(self):
        try:
            # 访问新闻页面
            self.driver.get(self.base_url)
            print(f"Accessed URL: {self.base_url}")
            
            # 等待新闻容器加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "news-box"))
            )
            
            # 获取页面内容
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            news_items = []
            
            # 查找所有新闻容器
            news_containers = soup.find_all('div', class_='news-box')
            print(f"Found {len(news_containers)} news containers")
            
            for container in news_containers:
                try:
                    # 获取标题
                    title_elem = container.find('a', attrs={'data-cut': 'newtitle'})
                    # 获取时间
                    time_elem = container.find('span', class_='rf-news')
                    
                    if title_elem and time_elem:
                        title = title_elem.text.strip()
                        time_str = time_elem.text.strip()
                        
                        try:
                            # 如果时间字符串只包含日期，添加默认时间
                            if len(time_str) == 10:  # 格式: YYYY-MM-DD
                                time_str += ' 00:00:00'
                            
                            # 解析时间
                            pub_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                            # 设置为中国时区
                            china_tz = pytz.timezone('Asia/Shanghai')
                            pub_time = china_tz.localize(pub_time)
                            
                            # 打印调试信息
                            print(f"Processing news: {title[:30]}... (Time: {time_str})")
                            
                            # 获取新闻内容
                            content_elem = container.find('div', class_='article')
                            content = content_elem.text.strip() if content_elem else ""
                            
                            # 使用AI生成摘要
                            summarizer = AISummarizer()
                            summary = summarizer.generate_summary(content)
                            
                            # 获取新闻链接
                            url = title_elem['href']
                            if not url.startswith('http'):
                                url = f"https://www.meadin.com{url}"
                            
                            news_items.append({
                                'title': title,
                                'pub_time': pub_time,
                                'summary': summary,
                                'url': url
                            })
                            print(f"Added news item: {title}")
                            
                        except ValueError as e:
                            print(f"Error parsing time: {time_str} - {str(e)}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing news item: {e}")
                    continue
            
            print(f"Successfully collected {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            print(f"Error scraping news: {e}")
            return []
            
        finally:
            # 添加随机延迟
            delay = random.uniform(1, 3)
            time.sleep(delay)

    def __del__(self):
        """确保 WebDriver 被正确关闭"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
                print("Chrome WebDriver closed successfully")
        except Exception as e:
            print(f"Error closing Chrome WebDriver: {e}")
