import openai
from openai import AzureOpenAI, OpenAI
from config import Config

class AISummarizer:
    def __init__(self):
        self.setup_ai_client()

    def setup_ai_client(self):
        """根据配置初始化AI客户端"""
        if Config.AI_PROVIDER == 'azure':
            self.client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_KEY,
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
            )
            self.model = Config.AZURE_DEPLOYMENT
            self.debug_print(f"初始化Azure OpenAI客户端：\n"
                          f"Endpoint: {Config.AZURE_OPENAI_ENDPOINT}\n"
                          f"API Version: {Config.AZURE_OPENAI_API_VERSION}\n"
                          f"Deployment: {Config.AZURE_DEPLOYMENT}")
        else:
            # OpenAI或其他供应商
            client_kwargs = {
                'api_key': Config.AI_API_KEY
            }
            if Config.AI_BASE_URL:
                client_kwargs['base_url'] = Config.AI_BASE_URL

            self.client = OpenAI(**client_kwargs)
            self.model = Config.AI_MODEL
            self.debug_print(f"初始化OpenAI客户端：\n"
                          f"Base URL: {Config.AI_BASE_URL or 'default'}\n"
                          f"Model: {self.model}")

    def debug_print(self, message):
        """调试信息打印"""
        print(f"[AI Debug] {message}")

    def summarize_tweets(self, tweets):
        try:
            if not tweets:
                return "没有找到最新推文。"
                
            # 按照 order 字段排序推文
            sorted_tweets = sorted(tweets, key=lambda x: x.get('order', float('inf')))
            
            # 准备推文内容和链接，确保一一对应
            tweet_texts = []
            tweet_urls = []
            tweet_previews = []
            for tweet in sorted_tweets:
                # 提取推文正文，去除用户名和时间信息
                text = tweet['text']
                # 检查是否为置顶推文
                is_pinned = tweet.get('pinned', False)
                # 如果是置顶推文，添加标识
                if is_pinned:
                    text = '📌 ' + text
                # 移除包含 @ 的用户名信息
                text = ' '.join([word for word in text.split() if not word.startswith('@')])
                # 移除日期信息（通常在推文末尾，格式如 Jan 28）
                text = ' '.join([word for word in text.split() if not any(month in word for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])])
                
                tweet_texts.append(text)
                tweet_urls.append(tweet.get('url', ''))
                # 生成推文预览（前10个单词），保留置顶标识
                words = text.split()
                preview = ' '.join(words[:10]) + '...' if len(words) > 10 else text
                tweet_previews.append(preview)
            
            text = "\n".join(tweet_texts)
            
            self.debug_print(f"准备发送请求到{Config.AI_PROVIDER.upper()}")
            
            # 计算最大长度限制
            max_tokens = 800
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的双语总结助手。你需要提供清晰、格式化的中英文对照总结。请提取推文中最重要的信息点进行总结。"},
                    {
                        "role": "user",
                        "content": f"""请对以下推文内容进行双语总结：

1. 提取2-3个最重要的核心信息点
2. 每个信息点都需要中英文对照
3. 数据指标用`*加粗*`突出显示

推文内容：
{text}

输出格式：
📌 *核心信息概览* | *Key Information*
━━━━━━━━━━━━━━━━━━━━━

1️⃣ 中文核心信息点一
   🔹 Key information point 1 in English

2️⃣ 中文核心信息点二
   🔹 Key information point 2 in English

3️⃣ 中文核心信息点三
   🔹 Key information point 3 in English"""
                    }
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            
            self.debug_print(f"成功收到{Config.AI_PROVIDER.upper()}响应")
            content = response.choices[0].message.content
            
            # 添加推文预览部分
            preview_section = "\n\n📝 *原始推文* | *Original Tweets*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            for i, (preview, url) in enumerate(zip(tweet_previews, tweet_urls), 1):
                preview_section += f"{i}. {preview}\n   🔗 {url}\n\n"
            
            return content + preview_section

        except Exception as e:
            error_message = f"处理推文时发生错误：{str(e)}"
            self.debug_print(error_message)
            return error_message

    def _generate_tweet_summary_template(self, urls):
        """生成推文总结模板，确保链接一一对应"""
        template = []
        for i, url in enumerate(urls, 1):
            template.append(f"{i}. 第{i}条推文中文总结\n   🔹 Tweet {i} summary in English\n   🔗 {url}\n")
        return "\n".join(template)
    
    def _split_content(self, content):
        """将内容分段，确保不超过Telegram消息长度限制"""
        # 按照段落分割内容
        parts = []
        current_part = ""
        
        # 分割内容为核心信息和原始推文两部分
        sections = content.split("📝 *原始推文* | *Original Tweets*")
        
        if len(sections) == 2:
            overview = sections[0].strip()
            tweets_section = "📝 *原始推文* | *Original Tweets*" + sections[1]
            
            # 添加核心信息概览作为第一部分
            if len(overview) > 4000:
                # 如果概览部分过长，也需要分段
                words = overview.split()
                for word in words:
                    if len(current_part) + len(word) + 1 > 3900:  # 留出空间给页码和导航标记
                        parts.append(current_part.strip())
                        current_part = word
                    else:
                        current_part += " " + word if current_part else word
                if current_part:
                    parts.append(current_part.strip())
            else:
                parts.append(overview)
            
            # 处理推文部分
            current_part = ""
            tweets = tweets_section.split("\n\n")
            
            for tweet in tweets:
                if len(current_part) + len(tweet) + 2 > 3900:  # 留出空间给页码和导航标记
                    if current_part:
                        parts.append(current_part.strip())
                    current_part = tweet
                else:
                    current_part += "\n\n" + tweet if current_part else tweet
            
            if current_part:
                parts.append(current_part.strip())
        else:
            # 如果无法正确分割，则按照固定长度分割
            words = content.split()
            for word in words:
                if len(current_part) + len(word) + 1 > 3900:  # 留出空间给页码和导航标记
                    parts.append(current_part.strip())
                    current_part = word
                else:
                    current_part += " " + word if current_part else word
            
            if current_part:
                parts.append(current_part.strip())
        
        # 为分段内容添加页码标记和导航按钮标记
        formatted_parts = []
        total_pages = len(parts)
        
        for i, part in enumerate(parts):
            page_info = f"\n\n📄 第{i+1}页/共{total_pages}页"
            # 添加特殊标记用于Telegram处理程序识别并添加导航按钮
            nav_marker = f"\n[NAV:{i+1}:{total_pages}]"
            formatted_parts.append(f"{part}{page_info}{nav_marker}")
        
        return formatted_parts
        
        # 为分段内容添加页码标记
        return [f"{content}\n\n📄 第{i+1}页/共{len(parts)}页" for i, content in enumerate(parts)]