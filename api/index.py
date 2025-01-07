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
    <!DOCTYPE html>
    <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>酒店新闻聚合</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .news-container {
                    white-space: pre-wrap;
                    font-family: 'Microsoft YaHei', sans-serif;
                }
                .loading {
                    display: none;
                }
                .btn-group {
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container py-4">
                <h1 class="text-center mb-4">酒店新闻聚合</h1>
                
                <div class="btn-group d-flex justify-content-center" role="group">
                    <button type="button" class="btn btn-primary mx-2" onclick="getNews('morning')">获取早报</button>
                    <button type="button" class="btn btn-primary mx-2" onclick="getNews('evening')">获取晚报</button>
                    <button type="button" class="btn btn-secondary mx-2" onclick="copyNews()">复制内容</button>
                </div>

                <div class="loading text-center my-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p>正在获取新闻...</p>
                </div>

                <div class="card mt-4">
                    <div class="card-body">
                        <div id="newsContent" class="news-container"></div>
                    </div>
                </div>

                <div class="text-center mt-4">
                    <p>API 接口：</p>
                    <code>GET /api/news?type=morning</code> - 获取早报<br>
                    <code>GET /api/news?type=evening</code> - 获取晚报
                </div>
            </div>

            <script>
                async function getNews(type) {
                    const newsContent = document.getElementById('newsContent');
                    const loading = document.querySelector('.loading');
                    
                    try {
                        loading.style.display = 'block';
                        newsContent.innerHTML = '';
                        
                        const response = await fetch(`/api/news?type=${type}`);
                        const data = await response.json();
                        
                        if (data.success) {
                            newsContent.innerHTML = data.data;
                        } else {
                            newsContent.innerHTML = '获取新闻失败：' + data.error;
                        }
                    } catch (error) {
                        newsContent.innerHTML = '获取新闻失败：' + error.message;
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
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 