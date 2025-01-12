from flask import Flask, request, jsonify
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper import MeadinScraper
from traveldaily_scraper import TravelDailyScraper
from news_processor import NewsProcessor
from summarizer import NewsSummarizer

app = Flask(__name__)

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
        except ValueError:
            print("Warning: OpenAI API key not found, running without AI summarization")
            self.use_ai = False

    def get_news_summary(self):
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
        filtered_news = self.processor.filter_news(news_items)
        
        if not filtered_news:
            return "暂无相关新闻"
        
        # 如果启用了AI摘要，使用AI生成摘要
        if self.use_ai:
            try:
                return self.summarizer.summarize_news(filtered_news)
            except Exception as e:
                print(f"AI summarization failed: {e}")
                return self.processor.format_news_report(filtered_news)
        else:
            return self.processor.format_news_report(filtered_news)

@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        aggregator = NewsAggregator()
        summary = aggregator.get_news_summary()
            
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
    <!DOCTYPE html>
    <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>酒店新闻聚合</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    background-color: #f8f9fa;
                }
                .news-container {
                    white-space: pre-wrap;
                    font-family: 'Microsoft YaHei', sans-serif;
                    line-height: 1.8;
                }
                .loading {
                    display: none;
                }
                .btn-group {
                    margin: 20px 0;
                }
                .card {
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #2c3e50;
                    font-weight: bold;
                }
                .news-content {
                    font-size: 16px;
                }
                .news-content a {
                    color: #3498db;
                    text-decoration: none;
                }
                .news-content a:hover {
                    text-decoration: underline;
                }
                .divider {
                    border-top: 2px solid #eee;
                    margin: 20px 0;
                }
                .footer {
                    color: #7f8c8d;
                    font-size: 14px;
                    margin-top: 30px;
                }
            </style>
        </head>
        <body>
            <div class="container py-4">
                <h1 class="text-center mb-4">酒店新闻聚合</h1>
                
                <div class="d-flex justify-content-center mb-4">
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-primary mx-2" onclick="getNews()">
                            <i class="fas fa-sync-alt"></i> 获取最新资讯
                        </button>
                        <button type="button" class="btn btn-secondary mx-2" onclick="copyNews()">
                            <i class="fas fa-copy"></i> 复制内容
                        </button>
                    </div>
                </div>

                <div class="loading text-center my-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">正在获取新闻，请稍候...</p>
                </div>

                <div class="card">
                    <div class="card-body">
                        <div id="newsContent" class="news-container news-content"></div>
                    </div>
                </div>

                <div class="text-center mt-4 footer">
                    <div class="divider"></div>
                    <p>API 接口说明：</p>
                    <code>GET /api/news</code> - 获取最新酒店资讯
                </div>
            </div>

            <script>
                async function getNews() {
                    const newsContent = document.getElementById('newsContent');
                    const loading = document.querySelector('.loading');
                    
                    try {
                        loading.style.display = 'block';
                        newsContent.innerHTML = '';
                        
                        const response = await fetch('/api/news');
                        const data = await response.json();
                        
                        if (data.success) {
                            // 将 Markdown 格式转换为 HTML
                            let content = data.data
                                .replace(/^# (.*$)/gm, '<h1 class="mb-4">$1</h1>')
                                .replace(/^(\d+)\. (.*$)/gm, '<h3 class="mt-4">$1. $2</h3>')
                                .replace(/\[原文链接\]\((.*?)\)/g, '<a href="$1" target="_blank" class="text-primary">原文链接</a>')
                                .replace(/^-{4,}/gm, '<hr class="my-4">')
                                .replace(/\n\n/g, '<br><br>');
                            
                            newsContent.innerHTML = content;
                        } else {
                            newsContent.innerHTML = '<div class="alert alert-danger">获取新闻失败：' + data.error + '</div>';
                        }
                    } catch (error) {
                        newsContent.innerHTML = '<div class="alert alert-danger">获取新闻失败：' + error.message + '</div>';
                    } finally {
                        loading.style.display = 'none';
                    }
                }

                function copyNews() {
                    const newsContent = document.getElementById('newsContent');
                    const text = newsContent.innerText;
                    
                    if (!text) {
                        alert('没有可复制的内容');
                        return;
                    }
                    
                    navigator.clipboard.writeText(text).then(() => {
                        alert('内容已复制到剪贴板');
                    }).catch(err => {
                        alert('复制失败：' + err);
                    });
                }
            </script>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
