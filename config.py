import os
from dotenv import load_dotenv

class Config:
    # 加载.env文件
    load_dotenv()
    
    # 从环境变量中获取配置
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')
    AZURE_DEPLOYMENT = os.getenv('AZURE_DEPLOYMENT')
    
    # 调试配置
    DEBUG_CRAWLER = os.getenv('DEBUG_CRAWLER', 'false').lower() == 'true'
    
    # 数据库配置
    DATABASE_URL = "sqlite:///twitter_monitor.db" 