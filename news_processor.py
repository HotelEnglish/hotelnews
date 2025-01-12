from datetime import datetime, timedelta
import pytz

class NewsProcessor:
    @staticmethod
    def filter_news(news_items, is_morning=True):
        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        
        # 获取最近三天的新闻
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        three_days_ago = today - timedelta(days=3)
        
        filtered_news = []
        for news in news_items:
            # 检查是否是最近三天的新闻
            news_date = news['pub_time'].replace(hour=0, minute=0, second=0, microsecond=0)
            if news_date >= three_days_ago:
                filtered_news.append(news)
                    
        # 按时间倒序排序并取前10条
        filtered_news.sort(key=lambda x: x['pub_time'], reverse=True)
        return filtered_news[:10]

    @staticmethod
    def format_news_report(news_items, is_morning=True):
        """格式化新闻报告为markdown格式"""
        if not news_items:
            return "暂无相关新闻"

        # 获取当前时间
        current_time = datetime.now(pytz.timezone('Asia/Shanghai'))
        time_str = current_time.strftime("%Y年%m月%d日")
        
        # 构建报告
        report = f"# {time_str}酒店新闻速报\n\n"
        
        # 添加每条新闻
        for i, news in enumerate(news_items, 1):
            report += f"{i}. {news['title']}\n"
            if 'summary' in news:
                report += f"{news['summary']}\n"
            report += f"[原文链接]({news['url']})\n\n"
        
        # 添加分隔线和页脚
        report += "------\n\n"
        report += "【酒店英语】早报，更多资讯请访问：https://www.hotelenglish.cn/"
        
        return report
