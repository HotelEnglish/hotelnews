from scraper import MeadinScraper
from news_processor import NewsProcessor
from summarizer import NewsSummarizer
from datetime import datetime
import pytz
import os

class NewsAggregator:
    def __init__(self):
        self.scraper = MeadinScraper()
        self.processor = NewsProcessor()
        try:
            self.summarizer = NewsSummarizer()
            self.use_ai = True
        except ValueError:
            print("Warning: OpenAI API key not found, running without AI summarization")
            self.use_ai = False

    def get_news_summary(self, is_morning=True):
        # 获取新闻
        news_items = self.scraper.get_news()
        
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

def handle_command(command):
    aggregator = NewsAggregator()
    if command == "早报":
        return aggregator.get_news_summary(is_morning=True)
    elif command == "晚报":
        return aggregator.get_news_summary(is_morning=False)
    else:
        return '请发送"早报"或"晚报"获取新闻汇总'

if __name__ == "__main__":
    while True:
        command = input("请输入命令（早报/晚报）：")
        if command in ["退出", "quit", "exit"]:
            break
        print(handle_command(command)) 