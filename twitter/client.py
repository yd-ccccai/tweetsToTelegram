import requests
from bs4 import BeautifulSoup
import re
import random
import time
import json
import urllib3
import os
import shutil
from urllib.parse import urlparse
from config import Config
import cloudscraper  # 添加 cloudscraper 库

# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TwitterClient:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Referer": "https://nitter.net/",  # 添加 Referer
            "Origin": "https://nitter.net"     # 添加 Origin
        }
        self.delay_range = (2, 5)
        self.debug = Config.DEBUG_CRAWLER
        self.scraper = cloudscraper.create_scraper()  # 初始化 cloudscraper
        # 默认的nitter实例列表（作为备份）
        self.default_instances = [
            "https://nitter.net",
            "https://nitter.privacydev.net",
            "https://nitter.1d4.us",
            "https://nitter.moomoo.me",
            "https://nitter.weiler.rocks"
        ]
        
        # 创建并清理temp目录
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
        self.clean_temp_directory()

    def clean_temp_directory(self):
        """清理temp目录"""
        try:
            if os.path.exists(self.temp_dir):
                self.debug_print("清理temp目录...")
                shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir, exist_ok=True)
            self.debug_print("✅ temp目录已准备就绪")
        except Exception as e:
            self.debug_print(f"❌ 清理temp目录时出错: {str(e)}")

    def save_html_to_temp(self, url: str, html_content: str):
        """保存HTML内容到temp目录"""
        try:
            # 从URL生成文件名
            parsed_url = urlparse(url)
            filename = f"{parsed_url.netloc}{parsed_url.path}".replace('/', '_') + '.html'
            filepath = os.path.join(self.temp_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.debug_print(f"✅ HTML已保存到: {filepath}")
        except Exception as e:
            self.debug_print(f"❌ 保存HTML时出错: {str(e)}")

    def debug_print(self, message):
        """调试信息打印"""
        if self.debug:
            print(f"[Crawler Debug] {message}")

    def get_nitter_instances(self):
        """获取最新的nitter实例列表"""
        try:
            # 尝试从多个来源获取实例列表
            sources = [
                "https://raw.githubusercontent.com/zedeus/nitter/master/nitter.json",
                "https://raw.githubusercontent.com/zedeus/nitter/master/instances.json",
                "https://github.com/zedeus/nitter/wiki/Instances"
            ]
            
            instances = set()
            
            for source in sources:
                try:
                    self.debug_print(f"尝试从 {source} 获取nitter实例列表...")
                    response = requests.get(source, headers=self.headers, timeout=10, verify=False)
                    
                    if response.status_code == 200:
                        if source.endswith('.json'):
                            # 处理JSON格式的源
                            data = response.json()
                            if isinstance(data, dict):
                                instances.update([f"https://{instance}" for instance in data.keys()])
                            elif isinstance(data, list):
                                instances.update([f"https://{instance}" for instance in data])
                        else:
                            # 处理GitHub wiki页面
                            soup = BeautifulSoup(response.text, 'html.parser')
                            # 获取所有链接，过滤非https://开头的链接，并排除包含github和ssllabs的地址
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                if (href.startswith('https://') and
                                    'github' not in href and
                                    'ssllabs' not in href):
                                    instances.add(href.rstrip('/'))
                                    
                        self.debug_print(f"从 {source} 成功获取实例列表")
                        break
                        
                except Exception as e:
                    self.debug_print(f"从 {source} 获取实例列表失败: {str(e)}")
                    continue
            
            # 如果没有获取到任何实例，使用默认列表
            if not instances:
                self.debug_print("使用默认nitter实例列表")
                return self.default_instances
            
            # 过滤掉已知的不可用实例
            blacklist = {}  # 可以添加已知不可用的实例
            instances = [i for i in instances if not any(b in i for b in blacklist)]
            
            self.debug_print(f"最终获取到 {len(instances)} 个nitter实例")
            return list(instances)
            
        except Exception as e:
            self.debug_print(f"获取nitter实例列表失败: {str(e)}")
            return self.default_instances

    def get_recent_tweets(self, username: str, count: int = 5):
        """获取用户最近的推文"""
        try:
            delay = random.uniform(*self.delay_range)
            self.debug_print(f"等待 {delay:.2f} 秒后开始获取推文...")
            time.sleep(delay)
            
            # 获取最新的nitter实例列表
            nitter_instances = self.get_nitter_instances()
            self.debug_print(f"准备尝试的nitter实例数量: {len(nitter_instances)}")
            
            tweets = []
            success = False
            
            # 随机打乱实例列表顺序
            random.shuffle(nitter_instances)
            
            for instance in nitter_instances:
                try:
                    url = f"{instance}/{username}"
                    self.debug_print(f"\n=== 尝试访问URL: {url} ===")
                    
                    # 创建session并设置重定向处理
                    session = requests.Session()
                    session.max_redirects = 3
                    
                    # 发送请求，禁用SSL验证
                    self.debug_print("发送请求...")
                    response = session.get(
                        url,
                        headers=self.headers,
                        timeout=10,
                        verify=False,
                        allow_redirects=True
                    )
                    
                    # 检查是否被重定向到本地
                    if '127.0.0.1' in response.url or 'localhost' in response.url:
                        self.debug_print(f"❌ 被重定向到本地地址：{response.url}，跳过此URL")
                        continue
                        
                    # 如果发生了重定向，输出最终URL
                    if response.url != url:
                        self.debug_print(f"⚠️ 发生重定向")
                        self.debug_print(f"原始URL: {url}")
                        self.debug_print(f"最终URL: {response.url}")
                        
                    self.debug_print(f"请求状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        self.debug_print("✅ 请求成功")
                        
                        # 保存HTML到temp目录
                        self.save_html_to_temp(response.url, response.text)
                        
                        soup = BeautifulSoup(response.text, 'html.parser')
                        self.debug_print("成功解析页面HTML")
                        
                        # 输出页面基本结构
                        self.debug_print("\n=== 页面结构分析 ===")
                        self.debug_print(f"页面标题: {soup.title.string if soup.title else '无标题'}")
                        
                        # 检查是否是错误页面
                        error_msg = soup.find(class_=lambda x: x and 'error' in str(x).lower())
                        if error_msg:
                            self.debug_print(f"⚠️ 检测到错误信息: {error_msg.get_text().strip()}")
                        
                        # 查找推文容器
                        timeline = soup.find('div', class_='timeline')
                        self.debug_print("\n=== Timeline容器查找 ===")
                        if timeline:
                            self.debug_print("✅ 找到timeline容器")
                            self.debug_print(f"Timeline容器类名: {timeline.get('class', [])}")
                            tweet_items = timeline.find_all(['div', 'article'], class_=['timeline-item', 'tweet-card', 'tweet'])
                            self.debug_print(f"在timeline中找到 {len(tweet_items)} 条推文")
                        else:
                            self.debug_print("❌ 未找到timeline容器")
                            self.debug_print("检查所有div的class属性:")
                            for div in soup.find_all('div', class_=True):
                                self.debug_print(f"发现div，类名: {div.get('class', [])}")
                            
                            self.debug_print("\n尝试直接查找推文...")
                            tweet_items = soup.find_all(['div', 'article'], class_=['timeline-item', 'tweet-card', 'tweet'])
                            
                        self.debug_print(f"\n=== 推文查找结果 ===")
                        self.debug_print(f"找到 {len(tweet_items)} 条原始推文")
                        
                        if not tweet_items:
                            self.debug_print("\n=== 使用备用选择器 ===")
                            self.debug_print("搜索包含tweet或timeline-item的所有元素")
                            tweet_items = soup.find_all(class_=lambda x: x and any(term in str(x).lower() for term in ['tweet', 'timeline-item']))
                            self.debug_print(f"使用备用选择器找到 {len(tweet_items)} 条推文")
                        
                        for item in tweet_items:
                            if len(tweets) >= count:
                                break
                                
                            # 获取推文内容
                            tweet_content = None
                            content_candidates = item.find_all(['div', 'p'], class_=lambda x: x and any(term in str(x).lower() for term in ['content', 'text', 'body']))
                            
                            for candidate in content_candidates:
                                if candidate.get_text().strip():
                                    tweet_content = candidate
                                    break
                                    
                            if not tweet_content:
                                self.debug_print("跳过一条无内容的推文")
                                continue
                                
                            content_text = tweet_content.get_text().strip()
                            if not content_text:
                                self.debug_print("跳过一条空内容的推文")
                                continue
                                
                            # 获取时间
                            time_element = item.find(['span', 'a'], class_=lambda x: x and any(term in str(x).lower() for term in ['date', 'time']))
                            tweet_time = "Unknown time"
                            if time_element:
                                tweet_time = time_element.get('title', None) or time_element.get_text().strip()
                            
                            # 获取统计信息
                            stats = {}
                            stats_elements = item.find_all(['span', 'div'], class_=lambda x: x and any(term in str(x).lower() for term in ['stat', 'count', 'activity']))
                            
                            for stat in stats_elements:
                                text = stat.get_text().strip().lower()
                                if 'retweet' in text or '转推' in text or 'rt' in text:
                                    match = re.search(r'\d+', text)
                                    if match:
                                        stats['retweets'] = match.group()
                                elif 'like' in text or '喜欢' in text:
                                    match = re.search(r'\d+', text)
                                    if match:
                                        stats['likes'] = match.group()
                            
                            tweet = {
                                "text": content_text,
                                "time": tweet_time,
                                "stats": stats
                            }
                            tweets.append(tweet)
                            self.debug_print(f"已处理第 {len(tweets)} 条推文，发布时间: {tweet_time}")
                        
                        if tweets:
                            success = True
                            self.debug_print(f"成功从 {instance} 获取推文")
                            break
                        else:
                            self.debug_print("未能提取到任何有效推文，尝试下一个实例")
                    
                except requests.exceptions.SSLError:
                    self.debug_print(f"SSL错误，跳过实例 {instance}")
                    continue
                except requests.exceptions.Timeout:
                    self.debug_print(f"请求超时，跳过实例 {instance}")
                    continue
                except requests.exceptions.RequestException as e:
                    self.debug_print(f"请求错误，跳过实例 {instance}: {str(e)}")
                    continue
                except Exception as e:
                    self.debug_print(f"未知错误，跳过实例 {instance}: {str(e)}")
                    continue
                finally:
                    if 'session' in locals():
                        session.close()
            
            if not success:
                self.debug_print("所有实例均获取失败")
                return []
            
            self.debug_print(f"最终获取到 {len(tweets)} 条推文")
            return tweets[:count]
            
        except Exception as e:
            self.debug_print(f"获取推文过程中发生错误: {str(e)}")
            return []

    def fetch_page(self, url):
        try:
            # 使用 cloudscraper 发送请求
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)  # 设置随机延迟
            response = self.scraper.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.debug_print(f"请求失败: {e}")
            return None 