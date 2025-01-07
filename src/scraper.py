import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import time
import random
import json

class MeadinScraper:
    def __init__(self):
        self.base_url = "https://www.meadin.com/jd/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.meadin.com/'
        }

    def get_news(self):
        try:
            session = requests.Session()
            
            # 首先访问主页获取必要的 cookies
            session.get('https://www.meadin.com/', headers=self.headers)
            
            # 添加随机延迟
            self._add_delay()
            
            # 获取新闻页面
            response = session.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            
            # 使用 BeautifulSoup 解析页面
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = []
            
            # 查找所有新闻容器
            news_containers = soup.find_all('div', class_='news-box')
            
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
                            
                        except ValueError as e:
                            print(f"Error parsing time: {time_str} - {str(e)}")
                            continue
                            
                except Exception as e:
                    print(f"Error processing news item: {e}")
                    continue
            
            if not news_items:
                print("Warning: No news items found")
                print("Response status:", response.status_code)
                print("Response content preview:", response.text[:500])
            
            return news_items
            
        except Exception as e:
            print(f"Error scraping news: {e}")
            return []

    def _add_delay(self):
        """添加随机延迟以避免被封禁"""
        delay = random.uniform(1, 3)
        time.sleep(delay) 