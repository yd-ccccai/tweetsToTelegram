import openai
from openai import AzureOpenAI
from config import Config

class AISummarizer:
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.debug_print(f"初始化Azure OpenAI客户端：\n"
                      f"Endpoint: {Config.AZURE_OPENAI_ENDPOINT}\n"
                      f"API Version: {Config.AZURE_OPENAI_API_VERSION}\n"
                      f"Deployment: {Config.AZURE_DEPLOYMENT}")

    def debug_print(self, message):
        """调试信息打印"""
        print(f"[AI Debug] {message}")

    def summarize_tweets(self, tweets):
        try:
            text = "\n".join([t['text'] for t in tweets])
            self.debug_print("准备发送请求到Azure OpenAI")
            
            response = self.client.chat.completions.create(
                model=Config.AZURE_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "你是一个专业的双语总结助手。你需要提供清晰、格式化的中英文对照总结，特别注意在Telegram消息中的显示效果。"},
                    {
                        "role": "user",
                        "content": f"""请对以下推文内容进行中英文对照总结，要求：
1. 提取3-5个最重要的要点
2. 每个要点都包含中英文对照
3. 数据指标需要用`*加粗*`突出显示
4. 使用清晰的分隔和emoji标记

推文内容：
{text}

输出格式：
📌 *推文要点总结* | *Tweet Summary*
━━━━━━━━━━━━━━━━━━━━━

1️⃣ 中文要点一
   🔹 English Point 1

2️⃣ 中文要点二
   🔹 English Point 2

3️⃣ 中文要点三
   🔹 English Point 3

━━━━━━━━━━━━━━━━━━━━━
📊 *数据亮点* | *Key Metrics*
• 中文指标 (*具体数字*)
• English metric (*specific number*)
"""
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            self.debug_print("成功收到Azure OpenAI响应")
            return response.choices[0].message.content
            
        except openai.RateLimitError:
            self.debug_print("触发频率限制")
            return "⚠️ *请求过于频繁，请稍后再试*"
        except openai.APIError as e:
            self.debug_print(f"API错误：{str(e)}")
            return f"❌ *API调用错误*：{str(e)}"
        except Exception as e:
            self.debug_print(f"其他错误：{str(e)}")
            return f"❌ *系统错误*：{str(e)}" 