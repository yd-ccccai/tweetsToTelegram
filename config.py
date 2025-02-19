import os
from dotenv import load_dotenv

class Config:
    # 加载.env文件
    load_dotenv()
    
    # 从环境变量中获取配置
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # AI服务商配置
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'azure')  # 默认使用azure，可选：azure, openai
    AI_BASE_URL = os.getenv('AI_BASE_URL')  # OpenAI时可选
    AI_API_KEY = os.getenv('AI_API_KEY')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-4')  # 默认使用gpt-4
    
    # Azure OpenAI特定配置
    AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
    AZURE_DEPLOYMENT = os.getenv('AZURE_DEPLOYMENT')
    
    # 调试配置
    DEBUG_CRAWLER = os.getenv('DEBUG_CRAWLER', 'false').lower() == 'true'
    
    # 数据库配置
    DATABASE_URL = "sqlite:///twitter_monitor.db"