from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import random
import os

class MeadinScraper:
    def __init__(self):
        self.base_url = "https://www.meadin.com/jd/"
        # 配置Chrome选项
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # 无头模式
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')

        # 设置Chrome浏览器路径
        chrome_path = r"D:\电脑工具\Chrome\App\chrome.exe"
        if os.path.exists(chrome_path):
            self.chrome_options.binary_location = chrome_path
            print(f"Chrome browser found at: {chrome_path}")
        else:
            print(f"Warning: Chrome browser not found at {chrome_path}")

        # 设置ChromeDriver
        try:
            self.service = Service(ChromeDriverManager().install())
            print("ChromeDriver installed successfully")
        except Exception as e:
            print(f"Error setting up ChromeDriver: {e}")
            self.service = None

    def get_news(self):
        if not self.service:
            print("Error: ChromeDriver service not initialized")
            return []

        driver = None
        try:
            # 创建浏览器实例
            driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            print("Chrome WebDriver initialized successfully")
            
            # 访问页面
            driver.get(self.base_url)
            print(f"Accessed URL: {self.base_url}")
            
            # 等待新闻内容加载
            wait = WebDriverWait(driver, 10)
            news_containers = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "news-box"))
            )
            print(f"Found {len(news_containers)} news containers")
            
            news_items = []
            
            # 解析新闻内容
            for container in news_containers:
                try:
                    # 获取标题
                    title_elem = container.find_element(By.CSS_SELECTOR, 'a[data-cut="newtitle"]')
                    # 获取时间
                    time_elem = container.find_element(By.CLASS_NAME, 'rf-news')
                    
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
                            
                            news_items.append({
                                'title': title,
                                'pub_time': pub_time
                            })
                            print(f"Added news item: {title[:30]}...")
                        except ValueError as e:
                            print(f"Error parsing time: {time_str} - {str(e)}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing news item: {e}")
                    continue
            
            if not news_items:
                print("Warning: No news items found")
                # 打印一个示例新闻容器的HTML
                if news_containers:
                    print("Sample news container HTML:")
                    print(news_containers[0].get_attribute('outerHTML'))
            else:
                print(f"Successfully collected {len(news_items)} news items")
            
            return news_items
            
        except Exception as e:
            print(f"Error scraping news: {e}")
            if driver:
                print("Page source:", driver.page_source[:500])
            return []
            
        finally:
            if driver:
                try:
                    driver.quit()
                    print("Chrome WebDriver closed successfully")
                except Exception as e:
                    print(f"Error closing WebDriver: {e}")

    def _add_delay(self):
        """添加随机延迟以避免被封禁"""
        delay = random.uniform(1, 3)
        time.sleep(delay) 
