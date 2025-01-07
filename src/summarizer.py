from openai import OpenAI
from datetime import datetime
import pytz
import os

class NewsSummarizer:
    def __init__(self):
        # 设置 API 基础 URL 和密钥
        self.base_url = "https://api.xi-ai.cn/v1"
        self.api_key = "sk-ELEVTsylkeIO7mJU920a7d17A29541E88a5903BbF1D7118b"
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "Content-Type": "application/json"
            }
        )

    def summarize_news(self, news_items):
        """使用GPT-4对新闻进行摘要"""
        if not news_items:
            return "暂无相关新闻"

        # 构建提示词
        prompt = "你是一个专业的新闻编辑，请对以下酒店行业新闻进行简要总结。要求：\n"
        prompt += "1. 每条新闻用一句话概括主要内容\n"
        prompt += "2. 使用简洁明了的语言\n"
        prompt += "3. 保持新闻的专业性\n"
        prompt += "4. 确保输出10条新闻摘要\n\n"
        prompt += "新闻内容：\n"
        
        for item in news_items:
            time_str = item['pub_time'].strftime("%H:%M")
            prompt += f"[{time_str}] {item['title']}\n"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个专业的酒店行业新闻编辑，善于提炼新闻重点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # 获取当前时间和时段
            current_time = datetime.now(pytz.timezone('Asia/Shanghai'))
            time_str = current_time.strftime("%Y年%m月%d日")
            period = "早间" if current_time.hour < 12 else "晚间"
            
            # 添加标题和内容
            summary = f"# {time_str}{period}新闻速报\n\n"
            summary += response.choices[0].message.content
            
            # 添加网站链接
            summary += "\n\n更多资讯请访问酒店英语官网：https://www.hotelenglish.cn"
            
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return self._format_fallback_report(news_items)
    
    def _format_fallback_report(self, news_items):
        """当AI摘要失败时的后备格式化方法"""
        current_time = datetime.now(pytz.timezone('Asia/Shanghai'))
        time_str = current_time.strftime("%Y年%m月%d日")
        period = "早间" if current_time.hour < 12 else "晚间"
        
        summary = f"# {time_str}{period}新闻速报\n\n"
        for i, item in enumerate(news_items, 1):
            pub_time = item['pub_time'].strftime("%H:%M")
            summary += f"{i}. [{pub_time}] {item['title']}\n"
            
        # 添加网站链接
        summary += "\n更多资讯请访问酒店英语官网：https://www.hotelenglish.cn"
        
        return summary 