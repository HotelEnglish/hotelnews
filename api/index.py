from flask import Flask, request, jsonify
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import MeadinScraper
from news_processor import NewsProcessor
from summarizer import NewsSummarizer

app = Flask(__name__)

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
                return self.processor.format_news_report(filtered_news, is_morning)
        else:
            return self.processor.format_news_report(filtered_news, is_morning)

@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        report_type = request.args.get('type', 'morning')  # 默认为早报
        aggregator = NewsAggregator()
        
        if report_type == 'morning':
            summary = aggregator.get_news_summary(is_morning=True)
        elif report_type == 'evening':
            summary = aggregator.get_news_summary(is_morning=False)
        else:
            return jsonify({'error': 'Invalid report type'}), 400
            
        return jsonify({
            'success': True,
            'data': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>酒店新闻API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                code { background: #f4f4f4; padding: 2px 5px; }
            </style>
        </head>
        <body>
            <h1>酒店新闻API使用说明</h1>
            <p>获取早报：<code>GET /api/news?type=morning</code></p>
            <p>获取晚报：<code>GET /api/news?type=evening</code></p>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 