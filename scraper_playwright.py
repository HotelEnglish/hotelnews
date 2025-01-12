from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import random

class MeadinScraper:
    def __init__(self):
        self.base_url = "https://www.meadin.com/jd/"
        self.playwright = sync_playwright().start()
        self.browser = None
        self.context = None

    def _setup_browser(self):
        if not self.browser:
            self.browser = self.playwright.chromium.launch(headless=True)
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            )

    def get_news(self):
        try:
            self._setup_browser()
            page = self.context.new_page()
            
            # 访问新闻页面
            page.goto(self.base_url)
            
            # 等待新闻内容加载
            page.wait_for_selector('.news-box', timeout=30000)
            
            # 获取页面内容
            html = page.content()
            
            # 使用 BeautifulSoup 解析页面
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
                            
                            news_items.append({
                                'title': title,
                                'pub_time': pub_time
                            })
                            print(f"Added news: {title[:30]}... ({time_str})")
                            
                        except ValueError as e:
                            print(f"Error parsing time: {time_str} - {str(e)}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing news item: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"Error scraping news: {e}")
            return []
            
        finally:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

    def __del__(self):
        """确保资源被正确释放"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop() 