from datetime import datetime, timedelta
import pytz

class NewsProcessor:
    @staticmethod
    def filter_news(news_items, is_morning=True):
        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        today_noon = now.replace(hour=12, minute=0, second=0, microsecond=0)
        
        # 获取今天的日期（不包含时间）
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # 获取昨天的日期
        yesterday = today - timedelta(days=1)
        
        filtered_news = []
        for news in news_items:
            # 检查是否是今天或昨天的新闻
            news_date = news['pub_time'].replace(hour=0, minute=0, second=0, microsecond=0)
            if news_date >= yesterday:  # 包含昨天和今天的新闻
                if is_morning and news['pub_time'].hour < 12:
                    filtered_news.append(news)
                elif not is_morning and news['pub_time'].hour >= 12:
                    filtered_news.append(news)
                    
        # 按时间倒序排序并取前10条
        filtered_news.sort(key=lambda x: x['pub_time'], reverse=True)
        return filtered_news[:10]

    @staticmethod
    def format_news_report(news_items, is_morning=True):
        """格式化新闻报告"""
        if not news_items:
            return "暂无相关新闻"

        current_time = datetime.now(pytz.timezone('Asia/Shanghai'))
        time_str = current_time.strftime("%Y年%m月%d日")
        period = "早间" if is_morning else "晚间"
        
        report = f"# {time_str}{period}新闻速报\n\n"
        
        for i, news in enumerate(news_items, 1):
            pub_time = news['pub_time'].strftime("%H:%M")
            report += f"{i}. [{pub_time}] {news['title']}\n"
        
        # 添加网站链接
        report += "\n更多资讯请访问酒店英语官网：https://www.hotelenglish.cn"
        
        return report 