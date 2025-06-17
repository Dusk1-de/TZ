import requests
import json
from datetime import datetime, timedelta
import re
from typing import List, Dict
import os
import opencc
import schedule
import time
class AINewsFetcher:
    def __init__(self, api_key: str):
        """
        初始化AI新闻获取器
        Args:
            api_key: NewsAPI的API密钥
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.ai_keywords = [
            "人工智能", "AI", "机器学习", "深度学习", "大模型", "生成式AI",
            "ChatGPT", "GPT", "Claude", "Gemini", "OpenAI", "Deepseek",
            "Anthropic", "神经网络", "算法", "自然语言处理", "计算机视觉",
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "transformer", "large language model", "LLM"
        ]
    def fetch_ai_news(self, language='zh', page_size=200, days_back=7) -> List[Dict]:
        """
        获取AI相关新闻
        Args:
            language: 新闻语言 ('zh' 简体中文, 'en' 英文)
            page_size: 每页新闻数量
            days_back: 向前搜索天数
        Returns:
            新闻列表
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        date_from = start_date.strftime("%Y-%m-%d")
        date_to = end_date.strftime("%Y-%m-%d")
        print(f"搜索日期范围: {date_from} 到 {date_to}")
        if language == 'zh':
            query = "人工智能 OR AI OR 机器学习 OR 大模型 OR ChatGPT OR OpenAI OR 生成式AI"
        elif language == 'en':
            query = "artificial intelligence OR AI OR machine learning OR ChatGPT OR OpenAI OR generative AI"
        else:
            query = "人工智能 OR AI OR 机器学习 OR 大模型 OR ChatGPT OR OpenAI OR 生成式AI"
            language = 'zh'
        url = f"{self.base_url}/everything"
        params = {
            'q': query,
            'apiKey': self.api_key,
            'from': date_from,
            'to': date_to,
            'language': language,
            'sortBy': 'publishedAt',
            'pageSize': min(page_size, 200)
        }
        print(f"正在请求API: {url}")
        print(f"请求参数: {params}")
        try:
            response = requests.get(url, params=params, timeout=30)
            print(f"响应状态码: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            print(f"API响应状态: {data.get('status')}")
            print(f"总结果数: {data.get('totalResults', 0)}")
            if data['status'] == 'ok':
                articles = data['articles']
                print(f"成功获取 {len(articles)} 条新闻")
                return articles
            else:
                print(f"API错误: {data.get('message', '未知错误')}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return []
        except Exception as e:
            print(f"未知错误: {e}")
            return []
    def fetch_tech_news(self, language='zh', page_size=200, days_back=7) -> List[Dict]:
        """
        获取科技新闻并筛选AI相关内容
        """
        print(f"尝试获取科技新闻 (最近{days_back}天)")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        date_from = start_date.strftime("%Y-%m-%d")
        date_to = end_date.strftime("%Y-%m-%d")
        if language == 'zh':
            query = "科技 OR 技术 OR 互联网 OR 数字化 OR 创新"
        else:
            query = "technology OR tech OR innovation OR digital"
        url = f"{self.base_url}/everything"
        params = {
            'q': query,
            'apiKey': self.api_key,
            'from': date_from,
            'to': date_to,
            'language': language,
            'sortBy': 'publishedAt',
            'pageSize': min(page_size, 100)
        }
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            if data['status'] == 'ok':
                articles = data['articles']
                print(f"获取到 {len(articles)} 条科技新闻")
                ai_articles = self.filter_ai_articles(articles)
                print(f"筛选出 {len(ai_articles)} 条AI相关新闻")
                return ai_articles
            else:
                print(f"获取科技新闻失败: {data.get('message', '未知错误')}")
                return []
        except Exception as e:
            print(f"获取科技新闻错误: {e}")
            return []
    def filter_ai_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        从文章列表中筛选AI相关文章
        """
        ai_articles = []
        ai_keywords = [
            'ai', 'artificial intelligence', '人工智能', 'machine learning', '机器学习',
            'chatgpt', 'gpt', 'claude', 'gemini', 'openai', 'deepseek', 'anthropic',
            '大模型', 'llm', 'neural network', '神经网络', 'deep learning', '深度学习',
            'generative ai', '生成式ai', 'transformer', '算法', 'algorithm',
            '智能', '自动化', 'automation', '智能化', '数字化转型'
        ]
        for article in articles:
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            content = article.get('content', '').lower()
            text_to_check = f"{title} {description} {content}"
            if any(keyword in text_to_check for keyword in ai_keywords):
                ai_articles.append(article)
        return ai_articles
    def calculate_importance_score(self, article: Dict) -> float:
        """
        计算新闻重要程度得分
        Args:
            article: 新闻文章字典
        Returns:
            重要程度得分 (0-100)
        """
        score = 0
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = article.get('content', '').lower()
        high_impact_keywords = {
            'breakthrough': 15, 'revolutionary': 15, '突破': 15, '革命性': 15,
            'AI': 30, '颠覆': 15, '领先': 12, '超越': 12, '震撼': 15,
            'deepmind': 15, 'openai': 15, 'anthropic': 12, 'google': 10,
            '投资': 10, '融资': 10, '估值': 8, '百亿': 20, '千亿': 25,
            'billion': 15, 'million': 8, '亿元': 12, '美元': 15,
            '发布': 8, '推出': 8, '上线': 6, '升级': 6
        }
        medium_impact_keywords = {
            'launch': 6, 'release': 6, 'update': 4, 'improve': 4,
            '改进': 4, '优化': 4, '提升': 5, '增强': 5,
            'performance': 6, '性能': 6, '准确率': 8, '效率': 6,
            '模型': 5, '算法': 5, '技术': 3, '创新': 6
        }
        text_to_check = f"{title} {description} {content}"
        for keyword, weight in high_impact_keywords.items():
            count = text_to_check.count(keyword)
            score += weight * count
        for keyword, weight in medium_impact_keywords.items():
            count = text_to_check.count(keyword)
            score += weight * count
        source = article.get('source', {}).get('name', '').lower()
        high_quality_sources = ['36kr', '今日头条', 'IT之家', '新智元', '量子位',
                                '新浪科技', '新浪新闻', '搜狐']
        if any(domain in source for domain in high_quality_sources):
            score *= 5
        published_at = article.get('publishedAt', '')
        if published_at:
            try:
                pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                hours_ago = (datetime.now() - pub_time.replace(tzinfo=None)).total_seconds() / 3600
                if hours_ago < 1:
                    score *= 5
                elif hours_ago < 24:
                    score *= 1.2
                elif hours_ago < 72:
                    score *= 1.1
            except:
                pass
        return min(score, 100)
    def rank_news(self, articles: List[Dict]) -> List[Dict]:
        """
        对新闻进行排序
        """
        for article in articles:
            article['importance_score'] = self.calculate_importance_score(article)
        return sorted(articles, key=lambda x: x['importance_score'], reverse=True)
    def clean_text(self, text: str) -> str:
        """
        清理文本，去除多余字符，并将繁体转换为简体
        """
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\w\s\u4e00-\u9fff\.,，。！？：；""''（）【】％%]', '', text)
        converter = opencc.OpenCC('t2s.json')
        text = converter.convert(text)
        return text
    def summarize_text(self, text: str, max_length: int = 100) -> str:
        """
        提炼文本摘要，确保不超过指定长度。
        """
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        end_index = -1
        for punc in ['。', '！', '？', '.', '!', '?']:
            idx = text.rfind(punc, 0, max_length)
            if idx != -1:
                end_index = max(end_index, idx)
        if end_index != -1:
            summary = text[:end_index + 1]
        else:
            summary = text[:max_length]
        if len(summary) > max_length:
            summary = summary[:max_length]
        return summary
    def format_to_markdown(self, articles: List[Dict], top_n: int = 10) -> str:
        """
        将新闻格式化为Markdown格式，与示例文档 "2025年6月7日AI新闻.md" 一致。
        优先输出简体中文内容。
        """
        markdown_content = ""
        count = 0
        for article in articles:
            if count >= top_n:
                break
            title = self.clean_text(article.get('title', ''))
            url = article.get('url', '')
            description = self.clean_text(article.get('description', ''))
            content = self.clean_text(article.get('content', ''))
            if self.is_english_text(title):
                title = f"{title} [英文]"
            detailed_description = description
            if not detailed_description or len(detailed_description) < 20:
                if content and len(content) > 20:
                    detailed_description = content
            if not detailed_description:
                detailed_description = "暂无详细描述。"
            news_summary = self.summarize_text(detailed_description, 200)
            introduction = news_summary
            display_text = introduction  # 使用生成的摘要
            markdown_content += f"## {count + 1}. [{title}]({url})\n"
            markdown_content += f"   {display_text}\n\n"
            count += 1
        if not markdown_content:
            markdown_content = "# 今日暂无相关AI新闻\n"
            markdown_content += "请稍后再试。"
        return markdown_content
    def is_english_text(self, text: str) -> bool:
        """
        判断文本是否主要为英文
        """
        if not text:
            return False
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        return english_chars > chinese_chars
    def translate_title(self, title: str) -> str:
        """
        简单的英文标题翻译（关键词替换）
        """
        translations = {
            'AI': 'AI',
            'Artificial Intelligence': '人工智能',
            'Machine Learning': '机器学习',
            'Deep Learning': '深度学习',
            'ChatGPT': 'ChatGPT',
            'OpenAI': 'OpenAI',
            'Google': '谷歌',
            'Microsoft': '微软',
            'breakthrough': '突破',
            'announces': '宣布',
            'launches': '推出',
            'releases': '发布',
            'investment': '投资',
            'funding': '融资',
            'billion': '十亿',
            'million': '百万'
        }
        translated = title
        for en, zh in translations.items():
            translated = re.sub(en, zh, translated, flags=re.IGNORECASE)
        return translated
    def save_to_file(self, content: str, filename: str = None) -> str:
        """
        保存内容到文件
        """
        if filename is None:
            today = datetime.now().strftime("%Y年%m月%d日")
            filename = f"{today}AI新闻.md"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"新闻已保存至: {filename}")
            return filename
        except Exception as e:
            print(f"保存文件失败: {e}")
            return ""
    def run(self, top_n: int = 10, language: str = 'zh') -> str:
        """
        执行完整的新闻获取和处理流程。
        优先获取简体中文新闻，并确保输出内容为简体中文。
        Args:
            top_n: 输出前N条新闻
            language: 优先获取的新闻语言 ('zh' 代表简体中文)
        Returns:
            保存的文件路径
        """
        print("正在获取AI相关新闻...")
        print(f"开始获取AI新闻，优先语言: {language}")
        articles = self.fetch_ai_news(language=language, page_size=100, days_back=3)
        if language == 'zh' and len(articles) < top_n * 2:
            print(f"简体中文新闻数量 ({len(articles)}) 不足，尝试补充英文新闻...")
            en_articles = self.fetch_ai_news(language='en', page_size=50, days_back=3)
            articles.extend(en_articles)
            print(f"补充后新闻总数: {len(articles)}")
        if len(articles) < top_n * 3:
            print(f"新闻数量 ({len(articles)}) 仍较少，尝试从科技新闻中筛选...")
            if language == 'zh':
                tech_articles_zh = self.fetch_tech_news(language='zh', page_size=50, days_back=3)
                articles.extend(tech_articles_zh)
            tech_articles_en = self.fetch_tech_news(language='en', page_size=50, days_back=3)
            articles.extend(tech_articles_en)
            print(f"从科技新闻补充后总数: {len(articles)}")
        seen_urls = set()
        unique_articles = []
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls and article.get('title'):
                seen_urls.add(url)
                unique_articles.append(article)
        if not unique_articles:
            print("未获取到新闻数据")
            return ""
        print(f"去重后获取到 {len(unique_articles)} 条新闻，正在排序...")
        ranked_articles = self.rank_news(unique_articles)
        print(f"正在格式化前 {top_n} 条新闻...")
        markdown_content = self.format_to_markdown(ranked_articles, top_n)
        filename = self.save_to_file(markdown_content)
        print("处理完成！")
        print(f"生成了 {top_n} 条AI新闻，详细程度已优化")
        return filename
def main():
    """
    主函数
    """
    API_KEY = "50dcfc12c17544049c685687c0d62883"
    print("正在测试API密钥...")
    test_url = "https://newsapi.org/v2/top-headlines"
    test_params = {
        'apiKey': API_KEY,
        'country': 'us',
        'pageSize': 1
    }
    try:
        test_response = requests.get(test_url, params=test_params, timeout=10)
        if test_response.status_code == 401:
            print("❌ API密钥无效，请检查密钥是否正确")
            return
        elif test_response.status_code == 429:
            print("❌ API调用次数已达上限")
            return
        elif test_response.status_code != 200:
            print(f"❌ API测试失败，状态码: {test_response.status_code}")
            return
        else:
            print("✅ API密钥验证成功")
    except Exception as e:
        print(f"❌ 网络连接失败: {e}")
        return
    fetcher = AINewsFetcher(API_KEY)
    def update_news():
        result_file = fetcher.run(top_n=10, language='zh')
        if result_file:
            print(f"\n✅ 成功生成AI新闻文档: {result_file}")
            print("新闻内容已优先获取简体中文，输出格式已参考示例文档。")
        else:
            print("\n❌ 新闻获取或生成失败，请检查API密钥或网络连接。")
    schedule.every().day.at("09:00").do(update_news)
    update_news()
    while True:
        schedule.run_pending()
        time.sleep(1)
if __name__ == "__main__":
    main()