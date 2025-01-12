from scraper import MeadinScraper
from traveldaily_scraper import TravelDailyScraper
from news_processor import NewsProcessor
from summarizer import NewsSummarizer
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

# 确保在程序开始时就加载环境变量
load_dotenv()

class NewsAggregator:
    def __init__(self):
        self.scrapers = [
            MeadinScraper(),
            TravelDailyScraper()
        ]
        self.processor = NewsProcessor()
        try:
            self.summarizer = NewsSummarizer()
            self.use_ai = True
        except Exception as e:
            print(f"Error initializing AI summarizer: {e}")
            self.use_ai = False

    def get_news_summary(self, is_morning=True):
        # 从多个来源获取新闻
        news_items = []
        for scraper in self.scrapers:
            try:
                items = scraper.get_news()
                if items:
                    news_items.extend(items)
            except Exception as e:
                print(f"Error getting news from {scraper.__class__.__name__}: {e}")
        
        # 过滤新闻
        filtered_news = self.processor.filter_news(news_items, is_morning)
        
        if not filtered_news:
            return "暂无相关新闻"
        
        # 如果启用了AI摘要，使用AI生成摘要
        if self.use_ai:
            try:
                return self.summarizer.summarize_news(filtered_news)
            except Exception as e:
                print(f"AI summarization failed: {e}")
                # 如果AI摘要失败，使用常规格式化
                return self.processor.format_news_report(filtered_news, is_morning)
        else:
            # 使用常规格式化
            return self.processor.format_news_report(filtered_news, is_morning)

def handle_command():
    aggregator = NewsAggregator()
    
    # 获取所有新闻
    news_items = []
    
    # 从迈点网获取新闻
    try:
        meadin_scraper = MeadinScraper()
        meadin_news = meadin_scraper.get_news()
        if meadin_news:
            news_items.extend(meadin_news)
    except Exception as e:
        print(f"Error getting news from Meadin: {e}")
    
    # 从环球旅讯获取新闻
    try:
        traveldaily_scraper = TravelDailyScraper()
        traveldaily_news = traveldaily_scraper.get_news()
        if traveldaily_news:
            news_items.extend(traveldaily_news)
    except Exception as e:
        print(f"Error getting news from TravelDaily: {e}")
    
    # 过滤和格式化新闻
    processor = NewsProcessor()
    filtered_news = processor.filter_news(news_items)
    return processor.format_news_report(filtered_news)

if __name__ == "__main__":
    print(handle_command())
