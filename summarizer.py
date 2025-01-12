from openai import OpenAI
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
import re

class NewsSummarizer:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 从环境变量获取配置
        self.base_url = os.getenv('OPENAI_BASE_URL')
        self.api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.api_key or not self.base_url:
            raise ValueError("Missing required environment variables: OPENAI_API_KEY or OPENAI_BASE_URL")
        
        # 初始化 OpenAI 客户端
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                http_client=None,
                default_headers={
                    "Content-Type": "application/json"
                }
            )
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            raise

    def summarize_news(self, news_items):
        """使用GPT-4对新闻进行摘要"""
        if not news_items:
            return "暂无相关新闻"

        # 构建提示词
        prompt = (
            "作为酒店行业资深编辑，请对以下酒店行业新闻进行专业的分析和总结：\n\n"
            "要求：\n"
            "1. 每条新闻总结2-3句话，突出重要信息\n"
            "2. 分析新闻背后的商业意义和行业影响\n"
            "3. 使用专业的酒店行业术语\n"
            "4. 新闻按重要性排序，不是按时间排序\n"
            "5. 输出格式：\n"
            "   1. 第一条新闻的详细总结...\n"
            "   2. 第二条新闻的详细总结...\n"
            "   （确保输出至少10条新闻）\n\n"
            "新闻内容：\n"
        )
        
        # 添加新闻内容
        for item in news_items:
            prompt += f"- {item['title']}\n"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "你是一位资深的酒店行业分析师和新闻编辑，擅长解读新闻背后的商业逻辑和行业趋势。"
                            "请用专业的视角分析新闻，并提供深入的见解。每条新闻的总结都应该包含具体的信息和数据。"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 获取当前时间和时段
            current_time = datetime.now(pytz.timezone('Asia/Shanghai'))
            time_str = current_time.strftime("%Y年%m月%d日")
            period = "早间" if current_time.hour < 12 else "晚间"
            
            # 添加标题
            summary = f"# {time_str}{period}新闻速报\n\n"
            
            # 处理 AI 响应，移除时间标记
            content = response.choices[0].message.content
            content = re.sub(r'\[\d{2}:\d{2}\]\s*', '', content)
            summary += content
            
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
        
        # 直接输出标题，不包含时间
        for i, item in enumerate(news_items, 1):
            summary += f"{i}. {item['title']}\n"
            
        # 添加网站链接
        summary += "\n更多资讯请访问酒店英语官网：https://www.hotelenglish.cn"
        
        return summary 