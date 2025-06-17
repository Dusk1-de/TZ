import os
from datetime import datetime
from flask import Flask, render_template, send_from_directory, request
import markdown
app = Flask(__name__)
# 路径配置
NEWS_DIR = "news"
STATIC_DIR = "static"
# 确保目录存在
os.makedirs(NEWS_DIR, exist_ok=True)
def read_markdown_file(filename):
    """读取 Markdown 文件并转为 HTML"""
    with open(os.path.join(NEWS_DIR, filename), "r", encoding="utf-8") as f:
        content = f.read()
    return markdown.markdown(content, extensions=["fenced_code", "tables"])
@app.route("/")
def home():
    def extract_date(filename):
        # 从文件名中提取日期
        try:
            date_str = filename.split('AI新闻')[0].strip()
            return datetime.strptime(date_str, '%Y年%m月%d日')
        except:
            # 如果解析失败，返回一个很早的日期
            return datetime(1900, 1, 1)
    news_files = [f for f in os.listdir(NEWS_DIR) if f.endswith(".md")]
    # 按日期排序
    news_files.sort(key=extract_date, reverse=True)
    news_list = []
    for filename in news_files:
        # 保留原始大小写
        title = filename.replace(".md", "").replace("-", " ")
        news_list.append({"filename": filename, "title": title})
    return render_template("index.html", news_list=news_list)
@app.route("/news/<filename>")
def news_detail(filename):
    """新闻详情页"""
    html_content = read_markdown_file(filename)
    title = filename.replace(".md", "").replace("-", " ")
    return render_template("news_detail.html", content=html_content, title=title)
@app.route("/daily")
def daily_news():
    """查看所有新闻汇总"""
    def extract_date(filename):
        # 从文件名中提取日期
        try:
            date_str = filename.split('AI新闻')[0].strip()
            return datetime.strptime(date_str, '%Y年%m月%d日')
        except:
            # 如果解析失败，返回一个很早的日期
            return datetime(1900, 1, 1)
    today_display = datetime.now().strftime("%Y年%m月%d日") # For display purposes
    news_files = [f for f in os.listdir(NEWS_DIR) if f.endswith(".md")]
    # 按日期排序
    news_files.sort(key=extract_date, reverse=True)
    all_html = []
    for filename in news_files:
        html_content = read_markdown_file(filename)
        all_html.append(html_content)
    # 生成每日汇总页面
    return render_template("daily_summary.html", today=today_display, news_content=all_html)
@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory(STATIC_DIR, path)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)